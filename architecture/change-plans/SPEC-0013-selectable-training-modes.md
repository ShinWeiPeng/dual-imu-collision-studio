# SPEC-0013 implementation authoring record

Specification: `specs/SPEC-0013-selectable-training-modes.md`, revision 7.
User execution authorization: current task, 2026-08-31, exact `開始執行`.
This record does not accept ADR-0001/0002 or make a new runtime-performance claim.

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Capture active Training settings | studio_application | learning_qualification | studio_application | controller-owned editable values | LearningRequest and LearningSettings | studio_application | private next-run settings snapshot | application -> learning | learning -> Qt/controller |
| Save/open editable settings and immutable run provenance | learning_qualification | project_session | studio_application | LearningSettings and RunProvenance | ProjectDocument | studio_application | immutable values only | application -> learning/project | learning -> project; project -> learning |
| Evaluate fixed or optimized parameter folds | learning_qualification | history_worker_adapter | studio_application | FoldJob | LearningExecutionPort | studio_application | immutable dataset, fold plan and settings | adapter -> learning contracts | learning -> multiprocessing bindings |

## Type Ownership Matrix

| Type | Owner / level | Declaration | Semantic kind / visibility | Lifetime / mutability | Authority and consumers | Field roles | Compatibility consequences |
|---|---|---|---|---|---|---|---|
| TrainingMode | learning_qualification / L1 | domain/learning/model.py | domain value / cross-module | process/run value / immutable | no mutation; Learning, application and worker adapter consume it | policy identity for fixed-grid or optimized dispatch | New Python enum; serialized by value. No native ABI, Replay CSV, Model TXT or Profile Header change. |
| LearningSettings | learning_qualification / L1 | domain/learning/model.py | domain value / cross-module | next-run or captured-run lifetime / immutable | constructed by Learning or application; Learning, application and worker adapter consume it | mode and fixed selections are policy/configuration; existing CV/search fields retain their roles | Adds optional project fields with explicit legacy defaults; positional order of existing fields is preserved. |
| LearningRequest | learning_qualification / L1 | domain/learning/model.py | command / cross-module | one run / immutable | application constructs; Learning consumes | workspace is domain value, numeric type and settings are policy | Existing command gains no new top-level field; settings carries mode-specific values. |
| LearningLogEvidence | learning_qualification / L1 | domain/learning/model.py | domain value / cross-module | one progress observation / immutable | Learning constructs; application displays | fixed-grid evaluated/rejected disposition is domain evidence | Adds a bounded UI-only evidence kind; project and export schemas remain unchanged. |

Every governed field has one owner. No framework handle, storage representation or
mutable runtime object enters an L1 public type. Project JSON conversion remains an
application-owned mapping rather than a field representation inside Learning.

## State Object Ownership Matrix

| State | Definition/type | Owner / lifetime | Read authority | Write authority | Storage / leakage / pointer escape |
|---|---|---|---|---|---|
| Editable next-run settings | StudioController `_learning_settings`: LearningSettings | studio_application / application session | controller and QML projection | controller only by immutable replacement | instance field; only immutable snapshots cross boundaries; no pointer escape |
| Captured run settings | LearningRequest / RunProvenance LearningSettings | learning_qualification / one run and retained result | Learning, application presentation and persistence mapper | constructed once; no mutation | immutable value; serialized copy only |
| Parameter cache and search frontier | function-local dictionaries/sets | learning_qualification / one fallback round | coordinator | coordinator only | local storage; immutable jobs/results cross the execution port |
| Process and IPC bindings | adapter-private worker state | history_worker_adapter / one batch | adapter | adapter only | never exposed through Learning contracts |

No mutable file-scope, static-storage, thread-local, external-linkage or address-passed
state is added. The manifest therefore retains an empty `state_objects` catalog.

## Dependencies, parents and mappings

Actual and intended edges remain `studio_application -> learning_qualification`,
`studio_application -> project_session`, `studio_application -> desktop_adapter`, and
`history_worker_adapter -> learning_qualification` demand contracts. All L1 modules
remain children of `studio_application`; L3 adapters remain unparented technical
implementations. The new `learning-settings-to-project` mapping is parent-owned and
forbids direct Learning/project sibling dependencies. There is no new Port, event sink,
callback, Task, process, Queue, channel or execution mapping.

## Algorithm and Flow review

As-is optimized candidate generation builds the existing coarse grid, evaluates all N
folds, follows complete fine-search paths, retains minimum four-decimal half-up parameter
ties, applies Validation allowance and fold Kernel Loss selection, then qualifies original
fold kernels. The selected change preserves that route at the public service seam.

Fixed-grid candidate generation maps the checked History values to effective tap counts,
preserves ordered aliases when sample-rate rounding collides, takes the Cartesian product
with checked Ridge alphas and fixes Robust K to zero. Every effective point uses the same
fold plan and aggregate/select/qualify functions. Nonwinning fixed points publish an
explicit CV-rejected disposition; only minimum rounded Loss ties continue, exactly as the
shared pipeline requires.

Alternative A was a separate informational-only CV plus final all-data fit. It was
superseded by DEC-069 because it duplicates model-selection semantics. Alternative B was
to skip CV in fixed mode; it was rejected because it removes comparable Validation
evidence. The selected shared pipeline concentrates the difference at one Learning-owned
candidate-source seam.

For selected effective History count H, alpha count A and fold count N, fixed fitting work
is exactly `H*A*N` fold jobs before unchanged detector Qualification. The bounded maximum
is `6*5*N`, less than or equal to the existing optimized coarse frontier and without fine
neighbors. Dataset, FIR matrix and worker memory behavior is unchanged. This best-effort
Flow adds no deadline, worker, copy, allocation, Queue, cache, branch/SIMD or platform
claim; the existing runtime evidence obligations remain. Assurance is estimated for cost
and validated only by functional tests until the existing Windows validation profile is
run.

## Validation seams and order

The pre-agreed public seams are the SPEC-0013 acceptance methods: LearningSettings and
LearningService candidate/evaluation APIs; controller QML properties, setting commands,
readiness and captured LearningRequest; ProjectSessionService plus save/open round-trip;
and existing optimized run/export regression tests. Red/green slices are settings and
fixed candidate planning, fixed fold selection/dispatch, controller persistence/readiness,
then QML visibility. Architecture render/gate and the full test suite close the change.

