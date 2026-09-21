---
spec_version: 1
spec_id: SPEC-0029
revision: 2
status: implemented
change_set: extended-history-memory-validation
---

# Extended History memory estimation and diagnosis

## Problem
The user retained 32 ms History and pointed out that the UI supports up to 128 ms. SPEC-0028 validated only 8/16 ms. The new captured batch has 33 taps, hidden (8,8), L2 0.001, estimated additional 7099717006 bytes and budget 4829742285 bytes. The budget arithmetic is correct; this does not prove that the demand estimate is accurate. Original random fold membership is unavailable.

## Solution
Continue the user-selected estimator/diagnostic-only scope. Audit allocation lifetimes for all supported History choices, reproduce a deterministic representative 32 ms batch, and extend evidence to 64/128 ms where the unchanged system budget permits. Correct only source-supported accounting defects. Never reduce the estimate merely to admit a batch. Keep all History choices visible and selectable.

## User Stories
- As an analyst, I need supported History settings to receive accurate resource admission and actionable explanations without silently changing my training settings.

## Requirements
| ID | Requirement |
|---|---|
| REQ-001 | Preserve 4/8/16/32/64/128 ms choices, float64 semantics, matrix construction, training mathematics, fixed concurrency, terminal failures and system-wide 90% policy. |
| REQ-002 | Audit full dataset copies separately from selected fold workspace, temporary overlap, worker startup and parent serialization across every supported History. Only change components with allocation or native evidence. |
| REQ-003 | Validate 32 ms hidden (8,8), L2 0.001 with three complete real-data folds, fixed documented seed and fingerprint-verified sources. Preserve exact selected fold maps and do not claim reproduction of the unavailable original random allocation. |
| REQ-004 | Test count/component contracts for all History options. Attempt real 64/128 ms complete batches only when the unchanged budget admits them. Record refused/unmeasured cases as unvalidated, never PASS; fixture evidence is not full-scale runtime proof. |
| REQ-005 | Report History ms/taps, fold count, estimate, current additional budget, shortfall and dominant component in readable units; preserve detailed numeric diagnostics without source waveforms. Distinguish admission estimates from measured peaks. |
| REQ-006 | Require every completed native case's estimate to cover its measured additional conservative peak envelope. Underestimation fails; missing coverage blocks. Run applicable regression, architecture gates and independent review before delivery. |

## Decisions
| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Retain 32 ms and the existing range through 128 ms. | User explicitly requested retaining 32 ms and referenced the 128 ms option. |
| DEC-002 | Continue estimator/diagnostic-only scope and the existing 90% policy. | Existing user scope remains effective; no allocation rewrite or scheduling change has been requested. |

## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | Existing settings and training contracts remain unchanged. | Source review and regressions. | PASS: unchanged model/allocation/concurrency settings; 482 regression tests in build/spec29-tests.log. |
| AC-002 | REQ-002 | Every changed component has documented allocation/lifetime evidence. | Source inventory and focused accounting tests. | PASS: source inventory and independent allocation review found no justified formula reduction; docs/validation/SPEC-0029-extended-history.md. |
| AC-003 | REQ-003 | Representative complete 32 ms three-fold evidence has identities, counts and native peaks. | Native Windows runner under existing admission guard. | PASS: build/spec29-native2/history-32/result.json and build/spec29-bundles/history-32/result.json; three complete native folds. |
| AC-004 | REQ-004 | All History contracts tested; real 64/128 ms coverage or exact admission limitation is explicitly recorded. | Controlled tests and bounded native attempts. | PASS: positive-row tests for all six History choices and all three folds; 64/128 ms actual admission limitations recorded in build/spec29-native2/result.json, not claimed as runtime PASS. |
| AC-005 | REQ-005 | Refusal explains estimate versus budget and shortfall without implying measured demand. | Diagnostic contract tests. | PASS: readable-summary contract test plus actual native admission error captures. |
| AC-006 | REQ-006 | Completed native cases have no underestimation and all required checks pass. | Native peak evidence, regression, review and architecture CLI. | PASS: completed 32 ms native case has no underestimation; regressions, independent review and build/spec29-release-gate.log. |

## Relationships
| Source | Relation | Target |
|---|---|---|
| DEC-001 | refines | REQ-001 |
| DEC-002 | refines | REQ-001 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |
| AC-003 | depends_on | REQ-003 |
| AC-004 | depends_on | REQ-004 |
| AC-005 | depends_on | REQ-005 |
| AC-006 | depends_on | REQ-006 |

## Out of Scope
No RAM threshold increase, automatic concurrency reduction, retries, configuration removal, feature matrix rewrite or promise that every full dataset fits at 128 ms. No full parameter search. SPEC-0028 remains immutable. A proven legitimate memory shortage is not an estimator defect.

## Open Decisions
None.

## Routing/Gates
Spec review: PASS

Read-only discovery used ask-matt and clarify-improvement-proposals. Before source changes, refresh Learning/worker adapter boundary, type/state ownership and dependency tables against the manifest and validate the design. Existing module ownership and dependency edges are intended to remain unchanged; any new contract must be governed before editing. No new training algorithm or execution scheduling method is selected. Update only manifest descriptions and render generated views when affected. Use architecture_cli.py development/release gates and independent Spec/Standards review. Runtime scripts remain outside release sources. User authorized 開始執行. Implementation and pending native acceptance are recorded in docs/validation/SPEC-0029-extended-history.md; required 32 ms native acceptance is now PASS; 64/128 ms admission limits remain explicitly reported.

## Revision History
| Revision | Date | Change |
|---|---|---|
| 1 | 2026-09-09 | Extend the retained estimator/diagnostic scope to supported History settings and record honest runtime coverage boundaries. |
| 2 | 2026-09-09 | Recorded implementation PASS evidence. |
