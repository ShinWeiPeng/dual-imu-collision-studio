# CAT-ports

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-ports |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: ports
value:
- id: project.command
  owner: project_session
  direction: input
  kind: command
  contract: src/dual_imu_collision_studio/domain/project_session/service.py
  implemented_by: []
  description:
    purpose: Validate a complete semantic project document for save or transactional
      reopen.
    data: Versioned project identity, source references, mappings, annotations, templates,
      UI selection, and optional completed Profiles.
    timing: sync
    immediate_rejections:
    - code: invalid-project
      condition: The semantic project is incomplete, inconsistent, unsupported, or
        references a source without exact integrity evidence.
  symbols:
  - ProjectSessionService
- id: project.file-storage
  owner: project_session
  direction: output
  kind: dependency
  contract: src/dual_imu_collision_studio/domain/project_session/contracts.py
  implemented_by:
  - project_file_adapter
  description:
    purpose: Read or atomically replace one strict UTF-8 JSON .dicsproj artifact and
      compute source-file identity.
    data: ProjectDocument values and source path fingerprints; no waveform samples
      or framework handles.
    timing: sync
    immediate_rejections:
    - code: project-io-failed
      condition: Parsing, hashing, validation, or atomic replacement cannot complete
        safely.
  symbols:
  - ProjectFilePort
- id: workspace.command
  owner: data_workspace
  direction: input
  kind: command
  contract: src/dual_imu_collision_studio/domain/data_workspace/contracts.py
  implemented_by: []
  description:
    purpose: Import, configure, annotate, or validate workspace data.
    data: Semantic recording, mapping, condition, atomic reference activation, destination
      Anchor Cycle, cadence generation, and same-speed annotation projection commands.
    timing: sync
    immediate_rejections:
    - code: invalid-workspace-command
      condition: Command violates a workspace invariant.
  symbols:
  - WorkspaceCommandPort
- id: workspace.tabular-input
  owner: data_workspace
  direction: output
  kind: dependency
  contract: src/dual_imu_collision_studio/domain/data_workspace/contracts.py
  implemented_by:
  - tabular_adapter
  description:
    purpose: Read selected tabular data through a domain-owned contract.
    data: Column names, row values, and source metadata.
    timing: sync
    immediate_rejections:
    - code: unreadable-table
      condition: The selected file cannot be decoded safely.
  symbols:
  - TabularInputPort
- id: workspace.events
  owner: data_workspace
  direction: output
  kind: event
  contract: src/dual_imu_collision_studio/domain/data_workspace/contracts.py
  implemented_by: []
  description:
    purpose: Publish a committed workspace snapshot.
    data: Immutable semantic workspace snapshot.
    timing: sync
    immediate_rejections: []
  symbols:
  - WorkspaceEventPort
- id: learning.command
  owner: learning_qualification
  direction: input
  kind: command
  contract: src/dual_imu_collision_studio/domain/learning/contracts.py
  implemented_by: []
  description:
    purpose: Start or cancel one bounded learning and qualification run.
    data: Workspace snapshot, numeric type, captured Training mode, mode-specific
      candidate policy, grouped-CV settings, and memory limit.
    timing: async
    immediate_rejections:
    - code: learning-not-ready
      condition: Required setup or annotations are incomplete.
  symbols:
  - LearningCommandPort
- id: learning.events
  owner: learning_qualification
  direction: output
  kind: event
  contract: src/dual_imu_collision_studio/domain/learning/contracts.py
  implemented_by: []
  description:
    purpose: Publish learning progress and committed qualification results.
    data: Progress stage, candidate counts, typed parameter and kernel Loss evidence,
      speed coverage, per-recording Qualification results, qualified ranking, minimum-misjudgment
      diagnostic ranking, selected profile, and an immutable completed-candidate snapshot
      when cancellation terminates accepted work.
    timing: async
    immediate_rejections: []
  symbols:
  - LearningEventPort
- id: learning.history-execution
  owner: learning_qualification
  direction: output
  kind: dependency
  contract: src/dual_imu_collision_studio/domain/learning/contracts.py
  implemented_by:
  - history_worker_adapter
  description:
    purpose: Execute the four independent requested-History jobs for one fallback
      round without exposing process technology to Learning.
    data: Immutable History jobs, ordered results, bounded progress, typed failures,
      attempt durations, and process-tree Peak RSS evidence.
    timing: async
    immediate_rejections:
    - code: insufficient-hardware-memory
      condition: A child reports MemoryError or aggregate Peak RSS exceeds 85 percent
        of launch-time available RAM.
    - code: history-worker-failed
      condition: A startup or abnormal process failure still fails after its one permitted
        retry.
  symbols:
  - HistoryExecutionPort
- id: learning.replay-export
  owner: learning_qualification
  direction: input
  kind: command
  contract: src/dual_imu_collision_studio/domain/learning/service.py
  implemented_by: []
  description:
    purpose: Render one selected candidate and complete recording as the governed
      full-resolution diagnostic CSV schema.
    data: Immutable ReplayEvidence containing aligned raw, FIR, residual, detector
      score, threshold, ratio, state, and trigger values.
    timing: async
    immediate_rejections:
    - code: replay-evidence-unavailable
      condition: The selected retained kernel or recording cannot produce complete
        Replay evidence.
    - code: replay-export-busy
      condition: One Replay CSV or Model TXT artifact export is already active.
  symbols:
  - LearningService
- id: learning.replay-file-output
  owner: learning_qualification
  direction: output
  kind: dependency
  contract: src/dual_imu_collision_studio/domain/learning/contracts.py
  implemented_by:
  - desktop_adapter
  description:
    purpose: Atomically replace one user-selected Replay CSV destination without exposing
      filesystem technology to Learning.
    data: Destination path and a deterministic stream of UTF-8 CSV rows rendered from
      one immutable ReplayEvidence value.
    timing: sync
    immediate_rejections:
    - code: replay-write-failed
      condition: The destination or same-folder temporary file cannot be written,
        flushed, or atomically replaced.
  symbols:
  - ReplayCsvFilePort
- id: learning.model-export
  owner: learning_qualification
  direction: input
  kind: command
  contract: src/dual_imu_collision_studio/domain/learning/service.py
  implemented_by: []
  description:
    purpose: Render one selected retained candidate as the governed deterministic
      Model TXT schema.
    data: Candidate identifier, sample rate, numeric type, detector parameters, FIR
      weights, bias, residual center, and residual scale.
    timing: async
    immediate_rejections:
    - code: model-evidence-unavailable
      condition: The selected retained kernel or required model metadata is unavailable.
    - code: model-export-busy
      condition: One artifact export is already active.
  symbols:
  - LearningService
- id: learning.model-file-output
  owner: learning_qualification
  direction: output
  kind: dependency
  contract: src/dual_imu_collision_studio/domain/learning/contracts.py
  implemented_by:
  - desktop_adapter
  description:
    purpose: Atomically replace one user-selected Model TXT destination without exposing
      filesystem technology to Learning.
    data: Destination path and a deterministic stream of UTF-8 LF-delimited Model
      TXT lines.
    timing: sync
    immediate_rejections:
    - code: model-write-failed
      condition: The destination or same-folder temporary file cannot be written,
        flushed, or atomically replaced.
  symbols:
  - ModelTextFilePort
- id: profile.command
  owner: profile_export
  direction: input
  kind: command
  contract: src/dual_imu_collision_studio/domain/profile_export/contracts.py
  implemented_by: []
  description:
    purpose: Render and save an approved qualified profile.
    data: Qualified semantic profile, language target, namespace, and destination.
    timing: sync
    immediate_rejections:
    - code: profile-not-qualified
      condition: No accepted qualified profile was selected.
  symbols:
  - ProfileCommandPort
- id: profile.file-output
  owner: profile_export
  direction: output
  kind: dependency
  contract: src/dual_imu_collision_studio/domain/profile_export/contracts.py
  implemented_by:
  - desktop_adapter
  description:
    purpose: Save generated header text to a user-selected path.
    data: Destination path, UTF-8 header text, and overwrite choice.
    timing: sync
    immediate_rejections:
    - code: write-denied
      condition: Destination cannot be written or overwrite was not approved.
  symbols:
  - ProfileFilePort
- id: profile.events
  owner: profile_export
  direction: output
  kind: event
  contract: src/dual_imu_collision_studio/domain/profile_export/contracts.py
  implemented_by: []
  description:
    purpose: Publish successful profile export metadata.
    data: File path, language, numeric type, and qualified speed range.
    timing: sync
    immediate_rejections: []
  symbols:
  - ProfileEventPort
- id: diagnostics.output
  owner: process_diagnostics
  direction: output
  kind: dependency
  contract: src/dual_imu_collision_studio/domain/process_diagnostics/contracts.py
  implemented_by:
  - desktop_adapter
  description:
    purpose: Persist bounded process-lifecycle, Learning-stage, and Qt/QML diagnostic
      evidence.
    data: Immutable diagnostic status plus primitive stage, progress, Speed, Offset,
      failure, and runtime metadata without dataset payloads.
    timing: sync
    immediate_rejections:
    - code: diagnostics-unavailable
      condition: The per-user diagnostic location cannot be written; application operation
        continues without claiming persisted evidence.
  symbols:
  - DiagnosticsPort
- id: replay.events
  owner: studio_application
  direction: output
  kind: event
  contract: src/dual_imu_collision_studio/adapters/desktop/controller.py
  implemented_by: []
  description:
    purpose: Publish the terminal outcome of one accepted background Replay CSV or
      Model TXT export.
    data: Artifact kind plus saved destination path on success or a bounded failure
      message on failure.
    timing: async
    immediate_rejections: []
  symbols:
  - StudioController
- id: learning.execution
  owner: learning_qualification
  direction: output
  kind: query
  contract: src/dual_imu_collision_studio/domain/learning/contracts.py
  implemented_by:
  - history_worker_adapter
  description:
    purpose: Execute complete candidate-fold or recording jobs under one globally
      bounded queue.
    data: Immutable dataset and fold jobs or independent complete recording jobs;
      ordered results and resource evidence.
    timing: sync
    immediate_rejections:
    - code: invalid-batch
      condition: Duplicate job identities or unsupported worker capacity.
  symbols:
  - LearningExecutionPort
```
