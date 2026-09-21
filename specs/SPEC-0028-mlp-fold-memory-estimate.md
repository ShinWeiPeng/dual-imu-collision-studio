---
spec_version: 1
spec_id: SPEC-0028
revision: 4
status: implemented
change_set: mlp-fold-memory-estimate
---

# Fold-aware MLP memory estimate proposal

## Problem
The verified user dataset contains 805710 rows across 16 recordings. The failing round selects three recordings with 130462 raw rows. The existing estimator charges full-dataset history workspace to every fold. The production executor reproduced the captured 3.198 GB admission rejection. See build/spec27-memory-audit.md. The original random fold assignment is unavailable; final seed-42 representative peak evidence is recorded in docs/validation/SPEC-0028-memory-estimate.md.

## Solution
Define a fold-aware estimate separating resident dataset copies, selected evidence, matrix construction, fitting, evaluation and adapter/runtime overhead. Scope is estimate and diagnostics only. Acceptance uses two complete three-fold real-data cases in the screenshot parameter range; estimated additional memory must not be below the measured additional peak in either case. Preserve the confirmed SPEC-0027 system-wide 90 percent ceiling, fixed concurrency, terminal memory failures and no retries.

## User Stories
- As an analyst, I need memory admission to reflect the selected folds without underestimating worker memory or changing training results.

## Requirements
| ID | Requirement |
|---|---|
| REQ-001 | Produce a source-backed proposal correcting full-dataset matrix workspace accounting while retaining the established 90 percent system policy and training contracts. |

| REQ-002 | Count each FoldJob training and held-out evidence using the same Cycle selection, Normal/Pick/Put eligibility, Ignore/Collision exclusion, discontinuities, finite-value and causal History support rules as production. Count training matrices separately from condition-specific validation/evaluation matrices; do not build full feature matrices solely for estimation or train during admission. Preserve actual sample order and all training code behavior. |
| REQ-003 | Separate full dataset copies per worker from fold-specific evidence, feature/target/index arrays, Python list/scalar construction peaks, preprocessing, optimizer/checkpoint arrays, validation/prediction temporaries and execution/runtime overhead. Use overlapping lifetimes to derive each worker peak and a conservative simultaneous batch peak. Include added parent serialization/queue workspace without recharging pre-existing parent resident memory. Retain estimator constants only with documented source/allocation-size or calibration evidence, not a magic replacement of the previous total. |
| REQ-004 | Keep the SPEC-0027 admission budget available minus 10 percent of total physical RAM and sampled system-wide runtime stop above 90 percent. Keep worker caps, job/result ordering, cancellation cleanup, terminal memory/execution failures and zero retries. Keep float64 training, model settings, thresholds, model selection, matrix allocation and project schema unchanged. |
| REQ-005 | Add bounded diagnostics showing parameter identity, per-fold eligible feature counts, full dataset-copy cost, selected workspace components, estimated batch additional peak and current system budget. On refusal, include the dominant estimated component. Publish summary and bounded details through existing Learning progress/log and failure paths; do not store waveforms or introduce per-sample logs or new persistent UI settings. |
| REQ-006 | Validate against the supplied mlp.dicsproj and fingerprint-verified sources. Case 1 recreates speed 1000 mm/s, offsets 4/6/8 mm, History 16 ms, hidden (8,16), with a documented deterministic seed. Case 2 selects the largest estimated working set among valid fallback-round scopes and the screenshot range: History 8/16 ms, each hidden layer 8/16, three folds, float64 and the three existing L2 choices. L2 does not change allocation shapes; use the first selected L2 for both complete fits and record it. Select the case by count/estimate without running the full parameter grid. |
| REQ-007 | Run one complete three-fold batch for each selected case with original training semantics. For each, estimated additional memory must be greater than or equal to measured additional peak, including complete new worker resident costs and positive added parent working set, excluding pre-existing parent memory and unrelated applications. Capture native Windows process-memory evidence with batch identity, process lifetimes and monotonic correlation. A lower estimate fails acceptance; incomplete coverage or unavailable required measurement is BLOCKED. Calibrate then repeat acceptance if it underestimates; do not claim general safety from only these two cases. |

## Decisions
| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Only correct the memory estimator and diagnostics; preserve existing matrix construction and fitting implementation. | User explicitly selected 只修估算與診斷. |

| DEC-002 | Adopt two representative complete three-fold training cases with zero observed underestimation of additional peak before delivery. | User answered 採用 to the proposed acceptance method. |
| DEC-003 | Use option A: History 8/16 ms and each hidden width 8/16 for case selection, instead of including saved-file 32 ms/width 32. | User explicitly answered 採用A. |

## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | Define selected scope, accounting ownership, peak-lifetime model, calibration boundary, rejection semantics and regression validation. | Confirmed decision review, controlled executor-entry replay, representative Windows runtime memory evidence. | PASS: architecture/change-plans/SPEC-0028-memory-estimate.md; design/development/release gates and independent Spec review. |

| AC-002 | REQ-002 | Estimated row counts equal actual matrix feature counts for controlled gaps/exclusions and the representative data; no full feature matrix allocation occurs in admission. | Exact count-vs-production matrix tests and memory boundary checks. | PASS: tests/test_learning_memory_estimate.py; all six row_count_parity records in build/spec28-native2/result.json. |
| AC-003 | REQ-003 | Every estimate component has an allocation/lifetime source; raw copies remain counted even for excluded recordings, selected workspace only changes with selected evidence. The old 3.198 GB estimate remains reproducible as baseline. | Component accounting tests, lifetime review and captured regression fixture. | PASS: validation/SPEC-0028-method.md; exclusion/copy test and native peak calibration; baseline build/spec27-memory-audit.json. |
| AC-004 | REQ-004 | Preserved execution and model contracts pass all focused and full regressions; estimate affects admission only. | Existing Learning/MLP/History tests plus cancellation and failure tests. | PASS: 481 tests in build/spec28-final-tests.log; original training algorithms unchanged. |
| AC-005 | REQ-005 | Per-fold counts, component totals, budget and parameter identity appear in bounded diagnostic records and the refusal message without analytical payload or project-schema changes. | Capture existing log/failure paths; diagnostic-size and privacy assertions. | PASS: tests/test_learning_memory.py and native inputs/results; bounded numeric fold/component diagnostics reviewed. |
| AC-006 | REQ-006 | Record source fingerprints, screenshot overrides, seed, selected round scopes, parameters and fold memberships for both cases before training. | Reproducible validation manifest; no claim of original random membership replay. | PASS: build/spec28-native2/selection.json and both inputs.json files preserve source references, seed, parameters and fold maps. |
| AC-007 | REQ-007 | Both full three-fold batches complete with complete native-memory coverage and estimate minus measured added peak at least zero bytes. Calibration runs are separated from final acceptance, and any missing evidence blocks the claim. | Bounded Windows validation runner and machine-readable PASS/FAIL/BLOCKED report, using real adapter composition. | PASS: build/spec28-bundles/reported/result.json and build/spec28-bundles/largest/result.json; complete native coverage, margins 259938374 and 77926630 bytes. |

## Relationships
| Source | Relation | Target |
|---|---|---|
| AC-001 | depends_on | REQ-001 |
| DEC-001 | refines | REQ-001 |
| DEC-002 | refines | REQ-007 |
| DEC-003 | refines | REQ-006 |
| AC-002 | depends_on | REQ-002 |
| AC-003 | depends_on | REQ-003 |
| AC-004 | depends_on | REQ-004 |
| AC-005 | depends_on | REQ-005 |
| AC-006 | depends_on | REQ-006 |
| AC-007 | depends_on | REQ-007 |

## Out of Scope
Do not rewrite feature-matrix allocation or training mathematics. Do not change the RAM ceiling, auto-reduce workers, auto-retry, remove selected parameter combinations or silently change float64 training. Product changes were authorized by the subsequent exact 開始執行; only the confirmed estimator/diagnostic scope is implemented.

## Open Decisions
None.

## Routing/Gates
Spec review: PASS

ask-matt -> grilling -> spec-governance -> clarify-improvement-proposals. Architecture ownership, algorithm screening, resource model and validation enablement must precede implementation. Existing SPEC-0027 is implemented and is not reopened; the new spec will explicitly supersede its estimator-preservation clause only within this new scope.

## Revision History
| Revision | Date | Change |
|---|---|---|
| 1 | 2026-09-09 | Start new proposal from verified estimator audit. |
| 4 | 2026-09-09 | Recorded implementation PASS evidence. |

## Discussion Context

### DISC-001: Proposal requested after audit
- **Situation:** The production estimator reproduces the reported failure with full-dataset rows; selected fold matrices are much smaller.
- **Question:** What change should address the verified estimate mismatch?
- **Options and tradeoffs:** Estimate-only correction limits behavioral scope; matrix allocation changes could also reduce temporaries but require stronger FIR/MLP parity verification.
- **User answer:** 提出修改方案
- **Explicit rationale:** None additionally stated.
- **Resulting impact:** REQ-001 and AC-001 define proposal discovery only; OD-001 and OD-002 remain unresolved.

### DISC-002: Estimator-only scope confirmed

- **Situation:** The confirmed mismatch is full-dataset workspace accounting; matrix-building temporaries are another potential optimization but not required to fix the estimate.
- **Question:** Correct the estimator and diagnostics only, or also rewrite matrix allocation?
- **Options and tradeoffs:** Estimator-only limits behavioral scope and leaves actual memory usage unchanged; allocation changes could lower peaks but affect shared FIR/MLP code and require additional parity evidence.
- **User answer:** 只修估算與診斷
- **Explicit rationale:** No additional rationale stated.
- **Resulting impact:** DEC-001 refines REQ-001 and resolves OD-001. AC-001 retains runtime acceptance as pending OD-002. No product mutation is authorized by this scope selection.

### DISC-003: Complete representative-batch acceptance

- **Situation:** Formula correction alone does not establish that temporary/runtime memory is covered.
- **Question:** Adopt two complete three-fold cases and require estimated additional memory not below measured additional peak?
- **Options and tradeoffs:** Real-data complete fitting costs validation time and exercises allocation lifetimes; formula-only validation is cheaper but cannot verify the rejected batch peak and is not the selected acceptance.
- **User answer:** 採用。現在都沒有其他選項的說明了
- **Explicit rationale:** User also requested alternatives and tradeoffs remain visible in future decision questions.
- **Resulting impact:** DEC-002 refines REQ-007 and AC-007, resolving the acceptance portion of OD-002. Continue without changing conversation mode.

### DISC-004: Screenshot validation range

- **Situation:** The saved project includes 32 ms and width 32, while the screenshot selects only 8/16.
- **Question:** Use A screenshot range or B broader saved-file range to choose the larger case?
- **Options and tradeoffs:** A matches the reported settings and limits validation cost; B includes larger shapes and can increase time and RAM.
- **User answer:** 採用A
- **Explicit rationale:** No additional rationale stated.
- **Resulting impact:** DEC-003 refines REQ-006 and AC-006. OD-002 is closed; no product execution authority is granted by selecting A.

## Architecture and implementation plan

Learning-owned counting and allocation-size semantics stay in learning_qualification, with a small private estimator source and immutable summary contract if needed. history_worker_adapter owns Windows memory readings, process/runtime overhead and the admission decision; it consumes the Learning estimate through the existing Learning-owned execution contract. studio_application maps bounded diagnostics to its existing log. No new dependency from Learning to psutil or the adapter is allowed. Job input/summary additions, if needed, must be declared with single ownership and mapped at the existing boundary. No global mutable cache or duplicate training state.

Before source changes: complete boundary/type/state ownership tables and actual/intended dependency graph against the manifest; validate the planned manifest through architecture_cli.py design gate. Inventory estimator lifetimes and counters before choosing constants. Keep the counted evidence predicate aligned with production through contract tests; do not refactor matrix construction as part of this scope. Any new algorithm record remains proposed pending explicit human approval. Update only the manifest as the description source and regenerate applicable Learning, application, System and execution views; no manual generated-page edits or schema migration. No hardware/RTOS or real-time scheduling change.

The flow remains Learning -> bounded execution adapter -> Windows workers -> ordered results. Added work is count/estimate before spawn plus bounded diagnostics. Extra work depends on source row count but must not allocate feature-sized arrays for counting. Memory model assurance is estimated until calibration and final acceptance; actual speed, estimator overprediction ratio and untested workloads are not guaranteed. The 10 percent system reserve is the existing user-selected budget, not an estimator error allowance. Additional recording scenarios affect raw-copy accounting; additional interval types require count-contract tests; another OS requires equivalent adapter memory evidence. Existing parent/module relationships remain unchanged.

## Validation and delivery plan

1. Enablement before product changes: confirm Windows native memory capture capability for all new worker lifetimes and parent baseline; document tracked validation profile/local bindings. Use OS-native evidence (ETW/WPR where required by the governing validation skill) and a unique run ID with monotonic correlation. Verify parser fixtures distinguish PASS, FAIL and missing/incomplete evidence BLOCKED. Determine the bounded run deadline from a probe and the existing finite epoch cap; do not invent an unmeasured universal timeout. Do not deliberately exhaust system RAM or bypass the 90 percent stop.
2. Development: red-capable old-estimate fixture, exact evidence-count parity tests and component-lifetime tests at the Learning/adapter boundary. Planned command: `.venv/Scripts/python.exe -m pytest tests/test_learning_memory_estimate.py tests/test_learning_memory.py -q`. The new test file is created during authorized implementation.
3. Final runtime: use a tracked runner under tools/validation for the two cases and store configuration, seed/fold maps, estimate breakdown, native memory evidence and zero-underestimation verdict. Snapshot pre-existing parent usage, count each child from spawn through exit, and distinguish simultaneous observed RSS from conservative per-process high-water envelopes. Retain complete capture coverage and state exactly which native metric is used. No change to model math is permitted to make acceptance pass.
4. Regression: `.venv/Scripts/python.exe -m pytest -q`; targeted formatter check; `architecture_cli.py render`, followed by development and release gates with manifest/adoption/baseline. Generated-view comparison is performed by the gates. Run independent Standards and Spec review and record actual commands, exit codes and artifact hashes.

## Alternatives and tradeoffs

Selected estimator-only correction addresses the verified full-dataset workspace mismatch and preserves trained-result semantics. It adds count/accounting code and bounded diagnostics, so peak-lifetime logic must remain coupled to allocation behavior through tests. Rewriting matrix allocation might reduce actual usage but is deferred by DEC-001. Raising RAM limits and adaptive parallelism are outside the confirmed scope. Actual RAM usage is not reduced by a more accurate estimate, and other processes may still cause a terminal stop. Two accepted cases validate only the chosen data/settings range; they do not prove every possible width, History, depth or dataset safe. No claim is made that the current 524 MB arithmetic is a correct replacement.

## Execution authorization

Spec review: PASS

Independent Spec and Standards findings were corrected; final native acceptance and six row-count checks passed. Review evidence is recorded in docs/validation/SPEC-0028-memory-estimate.md.

The user subsequently supplied exact 開始執行 for this change set. Product edits, tests and representative native validation were executed within the confirmed scope. Final evidence: docs/validation/SPEC-0028-memory-estimate.md; no new ADR was accepted.
