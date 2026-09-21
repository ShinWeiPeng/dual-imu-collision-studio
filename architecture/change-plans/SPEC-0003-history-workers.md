# SPEC-0003 History Worker Pre-Code Design

Status: confirmed for implementation by the user's `開始執行` on 2026-08-26.

## Boundary Design Table

| Boundary | Demand owner | Provider | Input | Output | Failure authority |
|---|---|---|---|---|---|
| `learning.history-execution` | `learning_qualification` | `history_worker_adapter` | Immutable `HistoryJob` containing one fallback state, one History, dataset, and numeric type | Immutable `HistoryJobResult` plus bounded `HistoryWorkerProgress` | Learning classifies semantic/numerical outcomes; the adapter classifies startup, abnormal process exit, explicit `MemoryError`, and cancellation |
| `learning.command` | `learning_qualification` | `studio_application` caller | Existing Learning dataset and numeric type | Existing progress and Qualification result | Unchanged |
| worker-to-UI bridge | `studio_application` | Qt queued signals | Existing `LearningProgress` and terminal result/error | QML presentation state | Unchanged; framework types do not enter L1 |

The process adapter owns Windows `spawn`, process handles, IPC, retry attempts, aggregate RSS sampling, and termination. The Learning domain owns job semantics, deterministic stable ordering, cache content, fallback decisions, and error classification values. No `multiprocessing`, Qt, process handle, Queue, Pipe, or exception traceback crosses the L1 public contract.

## Type Ownership Matrix

| Type | Owner | Visibility | Mutability | Consumers |
|---|---|---|---|---|
| `HistoryJob` | `learning_qualification` | cross-module | immutable | Learning, history worker adapter |
| `HistoryJobResult` | `learning_qualification` | cross-module | immutable | Learning, history worker adapter |
| `HistoryWorkerProgress` | `learning_qualification` | cross-module | immutable | Learning, history worker adapter, application presentation |
| `HistoryWorkerFailure` | `learning_qualification` | cross-module | immutable | Learning, history worker adapter |
| `HistoryExecutionPort` | `learning_qualification` | cross-module port | immutable protocol | Learning, history worker adapter |
| `_WorkerAttempt` and process messages | `history_worker_adapter` | private | adapter-owned mutable | history worker adapter only |
| FIR matrix cache entries | `learning_qualification` | private | immutable arrays after construction | one History job only |

## State Object Ownership Matrix

| State | Owner | Mutation authority | Lifetime | Release rule |
|---|---|---|---|---|
| Active History jobs and deterministic result slots | `learning_qualification` | `LearningService` | one fallback round | released after deterministic merge or failure |
| Spawned process handles and IPC endpoints | `history_worker_adapter` | `SpawnHistoryExecutor` | one first attempt or retry attempt | close after join; terminate all immediately on explicit `MemoryError` or cancellation |
| Retry count per History | `history_worker_adapter` | `SpawnHistoryExecutor` | one fallback round | maximum one retry for startup/abnormal process loss only |
| Per-History/fold FIR matrices | `learning_qualification` | worker-local Learning code | one History job | released when that worker returns, fails, or is cancelled |
| Launch-time available RAM and process-tree Peak RSS | `history_worker_adapter` | `SpawnHistoryExecutor` | one fallback round | retained only as immutable timing/resource evidence |
| UI run and stage clocks | `studio_application` | `StudioController` | one run | reset at next Start Learning |

## Dependency Edges

| Edge | Actual before change | Intended | Decision |
|---|---|---|---|
| `studio_application -> learning_qualification` | yes | yes | preserve |
| `studio_application -> desktop_adapter` | yes | yes | preserve |
| `studio_application -> history_worker_adapter` | no | yes | composition root injects the adapter |
| `history_worker_adapter -> learning_qualification` | no | yes | adapter implements demand-owned port and consumes immutable job/result types |
| `learning_qualification -> history_worker_adapter` | no | forbidden | domain cannot import multiprocessing adapter |
| `learning_qualification -> multiprocessing/Qt` | no | forbidden | technology remains outside L1 |
| worker process -> UI | no | forbidden | all presentation crosses coordinator and existing Qt queued signals |

## Parent Mappings

| Interaction | Producer | Consumer | Parent/mapping owner |
|---|---|---|---|
| Workspace to Learning request | `data_workspace` | `learning_qualification` | existing `studio_application` mapping |
| Learning History job to process attempt | `learning_qualification` | `history_worker_adapter` | demand-owned `learning.history-execution`; no sibling mapping required |
| History results to round candidates | `history_worker_adapter` | `learning_qualification` | `learning_qualification` deterministic merge |
| Learning progress/result to QML | `learning_qualification` | `desktop_adapter` | existing `studio_application` Qt bridge |

## Execution and Data Plan

- One coordinator remains on the existing Qt `QRunnable` so the UI event loop stays responsive.
- Exactly four independent Windows `spawn` processes are launched for requested Histories 4, 8, 16, and 32 ms. Independent process handles prevent one abnormal exit from invalidating healthy workers.
- Deduplicated tap aliases still produce exactly four requested jobs; if two requested Histories map to one tap count, the worker result is reused without changing stable candidate order.
- Each worker creates reusable raw FIR feature, target, and row-index matrices once per fold role and final fit for its History. Rule evaluation reuses these arrays.
- Successful History results are merged by the original History declaration order, never completion order.
- Explicit child `MemoryError` is terminal: terminate all workers, do not retry, and report insufficient hardware memory.
- Startup failure or unexpected process termination receives one immediate fresh-process retry for that History while healthy workers continue. Data, numerical, product-code, and cancellation failures do not retry.
- Aggregate parent-plus-worker Peak RSS must remain at or below 85% of available RAM measured immediately before first launch. One non-retry fallback round must complete within 30 minutes on the supplied dataset.

## TDD Seams

The confirmed public seams are `LearningService.learn_and_qualify`, `HistoryExecutionPort.execute`, and immutable Learning progress/completion values. Tests observe exact results, failure policy, retry count, cancellation, timing/resource evidence, and stable ordering through those seams; they do not mock private process handles or FIR cache dictionaries.
