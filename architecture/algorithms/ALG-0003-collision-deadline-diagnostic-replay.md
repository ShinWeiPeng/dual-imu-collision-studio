# ALG-0003: Collision deadline, diagnostic ranking, and analytical Replay

## Metadata

- Status: accepted
- Owner module: `learning_qualification`
- Product feature: 150 ms collision Qualification and minimum-misjudgment Replay diagnostics
- Flow IDs: `learn-and-qualify`
- Related ADRs: None
- Source paths: `src/dual_imu_collision_studio/domain/learning/model.py`, `src/dual_imu_collision_studio/domain/learning/service.py`, `src/dual_imu_collision_studio/adapters/desktop/controller.py`, `src/dual_imu_collision_studio/qml/Main.qml`
- Test and benchmark paths: `tests/test_candidate_qualification.py`, `tests/test_learning_run.py`, `tests/test_controller_export.py`, `tests/test_qml_smoke.py`
- Supersedes: The 10 ms qualification boundary described by ALG-0002; ALG-0002 otherwise remains applicable to parallel fitting and score caching.

## Problem and observable success

The former 10 ms rule rejects useful triggers that occur shortly after collision onset, and a failed run exposes no comparable best-available retained kernel. Replay also lacks the FIR prediction and detector evidence needed to explain a result. Success means exactly-150-ms triggers pass, later triggers fail, qualified export behavior remains unchanged, failed runs expose only the minimum-error retained round winner set, and Replay reproduces target-numeric analytical arrays without altering timing through display decimation.

## Inputs, outputs, units, ranges, and data-quality assumptions

- Inputs are the immutable supplied `LearningDataset`, one retained `QualifiedCandidate`, and one selected complete recording. Event annotations remain collision truth for Qualification but are not Replay export selectors.
- Time is seconds internally and milliseconds for displayed latency.
- Collision truth starts at the confirmed Fork Collision interval start. The interval end does not shorten the response window.
- False events are emitted triggers in every non-Ignore sample outside an applicable collision allowance. Normal Robot Motion and unannotated Cycle-external triggers aggregate into `normal_false_events`; Pick and Put retain their existing counters.
- A missed collision is one confirmed Fork Collision interval with no eligible trigger through onset plus 150 ms inclusive.
- Normal, Pick, and Put classes are evaluated only when their intervals occur. An absent non-Collision class is neutral; any false trigger in a present class fails the recording.
- Collision evidence is mandatory. A recording with zero Collision intervals is a Coverage Gap rather than PASS or an unexplained Fail.
- Replay arrays retain one analytical value per expanded recording sample, including repaired samples. Missing prehistory is zero in target arithmetic, not intentional NaN; repaired gaps introduce no reset (SPEC-0009). QML may decimate only during rendering.

## Constraints and quantitative acceptance thresholds

- Collision deadline: `150 ms`, inclusive with floating-point tolerance.
- Re-arm quiet time: unchanged `50 ms`.
- Diagnostic pool: exactly one existing retained winner from each completed fallback round.
- Comparison denominator: every supplied recording, including excluded speed/Offset conditions.
- Diagnostic rank: minimum total errors, then minimum finite worst detected-collision latency, then all exact ties.
- When no minimum-error winner has finite latency, retain every minimum-error winner and display `N/A` plus exact detected/total collision counts.
- Diagnostic-only winners are not accepted by Profile Export.

## Candidate methods and comparative evidence

1. Rank every evaluated detector candidate: potentially finds a lower-error model but violates the selected one-winner-per-round retention architecture and materially increases retained data.
2. Rank only retained round winners over their active fallback scope: cheap, but incomparable shrinking denominators favor narrow late rounds.
3. Rank retained round winners over all supplied recordings: selected because every candidate uses the same truth and denominator while preserving bounded retained state.

For Replay, recomputing typed FIR prediction from the frozen model is selected over persisting waveform arrays. It preserves exact current-source evidence and avoids enlarging `.dicsproj` storage.

## Selected method and reasons for rejecting alternatives

Qualification extends the eligible trigger boundary to onset plus 150 ms. Each retained winner already contains all-supplied `ConditionQualification` evidence, so diagnostic totals are derived without resurrecting discarded candidates. Replay recomputes prediction, residual, normalized residual, score, ratio, state, and trigger evidence from the retained frozen model and complete selected source recording. FIR history resets only at recording start and acquisition discontinuities; annotations, including Ignore, do not reset prediction or detector state.

## Exact behavior, formula or pseudocode, boundaries, and tie-breaking

```text
eligible(trigger, collision) =
    trigger_index >= collision.start_index
    and trigger_time <= collision_start_time + 0.150 + tolerance

recording_passes =
    collision_interval_count > 0
    and collision_detected_count == collision_interval_count
    and worst_collision_latency_ms <= 150 + tolerance
    and normal_false_events == 0
    and pick_false_events == 0
    and put_false_events == 0

recording_status =
    COVERAGE_GAP if collision_interval_count == 0
    else PASS if recording_passes
    else FAIL

false_triggers(candidate) =
    sum(normal_false_events + pick_false_events + put_false_events)

missed_collisions(candidate) =
    sum(collision_interval_count - collision_detected_count)

total_errors(candidate) = false_triggers + missed_collisions

minimum = candidates with minimum total_errors
if any minimum candidate has a finite detected-collision latency:
    keep candidates having the minimum finite latency
else:
    keep all minimum candidates and expose latency as N/A
```

Exact ties are retained in stable fallback completion order. FIR prediction uses the frozen target numeric type and existing tap ordering. `residual = actual_external - predicted_external`; normalized residual uses the frozen centers and scales; score and detector state use the existing replay function.

## Parameters, calibration, versioning, and compatibility

The 150 ms deadline is a product rule, not a tunable user parameter. Existing saved Profiles produced under the stricter 10 ms rule remain valid and are presented as current without migration or legacy labeling. No waveform arrays or diagnostic-only kernels are added to the project storage format.

## Time and space complexity and resource budgets

Diagnostic ranking is `O(R)` in retained round winners after existing Qualification evidence is available. One selected Replay recomputation is `O(N * 9 * L)` time for `N` samples and `L` taps and `O(N)` output storage. It runs after Training, not in the four-worker candidate grid, and does not change the existing fallback-round or Peak RSS budgets. The cost model is estimated; public numerical tests and a bounded Windows UI smoke run provide implementation evidence.

## Errors, degradation, fallback, and forbidden behavior

- A retained candidate lacking a model, History, or detector configuration cannot produce Replay evidence and is shown as unavailable rather than fabricated.
- A selected recording not present in the supplied dataset is rejected.
- Diagnostic-only candidates remain visible but cannot be selected for export.
- Forbidden: counting one missed collision multiple times, shortening the 150 ms window to the annotation end, comparing different denominators, ranking discarded non-winners, persisting analytical arrays, or changing the 50 ms re-arm rule.

## Validation cases and evidence

- Boundary vectors at 149 ms, exactly 150 ms, and 151 ms with collision intervals shorter than 150 ms.
- Recordings with each absent Normal/Pick/Put class, no Collision interval, and false triggers in present non-Collision activity.
- Error totals that include repeated false triggers and one count per missed collision.
- Winner fixtures for finite-latency tie-breaks, exact ties, and all-`N/A` latency.
- Controller/export tests proving diagnostic-only candidates remain visible and non-exportable.
- Numerical Replay tests for complete-recording predicted External IMU, residual, normalized score, ratio, detector state, trigger indexes, zero-initialized startup, and Ignore/repaired-gap state continuity.
- QML runtime tests for the recording-only selector, Replay CSV and Model TXT actions, absence of Cycle/Event APIs, and collision-safe suggested filenames.
- Development architecture gate and bounded Windows application smoke test.

## Risks and monitoring

Display decimation could appear to move peaks if it were reused analytically; therefore only `WaveformItem` rendering may decimate. A diagnostic winner can still be unsuitable for deployment; the UI must state its error count and non-qualified status.

## Human approval

- Approved by: Hugo Peng
- Approval date: 2026-08-26
- Approval reference: `SPEC-0004` revision 8 and the user's explicit `開始執行` authorization.

## Pre-code architecture gate

### Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Rank retained winners and obtain selected analytical Replay | `learning_qualification` | `studio_application` | `studio_application` | `QualificationResult`, `ReplayEvidence` | Controller-owned immutable QML maps/lists | `studio_application` | Completed Learning result and selected source recording; no child mutable state | `studio_application->learning_qualification`, QML->`StudioController` | `learning_qualification->desktop_adapter`, `learning_qualification->profile_export` |
| Export a selected result | `learning_qualification` | `profile_export` | `studio_application` | Qualified `QualifiedCandidate` | `SemanticProfile` | `studio_application` | Completed qualified candidates only | `studio_application->learning_qualification`, `studio_application->profile_export` | `learning_qualification->profile_export`, diagnostic-only export |

### Type Ownership Matrix

| Type | Owner/level | Declaration | Semantic kind and visibility | Lifetime/mutability/authority | Consumers and references | Field impact | ABI/wire/storage impact |
|---|---|---|---|---|---|---|---|
| `QualificationResult` | `learning_qualification` / L1 | `model.py` | Domain value / cross-module | Completed run / immutable / constructor only | Learning and L0; references `QualifiedCandidate` | Adds diagnostic winner subset | Python memory only; saved schema unchanged |
| `QualifiedCandidate` | `learning_qualification` / L1 | `model.py` | Domain value / cross-module | Completed run / immutable / constructor only | Learning and L0; references condition/model/config values | Adds all-supplied error and collision totals | Python memory only; qualified Profile schema unchanged |
| `ReplayEvidence` | `learning_qualification` / L1 | `model.py` | Domain value / cross-module | One selection / immutable / constructor only | Learning and L0; references recording/candidate/trace semantics | Full-resolution arrays and selected-event metadata | Python memory only; no ABI, wire, or storage effect |
| `StudioController` | `studio_application` / L0 | `controller.py` | Composition mapping / module-public | Application / owner-mutable / L0 only | QML and sibling mappings | Retains one recording selection and immutable artifact-export snapshots | Qt-facing only; saved project compatibility unchanged |

### State Object Ownership Matrix

| State | Type/definition | Owner | Lifetime | Mutability and authority | Linkage/public leakage/pointer escape |
|---|---|---|---|---|---|
| Completed retained candidates | Controller-private tuple/list copied from `QualificationResult` | `studio_application` | Until next run/project change | Owner-mutable replacement only | Instance-private; immutable candidate values cross L1/L0 |
| Replay recording selection | Controller-private primitive field | `studio_application` | Completed-result view | Owner-mutable through one QML slot | Instance-private; QML receives copied primitives/lists only |
| Replay analytical evidence | Immutable `ReplayEvidence` | `learning_qualification` value held by L0 | Current selection | Replaced atomically; no in-place mutation | No global linkage or pointer escape |

### Dependency, parent, and Flow review

- Actual and intended edges remain `studio_application -> learning_qualification`, `studio_application -> profile_export`, and QML -> `StudioController`.
- `learning_qualification` remains the L1 owner of deadline semantics, error counts, ranking, target arithmetic, and Replay evidence. `studio_application` remains the parent mapper; `desktop_adapter` renders only.
- As-is candidate A exposes only qualified `SemanticProfile` values and a placeholder waveform, so failed runs lose their best available evidence.
- Selected candidate B retains one typed diagnostic subset and recomputes one selected Replay on demand. It preserves module direction and storage compatibility with `O(R)` retained ranking plus one `O(N * L)` query.
- Rejected candidate C persists every replay array and all evaluated candidates; it enlarges storage, duplicates source data, and violates the selected retained-winner scope.
- The Flow remains best-effort on the existing Windows UI/analysis units. The 150 ms value is an offline event acceptance window, not a Task scheduling deadline; no real-time scheduling study is triggered.

## SPEC-0009 revision 31 amendment

The user confirmed 150 ms for C extraction and Qualification, fixed absolute time
with Ignore sample subtraction and no time compensation, then authorized execution
with `開始執行` in the current task on 2026-08-27. This amends the original SPEC-0004
20-ms timing approval only; diagnostic ranking and all other contracts remain.
The selected-event Replay latency excludes Ignore triggers while retaining the
complete continuous raw detector trace. Prior ADR statuses are unchanged.

## SPEC-0014 revision 3 amendment

The user confirmed that absent Normal, Pick, or Put activity is neutral, Collision
evidence remains mandatory, and every confirmed Collision must be detected no later
than 150 ms from its start, then authorized execution with `開始執行` on 2026-08-31.
The controller preserves PASS, FAIL, and COVERAGE_GAP meaning with an explicit
reason and presents active/excluded supplied speeds separately from ranges. No
domain type fields, project/Profile schema, detector arithmetic, or fallback rule changes.

## SPEC-0017 revision 2 amendment

The user confirmed that cancellation retains only candidates whose frozen model and
complete Qualification evidence committed before cancellation was observed. If at
least one such candidate is qualified, all completed qualified candidates remain
selectable in Candidate Dashboard and Analytical Replay. Otherwise, apply the
existing diagnostic formula in this record: minimize false triggers plus missed
collisions, then finite worst collision latency, and retain exact ties in stable
order. A cancellation before the first complete candidate retains no kernel.

The selected implementation commits each candidate to the Learning-owned immutable
`QualificationResult` immediately after complete Qualification, then publishes one
at-most-once cancellation result to the L0 parent. Periodically copying partial
results through progress was rejected because it duplicates analytical-result
authority in the controller and makes correctness depend on progress coalescing.
The run remains visibly `Cancelled`; incomplete candidates are discarded and
diagnostic-only results remain non-exportable. The cancellation observation points,
worker topology, target arithmetic, Qualification criteria, ranking formula,
project/Profile schemas, and Replay calculation remain unchanged.

- Approval: Hugo Peng, 2026-09-01, `SPEC-0017` revision 2 and explicit
  `開始執行` authorization in the current task.
- Validation: `tests/test_learning_run.py`,
  `tests/test_learning_worker_controller.py`, `tests/test_diagnostic_replay.py`,
  Replay/controller regressions, and architecture development gate.
