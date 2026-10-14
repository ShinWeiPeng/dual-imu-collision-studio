# export-model-txt

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | export-model-txt |
| version | 1 |
| kind | flow |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: export-model-txt
  owner: studio_application
  description: Export one selected retained kernel as a deterministic standalone Model
    TXT artifact.
  trigger:
    kind: command
    ref: learning.model-export
    description: The user chooses a TXT destination after selecting a retained kernel
      in Replay.
  steps:
  - id: export-model-txt.step-1
    order: 1
    module: studio_application
    action: Resolve and snapshot the selected candidate, sample rate, numeric type,
      and destination, reject unavailable or concurrent work, and dispatch one background
      export.
    receives:
    - learning.model-export
    emits:
    - model.exported
    - model.export-failed
    state_changes: []
    side_effects:
    - Schedule one QRunnable on the Qt thread pool.
  - id: export-model-txt.step-2
    order: 2
    module: learning_qualification
    action: Stream deterministic scalar metadata and named FIR weights, bias, residual
      center, and residual scale sections without changing numeric values.
    receives:
    - learning.model-export
    emits: []
    state_changes: []
    side_effects: []
  - id: export-model-txt.step-3
    order: 3
    module: desktop_adapter
    action: Write UTF-8 LF-delimited lines to a same-folder temporary file, flush
      them, and atomically replace the selected destination.
    receives:
    - learning.model-file-output
    emits: []
    state_changes: []
    side_effects:
    - Atomically replace one user-selected TXT file.
  success:
    result: One complete Model TXT for the selected kernel is saved and the UI reports
      its path.
    events:
    - model.exported
  errors:
  - condition: Model evidence is unavailable or another artifact export is active.
    event: model.export-failed
    handling: Preserve the current session and show the rejection in the status bar.
  - condition: Rendering or atomic file output fails.
    event: model.export-failed
    handling: Preserve any previous destination and report the bounded failure message
      on the UI thread.
```
