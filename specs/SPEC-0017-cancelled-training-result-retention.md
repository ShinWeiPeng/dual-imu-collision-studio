---
spec_version: 1
spec_id: SPEC-0017
revision: 3
status: implemented
change_set: cancelled-training-result-retention
---

# Retain usable Training results after cancellation

## Problem

Cancelling an active Training run currently raises an interruption and discards the run-local `QualificationResult`. Even if one or more kernels have already completed Qualification, the cancelled run leaves no retained candidate for Analytical Replay.

## Solution

When cancellation is observed, return a deterministic partial result containing only candidates whose fitting and Qualification work completed before the cancellation boundary. If at least one completed candidate is qualified, retain all completed qualified candidates for Replay. If none is qualified, minimize total errors (`false trigger count + missed collision count`), then prefer the lowest finite worst collision latency, and retain all remaining exact ties. Keep cancellation visibly distinct from successful completion, and never fabricate a result from an incomplete candidate.

## User Stories

- As a user who cancels a long Training run, I can inspect already completed useful evidence in Analytical Replay instead of losing all completed work.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | On user cancellation, preserve candidates only after their complete frozen model and Qualification evidence have been produced; discard incomplete fitting, fold, recording, threshold, or candidate work. |
| REQ-002 | If the partial result contains one or more completed qualified candidates, retain all those qualified candidates and expose them through the existing Candidate Dashboard and Analytical Replay selection paths. |
| REQ-003 | If the partial result contains no qualified candidate, rank completed diagnostic candidates by the minimum sum of false triggers and missed collisions; among that minimum-error set, prefer the lowest finite worst collision latency when finite latency evidence exists, and retain all exact remaining ties in stable order. Expose the retained diagnostic candidate or candidates through the existing diagnostic-only Replay path. |
| REQ-004 | A retained partial result shall remain visibly `Cancelled`; it shall not be reported as `Complete`, and diagnostic-only candidates shall remain non-exportable under the existing export policy. |
| REQ-005 | If cancellation occurs before any candidate completes Qualification, retain no candidate and preserve the existing no-result cancelled behavior. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | The atomic retention boundary is a fully qualified candidate, not a partially processed fold, recording batch, threshold, or candidate. | Replay requires a frozen model, detector configuration, and complete recording Qualification evidence; retaining a smaller unit would create incomplete or misleading evidence. |
| DEC-002 | Cancellation remains a distinct terminal run state even when usable partial results are retained. | The user cancelled before the planned search completed, so the UI must not imply that the full fallback search completed. |
| DEC-003 | Preserve all completed qualified candidates already retained by the run. | The request explicitly asks to preserve candidates that have passed Qualification, and existing Replay already supports selecting among multiple retained kernels. |
| DEC-004 | When none qualifies, minimize total errors, then finite worst collision latency, and keep exact ties. | The user selected option 1; this preserves the application's existing completed-run diagnostic ranking and balances false triggers with missed collisions. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-005 | Cancelling before the first complete candidate yields `Cancelled` with no Replay kernel; cancelling after one candidate but during later work retains only the earlier complete candidate. | Domain service cancellation tests at deterministic work boundaries. | PASS — pre-candidate, completed-candidate, and intra-fold cancellation tests; full suite 397/397. |
| AC-002 | REQ-002, REQ-004 | A cancelled run with completed qualified candidates remains visibly `Cancelled`, lists all those kernels as qualified, and allows selecting each in Analytical Replay without changing qualified exportability. | Controller and Replay regression tests. | PASS — two qualified cancelled kernels verified selectable in Replay and exportable after selection; full suite 397/397. |
| AC-003 | REQ-003, REQ-004 | A cancelled run with no qualified candidate lists only the minimum-total-error diagnostic winner(s), applies finite worst-latency tie-breaking, preserves exact ties, allows Replay, and keeps them non-exportable. | Domain ranking and controller/Replay tests. | PASS — loser exclusion, finite-latency preference, stable exact ties, Replay selection, and non-exportability verified; full suite 397/397. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| DEC-001 | refines | REQ-001 |
| DEC-002 | refines | REQ-004 |
| DEC-003 | refines | REQ-002 |
| DEC-004 | refines | REQ-003 |
| AC-001 | depends_on | REQ-001 |
| AC-001 | depends_on | REQ-005 |
| AC-002 | depends_on | REQ-002 |
| AC-002 | depends_on | REQ-004 |
| AC-003 | depends_on | REQ-003 |
| AC-003 | depends_on | REQ-004 |

## Out of Scope

Do not resume a cancelled search, persist incomplete numerical work, change Qualification criteria, change detector arithmetic, promote diagnostic-only kernels to exportable profiles, or report cancellation as successful completion.

## Open Decisions

None.

## Routing/Gates

ask-matt -> grilling -> spec-governance; implementation requires architecture governance, TDD, controller/Replay validation, and code review. Product mutation requires exact `開始執行` authorization after this specification is confirmed.

Spec review: PASS. Standards review: PASS. Architecture development and release gates: VERIFIED PASS.

## Revision History

| Revision | Date | Change |
|---|---|---|
| 1 | 2026-09-01 | Started the governed change set from the requested cancelled-Training retention behavior and repository evidence. |
| 2 | 2026-09-01 | Selected total-error diagnostic ranking, finite latency tie-breaking, and exact-tie retention. |
| 3 | 2026-09-01 | Implemented complete-candidate cancellation retention, Replay exposure, qualified export preservation, diagnostic ranking, and verified all acceptance criteria. |

## Discussion Context

### DISC-001: Diagnostic fallback ranking after cancellation

- **Situation:** A cancellation can occur after completed candidates exist but before any candidate satisfies the full qualified coverage envelope. Those candidates have both false-trigger and missed-collision evidence, and the existing completed-run diagnostic path already combines them.
- **Question:** When no completed candidate qualifies, how should the retained diagnostic candidate or candidates be ranked?
- **Options and tradeoffs:** Option 1 minimizes total errors (false triggers plus missed collisions), then finite worst collision latency, retaining exact ties; it is consistent with the existing diagnostic path and balances both failure classes. Option 2 prioritizes false triggers before missed collisions and can retain a model that misses more collisions. Option 3 considers only false triggers and can ignore materially different collision detection performance.
- **User answer:** 1
- **Explicit rationale:** No separate rationale was stated; the selected recommended option reuses the existing diagnostic ranking and considers both false alarms and missed collisions.
- **Resulting impact:** DEC-004 resolves OD-001; REQ-003 and AC-003 now define the exact diagnostic ranking and tie behavior.
