# ALG-001: Full 3x3 MIMO FIR Ridge learning

Status: approved by confirmed SPEC-0001 and refined by confirmed SPEC-0007

## Purpose and owner

`learning_qualification` owns deterministic non-collision robot-motion model fitting and full-recording target replay. The model predicts the three External IMU axes from the three Internal IMU axes with a causal full 3x3 FIR. Cycle-contained Normal Robot Motion, Robot Pick, and Robot Put enter fitting. Fork Collision, Ignore, Cycle-external samples, invalid samples, discontinuity-crossing support, and cross-Cycle support never enter fitting.

## Inputs and output

Inputs are immutable Cycle-grouped eligible source-scale samples, complete recording arrays with acquisition-discontinuity markers, one confirmed sample rate, active minimum Robot Speed, requested histories `{4, 8, 16, 32}` ms, Ridge alpha grid `{1e-6, 1e-4, 1e-2, 1, 100}`, residual estimator grid `{STD, MAD}`, robust K grid `{4, 6, 8}`, score grid `{MAX_ABS, L2_NORM}`, confirmation grid `{1_OF_1, 2_CONSECUTIVE, 2_OF_3}`, and thresholds `5.00..20.00` inclusive by `0.50` under SPEC-0008 revision 5. See ALG-0004 for pooled Offset/speed progression and qualified ranking.

The output is a frozen source-scale candidate: requested-history aliases, effective history, tap count, 9L weights in `[output][input][lag]` order, three biases, fit provenance, residual centers/scales, robust K, score mode, confirmation mode, and threshold.

## Semantics

For requested history `H` and sample rate `fs`, `L = floor(H * fs / 1000) + 1`; lag zero is the current sample and `effective_history_ms = 1000 * (L - 1) / fs`. Duplicate requested histories with the same `L` execute once and retain ordered aliases.

Each fold standardizes every FIR feature with fitting-row population mean and standard deviation. A shared Ridge alpha minimizes mean squared prediction loss plus `alpha * ||W||²` in standardized space. Selection first minimizes the worst active-condition held-out loss, then pooled held-out loss, then declared alpha order. Cycle is the minimum indivisible group; fold count is `min(5, smallest eligible cycle count)` and must be 3..5. Contiguous Normal/Pick/Put samples may share FIR history inside a Cycle, while Collision, Ignore, Cycle-external gaps, and acquisition discontinuities split fitting support.

Target replay applies the frozen source-scale coefficients to each complete continuous recording segment. Annotation boundaries do not affect arithmetic validity. The first `tap_count - 1` samples at recording start and after every acquisition discontinuity are non-finite warm-up evidence; all later prediction, residual, normalized residual, detector score, ratio, state, and trigger values are computed. Detector confirmation, latch, and release state continue through Ignore. Qualification excludes Ignore, recognizes each collision only through its inclusive 20 ms acceptance window, and counts every other non-collision trigger in Normal/Pick/Put or Cycle-external evidence; Cycle-external triggers aggregate into `normal_false_events`.

Every fold and final fit performs one initial fit and exactly one robust refit. Residual cutoffs are `median(score) + K * MAD(score)`. Seeded rows reject output/tap support overlap without fixed-time dilation; rejection is capped at the deterministic worst 5 percent. Final standardized weights and biases are algebraically transformed to source scale.

Per residual axis, STD uses population mean/population standard deviation. MAD uses median and the specification's declared normal-consistency multiplier. Non-finite values and scales at or below the exact machine-epsilon degeneracy limit make the candidate ineligible; no floor or axis omission is allowed.

## Complexity and evidence

Feature construction and full replay are `O(N * 3L)`. Ridge solves a bounded `(3L) x (3L)` system for each fold/alpha. Qualification computes each fixed model/recording score array once and reuses it across the Threshold/Confirmation grid as governed by `architecture/algorithms/ALG-0002-qualification-replay-score-cache.md`. Memory is preflight-capped at 60 percent of available RAM, with one target-type score value per supplied sample plus at most 10 MiB cache bookkeeping for the active model. Required evidence includes history/tap properties, fitting eligibility and gap-split tests, fold leakage tests, Ridge references, robust-refit spies, source-scale equivalence, deterministic identity, full-recording warm-up/discontinuity assertions, Ignore state continuity, non-Ignore qualification counts, shortage/degeneracy provenance, cached/uncached same-grid equivalence, and bounded cache lifetime.
