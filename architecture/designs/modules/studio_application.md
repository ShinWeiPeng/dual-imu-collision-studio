# studio_application

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | studio_application |
| version | 1 |
| kind | module |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: studio_application
  level: L0
  role: composition
  implementation_status: implemented
  paths:
  - src/dual_imu_collision_studio/app.py
  - src/dual_imu_collision_studio/adapters/desktop/controller.py
  parent: null
  depends_on:
  - data_workspace
  - process_diagnostics
  - learning_qualification
  - project_session
  - profile_export
  - desktop_adapter
  - history_worker_adapter
  - project_file_adapter
  - tabular_adapter
  implements_ports: []
  description:
    purpose: Compose the desktop workflow, own annotation edit history, map immutable
      results between sibling domains, coordinate durable project reopen/save, and
      dispatch recording-only Replay evidence and model artifacts to bounded background
      exports.
    input_ports: []
    output_ports:
    - replay.events
    emitted_events:
    - replay.exported
    - replay.export-failed
    - model.exported
    - model.export-failed
    owned_state: []
    side_effects:
    - description: Start the Qt application and coordinate bounded background work.
    - description: Publish bounded process-lifecycle and Learning diagnostics through
        the application-owned diagnostics port.
    errors: []
    invariants:
    - Sibling domains communicate only through application-owned mappings.
    - Exactly one release composition root exists.
    - The QML engine retains the StudioController for the complete main-window lifetime.
    - QML coordinates are converted to sample indexes before domain validation.
    - Provisional annotation edits never enter Learning until the complete set is
      confirmed.
    - The application owns the session-local speed-to-template registry while data_workspace
      owns template semantics and projection.
    - The application restores its session-local manual annotation identity allocator
      above every persisted manual annotation identity before accepting post-open
      edits.
    - Successful reference activation clears both the primary selected annotation
      index and the selected-annotation set before publishing the refreshed UI state.
    - The application maps sibling-owned workspace and Profile values into project_session-owned
      persistence values without exposing JSON representations to functional domains.
    - Replay CSV export snapshots one selected recording and candidate, computes the
      complete continuous recording exactly once, and streams Learning-owned ReplayEvidence
      off the UI thread without display normalization.
    - Model TXT export snapshots one candidate and renders every governed model parameter
      exactly once off the UI thread.
    - The Candidate Dashboard execution log is session-only, capped at 10,000 accepted-run
      entries, never enters the project document or exported artifacts, and clears
      only on an accepted new Learning run, a direct session reset, or successful
      Open project replacement. Pointer presence anywhere inside the Execution Log
      pane pauses automatic following; pointer exit immediately positions the viewport
      at the newest entry, and log or layout updates keep the newest entry visible
      while the pointer is outside.
    - SPEC-0045 Open restores frozen models, existing condition aggregates and saved
      per-recording/collision details after source fingerprint and schema validation;
      it never invokes Training, Qualification or full score replay. Missing historical
      details display Not stored / N/A; stale bindings retain readable historical
      results but cannot grant current export qualification.
    - A cancelled Learning run commits one immutable partial result on the UI thread,
      remains visibly Cancelled, and exposes only fully qualified candidates or, when
      none qualifies, the existing minimum-total-error diagnostic subset in Candidate
      Dashboard and Analytical Replay.
    - Recording Qualification Results maps Learning-owned chronological per-Collision
      Detector Score SNR evidence into one display-only dB string without recomputation,
      status changes, persistence, or export.
    - Selected-kernel presentation exposes the Learning-owned stored Kernel Loss as
      Training loss without recomputation, uses N/A when historical evidence is unavailable,
      and shares one packaged DI icon between the in-app header and application-level
      window identity; Windows startup assigns the stable explicit DualIMU.CollisionStudio
      AppUserModelID before QGuiApplication construction so pythonw.exe launches retain
      the DI taskbar identity.
    - Completing Mapping Wizard preserves the Recordings ListView pixel viewport across
      the controller snapshot refresh and clamps it only when refreshed content makes
      the prior position invalid.
    - The parent maps frozen MLP layers to inert project data; model-family settings
      and results survive reopen without model retraining.
    - Mapping inventories per-IMU raw or filtered XYZ independently of algorithm selection.
      Training captures per-algorithm sources, rejects the complete requested batch
      on any incompatible recording, runs compatible methods serially in the existing
      analysis worker, and retains frozen result/source identity for replay and project
      reopen (SPEC-0033).
    - SPEC-0044 Training installs current-policy qualification evidence bound to frozen
      model, source, threshold and coverage. Project persistence preserves this identity;
      legacy or stale evidence requires frozen-model Qualification from Replay. JSON
      export performs background snapshot validation, rendering and atomic writes;
      busy state rejects duplicate export and project replacement until completion.
    - SPEC-0046 worker count is explicit one through eight, default one, application
      session state only and excluded from project/model persistence. Training locks
      this count. Auto, memory-preview worker/state and estimate busy dependencies
      are removed. Failure summaries retain bounded expandable/copyable details.
      See architecture/designs/SPEC-0046-pre-code-notes.md for ownership and flow.
    - Application-owned mapping serializes optional qualification_results from Learning
      values and reconstructs immutable Learning values only after ProjectSessionService
      validates structure. Existing qualification_evidence remains the sole current
      export admission proof, with its original policy and frozen-input checks.
  entrypoints:
  - path: src/dual_imu_collision_studio/app.py
    symbol: main
    kind: function
  public_symbols:
  - path: src/dual_imu_collision_studio/app.py
    symbol: main
    kind: function
  - path: src/dual_imu_collision_studio/adapters/desktop/controller.py
    symbol: StudioController
    kind: class
```
