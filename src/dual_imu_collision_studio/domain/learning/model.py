from __future__ import annotations

from dataclasses import dataclass, field, replace
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar

import numpy as np
from .preprocessing import SingleImuSettings


class TrainingMode(str, Enum):
    FIXED_GRID = "fixed_grid"
    OPTIMIZED = "optimized"


@dataclass(frozen=True, slots=True)
class LearningSettings:
    FIXED_HISTORY_OPTIONS_MS: ClassVar[tuple[int, ...]] = (4, 8, 16, 32, 64, 128)
    FIXED_RIDGE_ALPHA_OPTIONS: ClassVar[tuple[float, ...]] = (
        1e-6,
        1e-4,
        1e-2,
        1.0,
        100.0,
    )

    n_fold: int = 3
    include_training_mse: bool = True
    use_robust_refit: bool = False
    convergence_tolerance_percent: float = 0.1
    validation_allowance_percent: float = 20.0
    training_mode: TrainingMode = TrainingMode.FIXED_GRID
    fixed_history_ms: tuple[int, ...] = ()
    fixed_ridge_alphas: tuple[float, ...] = ()

    model_families: tuple[str, ...] = ("fir",)
    mlp_history_ms: tuple[int, ...] = ()
    mlp_layer_widths: tuple[tuple[int, ...], ...] = ((), ())
    mlp_l2: tuple[float, ...] = ()

    @property
    def mlp_depth(self):
        return len(self.mlp_layer_widths)

    @property
    def mlp_parameter_count(self):
        import math

        return (
            len(self.mlp_history_ms)
            * len(self.mlp_l2)
            * math.prod(map(len, self.mlp_layer_widths))
        )

    @property
    def selections_ready(self):
        return bool(self.model_families) and all(
            (
                self.training_mode is TrainingMode.OPTIMIZED
                or bool(self.fixed_history_ms and self.fixed_ridge_alphas)
            )
            if family == "fir"
            else bool(self.mlp_parameter_count)
            for family in self.model_families
        )

    def __post_init__(self) -> None:
        families = tuple(self.model_families)
        if any(v not in ("fir", "mlp") for v in families) or len(set(families)) != len(
            families
        ):
            raise ValueError("Unknown or duplicate model family")
        object.__setattr__(
            self, "model_families", tuple(v for v in ("fir", "mlp") if v in families)
        )
        object.__setattr__(
            self,
            "mlp_history_ms",
            self._ordered_selection(
                self.mlp_history_ms, self.FIXED_HISTORY_OPTIONS_MS, "MLP History"
            ),
        )
        object.__setattr__(
            self,
            "mlp_l2",
            self._ordered_selection(self.mlp_l2, (0.0001, 0.001, 0.01), "MLP L2"),
        )
        if not self.mlp_layer_widths or isinstance(self.mlp_layer_widths, (str, bytes)):
            raise ValueError("MLP requires a positive hidden depth")
        layers = tuple(
            self._ordered_selection(v, (4, 8, 16, 32, 64, 128), "MLP width")
            for v in self.mlp_layer_widths
        )
        object.__setattr__(self, "mlp_layer_widths", layers)
        try:
            mode = TrainingMode(self.training_mode)
        except (TypeError, ValueError) as exc:
            raise ValueError("Training mode must be fixed_grid or optimized") from exc
        object.__setattr__(self, "training_mode", mode)
        if type(self.n_fold) is not int or not 2 <= self.n_fold <= 10:
            raise ValueError("N-fold must be an integer from 2 to 10")
        if (
            type(self.include_training_mse) is not bool
            or type(self.use_robust_refit) is not bool
        ):
            raise ValueError("Learning options must be boolean")
        for name, minimum in (
            ("convergence_tolerance_percent", 0.001),
            ("validation_allowance_percent", 0.0),
        ):
            value = getattr(self, name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not np.isfinite(value)
            ):
                raise ValueError(f"{name} must be finite")
            decimal = Decimal(str(value))
            if not minimum <= value <= 100 or decimal != decimal.quantize(
                Decimal("0.001")
            ):
                raise ValueError(
                    f"{name} must be {minimum} through 100, with at most 3 decimal places"
                )
        histories = self._ordered_selection(
            self.fixed_history_ms, self.FIXED_HISTORY_OPTIONS_MS, "History"
        )
        alphas = self._ordered_selection(
            self.fixed_ridge_alphas, self.FIXED_RIDGE_ALPHA_OPTIONS, "Ridge alpha"
        )
        object.__setattr__(self, "fixed_history_ms", histories)
        object.__setattr__(self, "fixed_ridge_alphas", alphas)

    @staticmethod
    def _ordered_selection(values, options, label):
        if isinstance(values, (str, bytes)):
            raise ValueError(f"{label} selection must be a sequence")
        try:
            selected = set(values)
        except TypeError as exc:
            raise ValueError(f"{label} selection must be a sequence") from exc
        if any(
            type(value) not in (int, float) or value not in options
            for value in selected
        ):
            raise ValueError(f"{label} selection contains an unsupported value")
        return tuple(option for option in options if option in selected)

    def for_run(self) -> LearningSettings:
        if self.training_mode is TrainingMode.OPTIMIZED:
            if not self.fixed_history_ms and not self.fixed_ridge_alphas:
                return self
            return replace(self, fixed_history_ms=(), fixed_ridge_alphas=())
        if not self.use_robust_refit and self.convergence_tolerance_percent == 0.1:
            return self
        return replace(
            self,
            use_robust_refit=False,
            convergence_tolerance_percent=0.1,
        )


class CycleAllocationError(ValueError):
    """Terminal Cycle count/allocation failure, not a fallback evidence gap."""


class CandidateNumericalError(ArithmeticError):
    """Expected invalid fitted candidate on otherwise valid input."""


@dataclass(frozen=True, slots=True)
class HistorySpec:
    tap_count: int
    requested_history_aliases_ms: tuple[int, ...]
    effective_history_ms: float


class HistoryExecutionError(RuntimeError):
    pass


class HardwareMemoryInsufficientError(HistoryExecutionError):
    pass


class InsufficientTrainingEvidence(ValueError):
    """The selected scope cannot support Training, independently of model rules."""


@dataclass(frozen=True, slots=True)
class HistoryJob:
    job_index: int
    dataset: Any
    numeric_type: str
    history: HistorySpec
    active_offsets: tuple[float, ...]
    excluded_offsets: tuple[float, ...]
    training_speeds: tuple[float, ...]
    supplied_offsets: tuple[float, ...]
    supplied_speeds: tuple[float, ...]
    outer_round: int
    inner_round: int
    stable_order_base: int


@dataclass(frozen=True, slots=True)
class HistoryJobResult:
    job_index: int
    history: HistorySpec
    candidates: tuple[Any, ...]
    attempt_durations_s: tuple[float, ...] = ()
    unavailable_reason: str = ""


@dataclass(frozen=True, slots=True)
class HistoryBatchResult:
    results: tuple[HistoryJobResult, ...]
    peak_rss_bytes: int
    launch_available_ram_bytes: int
    worker_pids: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class HistoryWorkerProgress:
    job_index: int
    history_ms: int
    attempt: int
    stage: str
    fraction: float
    elapsed_s: float
    message: str
    current_speed_mm_s: float | None = None
    current_offset_mm: float | None = None


@dataclass(frozen=True, slots=True)
class CandidatePlan:
    histories: tuple[HistorySpec, ...]
    ridge_alphas: tuple[float, ...]
    scale_methods: tuple[str, ...]
    robust_k_values: tuple[int, ...]
    score_modes: tuple[str, ...]
    confirmation_modes: tuple[str, ...]
    thresholds: tuple[float, ...]

    @property
    def parameter_count(self) -> int:
        return len(self.histories) * len(self.ridge_alphas) * len(self.robust_k_values)

    @property
    def candidate_count(self) -> int | None:
        if not self.thresholds:
            return None  # Determined only after each frozen model has been scored.
        return (
            len(self.histories)
            * len(self.ridge_alphas)
            * len(self.scale_methods)
            * len(self.robust_k_values)
            * len(self.score_modes)
            * len(self.confirmation_modes)
            * len(self.thresholds)
        )


@dataclass(frozen=True, slots=True)
class HistoryAttemptTiming:
    history_ms: int
    attempt: int
    duration_s: float


@dataclass(frozen=True, slots=True)
class LearningLogEvidence:
    kind: str
    parameter: ParameterPoint | None = None
    parameter_loss: float | None = None
    previous_parameter_loss: float | None = None
    fold_index: int | None = None
    kernel_loss: float | None = None
    validation_pass: bool | None = None
    validation_outcomes: tuple[tuple[float, float, bool], ...] = ()
    evaluated_count: int = 0
    pending_count: int = 0
    disposition: str = ""
    reason: str = ""

    def __post_init__(self) -> None:
        if self.kind not in {
            "parameter-best",
            "parameter-final",
            "parameter-evaluated",
            "kernel-admitted",
            "fallback",
            "skipped",
            "terminal",
        }:
            raise ValueError("unknown Learning log evidence kind")
        if self.evaluated_count < 0 or self.pending_count < 0:
            raise ValueError("Learning log work counts cannot be negative")
        if self.kind in {"parameter-best", "parameter-final"}:
            if self.parameter is None or self.parameter_loss is None:
                raise ValueError(
                    f"{self.kind} evidence requires a parameter and Parameter Loss"
                )
        if self.kind == "parameter-evaluated":
            if self.parameter is None or self.parameter_loss is None:
                raise ValueError(
                    "parameter-evaluated evidence requires a parameter and Parameter Loss"
                )
            if (
                self.disposition not in {"cv-selected", "cv-rejected"}
                or not self.reason
            ):
                raise ValueError(
                    "parameter-evaluated evidence requires a disposition and reason"
                )
        if self.kind == "kernel-admitted":
            if (
                self.parameter is None
                or self.parameter_loss is None
                or self.fold_index is None
                or self.kernel_loss is None
                or self.validation_pass is None
                or not self.validation_outcomes
            ):
                raise ValueError(
                    "kernel-admitted evidence requires complete fold and validation evidence"
                )
            if self.validation_pass != all(
                outcome[2] for outcome in self.validation_outcomes
            ):
                raise ValueError(
                    "kernel-admitted validation summary must match its outcomes"
                )


@dataclass(frozen=True, slots=True)
class LearningProgress:
    stage: str
    fraction: float
    outer_round: int
    inner_round: int
    message: str
    active_offsets: tuple[float, ...] = ()
    excluded_offsets: tuple[float, ...] = ()
    training_speeds: tuple[float, ...] = ()
    supplied_offsets: tuple[float, ...] = ()
    supplied_speeds: tuple[float, ...] = ()
    current_speed_mm_s: float | None = None
    current_offset_mm: float | None = None
    worker_attempt_timings: tuple[HistoryAttemptTiming, ...] = ()
    round_elapsed_s: float | None = None
    process_tree_peak_rss_bytes: int = 0
    launch_available_ram_bytes: int = 0
    worker_pids: tuple[int, ...] = ()
    unavailable_reason: str = ""
    log_evidence: LearningLogEvidence | None = None
    evaluated_count: int | None = None
    pending_count: int | None = None

    def __post_init__(self) -> None:
        if self.stage not in {
            "Learning",
            "Qualifying",
            "Refining Speed Range",
            "Complete",
        }:
            raise ValueError("unknown Learning progress stage")
        if not 0.0 <= self.fraction <= 1.0:
            raise ValueError("Learning progress fraction must be between zero and one")
        if self.evaluated_count is not None and self.evaluated_count < 0:
            raise ValueError("evaluated work count cannot be negative")
        if self.pending_count is not None and self.pending_count < 0:
            raise ValueError("pending work count cannot be negative")


@dataclass(frozen=True, slots=True)
class LearningRequest:
    workspace: Any
    numeric_type: str
    settings: LearningSettings = field(default_factory=LearningSettings)


@dataclass(frozen=True, slots=True)
class LearningInterval:
    kind: str
    start_index: int
    end_index: int
    cycle_index: int = -1

    def __post_init__(self) -> None:
        if self.start_index < 0 or self.end_index <= self.start_index:
            raise ValueError("Learning interval must have a non-empty sample range")


@dataclass(frozen=True, slots=True)
class LearningRecording:
    recording_id: str
    robot_speed_mm_s: float
    collision_offset_mm: float
    sample_rate_hz: float
    time_s: Any
    internal_imu: Any
    external_imu: Any
    discontinuity_before: Any
    intervals: tuple[LearningInterval, ...]
    preprocessing: SingleImuSettings | None = None
    training_eligible: Any = None
    prepared_self: bool = False

    def __post_init__(self) -> None:
        sample_count = len(self.time_s)
        if (
            not self.recording_id
            or self.robot_speed_mm_s <= 0
            or self.sample_rate_hz <= 0
        ):
            raise ValueError(
                "Learning recording identity, Robot Speed, and Sample Rate are required"
            )
        if (
            self.preprocessing is None
            or self.preprocessing.sensor == "internal"
            or self.prepared_self
        ) and np.asarray(self.internal_imu).shape != (sample_count, 3):
            raise ValueError("Learning Internal IMU must have Nx3 shape")
        if (
            self.preprocessing is None
            or self.preprocessing.sensor == "external"
            or self.prepared_self
        ) and np.asarray(self.external_imu).shape != (sample_count, 3):
            raise ValueError("Learning External IMU must have Nx3 shape")
        if np.asarray(self.discontinuity_before).shape != (sample_count,):
            raise ValueError("Learning discontinuity markers must match sample rows")
        if any(interval.end_index > sample_count for interval in self.intervals):
            raise ValueError("Learning interval exceeds its recording")


@dataclass(frozen=True, slots=True)
class LearningDataset:
    recordings: tuple[LearningRecording, ...]

    def __post_init__(self) -> None:
        if not self.recordings:
            raise ValueError("Learning dataset requires at least one recording")


@dataclass(frozen=True, slots=True)
class FitEvidence:
    internal_imu: Any
    external_imu: Any
    segment_ids: Any
    recording_count: int
    interval_count: int


@dataclass(frozen=True, slots=True)
class FirMatrixEvidence:
    features: Any
    targets: Any
    row_indexes: Any


@dataclass(frozen=True, slots=True)
class HistoryFoldEvidence:
    training: FirMatrixEvidence
    held_out_by_condition: tuple[tuple[tuple[float, float], FirMatrixEvidence], ...]


@dataclass(frozen=True, slots=True)
class CycleFoldGroup:
    recording_id: str
    robot_speed_mm_s: float
    collision_offset_mm: float
    cycle_index: int

    def __post_init__(self) -> None:
        if not self.recording_id or self.robot_speed_mm_s <= 0 or self.cycle_index < 0:
            raise ValueError(
                "Cycle fold group requires recording, condition, and Cycle identity"
            )


@dataclass(frozen=True, slots=True)
class CrossValidationFold:
    fold_index: int
    held_out_groups: tuple[CycleFoldGroup, ...]

    def __post_init__(self) -> None:
        if self.fold_index < 1 or not self.held_out_groups:
            raise ValueError(
                "Cross-validation fold requires a one-based index and held-out groups"
            )


@dataclass(frozen=True, slots=True)
class CrossValidationPlan:
    fold_count: int
    evidence_level: str
    folds: tuple[CrossValidationFold, ...]

    def __post_init__(self) -> None:
        if (
            type(self.fold_count) is not int
            or not 2 <= self.fold_count <= 10
            or len(self.folds) != self.fold_count
        ):
            raise ValueError("Cross-validation requires exactly two to ten folds")


@dataclass(frozen=True, slots=True)
class QualificationResult:
    candidates: tuple[QualifiedCandidate, ...]
    diagnostic_candidates: tuple[QualifiedCandidate, ...] = ()
    unavailable_rounds: tuple[LearningProgress, ...] = ()
    run_provenance: RunProvenance | None = None
    family_provenance: tuple[RunProvenance, ...] = ()


class LearningCancelled(InterruptedError):
    """Cancellation observed with the last complete-candidate result."""

    __slots__ = ("_result",)

    def __init__(self, result: QualificationResult) -> None:
        super().__init__("Learning cancelled")
        self._result = result

    @property
    def result(self) -> QualificationResult:
        """Return the immutable snapshot retained at the cancellation boundary."""
        return self._result


@dataclass(frozen=True, slots=True)
class DetectorConfig:
    numeric_type: str
    score_mode: str
    confirmation_mode: str
    threshold: float
    release_ratio: float = 0.5
    release_quiet_time_s: float = 0.050


@dataclass(frozen=True, slots=True)
class DetectorTrace:
    scores: np.ndarray
    collision_ratio: np.ndarray
    states: tuple[str, ...]
    trigger_indices: tuple[int, ...]
    trigger_times_s: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class ReplayEvidence:
    candidate_id: str
    recording_id: str
    cycle_index: int
    event_kind: str
    event_ordinal: int
    time_s: np.ndarray
    internal_imu: np.ndarray
    actual_external_imu: np.ndarray
    predicted_external_imu: np.ndarray
    residual: np.ndarray
    normalized_residual: np.ndarray
    detector_trace: DetectorTrace
    threshold: float
    selected_event_start_index: int
    selected_event_end_index: int
    selected_event_latency_ms: float | None
    model_family: str = "fir"


@dataclass(frozen=True, slots=True)
class OffsetQualification:
    collision_offset_mm: float
    passing_speeds: tuple[float, ...]
    collision_detectable_speeds: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class ConditionQualification:
    robot_speed_mm_s: float
    collision_offset_mm: float
    recording_count: int
    valid_cycle_count: int
    normal_interval_count: int
    pick_interval_count: int
    put_interval_count: int
    collision_interval_count: int
    normal_false_events: int
    pick_false_events: int
    put_false_events: int
    collision_detected_count: int
    worst_collision_latency_ms: float | None
    status: str

    def __post_init__(self) -> None:
        if self.status not in {"PASS", "FAIL", "COVERAGE_GAP"}:
            raise ValueError("unknown condition Qualification status")


@dataclass(frozen=True, slots=True)
class RecordingQualification:
    recording_id: str
    robot_speed_mm_s: float
    collision_offset_mm: float
    normal_false_events: int
    pick_false_events: int
    put_false_events: int
    collision_detected_count: int
    collision_interval_count: int
    worst_collision_latency_ms: float | None
    status: str
    collision_snrs_db: tuple[float | None, ...] = ()

    def __post_init__(self) -> None:
        if not self.recording_id:
            raise ValueError("recording Qualification requires an identity")
        if self.status not in {"PASS", "FAIL", "COVERAGE_GAP"}:
            raise ValueError("unknown recording Qualification status")
        if len(self.collision_snrs_db) != self.collision_interval_count:
            raise ValueError(
                "recording Qualification requires one SNR entry per Collision"
            )
        if any(
            value is not None and not np.isfinite(value)
            for value in self.collision_snrs_db
        ):
            raise ValueError(
                "recording Qualification SNR entries must be finite or unavailable"
            )


@dataclass(frozen=True, slots=True)
class FallbackState:
    active_offsets: tuple[float, ...]
    excluded_offsets: tuple[float, ...]
    training_speeds: tuple[float, ...]
    outer_round: int = 1
    inner_round: int = 1


class FallbackAction(Enum):
    STOP_RANGE_MATCH = "stop-range-match"
    EXCLUDE_OFFSET = "exclude-offset"
    REDUCE_SPEED = "reduce-speed"
    EXHAUSTED = "exhausted"


@dataclass(frozen=True, slots=True)
class QualifiedCandidate:
    candidate_id: str
    training_speeds: tuple[float, ...]
    passing_speeds: tuple[float, ...]
    tap_count: int
    worst_latency_ms: float
    robustness_margin: float
    stable_order: int
    offset_qualifications: tuple[OffsetQualification, ...] = ()
    conditions: tuple[ConditionQualification, ...] = ()
    model: FrozenFirModel | FrozenMlpModel | None = None
    history: HistorySpec | None = None
    detector_config: DetectorConfig | None = None
    active_offsets: tuple[float, ...] = ()
    excluded_offsets: tuple[float, ...] = ()
    false_trigger_robustness_margin: float = float("-inf")
    collision_detection_robustness_margin: float = float("-inf")
    outer_round: int = 1
    inner_round: int = 1
    cross_validation_fold_count: int = 0
    cross_validation_evidence_level: str = ""
    cross_validation_worst_condition_mse: float | None = None
    cross_validation_pooled_mse: float | None = None
    total_misjudgments: int = 0
    false_trigger_count: int = 0
    missed_collision_count: int = 0
    collision_detected_count: int = 0
    collision_interval_count: int = 0
    diagnostic_worst_latency_ms: float | None = None
    training_evidence: KernelTrainingEvidence | None = None
    recording_qualifications: tuple[RecordingQualification, ...] = ()

    @property
    def qualified_speed_range(self) -> tuple[float, float] | None:
        if not self.passing_speeds:
            return None
        return self.passing_speeds[0], self.passing_speeds[-1]


@dataclass(frozen=True, slots=True)
class FallbackTransition:
    winner: QualifiedCandidate
    action: FallbackAction
    next_state: FallbackState | None


@dataclass(frozen=True, slots=True)
class FrozenFirModel:
    tap_count: int
    weights: np.ndarray
    biases: np.ndarray
    alpha: float
    residual_centers: np.ndarray
    residual_scales: np.ndarray
    scale_method: str
    robust_k: int
    score_mode: str
    initial_fit_rows: int
    refit_rows: int
    use_robust_refit: bool | None = None


@dataclass(frozen=True, slots=True)
class FrozenMlpModel:
    tap_count: int
    weights: tuple[np.ndarray, ...]
    biases: tuple[np.ndarray, ...]
    alpha: float
    residual_centers: np.ndarray
    residual_scales: np.ndarray
    initial_fit_rows: int
    refit_rows: int
    epochs: int = 0
    stop_reason: str = ""
    scale_method: str = "STD"
    robust_k: int = 0
    score_mode: str = "L2_NORM"
    use_robust_refit: bool = False

    def __post_init__(self):
        if type(self.tap_count) is not int or self.tap_count < 1:
            raise ValueError("Invalid MLP tap count")
        if len(self.weights) < 2 or len(self.weights) != len(self.biases):
            raise ValueError("MLP layer count mismatch")
        previous = 3 * self.tap_count
        frozen_w, frozen_b = [], []
        for index, (w, b) in enumerate(zip(self.weights, self.biases)):
            w, b = np.array(w, copy=True), np.array(b, copy=True)
            if w.ndim != 2 or w.shape[0] != previous or b.shape != (w.shape[1],):
                raise ValueError("MLP layer shape mismatch")
            if (
                w.dtype not in (np.dtype("float32"), np.dtype("float64"))
                or w.dtype != b.dtype
                or (frozen_w and w.dtype != frozen_w[0].dtype)
            ):
                raise ValueError("MLP numeric type mismatch")
            if not np.all(np.isfinite(w)) or not np.all(np.isfinite(b)):
                raise ValueError("MLP parameters must be finite")
            if index < len(self.weights) - 1 and w.shape[1] not in (
                4,
                8,
                16,
                32,
                64,
                128,
            ):
                raise ValueError("Unsupported hidden width")
            previous = w.shape[1]
            w.flags.writeable = b.flags.writeable = False
            frozen_w.append(w)
            frozen_b.append(b)
        if previous != 3:
            raise ValueError("MLP requires three output axes")
        object.__setattr__(self, "weights", tuple(frozen_w))
        object.__setattr__(self, "biases", tuple(frozen_b))
        for name in ("residual_centers", "residual_scales"):
            value = np.array(getattr(self, name), dtype=frozen_w[0].dtype, copy=True)
            if value.shape != (3,) or not np.all(np.isfinite(value)):
                raise ValueError("Invalid MLP residual parameters")
            if name == "residual_scales" and np.any(value <= 0):
                raise ValueError("Invalid MLP residual scales")
            value.flags.writeable = False
            object.__setattr__(self, name, value)

    def __reduce__(self):
        # IPC reconstructs through validation so immutable arrays stay read-only.
        from dataclasses import fields

        return type(self), tuple(getattr(self, f.name) for f in fields(self))


@dataclass(frozen=True, slots=True)
class CrossValidatedModel:
    model: FrozenFirModel | FrozenMlpModel
    history: HistorySpec
    fold_count: int
    evidence_level: str
    worst_condition_mse: float
    pooled_mse: float
    stable_rule_order: int

    def __post_init__(self) -> None:
        if not 2 <= self.fold_count <= 10:
            raise ValueError("Cross-validated model requires two to ten folds")
        if self.model.tap_count != self.history.tap_count:
            raise ValueError(
                "Cross-validated model and History must use the same tap count"
            )
        if self.stable_rule_order < 0:
            raise ValueError("Cross-validated model rule order cannot be negative")
        if not np.isfinite(self.worst_condition_mse) or not np.isfinite(
            self.pooled_mse
        ):
            raise ValueError("Cross-validation losses must be finite")


@dataclass(frozen=True, slots=True, order=True)
class ParameterPoint:
    tap_count: int
    alpha: float
    robust_k: int = 0
    hidden_layers: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class ConditionLoss:
    robot_speed_mm_s: float
    collision_offset_mm: float
    training_mse: float
    validation_mse: float
    training_sample_count: int = 0
    validation_sample_count: int = 0

    def loss(self, include_training: bool) -> float:
        return (
            0.5 * self.training_mse + 0.5 * self.validation_mse
            if include_training
            else self.validation_mse
        )


@dataclass(frozen=True, slots=True)
class FoldJob:
    job_index: int
    point: ParameterPoint
    fold_index: int
    training_groups: tuple[CycleFoldGroup, ...]
    held_out_groups: tuple[CycleFoldGroup, ...]
    numeric_type: str
    settings: LearningSettings


@dataclass(frozen=True, slots=True)
class FoldResult:
    job_index: int
    point: ParameterPoint
    fold_index: int
    model: FrozenFirModel | FrozenMlpModel | None
    conditions: tuple[ConditionLoss, ...] = ()
    invalid_reason: str = ""


@dataclass(frozen=True, slots=True)
class ParameterResult:
    point: ParameterPoint
    folds: tuple[FoldResult, ...]
    loss: float


@dataclass(frozen=True, slots=True)
class KernelTrainingEvidence:
    settings: LearningSettings
    fold_index: int
    conditions: tuple[ConditionLoss, ...]
    parameter_loss: float
    kernel_loss: float
    round_seed: int
    fold_plan: CrossValidationPlan


@dataclass(frozen=True, slots=True)
class RoundProvenance:
    outer_round: int
    inner_round: int
    seed: int
    active_offsets: tuple[float, ...]
    training_speeds: tuple[float, ...]
    fold_plan: CrossValidationPlan


@dataclass(frozen=True, slots=True)
class RunProvenance:
    seed: int
    settings: LearningSettings
    rounds: tuple[RoundProvenance, ...] = ()
    sampler_version: str = "balanced-cycle-permutation/1"
    family: str = "fir"


@dataclass(frozen=True, slots=True)
class ExecutionBatch:
    results: tuple[Any, ...]
    peak_rss_bytes: int = 0
    launch_available_ram_bytes: int = 0
    worker_pids: tuple[int, ...] = ()
    memory_diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RecordingJob:
    job_index: int
    recording: LearningRecording
    model: FrozenFirModel | FrozenMlpModel
    numeric_type: str
    config: DetectorConfig | None = None
    scores: Any = None


@dataclass(frozen=True, slots=True)
class RecordingResult:
    job_index: int
    scores: Any = None
    metrics: Any = None
