---
spec_version: 1
spec_id: SPEC-0009
revision: 39
status: confirmed
change_set: score-derived-threshold-range
---

# Score-derived threshold range

## Problem

The implemented threshold grid is fixed at 5 through 20. The user wants a range derived from labeled evidence, not the entire recording indiscriminately. The user additionally requests actual numeric FIR startup output instead of intentional warm-up NaN placeholders, and interpolation of timestamp gaps at Import with visible identification during annotation validation.

## Solution

Compute the frozen model scores first, derive threshold bounds from labeled Normal Robot Motion and Robot Fork Collision evidence, then run Qualification. For each eligible Normal Robot Motion interval, take its maximum Score, then set the Normal lower-bound reference N to the maximum of those interval maxima so no candidate threshold is below the largest observed Normal fluctuation. For each eligible Robot Fork Collision response window, take its maximum Score, then set the Collision upper-bound reference C to the minimum of those window maxima so a candidate does not exceed the weakest labeled Collision peak. Normal Robot Motion supplies the lower search bound and Robot Fork Collision supplies the upper search bound. Each Collision maximum uses its onset-through-150-ms response window, including the deadline, rather than its full manually selected annotation duration; an earlier annotation end does not shorten this window. The search includes both endpoints N and C subject to the positive-threshold exception in DEC-017: when N=0, omit only the zero candidate, keep all positive grid candidates, and skip model Qualification if none remain. Candidate thresholds start at N and advance in 0.5 increments while remaining within [N,C]; append C if the increments do not reach it. Include each represented threshold once. Derive the bounds separately for each frozen model using only supplied recordings whose Speed and Offset are both active in the current fallback round. Pick/Put do not contribute to these bound calculations and retain their existing downstream Qualification checks. When C < N, record an empty threshold range and skip Qualification for that frozen model. Continue other models; if the whole round has no candidate, continue the existing fallback sequence while retaining earlier qualified kernels. The change set also covers numeric FIR warm-up output and derived import-gap interpolation with annotation-validation provenance. Initialize missing FIR startup history to zero and compute from the first sample. Startup Scores participate normally in threshold-bound estimation and Qualification under the existing annotation and active-round scope, without a warm-up exclusion. For repairable timestamp gaps, interpolate each of the six raw IMU axes linearly in time between the bracketing measured samples, retaining derived-sample provenance. Use the sample rate to count consecutive missing samples: interpolate gaps of one through three missing samples, and reject the entire recording if any gap contains four or more consecutive missing samples. This supersedes the earlier fixed 3-ms endpoint limit. After a short gap is successfully interpolated, feed its inserted samples into FIR in timestamp order and preserve the existing FIR history across the repaired region; do not zero-restart it. Interpolated data participate normally in Training, N/C search and Qualification according to existing activity roles, with repair provenance retained. Successfully repaired spans do not introduce an artificial FIR or detector reset. For timestamp gaps, choose the nearest integer number of nominal sample periods between measured endpoints, subtract one to count missing samples, and equally subdivide the measured interval when the missing count is one through three. Each repaired period must be within the existing inclusive +/-2% tolerance of the nominal period; otherwise reject the recording. Original measured timestamps remain unchanged. During annotation validation, display interpolated locations and inserted-sample counts, retain the existing annotation confirmation operation, and add no separate per-gap approval. Save enough project provenance to restore the markers after reopening with the unchanged source available. Old-project compatibility, migration, annotation conversion and legacy-result conversion are out of scope under DEC-020. New-contract project save/reopen restoration remains required. The user rejected treating a Collision window fully masked by Ignore as a reason to skip model Qualification: that annotation arrangement must be rejected during annotation validation per REQ-010. Any overlap of Ignore with a Collision annotation interval prevents annotation confirmation and Start Learning. Use existing half-open interval membership, so adjacency is permitted. This rule does not extend the protected interval to the whole 150-ms response window or change Ignore overlap with Pick/Put. Do not require each recording to contain both Normal Robot Motion and Collision; aggregate eligible intervals across the active-round recordings under REQ-003. If the entire active round has no eligible Normal interval or no eligible Collision interval, record the missing threshold-search evidence class, skip Qualification for that round, continue existing fallback and retain earlier qualified results under REQ-011. Detector triggering uses the strict predicate Score > Threshold across Qualification, Replay, diagnostics and the exported profile semantic contract; therefore threshold=N is above every observed Normal value for triggering purposes because equality does not trigger. All decisions are resolved; implementation and validation remain pending.

The confirmed timing amendment uses a fixed absolute endpoint t0 + 150 ms for both C extraction and Qualification. Remove Ignore-covered samples from that window without compressing timestamps, pausing the clock, extending the endpoint, or truncating all samples after the first Ignore interval. A [60,90) ms Ignore span leaves [0,60) and [90,150] ms eligible. Detector/FIR state continues across Ignore under existing semantics. Actual Collision annotations remain subject to the existing non-overlap gate.

The latest Collision-bound amendment restores the weakest-Collision aggregation for constructing the candidate threshold range: C is the minimum of eligible per-window Collision peak Scores. Candidate Threshold values therefore never exceed the weakest labeled Collision peak. Qualification continues to require every labeled Collision to be detected within the existing 150-ms acceptance window.

The confirmed Normal-derivation amendment aligns annotation confirmation with that same response window. After an annotation set is confirmed, derived Normal Robot Motion excludes the complete fixed Collision response window from each Collision onset through onset plus 150 ms, inclusive at the deadline, rather than excluding only the manually selected Collision interval. The exclusion is clipped by the containing Cycle and stops at the first true acquisition discontinuity, matching the response-window boundary used by Learning. The artificial extension is derived and read-only: it does not rewrite the user's Collision annotation, change its visible end handle, or alter project persistence. Ignore samples retain their existing exclusion semantics. This prevents one post-annotation Collision-response sample from simultaneously supplying the Normal lower bound N while Qualification treats it as Collision acceptance evidence.

## User Stories

As a user, I want the threshold search range to reflect the labeled normal and collision scores.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Before Qualification candidate replay, compute N = max_i(max_t Score(NormalInterval_i,t)) and C = min_j(max_t Score(CollisionWindow_j,t)) with CollisionWindow_j defined in REQ-002; use N as the lower search-bound reference and C as the upper search-bound reference. Normal uses the maximum of per-interval maxima so the search does not begin below any observed eligible Normal fluctuation; Collision retains the minimum of per-window maxima so the upper bound does not exceed the weakest labeled Collision peak. Both N and C shall be included as candidate thresholds when a valid ordered search range exists, except that DEC-017 omits the zero candidate when N=0; grid construction must not omit any positive endpoint through rounding. For valid ordered bounds, generate N + 0.5*k for nonnegative integers k while the value is at most C, then append C if it has not already been included; do not exceed C or round away either endpoint. Emit unique candidate thresholds in ascending order, with no repeated endpoint. Use the round scope defined by REQ-003. Apply REQ-004 when C < N or no positive candidates remain under DEC-017. For finite nonnegative ordered bounds with N=0, build the same N-anchored grid plus C, then omit zero without shifting the grid or inventing an epsilon threshold; retain all positive candidates. Apply REQ-011 when the entire active round lacks a required evidence class. Invalid annotations are rejected by REQ-010 and existing annotation validation. Genuine non-finite arithmetic/model/input errors are not missing-class evidence and must not be hidden by dropping affected required intervals, substituting zero, fabricating bounds or using the missing-evidence fallback. Threshold N remains an included candidate under REQ-013 because Score equal to Threshold does not trigger; this search range is not a Qualification PASS or a guarantee of zero false triggers. |
| REQ-002 | For each confirmed Robot Fork Collision onset t0, derive its maximum Score from samples in [t0, t0 + 0.150 s], including exactly 150 ms under REQ-012. The annotation end neither shortens this response window nor permits sampling after its deadline. Use the same 150-ms Qualification deadline and preserve existing threshold/confirmation/re-arm rules; startup eligibility is defined by REQ-005 and interpolated-data eligibility by REQ-008. Use valid non-Ignore samples in the response window and preserve existing true-discontinuity boundaries for replay/diagnostic inputs; newly imported gaps obey REQ-006. The invalid Collision/Ignore annotation arrangement is rejected before Learning per REQ-010 rather than used to skip model Qualification. A valid nonempty Collision annotation includes its non-Ignore onset sample; REQ-005 and REQ-008 remove intentional startup/repaired-gap exclusions. A missing required evidence class across the whole active round follows REQ-011. Genuine numerical errors remain errors rather than absent-class fallback. Interpolated values must remain identified as derived data under REQ-006, never represented as original measured samples. |
| REQ-003 | For each frozen model and current fallback round, compute N and C only from the corresponding Normal Robot Motion intervals and Collision response windows in supplied recordings whose Robot Speed belongs to that round's training_speeds and whose Collision Offset belongs to active_offsets. Excluded speeds or offsets must not influence either bound. Do not invent unsupplied Speed/Offset combinations. Aggregate each evidence class across the eligible recordings; a single recording need not contain both Normal Robot Motion and Collision. Do not add a per-recording dual-class annotation-confirmation or Start Learning gate. One eligible recording may supply Normal intervals while another supplies Collision intervals. This does not change existing fitting eligibility, annotation geometry, or downstream Qualification coverage/pass-fail checks. Preserve existing all-recording Score/replay evidence and out-of-range diagnostic behavior; restricting bound evidence does not remove recordings from replay. Pick/Put remain downstream Qualification checks and are not additional inputs to the two-class bound formulas. |
| REQ-004 | If computed finite bounds satisfy C < N, do not generate detector configurations or perform Qualification detector replay for that frozen model. Record the model/round, N, C and an empty-threshold-range reason. Continue other eligible models in the same round. If the round has no candidate after all models are handled, continue the existing ordered fallback sequence and retain earlier qualified kernels. Do not swap bounds, expand them, revert to the legacy fixed grid or fabricate a failed/qualified candidate. Equal positive bounds retain the one-value closed interval. Under DEC-017, if filtering zero from an N=0 range leaves no positive candidates, skip model Qualification, record N/C and the no-positive-threshold-candidates reason, and apply the same other-model/fallback/previous-kernel-retention behavior. N=C=0 therefore skips the model; do not pass zero to the detector or fabricate candidates. |
| REQ-005 | For finite valid inputs and a valid model, compute actual FIR startup prediction/residual/Score values with all unavailable pre-recording Internal IMU history taps initialized to zero in source units and the selected target numeric type instead of intentionally leaving warm-up output as NaN solely because pre-recording history is unavailable. At sample zero, use the current measured Internal IMU vector for lag zero and zeros for older taps; retain the model weights and biases unchanged. Later samples replace the zero history naturally with measured values. Do not zero the measured External IMU or override the FIR prediction with zero. Startup Scores, including zero-initialization transients, shall participate normally in N/C bound estimation wherever the existing activity/window and active-round scope selects those samples, and in detector replay/Qualification under the existing evaluation rules. Do not add a warm-up exclusion, suppress startup triggers, or replace startup scores merely because full measured history is not yet accumulated. Existing confirmation modes still determine the first possible trigger. This decision does not independently change FIR fitting-row eligibility. FIR history continuity across successfully interpolated gaps follows REQ-007; detector-state and analytical-evidence treatment follow REQ-008. This requirement does not authorize hiding genuine arithmetic errors or replacing every NaN/Inf with a fabricated finite value. |
| REQ-006 | During Import, fill repairable timestamp gaps with derived samples obtained by independent time-linear interpolation of Internal X/Y/Z and External X/Y/Z. For each inserted time t between bracketing measured times t_left < t_right, each axis value is v_left + (v_right - v_left) * (t - t_left) / (t_right - t_left). Preserve bracketing measured values and visibly identify inserted locations during annotation validation. Interpolate raw IMU values, not model predictions, residuals or Scores; downstream model arithmetic computes those derived quantities. Preserve original source-file contents and distinguish inserted/interpolated samples from measured rows. Determine the number m of consecutive missing samples from the sample period T=1/fs and the measured timestamps. For exact grid-aligned endpoints, m=(t_right-t_left)/T-1; do not count the right measured endpoint as missing. With timestamp jitter, let q=(t_right-t_left)/T, choose its nearest integer n, and use m=n-1. Preserve the existing nominal sample-rate determination. For m=1, 2 or 3, insert times t_left+k*(t_right-t_left)/n for k=1 through m, preserving both measured endpoint times and values. The repaired period d=(t_right-t_left)/n must satisfy abs(d-T)/T <= 0.02; otherwise reject the entire recording. Do not force-fit a noncompliant gap by moving measured timestamps, choosing a different count or using a larger tolerance. The missing-count rejection at m>=4 takes precedence over successful period alignment. Half-integer counts near the repairable range cannot satisfy the 2% check and are rejected regardless of tie rounding; do not silently admit ambiguous gaps. A bounded gap with m=1, 2 or 3 may be linearly interpolated. Any gap with m>=4 shall reject the entire recording from the usable imported dataset, with recording/gap/count provenance; do not partly admit that recording, silently split it, or override the limit with a fixed millisecond cap. Preserve source bytes and do not reject unrelated valid recordings solely because another recording failed. Preserve FIR history across successfully interpolated gaps per REQ-007. Analytical eligibility and detector continuity follow REQ-008. Timestamp-grid construction/alignment tolerance follows DEC-018. Provenance presentation, confirmation and save/reopen restoration follow REQ-009. Old-project/result compatibility is out of scope under DEC-020. The request concerns time gaps and does not silently widen the separate invalid-cell repair policy. |
| REQ-007 | For a successfully interpolated gap of one through three missing samples, insert the derived samples into the FIR input sequence in chronological order and retain the preceding FIR history. Do not clear or zero-reinitialize FIR history at the first inserted sample or at the next measured sample after the repaired region. Repaired-sample provenance remains available independently of FIR continuity. This does not authorize interpolation of rejected gaps; detector state, fitting-row, threshold-bound and Qualification evidence eligibility follow REQ-008. |
| REQ-008 | Successfully interpolated samples and outputs influenced by their FIR history participate normally in Training, N/C calculation and Qualification according to the existing activity/annotation and active-round scope. Normal Robot Motion, Pick and Put remain eligible fitting activities inside confirmed Cycles under existing fitting rules; Collision, Ignore and Cycle-external samples do not become fitting data. N and C still use only their selected Normal and Collision evidence classes. Do not impose a synthetic-data-only exclusion or automatic Coverage Gap. Keep annotation confirmation and repair provenance; repaired spans may be crossed by otherwise valid annotations. Feed the repaired sequence through the ordinary detector confirmation/latch/re-arm logic without a reset or history clear solely because the samples were interpolated. Results describe the repaired supplied dataset, not proof of recovery of unobserved measured peaks. |
| REQ-009 | During annotation validation, visibly identify the locations of interpolated samples and the number of inserted samples. Use the existing annotation confirmation operation without adding a separate per-gap or per-sample interpolation acceptance requirement. Preserve derived-versus-measured identity. Saving and reopening a project created under the new rules with unchanged source data available must restore the same repair locations and counts, and preserve correspondence between the repaired sample timeline and annotations. Preserve the existing source-reference project design and source-integrity checks; do not embed raw waveforms or alter original source files to achieve restoration. Exact storage representation is an implementation detail subject to architecture governance. Old-project compatibility/migration and conversion of previously calculated legacy results are out of scope under DEC-020. This exclusion does not waive new-contract project round-trip correctness or authorize deletion/modification of old project files. |
| REQ-010 | Any overlap between an Ignore interval and a Robot Fork Collision annotation interval is invalid, including partial overlap or complete containment in either direction. Apply the existing half-open [Start,End) sample membership; touching boundaries with no shared sample remain valid. Identify conflicting annotations, prevent their confirmation and block Start Learning until corrected. Enforce this validity requirement for annotation creation/editing and every confirmation/progression path, retaining invalid drafts for correction under the existing workflow rather than automatically deleting or relabeling annotations. Do not defer the error to Qualification or handle it by skipping the frozen model. This restriction concerns the Collision annotation interval, not its extended onset-through-150-ms response window; preserve existing Ignore masking outside the annotation and existing Pick/Put overlap rules. No Score computation or detector-latency pass/fail check is required during annotation. |
| REQ-011 | If all supplied recordings eligible under REQ-003 collectively contain no eligible Normal Robot Motion interval or no eligible Robot Fork Collision interval, N or C cannot be formed. Mark that round as missing threshold-search evidence, identify the missing class or classes and the active Speed/Offset scope, generate no threshold candidates and perform no Qualification for that round. Continue the existing ordered speed/offset fallback and retain all previously qualified results. Do not fabricate zero/NaN bounds, revert to the old grid, import excluded-condition evidence, fabricate candidate outcomes, or impose a requirement that each recording contain both classes. Complementary evidence across eligible recordings is sufficient to attempt bound calculation. This is a class-absence condition, distinct from C<N or no positive threshold candidates under REQ-004, invalid annotation under REQ-010, and numerical/resource/unexpected execution errors, which retain their existing error classification rather than being converted to evidence shortage. |
| REQ-012 | Temporarily use one inclusive absolute onset-through-150-ms deadline for BOTH C peak extraction and Qualification collision detection/latency acceptance. Let W=[t0,t0+0.150 s] and I be the union of Ignore sample intervals; use W minus I for eligible collision evidence. Preserve timestamps and measure latency as the actual trigger time minus t0. Ignore neither pauses the clock nor extends or shortens the absolute endpoint. Retain eligible samples after Ignore ends within W. Ignore does not reset or pause FIR/detector state; preserve existing confirmation/re-arm semantics. The actual Collision annotation must still pass REQ-010, including partial-overlap rejection and half-open adjacency. Do not reject an otherwise valid annotation solely for Ignore overlap with the expanded response window. Keep N=max(Normal interval maxima), C=min(Collision window maxima), the positive threshold grid, C<N skipping and fallback unchanged. Update deadline-dependent result checks and visible policy wording; results under this policy must not be presented as satisfying 20 ms. |
| REQ-013 | Across Qualification, analytical Replay, diagnostic results and the exported profile semantic contract, a valid sample satisfies the detector threshold predicate only when `Score > Threshold`. Equality (`Score == Threshold`) shall not satisfy any confirmation slot. Apply the same strict predicate to `1_OF_1`, each sample of `2_CONSECUTIVE`, and each sample counted by `2_OF_3`. Keep the existing threshold positivity rule, confirmation history, latch behavior, collision ratio calculation, and re-arm condition `Score < release_ratio * Threshold` unchanged. This requirement supersedes only the inclusive `Score >= Threshold` comparator in SPEC-0001 REQ-004 and the corresponding algorithm descriptions; every runtime and exported consumer must use identical strict semantics. |
| REQ-014 | For candidate-range construction, supersede the Collision aggregation clauses of REQ-001 and REQ-012 and compute C = max_j(max_t Score(CollisionWindow_j,t)). Preserve N=max(Normal interval maxima), the existing active-round scope, [N,C] grid, strict `Score > Threshold`, empty-range handling and fallback. C=max is only a search upper bound and does not make a candidate qualified. Qualification shall retain the requirement that every labeled Collision is detected within the 150-ms acceptance window; a candidate missing any weaker Collision remains failed. Do not lower the required collision count, convert misses into warnings, or present C=max as a guarantee that all Collisions exceed a candidate threshold. |
| REQ-015 | When a recording's complete annotation set is confirmed, derive Normal Robot Motion as the portions of each confirmed Cycle that remain after subtracting every explicit event interval and every Collision response window `[t0, t0 + 0.150 s]`, including a sample exactly at the deadline. If a true acquisition discontinuity occurs after t0 and before the deadline, stop that Collision response exclusion at the discontinuity; never exclude beyond the containing Cycle. Use timestamps rather than assuming 150 samples. Preserve the manually selected Collision interval and its persisted start/end indexes unchanged: the added response exclusion is derived, read-only eligibility, not an annotation edit. Apply the resulting derived Normal intervals consistently to Learning fitting eligibility and N calculation. Qualification shall use the same response-window boundary so no sample can be both derived Normal evidence and Collision acceptance evidence for the same Collision. Ignore, Pick, Put, Cycle-external, confirmation, detector-state and re-arm rules remain otherwise unchanged. Reconfirming after annotation edits shall recompute the derived intervals deterministically. |
| REQ-016 | For candidate-range construction, supersede REQ-014 and restore C = min_j(max_t Score(CollisionWindow_j,t)). Each CollisionWindow uses the existing inclusive onset-through-150-ms boundary and Ignore subtraction. Preserve N=max(Normal interval maxima), active-round evidence scope, the N-anchored 0.5 candidate grid including positive endpoints, strict `Score > Threshold`, C<N/no-positive-candidate handling, fallback, and the requirement that Qualification detect every labeled Collision. Do not admit any candidate Threshold greater than the weakest eligible Collision-window peak. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Use activity-specific Score evidence for threshold bounds, not a recording-wide maximum combining all activities. | User explicitly corrected the interpretation. |
| DEC-002 | Apply minimum-of-interval-maxima aggregation independently to BOTH Normal Robot Motion and Robot Fork Collision; map them to lower and upper search-bound references respectively. Do not substitute maximum-of-normal-maxima. | User explicitly applied the selected phrase to both activity classes; no additional rationale supplied. |
| DEC-003 | Use the closed search interval [N,C], including both N and C as candidate thresholds subject to the zero-candidate exception in DEC-017. Interior grid construction is resolved by DEC-004. | User explicitly confirmed inclusion after the notation was explained. |
| DEC-004 | Start the threshold grid at N, retain spacing 0.5, and append C when the regular increments do not reach it; the final gap may be smaller than 0.5. Do not duplicate C when it is already a grid point. | User accepted this exact generation rule and the example 3.2, 3.7, 4.2, 4.4. |
| DEC-005 | Use each Collision onset-through-20-ms response window for its peak Score, inclusive of 20 ms; do not use the entire annotation when it extends later, or truncate the window when the annotation ends earlier. | User specified that Collision max Score can be sampled within 20 ms, selecting the response-window scope rather than the proposed full annotation scope. |
| DEC-006 | Use only the current round's still-active Speed and Offset data to derive N and C. Recompute bounds for each frozen model in that round; excluded conditions cannot constrain its threshold search. | User explicitly accepted the proposed current-round rule. |
| DEC-007 | C < N skips Qualification for that model; a round with no candidate advances through existing fallback and does not discard earlier qualified kernels. | User confirmed the explanation and explicitly stated that C < N needs no Qualification. |
| DEC-008 | Replace intentional FIR warm-up NaN placeholders with actual numeric computation; buffer initial values are resolved by DEC-010 and startup search/Qualification eligibility by DEC-011. | User annotated the explanation of deliberate warm-up NaNs and requested actual output values instead. |
| DEC-009 | Interpolate Import timestamp gaps and mark the affected locations during annotation validation; the interpolation method is defined by DEC-012 and the sample-count limit/rejection rule by DEC-014, which supersedes DEC-013; time-grid construction follows DEC-018 and analytical participation follows DEC-016. Provenance confirmation/persistence follows DEC-019; old-project/result compatibility is out of scope under DEC-020. | User annotated the accepted-and-marked time-gap behavior and requested interpolation plus annotation-validation marking. |
| DEC-010 | Select zero initialization for unavailable FIR startup history; compute numeric prediction/residual/Score from the first sample, without first-sample extension or invented real pre-history. | After comparing zero initialization, first-sample extension and real pre-roll, the user explicitly chose zero padding. |
| DEC-011 | Include zero-initialized startup Scores normally in threshold search and Qualification; do not create a separate warm-up exclusion. Preserve existing annotation, active-round, Ignore and confirmation-mode rules. | User explicitly stated that startup Scores participate normally in search and validation. |
| DEC-012 | Use time-linear interpolation independently for all six raw Internal/External IMU axes between measured samples bracketing a repairable timestamp gap. Keep inserted-sample provenance for annotation validation. | User explicitly accepted the proposed time-linear interpolation method and example. |
| DEC-013 | Superseded by DEC-014. Previously: limit time-gap interpolation to a measured-endpoint time difference of at most 3 ms, inclusive. Do not subtract the ordinary sample period or reinterpret the limit as three missing samples. Over-limit behavior remains unselected. | The user answered 3 ms to the question asking for the maximum elapsed time between the two measured samples bracketing the gap. |
| DEC-014 | Supersede the fixed 3-ms limit with a sampling-rate-dependent missing-sample count: linearly interpolate one through three consecutive missing samples; reject the recording at four or more consecutive missing samples. | User corrected the prior limit, stating it must depend on sample rate and that four consecutive missing samples reject the recording. |
| DEC-015 | Choose option 1: preserve FIR continuity across successfully interpolated short gaps; feed inserted samples normally without clearing history or restarting with zeros. | User selected option 1 from the FIR-history comparison. |
| DEC-016 | Choose option 1: interpolated data participate normally in Training, N/C calculation and Qualification under existing activity roles; retain interpolation markers. Together with DEC-015, process successfully repaired spans continuously without special detector resets or synthetic-only exclusions. | User selected option 1 from the analytical-use comparison after the effects of interpolation on validation evidence were explained. |
| DEC-017 | When N=0, omit threshold=0 and retain all positive candidates from the existing grid within [N,C]. If none remain, skip model Qualification and follow REQ-004 continuation/retention rules. This is the explicit zero-endpoint exception to DEC-003, not a change to the 0.5 grid or a relaxation of the detector threshold>0 contract. | User accepted the proposed zero-candidate exception and empty-positive-set model skip; no additional rationale supplied. |
| DEC-018 | Determine missing count from the nearest integer number of nominal sample intervals between measured endpoints; for one through three missing samples, equally divide the measured endpoint interval and require the repaired period to remain within the existing inclusive +/-2% tolerance. Reject misaligned recordings and retain the m>=4 whole-recording rejection. | User accepted the proposed alignment rule, including the 1000-Hz example with a 4.04-ms endpoint gap repaired into four 1.01-ms intervals. |
| DEC-019 | Show interpolation locations and inserted-sample counts during annotation validation; retain the original annotation confirmation operation without an additional per-gap confirmation. Save project provenance sufficient to restore these markers when reopening. | User accepted the proposed presentation, confirmation and persistence behavior; no additional rationale supplied. |
| DEC-020 | Exclude old projects from this change set: do not implement legacy project compatibility, migration, annotation remapping or conversion of legacy calculated results. Preserve the new-contract project save/reopen and interpolation-marker restoration requirements. | User explicitly said to disregard old projects instead of accepting the proposed old-project migration/recalculation workflow. |
| DEC-021 | Reject the proposed model-skip handling for a required Collision window wholly masked by Ignore; this must be an invalid annotation arrangement caught during annotation validation. The precise overlap restriction is resolved by DEC-022. | User stated that such a configuration is not allowed at labeling time, rejecting the preceding proposed Qualification fallback policy. |
| DEC-022 | Prohibit any Ignore overlap with the Collision annotation interval, block annotation confirmation and Start Learning, and retain existing half-open adjacency semantics. Do not extend the restriction to the full 20-ms response window or implicitly to other activity classes. | User explicitly agreed that any Ignore/Collision annotation overlap must block confirmation and Start Learning. |
| DEC-023 | Do not require every recording to contain at least one valid Normal Robot Motion interval and one Collision interval. Preserve the current-round aggregation of available class-specific evidence across recordings and existing independent validation/Qualification rules. | User rejected the proposed per-recording dual-class annotation gate with No need. |
| DEC-024 | When the whole active round lacks Normal or Collision threshold-search evidence, label the missing search evidence, skip that round's Qualification, continue the existing fallback and retain previous qualified results. | User agreed to this whole-round rule after rejecting the stricter per-recording dual-class requirement. |
| DEC-025 | Set BOTH C extraction and Qualification collision deadlines to 150 ms, inclusive, temporarily; supersede the 20-ms duration in DEC-005 without changing the onset reference or other timing-window rules. | User explicitly chose 150 ms for both uses rather than the suggested 100 ms. |
| DEC-026 | Automatically subtract Ignore-covered portions from the Collision response window used for C extraction and Qualification, rather than rejecting annotations just because the expanded response window overlaps Ignore. The exact time-axis example is pending OD-013. Preserve the existing restriction on overlap of the actual Collision annotation itself unless explicitly changed. | User corrected the proposed whole-window rejection policy and asked to subtract covered Ignore time. |
| DEC-027 | Confirm fixed-deadline set subtraction: for W=[0,150] ms and Ignore=[60,90) ms, eligible samples are [0,60) and [90,150] ms. Do not extend to 180 ms, reduce the endpoint to 120 ms, or compress timestamps. Apply this to C and Qualification while preserving actual Collision/Ignore annotation rejection. Supersede the provisional time-axis clause of DEC-026; retain its exclusion policy. | User confirmed the concrete fixed-endpoint example and separately reaffirmed the original annotation restriction. |
| DEC-028 | Supersede DEC-002 for threshold aggregation: Normal Robot Motion uses the maximum of its per-interval maxima, while Robot Fork Collision retains the minimum of its per-window maxima. The exact strictly-above-N candidate rule remains open in OD-014 because detector comparison uses Score >= Threshold. | User corrected the requirement: threshold must be above all Normal fluctuations. |
| DEC-029 | Use strict `Score > Threshold` detection everywhere and keep N itself as the first threshold candidate. Equality does not contribute to confirmation. Preserve the existing strict-below release/re-arm predicate and collision-ratio calculation. | User explicitly answered: change to `Score > Threshold`. |
| DEC-030 | Change the Collision upper-bound aggregation to the maximum of eligible per-window Collision peak Scores, accepting that thresholds admitted by this search bound may exceed weaker Collision peaks. | User selected option 2 after being told that weaker labeled Collisions may no longer be guaranteed to trigger. The downstream Qualification policy remains unresolved in OD-015. |
| DEC-031 | Retain the existing Qualification requirement that every labeled Collision be detected even though C now uses the strongest Collision peak for candidate-range construction. | User selected option 1 after the distinction between candidate generation and final Qualification was explained. |
| DEC-032 | After `Confirm all annotation sets`, subtract each Collision onset-through-150-ms response window from derived Normal Robot Motion, while preserving the user's manual Collision annotation geometry. | The user confirmed that the complete 150-ms range must not count as Normal and explicitly tied recomputation to annotation confirmation. This aligns Normal derivation, threshold search and Qualification without inventing a second timing rule. |
| DEC-033 | Restore C to the minimum of the eligible per-Collision response-window peak Scores, superseding the strongest-Collision choice in DEC-030. | The user explicitly requested that the current C be changed back to min, matching the earlier recommendation that the Threshold upper bound remain below the weakest labeled Collision peak. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | A fixture whose Normal interval maxima are 3, 8, 15 and Collision interval maxima are 12, 18, 25 produces raw bound references N=15 and C=12, therefore follows REQ-004 without generating threshold candidates. The test must distinguish maximum-of-normal-maxima from the superseded minimum-of-normal-maxima rule. A second ordered fixture whose Normal interval maxima are 3, 8, 10 and Collision interval maxima are 12, 18, 25 produces N=10 and C=12; its first candidate is N=10, which does not trigger at Score=10 under REQ-013 and DEC-029. An additional fixture with endpoints N=3.2 and C=4.4 produces 3.2, 3.7, 4.2, 4.4 in ascending order; N=3 and C=4 produces 3, 3.5, 4 without duplicating C. A positive equal-bound case N=C has one candidate value. N=0,C=1.2 produces 0.5,1.0,1.2; N=0,C=0.2 produces only 0.2. No zero candidate or replacement epsilon is emitted, and the positive grid is not re-anchored. Expected values are compared in the declared target numeric type. Detector replay and final Qualification gates remain required. | Deterministic public Learning fixtures after policy confirmation. | Pending; not implemented. |
| AC-002 | REQ-002 | A valid uninterrupted fixture with annotation end at 5 ms and a peak at 15 ms includes that peak; a peak exactly at 150 ms is included; a larger peak after 150 ms is excluded even if the annotation continues. Each collision window is reduced separately before the minimum across collisions. | Deterministic boundary-window tests through the public Learning seam. | Pending; not implemented. |
| AC-003 | REQ-003 | A fixture with more extreme peaks in an excluded speed or offset leaves current-round N and C unchanged; peaks in an included recording affect the proper bound. Bounds are recomputed after a round/model change. A fixture with Normal evidence in one eligible recording and Collision evidence in another derives N and C from their respective classes without requiring both classes in each recording; no new per-recording dual-class gate is introduced. Pick/Put do not alter bound calculations but their downstream false-trigger checks and existing out-of-range replay diagnostics remain intact. | Public Learning fixtures spanning round scope, per-model differences and downstream replay. | Pending; not implemented. |
| AC-004 | REQ-004 | With N=15 and C=12, the model produces no threshold configurations and no Qualification detector replay calls, with an identifiable reason and bounds. A second model with N=3 and C=10 still runs. If all models in a round have empty ranges, later fallback rounds continue and prior qualified kernels remain retained. Equal positive bounds produce one tested threshold. N=C=0 skips Qualification with a no-positive-threshold-candidates reason, retains the original bounds and follows the same model/fallback/previous-kernel behavior. No failed or passed candidate is fabricated for a skipped model. | Public Learning tests with existing replay-call spies, mixed model results and fallback-retention fixtures. | Pending; not implemented. |
| AC-005 | REQ-005 | A finite startup fixture has prediction at sample zero equal to model bias plus lag-zero weights times the measured Internal IMU vector, with all older input taps zero. A diagonal three-tap unit-weight fixture with constant input 10 and zero bias produces predictions 10, 20, 30 and then 30 per axis; residual and Score follow the frozen model normalization, with no intentional warm-up NaN placeholders. Validate both target numeric types. A startup peak within an eligible Normal interval or Collision response window contributes to the corresponding interval maximum and bound; startup detector events are evaluated under ordinary Qualification rules and may cause a failure. Tests distinguish ordinary inclusion from a warm-up exclusion and retain confirmation-mode semantics. True numeric errors remain separately identifiable. | Golden startup vectors and replay/target-arithmetic equivalence checks after policy confirmation. | Pending; not implemented. |
| AC-006 | REQ-006 | For a 1-ms sample-grid fixture, measured values v(2 ms)=4 and v(5 ms)=10 yield inserted values v(3 ms)=6 and v(4 ms)=8. Distinct per-axis slopes verify independent interpolation of all six axes. Measured rows remain unchanged and distinguishable, source bytes are unchanged, and annotation validation visibly identifies repaired locations. At 1000 Hz, a 4-ms measured-endpoint separation has three missing samples and permits interpolation; a 5-ms separation has four missing samples and rejects the recording. At 2000 Hz the corresponding boundaries are 2 ms and 2.5 ms; at 500 Hz they are 8 ms and 10 ms. Verify exact missing-count boundaries, all six interpolated axes, rejection of the whole offending recording, unchanged original source bytes and unaffected valid recordings. There is no remaining fixed 3-ms cap. At nominal 1000 Hz, endpoints t_left=0 and t_right=4.04 ms produce three inserted times 1.01,2.02,3.03 ms while preserving measured endpoints; all six values follow the same time-linear fractions. Endpoint gaps 3.92 ms and 4.08 ms are accepted at the inclusive +/-2% repaired-period limits; values demonstrably outside those limits are rejected, allowing only numeric comparison tolerance rather than a widened data tolerance. A 5-ms gap still rejects for four missing samples despite perfect alignment; a 4.5-ms ambiguous gap also rejects. Equivalent rate-scaled fixtures verify the rule is not a fixed millisecond cap. Provenance presentation/persistence follows REQ-009; downstream eligibility follows REQ-008. | Import numerical fixtures, provenance/annotation UI checks, and round-trip tests after policy confirmation. | Pending; not implemented. |
| AC-007 | REQ-007 | A nontrivial FIR fixture with a nonzero history before a repaired gap produces exactly the same FIR predictions as continuous replay of the explicitly expanded sequence; compare predictions during the inserted rows and for the following full history window. A zero-restart reference differs, and no new intentional warm-up NaN region is introduced. Repair markers remain available. | Deterministic public replay fixtures for one, two and three inserted samples in both target numeric types. | Pending; not implemented. |
| AC-008 | REQ-008 | A repaired sequence and the same explicitly expanded numeric sequence produce matching fit eligibility, N/C bounds and detector/Qualification results under identical activity annotations. Confirm interpolated Normal/Pick/Put rows follow existing fit rules while Collision/Ignore rows remain excluded from fitting; synthetic status alone does not remove events or create Coverage Gap. Pending confirmation and latch/re-arm timing continue across the repaired span. Annotation validation permits an otherwise valid interval across a successfully repaired gap and still exposes repair markers. | Public Learning/Workspace fixtures, detector continuity vectors and provenance-visible UI checks. | Pending; not implemented. |
| AC-009 | REQ-009 | A recording containing multiple successfully repaired gaps visibly identifies their locations and inserted-sample counts during annotation validation. The existing annotation confirmation action suffices; there is no required per-gap approval. Save and reopen a project created under the new rules with its unchanged source available and verify identical repair markers/counts and annotation time alignment. Legacy-project migration/conversion is not required by this acceptance criterion. Original source bytes remain unchanged, repaired samples remain distinguishable from measured samples, and project persistence retains the source-reference/no-embedded-waveform contract. | Workspace UI/interaction checks and existing project round-trip fixtures extended for repaired recordings. | Pending; not implemented. |
| AC-010 | REQ-010 | Partial Ignore/Collision overlap, identical intervals and containment in either direction are rejected at annotation confirmation and block Start Learning with identifiable conflicting intervals. Verify direct edits and reference/template confirmation paths cannot bypass this rule. Exactly adjacent half-open intervals remain valid, and correcting the overlap clears the relevant blocker. A Collision annotation ending at 5 ms followed by Ignore at 10-15 ms within its 150-ms response window is not rejected by this rule; those Ignore samples remain excluded from analytical evidence by existing semantics. Preserve existing Ignore/Pick and Ignore/Put masking behavior. No Qualification model skip/fallback is used to resolve annotation errors. | Workspace annotation validation and progression tests, template/reference entry-path checks, UI conflict feedback and boundary/adjacency fixtures. | Pending; not implemented. |
| AC-011 | REQ-011 | Fixtures whose active-round recordings collectively lack Normal, Collision, or both produce an identifiable missing-class round outcome without any threshold configuration or Qualification replay. Complementary recordings collectively supplying both classes proceed to bound calculation. Excluded Speed/Offset evidence cannot fill the missing class. Verify fallback continues in the existing order and previously qualified results remain available, including when an outer-offset transition restores supplied speeds. No zero/NaN bound, legacy grid or candidate outcome is fabricated. Numerical/resource/unexpected execution errors are not reclassified as missing search evidence. | Public Learning round/fallback fixtures with existing replay-call spies and retained-winner assertions; error-classification regression checks. | Pending; not implemented. |
| AC-012 | REQ-012 | C extraction includes a peak at exactly 150 ms and excludes a later peak; Qualification accepts a qualifying collision detection at 150 ms and rejects one beyond 150 ms. Both paths and latency/result validation use the same deadline; visible policy text does not claim 20-ms compliance. | Existing public Learning/Qualification boundary tests, result validation and presentation checks. | Pending implementation and measured verification. |
| AC-013 | REQ-012 | With a valid Collision annotation ending before 60 ms and Ignore [60,90) ms, C extraction ignores a larger peak inside Ignore and includes eligible peaks before 60 ms and from 90 through 150 ms. Qualification excludes triggers within Ignore, retains eligible triggers afterward, and reports actual elapsed latency from onset. Verify the Ignore start is excluded and end is eligible, multiple Ignore spans are subtracted, an Ignore span covering the deadline excludes that sample, and no extension/compression occurs. Preserve detector state across Ignore and retain all AC-010 annotation rejection checks. | Extend existing Learning/Qualification masking, boundary, detector-continuity and Workspace tests. | Pending implementation and measured verification. |
| AC-014 | REQ-013 | For float32 and float64, samples immediately below Threshold and exactly equal to Threshold do not fill a confirmation slot; the smallest tested value above Threshold does. Verify `1_OF_1`, `2_CONSECUTIVE`, and `2_OF_3`, including mixed below/equal/above sequences, reset, latch and unchanged strict-below release behavior. Qualification, Replay, diagnostic evidence and exported profile semantics must agree. A bound fixture with N equal to the highest eligible Normal Score includes threshold N without triggering on that equal Normal sample. | Public detector/Qualification/Replay tests, export semantic-contract checks, and target-numeric boundary vectors. | Pending implementation and measured verification. |
| AC-015 | REQ-014 | A fixture with Normal interval maxima 3, 8, 16 and Collision window maxima 14, 18, 25 produces N=16 and C=25 and generates the expected N-anchored candidate grid through C, proving C uses the strongest rather than weakest Collision peak. Qualification replay at threshold 16 detects the 18 and 25 peaks but misses the 14 peak and therefore remains FAIL with one missed Collision. A separate fixture in which every Collision is detected can still PASS. Validate both target numeric types and all confirmation modes without changing the 150-ms deadline or false-trigger requirements. | Public threshold-bound and Qualification tests with replay-call spies and exact detected/missed counts. | Pending implementation and measured verification. |
| AC-016 | REQ-015 | At 1000 Hz, a confirmed Collision annotation `[18205,18305)` inside a Cycle derives no Normal support from onset through index 18355 inclusive. A Score peak at index 18339 therefore contributes to Collision-window C evidence and Qualification acceptance but never to Normal N evidence or a Normal false-trigger class. Verify the equivalent boundary at non-1000-Hz and irregular valid timestamps, exact inclusion at 150 ms, the first sample after the deadline returning to Normal when otherwise eligible, clipping at Cycle end, stopping at a true discontinuity, deterministic recomputation after annotation edits, and unchanged persisted/manual Collision start/end indexes. A regression fixture reproducing the K058 `8mm_100` overlap proves that the former 16.1424 sample is not classified as Normal. | Workspace derivation unit tests, controller LearningDataset mapping tests, Learning threshold-bound/Qualification integration tests, and project round-trip assertions. | Pending implementation and measured verification. |
| AC-017 | REQ-016 | For Normal interval maxima 3, 8, 10 and Collision-window maxima 12, 18, 25, derive N=10 and C=12 and generate only the N-anchored candidates 10, 10.5, 11, 11.5, 12. No candidate above 12 is replayed. For Normal maxima 3, 8, 15 with the same Collision maxima, derive N=15 and C=12, skip that model's Qualification with the existing empty-range reason, continue fallback, and retain earlier qualified kernels. Verify both target numeric types and preserve the inclusive 150-ms window, Ignore masking, strict predicate and all-Collision Qualification. | Public Learning threshold-bound tests, Qualification replay spies, and fallback-retention regression tests. | Pending implementation and measured verification. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| DEC-002 | refines | REQ-001 |
| DEC-003 | refines | REQ-001 |
| DEC-004 | refines | REQ-001 |
| DEC-005 | refines | REQ-002 |
| DEC-025 | supersedes | DEC-005 |
| DEC-025 | refines | REQ-012 |
| DEC-026 | refines | REQ-012 |
| DEC-027 | supersedes | DEC-026 |
| DEC-027 | refines | REQ-012 |
| DEC-028 | supersedes | DEC-002 |
| DEC-028 | refines | REQ-001 |
| DEC-029 | refines | REQ-013 |
| DEC-029 | refines | DEC-028 |
| DEC-030 | supersedes | DEC-028 |
| DEC-030 | refines | REQ-001 |
| DEC-030 | refines | REQ-012 |
| DEC-031 | refines | DEC-030 |
| REQ-014 | supersedes | REQ-001 |
| REQ-014 | supersedes | REQ-012 |
| REQ-014 | depends_on | REQ-013 |
| DEC-032 | refines | REQ-015 |
| REQ-015 | depends_on | REQ-012 |
| REQ-015 | refines | REQ-003 |
| DEC-033 | supersedes | DEC-030 |
| DEC-033 | refines | REQ-016 |
| REQ-016 | supersedes | REQ-014 |
| REQ-016 | refines | REQ-001 |
| REQ-016 | refines | REQ-012 |
| REQ-016 | depends_on | REQ-013 |
| REQ-001 | depends_on | REQ-013 |
| REQ-012 | depends_on | REQ-010 |
| REQ-012 | Temporarily use one inclusive absolute onset-through-150-ms deadline for BOTH C peak extraction and Qualification collision detection/latency acceptance. Let W=[t0,t0+0.150 s] and I be the union of Ignore sample intervals; use W minus I for eligible collision evidence. Preserve timestamps and measure latency as the actual trigger time minus t0. Ignore neither pauses the clock nor extends or shortens the absolute endpoint. Retain eligible samples after Ignore ends within W. Ignore does not reset or pause FIR/detector state; preserve existing confirmation/re-arm semantics. The actual Collision annotation must still pass REQ-010, including partial-overlap rejection and half-open adjacency. Do not reject an otherwise valid annotation solely for Ignore overlap with the expanded response window. Keep N/C min-of-maxima, positive threshold grid, C<N skipping and fallback unchanged. Update deadline-dependent result checks and visible policy wording; results under this policy must not be presented as satisfying 20 ms. |
| REQ-001 | depends_on | REQ-002 |
| DEC-006 | refines | REQ-003 |
| REQ-001 | depends_on | REQ-003 |
| DEC-007 | refines | REQ-004 |
| REQ-001 | depends_on | REQ-004 |
| DEC-008 | refines | REQ-005 |
| DEC-009 | refines | REQ-006 |
| REQ-001 | depends_on | REQ-005 |
| REQ-003 | depends_on | REQ-006 |
| DEC-010 | refines | REQ-005 |
| DEC-011 | refines | REQ-005 |
| DEC-012 | refines | REQ-006 |
| DEC-013 | refines | REQ-006 |
| DEC-014 | supersedes | DEC-013 |
| DEC-014 | refines | REQ-006 |
| DEC-015 | refines | REQ-007 |
| REQ-005 | depends_on | REQ-007 |
| REQ-006 | depends_on | REQ-007 |
| DEC-016 | refines | REQ-008 |
| REQ-002 | depends_on | REQ-008 |
| REQ-006 | depends_on | REQ-008 |
| REQ-007 | depends_on | REQ-008 |
| DEC-017 | refines | DEC-003 |
| DEC-017 | refines | REQ-001 |
| DEC-017 | refines | REQ-004 |
| DEC-018 | refines | REQ-006 |
| DEC-018 | refines | DEC-014 |
| DEC-019 | refines | REQ-009 |
| REQ-006 | depends_on | REQ-009 |
| REQ-008 | depends_on | REQ-009 |
| DEC-020 | refines | REQ-009 |
| DEC-021 | refines | REQ-010 |
| REQ-002 | depends_on | REQ-010 |
| DEC-022 | refines | DEC-021 |
| DEC-022 | refines | REQ-010 |
| DEC-023 | refines | REQ-003 |
| DEC-024 | refines | REQ-011 |
| REQ-001 | depends_on | REQ-011 |
| REQ-011 | depends_on | REQ-003 |

This change set supersedes SPEC-0008 REQ-005 and DEC-005 fixed grid endpoints and fixed candidate count, replacing them with REQ-001/REQ-004/REQ-011 while preserving 0.5 interior spacing, model Score reuse and existing fallback ordering. REQ-011 adds a distinct whole-round search-evidence absence outcome without broadening the numerical-error category. SPEC-0008 is implemented and must not reopen. The current manifest at lines 237-240 still requires fixed endpoints and per-model Score reuse. CONTEXT.md is absent; no accepted ADR match was found in architecture/decisions.

Expanded intended supersedes relationships: SPEC-0007 REQ-002 and the warm-up portions of AC-001/AC-002, plus architecture/manifest.yaml warm-up invalidity invariant near line 247, are superseded by REQ-005 with the confirmed DEC-010 zero initialization and DEC-011 startup inclusion. The implementation must update the manifest and generated descriptions to match before delivery. SPEC-0001 REQ-040/AC-061 currently prohibit timestamp interpolation and require discontinuity segmentation; REQ-006 intentionally replaces timestamp-gap rejection/segmentation with the confirmed DEC-012/DEC-014/DEC-018 interpolation/count/alignment rules for accepted recordings, preserving measured source data and ordinary jitter validation. SPEC-0001 REQ-041/AC-062 describe a distinct explicitly accepted isolated invalid-IMU-row repair path; do not equate it with timestamp-gap interpolation. The separate invalid-cell path is outside this timestamp-gap change: preserve current invalid-cell rejection rather than implementing a new cell-repair feature. The pre-existing specification/source discrepancy is recorded for separate work and does not authorize scope expansion. Both existing ADRs remain proposed, not accepted; no ADR status change is authorized. Prior canonical specifications remain historical references and architecture files are unchanged during clarification; the new canonical specification governs this change set. Neither proposed ADR is accepted by this work.

Annotation-policy discrepancy found during DISC-021: SPEC-0001 REQ-042 and AC-063 explicitly exempt Ignore from non-overlap restrictions. WorkspaceService._POSITIVE_EVENT_KINDS and validate_annotations likewise exclude Ignore from the overlap check. DEC-022 and REQ-010 supersede the Ignore-overlap exemption only for overlap with Robot Fork Collision annotation intervals, including partial overlap. Preserve half-open adjacency and the exemption for other activities. Do not claim existing source already enforces the new rule, or extend the annotation restriction to the full response window. This is a confirmed change, not an unresolved conflict between the intended requirements.

Timing amendment: DEC-025 supersedes DEC-005 only for the numeric deadline; REQ-012 supersedes the corresponding timing portion of REQ-002 and the existing 20-ms Qualification invariant. Historical decisions remain preserved.

## Out of Scope

No source, tests, architecture, generated views, Git, or external changes are authorized. Do not change FIR fitting or detector confirmation/re-arm semantics implicitly. REQ-015 does not lengthen, rewrite, persist, or visually move the user's manual Collision annotation; it changes only derived Normal eligibility. Numeric startup and interpolation are now explicit change-set scope, but zero initialization is explicitly selected by DEC-010 and startup search/Qualification inclusion by DEC-011; time-linear interpolation is explicitly selected by DEC-012; the missing-sample-count limit and rejection policy are explicitly selected by DEC-014, replacing DEC-013; synthetic-data analytical eligibility is explicitly selected by DEC-016; time-grid/alignment is explicitly selected by DEC-018. Provenance display, ordinary annotation confirmation and marker restoration on project reopen are explicitly selected by DEC-019. Old-project compatibility, migration, legacy annotation conversion and old-result conversion are explicitly excluded by DEC-020. Do not add legacy support or compatibility test work to this change set. This does not authorize deleting or modifying old projects, treating legacy results as evidence of the new rules, or dropping new-contract project save/reopen support.

## Open Decisions

None.

## Routing/Gates

ask-matt -> grilling -> spec-governance. Expanded changes require clarify-improvement-proposals and govern-modular-event-architecture after decisions are complete, including ownership/boundary design, planned manifest validation and coordinated source/tests/generated views. Explanation and clarification only. Product mutation requires confirmed specification and explicit execution authorization, then architecture, tests and code review gates.

## Revision History

| Revision | Date | Change |
|---|---|---|
| 1 | 2026-08-27 | Start clarification of score-derived threshold bounds. |
| 2 | 2026-08-27 | Persist activity-specific evidence correction. |
| 3 | 2026-08-27 | Confirm minimum-of-interval-maxima aggregation for both classes; resolve OD-001. |
| 4 | 2026-08-27 | Normalize relationship and acceptance table headers; no decision change. |
| 5 | 2026-08-27 | Confirm closed interval [N,C]; narrow OD-002 to interior grid policy. |
| 6 | 2026-08-27 | Confirm N-anchored 0.5 grid plus C; resolve OD-002. |
| 7 | 2026-08-27 | Confirm Collision peak within onset-through-20-ms response window; resolve OD-003. |
| 8 | 2026-08-27 | Confirm active-round Speed/Offset scope; resolve OD-004 and normalize Markdown tables. |
| 9 | 2026-08-27 | Confirm C < N skips model Qualification and preserves fallback/earlier kernels; narrow OD-005. |
| 10 | 2026-08-27 | Add user-requested numeric FIR startup and marked timestamp-gap interpolation; preserve all threshold decisions and open necessary initialization/repair policies. |
| 11 | 2026-08-27 | Confirm zero initialization of missing startup FIR history; refine numeric startup acceptance and narrow OD-006. |
| 12 | 2026-08-27 | Confirm normal inclusion of startup Scores in bound search and Qualification; narrow OD-006 to interpolated-gap reset behavior. |
| 13 | 2026-08-27 | Confirm time-linear timestamp-gap interpolation per raw IMU axis; narrow OD-007. |
| 14 | 2026-08-27 | Record inclusive 3-ms measured-endpoint gap limit; subsequently superseded by revision 15. |
| 15 | 2026-08-27 | Replace fixed 3-ms limit with sample-rate-based missing count: interpolate 1-3; reject recording at 4 or more. |
| 16 | 2026-08-27 | Confirm FIR history continuity across successfully interpolated gaps; preserve pending analytical/detector eligibility decisions. |
| 17 | 2026-08-27 | Confirm ordinary analytical participation of interpolated data under existing activity roles; resolve detector continuity and narrow OD-008. |
| 18 | 2026-08-27 | Confirm zero-threshold omission without shifting the positive grid; skip models with no remaining positive candidates and narrow OD-005. |
| 19 | 2026-08-27 | Confirm nearest-integer gap counting, equal endpoint subdivision and inclusive +/-2% repaired-period validation; resolve OD-007 with confirmation remaining in OD-008. |
| 20 | 2026-08-27 | Confirm visible repair locations/counts, no extra per-gap confirmation and marker restoration on project reopen; narrow OD-008 to old-project/result compatibility. |
| 21 | 2026-08-27 | Exclude old-project compatibility/migration/conversion per user instruction, preserve new-project marker round trips, and resolve OD-008. |
| 22 | 2026-08-27 | Record user rejection of missing-Score model skipping for invalid Collision/Ignore labels; require annotation-stage rejection and clarify the existing Ignore-overlap exception. |
| 23 | 2026-08-27 | Confirm any Ignore/Collision annotation overlap blocks confirmation and Learning; preserve adjacency, other activities and the separate 20-ms response window; narrow OD-005 to required evidence availability. |
| 24 | 2026-08-27 | Reject per-recording Normal-plus-Collision prerequisite; preserve pooled active-round evidence and narrow OD-005 to a class absent from the entire round. |
| 25 | 2026-08-27 | Confirm whole-round missing-class search-evidence handling, preserve fallback and earlier results, resolve OD-005 and finalize requirement/acceptance references for materialization. |
| 26 | 2026-08-27 | Normalize acceptance table headers to the canonical validator contract; all validation methods and Pending implementation evidence remain unchanged. |

| 31 | 2026-08-27 | Confirm shared fixed 150-ms deadline, subtract Ignore sample intervals without time compensation, preserve annotation overlap rejection; close OD-013. |
| 32 | 2026-08-31 | Reopen after the user corrected Normal aggregation to maximum-of-interval-maxima; add DEC-028 and OD-014 for the unresolved strictly-above-N candidate rule. |
| 33 | 2026-08-31 | Resolve OD-014 by changing all detector threshold comparisons to strict Score > Threshold while retaining N as an included first candidate; add REQ-013, DEC-029 and AC-014. |
| 34 | 2026-08-31 | Accept C=max(Collision window peaks), explicitly accepting possible weak-Collision misses; add DEC-030 and open OD-015 for the downstream Qualification policy. |
| 35 | 2026-08-31 | Retain all-Collision Qualification despite C=max candidate-range construction; add REQ-014, DEC-031 and AC-015 and resolve OD-015. |
| 36 | 2026-08-31 | Add derived-Normal Collision-response exclusion through 150 ms, preserving manual Collision geometry. |
| 37 | 2026-08-31 | Reconcile and confirm the derived-Normal amendment with REQ-015, DEC-032 and AC-016. |
| 38 | 2026-09-01 | Restore C=min(Collision-window peaks), superseding the strongest-Collision candidate bound; add REQ-016, DEC-033 and AC-017. |

## Discussion Context

### DISC-001: Activity-specific threshold bounds
- **Situation:** Prior explanation warned against a whole-recording maximum; the user corrected that interpretation.
- **Question:** What labeled evidence should define threshold bounds?
- **Options and tradeoffs:** User supplied a premise correction rather than selecting options; aggregation across intervals remains open.
- **User answer:** The user wants the maximum Score of robot normal move segments to find the minimum threshold, and the maximum Score of collision segments to find the maximum threshold, rather than inspecting the entire Score recording indiscriminately.
- **Explicit rationale:** Find a suitable threshold range using the two labeled activity classes.
- **Resulting impact:** REQ-001, DEC-001 and AC-001 capture the scope correction without inferring aggregation, endpoints or window policy.

### DISC-002: Both activity classes use minimum of interval maxima
- **Situation:** The prior response proposed minimum of Collision interval maxima, while Normal aggregation remained unclear.
- **Question:** How should maxima from multiple Collision intervals be aggregated?
- **Options and tradeoffs:** The assistant illustrated minimum versus maximum of collision peaks and recommended the minimum to avoid selecting thresholds above a required collision peak. User expanded the decision to both activity classes. A Normal minimum-of-maxima lower bound can still admit false triggers in other Normal intervals; final Qualification remains responsible for rejecting failing candidates.
- **User answer:** Both Collision and Normal Robot Motion use the minimum of the maximum values of their individual intervals. Annotation 1 selected the phrase minimum of the individual interval maxima.
- **Explicit rationale:** No new rationale was supplied.
- **Resulting impact:** REQ-001 and AC-001 are refined; DEC-002 records both-class aggregation. OD-001 is resolved; endpoint/grid, interval window, round/speed/Offset scope and empty-range policies remain open.

### DISC-003: Include both threshold endpoints
- **Situation:** N and C aggregation had been confirmed; the user requested an explanation of [N,C] notation before deciding endpoint inclusion.
- **Question:** Should the threshold search include N and C themselves?
- **Options and tradeoffs:** Inclusion tests both boundary candidates and lets Qualification reject failures; exclusion would omit those boundary candidates. The prior 0.5 example illustrated notation and did not confirm grid spacing.
- **User answer:** Include N and C in [N,C].
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-003 refines REQ-001 and AC-001 with endpoint inclusion; OD-002 retains only unresolved interior grid/precision policy. OD-003 through OD-005 remain open.

### DISC-004: N-anchored grid at 0.5 spacing with terminal C
- **Situation:** Both-class minimum-of-maxima and inclusive endpoints were already confirmed; intermediate threshold generation remained open.
- **Question:** Use increments of 0.5 starting at N and append C if the regular increments do not reach it?
- **Options and tradeoffs:** The proposed rule preserves the existing spacing, anchors the search at the observed lower bound and retains the exact upper endpoint; the terminal gap can be smaller than 0.5 and total candidate count becomes model-dependent. Example supplied: N=3.2, C=4.4 yields 3.2, 3.7, 4.2, 4.4.
- **User answer:** Agreed.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-004 refines REQ-001 and AC-001 with grid construction; OD-002 is resolved. OD-003 through OD-005 remain open.

### DISC-005: Collision peak sampling within 20 ms
- **Situation:** The previous question proposed using the complete Collision annotation for its peak; existing Qualification already uses an onset-through-20-ms window independent of annotation end.
- **Question:** Should Collision max Score come from the complete annotated Collision interval?
- **Options and tradeoffs:** Full-annotation peaks can occur after the detection deadline or omit relevant response samples when an annotation ends early. A 20-ms response window aligns peak evidence with the existing detection deadline, while subsequent detector replay is still necessary.
- **User answer:** Collision max Score may be sampled within 20 ms.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-005 and REQ-002 define Collision peak timing; AC-002 records boundary tests. REQ-001 now refers to Collision windows. OD-003 is resolved; OD-004 and OD-005 remain open.

### DISC-006: Current-round active Speed and Offset scope
- **Situation:** Fallback excludes speed and Offset strata. Using excluded recordings to derive N and C could keep those excluded conditions constraining the search.
- **Question:** Derive N and C only from the current round's Speed and Offset data that have not been excluded?
- **Options and tradeoffs:** Current-round scope aligns bound evidence with the round's declared coverage. Using all supplied conditions would retain excluded-condition influence. Existing replay diagnostics need not be removed by the scope decision.
- **User answer:** Yes, adopt this rule.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-006 and REQ-003 define active-round scope, with AC-003 for verification; REQ-001 depends on REQ-003. OD-004 is resolved. The already selected two-class formulas do not add Pick/Put as bound inputs; downstream Qualification remains required. OD-005 remains open.

### DISC-007: Skip Qualification when C is below N
- **Situation:** N=15 and C=12 leave no threshold satisfying the confirmed closed interval; the user requested a plain-language explanation of skipping a model versus advancing a whole round.
- **Question:** Skip the model with an empty range, continue other models, and if the entire round has no candidate continue fallback while keeping earlier qualified kernels?
- **Options and tradeoffs:** The proposed path avoids replay with no candidate threshold and preserves progress; swapping/expanding bounds or falling back to the old grid would change the confirmed search rule. An empty range is not evidence that every conceivable detector configuration fails.
- **User answer:** Yes, that is correct. When C < N there is no need to perform Qualification.
- **Explicit rationale:** No Qualification is needed when C < N.
- **Resulting impact:** DEC-007 and REQ-004 define the skipped-model and empty-round behavior; AC-004 records validation. REQ-001 refers to REQ-004. OD-005 now concerns unavailable/invalid evidence and non-positive bounds, not the resolved C < N case.

### DISC-008: Numeric FIR startup output
- **Situation:** Read-only explanation established that Studio intentionally leaves startup outputs as NaN, whereas float FIR arithmetic depends on history-buffer initial values.
- **Question:** The user supplied a new scope instruction in response annotation 1.
- **Options and tradeoffs:** Numeric startup may exhibit initialization-dependent transients; choosing zero versus first-sample history changes output and cannot be inferred from float alone. No actual firmware buffer initialization has been verified.
- **User answer:** Use actual output values; do not use NaN.
- **Explicit rationale:** Prefer actual FIR output values over intentional unavailable-result placeholders.
- **Resulting impact:** REQ-005, DEC-008 and AC-005 add numeric startup scope. OD-006 records missing initialization and downstream eligibility decisions; REQ-001 depends on the resulting Score semantics.

### DISC-009: Interpolate and mark import timestamp gaps
- **Situation:** Read-only inspection found that timestamp jumps are accepted and flagged, while annotation intervals crossing a flagged gap are rejected.
- **Question:** The user supplied a new scope instruction in response annotation 2.
- **Options and tradeoffs:** Interpolation inserts estimates rather than measured IMU samples. Preserving repair provenance enables the annotation workflow to identify affected regions, but neither interpolation method nor permission to treat repaired Collision peaks as measured evidence follows automatically.
- **User answer:** Fill gaps by interpolation, and mark them during annotation validation.
- **Explicit rationale:** Make interpolated locations visible during annotation validation.
- **Resulting impact:** REQ-006, DEC-009 and AC-006 add marked timestamp-gap interpolation. OD-007 and OD-008 retain method, bounds, visibility and downstream eligibility decisions.

### DISC-010: Select zero initialization of FIR history
- **Situation:** The user requested alternatives before choosing how to initialize unavailable startup history. No actual firmware implementation has been verified.
- **Question:** Which initialization should be used for missing FIR startup history?
- **Options and tradeoffs:** Zero initialization is deterministic and may cause startup transients; first-sample extension assumes preceding input matched the first sample; real pre-roll requires available measured pre-history. The comparison did not establish actual firmware equivalence.
- **User answer:** Choose zero padding.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-010 refines REQ-005 and AC-005 with zero-filled source-scale history and first-sample computation. DEC-008 refers to the resolved initialization. OD-006 remains open only for startup evidence eligibility and gap/reset behavior; interpolation and exceptional numeric policies remain open.

### DISC-011: Include startup Scores in search and Qualification
- **Situation:** Zero initialization and numeric output from the first sample were already confirmed; whether to exclude startup transients from search/validation remained open.
- **Question:** Should startup Scores participate normally in threshold search and Qualification under existing annotation and range rules?
- **Options and tradeoffs:** Normal inclusion exposes real zero-initialization transients and can reject candidates with startup false triggers; display-only startup values with an evaluation exclusion would hide those startup failures.
- **User answer:** Startup Scores also participate normally in search and validation.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-011 refines REQ-005 and AC-005 with ordinary startup inclusion; DEC-008 now refers to the settled eligibility. OD-006 retains only interpolated-gap reset behavior. OD-005, OD-007 and OD-008 remain open.

### DISC-012: Select time-linear gap interpolation
- **Situation:** Marked Import timestamp-gap interpolation was requested, but its numerical method had not been selected.
- **Question:** Use time-linear interpolation per each of the six Internal/External IMU axes between the measured samples before and after a gap?
- **Options and tradeoffs:** Linear interpolation is simple and stays between each axis's endpoint values for interior times, but cannot reconstruct an unobserved collision peak. The shown 1-ms-grid example maps endpoints 2 ms:4 and 5 ms:10 to inserted values 3 ms:6 and 4 ms:8.
- **User answer:** Use this linear interpolation for time gaps.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-012 refines REQ-006 and AC-006 with the per-axis time-linear method; DEC-009 refers to the resolved method. OD-007 retains grid/length/confirmation policies; downstream interpolated-data eligibility and reset behavior remain open.

### DISC-013: Maximum interpolation gap is 3 ms
- **Situation:** Linear interpolation was selected, but its maximum eligible gap duration remained open. The user also requested clearer alternatives for future decision questions; this did not itself select a gap policy.
- **Question:** What maximum elapsed time between the measured samples before and after a gap is allowed for interpolation?
- **Options and tradeoffs:** No quantitative default was imposed. A longer permitted gap admits more repair but cannot establish the true unobserved collision peak. The 20-ms detection deadline is not an interpolation-quality guarantee.
- **User answer:** 3 ms, attached to the earlier interpolation-duration question in response annotation 1.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-013 refines REQ-006 and AC-006 with an inclusive 3-ms measured-endpoint time limit. OD-007 now concerns over-limit handling, grid/alignment and confirmation, rather than the settled maximum duration.

### DISC-014: Replace time cap with consecutive missing-sample count
- **Situation:** A fixed 3-ms limit had just been recorded, but the user immediately corrected the limit and supplied the over-limit rejection outcome.
- **Question:** The user steered the pending interpolation limit/over-limit policy with a correction.
- **Options and tradeoffs:** A fixed time cap permits different missing-sample counts at different sampling rates. The selected count rule interpolates up to three missing samples at each rate and rejects the entire recording on a gap of four or more; unaffected valid portions of that rejected recording are not admitted separately.
- **User answer:** It should depend on sample rate; four consecutive missing samples reject the recording.
- **Explicit rationale:** The limit must account for sampling rate.
- **Resulting impact:** DEC-014 supersedes DEC-013 and refines REQ-006/AC-006. The 3-ms rule is historical only. OD-007 no longer leaves over-limit handling unresolved; alignment/grid and downstream evidence decisions remain open.

### DISC-015: Preserve FIR history across repaired gaps
- **Situation:** The count-based interpolation policy was confirmed, but FIR history at repaired regions was not.
- **Question:** Preserve FIR history across a successfully interpolated gap or clear history and restart with zeros after it?
- **Options and tradeoffs:** Option 1 feeds inserted samples sequentially and preserves history, avoiding a restart transient while allowing estimated inputs to influence later output. Option 2 clears prior history and introduces a fresh zero-initialization transient. Both retain interpolation provenance.
- **User answer:** 1.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-015 and REQ-007 confirm FIR continuity, with AC-007 for verification. REQ-005/REQ-006 refer to REQ-007. Detector state and synthetic-data fitting/threshold/Qualification eligibility remain open under OD-006/OD-008.

### DISC-016: Normal analytical participation of interpolated data
- **Situation:** Successfully repaired gaps already preserve FIR history, while whether repaired data qualify as Training/search/Qualification evidence remained open.
- **Question:** Let interpolated data participate normally in analysis or use them only for FIR continuity while excluding affected analytical evidence?
- **Options and tradeoffs:** Option 1 retains data under existing activity roles and keeps interpolation markers, but validation results reflect estimates in repaired regions. Option 2 treats affected evidence as unavailable and may prevent Qualification. Neither option reconstructs unknown true collision peaks.
- **User answer:** 1.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-016 and REQ-008 confirm normal participation and preserved activity roles, with AC-008 for verification. Ordinary continuous processing implies no special detector reset solely for repaired samples; repaired spans are not rejected as acquisition boundaries during otherwise valid annotation checks. OD-006 is resolved; OD-008 retains provenance interaction/persistence/artifact details.


### DISC-017: Zero threshold endpoint exception

- **Situation:** The accepted closed interval can include N=0, but the existing detector requires threshold>0.
- **Question:** Accept omitting threshold=0 while keeping other positive in-range candidates, and skipping model Qualification when none remain?
- **Options and tradeoffs:** The proposed exception preserves positive candidates and existing detector validity but does not test the zero endpoint; rejecting every N=0 model would also discard usable positive candidates. Supporting zero would require separate detector and ratio semantics outside this proposal.
- **User answer:** Accepted.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-017 refines DEC-003, REQ-001 and REQ-004; AC-001/AC-004 cover a zero lower bound, a positive upper endpoint smaller than one grid step, and N=C=0 model skipping. OD-005 no longer leaves zero-threshold handling open. Other evidence, grid-alignment and provenance decisions remain open.


### DISC-018: Timestamp alignment for gap interpolation

- **Situation:** Slightly jittered measured timestamps do not necessarily span an exact integer number of nominal sample periods; a deterministic count and inserted-time rule is needed.
- **Question:** Accept nearest-integer interval counting, equal subdivision between measured endpoints and the existing +/-2% period tolerance, while retaining rejection for four or more missing samples?
- **Options and tradeoffs:** The proposed rule preserves measured endpoints and tolerates bounded jitter by equally spacing derived samples. Inserting exact nominal periods from the left would concentrate timing mismatch at the last interval; rejecting every nonexact gap would reject otherwise tolerated timestamp jitter. Neither alternative was selected.
- **User answer:** Can accept.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-018 refines REQ-006 and DEC-014; AC-006 adds jittered timestamps, inclusive tolerance boundaries and misaligned/over-count rejection. OD-007 is resolved; interpolation confirmation/provenance remains in OD-008 and unavailable Score evidence remains in OD-005.


### DISC-019: Repair marker display, confirmation and persistence

- **Situation:** Interpolated samples must remain identifiable during annotation validation and after reopening a saved project.
- **Question:** Accept showing repair locations and counts, using the existing annotation confirmation without per-gap approval, and restoring markers after project save/reopen?
- **Options and tradeoffs:** The proposed behavior keeps repair provenance visible without repeated approval operations. A separate per-gap approval would add review work; temporary display without restoration would lose provenance on reopening. Neither alternative was selected.
- **User answer:** Accepted.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-019 refines REQ-009, with AC-009 for UI and project round-trip validation; REQ-006 and REQ-008 depend on REQ-009. OD-008 now retains only old-project/result compatibility. Source-reference persistence and source-integrity checks remain existing constraints rather than permission to embed waveforms or modify source data.


### DISC-020: Exclude old projects

- **Situation:** Changed sample indexing and analytical rules raised a legacy-project/result compatibility question.
- **Question:** Accept preserving old source/annotations with time-based remapping, reconfirming affected annotations and recalculating old results?
- **Options and tradeoffs:** The proposed migration path would retain old work but require annotation conversion and recalculation support. The user instead excluded old projects from scope, avoiding this work without promising compatibility.
- **User answer:** Do not consider old projects.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-020 narrows REQ-009 and AC-009 to new-contract project round trips and explicitly excludes legacy compatibility/migration/conversion. OD-008 is resolved; OD-005 remains open. No old files may be deleted or modified merely because they are out of scope.


### DISC-021: Reject invalid labels before Learning

- **Situation:** The assistant proposed treating a Collision response window wholly masked by Ignore as insufficient Score evidence and skipping model Qualification. Existing SPEC-0001 REQ-042/AC-063 and WorkspaceService allow Ignore overlap, so the stated desired annotation restriction is not already enforced by the inspected rule.
- **Question:** Accept a model skip/fallback for the described missing-evidence case?
- **Options and tradeoffs:** The proposed Qualification skip would defer invalid annotation handling until model evaluation. The user rejected that premise and required preventing this labeling arrangement. Precise overlap scope needs clarification before changing the existing Ignore exception.
- **User answer:** This configuration is not allowed; it cannot be labeled this way.
- **Explicit rationale:** The scenario should be prohibited at annotation time.
- **Resulting impact:** DEC-021 establishes REQ-010 and AC-010 for annotation-stage rejection; REQ-002 depends on REQ-010. OD-005 now prioritizes exact Ignore-overlap scope. The proposed missing-Score model-skip policy was never accepted and must not be implemented as a settled requirement.


### DISC-022: Exact Ignore/Collision overlap restriction

- **Situation:** Existing Ignore overlap exemptions conflict with the user-requested annotation-stage rejection; the precise affected interval needed confirmation.
- **Question:** Does any overlap between Ignore and the Collision annotation interval prevent annotation confirmation and Start Learning?
- **Options and tradeoffs:** The proposed rule forbids any overlap with the annotation interval. A weaker complete-masking-only restriction would permit partial overlap, while a full-response-window restriction would block Ignore beyond the annotated Collision end. Neither alternative was selected.
- **User answer:** Correct.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-022 refines DEC-021 and REQ-010; AC-010 covers partial/complete overlap, containment, adjacency, progression paths and the annotation-versus-response-window distinction. The existing Ignore exemption is superseded only for Collision annotation overlap. OD-005 now concerns absence of the required evidence classes, not settled overlap scope.


### DISC-023: No per-recording dual-class prerequisite

- **Situation:** The assistant proposed requiring each recording to contain both a derived Normal interval and a Collision interval before annotation confirmation/Start Learning.
- **Question:** Require both classes in every recording and block Start Learning otherwise?
- **Options and tradeoffs:** The proposed per-recording prerequisite would prevent empty local classes but reject recordings whose evidence could complement other recordings. The user rejected that prerequisite; active-round pooled class-specific bound calculation remains the accepted scope.
- **User answer:** No need.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-023 refines REQ-003 and AC-003 to forbid the proposed per-recording dual-class gate. The existing active-round aggregation is preserved, not broadened to excluded conditions. OD-005 concerns only a required class absent from the whole active round.


### DISC-024: Whole-round missing threshold-search evidence

- **Situation:** Individual recordings need not contain both classes, but N or C is undefined if the entire active-round scope lacks its evidence class. This is distinct from invalid Ignore/Collision labeling and numerical errors.
- **Question:** Mark a whole round missing Normal or Collision as lacking threshold-search evidence, skip Qualification, continue existing fallback and retain prior qualified results?
- **Options and tradeoffs:** The proposed whole-round skip preserves usable prior/future round results without inventing bounds; aborting the entire run would lose further fallback opportunities. A per-recording prerequisite was explicitly rejected in DEC-023.
- **User answer:** Correct.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-024 defines REQ-011 and AC-011; REQ-001 depends on REQ-011, which depends on the REQ-003 active-round scope. OD-005 is resolved. All user decisions are settled; source, architecture updates and acceptance execution remain pending and require explicit product execution authorization.


### DISC-025: Temporary collision timing relaxation

- **Situation:** Actual round 4.2 History 4 ms has N=[REDACTED: personal data] and C=[REDACTED: personal data] at 20 ms. Full annotation peak latencies are 8, 37 and 75 ms, which do not establish physical onset or earliest detection.
- **Question:** What temporary duration should replace 20 ms, and should the same deadline govern C extraction and Qualification?
- **Options and tradeoffs:** Keeping 20 ms preserves the original requirement but this model has an empty range. A longer shared window admits later evidence and detections but cannot demonstrate 20 ms compliance or guarantee Qualification. Enlarging only C extraction leaves the original Qualification deadline in force.
- **User answer:** 但是程式無法判斷實際碰撞起點。還是暫時間放寬好了
- **Explicit rationale:** The program cannot determine actual physical collision onset.
- **Resulting impact:** Temporary relaxation is requested in principle; OD-011 remains unresolved. REQ-002, DEC-005 and AC-002 need an explicit replacement contract alongside the manifest's Qualification deadline. Preserve min-of-maxima N/C, inclusive endpoints and C<N skipping. No automatic annotation shifts or product mutation are authorized.


### DISC-026: Shared 150-ms deadline and Ignore constraint

- **Situation:** The user selected a duration and added an Ignore restriction. Current code excludes Ignore samples from the response window but only rejects overlap with the actual Collision annotation interval; DEC-022 intentionally did not prohibit Ignore in the rest of the response window.
- **Question:** How should an Ignore overlap with the expanded response window be handled before Learning?
- **Options and tradeoffs:** Rejecting any response-window overlap preserves a complete 150-ms interval but requires annotation correction. Clipping at Ignore shortens usable evidence; excluding Ignore samples allows a fragmented response window. Neither alternative handling policy is assumed accepted.
- **User answer:** 兩者都先到150ms。但是這個時間區段不可以在ignore時間區段內
- **Explicit rationale:** No additional rationale supplied for 150 ms; the user explicitly disallows the interval being within Ignore.
- **Resulting impact:** DEC-025 and REQ-012/AC-012 settle both deadlines at 150 ms, superseding the prior timing contract. OD-011 is resolved. OD-012 records the exact scope/failure behavior of the Ignore restriction affecting REQ-010 and DEC-022. N/C aggregation and C<N behavior remain unchanged. Source, tests, architecture and external state remain unmodified.


### DISC-027: Subtract Ignore overlap instead of rejecting the expanded window

- **Situation:** The assistant asked whether any overlap of the expanded response window with Ignore should reject annotation confirmation and Start Learning. The user corrected that proposed rejection policy.
- **Question:** Does subtracting the covered Ignore time mean excluding those timestamped samples while retaining the original 150-ms deadline?
- **Options and tradeoffs:** Removing only the overlapping samples preserves the absolute deadline and can leave disjoint eligible spans. Pausing the clock would extend elapsed permitted latency; subtracting a duration from the endpoint would discard other unignored samples. Whole-window rejection was rejected by the user.
- **User answer:** 應該說從collision start 到collision start 150ms內，有涵蓋到ignore。則自動減去涵蓋的ignore時間
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-026 refines REQ-012: automatically subtract Ignore overlap, rather than introducing a whole-response-window rejection gate. OD-012 is resolved; OD-013 asks one concrete time-axis example before finalizing AC-012. The two 150-ms settings, N/C aggregation and C<N rule remain settled. Existing actual Collision/Ignore annotation-overlap restrictions are not implicitly removed. No source, test or architecture mutation is authorized.


### DISC-028: Preserve actual Collision annotation overlap rejection

- **Situation:** Ignore subtraction from an expanded response window must not relax validation of the manually annotated Collision interval itself.
- **Question:** Preserve rejection at annotation validation when actual Collision and Ignore intervals overlap?
- **Options and tradeoffs:** Preserving the existing gate keeps invalid truth annotations from reaching Learning while allowing Ignore subtraction only from the expanded response-window portion outside the Collision annotation. Relaxing that gate would alter previously confirmed labeling rules and was not requested.
- **User answer:** 但是原本在標註事件階段，仍拒絕collision與ignore時間區段重疊
- **Explicit rationale:** User explicitly preserves the original annotation-stage restriction; no additional rationale supplied.
- **Resulting impact:** REQ-010 and DEC-022 remain unchanged and explicitly confirmed. DEC-026/REQ-012 apply Ignore subtraction to the expanded response window without weakening annotation validation. AC-010 remains required. OD-013 still concerns only the exact subtraction/time-axis example; no additional open question is introduced.


### DISC-029: Confirm fixed deadline and unmodified time axis

- **Situation:** Both uses are set to 150 ms. Ignore overlap is removed from response evidence while the actual Collision annotation remains protected by annotation validation.
- **Question:** For Ignore at 60-90 ms, use the non-Ignore portions at 0-60 and 90-150 ms, retain the 150-ms endpoint, and do not compensate with later time?
- **Options and tradeoffs:** Fixed-time exclusion preserves an actual 150-ms deadline but leaves fewer eligible samples. Extending the window would admit detections beyond the selected deadline; compressing time would misrepresent actual latency. Neither time alteration was selected.
- **User answer:** 正確
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-027 finalizes DEC-026 and REQ-012; AC-012/AC-013 cover endpoint and Ignore behavior. REQ-002 and AC-002 reflect the revised numeric deadline, and AC-010 retains actual annotation overlap rejection. OD-013 is resolved, no open decisions remain, and canonical materialization is required. Implementation still requires a new exact execution authorization.


### DISC-030: Threshold must be above every Normal fluctuation

- **Situation:** Runtime diagnosis showed a diagnostic-only threshold near 2.94521 despite observed collision peaks above 10. The prior contract used the minimum of Normal interval maxima, which allowed the search to begin below larger Normal fluctuations.
- **Question:** Should the Normal lower-bound reference use the maximum of all eligible Normal interval maxima?
- **Options and tradeoffs:** Maximum-of-Normal-maxima prevents the search from beginning below any observed eligible Normal peak, but can make C<N and leave no separating threshold when the strongest Normal fluctuation exceeds the weakest Collision peak. The superseded minimum rule searches more sensitive thresholds but admits candidates below other Normal peaks and relies on Qualification to reject them.
- **User answer:** threshold must be above all Normal fluctuations.
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-028 supersedes DEC-002 for aggregation; REQ-001 and AC-001 now use N=max(Normal interval maxima) while C remains min(Collision window maxima). OD-014 remains because equality does not satisfy “above” under the detector's Score >= Threshold comparison. Existing C<N fallback remains applicable. No product, test, architecture, generated-view, Git, or external mutation is authorized.


### DISC-031: Strict detector comparison

- **Situation:** With N equal to the largest eligible Normal Score, the existing inclusive detector predicate `Score >= Threshold` would still trigger when a Normal sample equals N. OD-014 previously asked whether to move the first candidate above N.
- **Question:** Should the detector comparison itself change to strict `Score > Threshold`?
- **Options and tradeoffs:** Strict comparison keeps threshold N in the grid and prevents equality from triggering, but changes a detector boundary specified by SPEC-0001 and requires consistent Qualification, Replay, diagnostics, tests and exported semantics. Retaining inclusive comparison would require adding a positive margin above N.
- **User answer:** 改 `Score > Threshold`
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-029 and REQ-013 replace the inclusive predicate across all detector uses; AC-014 adds exact-equality boundary evidence. Threshold N remains included, OD-014 is resolved, and the release/re-arm predicate remains unchanged. SPEC-0001 REQ-004 is superseded only for the comparator. Product execution requires a new exact `開始執行` authorization.


### DISC-032: Strongest-Collision upper bound

- **Situation:** With N set above every eligible Normal fluctuation, the observed strongest Normal Score can exceed the weakest Collision peak and make the threshold interval empty. Changing C from the weakest to the strongest Collision peak can create a search interval, but admitted thresholds may miss weaker labeled Collisions.
- **Question:** Retain C as the weakest Collision peak, or change C to the strongest Collision peak while accepting possible weak-Collision misses?
- **Options and tradeoffs:** Option 1 preserves a bound intended to keep every labeled Collision detectable but rejects overlapping score distributions. Option 2 broadens the search through the strongest Collision peak and accepts that weaker Collisions may fall below threshold. The user selected option 2.
- **User answer:** 2
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-030 selects C=max(Collision window peaks) and supersedes the Collision portion of DEC-028. OD-015 remains open because current Qualification independently requires every labeled Collision to be detected, so changing C alone does not permit a weak-Collision miss to qualify. No product, test, architecture, generated-view, Git, or external mutation is authorized.


### DISC-033: Preserve all-Collision Qualification

- **Situation:** C=max broadens candidate generation, but current Qualification independently requires `detected == collision_count`. In an example with N=16 and Collision peaks 14, 18 and 25, threshold 16 is generated but misses the 14-point Collision and therefore fails Qualification.
- **Question:** Retain the requirement that every labeled Collision be detected, or relax Qualification to allow weaker Collision misses?
- **Options and tradeoffs:** Option 1 keeps the final detector acceptance strict and uses C=max only to broaden attempted thresholds, so overlapping data may still yield no qualified model. Option 2 would permit a model that detects only some Collisions and would require a new miss-rate policy. The user selected option 1.
- **User answer:** 1
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-031 and REQ-014 retain all-Collision Qualification while applying C=max only to search-bound construction; AC-015 verifies that weak-Collision misses still fail. OD-015 is resolved and no open decisions remain. Product execution still requires a new exact `開始執行` authorization.


### DISC-034: Exclude Collision response window from derived Normal

- **Situation:** In K058 `8mm_100`, the Score peak at index 18339 occurs after the manually annotated Collision end at index 18305 but before the Qualification deadline at index 18355. Existing workspace derivation classifies it as Normal while Qualification classifies it as Collision acceptance evidence, forcing N to 16.1424 even though threshold 10 can pass the selected high-speed Qualification scope.
- **Question:** After `Confirm all annotation sets`, should derived Normal Robot Motion automatically subtract the complete Collision onset-through-150-ms response window?
- **Options and tradeoffs:** Subtracting the shared response window aligns labeling, N calculation and Qualification while reducing Normal training support by at most the post-annotation remainder of each window. Retaining manual-end-only subtraction preserves more training samples but permits contradictory class identity. Extending the persisted/manual Collision annotation would alter user-authored geometry and project data unnecessarily.
- **User answer:** 沒錯
- **Explicit rationale:** The user first stated that Collision onset through 150 ms must not count as Normal, then confirmed the exact post-confirmation behavior.
- **Resulting impact:** DEC-032 and REQ-015 align derived Normal with the existing REQ-012 response window. AC-016 adds timestamp, Cycle, discontinuity, persistence and K058 regression evidence. No new public type, runtime state, module, port, event, callback, dependency edge or project schema field is introduced.

### DISC-035: Restore weakest-Collision upper bound

- **Situation:** The current implementation aggregates per-Collision 150-ms peak Scores with `max`, so the candidate range may include Threshold values above weaker labeled Collision peaks even though Qualification later rejects missed Collisions.
- **Question:** Keep the current strongest-Collision upper bound or restore the weakest-Collision upper bound?
- **Options and tradeoffs:** Keeping `max` explores a wider candidate range but can spend Qualification work on thresholds that cannot detect weaker labeled Collisions. Restoring `min` narrows the range to thresholds no greater than the weakest Collision peak; when that peak is below N, the existing model-skip and fallback behavior applies.
- **User answer:** 我想把目前C改回使用min
- **Explicit rationale:** The selected earlier recommendation defines C as the minimum of the individual Collision-window maxima so the Threshold upper bound remains below the weakest labeled Collision peak.
- **Resulting impact:** DEC-033 and REQ-016 supersede the C=max candidate-bound rule in DEC-030 and REQ-014. The 150-ms window, N=max, strict `Score > Threshold`, C<N fallback, and all-Collision Qualification remain unchanged. No public type, runtime state, module, port, event, callback, dependency edge or project schema field changes.
