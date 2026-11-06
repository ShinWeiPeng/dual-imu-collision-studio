from __future__ import annotations

import os
import stat
import json
import hashlib
import tempfile
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from uuid import uuid4
from datetime import datetime

from ...domain.data_workspace.model import (
    AnnotatedDatasetSnapshot,
    AnnotatedExportCancelled,
)
from ...domain.data_workspace.service import prepare_annotated_export


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


def _annotated_json_value(value):
    if isinstance(value, Mapping):
        return {key: _annotated_json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_annotated_json_value(item) for item in value]
    if hasattr(value, "item"):
        return value.item()
    return value


def _annotated_component(value, fallback):
    clean = re.sub(r"[^\w.-]+", "_", str(value), flags=re.UNICODE).strip(" ._-")
    return (clean or fallback)[:70]


def _annotated_cancel(cancelled):
    if cancelled and cancelled():
        raise AnnotatedExportCancelled("Annotated data export cancelled")


def _verify_annotated_staging(
    staging, parent, identity, created, *, allow_missing=False
):
    info = staging.lstat()
    if (
        staging.is_symlink()
        or staging.parent.resolve() != parent
        or staging.resolve(strict=True) != staging
        or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
        or (info.st_dev, info.st_ino) != identity
    ):
        raise OSError("Staging identity changed; refusing publication or cleanup")
    if not allow_missing and set(staging.iterdir()) != {path for path, _ in created}:
        raise OSError("Staging contents changed; refusing publication")
    for path, file_identity in created:
        try:
            info = path.lstat()
        except FileNotFoundError:
            if allow_missing:
                continue
            raise
        if (
            path.parent.resolve(strict=True) != staging
            or not stat.S_ISREG(info.st_mode)
            or getattr(info, "st_file_attributes", 0)
            & stat.FILE_ATTRIBUTE_REPARSE_POINT
            or (info.st_dev, info.st_ino) != file_identity
        ):
            raise OSError(
                "Created file identity changed; refusing publication or cleanup"
            )


class AtomicAnnotatedDataWriter:
    """Publish a whole new batch of independently usable recording JSONL files."""

    @staticmethod
    def write(
        parent,
        dataset: AnnotatedDatasetSnapshot,
        *,
        cancelled=None,
        progress=None,
        chunk_rows=4096,
    ) -> str:
        if type(chunk_rows) is not int or not 1 <= chunk_rows <= 65536:
            raise ValueError("JSONL chunk_rows must be between 1 and 65536")
        parent = Path(parent).resolve()
        if not parent.is_dir():
            raise ValueError("Annotated export parent folder must exist")
        dataset = prepare_annotated_export(dataset, cancelled=cancelled)
        _annotated_cancel(cancelled)
        stem = _annotated_component(Path(dataset.project_name).stem, "studio")
        stamp = datetime.fromisoformat(
            dataset.created_at.replace("Z", "+00:00")
        ).strftime("%Y%m%d_%H%M%S")
        batch_name = f"{stem}_annotated_{stamp}_{_annotated_component(dataset.export_id, 'job')[:8]}"
        target = parent / batch_name
        while target.exists():
            target = parent / (batch_name + "_" + uuid4().hex[:8])
        staging = None
        staging_identity = None
        created = []
        phase = "create-staging"
        current_name = "batch"
        total_rows = sum(len(entry.recording.time_s) for entry in dataset.recordings)
        rows_done = 0
        try:
            staging = Path(
                tempfile.mkdtemp(prefix=f".{stem}_annotated.tmp-", dir=parent)
            )
            info = staging.lstat()
            staging_identity = (info.st_dev, info.st_ino)
            for ordinal, entry in enumerate(dataset.recordings, 1):
                current_name = entry.name
                phase = "open"
                _annotated_cancel(cancelled)
                suffix = (
                    "_" + _annotated_component(entry.worksheet, "sheet")
                    if entry.worksheet
                    else ""
                )
                filename = f"r{ordinal:04d}_{_annotated_component(Path(entry.name).stem, 'recording')}{suffix}.annotated.jsonl"
                output = staging / filename
                digest = hashlib.sha256()
                annotation_count = 0
                block_count = 0
                recording = entry.recording
                count = len(recording.time_s)
                with output.open("xb") as stream:
                    info = os.fstat(stream.fileno())
                    created.append((output, (info.st_dev, info.st_ino)))

                    def emit(value, hashed=True):
                        encoded = (
                            json.dumps(
                                _annotated_json_value(value),
                                ensure_ascii=False,
                                allow_nan=False,
                                separators=(",", ":"),
                            )
                            + "\n"
                        ).encode("utf-8")
                        stream.write(encoded)
                        if hashed:
                            digest.update(encoded)

                    phase = "header"
                    emit(AtomicAnnotatedDataWriter._header(dataset, entry, ordinal))
                    phase = "annotations"
                    for origin, intervals in (
                        ("explicit", recording.annotations),
                        ("derived", entry.normal_intervals),
                    ):
                        for interval in intervals:
                            _annotated_cancel(cancelled)
                            emit(
                                {
                                    "type": "annotation",
                                    "origin": origin,
                                    "interval_id": interval.interval_id,
                                    "kind": interval.kind.value,
                                    "start_index": interval.start_index,
                                    "end_index": interval.end_index,
                                    "reason": interval.reason,
                                    "provisional": interval.provisional,
                                    "source_recording_id": interval.source_recording_id,
                                    "source_cycle_index": interval.source_cycle_index,
                                    "start_time_s": float(
                                        recording.time_s[interval.start_index]
                                    ),
                                    "last_included_time_s": float(
                                        recording.time_s[interval.end_index - 1]
                                    ),
                                    "end_boundary_time_s": float(
                                        recording.time_s[interval.end_index]
                                    )
                                    if interval.end_index < count
                                    else None,
                                    **(
                                        {
                                            "derived": True,
                                            "policy": "cycle-normal-collision-response-v1",
                                            "collision_response_window_s": 0.150,
                                        }
                                        if origin == "derived"
                                        else {}
                                    ),
                                }
                            )
                            annotation_count += 1
                    inserted = set(entry.interpolated_indices)
                    inserted_before = 0
                    data_start = int(entry.mapping["data_start_row"])
                    phase = "samples"
                    for start in range(0, count, chunk_rows):
                        _annotated_cancel(cancelled)
                        rows = []
                        for index in range(start, min(start + chunk_rows, count)):
                            interpolated = index in inserted
                            if interpolated:
                                source_row = None
                                inserted_before += 1
                            else:
                                source_row = data_start + index - inserted_before
                            row = [
                                index,
                                float(recording.time_s[index]),
                                source_row,
                                interpolated,
                                bool(recording.discontinuity_before[index])
                                if recording.discontinuity_before is not None
                                else False,
                            ]
                            row += [
                                float(
                                    getattr(recording, channel.sensor + "_imu")[
                                        index, channel.array_column
                                    ]
                                )
                                for channel in entry.channels
                            ]
                            rows.append(row)
                        emit({"type": "samples", "rows": rows})
                        block_count += 1
                        rows_done += len(rows)
                        if progress:
                            progress(rows_done, total_rows)
                    _annotated_cancel(cancelled)
                    emit(
                        {
                            "type": "end",
                            "complete": True,
                            "sample_count": count,
                            "annotation_count": annotation_count,
                            "sample_block_count": block_count,
                            "content_sha256": digest.hexdigest(),
                        },
                        hashed=False,
                    )
                    phase = "flush"
                    stream.flush()
                    phase = "fsync"
                    os.fsync(stream.fileno())
                    phase = "close"
            phase = "publish"
            current_name = "complete batch"
            _annotated_cancel(cancelled)
            # The chosen Windows target rejects a destination that appeared after admission.
            # Never replace existing batches; cancellation after publication cannot undo a save.
            if target.exists():
                raise FileExistsError(
                    f"Annotated export destination appeared: {target}"
                )
            _verify_annotated_staging(staging, parent, staging_identity, created)
            _annotated_cancel(cancelled)
            os.rename(staging, target)
            staging = None
            return str(target)
        except AnnotatedExportCancelled:
            raise
        except Exception as exc:
            raise OSError(f"Annotated export {current_name} [{phase}]: {exc}") from exc
        finally:
            if staging is not None:
                try:
                    _verify_annotated_staging(
                        staging, parent, staging_identity, created, allow_missing=True
                    )
                    for path, _ in created:
                        path.unlink(missing_ok=True)
                    staging.rmdir()
                except OSError as exc:
                    raise OSError(
                        f"Annotated export cleanup failed; remaining staging: {staging}: {exc}"
                    ) from exc

    @staticmethod
    def _header(dataset, entry, ordinal):
        recording = entry.recording
        columns = [
            {
                "column_id": "sample_index",
                "value_type": "integer",
                "unit": None,
                "unit_status": "not_applicable",
            },
            {
                "column_id": "time_s",
                "value_type": "number",
                "unit": "s",
                "unit_status": "known",
            },
            {
                "column_id": "source_data_row",
                "value_type": "integer_or_null",
                "unit": None,
                "unit_status": "not_applicable",
            },
            {
                "column_id": "is_interpolated",
                "value_type": "boolean",
                "unit": None,
                "unit_status": "not_applicable",
            },
            {
                "column_id": "discontinuity_before",
                "value_type": "boolean",
                "unit": None,
                "unit_status": "not_applicable",
            },
        ]
        columns += [
            {
                "column_id": channel.column_id,
                "value_type": "number",
                "sensor": channel.sensor,
                "signal_kind": channel.signal_kind,
                "axis": channel.axis,
                "source_column": channel.source_column,
                "source_mapping_role": channel.source_mapping_role,
                "configured_preprocessing": channel.configured_mode,
                "unit": channel.unit,
                "unit_status": "known" if channel.unit else "unknown",
                "unit_evidence": "recorded_metadata"
                if channel.unit
                else "not_recorded",
            }
            for channel in entry.channels
        ]
        return {
            "type": "header",
            "format": "studio-annotated-recording",
            "schema_version": 1,
            "export_id": dataset.export_id,
            "created_at": dataset.created_at,
            "studio_version": dataset.studio_version,
            "batch": {
                "recordings_total": len(dataset.recordings),
                "ordinal": ordinal,
                "excluded_recordings": [],
            },
            "confirmation": {
                "annotations_ready": True,
                "mapping_confirmed": True,
                "has_provisional": False,
                "annotation_validation": "valid",
            },
            "recording": {
                "recording_id": recording.recording_id,
                "display_name": entry.name,
                "source_basename": Path(recording.source_path).name,
                "worksheet": entry.worksheet,
                "row_count": len(recording.time_s),
                "sample_rate_hz": recording.sample_rate_hz,
                "robot_speed_mm_s": recording.condition.robot_speed_mm_s,
                "collision_offset_mm": recording.condition.collision_offset_mm,
                "single_sensor": recording.single_sensor,
            },
            "columns": columns,
            "mapping": entry.mapping,
            "provenance": {
                "data_view": "studio_imported_aligned",
                "time_origin_s": float(recording.time_s[0]),
                "source_sha256": entry.mapping.get("source_sha256"),
                "fingerprint_capture_stage": "mapping_confirmation"
                if entry.mapping.get("source_sha256")
                else "not_recorded",
                "source_reverified_at_export": False,
                "time_origin": "source_time_column"
                if entry.mapping.get("time_column")
                else "fixed_rate_generated",
                "import_warnings": entry.import_warnings,
                "interpolated_indices": entry.interpolated_indices,
                "source_data_row_index_base": 1,
                "source_data_row_note": "Table row, not a physical CSV line; null for inserted samples.",
                "discontinuity_origin": "imported"
                if recording.discontinuity_before is not None
                else "default_false",
            },
            "views": {
                "primary": {
                    "exported": True,
                    "channels": [c.column_id for c in entry.channels],
                },
                "other_mapped_or_application_filtered": {
                    "exported": False,
                    "reason": "not_in_primary_view",
                    "configuration": entry.mapping.get(
                        "signals", entry.mapping.get("preprocessing")
                    ),
                },
            },
            "policy": {
                "index_base": 0,
                "interval_convention": "[start_index,end_index)",
                "timeline": "studio_imported_aligned",
                "normal_policy": "cycle-normal-collision-response-v1",
                "collision_response_window_s": 0.150,
                "normal_response_deadline": "inclusive",
                "cycle_is_activity_label": False,
                "ignore_is_normal": False,
                "unlabelled_is_normal": False,
                "derived_normal_status": "available",
                "digest_scope": "UTF-8 bytes including LF from header to immediately before end",
            },
        }
