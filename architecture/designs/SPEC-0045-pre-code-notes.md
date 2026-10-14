# SPEC-0045 pre-code design

Confirmed revision 7; authorized by actual user message 01a12ed0-26eb-7541-94a2-bd4a359a5343. Stable skills 0.20.0. Existing Windows Python/Qt desktop, best-effort workload; no worker, scheduler, numeric-policy or public UI changes. ADRs remain proposed.

## Boundary Design Table
| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Qualification evidence | LearningService | application | studio_application | immutable Collision/RecordingQualification | retained candidate | studio_application | call-local metrics, retained immutable results | L0 to Learning public values | project_session computes collisions |
| Save | application | project_session | studio_application | Learning values | schema-1 primitive qualification_results | studio_application | existing retained candidates/results | L0 to sibling contracts | Learning imports persistence schema |
| Open | project_session / file adapter | application | studio_application | validated JSON and source fingerprints | frozen model and immutable results | studio_application | temporary restored document | existing ports, atomic session commit | any Open Training/Qualification/score fallback |
| Export admission | restored evidence | application | studio_application | existing frozen input/profile hashes and actual policy | existing qualification status | studio_application | existing results/bindings | existing identity checks | historical or missing data promoted to PASS |

## Type Ownership Matrix
| Type | Owner/level/declaration | Fields/role | Visibility/lifetime/mutability/authority | References/consumers | ABI/wire/storage |
|---|---|---|---|---|---|
| CollisionQualification | learning_qualification/L1, domain/learning/model.py | recording identity, ordinal, half-open annotation interval, detection, optional trigger/time/latency/margin/SNR and immutable unavailable reasons | public semantic value, retained result, frozen, Learning constructs and application maps copies | primitives; RecordingQualification, L0 | new optional schema-1 event rows; no binary ABI |
| RecordingQualification | same | existing values plus chronological collision tuple and nullable finite margins | frozen result; owner computes, application restores | CollisionQualification; Learning/L0 | optional result rows; legacy absent tuple remains unavailable |
| QualifiedCandidate | same | existing values plus actual qualification_policy metadata | frozen, same lifetime/consumers | existing RecordingQualification | actual policy remains historical when restored |
| ProjectDocument / ProjectSessionService | project_session/L1 | optional schema-1 results and finite/dimension/reference checks | existing persistence authority, immutable document | primitives, L0 maps | project schema 2 remains, optional independently versioned section |
| StudioController | studio_application/L0 | existing private retained-candidate and qualification dictionaries | existing UI-session mutation authority only | existing domain contracts | maps values at Save/Open, no new shared state |
Every new field is a domain value or metadata; none carries framework bindings or sample arrays.

## State Object Ownership Matrix
| State | Owner | Lifetime / authority | Storage/linkage | Escape |
|---|---|---|---|---|
| collision rows and finite margins | learning_qualification | one existing Qualification call, local accumulation only | local lists converted to frozen tuples | immutable snapshots only |
| retained candidates/results/bindings | studio_application | existing session, controller UI thread mutates containers | existing private instance state | primitive saved copies |
| candidate document and restored values | studio_application | one Save/Open transaction; commit after all checks | local values | no partial session commit |
| document schema | project_session | stateless validation of one immutable document | existing service | values only |
No mutable globals, static/thread-local/extern objects, callbacks, queues, tasks or new state owners.

## Edges and parent mappings
Actual Open L0 -> project_session/reader -> Learning.qualify_model -> replay. Intended Open removes qualify/replay and maps saved data to frozen values. All other dependencies remain L0 -> learning_qualification/project_session/profile_export and concrete adapters at composition. Sibling domains never import each other. Parent is studio_application for all affected L1 modules.

## Flow and cost review
As-is manage-project synchronously reconstructs CSV data and performs model x sample replay. Original bounded FIR probe: source restoration 100.51 s, dataset construction 48.61 s, first Qualification began 149.12 s and remained unfinished at 180 s. This is not a completed baseline or SPEC-0043/44 regression proof.
Candidate A retains Open Qualification and adds parallel workers; violates the confirmed no-worker-change scope and retains redundant computation. Selected B stores immutable event summaries during existing Qualification and restores them: Open source fingerprint/read costs remain O(source bytes + samples), result mapping O(models x recordings/events), no per-model full sample replay. Save grows O(models x events), not sample arrays. No timing/resource SLO, platform winner or calibrated improvement is claimed before AC-005 actual Windows evidence. No scheduling study applies: best-effort flow and unchanged execution grouping.
Evolution: new model family touches existing mapping; policy upgrades invalidate current evidence without replay; future results versions require validator and fixture changes. Malformed result data rejects before active-state commit. JSON atomic I/O and original external source protection remain unchanged.

## ALG-0045 — capture and restore Qualification summaries
Status proposed; no AI approval claimed. Owners learning_qualification (capture), project_session (schema), studio_application (mapping); flows learn-and-qualify and manage-project. Confirmed contract SPEC-0045 REQ-001..006.
Capture reuses the existing inclusive 150-ms eligible-trigger decision and chronological SNR values, without recalculating traces or changing aggregation. Store first eligible trigger index/time, original latency and margin, and explicit no-trigger/no-finite-response/nonpositive-noise reasons. Convert unavailable non-finite margins to null. Persist only retained profile results; incomplete legacy details are omitted, never manufactured. Restore schema-1 rows to immutable domain values, preserve actual policy and aggregate metrics, and retain existing evidence binding. Missing rows are Not stored / N/A. Unknown schema or corrupt types/counts/indices/references fail transactionally. Existing source/model/mapping/preprocessing/labels/rate/numeric/coverage/policy identity checks remain authoritative. No Training/Qualification/score compute during Open.

## Verification traceability
REQ-001/002 -> AC-001: intercept every compute entry during new/legacy Open and regress existing Start Training/Save. REQ-003/005 -> AC-002: deterministic PASS/FAIL/COVERAGE_GAP events, nullable SNR, float32/64 exact values, file contains no arrays. REQ-004 -> AC-003: binding/policy mutation and existing export tests. REQ-006 -> AC-004: legacy unavailable UI, malformed results and I/O/source failures preserve session and files. AC-005: bounded Windows original FIR copy and new results copy, six models, measured stage/Save/file/RSS values; original SHA retained. Existing whole-project layout findings remain actual failures until remediated, never waived by host tests.

Review refinement: QualifiedCandidate owns immutable original input/profile SHA256 metadata in addition to policy. Current export eligibility may be invalidated independently; Save preserves these original identities. Legacy coverage remains a profile-owned display fallback; unknown counters display N/A. No new mutable state owner or dependency edge.
