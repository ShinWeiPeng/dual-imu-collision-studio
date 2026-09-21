---
spec_version: 1
spec_id: SPEC-0018
revision: 7
status: confirmed
change_set: qualification-tie-optimization
---

# Qualification tie optimization

## Problem

Fine search can retain hundreds of distinct parameter configurations whose losses tie after four-decimal half-up rounding. Each retained parameter currently contributes its two lowest rounded Kernel Loss folds plus second-place ties to Qualification. The run qualifies every admitted fold kernel before evaluating the fallback transition, making a final round appear stuck and consuming disproportionate runtime.

## Solution

Keep raw Loss calculation unchanged. Replace four-decimal Parameter Loss tie admission with a relative window anchored at the minimum raw Parameter Loss: retain a parameter when `raw_loss <= best_raw_loss * (1 + convergence_tolerance_percent / 100)`. For each retained parameter, admit only folds whose raw Kernel Loss equals that parameter's minimum raw Kernel Loss; admit every exact raw minimum tie. Complete Qualification for every admitted parameter/fold before ranking and do not stop on the first full-range PASS. Expose parameter/fold identity and completed/total progress. Collect reproducible before/after timing and work-count evidence on a fingerprinted real dataset in addition to synthetic regression fixtures. Because parameter and fold admission semantics change, report work, timing, memory, and result differences descriptively without a fixed performance pass threshold; functional correctness remains independently pass/fail validated.

## User Stories

- As an analyst, I can complete optimization without disproportionate repeated Qualification work.
- As an analyst, I can tell whether Qualification is progressing and how much work remains.
- As an analyst, I retain an explicitly agreed level of model-selection quality and reproducibility.
- As a developer, I can compare baseline and modified performance on representative real recordings.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | The optimizer shall leave raw Parameter Loss calculation unchanged and retain for Qualification exactly the valid parameters whose raw Loss is no greater than `best_raw_loss * (1 + convergence_tolerance_percent / 100)`. |
| REQ-002 | Qualification progress shall expose the current parameter/fold identity and completed/total work. |
| REQ-003 | For each retained ParameterPoint, Qualification shall admit every fold whose raw Kernel Loss exactly equals that parameter's minimum raw Kernel Loss and no other fold; rounded Kernel Loss, second place, and near ties shall not affect fold admission. |
| REQ-004 | Qualification shall complete every admitted parameter/fold kernel before ranking and shall not stop at the first full-range PASS. |
| REQ-005 | Performance validation shall compare baseline and modified implementations using the same fingerprinted real dataset, settings, seed, machine/runtime environment, three bounded repeated runs, and captured parameter count, admitted fold count, Qualification wall time, total run wall time, peak RSS, and selected result summary. |
| REQ-006 | The benchmark shall report absolute and relative differences in admitted Qualification fold count, median Qualification wall time, total run wall time, peak RSS, and selected result summary without applying a fixed performance PASS threshold; functional tests shall independently determine algorithm correctness. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Replace minimum four-decimal Parameter Loss tie admission with a relative window using the existing convergence tolerance percentage; do not modify the fitted model or raw Loss calculation. | The user selected option 1 after confirming that the change narrows tie eligibility rather than artificially lowering Loss. At Loss near 0.0038, the former 0.0001 bucket spans about 2.63%, far wider than the configured 0.1% convergence tolerance. |
| DEC-002 | Complete Qualification for all parameters admitted by the relative 0.1% window, then apply the existing result ranking; do not use first-PASS early stopping. | The user explicitly adopted this behavior, preserving deterministic comparison among the narrowed parameter set. |
| DEC-003 | Compare fold kernels using raw Kernel Loss, admit all folds exactly equal to the minimum raw Kernel Loss for that parameter, and reject all other folds. | The user corrected the earlier one-fold rule: only minimum Kernel Loss matters, and all exactly equal minima must enter Qualification. |
| DEC-004 | Add a reproducible before/after benchmark based on real project recordings, alongside deterministic synthetic tests. | The user explicitly requested collecting real data for benchmark calculation. |
| DEC-005 | Use a measurement-only real-data benchmark with no fixed performance improvement threshold. | The user changed the selection from option 1 to option 3 because the admission-threshold change produces a different candidate set and therefore should not be treated as an equivalent-result performance comparison. |

## Discussion Context

### DISC-001: Parameter Loss tie admission
- **Situation:** Four-decimal half-up rounding can group hundreds of parameters even when their raw Loss differs by more than the optimizer's convergence tolerance.
- **Question:** Should the final Parameter tie set use a relative Loss window, a fixed top-K cap, or preserve all four-decimal ties?
- **Options and tradeoffs:** A relative window aligns admission with the existing tolerance but changes the legacy selected set; top-K provides a hard bound but introduces an arbitrary cap; preserving every four-decimal tie keeps compatibility but does not control the observed workload.
- **User answer:** Adopt option 1, the relative Loss tolerance.
- **Explicit rationale:** The user first verified that this does not make Loss smaller; it only changes which parameters remain eligible.
- **Resulting impact:** DEC-001 closes OD-001 and defines REQ-001 using the existing convergence tolerance percentage.

### DISC-002: Qualification completion after narrowing Parameter ties
- **Situation:** First-PASS early stopping would reduce runtime further but would make the selected result depend on evaluation order and could skip a shorter-tap or lower-latency candidate.
- **Question:** Should all relative 0.1% Parameter ties finish Qualification before ranking?
- **Options and tradeoffs:** Completing all admitted candidates preserves deterministic ranking at some remaining cost; first-PASS stopping minimizes time but weakens result selection; conditional pruning adds complexity.
- **User answer:** Adopt completing all relative 0.1% ties before ranking.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-002 closes OD-002 and defines REQ-004.

### DISC-003: Fold kernels admitted per retained parameter
- **Situation:** Current selection admits two best rounded Kernel Loss folds plus second-place ties, multiplying Qualification work after Parameter tie admission.
- **Question:** How many fold kernels should each retained parameter contribute?
- **Options and tradeoffs:** Keeping the current set retains more representatives but multiplies Qualification; exactly one reduces work most but discards exact equal minima; selecting exact raw minima retains indistinguishable best folds without admitting rounded or second-place near ties.
- **User answer:** Compare only minimum Kernel Loss; if all are equal, all enter Qualification.
- **Explicit rationale:** The ordinary case materially reduces fold count while preserving every truly equal minimum.
- **Resulting impact:** DEC-003 replaces the earlier exactly-one interpretation, closes OD-004, and defines REQ-003.

### DISC-004: Real-data performance evidence
- **Situation:** Synthetic fixtures prove selection semantics but may not represent the observed Qualification duration and candidate distribution.
- **Question:** Should validation also collect real-data timing benchmark evidence?
- **Options and tradeoffs:** Real-data before/after runs cost more execution time but measure the actual workflow; synthetic-only evidence is faster but cannot support a representative timing claim.
- **User answer:** Also collect real data to calculate the benchmark.
- **Explicit rationale:** The user wants the performance conclusion grounded in representative data.
- **Resulting impact:** DEC-004 defines REQ-005.

### DISC-005: Performance acceptance threshold
- **Situation:** The proposed implementation changes which parameters and folds enter Qualification, so the before and after runs do not evaluate identical candidate sets.
- **Question:** Should the real-data benchmark enforce a fixed improvement threshold or report descriptive measurements only?
- **Options and tradeoffs:** A fixed threshold enables a performance PASS/FAIL claim but may imply stronger result equivalence than the changed algorithm provides; measurement-only evidence still compares workload and elapsed time under identical data/settings while avoiding that claim.
- **User answer:** Change to option 3, measurement only.
- **Explicit rationale:** After changing the admission threshold, the user considers a fixed equivalent-result comparison inappropriate.
- **Resulting impact:** DEC-005 closes OD-003 and changes REQ-006 and AC-004 to require complete descriptive evidence without a performance PASS threshold.

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | A deterministic fixture with best raw Loss `0.0037980` retains `0.0038005` at a 0.1% tolerance and rejects `0.0038100` and `0.0038490`; raw Loss values remain unchanged. | Focused optimizer regression test. | PASS: `test_fixed_parameter_selection_uses_relative_raw_loss_window` and `test_optimized_parameter_selection_uses_relative_raw_loss_window`; full suite 402 passed. |
| AC-002 | REQ-002 | A tie-heavy fixture reports monotonic completed/total Qualification progress with parameter and fold identity. | Controller/progress regression test. | PASS: pre-replay and completion progress are covered by `test_all_selected_fold_kernels_reach_qualification_without_refit`; rendered work text is covered by `test_qualification_log_exposes_parameter_fold_and_completed_total_work`. |
| AC-003 | REQ-003, REQ-004 | A fixture qualifies only the raw minimum Kernel Loss fold for each parameter, qualifies every exact raw minimum tie, rejects rounded and second-place near ties, completes every admitted parameter, and does not terminate on an earlier PASS. | Learning-plan integration regression test. | PASS: `test_fold_selection_keeps_only_exact_raw_minimum_kernel_loss_ties` and `test_all_selected_fold_kernels_reach_qualification_without_refit`; full suite 402 passed. |
| AC-004 | REQ-005, REQ-006 | A machine-readable benchmark artifact from the same fingerprinted real dataset and environment contains all three baseline and modified runs, absolute and relative admitted-fold, Qualification-time, total-time, and peak-RSS comparisons, selected-result summaries, and an explicit `MEASUREMENT_ONLY` performance verdict; artifact completeness, not improvement magnitude, determines PASS. | Reproducible benchmark command with per-run and aggregate JSON output. | PENDING MEASUREMENT: runner and report-contract tests pass; real project copy loads 8 recordings and 216,611 rows with fingerprint `sha256:1a2b892f8d0f2076fd158c9e2b772555dafdb72ea7bd48aaabeac659052e4bbf`. The required three baseline and three modified runs have not completed; the observed legacy run exceeded 21 hours. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0011 |
| REQ-001 | depends_on | DEC-001 |
| REQ-002 | refines | SPEC-0011 |
| REQ-003 | refines | SPEC-0011 |
| REQ-003 | depends_on | DEC-003 |
| REQ-004 | depends_on | DEC-002 |
| REQ-005 | depends_on | DEC-004 |
| REQ-006 | depends_on | DEC-005 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |
| AC-003 | depends_on | REQ-003 |
| AC-003 | depends_on | REQ-004 |
| AC-004 | depends_on | REQ-005 |
| AC-004 | depends_on | REQ-006 |

## Out of Scope

- Replacing FIR/Ridge fitting with Adam, RMSProp, or another gradient optimizer unless later evidence shows a separate fitting bottleneck.
- Changing collision detection correctness, the inclusive 150 ms deadline, or supplied-speed/offset qualification coverage.
- Uploading real recordings or benchmark artifacts to an external service.

## Open Decisions

None.

## Routing/Gates

- Governed route: grilling, then spec-governance, then clarify-improvement-proposals.
- Required implementation gates: architecture governance, TDD, performance evidence, architecture CLI development gate, and code review.
- Product implementation was authorized by the user's `開始執行`; status remains `confirmed` until the required real-data benchmark evidence completes.

## Revision History

| Revision | Change |
|---|---|
| 0 | Started the tie-heavy Qualification improvement interview from the observed Round 4.1 behavior. |
| 2 | Adopted relative Parameter Loss tie admission using the existing convergence tolerance and closed OD-001. |
| 3 | Required every admitted Parameter tie to finish Qualification and initially interpreted fold admission as exactly one per parameter. |
| 4 | Corrected fold admission to all exact raw Kernel Loss minima and added a fingerprinted real-data before/after benchmark requirement. |
| 5 | Adopted the balanced quantitative performance threshold and closed the final open decision. |
| 6 | Replaced the fixed performance threshold with a measurement-only benchmark because admission semantics change the compared candidate set. |
| 7 | Recorded implementation authorization and functional PASS evidence while keeping AC-004 pending until the bounded real-data 3+3 benchmark completes. |
