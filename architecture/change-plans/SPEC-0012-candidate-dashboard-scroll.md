# SPEC-0012 pre-code architecture design

## Responsibility and observable behavior

`learning_qualification` publishes typed, immutable loss evidence while it searches and
retains the already-computed per-recording Qualification metrics with each retained
kernel. `studio_application` converts those values into a session-only chronological
log and Replay table. `desktop_adapter` owns only the QML viewport, smart-follow, and
unseen-entry presentation state. On completed-project Open, the application rebuilds
the otherwise non-persisted retained-candidate drilldown once from the validated frozen
Profile and fingerprint-validated supplied recordings. No project schema, Profile schema, worker topology,
algorithm ranking, threshold rule, or Replay arithmetic changes.

## Flow review

### Training progress evidence

| Dimension | Candidate A: parse progress text | Candidate B: typed loss evidence (selected) |
|---|---|---|
| Functional admission | Message wording becomes an undeclared data contract and cannot reliably distinguish parameter, fold, validation, or terminal evidence. | Learning owns exact values and event meaning; the application only formats immutable evidence. |
| Execution cost | Negligible parsing cost, but still requires string allocation. | One bounded immutable value on existing coalescible progress delivery; no queue, worker, or replay work is added. |
| Evolution | Any wording change can silently break the UI. | New evidence kinds and fields remain owned by Learning and are testable at the existing event seam. |
| Assurance | Rejected: semantics cannot be proven from prose. | Estimated PASS for this best-effort local projection; no benchmark trigger applies because there is no new task, queue, copy of waveform data, or unbounded state. |

### Replay recording results

| Dimension | Candidate A: recompute on selection | Candidate B: retain Qualification metrics (selected) |
|---|---|---|
| Functional admission | A later recomputation can fail or diverge from the exact completed run and blocks UI selection. | The displayed row is the same immutable recording result used to aggregate the retained candidate. |
| Execution cost | Adds detector replay to the UI interaction path. | Adds only bounded metadata to each retained candidate; waveform arrays are not duplicated. |
| Evolution | Couples presentation to private Qualification execution. | Keeps Replay presentation dependent only on the public retained-candidate contract. |
| Assurance | Rejected: violates result provenance and responsiveness intent. | Estimated PASS; storage is linear in retained kernels times supplied recordings and bounded by the accepted session inputs. |

The selected design retains metrics during a run. Because those transient candidates
are intentionally excluded from `.dicsproj`, a successful completed-project Open uses
the existing public Qualification seam once during transactional restore to reconstruct
the same per-recording evidence and Model TXT input. Kernel selection itself remains a
metadata-only operation and does not replay recordings.

Both affected flows are best-effort. No hard/soft real-time scheduling study applies.

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Publish structured search/fold loss evidence | `learning_qualification` | `studio_application` | `studio_application` | `LearningProgress` with optional `LearningLogEvidence` | QML-facing immutable list snapshots | `studio_application` | Controller-owned session log only | `studio_application->learning_qualification` | `learning_qualification->desktop_adapter` |
| Present exact per-recording Qualification rows | `learning_qualification` | `studio_application` | `studio_application` | `QualifiedCandidate.recording_qualifications` | QML Replay row maps | `studio_application` | Selected kernel and recording index | `studio_application->learning_qualification` | `desktop_adapter->learning_qualification` |
| Export Replay from a table row | `studio_application` | `learning_qualification` | `studio_application` | Existing selected candidate and recording snapshot | Existing `learning.replay-export` command | `studio_application` | Selected recording index | Existing export Flow edges | Direct QML/domain dependency |
| Rebuild completed-project drilldown | `studio_application` | `learning_qualification` | `studio_application` | Validated frozen Profile plus fingerprint-validated supplied recordings | Existing `qualify_model` result | `studio_application` | Transaction-local restored data | `studio_application->learning_qualification` | Persisting transient log or candidate values |

## Type Ownership Matrix

| Type | Owner / level | Declaration | Semantic kind / visibility | Lifetime / mutability / authority | Consumers | Field roles | References | ABI / wire / storage impact |
|---|---|---|---|---|---|---|---|---|
| `LearningLogEvidence` | `learning_qualification` / L1 | `domain/learning/model.py` | domain value / cross-module | One progress event / immutable / none | Learning, application | evidence kind, parameter identity, Loss values, fold identity, validation verdict, evaluated/pending counts | `ParameterPoint` | Python in-process only; no wire or storage schema |
| `RecordingQualification` | `learning_qualification` / L1 | `domain/learning/model.py` | domain value / cross-module | Retained candidate lifetime / immutable / none | Learning, application | recording identity, condition, activity counts, detections, latency, status | none | Python in-process only; no Profile or project persistence |
| `LearningProgress` (modified) | `learning_qualification` / L1 | `domain/learning/model.py` | domain value / cross-module | One event / immutable / none | Learning, application, worker adapter | existing progress fields plus optional typed log evidence | `LearningLogEvidence` | Backward-compatible default; no storage |
| `QualifiedCandidate` (modified) | `learning_qualification` / L1 | `domain/learning/model.py` | domain value / cross-module | Completed run / immutable / none | Learning, application | existing aggregate evidence plus ordered recording results | `RecordingQualification` | Backward-compatible default; excluded from project/Profile schemas |
| `StudioController` (modified) | `studio_application` / L0 | `adapters/desktop/controller.py` | composition mapping / module-public | Application session / owner-mutable / application | QML | bounded presentation log and selection maps | Learning public values | Qt property surface only; no persisted schema |

## State Object Ownership Matrix

| State | Definition / type | Owner | Lifetime | Mutability | Read / write authority | Linkage / storage | Public leakage | Pointer escape |
|---|---|---|---|---|---|---|---|---|
| Training log entries | `StudioController._training_log_entries`, list of primitive maps | `studio_application` | Current process session; reset at accepted Start and successful New/Open project replacement | owner-mutable, capped at 10,000 | application / application | Python instance storage | immutable Qt list snapshots only | none |
| Discard counter | `StudioController._training_log_discarded_count`, integer | `studio_application` | Same accepted run | owner-mutable | application / application | Python instance storage | formatted marker only | none |
| Smart-follow state | QML Flickable position and unseen count | `desktop_adapter` | Current Training page instance | adapter-mutable | QML / QML | QML object instance | no domain exposure | none |

No mutable file-scope, static, thread-local, external-linkage, or address-crossing
object is introduced, so the manifest `state_objects` catalog remains unchanged.

## Dependency edges and parent mappings

- Actual and intended dependencies remain `studio_application -> learning_qualification`
  and `desktop_adapter -> learning_qualification` only for the adapter's declared
  public-contract implementation. Learning does not import Qt or controller types.
- `studio_application` remains the parent and explicit mapper from Learning-owned
  values to primitive QML maps.
- QML invokes only `StudioController`; it never calls Learning directly.
- Existing Replay CSV and Model TXT ports, events, execution units, channels, and
  mapping owners remain unchanged.
- New/Open lifecycle checks and completed-project reconstruction remain application-owned;
  successful reconstruction commits atomically, while rejected/failed replacement leaves
  the existing project and session log unchanged.

## Algorithm screening

No product algorithm changes. Parameter search, half-up four-decimal tie behavior,
Validation allowance, fold selection, Qualification replay, fallback, and diagnostic
ranking remain exactly ALG-0006/ALG-0004 behavior. This change exposes existing
intermediate and per-recording evidence, so no new ALG record or ADR is applicable.
