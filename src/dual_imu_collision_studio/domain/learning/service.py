from __future__ import annotations

from dual_imu_collision_studio.domain.learning.model import CandidateNumericalError

import csv
import io
import math
from collections.abc import Iterator
from dataclasses import replace
import time
from typing import TextIO
from typing import Callable

import numpy as np

from dual_imu_collision_studio.domain.learning.model import (
    CandidatePlan,
    ConditionQualification,
    CrossValidationFold,
    CrossValidationPlan,
    CrossValidatedModel,
    CycleFoldGroup,
    DetectorConfig,
    DetectorTrace,
    FallbackAction,
    FallbackState,
    FallbackTransition,
    FirMatrixEvidence,
    FrozenFirModel,
    FrozenMlpModel,
    HistorySpec,
    HistoryFoldEvidence,
    HistoryBatchResult,
    HistoryAttemptTiming,
    HistoryJob,
    HistoryJobResult,
    InsufficientTrainingEvidence,
    FitEvidence,
    LearningDataset,
    LearningProgress,
    OffsetQualification,
    QualificationResult,
    QualifiedCandidate,
    RecordingQualification,
    ReplayEvidence,
    HistoryWorkerProgress,
)
from dual_imu_collision_studio.domain.learning.contracts import HistoryExecutionPort


class LearningService:
    REPLAY_CSV_HEADER = (
        "sample_index",
        "time_s",
        "internal_imu_x",
        "internal_imu_y",
        "internal_imu_z",
        "actual_external_imu_x",
        "actual_external_imu_y",
        "actual_external_imu_z",
        "fir_predicted_external_imu_x",
        "fir_predicted_external_imu_y",
        "fir_predicted_external_imu_z",
        "residual_x",
        "residual_y",
        "residual_z",
        "normalized_residual_x",
        "normalized_residual_y",
        "normalized_residual_z",
        "score",
        "threshold",
        "collision_ratio",
        "detector_state",
        "trigger",
    )

    MODEL_TEXT_SCHEMA_VERSION = 1

    @staticmethod
    def _model_number(value: object) -> str:
        if isinstance(value, np.generic):
            value = value.item()
        return repr(float(value))

    def iter_model_text_lines(
        self, candidate: QualifiedCandidate, *, sample_rate_hz: float
    ) -> Iterator[str]:
        model = candidate.model
        config = candidate.detector_config
        if model is None or config is None:
            raise ValueError("selected retained candidate has no frozen model")
        if not np.isfinite(sample_rate_hz) or sample_rate_hz <= 0:
            raise ValueError("Model TXT requires a positive finite Sample Rate")
        if isinstance(model, FrozenMlpModel):
            raise ValueError("MLP standalone export is not available in this phase")
        if model.weights.shape != (3, 3, model.tap_count):
            raise ValueError("frozen FIR weights do not match tap_count")
        vectors = (model.biases, model.residual_centers, model.residual_scales)
        if any(np.asarray(values).shape != (3,) for values in vectors):
            raise ValueError("frozen model vectors must contain X, Y, and Z")

        scalars = (
            ("schema_version", str(self.MODEL_TEXT_SCHEMA_VERSION)),
            ("kernel_id", candidate.candidate_id),
            ("sample_rate_hz", self._model_number(sample_rate_hz)),
            ("numeric_type", config.numeric_type),
            ("tap_count", str(model.tap_count)),
            ("score_mode", config.score_mode),
            ("confirmation_mode", config.confirmation_mode),
            ("threshold", self._model_number(config.threshold)),
            ("release_ratio", self._model_number(config.release_ratio)),
            ("release_quiet_time_s", self._model_number(config.release_quiet_time_s)),
        )
        for key, value in scalars:
            yield f"{key}={value}\n"
        yield "\n"
        yield "[fir_weights]\n"
        yield "output_axis,input_axis,lag,value\n"
        axes = "XYZ"
        for output_axis, output_name in enumerate(axes):
            for input_axis, input_name in enumerate(axes):
                for lag in range(model.tap_count):
                    value = self._model_number(
                        model.weights[output_axis, input_axis, lag]
                    )
                    yield f"{output_name},{input_name},{lag},{value}\n"
        for section, values in (
            ("bias", model.biases),
            ("residual_center", model.residual_centers),
            ("residual_scale", model.residual_scales),
        ):
            yield "\n"
            yield f"[{section}]\n"
            yield "axis,value\n"
            for axis, value in zip(axes, values, strict=True):
                yield f"{axis},{self._model_number(value)}\n"

    def iter_replay_csv_lines(self, evidence: ReplayEvidence) -> Iterator[str]:
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        for row in self._replay_csv_rows(evidence):
            buffer.seek(0)
            buffer.truncate(0)
            writer.writerow(row)
            yield buffer.getvalue()

    def write_replay_csv(self, evidence: ReplayEvidence, stream: TextIO) -> None:
        stream.writelines(self.iter_replay_csv_lines(evidence))

    def _replay_csv_rows(
        self, evidence: ReplayEvidence
    ) -> Iterator[tuple[object, ...]]:
        times = np.asarray(evidence.time_s)
        matrices = tuple(
            np.asarray(values)
            for values in (
                evidence.internal_imu,
                evidence.actual_external_imu,
                evidence.predicted_external_imu,
                evidence.residual,
                evidence.normalized_residual,
            )
        )
        scores = np.asarray(evidence.detector_trace.scores)
        ratios = np.asarray(evidence.detector_trace.collision_ratio)
        states = evidence.detector_trace.states
        count = len(times)
        if times.ndim != 1:
            raise ValueError("Replay time evidence must contain one value per sample")
        if any(values.shape != (count, 3) for values in matrices):
            raise ValueError(
                "Replay IMU and residual evidence must contain aligned Nx3 samples"
            )
        if scores.shape != (count,) or ratios.shape != (count,) or len(states) != count:
            raise ValueError("Replay detector evidence must align with every sample")

        triggers = frozenset(evidence.detector_trace.trigger_indices)
        yield (
            tuple(
                name.replace("fir_predicted_", "mlp_predicted_")
                for name in self.REPLAY_CSV_HEADER
            )
            if evidence.model_family == "mlp"
            else self.REPLAY_CSV_HEADER
        )
        for index in range(count):
            internal, actual, predicted, residual, normalized = (
                values[index] for values in matrices
            )
            yield (
                index,
                times[index],
                *internal,
                *actual,
                *predicted,
                *residual,
                *normalized,
                scores[index],
                evidence.threshold,
                ratios[index],
                states[index],
                "true" if index in triggers else "false",
            )

    COLLISION_DETECTION_WINDOW_MS = 150.0
    COLLISION_DETECTION_WINDOW_S = COLLISION_DETECTION_WINDOW_MS / 1000.0
    REQUESTED_HISTORIES_MS = (4, 8, 16, 32)
    RIDGE_ALPHAS = (1e-6, 1e-4, 1e-2, 1.0, 100.0)
    SCALE_METHODS = ("STD", "MAD")
    ROBUST_K_VALUES = (4, 6, 8)
    SCORE_MODES = ("MAX_ABS", "L2_NORM")
    CONFIRMATION_MODES = ("1_OF_1", "2_CONSECUTIVE", "2_OF_3")
    THRESHOLD_STEP = 0.5

    def __init__(
        self,
        history_executor: HistoryExecutionPort | None = None,
        *,
        learning_executor=None,
    ) -> None:
        self._history_executor = history_executor
        self._learning_executor = learning_executor

    def learn_and_qualify(
        self, dataset, numeric_type, progress=None, cancelled=None, *, settings=None
    ):
        if getattr(dataset.recordings[0], "preprocessing", None) is not None:
            from .self_imu import service_for_dataset

            return service_for_dataset(
                dataset,
                history_executor=self._history_executor,
                learning_executor=self._learning_executor,
            ).learn_and_qualify(
                dataset, numeric_type, progress, cancelled, settings=settings
            )
        from .mlp import run_families as run_learning
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
            self, dataset, numeric_type, captured.for_run(), progress, cancelled
        )

    def maximum_taps(self, rate):
        return math.floor(0.128 * rate) + 1

    def evaluate_recording_job(self, job):
        from dual_imu_collision_studio.domain.learning.model import RecordingResult

        recording = job.recording
        if job.config is None:
            scores = self._detector_scores(
                self._target_normalized_residual(
                    recording, job.model, job.numeric_type
                )[0],
                job.model.score_mode,
                job.numeric_type,
            )
            return RecordingResult(job.job_index, scores=scores)
        trace = self._replay_scores(
            job.scores,
            np.asarray(recording.time_s),
            job.config,
            np.asarray(recording.discontinuity_before, dtype=np.bool_),
        )
        return RecordingResult(
            job.job_index,
            metrics=self._recording_qualification(
                recording, trace, job.config.threshold
            ),
        )

    def evaluate_history_job(
        self,
        job: HistoryJob,
        *,
        attempt: int = 1,
        progress: Callable[[HistoryWorkerProgress], None] | None = None,
        cancelled: Callable[[], bool] | None = None,
    ) -> HistoryJobResult:
        publish = progress if progress is not None else lambda _value: None
        is_cancelled = cancelled if cancelled is not None else lambda: False
        started = time.monotonic()
        requested_history_ms = job.history.requested_history_aliases_ms[0]

        def emit(
            stage: str,
            fraction: float,
            message: str,
            current_speed: float | None = None,
            current_offset: float | None = None,
        ) -> None:
            publish(
                HistoryWorkerProgress(
                    job.job_index,
                    requested_history_ms,
                    attempt,
                    stage,
                    fraction,
                    time.monotonic() - started,
                    message,
                    current_speed,
                    current_offset,
                )
            )

        emit("Learning", 0.0, f"Training History {requested_history_ms} ms.")
        missing = self._missing_search_evidence(
            job.dataset, job.active_offsets, job.training_speeds
        )
        if missing:
            emit("Learning", 1.0, missing)
            return HistoryJobResult(
                job.job_index, job.history, (), unavailable_reason=missing
            )
        try:
            selected = self.cross_validate_model_rules(
                job.dataset,
                job.active_offsets,
                job.training_speeds,
                job.history,
                progress=lambda completed, total: emit(
                    "Learning",
                    0.5 * completed / total,
                    f"Training History {requested_history_ms} ms: {completed} of {total} rules.",
                ),
                cancelled=is_cancelled,
            )
            model = self._freeze_model_numeric_type(selected.model, job.numeric_type)
        except InsufficientTrainingEvidence as exc:
            emit(
                "Learning", 1.0, f"History {requested_history_ms} ms unavailable: {exc}"
            )
            return HistoryJobResult(
                job.job_index, job.history, (), unavailable_reason=str(exc)
            )

        score_cache = self._qualification_score_cache(
            job.dataset, model, job.numeric_type
        )
        lower, upper = self._threshold_bounds(
            job.dataset, score_cache, job.active_offsets, job.training_speeds
        )
        thresholds = self._threshold_grid(lower, upper, job.numeric_type)
        if not thresholds:
            cause = (
                "empty threshold range (C < N)"
                if upper < lower
                else "no positive threshold candidates"
            )
            reason = f"History {requested_history_ms} ms: {cause}; N={lower:.17g}, C={upper:.17g}"
            emit("Learning", 1.0, reason)
            return HistoryJobResult(
                job.job_index, job.history, (), unavailable_reason=reason
            )
        candidates: list[QualifiedCandidate] = []
        condition_keys = tuple(
            (speed, offset)
            for speed in job.supplied_speeds
            for offset in job.supplied_offsets
        )
        candidate_count = len(self.CONFIRMATION_MODES) * len(thresholds)
        candidate_index = 0
        for confirmation_mode in self.CONFIRMATION_MODES:
            for threshold in thresholds:
                if is_cancelled():
                    raise InterruptedError("Learning cancelled")
                key = (
                    condition_keys[candidate_index % len(condition_keys)]
                    if condition_keys
                    else (None, None)
                )
                emit(
                    "Qualifying",
                    0.5 + 0.5 * candidate_index / candidate_count,
                    f"Qualifying History {requested_history_ms} ms; N={lower:.9g}, C={upper:.9g}; {candidate_index + 1}/{candidate_count}.",
                    key[0],
                    key[1],
                )
                dtype = self._target_dtype(job.numeric_type)
                config = DetectorConfig(
                    job.numeric_type,
                    model.score_mode,
                    confirmation_mode,
                    float(dtype(threshold)),
                    float(dtype(0.5)),
                    float(dtype(0.050)),
                )
                candidate = self._qualify_model_from_scores(
                    job.dataset,
                    model,
                    config,
                    score_cache,
                    training_speeds=job.training_speeds,
                    active_offsets=job.active_offsets,
                    candidate_id=(
                        f"o{job.outer_round:02d}i{job.inner_round:02d}"
                        f"-t{job.history.tap_count}-c{confirmation_mode}-q{threshold:.17g}"
                    ),
                    stable_order=job.stable_order_base + candidate_index,
                )
                candidates.append(
                    replace(
                        candidate,
                        model=model,
                        history=job.history,
                        detector_config=config,
                        active_offsets=job.active_offsets,
                        excluded_offsets=job.excluded_offsets,
                        outer_round=job.outer_round,
                        inner_round=job.inner_round,
                        cross_validation_fold_count=selected.fold_count,
                        cross_validation_evidence_level=selected.evidence_level,
                        cross_validation_worst_condition_mse=selected.worst_condition_mse,
                        cross_validation_pooled_mse=selected.pooled_mse,
                    )
                )
                candidate_index += 1
        emit("Qualifying", 1.0, f"History {requested_history_ms} ms complete.")
        return HistoryJobResult(job.job_index, job.history, tuple(candidates))

    @staticmethod
    def _missing_search_evidence(dataset, active_offsets, training_speeds) -> str:
        classes = {
            interval.kind
            for recording in dataset.recordings
            if recording.collision_offset_mm in active_offsets
            and recording.robot_speed_mm_s in training_speeds
            for interval in recording.intervals
        }
        missing = [
            kind
            for kind in ("Normal Robot Motion", "Robot Fork Collision")
            if kind not in classes
        ]
        return (
            "Missing threshold-search evidence: " + ", ".join(missing)
            if missing
            else ""
        )

    def _threshold_bounds(
        self, dataset, score_cache, active_offsets, training_speeds
    ) -> tuple[float, float]:
        maxima: dict[str, list[float]] = {
            "Normal Robot Motion": [],
            "Robot Fork Collision": [],
        }
        for recording, scores in zip(dataset.recordings, score_cache, strict=True):
            if (
                recording.collision_offset_mm not in active_offsets
                or recording.robot_speed_mm_s not in training_speeds
            ):
                continue
            times = np.asarray(recording.time_s)
            ignored = np.zeros(len(times), dtype=bool)
            for interval in recording.intervals:
                if interval.kind == "Ignore":
                    ignored[interval.start_index : interval.end_index] = True
            for interval in recording.intervals:
                if interval.kind not in maxima:
                    continue
                start, end = interval.start_index, interval.end_index
                if interval.kind == "Robot Fork Collision":
                    if ignored[start:end].any():
                        raise ValueError("Ignore and Collision annotations overlap")
                    deadline = float(times[start]) + self.COLLISION_DETECTION_WINDOW_S
                    end = int(np.searchsorted(times, deadline + 1e-12, side="right"))
                    breaks = np.flatnonzero(
                        recording.discontinuity_before[start + 1 : end]
                    )
                    if len(breaks):
                        end = start + 1 + int(breaks[0])
                values = scores[start:end][~ignored[start:end]]
                if (
                    recording.preprocessing is not None
                    or recording.training_eligible is not None
                ):
                    values = values[np.isfinite(values)]
                    if not len(values):
                        continue
                if not len(values) or not np.all(np.isfinite(values)):
                    raise ValueError(
                        f"Invalid threshold Score evidence: {recording.recording_id}, {interval.kind}"
                    )
                maxima[interval.kind].append(float(np.max(values)))
        if not all(maxima.values()):
            raise ValueError("threshold bounds require both active evidence classes")
        return max(maxima["Normal Robot Motion"]), min(maxima["Robot Fork Collision"])

    @classmethod
    def _threshold_grid(
        cls, lower: float, upper: float, numeric_type: str
    ) -> tuple[float, ...]:
        if (
            not math.isfinite(lower)
            or not math.isfinite(upper)
            or min(lower, upper) < 0
        ):
            raise ValueError("threshold bounds must be finite nonnegative Scores")
        if upper < lower or upper == 0:
            return ()
        dtype = cls._target_dtype(numeric_type)
        span = (upper - lower) / cls.THRESHOLD_STEP
        if not math.isfinite(span):
            raise ValueError("threshold grid span exceeds numeric range")
        thresholds: list[float] = []
        for index in range(math.floor(span) + 1):
            value = float(dtype(lower + cls.THRESHOLD_STEP * index))
            if 0 < value <= upper and (not thresholds or value != thresholds[-1]):
                thresholds.append(value)
        if not thresholds or thresholds[-1] != upper:
            thresholds.append(upper)
        return tuple(thresholds)

    @classmethod
    def _freeze_model_numeric_type(
        cls, model: FrozenFirModel, numeric_type: str
    ) -> FrozenFirModel:
        dtype = cls._target_dtype(numeric_type)
        return FrozenFirModel(
            model.tap_count,
            np.asarray(model.weights, dtype=dtype),
            np.asarray(model.biases, dtype=dtype),
            float(dtype(model.alpha)),
            np.asarray(model.residual_centers, dtype=dtype),
            np.asarray(model.residual_scales, dtype=dtype),
            model.scale_method,
            model.robust_k,
            model.score_mode,
            model.initial_fit_rows,
            model.refit_rows,
        )

    @staticmethod
    def validate_dataset(dataset: LearningDataset) -> float:
        source_settings = dataset.recordings[0].preprocessing
        if any(r.preprocessing != source_settings for r in dataset.recordings):
            raise ValueError(
                "One Learning run requires one sensor identity and identical preprocessing; do not mix dual and single IMU mappings"
            )
        for recording in dataset.recordings:
            if not all(
                np.all(np.isfinite(v))
                for v in (
                    recording.time_s,
                    recording.internal_imu,
                    recording.external_imu,
                )
                if v is not None
            ):
                raise ValueError("Learning source data must be finite")
            if len(recording.time_s) == 0 or np.any(np.diff(recording.time_s) <= 0):
                raise ValueError("Learning timestamps must be nonempty and increasing")
            if (
                not math.isfinite(recording.sample_rate_hz)
                or recording.sample_rate_hz <= 0
            ):
                raise ValueError("Learning Sample Rate must be finite and positive")
        rates = np.asarray(
            [item.sample_rate_hz for item in dataset.recordings], dtype=np.float64
        )
        session_rate = float(np.median(rates))
        relative_error = np.abs(rates - session_rate) / session_rate
        if np.any(relative_error > 0.005):
            raise ValueError(
                "every Learning recording Sample Rate must be within 0.5% of the session rate: "
                + ", ".join(
                    f"{r.recording_id}={r.sample_rate_hz:g} Hz"
                    for r in dataset.recordings
                )
            )
        return session_rate

    def build_fit_evidence(
        self,
        dataset: LearningDataset,
        active_offsets: tuple[float, ...] | list[float],
        training_speeds: tuple[float, ...] | list[float],
    ) -> FitEvidence:
        self.validate_dataset(dataset)
        groups = tuple(
            CycleFoldGroup(
                recording.recording_id,
                recording.robot_speed_mm_s,
                recording.collision_offset_mm,
                cycle,
            )
            for recording in dataset.recordings
            if recording.collision_offset_mm in active_offsets
            and recording.robot_speed_mm_s in training_speeds
            for cycle in sorted(
                {
                    i.cycle_index
                    for i in recording.intervals
                    if i.cycle_index >= 0
                    and i.kind in {"Normal Robot Motion", "Robot Pick", "Robot Put"}
                }
            )
        )
        try:
            return self._build_group_evidence(dataset, groups)
        except InsufficientTrainingEvidence as exc:
            raise InsufficientTrainingEvidence(
                "no active Cycle-contained Normal, Pick, or Put fit evidence is available"
            ) from exc

    @staticmethod
    def target_predict_rows(weights, biases, features, numeric_type):
        dtype = LearningService._target_dtype(numeric_type)
        x = np.asarray(features, dtype=dtype)
        result = np.broadcast_to(np.asarray(biases, dtype=dtype), (len(x), 3)).copy()
        flat = np.asarray(weights, dtype=dtype).reshape(3, -1)
        # Same input-axis/lag accumulation order and rounding as scalar Replay.
        for column in range(x.shape[1]):
            for axis in range(3):
                result[:, axis] = np.add(
                    result[:, axis],
                    np.multiply(x[:, column], flat[axis, column], dtype=dtype),
                    dtype=dtype,
                )
        if not np.all(np.isfinite(result)):
            raise CandidateNumericalError("Non-finite target prediction")
        return result

    def evaluate_fold_job(self, dataset, job):
        from .optimization import evaluate_fold_job

        return evaluate_fold_job(self, dataset, job)

    @staticmethod
    def aggregate_fold_results(point, folds, settings):
        from .optimization import aggregate_fold_results

        return aggregate_fold_results(point, folds, settings)

    @staticmethod
    def select_fold_kernels(result, settings):
        from .optimization import select_fold_kernels

        return select_fold_kernels(result, settings)

    def search_parameters(
        self, dataset, plan, settings, numeric_type, progress=None, cancelled=None
    ):
        from .optimization import search_parameters

        return search_parameters(
            self, dataset, plan, settings, numeric_type, progress, cancelled
        )

    def evaluate_fixed_parameters(
        self, dataset, plan, settings, numeric_type, progress=None, cancelled=None
    ):
        from .optimization import evaluate_fixed_parameters

        return evaluate_fixed_parameters(
            self, dataset, plan, settings, numeric_type, progress, cancelled
        )

    def build_cross_validation_plan(
        self,
        dataset: LearningDataset,
        active_offsets,
        training_speeds,
        *,
        fold_count: int = 3,
        seed: int = 0,
    ) -> CrossValidationPlan:
        from dual_imu_collision_studio.domain.learning.model import CycleAllocationError
        import random

        if type(fold_count) is not int or not 2 <= fold_count <= 10:
            raise ValueError("N-fold must be an integer from 2 to 10")
        self.validate_dataset(dataset)
        by_condition = {}
        shortages = []
        seen = set()
        for recording in dataset.recordings:
            if (
                recording.collision_offset_mm not in active_offsets
                or recording.robot_speed_mm_s not in training_speeds
            ):
                continue
            if recording.recording_id in seen:
                raise ValueError("Learning recording identity must be unique")
            seen.add(recording.recording_id)
            key = (recording.robot_speed_mm_s, recording.collision_offset_mm)
            cycles = sorted(
                {
                    i.cycle_index
                    for i in recording.intervals
                    if i.cycle_index >= 0
                    and i.kind in {"Normal Robot Motion", "Robot Pick", "Robot Put"}
                }
            )
            if len(cycles) < 2:
                shortages.append(
                    f"{recording.recording_id}: {len(cycles)} valid Cycles, requires at least 2"
                )
            by_condition.setdefault(key, {})[recording.recording_id] = [
                CycleFoldGroup(recording.recording_id, *key, c) for c in cycles
            ]
        for key, recordings in sorted(by_condition.items()):
            total = sum(map(len, recordings.values()))
            if total < fold_count:
                shortages.append(
                    f"{key[0]:g} mm/s @ {key[1]:g} mm: {total} valid Cycles, N={fold_count}"
                )
        if not by_condition:
            shortages.append("no active condition Cycle groups")
        if shortages:
            raise CycleAllocationError(
                "Cycle allocation insufficient: " + "; ".join(shortages)
            )
        rng = random.Random(seed)
        held_out = [[] for _ in range(fold_count)]
        for key, recordings in sorted(by_condition.items()):
            # Consecutive recording blocks distributed cyclically guarantee both
            # global count balance and at least two roles for every recording.
            names = sorted(recordings)
            rng.shuffle(names)
            labels = list(range(fold_count))
            rng.shuffle(labels)
            cursor = 0
            for name in names:
                groups = list(recordings[name])
                rng.shuffle(groups)
                for group in groups:
                    held_out[labels[cursor % fold_count]].append(group)
                    cursor += 1
        folds = tuple(
            CrossValidationFold(
                i + 1,
                tuple(
                    sorted(
                        groups,
                        key=lambda g: (
                            g.robot_speed_mm_s,
                            g.collision_offset_mm,
                            g.recording_id,
                            g.cycle_index,
                        ),
                    )
                ),
            )
            for i, groups in enumerate(held_out)
        )
        return CrossValidationPlan(fold_count, "BALANCED_COMPLETE_CYCLE_FOLDS", folds)

    def cross_validate_model_rules(
        self,
        dataset: LearningDataset,
        active_offsets: tuple[float, ...] | list[float],
        training_speeds: tuple[float, ...] | list[float],
        history: HistorySpec,
        *,
        progress: Callable[[int, int], None] | None = None,
        cancelled: Callable[[], bool] | None = None,
    ) -> CrossValidatedModel:
        publish = progress if progress is not None else lambda _completed, _total: None
        is_cancelled = cancelled if cancelled is not None else lambda: False
        plan = self.build_cross_validation_plan(
            dataset, active_offsets, training_speeds
        )
        all_groups = tuple(
            group for fold in plan.folds for group in fold.held_out_groups
        )
        fold_evidence: list[HistoryFoldEvidence] = []
        for fold in plan.folds:
            held_out_ids = {
                (group.recording_id, group.cycle_index)
                for group in fold.held_out_groups
            }
            training_groups = tuple(
                group
                for group in all_groups
                if (group.recording_id, group.cycle_index) not in held_out_ids
            )
            training = self._build_group_evidence(dataset, training_groups)
            by_condition: dict[tuple[float, float], list[CycleFoldGroup]] = {}
            for group in fold.held_out_groups:
                by_condition.setdefault(
                    (group.robot_speed_mm_s, group.collision_offset_mm), []
                ).append(group)
            held_out_by_condition = tuple(
                (
                    key,
                    self._prepare_fir_matrix(
                        self._build_group_evidence(dataset, tuple(groups)),
                        history.tap_count,
                    ),
                )
                for key, groups in by_condition.items()
            )
            fold_evidence.append(
                HistoryFoldEvidence(
                    self._prepare_fir_matrix(training, history.tap_count),
                    held_out_by_condition,
                )
            )
        final_evidence = self.build_fit_evidence(
            dataset, active_offsets, training_speeds
        )
        final_matrix = self._prepare_fir_matrix(final_evidence, history.tap_count)
        if not len(final_matrix.row_indexes):
            raise InsufficientTrainingEvidence(
                "final Training has no eligible FIR rows"
            )
        for prepared_fold in fold_evidence:
            if not len(prepared_fold.training.row_indexes):
                raise InsufficientTrainingEvidence(
                    "Training fold has no eligible FIR rows"
                )
            if any(
                not len(matrix.row_indexes)
                for _, matrix in prepared_fold.held_out_by_condition
            ):
                raise InsufficientTrainingEvidence(
                    "held-out Cycle has no eligible FIR rows"
                )
        ranked: list[tuple[float, float, int, tuple[float, str, int, str]]] = []
        stable_order = 0
        rule_count = (
            len(self.RIDGE_ALPHAS)
            * len(self.SCALE_METHODS)
            * len(self.ROBUST_K_VALUES)
            * len(self.SCORE_MODES)
        )
        for alpha in self.RIDGE_ALPHAS:
            for scale_method in self.SCALE_METHODS:
                for robust_k in self.ROBUST_K_VALUES:
                    for score_mode in self.SCORE_MODES:
                        if is_cancelled():
                            raise InterruptedError("Learning cancelled")
                        condition_sse: dict[tuple[float, float], float] = {}
                        condition_rows: dict[tuple[float, float], int] = {}
                        for prepared_fold in fold_evidence:
                            fold_model = self._fit_mimo_fir_matrix(
                                prepared_fold.training,
                                history.tap_count,
                                alpha,
                                scale_method,
                                robust_k,
                                score_mode,
                            )
                            for key, held_out in prepared_fold.held_out_by_condition:
                                predicted = self._predict_rows(
                                    fold_model.weights,
                                    fold_model.biases,
                                    held_out.features,
                                )
                                error = held_out.targets - predicted
                                condition_sse[key] = condition_sse.get(
                                    key, 0.0
                                ) + float(np.sum(error**2))
                                condition_rows[key] = condition_rows.get(key, 0) + int(
                                    error.size
                                )
                        if condition_rows:
                            losses = {
                                key: condition_sse[key] / count
                                for key, count in condition_rows.items()
                            }
                            total_rows = sum(condition_rows.values())
                            ranked.append(
                                (
                                    max(losses.values()),
                                    sum(condition_sse.values()) / total_rows,
                                    stable_order,
                                    (alpha, scale_method, robust_k, score_mode),
                                )
                            )
                        stable_order += 1
                        publish(stable_order, rule_count)
        if not ranked:
            raise ValueError(
                "no model rule combination completed grouped cross-validation"
            )
        worst_mse, pooled_mse, selected_order, rules = min(
            ranked, key=lambda item: (item[0], item[1], item[2])
        )
        alpha, scale_method, robust_k, score_mode = rules
        final_model = self._fit_mimo_fir_matrix(
            final_matrix,
            history.tap_count,
            alpha,
            scale_method,
            robust_k,
            score_mode,
        )
        return CrossValidatedModel(
            final_model,
            history,
            plan.fold_count,
            plan.evidence_level,
            worst_mse,
            pooled_mse,
            selected_order,
        )

    @staticmethod
    def _build_group_evidence(
        dataset: LearningDataset,
        groups: tuple[CycleFoldGroup, ...],
    ) -> FitEvidence:
        selected = {(group.recording_id, group.cycle_index) for group in groups}
        internal_parts: list[np.ndarray] = []
        external_parts: list[np.ndarray] = []
        segment_parts: list[np.ndarray] = []
        selected_recordings: set[str] = set()
        segment_id = -1
        interval_count = 0
        for recording in dataset.recordings:
            internal = np.asarray(recording.internal_imu)
            external = np.asarray(recording.external_imu)
            discontinuities = np.asarray(recording.discontinuity_before, dtype=np.bool_)
            eligible = np.zeros(len(internal), dtype=np.bool_)
            eligible_cycle = np.full(len(internal), -1, dtype=np.int64)
            for interval in recording.intervals:
                if (
                    interval.kind
                    not in {"Normal Robot Motion", "Robot Pick", "Robot Put"}
                    or (recording.recording_id, interval.cycle_index) not in selected
                ):
                    continue
                eligible[interval.start_index : interval.end_index] = True
                eligible_cycle[interval.start_index : interval.end_index] = (
                    interval.cycle_index
                )
                interval_count += 1
            for excluded in recording.intervals:
                if excluded.kind in {"Ignore", "Robot Fork Collision"}:
                    eligible[excluded.start_index : excluded.end_index] = False
            if recording.prepared_self:
                raw_eligible = eligible.copy()
                eligible[0] = False
                eligible[1:] &= raw_eligible[:-1] & (
                    eligible_cycle[1:] == eligible_cycle[:-1]
                )
            if recording.training_eligible is not None:
                eligible &= np.asarray(recording.training_eligible, dtype=bool)
            if not eligible.any():
                continue
            selected_recordings.add(recording.recording_id)
            selected_indexes = np.flatnonzero(eligible)
            selected_segments = np.empty(len(selected_indexes), dtype=np.int64)
            previous_index = -2
            previous_cycle = -1
            for output_index, source_index in enumerate(selected_indexes):
                cycle = int(eligible_cycle[source_index])
                if (
                    source_index != previous_index + 1
                    or cycle != previous_cycle
                    or bool(discontinuities[source_index])
                ):
                    segment_id += 1
                selected_segments[output_index] = segment_id
                previous_index = int(source_index)
                previous_cycle = cycle
            internal_parts.append(internal[selected_indexes])
            external_parts.append(external[selected_indexes])
            segment_parts.append(selected_segments)
        if not internal_parts:
            raise InsufficientTrainingEvidence(
                "no selected Cycle evidence is available"
            )
        return FitEvidence(
            np.concatenate(internal_parts),
            np.concatenate(external_parts),
            np.concatenate(segment_parts),
            len(selected_recordings),
            interval_count,
        )

    @staticmethod
    def retain_round_winner(
        result: QualificationResult, winner: QualifiedCandidate
    ) -> QualificationResult:
        if any(item.candidate_id == winner.candidate_id for item in result.candidates):
            raise ValueError(
                "each retained round winner requires a unique candidate id"
            )
        return replace(
            result, candidates=result.candidates + (winner,), diagnostic_candidates=()
        )

    @staticmethod
    def initial_fallback_state(
        offsets: list[float] | tuple[float, ...],
        speeds: list[float] | tuple[float, ...],
    ) -> FallbackState:
        active_offsets = tuple(sorted(set(float(value) for value in offsets)))
        training_speeds = tuple(sorted(set(float(value) for value in speeds)))
        if not active_offsets:
            raise ValueError("at least one Collision Offset is required")
        if not training_speeds or training_speeds[0] <= 0:
            raise ValueError("at least one positive Robot Speed is required")
        return FallbackState(active_offsets, (), training_speeds)

    @staticmethod
    def advance_fallback(
        state: FallbackState,
        winner: QualifiedCandidate,
        supplied_speeds: list[float] | tuple[float, ...],
    ) -> FallbackTransition:
        if winner.training_speeds != state.training_speeds:
            raise ValueError(
                "winner Training speed range must match the current fallback state"
            )
        evidence = {
            item.collision_offset_mm: item for item in winner.offset_qualifications
        }
        missing = [offset for offset in state.active_offsets if offset not in evidence]
        if missing:
            raise ValueError("every active offset requires Qualification evidence")
        expected_suffix = (
            state.training_speeds[
                len(state.training_speeds) - len(winner.passing_speeds) :
            ]
            if winner.passing_speeds
            else ()
        )
        if winner.passing_speeds != expected_suffix:
            raise ValueError(
                "winner passing speeds must be a suffix of the current Training range"
            )
        range_matches = winner.training_speeds == winner.passing_speeds
        next_state = LearningService._next_fallback_state(
            state, supplied_speeds, range_matches
        )
        if next_state is None:
            action = (
                FallbackAction.STOP_RANGE_MATCH
                if range_matches
                else FallbackAction.EXHAUSTED
            )
        elif next_state.outer_round == state.outer_round:
            action = FallbackAction.REDUCE_SPEED
        else:
            action = FallbackAction.EXCLUDE_OFFSET
        return FallbackTransition(winner, action, next_state)

    @staticmethod
    def _next_fallback_state(
        state: FallbackState,
        supplied_speeds: list[float] | tuple[float, ...],
        range_matches: bool,
    ) -> FallbackState | None:
        if not range_matches and len(state.training_speeds) > 1:
            return FallbackState(
                state.active_offsets,
                state.excluded_offsets,
                state.training_speeds[1:],
                state.outer_round,
                state.inner_round + 1,
            )
        # Complete this pooled-offset envelope before narrowing its coverage.
        # Detectability never bypasses a required speed-suffix refit.
        excluded_now = min(state.active_offsets)
        remaining = tuple(
            offset for offset in state.active_offsets if offset != excluded_now
        )
        if not remaining:
            return None
        return FallbackState(
            remaining,
            tuple(sorted(set(state.excluded_offsets + (excluded_now,)))),
            tuple(sorted(set(float(value) for value in supplied_speeds))),
            state.outer_round + 1,
            1,
        )

    @staticmethod
    def common_passing_suffix(
        per_offset_passing_speeds: tuple[tuple[float, ...], ...],
        supplied_speeds: list[float] | tuple[float, ...],
    ) -> tuple[float, ...]:
        if not per_offset_passing_speeds:
            raise ValueError("at least one active Offset is required")
        supplied = tuple(sorted(set(float(value) for value in supplied_speeds)))
        common = set(supplied)
        for values in per_offset_passing_speeds:
            common &= set(float(value) for value in values)
        start = len(supplied)
        while start > 0 and supplied[start - 1] in common:
            start -= 1
        return supplied[start:]

    @staticmethod
    def build_speed_rounds(
        speeds: list[float] | tuple[float, ...],
    ) -> tuple[tuple[float, ...], ...]:
        ordered = tuple(sorted(set(float(speed) for speed in speeds)))
        if not ordered or ordered[0] <= 0:
            raise ValueError("at least one positive Robot Speed is required")
        return tuple(ordered[index:] for index in range(len(ordered)))

    @staticmethod
    def select_winner(
        candidates: list[QualifiedCandidate] | tuple[QualifiedCandidate, ...],
        supplied_speeds: tuple[float, ...],
    ) -> QualifiedCandidate:
        supplied = tuple(sorted(set(supplied_speeds)))
        if not candidates:
            raise ValueError("at least one qualified candidate is required")
        for candidate in candidates:
            expected_suffix = (
                supplied[len(supplied) - len(candidate.passing_speeds) :]
                if candidate.passing_speeds
                else ()
            )
            if candidate.passing_speeds != expected_suffix:
                raise ValueError(
                    "passing speeds must be a contiguous high-speed suffix"
                )
            if (
                candidate.passing_speeds
                and candidate.worst_latency_ms
                > LearningService.COLLISION_DETECTION_WINDOW_MS
            ):
                raise ValueError(
                    "a passing candidate cannot exceed 150 ms collision latency"
                )
        return min(
            candidates,
            key=LearningService._candidate_rank,
        )

    @staticmethod
    def _candidate_rank(
        item: QualifiedCandidate,
    ) -> tuple[int, int, int, float, float, int]:
        return (
            -len(item.passing_speeds),
            -len(item.active_offsets),
            item.tap_count,
            item.worst_latency_ms,
            -item.robustness_margin,
            item.stable_order,
        )

    @staticmethod
    def rank_qualified_candidates(
        candidates: list[QualifiedCandidate] | tuple[QualifiedCandidate, ...],
        supplied_speeds: tuple[float, ...],
    ) -> tuple[QualifiedCandidate, ...]:
        qualified = tuple(
            item
            for item in candidates
            if item.passing_speeds and LearningService.round_can_stop(item)
        )
        if qualified:
            # Apply the same suffix and latency checks used for round selection.
            LearningService.select_winner(qualified, supplied_speeds)
        return tuple(sorted(qualified, key=LearningService._candidate_rank))

    @staticmethod
    def round_can_stop(winner: QualifiedCandidate) -> bool:
        return winner.training_speeds == winner.passing_speeds

    def qualify_model(
        self,
        dataset: LearningDataset,
        model: FrozenFirModel,
        config: DetectorConfig,
        *,
        training_speeds: tuple[float, ...],
        active_offsets: tuple[float, ...],
        candidate_id: str,
        stable_order: int,
    ) -> QualifiedCandidate:
        self.validate_dataset(dataset)
        if model.score_mode != config.score_mode:
            raise ValueError("frozen model and detector Score Mode must match")
        supplied_speeds = tuple(
            sorted({item.robot_speed_mm_s for item in dataset.recordings})
        )
        supplied_offsets = tuple(
            sorted({item.collision_offset_mm for item in dataset.recordings})
        )
        if not set(training_speeds).issubset(supplied_speeds):
            raise ValueError("Training speeds must come from supplied recordings")
        if not set(active_offsets).issubset(supplied_offsets):
            raise ValueError("active Offsets must come from supplied recordings")
        score_cache = self._qualification_score_cache(
            dataset, model, config.numeric_type
        )
        return self._qualify_model_from_scores(
            dataset,
            model,
            config,
            score_cache,
            training_speeds=training_speeds,
            active_offsets=active_offsets,
            candidate_id=candidate_id,
            stable_order=stable_order,
        )

    def _qualify_model_from_scores(
        self,
        dataset: LearningDataset,
        model: FrozenFirModel,
        config: DetectorConfig,
        score_cache: tuple[np.ndarray, ...],
        *,
        training_speeds: tuple[float, ...],
        active_offsets: tuple[float, ...],
        candidate_id: str,
        stable_order: int,
        recording_metrics=None,
    ) -> QualifiedCandidate:
        """Replay a cache produced in this method's immediate caller scope."""
        if len(score_cache) != len(dataset.recordings):
            raise ValueError("Qualification score cache must match supplied recordings")
        supplied_speeds = tuple(
            sorted({item.robot_speed_mm_s for item in dataset.recordings})
        )
        supplied_offsets = tuple(
            sorted({item.collision_offset_mm for item in dataset.recordings})
        )

        grouped: dict[tuple[float, float], list[dict[str, object]]] = {}
        per_recording: list[RecordingQualification] = []
        if recording_metrics is not None and len(recording_metrics) != len(
            dataset.recordings
        ):
            raise ValueError("Recording metrics must cover all supplied recordings")
        for index, (recording, scores) in enumerate(
            zip(dataset.recordings, score_cache, strict=True)
        ):
            key = (recording.robot_speed_mm_s, recording.collision_offset_mm)
            if recording_metrics is None:
                trace = self._replay_scores(
                    scores,
                    np.asarray(recording.time_s),
                    config,
                    np.asarray(recording.discontinuity_before, dtype=np.bool_),
                )
                metrics = self._recording_qualification(
                    recording, trace, config.threshold
                )
            else:
                metrics = recording_metrics[index]
            grouped.setdefault(key, []).append(metrics)
            per_recording.append(self._recording_result(recording, metrics))

        conditions = tuple(
            self._combine_condition(key, rows)
            for key, rows in sorted(grouped.items(), key=lambda item: item[0])
        )
        by_key = {
            (item.robot_speed_mm_s, item.collision_offset_mm): item
            for item in conditions
        }
        offset_evidence: list[OffsetQualification] = []
        for offset in supplied_offsets:
            passing = tuple(
                speed
                for speed in supplied_speeds
                if (row := by_key.get((speed, offset))) is not None
                and row.status == "PASS"
            )
            detectable = tuple(
                speed
                for speed in supplied_speeds
                if (row := by_key.get((speed, offset))) is not None
                and row.collision_interval_count > 0
                and row.collision_detected_count == row.collision_interval_count
                and row.worst_collision_latency_ms is not None
                and row.worst_collision_latency_ms <= self.COLLISION_DETECTION_WINDOW_MS
            )
            offset_evidence.append(OffsetQualification(offset, passing, detectable))
        passing_by_training_speed = tuple(
            speed
            for speed in training_speeds
            if (
                rows := [
                    item
                    for item in conditions
                    if item.robot_speed_mm_s == speed
                    and item.collision_offset_mm in active_offsets
                ]
            )
            and all(item.status == "PASS" for item in rows)
        )
        common_suffix = self.common_passing_suffix(
            (passing_by_training_speed,), training_speeds
        )
        in_range = [
            item
            for item in conditions
            if item.collision_offset_mm in active_offsets
            and item.robot_speed_mm_s in common_suffix
        ]
        latencies = [
            item.worst_collision_latency_ms
            for item in in_range
            if item.worst_collision_latency_ms is not None
        ]
        false_margins = [
            float(row["false_margin"])
            for (speed, offset), rows in grouped.items()
            if speed in common_suffix and offset in active_offsets
            for row in rows
        ]
        collision_margins = [
            float(row["collision_margin"])
            for (speed, offset), rows in grouped.items()
            if speed in common_suffix and offset in active_offsets
            for row in rows
        ]
        false_margin = min(false_margins) if false_margins else float("-inf")
        collision_margin = (
            min(collision_margins) if collision_margins else float("-inf")
        )
        false_trigger_count = sum(
            item.normal_false_events + item.pick_false_events + item.put_false_events
            for item in conditions
        )
        collision_interval_count = sum(
            item.collision_interval_count for item in conditions
        )
        collision_detected_count = sum(
            item.collision_detected_count for item in conditions
        )
        missed_collision_count = collision_interval_count - collision_detected_count
        diagnostic_latencies = [
            item.worst_collision_latency_ms
            for item in conditions
            if item.worst_collision_latency_ms is not None
        ]
        return QualifiedCandidate(
            candidate_id=candidate_id,
            training_speeds=tuple(training_speeds),
            passing_speeds=common_suffix,
            tap_count=model.tap_count,
            worst_latency_ms=max(latencies) if latencies else float("inf"),
            robustness_margin=min(false_margin, collision_margin),
            stable_order=stable_order,
            offset_qualifications=tuple(offset_evidence),
            conditions=conditions,
            false_trigger_robustness_margin=false_margin,
            collision_detection_robustness_margin=collision_margin,
            total_misjudgments=false_trigger_count + missed_collision_count,
            false_trigger_count=false_trigger_count,
            missed_collision_count=missed_collision_count,
            collision_detected_count=collision_detected_count,
            collision_interval_count=collision_interval_count,
            diagnostic_worst_latency_ms=max(diagnostic_latencies)
            if diagnostic_latencies
            else None,
            recording_qualifications=tuple(per_recording),
        )

    @staticmethod
    def _qualification_status(
        collision_count: int,
        normal_false: int,
        pick_false: int,
        put_false: int,
        detected: int,
        worst_latency_ms: float | None,
    ) -> str:
        passes = (
            collision_count > 0
            and normal_false == pick_false == put_false == 0
            and detected == collision_count
            and worst_latency_ms is not None
            and worst_latency_ms <= LearningService.COLLISION_DETECTION_WINDOW_MS + 1e-9
        )
        return "PASS" if passes else "COVERAGE_GAP" if collision_count <= 0 else "FAIL"

    @staticmethod
    def _recording_result(recording, metrics) -> RecordingQualification:
        latency = float(metrics["worst_latency"])
        finite_latency = latency if np.isfinite(latency) else None
        status = LearningService._qualification_status(
            int(metrics["collision_count"]),
            int(metrics["normal_false"]),
            int(metrics["pick_false"]),
            int(metrics["put_false"]),
            int(metrics["detected"]),
            finite_latency,
        )
        if metrics.get("coverage_gap", False):
            status = "COVERAGE_GAP"
        return RecordingQualification(
            recording.recording_id,
            recording.robot_speed_mm_s,
            recording.collision_offset_mm,
            int(metrics["normal_false"]),
            int(metrics["pick_false"]),
            int(metrics["put_false"]),
            int(metrics["detected"]),
            int(metrics["collision_count"]),
            finite_latency,
            status,
            tuple(metrics["collision_snrs_db"]),
        )

    @staticmethod
    def rank_diagnostic_candidates(
        candidates: tuple[QualifiedCandidate, ...] | list[QualifiedCandidate],
    ) -> tuple[QualifiedCandidate, ...]:
        enriched: list[QualifiedCandidate] = []
        for candidate in candidates:
            false_count = sum(
                row.normal_false_events + row.pick_false_events + row.put_false_events
                for row in candidate.conditions
            )
            collision_total = sum(
                row.collision_interval_count for row in candidate.conditions
            )
            collision_detected = sum(
                row.collision_detected_count for row in candidate.conditions
            )
            missed = collision_total - collision_detected
            latencies = [
                row.worst_collision_latency_ms
                for row in candidate.conditions
                if row.worst_collision_latency_ms is not None
            ]
            enriched.append(
                replace(
                    candidate,
                    total_misjudgments=false_count + missed,
                    false_trigger_count=false_count,
                    missed_collision_count=missed,
                    collision_detected_count=collision_detected,
                    collision_interval_count=collision_total,
                    diagnostic_worst_latency_ms=max(latencies) if latencies else None,
                )
            )
        if not enriched:
            return ()
        minimum_errors = min(item.total_misjudgments for item in enriched)
        minimum = [
            item for item in enriched if item.total_misjudgments == minimum_errors
        ]
        finite = [
            item.diagnostic_worst_latency_ms
            for item in minimum
            if item.diagnostic_worst_latency_ms is not None
            and math.isfinite(item.diagnostic_worst_latency_ms)
        ]
        if finite:
            best_latency = min(finite)
            minimum = [
                item
                for item in minimum
                if item.diagnostic_worst_latency_ms == best_latency
            ]
        return tuple(sorted(minimum, key=lambda item: item.stable_order))

    def _qualification_score_cache(
        self,
        dataset: LearningDataset,
        model: FrozenFirModel,
        numeric_type: str,
    ) -> tuple[np.ndarray, ...]:
        cache = tuple(
            self._detector_scores(
                self._target_normalized_residual(
                    recording,
                    model,
                    numeric_type,
                )[0],
                model.score_mode,
                numeric_type,
            )
            for recording in dataset.recordings
        )
        if not getattr(model, "preprocessing", None) and any(
            not np.all(
                np.isfinite(
                    scores[self._source_score_ready(recording, model.tap_count)]
                )
            )
            for recording, scores in zip(dataset.recordings, cache)
        ):
            raise ValueError("Qualification Score is non-finite in target arithmetic")
        return cache

    @staticmethod
    def _recording_qualification(
        recording, trace: DetectorTrace, threshold: float
    ) -> dict[str, object]:
        triggers = tuple(trace.trigger_indices)
        counts = {
            "Normal Robot Motion": 0,
            "Robot Pick": 0,
            "Robot Put": 0,
            "Robot Fork Collision": 0,
        }
        false_events = {"Normal Robot Motion": 0, "Robot Pick": 0, "Robot Put": 0}
        detected = 0
        latencies: list[float] = []
        false_scores: list[float] = []
        collision_margins: list[float] = []
        times = np.asarray(recording.time_s, dtype=np.float64)
        scores = np.asarray(trace.scores, dtype=np.float64)
        collision_acceptance = np.zeros(len(times), dtype=np.bool_)
        collision_interval_mask = np.zeros(len(times), dtype=np.bool_)
        ignore_mask = np.zeros(len(times), dtype=np.bool_)
        false_class = np.ones(len(times), dtype=np.int8)
        for interval in recording.intervals:
            support = slice(interval.start_index, interval.end_index)
            if interval.kind == "Ignore":
                ignore_mask[support] = True
            elif interval.kind == "Robot Fork Collision":
                collision_interval_mask[support] = True
            elif interval.kind == "Robot Pick":
                false_class[support] = 2
            elif interval.kind == "Robot Put":
                false_class[support] = 3
        for collision in recording.intervals:
            if collision.kind != "Robot Fork Collision":
                continue
            deadline = (
                float(times[collision.start_index])
                + LearningService.COLLISION_DETECTION_WINDOW_S
            )
            for index in range(collision.start_index, len(times)):
                if index > collision.start_index and bool(
                    recording.discontinuity_before[index]
                ):
                    break
                if float(times[index]) > deadline + 1e-12:
                    break
                collision_acceptance[index] = True
        noise_scores = scores[
            np.isfinite(scores) & ~collision_interval_mask & ~ignore_mask
        ]
        noise_rms = (
            float(np.sqrt(np.mean(np.square(noise_scores, dtype=np.float64))))
            if noise_scores.size
            else None
        )
        collision_snrs_db: list[float | None] = []
        coverage_gap = False
        collisions = sorted(
            (
                interval
                for interval in recording.intervals
                if interval.kind == "Robot Fork Collision"
            ),
            key=lambda interval: (interval.start_index, interval.end_index),
        )
        for collision in collisions:
            deadline = (
                float(times[collision.start_index])
                + LearningService.COLLISION_DETECTION_WINDOW_S
            )
            response_scores: list[float] = []
            for index in range(collision.start_index, len(times)):
                if index > collision.start_index and bool(
                    recording.discontinuity_before[index]
                ):
                    break
                if float(times[index]) > deadline + 1e-12:
                    break
                if not bool(ignore_mask[index]) and math.isfinite(float(scores[index])):
                    response_scores.append(float(scores[index]))
            if (
                recording.preprocessing is not None
                or recording.training_eligible is not None
            ) and not response_scores:
                coverage_gap = True
            signal_peak = max(response_scores) if response_scores else None
            if (
                signal_peak is None
                or noise_rms is None
                or not math.isfinite(signal_peak)
                or not math.isfinite(noise_rms)
                or signal_peak <= 0.0
                or noise_rms <= 0.0
            ):
                collision_snrs_db.append(None)
                continue
            snr_db = 20.0 * math.log10(signal_peak / noise_rms)
            collision_snrs_db.append(snr_db if math.isfinite(snr_db) else None)
        false_class[ignore_mask | collision_acceptance] = 0
        valid_cycles = {
            interval.cycle_index
            for interval in recording.intervals
            if interval.kind != "Ignore" and interval.cycle_index >= 0
        }
        for interval in recording.intervals:
            if interval.kind not in counts:
                continue
            counts[interval.kind] += 1
            if interval.kind != "Robot Fork Collision":
                continue
            start_time = float(times[interval.start_index])
            deadline = start_time + LearningService.COLLISION_DETECTION_WINDOW_S
            # Collision annotations identify the onset, but their manually selected
            # end may be shorter than the detector's 150 ms response window.
            eligible = [
                index
                for index in triggers
                if interval.start_index <= index
                and float(times[index]) <= deadline + 1e-12
                and bool(collision_acceptance[index])
                and not bool(ignore_mask[index])
            ]
            if eligible:
                trigger = eligible[0]
                detected += 1
                latency_ms = 1000.0 * (float(times[trigger]) - start_time)
                if (
                    abs(latency_ms - LearningService.COLLISION_DETECTION_WINDOW_MS)
                    <= 1e-9
                ):
                    latency_ms = LearningService.COLLISION_DETECTION_WINDOW_MS
                latencies.append(latency_ms)
                collision_margins.append(float(trace.scores[trigger]) - threshold)
        for index in triggers:
            category = int(false_class[index])
            if category == 1:
                false_events["Normal Robot Motion"] += 1
            elif category == 2:
                false_events["Robot Pick"] += 1
            elif category == 3:
                false_events["Robot Put"] += 1
        false_scores.extend(
            float(trace.scores[index])
            for index, category in enumerate(false_class)
            if category > 0 and np.isfinite(trace.scores[index])
        )
        false_margin = threshold - max(false_scores, default=0.0)
        collision_margin = min(collision_margins, default=float("-inf"))
        return {
            "coverage_gap": coverage_gap,
            "recording_count": 1,
            "cycle_count": len(valid_cycles),
            "normal_count": counts["Normal Robot Motion"],
            "pick_count": counts["Robot Pick"],
            "put_count": counts["Robot Put"],
            "collision_count": counts["Robot Fork Collision"],
            "normal_false": false_events["Normal Robot Motion"],
            "pick_false": false_events["Robot Pick"],
            "put_false": false_events["Robot Put"],
            "detected": detected,
            "worst_latency": max(latencies) if latencies else float("nan"),
            "combined_margin": min(false_margin, collision_margin),
            "false_margin": false_margin,
            "collision_margin": collision_margin,
            "collision_snrs_db": tuple(collision_snrs_db),
        }

    @staticmethod
    def _combine_condition(
        key: tuple[float, float], rows: list[dict[str, object]]
    ) -> ConditionQualification:
        names = (
            "recording_count",
            "cycle_count",
            "normal_count",
            "pick_count",
            "put_count",
            "collision_count",
            "normal_false",
            "pick_false",
            "put_false",
            "detected",
        )
        totals = {name: sum(int(row[name]) for row in rows) for name in names}
        latencies = [
            float(row["worst_latency"])
            for row in rows
            if np.isfinite(float(row["worst_latency"]))
        ]
        worst_latency = max(latencies) if latencies else None
        status = LearningService._qualification_status(
            totals["collision_count"],
            totals["normal_false"],
            totals["pick_false"],
            totals["put_false"],
            totals["detected"],
            worst_latency,
        )
        if any(row.get("coverage_gap", False) for row in rows):
            status = "COVERAGE_GAP"
        return ConditionQualification(
            key[0],
            key[1],
            totals["recording_count"],
            totals["cycle_count"],
            totals["normal_count"],
            totals["pick_count"],
            totals["put_count"],
            totals["collision_count"],
            totals["normal_false"],
            totals["pick_false"],
            totals["put_false"],
            totals["detected"],
            worst_latency,
            status,
        )

    @staticmethod
    def _target_normalized_residual(
        recording, model: FrozenFirModel, numeric_type: str
    ) -> tuple[np.ndarray, np.ndarray]:
        _, _, normalized, reset_before = LearningService._target_replay_arrays(
            recording,
            model,
            numeric_type,
        )
        return normalized, reset_before

    @staticmethod
    def _target_replay_arrays(
        recording, model: FrozenFirModel, numeric_type: str
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        from .self_imu import FrozenSelfImuModel, replay_arrays as self_replay_arrays

        if isinstance(model, FrozenSelfImuModel):
            return self_replay_arrays(recording, model, numeric_type)
        if isinstance(model, FrozenMlpModel):
            from .mlp import replay_arrays

            arrays = replay_arrays(recording, model, numeric_type)
            ready = LearningService._source_score_ready(recording, model.tap_count)
            arrays[2][~ready] = np.nan
            return arrays
        dtype = LearningService._target_dtype(numeric_type)
        internal = np.asarray(recording.internal_imu, dtype=dtype)
        external = np.asarray(recording.external_imu, dtype=dtype)
        count = len(internal)
        predicted_external = np.empty((count, 3), dtype=dtype)
        residual_values = np.empty((count, 3), dtype=dtype)
        normalized = np.empty((count, 3), dtype=dtype)
        reset_before = np.asarray(recording.discontinuity_before, dtype=np.bool_).copy()
        if count:
            reset_before[0] = True
        segment_start = 0
        for index in range(count):
            if reset_before[index]:
                segment_start = index
            for output_axis in range(3):
                predicted = dtype(model.biases[output_axis])
                for input_axis in range(3):
                    for lag in range(model.tap_count):
                        product = dtype(
                            dtype(model.weights[output_axis, input_axis, lag])
                            * (
                                dtype(internal[index - lag, input_axis])
                                if index - lag >= segment_start
                                else dtype(0)
                            )
                        )
                        predicted = dtype(predicted + product)
                predicted_external[index, output_axis] = predicted
                residual = dtype(dtype(external[index, output_axis]) - predicted)
                residual_values[index, output_axis] = residual
                centered = dtype(residual - dtype(model.residual_centers[output_axis]))
                normalized[index, output_axis] = dtype(
                    centered / dtype(model.residual_scales[output_axis])
                )
        if not all(
            np.all(np.isfinite(values))
            for values in (predicted_external, residual_values, normalized)
        ):
            raise ValueError(
                "FIR replay produced non-finite values in target arithmetic"
            )
        normalized[~LearningService._source_score_ready(recording, model.tap_count)] = (
            np.nan
        )
        return predicted_external, residual_values, normalized, reset_before

    @staticmethod
    def _source_score_ready(recording, tap_count):
        eligible = recording.training_eligible
        if eligible is None or np.all(eligible):
            return np.ones(len(recording.time_s), dtype=bool)
        ready = np.zeros(len(recording.time_s), dtype=bool)
        history = 0
        for index, usable in enumerate(eligible):
            if recording.discontinuity_before[index] or not usable:
                history = 0
            if usable:
                history += 1
            ready[index] = history >= tap_count
        return ready

    def replay_candidate(
        self,
        recording,
        candidate: QualifiedCandidate,
        *,
        cycle_index: int = -1,
        event_kind: str = "",
        event_ordinal: int = -1,
    ) -> ReplayEvidence:
        if candidate.model is None or candidate.detector_config is None:
            raise ValueError("selected retained candidate has no frozen Replay model")
        if getattr(candidate.model, "preprocessing", None) is not None:
            from .self_imu import prepare_recording

            recording = prepare_recording(recording, candidate.model.preprocessing)
        event = None
        if cycle_index >= 0 or event_kind or event_ordinal >= 0:
            matches = tuple(
                interval
                for interval in recording.intervals
                if interval.cycle_index == cycle_index and interval.kind == event_kind
            )
            if not 0 <= event_ordinal < len(matches):
                raise ValueError("selected Replay event does not exist")
            event = matches[event_ordinal]
        times = np.asarray(recording.time_s, dtype=np.float64)
        predicted, residual, normalized, reset_before = self._target_replay_arrays(
            recording,
            candidate.model,
            candidate.detector_config.numeric_type,
        )
        trace = self.replay_detector(
            normalized, times, candidate.detector_config, reset_before
        )
        latency: float | None = None
        if event is not None and event.kind == "Robot Fork Collision":
            start_time = float(times[event.start_index])
            deadline = start_time + self.COLLISION_DETECTION_WINDOW_S
            ignored = np.zeros(len(times), dtype=bool)
            for interval in recording.intervals:
                if interval.kind == "Ignore":
                    ignored[interval.start_index : interval.end_index] = True
            eligible = tuple(
                index
                for index in trace.trigger_indices
                if index >= event.start_index
                and float(times[index]) <= deadline + 1e-12
                and not bool(ignored[index])
            )
            if eligible:
                latency = 1000.0 * (float(times[eligible[0]]) - start_time)
                if abs(latency - self.COLLISION_DETECTION_WINDOW_MS) <= 1e-9:
                    latency = self.COLLISION_DETECTION_WINDOW_MS
        return ReplayEvidence(
            candidate.candidate_id,
            recording.recording_id,
            cycle_index,
            event_kind,
            event_ordinal,
            times,
            np.asarray(recording.internal_imu),
            np.asarray(recording.external_imu),
            predicted,
            residual,
            normalized,
            trace,
            candidate.detector_config.threshold,
            event.start_index if event is not None else 0,
            event.end_index if event is not None else 0,
            latency,
            "self_ridge"
            if getattr(candidate.model, "preprocessing", None)
            else ("mlp" if isinstance(candidate.model, FrozenMlpModel) else "fir"),
        )

    def fit_mimo_fir(
        self,
        internal_imu: np.ndarray,
        external_imu: np.ndarray,
        segment_ids: np.ndarray,
        tap_count: int,
        alpha: float,
        scale_method: str,
        robust_k: int,
        score_mode: str,
    ) -> FrozenFirModel:
        matrix = FirMatrixEvidence(
            *self._fir_rows(internal_imu, external_imu, segment_ids, tap_count)
        )
        return self._fit_mimo_fir_matrix(
            matrix, tap_count, alpha, scale_method, robust_k, score_mode
        )

    @classmethod
    def _prepare_fir_matrix(
        cls, evidence: FitEvidence, tap_count: int
    ) -> FirMatrixEvidence:
        return FirMatrixEvidence(
            *cls._fir_rows(
                evidence.internal_imu,
                evidence.external_imu,
                evidence.segment_ids,
                tap_count,
            )
        )

    def _fit_mimo_fir_matrix(
        self,
        matrix: FirMatrixEvidence,
        tap_count: int,
        alpha: float,
        scale_method: str,
        robust_k: int,
        score_mode: str,
        *,
        use_robust_refit: bool = True,
        numeric_type: str | None = None,
    ) -> FrozenFirModel:
        features = np.asarray(matrix.features)
        targets = np.asarray(matrix.targets)
        row_indexes = np.asarray(matrix.row_indexes)
        if len(features) == 0:
            raise ValueError("no eligible FIR rows remain")
        weights, biases = self._ridge_source_scale(features, targets, tap_count, alpha)
        retained = np.ones(len(features), dtype=np.bool_)
        if use_robust_refit:
            residual = targets - self._predict_rows(weights, biases, features)
            centers, scales = self._residual_scale(residual, scale_method)
            normalized = (residual - centers) / scales
            scores = self._score_rows(normalized, score_mode)
            median = float(np.median(scores))
            cutoff = median + robust_k * float(np.median(np.abs(scores - median)))
            seeded_samples = set(
                int(row_indexes[index]) for index in np.flatnonzero(scores > cutoff)
            )
            affected = np.asarray(
                [
                    any(
                        sample in seeded_samples
                        for sample in range(int(row) - tap_count + 1, int(row) + 1)
                    )
                    for row in row_indexes
                ],
                dtype=np.bool_,
            )
            maximum_rejections = int(np.floor(0.05 * len(features)))
            affected_indexes = np.flatnonzero(affected)
            if len(affected_indexes) > maximum_rejections:
                stable_worst = sorted(
                    affected_indexes.tolist(),
                    key=lambda index: (-float(scores[index]), int(row_indexes[index])),
                )
                affected[:] = False
                affected[stable_worst[:maximum_rejections]] = True
            retained = ~affected
            if not retained.any():
                raise ValueError("robust refit has no eligible rows")
            weights, biases = self._ridge_source_scale(
                features[retained], targets[retained], tap_count, alpha
            )
        if numeric_type is not None:
            dtype = self._target_dtype(numeric_type)
            weights, biases = weights.astype(dtype), biases.astype(dtype)
            final_residual = (
                np.asarray(targets[retained], dtype=dtype)
                - self.target_predict_rows(
                    weights, biases, features[retained], numeric_type
                )
            ).astype(np.float64)
        else:
            final_residual = targets[retained] - self._predict_rows(
                weights, biases, features[retained]
            )
        centers, scales = self._residual_scale(final_residual, scale_method)
        if numeric_type is not None:
            centers, scales = centers.astype(dtype), scales.astype(dtype)
            if not all(
                np.all(np.isfinite(v)) for v in (weights, biases, centers, scales)
            ) or np.any(scales <= 0):
                from dual_imu_collision_studio.domain.learning.model import (
                    CandidateNumericalError,
                )

                raise CandidateNumericalError("Invalid target model/calibration")
        return FrozenFirModel(
            tap_count=tap_count,
            weights=weights,
            biases=biases,
            alpha=float(alpha),
            residual_centers=centers,
            residual_scales=scales,
            scale_method=scale_method,
            robust_k=robust_k,
            score_mode=score_mode,
            initial_fit_rows=len(features),
            refit_rows=int(retained.sum()),
            use_robust_refit=use_robust_refit,
        )

    @classmethod
    def predict_mimo_fir(
        cls, model: FrozenFirModel, internal_imu: np.ndarray, segment_ids: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        dummy = np.zeros((len(internal_imu), 3), dtype=np.float64)
        features, _, row_indexes = cls._fir_rows(
            internal_imu, dummy, segment_ids, model.tap_count
        )
        return cls._predict_rows(model.weights, model.biases, features), row_indexes

    @staticmethod
    def _fir_rows(
        internal_imu: np.ndarray,
        external_imu: np.ndarray,
        segment_ids: np.ndarray,
        tap_count: int,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        internal = np.asarray(internal_imu, dtype=np.float64)
        external = np.asarray(external_imu, dtype=np.float64)
        segments = np.asarray(segment_ids)
        if (
            internal.ndim != 2
            or internal.shape[1] != 3
            or external.shape != internal.shape
        ):
            raise ValueError(
                "Internal and External IMU arrays must have matching Nx3 shape"
            )
        if len(segments) != len(internal) or tap_count < 1:
            raise ValueError("segment_ids and positive tap_count are required")
        features: list[list[float]] = []
        targets: list[np.ndarray] = []
        indexes: list[int] = []
        for row in range(tap_count - 1, len(internal)):
            support = slice(row - tap_count + 1, row + 1)
            if np.any(segments[support] != segments[row]):
                continue
            values = [
                internal[row - lag, axis]
                for axis in range(3)
                for lag in range(tap_count)
            ]
            if not np.all(np.isfinite(values)) or not np.all(
                np.isfinite(external[row])
            ):
                continue
            features.append(values)
            targets.append(external[row])
            indexes.append(row)
        return (
            np.asarray(features),
            np.asarray(targets),
            np.asarray(indexes, dtype=np.int64),
        )

    @staticmethod
    def _ridge_source_scale(
        features: np.ndarray, targets: np.ndarray, tap_count: int, alpha: float
    ) -> tuple[np.ndarray, np.ndarray]:
        if not math.isfinite(alpha) or not 1e-6 <= alpha <= 100:
            raise ValueError("Ridge alpha is outside [1e-6, 100]")
        feature_mean = np.mean(features, axis=0)
        feature_scale = np.std(features, axis=0, ddof=0)
        if np.any(
            feature_scale
            <= 64
            * np.finfo(np.float64).eps
            * np.maximum(1.0, np.max(np.abs(features), axis=0))
        ):
            raise CandidateNumericalError("degenerate FIR input feature scale")
        standardized = (features - feature_mean) / feature_scale
        target_mean = np.mean(targets, axis=0)
        count = len(features)
        normal = standardized.T @ standardized / count + alpha * np.eye(
            standardized.shape[1]
        )
        rhs = standardized.T @ (targets - target_mean) / count
        standardized_weights = np.linalg.solve(normal, rhs)
        source_weights_flat = standardized_weights / feature_scale[:, None]
        biases = target_mean - feature_mean @ source_weights_flat
        weights = source_weights_flat.T.reshape(3, 3, tap_count)
        return weights, biases

    @staticmethod
    def _predict_rows(
        weights: np.ndarray, biases: np.ndarray, features: np.ndarray
    ) -> np.ndarray:
        return features @ weights.reshape(3, -1).T + biases

    @staticmethod
    def _residual_scale(
        residual: np.ndarray, method: str
    ) -> tuple[np.ndarray, np.ndarray]:
        if method == "STD":
            centers = np.mean(residual, axis=0)
            scales = np.sqrt(np.mean((residual - centers) ** 2, axis=0))
        elif method == "MAD":
            centers = np.median(residual, axis=0)
            scales = 1.482602218505602 * np.median(np.abs(residual - centers), axis=0)
        else:
            raise ValueError("Residual Scale Method must be STD or MAD")
        limit = (
            64
            * np.finfo(np.float64).eps
            * np.maximum(1.0, np.max(np.abs(residual), axis=0))
        )
        if (
            not np.all(np.isfinite(centers))
            or not np.all(np.isfinite(scales))
            or np.any(scales <= limit)
        ):
            raise CandidateNumericalError("degenerate residual scale")
        return centers, scales

    @staticmethod
    def _score_rows(normalized: np.ndarray, mode: str) -> np.ndarray:
        if mode == "MAX_ABS":
            return np.max(np.abs(normalized), axis=1)
        if mode == "L2_NORM":
            return np.sqrt(np.sum(normalized**2, axis=1))
        raise ValueError("Score Mode must be MAX_ABS or L2_NORM")

    def build_candidate_plan(
        self, sample_rate_hz: float, settings=None
    ) -> CandidatePlan:
        from dual_imu_collision_studio.domain.learning.model import (
            LearningSettings,
            TrainingMode,
        )

        if sample_rate_hz <= 0 or not math.isfinite(sample_rate_hz):
            raise ValueError("Sample Rate must be finite and greater than zero")
        fixed = (
            settings is not None and settings.training_mode is TrainingMode.FIXED_GRID
        )
        mlp = settings is not None and settings.model_families == ("mlp",)
        requested_histories = (
            settings.mlp_history_ms
            if mlp
            else (settings.fixed_history_ms if fixed else self.REQUESTED_HISTORIES_MS)
        )
        aliases: dict[int, list[int]] = {}
        for requested_ms in requested_histories:
            tap_count = math.floor(requested_ms * sample_rate_hz / 1000.0) + 1
            aliases.setdefault(tap_count, []).append(requested_ms)
        histories = tuple(
            HistorySpec(
                tap_count=tap_count,
                requested_history_aliases_ms=tuple(requested),
                effective_history_ms=1000.0 * (tap_count - 1) / sample_rate_hz,
            )
            for tap_count, requested in aliases.items()
        )
        return CandidatePlan(
            histories=histories,
            ridge_alphas=settings.mlp_l2
            if mlp
            else (settings.fixed_ridge_alphas if fixed else self.RIDGE_ALPHAS),
            scale_methods=("STD",) if fixed else self.SCALE_METHODS,
            robust_k_values=(0,) if fixed else self.ROBUST_K_VALUES,
            score_modes=("L2_NORM",) if fixed else self.SCORE_MODES,
            confirmation_modes=self.CONFIRMATION_MODES,
            thresholds=(),
        )

    def replay_detector(
        self,
        normalized_residual: np.ndarray,
        time_s: np.ndarray,
        config: DetectorConfig,
        reset_before: np.ndarray | None = None,
    ) -> DetectorTrace:
        dtype = self._target_dtype(config.numeric_type)
        residual = np.asarray(normalized_residual, dtype=dtype)
        times = np.asarray(time_s, dtype=np.float64)
        if residual.ndim != 2 or residual.shape[1] != 3 or len(residual) != len(times):
            raise ValueError(
                "normalized residual and time arrays must contain matching Nx3 samples"
            )
        scores = self._detector_scores(residual, config.score_mode, config.numeric_type)
        return self._replay_scores(scores, times, config, reset_before)

    def _detector_scores(
        self,
        normalized_residual: np.ndarray,
        score_mode: str,
        numeric_type: str,
    ) -> np.ndarray:
        dtype = self._target_dtype(numeric_type)
        residual = np.asarray(normalized_residual, dtype=dtype)
        if residual.ndim != 2 or residual.shape[1] != 3:
            raise ValueError("normalized residual must contain Nx3 samples")
        scores = np.empty(len(residual), dtype=dtype)
        for index, axes in enumerate(residual):
            scores[index] = self._score(axes, score_mode, dtype)
        return scores

    def _replay_scores(
        self,
        detector_scores: np.ndarray,
        time_s: np.ndarray,
        config: DetectorConfig,
        reset_before: np.ndarray | None = None,
    ) -> DetectorTrace:
        dtype = self._target_dtype(config.numeric_type)
        scores = np.asarray(detector_scores, dtype=dtype)
        times = np.asarray(time_s, dtype=np.float64)
        if scores.ndim != 1 or len(scores) != len(times):
            raise ValueError(
                "detector scores and time arrays must have matching lengths"
            )
        resets = (
            np.zeros(len(times), dtype=np.bool_)
            if reset_before is None
            else np.asarray(reset_before, dtype=np.bool_)
        )
        if resets.shape != (len(times),):
            raise ValueError("reset markers must match replay samples")
        if config.threshold <= 0 or config.release_ratio <= 0:
            raise ValueError("detector thresholds must be greater than zero")
        target_threshold = dtype(config.threshold)
        release_threshold = dtype(dtype(config.threshold) * dtype(config.release_ratio))
        ratio = np.empty_like(scores)
        for index, score in enumerate(scores):
            ratio[index] = dtype(score / target_threshold)

        armed = True
        quiet_since: float | None = None
        confirmation: list[bool] = []
        states: list[str] = []
        trigger_indices: list[int] = []
        for index, score in enumerate(scores):
            if resets[index]:
                armed = True
                confirmation.clear()
                quiet_since = None
            if not np.isfinite(score) or not np.isfinite(times[index]):
                confirmation.clear()
                quiet_since = None
                states.append("INVALID")
                continue
            if not armed:
                if score < release_threshold:
                    if quiet_since is None:
                        quiet_since = float(times[index])
                    elapsed = float(times[index]) - quiet_since
                    time_tolerance = (
                        8.0
                        * np.finfo(np.float64).eps
                        * max(1.0, abs(float(times[index])))
                    )
                    if elapsed + time_tolerance >= config.release_quiet_time_s:
                        armed = True
                        confirmation.clear()
                        quiet_since = None
                else:
                    quiet_since = None
                states.append("ARMED" if armed else "LATCHED")
                continue
            confirmation.append(bool(score > target_threshold))
            if len(confirmation) > 3:
                confirmation.pop(0)
            if self._confirmation_complete(confirmation, config.confirmation_mode):
                trigger_indices.append(index)
                armed = False
                confirmation.clear()
                quiet_since = None
                states.append("TRIGGERED")
            else:
                states.append("ARMED")
        return DetectorTrace(
            scores=scores,
            collision_ratio=ratio,
            states=tuple(states),
            trigger_indices=tuple(trigger_indices),
            trigger_times_s=tuple(float(times[index]) for index in trigger_indices),
        )

    @staticmethod
    def _target_dtype(numeric_type: str) -> type[np.float32] | type[np.float64]:
        if numeric_type == "float32":
            return np.float32
        if numeric_type == "float64":
            return np.float64
        raise ValueError("Target Numeric Type must be float32 or float64")

    @staticmethod
    def _score(axes: np.ndarray, mode: str, dtype: type[np.float32] | type[np.float64]):
        if mode == "MAX_ABS":
            winner = dtype(abs(axes[0]))
            for axis in axes[1:]:
                value = dtype(abs(axis))
                if value > winner:
                    winner = value
            return winner
        if mode == "L2_NORM":
            x2 = dtype(dtype(axes[0]) * dtype(axes[0]))
            y2 = dtype(dtype(axes[1]) * dtype(axes[1]))
            z2 = dtype(dtype(axes[2]) * dtype(axes[2]))
            xy = dtype(x2 + y2)
            xyz = dtype(xy + z2)
            return dtype(np.sqrt(xyz, dtype=dtype))
        raise ValueError("Score Mode must be MAX_ABS or L2_NORM")

    @staticmethod
    def _confirmation_complete(history: list[bool], mode: str) -> bool:
        if mode == "1_OF_1":
            return bool(history and history[-1])
        if mode == "2_CONSECUTIVE":
            return len(history) >= 2 and history[-2:] == [True, True]
        if mode == "2_OF_3":
            return len(history) >= 3 and sum(history[-3:]) >= 2
        raise ValueError("unknown confirmation mode")
