from __future__ import annotations

from typing import Protocol

from dual_imu_collision_studio.domain.process_diagnostics.model import (
    DiagnosticStatus,
    LearningTimingEvidence,
)


class DiagnosticsPort(Protocol):
    @property
    def status(self) -> DiagnosticStatus: ...

    def record_learning_started(self, numeric_type: str, recording_count: int) -> None: ...

    def record_learning_progress(
        self,
        stage: str,
        fraction: float,
        outer_round: int,
        inner_round: int,
        speed_mm_s: float | None,
        offset_mm: float | None,
    ) -> None: ...

    def record_learning_finished(self, state: str, message: str) -> None: ...

    def record_learning_timing(self, evidence: LearningTimingEvidence) -> None: ...


class NullDiagnostics:
    @property
    def status(self) -> DiagnosticStatus:
        return DiagnosticStatus()

    def record_learning_started(self, numeric_type: str, recording_count: int) -> None:
        pass

    def record_learning_progress(
        self,
        stage: str,
        fraction: float,
        outer_round: int,
        inner_round: int,
        speed_mm_s: float | None,
        offset_mm: float | None,
    ) -> None:
        pass

    def record_learning_finished(self, state: str, message: str) -> None:
        pass

    def record_learning_timing(self, evidence: LearningTimingEvidence) -> None:
        pass
