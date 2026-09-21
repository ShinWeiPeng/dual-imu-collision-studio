---
spec_version: 1
spec_id: SPEC-0007
revision: 7
status: confirmed
change_set: replay-full-recording-prediction
---

# Full-recording FIR Replay Prediction

## Problem

Replay currently derives FIR eligibility from annotated Cycle membership. Samples outside a Cycle therefore receive non-finite FIR prediction values even when the imported recording is continuous, causing the exported prediction channels to fail to represent the expected External IMU waveform over the complete recording.

## Solution

Separate full-recording signal computation and qualification from annotation-scoped training. Continue FIR history across annotation boundaries and reset it only at a confirmed acquisition discontinuity. Compute prediction, residual, normalized residual, score, collision ratio, detector state, and trigger trace over every continuous recording segment. Fit the kernel from Normal Robot Motion, Pick, and Put samples inside confirmed Cycles while excluding Collision, Ignore, and Cycle-external samples. Evaluate final qualification over every non-Ignore sample: a trigger outside a Robot Fork Collision allowance is a false trigger, while each Robot Fork Collision must trigger within 20 ms of its start. Ignore alone does not affect pass/fail.

## User Stories

- As an analyst, I can compare continuous Internal IMU, FIR-predicted External IMU, Actual External IMU, residual, and detector traces over the complete exported recording.
- As an analyst, I can distinguish true FIR warm-up samples from samples that merely fall outside annotations.
- As an analyst, I can judge false collisions over every non-Ignore, non-collision portion of the recording and missed collisions within the governed 20 ms window without Ignore data affecting qualification.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Replay shall compute FIR-predicted External IMU for every sample in each continuous acquisition segment once the selected model has accumulated `tap_count` samples. |
| REQ-002 | Replay shall reset FIR history at each confirmed acquisition discontinuity and shall emit non-finite prediction values only for the first `tap_count - 1` samples of each resulting segment. |
| REQ-003 | Replay signal computation validity shall not reset at Cycle, event, or Ignore annotation boundaries. |
| REQ-004 | Replay CSV shall retain its governed header order and one-row-per-recording-sample alignment. |
| REQ-005 | FIR fitting shall use Normal Robot Motion, Robot Pick, and Robot Put samples inside confirmed Cycles; Robot Fork Collision, Ignore, and Cycle-external samples shall not enter fitting. |
| REQ-006 | Residual, normalized residual, detector score, collision ratio, detector state, and trigger trace shall be computed across every continuous recording segment wherever FIR history is valid. |
| REQ-007 | Qualification shall count a collision trigger in any non-Ignore sample outside the applicable Robot Fork Collision allowance as a false trigger, including Normal Robot Motion, Pick, Put, and unannotated Cycle-external samples; every Robot Fork Collision interval shall trigger no later than 20 ms from its start. |
| REQ-008 | Ignore intervals alone shall be excluded from false-trigger, missed-collision, latency, and pass/fail evidence. |
| REQ-009 | Detector score, confirmation, latch, release timer, state, and trigger processing shall continue through Ignore intervals without an Ignore-specific reset; Ignore-produced triggers remain diagnostic evidence but shall not enter qualification totals. |
| REQ-010 | False triggers in unannotated Cycle-external samples shall increment `normal_false_events` and participate in the existing total-misjudgment and PASS/FAIL arithmetic without adding a new persisted or exported false-event category. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Treat acquisition discontinuities, not annotations, as FIR history boundaries. | The user confirmed that prediction must continue outside Cycles and only the beginning of each true data segment may be invalid. |
| DEC-002 | Compute the complete Replay signal and detector trace across each continuous recording segment. | The user selected full-domain computation so every exported analytical field remains aligned and inspectable. |
| DEC-003 | Keep fitting Cycle-scoped but make qualification full-recording except for Ignore. | The user defined Ignore as excluded training/evaluation data and confirmed that Cycle-external triggers must also affect pass/fail. |
| DEC-004 | Train the FIR model with Normal Robot Motion, Pick, and Put while excluding Collision and Ignore. | Learning legitimate non-collision motion reduces Pick/Put residuals without teaching the predictor to reproduce collision shocks. |
| DEC-005 | Ignore affects training and qualification inclusion but does not interrupt detector execution or state. | The user wants complete detector evidence through Ignore while excluding its triggers from pass/fail. |
| DEC-006 | Aggregate unannotated Cycle-external false triggers into `normal_false_events`. | The user selected compatibility with the existing condition, project, UI, and generated Profile shape over separately auditable Cycle-external counts. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002, REQ-003 | A recording containing multiple Cycle, event, and Ignore boundaries but no acquisition discontinuity has exactly `tap_count - 1` leading non-finite prediction rows; adding one discontinuity creates exactly one additional warm-up region of the same bounded length. | Focused deterministic Replay unit test with identity FIR coefficients and exact row-index/value assertions. | Pending |
| AC-002 | REQ-004, REQ-006 | Exported CSV preserves the exact governed header and sample count, and every derived numeric/state/trigger cell matches aligned full-recording ReplayEvidence including bounded warm-up invalid values. | CSV artifact regression test parsed back into typed arrays. | Pending |
| AC-003 | REQ-005 | Fitting evidence contains every eligible Normal Robot Motion, Pick, and Put Cycle sample after History construction and contains no Collision, Ignore, or Cycle-external sample. | Deterministic fitting-evidence test with disjoint labeled sentinel ranges. | Pending |
| AC-004 | REQ-007, REQ-008 | Injected detector triggers in Normal, Pick, Put, and unannotated Cycle-external samples count as false triggers; a Collision trigger at 20 ms passes and one later than 20 ms fails; identical triggers in Ignore do not change qualification totals or status. | Parameterized qualification replay test with exact count, latency, and status assertions. | Pending |
| AC-005 | REQ-009 | A detector trace entering Ignore while ARMED or LATCHED continues with identical state-machine arithmetic across the Ignore boundaries; Ignore triggers appear in ReplayEvidence, do not alter qualification totals, and no reset marker is added solely because of Ignore. | State-machine boundary test with exact states, trigger indices, reset markers, and qualification totals. | Pending |
| AC-006 | REQ-010 | For identical traces, moving one false trigger between a Normal Robot Motion interval and an unannotated Cycle-external sample leaves `normal_false_events`, total misjudgments, status, project round-trip fields, UI false-count shape, and generated Profile struct layout unchanged. | Domain, controller, project-session, and Profile-export compatibility tests. | Pending |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | depends_on | DEC-001 |
| REQ-002 | depends_on | DEC-001 |
| REQ-003 | depends_on | DEC-001 |
| REQ-005 | depends_on | DEC-004 |
| REQ-006 | depends_on | DEC-002 |
| REQ-007 | depends_on | DEC-003 |
| REQ-008 | depends_on | DEC-003 |
| REQ-009 | depends_on | DEC-005 |
| REQ-010 | depends_on | DEC-006 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-004 |
| AC-003 | depends_on | REQ-005 |
| AC-004 | depends_on | REQ-007 |
| AC-005 | depends_on | REQ-009 |
| AC-006 | depends_on | REQ-010 |
| REQ-001 | refines | SPEC-0006 |

## Discussion Context

### DISC-001: Prediction validity boundary
- **Situation:** Current Replay prediction is finite only inside annotated Cycles, while the imported measurement remains continuous outside those annotations.
- **Question:** Should Cycle boundaries or acquisition discontinuities determine FIR history validity?
- **Options and tradeoffs:** Cycle-scoped history preserves current detector-oriented masking but creates non-physical prediction gaps; acquisition-scoped history produces a continuous model prediction but requires detector eligibility to be represented separately.
- **User answer:** Cycle outside also needs continuous prediction; only the first `tap_count - 1` samples of each segment may be invalid.
- **Explicit rationale:** The predicted External IMU should resemble the Actual External IMU waveform except for larger collision differences.
- **Resulting impact:** DEC-001 and REQ-001 through REQ-003 separate FIR prediction eligibility from annotation membership.

### DISC-002: Full-domain computation and annotation-scoped judgment
- **Situation:** Full-recording prediction can either stop at prediction alone or feed all derived Replay and detector fields, while training and final qualification still require explicit annotation semantics.
- **Question:** Which fields are computed outside Cycles, which samples train the kernel, and which annotations contribute final qualification evidence?
- **Options and tradeoffs:** Prediction-only computation is a smaller change but leaves derived CSV columns discontinuous; full computation produces coherent diagnostics but must keep evaluation masks separate to avoid changing qualification denominators.
- **User answer:** Compute all fields over the full recording. Train the kernel from Cycle data except Ignore. Judge false collisions over all non-Ignore data, including Pick, Put, Normal Robot Motion, and Cycle-external samples; require collisions within 20 ms; do not judge Ignore.
- **Explicit rationale:** Ignore means data excluded from training and judgment, while the learned kernel should process all Internal IMU samples to predict External IMU.
- **Resulting impact:** DEC-002 and DEC-003 add REQ-005 through REQ-008; fitting remains Cycle-scoped while computation and non-Ignore qualification cover the full recording.

### DISC-003: FIR fitting activity scope
- **Situation:** Current source fits only Normal Robot Motion. Training on every non-Ignore Cycle sample would also include Collision, which can teach the predictor to reproduce the anomaly that the detector is intended to expose.
- **Question:** Should fitting use only Normal Robot Motion, all legitimate non-collision motion, or every non-Ignore Cycle sample including Collision?
- **Options and tradeoffs:** Normal-only fitting isolates all events but may increase Pick/Put false residuals; Normal plus Pick and Put learns legitimate operating motion while preserving collision novelty; including Collision maximizes rows but can reduce collision residual and sensitivity.
- **User answer:** Option 2: train with Normal Robot Motion, Pick, and Put; exclude Collision and Ignore.
- **Explicit rationale:** The recommended option was selected; no additional rationale was stated.
- **Resulting impact:** DEC-004 refines the training side of DEC-003 and updates REQ-005 and AC-003.

### DISC-004: Ignore detector-state semantics
- **Situation:** Excluding Ignore triggers from qualification does not determine whether detector confirmation, latch, and release state continue through Ignore or reset at its boundaries.
- **Question:** Should Ignore triggers count as false triggers, remain diagnostic-only while state continues, or invalidate/reset detector processing?
- **Options and tradeoffs:** Counting them makes Ignore affect pass/fail; continuous diagnostic-only processing preserves the full trace but permits state to carry across Ignore; invalidating/resetting isolates later qualification but removes detector evidence inside Ignore.
- **User answer:** Option 2: detector continues through Ignore, but Ignore triggers do not enter pass/fail.
- **Explicit rationale:** Ignore is unwanted training data, while detector should still be able to process it.
- **Resulting impact:** DEC-005, REQ-009, and AC-005 preserve continuous detector execution while keeping Ignore outside qualification totals.

### DISC-005: Cycle-external false-trigger representation
- **Situation:** Existing `ConditionQualification`, UI, project persistence, and generated Profile contracts expose Normal, Pick, and Put false-event counters but no Cycle-external category.
- **Question:** Should Cycle-external false triggers receive a new field, be aggregated into Normal, or affect only the total without classified evidence?
- **Options and tradeoffs:** A new field is explicit but changes named and persisted/exported contracts; Normal aggregation preserves compatibility but loses source distinction; total-only accounting can produce a FAIL without classified detail.
- **User answer:** Option 2: aggregate Cycle-external false triggers into `normal_false_events`.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-006, REQ-010, and AC-006 preserve the existing data shape while broadening the operational meaning of `normal_false_events`.

## Out of Scope

- Changing fitted FIR formula, coefficient layout, Ridge alpha selection, or robust-refit rules.
- Changing the Replay CSV header order or project persistence format.
- Changing collision truth annotations or the inclusive 20 ms collision deadline.
- Counting Ignore samples toward qualification.

## Open Decisions

None.

## Routing/Gates

- Risk: governed algorithm and Replay data-flow change.
- Required before implementation: confirmed specification, algorithm record update, architecture design gate, TDD, development architecture gate, and code review.
- Exact `開始執行` authorization is required before product files are modified.

## Revision History

| Revision | Change |
|---|---|
| 1 | Started the change set from the confirmed full-recording FIR prediction requirement and recorded the remaining derived-signal scope decision. |
| 2 | Selected full-domain Replay computation and confirmed annotation-scoped fitting and qualification, including Normal Robot Motion false-trigger judgment. |
| 3 | Corrected qualification to include Cycle-external samples and exclude only Ignore. |
| 4 | Corrected the cross-spec relationship source so canonical materialization can preserve traceability to SPEC-0006. |
| 5 | Selected Normal Robot Motion, Pick, and Put as FIR fitting evidence while excluding Collision, Ignore, and Cycle-external samples. |
| 6 | Confirmed continuous detector execution through Ignore while excluding Ignore triggers from qualification. |
| 7 | Selected compatibility-preserving aggregation of Cycle-external false triggers into `normal_false_events`. |
