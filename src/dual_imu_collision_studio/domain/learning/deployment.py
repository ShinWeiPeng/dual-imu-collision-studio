"""Shared Qualification and Replay event policy; never deploys to hardware."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
import hashlib
import json
from collections.abc import Callable

import numpy as np

from dual_imu_collision_studio.domain.learning.model import (
    DetectorConfig,
    FrozenFirModel,
    FrozenMlpModel,
    DetectorTrace,
    LearningDataset,
    QualifiedCandidate,
)

COMMON_EVENT_POLICY = "common-rearm-0.8-50ms/qualification-v2"


@dataclass(frozen=True, slots=True)
class DeploymentQualification:
    input_sha256: str
    policy: str
    result: QualifiedCandidate
    passed: bool
    reason: str


def deployment_identity(dataset: LearningDataset, candidate: QualifiedCandidate) -> str:
    """Fingerprint actual frozen inputs, including sample bytes and confirmed labels."""
    digest = hashlib.sha256()

    def visit(value):
        if isinstance(value, np.ndarray):
            array = np.ascontiguousarray(value)
            visit((array.dtype.str, array.shape))
            digest.update(memoryview(array).cast("B"))
        elif is_dataclass(value):
            visit(type(value).__name__)
            for field in fields(value):
                # This training provenance does not affect frozen execution and is
                # not part of the persisted model contract.
                if (
                    isinstance(value, (FrozenFirModel, FrozenMlpModel))
                    and field.name == "use_robust_refit"
                ):
                    continue
                if isinstance(value, DetectorConfig) and field.name in {
                    "release_ratio",
                    "release_quiet_time_s",
                }:
                    continue
                visit(field.name)
                visit(getattr(value, field.name))
        elif isinstance(value, (tuple, list)):
            digest.update(b"[")
            for item in value:
                visit(item)
            digest.update(b"]")
        else:
            digest.update(
                json.dumps(value, ensure_ascii=False, default=str).encode("utf-8")
            )
            digest.update(b"\0")

    visit(COMMON_EVENT_POLICY)
    visit(dataset)
    visit(
        (
            candidate.candidate_id,
            candidate.model,
            candidate.detector_config,
            candidate.training_speeds,
            candidate.passing_speeds,
            candidate.active_offsets,
        )
    )
    return digest.hexdigest()


def replay_common_events(
    detector_scores: np.ndarray,
    time_s: np.ndarray,
    config: DetectorConfig,
    reset_before: np.ndarray | None = None,
    *,
    sample_rate_hz: float | None = None,
    cancelled: Callable[[], bool] | None = None,
) -> DetectorTrace:
    """Strict collision candidates enter one latch with continuous valid quiet time."""
    if config.numeric_type not in {"float32", "float64"}:
        raise ValueError("Target Numeric Type must be float32 or float64")
    if config.confirmation_mode != "1_OF_1":
        raise ValueError("Common deployment requires 1_OF_1 confirmation")
    dtype = np.dtype(config.numeric_type).type
    scores = np.asarray(detector_scores, dtype=dtype)
    times = np.asarray(time_s, dtype=np.float64)
    resets = (
        np.zeros(len(times), dtype=np.bool_)
        if reset_before is None
        else np.asarray(reset_before, dtype=np.bool_)
    )
    if scores.ndim != 1 or times.shape != scores.shape or resets.shape != scores.shape:
        raise ValueError(
            "Common replay arrays must have matching one-dimensional shape"
        )
    threshold = dtype(config.threshold)
    if not np.isfinite(threshold) or threshold <= 0:
        raise ValueError("Deployment threshold must be finite and positive")
    if sample_rate_hz is not None and (
        not np.isfinite(sample_rate_hz) or sample_rate_hz <= 0
    ):
        raise ValueError("Sample rate must be finite and positive")
    release_threshold = dtype(threshold * dtype(0.8))
    armed, quiet_deadline, previous_time = True, None, None
    states, triggers = [], []
    for index, (score, timestamp) in enumerate(zip(scores, times, strict=True)):
        if cancelled is not None and index % 1024 == 0 and cancelled():
            raise InterruptedError("Deployment validation cancelled")
        gap = resets[index]
        if previous_time is not None and np.isfinite(timestamp):
            elapsed_sample = timestamp - previous_time
            gap = (
                gap
                or elapsed_sample <= 0
                or (
                    sample_rate_hz is not None
                    and elapsed_sample > 1.02 / sample_rate_hz + 1e-12
                )
            )
        if gap:
            quiet_deadline = None
        if not np.isfinite(score) or not np.isfinite(timestamp):
            quiet_deadline = None
            previous_time = None
            states.append("INVALID")
            continue
        previous_time = float(timestamp)
        if not armed:
            if score < release_threshold:
                if quiet_deadline is None:
                    quiet_deadline = float(
                        Decimal(str(float(timestamp))) + Decimal("0.050")
                    )
                if timestamp >= quiet_deadline:
                    armed, quiet_deadline = True, None
            else:
                quiet_deadline = None
            states.append("ARMED" if armed else "LATCHED")
        elif score > threshold:
            triggers.append(index)
            armed, quiet_deadline = False, None
            states.append("TRIGGERED")
        else:
            states.append("ARMED")
    return DetectorTrace(
        scores,
        scores / threshold,
        tuple(states),
        tuple(triggers),
        tuple(float(times[i]) for i in triggers),
    )
