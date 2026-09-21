---
spec_version: 1
spec_id: SPEC-0024
revision: 6
status: implemented
change_set: annotation-identity-reference-recovery
---

# Restore annotation identity allocation after project open

## Problem

Opening a valid project restores persisted annotation identities but leaves the controller's session-local annotation identity counter at its initial value. The next newly created annotation can therefore reuse an existing identity. Duplicate identities make project saving fail and make `Replace Reference` remain disabled even when a complete Cycle is visibly selected. A second selection-state inconsistency can also leave an interval visibly selected after reference activation while the controller's primary selected index has been cleared.

## Solution

Restore a collision-free next annotation identity from the complete reopened project before accepting new annotations. Reference activation shall also clear both controller selection representations so the visible selection and command eligibility remain synchronized.

## User Stories

- As a user reopening an annotation project, I can add annotations and replace the active reference without creating duplicate identities or losing the ability to save.
- As a user selecting a Cycle, the visible selection and the command's actual enabled state are consistent.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | After a project is opened or relinked, every subsequently allocated annotation identity shall be non-empty and unique within its recording. |
| REQ-002 | Existing persisted annotation identities and proposal provenance shall remain unchanged during open. |
| REQ-003 | A newly created annotation after reopen shall not cause project save or reference activation to fail because of a duplicate identity. |
| REQ-004 | After reference activation, the controller shall clear both the primary selected annotation index and the selected-annotation set so QML no longer renders a stale selection. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Correct both reopened-project identity allocation and the stale visual-selection state in the same change set. | The user explicitly chose to fix both. They are adjacent consistency failures in the same annotation/reference workflow, and testing them together prevents the UI from representing command state incorrectly after the identity correction. |

## Discussion Context

### DISC-001: Identity-only fix or combined consistency fix
- **Situation:** Reopening a project leaves the manual annotation identity allocator at its initial value, while reference activation separately clears `_selected_annotation` without clearing `_selected_annotations`.
- **Question:** Should the change set remain limited to identity allocation, or also synchronize visual and primary selection state after reference activation?
- **Options and tradeoffs:** An identity-only correction is smaller but knowingly preserves misleading UI state. A combined correction adds one bounded controller/QML regression test and makes the visible state agree with command eligibility.
- **User answer:** Fix both together.
- **Explicit rationale:** No additional rationale was stated; the answer accepts the recommended combined scope.
- **Resulting impact:** DEC-001 closes OD-001. REQ-004 and AC-003 now require both controller selection representations to clear after successful reference activation.

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | A project containing existing `annotation-N` and non-numeric/proposal identities is reopened; the next created manual annotation receives an identity distinct from every restored identity, and all restored identities remain byte-for-byte unchanged. | Focused controller round-trip regression test. | PASS: open and relink regressions preserve persisted identities and allocate unique later identities. |
| AC-002 | REQ-003 | After reopen and creation of a new interval, selecting a complete Cycle makes `canUseSelectedCycleAsReference` true, reference replacement succeeds, and project save succeeds. | Focused controller integration regression test using a real `.dicsproj` round trip. | PASS: real .dicsproj round trip replaces the reference and saves after a post-open annotation. |
| AC-003 | REQ-004 | After successful reference activation, `selectedAnnotationCount` is zero, no interval reports `selected: true`, and `canUseSelectedCycleAsReference` is false until the user explicitly selects a Cycle again. | Focused controller test plus offscreen QML interaction regression test. | PASS: controller and offscreen QML regressions verify clearing, disabled state, and explicit-reselection re-enablement. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0001 |
| REQ-002 | depends_on | REQ-001 |
| REQ-003 | depends_on | REQ-001 |
| REQ-004 | depends_on | DEC-001 |
| AC-001 | depends_on | REQ-001 |
| AC-001 | depends_on | REQ-002 |
| AC-002 | depends_on | REQ-003 |
| AC-003 | depends_on | REQ-004 |

## Out of Scope

- Regenerating or migrating identities already stored in a valid project.
- Changing the `.dicsproj` schema or annotation identity field.
- Changing Cycle completeness, event cardinality, discontinuity, or reference-template projection rules.
- Selecting a Target Numeric Type.

## Open Decisions

None.

## Routing/Gates

- Risk: R2 governed runtime-state correction because session-owned allocation state and project restore behavior change.
- Required gates: clarification, architecture governance, TDD, and code review.
- Spec review: PASS
- Evidence: 433 tests passed; development architecture gate passed; Standards and Spec code-review axes passed with no remaining findings.

## Revision History

| Revision | Change |
|---|---|
| 1 | Started from the reproduced post-open duplicate annotation identity and disabled Replace Reference behavior. |
| 2 | Selected the combined identity-allocation and visual-selection consistency scope; closed OD-001 with DEC-001. |
| 3 | Reconciled the confirmed scope in a new journal epoch after continuity became unavailable. |
| 4 | Recorded passing acceptance evidence and both passing code-review axes. |
| 5 | Reconciled the completed validation evidence for canonical materialization. |
| 6 | 2026-09-03 | Recorded implementation PASS evidence. |
