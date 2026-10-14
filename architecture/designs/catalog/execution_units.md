# CAT-execution_units

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-execution_units |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: execution_units
value:
- id: qt-ui-thread
  profile: windows-desktop
  kind: event-loop
  priority: operating-system-default
  affinity: []
  concurrency: 1
  resources:
    memory: Viewport data and immutable presentation snapshots only.
  blocking: Bounded local UI and file-dialog operations only.
  allocation: Python and Qt runtime managed.
- id: analysis-worker
  profile: windows-desktop
  kind: worker-pool
  priority: operating-system-default
  affinity: []
  concurrency: 1
  resources:
    memory: Coordinator state and Qualification score cache; active Learning reserves
      10 percent of total physical RAM and stops when sampled system occupancy exceeds
      90 percent. Process-tree RSS is diagnostic only.
  blocking: Bounded local dataset reads and cooperative cancellation points.
  allocation: Python runtime managed with chunk-bounded temporary arrays.
- id: history-process-workers
  profile: windows-desktop
  kind: worker-pool
  priority: operating-system-default
  affinity: []
  concurrency: 4
  resources:
    memory: Four Windows spawn processes, each owning one dataset copy and one requested-History/fold
      FIR matrix cache; aggregate parent-plus-child Peak RSS is capped at 85 percent
      of launch-time available RAM.
  blocking: CPU-bound NumPy/Python Training with cooperative cancellation and bounded
    IPC polling.
  allocation: Python and NumPy runtime managed; worker-local FIR caches are released
    at process exit.
- id: replay-export-worker
  profile: windows-desktop
  kind: worker-pool
  priority: operating-system-default
  affinity: []
  concurrency: 1
  resources:
    memory: One worker-computed immutable ReplayEvidence or one bounded Model TXT
      line stream plus bounded formatting buffers; no full duplicate artifact string.
  blocking: CPU-bound artifact rendering followed by sequential same-folder temporary-file
    write, flush, and atomic replacement.
  allocation: Python and Qt thread-pool runtime managed.
- id: fold-process-workers
  profile: windows-desktop
  kind: worker-pool
  priority: operating-system-default
  affinity: []
  concurrency: 8
  resources:
    memory: At most eight dataset copies and job-local training arrays. FIR selects
      one to eight workers before spawn to fit the current budget; the batch count
      is then fixed. MLP retains its fixed cap. FIR and MLP estimated additional batch
      bytes must fit current available RAM minus 10 percent of total RAM. Active fold
      execution stops above sampled 90 percent system occupancy. SPEC-0043 Manual
      FIR/MLP count is one to eight capped by jobs; it is rejected if unaffordable,
      never silently reduced. Preview reports estimates only; each real batch refreshes
      memory.
  blocking: CPU-bound fold fitting with bounded IPC polling and terminal cancellation.
  allocation: Python/NumPy managed; no shared mutable model arrays.
- id: qualification-process-workers
  profile: windows-desktop
  kind: worker-pool
  priority: operating-system-default
  affinity: []
  concurrency: 4
  resources:
    memory: At most four complete recording jobs; scores reused per frozen model.
      Active execution stops above sampled 90 percent system occupancy.
  blocking: CPU-bound complete recording replay with bounded IPC polling.
  allocation: Worker-local arrays released after the batch.
```
