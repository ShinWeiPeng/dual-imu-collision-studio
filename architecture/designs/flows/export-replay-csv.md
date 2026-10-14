# export-replay-csv

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | export-replay-csv |
| version | 1 |
| kind | flow |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: export-replay-csv
  owner: studio_application
  description: Export one selected kernel and recording as a full-resolution diagnostic
    CSV without rendering Replay waveform charts.
  trigger:
    kind: command
    ref: learning.replay-export
    description: The user chooses a CSV destination after selecting a retained kernel
      and recording in Replay.
  steps:
  - id: export-replay-csv.step-1
    order: 1
    module: studio_application
    action: Resolve and snapshot the selected complete recording, candidate, and destination,
      reject unavailable or concurrent work, and dispatch one background export.
    receives:
    - learning.replay-export
    emits:
    - replay.exported
    - replay.export-failed
    state_changes: []
    side_effects:
    - Schedule one QRunnable on the Qt thread pool.
  - id: export-replay-csv.step-2
    order: 2
    module: learning_qualification
    action: Stream the exact ordered diagnostic columns and every aligned sample without
      changing Replay numeric or detector semantics.
    receives:
    - learning.replay-export
    emits: []
    state_changes: []
    side_effects: []
  - id: export-replay-csv.step-3
    order: 3
    module: desktop_adapter
    action: Write UTF-8 CSV rows to a same-folder temporary file, flush them, and
      atomically replace the selected destination.
    receives:
    - learning.replay-file-output
    emits: []
    state_changes: []
    side_effects:
    - Atomically replace one user-selected CSV file.
  success:
    result: One complete CSV for the selected kernel and recording is saved and the
      UI reports its path.
    events:
    - replay.exported
  errors:
  - condition: Replay evidence is unavailable or another export is active.
    event: replay.export-failed
    handling: Preserve the current session and show the rejection in the status bar.
  - condition: Rendering or atomic file output fails.
    event: replay.export-failed
    handling: Preserve any previous destination and report the bounded failure message
      on the UI thread.
```
