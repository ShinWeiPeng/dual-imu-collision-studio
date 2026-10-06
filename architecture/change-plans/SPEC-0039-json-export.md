# SPEC-0039 desktop JSON export design

## Boundary Design Table
| Boundary | Owner | Contract and authority |
|---|---|---|
| Encode qualified immutable profile | profile_export (L1) | ProfileExportService validates FIR, selected precision, dimensions, non-finite values, single-sample confirmation and explicit input units; returns JSON text. No filesystem or Qt. |
| UI selection and save coordination | studio_application (L0) | StudioController maps selected SemanticProfile into encoder and dispatches saved text to desktop_adapter. Revalidate active qualified result at save. |
| Save bytes | desktop_adapter (L3+) | AtomicProfileWriter writes UTF-8 to sibling temporary file, flushes, commits atomically; never replace without explicit confirmation. |
| Export dialogs | desktop_adapter (L3+) | Main.qml edits model name independently of filename, queues selected models, shows validation and operation errors. |

## Type Ownership Matrix
| Existing type | Owner | Lifetime and authority | Change |
|---|---|---|---|
| SemanticProfile | profile_export | Frozen qualified result; no export-time mutation | No fields or precision changes. |
| ProfileExportService | profile_export | Stateless public semantic service | Add JSON validation, stable naming and rendering. |
| ProfileCommandPort | profile_export | Demand-owned pure command | Add JSON render signature using existing SemanticProfile and text values. |
| StudioController | studio_application | Session owner; coordinates sibling boundaries | Add export queries/slots without exposing private model arrays. |
| AtomicProfileWriter | desktop_adapter | Stateless filesystem binding | Add explicitly approved JSON save with filename checks and temporary-file cleanup. |

## State Object Ownership Matrix
| State | Owner | Lifetime | Read/write authority |
|---|---|---|---|
| Existing profiles and selected IDs | studio_application | Session; invalidated by workspace/result changes | StudioController only; JSON save rechecks. |
| JSON dialog current model and batch queue | desktop_adapter | One QML export interaction | Main.qml only; cancellation ends the queue; no domain mutation. |
| JSON save temporary file | desktop_adapter | One save call | AtomicProfileWriter only, removed on failure. |

## Dependencies and parent mappings
Actual and intended edges remain studio_application -> profile_export and studio_application -> desktop_adapter. No new cross-domain edge. L0 maps frozen profile to JSON text; L3+ alone accesses files and Qt. profile_export remains child of studio_application; desktop_adapter keeps existing technical-adapter mapping. No new named Python type, thread, callback bus, or scheduling claim.

## Validation seams
REQ/AC-004,005,022,025,026,027,041,044,045,058,091,095: codec fixtures cover schema, independent files/names, qualification/family, precision and signed zero, shape/finite/rate/scale checks, single-sample rule and no capacity restriction. Controller fixtures cover current-result recheck, errors and selected profiles. Filesystem tests cover cancellation/no overwrite, explicit overwrite, atomic failure cleanup. QML smoke tests cover dialog load. Firmware/target criteria remain pending and are not asserted by host tests.

## Confirmed input fact
The current mapping stores time units but no acceleration units. The JSON input unit must come from confirmed source-data units; do not assume g or silently convert model parameters. The user explicitly confirmed Internal/External XYZ are in g in the current task. The controller supplies g without conversion; the codec accepts an explicit unit and rejects missing units.

## Desktop-only kernel-list revision (2026-09-22)
Boundary design: studio_application exposes computed qualified JSON rows and prepares a single kernel by stable ID; desktop_adapter renders four columns and dispatches that row's export. profile_export serialization and atomic writer boundaries remain unchanged.
Type ownership: existing StudioController (studio_application), SemanticProfile (profile_export), and QML components (desktop_adapter); no new named type or port.
State ownership: existing profiles remain session-owned by StudioController; existing QML JSON queue/current model/error/target remain interaction-owned by Main.qml. The row query is derived, not stored; preparing/exporting never changes selected kernel IDs.
Actual and intended dependencies and parent mappings remain unchanged. Validate current availability before preparing and before writing. Retained passing speeds supply exact qualified coverage, with profile range fallback after reopen. No firmware workload or runtime claim.
Acceptance: REQ/AC-097/098 controller and QML checks, plus existing desktop JSON regressions. Preserve repository formatter and current file newline styles.
