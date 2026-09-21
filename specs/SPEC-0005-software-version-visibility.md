---
spec_version: 1
spec_id: SPEC-0005
revision: 2
status: confirmed
change_set: software-version-visibility
---

# Software Version Visibility

## Problem

The package defines version `0.1.0`, but the application does not visibly identify the running software version and exported or persisted artifacts do not identify the producing software version.

## Solution

Use the package version as the single authoritative application version. Show it in the application header, persist it in newly saved project files, and emit it in every generated Profile header. Treat the project field as optional so existing projects remain compatible.

## User Stories

- As a user, I can identify the running software version.
- As a user, I can identify which software version saved a project or generated a Profile header.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | The application shall expose one software version from the package version source; the current value is `0.1.0`. |
| REQ-002 | The application header shall display the authoritative software version. |
| REQ-003 | Newly saved project files shall record the authoritative software version, while project files without that optional field shall remain valid and open normally. |
| REQ-004 | Every generated C99-compatible or C++17 Profile header shall contain the authoritative software version without changing the Profile schema version. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Show and record the version in the application header, project file, and generated Profile headers. | The user selected option 1 for complete traceability. |
| DEC-002 | Keep project-schema and Profile-schema versions distinct from the software version. | Software release identity must not imply a serialization contract change. |
| DEC-003 | Make the project software-version field optional on read and present on every new save. | Existing projects must remain compatible while new artifacts gain provenance. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | QML displays exactly the package version exposed by the controller. | Controller and QML smoke tests. | Pending |
| AC-002 | REQ-001, REQ-003 | A new project save contains `software_version: 0.1.0`, and a project without that field validates and opens. | Project persistence tests. | Pending |
| AC-003 | REQ-001, REQ-004 | Both generated header formats contain the same software version as the package. | Profile export and compile-smoke tests. | Pending |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-002 | depends_on | REQ-001 |
| REQ-003 | depends_on | REQ-001 |
| REQ-004 | depends_on | REQ-001 |
| REQ-002 | depends_on | DEC-001 |
| REQ-003 | depends_on | DEC-003 |
| REQ-004 | depends_on | DEC-002 |
| AC-001 | depends_on | REQ-001 |
| AC-001 | depends_on | REQ-002 |
| AC-002 | depends_on | REQ-003 |
| AC-003 | depends_on | REQ-004 |

## Discussion Context

### DISC-001: Version scope
- **Situation:** Package version `0.1.0` exists but is not user-visible or attached to produced artifacts.
- **Question:** Where shall the software version appear?
- **Options and tradeoffs:** UI only is smallest but lacks artifact provenance; UI plus Profile header omits project provenance; UI plus project and Profile header provides complete traceability with a wider but compatible change.
- **User answer:** Option 1: application UI, project file, and Profile header.
- **Explicit rationale:** The user selected the complete traceability scope; no additional rationale was stated.
- **Resulting impact:** DEC-001 through DEC-003 and REQ-001 through REQ-004.

## Out of Scope

- Automatic update checks.
- Release packaging or installers.
- Changing project-schema or Profile-schema versions.
- Rejecting or labeling projects created by another software version.

## Open Decisions

None.

## Routing/Gates

- Risk: R1 standard application metadata change.
- Required gates: TDD and code review.

## Revision History

| Revision | Change |
|---|---|
| 1 | Started software-version scope discussion. |
| 2 | Selected complete UI, project, and Profile-header version traceability with backward-compatible project loading. |
