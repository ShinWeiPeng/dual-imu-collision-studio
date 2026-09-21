# SPEC-0022 pre-code architecture design

## Responsibility and observable behavior

`desktop_adapter` owns Mapping Wizard presentation state. Pressing Next validates only the active step; pressing Finish validates final conditions and invokes the existing mapping command. Any recoverable failure leaves the Wizard and inputs intact and renders the exact bounded error inline. Successful Finish retains the existing accept/close behavior.

## Flow review

| Field | Candidate A — Wizard-local validation (selected) | Candidate B — controller step APIs |
|---|---|---|
| Identity | `prepare-workspace`, best-effort UI command, owned by `data_workspace` with `desktop_adapter` presentation | Same Flow, with five new QML/Python validation calls |
| Ordered path | QML Next validates local fields; QML Finish calls existing `StudioController.confirmMapping`; domain/adapter rejection is copied from `statusMessage` into private Wizard feedback | Every step marshals provisional UI values into new controller slots before advancing |
| Data | Primitive row, column, unit, rate, speed, and offset values; one private bounded string; no queues or copies beyond existing QML/Python call | Same values copied across the framework boundary on every step |
| Build | Existing Windows, Python 3.11+, PySide6 Qt Quick release composition | Same |
| Budget | Existing best-effort interaction latency; local validation is constant-time, while final source validation retains existing file-dependent cost | Adds boundary calls without reducing final file-dependent cost |
| Prediction | No new I/O, allocation, thread, queue, or blocking operation; constant-size local checks | More public surface and duplicated provisional state validation |
| Observation | Offscreen QML tests cover Next/Finish behavior; a fixed malformed fixture replays the original interior-gap rejection, while the externally recalculated supplied workbook now validates successfully | Would require controller and QML tests for new APIs |
| Assurance | Estimated before implementation; no benchmark trigger because the selected design adds only bounded local checks and no new execution structure | Estimated; no performance benefit |
| Evolution | New wizard field rules remain local to one presentation owner; existing controller/domain validation remains authoritative at Finish | Each new field or step changes both QML and controller interfaces |

Candidate A passes functional admission with a smaller stable interface and higher change locality. Candidate B is rejected because it creates new cross-boundary API and duplicated provisional state without changing observable correctness.

Algorithm screening: not applicable. The change performs no ranking, scoring, inference, numerical transformation, scheduling, or strategy selection; it only gates explicit UI transitions and presents existing validation results.

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Next current-step validation | `desktop_adapter` | `desktop_adapter` | N/A (owner-private) | Primitive QML control values | Boolean admission plus bounded string | `desktop_adapter` | `mapping-wizard-validation-error` | Owner-private QML reads/writes | Other modules reading or mutating Wizard-private state |
| Finish mapping confirmation | `desktop_adapter` | `data_workspace` / `tabular_adapter` through composition | `studio_application` | Primitive mapping and condition values | Existing `ColumnMapping`, `TabularInputPort`, and boolean result | `studio_application` | `mapping-wizard-validation-error`; existing controller-owned session state remains private | Existing QML-to-`StudioController` command and `studio_application` dependencies | Direct `desktop_adapter` access to domain runtime or tabular implementation state |

## Type Ownership Matrix

| Type | Owner / level | Declaration | Semantic kind / visibility | Lifetime / mutability / authority | Consumers / field roles | ABI, wire, storage impact |
|---|---|---|---|---|---|---|
| `ColumnMapping` | `data_workspace` / L1 | `domain/data_workspace/model.py` | Domain value / cross-module | One confirmation; immutable; constructed through application mapping | `studio_application`, `data_workspace`, `tabular_adapter`; mapping values | None; unchanged |
| `HeaderProposal` | `data_workspace` / L1 | `domain/data_workspace/model.py` | Domain value / cross-module | One Wizard session; immutable | Existing proposal consumers; provisional rows/columns | None; unchanged |
| `StudioController` | `studio_application` / L0 | `adapters/desktop/controller.py` | Composition mapping / module-public | Application session; owner-mutable by `studio_application` | Existing QML facade | None; unchanged |

No named type is added or changed.

## State Object Ownership Matrix

| State | Definition / type | Owner | Lifetime / mutability | Read / write authority | Storage / leakage / pointer escape |
|---|---|---|---|---|---|
| `mapping-wizard-validation-error` | `MappingWizard.qml::validationError` / string | `desktop_adapter` | One Wizard instance; owner-mutable | `desktop_adapter` / `desktop_adapter` | QML file-static property; private; no pointer escape |
| `recordings-viewport-before-wizard` | `Main.qml::recordingsViewportY` / real | `desktop_adapter` | One ImportPage instance; owner-mutable | `desktop_adapter` / `desktop_adapter` | Existing QML file-static property; private; unchanged |

## Dependency edges and parent mappings

- Actual unchanged edges: QML invokes the application-owned `StudioController`; `studio_application` maps to `data_workspace` and invokes `tabular_adapter` through the existing demand-owned port.
- Intended unchanged edges: no new module dependency, port, callback, or event. Wizard-local validation stays inside `desktop_adapter`; final semantic validation stays in existing owners.
- Parent mapping: `studio_application` remains the sole mapping owner between presentation primitives, `ColumnMapping`, the tabular input port, and committed workspace state.
- Forbidden: exposing `validationError` through controller/domain contracts; letting QML read domain-private or adapter-private runtime objects; committing any mapping on failed validation.

All owners, authorities, edges, and mappings are resolved: **PASS**.
