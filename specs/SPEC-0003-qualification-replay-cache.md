---
spec_version: 1
spec_id: SPEC-0003
revision: 11
status: confirmed
change_set: qualification-replay-cache
---

# Qualification Replay Score Cache

## Problem

For each fixed fitted FIR model, Qualification currently recomputes normalized residuals and detector scores for every Threshold and Confirmation Mode even though those arrays do not depend on either parameter. The repeated work makes one fallback round appear to repeat the same Speed and Offset conditions many times and increases runtime. The current 0.25 Threshold increment also evaluates more candidates than the newly selected 0.5 increment requires.

Measured Training on the supplied eight-recording dataset remained CPU-bound for more than one hour while using approximately one of the host's sixteen logical processors. The four independent History candidates are evaluated sequentially, leaving available CPU capacity unused.

## Solution

Change the Threshold grid to the inclusive sequence `2.0, 2.5, ..., 12.0`. Separate model-dependent residual/score calculation from configuration-dependent detector state replay. For each fixed History/model, compute and retain every recording's exact score array once, reuse it across all Threshold and Confirmation Mode candidates in the existing stable candidate order for the new grid, and release the complete per-History cache on completion, cancellation, or failure. Preserve Qualification arithmetic, evidence, ranking, fallback, cancellation, and output behavior relative to an uncached reference using the same 0.5 Threshold grid. Accept the optimization only when a same-host Qualification-only benchmark against that same-grid reference demonstrates at least a 30 percent median runtime reduction within the bounded score-cache memory formula and without reducing the existing accepted dataset envelope.

For Training, execute the four fixed History candidates in exactly four Windows spawned workers, cache reusable raw FIR fold matrices within each worker, merge results in deterministic History order, and apply the confirmed typed retry and terminal-memory policies. On the supplied eight-recording dataset and target host, require each completed non-retry fallback round to finish within 30 minutes and require aggregate parent-plus-worker Peak RSS to remain within 85 percent of available RAM measured immediately before worker launch.

## User Stories

- As a user, I can complete Training and Qualification with a 0.5 Threshold search increment and without repeatedly paying for identical residual and score calculations.
- As an analyst, I receive deterministic qualified candidates, condition evidence, winner ranking, and exported Profile values produced from the declared 0.5 Threshold grid.
- As a maintainer, I can validate cached and uncached same-grid Qualification paths against deterministic equivalence tests and representative performance evidence.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | For a fixed fallback round, History/model, recording, target numeric type, and Score Mode, Qualification shall compute normalized residuals and detector scores no more than once, retain the score arrays in one private per-History in-memory cache, and reuse them for all Threshold and Confirmation Mode candidates in the existing candidate order. |
| REQ-002 | Against an uncached reference that uses the same 0.5 Threshold grid, the optimization shall preserve candidate IDs and order, trigger indices and times, condition status and denominators, passing/detectable speeds, latency and robustness margins, winner ranking, retained rounds, fallback transitions, cancellation semantics, and exported Profile values exactly for both float32 and float64. Compatibility with winners selected only by the former 0.25 grid is not required. |
| REQ-003 | Cached numerical data shall be private to the active History/model computation, shall not enter project persistence or public domain contracts, and shall be released when that History/model or run is abandoned, completed, cancelled, or failed. The cache shall retain score arrays only; source time arrays and immutable recording metadata remain referenced rather than duplicated. |
| REQ-004 | On the same Windows host and software environment, the optimized Qualification-only path shall reduce median elapsed time by at least 30 percent versus an uncached reference using the same 0.5 Threshold grid over one warm-up and at least five measured runs of the same representative dataset and candidate plan. Peak RSS increase shall not exceed total supplied sample count multiplied by target numeric-type bytes plus 10 MiB, and the change shall not cause a dataset accepted by the existing 60-percent available-RAM preflight to be rejected. |
| REQ-005 | Qualification Thresholds shall be the deterministic inclusive sequence from 2.0 through 12.0 in increments of 0.5, yielding exactly 21 Thresholds and 63 Threshold/Confirmation candidates per successfully fitted History before other plan dimensions. |
| REQ-006 | Training shall request exactly four Windows spawned worker processes and assign one of the four fixed History candidates to each worker. It shall not adapt the requested worker count to detected RAM or CPU capacity. Result collection shall restore the existing History order before ranking, fallback, Qualification, persistence, or export observes the candidates. |
| REQ-007 | Within each History worker and fallback round, Training shall build each fold's reusable raw FIR feature matrix, target matrix, segment and row-index evidence no more than once, reuse the cached arrays across all model-rule combinations whose inputs are identical, and release all such arrays when the History job completes, fails, or is cancelled. Cached and uncached sequential references shall produce exactly equivalent selected rules and fitted models for float32 and float64. |
| REQ-008 | `MemoryError` from any History worker shall be terminal and shall not be retried; the parent shall immediately cancel all other running History workers, discard incomplete run results, mark the entire Training run failed, and the UI shall report that available hardware memory is insufficient to execute Training. Worker startup failure and unexpected worker-process termination shall each be eligible for at most one immediate fresh-worker retry without waiting for other workers; multiple eligible failures shall be retried concurrently. Data validation errors, numerical or product-code exceptions, and user cancellation shall not be retried. Healthy running workers and successful results shall remain valid for non-memory worker retries. If an eligible retry fails again, the Training run shall fail with the affected History and both attempt outcomes recorded. |
| REQ-009 | On the target Windows host using the supplied eight-recording dataset, confirmed annotations and mappings, and the same numeric type and candidate plan as the recorded sequential baseline, every completed non-retry fallback round shall take no more than 30 minutes wall-clock time. Aggregate process-tree Peak RSS across the parent and all workers shall not exceed 85 percent of available RAM sampled immediately before worker launch. The UI and diagnostics shall expose per-round, cumulative Training, cumulative Qualification, total-run, and per-History worker attempt durations. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Separate model-dependent score production from Threshold/Confirmation-dependent detector replay and reuse the scores. | The user selected this approach after confirming that process forking is neither required nor intended. |
| DEC-002 | Use one private full-recording score cache per fixed History/model and preserve the existing candidate-major evaluation order; release the cache at the History/model lifecycle boundary. | The user selected option 1. This minimizes control-flow and cancellation-order changes while bounding additional storage to one score value per supplied sample for the active model. |
| DEC-003 | Require at least 30 percent lower median Qualification-only elapsed time, exact result equivalence, bounded Peak RSS, and no regression of the existing memory-preflight acceptance envelope. | The user selected the balanced quantitative threshold so the optimization must produce an observable benefit without imposing an uncalibrated aggressive target. |
| DEC-004 | Change the Threshold increment from 0.25 to 0.5 while retaining inclusive endpoints 2.0 and 12.0. | The user explicitly selected the coarser Threshold grid to reduce candidate count. |
| DEC-005 | Apply DEC-003's 30 percent runtime, bounded-memory, and no-admission-regression thresholds against an uncached reference using the same 0.5 Threshold grid; exact equivalence to the former 0.25 grid is not required. | DEC-004 changes the candidate grid, so a same-grid baseline isolates the score-cache improvement while preserving the selected quantitative threshold. |
| DEC-006 | Add a fixed four-process Windows spawn pool for Training, with one History candidate assigned to each process and deterministic parent-side result ordering. | The user selected option 2 after stating that the target host has 32 GiB RAM. No additional rationale was stated. |
| DEC-007 | Cache the complete reusable raw FIR matrices and associated evidence once per fold inside each History worker, and release the cache at the History-job boundary. | The user selected option 1 to remove repeated FIR matrix construction across model-rule combinations. No additional rationale was stated. |
| DEC-008 | Preserve running and completed healthy History workers after another worker fails, wait for all first attempts to finish, then automatically retry each failed History once in a fresh worker before deciding the run outcome. | The user explicitly requested retaining continuing workers and delaying one automatic retry until the other workers have finished. |
| DEC-009 | Apply delayed one-time retry only to `MemoryError`, worker startup failure, and unexpected worker-process termination; do not retry data validation errors, numerical or product-code exceptions, or user cancellation. | The user selected option 2 so only failures that may change after memory is released or a fresh process is created consume a retry. |
| DEC-010 | Treat `MemoryError` as terminal hardware-insufficiency without retry; immediately and concurrently restart workers that fail to start or terminate unexpectedly, with at most one retry per History. | The user explicitly distinguished memory exhaustion from other worker-process failures and requested immediate concurrent worker restart for the latter. |
| DEC-011 | On terminal `MemoryError`, immediately cancel every other running History worker and fail the entire Training run rather than waiting for remaining work. | The user selected option 1 because a complete fixed-four-worker result cannot be produced after the declared hardware-insufficiency outcome. |
| DEC-012 | Accept the Training optimization only when each supplied-dataset fallback round completes within 30 minutes and aggregate process-tree Peak RSS remains within 85 percent of available RAM at worker launch. | The user selected option 1 for the runtime threshold and explicitly changed the proposed RAM threshold from 60 percent to 85 percent. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | Instrumented tests show one residual/score computation per fixed model and recording while all 21 Thresholds across all three Confirmation Modes are still evaluated in stable order. | Focused unit and learning-run call-count tests. | Pending |
| AC-002 | REQ-002 | Cached and uncached same-grid reference executions produce identical detector traces, Qualification results, retained winners, fallback states, and exported Profile artifacts for float32 and float64 across nominal, threshold-boundary, reset, confirmation, latch/rearm, coverage-gap, cancellation, and failure fixtures. | Differential and regression tests. | Pending |
| AC-003 | REQ-003 | No cache value crosses the learning_qualification module boundary or enters project files; cache storage is one score value per supplied sample for the active model, does not duplicate source time arrays, and is released on normal completion, cancellation, and error. | Static ownership inspection, architecture gate, storage-bound assertion, and lifecycle tests. | Pending |
| AC-004 | REQ-004 | After one warm-up and at least five same-host measured runs, optimized median Qualification-only elapsed time is no more than 70 percent of the uncached same-grid median; Peak RSS delta is no greater than `sample_count * dtype.itemsize + 10 MiB`; representative and boundary-shaped datasets preserve the existing preflight admission result; and AC-002 remains PASS. | Reproducible benchmark command recording host, dataset shape, candidate count, numeric type, Python/Numpy versions, elapsed samples, medians, ratio, Peak RSS, cache bound, and admission decisions. | Pending |
| AC-005 | REQ-005 | The candidate plan exposes exactly `(2.0, 2.5, ..., 12.0)`, contains 21 Thresholds, creates exactly 63 Threshold/Confirmation candidates per successfully fitted History, includes both endpoints once, and contains no former quarter-step-only value. | Exact sequence, cardinality, candidate-order, and boundary tests. | Pending |
| AC-006 | REQ-006 | Instrumented Windows tests observe four spawned History jobs, one for each fixed History, and show that shuffled worker completion produces exactly the same ordered models, candidates, winners, fallback transitions, Qualification evidence, and exported Profile bytes as the sequential reference. | Spawn-worker integration tests plus deterministic sequential-versus-parallel differential tests. | Pending |
| AC-007 | REQ-007 | Instrumented tests show one raw FIR matrix/evidence construction per History/fold/input selection, cache release on completion, cancellation, and failure, and exact selected-rule, model-array, candidate, winner, and exported-Profile equivalence to an uncached sequential reference for float32 and float64. | Construction call-count, lifecycle, differential, and regression tests. | Pending |
| AC-008 | REQ-008 | Typed failure-injection tests prove that `MemoryError` performs zero retries, cancels every other running worker, discards incomplete run results, marks Training failed, and exposes the hardware-insufficiency message; startup failure and unexpected termination submit one immediate fresh-worker retry without waiting for healthy workers; multiple eligible failures retry concurrently; validation errors, numerical or product-code exceptions, and cancellation never retry; no History retries more than once; and a second eligible failure reports the History plus both attempt outcomes. | Deterministic typed worker-failure integration tests with monotonic event capture, process-liveness assertions, concurrency barriers, UI-state assertions, and call counts. | Pending |
| AC-009 | REQ-009 | A same-host acceptance run records the supplied dataset identity, mappings, annotations, numeric type, candidate plan, available RAM before launch, parent and child PIDs, monotonic per-stage/per-round/per-attempt timestamps, and process-tree Peak RSS. Every completed non-retry fallback round is at most 30 minutes, Peak RSS is at most 85 percent of launch-time available RAM, and the UI durations reconcile with the diagnostics timeline. A bounded representative benchmark includes one warm-up and at least five measured runs to separate implementation regression from one full-dataset observation. | Reproducible Windows benchmark plus OS process-tree sampling, diagnostics reconciliation, and saved JSON/Markdown evidence. | Pending |

## Relationships

| Source | Relation | Target |
|---|---|---|
| DEC-001 | refines | REQ-001 |
| DEC-002 | refines | REQ-001 |
| DEC-002 | refines | REQ-003 |
| DEC-003 | refines | REQ-004 |
| DEC-004 | refines | REQ-005 |
| DEC-005 | supersedes | DEC-003 |
| DEC-005 | refines | REQ-004 |
| REQ-002 | depends_on | REQ-001 |
| REQ-002 | depends_on | REQ-005 |
| REQ-003 | depends_on | REQ-001 |
| REQ-004 | depends_on | REQ-001 |
| REQ-004 | depends_on | REQ-005 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |
| AC-003 | depends_on | REQ-003 |
| AC-004 | depends_on | REQ-004 |
| AC-005 | depends_on | REQ-005 |
| DEC-006 | refines | REQ-006 |
| REQ-006 | depends_on | REQ-002 |
| AC-006 | depends_on | REQ-006 |
| DEC-007 | refines | REQ-007 |
| REQ-007 | depends_on | REQ-002 |
| AC-007 | depends_on | REQ-007 |
| DEC-008 | refines | REQ-008 |
| REQ-008 | depends_on | REQ-006 |
| AC-008 | depends_on | REQ-008 |
| DEC-009 | refines | REQ-008 |
| DEC-010 | supersedes | DEC-008 |
| DEC-010 | supersedes | DEC-009 |
| DEC-010 | refines | REQ-008 |
| DEC-011 | refines | REQ-008 |
| DEC-012 | refines | REQ-009 |
| REQ-009 | depends_on | REQ-006 |
| REQ-009 | depends_on | REQ-007 |
| AC-009 | depends_on | REQ-009 |

## Discussion Context

### DISC-001: Optimization method
- **Situation:** Qualification recomputes fixed-model residuals and scores for each Threshold and Confirmation Mode candidate.
- **Question:** Shall Qualification use score caching and separated detector replay, process forking, or retain the current computation?
- **Options and tradeoffs:** Score caching preserves single-worker determinism and removes repeated numerical work but requires explicit memory/lifetime ownership; process forking adds IPC, memory, and determinism costs; retaining the current path avoids refactoring but preserves the repeated work.
- **User answer:** Use score caching and separated replay computation.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-001 defines REQ-001 through REQ-004 and excludes process forking.

### DISC-002: Cache scope and evaluation order
- **Situation:** Full-History caching preserves candidate-major control flow but adds one score value per supplied sample; recording-major streaming minimizes peak memory but changes evaluation and cancellation order and requires multi-candidate accumulation.
- **Question:** Shall the implementation cache all recordings for the active History/model or use recording-major streaming reuse?
- **Options and tradeoffs:** Full-History caching is the smallest behavioral change and preserves stable candidate order at the cost of bounded extra memory; recording-major streaming uses less memory but materially restructures Qualification and increases equivalence risk.
- **User answer:** Option 1: cache all recordings for the active History/model.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-002 refines REQ-001 and REQ-003; OD-001 is resolved.

### DISC-003: Runtime and memory acceptance threshold
- **Situation:** Removing duplicate score calculation must produce a measurable user benefit without consuming unbounded memory or shrinking the existing admitted dataset envelope.
- **Question:** Shall success require a balanced 30 percent median Qualification-only reduction, an aggressive 50 percent reduction, or only proof that duplicate calculation was removed?
- **Options and tradeoffs:** The balanced threshold proves observable improvement with moderate evidence risk; the aggressive threshold may require broader optimization; call-count-only evidence proves mechanism but not user-visible speed. All measured options retain exact-output and bounded-memory requirements.
- **User answer:** Option 1: balanced 30 percent median runtime reduction with bounded memory.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-003 defines the quantitative REQ-004 and AC-004; OD-002 is resolved.

### DISC-004: Threshold increment
- **Situation:** The confirmed spec preserved the former 0.25 Threshold grid, but the user requested a coarser search to reduce Qualification candidates further.
- **Question:** What deterministic Threshold increment shall Qualification use between the existing inclusive endpoints 2.0 and 12.0?
- **Options and tradeoffs:** A 0.25 increment retains finer candidate coverage at higher cost; a 0.5 increment halves the interior grid work but may select a different Threshold and winner; adaptive refinement would add new branching and calibration behavior.
- **User answer:** Use a 0.5 increment.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-004 and REQ-005 define the new 21-value grid; DEC-005 supersedes DEC-003 for baseline interpretation; REQ-002 and AC-002 now require exact equivalence only against an uncached reference using the same grid.

### DISC-005: Training worker-count policy
- **Situation:** The supplied eight-recording Training run used approximately one of sixteen logical processors for more than one hour, while the target host has 32 GiB RAM and the four History candidates are independent before deterministic result merging.
- **Question:** Shall Training use an adaptive one-to-four worker policy, a fixed four-worker policy, or remain single-process?
- **Options and tradeoffs:** Adaptive workers preserve portability but add resource policy; fixed four workers use the target host consistently but may be unsuitable on lower-memory machines; single-process execution minimizes multiprocessing risk but leaves CPU capacity unused.
- **User answer:** Option 2: fixed four workers.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-006, REQ-006, and AC-006 add fixed Windows spawn parallelism and reopen the former multiprocessing exclusion.

### DISC-006: Training FIR cache scope
- **Situation:** Each History evaluates the same fold data across approximately 120 model-rule combinations, while the current path repeatedly rebuilds raw FIR features, targets, and row-index evidence whose inputs have not changed.
- **Question:** Shall each worker cache complete reusable raw FIR matrices, cache only Cycle evidence and indexes, or rely on parallel workers without a Training cache?
- **Options and tradeoffs:** Complete raw-matrix caching removes the most repeated preparation work but raises per-worker Peak RSS; evidence-only caching saves less memory and less time; no cache is simplest but retains repeated work inside every worker.
- **User answer:** Option 1: cache the complete reusable raw FIR matrices.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-007, REQ-007, and AC-007 require a private per-History/fold Training cache with exact sequential-reference equivalence and bounded lifetime.

### DISC-007: Worker failure and delayed retry
- **Situation:** Cancelling all workers immediately after one History fails would discard lengthy healthy computations; retrying immediately could compete with still-running workers and raise Peak RSS.
- **Question:** How shall Training react when one fixed History worker fails while other workers are still running?
- **Options and tradeoffs:** Immediate failure is simplest but discards healthy work; delayed one-time retry preserves healthy results and avoids overlap with the first wave but extends failure completion time; main-process fallback changes the selected fixed-worker execution policy and may take hours.
- **User answer:** Preserve the continuing workers, wait until the other workers finish, and then automatically retry the failed worker once.
- **Explicit rationale:** Preserve work already in progress before retrying.
- **Resulting impact:** DEC-008, REQ-008, and AC-008 define delayed one-time fresh-worker retry without recomputing successful Histories.

### DISC-008: Retry-eligible failure classes
- **Situation:** A worker failure does not necessarily indicate insufficient RAM. Resource pressure or process loss may succeed after other workers release memory, but deterministic data, numerical, or product-code errors will usually repeat unchanged.
- **Question:** Shall every worker failure receive the delayed retry, or only resource and worker-process failures?
- **Options and tradeoffs:** Retrying every failure has a simpler rule but can repeat an hour-long deterministic failure; typed retry limits recovery to failures that can plausibly change after memory release or fresh process creation and requires explicit exception classification.
- **User answer:** Option 2: retry only memory or worker-process failures.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-009 refines REQ-008 and AC-008 with explicit retry-eligible and non-retryable failure classes.

### DISC-009: Memory exhaustion and immediate worker restart
- **Situation:** Waiting for all workers before retrying can reduce memory pressure, but a true `MemoryError` indicates that the fixed four-worker execution exceeded available memory, while startup loss or unexpected process termination may be transient and unrelated to RAM.
- **Question:** Shall `MemoryError` wait and retry with fewer concurrent jobs, or fail as insufficient hardware; and when shall non-memory worker-process failures retry?
- **Options and tradeoffs:** Memory retry could finish with lower concurrency but contradicts the fixed four-worker policy; terminal memory failure is explicit and avoids repeating an unsupported run. Delayed process restart reduces overlap, while immediate concurrent restart minimizes elapsed time but temporarily keeps the fixed worker load active.
- **User answer:** If it is `MemoryError`, show that hardware performance is insufficient and cannot execute; otherwise immediately restart workers concurrently.
- **Explicit rationale:** Memory exhaustion indicates insufficient hardware; other worker failures can restart immediately.
- **Resulting impact:** DEC-010 supersedes DEC-008 and DEC-009, rewrites REQ-008 and AC-008, resolves concurrent retry scheduling, and leaves terminal MemoryError cancellation behavior open.

### DISC-010: Terminal MemoryError cancellation
- **Situation:** After one worker reports terminal `MemoryError`, the fixed-four-worker run cannot produce a complete accepted result, while letting other workers continue consumes additional time and memory without changing the final failure.
- **Question:** Shall terminal `MemoryError` immediately cancel all other workers or let them finish before reporting failure?
- **Options and tradeoffs:** Immediate cancellation frees memory and returns a clear terminal result quickly but discards partial diagnostic computation; waiting preserves more intermediate progress but cannot produce a valid complete run and prolongs pressure.
- **User answer:** Option 1: immediately stop the other workers and fail the whole Training run.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-011 refines REQ-008 and AC-008 and resolves terminal memory-failure shutdown behavior.

### DISC-011: End-to-end Training performance envelope
- **Situation:** The observed first fallback round on the supplied eight-recording dataset ran from 08:40:37 to 10:13:08, approximately 92 minutes 31 seconds, and the run then entered another fallback round. A relative-only improvement could still leave each round longer than one hour.
- **Question:** Shall acceptance require a 30-minute round, a 45-minute round, or only a 30 percent relative reduction, and what Peak RSS share of launch-time available RAM is acceptable?
- **Options and tradeoffs:** A 30-minute limit requires about a 67 percent reduction from the observed round and gives a useful absolute bound; 45 minutes is easier but can still make multi-round runs exceed an hour; relative-only acceptance may not resolve user-visible waiting. Lower RAM shares preserve more OS headroom, while a higher share permits the fixed four-worker cache at greater system-pressure risk.
- **User answer:** Option 1: each fallback round shall not exceed 30 minutes; change the RAM limit to 85 percent.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-012, REQ-009, and AC-009 define the full Training runtime, process-tree Peak RSS, timing visibility, and benchmark evidence contract; OD-005 is resolved.

## Out of Scope

- Unix `fork`; Training uses Windows `spawn` only.
- Recording-major candidate accumulation.
- Adaptive Threshold refinement or changing the inclusive 2.0 and 12.0 endpoints.
- Changing Confirmation Modes, ranking rules, fallback rules, public ports, or persisted project schema.
- Treating the UI's synthetic Speed/Offset rotation as true per-recording progress.

## Open Decisions

None.

## Routing/Gates

- Grilling and spec governance are complete.
- Product implementation requires a new exact `開始執行` after confirmation because DEC-004 changes the algorithm contract.
- Required delivery gates: TDD, code review, algorithm record/governance updates, development architecture gate, same-grid differential equivalence, Threshold-grid validation, and performance/memory evidence.

## Revision History

| Revision | Date | Summary |
|---|---|---|
| 1 | 2026-08-25 | Started Qualification replay score-cache change set and recorded the selected optimization method. |
| 2 | 2026-08-25 | Selected private full-recording score caching per active History/model with existing candidate-major order. |
| 3 | 2026-08-25 | Selected balanced runtime and Peak RSS acceptance thresholds and completed the decision interview. |
| 4 | 2026-08-25 | Changed the Threshold increment from 0.25 to 0.5, updated same-grid equivalence, and reconfirmed the algorithm contract. |
| 5 | 2026-08-26 | Reopened the change set and selected a fixed four-process Windows spawn policy for the four History candidates. |
| 6 | 2026-08-26 | Selected complete reusable raw FIR matrix/evidence caching within each History worker. |
| 7 | 2026-08-26 | Selected preservation of healthy History workers and delayed one-time fresh-worker retry after all first attempts finish. |
| 8 | 2026-08-26 | Limited delayed retry to memory and worker-process failures; deterministic data, numerical, product-code, and cancellation outcomes do not retry. |
| 9 | 2026-08-26 | Made `MemoryError` terminal without retry and selected immediate concurrent one-time restart for startup failure or unexpected worker termination. |
| 10 | 2026-08-26 | Selected immediate cancellation of all workers and whole-run failure on terminal `MemoryError`. |
| 11 | 2026-08-26 | Selected a 30-minute per-round limit, 85-percent launch-time available-RAM Peak RSS limit, and complete timing evidence. |
