from __future__ import annotations

from typing import Protocol

from dual_imu_collision_studio.domain.profile_export.model import ProfileExportRequest


class ProfileCommandPort(Protocol):
    def render(self, request: ProfileExportRequest) -> str: ...


class ProfileFilePort(Protocol):
    def write(self, destination: str, text: str, overwrite: bool) -> None: ...


class ProfileEventPort(Protocol):
    def exported(self, destination: str) -> None: ...
