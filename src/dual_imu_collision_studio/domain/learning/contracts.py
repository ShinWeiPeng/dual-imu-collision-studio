from __future__ import annotations

from typing import Callable, Iterable, Protocol

from dual_imu_collision_studio.domain.learning.model import (
    HistoryBatchResult,
    HistoryJob,
    HistoryWorkerProgress,
    LearningRequest,
    QualificationResult,
    LearningDataset, FoldJob, RecordingJob, ExecutionBatch,
)


class LearningCommandPort(Protocol):
    def start(self, request: LearningRequest) -> None: ...
    def cancel(self) -> None: ...


class LearningEventPort(Protocol):
    def progressed(self, progress: float, state: str) -> None: ...
    def completed(self, result: QualificationResult) -> None: ...
    def cancelled(self, result: QualificationResult) -> None: ...


class HistoryExecutionPort(Protocol):
    def execute(
        self,
        jobs: tuple[HistoryJob, ...],
        progress: Callable[[HistoryWorkerProgress], None] | None = None,
        cancelled: Callable[[], bool] | None = None,
    ) -> HistoryBatchResult: ...


class LearningExecutionPort(Protocol):
    def evaluate_folds(self, dataset: LearningDataset, jobs: tuple[FoldJob, ...], progress: Callable | None = None, cancelled: Callable[[], bool] | None = None) -> ExecutionBatch: ...
    def evaluate_recordings(self, jobs: tuple[RecordingJob, ...], cancelled: Callable[[], bool] | None = None) -> ExecutionBatch: ...


class ReplayCsvFilePort(Protocol):
    def write(self, destination: str, lines: Iterable[str]) -> str: ...


class ModelTextFilePort(Protocol):
    def write(self, destination: str, lines: Iterable[str]) -> str: ...
