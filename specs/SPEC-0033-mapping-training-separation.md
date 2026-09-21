---
spec_version: 1
spec_id: SPEC-0033
revision: 20
status: implemented
change_set: mapping-training-separation
---
# Separate signal mapping from training algorithm selection

## Problem
Mapping currently binds sensor selection and preprocessing to the training algorithm. The user wants algorithm selection in Training instead.

## Solution
User-directed workflow: map acceleration signals and optionally enable filtering; select the algorithm in Training, validate data compatibility, and select the signal source for Single IMU. Formal names must describe the implemented methods.

## User Stories
- Map a recording once, then choose a compatible training method and signals.

## Requirements
| ID | Requirement |
|---|---|
| REQ-001 | Remove algorithm selection from Mapping Wizard; choose algorithms in Training. |
| REQ-002 | Provide an enable-filter checkbox during acceleration mapping. |
| REQ-003 | Validate selected data against the chosen training algorithm before execution. |
| REQ-004 | Single IMU training selects one physical IMU and its complete XYZ group; no individual-axis or cross-IMU combinations. |
| REQ-005 | Use the formal labels Dual IMU — MIMO FIR (Ridge), Dual IMU — MLP, and Single IMU — VAR (Ridge). Keep the selected physical sensor identity in the source field rather than defining separate algorithms. |

| REQ-006 | Provide a checkbox indicating existing filtered acceleration data; show corresponding filtered XYZ mapping fields only when checked. |

| REQ-007 | Internal and External IMUs each have independently selectable existing-filtered-data and enable-software-filtering checkboxes. |

| REQ-008 | For a given IMU, existing filtered data and software filtering are mutually exclusive; never activate both. Selecting neither is permitted and denotes raw XYZ; see REQ-009. |

| REQ-009 | Neither filtering option may be selected for an IMU, preserving raw XYZ. Training must make Single IMU — VAR (Ridge) unavailable for a raw selected source; eligible Single IMU sources must use imported filtered XYZ or software-filtered XYZ. |

| REQ-010 | Dual IMU FIR/MLP requires Internal and External to be both raw XYZ or both filtered XYZ. Mixed raw/filtered pairs are incompatible and must not start training. Mapping controls remain independently configurable per IMU. |

| REQ-011 | Training allows selecting multiple algorithms and executing them from one start action, producing distinguishable results. A batch may include Dual IMU FIR, Dual IMU MLP and Single IMU VAR together when each selected source passes admission. This does not require simultaneous execution or model fusion. |

| REQ-012 | Choose sources for all selected algorithms in Training. FIR and MLP use Internal XYZ as inputs and External XYZ as targets; VAR selects one physical IMU complete filtered XYZ group, using strictly past values to predict current values. Mapping defines columns and preprocessing, not algorithm choice. |

| REQ-013 | If any selected recording fails any selected algorithm admission requirement, block the entire requested training batch. Identify the recording, specific missing/incompatible data and affected algorithms. Require the user to adjust mappings, selected recordings or algorithms; never silently exclude recordings or run only a compatible subset. |
| REQ-014 | Preserve existing project/model identities, saved mappings, adopted filter coefficients, frozen models and results when reopening. Translate legacy workflow metadata as needed without retraining or redesigning filters; changing training configuration must not silently reinterpret saved results. Retain existing export support boundaries. |

| REQ-015 | Hovering each algorithm name/selection row in Training displays a tooltip explaining its full method name, prediction purpose, input/target signals, and raw/filtered eligibility. An unavailable algorithm retains readable explanation and its specific unavailability reason via the label or row hover target. |

## Decisions
| ID | Decision |
|---|---|
| DEC-001 | The user's requested separation is the direction; detailed behavior is not yet finalized. |

| DEC-002 | User confirmed one IMU complete XYZ as the Single IMU selection unit. |
| DEC-003 | Existing filtered-data presence is explicitly declared with a checkbox and conditional XYZ mapping. |

| DEC-004 | Per-IMU existing-filtered-data and software-filtering checkboxes are independent, as confirmed by the user. |

| DEC-005 | User rejected coexistence: choose only one of existing filtered data and software filtering per IMU. |

| DEC-006 | User permits raw bypass and explicitly excludes raw data from Single IMU — VAR (Ridge) training. |

| DEC-007 | User rejects mixed raw/filtered Dual IMU training; both physical sensors must share raw-versus-filtered category. |

| DEC-008 | User confirms multiple algorithms may run from one training action; do not impose a single-algorithm-only UI. |

| DEC-009 | User accepted a batch containing FIR, MLP and VAR, asked whether sources are selected in Training, and acknowledged the explanation that all three select sources there. |

| DEC-010 | User adopted the full-batch compatibility block and specifically highlighted the diagnostic showing file C missing External XYZ for FIR/MLP. |
| DEC-011 | Carry forward existing SPEC-0030 REQ-035/036 project compatibility and export boundaries; no new incompatible migration behavior was requested. |

| DEC-012 | User adopted all three formal algorithm labels and requested algorithm explanations on mouse hover. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | Mapping contains no algorithm selector and Training does. | UI behavior test for REQ-001. | PASS: AC-001 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-002 | REQ-002 | Mapping supports optional filtering. | Bypass/filter integration tests for REQ-002. | PASS: AC-002 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-003 | REQ-003 | Incompatible data is explained before training starts. | Admission tests for REQ-003. | PASS: AC-003 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-004 | REQ-004 | Single IMU uses exactly the selected physical sensor complete XYZ; individual-axis and cross-IMU selection are unavailable. | Signal-selection integration test for REQ-004. | PASS: AC-004 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-005 | REQ-005 | Algorithm labels identify the actual model method. | UI/model metadata consistency tests for REQ-005. | PASS: AC-005 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-006 | REQ-006 | Existing-filtered-data checkbox reveals/hides the corresponding XYZ mappings. | UI interaction and mapping persistence tests for REQ-006. | PASS: AC-006 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-007 | REQ-007 | Toggling either filtering checkbox for one IMU does not change the other IMU checkbox state or corresponding mapping visibility. | UI interaction tests for REQ-007. | PASS: AC-007 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-008 | REQ-008 | A given IMU cannot activate imported filtered data and software filtering simultaneously; the other IMU retains its independently chosen mode. | UI and domain validation tests for REQ-008. | PASS: AC-008 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-009 | REQ-009 | Raw mode maps successfully; VAR cannot be selected or started using a raw source. Either filtered source mode can satisfy the filtering prerequisite, subject to other data checks. | Mapping, training UI and backend admission tests for REQ-009. | PASS: AC-009 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-010 | REQ-010 | Dual IMU accepts raw/raw and filtered/filtered subject to other checks; rejects raw/filtered and filtered/raw with a specific explanation before execution. | Training UI and backend admission matrix tests for REQ-010. | PASS: AC-010 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-011 | REQ-011 | A valid multi-algorithm selection starts each selected algorithm and identifies its results separately. | Training orchestration and result identity tests for REQ-011, including FIR+MLP+VAR. | PASS: AC-011 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-012 | REQ-011, REQ-012 | In a valid batch, FIR/MLP use their Training-selected Internal-to-External sources and VAR uses its Training-selected single filtered sensor; each result preserves algorithm/source identity. | Multi-algorithm orchestration, result identity, and source-selection integration tests for REQ-011 and REQ-012. | PASS: AC-012 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-013 | REQ-013 | A batch with one incompatible recording starts no training job and lists recording, incompatibility and affected algorithms; after correction the valid requested batch can start. | UI and backend admission plus no-dispatch integration tests for REQ-013. | PASS: AC-013 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-014 | REQ-014 | Existing Dual/Single IMU project fixtures reopen with the same frozen predictions, filter coefficients and result identities, without training/filter-design calls; existing export support boundaries remain intact. | Legacy project round-trip and replay/export regression tests for REQ-014. | PASS: AC-014 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |
| AC-015 | REQ-015 | Hover each of the three algorithm rows and verify its method-specific tooltip, source direction and filtering constraints; an unavailable VAR row still explains its filtered-data requirement and current reason. | Runtime hover checks plus QML interaction tests for REQ-015. | PASS: AC-015 executed coverage in architecture/change-plans/SPEC-0033-verification.md; full suite 523 passed plus 2 native reruns passed; final feature suite 44 passed; Qt runtime PASS. |

## Relationships

| Source | Relation | Target | Rationale |
|---|---|---|---|
| REQ-001 | supersedes | SPEC-0030 | Replace mapping-time algorithm choice with Training selection. |
| REQ-014 | refines | SPEC-0030 | Retain legacy frozen results and export boundaries in the revised workflow. |
| REQ-015 | refines | REQ-005 | Explain the formal labels on hover. |

## Out of Scope
No new model family requested. No product implementation performed during initial clarification.

## Open Decisions
None

## Routing/Gates
Implementation authorized by the user's explicit start instruction. Architecture design, development and release gates PASS; formatter PASS; independent Standards review PASS. Spec review: PASS. Executed evidence, including resolved native-environment reruns, is recorded in [SPEC-0033 verification](../architecture/change-plans/SPEC-0033-verification.md). Initial discussion history below remains historical context.

## Revision History
- Revision 19: Adopt formal labels, add algorithm hover explanations, and normalize acceptance traceability for canonical materialization.
- Revision 17: Adopt full-batch admission diagnostics and retain established project compatibility requirements.
- Revision 15: Reconcile accepted FIR+MLP+VAR batches and acknowledged Training-stage source selection.
- Revision 13: Confirm multi-algorithm training; retain explicit uncertainty about combining VAR with Dual IMU algorithms.
- Revision 11: Require matching raw-versus-filtered categories for Dual IMU training.
- Revision 9: Allow raw XYZ bypass; forbid selecting or starting Single IMU VAR Ridge with raw source data.
- Revision 7: Record mutually exclusive filtering sources per IMU; clarify whether raw bypass remains permitted.
- Revision 5: Confirm independent per-IMU filtering checkboxes.
- Revision 3: Confirm complete XYZ selection and add existing-filtered-data checkbox with conditional mapping.
- Revision 1: Record the user's mapping/training separation request; identify open behavior decisions.
| 20 | 2026-09-12 | Recorded implementation PASS evidence. |

## Discussion Context
### DISC-001: Requested workflow separation
- **Situation:** Mapping Wizard currently exposes Dual IMU and sensor-specific Single IMU choices.
- **Question:** User initiated a change to where algorithms and signal sources are selected.
- **Options and tradeoffs:** Moving selection to Training permits reuse of mapping but requires explicit compatibility and source validation.
- **User answer:** Remove Algorithm from mapping; add optional filtering there; choose Algorithm and Single IMU signals in Training; use formal names.
- **Explicit rationale:** Algorithm selection belongs to Training.
- **Resulting impact:** REQ-001 REQ-002 REQ-003 REQ-004 REQ-005 DEC-001.

### DISC-002: Complete XYZ selection
- **Situation:** Clarify training source granularity.
- **Question:** 你說的「選擇要用哪些訊號」，希望能選到什麼粒度：是選一顆 IMU 的完整 XYZ，還是需要自由勾選個別軸或跨 IMU 的訊號？
- **Options and tradeoffs:** Complete XYZ retains the current vector model; arbitrary axes or cross-IMU signals would expand the model contract.
- **User answer:** 選一顆 IMU 的完整 XYZ
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** REQ-004 AC-004 DEC-002.

### DISC-003: Existing filtered acceleration mapping
- **Situation:** User annotated the optional filtering proposal.
- **Question:** How to represent source files that already contain filtered data.
- **Options and tradeoffs:** A separate presence checkbox exposes the corresponding mapping instead of requiring software filtering.
- **User answer:** Also allow checking whether filtered data exists; when present show the corresponding acceleration mapping.
- **Explicit rationale:** Display the corresponding mapping when existing filtered data is available.
- **Resulting impact:** REQ-006 AC-006 DEC-003.

### DISC-004: Independent per-IMU checkboxes
- **Situation:** Determine whether Internal and External filtering controls are coupled.
- **Question:** Internal 與 External IMU 的「已有濾波後資料」及「啟用軟體濾波」，是否要各自獨立設定？
- **Options and tradeoffs:** Independent controls support source files where only one sensor has filtered data.
- **User answer:** 獨立勾選
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** REQ-007 AC-007 DEC-004.

### DISC-005: Mutually exclusive filtering source
- **Situation:** Clarify whether imported filtered XYZ and software-filtered raw XYZ coexist for one IMU.
- **Question:** 同一顆 IMU 是否允許同時勾選「已有濾波後資料」與「啟用軟體濾波」，保留兩套結果，再於 Training 選擇使用哪一套？
- **Options and tradeoffs:** Coexistence would require Training to choose a result source; mutual exclusion keeps a single chosen preprocessing path per IMU.
- **User answer:** 只能二選一
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** REQ-008 AC-008 DEC-005.

### DISC-006: Raw bypass and VAR admission
- **Situation:** Clarify the neither-selected state and training availability.
- **Question:** 是否允許兩個選項都不勾選，直接使用原始 XYZ 資料？
- **Options and tradeoffs:** Raw bypass preserves unfiltered data; disallowing VAR on raw data retains its filtered-input requirement.
- **User answer:** 可以，但在Trining的時候就無法選擇Single IMU — VAR (Ridge)
- **Explicit rationale:** User explicitly requires Single IMU VAR Ridge to be unavailable when using raw data.
- **Resulting impact:** REQ-008 REQ-009 AC-009 DEC-006.

### DISC-007: Dual IMU source category matching
- **Situation:** Determine which raw/filtered combinations Dual IMU FIR and MLP accept.
- **Question:** Dual IMU 的 FIR／MLP 是否允許 Internal、External 各自使用原始或濾波後 XYZ，包括一顆使用原始資料、另一顆使用濾波資料？
- **Options and tradeoffs:** Independent categories would allow mixed pairs; matching categories limits training to raw/raw or filtered/filtered.
- **User answer:** Internal、External   只能都是原始資料或是都是濾波後的XYZ
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** REQ-010 AC-010 DEC-007.

### DISC-008: Multiple algorithms per training action
- **Situation:** User did not understand the initial mode question. A subsequent explanation contrasted running multiple algorithms with exactly one algorithm per start action, using FIR and MLP as the example and VAR as a separate-mode example.
- **Question:** Training 是否保留 Dual IMU 的 FIR 與 MLP 可同時勾選訓練，並讓 Single IMU — VAR (Ridge) 作為獨立模式？
- **Options and tradeoffs:** Multiple algorithms support one-action training of several methods; single selection restricts each action to one method. The answer does not explicitly settle cross-mode VAR inclusion.
- **User answer:** 可以跑多種
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** REQ-011 AC-011 DEC-008.

### DISC-009: Combined batch and source selection stage
- **Situation:** User requested clarification of the three-model example. The explanation showed Internal-to-External FIR and MLP plus Internal strict-past self-prediction VAR as three separate results from one start action.
- **Question:** 例如兩顆 IMU 都有濾波後 XYZ，是否也要支援一次勾選 FIR、MLP，以及使用 Internal XYZ 的 VAR，按一次開始就分別訓練並產生三種結果？
- **Options and tradeoffs:** Combining compatible algorithms avoids separate start actions while retaining separate models/results; it does not require concurrent execution.
- **User answer:** 可以，但是三種演算法是在training階段選擇來源?
- **Explicit rationale:** Acceptance was paired with a factual question about where algorithm sources are selected.
- **Resulting impact:** REQ-011 REQ-012 AC-011 AC-012 DEC-009.

### DISC-010: Acknowledged Training source selection
- **Situation:** The assistant clarified that all three algorithms select their sources in Training; Mapping only defines raw/filtered XYZ columns and filtering. FIR/MLP source direction and VAR filtered-only eligibility were explained.
- **Question:** Clarification of the user's question about source selection stage.
- **Options and tradeoffs:** Mapping reuse with algorithm-specific source selection and admission in Training.
- **User answer:** Understood; continue discussing.
- **Explicit rationale:** No further correction supplied.
- **Resulting impact:** REQ-001 REQ-012 DEC-009.

### DISC-011: Batch admission and actionable diagnostics
- **Situation:** Three files were selected for FIR, MLP and Internal VAR; file C had only filtered Internal XYZ, so it could not satisfy FIR/MLP External input requirements. The user highlighted the proposed missing-External diagnostic.
- **Question:** 只要所選資料有一筆不符合某個已勾選演算法的要求，是否就先阻擋整批訓練，列出檔名與原因，等你調整資料或演算法後再開始？
- **Options and tradeoffs:** Block the requested batch until the user corrects selection or mappings; avoid silently using different subsets or partially starting selected algorithms.
- **User answer:** 採用
- **Explicit rationale:** User highlighted the message identifying C, missing External XYZ and affected FIR/MLP algorithms.
- **Resulting impact:** REQ-013 AC-013 DEC-010.

### DISC-012: Existing compatibility contract retained
- **Situation:** Read implemented SPEC-0030 REQ-035/036 and AC-019. They require legacy-compatible reopen, preserved frozen coefficients/results and no implicit retraining or redesign.
- **Question:** Discoverable existing compatibility requirements.
- **Options and tradeoffs:** Preserve the existing contract; no new breaking migration policy was requested.
- **User answer:** No new answer required; retained existing implemented specification.
- **Explicit rationale:** Existing repository requirements and the user's requested workflow scope.
- **Resulting impact:** REQ-014 AC-014 DEC-011.

### DISC-013: Formal names and hover explanations
- **Situation:** Finalize the three proposed method-based labels.
- **Question:** 介面的正式名稱是否採用「Dual IMU — MIMO FIR (Ridge)」、「Dual IMU — MLP」與「Single IMU — VAR (Ridge)」？
- **Options and tradeoffs:** Formal method names describe the actual predictors; hover explanations keep the main selector concise while explaining sources and eligibility.
- **User answer:** 採用。滑鼠移到演算法時，可以顯示TIP說明演算法
- **Explicit rationale:** User requested explaining algorithms when hovering them.
- **Resulting impact:** REQ-005 REQ-015 AC-005 AC-015 DEC-012.

## Algorithm Tooltip Content
Tooltips follow the existing English UI language. Convey the following meanings without claiming superior detection performance:
- Dual IMU — MIMO FIR (Ridge): Multi-input multi-output finite impulse response model fitted with Ridge regression. Predicts External XYZ from current and historical Internal XYZ. Both sensors must use raw XYZ or both filtered XYZ.
- Dual IMU — MLP: Multilayer perceptron. Predicts External XYZ from current and historical Internal XYZ using a nonlinear model. Both sensors must use raw XYZ or both filtered XYZ.
- Single IMU — VAR (Ridge): Vector autoregressive model fitted with Ridge regression. Predicts the selected IMU current XYZ from its strictly earlier XYZ; uses measured-minus-predicted residuals for detection. Requires filtered XYZ and does not use current XYZ as an input.

## Verification Plan (original)
The following is the original plan. Executed PASS evidence is recorded in the Acceptance Criteria and linked verification report above.
- Validation enablement: use the existing Windows desktop validation profile and Python/QML test harness; inspect its capability before product edits. No hardware timing claim is introduced.
- Development: focused tests for all REQ/AC rows, especially per-IMU exclusive filtering state, source identity, multi-algorithm admission and zero dispatch on failed batch admission. Use the repository virtual-environment pytest runner.
- Runtime acceptance: run the real Mapping-to-Training flow for raw/raw Dual, filtered/filtered Dual, filtered VAR and a combined FIR/MLP/VAR batch; exercise each tooltip and invalid-source correction. Preserve observable screenshots/runtime evidence with scenario outcomes.
- Compatibility and release: reopen existing project fixtures without redesign/retraining; run the full relevant test suite, formatter check, and development/release architecture gates through tools/architecture/architecture_cli.py with the existing baseline. Record command, exit code and evidence.
- Before source edits, read complete architecture inputs and accepted ADRs, build boundary/type/state ownership tables and intended dependency/parent mappings, validate the planned manifest, then update source/tests/governance together and render generated views only through the architecture CLI. Existing numerical algorithms, optimization/scoring rules and export support limits are retained.
