from __future__ import annotations

import faulthandler
import json
import os
import sys
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import TracebackType
from typing import TextIO

from PySide6.QtCore import QtMsgType, qInstallMessageHandler

from ...domain.process_diagnostics.model import DiagnosticStatus, LearningTimingEvidence


class ProcessDiagnostics:
    """Best-effort, privacy-bounded process diagnostics for the desktop adapter."""

    def __init__(
        self,
        directory: Path,
        *,
        max_log_bytes: int = 1_000_000,
        backup_count: int = 3,
    ) -> None:
        self._directory = Path(directory)
        self._log_path = self._directory / "diagnostics.log"
        self._fatal_path = self._directory / "fatal.log"
        self._state_path = self._directory / "session_state.json"
        self._max_log_bytes = max(256, int(max_log_bytes))
        self._backup_count = max(0, int(backup_count))
        self._lock = threading.RLock()
        self._fatal_file: TextIO | None = None
        self._previous_sys_hook = None
        self._previous_thread_hook = None
        self._previous_qt_handler = None
        self._handlers_installed = False
        self._available = self._prepare_directory()
        previous = self._read_state() if self._available else {}
        self._status = DiagnosticStatus(
            str(self._log_path) if self._available else "",
            self._summarize_unclean(previous),
        )

    @property
    def status(self) -> DiagnosticStatus:
        return self._status

    def begin_session(self) -> None:
        marker = {
            "clean_shutdown": False,
            "stage": "Application startup",
            "fraction": 0.0,
            "outer_round": 0,
            "inner_round": 0,
            "speed_mm_s": None,
            "offset_mm": None,
            "updated_at": self._now(),
        }
        self._write_state(marker)
        self._append("process_started")

    def install_handlers(self) -> None:
        if self._handlers_installed:
            return
        self._previous_sys_hook = sys.excepthook
        self._previous_thread_hook = threading.excepthook
        self._previous_qt_handler = qInstallMessageHandler(self._qt_message_handler)
        sys.excepthook = self._sys_exception_hook
        threading.excepthook = self._thread_exception_hook
        try:
            if self._available:
                self._rotate_if_needed(self._fatal_path, 0)
                self._fatal_file = self._fatal_path.open("a", encoding="utf-8")
                faulthandler.enable(self._fatal_file, all_threads=True)
        except (OSError, RuntimeError):
            self._fatal_file = None
        self._handlers_installed = True

    def restore_handlers(self) -> None:
        if not self._handlers_installed:
            return
        if self._previous_sys_hook is not None:
            sys.excepthook = self._previous_sys_hook
        if self._previous_thread_hook is not None:
            threading.excepthook = self._previous_thread_hook
        qInstallMessageHandler(self._previous_qt_handler)
        if self._fatal_file is not None:
            try:
                faulthandler.disable()
            except RuntimeError:
                pass
        self._handlers_installed = False

    def record_learning_started(self, numeric_type: str, recording_count: int) -> None:
        self._append(
            "learning_started",
            numeric_type=str(numeric_type)[:16],
            recording_count=max(0, int(recording_count)),
        )

    def record_learning_progress(
        self,
        stage: str,
        fraction: float,
        outer_round: int,
        inner_round: int,
        speed_mm_s: float | None,
        offset_mm: float | None,
    ) -> None:
        bounded_fraction = min(1.0, max(0.0, float(fraction)))
        marker = {
            "clean_shutdown": False,
            "stage": str(stage)[:64],
            "fraction": bounded_fraction,
            "outer_round": max(0, int(outer_round)),
            "inner_round": max(0, int(inner_round)),
            "speed_mm_s": self._finite_or_none(speed_mm_s),
            "offset_mm": self._finite_or_none(offset_mm),
            "updated_at": self._now(),
        }
        self._write_state(marker)
        self._append("learning_progress", **{key: value for key, value in marker.items() if key != "clean_shutdown"})

    def record_learning_finished(self, state: str, message: str) -> None:
        self._append("learning_finished", state=str(state)[:32], message=str(message)[:1000])

    def record_learning_timing(self, evidence: LearningTimingEvidence) -> None:
        attempts = [
            {
                "history_ms": max(0, int(history_ms)),
                "attempt": max(1, int(attempt)),
                "duration_s": max(0.0, float(duration_s)),
            }
            for history_ms, attempt, duration_s in evidence.worker_attempts[:8]
        ]
        self._append(
            "learning_timing",
            outer_round=max(0, int(evidence.outer_round)),
            inner_round=max(0, int(evidence.inner_round)),
            round_elapsed_s=max(0.0, float(evidence.round_elapsed_s)),
            training_elapsed_s=max(0.0, float(evidence.training_elapsed_s)),
            qualification_elapsed_s=max(0.0, float(evidence.qualification_elapsed_s)),
            total_elapsed_s=max(0.0, float(evidence.total_elapsed_s)),
            worker_attempts=attempts,
            process_tree_peak_rss_bytes=max(0, int(evidence.process_tree_peak_rss_bytes)),
            launch_available_ram_bytes=max(0, int(evidence.launch_available_ram_bytes)),
            worker_pids=[max(0, int(pid)) for pid in evidence.worker_pids[:8]],
        )

    def record_qt_message(self, level: str, source: str, line: int, message: str) -> None:
        self._append(
            "qt_message",
            level=str(level)[:32],
            source=Path(str(source)).name[:160] if source else "",
            line=max(0, int(line)),
            message=str(message)[:1500],
        )

    def record_python_exception(
        self,
        exception_type: type[BaseException],
        exception: BaseException,
        trace: TracebackType | None,
        *,
        thread_name: str = "main",
    ) -> None:
        rendered = "".join(traceback.format_exception(exception_type, exception, trace))[-8000:]
        self._append(
            "python_exception",
            exception_type=exception_type.__name__[:160],
            message=str(exception)[:1000],
            thread=thread_name[:160],
            traceback=rendered,
        )

    def mark_clean_shutdown(self) -> None:
        marker = self._read_state()
        marker["clean_shutdown"] = True
        marker["updated_at"] = self._now()
        self._write_state(marker)
        self._append("process_finished", state="clean")

    def close(self) -> None:
        self.restore_handlers()
        if self._fatal_file is not None:
            try:
                self._fatal_file.close()
            except OSError:
                pass
            self._fatal_file = None

    def _sys_exception_hook(self, kind, value, trace) -> None:
        self.record_python_exception(kind, value, trace)
        if self._previous_sys_hook is not None:
            self._previous_sys_hook(kind, value, trace)

    def _thread_exception_hook(self, args) -> None:
        self.record_python_exception(
            args.exc_type,
            args.exc_value,
            args.exc_traceback,
            thread_name=getattr(args.thread, "name", "worker"),
        )
        if self._previous_thread_hook is not None:
            self._previous_thread_hook(args)

    def _qt_message_handler(self, mode, context, message) -> None:
        level = {
            QtMsgType.QtDebugMsg: "debug",
            QtMsgType.QtInfoMsg: "info",
            QtMsgType.QtWarningMsg: "warning",
            QtMsgType.QtCriticalMsg: "critical",
            QtMsgType.QtFatalMsg: "fatal",
        }.get(mode, "unknown")
        self.record_qt_message(level, getattr(context, "file", "") or "", getattr(context, "line", 0), message)
        if self._previous_qt_handler is not None:
            self._previous_qt_handler(mode, context, message)
        elif level in {"warning", "critical", "fatal"}:
            sys.stderr.write(f"{level}: {message}\n")

    def _append(self, event: str, **fields: object) -> None:
        if not self._available:
            return
        record = {"timestamp": self._now(), "event": event, **fields}
        encoded = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        try:
            with self._lock:
                self._rotate_if_needed(self._log_path, len(encoded))
                with self._log_path.open("ab") as stream:
                    stream.write(encoded)
                    stream.flush()
        except OSError:
            pass

    def _rotate_if_needed(self, path: Path, incoming_bytes: int) -> None:
        if not path.exists() or path.stat().st_size + incoming_bytes <= self._max_log_bytes:
            return
        if self._backup_count == 0:
            path.unlink(missing_ok=True)
            return
        oldest = path.with_name(f"{path.name}.{self._backup_count}")
        oldest.unlink(missing_ok=True)
        for index in range(self._backup_count - 1, 0, -1):
            source = path.with_name(f"{path.name}.{index}")
            if source.exists():
                source.replace(path.with_name(f"{path.name}.{index + 1}"))
        path.replace(path.with_name(f"{path.name}.1"))

    def _write_state(self, value: dict[str, object]) -> None:
        if not self._available:
            return
        temporary = self._state_path.with_suffix(".tmp")
        try:
            with self._lock:
                temporary.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
                os.replace(temporary, self._state_path)
        except OSError:
            try:
                temporary.unlink(missing_ok=True)
                self._state_path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
            except OSError:
                pass

    def _read_state(self) -> dict[str, object]:
        try:
            value = json.loads(self._state_path.read_text(encoding="utf-8"))
            return value if isinstance(value, dict) else {}
        except (OSError, ValueError):
            return {}

    def _prepare_directory(self) -> bool:
        try:
            self._directory.mkdir(parents=True, exist_ok=True)
            return True
        except OSError:
            return False

    @staticmethod
    def _summarize_unclean(marker: dict[str, object]) -> str:
        if not marker or marker.get("clean_shutdown") is True:
            return ""
        stage = str(marker.get("stage") or "Unknown stage")
        percent = round(float(marker.get("fraction") or 0.0) * 100)
        parts = [f"Previous run ended unexpectedly during {stage} at {percent}%"]
        speed = marker.get("speed_mm_s")
        offset = marker.get("offset_mm")
        if speed is not None:
            parts.append(f"{float(speed):g} mm/s")
        if offset is not None:
            parts.append(f"{float(offset):g} mm")
        return " · ".join(parts)

    @staticmethod
    def _finite_or_none(value: float | None) -> float | None:
        if value is None:
            return None
        result = float(value)
        return result if result == result and abs(result) != float("inf") else None

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")
