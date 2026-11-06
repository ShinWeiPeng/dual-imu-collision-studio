# SPEC-0050 pre-code design: normal training activity coverage

Scope: the confirmed SPEC-0050 r3 and adopted concept preview. Preserve every fitting/qualification numeric rule and explicit annotation. No ADR is accepted by this change.

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Confirmed annotations to Learning intervals | data_workspace | learning_qualification | studio_application | Recording / AnnotationInterval | LearningInterval | studio_application | confirmed workspace, read only | studio_application -> data_workspace; studio_application -> learning_qualification | data_workspace -> learning_qualification; reverse child/parent dependencies |
| Training activity source selection | learning_qualification | studio_application | studio_application | LearningService.training_activity_mask; new call-local Boolean result | derivedNormalIntervals primitive start/end fractions | studio_application | immutable interval input; no shared mutable state | studio_application -> learning_qualification | learning_qualification -> Qt or StudioController |
| Coverage presentation | studio_application | desktop_adapter | studio_application | primitive fractions through existing QML property | existing read-only Normal track | studio_application | confirmed workspace read only | existing composition/desktop binding | QML modifying derived coverage or learning truth |

## Type Ownership Matrix

| Named type | Owner / level | Declaration | Role / visibility | Lifetime / mutability / authority | Consumers / references | ABI, wire, storage impact |
|---|---|---|---|---|---|---|
| Recording, AnnotationInterval, ActivityKind | data_workspace / L1 | domain/data_workspace/model.py | immutable domain values, existing cross-module contracts | confirmed snapshot; owner creates values | existing studio_application consumers; ActivityKind references unchanged | None; no field changes |
| LearningInterval | learning_qualification / L1 | domain/learning/model.py | existing immutable evidence value | one dataset; owner semantics | studio_application parent mapping; no new project-type reference | None |
| LearningService | learning_qualification / L1 | domain/learning/service.py | existing public calculation seam; add pure activity-mask query | call-local newly allocated mask; no retained/shared state | studio_application and existing learning consumers | No serialized format or existing signature changes |
| StudioController | studio_application / L0 | adapters/desktop/controller.py | existing private composition/QML facade | application session; only parent mutates its state | existing desktop binding; Recording/LearningInterval references unchanged | Existing QVariantList shape unchanged |

No new named production type, field, event, callback, port or runtime-state object is introduced. Primitive/external NumPy values need no project DTO.

## State Object Ownership Matrix

| Object | Definition/type | Owner | Lifetime / mutability | Read/write authority | Linkage / leakage / escape |
|---|---|---|---|---|---|
| _confirmed_workspace, _annotations | existing StudioController members / workspace snapshot and annotation mapping | studio_application | session; existing owner-managed edits | parent writes; projection reads only | instance-private; no new escape |
| eligibility mask | LearningService.training_activity_mask local Boolean ndarray | learning_qualification calculation; caller owns returned fresh result | one calculation; mutable caller scratch | only current caller | no global/static/thread-local state; no retained reference |
| eligible_cycle, selected_segments | existing _build_group_evidence scratch arrays | learning_qualification | existing fit calculation | existing calculation only | no new cross-boundary pointer or linkage |

## Actual and intended dependency edges / parent mappings

Unchanged: studio_application -> data_workspace, learning_qualification, desktop_adapter. Both L1 domains remain siblings under studio_application. The parent maps workspace intervals into LearningInterval using one shared private mapper for both LearningDataset construction and UI projection. No sibling direct calls or framework imports enter Learning.

## Functional and algorithm design

Extract the existing activity selection from _build_group_evidence into a pure Learning-owned query: union Cycle-contained Normal/Pick/Put intervals, optionally restrict selected cycles, then subtract Ignore and actual Collision intervals. Fit retains its existing cycle assignment, interval_count, discontinuity, preprocessing and segment construction. UI calls the same query, partitions contiguous true runs separately within each confirmed Cycle, and maps half-open indexes to fractions. It does not claim model-specific FIR/warmup row eligibility.

The original exclusive Normal derivation, its inclusive 150-ms collision-response exclusion, threshold maxima, Qualification activity labels and annotated exports remain unchanged. If an explicit Pick/Put already follows an annotated Collision within its response tail, preserve its existing fit selection; do not invent a new learning exclusion in this display change.

Screening: the visual source-coverage method is deterministic Boolean union/subtraction. Selected: reuse actual training selection. Rejected: recolor exclusive Normal intervals (omits Pick/Put), broaden Normal truth (changes threshold/Qualification), independent QML merging (duplicates model semantics). No new score/model/search algorithm. Existing learning algorithm and its exact output are preserved; this record specifies the visual projection and extraction completely.

Complexity: O(sample_count + covered interval lengths), one Boolean array as already used by fitting; parent computes only the selected recording. No waveform copies or fit/model execution in the property. Keep Cycle boundaries even when adjacent. No scheduling, workload, thread, activation, priority, deadline or platform claim changes; realtime scheduling studies are not triggered.

## Planned validation

- Production LearningService: actual fitting rows and segments remain identical; selected cycles, Ignore/Pick overlap and Collision exclusions hold.
- Production StudioController: display mask equals actual fit activity samples; Pick/Put continuous coverage, Ignore/collision gaps, adjacent Cycle separation, unconfirmed and deselected state, refresh after edit/reconfirm.
- Existing workspace, threshold, annotation export and QML regression tests; targeted real Qt render captured after implementation.
- Single architecture_cli.py design and development gates; generated descriptions only through render.

Design owners, mapping authority and edges are resolved. Pre-code decision: ready for the design gate. Source edits wait for its actual PASS.
