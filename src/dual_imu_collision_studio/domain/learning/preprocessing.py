"""Immutable single-sensor preprocessing contracts and causal numerical operations."""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
from scipy import __version__ as scipy_version
from scipy import signal


@dataclass(frozen=True, slots=True)
class FilterStageSpec:
    kind: str
    passband_hz: tuple[float, ...]
    stopband_hz: tuple[float, ...]
    passband_attenuation_ratio: float
    stopband_amplitude_ratio: float

    def __post_init__(self):
        if self.kind not in {"highpass", "lowpass", "bandpass", "bandstop"}:
            raise ValueError("Unsupported filter type")
        count = 1 if self.kind in {"highpass", "lowpass"} else 2
        for name in ("passband_hz", "stopband_hz"):
            value = tuple(float(v) for v in getattr(self, name))
            if len(value) != count or any(
                not math.isfinite(v) or v <= 0 for v in value
            ):
                raise ValueError("Filter edges must be finite positive Hz values")
            object.__setattr__(self, name, value)
        rp, amplitude = self.passband_attenuation_ratio, self.stopband_amplitude_ratio
        if not math.isfinite(rp) or rp <= 1:
            raise ValueError("Passband maximum attenuation ratio must exceed 1")
        if not math.isfinite(amplitude) or not 0 < amplitude < 1:
            raise ValueError("Stopband maximum amplitude ratio must be between 0 and 1")
        if self.gstop <= self.gpass:
            raise ValueError("Stopband attenuation must exceed passband attenuation")

    @property
    def gpass(self):
        return 20 * math.log10(self.passband_attenuation_ratio)

    @property
    def gstop(self):
        return -20 * math.log10(self.stopband_amplitude_ratio)


@dataclass(frozen=True, slots=True)
class FilterDesign:
    specification: FilterStageSpec
    sample_rate_hz: float
    order: int
    sos: tuple[tuple[float, ...], ...]
    designer_version: str

    def __post_init__(self):
        if not math.isfinite(self.sample_rate_hz) or self.sample_rate_hz <= 0:
            raise ValueError("Filter sample rate must be finite and positive")
        if type(self.order) is not int or self.order <= 0:
            raise ValueError("Filter order must be a positive integer")
        coefficients = np.asarray(self.sos, dtype=np.float64)
        if (
            coefficients.ndim != 2
            or coefficients.shape[1] != 6
            or not len(coefficients)
        ):
            raise ValueError("Filter SOS must have six coefficients per section")
        if not np.isfinite(coefficients).all() or not np.all(coefficients[:, 3] == 1):
            raise ValueError("Filter SOS must be finite with normalized denominator")
        if len(coefficients) != (self.order + 1) // 2:
            raise ValueError("Filter order and SOS section count differ")
        if any(np.any(np.abs(np.roots(section[3:])) >= 1) for section in coefficients):
            raise ValueError("Filter poles must be strictly inside the unit circle")
        _validate_edges(self.specification, self.sample_rate_hz)
        _validate_response(self.specification, self.sample_rate_hz, coefficients)
        if not self.designer_version:
            raise ValueError("Filter designer provenance is required")
        object.__setattr__(
            self, "sos", tuple(tuple(float(v) for v in row) for row in coefficients)
        )


@dataclass(frozen=True, slots=True)
class SingleImuSettings:
    sensor: str = "internal"
    source_mode: str = "already_filtered"
    filters: tuple[FilterDesign, ...] = ()
    warmup_samples: int = 500

    def __post_init__(self):
        if self.sensor not in {"internal", "external"}:
            raise ValueError("Select one source sensor")
        if self.source_mode not in {"already_filtered", "application_filtered"}:
            raise ValueError("Select existing filtered data or application filtering")
        object.__setattr__(self, "filters", tuple(self.filters))
        if type(self.warmup_samples) is not int or self.warmup_samples < 1:
            raise ValueError("Warmup length must be a positive integer sample count")
        if self.source_mode == "already_filtered" and self.filters:
            raise ValueError(
                "Already-filtered columns must bypass application filtering"
            )
        if self.source_mode == "application_filtered" and not self.filters:
            raise ValueError("Adopt a filter design before using application filtering")
        if any(not isinstance(v, FilterDesign) for v in self.filters):
            raise ValueError("Invalid adopted filter design")


def _validate_edges(specification, fs):
    p, s = specification.passband_hz, specification.stopband_hz
    if specification.kind == "highpass":
        edges = (s[0], p[0])
    elif specification.kind == "lowpass":
        edges = (p[0], s[0])
    elif specification.kind == "bandpass":
        edges = (s[0], p[0], p[1], s[1])
    else:
        edges = (p[0], s[0], s[1], p[1])
    if any(a >= b for a, b in zip((0.0,) + edges, edges + (fs / 2,))):
        raise ValueError("Filter edges have invalid ordering or exceed Nyquist")


def _validate_response(specification, fs, sos):
    p, s = specification.passband_hz, specification.stopband_hz
    # Independently check specified edges; do not claim per-stage compliance proves cascade compliance.
    _, pass_response = signal.sosfreqz(sos, worN=np.asarray(p), fs=fs)
    _, stop_response = signal.sosfreqz(sos, worN=np.asarray(s), fs=fs)
    if np.any(
        np.abs(pass_response) < 1 / specification.passband_attenuation_ratio - 1e-8
    ):
        raise ValueError("Numerical design does not meet the passband requirement")
    if np.any(np.abs(stop_response) > specification.stopband_amplitude_ratio + 1e-8):
        raise ValueError("Numerical design does not meet the stopband requirement")


def design_filter(
    specification: FilterStageSpec, sample_rate_hz: float
) -> FilterDesign:
    fs = float(sample_rate_hz)
    if not math.isfinite(fs) or fs <= 0:
        raise ValueError("Sample rate must be finite and positive")
    _validate_edges(specification, fs)
    p, s = specification.passband_hz, specification.stopband_hz
    wp, ws = (p[0], s[0]) if len(p) == 1 else (p, s)
    prototype_order, wn = signal.buttord(
        wp, ws, specification.gpass, specification.gstop, fs=fs
    )
    sos = signal.butter(
        prototype_order, wn, btype=specification.kind, fs=fs, output="sos"
    )
    order = int(prototype_order) * (
        1 if specification.kind in {"highpass", "lowpass"} else 2
    )
    result = FilterDesign(
        specification, fs, order, tuple(map(tuple, sos)), scipy_version
    )
    return result


def preprocess(xyz, discontinuity_before, settings: SingleImuSettings, sample_rate_hz):
    values = np.array(xyz, dtype=np.float64, copy=True)
    if values.ndim != 2 or values.shape[1] != 3 or not np.isfinite(values).all():
        raise ValueError("Single-IMU source must contain finite XYZ samples")
    resets = np.asarray(discontinuity_before, dtype=bool)
    if resets.shape != (len(values),):
        raise ValueError("Discontinuities must match source rows")
    eligible = np.ones(len(values), dtype=bool)
    if settings.source_mode == "already_filtered":
        return values, eligible
    fs = float(sample_rate_hz)
    if not math.isfinite(fs) or fs <= 0:
        raise ValueError("Invalid effective sample rate")
    if any(abs(stage.sample_rate_hz - fs) / fs > 0.005 for stage in settings.filters):
        raise ValueError("Adopted filter sample rate does not match the recording")
    boundaries = np.unique(np.r_[0, np.flatnonzero(resets), len(values)])
    for start, end in zip(boundaries[:-1], boundaries[1:]):
        block = values[start:end]
        for stage in settings.filters:
            block = signal.sosfilt(np.asarray(stage.sos), block, axis=0)
        values[start:end] = block
        eligible[start : min(end, start + settings.warmup_samples)] = False
    if not np.isfinite(values).all():
        raise ValueError("Filtered output is non-finite")
    return values, eligible


def settings_to_data(settings):
    return {
        "sensor": settings.sensor,
        "source_mode": settings.source_mode,
        "warmup_samples": settings.warmup_samples,
        "filters": [
            {
                "kind": d.specification.kind,
                "passband_hz": list(d.specification.passband_hz),
                "stopband_hz": list(d.specification.stopband_hz),
                "passband_attenuation_ratio": d.specification.passband_attenuation_ratio,
                "stopband_amplitude_ratio": d.specification.stopband_amplitude_ratio,
                "sample_rate_hz": d.sample_rate_hz,
                "order": d.order,
                "sos": [list(row) for row in d.sos],
                "designer_version": d.designer_version,
            }
            for d in settings.filters
        ],
    }


def settings_from_data(data):
    if not isinstance(data, dict) or set(data) != {
        "sensor",
        "source_mode",
        "warmup_samples",
        "filters",
    }:
        raise ValueError("Invalid single-IMU settings")
    stages = tuple(
        FilterDesign(
            FilterStageSpec(
                v["kind"],
                tuple(v["passband_hz"]),
                tuple(v["stopband_hz"]),
                v["passband_attenuation_ratio"],
                v["stopband_amplitude_ratio"],
            ),
            v["sample_rate_hz"],
            v["order"],
            tuple(map(tuple, v["sos"])),
            v["designer_version"],
        )
        for v in data["filters"]
    )
    return SingleImuSettings(
        data["sensor"], data["source_mode"], stages, data["warmup_samples"]
    )


def cascade_response(settings):
    """Check the saved cascade at every declared edge; expose compounded attenuation."""
    if not settings.filters:
        return []
    sos = np.concatenate([np.asarray(d.sos) for d in settings.filters])
    fs = settings.filters[0].sample_rate_hz
    if any(d.sample_rate_hz != fs for d in settings.filters):
        raise ValueError("Cascade stages must share one design sample rate")
    rows = []
    for index, d in enumerate(settings.filters):
        spec = d.specification
        _, p = signal.sosfreqz(sos, worN=np.asarray(spec.passband_hz), fs=fs)
        _, s = signal.sosfreqz(sos, worN=np.asarray(spec.stopband_hz), fs=fs)
        if not np.isfinite(p).all() or not np.isfinite(s).all():
            raise ValueError("Cascade frequency response is non-finite")
        pass_min = float(np.abs(p).min())
        stop_max = float(np.abs(s).max())
        rows.append(
            dict(
                stage=index + 1,
                passband_min_amplitude=pass_min,
                passband_required_min=1 / spec.passband_attenuation_ratio,
                stopband_max_amplitude=stop_max,
                stopband_required_max=spec.stopband_amplitude_ratio,
                meets_stage_edges=pass_min >= 1 / spec.passband_attenuation_ratio - 1e-8
                and stop_max <= spec.stopband_amplitude_ratio + 1e-8,
            )
        )
    return rows
