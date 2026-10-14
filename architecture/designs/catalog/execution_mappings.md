# CAT-execution_mappings

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-execution_mappings |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: execution_mappings
value:
- id: project-ui-map
  profile: windows-desktop
  workload: project-io
  steps:
  - manage-project.step-1
  units:
  - qt-ui-thread
  serialization: One modal user-approved save/open transaction; active session commit
    occurs only after complete validation.
  reentrant: false
  activation: project command
  wcet: Not established; source hashing is bounded by the declared session source
    files.
- id: diagnostics-ui-map
  profile: windows-desktop
  workload: process-diagnostics
  steps:
  - record-process-diagnostics.step-1
  units:
  - qt-ui-thread
  serialization: The diagnostics adapter serializes writes from the UI and any Qt
    callback thread; no mutable diagnostic state escapes.
  reentrant: false
  activation: process lifecycle or diagnostic observation
  wcet: Not established; records are bounded and rotated.
- id: workspace-ui-map
  profile: windows-desktop
  workload: interactive-workspace
  steps:
  - prepare-workspace.step-1
  - prepare-workspace.step-2
  units:
  - qt-ui-thread
  serialization: Qt event loop serializes committed UI state changes.
  reentrant: false
  activation: user command
  wcet: Not established; p95 is measured by application benchmarks.
- id: analysis-worker-map
  profile: windows-desktop
  workload: analysis-run
  steps:
  - learn-and-qualify.step-1
  units:
  - analysis-worker
  - fold-process-workers
  - qualification-process-workers
  serialization: One active run with one bounded job queue; full-N parameter barriers
    and all fine paths complete before selection. Progress reaches Qt by queued signal.
    Search and Qualification worker batches never overlap.
  reentrant: false
  activation: Start Learning command
  wcet: Not established; bounded parameter domain but data-dependent convergence and
    ties. No wall-clock timeout; cancellation is cooperative at coordinator/job boundaries.
- id: profile-ui-map
  profile: windows-desktop
  workload: profile-write
  steps:
  - export-profile.step-1
  units:
  - qt-ui-thread
  serialization: One user-approved save operation.
  reentrant: false
  activation: export command
  wcet: Not established for local filesystem output.
- id: replay-csv-map
  profile: windows-desktop
  workload: replay-csv-write
  steps:
  - export-replay-csv.step-1
  - export-replay-csv.step-2
  - export-replay-csv.step-3
  units:
  - qt-ui-thread
  - replay-export-worker
  serialization: The UI snapshots one selected complete recording, candidate, and
    destination, permits one active artifact export, and receives one queued terminal
    completion or failure signal.
  reentrant: false
  activation: Replay CSV export command
  wcet: Data-dependent and bounded by the selected recording row count and local filesystem
    behavior.
- id: model-txt-map
  profile: windows-desktop
  workload: model-txt-write
  steps:
  - export-model-txt.step-1
  - export-model-txt.step-2
  - export-model-txt.step-3
  units:
  - qt-ui-thread
  - replay-export-worker
  serialization: The UI snapshots one selected candidate, sample rate, numeric type,
    and destination, shares the one-active-artifact exclusion with Replay CSV, and
    receives one queued terminal completion or failure signal.
  reentrant: false
  activation: Model TXT export command
  wcet: Data-dependent and bounded by tap_count and local filesystem behavior.
```
