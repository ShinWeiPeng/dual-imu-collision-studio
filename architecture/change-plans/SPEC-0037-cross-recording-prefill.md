# SPEC-0037 pre-source design

## Boundary Design Table
| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Explicit Adopt | SensorMapping | MappingWizard | desktop_adapter/window | filterParametersAdopted parameter-only snapshot | recentFilterParameters replacement | Wizard | current valid editor values, adopted result | same adapter signal upward | Domain exposed to QML mutable state |
| Enter IMU page | Wizard | SensorMapping / editor | desktop_adapter | parameter snapshot | prefillParameters / prefillIfEmpty | Wizard and owning editor | target private stages/warmup | same adapter downward call | shared mutable model or source mapping copy |
| Close/open recording | Main window | persistent Wizard | desktop_adapter | existing selectedRecording/open | existing load | existing window/controller mapping | original saved per-recording mapping | existing edges | persistence of template |

## Type Ownership Matrix
No named types or fields added/modified. FilterStageSpec, FilterDesign and SingleImuSettings stay immutable Learning-owned cross-module values declared in domain/learning/preprocessing.py with unchanged fields, references, consumers and storage. Signal payload uses primitive snapshot values, never Qt/domain handles or model references. No ABI/wire/project-schema change.

## State Object Ownership Matrix
| State | Owner/read/write authority | Declaration | Lifetime/reset | Consumers |
|---|---|---|---|---|
| recentFilterParameters | desktop_adapter only | MappingWizard.qml property var | window-owned Wizard lifetime; initial empty; replace only explicit Adopt; no reset on dialog close/open/recording switch; destroyed with window | child editors receive values only |
| stages/warmup/templateIndex | desktop_adapter only | SingleImuFilters.qml existing | target editor; load resets; prefill only no nonblank fields/default warmup | existing stage snapshots |
| filterPreview/adoptedFilter | desktop_adapter only | SensorMapping.qml existing | existing calculation/invalidation lifecycle | existing controller contract |

## Actual/intended edges and parent mappings
Unchanged domain and adapter dependencies. Existing Main has one MappingWizard instance which survives dialog closes. Wizard coordinates two SensorMapping instances and receives their explicit adoption signal. It strips no domain values because editor supplies fresh parameter-only arrays and primitives. Child prefill copies into its existing ListModel via loadSettings; no live model crosses a boundary. Prefill on entering step 2/3 and onOpened for an already-active sensor page avoids premature hidden-page fill. It leaves source/software toggles unchanged. No persistent files or controller process globals store defaults.

## Algorithm and flow screening
UI parameter snapshot/initialization only; no numerical algorithm or ranking, timing budget, new worker, execution unit, queue, retry, Port or domain Event. Existing design_filter validates new target sample rate. Two structural candidates: shared mutable editor model rejected (couples edits and ownership); parent-owned immutable snapshots selected by SPEC-0037 DEC-003/004. Per-entry work is linear in configured stage count, no performance claim. Existing best-effort UI execution retained.

## Gates and validation
SPEC-0037 revision 4 approved by current user 開始執行. Tests at real Wizard gestures and controller recording open seam were specified before source changes. Ruff 0.16.6 existing checks pass; retain compact QML style. Prior manifest/adoption/ARCHITECTURE/ADRs/baseline context remains current. State owner and mappings are fully resolved. Design gate on planned manifest must PASS before source edits; render and development/release follow. Existing ADRs remain proposed and baseline empty.
