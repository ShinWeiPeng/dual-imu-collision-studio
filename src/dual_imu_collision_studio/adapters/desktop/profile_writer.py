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
        if Path(
            artifact.filename
        ).name != artifact.filename or not artifact.filename.endswith(".h"):
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

    @staticmethod
    def write_json(
        destination: Path | str, text: str, *, replace: bool = False
    ) -> Path:
        """Commit complete UTF-8 JSON; create-only mode cannot overwrite a racing file."""
        target = Path(destination)
        name = target.name
        reserved = {"CON", "PRN", "AUX", "NUL"} | {
            f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
        }
        if (
            not target.stem
            or name == ".json"
            or target.suffix.lower() != ".json"
            or name.endswith((" ", "."))
            or any(ord(char) < 32 or char in '<>:"/\\|?*' for char in name)
            or name.split(".")[0].rstrip().upper() in reserved
        ):
            raise ValueError("Choose a valid .json filename")
        if not target.parent.is_dir():
            raise ValueError("JSON destination must be an existing folder")
        temporary = target.parent / f".model-json-{uuid4().hex}.tmp"
        try:
            with temporary.open("xb") as stream:
                stream.write(text.encode("utf-8"))
                stream.flush()
                os.fsync(stream.fileno())
            if replace:
                os.replace(temporary, target)
            elif os.name == "nt":
                # Windows rename is atomic and refuses an existing destination,
                # including on FAT/exFAT where hard links are unavailable.
                os.rename(temporary, target)
            else:
                os.link(temporary, target)
            return target
        finally:
            temporary.unlink(missing_ok=True)
