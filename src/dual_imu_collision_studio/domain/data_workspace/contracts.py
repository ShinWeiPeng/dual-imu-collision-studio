from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from dual_imu_collision_studio.domain.data_workspace.model import (
    AnnotatedDatasetSnapshot,
    AnnotationTemplate,
    ColumnMapping,
    ImportedSamples,
    Recording,
    WorkspaceSnapshot,
)


class WorkspaceCommandPort(Protocol):
    def validate(self, snapshot: WorkspaceSnapshot) -> WorkspaceSnapshot: ...

    def activate_annotation_template_source(
        self, recording: Recording, cycle_index: int
    ) -> tuple[Recording, AnnotationTemplate]: ...

    def build_annotation_template(
        self, recording: Recording, cycle_index: int
    ) -> AnnotationTemplate: ...

    def project_annotation_template(
        self, recording: Recording, template: AnnotationTemplate
    ) -> Recording: ...


class TabularInputPort(Protocol):
    def read(
        self, path: str, mapping: ColumnMapping, worksheet: str | None = None
    ) -> ImportedSamples: ...


class WorkspaceEventPort(Protocol):
    def workspace_changed(self, snapshot: WorkspaceSnapshot) -> None: ...


class AnnotatedDataOutputPort(Protocol):
    def write(
        self,
        parent: str,
        dataset: AnnotatedDatasetSnapshot,
        *,
        cancelled: Callable[[], bool] | None = None,
        progress: Callable[[int, int], None] | None = None,
        chunk_rows: int = 4096,
    ) -> str: ...
