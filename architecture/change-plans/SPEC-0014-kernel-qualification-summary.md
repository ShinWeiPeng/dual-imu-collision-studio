# SPEC-0014 pre-code architecture review

Specification: `specs/SPEC-0014-kernel-qualification-summary.md`, revision 3.

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Present selected-kernel speed scope and per-recording Qualification evidence | `learning_qualification` | `desktop_adapter` | `studio_application` | Existing `QualifiedCandidate` and `RecordingQualification` values | Existing controller-owned primitive QML maps | `studio_application` | Existing selected candidate only; no new state | `studio_application->learning_qualification`, `studio_application->desktop_adapter` | `learning_qualification->desktop_adapter`, `desktop_adapter->learning_qualification` |
| Invoke visible project actions | `desktop_adapter` | `studio_application` | `studio_application` | Existing QML commands | Existing `StudioController` slots | `studio_application` | Existing project and dirty state | QML -> `StudioController` | QML -> project storage, removal of the controller's non-UI reset capability |

## Type Ownership Matrix

| Type | Owner / level | Kind and visibility | Lifetime / mutability | Consumers | Change | ABI / wire / storage impact |
|---|---|---|---|---|---|---|
| `RecordingQualification` | `learning_qualification` / L1 | Cross-module domain value | Completed replay / immutable | Learning, application | Status semantics now make absent Normal/Pick/Put classes neutral and reserve Coverage Gap for no Collision evidence; fields are unchanged | None; Python in-process value and project/Profile schemas unchanged |
| `QualifiedCandidate` | `learning_qualification` / L1 | Cross-module domain value | Retained result / immutable | Learning, application | Existing `conditions` and `training_speeds` provide supplied and active speed sets | None |
| `SemanticProfile` | `profile_export` / L1 | Cross-module domain value | Saved/restored Profile / immutable | Profile, project, application | Existing coverage and Training range provide restored supplied and active speed sets | None |
| `StudioController` | `studio_application` / L0 | Public composition mapping | Application / owner-mutable | QML | Projection text/status changes; `newProject()` remains public | Qt-facing behavior only; no saved schema change |

No named type, field, enumeration, public symbol, callback, event, port, or ownership authority is added or removed.

## State Object Ownership Matrix

| State | Owner | Lifetime | Authority | Impact |
|---|---|---|---|---|
| Selected retained candidate and recording | `studio_application` | Current Replay view | Controller instance only | Read through existing immutable snapshots; no new mutable state |
| Learning Qualification replay locals | `learning_qualification` | One recording replay | Function-local coordinator only | Predicate changes only; no address or mutable state crosses a boundary |

The manifest continues to declare `state_objects: []`; no mutable file-scope, static, thread-local, external-linkage, or address-passed state is introduced.

## Dependency, parent, Flow, and cost review

- Actual and intended dependencies remain `studio_application -> learning_qualification`, `studio_application -> desktop_adapter`, and the existing QML-to-controller framework binding. Sibling domain imports remain forbidden.
- `learning_qualification` owns PASS/FAIL/COVERAGE_GAP authority. `studio_application` owns domain-to-QML mapping. `desktop_adapter` renders the supplied primitive values. These parent mappings are unchanged.
- Candidate A, the former all-four-class completeness gate, is rejected because it contradicts confirmed SPEC-0014 when Normal/Pick/Put classes are absent. Candidate B, selected, evaluates false events only for present non-Collision activity and requires one or more Collision intervals all detected within the inclusive 150 ms onset deadline. Candidate C, treating missing Collision evidence as PASS, is rejected because it removes the required positive collision denominator.
- The `learn-and-qualify` Flow keeps the same steps, units, queues, copies, retry behavior, and asymptotic cost. The predicate remains constant-time after existing counts are produced. No hard/soft real-time workload, scheduling candidate, benchmark, ABI, wire format, or storage representation is changed.
- Removing the QML New Project entry point does not remove `StudioController.newProject()` or alter Open/Save/Save As and dirty open/close flows.

