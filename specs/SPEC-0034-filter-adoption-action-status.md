---
spec_version: 1
spec_id: SPEC-0034
revision: 6
status: implemented
change_set: filter-adoption-action-status
---

# Filter adoption action and status separation

## Problem

SensorMapping.qml:119 changes the Adopt design button into Design adopted after adoption, while its enabled binding still depends only on preview success. Action and status are conflated. tests/test_sensor_mapping_scroll.py:89 currently asserts that wording change.

## Solution

Use a single stable presentation slot shared by one action button and a non-interactive Label. Before successful preview, the button reads Preview filter order and performs preview. After successful preview, that same button reads Adopt design and performs adoption. After adoption, replace the button with a true Design adopted Label in the same slot. Derive presentation from existing adoptedFilter and filterPreview; introduce no stored status flag. Apply through shared SensorMapping to both IMUs. The newer DEC-004 supersedes DEC-001 and DEC-003; those rows are retained only as decision history.

| Existing condition | Shared slot | Result of activation |
|---|---|---|
| Initial or relevant input edited | Preview filter order button | Successful preview changes it to Adopt design |
| Successful preview, not adopted | Adopt design button | Stores settings and replaces button with Design adopted Label |
| Adopted, including settings loaded from an existing mapping | Design adopted Label | No action, no button styling or keyboard activation |
| Preview fails | Preview filter order button | Error remains visible; retry is allowed |

Adoption takes precedence over preview presence when deriving the slot content. Any edit that affects the design (filter stages, their order or parameters, warmup, source selection, or relevant time/sample settings) invalidates preview and adoption and returns the slot to Preview filter order. A failed preview never advances to adoption. Keep preview results visible after adoption until invalidated. A single click executes only the current action, never preview and adoption together. Keep the slot position and minimum height stable across transitions. Hide the slot when software filtering is disabled.

Next remains clickable. When software filtering is enabled but the current design has not been adopted, Next must not advance or alter inputs, and must display the existing wizard validation feedback: Preview filter order and adopt the design before continuing. Valid adopted settings satisfy this filter prerequisite; other validation still applies. Raw-only and already-filtered modes retain their existing rules and do not require adoption. Preserve existing validation priority when other input errors coexist.

## User Stories

- As a user mapping either IMU, I can distinguish the available adoption action from the current design status.
- As a user editing a filter, I can see that the changed design needs preview and adoption again.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Present one action button in one slot: Preview filter order before successful preview, Adopt design after successful preview; each click performs only that action. |
| REQ-002 | Replace the action button with a genuine non-interactive Design adopted Label in the same slot after adoption; prioritize adopted settings, including restored mappings. |
| REQ-003 | Relevant edits invalidate both preview and adoption and reset the slot to Preview filter order; preserve errors, sensor independence, calculations and persisted settings. |
| REQ-004 | Keep the shared slot stable and reachable in the existing constrained-height scroll view for both sensors. |
| REQ-005 | When software filtering is enabled and the design is not adopted, Next stays clickable but displays existing wizard validation feedback and does not advance. Raw-only and already-filtered modes do not require adoption. |

## Decisions

| ID | Decision |
|---|---|
| DEC-001 | Separate action and status using a fixed button plus a status label below the action row. This is the recommended proposal, not an execution grant. |
| DEC-002 | Derive presentation from existing properties to avoid a second status authority. |
| DEC-003 | Disable an already completed adoption action to prevent redundant clicks; retain the visible button to keep its location stable. |
| DEC-004 | Use the user's preferred three-stage shared slot: Preview filter order button, then Adopt design button, then Design adopted Label. Relevant edits reset to the first stage. Supersedes DEC-001 and DEC-003. |
| DEC-005 | Retain Next as a clickable validation action; use the existing wizard feedback region to explain missing adoption and retain the current step. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | Real clicks perform preview then adoption separately; successful preview changes the single button caption, adoption stores settings and replaces the button with a Label that has no action or keyboard activation. | Update QML interaction tests for both sensors. | PASS: actual per-sensor preview/adoption clicks and Label checks; architecture/change-plans/SPEC-0034-verification.md. |
| AC-002 | REQ-002, REQ-003 | Initial, ready, restored-adopted, edited and failed-preview cases match the table; relevant edits reset preview/adoption, failed preview permits retry, loaded adopted settings display the Label immediately. | Focused QML lifecycle checks using existing fixtures and mapping tests. | PASS: edits, restored settings, failed preview and retry; final lifecycle retest 2 passed; architecture/change-plans/SPEC-0034-verification.md. |
| AC-003 | REQ-003, REQ-004 | Internal one-stage and External four-stage cases remain independently usable at the existing 740 by 430 viewport; actual wheel input reaches the slot; transitions preserve its placement without footer overlap. | Retain actual wheel/mouse coverage in test_sensor_mapping_scroll.py and inspect rendered UI. | PASS: Internal one-stage and External four-stage actual wheel/mouse tests at 740x430; rendered Qt scene inspected; architecture/change-plans/SPEC-0034-verification.md. |
| AC-004 | REQ-005 | With otherwise valid mapping inputs, Next in initial, previewed-but-not-adopted, edited and failed-preview states shows the wizard warning and retains step/inputs. Adoption permits the next step if other rules pass. Non-software modes do not require adoption. | MappingWizard real Next-click interaction tests for both IMU steps, including software-filter-off regression. | PASS: actual Next clicks preserve step and show warning before adoption; allow progress after adoption and in non-software modes; 49-test regression PASS; architecture/change-plans/SPEC-0034-verification.md. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-002 | depends_on | DEC-002 |
| AC-001 | depends_on | REQ-001 |
| AC-003 | depends_on | REQ-004 |
| DEC-004 | supersedes | DEC-001 |
| DEC-004 | supersedes | DEC-003 |
| REQ-001 | depends_on | DEC-004 |
| REQ-005 | depends_on | DEC-005 |
| AC-004 | depends_on | REQ-005 |

## Out of Scope

Filter mathematics, preview backend, persistence schemas, automatic adoption, new modules, new named types, new state objects, new callbacks, events or dependency edges.

## Open Decisions

None.

## Discussion Context

### DISC-001: Action and status distinction
- **Situation:** Clicking Adopt design currently replaces its caption with Design adopted.
- **Question:** What proposal addresses the user's distinction between an action and a status?
- **Options and tradeoffs:** A fixed button and independent label preserve semantics at the cost of an extra text row; hiding the button shifts the action layout; changing its caption retains the reported problem.
- **User answer:** The user stated that Adopt design is an action and Design adopted is a status, then requested a modification proposal.
- **Explicit rationale:** The user said the two concepts are different. They have not authorized implementation.
- **Resulting impact:** REQ-001 through REQ-004 and DEC-001 through DEC-003 define the proposed scope; routine details are assistant recommendations, not attributed user choices.

### DISC-002: User selects a shared slot
- **Situation:** The first proposal used separate preview/adoption buttons and a separate status row.
- **Question:** How should preview, adoption and adopted status share space, and what should Next do before adoption?
- **Options and tradeoffs:** The user prefers one shared slot; it presents only the current action and becomes a genuine Label after completion. This removes the separate preview action after adoption; editing returns the slot to preview.
- **User answer:** 我比較傾向 preview filter order跟adopt design共用一個按鈕並跟Design adopted  共用位置，一修改就變preview filter order，點選 preview filter order後變adopt design，點選adopt design後變Design adopted的label之類的。如果狀態沒有變成Design adopted，按下next會提示。
- **Explicit rationale:** Preview and adoption share one button and position with the adopted label; edits reset the action; Next warns when not adopted.
- **Resulting impact:** DEC-004 supersedes DEC-001 and DEC-003, DEC-005 records Next feedback, REQ-001 through REQ-004 and AC-001 through AC-003 are revised, and REQ-005/AC-004 are added. No implementation authorization was supplied.

## Routing/Gates

Implementation completed under the user's exact execution instruction following revision 4. Changes are confined to SensorMapping.qml, local MappingWizard feedback synchronization, focused QML tests, the architecture invariant and generated views. Existing filter calculations, persistence, ownership and dependency boundaries are preserved.

Spec review: PASS
Standards review: PASS
Architecture design, development and release gates: PASS, with the pre-existing SHOULD SYM004 notice for symbols without an installed language analyzer. Real Qt scene interaction tests and rendered images supplement that limitation; no new OS scheduling or hardware assurance is claimed.
Ruff 0.16.6 format checks: PASS for modified Python tests. Source edits use existing QML style and DesignTokens. Original changed-file bytes are retained under spec-governance/spec34-originals because this checkout has no Git metadata.

Evidence details are recorded in architecture/change-plans/SPEC-0034-verification.md. Final evidence publication ends product execution for this revision; it is not a new request for authorization.

## Revision History

- Revision 1, 2026-09-13: Proposed action/status separation in response to the user's request; implementation is not authorized.
- Revision 4, 2026-09-13: Reconciled the user's shared-slot decision and Next feedback requirement; previous separate-row proposal superseded; implementation is not authorized.
| 6 | 2026-09-13 | Recorded implementation PASS evidence. |
