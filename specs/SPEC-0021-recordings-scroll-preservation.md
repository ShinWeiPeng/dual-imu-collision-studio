---
spec_version: 1
spec_id: SPEC-0021
revision: 3
status: implemented
change_set: recordings-scroll-preservation
---

# Preserve Recordings scroll after Mapping Wizard

## Problem

Completing Mapping Wizard updates the selected recording and emits the controller's shared state notification. Because the `Recordings` ListView binds directly to a newly materialized `QVariantList`, the model is rebuilt and the viewport jumps from its current position to the top.

## Solution

Preserve the `Recordings` ListView's pre-refresh pixel scroll position across mapping-driven model refreshes. Restore the captured `contentY` after the refreshed model has completed layout, clamping only when the new legal scroll range is smaller.

## User Stories

- As a user mapping many recordings, I can finish one recording's wizard and continue from the same place in the Recordings list instead of being returned to the top.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Completing Mapping Wizard for an existing recording shall preserve the Recordings ListView's pre-refresh pixel `contentY` instead of resetting it to the top. |
| REQ-002 | Restoration shall clamp the captured position into the refreshed ListView's legal scroll range when its content or viewport bounds change. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Preserve the pre-refresh pixel `contentY`; clamp only when it exceeds the refreshed legal range. | The user selected option 1 because it retains the exact viewport they were using and introduces no automatic repositioning around the selected recording. |

## Discussion Context

### DISC-001: Post-Wizard viewport policy
- **Situation:** Mapping confirmation rebuilds the QML ListView model and resets `contentY` from the user's current position to zero. The selected recording and total content height remain unchanged in the reproduced case.
- **Question:** Which viewport position should be retained after Mapping Wizard completes?
- **Options and tradeoffs:** Preserving pixel `contentY` keeps the exact viewport and clamps only at new bounds; anchoring the selected recording tolerates layout changes but may move the viewport; automatically revealing the completed recording provides confirmation but deliberately overrides the user's position.
- **User answer:** Option 1: preserve the original scroll position.
- **Explicit rationale:** No additional rationale was stated; the selected option directly addresses the reported jump-to-top behavior with the least automatic movement.
- **Resulting impact:** DEC-001 closes OD-001. REQ-001, REQ-002, AC-001, and AC-002 require exact pixel-position restoration with legal-range clamping.

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | With a scrollable recordings list positioned away from the top, confirming mapping preserves the pre-refresh `contentY` within a sub-pixel tolerance after model layout settles. | Offscreen QML interaction regression test that exercises `StudioController.confirmMapping`. | PASS: the offscreen Wizard lifecycle regression reproduced the former 500-to-0 reset and now preserves contentY 500 within sub-pixel tolerance; the complete QML smoke suite passed 28/28. |
| AC-002 | REQ-002 | If refreshed content makes the captured position invalid, restoration settles at the nearest legal scroll bound and does not overscroll. | Offscreen QML boundary regression test. | PASS: the resized-viewport regression restores to the refreshed legal maximum with no overscroll; the architecture development gate passed with exit 0. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0001 |
| REQ-001 | depends_on | DEC-001 |
| REQ-002 | depends_on | DEC-001 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |

## Out of Scope

- Changing mapping validation, imported recording data, or selected-recording semantics.
- Redesigning the Recordings card or other scrollable views.
- Changing project persistence or architecture boundaries.

## Open Decisions

None.

## Routing/Gates

- Risk: R1 standard QML interaction correction.
- Required gates: TDD and code review.
- Product implementation was authorized by the user's exact `開始執行`; the complete 28-test QML smoke suite and architecture development gate passed.
- Standards review: PASS.
- Spec review: PASS.
- The broader suite stopped at 20 unrelated Windows atomic-output temp-path failures after 256 passes; isolated reruns fail without involving this QML/manifest change.

## Revision History

| Revision | Change |
|---|---|
| 1 | Started the recordings-scroll preservation change set from the reproduced Wizard-completion reset. |
| 2 | Selected exact pixel `contentY` preservation with legal-range clamping and closed OD-001. |
| 3 | 2026-09-03 | Recorded implementation PASS evidence. |
