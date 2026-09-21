---
spec_version: 1
spec_id: SPEC-0014
revision: 4
status: implemented
change_set: kernel-qualification-summary
---

# Kernel qualification summary and project actions

## Problem

The retained-kernel summary shows active/excluded Offsets but not active/excluded speeds. A recording with zero displayed Normal/Pick/Put false events, complete Collision detection, and latency within 150 ms can be presented as Fail because the current implementation requires positive counts for every activity class and collapses every non-PASS recording status into Fail. The project toolbar also exposes an unnecessary New Project action.

## Solution

Display active and excluded supplied speeds separately from the Training/Qualified range. Judge each recording only from activity intervals actually present: absent Normal/Pick/Put classes are neutral, every present Normal/Pick/Put interval must have zero false collision events, and at least one Collision interval must exist with every Collision detected no later than 150 ms from its confirmed start. Display the governing evidence clearly. Remove the New Project button while preserving Open, Save, Save As, and dirty-state protection.

## User Stories

- As an analyst, I can see which supplied speeds were active or excluded for each retained kernel.
- As an analyst, I can understand why each recording passes or fails without mistaking absent activity for an error.
- As a project user, I see only the project actions needed by this application.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | The retained-kernel summary shall display `Active Speed = training_speeds` and `Excluded Speed = supplied speeds - training_speeds`, while retaining the separate Training/Qualified range. |
| REQ-002 | A recording shall PASS when every actually supplied Normal, Pick, and Put interval emits zero false collision events, at least one supplied Collision interval exists, every supplied Collision interval is detected, and each detection onset occurs no later than 150 ms from its confirmed Collision interval start. A Normal, Pick, or Put class with zero intervals is neutral and shall not block PASS. Ignore samples remain excluded without extending or compressing the 150 ms deadline. |
| REQ-003 | Recording Qualification Results shall display a status derived from REQ-002 and expose the supporting activity denominators or failure reason; it shall not collapse semantically different evidence into an unexplained Fail label. |
| REQ-004 | The main toolbar shall not display New Project. Open Project, Save, Save As, and existing dirty-state protection for open/close transitions shall remain. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Define active speeds as `training_speeds` and excluded speeds as the supplied-speed set difference. | The user explicitly confirmed this mapping. |
| DEC-002 | Remove only the New Project UI entry point and its now-unreachable QML transition branch; do not broaden the change into unrelated project-session redesign. | The user stated that this project does not need a New Project button, while existing project requirements retain Open/Save/Save As. |
| DEC-003 | Evaluate only activity intervals that actually exist in a recording; absent Normal/Pick/Put classes are neutral, while Collision evidence remains mandatory and every Collision must be detected within the inclusive 150 ms onset deadline. | The user explicitly selected PASS for a recording with an absent non-Collision activity class and clarified the 150 ms Collision-onset rule. |

## Discussion Context

### DISC-001: Kernel speed-scope summary
- **Situation:** The selected-kernel summary exposes active/excluded Offsets and speed ranges but not the discrete active/excluded supplied speeds.
- **Question:** What do Active Speed and Excluded Speed mean?
- **Options and tradeoffs:** Training-scope membership preserves the actual fallback scope; qualified speeds describe a different result and remain in the Qualified range; deriving another definition would mislabel kernel provenance.
- **User answer:** `Active Speed = training_speeds`, `Excluded Speed = supplied speeds - training_speeds`; the user marked this correct.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-001 defines REQ-001 and keeps qualified speed evidence separate.

### DISC-002: Absent non-Collision activity classes
- **Situation:** Current source requires positive Normal, Pick, Put, and Collision interval counts before PASS. Zero false-event counts can therefore coexist with an unseen coverage shortage, and the controller currently renders every non-PASS recording as Fail.
- **Question:** If a recording contains zero intervals for Normal, Pick, or Put, is that absent class neutral for PASS or must it block PASS as Coverage Gap?
- **Options and tradeoffs:** Treating absent non-Collision classes as neutral matches the requested no-misjudgment rule and permits recordings that do not exercise every activity to pass; retaining the coverage gate prevents PASS without testing every activity but contradicts the requested recording outcome.
- **User answer:** It counts as PASS.
- **Explicit rationale:** The user's rule is that Normal/Pick/Put have no false detections and Collision is correct; a non-Collision activity that does not occur shall not itself cause failure.
- **Resulting impact:** DEC-003 closes OD-001 and defines REQ-002/REQ-003. The UI must no longer misrepresent absence as Fail.

### DISC-003: New Project action
- **Situation:** The toolbar contains New Project, while the established project-session specification requires Open Project, Save Project, and Save Project As but does not require New Project.
- **Question:** Should the toolbar keep New Project?
- **Options and tradeoffs:** Removing it simplifies the supported project workflow; retaining it offers session reset but contradicts the user's requested surface; removing all controller support would unnecessarily broaden interface and architecture scope.
- **User answer:** The project does not need a New Project button.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-002 defines REQ-004 as a UI-entry-point removal with existing persistence safeguards preserved.

### DISC-004: Collision detection deadline
- **Situation:** The user corrected the qualification discussion to the established 150 ms Collision deadline.
- **Question:** Is Collision correct when its detection onset occurs within 150 ms from the confirmed Fork Collision start?
- **Options and tradeoffs:** This is a factual contract clarification rather than a new alternative: the current UI copy and qualification source use an inclusive 150 ms deadline from Collision onset, with Ignore excluded without extending the deadline.
- **User answer:** Collision is allowed from its start point through 150 ms.
- **Explicit rationale:** The user expects the previously changed 150 ms onset rule to remain controlling.
- **Resulting impact:** REQ-002 explicitly preserves the inclusive 150 ms onset-to-detection rule; no shorter deadline or interval-end rule is introduced.

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | A fixture with supplied speeds 200/500/1000 and training speeds 500/1000 displays Active 500, 1000 mm/s and Excluded 200 mm/s, independently of Qualified range. | Controller and QML regression tests. | PASS: controller discrete speed-scope regression and QML Speeds binding; full pytest 391 passed. |
| AC-002 | REQ-002, REQ-003 | Recording fixtures prove that absent Normal/Pick/Put classes are neutral; any false event in a present class fails; zero Collision intervals fails with an explicit reason; complete detection at exactly 150 ms passes; a miss or detection after 150 ms fails; the UI exposes the governing denominators/reason and exact outcome. | Domain and controller/QML regression tests. | PASS: public Qualification absence, false-event, Collision coverage, 150 ms boundary, Ignore timing, and controller status/reason regressions; full pytest 391 passed. |
| AC-003 | REQ-004 | The QML object tree contains no New Project button or new-project transition action, while Open/Save/Save As and dirty open/close protection remain tested. | QML and project-session regression tests. | PASS: QML object-tree and static toolbar-transition regressions plus project-session protections; full pytest 391 passed. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0008 |
| REQ-002 | refines | SPEC-0011 |
| REQ-003 | refines | SPEC-0011 |
| REQ-004 | refines | SPEC-0002 |
| REQ-002 | depends_on | DEC-003 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |
| AC-002 | depends_on | REQ-003 |
| AC-003 | depends_on | REQ-004 |

## Out of Scope

- Changing FIR, Score, threshold, confirmation, fallback, or kernel-ranking algorithms.
- Treating a diagnostic-only kernel as exportable without satisfying the final confirmed qualification contract.
- Removing Open Project, Save, Save As, dirty-close protection, or the controller's non-UI session-reset capability.

## Open Decisions

None.

## Routing/Gates

- Governed route: grilling, then spec-governance.
- Risk: qualification semantic change plus QML/controller presentation change.
- Required gates: architecture governance, TDD, architecture CLI development gate, and code review.
- Spec review: PASS.
- Product implementation requires this confirmed canonical spec and a later exact `開始執行` authorization.

## Revision History

| Revision | Change |
|---|---|
| 1 | Started the combined kernel summary, recording qualification, and project-action change set from the user's screenshots and confirmations. |
| 2 | Made absent Normal/Pick/Put classes neutral for recording PASS, preserved mandatory Collision evidence and the inclusive 150 ms onset deadline, and closed OD-001. |
| 4 | 2026-08-31 | Recorded implementation PASS evidence. |
