# SPEC-0035 design

Authorized scope: Calculate filter wording and full captions at scaled fonts. Keep backend previewSingleImuMapping and all calculation/adoption/invalidation logic unchanged. Replace separately estimated TextMetrics with actual PaddedButton content implicit size and padding; constrain the local slot's minimum and preferred width/height. Qt fractional measurements are rounded up.

## Boundary Design Table
| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Calculate/adopt | SensorMapping | Existing controller facade / same sensor | studio_application composition / local desktop_adapter | unchanged primitive request/settings | existing calculation and adoption handlers | unchanged | filterPreview, adoptedFilter | current facade/local bindings | domain mutable state leakage |
| Measure captions | Qt Button/Label content | local slot | desktop_adapter | implicit sizes/padding | local geometry bindings | desktop_adapter | no added state | Qt-owned presentation data | new cross-module state |

## Type and State Ownership Matrices
| Type/object | Owner | Visibility/lifetime | Mutation and consumers | References/ABI/wire/storage impact |
|---|---|---|---|---|
| SensorMapping / PaddedButton / Label | desktop_adapter (Qt Label framework owned) | existing adapter bindings; wizard instance | local UI only | none; remove auxiliary TextMetrics instance |
| filterPreview / adoptedFilter | desktop_adapter | existing private vars; per-sensor wizard lifetime | existing calculation/adoption/invalidate/load; existing draft consumer | none |
| errorText / wizard.validationError | desktop_adapter | existing private strings | same validation and feedback handlers | wording only |
| new globals/static/thread-local/extern | none | n/a | n/a | none |

Actual/intended dependencies, formal parent (desktop_adapter remains null), composition mapping and state authority are identical to SPEC-0034. No new named project type, source set, public symbol, state object, event, port, workload, callback boundary, algorithm or timing claim. Manifest diff is only the invariant's action wording and complete-caption sizing description. Both ADRs remain proposed; baseline remains empty. Generated views must be rendered by architecture_cli.py.

Verification: existing QML lifecycle and wheel/mouse tests plus a subprocess matrix of four QT_SCALE_FACTOR values (1, 1.25, 1.5, 2) and 10/16-point Segoe UI fonts. Check actual Text.truncated and content bounds for every stage and both sensors at 740x430; save rendered evidence. Use Ruff 0.16.6 for Python and preserve local QML style.
