---
spec_version: 1
spec_id: SPEC-0027
revision: 3
status: implemented
change_set: mlp-memory-admission
---

# MLP training memory admission proposal

## Problem
The user reported Requested MLP layers exceed available training memory after approximately 18 hours and asks for a modification proposal. A controlled production-entry repro confirmed batch admission rejection with three folds: [REDACTED: personal data] estimated bytes per fold, [REDACTED: personal data] total, budget [REDACTED: personal data]. These are synthetic values, not measurements from the reported run.

## Solution
Use a 90% system-wide physical-memory pressure ceiling in the active SpawnLearningExecutor. For each psutil virtual_memory snapshot, define T=total and A=available; effective occupied memory is T-A. Admission additional budget is A-0.10*T. Runtime rejects when T-A > 0.90*T. Preserve concurrency, training math and terminal failures. This is sampled protection, not an OS-enforced allocation cap.

## User Stories
- As a user, I need a concrete proposal addressing late memory admission failure.

## Requirements
| ID | Requirement |
|---|---|
| REQ-001 | Produce an evidence-backed proposal for the reported MLP memory admission failure; execution was authorized by the user with exact 開始執行 on 2026-09-09. |

| REQ-002 | Set the active Learning executor default maximum_ram_fraction to 0.90 and interpret it as a fraction of total system physical RAM. Before MLP dispatch, compare the existing batch estimate E with A-(1-f)*T; reject when E exceeds that budget, without starting children. Equality is admitted. Validate finite sane memory readings and preserve existing environment-error handling. |
| REQ-003 | At existing runtime resource-check points, refresh T and A and stop the batch if T-A exceeds f*T. Do not compare aggregate process RSS against remaining RAM. Continue collecting process RSS for diagnostics. Preserve cancellation checks, cleanup and zero retries. The shared check applies to active FIR/MLP fold and Qualification execution. |
| REQ-004 | Preserve worker caps, job order, model parameters, result semantics, project schema and legacy History executor behavior. Distinguish admission rejection from runtime pressure in errors and include measured total, available, ceiling and estimated requirement where relevant. Do not alter the existing estimator in this change. |

## Decisions
| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Scope the first change to memory budget calculation; defer automatic concurrency reduction. | User explicitly prefers changing the limit first. |

| DEC-002 | Use a system-wide 90% RAM ceiling, accounting for other processes. | User explicitly selected this alternative. |

## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | The proposal defines admission behavior, scope, compatibility, costs and validation. | Review against confirmed decisions and source evidence. | PASS: confirmed decision review and docs/validation/SPEC-0027-memory-admission.md. |

| AC-002 | REQ-002 | With T=32 GiB and A=20 GiB, admit E up to 16.8 GiB and reject larger E before child startup. Cover below/at/above threshold and invalid readings. | Deterministic executor-entry tests with controlled memory snapshots and spawn interception. | PASS: 16 targeted memory tests, 48 focused tests and 469 full regression tests; docs/validation/SPEC-0027-memory-admission.md. |
| AC-003 | REQ-003 | Changing system availability across runtime checks triggers cleanup only above the configured occupied-memory ceiling; equality is allowed, existing parent RSS is not charged twice. | Controlled memory-sequence tests and bounded Windows spawn cleanup test. | PASS: 16 targeted memory tests, 48 focused tests and 469 full regression tests; docs/validation/SPEC-0027-memory-admission.md. |
| AC-004 | REQ-004 | Existing fold ordering, cancellation, terminal worker failure and MLP result contracts pass; error diagnostics expose the intended quantities. | Focused executor and existing MLP/History regressions; source review. | PASS: 16 targeted memory tests, 48 focused tests and 469 full regression tests; docs/validation/SPEC-0027-memory-admission.md. |

## Relationships
| Source | Relation | Target |
|---|---|---|
| AC-001 | depends_on | REQ-001 |
| DEC-001 | refines | REQ-001 |
| DEC-002 | refines | REQ-002 |
| AC-002 | depends_on | REQ-002 |
| AC-003 | depends_on | REQ-003 |
| AC-004 | depends_on | REQ-004 |

## Out of Scope
No product changes during proposal discovery. No change to learning mathematics or automatic parameter removal has been authorized.

## Open Decisions
None.

## Routing/Gates

Spec review: PASS. Standards review: PASS after correcting stale active memory descriptions. User execution authorization: exact 開始執行, 2026-09-09. Full regression: 469 passed. Development and release architecture gates: PASS, exit 0.

ask-matt -> grilling -> spec-governance -> clarify-improvement-proposals. Architecture and execution-flow governance required before final resource proposal. SPEC-0025 REQ-012/013 require terminal actual memory/worker failures; any change must be explicit. Product execution requires separate authorization.

## Revision History
| Revision | Date | Change |
|---|---|---|
| 1 | 2026-09-09 | Start proposal discovery with unresolved admission policy. |
| 3 | 2026-09-09 | Confirm system-wide 90 percent policy; implement after explicit authorization and record passing tests and gates. |

## Discussion Context

User confirmed the explained admission computation and requested a modification proposal. Admission policy was subsequently resolved by DISC-002.

### DISC-001: Limit calculation scope

- **Situation:** Current admission compares estimated jobs to 85% available RAM, while runtime compares total process-tree RSS to the same available-memory snapshot.
- **Question:** Should the proposal reduce concurrency or preserve concurrency and change the memory limit?
- **Options and tradeoffs:** Reducing concurrency may extend training; changing the budget preserves concurrency but requires a clear accounting basis.
- **User answer:** 我認為先修改上限好了，應該不能從剩餘的85%來計算。而是要全部的90%來計算。或是剩餘的95%之類的
- **Explicit rationale:** User considers the current remaining-memory 85% calculation unsuitable and wants the limit changed first.
- **Resulting impact:** DEC-001 resolves OD-001 by deferring concurrency changes. OD-002 remains open because the suggested alternatives have different admission and runtime semantics.

### DISC-002: System-wide ceiling confirmed

- **Situation:** Total-system 90%, remaining-memory 95%, and application-only 90% have distinct meanings.
- **Question:** Which accounting basis should govern admission and monitoring?
- **Options and tradeoffs:** System-wide 90% reserves 10% of total RAM; available-memory 95% leaves a smaller variable reserve; application-only 90% does not account for other applications.
- **User answer:** 採用整機總用量不超過 90%
- **Explicit rationale:** No additional rationale stated.
- **Resulting impact:** DEC-002 resolves OD-002. REQ-002 through REQ-004 and AC-002 through AC-004 define consistent admission and runtime accounting; no further product choice remains.

## Implementation and validation plan

1. Before source edits, read accepted ADRs and complete required architecture boundary/type/state/dependency inventory and planned-manifest validation. The existing history_worker_adapter remains the implementation owner of learning.execution; learning_qualification remains its demand owner. No new module, port, named type or dependency is proposed. Only adapter memory policy descriptions should change in the manifest and rendered views; use the single architecture CLI.
2. Add focused memory snapshot tests at the real executor entry point, including the reported rejection path and clean termination. Run with `.venv/Scripts/python.exe -m pytest tests/test_learning_memory.py -q` (planned test file).
3. Change the admission budget and runtime predicate together, retain RSS evidence and enhance rejection diagnostics. Run `.venv/Scripts/python.exe -m pytest tests/test_learning_memory.py tests/test_mlp_learning.py tests/test_history_execution.py -q`.
4. Exercise bounded real Windows spawn lifecycle under controlled measurements; do not intentionally exhaust host RAM. Assert results/cleanup and zero retries. No physical-device change or ESP32 performance claim is involved.
5. Render with `.venv/Scripts/python.exe tools/architecture/architecture_cli.py render`, then run development gate with manifest, adoption and baseline arguments. Run release gate and code review before delivery. Capture commands, exit codes and assertion output. Tests and architecture gates passed; see docs/validation/SPEC-0027-memory-admission.md. Runtime evidence is controlled Windows spawn lifecycle, not real RAM exhaustion or the original long workload.

## Impacts and limits

This is an admission/accounting policy change, not an MLP training algorithm change. No new user setting or project migration is required. Both active Learning families share runtime resource checks, so both use the chosen ceiling. Legacy History compatibility executor remains outside scope. OS metrics are sampled and allocations can grow between checks: 90% is a stop/admission threshold, not a guaranteed hard cap. Other applications can trigger the stop. Existing estimates remain conservative and uncalibrated; this change cannot guarantee completion of the reported 18-hour workload or remove all late failures. The selected policy is not always more permissive than 85% of available RAM. Automatic concurrency reduction, global-grid preflight, estimator redesign and retry/resume remain deferred.
