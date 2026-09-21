---
spec_version: 1
spec_id: SPEC-0006
revision: 11
status: confirmed
change_set: replay-csv-export
---

# Replay CSV Export

## Problem

Opening or inspecting analytical replay data in the application is too slow for the user's workflow. The application already computes full-resolution Internal IMU, FIR-predicted External IMU, and detector score arrays, but does not provide the requested CSV workflow.

## Solution

Replace the Replay waveform charts with deterministic recording-level CSV export while retaining `.dicsproj` project persistence and only the recording selector needed for Analytical Replay. Export the selected model parameters as a separate TXT artifact so FAMOS can independently reconstruct the Replay arithmetic.

## User Stories

- As an analyst, I can inspect Internal IMU, FIR-processed data, and score values efficiently in an external CSV tool.
- As an analyst, I can reconstruct the selected FIR model in FAMOS from the exported training parameters and compare its result with the Replay evidence.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | The application shall export time-aligned Internal IMU X/Y/Z, Actual External IMU X/Y/Z, FIR-predicted External IMU X/Y/Z, Residual X/Y/Z, Normalized Residual X/Y/Z, detector score, detector threshold, collision ratio, detector state, and trigger evidence from existing full-resolution Replay evidence to CSV. |
| REQ-002 | CSV numeric values shall preserve the Replay evidence values and sample alignment without silently substituting display-only zeroes for non-finite warm-up samples. |
| REQ-003 | The export shall report failure without leaving a partially replaced destination file. |
| REQ-004 | The Replay workflow shall stop rendering waveform charts and shall provide CSV export instead, without changing the `.dicsproj` project format. |
| REQ-005 | Each export shall produce one CSV for the currently inspected retained kernel and selected recording and shall include every sample in that recording without requiring or depending on a Cycle or Event selection. |
| REQ-006 | The CSV header order shall be `sample_index,time_s,internal_imu_x,internal_imu_y,internal_imu_z,actual_external_imu_x,actual_external_imu_y,actual_external_imu_z,fir_predicted_external_imu_x,fir_predicted_external_imu_y,fir_predicted_external_imu_z,residual_x,residual_y,residual_z,normalized_residual_x,normalized_residual_y,normalized_residual_z,score,threshold,collision_ratio,detector_state,trigger`. The `trigger` column shall be boolean evidence derived from membership in Replay trigger indices. |
| REQ-007 | A separate Export Model TXT action shall propose `<kernel_id>_model.txt` and export a UTF-8, LF-delimited, named-section text document for the currently inspected trained model. Its scalar header shall identify schema version, kernel ID, sample rate, numeric type, tap count, score mode, confirmation mode, threshold, release ratio, and release quiet time. Its `[fir_weights]` table shall use the header `output_axis,input_axis,lag,value` and contain every weight exactly once in `[output_axis][input_axis][lag]` order, followed by named `[bias]`, `[residual_center]`, and `[residual_scale]` sections with explicit X/Y/Z labels. Numeric values shall preserve the frozen model values. The Replay sample CSV shall remain a pure sample table. |
| REQ-008 | Analytical Replay shall expose only the recording selector; the Cycle and Pick/Put/Fork Collision Event selectors and their controller-facing selection APIs shall be removed from this workflow. |
| REQ-009 | Opening Export Replay CSV shall propose the collision-safe filename `<source_stem>_replay.csv` derived from the selected recording's imported source filename rather than the internal `recording-N` identity. For XLSX input, the sanitized worksheet name shall be inserted before `_replay` so worksheets from one workbook remain distinct. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Replace Replay waveform charts with CSV export while retaining `.dicsproj` project persistence. | The user clarified that Replay no longer needs to display charts; removing chart rendering directly addresses the slow in-application inspection path. |
| DEC-002 | Export one complete recording for the currently selected kernel and recording. | The user selected option 1, yielding one bounded artifact without duplicate batch output or Cycle/Event truncation. |
| DEC-003 | Use the compact requested column set plus sample alignment columns and threshold. | The user requested threshold in addition to Internal IMU, FIR-predicted data, and score; sample index and time make those values unambiguously aligned. |
| DEC-004 | Export the complete diagnostic column set in addition to sample index and time, superseding DEC-003. | The user revised the prior compact choice by selecting option 2, including Actual External IMU, residuals, threshold, collision ratio, detector state, and trigger evidence. |
| DEC-005 | Add the trained model parameters before the sample table rather than adding per-sample arithmetic expansion rows. | The user selected the model-parameter option so FAMOS can independently reconstruct and compare the FIR result. |
| DEC-006 | Export the trained model parameters as a separate TXT artifact and keep Replay CSV as a pure sample table. | The user selected the separate-model-file option and explicitly requested Export Model TXT. |
| DEC-007 | Analytical Replay selection is recording-only; remove Cycle and Event selectors. | Those selectors only select event-latency context, while the requested exported prediction and detector arrays already cover the complete recording. |
| DEC-008 | Derive the proposed Replay CSV filename from the imported recording filename. | The user wants exported artifacts to retain recognizable recording identity instead of an internal generated ID. |
| DEC-009 | Append `_replay` to the imported source stem and include an XLSX worksheet identity when present. | This preserves recognizable recording identity without proposing the same path as a source CSV or colliding across worksheets. |
| DEC-010 | Use a named, sectioned Model TXT format with explicit FIR output axis, input axis, lag, and value fields. | The user selected the self-describing format so FAMOS reconstruction does not depend on undocumented positional interpretation. |
| DEC-011 | Propose `<kernel_id>_model.txt` for Export Model TXT. | The model belongs to the inspected kernel and does not vary by selected recording, so a kernel-derived name avoids duplicate recording-specific identities for identical content. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002, REQ-006 | A representative Replay export has one aligned row per exported sample and contains exactly the specified ordered complete diagnostic columns, with numeric, state, and trigger values matching Replay evidence. | Automated CSV artifact test against Replay evidence arrays. | Pending |
| AC-002 | REQ-003 | A failed write preserves any prior destination artifact and reports a user-visible error. | Atomic-write fault-injection test. | Pending |
| AC-003 | REQ-004 | Replay no longer instantiates waveform chart panels, exposes CSV export, and retains existing project Open/Save behavior. | Controller and QML regression tests. | Pending |
| AC-004 | REQ-005 | Changing the inspected kernel or selected recording changes the exported evidence source; one export contains exactly the selected recording's complete sample count without Cycle/Event input. | Controller and CSV artifact tests. | Pending |
| AC-005 | REQ-007 | A representative Model TXT parser validates the exact named sections and scalar metadata, finds every selected-model FIR weight exactly once in governed axis/lag order plus matching bias and residual center/scale, and reconstructs predictions matching existing Replay evidence; Replay CSV begins directly with its sample header. | Automated TXT parse, FIR reconstruction, and CSV artifact test. | Pending |
| AC-006 | REQ-008, REQ-009 | Runtime Analytical Replay exposes one recording selector plus Export Replay CSV and Export Model TXT actions, exposes no Cycle/Event selectors, and proposes a collision-safe recording-derived CSV filename. | Controller and QML runtime regression tests. | Pending |

## Relationships

| Source | Relation | Target |
|---|---|---|
| AC-001 | depends_on | REQ-001 |
| AC-001 | depends_on | REQ-002 |
| AC-002 | depends_on | REQ-003 |
| REQ-004 | depends_on | DEC-001 |
| AC-003 | depends_on | REQ-004 |
| REQ-005 | depends_on | DEC-002 |
| AC-004 | depends_on | REQ-005 |
| DEC-004 | supersedes | DEC-003 |
| REQ-006 | depends_on | DEC-004 |
| AC-001 | depends_on | REQ-006 |
| REQ-007 | depends_on | DEC-005 |
| AC-005 | depends_on | REQ-007 |
| DEC-006 | supersedes | DEC-005 |
| REQ-007 | depends_on | DEC-006 |
| REQ-008 | depends_on | DEC-007 |
| REQ-009 | depends_on | DEC-008 |
| AC-006 | depends_on | REQ-008 |
| AC-006 | depends_on | REQ-009 |
| REQ-009 | depends_on | DEC-009 |
| REQ-007 | depends_on | DEC-010 |
| REQ-007 | depends_on | DEC-011 |

## Discussion Context

### DISC-001: CSV workflow scope
- **Situation:** Replay already exposes full-resolution evidence as in-application charts, while `.dicsproj` preserves mappings, annotations, and completed results. Replacing either workflow would remove existing capabilities.
- **Question:** Shall CSV export supplement Replay, replace Replay charts, or replace project persistence?
- **Options and tradeoffs:** Supplementing Replay preserves charts and project compatibility with the smallest behavioral change; replacing charts may reduce rendering work but removes visual inspection; replacing `.dicsproj` loses structured project restoration that a flat CSV cannot represent safely.
- **User answer:** Option 1: add Replay CSV export and retain the existing charts and `.dicsproj` behavior.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-001 and REQ-004 require additive CSV export with regression coverage for existing workflows.

### DISC-002: Replay chart retention correction
- **Situation:** The first answer selected additive export, but retaining Replay waveform charts would preserve the rendering path that the CSV workflow is intended to avoid.
- **Question:** Should Replay continue to display waveform charts after CSV export is available?
- **Options and tradeoffs:** Retaining charts preserves visual inspection but keeps rendering work; removing charts reduces Replay UI work and makes CSV the evidence-inspection path while losing in-app waveform visualization.
- **User answer:** Replay does not need to display charts.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-001, REQ-004, and AC-003 now require replacing Replay waveform charts with CSV export while retaining `.dicsproj` behavior.

### DISC-003: Export evidence scope
- **Situation:** Replay selection identifies a retained kernel, recording, Cycle, and Event, while the underlying evidence arrays cover the complete selected recording. Batch export would multiply artifacts and event-window export could hide samples outside the current annotation.
- **Question:** Should one action export the current kernel/recording, every recording for the current kernel, or every retained kernel and recording?
- **Options and tradeoffs:** One current kernel/recording produces one clear bounded artifact; all recordings provide convenient batch analysis with folder and partial-failure complexity; all kernels and recordings maximize evidence at the cost of large duplicate output and longer waits.
- **User answer:** Option 1: the currently selected kernel and recording.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-002, REQ-005, and AC-004 require one complete-recording CSV for the current kernel/recording selection without Cycle/Event cropping.

### DISC-004: CSV column set
- **Situation:** Replay evidence contains many diagnostic arrays, but the requested workflow names Internal IMU, FIR output, and score. Sample index and time are required to align rows, while threshold is needed to interpret score crossings.
- **Question:** Should the CSV use a compact requested schema, a complete diagnostic schema, or configurable columns?
- **Options and tradeoffs:** A compact schema is small and stable; a complete diagnostic schema adds Actual External IMU, residuals, ratios, states, and triggers at the cost of width; configurable columns add UI and artifact variability.
- **User answer:** Use the compact fields and also include threshold.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-003 and REQ-006 define the exact ten-column schema and exclude additional Replay diagnostic columns.

### DISC-005: Complete diagnostic column correction
- **Situation:** The canonical draft selected the compact schema, but the user subsequently annotated the complete diagnostic option.
- **Question:** Should the prior compact schema remain, or should the export include all available Replay diagnostics?
- **Options and tradeoffs:** The compact schema is narrower; the complete schema is wider but enables external inspection of measured versus predicted signals, residual normalization, detector state, and trigger decisions without reopening the charts.
- **User answer:** Select option 2: include Actual External IMU, Residual, Normalized Residual, Threshold, Collision Ratio, Detector State, and Trigger in addition to the existing aligned fields.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-004 supersedes DEC-003; REQ-001, REQ-006, and AC-001 now require the exact complete diagnostic schema.

### DISC-006: FAMOS verification payload
- **Situation:** The sample table already contains the FIR-predicted signal, but FAMOS cannot independently reproduce it without the selected trained model parameters. The phrase "recursive result" could mean either trained regression parameters or a per-sample arithmetic expansion.
- **Question:** Should the export add the trained model parameters or expand the first samples into individual FIR lag contributions?
- **Options and tradeoffs:** Model parameters let FAMOS reconstruct the complete recording with a compact preamble; per-sample expansion is easier to inspect manually but is wide, limited to selected samples, and does not provide a reusable model definition.
- **User answer:** Option 1: add the regression/training model parameters.
- **Explicit rationale:** The user wants to confirm the result in FAMOS.
- **Resulting impact:** DEC-005, REQ-007, and AC-005 require a selected-model parameter preamble that supports independent reconstruction.

### DISC-007: Separate model artifact and recording-only Replay
- **Situation:** A model preamble in the sample CSV complicates FAMOS sample-table import, while Cycle/Event selection only provides latency context and does not change the full-recording FIR, residual, score, threshold, or trigger arrays.
- **Question:** Should model parameters remain in the Replay CSV, move to a separate artifact, and which Replay selectors remain necessary?
- **Options and tradeoffs:** A combined CSV keeps one file but needs variable header skipping; a separate model artifact preserves a clean sample table; retaining Cycle/Event selectors preserves latency context but adds controls that do not affect the requested recording export.
- **User answer:** Choose the separate model artifact, make it TXT, retain only the recording selector, derive the CSV default filename from the recording filename, and add Export Model TXT.
- **Explicit rationale:** The user considers Cycle and Pick selection unnecessary in Analytical Replay and wants recognizable export naming plus a separate model file for FAMOS.
- **Resulting impact:** DEC-006 through DEC-008 and REQ-005, REQ-007 through REQ-009 define separate artifacts and a recording-only Replay workflow.

### DISC-008: Collision-safe recording-derived CSV name
- **Situation:** Reusing an imported CSV's exact filename could propose overwriting the source measurement; XLSX worksheets also share one workbook stem.
- **Question:** Should the proposed CSV name append a safe suffix or exactly reuse the recording filename with an overwrite guard?
- **Options and tradeoffs:** Appending `_replay` preserves source identity and avoids source-path collisions; exact reuse is shorter but requires rejecting the most natural destination when the source is already CSV.
- **User answer:** Option 1: append `_replay` and include worksheet identity where applicable.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-009 refines REQ-009 with a deterministic collision-safe default name.

### DISC-009: Model TXT encoding
- **Situation:** FAMOS can consume either labeled text or a positional numeric matrix, but a positional layout makes axis and lag mistakes difficult to detect during independent verification.
- **Question:** Should Model TXT use named sections with explicit axes/lags or pure numeric blocks with an externally documented order?
- **Options and tradeoffs:** Named sections are self-describing and auditable with modest parsing work; pure numeric blocks are faster to bulk-import but fragile when ordering assumptions differ.
- **User answer:** Option 1: use the named, sectioned format.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-010 and the refined REQ-007/AC-005 define a deterministic, labeled Model TXT contract.

### DISC-010: Model TXT default filename
- **Situation:** The selected frozen model belongs to the inspected kernel and is reused across recordings, so a recording-derived filename could produce differently named copies of identical model content.
- **Question:** Should Model TXT use a kernel-only name or combine recording and kernel identities?
- **Options and tradeoffs:** `<kernel_id>_model.txt` is stable and accurately reflects model ownership; `<recording_stem>_<kernel_id>_model.txt` groups artifacts by recording but implies recording-specific model content and creates duplicate names for the same model.
- **User answer:** Option 1: use `<kernel_id>_model.txt`.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-011 closes the artifact-naming contract in REQ-007.

## Out of Scope

- Changing FIR fitting, replay arithmetic, score calculation, or collision qualification behavior.
- Replacing the existing `.dicsproj` project persistence format unless explicitly selected.
- Batch export across multiple recordings or retained kernels.

## Open Decisions

None.

## Routing/Gates

- Existing governed project; architecture, TDD, architecture gate, and code review are required before delivery.

## Revision History

| Revision | Change |
|---|---|
| 1 | Started CSV Replay export contract from repository evidence. |
| 2 | Selected additive Replay CSV export while retaining charts and `.dicsproj` persistence. |
| 3 | Corrected the Replay scope: remove waveform charts and use CSV export while retaining `.dicsproj`. |
| 4 | Selected one complete-recording CSV for the current kernel and recording. |
| 5 | Selected the compact aligned column set with threshold and closed all product decisions. |
| 6 | Reopened and replaced the compact schema with the complete Replay diagnostic column set. |
| 7 | Reopened to add selected-model parameters for independent FAMOS reconstruction; the preamble encoding remains open. |
| 8 | Selected a separate Model TXT artifact, removed Cycle/Event selection from Analytical Replay, and requested recording-derived CSV naming; exact artifact naming/encoding remains open. |
| 9 | Selected collision-safe `<source_stem>[_worksheet]_replay.csv` default naming. |
| 10 | Selected a named, sectioned Model TXT encoding with explicit axis and lag labels. |
| 11 | Selected `<kernel_id>_model.txt` and closed all product decisions. |
| 7 | 2026-08-27 | Reopened before clarification: Clarify requested recursive-result rows for FAMOS verification. |
