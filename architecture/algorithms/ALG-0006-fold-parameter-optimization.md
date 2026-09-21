# ALG-0006: Selectable cycle-fold FIR parameter evaluation

Status: proposed record of user-confirmed SPEC-0011 revision 150 and SPEC-0013 revision 7; not an accepted ADR.
Owner: learning_qualification. Parent: studio_application. Execution adapter: history_worker_adapter.
Authoring tables and cost alternatives: ../change-plans/SPEC-0011-optimizer.md and
../change-plans/SPEC-0013-selectable-training-modes.md.

## Algorithm and contracts

Start captures target dtype, validated LearningSettings, its fixed-grid or optimized
Training mode, and a new 64-bit seed. Every
recording needs two valid Cycles and every active Speed x Offset condition needs N.
Cycle-count or allocation failure is terminal. Condition-local shuffled recording
blocks and shuffled Cycle order are distributed cyclically over permuted fold labels.
This gives floor/ceiling condition counts and at least two roles per recording;
every Cycle is Validation once. Each round has its own saved seed and actual map.
All parameters share that map and Training/Validation common targets supporting
128 ms. No required common target means skip that round, never lower History or N.

Each candidate-fold fit uses candidate-specific eligible FIR support. Plain Ridge
retains all eligible fitting rows; optional Robust mode retains the existing one
hard-rejection refit with five-percent cap. Both cast final coefficients to target
dtype, evaluate in exact Replay accumulation/subtraction order, and square residuals
in float64. Final residual center/STD uses final fitting rows only. Excluded robust
rows remain in common-target MSE. Fixed STD/L2_NORM detector behavior is separate
from Loss aggregation.

Per condition, average fold losses equally (Validation alone or half Training plus
half Validation), then take the maximum condition. Coarse grid: H 0/4/8/16/32/64/128,
alpha 1e-6/1e-4/.01/1/100, optional integer K 2/4/8/16/24/32. Deduplicate realized taps.
Top two raw losses plus second-place ties start independent joint-neighborhood fine
search. Project proposed coordinates to boundaries before deduplication. Cache each
effective parameter once for the round. Strict improvements move at current steps;
otherwise halve integer steps and square-root alpha ratio down to 1.05. Full final
neighborhood and relative improvement tolerance govern convergence, not elapsed time.
Keep all intermediate results. Let `L_min` be the minimum valid raw Parameter Loss;
final optimized-mode parameters are exactly those with
`loss <= L_min * (1 + convergence_tolerance_percent / 100)`. The Loss calculation
itself is unchanged. This relative admission rule replaces decimal half-up
four-place Parameter ties.

Fixed-grid mode replaces only that candidate-source stage. It accepts checked History
values from 4/8/16/32/64/128 ms and checked alpha values from
1e-6/1e-4/.01/1/100, deduplicates sample-rate-equivalent tap counts while retaining
ordered History aliases, evaluates their Cartesian product with Robust K fixed to zero,
and performs no coarse/fine neighborhood search. All effective points still complete the
same N-fold aggregation. Only parameters inside the same configured relative raw-Loss
window continue to the Validation-allowance, fold-kernel selection and Qualification stages; evaluated
nonwinners remain visible as CV-rejected evidence. New and legacy projects intentionally
default to fixed-grid with empty selections and cannot start until both sets are nonempty.

Filter those groups' original fold kernels by every-condition raw Validation allowance.
For each retained parameter, calculate the minimum raw maximum-condition Kernel Loss
among surviving folds and retain every fold exactly equal to that raw minimum. Do not
retain rounded near ties or second place. Never refit all data, merge different parameter
identities, choose a worse group as rescue, select before all paths finish, or stop
Qualification on the first full-range PASS.
Qualification uses the original coefficients/calibration over all supplied recordings;
N/C and inclusive 150-ms-minus-Ignore rules are unchanged. Retain all qualifying
selected kernels with original settings, fold map, losses and round provenance.
Continue the confirmed offset/speed fallback, reoptimizing the next scope.

Qualification progress identifies the current ParameterPoint and original fold and
reports completed and remaining admitted-kernel counts. The total is their sum and is
fixed after parameter/fold admission for that round.

## Execution, alternatives, failure and evidence

One coordinator owns search and barriers. learning.execution schedules at most eight
candidate-fold jobs, or four whole-recording jobs for Qualification. Processes reuse
one immutable context per batch; no nested pools or chunked detector state. Stable
job identity, not completion order, associates results. Duplicate/incomplete batches
fail closed. Cancellation, resource failure, startup failure and unexpected exits
terminate all workers; no retry or adaptive worker reduction is authorized.
Narrow numerical candidate failures require parameter/fold diagnostics and invalidate
that parameter aggregate; input/program errors are terminal. No epsilon repairs STD.

Serial execution remains the differential reference. Matrix storage is O(rows*taps),
normal solve O((3*taps)^3); all-N model caching and tie continuation can increase work.
No global optimum, speedup, wall-clock or native scheduler/memory capacity claim is
made without measured evidence. Existing launch-available 85% RSS admission remains.
Functional checks use pytest public service, execution-port, controller and persistence
seams. Native runtime acceptance is separate and requires a selected validation profile;
none currently exists in this repository. See SPEC-0011 implementation evidence.
