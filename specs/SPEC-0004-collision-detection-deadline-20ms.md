---
spec_version: 1
spec_id: SPEC-0004
revision: 8
status: confirmed
change_set: collision-detection-deadline-20ms
---

# Collision Detection Deadline 20 ms and Diagnostic Replay

## Problem

Qualification uses a 10 ms Fork Collision deadline. Failed runs expose no retained result identifying which round winner made the fewest mistakes, and Replay lacks the selected kernel's FIR-predicted External IMU and score waveform.

## Solution

Extend the deadline to 20 ms. Preserve one winner per fallback round, then rank those winners by minimum all-supplied misjudgment total and minimum Worst Collision Latency, keeping all exact ties. If every minimum-error winner has no finite latency, retain all minimum-error winners with `N/A` latency and explicit collision detected/total counts. Connect Replay to selected kernel/recording/Cycle/event provenance and show Internal IMU, actual and FIR-predicted External IMU, residual, score, threshold, ratio, detector state, trigger, and latency. Preserve 50 ms re-arm and silently retain saved stricter 10 ms results as current.

## User Stories

- As a user, I can qualify a trigger occurring within 20 ms.
- As a user, I can inspect the lowest-error retained round winners even when none qualifies or detects a collision.
- As an analyst, I can inspect FIR prediction and detector score waveforms.
- As a user, I can reopen an existing saved project without losing completed results.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Qualification shall count a confirmed Fork Collision as detected when the first eligible trigger occurs from the interval start through exactly 20 ms after that start, inclusive; a later trigger shall not satisfy that collision event. The confirmed interval end shall not shorten the 20 ms response window. |
| REQ-002 | Every applicable Qualification gate, fallback decision, result explanation, UI label, diagnostic, newly persisted semantic result, newly generated Profile declaration, specification statement, test, and algorithm/governance record shall use the 20 ms collision deadline. |
| REQ-003 | Normal Robot Motion/Pick/Put zero-false-event gates, every-collision detection, speed/Offset fallback, candidate ranking for qualified Profiles, one-winner-per-round retention, Profile export eligibility, target numeric arithmetic, and the independent 50 ms below-release re-arm time shall otherwise remain unchanged. |
| REQ-004 | Existing saved projects containing completed results produced under the former 10 ms deadline shall retain and present those results as current after opening, without a legacy marker, automatic invalidation, or forced rerun. |
| REQ-005 | After Qualification, including a run with no qualified Profile, the application shall compare only the existing retained winner from each completed fallback round according to DEC-011. Each winner shall be replayed against every supplied recording; its misjudgment count shall equal emitted detector triggers during Normal Robot Motion, Pick, and Put plus confirmed Fork Collision intervals without an eligible trigger by the inclusive 20 ms deadline. The result shall minimize all-supplied total, then finite Worst Collision Latency, and retain all exact ties. If no minimum-error winner has finite latency, every minimum-error winner shall remain visible with latency `N/A` and exact collision detected/total counts according to DEC-013. Diagnostic winners shall be visibly non-qualified and shall not become exportable solely from this ranking. |
| REQ-006 | Replay & Qualify shall allow selection of a retained qualified or diagnostic kernel and exact supplied Recording/Cycle/Event provenance, reproduce target-numeric FIR and detector replay, and expose synchronized full-resolution arrays for Internal IMU X/Y/Z, actual External IMU X/Y/Z, FIR-predicted External IMU X/Y/Z, residual X/Y/Z, normalized scalar score, threshold, collision ratio, detector state, trigger samples, and event latency. Rendering decimation shall not alter analytical samples or timing. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Replace the 10 ms Fork Collision detection deadline with 20 ms and cancel the previously proposed additional no-misjudgment kernel result behavior. | The user explicitly withdrew all earlier changes and requested only the deadline extension. |
| DEC-002 | Preserve existing saved results produced under the stricter 10 ms deadline and present them directly as current 20 ms results without a legacy label or forced rerun. | The user selected option 3. Any result that passed the stricter 10 ms deadline necessarily satisfies the wider 20 ms deadline, although the original deadline provenance will not remain visible. |
| DEC-003 | Pending: define how false triggers, missed collisions, and repeated triggers are converted into the misjudgment count used to retain the best diagnostic kernel result. | Different counting units can select different kernels and must be explicit before persistence or UI ranking is implemented. |
| DEC-004 | Replay the selected kernel against original supplied data and show Internal IMU, actual and FIR-predicted External IMU, residual, normalized score, threshold, collision ratio, detector state, and event trigger/latency on synchronized time axes. | The user requested visibility into how Internal IMU fits External IMU and produces the score waveform. |
| DEC-005 | Pending: decide whether minimum-misjudgment candidates are compared over every supplied recording or only the active speed/Offset scope of each candidate's fallback round. | Active-only totals shrink as conditions are excluded and therefore are not directly comparable across rounds; all-supplied totals preserve one denominator but include evidence outside a candidate's Training range. |
| DEC-006 | Supersede DEC-003 by defining total misjudgments as emitted false collision triggers during Normal Robot Motion, Pick, and Put plus missed Fork Collision intervals, where a collision is missed when no eligible trigger occurs by the inclusive 20 ms deadline. Minimize the arithmetic sum. | The user selected option 1 because the displayed metric shall represent actual nuisance trigger events plus missed collision events. |
| DEC-007 | Supersede DEC-005 by comparing every candidate over every supplied recording, including speeds and Offsets outside that candidate's fallback Training range. | The user selected option 1 so every candidate uses the same evidence and denominator and cross-round raw totals remain directly comparable. |
| DEC-008 | Pending: decide whether all candidates tied at the minimum all-supplied misjudgment total are retained or a secondary criterion selects one. | Sample-snapped detector behavior can produce exact ties across kernels. |
| DEC-009 | Supersede DEC-008 with lexicographic diagnostic ranking: first minimize all-supplied misjudgment total, then minimize finite Worst Collision Latency among that tied subset, then retain every candidate still exactly tied. | The user selected options 1 and 3 together and clarified that all exact ties remain available for Replay after latency comparison. |
| DEC-010 | Pending: decide whether the diagnostic ranking pool contains every evaluated frozen candidate or only each fallback round's existing selected winner. | Winner-only reuse is smaller but can discard a lower-error candidate selected against different qualified-coverage criteria. |
| DEC-011 | Supersede DEC-010 by restricting diagnostic ranking to the one existing winner retained from each completed fallback round. Do not retain or resurrect non-winning candidates from that round. | After reviewing the scenario, the user selected option 2 to preserve the existing round-winner architecture. |
| DEC-012 | Pending: define the diagnostic result when the minimum-error round winners have no finite collision latency because none detected any collision. | A finite-latency secondary comparison cannot select among all-missed winners, but the user still requested a minimum-error result. |
| DEC-013 | Supersede DEC-012 by retaining every minimum-error round winner when none has finite collision latency, displaying latency as `N/A` and exact collision detected/total counts. | The user selected option 1 so the best available diagnostic evidence remains visible even when every such winner misses all collisions. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | Tests accept triggers through exactly 20 ms and reject later triggers independent of annotation end. | Qualification tests. | Pending |
| AC-002 | REQ-002 | New runtime and visible results use 20 ms consistently. | Focused tests and architecture gate. | Pending |
| AC-003 | REQ-003 | Regression tests preserve existing fallback, qualified ranking/export, target replay, and 50 ms re-arm except deadline outcomes. | Differential tests. | Pending |
| AC-004 | REQ-004 | A pre-change project opens with results retained and unlabeled as legacy without rerunning. | Persistence tests. | Pending |
| AC-005 | REQ-005 | Fixtures prove only retained round winners enter all-supplied error summation and latency ranking; non-winners never reappear; finite-latency ties follow DEC-009; an all-nonfinite minimum-error set retains every tied winner with `N/A` and exact `0 / N` or applicable counts; diagnostic-only export is blocked. | Domain, controller, persistence, and QML tests. | Pending |
| AC-006 | REQ-006 | Replay reproduces prediction, residual, score, state, trigger, and latency; UI selection populates synchronized labeled traces without altering arrays. | Numerical, controller, WaveformItem, and QML tests. | Pending |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | depends_on | DEC-001 |
| REQ-002 | depends_on | REQ-001 |
| REQ-003 | depends_on | REQ-001 |
| REQ-004 | depends_on | DEC-002 |
| REQ-005 | depends_on | DEC-006 |
| REQ-005 | depends_on | DEC-007 |
| REQ-005 | depends_on | DEC-009 |
| REQ-005 | depends_on | DEC-011 |
| REQ-005 | depends_on | DEC-013 |
| REQ-006 | depends_on | DEC-004 |
| DEC-006 | supersedes | DEC-003 |
| DEC-007 | supersedes | DEC-005 |
| DEC-009 | supersedes | DEC-008 |
| DEC-011 | supersedes | DEC-010 |
| DEC-013 | supersedes | DEC-012 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |
| AC-003 | depends_on | REQ-003 |
| AC-004 | depends_on | REQ-004 |
| AC-005 | depends_on | REQ-005 |
| AC-006 | depends_on | REQ-006 |

## Discussion Context

### DISC-001: Baseline change
- **Situation:** A previous proposal used a different result definition.
- **Question:** Keep it or replace it with the 20 ms baseline?
- **Options and tradeoffs:** Keeping both expands scope; replacement preserves the selected baseline.
- **User answer:** Discard previous modifications and extend the trigger window to 20 ms.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-001 defines REQ-001 through REQ-003.

### DISC-002: Saved results
- **Situation:** Saved projects may contain stricter 10 ms results.
- **Question:** Invalidate, label legacy, or silently retain?
- **Options and tradeoffs:** Invalidation forces reruns; labeling preserves provenance; silent reuse removes provenance.
- **User answer:** Option 3: treat them as current without displaying a difference.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-002 defines REQ-004.

### DISC-003: Error metric
- **Situation:** False triggers and misses need one metric.
- **Question:** How shall errors be counted?
- **Options and tradeoffs:** Event summation reflects actual nuisance events and misses; interval counting hides repeated triggers.
- **User answer:** Option 1: sum false trigger events and missed collision intervals.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-006 supersedes DEC-003 and defines REQ-005.

### DISC-004: Replay evidence
- **Situation:** Replay lacks kernel/event data flow.
- **Question:** Which traces shall it expose?
- **Options and tradeoffs:** Full prediction and detector evidence explains outcomes; partial traces do not.
- **User answer:** Show fitted External IMU and score waveform.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-004 defines REQ-006.

### DISC-005: Comparison scope
- **Situation:** Active-only totals use shrinking denominators.
- **Question:** Compare all supplied evidence or active scope?
- **Options and tradeoffs:** All supplied is comparable; active-only favors narrow rounds.
- **User answer:** Option 1: all supplied recordings.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-007 supersedes DEC-005 and defines REQ-005.

### DISC-006: Ranking ties
- **Situation:** Candidates can share minimum errors.
- **Question:** Keep all or add a secondary criterion?
- **Options and tradeoffs:** Lower latency adds response preference while exact ties remain visible.
- **User answer:** Options 1 and 3: minimum errors, then minimum latency, then keep all ties.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-009 supersedes DEC-008 and defines REQ-005.

### DISC-007: Candidate pool
- **Situation:** Existing flow keeps one winner per fallback round.
- **Question:** Compare all evaluated kernels or only round winners?
- **Options and tradeoffs:** All candidates finds a global error minimum; winner-only preserves existing retention.
- **User answer:** Option 2: compare only each fallback round's existing winner.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-011 supersedes DEC-010 and defines REQ-003 and REQ-005.

### DISC-008: No finite latency
- **Situation:** Minimum-error winners can all miss every collision.
- **Question:** Display them with N/A latency or show no result?
- **Options and tradeoffs:** Displaying preserves best available evidence while exposing failure; empty output hides that comparison.
- **User answer:** Option 1: retain and display all such winners with N/A latency and collision detected/total counts.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-013 supersedes DEC-012 and completes REQ-005 and AC-005.

## Out of Scope

- Changing 50 ms re-arm, fallback policy, candidate grid, or qualified export selection.
- Exporting diagnostic-only kernels as qualified.
- Reconstructing new candidates from old saved results without rerunning.

## Open Decisions

None.

## Routing/Gates

- Grilling and spec reconciliation are complete.
- Product implementation requires a new exact `開始執行` authorization because the reopened contract changed.
- Required gates: TDD, algorithm/governance update, architecture gate, numerical replay validation, and code review.

## Revision History

| Revision | Date | Summary |
|---|---|---|
| 1 | 2026-08-26 | Started 20 ms change. |
| 2 | 2026-08-26 | Preserved saved stricter results. |
| 3 | 2026-08-26 | Reopened for ranking and Replay. |
| 4 | 2026-08-26 | Defined error summation. |
| 5 | 2026-08-26 | Selected all-supplied comparison. |
| 6 | 2026-08-26 | Added latency secondary ranking. |
| 7 | 2026-08-26 | Restricted comparison to round winners. |
| 8 | 2026-08-26 | Retained all minimum-error winners with N/A when no finite latency exists and completed the revised interview. |
