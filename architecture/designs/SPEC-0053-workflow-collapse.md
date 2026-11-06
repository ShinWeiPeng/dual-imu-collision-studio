# SPEC-0053 pre-code design: collapsible WORKFLOW

## Boundary Design Table
| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Toggle sidebar | user gesture / Qt Button | desktop_adapter QML | studio_application composition | clicked signal | private Boolean toggle and layout bindings | desktop_adapter | workflowCollapsed | adapter internal UI bindings | domain imports of Qt or UI state persistence |
| Select stage | desktop_adapter QML | studio_application | studio_application | existing index | existing StudioController.selectStage | studio_application | existing selectedStage / stages, unchanged | existing QML facade binding | new sibling domain edges |

## Type Ownership Matrix
| Type / declaration | Owner / level | Role / visibility | Lifetime / mutability / authority | Consumers / referenced project types | ABI / wire / storage impact |
|---|---|---|---|---|---|
| Existing Main.qml ApplicationWindow / Qt controls | desktop_adapter / L3+ | private view; external framework types | window; UI-thread owner only | QML layout; no new project type | None |
| Existing StudioController | studio_application / L0 | existing composition facade | session; existing authority unchanged | existing primitive stage projection | None |
No new named production type or project-type reference.

## State Object Ownership Matrix
| Object | Declaration / type | Owner | Lifetime / mutability | Read / write authority | Leakage / escape |
|---|---|---|---|---|---|
| workflow-collapsed | Main.qml workflowCollapsed / bool | desktop_adapter | one window, initially false; owner mutable | desktop_adapter only | private QML property; no persistence, global, static Python, cross-module reference or domain consumer |
| selectedStage / stages | existing Controller projection | studio_application | unchanged | existing controller commands; QML reads and selects through existing facade | unchanged |

## Actual/intended dependency edges and parent mappings
Unchanged: studio_application composes desktop_adapter; QML calls the existing studio facade. The collapse toggle and all associated layout state stay inside desktop_adapter. No new port/event, dependency, worker, queue, execution unit, workload mapping or parent mapping.

## Behavior and screening
Expanded width 238 px; collapsed width 72 px. Keep a constant 36 px header with an accessible toggle. Narrow mode hides names and session details, centers the 28 px stage markers and retains disabled/selected/complete states. Hover tooltips name each stage including unavailable stages. Sidebar sizing is constrained so RowLayout allocates the freed width to workspaceStack. Restore on click or keyboard activation. No animation is needed, avoiding transient clipping or delayed resizing.

Algorithm impact: not applicable; direct Boolean visibility/width bindings only. No sample processing, fitting, qualification, export, timing budget or scheduling change. No new public cross-module callback; Button.clicked is adapter-private framework wiring. Accepted ADRs: none (existing ADR-0001 and ADR-0002 remain proposed).

## Validation
Single architecture_cli render and design gate before source edits; development gate after source. Verify actual Qt clicks, keyboard activation, stage navigation and disabled behavior at default/minimum sizes, geometry and screenshots. Run existing relevant QML smoke tests. Preserve all prior dirty changes. No hardware/performance claim.
