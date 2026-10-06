from __future__ import annotations

from ...domain.learning.preprocessing import (
    SingleImuSettings,
    FilterStageSpec,
    design_filter,
    settings_from_data,
    settings_to_data,
    cascade_response,
    preprocess,
)
from ...domain.learning.self_imu import FrozenSelfImuModel, prepare_recording

import math
import re
import time
from datetime import datetime
from dataclasses import asdict, replace
from pathlib import Path
from threading import Event

import numpy as np
import psutil
from PySide6.QtCore import (
    Property,
    QObject,
    QRunnable,
    QThreadPool,
    QTimer,
    QUrl,
    Signal,
    Slot,
)

from ...domain.data_workspace.model import (
    ActivityKind,
    AnnotationInterval,
    AnnotationTemplate,
    ColumnMapping,
    Recording,
    TestCondition,
    WorkspaceSnapshot,
)
from ...domain.data_workspace.service import WorkspaceService
from ...domain.learning.model import (
    LearningDataset,
    LearningSettings,
    RunProvenance,
    RoundProvenance,
    KernelTrainingEvidence,
    CrossValidationPlan,
    CrossValidationFold,
    CycleFoldGroup,
    ConditionLoss,
    LearningInterval,
    LearningRecording as TrainingRecording,
    LearningRequest,
    LearningCancelled,
    TrainingMode,
    LearningProgress,
    QualificationResult,
    QualifiedCandidate,
    RecordingQualification,
    DetectorConfig,
    FrozenFirModel,
    FrozenMlpModel,
    HistorySpec,
)
from ...domain.learning.service import LearningService
from ...domain.profile_export.model import (
    ConditionCoverage,
    ProfileExportRequest,
    SemanticProfile,
)
from ...domain.profile_export.service import ProfileExportService
from ...domain.project_session.model import ProjectDocument
from ...domain.project_session.service import ProjectSessionService
from ...domain.process_diagnostics.contracts import DiagnosticsPort, NullDiagnostics
from ...domain.process_diagnostics.model import DiagnosticStatus, LearningTimingEvidence
from .profile_writer import AtomicProfileWriter
from .project_store import AtomicProjectStore
from .replay_writer import AtomicModelTextWriter, AtomicReplayCsvWriter
from ..parallel.learning_workers import SpawnLearningExecutor
from ..tabular.reader import TabularReader


class _LearningWorkerSignals(QObject):
    progressed = Signal(object)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal(object)


class LearningWorker(QRunnable):
    def __init__(
        self, service: LearningService, request: LearningRequest, requests=None
    ) -> None:
        super().__init__()
        self.signals = _LearningWorkerSignals()
        self._service = service
        self._request = request
        self._requests = dict(requests or {})
        self._cancelled = Event()

    def cancel(self) -> None:
        self._cancelled.set()

    def run(self) -> None:
        if self._requests:
            self._run_batch()
            return
        try:
            result = self._service.learn_and_qualify(
                self._request.workspace,
                self._request.numeric_type,
                self.signals.progressed.emit,
                self._cancelled.is_set,
                settings=self._request.settings,
            )
        except LearningCancelled as exc:
            self.signals.cancelled.emit(exc.result)
        except InterruptedError:
            self.signals.cancelled.emit(QualificationResult(()))
        except Exception as exc:
            self.signals.failed.emit(str(exc))
        else:
            self.signals.completed.emit(result)

    def _run_batch(self):
        candidates, diagnostics, unavailable, provenance = [], [], [], {}

        def retain(key, result):
            identities = []
            for incoming, destination in (
                (result.candidates, candidates),
                (result.diagnostic_candidates, diagnostics),
            ):
                for candidate in incoming:
                    identity = f"k{len(candidates) + len(diagnostics) + 1:03d}"
                    identities.append(identity)
                    destination.append(replace(candidate, candidate_id=identity))
            unavailable.extend(result.unavailable_rounds)
            provenance[key] = (
                result.run_provenance,
                result.family_provenance,
                tuple(identities),
            )

        def snapshot():
            return QualificationResult(
                tuple(candidates), tuple(diagnostics), tuple(unavailable)
            )

        for key, request in self._requests.items():
            if self._cancelled.is_set():
                self.signals.cancelled.emit((snapshot(), provenance))
                return

            def publish(progress):
                self.signals.progressed.emit(
                    replace(progress, message=key.upper() + ": " + progress.message)
                )

            try:
                result = self._service.learn_and_qualify(
                    request.workspace,
                    request.numeric_type,
                    publish,
                    self._cancelled.is_set,
                    settings=request.settings,
                )
            except LearningCancelled as exc:
                retain(key, exc.result)
                self.signals.cancelled.emit((snapshot(), provenance))
                return
            except InterruptedError:
                self.signals.cancelled.emit((snapshot(), provenance))
                return
            except Exception as exc:
                self.signals.failed.emit(key.upper() + ": " + str(exc))
                return
            retain(key, result)
        self.signals.completed.emit((snapshot(), provenance))


class _ReplayCsvExportSignals(QObject):
    completed = Signal(str)
    failed = Signal(str)


class _ReplayCsvExportWorker(QRunnable):
    def __init__(
        self,
        service: LearningService,
        recording: TrainingRecording,
        candidate: QualifiedCandidate,
        destination: Path,
    ) -> None:
        super().__init__()
        self.signals = _ReplayCsvExportSignals()
        self._service = service
        self._recording = recording
        self._candidate = candidate
        self._destination = destination

    def run(self) -> None:
        try:
            evidence = self._service.replay_candidate(
                self._recording,
                self._candidate,
            )
            saved = AtomicReplayCsvWriter.write(
                self._destination,
                self._service.iter_replay_csv_lines(evidence),
            )
        except Exception as exc:
            self.signals.failed.emit(str(exc))
        else:
            self.signals.completed.emit(str(saved))


class _ModelTextExportSignals(QObject):
    completed = Signal(str)
    failed = Signal(str)


class _ModelTextExportWorker(QRunnable):
    def __init__(
        self,
        service: LearningService,
        candidate: QualifiedCandidate,
        sample_rate_hz: float,
        destination: Path,
    ) -> None:
        super().__init__()
        self.signals = _ModelTextExportSignals()
        self._service = service
        self._candidate = candidate
        self._sample_rate_hz = sample_rate_hz
        self._destination = destination

    def run(self) -> None:
        try:
            saved = AtomicModelTextWriter.write(
                self._destination,
                self._service.iter_model_text_lines(
                    self._candidate, sample_rate_hz=self._sample_rate_hz
                ),
            )
        except Exception as exc:
            self.signals.failed.emit(str(exc))
        else:
            self.signals.completed.emit(str(saved))


class _ProjectSourceMissing(FileNotFoundError):
    def __init__(self, recording_index: int, source_name: str) -> None:
        super().__init__(f"source file is missing: {source_name}")
        self.recording_index = recording_index
        self.source_name = source_name


class StudioController(QObject):
    stateChanged = Signal()

    STAGES = (
        "Import & Map",
        "Annotate & Classify",
        "Train",
        "Replay & Qualify",
        "Export Profile",
    )

    def __init__(self, diagnostics: DiagnosticsPort | None = None) -> None:
        super().__init__()
        self._diagnostics = diagnostics or NullDiagnostics()
        self._diagnostic_status = getattr(
            self._diagnostics, "status", DiagnosticStatus()
        )
        self._selected_stage = 0
        self._selected_recording = -1
        self._project_path: Path | None = None
        self._project_dirty = False
        self._pending_project_document: ProjectDocument | None = None
        self._pending_project_path: Path | None = None
        self._pending_project_overrides: dict[int, str] = {}
        self._pending_project_missing_index = -1
        self._recordings: list[dict[str, object]] = []
        self._samples: dict[int, object] = {}
        self._annotations: dict[int, tuple[AnnotationInterval, ...]] = {}
        self._annotation_templates: dict[float, AnnotationTemplate] = {}
        self._annotation_undo: dict[int, list[tuple[AnnotationInterval, ...]]] = {}
        self._annotation_redo: dict[int, list[tuple[AnnotationInterval, ...]]] = {}
        self._reviewed_duplicate_keys: set[tuple[float, float, float]] = set()
        self._selected_annotation = -1
        self._selected_annotations: set[int] = set()
        self._next_annotation_id = 1
        self._confirmed_workspace: WorkspaceSnapshot | None = None
        self._active_learning_request: LearningRequest | None = None
        self._numeric_type = ""
        self._training_algorithms = ("fir",)
        self._training_sources = {"fir": "raw", "mlp": "raw", "var": "internal"}
        self._training_selection_explicit = False
        self._batch_requests = {}
        self._batch_source_choices = {}
        self._batch_provenance = {}
        self._learning_settings = LearningSettings()
        self._learning_family_provenance = ()
        self._learning_run_provenance = None
        self._kernel_training_evidence = {}
        self._learning_setting_notices = ()
        self._annotations_ready = False
        self._annotation_blocker_message = ""
        self._run_state = "Ready"
        self._progress = 0.0
        self._status_message = "Import CSV or XLSX data to begin."
        self._run_started_monotonic: float | None = None
        self._run_finished_monotonic: float | None = None
        self._run_started_at: str = ""
        self._run_finished_at: str = ""
        self._run_failure_reason: str = ""
        self._stage_name: str = ""
        self._stage_started_monotonic: float | None = None
        self._stage_finished_monotonic: float | None = None
        self._stage_elapsed_totals: dict[str, float] = {
            "Training": 0.0,
            "Qualification": 0.0,
            "Fallback": 0.0,
        }
        self._training_active_offsets: tuple[float, ...] = ()
        self._training_excluded_offsets: tuple[float, ...] = ()
        self._training_speeds: tuple[float, ...] = ()
        self._training_supplied_offsets: tuple[float, ...] = ()
        self._training_supplied_speeds: tuple[float, ...] = ()
        self._training_round = (0, 0)
        self._training_current_speed: float | None = None
        self._training_current_offset: float | None = None
        self._training_execution_summaries: dict[tuple[int, int], str] = {}
        self._training_log_entries: list[dict[str, object]] = []
        self._training_log_discarded_count = 0
        self._run_timer = QTimer(self)
        self._run_timer.setInterval(1000)
        self._run_timer.timeout.connect(self._emit_run_timing)
        self._header_format = "C++17"
        self._header_preview = ""
        self._profiles: list[SemanticProfile] = []
        self._retained_candidates: list[QualifiedCandidate] = []
        self._diagnostic_candidate_ids: set[str] = set()
        self._selected_kernel_ids: set[str] = set()
        self._preview_kernel_id = ""
        self._replay_recording_index = 0
        self._pending_export_folder: Path | None = None
        self._pending_export_artifacts = ()
        self._pending_export_conflicts: list[str] = []
        self._approved_replacements: set[str] = set()
        self._reader = TabularReader()
        self._workspace = WorkspaceService()
        self._learning = LearningService(learning_executor=SpawnLearningExecutor())
        self._export = ProfileExportService()
        self._writer = AtomicProfileWriter()
        self._project_service = ProjectSessionService()
        self._project_store = AtomicProjectStore()
        self._learning_worker: LearningWorker | None = None
        self._replay_export_worker: _ReplayCsvExportWorker | None = None
        self._model_export_worker: _ModelTextExportWorker | None = None

    @Property(bool, notify=stateChanged)
    def projectDirty(self) -> bool:
        return self._project_dirty

    @Property(bool, notify=stateChanged)
    def replayExportActive(self) -> bool:
        return self._replay_export_worker is not None

    @Property(bool, notify=stateChanged)
    def modelExportActive(self) -> bool:
        return self._model_export_worker is not None

    @Property(str, notify=stateChanged)
    def projectPath(self) -> str:
        return str(self._project_path) if self._project_path is not None else ""

    @Property(str, notify=stateChanged)
    def projectName(self) -> str:
        if self._project_path is None:
            return "Untitled project"
        return self._project_path.name

    @Property(bool, notify=stateChanged)
    def projectRelinkRequired(self) -> bool:
        return (
            self._pending_project_document is not None
            and self._pending_project_missing_index >= 0
        )

    @Property(str, notify=stateChanged)
    def projectRelinkSource(self) -> str:
        if not self.projectRelinkRequired:
            return ""
        raw = self._pending_project_document.data["recordings"][
            self._pending_project_missing_index
        ]
        return Path(str(raw["source"]["path"])).name

    @Property("QVariantList", notify=stateChanged)
    def stages(self) -> list[dict[str, object]]:
        completed = self._completed_stage()
        maximum_available = self._maximum_available_stage()
        return [
            {
                "name": name,
                "number": index + 1,
                "state": "complete"
                if index < completed
                else "current"
                if index == self._selected_stage
                else "pending",
                "enabled": index <= maximum_available,
            }
            for index, name in enumerate(self.STAGES)
        ]

    @Property(int, notify=stateChanged)
    def selectedStage(self) -> int:
        return self._selected_stage

    @Property("QVariantList", notify=stateChanged)
    def recordings(self) -> list[dict[str, object]]:
        values = [
            float(row["sampleRateValue"])
            for row in self._recordings
            if "sampleRateValue" in row
        ]
        session_rate = float(np.median(values)) if values else None
        duplicate_groups = self._duplicate_condition_groups()
        result: list[dict[str, object]] = []
        for row in self._recordings:
            presented = dict(row)
            if session_rate is None or "sampleRateValue" not in row:
                presented["rateStatus"] = "Rate pending"
            else:
                value = float(row["sampleRateValue"])
                presented["rateStatus"] = (
                    "Rate compatible"
                    if abs(value - session_rate) / session_rate <= 0.005
                    else "Rate mismatch"
                )
            key = self._condition_key(row)
            if key in duplicate_groups:
                presented["duplicateStatus"] = (
                    "Intentional repeat"
                    if key in self._reviewed_duplicate_keys
                    else "Review duplicate"
                )
            else:
                presented["duplicateStatus"] = "Unique condition"
            result.append(presented)
        return result

    @Property(int, notify=stateChanged)
    def selectedRecording(self) -> int:
        return self._selected_recording

    @Property(str, notify=stateChanged)
    def selectedRecordingName(self) -> str:
        if self._selected_recording < 0:
            return "No recording selected"
        return str(self._recordings[self._selected_recording]["name"])

    @Property("QVariantList", notify=stateChanged)
    def selectedColumns(self) -> list[str]:
        if self._selected_recording < 0:
            return []
        return list(self._recordings[self._selected_recording].get("columns", []))

    @Property("QVariantList", notify=stateChanged)
    def selectedPreviewRows(self) -> list[dict[str, object]]:
        if self._selected_recording < 0:
            return []
        return list(self._recordings[self._selected_recording].get("previewRows", []))

    @Property("QVariantList", notify=stateChanged)
    def proposedInternalColumns(self) -> list[str]:
        return self._proposed_axis_columns("Internal Accel")

    @Property("QVariantList", notify=stateChanged)
    def proposedExternalColumns(self) -> list[str]:
        return self._proposed_axis_columns("External Accel")

    def _proposed_axis_columns(self, prefix: str) -> list[str]:
        if self._selected_recording >= 0:
            mapping = self._recordings[self._selected_recording].get("mapping") or {}
            if mapping.get("single_sensor"):
                role = (
                    "internal_columns"
                    if prefix == "Internal Accel"
                    else "external_columns"
                )
                saved = mapping.get(role, [])
                if len(saved) == 3:
                    return list(saved)
        columns = self.selectedColumns
        return [
            next(
                (
                    column
                    for column in columns
                    if column.casefold() == f"{prefix} {axis}".casefold()
                ),
                "",
            )
            for axis in ("X", "Y", "Z")
        ]

    @Property(int, notify=stateChanged)
    def selectedHeaderRow(self) -> int:
        if self._selected_recording < 0:
            return 1
        return int(
            self._recordings[self._selected_recording].get("suggestedHeaderRow", 1)
        )

    @Property(int, notify=stateChanged)
    def selectedDataStartRow(self) -> int:
        if self._selected_recording < 0:
            return 2
        return int(
            self._recordings[self._selected_recording].get("suggestedDataStartRow", 2)
        )

    @Property(bool, notify=stateChanged)
    def selectedHasTimeColumn(self) -> bool:
        return any("time" in value.lower() for value in self.selectedColumns)

    @Property("QVariantList", notify=stateChanged)
    def waveformChannels(self) -> list[list[float]]:
        return self._waveform_channels("internal_imu")

    @Property("QVariantList", notify=stateChanged)
    def externalWaveformChannels(self) -> list[list[float]]:
        return self._waveform_channels("external_imu")

    def _waveform_channels(self, source_name: str) -> list[list[float]]:
        samples = self._samples.get(self._selected_recording)
        if samples is None:
            phase = np.linspace(0.0, 4.0 * math.pi, 420)
            return [
                np.sin(phase).tolist(),
                (0.7 * np.sin(phase + 0.8)).tolist(),
                (0.45 * np.cos(phase * 0.7)).tolist(),
            ]
        if getattr(samples, source_name) is None:
            return [[], [], []]
        values = np.asarray(getattr(samples, source_name))
        indexes = np.linspace(0, len(values) - 1, min(800, len(values)), dtype=int)
        return [values[indexes, axis].tolist() for axis in range(3)]

    @Slot(str, float, float, int, result="QVariantMap")
    def waveformViewport(
        self,
        source_name: str,
        viewport_start: float,
        viewport_end: float,
        plot_width: int,
    ) -> dict[str, object]:
        if source_name not in {"internal_imu", "external_imu"}:
            raise ValueError("waveform source must be internal_imu or external_imu")
        samples = self._samples.get(self._selected_recording)
        if samples is None:
            values = np.asarray(
                self._waveform_channels(source_name), dtype=np.float64
            ).T
        elif getattr(samples, source_name) is None:
            return {
                "mode": "raw",
                "positions": [],
                "minimums": [[], [], []],
                "maximums": [[], [], []],
                "means": [[], [], []],
            }
        else:
            values = np.asarray(getattr(samples, source_name), dtype=np.float64)
        projection = self._workspace.project_waveform_viewport(
            values, viewport_start, viewport_end, plot_width
        )
        return {
            "mode": projection.mode,
            "positions": list(projection.positions),
            "minimums": [list(channel) for channel in projection.minimums],
            "maximums": [list(channel) for channel in projection.maximums],
            "means": [list(channel) for channel in projection.means],
        }

    @Property("QVariantList", notify=stateChanged)
    def annotationIntervals(self) -> list[dict[str, object]]:
        if self._selected_recording < 0:
            return []
        sample_count = self._selected_sample_count()
        if sample_count == 0:
            return []
        lanes = {
            ActivityKind.CYCLE: 0,
            ActivityKind.PICK: 1,
            ActivityKind.PUT: 2,
            ActivityKind.FORK_COLLISION: 3,
            ActivityKind.IGNORE: 4,
        }
        values = self._annotations.get(self._selected_recording, ())
        row = self._recordings[self._selected_recording]
        speed = row.get("speed")
        template = (
            self._annotation_templates.get(float(speed)) if speed is not None else None
        )
        selected_recording_id = self._recording_id_for_index(
            self._selected_recording, row
        )
        confirmed_cycles = [
            item
            for item in values
            if item.kind is ActivityKind.CYCLE and not item.provisional
        ]
        anchor = (
            confirmed_cycles[0]
            if template is not None
            and selected_recording_id != template.source_recording_id
            and len(confirmed_cycles) == 1
            and any(
                item.kind is ActivityKind.CYCLE and item.provisional for item in values
            )
            else None
        )
        return [
            {
                "index": index,
                "kind": interval.kind.value,
                "lane": lanes[interval.kind],
                "startFraction": interval.start_index / sample_count,
                "endFraction": interval.end_index / sample_count,
                "reason": interval.reason or "",
                "selected": index in self._selected_annotations,
                "provisional": interval.provisional,
                "sourceRecordingId": interval.source_recording_id or "",
                "sourceCycleIndex": interval.source_cycle_index
                if interval.source_cycle_index is not None
                else -1,
                "anchor": interval is anchor,
                "intervalId": interval.interval_id,
            }
            for index, interval in enumerate(values)
        ]

    @Property(int, notify=stateChanged)
    def selectedAnnotationCount(self) -> int:
        return len(self._selected_annotations)

    @Property("QVariantList", notify=stateChanged)
    def interpolationMarkers(self) -> list[dict[str, object]]:
        samples = self._samples.get(self._selected_recording)
        if samples is None:
            return []
        indices = samples.interpolated_indices
        markers: list[dict[str, object]] = []
        for index in indices:
            if markers and index == markers[-1]["endIndex"]:
                markers[-1]["endIndex"] = index + 1
                markers[-1]["count"] += 1
            else:
                markers.append({"startIndex": index, "endIndex": index + 1, "count": 1})
        count = len(samples.time_s)
        for marker in markers:
            marker["startFraction"] = marker["startIndex"] / count
            marker["endFraction"] = marker["endIndex"] / count
        return markers

    @Property(str, notify=stateChanged)
    def annotationProgressText(self) -> str:
        total = len(self._recordings)
        if total == 0 or self._selected_recording < 0:
            return "No recording selected"
        completed = sum(
            not self._annotation_validation_error(index) for index in range(total)
        )
        values = self._annotations.get(self._selected_recording, ())
        counts = {
            kind: sum(item.kind is kind for item in values)
            for kind in (
                ActivityKind.CYCLE,
                ActivityKind.PICK,
                ActivityKind.PUT,
                ActivityKind.FORK_COLLISION,
            )
        }
        name = str(
            self._recordings[self._selected_recording].get(
                "name", f"Recording {self._selected_recording + 1}"
            )
        )
        return (
            f"Recording {self._selected_recording + 1}/{total}: {name} · "
            f"Completed {completed}/{total} · Cycle {counts[ActivityKind.CYCLE]} · "
            f"Pick {counts[ActivityKind.PICK]} · Put {counts[ActivityKind.PUT]} · "
            f"Collision {counts[ActivityKind.FORK_COLLISION]}"
        )

    @Property("QVariantList", notify=stateChanged)
    def derivedNormalIntervals(self) -> list[dict[str, float]]:
        if self._confirmed_workspace is None or self._selected_recording < 0:
            return []
        recording = self._confirmed_workspace.recordings[self._selected_recording]
        sample_count = len(recording.time_s)
        return [
            {
                "startFraction": interval.start_index / sample_count,
                "endFraction": interval.end_index / sample_count,
            }
            for interval in self._workspace.derive_normal_intervals(
                recording,
                collision_response_window_s=self._learning.COLLISION_DETECTION_WINDOW_S,
            )
        ]

    @Property(bool, notify=stateChanged)
    def canUndoAnnotation(self) -> bool:
        return bool(self._annotation_undo.get(self._selected_recording))

    @Property(bool, notify=stateChanged)
    def canRedoAnnotation(self) -> bool:
        return bool(self._annotation_redo.get(self._selected_recording))

    @Property("QVariantMap", notify=stateChanged)
    def learningSettings(self):
        return self._settings_mapping(self._learning_settings)

    @staticmethod
    def _settings_mapping(settings: LearningSettings) -> dict[str, object]:
        values = asdict(settings)
        values["training_mode"] = settings.training_mode.value
        values["fixed_history_ms"] = list(settings.fixed_history_ms)
        values["fixed_ridge_alphas"] = list(settings.fixed_ridge_alphas)
        values["model_families"] = list(settings.model_families)
        values["mlp_history_ms"] = list(settings.mlp_history_ms)
        values["mlp_layer_widths"] = [list(v) for v in settings.mlp_layer_widths]
        values["mlp_l2"] = list(settings.mlp_l2)
        return values

    @Property(bool, notify=stateChanged)
    def modelSelectionsReady(self):
        return self._learning_settings.selections_ready

    @Property(str, notify=stateChanged)
    def mlpCandidateCountText(self):
        settings = self._learning_settings
        count = settings.mlp_parameter_count
        rate = self._session_rate()
        if rate is not None and settings.mlp_history_ms:
            histories = len(
                self._learning.build_candidate_plan(
                    rate, replace(settings, model_families=("mlp",))
                ).histories
            )
            count = count // len(settings.mlp_history_ms) * histories
        count_text = (
            str(count)
            if count.bit_length() < 3300
            else f">10^{int((count.bit_length() - 1) * math.log10(2))}"
        )
        return f"{count_text} MLP parameter combinations × {settings.n_fold} folds per round"

    @Slot(int, result=bool)
    def setMlpDepth(self, depth):
        if type(depth) is not int or depth < 1:
            return False
        # Budget the dynamic Qt controls before allocating per-layer UI state.
        if depth * 65536 > psutil.virtual_memory().available * 0.05:
            self._status_message = "Requested layer controls exceed available UI memory; reduce hidden depth."
            self.stateChanged.emit()
            return False
        widths = self._learning_settings.mlp_layer_widths
        try:
            return self.setLearningSetting(
                "mlp_layer_widths", widths[:depth] + ((),) * max(0, depth - len(widths))
            )
        except MemoryError:
            self._status_message = "Insufficient memory for the requested hidden depth"
            self.stateChanged.emit()
            return False

    @Slot(str, bool, result=bool)
    def setModelFamilySelected(self, family, checked):
        values = set(self._learning_settings.model_families)
        values.add(family) if checked else values.discard(family)
        return self.setLearningSetting("model_families", tuple(values))

    @Slot(str, int, float, bool, result=bool)
    def setMlpSelected(self, field, layer, value, checked):
        if field not in ("mlp_history_ms", "mlp_l2", "mlp_layer_widths"):
            return False
        raw = getattr(self._learning_settings, field)
        if field == "mlp_layer_widths":
            if not 0 <= layer < len(raw):
                return False
            values = set(raw[layer])
        else:
            values = set(raw)
        values.add(value) if checked else values.discard(value)
        if field == "mlp_layer_widths":
            raw = list(raw)
            raw[layer] = tuple(values)
        else:
            raw = tuple(values)
        return self.setLearningSetting(field, raw)

    @Property("QVariantList", constant=True)
    def fixedHistoryOptions(self):
        return list(LearningSettings.FIXED_HISTORY_OPTIONS_MS)

    @Property("QVariantList", constant=True)
    def fixedRidgeAlphaOptions(self):
        return list(LearningSettings.FIXED_RIDGE_ALPHA_OPTIONS)

    @Property(bool, notify=stateChanged)
    def fixedGridSelectionsReady(self) -> bool:
        return bool(
            self._learning_settings.fixed_history_ms
            and self._learning_settings.fixed_ridge_alphas
        )

    @Property(bool, notify=stateChanged)
    def learningSettingsLocked(self):
        return self._learning_worker is not None or self._run_state in {
            "Learning",
            "Qualifying",
            "Refining Speed Range",
            "Cancelling",
        }

    @Slot(str, "QVariant", result=bool)
    def setLearningSetting(self, name, value):
        if self.learningSettingsLocked or name not in self._settings_mapping(
            self._learning_settings
        ):
            return False
        try:
            proposed = replace(self._learning_settings, **{name: value})
        except (TypeError, ValueError) as exc:
            self._status_message = str(exc)
            self.stateChanged.emit()
            return False
        self._learning_settings = proposed
        self._mark_project_dirty()
        self.stateChanged.emit()
        return True

    @staticmethod
    def _settings_from_project(raw):
        values = raw if isinstance(raw, dict) else {}
        settings = LearningSettings()
        notices = []
        defaults = StudioController._settings_mapping(settings)
        extension_fields = {
            "training_mode",
            "fixed_history_ms",
            "fixed_ridge_alphas",
            "model_families",
            "mlp_history_ms",
            "mlp_layer_widths",
            "mlp_l2",
        }
        for name, default in defaults.items():
            try:
                if name not in values:
                    raise ValueError("missing")
                settings = replace(settings, **{name: values[name]})
            except (TypeError, ValueError):
                if name not in extension_fields or name in values:
                    notices.append(f"{name} restored to default {default}")
        return settings, tuple(notices)

    @staticmethod
    def _captured_settings_from_project(raw):
        values = dict(raw)
        if "training_mode" not in values:
            values.update(
                {
                    "training_mode": TrainingMode.OPTIMIZED,
                    "fixed_history_ms": (),
                    "fixed_ridge_alphas": (),
                }
            )
        return LearningSettings(**values)

    @staticmethod
    def _fold_plan_from_project(raw):
        return CrossValidationPlan(
            raw["fold_count"],
            raw["evidence_level"],
            tuple(
                CrossValidationFold(
                    f["fold_index"],
                    tuple(CycleFoldGroup(**g) for g in f["held_out_groups"]),
                )
                for f in raw["folds"]
            ),
        )

    @classmethod
    def _run_provenance_from_project(cls, raw):
        if raw is None:
            return None
        return RunProvenance(
            raw["seed"],
            cls._captured_settings_from_project(raw["settings"]),
            tuple(
                RoundProvenance(
                    r["outer_round"],
                    r["inner_round"],
                    r["seed"],
                    tuple(r["active_offsets"]),
                    tuple(r["training_speeds"]),
                    cls._fold_plan_from_project(r["fold_plan"]),
                )
                for r in raw["rounds"]
            ),
            raw["sampler_version"],
            raw.get("family", "fir"),
        )

    @classmethod
    def _kernel_evidence_from_project(cls, raw):
        return KernelTrainingEvidence(
            cls._captured_settings_from_project(raw["settings"]),
            raw["fold_index"],
            tuple(ConditionLoss(**c) for c in raw["conditions"]),
            raw["parameter_loss"],
            raw["kernel_loss"],
            raw["round_seed"],
            cls._fold_plan_from_project(raw["fold_plan"]),
        )

    @Property(str, notify=stateChanged)
    def numericType(self) -> str:
        return self._numeric_type

    @Property(bool, notify=stateChanged)
    def annotationsReady(self) -> bool:
        return self._annotations_ready

    @Property("QVariantList", notify=stateChanged)
    def annotationRecordingOptions(self) -> list[dict[str, object]]:
        result: list[dict[str, object]] = []
        for index, row in enumerate(self._recordings):
            blocker = self._annotation_validation_error(index)
            status = (
                "Confirmed"
                if self._annotations_ready
                else "Ready"
                if not blocker
                else "Needs annotation"
            )
            result.append(
                {
                    "index": index,
                    "name": str(row.get("name", f"Recording {index + 1}")),
                    "status": status,
                    "label": f"{row.get('name', f'Recording {index + 1}')} · {status}",
                    "blocker": blocker,
                }
            )
        return result

    @Property(bool, notify=stateChanged)
    def canUseSelectedCycleAsReference(self) -> bool:
        if self._selected_recording < 0:
            return False
        values = self._annotations.get(self._selected_recording, ())
        if not 0 <= self._selected_annotation < len(values):
            return False
        selected = values[self._selected_annotation]
        if selected.kind is not ActivityKind.CYCLE:
            return False
        try:
            recording = self._recording_from_state(self._selected_recording, values)
            cycle_index = self._cycle_index(values, selected)
            self._workspace.activate_annotation_template_source(recording, cycle_index)
        except (KeyError, ValueError):
            return False
        return True

    @Property(str, notify=stateChanged)
    def activeTemplateSummary(self) -> str:
        if self._selected_recording < 0:
            return "No active reference for this speed"
        row = self._recordings[self._selected_recording]
        speed = row.get("speed")
        template = (
            self._annotation_templates.get(float(speed)) if speed is not None else None
        )
        if template is None:
            return "No active reference for this speed"
        source_index = self._recording_index_for_id(template.source_recording_id)
        source_name = (
            str(self._recordings[source_index]["name"])
            if source_index is not None
            else template.source_recording_id
        )
        return f"{template.robot_speed_mm_s:g} mm/s · {source_name} · Cycle {template.source_cycle_index + 1}"

    @Property(str, notify=stateChanged)
    def activeTemplateDetails(self) -> str:
        if self._selected_recording < 0:
            return ""
        speed = self._recordings[self._selected_recording].get("speed")
        template = (
            self._annotation_templates.get(float(speed)) if speed is not None else None
        )
        if template is None:
            return ""
        counts = {
            kind: sum(event.kind is kind for event in template.events)
            for kind in (
                ActivityKind.PICK,
                ActivityKind.PUT,
                ActivityKind.FORK_COLLISION,
                ActivityKind.IGNORE,
            )
        }
        ignore_reasons = ", ".join(
            event.reason or ""
            for event in template.events
            if event.kind is ActivityKind.IGNORE
        )
        ignore_detail = f" ({ignore_reasons})" if ignore_reasons else ""
        return (
            f"Pick {counts[ActivityKind.PICK]} · Put {counts[ActivityKind.PUT]} · "
            f"Fork Collision {counts[ActivityKind.FORK_COLLISION]} · "
            f"Ignore {counts[ActivityKind.IGNORE]}{ignore_detail} · "
            f"duration {template.reference_cycle_length_samples} samples · "
            f"cadence {template.cycle_period_samples:g} samples"
        )

    @Property(str, notify=stateChanged)
    def annotationBlockerMessage(self) -> str:
        return self._annotation_blocker_message

    @Property(bool, notify=stateChanged)
    def canConfirmAnnotations(self) -> bool:
        return bool(self._recordings) and all(
            not self._annotation_validation_error(index)
            for index in range(len(self._recordings))
        )

    @Property(bool, notify=stateChanged)
    def importReady(self) -> bool:
        duplicate_keys = set(self._duplicate_condition_groups())
        return bool(
            self._recordings
            and self.sessionRateReady
            and all(row["mappingStatus"] == "Confirmed" for row in self._recordings)
            and duplicate_keys.issubset(self._reviewed_duplicate_keys)
        )

    @Property(str, notify=stateChanged)
    def duplicateConditionSummary(self) -> str:
        summaries = []
        for (rate, speed, offset), rows in sorted(
            self._duplicate_condition_groups().items()
        ):
            if (rate, speed, offset) in self._reviewed_duplicate_keys:
                continue
            names = ", ".join(str(row["name"]) for row in rows)
            summaries.append(
                f"{rate:g} Hz · {speed:g} mm/s · offset {offset:g} mm: {names}"
            )
        return "; ".join(summaries)

    @Property(bool, notify=stateChanged)
    def sessionRateReady(self) -> bool:
        values = [
            float(row["sampleRateValue"])
            for row in self._recordings
            if "sampleRateValue" in row
        ]
        if len(values) != len(self._recordings) or not values:
            return False
        session_rate = float(np.median(values))
        return all(
            abs(value - session_rate) / session_rate <= 0.005 for value in values
        )

    @Property(bool, notify=stateChanged)
    def canStartLearning(self) -> bool:
        return bool(
            self._numeric_type
            and self._annotations_ready
            and self.sessionRateReady
            and self._confirmed_workspace is not None
            and self._recordings
            and all(row["mappingStatus"] == "Confirmed" for row in self._recordings)
            and self._learning_settings.selections_ready
            and not self.trainingAdmissionMessage
            and not self.learningSettingsLocked
        )

    @Property(str, notify=stateChanged)
    def runState(self) -> str:
        return self._run_state

    @Property(float, notify=stateChanged)
    def progress(self) -> float:
        return self._progress

    @Property(str, notify=stateChanged)
    def trainingFallbackSummary(self) -> str:
        if not self._training_speeds:
            return "Training fallback state unavailable"
        excluded_speeds = tuple(
            speed
            for speed in self._training_supplied_speeds
            if speed not in self._training_speeds
        )
        value_text = lambda values: (
            ", ".join(f"{value:g}" for value in values) if values else "none"
        )
        outer, inner = self._training_round
        return (
            f"Round {outer}.{inner} · Training speeds {value_text(self._training_speeds)} mm/s · "
            f"Excluded speeds {value_text(excluded_speeds)} mm/s · "
            f"Active offsets {value_text(self._training_active_offsets)} mm · "
            f"Excluded offsets {value_text(self._training_excluded_offsets)} mm"
        )

    @Property(str, notify=stateChanged)
    def trainingCurrentSummary(self) -> str:
        stage = self._run_state
        if stage == "Learning":
            stage_label = "Training"
        elif stage == "Qualifying":
            stage_label = "Qualification"
        elif stage == "Refining Speed Range":
            stage_label = "Fallback"
        else:
            stage_label = stage
        current = ""
        if (
            self._training_current_speed is not None
            and self._training_current_offset is not None
        ):
            current = f" · Speed {self._training_current_speed:g} mm/s · Offset {self._training_current_offset:g} mm"
        return f"Current stage: {stage_label} · Progress {self._progress * 100:.0f}%{current}"

    @Property(str, notify=stateChanged)
    def trainingExecutionSummary(self) -> str:
        return "\n".join(str(item["detail"]) for item in self._training_log_entries)

    @Property("QVariantList", notify=stateChanged)
    def trainingLogEntries(self) -> list[dict[str, object]]:
        return list(self._training_log_entries)

    @Property(str, notify=stateChanged)
    def trainingLogDiscardedText(self) -> str:
        if not self._training_log_discarded_count:
            return ""
        return f"Earlier log entries discarded: {self._training_log_discarded_count}"

    @Property(str, notify=stateChanged)
    def stageElapsedText(self) -> str:
        if self._stage_started_monotonic is None:
            return "Stage duration 00:00:00"
        end = (
            self._stage_finished_monotonic
            if self._stage_finished_monotonic is not None
            else time.monotonic()
        )
        elapsed = max(0, int(end - self._stage_started_monotonic))
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        return (
            f"Stage {self._stage_name} {hours:02d}:{minutes:02d}:{seconds:02d} · "
            f"Training total {self._format_duration(self._stage_total_seconds('Training'))} · "
            f"Qualification total {self._format_duration(self._stage_total_seconds('Qualification'))}"
        )

    @Property(str, notify=stateChanged)
    def statusMessage(self) -> str:
        return self._status_message

    @Property(str, notify=stateChanged)
    def diagnosticNotice(self) -> str:
        return self._diagnostic_status.previous_unclean_summary

    @Property(str, notify=stateChanged)
    def diagnosticLogPath(self) -> str:
        return self._diagnostic_status.log_path

    @Property(str, notify=stateChanged)
    def runStartedAtText(self) -> str:
        return self._run_started_at

    @Property(str, notify=stateChanged)
    def runFinishedAtText(self) -> str:
        return self._run_finished_at

    @Property(str, notify=stateChanged)
    def runElapsedText(self) -> str:
        if self._run_started_monotonic is None:
            return "Duration 00:00:00"
        end = (
            self._run_finished_monotonic
            if self._run_finished_monotonic is not None
            else time.monotonic()
        )
        elapsed = max(0, int(end - self._run_started_monotonic))
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{'Elapsed' if self._run_finished_monotonic is None else 'Duration'} {hours:02d}:{minutes:02d}:{seconds:02d}"

    @Property(str, notify=stateChanged)
    def runFailureReason(self) -> str:
        return self._run_failure_reason

    @Property(str, notify=stateChanged)
    def headerFormat(self) -> str:
        return self._header_format

    @Property(str, notify=stateChanged)
    def headerPreview(self) -> str:
        return self._header_preview

    @Property(str, notify=stateChanged)
    def completedTrainingMode(self) -> str:
        if self._learning_run_provenance is None:
            return ""
        if self._learning_family_provenance:
            return " + ".join(
                "MLP" if run.family == "mlp" else "FIR + Ridge"
                for run in self._learning_family_provenance
            )
        if (
            self._learning_run_provenance.settings.training_mode
            is TrainingMode.FIXED_GRID
        ):
            return "Fixed grid FIR + Ridge"
        return "Optimized linear regression"

    def _result_source_label(self, identity):
        for algorithm, provenance in self._batch_provenance.items():
            if identity in provenance[2]:
                source = self._batch_source_choices[algorithm]["source"]
                if algorithm == "var":
                    return f"Single IMU - VAR (Ridge) / {source.title()} filtered XYZ"
                method = "MIMO FIR (Ridge)" if algorithm == "fir" else "MLP"
                return f"Dual IMU - {method} / Internal to External, both {source} XYZ"
        return ""

    @Property(str, notify=stateChanged)
    def selectedResultSource(self):
        return self._result_source_label(self._preview_kernel_id)

    @Property("QVariantList", notify=stateChanged)
    def resultKernels(self) -> list[dict[str, object]]:
        if self._retained_candidates:
            profile_ids = {
                profile.kernel_id: index for index, profile in enumerate(self._profiles)
            }
            visible = [
                candidate
                for candidate in self._retained_candidates
                if candidate.candidate_id in profile_ids
                or candidate.candidate_id in self._diagnostic_candidate_ids
            ]
            visible.sort(
                key=lambda candidate: profile_ids.get(
                    candidate.candidate_id, len(profile_ids)
                )
            )
            return [
                {
                    "kernelId": candidate.candidate_id,
                    "selected": candidate.candidate_id in self._selected_kernel_ids,
                    "exportable": candidate.candidate_id in profile_ids,
                    "status": "Qualified"
                    if candidate.candidate_id in profile_ids
                    else "Diagnostic only",
                    "trainingRange": self._speed_tuple_text(candidate.training_speeds),
                    "qualifiedRange": self._speed_tuple_text(candidate.passing_speeds),
                    "kernelDepth": (
                        f"{candidate.history.effective_history_ms:g} ms / {candidate.tap_count} taps"
                        if candidate.history is not None
                        else f"{candidate.tap_count} taps"
                    ),
                    "latency": (
                        f"{candidate.diagnostic_worst_latency_ms:g} ms"
                        if candidate.diagnostic_worst_latency_ms is not None
                        else "N/A"
                    ),
                    "errors": candidate.total_misjudgments,
                    "falseTriggers": candidate.false_trigger_count,
                    "missedCollisions": candidate.missed_collision_count,
                    "collisionCount": f"{candidate.collision_detected_count} / {candidate.collision_interval_count}",
                    "coveredOffsets": self._offset_text(candidate.active_offsets),
                    "excludedOffsets": self._offset_text(candidate.excluded_offsets),
                    "round": f"{candidate.outer_round}.{candidate.inner_round}",
                }
                for candidate in visible
            ]
        return [
            {
                "kernelId": profile.kernel_id,
                "selected": profile.kernel_id in self._selected_kernel_ids,
                "exportable": True,
                "status": "Qualified",
                "trainingRange": self._range_text(profile.training_speed_range),
                "qualifiedRange": self._range_text(profile.qualified_speed_range),
                "kernelDepth": f"{profile.effective_history_ms:g} ms / {profile.tap_count} taps",
                "latency": f"{profile.worst_collision_latency_ms:g} ms",
                "robustness": f"{profile.combined_robustness_margin:g}",
                "coveredOffsets": self._offset_text(profile.covered_offsets_mm),
                "excludedOffsets": self._offset_text(profile.excluded_offsets_mm),
                "round": f"{profile.outer_round}.{profile.inner_round}",
                "errors": 0,
                "falseTriggers": 0,
                "missedCollisions": 0,
                "collisionCount": "—",
            }
            for profile in self._profiles
        ]

    @Property("QVariantList", notify=stateChanged)
    def analyticalKernels(self) -> list[dict[str, object]]:
        return [
            {
                "kernelId": row["kernelId"],
                "label": f"{row['kernelId']} · Round {row['round']} · {row['status']}"
                + (
                    " / " + self._result_source_label(row["kernelId"])
                    if self._result_source_label(row["kernelId"])
                    else ""
                ),
            }
            for row in self.resultKernels
        ]

    @Property("QVariantList", notify=stateChanged)
    def retainedKernelOptions(self) -> list[dict[str, object]]:
        return self.analyticalKernels

    @Property(int, notify=stateChanged)
    def analyticalKernelIndex(self) -> int:
        rows = self.resultKernels
        for index, row in enumerate(rows):
            if row["kernelId"] == self._preview_kernel_id:
                return index
        return 0 if rows else -1

    @Property(int, notify=stateChanged)
    def retainedKernelIndex(self) -> int:
        return self.analyticalKernelIndex

    @Property("QVariantMap", notify=stateChanged)
    def analyticalKernelParameters(self) -> dict[str, object]:
        candidate = self._current_candidate()
        if candidate is not None:
            model = candidate.model
            detector = candidate.detector_config
            active = self._offset_text(candidate.active_offsets)
            excluded = self._offset_text(candidate.excluded_offsets)
            supplied_speeds = tuple(
                sorted({row.robot_speed_mm_s for row in candidate.conditions})
            )
            return {
                "kernelId": candidate.candidate_id,
                "round": f"{candidate.outer_round}.{candidate.inner_round}",
                "trainingRange": self._speed_tuple_text(candidate.training_speeds),
                "qualifiedRange": self._speed_tuple_text(candidate.passing_speeds),
                "speeds": self._speed_scope_text(
                    candidate.training_speeds, supplied_speeds
                ),
                "offsets": f"Active {active} · Excluded {excluded}",
                "history": (
                    f"{candidate.history.effective_history_ms:g} ms / {candidate.tap_count} taps"
                    if candidate.history is not None
                    else f"N/A / {candidate.tap_count} taps"
                ),
                "ridgeAlpha": f"{model.alpha:g}" if model is not None else "N/A",
                "modelFamily": f"SELF RIDGE ({model.preprocessing.sensor.upper()})"
                if isinstance(model, FrozenSelfImuModel)
                else ("MLP" if isinstance(model, FrozenMlpModel) else "FIR"),
                **(
                    {
                        "preprocessing": "Existing filtered XYZ"
                        if model.preprocessing.source_mode == "already_filtered"
                        else f"Causal SOS: {len(model.preprocessing.filters)} stages",
                        "readiness": f"Not ready: first {model.tap_count + (model.preprocessing.warmup_samples if model.preprocessing.source_mode == 'application_filtered' else 0)} samples at startup/gap; Ignore resumes immediately",
                    }
                    if isinstance(model, FrozenSelfImuModel)
                    else {}
                ),
                "architecture": " -> ".join(str(w.shape[1]) for w in model.weights[:-1])
                if isinstance(model, FrozenMlpModel)
                else "Linear",
                "parameterCount": sum(
                    w.size + b.size for w, b in zip(model.weights, model.biases)
                )
                if isinstance(model, FrozenMlpModel)
                else (model.weights.size + model.biases.size if model else 0),
                "parameterBytes": sum(
                    w.nbytes + b.nbytes for w, b in zip(model.weights, model.biases)
                )
                if isinstance(model, FrozenMlpModel)
                else (model.weights.nbytes + model.biases.nbytes if model else 0),
                "workingBufferBytes": (
                    3 * model.tap_count + 2 * max(w.shape[1] for w in model.weights) + 9
                )
                * model.weights[0].dtype.itemsize
                if isinstance(model, FrozenMlpModel)
                else (
                    (3 * model.tap_count + 9) * model.weights.dtype.itemsize
                    if model
                    else 0
                ),
                "scaleAndK": (
                    f"{model.scale_method} / {model.robust_k}"
                    if model is not None
                    else "N/A"
                ),
                "threshold": f"{detector.threshold:g}"
                if detector is not None
                else "N/A",
                "trainingLoss": self._training_loss_text(candidate.candidate_id),
            }
        profile = self._current_profile()
        if profile is None:
            return {}
        supplied_speeds = tuple(
            sorted({row.robot_speed_mm_s for row in profile.coverage})
        )
        active_speeds = tuple(
            speed
            for speed in supplied_speeds
            if profile.training_speed_range[0]
            <= speed
            <= profile.training_speed_range[1]
        )
        return {
            "kernelId": profile.kernel_id,
            "round": f"{profile.outer_round}.{profile.inner_round}",
            "trainingRange": self._range_text(profile.training_speed_range),
            "qualifiedRange": self._range_text(profile.qualified_speed_range),
            "speeds": self._speed_scope_text(active_speeds, supplied_speeds),
            "offsets": (
                f"Active {self._offset_text(profile.covered_offsets_mm)} · "
                f"Excluded {self._offset_text(profile.excluded_offsets_mm)}"
            ),
            "history": f"{profile.effective_history_ms:g} ms / {profile.tap_count} taps",
            "ridgeAlpha": f"{profile.ridge_alpha:g}",
            "modelFamily": profile.model_family.upper(),
            "architecture": " -> ".join(
                str(np.asarray(w).shape[1]) for w in profile.weights[:-1]
            )
            if profile.model_family == "mlp"
            else "Linear",
            "scaleAndK": f"{profile.scale_method} / {profile.robust_k}",
            "threshold": f"{profile.threshold:g}",
            "trainingLoss": self._training_loss_text(profile.kernel_id),
        }

    @Property("QVariantMap", notify=stateChanged)
    def selectedKernelParameters(self) -> dict[str, object]:
        return self.analyticalKernelParameters

    @Property("QVariantList", notify=stateChanged)
    def trainingCandidates(self) -> list[dict[str, object]]:
        return [
            {
                "kernelId": profile.kernel_id,
                "round": f"{profile.outer_round}.{profile.inner_round}",
                "effectiveHistoryMs": profile.effective_history_ms,
                "tapCount": profile.tap_count,
                "ridgeAlpha": profile.ridge_alpha,
                "scaleMethod": profile.scale_method,
                "robustK": profile.robust_k,
                "scoreMode": profile.score_mode,
                "confirmationMode": profile.confirmation_mode,
                "initialFitRows": profile.initial_fit_rows,
                "refitRows": profile.refit_rows,
                "foldCount": profile.cross_validation_fold_count,
                "evidenceLevel": profile.cross_validation_evidence_level,
                "worstConditionMse": profile.cross_validation_worst_condition_mse,
                "pooledMse": profile.cross_validation_pooled_mse,
                "foldIndex": self._kernel_training_evidence[
                    profile.kernel_id
                ].fold_index
                if profile.kernel_id in self._kernel_training_evidence
                else None,
                "metricMode": (
                    "50% Training + 50% Validation"
                    if self._kernel_training_evidence[
                        profile.kernel_id
                    ].settings.include_training_mse
                    else "Validation only"
                )
                if profile.kernel_id in self._kernel_training_evidence
                else "Historical metric",
                "kernelLoss": self._kernel_training_evidence[
                    profile.kernel_id
                ].kernel_loss
                if profile.kernel_id in self._kernel_training_evidence
                else None,
            }
            for profile in self._profiles
        ]

    @Property(int, notify=stateChanged)
    def selectedKernelCount(self) -> int:
        return len(self._selected_kernel_ids)

    @Property(bool, notify=stateChanged)
    def canExportSelected(self) -> bool:
        return (
            self._run_state in {"Complete", "Cancelled"}
            and bool(self._selected_kernel_ids)
            and bool(self._header_preview)
            and all(
                p.model_family == "fir"
                for p in self._profiles
                if p.kernel_id in self._selected_kernel_ids
            )
        )

    @Property(str, notify=stateChanged)
    def exportConflictName(self) -> str:
        return (
            self._pending_export_conflicts[0] if self._pending_export_conflicts else ""
        )

    @Property("QVariantMap", notify=stateChanged)
    def qualificationSummary(self) -> dict[str, object]:
        candidate = self._current_candidate()
        if candidate is not None:
            exportable = any(
                item.kernel_id == candidate.candidate_id for item in self._profiles
            )
            return {
                "kernelId": candidate.candidate_id,
                "qualifiedRange": self._speed_tuple_text(candidate.passing_speeds),
                "trainingRange": self._speed_tuple_text(candidate.training_speeds),
                "kernelDepth": (
                    f"{candidate.history.effective_history_ms:g} ms / {candidate.tap_count} taps"
                    if candidate.history is not None
                    else f"{candidate.tap_count} taps"
                ),
                "latency": (
                    f"{candidate.diagnostic_worst_latency_ms:g} ms · {'Pass' if exportable else 'Diagnostic only'}"
                    if candidate.diagnostic_worst_latency_ms is not None
                    else "N/A · Diagnostic only"
                ),
                "status": "Qualified" if exportable else "Diagnostic only",
                "errors": candidate.total_misjudgments,
            }
        profile = self._current_profile()
        if profile is None:
            return {}
        return {
            "kernelId": profile.kernel_id,
            "qualifiedRange": self._range_text(profile.qualified_speed_range),
            "trainingRange": self._range_text(profile.training_speed_range),
            "kernelDepth": f"{profile.effective_history_ms:g} ms / {profile.tap_count} taps",
            "latency": f"{profile.worst_collision_latency_ms:g} ms · Pass",
        }

    @Property("QVariantList", notify=stateChanged)
    def qualificationConditions(self) -> list[dict[str, object]]:
        candidate = self._current_candidate()
        if candidate is not None:
            return [
                {
                    "speed": f"{row.robot_speed_mm_s:g} mm/s",
                    "offset": f"{row.collision_offset_mm:g} mm",
                    "status": row.status.title().replace("_", " "),
                    "falseCounts": f"{row.normal_false_events} / {row.pick_false_events} / {row.put_false_events}",
                    "collisionCount": f"{row.collision_detected_count} / {row.collision_interval_count}",
                    "latency": f"{row.worst_collision_latency_ms:g} ms"
                    if row.worst_collision_latency_ms is not None
                    else "N/A",
                    "recordings": row.recording_count,
                    "cycles": row.valid_cycle_count,
                }
                for row in candidate.conditions
            ]
        profile = self._current_profile()
        if profile is None:
            return []
        return [
            {
                "speed": f"{row.robot_speed_mm_s:g} mm/s",
                "offset": f"{row.collision_offset_mm:g} mm",
                "status": row.qualification_status.title().replace("_", " "),
                "falseCounts": f"{row.normal_false_events} / {row.pick_false_events} / {row.put_false_events}",
                "collisionCount": f"{row.collision_detected_count} / {row.collision_interval_count}",
                "latency": f"{row.worst_collision_latency_ms:g} ms"
                if row.worst_collision_latency_ms is not None
                else "—",
                "recordings": row.recording_count,
                "cycles": row.valid_cycle_count,
            }
            for row in profile.coverage
        ]

    @Property("QVariantList", notify=stateChanged)
    def replayRecordings(self) -> list[dict[str, object]]:
        dataset = self._learning_dataset_for_replay()
        if dataset is None:
            return []
        return [
            {
                "label": f"{item.recording_id} · {item.robot_speed_mm_s:g} mm/s · {item.collision_offset_mm:g} mm",
                "recordingId": item.recording_id,
            }
            for item in dataset.recordings
        ]

    @Property("QVariantList", notify=stateChanged)
    def replayRecordingResults(self) -> list[dict[str, object]]:
        candidate = self._current_candidate()
        if candidate is None:
            return []
        return [
            {
                "recordingIndex": index,
                "recording": row.recording_id,
                "speed": f"{row.robot_speed_mm_s:g} mm/s",
                "offset": f"{row.collision_offset_mm:g} mm",
                "falseCounts": (
                    f"{row.normal_false_events} / {row.pick_false_events} / "
                    f"{row.put_false_events}"
                ),
                "collisionCount": (
                    f"{row.collision_detected_count} / {row.collision_interval_count}"
                ),
                "collisionSnr": (
                    " / ".join(
                        f"{value:g}"
                        if value is not None and math.isfinite(value)
                        else "N/A"
                        for value in row.collision_snrs_db
                    )
                    or "N/A"
                ),
                "latency": (
                    f"{row.worst_collision_latency_ms:g} ms"
                    if row.worst_collision_latency_ms is not None
                    else "N/A"
                ),
                "status": row.status.title().replace("_", " "),
                "reason": self._recording_qualification_reason(row),
            }
            for index, row in enumerate(candidate.recording_qualifications)
        ]

    @Property("QVariantMap", notify=stateChanged)
    def replaySummary(self) -> dict[str, object]:
        candidate = self._current_candidate()
        recording = self._replay_recording()
        if candidate is None or recording is None:
            return {}
        return {
            "candidateId": candidate.candidate_id,
            "recordingId": recording.recording_id,
        }

    @staticmethod
    def _safe_artifact_component(value: object, fallback: str) -> str:
        normalized = "".join(
            character if character.isalnum() or character in "-_" else "_"
            for character in str(value).strip()
        )
        normalized = re.sub(r"_+", "_", normalized).strip("._-")
        return normalized or fallback

    @Property(str, notify=stateChanged)
    def replayCsvSuggestedFileName(self) -> str:
        recording = self._replay_recording()
        if recording is None:
            return "replay.csv"
        row = (
            self._recordings[self._replay_recording_index]
            if 0 <= self._replay_recording_index < len(self._recordings)
            else {}
        )
        source = row.get("path") or row.get("name") or recording.recording_id
        stem = self._safe_artifact_component(Path(str(source)).stem, "recording")
        worksheet = str(row.get("worksheet") or "").strip()
        if worksheet:
            stem += "_" + self._safe_artifact_component(worksheet, "worksheet")
        return f"{stem}_replay.csv"

    @Property(str, notify=stateChanged)
    def modelTxtSuggestedFileName(self) -> str:
        candidate = self._current_candidate()
        if candidate is None:
            return "model.txt"
        kernel_id = self._safe_artifact_component(candidate.candidate_id, "kernel")
        return f"{kernel_id}_model.txt"

    @Slot(int)
    def selectReplayRecording(self, index: int) -> None:
        if 0 <= index < len(self.replayRecordings):
            self._replay_recording_index = index
            self.stateChanged.emit()

    @Slot(QUrl, result=bool)
    def exportReplayCsv(self, value: QUrl) -> bool:
        if self.singleImuMode:
            self._status_message = (
                "Single-IMU export is unavailable in this desktop-simulation version."
            )
            self.stateChanged.emit()
            return False
        if (
            self._replay_export_worker is not None
            or self._model_export_worker is not None
        ):
            self._status_message = "An artifact export is already active."
            self.stateChanged.emit()
            return False
        candidate = self._current_candidate()
        recording = self._replay_recording()
        if candidate is None or recording is None:
            self._status_message = (
                "Replay CSV export failed: complete Replay evidence is unavailable."
            )
            self.stateChanged.emit()
            return False
        path = self._path_from_url(value)
        if path.suffix.lower() != ".csv":
            path = path.with_suffix(".csv")
        worker = _ReplayCsvExportWorker(
            self._learning,
            recording,
            candidate,
            path,
        )
        worker.signals.completed.connect(self._on_replay_export_completed)
        worker.signals.failed.connect(self._on_replay_export_failed)
        self._replay_export_worker = worker
        self._status_message = f"Exporting Replay CSV {path.name}..."
        self.stateChanged.emit()
        QThreadPool.globalInstance().start(worker)
        return True

    @Slot(str)
    def _on_replay_export_completed(self, destination: str) -> None:
        self._replay_export_worker = None
        self._status_message = f"Saved Replay CSV {Path(destination).name}."
        self.stateChanged.emit()

    @Slot(str)
    def _on_replay_export_failed(self, reason: str) -> None:
        self._replay_export_worker = None
        self._status_message = f"Replay CSV export failed: {reason}"
        self.stateChanged.emit()

    @Slot(QUrl, result=bool)
    def exportModelTxt(self, value: QUrl) -> bool:
        if self.singleImuMode:
            self._status_message = (
                "Single-IMU export is unavailable in this desktop-simulation version."
            )
            self.stateChanged.emit()
            return False
        if (
            self._replay_export_worker is not None
            or self._model_export_worker is not None
        ):
            self._status_message = "An artifact export is already active."
            self.stateChanged.emit()
            return False
        candidate = self._current_candidate()
        sample_rate_hz = self._session_rate() if self.sessionRateReady else None
        if candidate is None or sample_rate_hz is None:
            self._status_message = (
                "Model TXT export failed: complete model evidence is unavailable."
            )
            self.stateChanged.emit()
            return False
        if isinstance(candidate.model, FrozenMlpModel):
            self._status_message = "MLP deployment export is unavailable in this phase; save the project to retain parameters."
            self.stateChanged.emit()
            return False
        path = self._path_from_url(value)
        if path.suffix.lower() != ".txt":
            path = path.with_suffix(".txt")
        worker = _ModelTextExportWorker(
            self._learning, candidate, float(sample_rate_hz), path
        )
        worker.signals.completed.connect(self._on_model_export_completed)
        worker.signals.failed.connect(self._on_model_export_failed)
        self._model_export_worker = worker
        self._status_message = f"Exporting Model TXT {path.name}..."
        self.stateChanged.emit()
        QThreadPool.globalInstance().start(worker)
        return True

    @Slot(str)
    def _on_model_export_completed(self, destination: str) -> None:
        self._model_export_worker = None
        self._status_message = f"Saved Model TXT {Path(destination).name}."
        self.stateChanged.emit()

    @Slot(str)
    def _on_model_export_failed(self, reason: str) -> None:
        self._model_export_worker = None
        self._status_message = f"Model TXT export failed: {reason}"
        self.stateChanged.emit()

    @Property(int, notify=stateChanged)
    def candidateCount(self) -> int:
        rate = self._session_rate() if self.sessionRateReady else None
        if not rate:
            return 0
        plan = self._learning.build_candidate_plan(rate, self._learning_settings)
        if self._learning_settings.training_mode is TrainingMode.FIXED_GRID:
            return plan.parameter_count
        return plan.candidate_count or -1

    @Slot(int)
    def selectStage(self, index: int) -> None:
        if not 0 <= index < len(self.STAGES):
            return
        maximum_available = self._maximum_available_stage()
        if index > maximum_available:
            self._status_message = f"Complete {self.STAGES[maximum_available]} before opening {self.STAGES[index]}."
            self.stateChanged.emit()
            return
        if self._selected_stage != index:
            self._selected_stage = index
            self._mark_project_dirty()
        self.stateChanged.emit()

    @Slot(int)
    def selectRecording(self, index: int) -> None:
        if 0 <= index < len(self._recordings):
            changed = self._selected_recording != index
            self._selected_recording = index
            self._selected_annotation = -1
            self._selected_annotations.clear()
            if changed:
                self._mark_project_dirty()
            self.stateChanged.emit()

    @Slot(result=bool)
    def newProject(self) -> bool:
        if (
            self._learning_worker is not None
            or self._replay_export_worker is not None
            or self._model_export_worker is not None
        ):
            self._status_message = (
                "Finish or cancel active work before creating a new project."
            )
            self.stateChanged.emit()
            return False
        self._run_timer.stop()
        self._selected_stage = 0
        self._selected_recording = -1
        self._project_path = None
        self._project_dirty = False
        self._clear_pending_project_open()
        self._recordings.clear()
        self._samples.clear()
        self._annotations.clear()
        self._annotation_templates.clear()
        self._annotation_undo.clear()
        self._annotation_redo.clear()
        self._reviewed_duplicate_keys.clear()
        self._selected_annotation = -1
        self._selected_annotations.clear()
        self._next_annotation_id = 1
        self._confirmed_workspace = None
        self._active_learning_request = None
        self._numeric_type = ""
        self._training_algorithms = ("fir",)
        self._training_sources = {"fir": "raw", "mlp": "raw", "var": "internal"}
        self._training_selection_explicit = False
        self._batch_requests = {}
        self._batch_source_choices = {}
        self._batch_provenance = {}
        self._learning_settings = LearningSettings()
        self._learning_family_provenance = ()
        self._learning_run_provenance = None
        self._kernel_training_evidence = {}
        self._learning_setting_notices = ()
        self._annotations_ready = False
        self._annotation_blocker_message = ""
        self._run_state = "Ready"
        self._progress = 0.0
        self._run_started_monotonic = None
        self._run_finished_monotonic = None
        self._run_started_at = ""
        self._run_finished_at = ""
        self._run_failure_reason = ""
        self._stage_name = ""
        self._stage_started_monotonic = None
        self._stage_finished_monotonic = None
        self._stage_elapsed_totals = {
            "Training": 0.0,
            "Qualification": 0.0,
            "Fallback": 0.0,
        }
        self._training_active_offsets = ()
        self._training_excluded_offsets = ()
        self._training_speeds = ()
        self._training_supplied_offsets = ()
        self._training_supplied_speeds = ()
        self._training_round = (0, 0)
        self._training_current_speed = None
        self._training_current_offset = None
        self._training_execution_summaries.clear()
        self._training_log_entries.clear()
        self._training_log_discarded_count = 0
        self._header_preview = ""
        self._profiles.clear()
        self._retained_candidates.clear()
        self._diagnostic_candidate_ids.clear()
        self._selected_kernel_ids.clear()
        self._preview_kernel_id = ""
        self._replay_recording_index = 0
        self._pending_export_folder = None
        self._pending_export_artifacts = ()
        self._pending_export_conflicts.clear()
        self._approved_replacements.clear()
        self._status_message = "New project created. Import CSV or XLSX data to begin."
        self.stateChanged.emit()
        return True

    @Slot(int, bool, result=bool)
    def setFixedHistorySelected(self, value: int, selected: bool) -> bool:
        values = set(self._learning_settings.fixed_history_ms)
        values.add(value) if selected else values.discard(value)
        return self.setLearningSetting("fixed_history_ms", list(values))

    @Slot(float, bool, result=bool)
    def setFixedRidgeAlphaSelected(self, value: float, selected: bool) -> bool:
        values = set(self._learning_settings.fixed_ridge_alphas)
        values.add(value) if selected else values.discard(value)
        return self.setLearningSetting("fixed_ridge_alphas", list(values))

    @Slot(result=bool)
    def saveProject(self) -> bool:
        if self._project_path is None:
            self._status_message = "Choose Save Project As for this untitled project."
            self.stateChanged.emit()
            return False
        return self._save_project_to(self._project_path)

    @Slot(QUrl, result=bool)
    def saveProjectAs(self, value: QUrl) -> bool:
        path = self._path_from_url(value)
        if path.suffix.lower() != ".dicsproj":
            path = path.with_suffix(".dicsproj")
        return self._save_project_to(path)

    @Slot(QUrl, result=bool)
    def openProject(self, value: QUrl) -> bool:
        path = self._path_from_url(value)
        if path.suffix.lower() != ".dicsproj":
            self._status_message = "Project open failed: project filename must use the .dicsproj extension."
            self.stateChanged.emit()
            return False
        if self._learning_worker is not None:
            self._status_message = (
                "Cancel the active Learning run before opening a project."
            )
            self.stateChanged.emit()
            return False
        try:
            document = self._project_service.validate(self._project_store.read(path))
            restored = self._restore_project(document)
        except _ProjectSourceMissing as exc:
            self._pending_project_document = document
            self._pending_project_path = path
            self._pending_project_overrides = {}
            self._pending_project_missing_index = exc.recording_index
            self._status_message = f"Project source missing: {exc.source_name}. Locate the exact file or its folder."
            self.stateChanged.emit()
            return False
        except (ArithmeticError, KeyError, OSError, TypeError, ValueError) as exc:
            self._status_message = f"Project open failed: {exc}"
            self.stateChanged.emit()
            return False
        self._commit_restored_project(restored, path)
        self._status_message = f"Opened project {path.name}." + (
            " Settings: " + "; ".join(self._learning_setting_notices)
            if self._learning_setting_notices
            else ""
        )
        self.stateChanged.emit()
        return True

    @Slot(QUrl, result=bool)
    def relinkProjectFile(self, value: QUrl) -> bool:
        if not self.projectRelinkRequired:
            return False
        index = self._pending_project_missing_index
        candidate = self._path_from_url(value)
        raw = self._pending_project_document.data["recordings"][index]
        saved = self._project_service.source_reference(raw["source"])
        try:
            actual = self._project_store.fingerprint(candidate, saved.worksheet)
        except OSError as exc:
            self._status_message = f"Relink failed: {exc}"
            self.stateChanged.emit()
            return False
        if actual.size_bytes != saved.size_bytes or actual.sha256 != saved.sha256:
            self._status_message = f"Relink rejected: {candidate.name} does not match the saved fingerprint."
            self.stateChanged.emit()
            return False
        self._pending_project_overrides[index] = str(candidate)
        return self._attempt_pending_project_open()

    @Slot(QUrl, result=bool)
    def relinkProjectFolder(self, value: QUrl) -> bool:
        if not self.projectRelinkRequired:
            return False
        folder = self._path_from_url(value)
        for index, raw in enumerate(self._pending_project_document.data["recordings"]):
            saved = self._project_service.source_reference(raw["source"])
            if Path(self._pending_project_overrides.get(index, saved.path)).exists():
                continue
            exact_matches: list[Path] = []
            for candidate in folder.rglob(Path(saved.path).name):
                if not candidate.is_file():
                    continue
                actual = self._project_store.fingerprint(candidate, saved.worksheet)
                if (
                    actual.size_bytes == saved.size_bytes
                    and actual.sha256 == saved.sha256
                ):
                    exact_matches.append(candidate)
            if len(exact_matches) > 1:
                self._status_message = (
                    f"Relink is ambiguous: multiple exact matches were found for {Path(saved.path).name}. "
                    "Use Locate File to choose one."
                )
                self.stateChanged.emit()
                return False
            if exact_matches:
                self._pending_project_overrides[index] = str(exact_matches[0])
        return self._attempt_pending_project_open()

    @Slot()
    def cancelProjectRelink(self) -> None:
        self._clear_pending_project_open()
        self._status_message = (
            "Project open cancelled; the active session was not changed."
        )
        self.stateChanged.emit()

    @Slot(result=bool)
    def useSelectedCycleAsReference(self) -> bool:
        if not self.canUseSelectedCycleAsReference:
            self._annotation_blocker_message = (
                "Select one complete valid Cycle before Use as Reference."
            )
            self._status_message = self._annotation_blocker_message
            self.stateChanged.emit()
            return False
        source_index = self._selected_recording
        source_values = self._annotations.get(source_index, ())
        selected = source_values[self._selected_annotation]
        source_recording = self._recording_from_state(source_index, source_values)
        cycle_index = self._cycle_index(source_values, selected)
        try:
            activated_source, template = (
                self._workspace.activate_annotation_template_source(
                    source_recording, cycle_index
                )
            )
            pending: dict[int, tuple[AnnotationInterval, ...]] = {}
            affected = 0
            for index, row in enumerate(self._recordings):
                if (
                    row.get("mappingStatus") != "Confirmed"
                    or float(row.get("speed", -1.0)) != template.robot_speed_mm_s
                ):
                    continue
                current = (
                    activated_source.annotations
                    if index == source_index
                    else self._annotations.get(index, ())
                )
                recording = (
                    activated_source
                    if index == source_index
                    else self._recording_from_state(index, current)
                )
                projected = self._workspace.project_annotation_template(
                    recording, template
                )
                pending[index] = projected.annotations
                affected += 1
        except (KeyError, ValueError) as exc:
            self._annotation_blocker_message = str(exc)
            self._status_message = str(exc)
            self.stateChanged.emit()
            return False
        for index, proposed in pending.items():
            current = self._annotations.get(index, ())
            if proposed == current:
                continue
            self._annotation_undo.setdefault(index, []).append(current)
            self._annotation_redo[index] = []
            self._annotations[index] = proposed
        self._annotation_templates[template.robot_speed_mm_s] = template
        self._selected_annotation = -1
        self._selected_annotations.clear()
        self._annotation_blocker_message = ""
        self._invalidate_annotation_truth()
        counts = {
            kind: sum(event.kind is kind for event in template.events)
            for kind in (
                ActivityKind.PICK,
                ActivityKind.PUT,
                ActivityKind.FORK_COLLISION,
                ActivityKind.IGNORE,
            )
        }
        self._status_message = (
            f"Reference activated from {self._recordings[source_index]['name']} · "
            f"{template.robot_speed_mm_s:g} mm/s · Cycle {template.source_cycle_index + 1}; "
            f"Pick {counts[ActivityKind.PICK]}, Put {counts[ActivityKind.PUT]}, "
            f"Fork Collision {counts[ActivityKind.FORK_COLLISION]}, Ignore {counts[ActivityKind.IGNORE]}; "
            f"duration {template.reference_cycle_length_samples} samples, "
            f"cadence {template.cycle_period_samples:g} samples; "
            f"updated {affected} same-speed recording(s)."
        )
        self.stateChanged.emit()
        return True

    @Slot(int, result=bool)
    def removeRecording(self, index: int) -> bool:
        if not 0 <= index < len(self._recordings):
            return False
        if self._learning_worker is not None:
            self._status_message = (
                "Cancel the active Learning run before removing a recording."
            )
            self.stateChanged.emit()
            return False

        removed_name = str(self._recordings[index]["name"])
        del self._recordings[index]

        def without_index(values: dict[int, object]) -> dict[int, object]:
            return {
                old_index if old_index < index else old_index - 1: value
                for old_index, value in values.items()
                if old_index != index
            }

        self._samples = without_index(self._samples)
        self._annotations = without_index(self._annotations)
        self._annotation_undo = without_index(self._annotation_undo)
        self._annotation_redo = without_index(self._annotation_redo)
        self._annotation_templates.clear()
        self._selected_recording = min(index, len(self._recordings) - 1)
        self._selected_annotation = -1
        self._annotations_ready = False
        self._confirmed_workspace = None
        self._stale_results("Imported recording sources changed.")
        self._selected_stage = min(
            self._selected_stage, self._maximum_available_stage()
        )
        self._status_message = f"Removed {removed_name} from this session. The source file was not changed."
        self._mark_project_dirty()
        self.stateChanged.emit()
        return True

    @Slot(result=bool)
    def confirmIntentionalDuplicates(self) -> bool:
        duplicate_keys = set(self._duplicate_condition_groups())
        if not duplicate_keys:
            return False
        self._reviewed_duplicate_keys.update(duplicate_keys)
        self._mark_project_dirty()
        self._status_message = (
            "Duplicate conditions confirmed as intentional repeated acquisitions."
        )
        self.stateChanged.emit()
        return True

    @Slot("QVariantList", result=int)
    def importFiles(self, values: list[object]) -> int:
        first_imported_index = len(self._recordings)
        self._annotations_ready = False
        self._confirmed_workspace = None
        self._stale_results("Imported recording sources changed.")
        for value in values:
            url = value if isinstance(value, QUrl) else QUrl(str(value))
            path = Path(url.toLocalFile() if url.isLocalFile() else str(value))
            identities = self._reader.worksheets(path) or (None,)
            for worksheet in identities:
                preview = self._reader.preview(path, worksheet, 20)
                try:
                    proposal = self._reader.propose_header(preview)
                    columns = list(proposal.columns)
                    header_row = proposal.header_row
                    data_start_row = proposal.data_start_row
                except ValueError:
                    columns = [str(item) for item in preview[0]] if preview else []
                    header_row = 1
                    data_start_row = 2
                self._recordings.append(
                    {
                        "name": path.name
                        if worksheet is None
                        else f"{path.name} · {worksheet}",
                        "path": str(path),
                        "worksheet": worksheet or "",
                        "rows": "Pending",
                        "sampleRate": "Pending",
                        "mappingStatus": "Needs mapping",
                        "condition": "Needs values",
                        "validation": "Waiting",
                        "importWarnings": [],
                        "columns": columns,
                        "previewRows": [
                            {
                                "rowNumber": index + 1,
                                "cells": [
                                    "" if value is None else str(value)
                                    for value in preview_row
                                ],
                            }
                            for index, preview_row in enumerate(preview)
                        ],
                        "suggestedHeaderRow": header_row,
                        "suggestedDataStartRow": data_start_row,
                    }
                )
        if self._recordings and self._selected_recording < 0:
            self._selected_recording = 0
        self._status_message = f"{len(self._recordings)} recording source(s) inventoried. Confirm each Mapping Wizard."
        if len(self._recordings) > first_imported_index:
            self._mark_project_dirty()
        self.stateChanged.emit()
        return (
            first_imported_index if len(self._recordings) > first_imported_index else -1
        )

    @Slot(QUrl, result=int)
    def importFile(self, value: QUrl) -> int:
        return self.importFiles([value])

    @Slot(
        int,
        int,
        str,
        str,
        float,
        "QVariantList",
        "QVariantList",
        float,
        float,
        result=bool,
    )
    def confirmMapping(
        self,
        data_start_row: int,
        header_row: int,
        time_column: str,
        time_unit: str,
        sample_rate_hz: float,
        internal_columns: list[str],
        external_columns: list[str],
        robot_speed: float,
        collision_offset: float,
        preprocessing=None,
        signal_mapping=None,
    ) -> bool:
        if self._selected_recording < 0:
            return False
        row = self._recordings[self._selected_recording]
        try:
            mapping = ColumnMapping(
                data_start_row=data_start_row,
                header_row=header_row,
                time_column=time_column or None,
                time_unit=time_unit or None,
                sample_rate_hz=None if time_column else sample_rate_hz,
                internal_columns=tuple(internal_columns),
                external_columns=tuple(external_columns),
                single_sensor=preprocessing.sensor
                if preprocessing
                else (
                    "external"
                    if not internal_columns
                    else "internal"
                    if not external_columns
                    else None
                ),
            )
            samples = self._reader.read(row["path"], mapping, row["worksheet"] or None)
            if preprocessing is not None and any(
                abs(d.sample_rate_hz - samples.inferred_sample_rate_hz)
                / samples.inferred_sample_rate_hz
                > 0.005
                for d in preprocessing.filters
            ):
                raise ValueError(
                    "Sample rate changed after filter adoption; preview and adopt again"
                )
            if robot_speed <= 0:
                raise ValueError("Robot Speed must be greater than zero")
        except Exception as exc:
            self._status_message = str(exc)
            self.stateChanged.emit()
            return False
        self._samples[self._selected_recording] = samples
        self._annotations_ready = False
        self._confirmed_workspace = None
        self._annotations.pop(self._selected_recording, None)
        self._annotation_undo.pop(self._selected_recording, None)
        self._annotation_redo.pop(self._selected_recording, None)
        self._annotation_templates.clear()
        row.update(
            rows=str(len(samples.time_s)),
            sampleRate=f"{samples.inferred_sample_rate_hz:.3f} Hz",
            sampleRateValue=samples.inferred_sample_rate_hz,
            mappingStatus="Confirmed",
            condition=f"{robot_speed:g} mm/s · offset {collision_offset:g} mm",
            speed=robot_speed,
            offset=collision_offset,
            validation="Warning" if samples.warnings else "Ready",
            importWarnings=list(samples.warnings),
            mapping={
                "data_start_row": mapping.data_start_row,
                "header_row": mapping.header_row,
                "time_column": mapping.time_column,
                "time_unit": mapping.time_unit,
                "sample_rate_hz": mapping.sample_rate_hz,
                "internal_columns": list(mapping.internal_columns),
                "external_columns": list(mapping.external_columns),
                **(
                    {
                        "single_sensor": preprocessing.sensor,
                        "single_imu_schema": 1,
                        "preprocessing": settings_to_data(preprocessing),
                    }
                    if preprocessing
                    else {}
                ),
            },
        )
        if signal_mapping is not None:
            row["mapping"].update(
                signal_mapping_schema=1,
                signals=signal_mapping,
                source_sha256=self._project_store.fingerprint(
                    str(row["path"]), str(row.get("worksheet", ""))
                ).sha256,
                single_sensor=mapping.single_sensor,
            )
            self._training_selection_explicit = True
        condition_key = self._condition_key(row)
        if condition_key is not None:
            self._reviewed_duplicate_keys.discard(condition_key)
        if preprocessing is not None:
            self._learning_settings = replace(
                self._learning_settings, model_families=("fir",)
            )
        self._stale_results("Recording mapping or Test Conditions changed.")
        self._mark_project_dirty()
        self._status_message = (
            f"Mapping confirmed for {row['name']}. " + "; ".join(samples.warnings)
            if samples.warnings
            else f"Mapping confirmed for {row['name']}."
        )
        self.stateChanged.emit()
        return True

    @staticmethod
    def _signal_descriptors(row):
        mapping = row.get("mapping") or {}
        if mapping.get("signal_mapping_schema") == 1:
            return mapping["signals"]
        result = {}
        for sensor in ("internal", "external"):
            columns = list(mapping.get(sensor + "_columns", ()))
            settings = (
                mapping.get("preprocessing")
                if mapping.get("single_sensor") == sensor
                else None
            )
            mode = settings["source_mode"] if settings else "raw"
            result[sensor] = dict(
                mode=mode,
                raw_columns=[] if mode == "already_filtered" else columns,
                filtered_columns=columns if mode == "already_filtered" else [],
                settings=settings,
            )
        return result

    @Property("QVariantMap", notify=stateChanged)
    def selectedMappingTime(self):
        if self._selected_recording < 0:
            return {}
        mapping = self._recordings[self._selected_recording].get("mapping") or {}
        return {
            key: mapping[key]
            for key in ("time_column", "time_unit", "sample_rate_hz")
            if key in mapping
        }

    @Property("QVariantMap", notify=stateChanged)
    def selectedSignalMapping(self):
        import copy

        if self._selected_recording < 0 or not self._recordings[
            self._selected_recording
        ].get("mapping"):
            return {}
        return copy.deepcopy(
            self._signal_descriptors(self._recordings[self._selected_recording])
        )

    def _read_signal_columns(self, row, mapping, sensor, columns):
        selected = tuple(columns)
        source = ColumnMapping(
            int(mapping["data_start_row"]),
            mapping.get("header_row"),
            mapping.get("time_column") or None,
            mapping.get("time_unit") or None,
            None if mapping.get("time_column") else float(mapping["sample_rate_hz"]),
            selected if sensor == "internal" else (),
            selected if sensor == "external" else (),
            sensor,
        )
        return self._reader.read(row["path"], source, row.get("worksheet") or None)

    @Slot("QVariantMap", result=bool)
    def confirmSignalMapping(self, request):
        if self.learningSettingsLocked or self._selected_recording < 0:
            return False
        try:
            row = self._recordings[self._selected_recording]
            signals = {}
            reference = None
            sensor_columns = {}
            for sensor in ("internal", "external"):
                draft = request["signals"][sensor]
                mode = draft["mode"]
                if mode not in {"raw", "already_filtered", "application_filtered"}:
                    raise ValueError("Choose one preprocessing mode per IMU")
                raw = list(draft.get("raw_columns", ()))
                filtered = list(draft.get("filtered_columns", ()))
                if filtered and mode != "already_filtered":
                    raise ValueError(
                        "Existing filtered data and software filtering are mutually exclusive"
                    )
                settings = None
                if mode == "application_filtered":
                    settings = settings_from_data(draft.get("settings"))
                    if (
                        settings.sensor != sensor
                        or settings.source_mode != mode
                        or not raw
                    ):
                        raise ValueError(
                            "Preview and adopt the filter design for " + sensor
                        )
                elif mode == "already_filtered":
                    if not filtered:
                        raise ValueError(
                            sensor.title() + " filtered XYZ mapping is required"
                        )
                    settings = SingleImuSettings(sensor)
                sensor_columns[sensor] = raw or filtered
                for columns in (raw, filtered):
                    if not columns:
                        continue
                    samples = self._read_signal_columns(row, request, sensor, columns)
                    if reference is not None and not np.array_equal(
                        reference.time_s, samples.time_s
                    ):
                        raise ValueError(
                            "All raw/filtered XYZ mappings must have the same aligned rows"
                        )
                    reference = samples
                    if settings and any(
                        abs(d.sample_rate_hz - samples.inferred_sample_rate_hz)
                        / samples.inferred_sample_rate_hz
                        > 0.005
                        for d in settings.filters
                    ):
                        raise ValueError(
                            "Sample rate changed after filter adoption; preview and adopt again"
                        )
                signals[sensor] = dict(
                    mode=mode,
                    raw_columns=raw,
                    filtered_columns=filtered,
                    settings=settings_to_data(settings) if settings else None,
                )
            internal_columns = set(
                signals["internal"]["raw_columns"]
                + signals["internal"]["filtered_columns"]
            )
            external_columns = set(
                signals["external"]["raw_columns"]
                + signals["external"]["filtered_columns"]
            )
            if internal_columns & external_columns:
                raise ValueError("Internal and External XYZ must use different columns")
            if reference is None:
                raise ValueError("Map at least one IMU complete XYZ")
            return self.confirmMapping(
                int(request["data_start_row"]),
                int(request["header_row"]),
                request.get("time_column", ""),
                request.get("time_unit", ""),
                float(request["sample_rate_hz"]),
                sensor_columns["internal"],
                sensor_columns["external"],
                float(request["robot_speed"]),
                float(request["collision_offset"]),
                signal_mapping=signals,
            )
        except (KeyError, OSError, TypeError, ValueError) as exc:
            self._status_message = str(exc)
            self.stateChanged.emit()
            return False

    @Property("QVariantList", notify=stateChanged)
    def trainingAlgorithms(self):
        return list(self._training_algorithms)

    @Property("QVariantMap", notify=stateChanged)
    def trainingSources(self):
        return dict(self._training_sources)

    @Slot(str, bool)
    def setTrainingAlgorithmSelected(self, algorithm, selected):
        if self.learningSettingsLocked or algorithm not in {"fir", "mlp", "var"}:
            return
        values = set(self._training_algorithms)
        values.add(algorithm) if selected else values.discard(algorithm)
        self._training_algorithms = tuple(
            a for a in ("fir", "mlp", "var") if a in values
        )
        self._training_selection_explicit = True
        families = tuple(
            a for a in ("fir", "mlp") if a in values or (a == "fir" and "var" in values)
        )
        self._learning_settings = replace(
            self._learning_settings, model_families=families
        )
        self._stale_results("Training algorithms changed.")
        self._mark_project_dirty()
        self.stateChanged.emit()

    @Slot(str, str)
    def setTrainingSource(self, algorithm, source):
        allowed = (
            {"internal", "external"} if algorithm == "var" else {"raw", "filtered"}
        )
        if (
            self.learningSettingsLocked
            or algorithm not in {"fir", "mlp", "var"}
            or source not in allowed
        ):
            return
        self._training_sources[algorithm] = source
        self._training_selection_explicit = True
        self._stale_results("Training signal source changed.")
        self._mark_project_dirty()
        self.stateChanged.emit()

    def _source_admission_errors(self, algorithms=None, sources=None, rows=None):
        algorithms = self._training_algorithms if algorithms is None else algorithms
        sources = self._training_sources if sources is None else sources
        errors = []
        for row in self._recordings if rows is None else rows:
            signals = self._signal_descriptors(row)
            for algorithm in algorithms:
                category = "filtered" if algorithm == "var" else sources[algorithm]
                sensors = (
                    (sources[algorithm],)
                    if algorithm == "var"
                    else ("internal", "external")
                )
                for sensor in sensors:
                    descriptor = signals.get(sensor, {})
                    available = (
                        bool(descriptor.get("raw_columns"))
                        if category == "raw"
                        else (
                            descriptor.get("mode") == "already_filtered"
                            and bool(descriptor.get("filtered_columns"))
                            or descriptor.get("mode") == "application_filtered"
                            and bool(descriptor.get("raw_columns"))
                            and bool(descriptor.get("settings"))
                        )
                    )
                    if not available:
                        errors.append(
                            f"{row['name']}: missing {sensor.title()} {category} XYZ; cannot run {algorithm.upper()}"
                        )
        return errors

    @Property(str, notify=stateChanged)
    def trainingAdmissionMessage(self):
        if not self._training_selection_explicit:
            return ""
        if not self._training_algorithms:
            return "Select at least one algorithm"
        return "\n".join(self._source_admission_errors())

    @Property(bool, notify=stateChanged)
    def varSourceReady(self):
        return bool(self._recordings) and not self._source_admission_errors(("var",))

    @Property(bool, notify=stateChanged)
    def singleImuMode(self):
        candidate = self._current_candidate()
        if candidate is not None:
            return isinstance(candidate.model, FrozenSelfImuModel)
        if self._training_selection_explicit:
            return self._training_algorithms == ("var",)
        return any(
            (row.get("mapping") or {}).get("single_sensor") for row in self._recordings
        )

    @Property("QVariantMap", notify=stateChanged)
    def selectedSingleImuConfiguration(self):
        if self._selected_recording < 0:
            return {}
        return dict(
            (self._recordings[self._selected_recording].get("mapping") or {}).get(
                "preprocessing"
            )
            or {}
        )

    @Slot("QVariantMap", result="QVariantMap")
    def previewSingleImuMapping(self, request):
        try:
            mapping = ColumnMapping(
                int(request["data_start_row"]),
                int(request["header_row"]),
                request.get("time_column") or None,
                request.get("time_unit") or None,
                None
                if request.get("time_column")
                else float(request["sample_rate_hz"]),
                tuple(request["columns"]) if request["sensor"] == "internal" else (),
                tuple(request["columns"]) if request["sensor"] == "external" else (),
                request["sensor"],
            )
            row = self._recordings[self._selected_recording]
            samples = self._reader.read(row["path"], mapping, row["worksheet"] or None)
            rate = samples.inferred_sample_rate_hz
            designs = (
                ()
                if request["source_mode"] == "already_filtered"
                else tuple(
                    design_filter(
                        FilterStageSpec(
                            v["kind"],
                            tuple(v["passband_hz"]),
                            tuple(v["stopband_hz"]),
                            float(v["passband_attenuation_ratio"]),
                            float(v["stopband_amplitude_ratio"]),
                        ),
                        rate,
                    )
                    for v in request["stages"]
                )
            )
            warmup = request["warmup_samples"]
            if isinstance(warmup, bool) or int(warmup) != warmup:
                raise ValueError("Warmup samples must be an integer")
            settings = SingleImuSettings(
                request["sensor"], request["source_mode"], designs, int(warmup)
            )
            return {
                "ok": True,
                "settings": settings_to_data(settings),
                "sample_rate_hz": rate,
                "orders": [v.order for v in designs],
                "total_order": sum(v.order for v in designs),
                "cascade_response": cascade_response(settings),
                "warmup_seconds": 0
                if settings.source_mode == "already_filtered"
                else settings.warmup_samples / rate,
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    @Slot("QVariantMap", "QVariantMap", result=bool)
    def confirmSingleImuMapping(self, request, adopted):
        try:
            settings = settings_from_data(dict(adopted))
            if (
                settings.sensor != request["sensor"]
                or settings.source_mode != request["source_mode"]
            ):
                raise ValueError(
                    "Source changed after design adoption; preview and adopt again"
                )
            if settings.warmup_samples != request["warmup_samples"]:
                raise ValueError("Warmup changed after preview; preview again")
            requested = tuple(
                FilterStageSpec(
                    v["kind"],
                    tuple(v["passband_hz"]),
                    tuple(v["stopband_hz"]),
                    float(v["passband_attenuation_ratio"]),
                    float(v["stopband_amplitude_ratio"]),
                )
                for v in request["stages"]
            )
            if (
                settings.source_mode == "application_filtered"
                and tuple(d.specification for d in settings.filters) != requested
            ):
                raise ValueError(
                    "Filter changed after adoption; preview and adopt again"
                )
            return self.confirmMapping(
                int(request["data_start_row"]),
                int(request["header_row"]),
                request.get("time_column") or "",
                request.get("time_unit") or "",
                float(request["sample_rate_hz"]),
                request["columns"] if settings.sensor == "internal" else [],
                request["columns"] if settings.sensor == "external" else [],
                float(request["robot_speed"]),
                float(request["collision_offset"]),
                preprocessing=settings,
            )
        except Exception as exc:
            self._status_message = str(exc)
            self.stateChanged.emit()
            return False

    @Slot(str)
    def setNumericType(self, value: str) -> None:
        if value not in {"float32", "float64", ""}:
            return
        if self._run_state in {
            "Learning",
            "Qualifying",
            "Refining Speed Range",
            "Cancelling",
        }:
            self._status_message = (
                "Target Numeric Type is immutable while Learning is running."
            )
            self.stateChanged.emit()
            return
        if self._numeric_type != value:
            self._stale_results("Target Numeric Type changed.")
            self._mark_project_dirty()
        self._numeric_type = value
        self.stateChanged.emit()

    @Slot(str, float, float, str, result=bool)
    def createAnnotation(
        self, kind_text: str, start_fraction: float, end_fraction: float, reason: str
    ) -> bool:
        if self._selected_recording < 0 or self._selected_sample_count() == 0:
            return False
        try:
            kind = self._activity_kind(kind_text)
            start, end = self._fraction_range(start_fraction, end_fraction)
            interval = AnnotationInterval(
                kind,
                start,
                end,
                reason.strip() or None,
                interval_id=self._new_annotation_id(),
            )
        except ValueError as exc:
            self._status_message = str(exc)
            self.stateChanged.emit()
            return False
        values = self._annotations.get(self._selected_recording, ()) + (interval,)
        if kind is ActivityKind.CYCLE:
            row = self._recordings[self._selected_recording]
            speed = row.get("speed")
            template = (
                self._annotation_templates.get(float(speed))
                if speed is not None
                else None
            )
            confirmed_cycles = [
                item
                for item in values
                if item.kind is ActivityKind.CYCLE and not item.provisional
            ]
            if template is not None and len(confirmed_cycles) == 1:
                try:
                    recording = self._recording_from_state(
                        self._selected_recording, values
                    )
                    values = self._workspace.project_annotation_template(
                        recording, template
                    ).annotations
                except (KeyError, ValueError) as exc:
                    self._status_message = str(exc)
                    self.stateChanged.emit()
                    return False
        self._push_annotation_history()
        self._annotations[self._selected_recording] = values
        try:
            self._selected_annotation = values.index(interval)
        except ValueError:
            self._selected_annotation = -1
        self._selected_annotations = (
            {self._selected_annotation} if self._selected_annotation >= 0 else set()
        )
        self._invalidate_annotation_truth()
        self._status_message = (
            f"Created {kind.value} interval at samples {start}–{end}."
        )
        self.stateChanged.emit()
        return True

    @Slot(int)
    def selectAnnotation(self, index: int) -> None:
        values = self._annotations.get(self._selected_recording, ())
        self._selected_annotation = index if 0 <= index < len(values) else -1
        self._selected_annotations = (
            {self._selected_annotation} if self._selected_annotation >= 0 else set()
        )
        self.stateChanged.emit()

    @Slot(int, bool)
    def toggleAnnotationSelection(self, index: int, additive: bool) -> None:
        values = self._annotations.get(self._selected_recording, ())
        if not 0 <= index < len(values):
            return
        if not additive:
            self._selected_annotations = {index}
        elif index in self._selected_annotations:
            self._selected_annotations.remove(index)
        else:
            self._selected_annotations.add(index)
        self._selected_annotation = (
            index
            if index in self._selected_annotations
            else next(iter(sorted(self._selected_annotations)), -1)
        )
        self.stateChanged.emit()

    @Slot(int, bool, bool, float, result=bool)
    def commitAnnotationGesture(
        self, index: int, additive: bool, moved: bool, delta_fraction: float
    ) -> bool:
        values = self._annotations.get(self._selected_recording, ())
        if not 0 <= index < len(values):
            return False
        was_selected = index in self._selected_annotations
        if not was_selected:
            self._selected_annotations = (
                set(self._selected_annotations) | {index} if additive else {index}
            )
        elif not moved:
            if additive:
                self._selected_annotations.remove(index)
            else:
                self._selected_annotations = {index}
        self._selected_annotation = (
            index
            if index in self._selected_annotations
            else next(iter(sorted(self._selected_annotations)), -1)
        )
        if moved:
            return self.moveSelectedAnnotations(0.0, delta_fraction)
        self.stateChanged.emit()
        return True

    @Slot(float, float, result=bool)
    def moveSelectedAnnotations(
        self, _start_fraction: float, delta_fraction: float
    ) -> bool:
        values = list(self._annotations.get(self._selected_recording, ()))
        selected = sorted(
            index for index in self._selected_annotations if 0 <= index < len(values)
        )
        sample_count = self._selected_sample_count()
        if not selected or sample_count <= 0:
            return False
        try:
            delta = float(delta_fraction)
            if not math.isfinite(delta):
                raise ValueError("annotation displacement must be finite")
            lower = -min(values[index].start_index / sample_count for index in selected)
            upper = 1.0 - max(
                values[index].end_index / sample_count for index in selected
            )
            delta = max(lower, min(upper, delta))
            replacements: dict[int, AnnotationInterval] = {}
            for index in selected:
                current = values[index]
                start, end = self._fraction_range(
                    current.start_index / sample_count + delta,
                    current.end_index / sample_count + delta,
                )
                replacements[index] = AnnotationInterval(
                    current.kind,
                    start,
                    end,
                    current.reason,
                    interval_id=current.interval_id,
                )
        except ValueError as exc:
            self._status_message = str(exc)
            self.stateChanged.emit()
            return False
        self._push_annotation_history()
        for index, replacement in replacements.items():
            values[index] = replacement
        self._annotations[self._selected_recording] = tuple(values)
        self._invalidate_annotation_truth()
        self._status_message = f"Moved {len(selected)} selected annotation(s) by {delta * sample_count:g} samples."
        self.stateChanged.emit()
        return True

    @Slot(int, float, float, result=bool)
    def updateAnnotation(
        self, index: int, start_fraction: float, end_fraction: float
    ) -> bool:
        values = list(self._annotations.get(self._selected_recording, ()))
        if not 0 <= index < len(values):
            return False
        try:
            start, end = self._fraction_range(start_fraction, end_fraction)
            current = values[index]
            replacement = AnnotationInterval(
                current.kind,
                start,
                end,
                current.reason,
                interval_id=current.interval_id,
            )
        except ValueError as exc:
            self._status_message = str(exc)
            self.stateChanged.emit()
            return False
        self._push_annotation_history()
        values[index] = replacement
        self._annotations[self._selected_recording] = tuple(values)
        self._selected_annotation = index
        self._selected_annotations = {index}
        self._invalidate_annotation_truth()
        self.stateChanged.emit()
        return True

    @Slot()
    def deleteSelectedAnnotation(self) -> None:
        values = list(self._annotations.get(self._selected_recording, ()))
        if not 0 <= self._selected_annotation < len(values):
            return
        self._push_annotation_history()
        del values[self._selected_annotation]
        self._annotations[self._selected_recording] = tuple(values)
        self._selected_annotation = -1
        self._selected_annotations.clear()
        self._invalidate_annotation_truth()
        self._status_message = "Selected annotation deleted."
        self.stateChanged.emit()

    @Slot()
    def undoAnnotation(self) -> None:
        history = self._annotation_undo.get(self._selected_recording, [])
        if not history:
            return
        current = self._annotations.get(self._selected_recording, ())
        self._annotation_redo.setdefault(self._selected_recording, []).append(current)
        self._annotations[self._selected_recording] = history.pop()
        self._selected_annotation = -1
        self._selected_annotations.clear()
        self._invalidate_annotation_truth()
        self.stateChanged.emit()

    @Slot()
    def redoAnnotation(self) -> None:
        history = self._annotation_redo.get(self._selected_recording, [])
        if not history:
            return
        current = self._annotations.get(self._selected_recording, ())
        self._annotation_undo.setdefault(self._selected_recording, []).append(current)
        self._annotations[self._selected_recording] = history.pop()
        self._selected_annotation = -1
        self._selected_annotations.clear()
        self._invalidate_annotation_truth()
        self.stateChanged.emit()

    @Slot(result=bool)
    def confirmAnnotations(self) -> bool:
        recordings: list[Recording] = []
        for index, row in enumerate(self._recordings):
            try:
                samples = self._samples.get(index)
                if samples is None or row.get("mappingStatus") != "Confirmed":
                    raise ValueError(
                        f"{row.get('name', index)} must have confirmed mapping before annotations"
                    )
                validated = self._workspace.validate_annotations(
                    len(samples.time_s),
                    self._annotations.get(index, ()),
                    getattr(samples, "discontinuity_before", None),
                )
            except ValueError as exc:
                name = str(row.get("name", f"Recording {index + 1}"))
                self._selected_recording = index
                self._selected_annotation = -1
                self._annotations_ready = False
                self._confirmed_workspace = None
                self._annotation_blocker_message = f"{name}: {exc}"
                self._status_message = self._annotation_blocker_message
                self.stateChanged.emit()
                return False
            confirmed = tuple(
                replace(
                    item,
                    provisional=False,
                    source_recording_id=None,
                    source_cycle_index=None,
                )
                if item.provisional
                else item
                for item in validated
            )
            self._annotations[index] = confirmed
            recordings.append(self._recording_from_state(index, confirmed))
        self._confirmed_workspace = WorkspaceSnapshot(tuple(recordings))
        self._stale_results("Confirmed annotation evidence changed.")
        self._annotations_ready = True
        self._annotation_blocker_message = ""
        self._mark_project_dirty()
        self._status_message = (
            "Cycle, Pick, Put, Fork Collision, and derived Normal Motion are ready."
        )
        self.stateChanged.emit()
        return True

    @Slot()
    def startLearning(self) -> None:
        if not self.canStartLearning:
            if self.trainingAdmissionMessage:
                self._status_message = self.trainingAdmissionMessage
                self.stateChanged.emit()
                return
            if (
                self._learning_settings.training_mode is TrainingMode.FIXED_GRID
                and not self.fixedGridSelectionsReady
            ):
                self._status_message = "Select at least one History and one Ridge alpha before Start Learning."
            else:
                self._status_message = (
                    "Resolve every readiness blocker before Start Learning."
                )
            self.stateChanged.emit()
            return
        try:
            captured_batch = (
                self._prepare_training_batch()
                if self._training_selection_explicit
                else None
            )
            dataset = (
                captured_batch.workspace if captured_batch else self.learning_dataset()
            )
            offsets = tuple(
                sorted({item.collision_offset_mm for item in dataset.recordings})
            )
            speeds = tuple(
                sorted({item.robot_speed_mm_s for item in dataset.recordings})
            )
            state = self._learning.initial_fallback_state(offsets, speeds)
            if captured_batch is None:
                self._learning.build_fit_evidence(
                    dataset, state.active_offsets, state.training_speeds
                )
                self._learning.build_cross_validation_plan(
                    dataset, offsets, speeds, fold_count=self._learning_settings.n_fold
                )
            self._active_learning_request = captured_batch or LearningRequest(
                dataset, self._numeric_type, self._learning_settings.for_run()
            )
            self._set_training_fallback_state(
                state.active_offsets,
                state.excluded_offsets,
                state.training_speeds,
                offsets,
                speeds,
                state.outer_round,
                state.inner_round,
            )
            self._training_current_speed = state.training_speeds[0]
            self._training_current_offset = state.active_offsets[0]
        except ValueError as exc:
            self._finish_learning_run("Failed", str(exc))
            self._diagnostics.record_learning_finished("Failed", str(exc))
            self._status_message = str(exc)
            self.stateChanged.emit()
            return
        self._begin_learning_run()
        recording_count = (
            len(self._confirmed_workspace.recordings)
            if self._confirmed_workspace
            else 0
        )
        self._diagnostics.record_learning_started(self._numeric_type, recording_count)
        self._progress = 0.0
        self._run_state = "Learning"
        self._header_preview = ""
        self._profiles.clear()
        self._retained_candidates.clear()
        self._learning_family_provenance = ()
        self._learning_run_provenance = None
        self._kernel_training_evidence = {}
        self._diagnostic_candidate_ids.clear()
        self._selected_kernel_ids.clear()
        self._preview_kernel_id = ""
        self._mark_project_dirty()
        worker = LearningWorker(
            self._learning,
            self._active_learning_request,
            self._batch_requests if self._training_selection_explicit else None,
        )
        worker.signals.progressed.connect(self._on_learning_progress)
        worker.signals.completed.connect(self._on_learning_completed)
        worker.signals.failed.connect(self._on_learning_failed)
        worker.signals.cancelled.connect(self._on_learning_cancelled)
        self._learning_worker = worker
        QThreadPool.globalInstance().start(worker)
        self.stateChanged.emit()

    @Slot()
    def cancelLearning(self) -> None:
        if self._learning_worker is None:
            return
        self._learning_worker.cancel()
        self._run_state = "Cancelling"
        self._status_message = (
            "Cancellation requested; finishing the current bounded work unit."
        )
        self.stateChanged.emit()

    @Slot(str)
    def setHeaderFormat(self, value: str) -> None:
        if value in {"C++17", "C99-compatible"}:
            self._header_format = value
            if self._run_state in {"Complete", "Cancelled"}:
                self._refresh_header_preview()
            self.stateChanged.emit()

    @Slot(int, bool)
    def setKernelSelected(self, index: int, selected: bool) -> None:
        rows = self.resultKernels
        if not 0 <= index < len(rows):
            return
        kernel_id = str(rows[index]["kernelId"])
        if not bool(rows[index].get("exportable")):
            return
        if selected:
            self._selected_kernel_ids.add(kernel_id)
            self._preview_kernel_id = kernel_id
        else:
            self._selected_kernel_ids.discard(kernel_id)
            if self._preview_kernel_id == kernel_id:
                self._preview_kernel_id = next(
                    iter(sorted(self._selected_kernel_ids)), ""
                )
        self._mark_project_dirty()
        self._refresh_header_preview()
        self.stateChanged.emit()

    @Slot(int)
    def previewKernel(self, index: int) -> None:
        rows = self.resultKernels
        if 0 <= index < len(rows):
            self._preview_kernel_id = str(rows[index]["kernelId"])
            self._replay_recording_index = 0
            self._mark_project_dirty()
            self._refresh_header_preview()
            self.stateChanged.emit()

    @Slot(int)
    def selectAnalyticalKernel(self, index: int) -> None:
        self.previewKernel(index)

    @Slot(int)
    def selectRetainedKernel(self, index: int) -> None:
        self.previewKernel(index)

    def _json_export_text(self, kernel_id: str, model_name: str) -> str:
        if self._run_state not in {"Complete", "Cancelled"}:
            raise ValueError(
                "JSON export requires current qualified dual-IMU FIR results"
            )
        profile = next((p for p in self._profiles if p.kernel_id == kernel_id), None)
        if profile is None:
            raise ValueError("Choose a current qualified model before JSON export")
        candidate = next(
            (c for c in self._retained_candidates if c.candidate_id == kernel_id), None
        )
        config = candidate.detector_config if candidate is not None else None
        if config is None:
            # Historical SemanticProfile/header contract fixes these release settings.
            config = DetectorConfig(
                profile.numeric_type,
                profile.score_mode,
                profile.confirmation_mode,
                profile.threshold,
            )
        if (
            config.numeric_type != profile.numeric_type
            or config.confirmation_mode != profile.confirmation_mode
            or config.score_mode != profile.score_mode
            or config.threshold != profile.threshold
        ):
            raise ValueError("Frozen detector and qualified profile are inconsistent")
        return self._export.render_json(
            profile,
            model_name,
            input_units="g",
            release_ratio=config.release_ratio,
            release_quiet_time_s=config.release_quiet_time_s,
        )

    @Property("QVariantList", notify=stateChanged)
    def jsonExportKernels(self) -> list[dict]:
        candidates = {c.candidate_id: c for c in self._retained_candidates}
        rows = []
        for profile in self._profiles:
            if not profile.qualified:
                continue
            reason = ""
            if self._run_state not in {"Complete", "Cancelled"}:
                reason = "JSON export requires current qualified results."
            elif profile.model_family != "fir":
                reason = "JSON export supports dual-IMU FIR/Ridge only."
            elif profile.confirmation_mode != "1_OF_1":
                reason = "JSON export requires qualification with 1_OF_1 confirmation."
            candidate = candidates.get(profile.kernel_id)
            rows.append(
                {
                    "kernelId": profile.kernel_id,
                    "kernelDepth": f"{profile.effective_history_ms:g} ms / {profile.tap_count} taps",
                    "threshold": f"{profile.threshold:.9g}",
                    "qualifiedRange": self._discrete_speed_text(
                        candidate.passing_speeds
                    )
                    if candidate is not None
                    else self._range_text(profile.qualified_speed_range),
                    "exportable": not reason,
                    "exportReason": reason,
                }
            )
        return rows

    @Slot(str, result="QVariantList")
    def prepareJsonExport(self, kernel_id: str) -> list[dict]:
        profile = next((p for p in self._profiles if p.kernel_id == kernel_id), None)
        if profile is None:
            self._status_message = (
                "JSON export unavailable: model is no longer qualified."
            )
            self.stateChanged.emit()
            return []
        name = self._export.default_model_name(profile)
        reason = self.validateJsonModelName(kernel_id, name)
        if reason:
            self._status_message = f"JSON export unavailable: {reason}"
            self.stateChanged.emit()
            return []
        return [
            {
                "kernelId": kernel_id,
                "modelName": name,
                "sampleRate": profile.sample_rate_hz,
                "numericType": profile.numeric_type,
            }
        ]

    @Slot(result="QVariantList")
    def prepareJsonExports(self) -> list[dict]:
        rows = []
        try:
            for profile in self._profiles:
                if profile.kernel_id not in self._selected_kernel_ids:
                    continue
                name = self._export.default_model_name(profile)
                self._json_export_text(profile.kernel_id, name)
                rows.append(
                    {
                        "kernelId": profile.kernel_id,
                        "modelName": name,
                        "sampleRate": profile.sample_rate_hz,
                        "numericType": profile.numeric_type,
                    }
                )
            if not rows:
                raise ValueError(
                    "Select at least one qualified FIR model before JSON export"
                )
        except (ValueError, TypeError, OverflowError) as exc:
            self._status_message = f"JSON export unavailable: {exc}"
            self.stateChanged.emit()
            return []
        return rows

    @Slot(str, str, result=str)
    def validateJsonModelName(self, kernel_id: str, model_name: str) -> str:
        try:
            self._json_export_text(kernel_id, model_name)
        except (ValueError, TypeError, OverflowError) as exc:
            return str(exc)
        return ""

    @Slot(str, str, QUrl, bool, result=str)
    def exportJsonModel(
        self, kernel_id: str, model_name: str, destination: QUrl, replace: bool
    ) -> str:
        try:
            if not destination.isLocalFile():
                raise ValueError("Choose a local JSON destination")
            text = self._json_export_text(kernel_id, model_name)
            path = AtomicProfileWriter.write_json(
                destination.toLocalFile(), text, replace=replace
            )
        except FileExistsError:
            self._status_message = "JSON file already exists; choose Replace or Cancel."
            self.stateChanged.emit()
            return "exists"
        except (OSError, ValueError, TypeError, OverflowError) as exc:
            self._status_message = f"JSON export failed: {exc}"
            self.stateChanged.emit()
            return "error"
        self._status_message = f"Exported JSON model {model_name} to {path}"
        self.stateChanged.emit()
        return "saved"

    @Slot(str, result=bool)
    def prepareSelectedExport(self, url_text: str) -> bool:
        if not self.canExportSelected:
            self._status_message = (
                "Only current, selected, qualified kernels can be exported."
            )
            self.stateChanged.emit()
            return False
        selected = [
            profile
            for profile in self._profiles
            if profile.kernel_id in self._selected_kernel_ids
        ]
        if not selected:
            self._status_message = "Select at least one qualified kernel before Export."
            self.stateChanged.emit()
            return False
        url = QUrl(url_text)
        folder = Path(url.toLocalFile() if url.isLocalFile() else url_text)
        try:
            artifacts = self._export.render_batch(tuple(selected), self._header_format)
            if not folder.is_dir():
                raise ValueError("Select an existing destination folder")
        except (OSError, ValueError) as exc:
            self._status_message = str(exc)
            self.stateChanged.emit()
            return False
        self._pending_export_folder = folder
        self._pending_export_artifacts = artifacts
        self._approved_replacements.clear()
        self._pending_export_conflicts = [
            item.filename for item in artifacts if (folder / item.filename).exists()
        ]
        if self._pending_export_conflicts:
            self._status_message = (
                "Choose Replace or Skip for each existing Profile header."
            )
            self.stateChanged.emit()
            return False
        return self._commit_pending_export()

    @Slot(bool, result=bool)
    def resolveExportConflict(self, replace: bool) -> bool:
        if not self._pending_export_conflicts:
            return False
        filename = self._pending_export_conflicts.pop(0)
        if replace:
            self._approved_replacements.add(filename)
        else:
            self._pending_export_artifacts = tuple(
                item
                for item in self._pending_export_artifacts
                if item.filename != filename
            )
        if self._pending_export_conflicts:
            self.stateChanged.emit()
            return False
        return self._commit_pending_export()

    @Slot(object)
    def _on_learning_progress(self, progress: LearningProgress) -> None:
        if self._learning_worker is None:
            return
        self._switch_stage(progress.stage)
        self._run_state = progress.stage
        self._progress = progress.fraction
        self._status_message = progress.message
        self._append_training_log(progress)
        if progress.training_speeds:
            self._set_training_fallback_state(
                progress.active_offsets,
                progress.excluded_offsets,
                progress.training_speeds,
                progress.supplied_offsets,
                progress.supplied_speeds,
                progress.outer_round,
                progress.inner_round,
            )
            self._training_current_speed = progress.current_speed_mm_s
            self._training_current_offset = progress.current_offset_mm
        if "Invalid candidate" in progress.message:
            key = (progress.outer_round, progress.inner_round)
            previous = self._training_execution_summaries.get(key, "")
            self._training_execution_summaries[key] = (
                previous + ("\n" if previous else "") + progress.message
            )
        if (
            progress.worker_attempt_timings or progress.launch_available_ram_bytes > 0
        ) and progress.round_elapsed_s is not None:
            timing_parts = [
                (
                    f"History {item.history_ms} ms attempt {item.attempt} "
                    f"{self._format_duration(item.duration_s)}"
                )
                for item in progress.worker_attempt_timings
            ]
            memory = ""
            if progress.launch_available_ram_bytes > 0:
                gib = float(1024**3)
                fraction = (
                    100.0
                    * progress.process_tree_peak_rss_bytes
                    / progress.launch_available_ram_bytes
                )
                memory = (
                    f" · Peak RSS {progress.process_tree_peak_rss_bytes / gib:.2f} / "
                    f"{progress.launch_available_ram_bytes / gib:.2f} GiB ({fraction:.1f}%)"
                )
            invalid_details = [
                line
                for line in self._training_execution_summaries.get(
                    (progress.outer_round, progress.inner_round), ""
                ).splitlines()
                if "Invalid candidate" in line
            ]
            self._training_execution_summaries[
                (progress.outer_round, progress.inner_round)
            ] = (
                f"Round {progress.outer_round}.{progress.inner_round} "
                f"{self._format_duration(progress.round_elapsed_s)} · "
                + " · ".join(timing_parts)
                + memory
                + ("\n" + "\n".join(invalid_details) if invalid_details else "")
            )
            total_elapsed = (
                0.0
                if self._run_started_monotonic is None
                else time.monotonic() - self._run_started_monotonic
            )
            self._diagnostics.record_learning_timing(
                LearningTimingEvidence(
                    progress.outer_round,
                    progress.inner_round,
                    progress.round_elapsed_s,
                    self._stage_total_seconds("Training"),
                    self._stage_total_seconds("Qualification"),
                    total_elapsed,
                    tuple(
                        (item.history_ms, item.attempt, item.duration_s)
                        for item in progress.worker_attempt_timings
                    ),
                    progress.process_tree_peak_rss_bytes,
                    progress.launch_available_ram_bytes,
                    progress.worker_pids,
                )
            )
        if progress.unavailable_reason:
            self._record_unavailable_round(progress)
        self._diagnostics.record_learning_progress(
            progress.stage,
            progress.fraction,
            progress.outer_round,
            progress.inner_round,
            progress.current_speed_mm_s,
            progress.current_offset_mm,
        )
        self.stateChanged.emit()

    def _record_unavailable_round(self, progress: LearningProgress) -> None:
        invalid_details = [
            line
            for line in self._training_execution_summaries.get(
                (progress.outer_round, progress.inner_round), ""
            ).splitlines()
            if "Invalid candidate" in line
        ]
        offsets = ", ".join(f"{value:g}" for value in progress.active_offsets)
        speeds = ", ".join(f"{value:g}" for value in progress.training_speeds)
        self._training_execution_summaries[
            (progress.outer_round, progress.inner_round)
        ] = (
            f"Round {progress.outer_round}.{progress.inner_round} · Unavailable / skipped · "
            f"Offsets {offsets} mm · Speeds {speeds} mm/s · {progress.unavailable_reason}"
            + ("\n" + "\n".join(invalid_details) if invalid_details else "")
        )

    @Slot(object)
    def _on_learning_completed(self, result: QualificationResult) -> None:
        if isinstance(result, tuple):
            result, self._batch_provenance = result
        self._learning_worker = None
        self._install_learning_result(result)
        self._progress = 1.0
        if self._profiles:
            self._finish_learning_run("Complete")
            self._diagnostics.record_learning_finished("Complete", "")
            profile = self._profiles[0]
            self._set_training_fallback_state(
                profile.covered_offsets_mm,
                profile.excluded_offsets_mm,
                next(
                    candidate.training_speeds
                    for candidate in result.candidates
                    if candidate.candidate_id == profile.kernel_id
                ),
                tuple(sorted({float(item["offset"]) for item in self._recordings})),
                tuple(sorted({float(item["speed"]) for item in self._recordings})),
                profile.outer_round,
                profile.inner_round,
            )
            self._preview_kernel_id = self._profiles[0].kernel_id
            self._status_message = f"Qualification completed with {len(self._profiles)} selectable qualified kernel(s)."
        else:
            reason = (
                "Qualification failed: no kernel met the minimum qualified coverage envelope after the fallback rounds. "
                "Lower-speed conditions may have been removed from later training rounds; the remaining speed/offset "
                "conditions still failed collision detection, false-collision, or ≤ 150 ms latency requirements."
            )
            if result.unavailable_rounds:
                reason = (
                    "Qualification failed: no qualified kernel remained after the fallback search. "
                    f"{len(result.unavailable_rounds)} round(s) could not proceed to a retained qualified kernel; "
                    "see the round summaries for their scopes and reasons."
                )
            self._finish_learning_run("Failed", reason)
            self._diagnostics.record_learning_finished("Failed", reason)
            self._status_message = reason
            if result.diagnostic_candidates:
                self._preview_kernel_id = result.diagnostic_candidates[0].candidate_id
                self._status_message += f" Showing {len(result.diagnostic_candidates)} minimum-error diagnostic kernel(s)."
        self._append_training_terminal(self._run_state, self._status_message)
        if self._profiles:
            self._mark_project_dirty()
        self.stateChanged.emit()

    def _install_learning_result(self, result: QualificationResult) -> None:
        self._learning_family_provenance = result.family_provenance
        self._learning_run_provenance = result.run_provenance
        self._kernel_training_evidence = {
            c.candidate_id: c.training_evidence
            for c in result.candidates
            if c.training_evidence is not None
        }
        for skipped in result.unavailable_rounds:
            self._record_unavailable_round(skipped)
            round_text = f"{skipped.outer_round}.{skipped.inner_round}"
            if not any(
                item["round"] == round_text and item["message"] == skipped.message
                for item in self._training_log_entries
            ):
                self._append_training_log(skipped)
        self._retained_candidates = list(result.candidates)
        self._diagnostic_candidate_ids = {
            item.candidate_id for item in result.diagnostic_candidates
        }
        self._profiles = self._profiles_from_qualification(result)

    @Slot(str)
    def _on_learning_failed(self, message: str) -> None:
        self._learning_worker = None
        self._finish_learning_run("Failed", message)
        self._diagnostics.record_learning_finished("Failed", message)
        self._status_message = message
        self._append_training_terminal("Failed", message)
        self.stateChanged.emit()

    @Slot(object)
    def _on_learning_cancelled(self, result: QualificationResult) -> None:
        if isinstance(result, tuple):
            result, self._batch_provenance = result
        self._learning_worker = None
        self._install_learning_result(result)
        if self._profiles:
            self._preview_kernel_id = self._profiles[0].kernel_id
            self._refresh_header_preview()
            message = f"Learning cancelled; retained {len(self._profiles)} completed qualified kernel(s) for Replay."
        elif result.diagnostic_candidates:
            self._preview_kernel_id = result.diagnostic_candidates[0].candidate_id
            message = (
                "Learning cancelled with no completed qualified kernel; retained "
                f"{len(result.diagnostic_candidates)} minimum-error diagnostic kernel(s) for Replay."
            )
        else:
            message = "Learning cancelled before any candidate completed Qualification."
        self._finish_learning_run("Cancelled", message)
        self._diagnostics.record_learning_finished("Cancelled", message)
        self._status_message = message
        self._append_training_terminal("Cancelled", message)
        if self._profiles:
            self._mark_project_dirty()
        self.stateChanged.emit()

    def _begin_learning_run(self) -> None:
        self._run_started_monotonic = time.monotonic()
        self._run_finished_monotonic = None
        self._run_started_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
        self._run_finished_at = ""
        self._run_failure_reason = ""
        self._stage_name = "Training"
        self._stage_started_monotonic = self._run_started_monotonic
        self._stage_finished_monotonic = None
        self._stage_elapsed_totals = {
            "Training": 0.0,
            "Qualification": 0.0,
            "Fallback": 0.0,
        }
        self._training_execution_summaries.clear()
        self._training_log_entries.clear()
        self._training_log_discarded_count = 0
        self._run_timer.start()

    def _append_training_log(self, progress: LearningProgress) -> None:
        evidence = progress.log_evidence
        stage = {
            "Learning": "Training",
            "Qualifying": "Qualification",
            "Refining Speed Range": "Fallback",
        }.get(progress.stage, progress.stage)
        scope_parts = []
        if progress.current_speed_mm_s is not None:
            scope_parts.append(f"Speed {progress.current_speed_mm_s:g} mm/s")
        elif progress.training_speeds:
            scope_parts.append(
                "Speeds "
                + ", ".join(f"{value:g}" for value in progress.training_speeds)
                + " mm/s"
            )
        if progress.current_offset_mm is not None:
            scope_parts.append(f"Offset {progress.current_offset_mm:g} mm")
        elif progress.active_offsets:
            scope_parts.append(
                "Offsets "
                + ", ".join(f"{value:g}" for value in progress.active_offsets)
                + " mm"
            )
        detail = progress.message
        if evidence is not None and evidence.parameter is not None:
            point = evidence.parameter
            rate = self._session_rate() if self.sessionRateReady else None
            history = (
                f"{(point.tap_count - 1) * 1000.0 / rate:g} ms / {point.tap_count} taps"
                if rate
                else f"{point.tap_count} taps"
            )
            robust = "off" if point.robust_k == 0 else str(point.robust_k)
            if evidence.kind == "parameter-best":
                detail = (
                    f"New best Parameter Loss {evidence.parameter_loss:.17g} · "
                    f"History/taps {history} · Ridge alpha {point.alpha:.17g} · Robust K {robust}"
                )
                previous = evidence.previous_parameter_loss
                if previous is not None and previous != 0:
                    improvement = (
                        100.0 * (previous - evidence.parameter_loss) / previous
                    )
                    detail += f" · Relative improvement {improvement:.6g}%"
            elif evidence.kind == "parameter-final":
                detail = (
                    f"Final Parameter Loss {evidence.parameter_loss:.4f} · "
                    f"History/taps {history} · Ridge alpha {point.alpha:.17g} · Robust K {robust}"
                )
            elif evidence.kind == "parameter-evaluated":
                disposition = (
                    "CV selected"
                    if evidence.disposition == "cv-selected"
                    else "CV rejected"
                )
                detail = (
                    f"{disposition} · Parameter Loss {evidence.parameter_loss:.17g} · "
                    f"History/taps {history} · Ridge alpha {point.alpha:.17g} · "
                    f"{evidence.reason}"
                )
            elif evidence.kind == "kernel-admitted":
                outcomes = ", ".join(
                    f"{speed:g} mm/s @ {offset:g} mm {'PASS' if passed else 'FAIL'}"
                    for speed, offset, passed in evidence.validation_outcomes
                )
                detail = (
                    f"Fold {evidence.fold_index} Kernel Loss {evidence.kernel_loss:.17g} · "
                    f"History/taps {history} · Ridge alpha {point.alpha:.17g} · Robust K {robust} · "
                    f"Validation allowance {'PASS' if evidence.validation_pass else 'FAIL'}"
                    + (f" ({outcomes})" if outcomes else "")
                )
        if (
            evidence is not None
            and evidence.parameter is not None
            and evidence.parameter.hidden_layers
        ):
            detail = (
                "MLP "
                + " → ".join(map(str, evidence.parameter.hidden_layers))
                + " · "
                + detail
            )
        elif progress.message.startswith("FIR:"):
            detail = "FIR · " + detail
        evaluated = progress.evaluated_count
        pending = progress.pending_count
        if evidence is not None:
            evaluated = evidence.evaluated_count
            pending = evidence.pending_count
        if (
            progress.stage == "Qualifying"
            and evaluated is not None
            and pending is not None
        ):
            work = f"Completed {evaluated} · Total {evaluated + pending} · Pending {pending}"
        else:
            work = (
                f"Evaluated {evaluated} · Pending {pending}"
                if evaluated is not None or pending is not None
                else ""
            )
        elapsed = (
            f"Round elapsed {self._format_duration(progress.round_elapsed_s)}"
            if progress.round_elapsed_s is not None
            else ""
        )
        if progress.unavailable_reason:
            detail += f" · Skip reason: {progress.unavailable_reason}"
        self._training_log_entries.append(
            {
                "time": datetime.now()
                .astimezone()
                .strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "stage": stage,
                "round": f"{progress.outer_round}.{progress.inner_round}",
                "scope": " · ".join(scope_parts),
                "message": progress.message,
                "work": work,
                "elapsed": elapsed,
                "detail": detail,
            }
        )
        overflow = len(self._training_log_entries) - 10_000
        if overflow > 0:
            del self._training_log_entries[:overflow]
            self._training_log_discarded_count += overflow

    def _append_training_terminal(self, state: str, message: str) -> None:
        outer, inner = self._training_round
        scope = ""
        if self._training_speeds or self._training_active_offsets:
            scope = (
                "Speeds "
                + ", ".join(f"{value:g}" for value in self._training_speeds)
                + " mm/s"
                + " · Offsets "
                + ", ".join(f"{value:g}" for value in self._training_active_offsets)
                + " mm"
            )
        self._training_log_entries.append(
            {
                "time": datetime.now()
                .astimezone()
                .strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "stage": state,
                "round": f"{outer}.{inner}",
                "scope": scope,
                "message": message,
                "work": "",
                "elapsed": self.runElapsedText,
                "detail": f"{state}: {message}",
            }
        )
        overflow = len(self._training_log_entries) - 10_000
        if overflow > 0:
            del self._training_log_entries[:overflow]
            self._training_log_discarded_count += overflow

    @staticmethod
    def _format_duration(seconds_value: float) -> str:
        elapsed = max(0, int(seconds_value))
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _finish_learning_run(self, state: str, failure_reason: str = "") -> None:
        if self._run_started_monotonic is not None:
            self._run_finished_monotonic = time.monotonic()
            self._run_finished_at = (
                datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
            )
        if self._stage_started_monotonic is not None:
            self._stage_finished_monotonic = time.monotonic()
            self._stage_elapsed_totals[self._stage_name] = (
                self._stage_elapsed_totals.get(self._stage_name, 0.0)
                + self._stage_finished_monotonic
                - self._stage_started_monotonic
            )
        self._run_failure_reason = failure_reason
        self._run_state = state
        self._run_timer.stop()

    @Slot()
    def _emit_run_timing(self) -> None:
        if (
            self._run_started_monotonic is not None
            and self._run_finished_monotonic is None
        ):
            self.stateChanged.emit()

    def _switch_stage(self, stage: str) -> None:
        display_stage = {
            "Learning": "Training",
            "Qualifying": "Qualification",
            "Refining Speed Range": "Fallback",
        }.get(stage, stage)
        if display_stage == self._stage_name:
            return
        now = time.monotonic()
        if self._stage_started_monotonic is not None:
            self._stage_finished_monotonic = now
            self._stage_elapsed_totals[self._stage_name] = (
                self._stage_elapsed_totals.get(self._stage_name, 0.0)
                + now
                - self._stage_started_monotonic
            )
        self._stage_name = display_stage
        self._stage_started_monotonic = now
        self._stage_finished_monotonic = None

    def _stage_total_seconds(self, stage: str) -> float:
        total = self._stage_elapsed_totals.get(stage, 0.0)
        if (
            self._stage_name == stage
            and self._stage_started_monotonic is not None
            and self._stage_finished_monotonic is None
        ):
            total += time.monotonic() - self._stage_started_monotonic
        return max(0.0, total)

    def _set_training_fallback_state(
        self,
        active_offsets: tuple[float, ...],
        excluded_offsets: tuple[float, ...],
        training_speeds: tuple[float, ...],
        supplied_offsets: tuple[float, ...],
        supplied_speeds: tuple[float, ...],
        outer_round: int,
        inner_round: int,
    ) -> None:
        self._training_active_offsets = tuple(active_offsets)
        self._training_excluded_offsets = tuple(excluded_offsets)
        self._training_speeds = tuple(training_speeds)
        self._training_supplied_offsets = tuple(supplied_offsets)
        self._training_supplied_speeds = tuple(supplied_speeds)
        self._training_round = (outer_round, inner_round)

    def _profiles_from_qualification(
        self, result: QualificationResult
    ) -> list[SemanticProfile]:
        sample_rate = self._session_rate()
        if sample_rate is None or self._active_learning_request is None:
            return []
        profiles: list[SemanticProfile] = []
        supplied_speeds = tuple(
            sorted({float(item["speed"]) for item in self._recordings})
        )
        for candidate in LearningService.rank_qualified_candidates(
            result.candidates, supplied_speeds
        ):
            profile = self._profile_from_candidate(
                candidate, sample_rate, self._active_learning_request.numeric_type
            )
            if profile is not None:
                profiles.append(profile)
        return profiles

    @staticmethod
    def _profile_from_candidate(
        candidate: QualifiedCandidate, sample_rate: float, numeric_type: str
    ) -> SemanticProfile | None:
        if (
            not candidate.passing_speeds
            or not LearningService.round_can_stop(candidate)
            or candidate.model is None
            or candidate.history is None
            or candidate.detector_config is None
            or not np.isfinite(candidate.worst_latency_ms)
            or not np.isfinite(candidate.robustness_margin)
            or not np.isfinite(candidate.false_trigger_robustness_margin)
            or not np.isfinite(candidate.collision_detection_robustness_margin)
        ):
            return None
        covered = candidate.active_offsets
        qualified_speeds = candidate.passing_speeds
        coverage = tuple(
            ConditionCoverage(
                row.robot_speed_mm_s,
                row.collision_offset_mm,
                row.normal_interval_count,
                row.pick_interval_count,
                row.put_interval_count,
                row.collision_interval_count,
                row.status
                if row.collision_offset_mm in covered
                and row.robot_speed_mm_s in qualified_speeds
                else "OUT_OF_QUALIFIED_RANGE",
                row.recording_count,
                row.valid_cycle_count,
                row.normal_false_events,
                row.pick_false_events,
                row.put_false_events,
                row.collision_detected_count,
                row.worst_collision_latency_ms,
            )
            for row in candidate.conditions
        )
        return SemanticProfile(
            ProjectSessionService.ALGORITHM_CONTRACT,
            numeric_type,
            sample_rate,
            candidate.history.requested_history_aliases_ms,
            candidate.history.effective_history_ms,
            candidate.model.tap_count,
            candidate.model.weights,
            candidate.model.biases,
            candidate.model.alpha,
            candidate.model.residual_centers,
            candidate.model.residual_scales,
            candidate.model.scale_method,
            candidate.model.robust_k,
            candidate.model.score_mode,
            candidate.detector_config.confirmation_mode,
            candidate.detector_config.threshold,
            candidate.candidate_id,
            candidate.worst_latency_ms,
            candidate.robustness_margin,
            candidate.false_trigger_robustness_margin,
            candidate.collision_detection_robustness_margin,
            covered,
            candidate.excluded_offsets,
            (candidate.training_speeds[0], candidate.training_speeds[-1]),
            (qualified_speeds[0], qualified_speeds[-1]),
            max(row.robot_speed_mm_s for row in candidate.conditions),
            coverage,
            True,
            candidate.outer_round,
            candidate.inner_round,
            candidate.model.initial_fit_rows,
            candidate.model.refit_rows,
            candidate.cross_validation_fold_count,
            candidate.cross_validation_evidence_level,
            candidate.cross_validation_worst_condition_mse,
            candidate.cross_validation_pooled_mse,
            "self_ridge"
            if isinstance(candidate.model, FrozenSelfImuModel)
            else ("mlp" if isinstance(candidate.model, FrozenMlpModel) else "fir"),
            getattr(candidate.model, "epochs", 0),
            getattr(candidate.model, "stop_reason", ""),
        )

    def _candidate_from_profile(
        self,
        profile: SemanticProfile,
        dataset: LearningDataset,
        stable_order: int,
    ) -> QualifiedCandidate:
        if profile.model_family == "mlp":
            model = FrozenMlpModel(
                profile.tap_count,
                tuple(
                    np.asarray(w, dtype=profile.numeric_type) for w in profile.weights
                ),
                tuple(
                    np.asarray(b, dtype=profile.numeric_type) for b in profile.biases
                ),
                profile.ridge_alpha,
                profile.residual_centers,
                profile.residual_scales,
                profile.initial_fit_rows,
                profile.refit_rows,
                profile.mlp_epochs,
                profile.mlp_stop_reason,
            )
        else:
            model = FrozenFirModel(
                profile.tap_count,
                np.asarray(profile.weights),
                np.asarray(profile.biases),
                profile.ridge_alpha,
                np.asarray(profile.residual_centers),
                np.asarray(profile.residual_scales),
                profile.scale_method,
                profile.robust_k,
                profile.score_mode,
                profile.initial_fit_rows,
                profile.refit_rows,
                profile.robust_k > 0,
            )
        if profile.model_family == "self_ridge":
            from dataclasses import fields

            preprocessing = dataset.recordings[0].preprocessing
            if preprocessing is None:
                raise ValueError("Self-model source preprocessing is missing")
            model = FrozenSelfImuModel(
                **{f.name: getattr(model, f.name) for f in fields(FrozenFirModel)},
                preprocessing=preprocessing,
            )
        config = DetectorConfig(
            profile.numeric_type,
            profile.score_mode,
            profile.confirmation_mode,
            profile.threshold,
        )
        lower_speed, upper_speed = profile.training_speed_range
        training_speeds = tuple(
            sorted(
                {
                    recording.robot_speed_mm_s
                    for recording in dataset.recordings
                    if lower_speed <= recording.robot_speed_mm_s <= upper_speed
                }
            )
        )
        if not training_speeds:
            raise ValueError(
                f"profile {profile.kernel_id} has no supplied Training speed"
            )
        candidate = self._learning.qualify_model(
            dataset,
            model,
            config,
            training_speeds=training_speeds,
            active_offsets=profile.covered_offsets_mm,
            candidate_id=profile.kernel_id,
            stable_order=stable_order,
        )
        return replace(
            candidate,
            model=model,
            history=HistorySpec(
                profile.tap_count,
                profile.requested_history_aliases_ms,
                profile.effective_history_ms,
            ),
            detector_config=config,
            active_offsets=profile.covered_offsets_mm,
            excluded_offsets=profile.excluded_offsets_mm,
            outer_round=profile.outer_round,
            inner_round=profile.inner_round,
            cross_validation_fold_count=profile.cross_validation_fold_count,
            cross_validation_evidence_level=profile.cross_validation_evidence_level,
            cross_validation_worst_condition_mse=profile.cross_validation_worst_condition_mse,
            cross_validation_pooled_mse=profile.cross_validation_pooled_mse,
        )

    def _save_project_to(self, path: Path) -> bool:
        try:
            document = self._project_service.validate(self._build_project_document())
            self._project_store.write(path, document)
        except (KeyError, OSError, TypeError, ValueError) as exc:
            self._status_message = f"Project save failed: {exc}"
            self.stateChanged.emit()
            return False
        self._project_path = path
        self._project_dirty = False
        self._status_message = f"Saved project {path.name}."
        self.stateChanged.emit()
        return True

    def _build_project_document(self) -> ProjectDocument:
        recordings: list[dict[str, object]] = []
        for index, row in enumerate(self._recordings):
            source = self._project_store.fingerprint(
                str(row["path"]), str(row.get("worksheet", ""))
            )
            samples = self._samples.get(index)
            mapping = row.get("mapping")
            recordings.append(
                {
                    "recording_id": self._recording_id_for_index(index, row),
                    "name": str(row["name"]),
                    "source": source.to_data(),
                    "mapping": mapping,
                    "sample_rate_hz": float(row["sampleRateValue"])
                    if "sampleRateValue" in row
                    else None,
                    "robot_speed_mm_s": float(row["speed"]) if "speed" in row else None,
                    "collision_offset_mm": float(row["offset"])
                    if "offset" in row
                    else None,
                    "row_count": len(samples.time_s) if samples is not None else 0,
                    "interpolated_indices": list(samples.interpolated_indices)
                    if samples is not None
                    else [],
                    "confirmed": row.get("mappingStatus") == "Confirmed",
                    "annotations": [
                        self._annotation_to_project(item)
                        for item in self._annotations.get(index, ())
                    ],
                }
            )
        data: dict[str, object] = {
            "format": self._project_service.FORMAT,
            "schema_version": self._project_service.SCHEMA_VERSION,
            "algorithm_contract": self._project_service.ALGORITHM_CONTRACT,
            "result_contract": self._project_service.RESULT_CONTRACT,
            "recordings": recordings,
            "annotation_templates": [
                {
                    "robot_speed_mm_s": template.robot_speed_mm_s,
                    "source_recording_id": template.source_recording_id,
                    "source_cycle_index": template.source_cycle_index,
                    "reference_cycle_length_samples": template.reference_cycle_length_samples,
                    "cycle_period_samples": template.cycle_period_samples,
                    "events": [
                        {
                            "kind": event.kind.value,
                            "start_phase": event.start_phase,
                            "end_phase": event.end_phase,
                            "reason": event.reason,
                        }
                        for event in template.events
                    ],
                }
                for _, template in sorted(self._annotation_templates.items())
            ],
            "reviewed_duplicate_keys": [
                list(values) for values in sorted(self._reviewed_duplicate_keys)
            ],
            "selected_recording": self._selected_recording,
            "selected_stage": self._selected_stage,
            "annotations_ready": self._annotations_ready,
            "numeric_type": self._numeric_type,
            "learning_settings": self._settings_mapping(self._learning_settings),
            "learning_family_provenance": [
                asdict(run) for run in self._learning_family_provenance
            ],
            "learning_run_provenance": asdict(self._learning_run_provenance)
            if self._learning_run_provenance
            else None,
            "kernel_training_evidence": {
                key: asdict(value)
                for key, value in self._kernel_training_evidence.items()
            },
        }
        if (
            self._learning_worker is None
            and self._run_state == "Complete"
            and self._profiles
        ):
            data["results"] = {
                "state": "complete",
                "profiles": [
                    self._profile_to_project(profile) for profile in self._profiles
                ],
                "selected_kernel_ids": sorted(self._selected_kernel_ids),
                "preview_kernel_id": self._preview_kernel_id,
            }
        if self._training_selection_explicit:
            data["training_selection"] = {
                "algorithms": list(self._training_algorithms),
                "sources": dict(self._training_sources),
            }
        if self._batch_provenance and (
            data.get("results") or data["kernel_training_evidence"]
        ):
            data["algorithm_runs"] = {
                key: {
                    "choice": dict(self._batch_source_choices[key]),
                    "candidate_ids": list(identities),
                    "learning_run_provenance": asdict(run) if run else None,
                    "learning_family_provenance": [asdict(v) for v in families],
                }
                for key, (run, families, identities) in self._batch_provenance.items()
            }
        return ProjectDocument(data)

    def _restore_project(
        self, document: ProjectDocument, source_overrides: dict[int, str] | None = None
    ) -> dict[str, object]:
        data = document.data
        overrides = source_overrides or {}
        rows: list[dict[str, object]] = []
        samples_by_index: dict[int, object] = {}
        annotations_by_index: dict[int, tuple[AnnotationInterval, ...]] = {}
        confirmed_recordings: list[Recording] = []
        for index, raw in enumerate(data["recordings"]):
            source_data = raw["source"]
            saved_source = self._project_service.source_reference(source_data)
            source_path = overrides.get(index, saved_source.path)
            if not Path(source_path).is_file():
                raise _ProjectSourceMissing(index, Path(saved_source.path).name)
            actual_source = self._project_store.fingerprint(
                source_path, saved_source.worksheet
            )
            if (
                actual_source.size_bytes != saved_source.size_bytes
                or actual_source.sha256 != saved_source.sha256
            ):
                raise ValueError(
                    f"source fingerprint mismatch: {Path(saved_source.path).name}"
                )
            mapping_data = raw["mapping"]
            if mapping_data is None:
                preview = self._reader.preview(
                    source_path, saved_source.worksheet or None, 20
                )
                try:
                    proposal = self._reader.propose_header(preview)
                    columns = list(proposal.columns)
                    header_row = proposal.header_row
                    data_start_row = proposal.data_start_row
                except ValueError:
                    columns = [str(item) for item in preview[0]] if preview else []
                    header_row = 1
                    data_start_row = 2
                rows.append(
                    {
                        "name": str(raw["name"]),
                        "path": source_path,
                        "worksheet": saved_source.worksheet,
                        "rows": "Pending",
                        "sampleRate": "Pending",
                        "mappingStatus": "Needs mapping",
                        "condition": "Needs values",
                        "validation": "Waiting",
                        "importWarnings": [],
                        "columns": columns,
                        "previewRows": [
                            {
                                "rowNumber": number + 1,
                                "cells": [
                                    "" if value is None else str(value)
                                    for value in values
                                ],
                            }
                            for number, values in enumerate(preview)
                        ],
                        "suggestedHeaderRow": header_row,
                        "suggestedDataStartRow": data_start_row,
                    }
                )
                annotations_by_index[index] = ()
                continue
            mapping = ColumnMapping(
                data_start_row=int(mapping_data["data_start_row"]),
                header_row=None
                if mapping_data["header_row"] is None
                else int(mapping_data["header_row"]),
                time_column=mapping_data["time_column"] or None,
                time_unit=mapping_data["time_unit"] or None,
                sample_rate_hz=None
                if mapping_data["sample_rate_hz"] is None
                else float(mapping_data["sample_rate_hz"]),
                internal_columns=tuple(mapping_data["internal_columns"]),
                external_columns=tuple(mapping_data["external_columns"]),
                single_sensor=mapping_data.get("single_sensor"),
            )
            if mapping.single_sensor is not None and not mapping_data.get(
                "signal_mapping_schema"
            ):
                settings_from_data(dict(mapping_data["preprocessing"]))
            loaded = self._reader.read(
                source_path, mapping, saved_source.worksheet or None
            )
            if len(loaded.time_s) != int(raw["row_count"]):
                raise ValueError(
                    f"source row count changed: {Path(saved_source.path).name}"
                )
            if tuple(raw["interpolated_indices"]) != loaded.interpolated_indices:
                raise ValueError(
                    f"interpolation provenance changed: {Path(saved_source.path).name}"
                )
            preview = self._reader.preview(
                source_path,
                saved_source.worksheet or None,
                max(20, mapping.header_row or 1),
            )
            annotations = tuple(
                self._annotation_from_project(item) for item in raw["annotations"]
            )
            row = {
                "name": str(raw["name"]),
                "path": source_path,
                "worksheet": saved_source.worksheet,
                "rows": str(len(loaded.time_s)),
                "sampleRate": f"{loaded.inferred_sample_rate_hz:.3f} Hz",
                "sampleRateValue": loaded.inferred_sample_rate_hz,
                "mappingStatus": "Confirmed",
                "condition": f"{float(raw['robot_speed_mm_s']):g} mm/s · offset {float(raw['collision_offset_mm']):g} mm",
                "speed": float(raw["robot_speed_mm_s"]),
                "offset": float(raw["collision_offset_mm"]),
                "validation": "Warning" if loaded.warnings else "Ready",
                "importWarnings": list(loaded.warnings),
                "columns": [
                    str(v).strip()
                    for v in preview[mapping.header_row - 1]
                    if v is not None and str(v).strip()
                ]
                if mapping.header_row
                else [f"Column {i + 1}" for i in range(max(len(r) for r in preview))],
                "previewRows": [
                    {
                        "rowNumber": number + 1,
                        "cells": [
                            "" if value is None else str(value) for value in values
                        ],
                    }
                    for number, values in enumerate(preview)
                ],
                "suggestedHeaderRow": mapping.header_row or 1,
                "suggestedDataStartRow": mapping.data_start_row,
                "mapping": dict(mapping_data),
            }
            if mapping_data.get("signal_mapping_schema") == 1:
                for sensor, descriptor in mapping_data["signals"].items():
                    if descriptor.get("settings"):
                        settings_from_data(descriptor["settings"])
                    for columns in (
                        descriptor["raw_columns"],
                        descriptor["filtered_columns"],
                    ):
                        if columns:
                            alternate = self._read_signal_columns(
                                row, mapping_data, sensor, columns
                            )
                            if not np.array_equal(alternate.time_s, loaded.time_s):
                                raise ValueError(
                                    "Saved signal sources have different rows"
                                )
            rows.append(row)
            samples_by_index[index] = loaded
            annotations_by_index[index] = annotations
            if bool(data["annotations_ready"]):
                validated = self._workspace.validate_annotations(
                    len(loaded.time_s), annotations, loaded.discontinuity_before
                )
                confirmed_recordings.append(
                    Recording(
                        str(raw["recording_id"]),
                        source_path,
                        loaded.inferred_sample_rate_hz,
                        loaded.time_s,
                        loaded.internal_imu,
                        loaded.external_imu,
                        TestCondition(
                            float(raw["robot_speed_mm_s"]),
                            float(raw["collision_offset_mm"]),
                        ),
                        loaded.discontinuity_before,
                        validated,
                        single_sensor=mapping_data.get("single_sensor"),
                    )
                )
        templates = {
            float(raw["robot_speed_mm_s"]): AnnotationTemplate(
                float(raw["robot_speed_mm_s"]),
                str(raw["source_recording_id"]),
                int(raw["source_cycle_index"]),
                int(raw["reference_cycle_length_samples"]),
                float(raw["cycle_period_samples"]),
                tuple(
                    self._template_event_from_project(event) for event in raw["events"]
                ),
            )
            for raw in data["annotation_templates"]
        }
        settings, settings_notices = self._settings_from_project(
            data.get("learning_settings")
        )
        run_provenance = self._run_provenance_from_project(
            data.get("learning_run_provenance")
        )
        kernel_evidence = {
            key: self._kernel_evidence_from_project(value)
            for key, value in data.get("kernel_training_evidence", {}).items()
        }
        results = data.get("results")
        profiles = (
            [self._profile_from_project(raw) for raw in results["profiles"]]
            if results
            else []
        )
        for profile in profiles:
            if profile.model_family == "fir":
                self._export.render(ProfileExportRequest(profile, "C++17"))
        confirmed_workspace = (
            WorkspaceSnapshot(tuple(confirmed_recordings))
            if confirmed_recordings
            else None
        )
        active_learning_request = None
        retained_candidates: list[QualifiedCandidate] = []
        batch_requests, batch_choices, batch_provenance = {}, {}, {}
        for key, saved_run in data.get("algorithm_runs", {}).items():
            batch_choices[key] = dict(saved_run["choice"])
            batch_provenance[key] = (
                self._run_provenance_from_project(
                    saved_run.get("learning_run_provenance")
                ),
                tuple(
                    self._run_provenance_from_project(v)
                    for v in saved_run.get("learning_family_provenance", ())
                ),
                tuple(saved_run["candidate_ids"]),
            )
            if confirmed_workspace is not None:
                dataset = self._dataset_for_choice(
                    confirmed_workspace, batch_choices[key], rows
                )
                captured = replace(
                    settings, model_families=("fir" if key == "var" else key,)
                )
                batch_requests[key] = LearningRequest(
                    dataset, str(data["numeric_type"]), captured
                )
        if profiles and confirmed_workspace is not None:
            if batch_requests:
                retained_candidates = [
                    self._candidate_from_profile(
                        profile,
                        batch_requests[
                            next(
                                key
                                for key, provenance in batch_provenance.items()
                                if profile.kernel_id in provenance[2]
                            )
                        ].workspace,
                        stable_order,
                    )
                    for stable_order, profile in enumerate(profiles)
                ]
                active_learning_request = next(iter(batch_requests.values()))
            else:
                dataset = self._learning_dataset_from_snapshot(
                    confirmed_workspace, rows
                )
                if any(p.model_family == "self_ridge" for p in profiles) and any(
                    r.preprocessing != dataset.recordings[0].preprocessing
                    for r in dataset.recordings
                ):
                    raise ValueError(
                        "Saved single-IMU recordings have inconsistent preprocessing"
                    )
                retained_candidates = [
                    self._candidate_from_profile(profile, dataset, stable_order)
                    for stable_order, profile in enumerate(profiles)
                ]
                active_learning_request = LearningRequest(
                    dataset, str(data["numeric_type"]), settings
                )
        return {
            "training_selection": data.get("training_selection"),
            "batch_requests": batch_requests,
            "batch_source_choices": batch_choices,
            "batch_provenance": batch_provenance,
            "recordings": rows,
            "samples": samples_by_index,
            "annotations": annotations_by_index,
            "templates": templates,
            "reviewed_duplicate_keys": {
                tuple(float(value) for value in raw)
                for raw in data["reviewed_duplicate_keys"]
            },
            "selected_recording": int(data["selected_recording"]),
            "selected_stage": int(data["selected_stage"]),
            "annotations_ready": bool(data["annotations_ready"]),
            "numeric_type": str(data["numeric_type"]),
            "confirmed_workspace": confirmed_workspace,
            "active_learning_request": active_learning_request,
            "retained_candidates": retained_candidates,
            "profiles": profiles,
            "learning_settings": settings,
            "learning_setting_notices": settings_notices,
            "learning_family_provenance": tuple(
                self._run_provenance_from_project(v)
                for v in data.get("learning_family_provenance", ())
            ),
            "learning_run_provenance": run_provenance,
            "kernel_training_evidence": kernel_evidence,
            "selected_kernel_ids": set(results.get("selected_kernel_ids", ()))
            if results
            else set(),
            "preview_kernel_id": str(results.get("preview_kernel_id", ""))
            if results
            else "",
        }

    def _commit_restored_project(self, restored: dict[str, object], path: Path) -> None:
        self._recordings = restored["recordings"]
        self._samples = restored["samples"]
        self._annotations = restored["annotations"]
        self._annotation_templates = restored["templates"]
        self._reviewed_duplicate_keys = restored["reviewed_duplicate_keys"]
        self._selected_recording = restored["selected_recording"]
        self._selected_stage = restored["selected_stage"]
        self._annotations_ready = restored["annotations_ready"]
        self._numeric_type = restored["numeric_type"]
        self._learning_settings = restored["learning_settings"]
        selection = restored["training_selection"]
        self._training_selection_explicit = selection is not None
        if selection is None:
            legacy_sensor = next(
                (
                    (row.get("mapping") or {}).get("single_sensor")
                    for row in self._recordings
                    if (row.get("mapping") or {}).get("single_sensor")
                ),
                None,
            )
            self._training_algorithms = (
                ("var",)
                if legacy_sensor
                else tuple(self._learning_settings.model_families)
            )
            self._training_sources = {
                "fir": "raw",
                "mlp": "raw",
                "var": legacy_sensor or "internal",
            }
        else:
            self._training_algorithms = tuple(selection["algorithms"])
            self._training_sources = dict(selection["sources"])
        self._batch_requests = restored["batch_requests"]
        self._batch_source_choices = restored["batch_source_choices"]
        self._batch_provenance = restored["batch_provenance"]
        self._learning_setting_notices = restored["learning_setting_notices"]
        self._learning_family_provenance = restored["learning_family_provenance"]
        self._learning_run_provenance = restored["learning_run_provenance"]
        self._kernel_training_evidence = restored["kernel_training_evidence"]
        self._retained_candidates = restored["retained_candidates"]
        self._diagnostic_candidate_ids = set()
        self._confirmed_workspace = restored["confirmed_workspace"]
        self._profiles = restored["profiles"]
        self._selected_kernel_ids = restored["selected_kernel_ids"]
        self._preview_kernel_id = restored["preview_kernel_id"]
        self._annotation_undo = {}
        self._annotation_redo = {}
        self._selected_annotation = -1
        self._selected_annotations.clear()
        self._next_annotation_id = self._next_manual_annotation_id(self._annotations)
        self._active_learning_request = restored["active_learning_request"]
        self._training_log_entries.clear()
        self._training_log_discarded_count = 0
        self._training_execution_summaries.clear()
        self._run_state = "Complete" if self._profiles else "Ready"
        self._progress = 1.0 if self._profiles else 0.0
        self._run_failure_reason = ""
        self._project_path = path
        self._project_dirty = False
        self._selected_stage = min(
            self._selected_stage, self._maximum_available_stage()
        )
        self._refresh_header_preview()

    def _attempt_pending_project_open(self) -> bool:
        if self._pending_project_document is None or self._pending_project_path is None:
            return False
        document = self._pending_project_document
        path = self._pending_project_path
        overrides = dict(self._pending_project_overrides)
        try:
            restored = self._restore_project(document, overrides)
        except _ProjectSourceMissing as exc:
            self._pending_project_missing_index = exc.recording_index
            self._status_message = f"Project source missing: {exc.source_name}. Locate the exact file or its folder."
            self.stateChanged.emit()
            return False
        except (ArithmeticError, OSError, TypeError, ValueError) as exc:
            self._status_message = f"Project relink failed: {exc}"
            self.stateChanged.emit()
            return False
        self._commit_restored_project(restored, path)
        self._project_dirty = bool(overrides)
        self._clear_pending_project_open()
        self._status_message = (
            f"Opened project {path.name}; relocated source paths must be saved."
            if overrides
            else f"Opened project {path.name}."
        )
        self.stateChanged.emit()
        return True

    def _clear_pending_project_open(self) -> None:
        self._pending_project_document = None
        self._pending_project_path = None
        self._pending_project_overrides = {}
        self._pending_project_missing_index = -1

    @staticmethod
    def _annotation_to_project(item: AnnotationInterval) -> dict[str, object]:
        return {
            "kind": item.kind.value,
            "start_index": item.start_index,
            "end_index": item.end_index,
            "reason": item.reason,
            "provisional": item.provisional,
            "source_recording_id": item.source_recording_id,
            "source_cycle_index": item.source_cycle_index,
            "interval_id": item.interval_id,
        }

    @staticmethod
    def _annotation_from_project(data: dict[str, object]) -> AnnotationInterval:
        return AnnotationInterval(
            ActivityKind(str(data["kind"])),
            int(data["start_index"]),
            int(data["end_index"]),
            data.get("reason") or None,
            bool(data.get("provisional", False)),
            data.get("source_recording_id") or None,
            None
            if data.get("source_cycle_index") is None
            else int(data["source_cycle_index"]),
            str(data["interval_id"]),
        )

    @staticmethod
    def _template_event_from_project(data: dict[str, object]):
        from ...domain.data_workspace.model import AnnotationTemplateEvent

        return AnnotationTemplateEvent(
            ActivityKind(str(data["kind"])),
            float(data["start_phase"]),
            float(data["end_phase"]),
            data.get("reason") or None,
        )

    @staticmethod
    def _profile_to_project(profile: SemanticProfile) -> dict[str, object]:
        return {
            name: value
            for name, value in {
                "schema_version": profile.schema_version,
                "numeric_type": profile.numeric_type,
                "sample_rate_hz": profile.sample_rate_hz,
                "requested_history_aliases_ms": list(
                    profile.requested_history_aliases_ms
                ),
                "effective_history_ms": profile.effective_history_ms,
                "tap_count": profile.tap_count,
                "weights": [np.asarray(w).tolist() for w in profile.weights]
                if profile.model_family == "mlp"
                else np.asarray(profile.weights).tolist(),
                "biases": [np.asarray(b).tolist() for b in profile.biases]
                if profile.model_family == "mlp"
                else np.asarray(profile.biases).tolist(),
                **(
                    {
                        "model_family": "mlp",
                        "model_schema": 1,
                        "mlp_epochs": profile.mlp_epochs,
                        "mlp_stop_reason": profile.mlp_stop_reason,
                    }
                    if profile.model_family == "mlp"
                    else {}
                ),
                **(
                    {"model_family": "self_ridge", "model_schema": 1, "lag_start": 1}
                    if profile.model_family == "self_ridge"
                    else {}
                ),
                "ridge_alpha": profile.ridge_alpha,
                "residual_centers": np.asarray(profile.residual_centers).tolist(),
                "residual_scales": np.asarray(profile.residual_scales).tolist(),
                "scale_method": profile.scale_method,
                "robust_k": profile.robust_k,
                "score_mode": profile.score_mode,
                "confirmation_mode": profile.confirmation_mode,
                "threshold": profile.threshold,
                "kernel_id": profile.kernel_id,
                "worst_collision_latency_ms": profile.worst_collision_latency_ms,
                "combined_robustness_margin": profile.combined_robustness_margin,
                "false_trigger_robustness_margin": profile.false_trigger_robustness_margin,
                "collision_detection_robustness_margin": profile.collision_detection_robustness_margin,
                "covered_offsets_mm": list(profile.covered_offsets_mm),
                "excluded_offsets_mm": list(profile.excluded_offsets_mm),
                "training_speed_range": list(profile.training_speed_range),
                "qualified_speed_range": list(profile.qualified_speed_range),
                "maximum_supplied_speed": profile.maximum_supplied_speed,
                "coverage": [asdict(row) for row in profile.coverage],
                "qualified": profile.qualified,
                "outer_round": profile.outer_round,
                "inner_round": profile.inner_round,
                "initial_fit_rows": profile.initial_fit_rows,
                "refit_rows": profile.refit_rows,
                "cross_validation_fold_count": profile.cross_validation_fold_count,
                "cross_validation_evidence_level": profile.cross_validation_evidence_level,
                "cross_validation_worst_condition_mse": profile.cross_validation_worst_condition_mse,
                "cross_validation_pooled_mse": profile.cross_validation_pooled_mse,
            }.items()
        }

    @staticmethod
    def _profile_from_project(data: dict[str, object]) -> SemanticProfile:
        coverage = tuple(ConditionCoverage(**row) for row in data["coverage"])
        return SemanticProfile(
            str(data["schema_version"]),
            str(data["numeric_type"]),
            float(data["sample_rate_hz"]),
            tuple(int(value) for value in data["requested_history_aliases_ms"]),
            float(data["effective_history_ms"]),
            int(data["tap_count"]),
            tuple(np.asarray(w, dtype=data["numeric_type"]) for w in data["weights"])
            if data.get("model_family") == "mlp"
            else np.asarray(data["weights"]),
            tuple(np.asarray(b, dtype=data["numeric_type"]) for b in data["biases"])
            if data.get("model_family") == "mlp"
            else np.asarray(data["biases"]),
            float(data["ridge_alpha"]),
            np.asarray(data["residual_centers"]),
            np.asarray(data["residual_scales"]),
            str(data["scale_method"]),
            int(data["robust_k"]),
            str(data["score_mode"]),
            str(data["confirmation_mode"]),
            float(data["threshold"]),
            str(data["kernel_id"]),
            float(data["worst_collision_latency_ms"]),
            float(data["combined_robustness_margin"]),
            float(data["false_trigger_robustness_margin"]),
            float(data["collision_detection_robustness_margin"]),
            tuple(float(value) for value in data["covered_offsets_mm"]),
            tuple(float(value) for value in data["excluded_offsets_mm"]),
            tuple(float(value) for value in data["training_speed_range"]),
            tuple(float(value) for value in data["qualified_speed_range"]),
            float(data["maximum_supplied_speed"]),
            coverage,
            bool(data["qualified"]),
            int(data["outer_round"]),
            int(data["inner_round"]),
            int(data["initial_fit_rows"]),
            int(data["refit_rows"]),
            int(data["cross_validation_fold_count"]),
            str(data["cross_validation_evidence_level"]),
            None
            if data["cross_validation_worst_condition_mse"] is None
            else float(data["cross_validation_worst_condition_mse"]),
            None
            if data["cross_validation_pooled_mse"] is None
            else float(data["cross_validation_pooled_mse"]),
            model_family=data.get("model_family", "fir"),
            mlp_epochs=data.get("mlp_epochs", 0),
            mlp_stop_reason=data.get("mlp_stop_reason", ""),
        )

    @staticmethod
    def _path_from_url(value: QUrl) -> Path:
        return Path(value.toLocalFile() if value.isLocalFile() else value.toString())

    def _mark_project_dirty(self) -> None:
        self._project_dirty = True

    def _completed_stage(self) -> int:
        if self._run_state == "Complete":
            return 5
        if self._annotations_ready:
            return 2
        if self.importReady:
            return 1
        return 0

    @staticmethod
    def _condition_key(row: dict[str, object]) -> tuple[float, float, float] | None:
        required = ("sampleRateValue", "speed", "offset")
        if not all(name in row for name in required):
            return None
        return tuple(float(row[name]) for name in required)

    def _duplicate_condition_groups(
        self,
    ) -> dict[tuple[float, float, float], list[dict[str, object]]]:
        groups: dict[tuple[float, float, float], list[dict[str, object]]] = {}
        for row in self._recordings:
            key = self._condition_key(row)
            if key is not None:
                groups.setdefault(key, []).append(row)
        return {key: rows for key, rows in groups.items() if len(rows) > 1}

    def _maximum_available_stage(self) -> int:
        if self._run_state == "Complete":
            return 4
        if self._run_state == "Failed" and self._retained_candidates:
            return 3
        if self._run_state in {"Learning", "Qualifying", "Cancelling"}:
            return 3
        if self._annotations_ready:
            return 2
        if self.importReady:
            return 1
        return 0

    def _session_rate(self) -> float | None:
        values = [
            float(row["sampleRateValue"])
            for row in self._recordings
            if "sampleRateValue" in row
        ]
        return float(np.median(values)) if values else None

    def workspace_snapshot(self) -> WorkspaceSnapshot:
        if self._confirmed_workspace is None:
            raise ValueError("annotation truth has not been confirmed")
        return self._confirmed_workspace

    def _dataset_for_choice(self, snapshot, choice, rows=None):
        rows = self._recordings if rows is None else rows
        algorithm, source = choice["algorithm"], choice["source"]
        errors = self._source_admission_errors((algorithm,), {algorithm: source}, rows)
        if errors:
            raise ValueError("\n".join(errors))
        transformed, effective_rows, masks = [], [], []
        for recording, row in zip(snapshot.recordings, rows):
            expected = row["mapping"].get("source_sha256")
            if (
                expected
                and self._project_store.fingerprint(
                    str(row["path"]), str(row.get("worksheet", ""))
                ).sha256
                != expected
            ):
                raise ValueError(
                    row["name"]
                    + ": source changed after mapping; remap before training"
                )
            descriptors = self._signal_descriptors(row)
            values = {"internal": None, "external": None}
            eligible = np.ones(len(recording.time_s), dtype=bool)
            settings = None
            sensors = (source,) if algorithm == "var" else ("internal", "external")
            for sensor in sensors:
                descriptor = descriptors[sensor]
                category = "filtered" if algorithm == "var" else source
                mode = descriptor["mode"]
                columns = (
                    descriptor["filtered_columns"]
                    if category == "filtered" and mode == "already_filtered"
                    else descriptor["raw_columns"]
                )
                loaded = self._read_signal_columns(row, row["mapping"], sensor, columns)
                if not np.array_equal(loaded.time_s, recording.time_s):
                    raise ValueError(
                        row["name"]
                        + ": selected source rows differ from confirmed annotations"
                    )
                xyz = getattr(loaded, sensor + "_imu")
                if category == "filtered":
                    settings = (
                        settings_from_data(descriptor["settings"])
                        if descriptor.get("settings")
                        else SingleImuSettings(sensor)
                    )
                    if settings.sensor != sensor:
                        raise ValueError(
                            row["name"] + ": filter source identity differs"
                        )
                    if algorithm != "var":
                        xyz, warm = preprocess(
                            xyz,
                            loaded.discontinuity_before,
                            settings,
                            loaded.inferred_sample_rate_hz,
                        )
                        eligible &= warm
                values[sensor] = xyz
            transformed.append(
                replace(
                    recording,
                    internal_imu=values["internal"],
                    external_imu=values["external"],
                    single_sensor=source if algorithm == "var" else None,
                )
            )
            effective_rows.append(
                {
                    "mapping": {
                        "single_sensor": source,
                        "preprocessing": settings_to_data(settings),
                    }
                    if algorithm == "var"
                    else {}
                }
            )
            masks.append(eligible)
        dataset = self._learning_dataset_from_snapshot(
            WorkspaceSnapshot(tuple(transformed)), effective_rows
        )
        if algorithm != "var":
            dataset = LearningDataset(
                tuple(
                    replace(r, training_eligible=m)
                    for r, m in zip(dataset.recordings, masks)
                )
            )
        return dataset

    def _prepare_training_batch(self):
        if self.trainingAdmissionMessage:
            raise ValueError(self.trainingAdmissionMessage)
        requests, choices = {}, {}
        for algorithm in self._training_algorithms:
            choice = {
                "algorithm": algorithm,
                "source": self._training_sources[algorithm],
            }
            try:
                dataset = self._dataset_for_choice(self.workspace_snapshot(), choice)
                captured = replace(
                    self._learning_settings,
                    model_families=("fir" if algorithm == "var" else algorithm,),
                ).for_run()
                offsets = tuple(
                    sorted({r.collision_offset_mm for r in dataset.recordings})
                )
                speeds = tuple(sorted({r.robot_speed_mm_s for r in dataset.recordings}))
                # Validate all requested jobs before accepting any worker dispatch.
                validation_dataset = (
                    LearningDataset(
                        tuple(
                            prepare_recording(r, r.preprocessing)
                            for r in dataset.recordings
                        )
                    )
                    if algorithm == "var"
                    else dataset
                )
                self._learning.build_fit_evidence(validation_dataset, offsets, speeds)
                self._learning.build_cross_validation_plan(
                    validation_dataset, offsets, speeds, fold_count=captured.n_fold
                )
            except (OSError, ValueError) as exc:
                names = ", ".join(str(row["name"]) for row in self._recordings)
                raise ValueError(
                    f"{names}: cannot run {algorithm.upper()}: {exc}"
                ) from exc
            requests[algorithm] = LearningRequest(dataset, self._numeric_type, captured)
            choices[algorithm] = choice
        if not requests:
            raise ValueError("Select at least one algorithm")
        self._batch_requests = requests
        self._batch_source_choices = choices
        self._batch_provenance = {}
        return next(iter(requests.values()))

    def learning_dataset(self, algorithm=None) -> LearningDataset:
        if algorithm is not None:
            return self._dataset_for_choice(
                self.workspace_snapshot(),
                {"algorithm": algorithm, "source": self._training_sources[algorithm]},
            )
        return self._learning_dataset_from_snapshot(self.workspace_snapshot())

    def _learning_dataset_from_snapshot(
        self, snapshot: WorkspaceSnapshot, mapped_rows=None
    ) -> LearningDataset:
        mapped: list[TrainingRecording] = []
        source_rows = self._recordings if mapped_rows is None else mapped_rows
        for recording_index, recording in enumerate(snapshot.recordings):
            mapping_data = (
                (source_rows[recording_index].get("mapping") or {})
                if recording_index < len(source_rows)
                else {}
            )
            preprocessing = (
                settings_from_data(mapping_data["preprocessing"])
                if mapping_data.get("single_sensor")
                else None
            )
            cycles = tuple(
                item
                for item in recording.annotations
                if item.kind is ActivityKind.CYCLE
            )
            evidence = tuple(
                self._map_learning_interval(interval, cycles)
                for interval in (
                    tuple(
                        item
                        for item in recording.annotations
                        if item.kind is not ActivityKind.CYCLE
                    )
                    + self._workspace.derive_normal_intervals(
                        recording,
                        collision_response_window_s=self._learning.COLLISION_DETECTION_WINDOW_S,
                    )
                )
            )
            discontinuities = recording.discontinuity_before
            if discontinuities is None:
                discontinuities = np.zeros(len(recording.time_s), dtype=np.bool_)
            mapped.append(
                TrainingRecording(
                    recording.recording_id,
                    recording.condition.robot_speed_mm_s,
                    recording.condition.collision_offset_mm,
                    recording.sample_rate_hz,
                    recording.time_s,
                    recording.internal_imu,
                    recording.external_imu,
                    discontinuities,
                    evidence,
                    preprocessing=preprocessing,
                )
            )
        dataset = LearningDataset(tuple(mapped))
        self._learning.validate_dataset(dataset)
        return dataset

    @staticmethod
    def _map_learning_interval(
        interval: AnnotationInterval, cycles: tuple[AnnotationInterval, ...]
    ) -> LearningInterval:
        cycle_index = next(
            (
                index
                for index, cycle in enumerate(cycles)
                if cycle.start_index <= interval.start_index
                and interval.end_index <= cycle.end_index
            ),
            -1,
        )
        return LearningInterval(
            interval.kind.value, interval.start_index, interval.end_index, cycle_index
        )

    def _recording_from_state(
        self, index: int, annotations: tuple[AnnotationInterval, ...]
    ) -> Recording:
        row = self._recordings[index]
        samples = self._samples[index]
        worksheet = str(row.get("worksheet", ""))
        identity = (
            f"recording-{index + 1}"
            if not worksheet
            else f"recording-{index + 1}:{worksheet}"
        )
        return Recording(
            recording_id=identity,
            source_path=str(row["path"]),
            sample_rate_hz=float(row["sampleRateValue"]),
            time_s=samples.time_s,
            internal_imu=samples.internal_imu,
            external_imu=samples.external_imu,
            condition=TestCondition(float(row["speed"]), float(row["offset"])),
            discontinuity_before=getattr(samples, "discontinuity_before", None),
            annotations=annotations,
            single_sensor=(row.get("mapping") or {}).get("single_sensor"),
        )

    def _annotation_validation_error(self, index: int) -> str:
        if not 0 <= index < len(self._recordings):
            return "Recording is unavailable"
        row = self._recordings[index]
        samples = self._samples.get(index)
        if samples is None or row.get("mappingStatus") != "Confirmed":
            return "Mapping must be confirmed before annotation"
        try:
            self._workspace.validate_annotations(
                len(samples.time_s),
                self._annotations.get(index, ()),
                getattr(samples, "discontinuity_before", None),
            )
        except ValueError as exc:
            return str(exc)
        return ""

    @staticmethod
    def _cycle_index(
        annotations: tuple[AnnotationInterval, ...], selected: AnnotationInterval
    ) -> int:
        cycles = tuple(
            sorted(
                (item for item in annotations if item.kind is ActivityKind.CYCLE),
                key=lambda item: (item.start_index, item.end_index),
            )
        )
        try:
            return cycles.index(selected)
        except ValueError as exc:
            raise ValueError("Selected interval is not an available Cycle") from exc

    @staticmethod
    def _recording_id_for_index(index: int, row: dict[str, object]) -> str:
        worksheet = str(row.get("worksheet", ""))
        return (
            f"recording-{index + 1}"
            if not worksheet
            else f"recording-{index + 1}:{worksheet}"
        )

    def _recording_index_for_id(self, recording_id: str) -> int | None:
        return next(
            (
                index
                for index, row in enumerate(self._recordings)
                if self._recording_id_for_index(index, row) == recording_id
            ),
            None,
        )

    def _selected_sample_count(self) -> int:
        samples = self._samples.get(self._selected_recording)
        return len(samples.time_s) if samples is not None else 0

    @staticmethod
    def _activity_kind(kind_text: str) -> ActivityKind:
        aliases = {
            "Cycle": ActivityKind.CYCLE,
            "Pick": ActivityKind.PICK,
            "Robot Pick": ActivityKind.PICK,
            "Put": ActivityKind.PUT,
            "Robot Put": ActivityKind.PUT,
            "Fork Collision": ActivityKind.FORK_COLLISION,
            "Robot Fork Collision": ActivityKind.FORK_COLLISION,
            "Ignore": ActivityKind.IGNORE,
        }
        try:
            return aliases[kind_text]
        except KeyError as exc:
            raise ValueError(
                "Select Cycle, Pick, Put, Fork Collision, or Ignore"
            ) from exc

    def _fraction_range(
        self, start_fraction: float, end_fraction: float
    ) -> tuple[int, int]:
        if not math.isfinite(start_fraction) or not math.isfinite(end_fraction):
            raise ValueError("annotation coordinates must be finite")
        sample_count = self._selected_sample_count()
        low = max(0.0, min(1.0, min(start_fraction, end_fraction)))
        high = max(0.0, min(1.0, max(start_fraction, end_fraction)))
        start = min(sample_count - 1, int(round(low * sample_count)))
        end = min(sample_count, int(round(high * sample_count)))
        if end <= start:
            end = min(sample_count, start + 1)
        return start, end

    def _push_annotation_history(self) -> None:
        current = self._annotations.get(self._selected_recording, ())
        self._annotation_undo.setdefault(self._selected_recording, []).append(current)
        self._annotation_redo[self._selected_recording] = []

    @staticmethod
    def _next_manual_annotation_id(
        annotations: dict[int, tuple[AnnotationInterval, ...]],
    ) -> int:
        maximum = 0
        for values in annotations.values():
            for interval in values:
                prefix, separator, suffix = interval.interval_id.partition("-")
                if (
                    prefix == "annotation"
                    and separator
                    and suffix.isascii()
                    and suffix.isdigit()
                ):
                    maximum = max(maximum, int(suffix))
        return maximum + 1

    def _new_annotation_id(self) -> str:
        identity = f"annotation-{self._next_annotation_id}"
        self._next_annotation_id += 1
        return identity

    def _invalidate_annotation_truth(self) -> None:
        self._annotations_ready = False
        self._confirmed_workspace = None
        self._mark_project_dirty()
        self._stale_results("Annotation evidence changed.")

    def _refresh_header_preview(self) -> None:
        profile = next(
            (
                item
                for item in self._profiles
                if item.kernel_id == self._preview_kernel_id
            ),
            None,
        )
        self._header_preview = (
            self._export.render(ProfileExportRequest(profile, self._header_format))
            if profile is not None and profile.model_family == "fir"
            else ""
        )

    def _current_profile(self) -> SemanticProfile | None:
        if self._preview_kernel_id:
            return next(
                (
                    item
                    for item in self._profiles
                    if item.kernel_id == self._preview_kernel_id
                ),
                None,
            )
        return self._profiles[0] if self._profiles else None

    def _current_candidate(self) -> QualifiedCandidate | None:
        if self._preview_kernel_id:
            selected = next(
                (
                    item
                    for item in self._retained_candidates
                    if item.candidate_id == self._preview_kernel_id
                ),
                None,
            )
            if selected is not None:
                return selected
        return self._retained_candidates[0] if self._retained_candidates else None

    def _learning_dataset_for_replay(self) -> LearningDataset | None:
        candidate = self._current_candidate()
        key = next(
            (
                key
                for key, provenance in self._batch_provenance.items()
                if candidate and candidate.candidate_id in provenance[2]
            ),
            "",
        )
        if key in self._batch_requests:
            return self._batch_requests[key].workspace
        if self._active_learning_request is None:
            return None
        workspace = self._active_learning_request.workspace
        return workspace if isinstance(workspace, LearningDataset) else None

    def _replay_recording(self) -> TrainingRecording | None:
        dataset = self._learning_dataset_for_replay()
        if dataset is None or not dataset.recordings:
            return None
        index = min(self._replay_recording_index, len(dataset.recordings) - 1)
        return dataset.recordings[index]

    def _commit_pending_export(self) -> bool:
        if self._pending_export_folder is None:
            return False
        saved: list[str] = []
        failures: list[str] = []
        for artifact in self._pending_export_artifacts:
            try:
                path = self._writer.write(
                    self._pending_export_folder,
                    artifact,
                    replace=artifact.filename in self._approved_replacements,
                )
                if path is not None:
                    saved.append(str(path))
            except (OSError, ValueError) as exc:
                failures.append(f"{artifact.filename}: {exc}")
        self._pending_export_folder = None
        self._pending_export_artifacts = ()
        self._approved_replacements.clear()
        if failures:
            self._status_message = f"Saved {len(saved)} Profile(s); " + "; ".join(
                failures
            )
        else:
            self._status_message = f"Saved {len(saved)} Profile header(s)."
        self.stateChanged.emit()
        return not failures

    @staticmethod
    def _range_text(values: tuple[float, float]) -> str:
        return f"{values[0]:g}–{values[1]:g} mm/s"

    @staticmethod
    def _speed_tuple_text(values: tuple[float, ...]) -> str:
        if not values:
            return "None"
        return f"{values[0]:g}–{values[-1]:g} mm/s"

    @staticmethod
    def _discrete_speed_text(values: tuple[float, ...]) -> str:
        return (
            f"{', '.join(f'{value:g}' for value in values)} mm/s" if values else "None"
        )

    @classmethod
    def _speed_scope_text(
        cls,
        active_speeds: tuple[float, ...],
        supplied_speeds: tuple[float, ...],
    ) -> str:
        active = tuple(sorted(set(active_speeds)))
        active_set = set(active)
        excluded = tuple(
            speed for speed in sorted(set(supplied_speeds)) if speed not in active_set
        )
        return (
            f"Active {cls._discrete_speed_text(active)} · "
            f"Excluded {cls._discrete_speed_text(excluded)}"
        )

    @staticmethod
    def _recording_qualification_reason(row: RecordingQualification) -> str:
        if row.status == "PASS":
            return "All Collision intervals detected within 150 ms; no false collision events"
        if row.collision_interval_count <= 0:
            return "No Collision intervals"
        if row.status == "COVERAGE_GAP":
            return "Not ready: a Collision response window has no usable score (warmup/history/Ignore)"
        reasons: list[str] = []
        false_events = (
            ("Normal", row.normal_false_events),
            ("Pick", row.pick_false_events),
            ("Put", row.put_false_events),
        )
        if any(count > 0 for _, count in false_events):
            details = ", ".join(
                f"{name} {count}" for name, count in false_events if count > 0
            )
            reasons.append(f"False collision events: {details}")
        missed = row.collision_interval_count - row.collision_detected_count
        if missed > 0:
            reasons.append(f"Missed Collision intervals: {missed}")
        return "; ".join(reasons) or "Qualification requirements not met"

    @staticmethod
    def _offset_text(values: tuple[float, ...]) -> str:
        return ", ".join(f"{value:g} mm" for value in values) or "None"

    def _training_loss_text(self, kernel_id: str) -> str:
        evidence = self._kernel_training_evidence.get(kernel_id)
        return format(evidence.kernel_loss, ".8g") if evidence is not None else "N/A"

    def _stale_results(self, reason: str) -> None:
        self._learning_family_provenance = ()
        self._learning_run_provenance = None
        self._kernel_training_evidence = {}
        if self._profiles or self._retained_candidates:
            self._run_state = "Stale"
            self._header_preview = ""
            self._status_message = (
                f"{reason} Learning and Qualification results are stale."
            )
