# SPEC-0025 pre-code ownership plan

## Intended Implementation Boundaries

| Interaction | Producer | Consumer | Parent / mapping owner | Contracts / state | Allowed / forbidden edges |
|---|---|---|---|---|---|
| Capture model settings | desktop_adapter | learning_qualification | studio_application | UI selections to immutable LearningSettings | Parent maps; QML has no trainer state |
| Fit and replay | learning_qualification | history_worker_adapter | studio_application | FoldJob/RecordingJob and immutable results | Adapter implements Learning port; no domain-to-adapter import |
| Save and reopen | learning_qualification | project_session | studio_application | Frozen model to versioned project data | Parent maps sibling types; no direct sibling dependency |
| Profile presentation/export guard | learning_qualification | profile_export | studio_application | SemanticProfile and family identity | Parent maps; MLP cannot be rendered as FIR |

| Type / state | Owner | Lifetime / references | Storage / ABI impact |
|---|---|---|---|
| MLP settings, frozen model and parameter identity | learning_qualification | Immutable domain values; workers receive snapshots | Extend typed project model mapping; no device ABI |
| Adam weights/moments/checkpoint | learning_qualification | Fit-local mutable state, never shared between jobs | Not persisted as executable objects |
| Dynamic layer checkbox presentation | desktop_adapter | Bound to controller settings | Persist only mapped domain values |
| Family run evidence and active selections | studio_application | Session owner, maps Learning-owned snapshots | Independent family provenance in project data |
| Serialized layer arrays | project_session | Validated inert project payload | Versioned and shape/finite validated |

Existing L0 studio_application remains the parent of Learning, project_session and profile_export. Preserve the existing dependency graph; add private Learning algorithm implementation and declarations under its existing owner. No new production module, external trainer backend or device runtime is required. Proposed architecture manifest changes and tests must pass the architecture CLI design/development/release gates; no ADR is accepted by this specification.


New type: FrozenMlpModel, owned by learning_qualification, referenced by fold/candidate/recording-job snapshots and mapped by studio_application to profile_export/project_session. Mutable Adam arrays stay fit-local; no new global state or dependency edges. Native/foreign ABI unchanged; inert layer-array storage is added.
