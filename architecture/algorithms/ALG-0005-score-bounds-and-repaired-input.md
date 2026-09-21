# ALG-0005: Score bounds and repaired input

## Authority and ownership

Confirmed SPEC-0009 revision 39; execution authorized by Hugo Peng (`開始執行SPEC-0009/0015`).
Status: proposed; no ADR acceptance is implied.
Semantic owners: data_workspace L1 for input/annotation eligibility;
learning_qualification L1 for FIR, Score, threshold search and Qualification.
TabularReader realizes the workspace import contract; StudioController owns mapping
to project_session storage and QML presentation. Dependency directions are unchanged.
Boundary, type, state and parent tables: `architecture/reviews/SPEC-0009-precode.md`.
Flows: prepare-workspace, learn-and-qualify, manage-project.

## Inputs, outputs and selected algorithm

Input timestamps are seconds with the existing median-delta inferred nominal period.
For a detected gap, round elapsed/nominal period to the nearest integer n. Missing
count is n-1. Reject the recording at four missing samples, or if dividing elapsed
into n equal intervals differs from nominal by more than 2% (inclusive boundaries,
only floating comparison tolerance). For one through three missing samples, interpolate
each of six raw axes at fractions k/n. Copy measured endpoints exactly. Source bytes
remain unchanged. Persist inserted indexes and verify them when rereading a project.

Import once, then feed the expanded sequence to every analytical consumer. Labels
use expanded sample indexes. Normal/Pick/Put remain fit eligible; Collision/Ignore
are not fit evidence. Repairs do not reset FIR, pending confirmation, latch or re-arm.
Expose locations/counts in both annotation waveforms. The existing annotation
confirmation suffices. Ignore/Collision annotation overlap is invalid; adjacent
half-open intervals remain valid and the ban does not extend to the 150-ms window.

FIR prediction at every sample uses bias and measured lag-zero input; unavailable
prehistory taps use zero in the target dtype. Startup residual and Score participate
normally. Each frozen model produces one reusable Score array per recording.
Within the active speed/offset round, take each Normal interval maximum and each
Collision onset-through-150-ms inclusive maximum (excluding Ignore). N is the maximum
of the Normal interval maxima, so every Normal interval peak is covered. C is the
minimum of the per-Collision window maxima pooled across eligible recordings. Do not
require both classes in every recording.

Missing whole-round classes skip the round. C<N or no positive candidates skip only
that model, retaining raw bounds and a reason. Otherwise enumerate N+k*0.5 through C,
cast to target arithmetic, omit zero and duplicate values, and append C if needed.
Each confirmation mode still runs complete Qualification across all supplied conditions,
and every labeled Collision must still be detected; C only bounds candidate generation.
Every detector consumer uses `Score > Threshold`; equality does not fill confirmation
history. Release and re-arm retain the strict `Score < release_ratio * Threshold` rule.
Exported C99 and C++17 headers declare the same strict comparator contract.
Merge histories deterministically, renumber stable ordering, continue existing fallback,
and retain previously qualified kernels. Nonfinite arithmetic and resource failures
are execution failures, never missing evidence or fabricated zero outputs.

## Alternatives, cost, risks and evidence

Fixed 5..20 search, minimum-of-Normal-maxima, inclusive `Score >= Threshold`, NaN
warmup, per-replay interpolation, and a fixed 3-ms repair limit conflict with the
confirmed choices and are rejected.
Repair takes O(R+I) time/storage, with expanded rows at most 4R-3. FIR remains O(RL).
Bound cost is linear in selected support; grid and detector cost depend on C-N.
There is no artificial range cap. Existing four-worker timeout/memory supervision
is unchanged. No new worker, queue, scheduling study, throughput claim or device
parity claim is introduced. New project contract is version 2; legacy migration is
out of scope and existing source/project files are not rewritten.

Validation uses public import, workspace, History/round, replay and project seams:
`tests/test_tabular_reader.py`, `tests/test_workspace.py`,
`tests/test_learning_run.py`, `tests/test_diagnostic_replay.py`,
`tests/test_project_session.py`, `tests/test_qml_smoke.py` and the spawn differential
suite. Current results and incomplete release evidence belong in the SPEC-0009
implementation evidence report, not inferred algorithm acceptance.

## Revision 31 timing amendment

The fixed window is [t0,t0+150 ms] minus the union of Ignore sample intervals.
Ignore is half-open; a deadline sample inside Ignore is excluded. Do not pause,
compress or compensate time, truncate at the first Ignore, or reset detector state.
Qualification, selected-event Replay latency, Profile export, saved result validation
and user-visible policy text apply the same 150-ms deadline. Original annotation
overlap rejection remains unchanged. See SPEC-0009-150ms.md for validation evidence.

## Revision 36 Collision-bound amendment

C is the strongest eligible Collision-window peak rather than the weakest. This
widens candidate enumeration when Normal and weak-Collision Scores overlap, but does
not relax acceptance: Qualification still fails every candidate that misses any
labeled Collision. The rejected alternative retains the weakest-Collision upper bound,
which prevents evaluating the wider range but guarantees every enumerated threshold is
below every Collision peak before confirmation-state replay.

## Revision 37 Normal-derivation amendment

After a complete annotation set is confirmed, derived Normal Robot Motion subtracts
the same timestamp-based inclusive `[t0, t0 + 150 ms]` Collision response window used
by C extraction and Qualification. The subtraction is clipped at the containing Cycle
and stops at the first true acquisition discontinuity. The user's explicit Collision
start/end indexes remain unchanged and persisted as authored; the extended exclusion is
derived, read-only eligibility. Studio application supplies the Learning-owned response
duration when it maps workspace evidence, preserving sibling dependency inversion.

This prevents a response sample after the manual Collision end from simultaneously
raising N as Normal evidence while Qualification accepts it as Collision evidence.
The selected approach changes the workspace derivation source of truth. The rejected
threshold-only mask would leave Training and the annotation UI with contradictory
Normal regions; extending the persisted Collision annotation would rewrite user-owned
truth. Complexity remains linear in annotations and response-window support, with no
new worker, queue, allocation policy, runtime state, persistence field, execution unit,
or real-time claim.

## Revision 39 weakest-Collision amendment

For each frozen model and active fallback round, compute one maximum Score for every
eligible Collision's inclusive onset-through-150-ms response window after existing
Ignore masking and discontinuity clipping. Pool those per-Collision maxima across all
recordings whose Speed and Offset remain active, then set C to the minimum pooled
value. Do not average by recording or take the minimum of raw samples.

The selected method prevents candidate enumeration above the weakest labeled
Collision peak. The superseded strongest-Collision reduction produced a wider range
but necessarily evaluated candidates that could not satisfy the unchanged
all-Collision Qualification rule. Both reductions are deterministic O(number of
Collision windows) after the same O(evidence samples) peak scan and have identical
memory, worker, fallback, and execution behavior.
