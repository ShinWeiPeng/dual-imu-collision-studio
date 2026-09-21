---
spec_version: 1
spec_id: SPEC-0016
revision: 3
status: implemented
change_set: execution-log-date-prefix
---

# Execution Log date and time timestamps

## Problem

Execution Log entries currently display only local time as `HH:mm:ss.fff`. A Learning run that crosses midnight or lasts longer than one day leaves the calendar day ambiguous.

## Solution

Display every Execution Log timestamp as local `YYYY-MM-DD HH:mm:ss.fff`, preserving millisecond precision, ordering, session-only storage, and all existing log contents and lifecycle behavior.

## User Stories

- As a user monitoring a long Learning run, I can identify the calendar date of every Execution Log entry.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Every ordinary progress entry and terminal entry in the Candidate Dashboard Execution Log shall display local time in the exact format `YYYY-MM-DD HH:mm:ss.fff`. No event ordering, content, capacity, truncation, run lifecycle, persistence, or export behavior shall change. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Preserve local timezone and millisecond precision. | The current timestamps already use local zoned time and milliseconds; the reported defect is calendar-day ambiguity only. |
| DEC-002 | Use `YYYY-MM-DD HH:mm:ss.fff` for every Execution Log timestamp. | The user selected option 1, the unambiguous ISO-style year-first format that remains naturally sortable across days and years. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | Ordinary and terminal log rows both contain local timestamps matching `YYYY-MM-DD HH:mm:ss.fff`; entries on different calendar days are visibly distinguishable, and existing log lifecycle tests continue to pass. | Focused controller unit tests with a controlled clock plus existing QML/log regression tests. | PASS — cross-midnight controlled-clock test covers ordinary and terminal entries; 36 focused tests and 392 full-suite tests passed; architecture development gate exited 0 with `PASS: VERIFIED`; Spec review PASS with no uncovered REQ, unverified AC, or scope creep. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| DEC-001 | refines | REQ-001 |
| DEC-002 | refines | REQ-001 |
| AC-001 | depends_on | REQ-001 |

## Out of Scope

Do not change timezone behavior, event content or ordering, log capacity/truncation, hover-follow behavior, run lifecycle, project persistence, exports, Learning algorithms, or other timestamps in the application.

## Open Decisions

None.

## Routing/Gates

ask-matt -> grilling -> spec-governance -> TDD -> architecture governance -> code review. Product execution was authorized by exact `開始執行`. Architecture development gate: PASS. Standards review: PASS with no hard violations. Spec review: PASS.

## Revision History

| Revision | Date | Change |
|---|---|---|
| 1 | 2026-09-01 | Start the governed change set and record the date-format decision. |
| 2 | 2026-09-01 | Select `YYYY-MM-DD HH:mm:ss.fff` and resolve OD-001. |
| 3 | 2026-09-01 | Record implementation, validation, architecture-gate, and two-axis review PASS evidence. |

## Discussion Context

### DISC-001: Execution Log calendar-date format

- **Situation:** Execution Log timestamps are currently `HH:mm:ss.fff`, so entries spanning midnight cannot be assigned to a calendar day.
- **Question:** Which unambiguous calendar-date format should prefix the existing time?
- **Options and tradeoffs:** Option 1 `YYYY-MM-DD` is unambiguous and naturally sortable but longest; option 2 `YYYY/MM/DD` is familiar in some Chinese interfaces but less standards-aligned; option 3 `MM-DD` is shortest but ambiguous across years.
- **User answer:** 1
- **Explicit rationale:** No separate rationale was stated; the selected option is the recommended unambiguous ISO-style year-first format.
- **Resulting impact:** REQ-001 and AC-001 now require exact `YYYY-MM-DD HH:mm:ss.fff`; DEC-002 records the selected format and OD-001 is resolved.
