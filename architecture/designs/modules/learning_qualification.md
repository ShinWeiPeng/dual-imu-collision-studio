# learning_qualification

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | learning_qualification |
| version | 1 |
| kind | module |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: learning_qualification
  level: L1
  role: domain
  implementation_status: implemented
  paths:
  - src/dual_imu_collision_studio/domain/learning
  parent: studio_application
  depends_on: []
  implements_ports: []
  description:
    purpose: Fit independently selected FIR and custom-depth MLP candidates, retain
      original fold kernels and replay exact frozen predictions across supplied conditions.
    input_ports:
    - learning.command
    - learning.replay-export
    - learning.model-export
    output_ports:
    - learning.events
    - learning.history-execution
    - learning.execution
    - learning.replay-file-output
    - learning.model-file-output
    emitted_events:
    - learning.progressed
    - learning.completed
    - learning.cancelled
    owned_state: []
    side_effects: []
    errors: []
    invariants:
    - Qualification always replays all supplied speeds.
    - Qualification always replays all supplied offsets, including offsets excluded
      from subsequent fitting rounds.
    - Every supplied speed and offset tuple retains exact activity denominators, false-trigger
      counts, collision detections, latency, and status provenance.
    - Every completed per-recording Qualification result retains all Collision Detector
      Score SNR values in chronological order. Signal is the finite Score peak in
      the existing inclusive 150-ms response window; shared noise is finite Score
      RMS outside annotated Collision and Ignore intervals. Invalid positive finite
      ratios remain unavailable and never change Qualification decisions.
    - SPEC-0011 uses configurable two-to-ten complete-Cycle folds, default three.
      Each recording has at least two valid Cycles; each condition has at least N.
      Every fold retains Training from every recording and Validation from every condition
      with per-condition counts differing by at most one. Counts/allocation failure
      stops the run; no automatic N reduction.
    - Each Start captures new settings and seed; each round captures a balanced fold
      map reused by every parameter candidate. Common Training and Validation targets
      support 128 ms History and exclude Collision and Ignore. Missing common targets
      skip the round without resampling or lowering History.
    - Candidate Loss is the maximum across conditions of the equal-fold average of
      Validation MSE, or the default half Training plus half Validation MSE. Target-cast
      original fold models supply prediction and subtraction before float64 squaring.
      Residual STD uses only final fitting rows.
    - Search jointly optimizes tap depth through 128 ms and continuous Ridge alpha
      from 1e-6 to 100; integer K from 2 to 32 is active only with optional Robust
      refit, default off. Coarse top two plus raw ties seed fine search. Neighbors
      project to bounds before deduplication; final steps are one tap, one K, and
      alpha factor 1.05 with configured relative improvement tolerance. All paths
      complete; each effective parameter/fold runs once per context.
    - Fixed-grid mode accepts only checked 4/8/16/32/64/128 ms History aliases and
      checked 1e-6/1e-4/0.01/1/100 Ridge alphas, deduplicates equal effective taps
      while preserving aliases, fixes Robust K to zero, and performs no coarse or
      fine search. Its effective Cartesian-product points reuse the same grouped N-fold
      Loss ranking, Validation allowance, fold-kernel selection, Qualification and
      fallback path as optimized mode; evaluated nonwinning points remain visible
      as CV-rejected evidence.
    - All valid parameters within the configured relative convergence tolerance of
      the minimum raw Parameter Loss are retained. Per-condition raw Validation allowance
      filters their original fold kernels, then each parameter retains every fold
      whose raw maximum-condition Kernel Loss exactly equals that parameter's raw
      minimum; rounded and second-place near ties are excluded. Every admitted parameter
      and fold completes Qualification before ranking. No final all-data refit or
      worse-parameter rescue occurs.
    - A passing collision detection has latency no greater than 150 ms from the confirmed
      collision interval start, inclusive, regardless of interval end.
    - A recording passes when at least one Collision interval exists, every Collision
      is detected within the inclusive 150 ms onset deadline, and every present Normal,
      Pick, or Put interval has zero false triggers. A missing Normal, Pick, or Put
      class is neutral; missing Collision evidence is COVERAGE_GAP.
    - A retained fallback is accepted only when its training range equals its qualified
      range.
    - Each outer round trains all remaining offsets and exhausts lowest-speed removal
      until the active range passes or only one speed remains. Success or exhaustion
      then excludes the smallest active offset and restores all supplied speeds.
    - Only full active-range matches enter the qualified pool. Ranking prefers more
      supplied speed strata, more active offsets, shorter taps, lower worst latency,
      larger robustness margin, then stable parameter order (SPEC-0008; ALG-0004).
    - Proven insufficient Training evidence skips only that round, preserves earlier
      retained winners, and continues suffix/offset progression. Unavailable scopes
      and reasons remain in progress and completed results; unclassified empty models
      and input/resource/unexpected execution failures are not missing evidence. Narrowly
      classified candidate numerical failures invalidate that full-N parameter configuration
      with parameter and fold diagnostics; they never fabricate Loss.
    - SPEC-0009 derives per-model N as the maximum of active-round Normal interval
      maxima and C as the minimum of active-round per-Collision window maxima. Collision
      uses its inclusive onset-through-150-ms window excluding Ignore. Search starts
      at N with step 0.5 and includes C, omits zero and duplicate target values, and
      never expands the bounds. Qualification still requires every labeled Collision
      to be detected.
    - Qualification, Replay, and exported Profile semantics use the strict detector
      predicate Score greater than Threshold; equality does not fill confirmation
      history. Release and re-arm remain strictly below release_ratio times Threshold.
    - Collision response evidence is the fixed onset-through-150-ms window minus Ignore
      samples. Preserve timestamps and retain eligible samples after Ignore; do not
      extend or shorten the absolute deadline, compress time, or reset detector state.
      Actual Collision annotations still cannot overlap Ignore.
    - Derived Normal evidence and Collision acceptance evidence use the same onset-through-150-ms
      boundary, so one sample cannot belong to both classes for the same Collision.
    - Missing whole-round bound evidence skips that round; C below N or no positive
      candidates skips that model with bounds and reason. Existing fallback and earlier
      qualified results are retained. Numerical failures are never evidence shortages.
    - For one fixed History, frozen model, target numeric type, Score Mode, and recording,
      normalized detector scores are computed once and reused across Threshold and
      Confirmation candidates without crossing the frozen-fold-kernel lifetime.
    - Diagnostic ranking compares retained selected fold-kernel results over every
      supplied recording by total false trigger events plus missed collision intervals,
      then finite worst collision latency, retaining all exact ties.
    - Diagnostic-only winners are never exportable Profiles.
    - Replay CSV serialization preserves full-resolution sample alignment and emits
      the exact governed diagnostic header order without substituting display-only
      zeroes.
    - Training uses only Cycle-contained Normal Robot Motion, Robot Pick, and Robot
      Put samples; Collision, Ignore, and Cycle-external samples are excluded and
      split FIR history.
    - Replay prediction and detector arithmetic start at the first sample with unavailable
      Internal FIR history initialized to zero. Numeric startup scores participate
      normally; successfully interpolated gaps preserve FIR and detector continuity.
    - Ignore never resets or pauses detector state; Ignore evidence remains visible
      but is excluded from Training and qualification pass or fail counts only.
    - Qualification counts false triggers in every non-Ignore Normal, Pick, Put, and
      Cycle-external sample; Cycle-external events aggregate into normal_false_events
      for compatibility.
    - Model TXT serialization emits deterministic scalar metadata, FIR weights, bias,
      residual center, and residual scale without changing stored project or profile
      schemas.
    - Search and fold-selection progress publishes typed Loss evidence; every retained
      candidate preserves the exact ordered per-recording Qualification metrics used
      by its condition aggregates.
    - Cancellation retains only candidates whose complete Qualification evidence committed
      before cancellation observation. Completed qualified candidates remain selectable;
      only when none qualifies does the existing minimum-total-error, finite-latency,
      exact-tie diagnostic ranking become visible. The terminal state remains Cancelled.
    - FIR and MLP sample and select independently; model-family results retain separate
      seeds, fold maps and immutable kernels.
    - MLP hidden depth is a custom positive integer defaulting to two; each layer
      independently selects widths 4,8,16,32,64,128. Only selected Cartesian combinations
      run; no final all-data refit.
    - SPEC-0030 adds one-sensor Ridge self-prediction using only lags 1..L, adopted
      causal SOS preprocessing, explicit warmup, continuous Ignore history and separate
      frozen model identity.
    - SPEC-0044 Training Qualification and Replay share strict 1_OF_1 collision triggering
      and fixed 0.8/50 ms continuous-valid-time rearm. Invalid data or discontinuity
      clears quiet time without releasing the latch. Frozen-model requalification
      never fits or narrows the required original speed/offset coverage.
    - SPEC-0045 captures chronological collision decisions, trigger indices/times,
      latency, margins and SNR unavailable reasons in the same Qualification pass.
      Retained candidates carry their actual policy. Numerical detection and Training
      are unchanged.
    - SPEC-0046 FIR fitting and prediction borrow source samples and construct at most
      eight MiB of float64 feature rows per block. Ridge accumulates centered
      statistics and Gram/RHS by block, with unchanged alpha, degeneracy, valid-row,
      channel/lag order, target rounding, exact residual calibration and robust
      selection contracts. Dense features remain explicit for MLP. Frozen results
      never retain lazy feature rows, block buffers or original fitting samples.
  entrypoints:
  - path: src/dual_imu_collision_studio/domain/learning/service.py
    symbol: LearningService
    kind: class
  public_symbols:
  - path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: LearningCommandPort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: LearningEventPort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: HistoryExecutionPort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: ReplayCsvFilePort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: ModelTextFilePort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/learning/service.py
    symbol: LearningService
    kind: class
  - path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: LearningExecutionPort
    kind: class
  - path: src/dual_imu_collision_studio/domain/learning/self_imu.py
    symbol: service_for_dataset
    kind: function
  - path: src/dual_imu_collision_studio/domain/learning/deployment.py
    symbol: DeploymentQualification
    kind: class
  - path: src/dual_imu_collision_studio/domain/learning/deployment.py
    symbol: replay_common_events
    kind: function
  - path: src/dual_imu_collision_studio/domain/learning/deployment.py
    symbol: deployment_identity
    kind: function
```
