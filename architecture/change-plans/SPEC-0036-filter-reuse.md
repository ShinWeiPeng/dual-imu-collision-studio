# SPEC-0036 pre-source design

## Boundary Design Table
| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Edit/add filter | SingleImuFilters | SensorMapping | desktop_adapter | edited + stageSpecifications values | invalidate/preview | desktop_adapter | editor stages/templateIndex; sensor preview/adoption | Existing editor to pane | Shared mutable stages across IMUs |
| Calculate | desktop_adapter | learning_qualification | studio_application | primitive stage draft | FilterStageSpec | existing controller | immutable request/result | application to learning | Learning to QML |
| Save/reopen | learning_qualification | project_session | studio_application | immutable SingleImuSettings | inert project data | existing parent mappings | existing project state | existing parent orchestration | sibling direct dependencies |

## Type Ownership Matrix
| Type/fields | Owner/level | Declaration | Role/visibility/lifetime | Mutation authority/consumers | References | ABI/wire/storage |
|---|---|---|---|---|---|---|
| FilterStageSpec: kind, passband_hz, stopband_hz, passband_attenuation_ratio, stopband_amplitude_ratio | learning_qualification L1 | preprocessing.py FilterStageSpec | immutable public domain configuration, captured design lifetime | none; Learning/application/history worker | none | same fields; kind also accepts lowpass |
| FilterDesign: specification, sample_rate_hz, order, sos, designer_version | learning_qualification L1 | preprocessing.py FilterDesign | immutable public result, captured model lifetime | none; same consumers | FilterStageSpec | same shape and coefficient persistence; lowpass order is N |
| SingleImuSettings: sensor, source_mode, filters, warmup_samples | learning_qualification L1 | preprocessing.py SingleImuSettings | unchanged immutable configuration | none; same consumers | FilterDesign | unchanged |

## State Object Ownership Matrix
| State | Owner | Read/write authority | Lifetime/reset | Cross-boundary access |
|---|---|---|---|---|
| templateIndex (new int) | desktop_adapter, private SingleImuFilters | editor only | -1 empty; focus/edit/select records index; add selects new stage; load/delete fallback last; move adjusts identity | none |
| stages (existing QML ListModel) | desktop_adapter, per editor | editor only | load clears/reloads; add copies primitive roles | output value snapshots only |
| filterPreview/adoptedFilter (existing) | desktop_adapter, per SensorMapping | pane only | edited invalidates | immutable mapping result |

## Dependencies and parents
Actual and intended edges are identical: desktop adapter gesture -> existing application/controller mapping -> Learning design; application maps Learning settings into project-session storage. No new module, type, port, event, worker or dependency. New source set classification is not required. New selection state is UI-local, with no shared settings registry.

## Algorithm and validation
Extend existing ALG-0009 Butterworth design to lowpass via existing buttord/butter SOS path. Single-edge order N; band transform 2N. Four filter kinds retain edge-response validation. UI type inference compares finite positive input edges and reports equal/incomplete input as invalid. Parameter reuse is value copying rather than signal processing, with no numerical or performance claim. Existing Windows best-effort execution and allocation remain unchanged.
Seams approved in SPEC-0036: Qt gestures/editor snapshots, public design_filter and preprocessing/settings roundtrip, controller project save/reopen and filter adoption. Ruff 0.16.6 is the existing formatter; Python original check passed. Preserve existing compact QML style; no whole-program formatting.
Source edits wait for planned-manifest design PASS. Both existing ADRs remain proposed; baseline stays empty. Full manifest/adoption/baseline and generated guide/ADRs inspected in this task. No ownership or authority is unresolved.
