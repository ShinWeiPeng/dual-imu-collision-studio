# ALG-0002: Parallel History Training and cached replay

## Metadata

- Status: proposed
- Owner module: `learning_qualification`
- Product feature: Fixed-four History Training, per-fold FIR matrix caching, and cached Qualification replay
- Flow IDs: `learn-and-qualify`
- Related ADRs: `ADR-0002-windows-history-workers` (proposed)
- Source paths: `src/dual_imu_collision_studio/domain/learning/model.py`, `src/dual_imu_collision_studio/domain/learning/contracts.py`, `src/dual_imu_collision_studio/domain/learning/service.py`, `src/dual_imu_collision_studio/adapters/parallel/history_workers.py`, `src/dual_imu_collision_studio/adapters/desktop/controller.py`, `src/dual_imu_collision_studio/qml/Main.qml`
- Test and benchmark paths: `tests/test_learning_run.py`, `tests/test_history_execution.py`, `tests/test_learning_worker_controller.py`, `tests/benchmark_qualification_cache.py`, `tests/benchmark_parallel_history.py`
- Supersedes: ALG-0002 before SPEC-0003 revision 11, including its single-analysis-worker decision and 60-percent RAM statement.

## Problem and observable success

Training previously evaluated the 4, 8, 16, and 32 ms Histories sequentially in one Python process and rebuilt identical FIR feature, target, and row-index matrices for every model-rule candidate. One observed first fallback round took about 92 minutes 31 seconds while using approximately one of sixteen logical processors. Qualification already removed repeated normalized-score production, but Training remained dominant.

Success requires exactly four independent Windows `spawn` workers, one per requested History; complete worker-local FIR matrices prepared once per fold role and reused across model rules; stable result merging in requested-History order; exact sequential/parallel semantic equivalence; the confirmed retry and MemoryError policy; per-round, stage, total, worker, and attempt timing evidence; one non-retry fallback round at or below 30 minutes on the supplied dataset; and aggregate parent-plus-worker Peak RSS at or below 85 percent of available RAM measured immediately before launch.

## Inputs, outputs, units, ranges, and data assumptions

- Histories: exactly 4, 8, 16, and 32 ms requested jobs. A low Sample Rate may alias tap counts, but requested jobs remain distinct and ordered.
- Model rules: five Ridge alphas, two residual-scale methods, three robust-K values, and two Score Modes.
- Cross-validation: the existing deterministic two-to-five complete-Cycle/recording grouping plan.
- Qualification: three Confirmation Modes and a per-model inclusive [N,C] threshold grid starting at N with step 0.5, appending C and omitting zero/duplicate target values (SPEC-0009; ALG-0005). Count is unknown before scoring.
- Numeric types: exact target `float32` or `float64` replay.
- Inputs are immutable `LearningDataset` values copied by Windows spawn; workers never mutate source arrays.
- Outputs are immutable History candidates and bounded progress, attempt duration, launch-memory, and process-tree Peak RSS evidence.

## Constraints and quantitative acceptance thresholds

- Candidate and winner order remains History declaration order, Confirmation Mode declaration order, then ascending Threshold order; process completion order has no ranking authority.
- FIR features, targets, and row indexes are prepared once for each History/fold training role, each held-out condition role, and the final fit role.
- Qualification scores are produced once per frozen model and recording and reused for bound derivation and all candidates in its data-derived grid.
- Parallel and sequential executions are exact for frozen coefficients, detector configurations, condition evidence, rankings, fallback transitions, and retained Profiles.
- Exactly four first-attempt processes launch. Startup failure or unexpected termination receives one immediate fresh-process retry for that History only.
- Explicit `MemoryError`, data validation, numerical, product-code, and cancellation outcomes do not retry. `MemoryError` terminates all other workers and reports insufficient hardware memory.
- One non-retry fallback round must complete in at most 1800 seconds on the supplied dataset.
- Aggregate process-tree Peak RSS must not exceed 0.85 times launch-time available RAM.

## Candidate methods and comparative evidence

1. Keep one process and rebuild matrices for every rule: simplest, but observed runtime is unacceptable and CPU utilization is low.
2. Use Python threads: shares memory, but Python-level FIR preparation does not provide reliable CPU scaling under the GIL.
3. Use one shared process pool: convenient scheduling, but one abnormal process can break the pool and discard healthy History work.
4. Use four independent spawn processes plus worker-local matrix caches: selected because Histories are independent, failures can be isolated, and deterministic merge order is explicit.
5. Use Unix `fork`: excluded because the supported product target is Windows 10 or later.

## Selected method and exact behavior

```text
for fallback_round:
    launch_available_ram = available_ram_now()
    jobs = [History 4 ms, History 8 ms, History 16 ms, History 32 ms]
    launch one independent spawn process per job

    in each History process:
        build grouped folds
        prepare and cache FIR matrices once per fold role and final-fit role
        for each model rule in declared order:
            fit and score from cached matrices
        freeze selected model in target numeric type
        compute one score array per supplied recording
        derive active-round N/C; replay 3 confirmation modes x positive inclusive grid
        return immutable History result

    parent coordinator:
        sample aggregate parent + active-child RSS
        if explicit MemoryError or RSS > 85% launch available RAM:
            terminate all workers; fail as insufficient hardware memory
        if startup or abnormal exit and attempt == 1:
            immediately launch one fresh attempt for that History
        if startup or abnormal exit and attempt == 2:
            terminate remaining workers; fail
        merge successful results by requested-History order
        select and retain the round winner using ALG-0004 tie-break rules
        apply the ALG-0004 Offset/speed fallback transition
```

One shared pool is forbidden. Process handles, IPC connections, tracebacks, and multiprocessing types remain private to `history_worker_adapter`. Learning owns all job/result/failure semantics through `learning.history-execution`.

## Time and space complexity and resource budgets

Let `H=4`, `F` be folds, `M=120` model-rule combinations, `N` eligible fitting rows, `L` taps, and `C` the data-dependent detector candidate count.

- Former Training row preparation: approximately `O(H * M * F * N * L)` Python-level construction.
- Selected Training row preparation: `O(H * F * N * L)`, followed by matrix reuse for all `M` rules.
- Wall time can scale across four independent History processes; no linear speedup is claimed because Windows spawn copies data and NumPy backend scheduling varies.
- Worker-local cache space is `O(F * N * 3L)` per History plus copied dataset and temporary linear-algebra arrays.
- Qualification cache remains `O(N)` target-dtype score values per active frozen model.
- Runtime and memory acceptance are measured, not inferred: 1800 seconds per non-retry round and 85 percent launch-available-RAM process-tree Peak RSS.

## Errors, degradation, fallback, and forbidden behavior

- Explicit child `MemoryError`: no retry, terminate all active workers, fail with hardware-memory-insufficient guidance.
- Startup failure or child exit without a typed terminal message: retry once immediately for that History while healthy workers continue.
- Data validation, numerical, product-code, and cancellation outcomes: no retry.
- Cancellation terminates child processes and returns the existing cancelled run state.
- A completed History is never recomputed because another History retries.
- Forbidden: adaptive worker count, sequential main-process fallback after worker failure, Unix `fork`, shared mutable FIR matrices, completion-order ranking, persistence of FIR/score caches, skipped Qualification conditions, or weakening the current collision-latency rule defined by ALG-0003.

## Validation cases and evidence

- Public cross-validation seam proves one matrix preparation per fold role (7 preparations for the three-fold one-condition fixture instead of 361).
- Spawn adapter proves four out-of-order completions merge deterministically.
- Abnormal-exit injection proves only the failed History retries and only once.
- `MemoryError` injection proves other workers terminate promptly without retry.
- Sequential/spawn differential test proves exact coefficients, detector configurations, condition evidence, and stable ordering for all four Histories.
- Desktop composition test proves production uses `SpawnHistoryExecutor`.
- UI/controller test proves round duration, per-History attempt duration, and Peak RSS evidence are visible.
- Full pytest regression, generated architecture render, development architecture gate, Qualification cache benchmark, and supplied-dataset Windows process benchmark remain required before release.

## Risks and monitoring

- Windows spawn copies the dataset four times; live process-tree RSS monitoring and the 85-percent terminal guard bound pressure.
- Operating-system termination under extreme pressure may appear as abnormal exit rather than Python `MemoryError`; it receives the one permitted process retry, then fails explicitly.
- NumPy may use internal native threads in each child, causing oversubscription; the supplied-dataset benchmark is authoritative and thread limiting may be revisited only through a new confirmed decision.
- Concurrent worker progress is presented as global Training while any History remains in Training, then global Qualification, preventing stage oscillation.

## Human approval

- Worker count, cache scope, retry classes, terminal MemoryError behavior, 30-minute round limit, and 85-percent RAM limit: user-confirmed in SPEC-0003 revision 11.
- Formal ADR/algorithm record acceptance: pending non-AI approval reference; this record remains proposed.
