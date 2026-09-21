# SPEC-0017 pre-code architecture and Flow review

## Responsibility and observable behavior

`learning_qualification` remains the sole owner of candidate completion, Qualification evidence, qualified ranking, diagnostic ranking, and cancellation snapshots. After cancellation is observed, the module publishes one immutable partial `QualificationResult` containing only candidates that crossed the complete-candidate boundary. `studio_application` maps that result into the existing Candidate Dashboard and Analytical Replay views while retaining the terminal `Cancelled` state.

## Flow review

| Field | As-is candidate A | Selected candidate B | Rejected candidate C |
|---|---|---|---|
| Identity | `learn-and-qualify`; user Cancel; best-effort; `learning_qualification` | Same Flow, trigger, timing class, and owner | Same Flow, but periodic progress snapshots carry partial results |
| Ordered path | UI sets cancellation flag -> bounded worker observes it -> `InterruptedError` unwinds -> zero-payload Qt cancellation signal -> controller reports `Cancelled` and loses run-local candidates | UI sets cancellation flag -> bounded worker observes it -> Learning freezes the last committed complete-candidate result -> typed cancellation outcome crosses the existing queued worker/UI boundary -> controller commits the immutable result -> existing Dashboard/Replay queries expose it while state remains `Cancelled` | Every completed candidate is copied into a progress event -> controller owns a second partial-result accumulator -> later cancellation consumes the last progress snapshot |
| Data | No terminal result payload | One bounded immutable `QualificationResult`; candidate arrays/models are existing immutable in-process values; one queued handoff, no serialization or waveform copy | Repeated growing result snapshots on the progress channel and duplicate accumulator authority |
| Build/execution | Existing Windows CPython/PySide6 release; one analysis QRunnable plus existing spawn workers | Identical units, process topology, compiler/runtime, worker capacities, cancellation polling, and release composition | Same units but more Qt event traffic and ordering/coalescing constraints |
| Budget/cost | Meets cancellation observation budget but loses useful completed work | Same cancellation observation points and `O(1)` additional terminal event; ranking remains existing `O(R)` over retained candidates; no new latency, memory, queue, retry, lock, or real-time claim | Up to `O(R^2)` accumulated candidate references across repeated snapshots and possible progress coalescing ambiguity |
| Assurance | Functionally fails SPEC-0017 | Estimated static cost; functional behavior validated at domain and controller seams; existing runtime cancellation budget remains applicable because polling topology is unchanged | Rejected on ownership and event-ordering risk without product benefit |
| Evolution | Any cancellation feature must reconstruct lost state | Adding a result field remains Learning-owned; adding a UI consumer remains an L0 mapping change | Adding a subscriber or progress policy also changes partial-result correctness and duplicated state |

Candidate B passes functional admission: Learning commits candidate state before publishing cancellation, the queued event is at-most-once, the parent owns presentation mapping, and no sibling dependency is introduced. Candidate C is rejected because `studio_application` would become a second authority for an L1 partial analytical result and progress coalescing could hide the last committed candidate. No benchmark trigger applies: the selected design adds one terminal in-process reference handoff and no new execution unit, queue, copy, serialization, allocation loop, retry, timing class, or resource budget. Model assurance is `estimated`; it makes no new platform-performance claim.

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Commit a complete candidate | `learning_qualification` | `learning_qualification` | `studio_application` | `QualifiedCandidate` | `QualificationResult.candidates` | `learning_qualification` | Run-local immutable result | Internal L1 only | Adapter or L0 mutation of L1 candidate state |
| Publish cancelled partial result | `learning_qualification` | `studio_application` | `studio_application` | `LearningCancelled.result` / `QualificationResult` | `learning.cancelled` presentation mapping | `studio_application` | Immutable committed partial result | `studio_application->learning_qualification`; Learning event to parent | `learning_qualification->desktop_adapter`; child mutation of controller state |
| Expose retained cancellation result in Replay | `learning_qualification` | `studio_application` | `studio_application` | `QualificationResult`, `QualifiedCandidate`, `ReplayEvidence` | Existing controller QML maps and Replay query | `studio_application` | Controller-private selected candidate and recording identity | `studio_application->learning_qualification`; QML->controller | Diagnostic candidate export; Learning->QML/framework |

## Type Ownership Matrix

| Type | Owner / level | Declaration | Semantic role / visibility | Lifetime / mutability / authority | Consumers / referenced project types | Field roles | ABI, wire, storage impact |
|---|---|---|---|---|---|---|---|
| `LearningCancelled` | `learning_qualification` / L1 | `domain/learning/model.py` | Typed terminal cancellation outcome / cross-module | One cancelled call; immutable result reference; Learning constructs | Learning and `studio_application`; references `QualificationResult` | `result`: committed domain value | Python in-process exception only; no IPC, wire, ABI, or disk schema |
| `QualificationResult` | `learning_qualification` / L1 | `domain/learning/model.py` | Existing result / cross-module | One run through session; immutable; Learning constructs | Learning and L0; existing candidate/progress/provenance references | Fields unchanged; cancellation reuses existing candidates and diagnostic subset | No field, pickle, profile, or project-schema change |
| `QualifiedCandidate` | `learning_qualification` / L1 | `domain/learning/model.py` | Existing complete candidate evidence / cross-module | Run/session; immutable; Learning constructs | Learning and L0; existing model/config/history/evidence references | Fields unchanged | No ABI, wire, or storage change |
| `_LearningWorkerSignals` | `studio_application` / L0 | `adapters/desktop/controller.py` | Private Qt composition mapping | Application; Qt-owned signal object; L0 authority | L0 only; references `QualificationResult` | `cancelled` carries one immutable result payload | In-process Qt signal signature changes; no disk/wire format |
| `LearningWorker` | `studio_application` / L0 | `adapters/desktop/controller.py` | Private worker composition mapping | One run; owner-mutable cancellation flag; L0 authority | L0 and Learning public values | Maps typed Learning cancellation to queued result event | No persistence or external ABI |

## State Object Ownership Matrix

| State object | Definition/type | Owner | Lifetime | Mutability / read-write authority | Linkage, leakage, pointer escape |
|---|---|---|---|---|---|
| Run-local partial result | Local immutable `QualificationResult` binding in `run_learning` | `learning_qualification` | One run | Replaced only by Learning after a complete candidate | Stack/local Python reference; immutable snapshot crosses only through the event contract |
| Worker cancellation flag | Existing `threading.Event` in `LearningWorker` | `studio_application` | One run | Set/read only by L0 worker/controller composition | Private instance state; no new public access |
| Retained candidates, profiles, diagnostic IDs and preview ID | Existing controller-private fields | `studio_application` | Until next run/session replacement | Replaced by controller on terminal event | QML receives copied presentation values; no mutable child state leaks |
| Spawn worker/process state | Existing adapter-private objects | `history_worker_adapter` | One batch | Unchanged adapter authority | No process handle or IPC object crosses the Learning contract |

No mutable file-scope, static, thread-local, external-linkage object, pointer escape, or new persistent state is introduced.

## Dependency edges and parent mappings

Actual edges remain `studio_application -> learning_qualification` and `studio_application -> history_worker_adapter`; the adapter continues to implement the Learning-owned execution port. Intended edges are identical. The cancellation result travels through the Learning-owned output event to its L0 parent, which owns Qt signal and QML mappings. Forbidden edges remain `learning_qualification -> desktop_adapter`, `learning_qualification -> profile_export`, and adapter access to controller-private state.

## Algorithm screening and execution impact

The feature changes user-visible fallback/ranking behavior after cancellation, so ALG-0003 is amended. It reuses the already accepted total-error, finite-latency, exact-tie algorithm and adds only the complete-candidate cancellation boundary. The Flow remains best-effort offline analysis on the existing Windows execution units. No Task count, activation, rate, priority, core, queue capacity, scheduler, hard/soft real-time claim, or platform selection changes; no scheduling study is triggered.

## Planned validation

- Design manifest gate before product source edits.
- Red/green domain test: cancellation before any complete candidate returns no retained candidate; cancellation after a complete candidate retains only completed candidates.
- Red/green controller test: a cancelled partial result remains `Cancelled`, exposes qualified kernels or the exact existing diagnostic fallback in Replay, and keeps diagnostic kernels non-exportable.
- Existing Learning, worker, Replay, controller, project, QML, and architecture regression suites.
- Development architecture gate and generated-view stale check.
