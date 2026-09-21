---
spec_version: 1
spec_id: SPEC-0015
revision: 3
status: confirmed
change_set: execution-log-always-follow
---

# Execution Log always follows latest entry

## Problem

The implemented Candidate Dashboard Execution Log uses Smart follow. Once the user scrolls upward, incoming entries stop moving the viewport and the newest log is hidden behind a `Latest (N)` action. The user requires the visible viewport to return to the newest entry whenever log content advances so current Learning progress is always visible.

## Solution

Replace Smart follow with hover-controlled follow. While the mouse pointer is inside the Execution Log pane, do not call `positionViewAtEnd()` automatically, so the user can scroll and inspect older entries. When the pointer leaves the pane, immediately schedule `positionViewAtEnd()` after QML layout completion. While the pointer remains outside, every model-count or layout change that can move the newest delegate schedules `positionViewAtEnd()`, so unattended monitoring always displays the newest log. Remove the `Latest (N)` button, unseen-entry counter, bottom tolerance, and manual follow flag. Preserve the scrollable log, 10,000-entry capacity, discarded-entry marker, run lifecycle, log contents, controller model, and session-only persistence rules.

## User Stories

- As a user monitoring Learning, I always see the newest Execution Log entry when new progress arrives.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Supersede the Smart-follow behavior of SPEC-0012 REQ-015 with hover-controlled follow. Use pointer containment over the complete Execution Log pane as the sole pause condition. While the pointer is inside the pane, automatic `positionViewAtEnd()` calls shall be suppressed and manual wheel, drag, scrollbar, or keyboard inspection may retain an older viewport position even as entries arrive. On pointer exit, immediately schedule `positionViewAtEnd()` after QML layout completion; do not wait for another log entry. While the pointer is outside, every model-count, reset, overflow-trim, first-entry, delegate-size, or layout change that can move the newest delegate shall schedule `positionViewAtEnd()` after layout. Remove the prior bottom-tolerance/follow flag, unseen-entry counting, and `Latest (N)` control. Preserve vertical scrolling, the 10,000 newest-event bound and discarded marker, accepted-run clearing, terminal retention, event ordering/content, session-only lifetime, and project/export exclusions. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Use mouse-pointer containment of the complete Execution Log pane to pause automatic following; pointer exit immediately returns to the newest entry, and outside-pointer updates continuously follow the newest entry. | The user explicitly proposed this behavior so active inspection is preserved only while the pointer signals attention to the log. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | With enough entries to overflow the viewport, moving the pointer inside the complete Execution Log pane and scrolling upward preserves that older viewport position while additional entries arrive. Moving the pointer outside immediately positions the newest delegate visibly at the end without waiting for another entry. While outside, appends, delegate resizing, model reset, accepted-run first entry, and 10,000-event overflow trimming keep the newest delegate visible and the discarded marker correct. Re-entering without scrolling does not move the viewport away from the end. No `Latest (N)` control, unseen counter, manual follow flag, or bottom-tolerance behavior remains. Existing terminal retention, rejected-start preservation, event ordering/content, capacity, session-only and project-schema tests continue to pass. | QML pointer/scroll interaction tests, structural absence assertions, controller log lifecycle regressions, and rendered Training-page inspection. | Pending implementation and verification. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| DEC-001 | refines | REQ-001 |
| AC-001 | depends_on | REQ-001 |

## Out of Scope

Do not change Learning event production, log text or ordering, controller storage, capacity, truncation accounting, run lifecycle, project persistence, export formats, detector/Learning algorithms, or other scroll views. Do not disable manual scrolling between log updates.

## Open Decisions

None.

## Routing/Gates

ask-matt -> grilling -> spec-governance; implementation requires architecture governance, TDD, QML interaction/render validation, and code review. Product mutation requires exact `開始執行` authorization after this specification is confirmed.

## Revision History

| Revision | Date | Change |
|---|---|---|
| 1 | 2026-09-01 | Replace SPEC-0012 Smart follow with unconditional follow-on-log-update behavior. |
| 2 | 2026-09-01 | Select hover-controlled pause: pointer-inside preserves inspection; pointer exit and outside updates immediately follow latest. |

## Discussion Context

### DISC-001: Always show newest Execution Log entry

- **Situation:** The current QML pauses automatic following after the user scrolls upward and displays `Latest (N)`, so new Learning progress may not be visible.
- **Question:** Should incoming log entries preserve the user's older scroll position or force the viewport back to the newest entry?
- **Options and tradeoffs:** Smart follow preserves uninterrupted reading of old entries but can hide live progress. Forced follow makes current progress continuously visible but interrupts older-log inspection whenever a new event arrives.
- **User answer:** 使用 Execution Log pane 的滑鼠位置控制：滑鼠在窗格內不執行 `positionViewAtEnd()`；滑鼠不在窗格內就執行 `positionViewAtEnd()`。
- **Explicit rationale:** Pointer presence indicates that the user is actively inspecting the log; otherwise the pane should show the newest log.
- **Resulting impact:** REQ-001 and DEC-001 supersede the implemented SPEC-0012 Smart-follow contract with hover-controlled follow and resolve OD-001. Pointer exit returns immediately rather than waiting for the next log. Only Candidate Dashboard QML behavior and its tests/architecture description change; controller state, types, dependencies, persistence and algorithms remain unchanged.
