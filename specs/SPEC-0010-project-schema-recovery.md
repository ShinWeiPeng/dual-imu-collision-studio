---
spec_version: 1
spec_id: SPEC-0010
revision: 2
status: confirmed
change_set: project-schema-recovery
---
# Project schema recovery

## Problem
The supplied test.dicsproj uses schema 1 and reproduces unsupported project schema version in the current schema-2 loader. Its eight source files match stored hashes; 96 annotations and two templates exist; no Learning results are saved. Current import needs zero inserted samples and preserves all row counts. The original project is unchanged.

## Solution
Convert this file only into same-directory test-v2.dicsproj. Set schema_version=2, algorithm_contract=dual-imu-collision-profile/2, result_contract=semantic-profile/2 and add interpolated_indices=[] to each recording. Preserve all other project values, source references, mappings, conditions, annotation indexes, templates, confirmation states and selections. No general legacy compatibility change.

## User Stories
As the user, I want to open my existing annotated project in the current application while retaining the original and existing work.

## Requirements
| ID | Requirement |
|---|---|
| REQ-001 | Convert only the supplied test.dicsproj to a new same-directory test-v2.dicsproj using the three version fields and eight empty interpolation fields above. Preserve every other project value and all sources, 96 annotations and two templates. Do not modify the original, overwrite an existing destination, change application compatibility or fabricate results. Validate the actual saved file through the current loading path. Stop if source identities, the original file, zero-interpolation assumption, destination availability or validation differ from the inspected conditions. |

## Decisions
| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Perform the one-file conversion into test-v2.dicsproj, retaining the original and existing mappings, annotations and templates; do not change Open Project compatibility logic. | The user accepted the explicitly proposed single-file scope. The inspected file has no interpolation-induced row changes and no saved Learning results. |

## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | The saved new file validates and opens using the current controller path. Eight recordings, 96 annotations, two templates and all source/mapping/condition/index/confirmation/selection values remain identical. Only the three version fields and eight empty interpolation fields differ; no results are added. Original-project and source hashes remain unchanged and no existing destination is overwritten. | Compare parsed documents excluding exactly the allowed changed fields; verify original/source hashes; read the new artifact and exercise actual Open Project validation and restoration. | Preflight only: in-memory converted ProjectDocument validation and all eight annotation sets passed; destination absent. Actual write and reopen pending authorization. |

## Relationships
- depends_on: SPEC-0002, SPEC-0009
- refines: none
- supersedes: none
- conflicts_with: none
Separate recovery request; SPEC-0009 analytical rules and its original change-set scope remain unchanged.

## Out of Scope
General legacy compatibility, other projects, source recordings, application source/tests/architecture, model selection, FIR/threshold policies, annotation remapping and saved Learning-result migration.

## Open Decisions
None.

## Routing/Gates
ask-matt -> grilling -> spec-governance. Materialize the confirmed contract, then require exact 開始執行 before the external file action. Desktop writes additionally require native filesystem approval. Verify the actual saved artifact and loader; preflight is not delivery evidence.

## Revision History
| Revision | Change |
|---|---|
| 1 | Recorded the verified schema failure and opened OD-001. |
| 2 | Resolved OD-001 through DEC-001 and clarified REQ-001/AC-001; recorded read-only preflight. |

## Discussion Context
### DISC-001: Recovery scope
- **Situation:** The inspected schema-1 project cannot open under schema 2, but source hashes and row counts match and no interpolation is needed.
- **Question:** Convert only this project into a separate test-v2.dicsproj while retaining the original and avoiding general compatibility changes?
- **Options and tradeoffs:** Single-file conversion preserves this known project's work with bounded changes but does not support other old files automatically. General compatibility changes application loading and requires more migration rules. The single-file approach was recommended for this inspected no-interpolation/no-results file.
- **User answer:** 可以
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-001 confirms REQ-001 and AC-001; OD-001 is resolved. Actual file creation awaits execution and filesystem authorization.
