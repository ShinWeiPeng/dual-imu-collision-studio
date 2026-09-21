# ALG-0004: Pooled Offset and speed-suffix search

## Metadata

- Status: proposed
- Owner module: `learning_qualification`
- Product feature: Complete fallback search and qualified candidate ranking
- Flow IDs: `learn-and-qualify`
- Related ADRs: None; module/port/storage contracts remain unchanged.
- Source paths: `src/dual_imu_collision_studio/domain/learning/service.py`, `src/dual_imu_collision_studio/adapters/desktop/controller.py`
- Test and benchmark paths: `tests/test_speed_fallback.py`, `tests/test_learning_run.py`, `tests/test_learning_plan.py`, `tests/test_controller_export.py`, `tests/test_diagnostic_replay.py`, `tests/test_history_execution.py`
- Supersedes: Early undetectable-offset exclusion, 2-12 threshold endpoints, and terminal failure on proven insufficient-evidence rounds. SPEC-0008 DEC-001 through DEC-007 define the behavior; ALG-0002 cache and ALG-0003 diagnostic rules otherwise remain applicable.

## Problem and observable success

Undetectable offsets previously skipped reduced-speed refits. A full-range pass also stopped the entire search. Both lose candidate coverage envelopes. Every remaining-offset pool must finish its speed search and then advance, including after success. Only winners passing their complete training range are qualified; failed winners remain diagnostic evidence.

## Inputs, outputs, units, ranges, and data-quality assumptions

Sorted supplied offsets (mm), speeds (mm/s), immutable LearningDataset and target numeric type. Each outer round pools all active offsets. Output remains QualificationResult in completion order, plus the existing diagnostic subset. Qualified ranking is a separate view; no persistent fields change. Sparse datasets retain existing supplied-tuple semantics, not fabricated Cartesian evidence.

## Constraints and quantitative acceptance thresholds

Thresholds are exactly 5.0 through 20.0 by 0.5: 31 values, 93 confirmation/threshold configurations for a frozen History model. The 20 ms collision deadline, 50 ms rearm, target arithmetic, folds, fit data and robust refit stay unchanged. FIR incomplete-history samples stay NaN/INVALID and cannot trigger; the first supported sample remains eligible.

## Candidate methods and comparative evidence

1. As-is: exclude an undetectable offset immediately and terminate on a passing range. Fewer refits, but fails SPEC-0008's exhaustive outer coverage and inner suffix requirements.
2. Selected: exhaust or pass the inner suffix first, then exclude the smallest active offset and reset all speeds. This changes state sequencing, not workers or ports, and preserves every requested envelope at increased run time.
3. Exhaust all speed suffixes even after an inner pass: more work, rejected because the confirmed spec stops that inner search at its first full pass.

## Selected method and reasons for rejecting alternatives

Candidate 2 is selected by SPEC-0008. Do not infer runtime improvement: this is a coverage correction. A lower-error diagnostic winner is not automatically a qualified kernel.

## Exact behavior, formula or pseudocode, boundaries, and tie-breaking

```text
offsets = all supplied offsets
while offsets nonempty:
    speeds = all supplied speeds
    repeat:
        fit pooled eligible evidence for offsets and speeds
        if all Histories prove insufficient evidence:
            record scope/reason, preserve retained kernels
            remove lowest speed or finish inner search when only one remains
            continue without a fabricated winner
        qualify frozen models on all supplied recordings; retain one round winner
        if winner passes all active supplied conditions: finish inner search
        if only one speed remains: finish inner search
        otherwise remove the lowest speed and refit
    exclude the smallest active offset, even after a pass
qualified = retained winners with nonempty passing_speeds == training_speeds
rank qualified by (-speed_count, -active_offset_count, taps,
                   worst_latency, -robustness_margin, stable_order)
```

Retained IDs and diagnostic completion order do not change. Final range-match termination keeps STOP_RANGE_MATCH; final failed exhaustion keeps EXHAUSTED. Intermediate outer transitions use EXCLUDE_OFFSET. Each speed removal uses REDUCE_SPEED. Controller qualification mapping also rejects range mismatches.

## Parameters, calibration, versioning, and compatibility

DEC-007 adds the Learning-owned evidence-shortage type and optional immutable result/progress reason fields described below; existing constructors retain empty defaults. No serialized project fields, profile versions, or acquisition transforms change. Old saved profile parameters remain unchanged. The project-session validator accepts the union of the legacy 2-12 quarter-step grid and current 5-20 half-step grid, so new results can save/reopen without invalidating legacy profiles. This is persistence compatibility, not an enlarged Training search. Threshold is a fixed search grid, not an adaptive range or guaranteed separating boundary. Candidate plan counts derive from grid dimensions. Replaying additional thresholds does not refit FIR.

## Time and space complexity and resource budgets

For O offsets and S supplied speeds, at most O*S refit rounds, versus early termination in the as-is method. Threshold replay work per frozen model grows by 31/21; score-cache size is unchanged. At 1 kHz, the declared grid count is 4*5*2*3*2*3*31 = 22320. Four History worker processes, queues, copies, memory limits, cancellation checks, and per-round budgets remain unchanged. Retained round metadata grows at most O(O*S); cached arrays remain History-local. Assurance is estimated for full user datasets; tests validate functional sequencing, not a worst-case runtime guarantee.

## Errors, degradation, fallback, and forbidden behavior

SPEC-0008 DEC-007 refines missing-evidence handling: a typed InsufficientTrainingEvidence denotes absent fit samples, insufficient Cycle groups, or no supported FIR windows in a required fold/final fit. History evaluation returns an explicit unavailable reason only for this type. A round with only proven-unavailable History results is recorded in progress and the completed result, then advances like a failed round without manufacturing a winner. Every empty History must carry this evidence reason, including in mixed batches containing successful Histories. Numerical/resource/unexpected execution failures propagate immediately, including a single failed solve among otherwise viable model rules; no successful rule is not evidence shortage. Cancellation remains terminal. An empty qualified pool still maps to Failed in the application. Never skip speed reduction solely because an offset is undetectable. Never admit a partially passing training range into export. Do not convert warm-up NaN to a Score or hard-code four invalid rows for every tap count.

## Validation cases and evidence

SPEC-0008 AC-001 through AC-006 define the public domain state-machine, run/progress, ranking, plan, qualification/cache, controller/export and replay seams. Cases include the fully failing 4-offset/2-speed eight-round controller sequence; full/reduced passes; smallest-offset removal; every ranking tie; partial-winner exclusion; 31 thresholds/93 configurations; threshold above 12; float32/float64 warm-up/discontinuity; real sparse earlier-winner retention; later-offset continuation; insufficient Cycles/FIR support; all-unavailable failure; mixed/unclassified empty History results; single and repeated numerical/resource/unexpected failures; and Windows spawn reason preservation without retry. On 2026-08-27, `.venv/Scripts/python.exe -m pytest -q --basetemp .test_tmp/spec8-retention-full --tb=short` passed 219 tests in 38.49 s. Architecture design/development/release gates returned exit 0 PASS VERIFIED (existing QML symbol-analyzer SHOULD warning). Source-level Standards and Spec re-review passed after fixing both discovered error-boundary gaps. No fixed-point Git diff review is claimed because this workspace is not a Git repository. Full user-dataset Training/performance has not been rerun.

## Risks and monitoring

More rounds and thresholds take longer; no maximum-dataset performance claim is made without target evidence. Wider thresholds can still miss collisions. Preserve all-supplied diagnostic denominators and evidence for failed rounds.

## Human approval

Behavior is authorized by the user's SPEC-0008 confirmation and execution request in this task. This algorithm record remains proposed; no ADR acceptance is inferred.

## Pre-code boundary and ownership review

### Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Fit each fallback round | learning_qualification | history_worker_adapter | studio_application | HistoryJob | HistoryExecutionPort | studio_application | Immutable dataset and range | application -> Learning/adapter; adapter -> demand-owned Learning port | Learning -> concrete adapter |
| Publish completed candidates | learning_qualification | studio_application | studio_application | QualificationResult | controller result view | studio_application | Immutable retained winners | application -> Learning | Learning -> Qt |
| Admit and rank exportable profiles | learning_qualification | profile_export | studio_application | QualifiedCandidate | SemanticProfile | studio_application | Immutable full-range winners | application -> both domains | sibling domain -> sibling domain |

### Type Ownership Matrix

| Type | Owner | Declaration | Visibility / semantics | Lifetime / mutation authority | Consumers / project references | ABI, wire, storage impact |
|---|---|---|---|---|---|---|
| FallbackState, FallbackAction, FallbackTransition | learning_qualification | domain/learning/model.py | Existing domain values; active ranges and next transition | Run; immutable construction by Learning | Learning; transition references state/action/candidate | None; fields unchanged |
| QualifiedCandidate, QualificationResult | learning_qualification | domain/learning/model.py | Cross-module immutable model and result evidence | Run/result; constructor only | Learning and application; model/config/history/condition/candidate references unchanged | None; result candidates remain completion-ordered |
| HistoryJob, HistoryJobResult, HistoryBatchResult | learning_qualification | domain/learning/model.py | Cross-module immutable execution values | One round; constructor only | Learning and History adapter; dataset/history/candidate references unchanged | No IPC field changes |
| LearningService | learning_qualification | domain/learning/service.py | Public domain service | Session; Learning owns execution handle | Application, Learning; demand-owned HistoryExecutionPort | Methods only; no fields added |
| StudioController | studio_application | adapters/desktop/controller.py | Composition mapping | Application; L0 only | QML, immutable Learning values and SemanticProfile | No persistent field changes |
| ProjectSessionService | project_session | domain/project_session/service.py | Existing semantic validation service | Session; project_session authority | Application; existing ProjectDocument references | Validation accepts the new grid in addition to legacy values; no format/field/edge changes |

### State Object Ownership Matrix

| State | Owner | Lifetime | Read/write authority | Boundary and linkage |
|---|---|---|---|---|
| Current FallbackState and retained result local variables | learning_qualification | One learn_and_qualify call | Learning replaces immutable values | No mutable shared globals |
| Candidate plan THRESHOLDS tuple | learning_qualification | Process | Immutable class constant | No mutable file/static/thread-local state added |
| Per-History caches and worker state | Existing Learning/adapter owners | Existing History/round lifetime | Unchanged private owners | Existing immutable IPC only |
| Controller retained candidates/profiles/preview selection | studio_application | Completed run | Controller only | QML sees presentation values; no child state access |

Actual and intended dependency edges and parent mappings are identical to the manifest; all behavior changes remain in the existing Learning owner and its L0 profile mapping. No new execution unit, callback, queue, lock, subscriber, platform, or ABI. Adding a speed or offset is data-only; adding a confirmation mode affects the Learning grid and detector tests, not module topology. The workload is best-effort offline analysis: the collision window is not an OS scheduling deadline. No scheduling study or platform-performance winner is claimed.

### DEC-007 pre-code ownership and Flow review

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Return proven History shortage | learning_qualification | history_worker_adapter / learning_qualification | studio_application | HistoryJobResult with unavailable_reason | Existing HistoryExecutionPort result | studio_application | Immutable result only | adapter -> Learning contract | Learning -> adapter implementation |
| Show skipped round and preserve winners | learning_qualification | studio_application | studio_application | LearningProgress / QualificationResult | Existing controller summary | studio_application | Owner-private summary mapping | application -> Learning contract | Learning -> Qt |

| Type / fields | Owner / level | Declaration / visibility | Semantics, lifetime, mutation authority | Consumers / references | ABI, IPC, storage |
|---|---|---|---|---|---|
| InsufficientTrainingEvidence | learning_qualification / L1 | model.py / module-public | ValueError subtype; proven evidence shortage only; one evaluation; constructor authority | Learning / no project references | New internal Python type; not serialized as worker error |
| HistoryJobResult.unavailable_reason | learning_qualification / L1 | model.py / cross-module | Immutable metadata string, empty default; one job; Learning constructs | Learning, History adapter / unchanged references | Additive Python IPC field; coordinated same-version workers; no disk schema |
| LearningProgress.unavailable_reason | learning_qualification / L1 | model.py / cross-module | Immutable metadata string, empty default; one run; Learning constructs | Application, Learning / unchanged references | Additive Python field; no disk schema |
| QualificationResult.unavailable_rounds | learning_qualification / L1 | model.py / cross-module | Immutable tuple of LearningProgress; empty default; completed result; Learning constructs | Application / LearningProgress and QualifiedCandidate | Additive Python result; no project/profile schema |

| State object | Owner | Lifetime / read-write authority | Linkage / boundary |
|---|---|---|---|
| Skipped-round snapshots in local result | Learning | One run, immutable replacement by Learning only | Local variable; snapshots cross boundary, no mutable alias |
| Existing execution summaries | studio_application | Current run; controller reads/writes | Private instance mapping; QML gets presentation text |

The actual and intended edges/parents above are unchanged. No new persistent state, shared mutable globals, ports, workers, retries, or scheduling policy. One private next-state calculation serves both ordinary and unavailable rounds so terminal scope and progression cannot diverge.

As-is Flow: Learning -> existing History port -> grouped fit -> empty candidate -> terminal failure, losing earlier accessible results. Selected Flow: same path -> typed shortage metadata -> owner commits unavailable snapshot -> existing progress output -> next suffix/offset -> completed retained results. Blanket catching empty/error results was rejected because it hides numerical and resource faults. Costs: at most O(offsets*speeds) small metadata snapshots, no additional waveform copy or matrix pass; existing History IPC carries one extra bounded reason string. Offline best-effort cost assurance remains estimated, not a performance claim. Adding a source changes dataset input only; adding a shortage condition changes Learning's typed classification and public-seam tests; adding an adapter preserves the existing History result contract. Validation is the real sparse regression plus error, empty-pool, continuation, progress/controller, and spawn-equivalence tests.
