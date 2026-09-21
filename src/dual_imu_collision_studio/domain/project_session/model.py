from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ProjectSourceReference:
    path: str
    worksheet: str
    size_bytes: int
    sha256: str

    def __post_init__(self) -> None:
        if not self.path.strip():
            raise ValueError("project source path is required")
        if self.size_bytes < 0:
            raise ValueError("project source size cannot be negative")
        if len(self.sha256) != 64 or any(character not in "0123456789abcdef" for character in self.sha256):
            raise ValueError("project source SHA-256 must contain 64 lowercase hexadecimal characters")

    def to_data(self) -> dict[str, object]:
        return {
            "path": self.path,
            "worksheet": self.worksheet,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True, init=False)
class ProjectDocument:
    _data: Mapping[str, Any]

    def __init__(self, data: Mapping[str, Any]) -> None:
        object.__setattr__(self, "_data", deepcopy(dict(data)))

    @property
    def data(self) -> dict[str, Any]:
        return deepcopy(dict(self._data))

    @classmethod
    def minimal_for_test(cls) -> "ProjectDocument":
        return cls(
            {
                "format": "dual-imu-collision-studio-project",
                "schema_version": 2,
                "algorithm_contract": "dual-imu-collision-profile/2",
                "result_contract": "semantic-profile/2",
                "recordings": [],
                "annotation_templates": [],
                "reviewed_duplicate_keys": [],
                "selected_recording": -1,
                "selected_stage": 0,
                "annotations_ready": False,
                "numeric_type": "",
            }
        )
