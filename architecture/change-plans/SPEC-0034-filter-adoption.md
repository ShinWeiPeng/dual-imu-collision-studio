# SPEC-0034 pre-code design

The authorized revision 4 changes only the desktop_adapter presentation of the existing per-sensor preview/adoption lifecycle. One stable slot contains the next action button or a genuine Label after adoption. Next keeps its existing current-step validation and warning region. No new algorithm, state authority, source set, module, callback boundary, port, event, workload or scheduler policy.

## Boundary Design Table
| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Preview current design | SensorMapping in desktop_adapter | StudioController in studio_application | studio_application | Existing primitive preview request | previewSingleImuMapping | studio_application | per-sensor filterPreview | existing Qt facade call | direct QML access to domain mutable state |
| Adopt and display | SensorMapping | Same SensorMapping instance | desktop_adapter local composition | successful preview.settings | adoptedFilter | desktop_adapter | filterPreview, adoptedFilter | local bindings and handler only | shared mutable state between sensors |
| Validate Next | MappingWizard | SensorMapping.validate | desktop_adapter local composition | current-step validation | boolean and errorText | desktop_adapter | wizard.validationError | existing local call | adopting implicitly on Next |

## Type Ownership Matrix
| Type | Owner | Role/visibility/declaration | Lifetime/mutation authority | Consumers/references | ABI/wire/storage impact |
|---|---|---|---|---|---|
| SensorMapping | desktop_adapter L3+, parent null as declared | existing module-public adapter-binding in qml/SensorMapping.qml | wizard instance; desktop_adapter only | MappingWizard; existing primitive settings | None |
| StudioController | studio_application L0 | existing Qt composition mapping in adapters/desktop/controller.py | application; L0 only | existing facade consumers; no new references | None |
| PaddedButton and Label | desktop_adapter / Qt framework | existing UI component and framework control, local instances only | component lifetime | SensorMapping | None; no new project type |

## State Object Ownership Matrix
| Object | Definition/type | Owner | Lifetime/storage | Read/write authority | Escape |
|---|---|---|---|---|---|
| filterPreview | SensorMapping.qml var | desktop_adapter | per-sensor wizard instance | owning component | unchanged primitive settings |
| adoptedFilter | SensorMapping.qml var | desktop_adapter | per-sensor wizard instance | owning component | existing draft/confirm mapping |
| errorText / validationError | SensorMapping / MappingWizard string | desktop_adapter | component/wizard instance | existing validation handlers | label text only |
| globals/static/thread-local/extern | none added | n/a | n/a | n/a | none |

## Dependencies and parent mappings
Actual and intended edges remain identical: QML uses the composed StudioController facade; MappingWizard orchestrates its two SensorMapping instances; each SensorMapping owns its SingleImuFilters editor. desktop_adapter retains its existing null formal parent and dependency list. No cross-module mapping change. No duplicate stored presentation-state flag.

## Planned manifest and verification
Keep schema 2.2.0 and every existing declaration. Add one desktop_adapter invariant documenting the authorized shared slot and Next prerequisite; render views exclusively through architecture_cli.py. Planned design gate must pass before source edits. Focused QML wheel/mouse and Next lifecycle tests cover both sensors, restoration, edits, preview failure and software-filter-off behavior; existing mapping/controller and QML tests cover adjacent behavior. Runtime visuals inspect the actual Qt scene. No new numerical or performance claim.

Formatter: existing Python test uses Ruff 0.16.6, nonmutating check passed and byte hashes unchanged; QML keeps the existing local style and centralized DesignTokens. Formatting stays in the modified-file scope authorized by this UI change. No Git metadata is available in this checkout; original modified files are retained in local governance evidence for exact comparison.

## Runtime feedback correction
The rendered adoption scenario exposed stale pane and wizard warnings after successful adoption. Clear pane.errorText in the existing adoption action and let MappingWizard clear its validationError when the active sensor errorText changes. These are local QML property-change handlers within desktop_adapter, not a new cross-module callback, signal, state authority or boundary. Existing validateCurrentStep sets the current error after validation returns, preserving Next error priority. Actual and intended dependencies and state ownership remain unchanged.
