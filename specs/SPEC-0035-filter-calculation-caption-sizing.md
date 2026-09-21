---
spec_version: 1
spec_id: SPEC-0035
revision: 3
status: implemented
change_set: filter-calculation-caption-sizing
---

# Filter calculation wording and complete action captions

## Problem

The user reports that Preview filter order is misleading for an action that calculates the filter design, and supplies a screenshot where its caption is truncated to Preview filter ord.... The shared slot currently uses independent TextMetrics and only a preferred width, rather than the control's actual content size and a minimum width.

## Solution

Rename the first action Calculate filter. Update the missing-adoption warning to Calculate the filter and adopt the design before continuing. Measure the slot from the actual button/label implicit content plus padding, set adequate minimum and preferred sizes, and keep the full captions visible at normal and enlarged font/display scales. Preserve the existing shared slot, explicit calculation then adoption, adopted Label, invalidation and Next validation semantics. Apply to both IMUs.

## User Stories

- As a user, I see that the first action calculates the filter.
- As a user, I can read the complete action caption without ellipsis or clipping.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | The first-stage action shall read Calculate filter, and missing-adoption feedback shall use consistent calculation wording. |
| REQ-002 | Size this shared action/status slot using actual control content and padding, with minimum width and height preventing clipping or ellipsis of Calculate filter, Adopt design and Design adopted at the existing supported window sizes and normal/enlarged font scales. |
| REQ-003 | Preserve SPEC-0034 lifecycle, per-sensor independence, explicit adoption, edit invalidation, error retry, and clickable Next validation. |

## Decisions

| ID | Decision |
|---|---|
| DEC-001 | Use Calculate filter as the concise English equivalent of the user's requested calculation action. |
| DEC-002 | Derive sizing from actual button/label content and padding instead of separately estimated text width; fix only this slot. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-003 | Both IMUs show Calculate filter initially and after edits, Adopt design after successful calculation, and a genuine Design adopted Label after adoption; Next uses the revised warning without advancing beforehand. | Update existing lifecycle interaction tests; inspect all user-visible strings. | PASS: both IMU lifecycle and Next wording interaction checks; architecture/change-plans/SPEC-0035-verification.md. |
| AC-002 | REQ-002 | All three captions fit actual content bounds without elision or clipping at 100%, 125%, 150% and 200% display scales, with normal and enlarged fonts; scroll-reachable controls remain inside the wizard. | Parameterized Qt content-bound assertions and rendered screenshots, including the existing 740x430 fixture. | PASS: 8 scale/font processes check all 48 sensor/stage combinations, actual text truncation and bounds, rendered images inspected; architecture/change-plans/SPEC-0035-verification.md. |
| AC-003 | REQ-003 | Existing mapping/filter and wheel interaction checks remain passing. | Focused mapping/QML regressions. | PASS: 57 focused/regression tests; architecture design/development/release and formatter checks; architecture/change-plans/SPEC-0035-verification.md. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-003 | refines | SPEC-0034 |
| REQ-002 | depends_on | DEC-002 |

## Out of Scope

Filter mathematics, backend method renaming, persistence, other application buttons, new modules/types/state objects and architecture boundary changes.

## Open Decisions

None.

## Discussion Context

### DISC-001: Calculation wording and visible captions
- **Situation:** The user sees a truncated Preview filter order caption after SPEC-0034 implementation.
- **Question:** Which action wording and sizing behavior should replace the current presentation?
- **Options and tradeoffs:** Calculate filter expresses the calculation action; natural control sizing consumes sufficient space to preserve the full label rather than truncating it.
- **User answer:** `Preview filter order` 。我認為不該叫preview。應該叫計算filter之類的。還有按鈕框太小了。要所有字都看得到
- **Explicit rationale:** The action should be described as calculation, and all text must remain readable.
- **Resulting impact:** REQ-001 through REQ-003 and DEC-001/002 define the correction; no new explicit execution phrase has been supplied for this follow-up.

## Routing/Gates

Spec review: PASS
Standards review: PASS
Implementation completed under the current user execution instruction. Final evidence: architecture/change-plans/SPEC-0035-verification.md. No requirements or decisions changed during execution.

Follow-up to implemented SPEC-0034, which remains immutable. Before implementation verify this canonical specification and execution admission, preserve current QML style, inspect architecture ownership, and run applicable architecture gates through architecture_cli.py. No algorithm or cross-module architecture change is intended. Use existing Qt mouse/wheel/lifecycle seams and content-bound checks for the reported sizing defect. This file records the reviewable requested scope; it does not claim the correction is implemented or validated.

## Revision History

- Revision 1: User requests calculation wording and fully visible action captions.
| 3 | 2026-09-13 | Recorded implementation PASS evidence. |
