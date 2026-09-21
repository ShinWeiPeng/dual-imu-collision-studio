---
spec_version: 1
spec_id: SPEC-0008
revision: 10
status: implemented
change_set: offset-speed-fallback-order
---

# Offset-by-Offset Speed Fallback Order

## Problem

The implemented pooled active-Offset fallback skips inner speed-suffix rounds when an Offset is undetectable at every supplied speed. The intended behavior completes the speed-suffix search for the current active-Offset set before advancing the outer Offset-exclusion round.

## Solution

Retain pooled Training across the current active Offset set. Within one outer round, begin with all supplied speeds and remove exactly the current lowest speed after a failed winner, refitting until one speed suffix passes every required judgment or no narrower suffix remains. Then advance to the next outer round regardless of success by excluding the smallest active Offset, restoring the full supplied speed set, and training on every remaining Offset. Only fully qualified kernels enter the candidate pool. Final ranking first maximizes the number of supplied speed strata in the qualified contiguous suffix, then maximizes active Offset coverage, and then applies the existing technical ordering.

For supplied Offsets 4/5/7/8 mm and speeds 500/1000 mm/s, a fully failing run executes:

| Round | Active Offsets (mm) | Training Speeds (mm/s) | Excluded Offset(s) | Excluded Speed(s) |
|---|---|---|---|---|
| 1.1 | 4, 5, 7, 8 | 500, 1000 | none | none |
| 1.2 | 4, 5, 7, 8 | 1000 | none | 500 |
| 2.1 | 5, 7, 8 | 500, 1000 | 4 | none |
| 2.2 | 5, 7, 8 | 1000 | 4 | 500 |
| 3.1 | 7, 8 | 500, 1000 | 4, 5 | none |
| 3.2 | 7, 8 | 1000 | 4, 5 | 500 |
| 4.1 | 8 | 500, 1000 | 4, 5, 7 | none |
| 4.2 | 8 | 1000 | 4, 5, 7 | 500 |

The Score threshold search shall use the inclusive fixed grid 5.0 through 20.0 at the existing 0.5 spacing (31 thresholds, 93 threshold/confirmation combinations per frozen model). Scores remain cached per frozen model; thresholds do not require independent FIR fits. This supersedes only the threshold endpoints in SPEC-0001 DEC-024 and SPEC-0003 DEC-004, retaining the latter's spacing and replay-cache contract. The partial implementation has updated the manifest and algorithm descriptions to the selected grid; the later-round insufficient-evidence policy below is now implemented and covered by regression tests.

Preserve incomplete-history exclusion: in the supplied replay CSV, sample indexes 0 through 3 are NaN/INVALID and do not trigger; the first finite Score at index 4 is approximately 0.1734 and does not trigger. These observations do not establish a warm-up false alarm or a universally sufficient threshold range. Warm-up length follows actual FIR tap support, not a universal four-row constant.

## User Stories

- As a user, I can see every required outer Offset-exclusion and inner speed-suffix round execute.
- As a user, I can compare qualified kernels by speed coverage first and Offset coverage second.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Outer Round 1 shall train from pooled eligible evidence across every supplied Collision Offset. Within each outer round, inner Round 1 shall use every supplied speed; after a failed winner, each next inner round shall remove exactly the current lowest speed and refit the same active Offset set until a winner passes every required judgment in the active speed suffix or no narrower suffix remains. |
| REQ-002 | After the inner speed search passes or exhausts, the next outer round shall execute regardless of success by excluding exactly the smallest active Collision Offset, retaining every larger Offset, restoring the complete supplied speed set, and restarting at inner Round 1. The search shall end after the final active Offset completes its inner search. |
| REQ-003 | A kernel shall enter the qualified candidate pool only when every required judgment across its complete active Offset set and active speed suffix passes. Failed round winners may remain diagnostic but shall not enter the qualified pool. |
| REQ-004 | Final qualified-kernel selection shall first maximize the number of supplied Robot Speed strata in the contiguous qualified suffix, then maximize the number of active Collision Offsets. Remaining ties shall prefer shorter FIR kernel depth/tap count, lower worst in-range collision latency, larger combined robustness margin, and stable declared parameter order, in that exact sequence. |
| REQ-005 | Qualification shall evaluate exactly the inclusive Score threshold grid 5.0 + 0.5*i for integer i from 0 through 30, for each existing Confirmation Mode. Preserve frozen-model Score caching and evaluate 93 threshold/confirmation combinations per fixed model. Planned candidate counts shall derive from the new 31-value grid; do not retrain FIR solely because threshold changes. |
| REQ-006 | Preserve exclusion of FIR rows without complete valid same-segment tap support: their derived values remain invalid and they shall not generate triggers or count as positive confirmation samples. Derive the excluded prefix from actual tap support; do not hard-code four rows or discard an additional fully supported row merely because it is the first valid output. |
| REQ-007 | When a round is proven to lack sufficient eligible Training evidence, record its round identity, active Offsets, Training speeds, and unavailable reason; skip that round without inventing a winner or discarding previously retained candidates, including qualified kernels. Continue the remaining inner suffixes and outer rounds under REQ-001/REQ-002, then rank qualified kernels normally. An empty qualified pool remains Failed. Numerical, resource, and unexpected failures remain terminal and shall not be silently treated as insufficient evidence. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Supersede early Offset exclusion with an exhaustive inner speed-suffix search for the current active Offset set before every outer transition. | The user confirmed that a failed full-speed round must reduce the lowest speed and refit instead of immediately excluding an Offset. |
| DEC-002 | Outer rounds use pooled active-Offset evidence: Round 1.x trains every supplied Offset; Round 2.x excludes the smallest Offset and trains every remaining Offset; later outer rounds continue smallest-first exclusion. | The user explicitly defined the outer-round Training scope. |
| DEC-003 | Advance to the next outer round after the current inner search either finds a fully qualified kernel or exhausts every valid speed suffix. | Every Offset-coverage envelope must be evaluated; success controls candidate admission, not whether the next outer round runs. |
| DEC-004 | Rank qualified kernels by widest supplied speed suffix first, then greatest active Offset coverage, followed by shorter kernel, lower worst latency, larger robustness margin, and stable order. | The user selected greater Offset coverage as the first tie-break after maximum speed coverage. |
| DEC-005 | Replace Score threshold endpoints 2.0/12.0 with 5.0/20.0, retaining the existing 0.5 increment and three confirmation modes. | The user explicitly requested 5-20 because the prior range is too small for the observed Scores. This is a selected search range, not evidence that every condition can qualify. |
| DEC-006 | Preserve existing FIR warm-up invalidity instead of deleting source rows or additionally suppressing the first fully supported output. | The user clarified that the unusable samples are indexes 0-3; the supplied replay already marks those rows NaN/INVALID with no triggers. |
| DEC-007 | Refine the fallback progression and retention contract to skip only proven insufficient-evidence rounds, preserve earlier retained results, and continue the search with explicit unavailable-round provenance. | The user confirmed retaining earlier successful results when a later round has no eligible Training data. No additional rationale was stated; genuine execution failures are outside this exception. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | With Offsets 4/5/7/8 and speeds 500/1000, failed full-speed winners produce 1.2, 2.2, 3.2, and 4.2 before each next outer transition; active Offset and Training speed values exactly match the Solution table, with every outer Round .1 restoring speeds 500/1000. | Domain state-machine test and controller progress test. | PASS: tests/test_speed_fallback.py plus test_all_failed_offset_speed_envelopes_reach_controller_in_exact_eight_round_order; exact eight rounds and scopes; full suite 219 passed. |
| AC-002 | REQ-003 | A passing inner-round winner enters the qualified candidate pool; failed winners remain diagnostic only, and outer progression occurs in either case. | Domain qualification and candidate-retention tests. | PASS: tests/test_learning_run.py and tests/test_controller_export.py; qualified-only admission, success/exhaustion progression, sparse earlier-winner retention; full suite 219 passed. |
| AC-003 | REQ-004 | Ranking first prefers more qualified supplied speed strata, then more active Offsets, then shorter taps, lower worst latency, larger robustness margin, and stable order; a fixture independently flips each criterion while holding all earlier criteria equal. | Ranking tests. | PASS: tests/test_speed_fallback.py independently covers all ranking priorities; controller best-kernel completion tests; full suite 219 passed. |
| AC-004 | REQ-005 | The exact grid contains 31 values including 5.0 and 20.0, excludes values outside that range, and produces 93 replay configurations per frozen model. A deterministic fixture requiring a threshold above 12 can qualify; a fixture failing every threshold remains failed. Candidate plan counts agree with the grid and cached/uncached replay agrees without threshold-driven refits. | Grid and plan tests, qualification fixtures, cache equivalence and fit-call spies. | PASS: tests/test_learning_plan.py, test_candidate_qualification.py, test_learning_run.py, test_history_execution.py and test_project_session.py; exact grid, above-12 qualification, cache/fit equivalence, counts and persistence compatibility; full suite 219 passed. |
| AC-005 | REQ-006 | At segment start or after a discontinuity, incomplete FIR windows produce no finite Score or trigger; the first complete valid window is evaluated normally. A 5-tap fixture excludes indexes 0-3, with index 4 first eligible, and other tap counts establish this is not a four-row constant. | FIR replay and detector regression tests, including invalid-prefix and discontinuity fixtures. Supplied CSV confirms indexes 0-3 INVALID/no trigger but is not full acceptance evidence. | PASS: tests/test_diagnostic_replay.py and detector regressions cover float32/float64, taps 1/3/5, all confirmation modes and discontinuities; full suite 219 passed. |
| AC-006 | REQ-007 | A sparse fixture with supplied tuples (Offset 4, speed 800) and (Offset 8, speed 500) retains its fully qualified Round 1.1 when Round 2.2 has no eligible evidence. The unavailable round is identifiable with scope and reason, produces no fabricated candidate, and does not stop remaining search. A run with no qualified kernel remains Failed; injected numerical, resource, and unexpected failures are not swallowed as missing evidence. | Regression tests through public Learning and controller/progress seams, including sparse evidence, continued progression, empty qualification, and genuine execution-error cases. | PASS: tests/test_learning_run.py, test_controller_export.py and test_history_execution.py cover sparse retained winner, scope/reason, continuation, all-unavailable Failed, real spawn, mixed/unclassified empty results and single/repeated solver/resource/unexpected failures; full suite 219 passed. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | depends_on | DEC-001 |
| REQ-002 | depends_on | DEC-002 |
| REQ-002 | depends_on | DEC-003 |
| REQ-003 | depends_on | DEC-003 |
| REQ-004 | depends_on | REQ-003 |
| REQ-004 | depends_on | DEC-004 |
| AC-001 | depends_on | REQ-001 |
| AC-001 | depends_on | REQ-002 |
| AC-002 | depends_on | REQ-003 |
| AC-003 | depends_on | REQ-004 |
| REQ-005 | depends_on | DEC-005 |
| REQ-006 | depends_on | DEC-006 |
| AC-004 | depends_on | REQ-005 |
| AC-005 | depends_on | REQ-006 |
| REQ-007 | refines | REQ-001 |
| REQ-007 | refines | REQ-002 |
| REQ-007 | refines | REQ-003 |
| REQ-007 | depends_on | DEC-007 |
| AC-006 | depends_on | REQ-007 |

Cross-spec supersedes relationships: DEC-005 supersedes only the threshold endpoint rule in SPEC-0001 DEC-024 and SPEC-0003 DEC-004. Other requirements in those specifications remain unchanged.

## Discussion Context

### DISC-001: Exhaustive inner speed progression
- **Situation:** The current implementation advances directly from X.1 to X+1.1 when an active Offset is undetectable at every speed.
- **Question:** Must the current active-Offset set complete its speed-suffix search before advancing?
- **Options and tradeoffs:** Completing the inner search costs more Training time but preserves every recoverable speed suffix; early Offset exclusion is faster but skips required suffix rounds.
- **User answer:** Run the speed fallback for the current Offset coverage; advance to the next outer round whether it passes or exhausts, and admit a kernel only when every required judgment passes.
- **Explicit rationale:** The final result must be able to find the kernel that passes the broadest speed interval.
- **Resulting impact:** DEC-001 and DEC-003 define REQ-001 through REQ-003 and supersede the current early Offset-exclusion transition.

### DISC-002: Pooled active-Offset Training scope
- **Situation:** Outer-round identity could mean one Offset, cumulative Offsets, or the remaining pooled Offset set.
- **Question:** Which Offset evidence shall each outer round use for Training?
- **Options and tradeoffs:** Current-Offset-only Training produces Offset-specific kernels; cumulative Training depends on ordering; remaining-set pooled Training produces one kernel for the exact declared active Offset coverage at each outer round.
- **User answer:** Round 1.x trains all Offsets; Round 2.x excludes the smallest Offset and trains all remaining Offsets; later rounds continue excluding the smallest Offset in order.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-002 closes OD-001 and defines the outer transition and Training scope in REQ-002.

### DISC-003: Cross-round qualified-kernel ranking
- **Situation:** Multiple outer rounds can produce qualified kernels with identical maximum supplied speed coverage but different active Offset coverage and technical characteristics.
- **Question:** What shall break a tie after maximum speed coverage?
- **Options and tradeoffs:** Preferring more active Offsets preserves broader collision-condition coverage; ignoring Offset count can select a technically smaller kernel with a narrower operating envelope; retaining all ties requires a later manual choice.
- **User answer:** Prefer the kernel covering more Offsets, then use the existing technical ranking.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-004 closes OD-002 and completes REQ-004 and AC-003.

### DISC-004: Score threshold range
- **Situation:** The current threshold grid is 2.0 through 12.0 in 0.5 increments. The user identified the displayed quantity as Score and reported Normal peaks around 15 and collision peaks around 20; the screenshot has no event labels proving those classes.
- **Question:** What threshold range should the search cover?
- **Options and tradeoffs:** Retaining 2-12 omits higher thresholds; selecting 5-20 permits higher thresholds while excluding values below 5 and increases grid cardinality from 21 to 31. Neither range guarantees qualified detection without replay of all annotated conditions.
- **User answer:** 太小了，應該要5-20。
- **Explicit rationale:** The prior range is too small relative to the observed Scores.
- **Resulting impact:** DEC-005 defines REQ-005 and AC-004; existing 0.5 spacing is unchanged, and only the prior endpoint rules are superseded.

### DISC-005: Identification of FIR warm-up rows
- **Situation:** The user said FIR startup data must not cause a false alarm. In the supplied CSV, indexes 0-3 have NaN scores, INVALID state, and trigger=false; index 4 has Score approximately 0.1734 and trigger=false.
- **Question:** Which samples does the user mean by the first unusable FIR data?
- **Options and tradeoffs:** Incomplete-history rows must remain invalid; excluding an additional complete-history row would change valid detection coverage and is not supported by this evidence.
- **User answer:** sample index 0~3。
- **Explicit rationale:** The user considers those initial FIR rows unusable and wants to avoid false judgments from them.
- **Resulting impact:** DEC-006, REQ-006, and AC-005 preserve and verify current warm-up exclusion. No root cause of a warm-up false trigger is claimed.

### DISC-006: Later non-trainable round after an earlier qualified winner
- **Situation:** Execution of the new exhaustive outer search with sparse supplied tuples (Offset 4 mm / speed 800 mm/s and Offset 8 mm / speed 500 mm/s) produced a fully passing Round 1.1. Round 2.1 failed its full speed range; Round 2.2 had no eligible training evidence at Offset 8 / speed 800 and raised "Round 2.2 produced no eligible frozen candidates", failing the whole run.
- **Question:** Should a non-trainable round be recorded as unavailable and skipped while preserving earlier winners, or should it terminate the run as it currently does?
- **Options and tradeoffs:** Skipping only a proven non-trainable round preserves qualified evidence and completes other envelopes but requires explicit unavailable-round provenance and must not swallow numerical, resource, or unexpected failures. Retaining terminal failure keeps the current no-eligible-model error policy but loses access to earlier qualified results through the failed-run path.
- **User answer:** 是要保留。The user also asked why a recording could be described as unavailable for Training.
- **Explicit rationale:** No additional rationale was stated. Existing source files are not lost: the round's simultaneous Offset and speed filters can exclude all available evidence. In the reproduced sparse fixture, (4,800) is excluded by Offset and (8,500) by speed for Round 2.2; this fixture is not a claim that the user's dataset has the same missing tuple.
- **Resulting impact:** DEC-007 and REQ-007 refine REQ-001/REQ-002/REQ-003; AC-006 adds acceptance evidence and closes OD-003. Preserve the existing partial implementation. The user subsequently supplied exact `開始執行`, authorizing this contract delta before product changes.

## Implementation evidence

- User execution authorization:[REDACTED: credential] `開始執行` after revision 8 confirmation.
- Implemented pooled Offset/speed suffix sequencing; qualified-only speed/Offset/technical ranking; threshold grid 5-20 by 0.5; compatible legacy/new threshold save/reopen; preserved FIR warm-up exclusion.
- Implemented typed insufficient-evidence classification, retained unavailable-round snapshots and visible controller summaries, preservation of earlier kernels, continuation after unavailable rounds, and Failed when no qualified kernel remains.
- Single or repeated numerical/resource/unexpected failures remain terminal; an unclassified empty History is terminal even when sibling Histories have candidates. No broad numerical exception swallowing remains in model-rule selection.
- Validation on 2026-08-27: `.venv/Scripts/python.exe -m pytest -q --basetemp .test_tmp/spec8-retention-full --tb=short`: **219 passed in 38.49 seconds**.
- Architecture CLI design, development and release gates: exit 0, PASS VERIFIED; existing QML symbol-analyzer SHOULD warning remains. Generated views were rendered from the manifest.
- Standards review: PASS (source-level). Spec review: PASS (source-level). Both discovered error-boundary findings were reproduced with failing tests, fixed and independently re-reviewed.
- No fixed-point Git diff review or commit is claimed: this workspace has no Git repository. No full user-dataset Training/performance rerun or guarantee of a qualified kernel is claimed.
- Earlier 203-test checkpoint preceded the new insufficient-evidence regression and is superseded by the 219-test run.

## Out of Scope

- Product implementation before exact execution authorization.
- Changing residual standardization, Score arithmetic, confirmation/rearm semantics, or collision latency requirements.
- Automatic threshold range expansion or a claim that 5-20 guarantees qualification.

## Open Decisions

None.

## Routing/Gates

- Earlier confirmed decisions remain settled; DISC-006 / OD-003 reopened the change set after an execution finding and is now resolved. The contract is decision-complete with no unresolved conflicts; the user's new exact `開始執行` authorized the completed implementation.
- Required delivery gates: TDD, algorithm/governance update, architecture CLI development gate, and code review.
- Exact post-confirmation execution authorization was received. Spec review: PASS; Standards review: PASS. No commit or tracker publication was requested.

## Revision History

| Revision | Date | Summary |
|---|---|---|
| 1 | 2026-08-27 | Started correction of Offset/speed fallback order. |
| 2 | 2026-08-27 | Defined pooled remaining-Offset Training and smallest-first outer progression after each inner search. |
| 3 | 2026-08-27 | Added the complete Offset/speed round table and finalized speed-first, Offset-second kernel ranking. |
| 4 | 2026-08-27 | Reopened in place; selected threshold grid 5-20 with unchanged 0.5 spacing and recorded preservation of FIR warm-up exclusion. |
| 5 | 2026-08-27 | Expressed endpoint-only cross-spec supersession separately from local-ID traceability and reconfirmed the selected range and warm-up preservation. |
| 6 | 2026-08-27 | Preserved partial implementation and 203 passing regressions; reopened non-trainable-round policy after sparse-data reproduction. |
| 7 | 2026-08-27 | Confirmed retention of earlier results and skipping proven insufficient-evidence rounds; closed OD-003 with explicit provenance and non-swallowing error boundaries. |
| 8 | 2026-08-27 | Normalized the empty Open Decisions section for strict contract validation; no behavior change. |
| 9 | 2026-08-27 | Recorded renewed execution authorization, 219 passing regressions, architecture gates and two-axis source review PASS; all acceptance criteria have evidence. |
| 10 | 2026-08-27 | Recorded implementation PASS evidence. |

