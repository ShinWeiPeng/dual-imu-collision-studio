---
spec_version: 1
spec_id: SPEC-0019
revision: 5
status: implemented
change_set: recording-collision-snr
---

# Per-collision SNR in Recording Qualification Results

## Problem

The Recording Qualification Results table reports collision detection count and worst latency but does not show signal-to-noise ratio for the collision events in each recording.

## Solution

Add one `Collision SNR (dB)` column to each recording result. List every collision's SNR in chronological order, separated by ` / `; an empty collision set displays `N/A`. For each collision, use the maximum finite detector Score in its existing 150 ms Qualification response window as signal amplitude and the RMS of finite detector Scores outside all Collision and Ignore intervals in the same recording as the shared noise amplitude. Report `20 * log10(signal / noise)` in dB. If the signal or noise amplitude is zero, non-finite, or unavailable, display `N/A` for that collision without fabricating a finite value.

## User Stories

- As an analyst, I want to see the detector-Score SNR of every collision event for each recording so that I can compare collision evidence strength rather than only pass/fail and latency.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Recording Qualification Results shall add one `Collision SNR (dB)` column. For every recording, list SNR values for all collision intervals in chronological order separated by ` / `; exactly three intervals therefore display three values, fewer display only the available values, more display every value, and zero intervals display `N/A`. Each collision's signal amplitude is the maximum finite detector Score in that collision's existing 150 ms Qualification response window. The shared recording noise amplitude is the RMS of all finite detector Scores outside every Collision and Ignore interval in that recording. SNR is `20 * log10(signal / noise)` in dB. If either amplitude is zero, non-finite, or unavailable, that collision's entry shall be `N/A`; do not substitute epsilon or emit an infinite value. Preserve existing qualification status, counts, latency, reason, and replay export behavior. |

## Decisions

| ID | Decision | Status |
|---|---|---|
| DEC-001 | Use Detector Score SNR: collision-window peak Score divided by the recording's non-Collision/non-Ignore Score RMS, converted with `20 * log10` and reported in dB. | Confirmed by the user's selection of option 1. |
| DEC-002 | Present all per-collision SNR values in one `Collision SNR (dB)` column, ordered chronologically and separated by ` / `; use `N/A` only when there are no collision intervals. | Confirmed by the user's selection of option 2. |
| DEC-003 | Display `N/A` for an individual collision whenever its signal or shared noise amplitude cannot form a finite positive ratio; never introduce epsilon or display positive/negative infinity. | Confirmed by the user's selection of option 2. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | Each recording row has one `Collision SNR (dB)` cell containing every chronologically ordered SNR value. Fixtures with exactly three, fewer than three, more than three, and zero collision intervals show respectively three, the available count, the complete count, and `N/A`. Collision peaks, shared recording noise RMS, and dB conversion match the confirmed Detector Score definition. A zero, non-finite, empty, or otherwise unavailable signal/noise produces `N/A` only for the affected collision, while valid sibling collision values remain visible. Existing qualification status, counts, latency, reason, and replay export remain unchanged. | Learning-domain unit tests with deterministic Score arrays, controller mapping tests, and QML smoke tests. | PASS: 406 pytest cases; deterministic Learning SNR edge cases; controller/QML checks; build check; development architecture gate; Standards PASS; Spec PASS. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0011 |
| DEC-001 | refines | REQ-001 |
| DEC-002 | refines | REQ-001 |
| DEC-003 | refines | REQ-001 |
| AC-001 | depends_on | REQ-001 |

## Out of Scope

- Changing detector thresholds, collision pass/fail rules, latency rules, model training, or replay export contents.
- Altering the number or timing of source annotations.
- Presenting this detector-derived metric as raw-sensor SNR.
- Persisting SNR in project files or adding it to Replay CSV export.

## Open Decisions

None.

## Routing/Gates

- Authoritative route: ask-matt -> grilling -> spec-governance -> TDD -> architecture governance -> code review.
- Risk: R1 standard presentation/evidence change; it adds no persistent schema and does not change detector decisions.
- Required before delivery: spec verification, TDD, architecture development gate, and two-axis code review.
- Spec review: PASS.
- Product execution was authorized by the user's exact `開始執行` instruction on 2026-09-01.

## Discussion Context

### DISC-001: Per-collision SNR definition

- **Situation:** The repository has detector Score, raw IMU signals, annotated collision windows, and non-collision intervals, but no existing SNR definition. Different definitions produce materially different values.
- **Question:** Which signal and noise populations should define each collision's SNR?
- **Options and tradeoffs:** Option 1 uses detector Score peak in the collision window relative to RMS Score outside collision/Ignore windows and directly reflects detector separability, but it is a detector-score metric rather than raw sensor SNR. Option 2 uses RMS external-IMU acceleration in the collision window relative to RMS external-IMU acceleration in Normal intervals and resembles sensor SNR, but robot motion and gravity can dominate it. Option 3 uses prediction-residual RMS inside the collision window relative to prediction-residual RMS in Normal/Pick/Put intervals and measures model surprise, but it needs an exact pooling rule and is less directly tied to threshold crossing than Score.
- **User answer:** 1
- **Explicit rationale:** No separate rationale was stated; the selected option is the recommended metric most directly tied to existing detector separability.
- **Resulting impact:** DEC-001 refines REQ-001 with the Detector Score peak, shared non-Collision/non-Ignore Score RMS, and `20 * log10` dB formula; OD-001 is resolved.

### DISC-002: Collision-count and column presentation

- **Situation:** Recordings normally have three collision intervals, but the domain model permits other counts. Fixed or dynamic columns can make the table wider or hide extra evidence.
- **Question:** Should the table use three fixed SNR columns, one combined SNR column containing all events, or a dynamic number of columns?
- **Options and tradeoffs:** Option 1 makes three event positions easy to compare but widens the table and needs a secondary mechanism for extras. Option 2 uses one compact column with every value in chronological order, handles any count truthfully, and avoids hidden evidence, but cross-row event-position comparison is less direct. Option 3 exposes every event in its own column but changes the table structure after different runs and produces unstable width.
- **User answer:** 2
- **Explicit rationale:** No separate rationale was stated; the selected option preserves every collision value in one stable column.
- **Resulting impact:** DEC-002 refines REQ-001 and AC-001 with one `Collision SNR (dB)` column, chronological ` / ` separation, complete variable-count display, and `N/A` for zero intervals; OD-002 is resolved.

### DISC-003: Zero and unavailable SNR values

- **Situation:** The dB ratio is not a finite real number when signal or noise is zero, non-finite, or unavailable. Displaying infinity is mathematically explicit, while epsilon substitution fabricates a finite measurement.
- **Question:** Should exceptional ratios display infinity where defined, display `N/A`, or use an epsilon floor?
- **Options and tradeoffs:** Option 1 distinguishes positive/negative infinity but exposes hard-to-interpret UI values. Option 2 displays `N/A` for any ratio that cannot be formed from finite positive amplitudes, avoids fabricated measurements, and preserves valid sibling values, but does not distinguish zero noise from zero signal. Option 3 always displays a finite result but makes the value depend on an arbitrary floor.
- **User answer:** 2
- **Explicit rationale:** No separate rationale was stated; the selected option avoids fabricated finite values and unstable infinity presentation.
- **Resulting impact:** DEC-003 refines REQ-001 and AC-001 with per-collision `N/A` behavior and resolves OD-003. The change set is decision-complete.

## Revision History

| Revision | Date | Change |
|---|---|---|
| 1 | 2026-09-01 | Started the governed change set and recorded the two unresolved SNR presentation decisions. |
| 2 | 2026-09-01 | Selected Detector Score SNR and recorded its exact signal, noise, and dB definition. |
| 3 | 2026-09-01 | Selected one combined chronological SNR column that displays every collision interval. |
| 4 | 2026-09-01 | Defined `N/A` for zero, non-finite, or unavailable signal/noise and completed all decisions. |
| 5 | 2026-09-01 | Recorded implementation PASS evidence. |
