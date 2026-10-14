from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


def _new_interval_id() -> str:
    return uuid4().hex


class ActivityKind(str, Enum):
    CYCLE = "Cycle"
    PICK = "Robot Pick"
    PUT = "Robot Put"
    FORK_COLLISION = "Robot Fork Collision"
    IGNORE = "Ignore"
    NORMAL_MOTION = "Normal Robot Motion"


@dataclass(frozen=True, slots=True)
class AnnotationInterval:
    kind: ActivityKind
    start_index: int
    end_index: int
    reason: str | None = None
    provisional: bool = False
    source_recording_id: str | None = None
    source_cycle_index: int | None = None
    interval_id: str = field(default_factory=_new_interval_id)

    def __post_init__(self) -> None:
        if self.start_index < 0 or self.end_index <= self.start_index:
            raise ValueError(
                "annotation interval must have a non-empty, non-negative range"
            )
        if self.kind is ActivityKind.NORMAL_MOTION:
            raise ValueError(
                "Normal Robot Motion is derived and cannot be created explicitly"
            )
        if self.kind is ActivityKind.IGNORE and not (self.reason or "").strip():
            raise ValueError("Ignore interval requires a non-empty reason")
        if self.kind is not ActivityKind.IGNORE and self.reason is not None:
            raise ValueError("only Ignore intervals may carry a reason")
        if self.provisional:
            if (
                not (self.source_recording_id or "").strip()
                or self.source_cycle_index is None
            ):
                raise ValueError(
                    "provisional annotations require source recording and Cycle provenance"
                )
        elif (
            self.source_recording_id is not None or self.source_cycle_index is not None
        ):
            raise ValueError("confirmed annotations cannot carry proposal provenance")
        if not self.interval_id.strip():
            raise ValueError("annotation interval identity is required")


@dataclass(frozen=True, slots=True)
class AnnotationTemplateEvent:
    kind: ActivityKind
    start_phase: float
    end_phase: float
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in {
            ActivityKind.PICK,
            ActivityKind.PUT,
            ActivityKind.FORK_COLLISION,
            ActivityKind.IGNORE,
        }:
            raise ValueError(
                "annotation templates contain only Pick, Put, Fork Collision, and Ignore"
            )
        if not 0.0 <= self.start_phase < self.end_phase <= 1.0:
            raise ValueError(
                "annotation template phases must be ordered within one Cycle"
            )
        if self.kind is ActivityKind.IGNORE and not (self.reason or "").strip():
            raise ValueError("template Ignore interval requires a non-empty reason")
        if self.kind is not ActivityKind.IGNORE and self.reason is not None:
            raise ValueError("only template Ignore intervals may carry a reason")


@dataclass(frozen=True, slots=True)
class AnnotationTemplate:
    robot_speed_mm_s: float
    source_recording_id: str
    source_cycle_index: int
    reference_cycle_length_samples: int
    cycle_period_samples: float
    events: tuple[AnnotationTemplateEvent, ...]

    def __post_init__(self) -> None:
        if self.robot_speed_mm_s <= 0:
            raise ValueError("Robot Speed must be greater than zero")
        if not self.source_recording_id.strip() or self.source_cycle_index < 0:
            raise ValueError("annotation template source provenance is required")
        if self.reference_cycle_length_samples <= 0 or self.cycle_period_samples <= 0:
            raise ValueError(
                "annotation template Cycle length and period must be positive"
            )
        if not any(
            event.kind
            in {ActivityKind.PICK, ActivityKind.PUT, ActivityKind.FORK_COLLISION}
            for event in self.events
        ):
            raise ValueError(
                "reference Cycle requires at least one Pick, Put, or Fork Collision event"
            )


@dataclass(frozen=True, slots=True)
class TestCondition:
    robot_speed_mm_s: float
    collision_offset_mm: float

    def __post_init__(self) -> None:
        if self.robot_speed_mm_s <= 0:
            raise ValueError("Robot Speed must be greater than zero")


@dataclass(frozen=True, slots=True)
class Recording:
    recording_id: str
    source_path: str
    sample_rate_hz: float
    time_s: Any
    internal_imu: Any
    external_imu: Any
    condition: TestCondition
    discontinuity_before: Any = None
    annotations: tuple[AnnotationInterval, ...] = ()
    single_sensor: str | None = None

    def __post_init__(self) -> None:
        if not self.recording_id.strip():
            raise ValueError("recording_id is required")
        if self.sample_rate_hz <= 0:
            raise ValueError("Sample Rate must be greater than zero")
        sample_count = len(self.time_s)
        if sample_count == 0:
            raise ValueError("recording contains no samples")
        present = [v for v in (self.internal_imu, self.external_imu) if v is not None]
        if self.single_sensor not in {None, "internal", "external"}:
            raise ValueError("Invalid single sensor identity")
        if self.single_sensor is None and len(present) != 2:
            raise ValueError("Dual-IMU recording requires both sensors")
        if (
            self.single_sensor is not None
            and getattr(self, self.single_sensor + "_imu") is None
        ):
            raise ValueError("Selected sensor is absent")
        if any(len(v) != sample_count for v in present):
            raise ValueError("time and IMU arrays must have equal row counts")
        if self.internal_imu is not None and getattr(
            self.internal_imu, "shape", (0, 0)
        )[1:] not in ((3,), (6,)):
            raise ValueError(
                "Internal IMU must contain one or two complete XYZ signal groups"
            )
        if self.external_imu is not None and getattr(
            self.external_imu, "shape", (0, 0)
        )[1:] not in ((3,), (6,)):
            raise ValueError(
                "External IMU must contain one or two complete XYZ signal groups"
            )
        if (
            self.discontinuity_before is not None
            and len(self.discontinuity_before) != sample_count
        ):
            raise ValueError("discontinuity markers must match the recording row count")


@dataclass(frozen=True, slots=True)
class WorkspaceSnapshot:
    recordings: tuple[Recording, ...]


@dataclass(frozen=True, slots=True)
class HeaderProposal:
    header_row: int
    data_start_row: int
    columns: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.header_row < 1 or self.data_start_row <= self.header_row:
            raise ValueError("Header proposal rows must be positive and ordered")
        if len(self.columns) < 3 or len(set(self.columns)) != len(self.columns):
            raise ValueError("Header proposal requires at least three unique columns")


@dataclass(frozen=True, slots=True)
class ColumnMapping:
    data_start_row: int
    header_row: int | None
    time_column: str | None
    time_unit: str | None
    sample_rate_hz: float | None
    internal_columns: tuple[str, ...]
    external_columns: tuple[str, ...]
    single_sensor: str | None = None

    def __post_init__(self) -> None:
        if self.data_start_row < 1:
            raise ValueError("Data Start Row is 1-based")
        imu_columns = self.internal_columns + self.external_columns
        expected = len(imu_columns)
        if self.single_sensor not in {None, "internal", "external"}:
            raise ValueError("Invalid single sensor identity")
        if (
            not expected
            or len(set(imu_columns)) != expected
            or any(not name for name in imu_columns)
        ):
            raise ValueError("every mapped IMU axis must use a distinct column")
        if self.single_sensor is not None and len(
            getattr(self, self.single_sensor + "_columns")
        ) not in (3, 6):
            raise ValueError(
                "Select one or two complete XYZ groups for the single sensor"
            )
        if any(
            len(v) not in (3, 6)
            for v in (self.internal_columns, self.external_columns)
            if v
        ):
            raise ValueError("Each IMU requires one or two complete XYZ groups")
        if self.single_sensor is None and (
            not self.internal_columns or not self.external_columns
        ):
            raise ValueError("Dual IMU mapping requires both sensors")
        if self.single_sensor and getattr(
            self,
            ("external" if self.single_sensor == "internal" else "internal")
            + "_columns",
        ):
            raise ValueError("Single IMU mapping cannot contain another sensor")
        if self.time_column is None:
            if self.sample_rate_hz is None or self.sample_rate_hz <= 0:
                raise ValueError("No Time Column requires a positive fixed Sample Rate")
        elif self.time_unit not in {"s", "ms", "us", "µs"}:
            raise ValueError("Time Unit must be s, ms, or µs")


@dataclass(frozen=True, slots=True)
class ImportedSamples:
    time_s: Any
    internal_imu: Any
    external_imu: Any
    inferred_sample_rate_hz: float
    discontinuity_before: Any
    warnings: tuple[str, ...] = ()
    interpolated_indices: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class WaveformViewportProjection:
    mode: str
    positions: tuple[float, ...]
    minimums: tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]
    maximums: tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]
    means: tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]
    sample_start: int
    sample_end: int

    def __post_init__(self) -> None:
        if self.mode not in {"raw", "envelope"}:
            raise ValueError("waveform projection mode must be raw or envelope")
        count = len(self.positions)
        if any(
            len(channel) != count
            for channel in self.minimums + self.maximums + self.means
        ):
            raise ValueError("waveform projection channels must match its positions")
        if self.sample_start < 0 or self.sample_end < self.sample_start:
            raise ValueError("waveform projection sample range must be ordered")
