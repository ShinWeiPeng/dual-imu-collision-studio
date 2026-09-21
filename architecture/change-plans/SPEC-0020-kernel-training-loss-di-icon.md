# SPEC-0020 pre-code architecture review

Specification: `specs/SPEC-0020-kernel-training-loss-di-icon.md`, revision 2.

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Present selected retained-kernel Training loss | `learning_qualification` | `desktop_adapter` | `studio_application` | Existing immutable `KernelTrainingEvidence.kernel_loss` | Existing controller-owned primitive `QVariantMap` consumed by QML | `studio_application` | Existing selected kernel and evidence map only; no new state | `studio_application -> learning_qualification`, QML -> `StudioController` property | `desktop_adapter -> learning_qualification`, recomputing loss in QML/controller |
| Apply DI application identity | Packaged QML asset | Qt window system | `studio_application` | One static, application-owned DI SVG resource | Existing `QGuiApplication.windowIcon` and QML header image | `studio_application` | Process-wide immutable icon value; no domain state | `studio_application -> desktop_adapter` | Domain modules -> Qt/resource APIs |

## Type Ownership Matrix

| Type | Owner / level | Kind and visibility | Lifetime / mutability | Consumers | Change | ABI / wire / storage impact |
|---|---|---|---|---|---|---|
| `KernelTrainingEvidence` | `learning_qualification` / L1 | Cross-module immutable domain value | Completed Training run / immutable | Learning, application | Existing `kernel_loss` is projected without modification | None |
| `StudioController` | `studio_application` / L0 | Public composition mapping | Application / owner-mutable | QML | Existing summary map gains one primitive display string | Qt-facing map only; no saved schema change |
| DI SVG resource | `desktop_adapter` / L3+ | Static packaged visual asset | Application package / immutable | Qt application and QML header | New resource reuses the existing primary color and exact `DI` text | No ABI, wire, or storage impact |

No domain named type, field, enumeration, callback, event, port, or ownership authority is added or removed.

## State Object Ownership Matrix

| State | Owner | Lifetime | Authority | Impact |
|---|---|---|---|---|
| Selected retained kernel | `studio_application` | Current Replay view | Controller instance only | Existing selection chooses which stored evidence is projected; no new mutable state |
| Application window icon and Windows AppUserModelID | `studio_application` | Process lifetime | `QGuiApplication` and Windows Shell | One immutable resource is assigned before the main window loads, and the stable explicit AppUserModelID is assigned before `QGuiApplication` construction so `pythonw.exe` launches receive an independent taskbar identity |

The manifest continues to declare `state_objects: []`; no mutable file-scope, static, thread-local, external-linkage, or address-passed state is introduced.

## Actual and intended dependency edges

- Actual edges remain `studio_application -> learning_qualification` for reading `KernelTrainingEvidence`, and `studio_application -> desktop_adapter` for Qt/QML presentation.
- Intended edges are identical. QML consumes only the controller's primitive `trainingLoss` string and never imports or recalculates domain loss.
- The packaged SVG remains an adapter presentation resource; no domain module depends on Qt or resource lookup.
- The Windows Shell identity call remains composition-root startup behavior and uses only the Python standard library; it introduces no adapter-to-domain edge.
- No module, port, callback, event, worker channel, persistence schema, or third-party dependency changes.

## Parent mappings and flow impact

- `studio_application` remains the L0 parent mapping Learning-owned evidence to desktop presentation.
- `learning_qualification` remains authoritative for the numeric `kernel_loss`; the application owns only deterministic formatting and `N/A` fallback.
- The `learn-and-qualify` flow, candidate selection, optimization, replay, export, workload units, queues, copies, retries, and asymptotic costs are unchanged.
- Application-icon and AppUserModelID assignment are startup presentation work with bounded constant cost and no runtime scheduling or real-time impact.

## Planned manifest effect

The `studio_application` invariant will state that selected-kernel presentation exposes the stored Kernel Loss without recomputation and uses the packaged DI application icon with a stable explicit Windows AppUserModelID. All ownership, dependency, type, state, mapping, flow, workload, execution, data-access, and microarchitecture declarations remain unchanged.
