"""Single-sensor strict-past Ridge behavior, sharing the existing fold optimizer."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import math
import numpy as np

from dual_imu_collision_studio.domain.learning.model import (
    FrozenFirModel,
    LearningDataset,
    HistorySpec,
    CandidatePlan,
)
from .preprocessing import SingleImuSettings, preprocess
from dual_imu_collision_studio.domain.learning.service import LearningService


@dataclass(frozen=True, slots=True)
class FrozenSelfImuModel(FrozenFirModel):
    preprocessing: SingleImuSettings = SingleImuSettings()


def self_rows(xyz, discontinuities, eligible, lag_count):
    values = np.asarray(xyz, dtype=np.float64)
    valid = np.asarray(eligible, dtype=bool)
    resets = np.asarray(discontinuities, dtype=bool)
    if (
        values.ndim != 2
        or values.shape[1] not in (3, 6)
        or valid.shape != (len(values),)
        or resets.shape != valid.shape
    ):
        raise ValueError(
            "Self-prediction needs XYZ and matching eligibility/reset masks"
        )
    if type(lag_count) is not int or lag_count < 1:
        raise ValueError("History must contain at least one strictly past sample")
    indexes, rows = [], []
    for t in range(lag_count, len(values)):
        if (
            not valid[t - lag_count : t + 1].all()
            or resets[t - lag_count + 1 : t + 1].any()
        ):
            continue
        window = values[t - lag_count : t + 1]
        if not np.isfinite(window).all():
            continue
        indexes.append(t)
        rows.append(values[t - lag_count : t][::-1].T.reshape(-1))
    indexes = np.asarray(indexes, dtype=np.int64)
    return (
        np.asarray(rows).reshape(-1, values.shape[1] * lag_count),
        values[indexes],
        indexes,
    )


def _wrap(model, settings):
    return FrozenSelfImuModel(
        **{field.name: getattr(model, field.name) for field in fields(FrozenFirModel)},
        preprocessing=settings,
    )


def prepare_recording(recording, settings):
    if recording.preprocessing != settings:
        raise ValueError(
            "Recording preprocessing does not match the frozen single-IMU model"
        )
    if getattr(recording, "prepared_self", False):
        if recording.preprocessing != settings:
            raise ValueError("Prepared source settings do not match frozen model")
        return recording
    source = getattr(recording, settings.sensor + "_imu")
    if source is None:
        raise ValueError("Selected single sensor is absent")
    filtered, warm = preprocess(
        source, recording.discontinuity_before, settings, recording.sample_rate_hz
    )
    if recording.training_eligible is not None:
        warm &= np.asarray(recording.training_eligible, dtype=bool)
    # These are internal solver input/target buffers, not a fabricated second physical sensor.
    shifted = np.zeros_like(filtered)
    shifted[1:] = filtered[:-1]
    valid = warm.copy()
    if len(valid):
        valid[0] = False
        valid[1:] &= warm[:-1]
    resets = np.asarray(recording.discontinuity_before, dtype=bool)
    valid[resets] = False
    return replace(
        recording,
        internal_imu=shifted,
        external_imu=filtered,
        preprocessing=settings,
        training_eligible=valid,
        prepared_self=True,
    )


def service_for_dataset(dataset, **kwargs):
    settings = getattr(dataset.recordings[0], "preprocessing", None)
    return (
        SelfImuLearningService(settings, **kwargs)
        if settings is not None
        else LearningService(**kwargs)
    )


class SelfImuLearningService(LearningService):
    def __init__(self, settings: SingleImuSettings, **kwargs):
        super().__init__(**kwargs)
        self._single_settings = settings

    def learn_and_qualify(
        self, dataset, numeric_type, progress=None, cancelled=None, *, settings=None
    ):
        from .optimization import run_learning

        if settings is not None and settings.model_families != ("fir",):
            raise ValueError(
                "Single-IMU mode supports Ridge only; deselect dual-IMU MLP"
            )
        if any(r.preprocessing != self._single_settings for r in dataset.recordings):
            raise ValueError(
                "Single-IMU recordings must share preprocessing settings and sensor identity"
            )
        prepared = LearningDataset(
            tuple(
                prepare_recording(r, self._single_settings) for r in dataset.recordings
            )
        )
        from dual_imu_collision_studio.domain.learning.model import (
            LearningSettings,
            TrainingMode,
        )

        captured = (
            settings
            if settings is not None
            else LearningSettings(training_mode=TrainingMode.OPTIMIZED)
        )
        return run_learning(
            self, prepared, numeric_type, captured.for_run(), progress, cancelled
        )

    def maximum_taps(self, rate):
        return max(1, math.floor(0.128 * rate))

    def build_candidate_plan(self, sample_rate_hz, settings=None):
        original = super().build_candidate_plan(sample_rate_hz, settings)
        by_taps = {}
        for history in original.histories:
            taps = max(1, history.tap_count - 1)
            by_taps.setdefault(taps, []).extend(history.requested_history_aliases_ms)
        histories = tuple(
            HistorySpec(t, tuple(v), 1000 * t / sample_rate_hz)
            for t, v in by_taps.items()
        )
        return replace(original, histories=histories)

    def _fit_mimo_fir_matrix(self, *args, **kwargs):
        return _wrap(
            super()._fit_mimo_fir_matrix(*args, **kwargs), self._single_settings
        )

    def _freeze_model_numeric_type(self, model, numeric_type):
        return _wrap(
            super()._freeze_model_numeric_type(model, numeric_type),
            self._single_settings,
        )


def replay_arrays(recording, model, numeric_type):
    prepared = prepare_recording(recording, model.preprocessing)
    plain = FrozenFirModel(
        **{f.name: getattr(model, f.name) for f in fields(FrozenFirModel)}
    )
    predicted, residual, normalized, reset = LearningService._target_replay_arrays(
        prepared, plain, numeric_type
    )
    valid = np.asarray(prepared.training_eligible, dtype=bool).copy()
    # Readiness follows continuous history, independent of Ignore and of common CV scoring horizon.
    count_since_reset = 0
    for index in range(len(valid)):
        if reset[index]:
            count_since_reset = 0
        count_since_reset = count_since_reset + 1 if valid[index] else 0
        if count_since_reset < model.tap_count:
            normalized[index] = np.nan
    for interval in prepared.intervals:
        if interval.kind == "Ignore":
            normalized[interval.start_index : interval.end_index] = np.nan
    return predicted, residual, normalized, reset
