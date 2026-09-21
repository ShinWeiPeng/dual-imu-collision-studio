from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path
from uuid import uuid4


class AtomicReplayCsvWriter:
    """Stream one Replay CSV through a same-folder temporary file."""

    @staticmethod
    def write(destination: Path | str, lines: Iterable[str]) -> str:
        target = Path(destination)
        if target.suffix.lower() != ".csv":
            raise ValueError("Replay destination must use the .csv extension")
        if not target.parent.is_dir():
            raise ValueError("Replay destination folder must exist")

        temporary_path: Path | None = None
        try:
            temporary_path = target.parent / f".{target.name}.{uuid4().hex}.tmp"
            with temporary_path.open("x", encoding="utf-8", newline="") as stream:
                for line in lines:
                    if not isinstance(line, str):
                        raise TypeError("Replay CSV stream must contain text lines")
                    stream.write(line)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, target)
            temporary_path = None
            return str(target)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)


class AtomicModelTextWriter:
    """Stream one Model TXT through a same-folder temporary file."""

    @staticmethod
    def write(destination: Path | str, lines: Iterable[str]) -> str:
        target = Path(destination)
        if target.suffix.lower() != ".txt":
            raise ValueError("Model destination must use the .txt extension")
        if not target.parent.is_dir():
            raise ValueError("Model destination folder must exist")

        temporary_path: Path | None = None
        try:
            temporary_path = target.parent / f".model-artifact-{uuid4().hex}.tmp"
            with temporary_path.open("xb") as stream:
                for line in lines:
                    if not isinstance(line, str):
                        raise TypeError("Model TXT stream must contain text lines")
                    if line and not line.endswith("\n"):
                        raise ValueError("Model TXT lines must be LF-delimited")
                    stream.write(line.encode("utf-8"))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, target)
            temporary_path = None
            return str(target)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
