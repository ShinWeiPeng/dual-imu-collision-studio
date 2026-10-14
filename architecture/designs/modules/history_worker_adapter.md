# history_worker_adapter

Supplement: [SPEC-0042 pre-code design](../SPEC-0042-pre-code-notes.md).

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | history_worker_adapter |
| version | 1 |
| kind | module |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: history_worker_adapter
  level: L3+
  role: adapter
  implementation_status: implemented
  paths:
  - src/dual_imu_collision_studio/adapters/parallel/history_workers.py
  - src/dual_imu_collision_studio/adapters/parallel/learning_workers.py
  parent: null
  depends_on:
  - learning_qualification
  implements_ports:
  - learning.history-execution
  - learning.execution
  description:
    purpose: Execute immutable candidate-fold or complete-recording jobs in bounded
      reusable Windows spawn workers. Legacy History execution remains available only
      for compatibility tests; Start Learning uses learning.execution.
    input_ports: []
    output_ports: []
    emitted_events: []
    owned_state: []
    side_effects:
    - description: Spawn, monitor, join, or terminate at most eight search workers
        or four Qualification workers and sample aggregate process-tree RSS.
    errors: []
    invariants:
    - Process handles, IPC objects, tracebacks, and multiprocessing framework types
      never cross into L1 contracts.
    - Successful results are returned in requested job order rather than process completion
      order.
    - Explicit MemoryError terminates all workers without retry.
    - SPEC-0046 production fold execution performs no estimated allocation calculation
      or estimated-budget admission. User-selected integer one through eight defaults
      to one and is capped by jobs; the count is fixed within the batch. No Auto mode,
      silent memory-based resizing, or retry remains in this path.
    - Active Learning execution retains the default 90 percent measured system-wide
      physical RAM ceiling. Runtime checks refresh total and available bytes and stop
      above the ceiling. Process-tree RSS remains diagnostic evidence; checks are
      sampled rather than a hard allocation cap. Legacy History execution retains
      its isolated compatibility policy.
    - New Learning worker startup failure or unexpected exit is terminal with zero
      retries; cancellation and memory failure clean up the whole batch. The isolated
      legacy History adapter retains its old contract.
    - SPEC-0046 removes the shared FIR/MLP preview estimate entry. Idle-only explicit
      fold worker configuration is session state. Whole-recording Qualification
      retains its four-worker cap and immutable ordered result contract.
  entrypoints:
  - path: src/dual_imu_collision_studio/adapters/parallel/history_workers.py
    symbol: SpawnHistoryExecutor
    kind: class
  public_symbols:
  - path: src/dual_imu_collision_studio/adapters/parallel/history_workers.py
    symbol: SpawnHistoryExecutor
    kind: class
  - path: src/dual_imu_collision_studio/adapters/parallel/learning_workers.py
    symbol: SpawnLearningExecutor
    kind: class
```

