from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ConditionCoverage:
    robot_speed_mm_s: float
    collision_offset_mm: float
    normal_interval_count: int
    pick_interval_count: int
    put_interval_count: int
    collision_interval_count: int
    qualification_status: str = "PASS"
    recording_count: int = 0
    valid_cycle_count: int = 0
    normal_false_events: int = 0
    pick_false_events: int = 0
    put_false_events: int = 0
    collision_detected_count: int = 0
    worst_collision_latency_ms: float | None = None


@dataclass(frozen=True, slots=True)
class SemanticProfile:
    schema_version: str
    numeric_type: str
    sample_rate_hz: float
    requested_history_aliases_ms: tuple[int, ...]
    effective_history_ms: float
    tap_count: int
    weights: Any
    biases: Any
    ridge_alpha: float
    residual_centers: Any
    residual_scales: Any
    scale_method: str
    robust_k: int
    score_mode: str
    confirmation_mode: str
    threshold: float
    kernel_id: str
    worst_collision_latency_ms: float
    combined_robustness_margin: float
    false_trigger_robustness_margin: float
    collision_detection_robustness_margin: float
    covered_offsets_mm: tuple[float, ...]
    excluded_offsets_mm: tuple[float, ...]
    training_speed_range: tuple[float, float]
    qualified_speed_range: tuple[float, float]
    maximum_supplied_speed: float
    coverage: tuple[ConditionCoverage, ...]
    qualified: bool
    outer_round: int = 1
    inner_round: int = 1
    initial_fit_rows: int = 0
    refit_rows: int = 0
    cross_validation_fold_count: int = 0
    cross_validation_evidence_level: str = ""
    cross_validation_worst_condition_mse: float | None = None
    cross_validation_pooled_mse: float | None = None
    model_family: str = "fir"
    mlp_epochs: int = 0
    mlp_stop_reason: str = ""


@dataclass(frozen=True, slots=True)
class ProfileExportRequest:
    profile: SemanticProfile
    language: str
    destination: str | None = None


@dataclass(frozen=True, slots=True)
class ProfileHeaderArtifact:
    kernel_id: str
    filename: str
    semantic_hash: str
    text: str
