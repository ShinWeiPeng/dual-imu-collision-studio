# SPEC-0044 pre-code design

Authorized scope: SPEC-0044 revision 3 and SPEC-0043 revision 6, user message msg_01a12d91-5c15-7fa0-b035-68e2b9a6586b. Version 0.20.0. Windows desktop, existing Python/Qt toolchain. No ADR approval claimed.

## Boundary Design Table
| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Common event replay | LearningService | replay_common_events | learning_qualification | scores/time/config/reset | immutable trace | learning_qualification | call-local latch/timer | Learning to owned helper | export-owned event semantics |
| Qualification evidence | LearningWorker | StudioController | studio_application | immutable evidence or failure/cancel | correlated UI completion | studio_application | session results/epoch | L0 composition to Learning | UI computes qualification math |
| JSON command | QML | StudioController | studio_application | name/path/overwrite consent | immediate rejection or accepted background work | studio_application | one active worker | desktop to L0 | blocking file write on UI |
| JSON worker completion | _JsonExportWorker | controller/QML | studio_application | saved/exists/error result | release busy and project-owned result | studio_application | captured snapshot | composed export service plus file adapter | worker mutates live controller |
| Evidence persistence | controller | ProjectSessionService | studio_application | versioned policy/input/profile identity | optional legacy-compatible validated data | studio_application | project evidence | composition maps domain and storage | inferred PASS for old files |

## Type Ownership Matrix
| Type | Owner/level | Declaration | Role/visibility | Lifetime/mutability/authority | References/consumers | Wire/storage impact |
|---|---|---|---|---|---|---|
| StudioController | studio_application/L0 | adapters/desktop/controller.py | composition | session, UI owner mutable | domain services, Qt/QML | optional qualification_evidence mapping in project results; JSON unchanged |
| LearningWorker | studio_application/L0 | same | composition QRunnable | task, captured snapshot; cancel Event | LearningService, DeploymentQualification | rename deployment UI workflow to requalification |
| _JsonExportSignals | studio_application/L0 | same | private framework signals | one job | controller/QML, primitives | result signal, no storage |
| _JsonExportWorker | studio_application/L0 | same | private composition | one job, captured model/data immutable by ownership | ProfileExportService, AtomicProfileWriter | no JSON schema change |
| DeploymentQualification | learning_qualification/L1 | domain/learning/deployment.py | existing immutable evidence | one qualification | QualifiedCandidate, LearningService, controller | reused evidence type; no deployment side effect |
| DetectorConfig | learning_qualification/L1 | domain/learning/model.py | immutable config | captured call | common replay | new default 0.8; policy version distinguishes legacy |
| ProjectSessionService | project_session/L1 | domain/project_session/service.py | validation service | stateless | controller | validate optional evidence fields and hashes |

## State Object Ownership Matrix
| State | Type/owner | Lifetime | Mutation/read authority | Storage/linkage | Escape |
|---|---|---|---|---|---|
| qualification results/bindings/epoch | existing dictionaries/scalars; studio_application | session, invalidated by source/model changes | controller UI thread only | private instance | serialized primitive copies |
| requalification worker/cancel | LearningWorker/Event; studio_application | single task | UI cancels, worker checks, UI completes | private instance | immutable signal results |
| JSON active worker/kernel | _JsonExportWorker/scalar; studio_application | one export | UI accepts/releases, worker owns captured inputs | private instance | completion primitives only |
| latch/quiet deadline | local scalars; learning_qualification | replay | common replay only | call-local | immutable trace |
No new mutable global/static/thread-local/extern state. JSON work blocks project switching and close until completion; no write-time cancel. Existing QML queue remains desktop_adapter-owned.

## Dependencies and parent mappings
Actual and intended edges remain studio_application -> learning_qualification/profile_export/project_session and concrete L3 file adapters at composition; domains do not import sibling adapters or QML. No new source file/module/port required. Requalification is a Qualification-page command, not an Export prerequisite workflow.

## Flow review
As-is: historical 0.5 replay plus independent 0.8 export gate, synchronous JSON write. Candidate A: only remove export button and change constant; rejected because divergent gap semantics and UI blocking remain. Selected B: all replay paths call existing common-event helper; qualification evidence is persisted/bound; single background JSON job reports completion. Structural separation keeps validation in Learning and formatting/writing in export composition.
Windows best-effort desktop; no hard/soft real-time deadline or speedup claim. Replay O(samples), state O(1) plus returned trace; snapshot/fingerprint O(input bytes), one extra captured export snapshot, one active job. Existing fitting and pool memory protection unchanged. Physical peak or timing calibration is not claimed.

## ALG-0044 — common qualification event policy
Owner learning_qualification; flow learn-and-qualify. User-selected semantics in SPEC-0044 DEC-001; record status proposed (no AI acceptance). Inputs target-precision scores, finite times, explicit discontinuities and sample rate; output DetectorTrace. Strict > collision threshold triggers one event and latches. Strict < 0.8 threshold for continuous valid 0.050 seconds rearms; equality/high/invalid/gap clears quiet timer, never implicitly rearms a latch. Reuse existing common helper; remove duplicate historical state machine. Include sample rate at recording-based callers. Evidence: deterministic thresholds/time/gap tests and Training/Replay parity; no performance winner from estimates.

## Verification seams
REQ-001/002 -> AC-001/002: shared replay boundary and family integration. REQ-003/004/008 -> AC-003/007: qualification-to-export and unchanged JSON. REQ-005/006 -> AC-004/005: Qt busy/results with delayed atomic writer, cancellation before write, failures, close/switch guard. REQ-007 -> AC-006: legacy and current persisted evidence, source/model invalidation, frozen-model requalification without fit. SPEC-0043 existing worker tests remain regression scope.

## Existing JSON compatibility

REQ-008 is read together with its SPEC-0041 relationship and preservation requirement: accelerometer-only model JSON retains schema_version 1; existing gyroscope/combined signal metadata retains schema_version 2. No schema downgrade, new model family, or release fields are introduced.
