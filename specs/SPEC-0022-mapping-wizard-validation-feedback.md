---
spec_version: 1
spec_id: SPEC-0022
revision: 6
status: implemented
change_set: mapping-wizard-validation-feedback
---

# Show Mapping Wizard validation failures

## Problem

When Mapping Wizard confirmation fails, `StudioController.confirmMapping` stores the validation error only in the main window status bar and returns `false`. The modal wizard correctly remains open, but it does not render that error, while the main status bar is dimmed and visually separated behind the modal. The Finish action therefore appears unresponsive and gives no actionable explanation. During diagnosis, the supplied `offset8mm_speed20%.xlsx` reproduced this at source row 43102 because mapped `External Accel X/Y/Z` cached cells contained `#REF!` before later complete rows. The workbook was subsequently recalculated outside this change set and its current row 43102 values are valid, so the durable regression uses an equivalent fixed malformed source fixture. The same visibility rule must cover every recoverable configuration, mapping, source-data, or file-read error encountered during the wizard, rather than only final confirmation.

## Solution

Keep errors non-destructive and keep the wizard open. Validate the current step when the user presses Next and validate final mapping/conditions when the user presses Finish. Show every recoverable configuration, mapping, source-data, and file-read error as a visible inline error, preserve all current selections, and prevent advancement or closure. Clear stale feedback when relevant input changes and replace it with the current result on retry.

## User Stories

- As a user completing Mapping Wizard, I can immediately see why Finish did not complete so I can correct the mapping or source data.
- As a user with invalid imported data, I do not lose my current wizard selections when validation fails.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Any recoverable configuration, mapping, source-data, or file-read error encountered during Mapping Wizard shall keep the wizard open and visibly present the exact error inline within the active wizard. |
| REQ-002 | Editing input relevant to the displayed error shall clear stale inline feedback; each later failed retry shall show the current error. |
| REQ-003 | Successful confirmation shall retain existing behavior: accept and close the wizard. |
| REQ-004 | Mapping validation shall remain unchanged, source workbooks shall not be modified by the wizard, and interior mapped gaps such as the originally observed source row 43102 shall continue to be rejected. |
| REQ-005 | No recoverable error from a user-triggered Mapping Wizard operation shall fail silently or be visible only outside the active wizard. |
| REQ-006 | Each step shall validate when Next is pressed, and final mapping/conditions shall validate when Finish is pressed; validation failure shall prevent advancement or closure. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Present failed Finish validation as an inline error inside the still-open Mapping Wizard, without an additional dialog. | The user changed the selection from option 2 to option 1. This keeps the failure visible beside the active task and allows immediate correction without an extra dismissal. |
| DEC-002 | Run validation on Next and Finish actions rather than continuously while the user edits. | The user selected option 1. This reports every actionable error before progression without noisy transient errors during incomplete input. |

## Discussion Context

### DISC-001: Validation-error presentation

- **Situation:** Finish correctly remains in the wizard when `confirmMapping` returns `false`, but the only error text is in the obscured main-window status bar.
- **Question:** How should a failed Finish attempt present the validation error inside Mapping Wizard?
- **Options and tradeoffs:** A wizard-local inline error avoids an extra click and stays near the inputs; a modal error dialog is more interruptive and must be dismissed before adjustment.
- **User answer:** The user first selected option 2, then explicitly changed the answer to option 1: show an inline wizard error.
- **Explicit rationale:** No additional rationale was stated; the final selection favors uninterrupted correction in the active wizard.
- **Resulting impact:** DEC-001 closes OD-001. REQ-001, REQ-002, AC-001, and AC-002 require inline error presentation and stale-error handling.

### DISC-002: Error coverage throughout setup

- **Situation:** The initial contract covered errors returned by final mapping confirmation, while earlier wizard steps currently advance without an explicit validation-feedback contract.
- **Question:** Which errors during Mapping Wizard setup must be shown?
- **Options and tradeoffs:** Limiting feedback to Finish is the smallest change but leaves earlier failures opaque; covering all recoverable wizard errors creates consistent behavior but requires validation at each user-triggered operation.
- **User answer:** "在設定過程中，如果有任何異常都要顯示" (During setup, display any exception.)
- **Explicit rationale:** The user requires complete visibility throughout configuration, not only at Finish.
- **Resulting impact:** REQ-001 and REQ-002 broaden to the full wizard; REQ-005 and AC-004 are added. OD-002 captures the validation-timing decision.

### DISC-003: Validation timing

- **Situation:** Complete error coverage can run continuously during editing or at explicit step-transition actions.
- **Question:** When should each wizard step validate and display its recoverable errors?
- **Options and tradeoffs:** Next/Finish validation avoids transient errors and repeated large-file work; live validation responds sooner but can be noisy and expensive; hybrid validation improves responsiveness at greater implementation complexity.
- **User answer:** Option 1: validate on Next and Finish.
- **Explicit rationale:** No additional rationale was stated; the selected option provides complete gating with stable, action-oriented feedback.
- **Resulting impact:** DEC-002 closes OD-002. REQ-006 and AC-005 require step-transition validation and blocked progression on error.

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-004 | With an interior mapped-value gap equivalent to the originally observed workbook defect, Finish leaves the wizard open and visibly shows the exact source row inline within the active wizard. | Controller-backed offscreen QML interaction regression test or the nearest existing QML seam. | PASS: `test_mapping_wizard_finish_shows_controller_source_error_inline` keeps the wizard on Review and displays `mapped value gap inside recording at source row 3`; the reader's rejection rule is unchanged. The recalculated supplied workbook currently maps successfully because row 43102 no longer contains invalid cached values. |
| AC-002 | REQ-002 | After a failed Finish, changing relevant input clears the stale inline error; a later failed retry presents the current controller error. | Focused QML interaction regression test. | PASS: the Finish regression invokes the TextField edit signal, observes the inline error clear, retries, and observes the current controller error return. |
| AC-003 | REQ-003 | With a valid mapping, Finish calls successful confirmation and closes the wizard. | Existing mapping test plus focused QML regression test. | PASS: the same controller-backed QML regression repairs the source fixture, presses Finish, and observes the wizard close. |
| AC-004 | REQ-001, REQ-005 | Representative invalid row/header, time-basis, IMU-column, test-condition, source-data, and file-read cases each produce visible inline feedback in the active wizard and do not silently advance or close it. | Parameterized controller-backed QML interaction tests at each wizard operation seam. | PASS: focused QML tests cover row order, fixed sample rate, internal and cross-IMU distinctness, Robot Speed, interior source gaps, and a missing source file; every failure remains visible in the active wizard. |
| AC-005 | REQ-006 | Pressing Next with an invalid current step keeps that step active and shows its error; pressing Finish with invalid final or source data keeps the wizard open and shows its error. No validation error is emitted merely because input is temporarily incomplete while typing. | Focused offscreen QML interaction tests for every step transition and Finish. | PASS: Next/Finish interaction tests cover all five steps and verify no transition or closure on failure; validation is called only by the buttons, while edit handlers only clear stale feedback. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0001 |
| REQ-001 | depends_on | DEC-001 |
| REQ-002 | depends_on | REQ-001 |
| REQ-002 | depends_on | DEC-001 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |
| AC-003 | depends_on | REQ-003 |
| AC-004 | depends_on | REQ-001 |
| AC-004 | depends_on | REQ-005 |
| REQ-006 | depends_on | DEC-002 |
| AC-005 | depends_on | REQ-006 |

## Out of Scope

- Repairing formulas or modifying the supplied workbook.
- Relaxing rejection of incomplete mapped values inside a recording.
- Changing how IMU columns are proposed or interpreted.
- Redesigning unrelated status or notification surfaces.

## Open Decisions

None.

## Routing/Gates

- Risk: R1 standard QML interaction correction.
- Required gates: TDD and code review.
- Product implementation was authorized by the user's exact `開始執行`.
- TDD: PASS; Mapping Wizard focused tests passed 8/8, QML smoke passed 32/32, and the complete suite passed 413/413 with pytest temporary storage redirected from the host's broken system Temp path into `build/pytest-temp`.
- Architecture development gate: PASS (exit 0), with only the existing SHOULD `SYM004` for unavailable QML language analysis.
- Standards review: PASS; the inaccurate workspace-port rejection and duplicated test setup found on first review were corrected, then re-reviewed with no remaining finding.
- Spec review: PASS; REQ-001 through REQ-006 and AC-001 through AC-005 are covered with no scope creep or unverified acceptance criterion.

## Revision History

| Revision | Change |
|---|---|
| 1 | Started the Mapping Wizard validation-feedback change set from the reproduced hidden-error defect. |
| 2 | Initially selected modal error-dialog presentation. |
| 3 | Replaced the prior selection with inline wizard feedback at the user's request and closed OD-001 with the final choice. |
| 4 | Reopened and broadened error visibility to every recoverable Mapping Wizard error; added OD-002 for validation timing. |
| 5 | Selected validation on Next and Finish, blocked progression on errors, and closed OD-002. |
| 6 | Recorded implementation evidence and reconciled AC-001 with the externally recalculated supplied workbook while retaining the fixed interior-gap regression. |
