# SPEC-0033 pre-code design

## Responsibility and flow review
L0 StudioController owns source selection, admission across all selected recordings, immutable per-algorithm requests and result/source identity. Existing L1 Learning owns filters, fitting, qualification and replay. QML owns only editable view state. Project Session validates inert serialized mappings; TabularReader reads selected columns. No new cross-domain dependency or model fitting method.

Candidate A: one existing analysis worker serially evaluates the selected requests and returns separately identified results. Candidate B: independent concurrent analysis workers per algorithm. Select A: preserves the existing single analysis-worker concurrency and cancellation boundary; B multiplies active worker pools/dataset copies and requires new admission/resource scheduling behavior. No faster/runtime-budget claim is made. Existing host execution profile and numerical algorithms are retained. Cost estimate: sum of selected algorithm costs; immutable input arrays can be referenced across requests, filtered arrays live with their mapped source; no persistent waveform payload. Assurance is estimated until tests/runtime scenarios run.

## Boundary Design Table
| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Map source signals | tabular_adapter | data_workspace | studio_application | ImportedSamples | Recording | studio_application | Controller source snapshots | L0 to tabular/data_workspace | workspace to Learning |
| Prepare algorithm input | data_workspace | learning_qualification | studio_application | WorkspaceSnapshot | LearningRequest/LearningDataset | studio_application | owner-private selection/source maps | L0 to both L1 domains | L1 sibling imports |
| Batch result delivery | learning_qualification | studio_application | studio_application | QualificationResult | UI/result primitives | studio_application | retained result/request identity | L0 to Learning | Learning to Qt |
| Persist/reopen | studio_application | project_session | studio_application | primitive inert source descriptors | ProjectDocument | studio_application | frozen source metadata, not waveform samples | L0 to project_session | project_session to Learning implementations |

## Type Ownership Matrix
| Type | Owner/level | Declaration | Role/visibility | Lifetime/mutation | Consumers/references | Storage impact |
|---|---|---|---|---|---|---|
| StudioController | studio_application L0 | adapters/desktop/controller.py | composition mapping/module public | session; L0 mutates | existing sibling domain values only | additive versioned mapping/source metadata and kernel-specific source choices; old projects accepted |
| LearningWorker and signals | studio_application L0 | adapters/desktop/controller.py | private existing Qt binding | batch; worker private event and snapshots | LearningRequest, QualificationResult | none |
| LearningRequest/LearningRecording/QualificationResult | learning_qualification L1 | domain/learning/model.py | immutable domain values/cross-module | one job/result; no mutation | existing owners/consumers | unchanged numeric contracts |
| SensorMapping | desktop_adapter L3+ | qml/SensorMapping.qml | private view component | wizard lifetime, QML-owned edits | primitive column/settings snapshots | no direct file access |
| SingleImuFilters | desktop_adapter L3+ | qml/SingleImuFilters.qml | reusable filter editor | per sensor wizard lifetime | immutable adopted design snapshots | existing coefficient format retained |

## State Object Ownership Matrix
| Object | Definition/type | Owner | Lifetime/storage | Read/write authority | Public leakage/escape |
|---|---|---|---|---|---|
| training sources and algorithm choices | StudioController instance dictionaries/tuple | studio_application | session/private instance | L0 only | QML receives primitive copies |
| mapped signal arrays/settings | StudioController instance dictionaries | studio_application mapping | source/project lifetime | L0 owns references; Learning receives immutable job snapshot | no child gets mutable registry |
| captured batch requests/result source descriptors | StudioController instance dictionaries | studio_application | accepted batch/retained result | L0 commit on Qt thread | immutable request values only |
| worker request sequence, cancellation Event | LearningWorker instance tuple/Event | studio_application private binding | accepted worker | worker and cancel command | no registry returned |
| per-sensor filterPreview/adoptedFilter | SensorMapping.qml var | desktop_adapter | wizard instance | QML component only | copies passed to confirm command |
| module globals/statics/thread-local/extern | none added | n/a | n/a | n/a | none |

## Dependencies and parent mappings
Actual and intended module edges are identical. L0 maps Workspace values to Learning values and maps profiles/source descriptors to ProjectDocument. QML accesses the established facade. No new sibling edge, Port, Event, Thread, Queue or retry mechanism. Existing completion/cancellation signals remain at-most-once per batch, published after final merged immutable results; failed admission dispatches zero jobs. Per-algorithm result IDs and source descriptors prevent mixed replay contexts.

## Verification seams
Controller mapping/selection/start commands and QML interactions; real preprocessing calculations and candidate Replay; strict project validation and round-trip; fake Learning service only at worker request boundary to verify selection, no dispatch, order, cancellation and result isolation. Final GUI hover/visibility scenarios use the real QML engine. Existing full regression and unified architecture development/release gates remain required. No physical hardware or new scheduler-performance claim.
