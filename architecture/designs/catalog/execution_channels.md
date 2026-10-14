# CAT-execution_channels

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-execution_channels |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: execution_channels
value:
- id: history-worker-ipc
  profile: windows-desktop
  from_unit: analysis-worker
  to_unit: history-process-workers
  contract_refs:
  - learning.history-execution
  capacity: 4
  ordering: FIFO per History attempt; final merge uses declared History order
  copy_policy: Windows spawn pickle copy of immutable domain values
  timeout_ms: 100
  overload: reject
- id: worker-ui-progress
  profile: windows-desktop
  from_unit: analysis-worker
  to_unit: qt-ui-thread
  contract_refs:
  - learning.progressed
  - learning.completed
  - learning.cancelled
  capacity: 2
  ordering: FIFO per event type
  copy_policy: immutable snapshot copy
  timeout_ms: 0
  overload: coalesce
- id: replay-export-command
  profile: windows-desktop
  from_unit: qt-ui-thread
  to_unit: replay-export-worker
  contract_refs:
  - learning.replay-export
  - learning.replay-file-output
  capacity: 1
  ordering: One selected input snapshot per accepted export command
  copy_policy: Immutable selection inputs and NumPy arrays are shared read-only within
    the process; only bounded row text is copied to file buffers.
  timeout_ms: 0
  overload: reject
- id: model-export-command
  profile: windows-desktop
  from_unit: qt-ui-thread
  to_unit: replay-export-worker
  contract_refs:
  - learning.model-export
  - learning.model-file-output
  capacity: 1
  ordering: One selected candidate snapshot per accepted export command
  copy_policy: Immutable candidate parameters are shared read-only within the process;
    only bounded line text is copied to file buffers.
  timeout_ms: 0
  overload: reject
```
