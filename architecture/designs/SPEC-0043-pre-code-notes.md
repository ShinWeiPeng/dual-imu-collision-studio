# SPEC-0043 pre-code design

Scope: Auto or Manual 1..8 for FIR/MLP folds, session-only. Qualification and self-IMU remain unchanged. Existing mathematical estimates and 90% RAM protection are retained. User adoption: SPEC-0043 DEC-001; execution: 01a1295d-cbc2-7a91-8069-12b0fac0b4bb.

## Boundary Design Table
| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Training preference | QML | StudioController | studio_application | Auto/Manual and integer | validated scalar | studio_application | private session preference | QML to L0 | persistence of preference |
| Run composition | StudioController | SpawnLearningExecutor | studio_application | captured scalar count | adapter idle configuration command | studio_application | immutable per-run choice | L0 wires adapter to Learning | domain imports adapter |
| Estimate query | LearningService | LearningWorker | studio_application | immutable FoldJob batches | preview-only execution | studio_application | captured dataset/settings | L0 to Learning public method | training during preview |
| Memory query | SpawnLearningExecutor | controller preview | studio_application | primitive estimate dictionary | display mapping | studio_application | OS memory snapshot | L0 composition to adapter | OS handles in domain |
| Preview completion | LearningWorker | StudioController | studio_application | completed/failed Qt signals | correlated captured input key | studio_application | private latest estimate | owner-local Qt delivery | stale result publication |

## Type Ownership Matrix
| Type | Owner/level | Declaration | Role/visibility | Lifetime/mutability/authority | Consumers/references | Fields and effects |
|---|---|---|---|---|---|---|
| StudioController | studio_application/L0 | adapters/desktop/controller.py | private composition mapping | application; UI-thread owner mutable | QML, LearningWorker | worker preference scalar; preview worker handle, captured key, report; no ABI/wire/storage change |
| LearningWorker | studio_application/L0 | adapters/desktop/controller.py | private composition mapping | one accepted task; immutable request, Event cancellation | LearningService, SpawnLearningExecutor, signals | preview executor optional binding; dataset/settings captured; no persistence |
| _LearningWorkerSignals | studio_application/L0 | adapters/desktop/controller.py | private framework binding | worker lifetime | controller | existing completed/failed/cancelled signals; no new events |
| SpawnLearningExecutor | history_worker_adapter/L3+ | adapters/parallel/learning_workers.py | adapter | idle-only owner command configures next run; batch snapshots selection; private per-call pool | LearningDataset, FoldJob, ExecutionBatch | configured count 0=Auto or 1..8; report primitives; no process handles escape |
| LearningService | learning_qualification/L1 | domain/learning/service.py | public service | existing service lifetime | FoldJob, ParameterPoint, LearningSettings | preview job generator, existing immutable domain contracts; no persisted setting |

## State Object Ownership Matrix
| Definition | Type | Owner | Lifetime | Mutation/read authority | Storage/linkage | Escape |
|---|---|---|---|---|---|---|
| worker mode/count and latest preview | scalar/dict | studio_application | session | UI thread only | controller instance including private composed executor binding | copied QVariant values only |
| preview QRunnable/cancel flag | LearningWorker/Event | studio_application | one bounded preview | cancel request UI; execution worker; completion UI | private instance | existing Qt signal connection only |
| captured worker count | int | history_worker_adapter | executor/run | adapter configure command while UI idle; batch local copy | private instance/local | no mutable reference |
| process map, pipes, pending jobs | existing containers | history_worker_adapter | batch | adapter only | local | no new escapes |
No new mutable global, static, thread-local or extern state. Existing module-level classes remain cataloged.

## Dependencies and parent mapping
Actual and intended edges stay studio_application -> learning_qualification and concrete adapter at composition; history_worker_adapter -> learning_qualification. No sibling/domain-to-adapter dependency added. QML -> controller scalar validation -> immutable executor configuration. Learning emits immutable job batches; adapter computes the existing memory estimate; parent formats display. Training repeats the estimate and fresh memory read immediately before spawn.

## Flow review and execution
As-is: UI captures requests; one Qt worker performs serial algorithms; FIR pool selects affordable count, MLP cap8, qualification cap4. Existing pool stays bounded and fixed per batch.
Selected: user count enters adapter composition; a single cancellable preview task computes estimates off UI thread, without spawning training children. Input identity mismatch marks display stale; refresh captures latest inputs; training rechecks regardless of preview.
Alternative: synchronous UI preview would retain simpler sequencing but expensive evidence counting could freeze UI. Rejected. Silent worker reduction in Manual violates adopted behavior.
Best-effort Windows desktop workload; no priority, affinity, deadline, scheduler or performance claim changes. Cost remains O(number of job evidence rows) for estimation plus bounded summaries; one preview maximum, no automatic queue of obsolete previews. Batch memory is parent serialization + sum of largest k phase peaks with existing 128 MiB per-worker allowance. Model assurance remains estimated; functional tests do not calibrate physical peaks. Lower concurrency may take longer.

## Algorithm and validation
Training, filtering, scoring and optimization math unchanged. Manual dispatch chooses min(requested, jobs) and admits only within fresh budget; recommendation is largest affordable 1..min(8,jobs), zero if none. Auto retains FIR recommendation and MLP existing cap. No retry or runtime resizing. Validate Auto/Manual boundaries, no-spawn rejection, budget refresh, stale preview, settings lock/session lifecycle, fold results, cancellation and cleanup. Existing timing tolerances are unchanged. No ADR acceptance is claimed.
