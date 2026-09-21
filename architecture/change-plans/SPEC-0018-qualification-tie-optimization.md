# SPEC-0018 qualification tie optimization — pre-code design

## Responsibility and observable behavior

`learning_qualification` continues to own parameter search, fold selection, Qualification, and progress evidence. Raw Loss computation is unchanged. Final parameter admission changes from minimum four-decimal equality to the configured relative convergence window. Fold admission changes from the lowest two rounded Kernel Losses plus ties to every exact raw minimum Kernel Loss fold. All admitted kernels still complete Qualification before ranking. Existing progress contracts expose the current ParameterPoint, fold identity, completed count, and pending count; total work is `completed + pending`.

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Parameter admission | `search_parameters` in `learning_qualification` | `run_learning` in `learning_qualification` | `learning_qualification` | Ordered `ParameterResult` values with raw Loss | Relative-window ParameterResult sequence | None; private same-module call | Function-local parameter cache, read after search completion | Private calls within `learning_qualification` | No adapter, application, or sibling-domain selection authority |
| Fold admission | `select_fold_kernels` in `learning_qualification` | Qualification coordinator in `learning_qualification` | `learning_qualification` | One ParameterResult's original FoldResults | All and only exact raw minimum Kernel Loss folds | None; private same-module call | Immutable FoldResult tuple | Private calls within `learning_qualification` | No worker-local or UI-driven ranking |
| Qualification progress | Qualification coordinator in `learning_qualification` | `studio_application` presentation mapper | `studio_application` | Existing `LearningProgress` plus `LearningLogEvidence` | Existing `learning.progressed` event handling | Existing application presentation mapping | Immutable progress snapshot only | `studio_application -> learning_qualification` contract dependency | No desktop-adapter mutation of Learning state; no waveform payload in diagnostics |

## Type Ownership Matrix

| Type | Owner / level | Declaration | Semantic kind / visibility | Lifetime and mutability | Mutation authority | Consumers / referenced project types | Field roles | ABI, wire, storage impact |
|---|---|---|---|---|---|---|---|---|
| `LearningSettings` | `learning_qualification` / L1 | `domain/learning/model.py` | Configuration / cross-module | Immutable per accepted run | `learning_qualification` validates/captures | application, Learning; primitive tolerance fields | Configuration | None; no field or persistence change |
| `ParameterResult` | `learning_qualification` / L1 | `domain/learning/model.py` | Domain value / cross-module | Immutable round evidence | Learning search constructs | Learning; references ParameterPoint and FoldResult | Domain values and provenance | None |
| `FoldResult` | `learning_qualification` / L1 | `domain/learning/model.py` | Domain value / cross-module | Immutable fold evidence | Learning workers construct; Learning validates identity | Learning and worker adapter; references ParameterPoint and ConditionLoss | Domain identity/value | None |
| `LearningLogEvidence` | `learning_qualification` / L1 | `domain/learning/model.py` | Domain value / cross-module | Immutable event payload | Learning coordinator constructs | Learning and application; references ParameterPoint | Existing parameter/fold identity and completed/pending metadata | None; existing fields reused |
| `LearningProgress` | `learning_qualification` / L1 | `domain/learning/model.py` | Domain value / cross-module | Immutable event payload | Learning coordinator constructs | Learning and application; references LearningLogEvidence | Existing evaluated/pending progress metadata | None; existing fields reused |

## State Object Ownership Matrix

No governed mutable static, file-scope, thread-local, extern, address-passed, or cross-module runtime state changes. Search caches, admitted parameter tuples, admitted fold tuples, and counters remain function-local values owned by `learning_qualification`; no pointer/address escapes and no new state catalog row is planned.

## Dependency edges and parent mapping

- Actual and intended edges remain unchanged: `studio_application -> learning_qualification`; `history_worker_adapter -> learning_qualification` while implementing the Learning-owned execution port.
- `learning_qualification` remains an L1 child of `studio_application`; `history_worker_adapter` remains L3+ and unparented.
- No new module, Port, Event, callback, queue, process, execution unit, channel, or sibling dependency is introduced.
- Existing forbidden reverse edges remain forbidden, including `learning_qualification -> studio_application` and `learning_qualification -> history_worker_adapter` implementation dependency.

## Flow cost review

| Field | As-is | Selected candidate | First-PASS alternative |
|---|---|---|---|
| Identity | `learn-and-qualify`, command-triggered, best-effort, owner `learning_qualification` | Same Flow and execution contexts | Same Flow but order-dependent termination |
| Functional admission | Minimum four-decimal Parameter Loss group; lowest two rounded Kernel Loss folds plus ties | Relative Parameter Loss window; every exact raw minimum Kernel Loss fold; all admitted kernels complete | Same admission as selected but stops on first full-range PASS |
| Ordered path | Search → worker fold fits → rounded selection → Qualification replay → ranking | Search → worker fold fits → relative/raw selection → Qualification replay → ranking | Search → worker fold fits → relative/raw selection → partial Qualification → first PASS |
| Data and ownership | Immutable ParameterResult/FoldResult and recording jobs; Learning owns ranking | Same types, copies, lifetime, authority, and four-process Qualification batches | Same types but result depends on scheduling order unless serialized |
| Static cost | `Q_old = P_4dp × F_two_plus_ties × recording replay work` | `Q_new = P_relative × F_exact_raw_min × recording replay work`; fold factor never exceeds the existing selected-fold set, while Parameter count requires measurement near rounding boundaries | Potentially lowest replay count, but unbounded quality/order sensitivity |
| Functional verdict | PASS but observed excessive work | PASS by SPEC-0018; preserves complete comparison of the admitted set | Rejected: violates deterministic complete ranking decision |
| Model assurance | Calibrated only by existing observed log; no bound for this dataset | `estimated` until the real-data measurement-only benchmark records the actual before/after distributions | Rejected before performance comparison |
| Evolution | Selection changes require Learning algorithm/tests/manifest/ALG update | One semantic owner; no public interface or deployment migration | Adds order/parallel-scheduler coupling and more regression surface |

The benchmark trigger applies because candidate admission changes repeated CPU work and observed wall time. No platform-specific winner or fixed speedup is claimed. The Windows execution profile, worker counts, scheduler, queues, memory admission, progress/cancellation budgets, and release composition remain unchanged; therefore no real-time scheduling study or Tier 2 platform tuning is required.

## Planned manifest and description-view diff

- Replace the `learning_qualification` invariant describing four-decimal Parameter ties and lowest-two fold ties.
- Update `learn-and-qualify.step-3` with relative Parameter admission, exact raw-minimum fold admission, and completed/total progress evidence.
- Clarify existing `learning-log-evidence` and `learning-progress` field descriptions for Qualification counters; no fields are added.
- Keep module, Port, Event, source path, entrypoint, public symbol, execution unit, mapping, channel, and dependency catalogs unchanged.
- Regenerate `architecture/ARCHITECTURE.md`, `architecture/generated/system.md`, and `architecture/generated/learning_qualification.md`; other marker-owned views may be rewritten only if deterministic rendering changes them.
- Update `ALG-0006`; keep it `proposed`. No ADR exception or acceptance change is required.

## Validation gates

1. Planned manifest: `python tools\architecture\architecture_cli.py gate --phase design --manifest architecture\manifest.yaml --adoption architecture\adoption.yaml --baseline architecture\baseline.yaml --format text`.
2. TDD: focused public optimizer and Learning-run seams go red before source changes, then green.
3. Measurement: same fingerprinted real dataset/settings/seed, three baseline and three modified runs, machine-readable `MEASUREMENT_ONLY` JSON.
4. Development: full pytest suite and the single development architecture gate.
5. Release acceptance remains separate; this change adds no physical-device or hard/soft-real-time evidence requirement.
