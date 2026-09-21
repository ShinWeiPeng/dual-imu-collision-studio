from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from dual_imu_collision_studio.domain.profile_export.model import ProfileHeaderArtifact


class AtomicProfileWriter:
    """Write one approved header without coupling sibling domain modules to files."""

    @staticmethod
    def write(
        destination_folder: Path | str,
        artifact: ProfileHeaderArtifact,
        *,
        replace: bool,
    ) -> Path | None:
        folder = Path(destination_folder)
        if Path(artifact.filename).name != artifact.filename or not artifact.filename.endswith(".h"):
            raise ValueError("Profile filename must be a plain .h filename")
        if not folder.is_dir():
            raise ValueError("Profile destination must be an existing folder")
        target = folder / artifact.filename
        if target.exists() and not replace:
            return None

        temporary_path: Path | None = None
        try:
            temporary_path = folder / f".{artifact.filename}.{uuid4().hex}.tmp"
            with temporary_path.open("xb") as stream:
                stream.write(artifact.text.encode("utf-8"))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, target)
            temporary_path = None
            return target
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
