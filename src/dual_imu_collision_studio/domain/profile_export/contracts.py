from __future__ import annotations

from typing import Protocol

from dual_imu_collision_studio.domain.profile_export.model import (
    ProfileExportRequest,
    SemanticProfile,
)


class ProfileCommandPort(Protocol):
    def render(self, request: ProfileExportRequest) -> str: ...
    def render_json(
        self,
        profile: SemanticProfile,
        model_name: str,
        *,
        input_units: str,
    ) -> str: ...


class ProfileFilePort(Protocol):
    def write(self, destination: str, text: str, overwrite: bool) -> None: ...


class ProfileEventPort(Protocol):
    def exported(self, destination: str) -> None: ...
