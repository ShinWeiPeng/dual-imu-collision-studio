from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from ...domain.project_session.model import ProjectDocument, ProjectSourceReference


class AtomicProjectStore:
    @staticmethod
    def fingerprint(path: str | Path, worksheet: str = "") -> ProjectSourceReference:
        source = Path(path)
        digest = hashlib.sha256()
        size = 0
        with source.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
                size += len(chunk)
        return ProjectSourceReference(str(source), worksheet, size, digest.hexdigest())

    @staticmethod
    def read(path: str | Path) -> ProjectDocument:
        source = Path(path)

        def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"duplicate JSON key: {key}")
                result[key] = value
            return result

        try:
            text = source.read_text(encoding="utf-8")
            data = json.loads(
                text,
                object_pairs_hook=reject_duplicates,
                parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"non-finite JSON value: {value}")),
            )
        except UnicodeDecodeError as exc:
            raise ValueError("project must be UTF-8 JSON") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed project JSON: {exc.msg}") from exc
        if not isinstance(data, dict):
            raise ValueError("project root must be a JSON object")
        return ProjectDocument(data)

    @staticmethod
    def write(path: str | Path, document: ProjectDocument) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            rendered = json.dumps(
                document.data,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                indent=2,
                separators=(",", ": "),
            ) + "\n"
        except (TypeError, ValueError) as exc:
            raise ValueError("project must contain finite JSON values only") from exc
        temporary_path = destination.with_name(f".{destination.name}.{uuid4().hex}.tmp")
        try:
            with temporary_path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(rendered)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, destination)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise
        return destination
