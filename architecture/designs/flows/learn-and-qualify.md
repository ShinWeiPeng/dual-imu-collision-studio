# learn-and-qualify

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | learn-and-qualify |
| version | 1 |
| kind | flow |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: learn-and-qualify
  owner: learning_qualification
  description: Fit candidate kernels and qualify exact target replay across all supplied
    offsets and speeds using nested fallback rounds.
  trigger:
    kind: command
    ref: learning.command
    description: The user selects compatible algorithm/source pairs in Training; L0
      admits every selected recording before dispatching serial immutable requests
      on the existing analysis worker.
  steps:
  - id: learn-and-qualify.step-1
    order: 1
    module: learning_qualification
    action: Capture settings and run seed, preflight complete-Cycle counts, and allocate
      a fresh reproducible round fold map. Check common 128-ms evaluation and threshold
      evidence. In fixed-grid mode dispatch only the deduplicated checked History
      by alpha Cartesian product with Robust K zero and publish every evaluated disposition;
      in optimized mode dispatch the unchanged coarse and joint fine frontiers. Require
      all N results before shared aggregation and publish typed Loss evidence plus
      the rounded round-final Loss.
    receives:
    - learning.command
    - learning.history-execution
    emits:
    - learning.progressed
    state_changes: []
    side_effects: []
  - id: learn-and-qualify.step-2
    order: 2
    module: history_worker_adapter
    action: SPEC-0046 captures the user-selected one-to-eight fold workers, default
      one and capped by jobs, for reusable Windows spawn execution. Whole-recording
      Score and detector replay retain their four-worker cap. No Auto, estimated
      allocation admission, nested pools, retries, runtime resizing or worker-local
      model selection. FIR fitting and scoring use bounded feature blocks and
      float64 statistics; no full row-by-history matrix is retained for FIR. Return
      immutable job-identified results and measured Peak RSS evidence; measured
      system RAM above the existing ceiling, cancellation or unexpected failure
      terminates and cleans up the complete batch.
    receives:
    - learning.history-execution
    emits: []
    state_changes: []
    side_effects:
    - Spawn, monitor, join, or terminate child processes.
  - id: learn-and-qualify.step-3
    order: 3
    module: learning_qualification
    action: Aggregate equal-fold condition losses, retain every parameter within the
      configured relative tolerance of the minimum raw Parameter Loss, apply Validation
      allowance, and retain every fold whose raw maximum-condition Kernel Loss exactly
      equals that parameter's raw minimum while excluding rounded and second-place
      near ties. Publish the current parameter and fold plus completed, remaining,
      and derived total Qualification work. Qualify every admitted original kernel
      without refit before ranking, using the maximum Normal interval maximum as N,
      the minimum of the per-Collision window maxima as C for candidate generation,
      the strict Score-greater-than-Threshold predicate, mandatory all-Collision detection
      within the inclusive 150-ms minus-Ignore deadline, and neutral absence of Normal,
      Pick, or Put classes. Derive chronological per-Collision Detector Score SNR
      from each existing whole-recording Score trace without changing detector decisions.
      Commit every fully qualified selected kernel immediately with its ordered per-recording
      metrics and provenance. On normal completion publish the fallback result; on
      cancellation publish only the committed qualified candidates or, when none qualifies,
      the existing minimum-total-error diagnostic subset while keeping the terminal
      state Cancelled. See ALG-0007, ALG-0006, ALG-0005, ALG-0004 and ALG-0003.
    receives:
    - learning.history-execution
    emits:
    - learning.progressed
    - learning.completed
    - learning.cancelled
    state_changes: []
    side_effects: []
  success:
    result: Retained round winners expose covered offsets, valid speed ranges, minimum-misjudgment
      diagnostic status, and full-resolution selectable Replay evidence; only qualified
      winners remain exportable.
    events:
    - learning.completed
  errors:
  - condition: The user cancels accepted Learning work.
    event: learning.cancelled
    handling: Discard incomplete candidate work, freeze the last complete-candidate
      result, expose qualified candidates or the diagnostic fallback in Replay, and
      retain the Cancelled terminal state.
```
