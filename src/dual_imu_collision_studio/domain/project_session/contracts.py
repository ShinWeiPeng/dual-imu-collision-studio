from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .model import ProjectDocument, ProjectSourceReference


class ProjectFilePort(Protocol):
    def read(self, path: str | Path) -> ProjectDocument: ...

    def write(self, path: str | Path, document: ProjectDocument) -> Path: ...

    def fingerprint(self, path: str | Path, worksheet: str = "") -> ProjectSourceReference: ...

