---
spec_version: 1
spec_id: SPEC-0025
revision: 16
status: implemented
change_set: small-mlp-no-psram
---

# Small MLP comparison for normal-motion Score spikes

## Problem

The user observes Score / Collision Ratio spikes during non-collision motion and requests adding a small MLP to the existing desktop application. Their deployment target is ESP32-S3 without external PSRAM. The current product implements FIR + Ridge. The older MLP/Extra Trees working bundle remains unfinished and contains lifecycle policies that differ from the current implemented FIR workflow.

## Solution

Add a bounded MLP regression family beside FIR, preserving the Internal IMU causal History to External IMU XYZ prediction and residual / Score / detector pipeline. Establish desktop comparison evidence before claiming improvement or ESP32-S3 runtime readiness. This working bundle narrows this request to MLP; it does not overwrite the independent Extra Trees draft or automatically adopt its conflicting lifecycle policies.

## User Stories

- As an analyst, I can compare a small nonlinear predictor with FIR on normal-motion spikes and collision detection.
- As an ESP32-S3 user without PSRAM, I need a bounded model whose deployment resource requirements are explicit.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Provide independently selectable FIR + Ridge and MLP model-family checkboxes. A run may select FIR alone, MLP alone or both. Each selected family uses its own captured model settings and trains independently; no ensemble is formed. Identify model family on comparative results. Preserve existing FIR settings and results. No Extra Trees or recurrent network is added by this request. |
| REQ-002 | MLP predicts current External XYZ from current and historical Internal XYZ only, then uses existing residual normalization, Score, Collision Ratio and confirmation/re-arm semantics. |
| REQ-003 | Evaluate normal false triggers, missed collisions, detection latency and normal-motion Score spikes; do not claim improvement from Training MSE alone. Compare on matching data and disclose data roles. |
| REQ-004 | Use the prior MLP design as inherited context: ReLU hidden structures with three linear outputs; a user-entered positive integer hidden-layer count defaulting to 2 (excluding input and the fixed three-output layer), with one independent width-checkbox group per active hidden layer using 4,8,16,32,64,128; candidates are the Cartesian product of the active layers selected widths, including equal and increasing widths, with no halving constraint; a run uses the entered depth rather than automatically mixing depths; invalid, zero, fractional or negative depth must not start training; user-selectable requested History checkboxes 4,8,16,32,64,128 ms with FIR and MLP selection sets independently editable and persisted, using the existing tap-count mapping and deduplication; independent user-selectable structure and L2 regularization checkboxes, with L2 values 0.0001,0.001,0.01; evaluate only the Cartesian product of selected Histories, structures and L2 strengths; NumPy-owned Adam training and fold-local preprocessing. Retain the prior detailed optimizer and checkpoint decisions unless an explicit conflict is reconciled. |
| REQ-005 | Treat ESP32-S3 without PSRAM as the intended deployment constraint. Report parameter bytes and working-buffer estimates separately; do not label desktop evidence as board timing, memory, quantization or hardware PASS. Actual tap count depends on sample rate. |
| REQ-006 | This phase delivers desktop model selection, training, Qualification, results, Replay CSV and project save/reopen with preserved frozen MLP identity and predictions. Defer standalone MLP deployment artifacts, C/C++ generation, ESP-DL quantization/export and user-facing model import. Preserve current FIR exports; when MLP is selected, unsupported model/profile export actions must clearly indicate unavailability rather than produce FIR artifacts. Internal project serialization is required and is distinct from future standalone parameter import. |
| REQ-007 | MLP shall reuse the current complete-Cycle N-fold allocation, condition-wise Training/Validation MSE aggregation, Loss-based parameter selection, Validation allowance, retained fold-kernel selection, Qualification/fallback, detector and Replay workflow. Use frozen retained fold models without an additional all-data final refit. Preserve FIR behavior. The prior MLP all-candidate/final-refit proposal does not apply to this change set. Model-specific optimizer and hyperparameter definitions remain distinct from FIR. Within one mixed comparison run, FIR and MLP independently sample their complete-Cycle N-fold allocations, even when the active data scope is identical. Preserve each family actual seed/allocation in provenance; independent sampling does not require artificially different memberships if allocations coincide by chance. Apply the existing Loss-based parameter and retained-fold selection independently within each family, rather than pooling families before selection. Keep current allowance/tolerance/tie handling; the phrase best Loss does not impose a new exactly-one-candidate rule. Retain independent weights, History selections and hyperparameters. Replay uses each retained frozen model and its own detector evidence; no paired-fold comparison claim is made. Different fallback data scopes must be identified explicitly. |

| REQ-008 | Initialize new MLP History/L2/layer-width sets empty with hidden depth 2. Preserve the current FIR-only default for old projects and initial model selection. With MLP selected, require a selected History, L2 and at least one width per active hidden layer; no selected model blocks Start. Switching model selection retains each family settings. Increasing depth adds empty layer groups; reducing depth removes inactive tail groups from the captured run. Compute candidate count without eagerly materializing the Cartesian product; never silently truncate the selected set. |
| REQ-009 | MLP uses the selected bounded grid only, without FIR coarse/fine or robust-refit search. Keep FIR fixed and optimized modes. Reuse the current raw Parameter Loss tolerance, condition coverage, Validation allowance and retained minimum fold Loss ties, separately per family. Preserve common 128-ms eligible evaluation targets, existing Cycle evidence and causal discontinuity/startup rules. |
| REQ-010 | Use a project-owned NumPy trainer: float64 fit statistics and optimization; training-only input mean/population scales and target means; degenerate features use scale 1 and zero restored input connections using the inherited 64*epsilon*max(1,max_abs) threshold. Use ReLU hidden activations and linear XYZ outputs. The inherited objective is mean over rows of summed XYZ squared error plus alpha times all weight squares, excluding biases. Report common selection MSE separately from the optimizer objective. |
| REQ-011 | Use Adam learning rate .001, beta1 .9, beta2 .999, epsilon 1e-8, batch min(200,N), complete final partial batch, fit-local seed 42 and aligned-example shuffling. Initialize every weight and bias with Glorot uniform bounds sqrt(6/(fan_in+fan_out)). Cap at 200 epochs, evaluate full training objective after each epoch, keep the strict best checkpoint, and stop after 20 epochs without cumulative .0001 relative improvement against the effective anchor. Exact zero stops immediately; cap reached is recorded without automatic retry. Preserve cancellation checks between bounded minibatches. |
| REQ-012 | Freeze the restored model to the selected float32 or float64 path and use it consistently for CV, Qualification and Replay. Preserve training-only residual center/scale estimation and existing invalid-scale handling. Explicit-preprocessing and folded input paths must be validated over every eligible validation example before accepting a folded representation; numerical calibration and error bounds must distinguish accumulation rounding from indexing/transform defects. Do not claim device or quantized parity. Unknown errors and memory exhaustion remain terminal; known numerical candidate failures are explicit exclusions. No automatic type promotion or refit. |
| REQ-013 | Reuse the existing bounded Windows worker execution and cancellation-result retention contracts, without multiplying worker limits by family, depth or candidate count. Run family learning independently with separate seeds, fallback state and provenance; use stable family-prefixed candidate identity and family-labeled progress. Preserve completed qualified candidates or current diagnostic-only selections from each family on cancellation. A family with no valid result must not erase another family completed result. Respect current terminal worker/data/memory failures. |
| REQ-014 | Persist model-family identity, hidden depth and ordered selected widths, frozen layer arrays, numeric type, preprocessing/residual/detector parameters, and each family run/fold/kernel evidence in project-owned versioned data. Preserve exact finite selected-type values on round-trip; use no executable object serialization. Strictly validate layer count, shapes, input dimension 3*taps, final output dimension 3, selected widths, finite values and provenance references before constructing models. Old FIR projects remain readable; unknown model/schema versions fail transactionally. Current-session diagnostic model inspection remains available; persist results according to current qualified-only contract. |
| REQ-015 | Display model family, selected hidden architecture, parameter count and parameter-byte estimates with model results; retain existing numerical scores, misjudgment counts and latency evidence without introducing a new ranking objective. Replay CSV computes through the selected frozen family model and retains the existing common column meanings. MLP standalone TXT/header/deployment export remains unavailable with a clear reason. Parameter bytes do not imply total RAM fit or device timing PASS. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | The requested issue is normal-motion Score / Collision Ratio spikes. | Explicit user clarification. |
| DEC-002 | The requested new family is small MLP, with intended ESP32-S3 deployment without PSRAM. | User supplied hardware constraint and explicitly asked to add small MLP first. |
| DEC-003 | Integrate MLP through the existing workflow, including Loss filtering and retained fold models, rather than introduce the older separate all-candidate/final-refit lifecycle. | The user challenged the separate flow: MLP cannot use the current workflow? The assistant clarified that it can; subsequent request is to continue this discussion. |
| DEC-004 | Deliver desktop comparison first; defer deployment export and standalone import. Future deployment should favor loading model parameters, with its format and loading target to be decided later. | Explicit user choice; do not infer a JSON, binary, ESP-DL or firmware-code format. |
| DEC-005 | MLP uses the same six History checkbox values as FIR: 4, 8, 16, 32, 64, 128 ms. | Explicit user selection; compare matching History values while preserving user control over workload. |
| DEC-006 | Provide independent checkboxes for MLP hidden structure and L2 strength; train only selected combinations. | User explicitly selected manual checkbox selection; the annotation separately questions the available hidden sizes. |
| DEC-007 | Single-layer widths are 4,8,16,32,64,128; each of the two hidden layers independently uses these same checkbox values, with all selected pairs evaluated. | User proposed the six widths and explicitly confirmed independent two-layer selection; halving is not required. |
| DEC-008 | FIR and MLP History selections are independent and saved separately in the project. Editing one never changes the other. | Explicit user selection; separate control of each model training workload. |
| DEC-009 | Model selection is multi-select: FIR alone, MLP alone, or both in one comparison run. | User explicitly approved this UI and run behavior after asking for clarification of the comparison scenario. This does not answer the separate fold-allocation question. |
| DEC-010 | Same-run FIR/MLP comparison on identical data scope shares the sampled Cycle N-fold allocation; models train independently. | User selected option 1, shared grouping, after the options were displayed as persistent plain text. |

| DEC-011 | Supersede DEC-010: FIR and MLP independently sample Cycle folds and record their own allocations. | The user explicitly changed shared grouping to independent sampling because the comparison is between each family best-Loss models. |
| DEC-012 | Apply existing Loss selection separately within each family before comparing retained candidates in Replay. | Derived from the user stated comparison of each model best Loss; preserves current filtering/ties and resolves OD-008 without pooling candidates across families. |

| DEC-013 | Replace the fixed single/two-layer structure selection from DEC-007 with a custom hidden-layer count, default 2. Preserve the six width options independently for every active layer. | Explicit user request: 提供自訂層數、預設2層. This is hidden depth, excluding input/output. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-004 | FIR-only, MLP-only and mixed selections dispatch exactly the selected independent families, retain their own captured settings and identify family on results; no ensemble is formed and FIR behavior is preserved. MLP exposes exactly 4,8,16,32,64,128-ms History checkboxes, evaluates only selected histories and deduplicates equal tap counts while retaining requested aliases. Independent structure/L2 checkboxes dispatch exactly the selected Cartesian product without automatic expansion. Depth defaults to 2 and dynamically determines the layer controls. For depth D and selected width counts k_i, structure count is the product of k_i; multiply by distinct selected Histories and L2 strengths for per-round parameter count. With default depth 2 and every width/History/L2 selected, there are 36 structures and 648 parameter combinations before N-fold multiplication. Verify depths 1,2,3 and invalid depth inputs; do not automatically include other depths. | Planner, trainer and UI integration tests. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |
| AC-002 | REQ-002, REQ-003 | Frozen MLP replay uses causal Internal-only inputs and common detector semantics, with explicit false/missed/latency evidence. | Controlled nonlinear normal-motion and injected-collision fixtures; user recording comparison when identified. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |
| AC-003 | REQ-005 | Parameter and buffer estimates are reproducible and separated from unmeasured deployment evidence. | Size calculations and documented device validation boundary. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |
| AC-004 | REQ-006 | Desktop save/reopen and Replay CSV preserve frozen MLP predictions and identity. Custom MLP depth and the ordered per-layer selections round-trip exactly. Distinct FIR/MLP History selections round-trip independently, including empty sets; editing either set does not mutate the other. FIR standalone exports still work; MLP standalone export is visibly unavailable and cannot emit a mislabeled FIR artifact. No new model-import or device runtime feature is exposed. | Project round-trip, replay parity and export-availability integration tests. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |
| AC-005 | REQ-007 | Controlled MLP candidates pass through the same Loss/allowance/fold selection functions and frozen-model Qualification lifecycle as FIR; no all-data final refit occurs. Mixed-family fits independently sample allocations and preserve training/validation isolation; deterministic tests verify independently addressed random streams and provenance, not an assertion that sampled memberships must differ. Loss selection runs separately per family, so another family lower Loss cannot remove its retained candidates. Replay remains tied to the selected frozen candidate with its own Score and detector evidence. FIR regression evidence remains unchanged. | Candidate-dispatch, fold-isolation, shared-selection and no-refit lifecycle integration tests. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |

| AC-006 | REQ-008 | Verify the complete REQ-008 contract through real production entry points and controlled failure cases. | UI readiness, dynamic-layer and selected-grid tests. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |
| AC-007 | REQ-009 | Verify the complete REQ-009 contract through real production entry points and controlled failure cases. | Cross-family fold and candidate filtering integration tests. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |
| AC-008 | REQ-010 | Verify the complete REQ-010 contract through real production entry points and controlled failure cases. | Finite-difference gradient, preprocessing isolation and nonlinear regression tests. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |
| AC-009 | REQ-011 | Verify the complete REQ-011 contract through real production entry points and controlled failure cases. | Deterministic Adam/checkpoint and cancellation tests. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |
| AC-010 | REQ-012 | Verify the complete REQ-012 contract through real production entry points and controlled failure cases. | Selected-type frozen prediction, replay parity and numeric failure tests. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |
| AC-011 | REQ-013 | Verify the complete REQ-013 contract through real production entry points and controlled failure cases. | Windows worker, mixed-family cancellation and failure integration tests. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |
| AC-012 | REQ-014 | Verify the complete REQ-014 contract through real production entry points and controlled failure cases. | Old-FIR and MLP/mixed project round-trip and malformed payload tests. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |
| AC-013 | REQ-015 | Verify the complete REQ-015 contract through real production entry points and controlled failure cases. | Result presentation, replay and export availability tests. | PASS: tests/test_mlp_learning.py and existing desktop/FIR regression; 453 regression tests plus 20 post-review focused tests. See docs/validation/SPEC-0025-desktop-mlp.md for per-contract evidence and real-recording/device limits. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| DEC-001 | refines | REQ-003 |
| DEC-002 | refines | REQ-001 |
| DEC-002 | refines | REQ-005 |
| AC-001 | depends_on | REQ-001 |
| AC-001 | depends_on | REQ-004 |
| AC-002 | depends_on | REQ-002 |
| AC-002 | depends_on | REQ-003 |
| AC-003 | depends_on | REQ-005 |
| AC-004 | depends_on | REQ-006 |
| AC-005 | depends_on | REQ-007 |
| DEC-003 | refines | REQ-007 |
| DEC-004 | refines | REQ-006 |
| DEC-005 | refines | REQ-004 |
| DEC-006 | refines | REQ-004 |
| DEC-007 | refines | REQ-004 |
| DEC-008 | refines | REQ-004 |
| DEC-008 | refines | REQ-006 |
| DEC-009 | refines | REQ-001 |
| DEC-010 | refines | REQ-007 |
| DEC-011 | supersedes | DEC-010 |
| DEC-011 | refines | REQ-007 |
| DEC-012 | refines | REQ-007 |
| DEC-013 | supersedes | DEC-007 |
| DEC-013 | refines | REQ-004 |

| AC-006 | depends_on | REQ-008 |
| AC-007 | depends_on | REQ-009 |
| AC-008 | depends_on | REQ-010 |
| AC-009 | depends_on | REQ-011 |
| AC-010 | depends_on | REQ-012 |
| AC-011 | depends_on | REQ-013 |
| AC-012 | depends_on | REQ-014 |
| AC-013 | depends_on | REQ-015 |

Inherited context: spec-governance/WORKING-SPEC-921afab2777b-mlp-extra-trees-learning-models.md. Current FIR behavior: SPEC-0011, SPEC-0013, SPEC-0017 and SPEC-0018. These remain independent sources; no implemented SPEC is reopened.

## Out of Scope

- Extra Trees, RNN, direct collision classification, and a claim that lower MSE proves lower false triggers.
- Board validation claims without hardware evidence.
- Standalone MLP parameter export/import, MLP C/C++ deployment artifacts, ESP-DL conversion and device firmware in this phase.

## Open Decisions

None.

## Routing/Gates

Spec review: PASS. Standards review: PASS. Independent post-fix review and validation evidence: `docs/validation/SPEC-0025-desktop-mlp.md`.

- Guided router PASS: grilling, immediate resume target spec-governance.
- Architecture: read manifest/adoption/generated overview/ADRs/baseline; planned ownership tables and manifest validation required before source edits.
- Required delivery: spec verification, formatter governance, meaningful trainer/replay/project tests, architecture CLI development/release gates and code review.
- User authorized execution of the current custom-depth design with exact 開始執行. Product source is still unchanged at specification materialization. Formatter and architecture authoring gates precede implementation.

## Discussion Context

### DISC-001: User request and hardware constraint

- **Situation:** Normal-motion Score / Collision Ratio spikes are the user's issue; ESP-DL was explained as a deployment library and MLP as a feed-forward model with a causal input window.
- **Question:** Which metric is high and which hardware is targeted?
- **Options and tradeoffs:** Metric clarification distinguished aggregate Training Loss from time-local detector scores. Hardware clarification established a no-PSRAM memory constraint; no design choice was inferred from the hardware name.
- **User answer:** Score / Collision Ratio spikes; ESP32-S3 without external memory; add small MLP first.
- **Explicit rationale:** Try a small MLP for the observed normal-motion issue.
- **Resulting impact:** DEC-001 and DEC-002 define REQ-001, REQ-003 and REQ-005. The prior desktop-only multi-family draft is context, not blanket approval for Extra Trees or changed FIR policies.

### DISC-002: Reuse the current workflow

- **Situation:** The assistant offered all-candidate Qualification versus current Loss filtering, but did not clearly explain that MLP can share the whole existing workflow.
- **Question:** Must MLP use a separate selection workflow?
- **Options and tradeoffs:** The prior all-candidate design increases Qualification work and differs from current frozen-fold selection. Reusing the current workflow preserves familiar filtering and downstream behavior, but retains the known limitation that Loss filtering can omit candidates with useful detection behavior.
- **User answer:** 沒有其他選項?MLP不能跟現在流程一樣? The user then requested: 討論不要停下來.
- **Explicit rationale:** Preference for the current workflow; no additional rationale stated.
- **Resulting impact:** DEC-003 defines REQ-007, AC-005 validates it, and OD-001 is closed. Earlier broad MLP draft remains unchanged; this change set explicitly uses the current retained-fold lifecycle.

### DISC-003: Desktop comparison before deployment

- **Situation:** Existing FIR can export C/C++ headers; small MLP could have a similar exporter or an ESP-DL pipeline, but neither is required to compare it on desktop.
- **Question:** Which export/deployment scope should this phase include?
- **Options and tradeoffs:** C/C++ generation provides firmware code but requires inference parity checks. ESP-DL adds quantization and deployment validation. Desktop-first provides comparative evidence sooner while deferring device-ready artifacts.
- **User answer:** 先完成桌面比較。匯出部分我比較傾向參數匯入的方式。
- **Explicit rationale:** No further rationale stated.
- **Resulting impact:** DEC-004 defines REQ-006 and AC-004 validates the desktop-only boundary. OD-002 export scope is resolved; future parameter loading is a recorded preference, not a selected format or an implementation requirement for this phase. OD-003 captures the remaining History UI integration question.

### DISC-004: MLP History checkboxes

- **Situation:** FIR already offers six selectable Histories; the older MLP proposal automatically used four.
- **Question:** Which History choices should MLP expose?
- **Options and tradeoffs:** Six checkboxes preserve same-window comparison and allow long histories at increased cost; four checkboxes restrict model size; the old automatic four-value grid reduces configuration but removes selection control.
- **User answer:** 建議沿用 FIR 的 **4、8、16、32、64、128 ms 勾選項目**
- **Explicit rationale:** No additional rationale stated.
- **Resulting impact:** DEC-005 refines REQ-004; AC-001 validates the six values, selection and tap deduplication. OD-003 is closed. OD-004 isolates selection controls for the already documented MLP-specific structures and regularization strengths.

### DISC-005: Manual MLP candidate selection and network-size question

- **Situation:** The previous question offered manual structure/L2 checkboxes versus automatically comparing the old nine combinations per History.
- **Question:** How should MLP candidate parameters be selected?
- **Options and tradeoffs:** Manual selection controls workload but requires choosing a subset; automatic selection covers every predefined combination with less UI work but cannot reduce training cost.
- **User answer:** 使用自行勾選。 Annotation on 單層 16、單層 32、雙層 32 → 16: 只16、32?
- **Explicit rationale:** No additional rationale stated.
- **Resulting impact:** DEC-006 refines REQ-004 and AC-001 validates selected Cartesian dispatch. OD-004 is closed. OD-005 records the user's challenge to the provisional structure range; it does not reopen checkbox selection or L2 values.

### DISC-006: Independent hidden-layer widths

- **Situation:** The earlier provisional grid used widths 16 and 32 and a halved second layer. These are candidate choices, not neural-network constraints.
- **Question:** Should both hidden layers independently select widths 4,8,16,32,64,128 and compare all selected pairs?
- **Options and tradeoffs:** Independent layer selections cover shrinking, equal and expanding structures but multiply the number of fits. Restricted pairs reduce workload but omit supported structures.
- **User answer:** 單層可以4、8、16、32、64、128?雙層中的第二層都是要第一層的一半? After the assistant proposed independent layer checkboxes and Cartesian comparison, the user answered: 對.
- **Explicit rationale:** No additional rationale stated.
- **Resulting impact:** DEC-007 refines REQ-004, AC-001 validates widths and candidate counts, and OD-005 is closed. OD-006 isolates cross-family History selection ownership; model-size choices are settled.

### DISC-007: Independent History persistence

- **Situation:** Both families expose the same six History values, but shared selection would couple their training workloads.
- **Question:** Should History selection be shared or stored separately for FIR and MLP?
- **Options and tradeoffs:** Independent sets allow different workloads and require matching values explicitly for same-History comparisons. A shared set simplifies matching but prevents different ranges.
- **User answer:** 各自保存（建議）：例如 FIR 勾到128 ms、MLP先測16／32 ms，可分別控制訓練量；做相同History比較時需自行選成一致。
- **Explicit rationale:** The selected option describes separate workload control; no additional rationale was stated.
- **Resulting impact:** DEC-008 refines REQ-004 and REQ-006, AC-004 verifies independent round-trip behavior, and OD-006 closes. OD-007 isolates cross-family fold allocation semantics for fair comparison.

### DISC-008: Explicit model-family multi-selection

- **Situation:** The shared-fold question assumed simultaneous FIR/MLP comparison, which the user asked to clarify before answering.
- **Question:** Should model selection allow FIR and MLP to be checked together, as well as each individually?
- **Options and tradeoffs:** Multi-selection enables independent same-run comparison and requires family-labeled results. Single-family selection would require separate runs. The clarified design does not combine models into an ensemble.
- **User answer:** 這個問題情境是指可以一起比較FIR跟MLP的意思?所以模型可以改成勾選多個模型? After the assistant explicitly asked to enable simultaneous FIR/MLP selection, the user answered: 可以。
- **Explicit rationale:** No additional rationale stated.
- **Resulting impact:** DEC-009 defines REQ-001 and AC-001 validates independent family dispatch and result identity. OD-007 remains open: approval of model multi-selection is not approval of shared fold allocation.

### DISC-009: Shared Cycle folds for model comparison

- **Situation:** FIR and MLP can be selected together. Independently sampled folds would confound model differences with grouping differences.
- **Question:** Should same-scope model comparisons share Cycle folds or sample each family independently?
- **Options and tradeoffs:** Shared folds support direct paired comparison while tying grouping; independent folds permit separate sampling but mix sampling variation into model comparison. Both keep weights and model-specific settings independent.
- **User answer:** 1
- **Explicit rationale:** No additional rationale stated. Option 1 was shared grouping. The user reported disappearing structured choices; future questions should be written directly in chat.
- **Resulting impact:** DEC-010 refines REQ-007, AC-005 validates shared memberships and independent fitting, and OD-007 closes. Technical reconciliation remains before materialization; the user's already settled decisions are not reopened.

### DISC-010: Independent folds and per-family best-Loss comparison

- **Situation:** The user previously selected shared folds. A subsequent question distinguished per-family Loss selection from pooled cross-family selection.
- **Question:** How should the changed sampling preference affect the comparison pipeline?
- **Options and tradeoffs:** Shared folds reduce sampling variation in paired comparisons. Independent folds preserve separate runs but allow sampling variation to contribute to observed differences. Per-family selection preserves each family retained candidates; pooled selection may eliminate an entire family.
- **User answer:** 改為各自抽樣就可以了，因為後面replay的時候，也是比較各模型最佳的loss
- **Explicit rationale:** Replay comparison is between each model best-Loss candidates.
- **Resulting impact:** DEC-011 supersedes DEC-010 and refines REQ-007; DEC-012 records the per-family selection implied by the rationale and resolves OD-008. AC-005 verifies independent sampling and separate selection. Existing Loss tolerances/ties are retained. Loss remains selection evidence; Replay shows frozen prediction, Score/Collision Ratio and detection behavior, and is not relabeled as a new Loss metric.

### DISC-011: Custom hidden depth

- **Situation:** Implementation preparation had started when the user pointed out that MLP depth should be configurable. Product source had not been modified; the specification was still a working bundle.
- **Question:** Offer a bounded depth menu or a custom layer count?
- **Options and tradeoffs:** Fixed 1/2 or 1/2/3 menus bound the candidate space; a custom count allows deeper models but makes dynamic controls, candidate-count calculation and resource preflight necessary.
- **User answer:** 提供自訂層數、預設2層
- **Explicit rationale:** No additional rationale stated.
- **Resulting impact:** DEC-013 supersedes DEC-007 only for the fixed-depth selection scheme, refines REQ-004, and updates AC-001/AC-004 for dynamic depth and persistence. Existing width options remain unchanged. The previous 42-structure/756-combination total is obsolete; default depth 2 permits 36 structures/648 combinations when all groups are selected. This is a specification change, not completed product implementation.

## Intended Implementation Boundaries

| Interaction | Producer | Consumer | Parent / mapping owner | Contracts / state | Allowed / forbidden edges |
|---|---|---|---|---|---|
| Capture model settings | desktop_adapter | learning_qualification | studio_application | UI selections to immutable LearningSettings | Parent maps; QML has no trainer state |
| Fit and replay | learning_qualification | history_worker_adapter | studio_application | FoldJob/RecordingJob and immutable results | Adapter implements Learning port; no domain-to-adapter import |
| Save and reopen | learning_qualification | project_session | studio_application | Frozen model to versioned project data | Parent maps sibling types; no direct sibling dependency |
| Profile presentation/export guard | learning_qualification | profile_export | studio_application | SemanticProfile and family identity | Parent maps; MLP cannot be rendered as FIR |

| Type / state | Owner | Lifetime / references | Storage / ABI impact |
|---|---|---|---|
| MLP settings, frozen model and parameter identity | learning_qualification | Immutable domain values; workers receive snapshots | Extend typed project model mapping; no device ABI |
| Adam weights/moments/checkpoint | learning_qualification | Fit-local mutable state, never shared between jobs | Not persisted as executable objects |
| Dynamic layer checkbox presentation | desktop_adapter | Bound to controller settings | Persist only mapped domain values |
| Family run evidence and active selections | studio_application | Session owner, maps Learning-owned snapshots | Independent family provenance in project data |
| Serialized layer arrays | project_session | Validated inert project payload | Versioned and shape/finite validated |

Existing L0 studio_application remains the parent of Learning, project_session and profile_export. Preserve the existing dependency graph; add private Learning algorithm implementation and declarations under its existing owner. No new production module, external trainer backend or device runtime is required. Proposed architecture manifest changes and tests must pass the architecture CLI design/development/release gates; no ADR is accepted by this specification.

## Revision History

| Revision | Date | Change |
|---|---|---|
| 1 | 2026-09-08 | Capture MLP-only request, confirmed Score metric and no-PSRAM target; identify candidate-admission integration decision. |
| 2 | 2026-09-08 | Reconcile current-workflow preference, close OD-001 and preserve no-final-refit fold lifecycle. |
| 3 | 2026-09-08 | Confirm desktop-first scope and future parameter-loading preference; defer standalone deployment and identify History UI integration. |
| 4 | 2026-09-08 | Confirm six MLP History checkbox values; close OD-003 and isolate MLP-specific candidate-selection controls. |
| 5 | 2026-09-08 | Confirm manual structure/L2 selection and open bounded network-size range in response to user annotation. |
| 6 | 2026-09-08 | Confirm six single-layer widths and independently selected two-layer width pairs; close OD-005. |
| 7 | 2026-09-08 | Confirm independent FIR/MLP History storage; close OD-006 and identify cross-family fold allocation semantics. |
| 8 | 2026-09-08 | Explicitly confirm FIR/MLP multi-selection; preserve the unanswered fold-allocation decision. |
| 9 | 2026-09-08 | Confirm shared Cycle folds for same-scope FIR/MLP comparison; close OD-007 and record plain-text question preference. |
| 10 | 2026-09-08 | Isolate cross-family Loss selection grouping before finalizing comparative candidate lifecycle. |
| 11 | 2026-09-08 | Supersede shared folds with independent family sampling; resolve per-family Loss selection from the user comparison rationale. |
| 12 | 2026-09-08 | Replace fixed depths with custom hidden-layer count defaulting to 2; update dynamic controls, counts and persistence acceptance. |
| 13 | 2026-09-08 | Complete technical delivery contracts and ownership plan after explicit execution authorization; no new user-facing design choice. |
| 16 | 2026-09-08 | Recorded implementation PASS evidence. |
