---
spec_version: 1
spec_id: SPEC-0039
revision: 185
status: confirmed
change_set: model-parameter-export
working_id: WORKING-SPEC-01a0a7a57a23-model-parameter-export
task_ref: 01a0c356-d77c-7421-935c-72e5a478a492
---

# Software model parameter export for ESP32

## Synchronization Status — 2026-09-21

Current scope updated on 2026-09-22 by explicit user instruction: desktop JSON export only. Firmware import/runtime, ESP32 RAM and device verification are excluded and are not acceptance prerequisites. Historical decisions and discussion remain historical; DEC-094 and current Requirements/Acceptance Criteria govern this revision.

## Problem

Export Profile currently hides JSON export behind a previous-page selection and devotes the page to unused header controls. Users need all qualified kernels and model metadata with directly accessible JSON export.

## Solution

Provide a full-width qualified-kernel list with four metadata columns and one JSON export action per row, preserving existing desktop JSON semantics and safe file writing.

## Current Decision Summary

Desktop JSON export and Export Profile UI only. Both Float32 and Float64 are preserved; input units are g. No firmware implementation, memory budget or physical-device evidence belongs to this delivery.

## User Stories

- As a user, I can deploy trained models as parameters and inspect software and firmware responsibilities separately.

## Requirements

| ID | Requirement |
|---|---|
| REQ-004 | Desktop export produces a strict UTF-8 JSON artifact for one qualified model. Firmware import and runtime are not deliverables of this specification. |
| REQ-005 | Each JSON file contains exactly one frozen model and its complete execution settings. Exporting different kernels produces independent files. |
| REQ-022 | Allow independent editing of model name and filename. Default name is model type, required sampling rate and stable kernel number, such as FIR_1000Hz_k001, without a timestamp. Suggest name plus .json; changing filename does not change embedded name. |
| REQ-025 | JSON export supports qualified dual-IMU FIR/Ridge only. Preserve existing desktop training and simulation for other families; explain unsupported JSON export without silently changing model family. |
| REQ-026 | Preserve the declared Float32 or Float64 model precision, exact selected-type numeric values including signed zero, array shapes and ordering. Never narrow precision for export. |
| REQ-027 | Desktop export adds no ESP32 RAM, taps, rate or capacity gate, warning or capability query. Keep qualification and JSON semantic validation. |
| REQ-040 | Export only current qualified profiles with the same frozen parameters, preprocessing, detector settings and numeric precision. Recheck current availability when preparing and saving; reject stale, failed, incomplete and invalid results. |
| REQ-044 | Export a complete frozen execution snapshot including format/version, name, family, numeric type, required rate, input identities, model coefficients, preprocessing, residual, detector and provenance. Do not rerun training or Qualification during export. |
| REQ-045 | Validate finite numbers, dimensions, rates, positive scales and thresholds, Unicode model names and local JSON filenames. Internal/External XYZ units are user-confirmed g, without conversion. Preserve provenance identity independently of display name and filename. |
| REQ-049 | Restore exported arrays and settings on the desktop and verify reference prediction and strict threshold behavior in the declared numeric precision. This is desktop roundtrip evidence, with no firmware or device parity claim. |
| REQ-058 | Preserve frozen single-sample 1_OF_1 detector semantics, threshold, release ratio and quiet time. Do not silently rewrite multi-sample confirmation. Show a reason for an otherwise qualified row that cannot be exported as JSON. |
| REQ-097 | Export Profile lists all qualified kernels independently of previous-page selection. Each row shows Kernel ID, History/taps, threshold and qualified range, with Export JSON at the far right. Use actual passing speeds when available without inventing continuous coverage. Keep fixed headings, a scrolling body, per-row eligibility reasons and empty-state guidance to Replay & Qualify. Each action opens the existing name and save dialogs for that row alone. |
| REQ-098 | Remove Header Format, Header Preview, Export Headers and Selected Kernels sidebar from Export Profile. Preserve existing header serialization APIs for other callers. Keep JSON filename validation, explicit overwrite confirmation, atomic commit and failure cleanup; show actionable save errors. |

| REQ-001 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-002 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-003 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-006 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-007 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-008 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-009 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-010 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-011 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-012 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-013 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-014 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-015 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-016 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-017 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-018 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-019 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-020 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-021 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-023 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-024 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-028 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-029 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-030 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-031 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-032 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-033 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-034 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-035 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-036 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-037 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-038 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-039 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-041 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-042 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-043 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-046 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-047 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-048 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-050 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-051 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-052 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-053 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-054 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-055 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-056 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-057 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-059 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-060 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-061 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-062 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-063 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-064 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-065 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-066 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-067 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-068 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-069 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-070 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-071 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-072 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-073 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-074 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-075 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-076 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-077 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-078 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-079 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-080 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-081 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-082 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-083 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-084 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-085 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-086 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-087 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-088 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-089 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-090 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-091 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-092 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-093 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-094 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-095 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |
| REQ-096 | Retired from current desktop delivery by DEC-094. The previous cross-project obligation remains historical and imposes no firmware implementation or device validation requirement on this task. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Discuss parameter-based deployment. | User requests parameters and references env_sensing. |
| DEC-002 | Maintain separate project-local software and firmware specifications. | Explicit user instruction on 2026-09-16. |

| DEC-003 | Use software file export followed by env_sensing Web import and device validation/apply/save. | User answered 符合 to Q-001 version 2. |

| DEC-004 | Select JSON as the exchange file format. | User answered 確定 to Q-002 version 4. |

| DEC-005 | Adopt one model with complete execution settings per JSON file. | User answered 採用 to Q-003 version 6. |

| DEC-006 | Retain multiple models on the device and select one to run through the Web UI. | User selected option 2 of Q-004 version 9. |

| DEC-007 | Adopt no-reboot Apply with the user correction: 套用後就停止IMU. | User selects option 1 with an explicit additional condition; automatic recovery wording is not adopted. |

| DEC-008 | Supersede DEC-007 wording 停止IMU with 停止碰撞判斷; preserve no-reboot Apply. | User explicitly clarified intended function. Acceleration-warning stop is only a question, not adopted. |

| DEC-009 | Add independent switches for collision detection and acceleration warning. | Explicit user request in response to Q-007; no persistence/default policy inferred. |

| DEC-010 | Use Web checkboxes with the existing Orientation Draft/Apply/Save/persistence behavior. | Explicit user reference plus inspected current UI and persistence code; do not copy Orientation default value. |

| DEC-011 | Both switches default enabled, including missing fields in legacy configurations. | User selects 兩項預設開啟 in Q-009. |

| DEC-012 | Preserve acceleration-warning independence; reject disabling it as a side effect of collision model changes. | User explicitly states models are for collision judgment and acceleration warning is unrelated. |

| DEC-013 | Resume acquisition after successful model Apply, preserve acceleration warning and require manual checkbox Apply to re-enable collision detection. | User adopts Q-011. This resolves the earlier alternative of leaving acquisition stopped after success. |

| DEC-014 | Reject sample-rate mismatch and explicitly show the model required rate and device effective input rate. | User chooses option 1 and requests sampling-rate explanation. |

| DEC-015 | Preserve the original collision method and add an explicit Web selector for it or an imported model. | User selects option 1 and requests a collision-model selection option. |

| DEC-016 | Show each loadable imported model separately with its sampling rate; exclude unloadable models from collision selection. | User says imported model count determines option count and requires hiding unloadable artifacts. Existing original-method option is retained. |

| DEC-017 | On selected-model load failure, automatically apply the original algorithm and preserve the prior collision-enable state. | Latest explicit user correction in DISC-025 supersedes prior forced-disable recovery. |

| DEC-018 | Let an already-triggered collision alarm finish normally after collision detection is disabled; suppress subsequent detections and preserve records. | User selected option 2 of Q-016 version 35. |

| DEC-019 | Deleting the applied model automatically applies the original algorithm and preserves the previous collision-enable state. | User selects option 1 with an explicit correction to its forced-disable behavior; ordinary model Apply retains its separate disabled-after-Apply policy; load-failure behavior is revised separately under DEC-017. |

| DEC-020 | Deleting applied A repairs a saved reference to A automatically, while other settings retain their Save semantics. | User selects option 1 of Q-018 version 40. |

| DEC-021 | New-model import only stores and lists the model; switching requires explicit selection and Apply. | User chose option 1 of Q-019 version 42, consistent with retaining multiple models at different sampling rates. |

| DEC-022 | Ask before replacing a same-name model with changed parameters; cancellation retains the old model. | User selects option 3 of Q-020 version 44. |

| DEC-023 | Export exposes editable model name and JSON filename; model default is type_required-Hz_model-number. | User chooses naming option 1 and asks to enter both names; filename initially follows model name with .json. |

| DEC-024 | Replacing the running model updates storage only; keep its old runtime parameters and show pending Apply until manual activation. | User selects option 1 of Q-022 version 48. |

| DEC-025 | Restart loads latest committed model parameters for the saved model selection; old RAM parameters last until Apply or restart. | User selects option 2 of reopened Q-025 version 54, superseding old-version retention across reboot. |

| DEC-026 | Include dual-IMU FIR/Ridge, dual-IMU MLP and single-IMU Ridge in the first JSON deployment release. | User selects option 1 of Q-024 version 52. |

| DEC-027 | Preserve the verified float32/float64 model precision without automatic down-conversion; predictive suitability rejection is withdrawn under DEC-028. | User selects precision preservation in Q-026; later Q-027 assigns suitability judgment to the user. |

| DEC-028 | User judges whether deployment is suitable; remove proposed automatic resource/support-envelope admission. | Explicit answer to Q-027 version 58 overrides earlier resource-ineligible rejection wording. Actual operation failures still require error handling. |

| DEC-029 | Keep JSON as both exchange and persistent model format; decode execution parameters at Apply or boot. | User selects option 1 of Q-028 version 60. |

| DEC-030 | Fix single-IMU input source to the trained/exported internal/external selection. | User selects option 1 of Q-029 version 62. |

| DEC-031 | Imported-model threshold equals JSON baseline multiplied by the effective device multiplier controlled through knob, Web or CANopen. | User adopts adjustable threshold with an explicit multiplicative refinement; original baseline is preserved. |

| DEC-032 | Last effective knob/Web/CANopen operation sets the imported-model multiplier; original-algorithm control rules remain separate. | User chooses option 2 of Q-031 version 66 and identifies zero-means-knob as legacy behavior. |

| DEC-033 | Share one multiplier across all imported collision models. | User selects option 2 of Q-032 version 68; only the JSON baseline changes when selecting another imported model. |

| DEC-034 | Restore the saved shared multiplier on boot; initial knob read only establishes a position baseline. | User selects option 1 of Q-033 version 70. |

| DEC-035 | Imported-model knob multiplier starts at 0.50 and increases by 0.25 over 16 positions, ending at 4.25. | Explicit user custom mapping; retain existing 1..15,0 position numbering rather than alter the physical selector convention. |

| DEC-036 | Web/CANopen multiplier can be any representable finite positive value, independently of physical knob detents. | User selects option 2 of Q-035 version 74. |

| DEC-037 | Reuse the existing collision-setting field and CANopen 0x2007:00 with algorithm-dependent interpretation. | User explicitly states that it is the same field with different calculations for different collision algorithms; separate-object recommendation is not adopted. |

| DEC-038 | Missing/new imported-model multiplier defaults to 1.0. | User confirms Q-037; preserve saved values and boot knob-baseline behavior. |

| DEC-039 | Algorithm switching retains the shared numeric field rather than restoring a previous value for that algorithm category. | User chooses option 2 of Q-038 version 80. |


| DEC-040 | Convert the original-algorithm zero sentinel to 1.0 on switching into an imported model, with visible Web notice. | User chooses option 1 of Q-039 version 82. |

| DEC-041 | New JSON export permits only software-qualified models. | User chooses option 1 of Q-040 version 84, retaining the current qualification restriction. |

| DEC-042 | Model names differing only in English letter case identify different models. | User chooses option 2 of Q-041 version 86. |

| DEC-043 | Permit qualified already-filtered single-IMU models to deploy with no additional model filter and user-managed input-preprocessing consistency. | User chooses option 1 of Q-042 version 88. |

| DEC-044 | Suspend collision-model preprocessing while collision detection is disabled; restart with fresh state and readiness on re-enable. | User adopts Q-043 option 2 to avoid unnecessary processing/CPU use when collision functionality is not needed. |

| DEC-045 | Complete technical contract using existing frozen-model, configuration and transactional lifecycle semantics; preserve all user choices. | Engineering consolidation of OD-002 through OD-006, with source basis in Technical Contract; no product implementation or new resource-admission policy. |

| DEC-046 | Separate Web collision-model file management into its own page; retain operational selection/settings in Device Configuration. | User chooses option 1 of Q-044 version 96. |

| DEC-047 | Hide original-algorithm-only settings in imported-model mode and retain their values for switching back. | User chooses option 1 of Q-045 version 98. |

| DEC-048 | Use one export dialog per model, with independently editable names and save location. | User selects option 2 of Q-046 version 100. |

| DEC-049 | Display model summary only in Device Configuration for now; retain the separate management page without a duplicated summary or full-coefficient viewer. | User limits summary placement after asking whether Device Configuration alone is sufficient. |

| DEC-050 | Adopt option 1: callback owns the complete collision algorithm; CollisionDetector.Process selects and invokes it and receives common results. | User explicitly selected 方案1 after proposing callbacks at the existing collision entry. No separate inference task is authorized by this choice. |

| DEC-051 | Use a bool-only collision callback result; handle warm-up and readiness internally. | User rejects the proposed richer result and notes the original algorithm also has warm-up. |

| DEC-052 | All original and imported collision algorithms execute their callback from one common post-input-preparation call site, accepting available single-source or complete paired input as applicable. | User explicitly requests moving the original call site and adopts the clarification that complete dual-IMU pairing is not mandatory for every invocation. This replaces the unaccepted separate per-algorithm call-site proposal. |

| DEC-053 | Adopt distinct initialize, reset and bool execute operations; share callback code by algorithm family and select artifact parameters separately. | User adopts the lifecycle proposal and requests continued discussion. |

| DEC-054 | Use single-score triggering and preserve runtime state on multiplier-only updates; next eligible score uses the new threshold. | User selected option 2 and explicitly corrected the example: score超過門檻一筆就觸發. No consecutive-count reset policy is needed. |

| DEC-055 | Supply one coherent setting snapshot per collision computation through the common configuration authority, independent of knob/Web/CANopen source. | User adopts the proposal that mid-computation updates take effect next time and algorithm callbacks do not access control sources directly. |

| DEC-056 | Select option 1: each algorithm manages its own private runtime state; outer orchestration uses initialize/reset/execute. | User selects 1 over centralizing family-specific state in CollisionDetector. |

| DEC-057 | Adopt option 1: initialize/reset/process function-pointer table plus opaque instance identity. | User selects function-pointer callbacks over a C++ virtual common interface, preserving algorithm-private state ownership. |

| DEC-058 | Select option 1: no previous-model parameter cache after switching; reload other selected models from Flash. | User selects 1 and additionally reports that current RAM is already tight. Switching peak memory needs separate design, not merely steady-state cache removal. |

| DEC-059 | Select option 1: release old model runtime after successful preflight/quiescence and before loading the new runtime. | User selects 1 in response to tight RAM; failed post-release loading follows the already accepted original-algorithm fallback. |

| DEC-060 | Select option 1: bounded streaming JSON parsing directly into final model arrays, with multiple passes when needed. | User chooses streaming over full-document parsing in the context of tight RAM. |

| DEC-061 | Select option 1: add algorithm-owned destroy to the lifecycle callback table. | User chooses common-table cleanup over a separate instance creation/destruction interface; initialize/reset/process retain their accepted semantics. |

| DEC-062 | Select option 1: pause IMU during model import, then restore prior acquisition/function state and continue the original selected model. | User adopts paused import rather than concurrent Flash writes and active sensing; ordinary Apply remains a separate action with its established behavior. |

| DEC-063 | Select option 1: fixed inline interruption notice and explicit 暫停 IMU 並匯入 action, without a second pause-confirmation modal. | User chooses the direct explained action; same-name replacement confirmation remains required. |

| DEC-064 | Consolidate model import, summary and existing model controls in Device Configuration; no separate collision-model management page. Supersedes DEC-046 and the separate-page clause of DEC-049; summary-only display remains. | User corrects the assistant page arrangement and explicitly states import in Device Configuration immediately displays the model summary. Q-057 navigation alternatives are withdrawn as inapplicable. |

| DEC-065 | Select option 2 with refinement: two summary areas only, with one reusable imported/selected-model preview and one actual applied-model summary. | User requests that switching the selected model also changes its summary and limits the model presentation to those two summary areas. |

| DEC-066 | Select option 2: no Cancel Import button or user-requested in-progress cancellation flow. | User chooses the simpler wait-for-success/failure flow; automatic failure cleanup and prior-state restoration remain required. |

| DEC-067 | Select option 1: directly expanded Device Configuration model section. | User selects immediate visibility over a collapsible model area. Together with prior export and summary decisions this settles the user-facing UI composition scope of OD-008. |

| DEC-068 | Adopt Q-061 option 1: original and imported collision algorithms remain in the existing collision module, split into separate implementation files with private per-algorithm state. | User annotation selects the recommendation and replies 採用; no separate model-inference module is requested. |

| DEC-069 | Select option 1: independent model-storage component alongside the existing device-configuration store, sharing underlying Flash coordination. | User confirms after clarification that separate persisted files and separate managing components do not require separate Flash hardware or partitions. |

| DEC-070 | Select option 1: build model lists from committed JSON metadata without a separate persistent index file. | User chooses one persistent artifact source rather than synchronizing an additional model index; only metadata is needed for enumeration. |

| DEC-071 | Retain original force calibration as read-only while an imported model is applied; require explicit Apply of the original algorithm before calibration operations. | User selected Q-064 option 1. |

| DEC-072 | During active original collision calibration collection, reject model switching and require the user to finish or cancel calibration before retrying Apply. | User selected Q-065 option 1. |

| DEC-073 | Competing model Apply and deletion during import receive immediate Busy rejection without a pending-operation queue. | User selected Q-066 option 1. |

| DEC-074 | On actual imported-model non-finite computation with valid input, coordinate fallback to the original algorithm while preserving collision enable and rewarming the original algorithm. | User selected Q-067 option 1; subsequent question requests explanation, not withdrawal. |

| DEC-075 | Supersede DEC-074 for actual non-finite model execution: choose option 2, disable collision, retain model and emit an abnormal log. Keep load-failure fallback unchanged. | User explicitly changes choice: 改選擇2，要輸出異常log。 |

| DEC-076 | Replace bool-only process with a small structured DetectionStatus plus ErrorCode result for all algorithms. No separate fault query or fault-notification callback is required. Supersedes DEC-051 and only the bool-return clause of DEC-053; lifecycle and readiness ownership remain. | User chooses 方案2 in the latest three-option comparison, meaning structured result, not the older Q-068 callback option. |

| DEC-077 | Parent the independent model-storage component under Device Management alongside configuration; keep Flash admission in Data Services and cross-parent IMU/runtime orchestration in firmware_system. | User selects Q-069 option 1. |

| DEC-078 | Adopt a separate model-parameter validation/loading component rather than embedding that responsibility in model storage. | User selects option 1 after clarification separating parameter checking, loading and code ownership. |

| DEC-079 | Parent the parameter validation/loading component under Sensor Pipeline, alongside collision; retain cross-L1 storage/execution orchestration in firmware_system. | User selects Q-071 option 1. |

| DEC-080 | Algorithm allocates and owns final parameter RAM; loader fills it via parent-mapped checked interfaces; algorithm lifecycle cleans incomplete instances. | User selects Q-072 option 1; retain one full parameter representation and release-before-load. |

| DEC-081 | Imported-model mode reuses 536 for score and 540 for effective threshold; 537-539 and 541-545 are not applicable. Preserve other applicable subscribed outputs and original-mode mappings. | User replaces Q-073 binary choices with explicit per-address behavior and continued subscription/output support. |

| DEC-082 | Keep 536/540 fixed Float32 output for compatibility; retain model-native internal precision and report out-of-range output invalid. | User selects Q-074 option 1. |

| DEC-083 | Use a designated quiet-NaN marker in existing Float32 binary collision fields with no new per-field wire status; distinguish it from actual model numeric Error. | User selects option 1, asks about immediate return on NaN, then confirms understanding. |

| DEC-084 | Project 536 score and 540 threshold from the same model evaluation; multiplier changes update the output pair on the next valid evaluation. | User selects Q-076 option 1. |

| DEC-085 | Preserve existing last-frame downsample behavior for model telemetry, without interval peak aggregation. | User explicitly says 沿用目前down sample方式就可以了. |

| DEC-086 | Accept the integrated architecture and finalize the two separate project specifications. Logical design is confirmed; implementation and all required validation remain pending. | User says 採用 after integrated review and clarification that latest-output snapshots are not historical capture. This accepts the SPEC design, not an ADR or product execution. |


| DEC-087 | First-release ESP32 deployment is dual-IMU FIR/Ridge only; supersedes DEC-026 family coverage. | User: 目前ESP32只要實作FIR/Ridge 就可以了。之前軟體模擬MLP跟single IMU結果都不理想。 |
| DEC-088 | Reuse fixed-capacity RAM and restrict ESP32-targeted history choices to supported capacity; supersedes variable model-sized allocation and blanket no-capacity-limit clauses. | User: 我比較傾向固定RAM，軟體也只能選取適合的時間長度。 No numeric budget/tap count is adopted. |
| DEC-089 | Restore and synchronize the separate firmware model contract under a non-conflicting new SPEC identity; preserve recovered historical snapshot. | User: 有辦法復原?我不小心刪除了; 幫我整理同步。 |

| DEC-090 | Software options and export are not restricted by ESP32 capacity; no deployment-purpose selector. Supersedes the software-history restriction in DEC-088 and DISC-093; fixed firmware RAM remains. | User: 不需要限制。使用者要知道自己的功能選項。 |

| DEC-091 | Execute the desktop JSON export scope now. Leave ESP32 RAM configuration, PP-001 adoption and target memory acceptance decisions to the firmware project. Firmware contracts remain interoperability references, not desktop implementation obligations or capacity gates. | current user request: 執行桌面端 JSON 匯出; annotation 1: 把 ESP32 記憶體配置的決定留給韌體專案。 |

| DEC-092 | Redesign desktop Export Profile around kernel rows with Kernel ID, History/taps, threshold, qualified range and directly accessible JSON export; remove Header Format and Export Headers controls. Preserve the user's alternatives of page-local selection or all-qualified per-row actions; the detailed assistant layout remains a proposal. | User request in task 01a0c356-d77c-7421-935c-72e5a478a492, 2026-09-22: Export profile。要可以選擇kernel。或著是列出所有通過的kernel，在最右邊點選 Export JSON。Header format不需要、Export headers不需要。條列式的kernel，要顯示Kernel ID、History/taps、threshold、qualified range。 |

| DEC-093 | Adopt the presented full-width all-qualified kernel list with per-row Export JSON, four requested metadata columns, no Header Format/Header Preview/Export Headers/Selected Kernels sidebar, fixed headings, scrolling and empty-state guidance. Preserve name/file/overwrite workflow and expose existing JSON eligibility errors per row. | user:01a0c6d2-2051-7b23-b2da-271b6992fb8f:execute-ui — 開始執行, following the presented UI plan. |

| DEC-094 | Limit current requirements, acceptance and execution to desktop JSON export and the adopted kernel-list UI. Supersedes cross-project scope in DEC-091 and earlier firmware deployment requirements for this deliverable. Preserve historical discussion without requiring firmware implementation or evidence. | User explicitly states only software JSON output, excludes firmware import/RAM/device verification and instructs continue execution. Source user:01a0c6e1-3f04-7e23-8fbe-6bbdb153c03d:continue-desktop |

## Discussion Context

### DISC-001: Deployment form and project ownership

- **Situation:** Existing exports and deferred deployment contracts do not define ESP32 parameter loading.
- **Question:** Which deployment form and specification ownership have been requested?
- **Options and tradeoffs:** Separate project-local specifications keep ownership explicit but require shared-contract consistency checks; the user already selected this split.
- **User answer:** 我想要用參數的形式。可以參考env_sensing專案。開始討論，要區分env_sensing專案SPEC、軟體SPEC。env_sensing專案SPEC放在env_sensing專案資料夾內。
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** REQ-001, REQ-002, DEC-001 and DEC-002 record the confirmed direction. No product execution requested.

### DISC-002: Confirmed file-to-Web deployment workflow

- **Situation:** Software and firmware responsibilities require one shared operator workflow.
- **Question:** 第一版採用「軟體匯出模型參數檔 → 使用者在 env_sensing 網頁匯入 → 裝置檢查後套用與儲存」的操作流程，符合你的預期嗎？
- **Options and tradeoffs:** Reuse the Web import interaction and keep export independent from device connectivity; manual file selection is required. Model handling remains new work.
- **User answer:** 符合
- **Explicit rationale:** No further rationale supplied.
- **Resulting impact:** Add REQ-003, DEC-003 and AC-003; resolve OD-001. Exact activation/save transaction semantics remain OD-004.

### DISC-003: Validation explanation and proposed JSON format

- **Situation:** User requests clarification of export validation and asks whether the parameter file is JSON.
- **Question:** 驗證哪些項目? 參數檔使用json格式?
- **Options and tradeoffs:** Propose checking current qualified model identity, complete finite arrays and shapes, complete preprocessing/detector contract, artifact roundtrip and numeric consistency, and target capability/size constraints. Propose JSON for inspectability and compatibility with existing env_sensing configuration tooling; larger files and parse-memory cost require explicit bounds. Existing configuration persistence envelope is 1024 bytes and is not a model capacity guarantee. These are discussion proposals, not adopted requirements.
- **User answer:** 驗證哪些項目? 參數檔使用json格式?
- **Explicit rationale:** Requests explanation; no format selection inferred.
- **Resulting impact:** Clarifies REQ-001 and AC-001 without changing their confirmed scope. OD-003 retains JSON/schema/numeric choices; OD-004 retains validation limits and acceptance evidence. Export checks do not establish board RAM or timing PASS.

### DISC-004: JSON exchange format confirmed

- **Situation:** The accepted file-to-Web workflow requires an exchange format.
- **Question:** 是否確定第一版以 JSON 作為軟體匯出、env_sensing 網頁匯入的模型參數檔格式？
- **Options and tradeoffs:** JSON is inspectable and familiar to existing firmware tooling; file size and parsing memory still need bounded design. Exchange format does not select Flash storage layout or numeric precision.
- **User answer:** 確定
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** Add REQ-004, DEC-004, AC-004 and refine REQ-001. Resolve exchange encoding portion of OD-003 only.

### DISC-005: Resource verification and legacy envelope clarification

- **Situation:** User asks what runtime resource checks mean and who imposes the reported 1 KB limit.
- **Question:** 不懂這個檢查項目。這是誰限制的?
- **Options and tradeoffs:** Desktop checks can count parameters and validate files. Device measurements determine total working RAM and ability to keep up with acquisition while other tasks run. Example only: 1000 float32 parameters occupy 4000 bytes before histories, intermediates and parsing. No resource limit is adopted by this explanation. The existing firmware AbConfigurationStore::MaxEnvelopeBytes = 1024U at src/adapters/littlefs/configuration/ab_configuration_store.h:36 is an application configuration envelope limit, enforced by its storage adapter; it is not an ESP32, JSON or LittleFS maximum. A model-specific capacity remains undecided.
- **User answer:** 不懂這個檢查項目。這是誰限制的?
- **Explicit rationale:** Clarification requests, not acceptance of new validation gates or capacity.
- **Resulting impact:** Clarify proposed REQ-001/AC-001 verification without new mandatory checks; retain OD-004 for actual limits and evidence.

### DISC-006: One model per JSON confirmed

- **Situation:** JSON file granularity must be distinguished from device model storage/activation count.
- **Question:** 是否採用「每個 JSON 檔只放一個模型，以及執行它所需的完整設定」？
- **Options and tradeoffs:** One self-contained model per file preserves independent inspection/replacement; multiple model exports create multiple files. This does not decide how many models the device retains or executes.
- **User answer:** 採用
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** Add REQ-005, DEC-005 and AC-005; refine OD-003 artifact granularity. Device retention and activation remain OD-004.

### DISC-007: Storage envelope versus signal envelope

- **Situation:** The same English word appears in storage and signal-processing code.
- **Question:** Envelope不是碰撞演算法的envelope?
- **Options and tradeoffs:** MaxEnvelopeBytes in AbConfigurationStore limits serialized configuration plus metadata/CRC in bytes; envelope_samples in DeviceConfiguration and AccelerationFeatureProcessor controls the signal-processing window in samples. They have different owners, units and purposes. Explain storage envelope as configuration file wrapper to avoid ambiguity; no renaming or algorithm change is requested.
- **User answer:** Envelope不是碰撞演算法的envelope?
- **Explicit rationale:** Terminology clarification requested.
- **Resulting impact:** Clarifies REQ-001 and REQ-002 discussion vocabulary; no new capacity or algorithm requirement.

### DISC-008: Multiple stored models with one active model

- **Situation:** A.json and B.json are independently exported artifacts. Device retention determines whether switching back requires upload.
- **Question:** ESP32 裝置內的模型保存方式，你希望採用哪一種？
- **Options and tradeoffs:** 只保存一個模型：匯入 B 並成功替換 A 後，想用回 A 就要重新上傳 A.json。儲存與操作較簡單，適合很少換模型；經常比較模型時較麻煩。 / 保存多個模型，每次選一個執行：先匯入 A.json、B.json，之後在網頁選擇啟用 A 或 B。適合經常比較或切換，不必重傳；需要較多 Flash、模型清單及刪除管理，保存數量與總容量另訂。
- **User answer:** 2
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** Add REQ-006, DEC-006 and AC-006. Device stores multiple models with a Web list and selection, runs one at a time; OD-004 retains capacity, replacement/deletion rules, activation and recovery decisions. Refines the REQ-005 note that file granularity did not decide device retention.

### DISC-009: Apply without reboot, then stop IMU

- **Situation:** Model selection requires an activation lifecycle. The user selects runtime Apply and adds a stop condition.
- **Question:** 在網頁選好另一個模型後，你希望怎麼切換生效？
- **Options and tradeoffs:** 按「套用」切換，不重啟 ESP32（建議）：裝置檢查並載入模型，重新初始化必要狀態，準備完成後恢復模型碰撞判定；切換與暖機期間顯示尚未就緒。適合反覆比較，但韌體需要處理切換協調與失敗復原。 / 重新啟動 ESP32 後生效：網頁記錄下次啟動的模型，重啟時載入。模型初始化流程較單純，適合只在維護時更換；每次切換會中斷裝置服務與連線。
- **User answer:** 選擇1。套用後就停止IMU。
- **Explicit rationale:** User explicitly adds stopping IMU after Apply; no further rationale.
- **Resulting impact:** Add REQ-007, DEC-007 and AC-007. Accept no-reboot Apply, but replace the option's automatic return to detection with the user's post-Apply IMU stop. OD-005 must clarify stop scope (physical acquisition versus publication), sequencing and subsequent restart behavior; do not silently equate this with Web live.stop.

### DISC-010: Stop collision judgment, not IMU acquisition

- **Situation:** Previous IMU-stop wording left acquisition versus publication ambiguous. User corrects the premise to collision judgment only and asks about existing controls.
- **Question:** 你說的「停止 IMU」，是指哪一種停止範圍？
- **Options and tradeoffs:** 停止 IMU 取樣與模型判定（依你的用語建議）：套用後不再產生新的取樣及模型判定結果；重新開始的操作另定。會影響依賴這些資料的功能，需要韌體協調停止流程。 / 只停止網頁即時資料傳送：IMU 仍可取樣，其他處理不因這個停止操作而關閉。較接近結束網頁 Live 工作階段，適合只想停止觀察；不等於停止感測器。
- **User answer:** 我的想法是停止碰撞判斷。目前env_sensing有停止碰撞判斷、停止加速度警告?
- **Explicit rationale:** User clarifies intended stopped function and asks factual capability question.
- **Resulting impact:** Refine REQ-007/AC-007 and add DEC-008 superseding DEC-007 stop wording only. Keep no-reboot Apply. Stop collision judgment after Apply; acquisition and telemetry are not stopped by this request. Existing DeviceConfiguration and ObservePhysicalCollision have no independent collision/acceleration-warning enable flags; both detectors are invoked on incoming samples. Collision threshold zero selects the hardware-selector path; acceleration warning compares RMS strictly above threshold, so zero is not off. OD-005 retains judgment restart/state/output handling and whether acceleration warning remains active. No independent-warning-stop behavior is inferred.

### DISC-011: Reference TCP parameter-update quiescence

- **Situation:** User notes stopping IMU may be simplest and points to the existing TCP setting flow.
- **Question:** Can the TCP parameter-update IMU-stop flow be used as reference?
- **Options and tradeoffs:** Existing SPEC-0048 stops and drains TCP publication, leaving publication stopped until explicit START. ConfigurePipeline stops physical acquisition while changing configuration and restarts on its resume path; ApplyAndSave stages then resumes physical acquisition. Thus the existing flow is a reference for coordination, not proof that IMU stays stopped after success. Reuse of a temporary acquisition pause is compatible with the user's collision-judgment-stop goal. Final acquisition state still requires clarification.
- **User answer:** 當然停止IMU是最簡單的方式。可以參考TCP設定時，會停止IMU那個流程
- **Explicit rationale:** User calls stopping IMU the simplest approach and requests reference to the TCP configuration flow.
- **Resulting impact:** Refine REQ-007/AC-007 so a temporary physical-acquisition pause is permitted as a candidate mechanism, and retain the requested post-Apply collision-judgment stop. OD-005 explicitly includes whether acquisition resumes after Apply or remains stopped. Preserve DEC-008 intent and do not infer a final-state selection from this reference request. Firmware relationship adds SPEC-0048 as reference only, not automatic wholesale adoption of every transport policy.

### DISC-012: Independent collision and acceleration-warning switches

- **Situation:** User proposes independent controls rather than using IMU acquisition stop as the only means to suppress judgment.
- **Question:** 參考 TCP 的停妥流程後，模型套用完成要停在哪個狀態？
- **Options and tradeoffs:** IMU 保持停止，等明確啟動才恢復（較符合你剛提的簡單方式）：碰撞與加速度警告都沒有新樣本可判斷，其他依賴 IMU 的功能也暫停；需要定義恢復取樣的操作。 / IMU 恢復取樣，但碰撞判斷保持停用：仍可觀察感測資料，加速度警告如何處理另定；需要新增獨立的碰撞判斷啟停控制，不能直接照搬現有 TCP 設定流程。
- **User answer:** 我認為可以追加碰撞偵測及加速度警告的開關
- **Explicit rationale:** No additional rationale supplied; user requests switches for both functions.
- **Resulting impact:** Add REQ-008, DEC-009 and AC-008. Independent switches are firmware-owned controls, separate from IMU sampling/telemetry. Each disabled function shall suppress new detection events without requiring sampling to remain stopped; precise signal-processing/state retention and already-active output handling remain open. Do not infer persistence, boot defaults, legacy-versus-model collision scope, or exact Apply-end switch values. REQ-007 post-Apply collision-stop intent remains; OD-005 retains activation sequencing and acceleration-warning behavior. OD-006 captures switch persistence/defaults and contract ownership relative to model JSON.

### DISC-013: Web checkboxes matching Orientation configuration semantics

- **Situation:** User specifies concrete Web controls by reference to the existing Orientation checkbox.
- **Question:** 碰撞偵測與加速度警告的開關，重新開機後要保留嗎？
- **Options and tradeoffs:** 納入裝置設定，按 Save 後保存（建議）：Apply 改變本次狀態，Save 決定重開機後的狀態，沿用現有設定操作。適合固定部署；若保存為關閉，重開機後也會維持關閉。 / 只在本次開機有效：不保存開關狀態，重開機回到另行約定的預設值。適合暫時測試；每次開機需要重新設定想停用的功能。
- **User answer:** web上也要有這兩個可設定的勾選，跟orientation相同
- **Explicit rationale:** User explicitly references the existing Orientation control.
- **Resulting impact:** Add REQ-009, DEC-010 and AC-009. Source web/src/features/configuration/controller.js renders boolean checkboxes, Apply submits Draft and Save stores applied state; orientation_enabled is persisted by ab_configuration_store.cpp. Adopt the same Draft/Apply/Save and boot-restore semantics for the two independent Web checkboxes. This resolves persistence by existing-behavior reference; checkbox defaults are not inferred from Orientation's own default. OD-006 retains defaults/migration and remaining cross-interface/JSON boundaries.

### DISC-014: Explicit reaffirmation of device-setting persistence

- **Situation:** User annotates the earlier persistence option while the initial-defaults question Q-009 remains pending.
- **Question:** Should the two switches be included in device configuration?
- **Options and tradeoffs:** Device configuration follows Apply/Save and restores saved values on reboot; session-only switches would not persist.
- **User answer:** 選擇納入裝置設定
- **Explicit rationale:** Explicit selection; no additional rationale supplied.
- **Resulting impact:** Reaffirm REQ-009, DEC-010 and AC-009 without changing their contract. This is not an answer to Q-009 about default/missing-field values. Preserve pending question and OD-006 defaults/migration.

### DISC-015: Both switches enabled by default

- **Situation:** Persistent checkbox behavior is confirmed; new and legacy missing-field initialization needs a decision.
- **Question:** 新設定的預設值，以及舊設定缺少這兩個欄位時，要怎麼初始化？
- **Options and tradeoffs:** 兩項預設開啟（建議）：延續目前兩種判斷都會執行的行為；需要停用時再取消勾選並 Apply。適合避免升級後既有偵測意外停止。 / 兩項預設關閉：先完成設定，再由使用者勾選啟用；初始操作較明確，但新裝置或舊設定升級後，未手動開啟前不會產生這兩類偵測事件。
- **User answer:** 兩項預設開啟
- **Explicit rationale:** Explicit selection; no additional rationale supplied.
- **Resulting impact:** Add REQ-010, DEC-011 and AC-010. Default both switches true; migrate each missing legacy field as true without overwriting an explicitly saved false. Defaults do not override the separately requested post-model-Apply collision-stop behavior. OD-006 default/migration portion is resolved; remaining activation and algorithm-selection details stay open.

### DISC-016: Acceleration warning is independent of collision models

- **Situation:** Assistant offered preserving or disabling acceleration warning during collision model activation. User rejects coupling these independent functions.
- **Question:** 套用新模型時，除了停止碰撞判斷，加速度警告的開關要怎麼處理？
- **Options and tradeoffs:** 維持原本設定（建議）：原本開啟就保持開啟，原本關閉就保持關閉；模型切換不改動獨立的加速度警告設定。有有效取樣時仍依原設定判斷，適合保留兩項功能的獨立性。 / 一併關閉：套用新模型後，碰撞判斷與加速度警告都停用，之後由使用者重新開啟。適合希望兩類事件都先暫停的測試流程，但需要額外啟用操作。
- **User answer:** 加速度跟模型沒關係吧，模式都是碰撞判斷用的
- **Explicit rationale:** Models serve collision judgment; acceleration warning is unrelated.
- **Resulting impact:** Add REQ-011, DEC-012 and AC-011. Collision model import/selection/Apply must not change acceleration-warning enable state or its independent threshold/algorithm configuration. Collision model JSON carries collision execution settings, not acceleration-warning controls. Withdraw coupled-disable proposal. A shared acquisition pause may temporarily remove samples but does not change warning settings. Remaining stop/resume and collision control details stay open in OD-005.

### DISC-017: Resume acquisition with collision detection disabled

- **Situation:** Independent switches allow acquisition and acceleration warning to resume without restarting collision judgment after model Apply.
- **Question:** 模型套用成功後，是否恢復 IMU 取樣，讓加速度警告依原設定運作，同時讓碰撞偵測維持關閉，等你手動勾選並 Apply 才重新開始？
- **Options and tradeoffs:** Resume acquisition after the temporary configuration pause, preserve independent warning settings, and leave collision detection disabled for explicit re-enable. Maintains observation/warning availability while requiring a deliberate collision start. Failure and warmup details remain separate.
- **User answer:** 採用
- **Explicit rationale:** User adopts the proposed complete success-state lifecycle.
- **Resulting impact:** Add REQ-012, DEC-013 and AC-012; refine REQ-007 and AC-007. Resolve successful post-Apply acquisition state and collision re-enable operation in OD-005. Saved states still follow REQ-009, not an automatic Flash write inferred from Apply. Remaining failure recovery and detector/output reset rules remain open.

### DISC-018: Reject incompatible sampling rate with explicit explanation

- **Situation:** A model trained for one sample interval cannot be applied to a different effective input rate without changing its temporal semantics.
- **Question:** 模型要求的取樣率與裝置實際提供給模型的取樣率不同時，要怎麼處理？
- **Options and tradeoffs:** 拒絕套用並提示差異（建議）：保留原模型與裝置設定，使用者先調整到相容取樣率再套用。避免模型切換連帶改變其他功能，但需要多一步設定。 / 套用時自動調整裝置取樣設定：在硬體能力允許且相關設定相容時，依模型要求更新後套用。操作較方便，但會連帶影響其他使用同一取樣資料的功能，需定義連動與失敗復原規則。
- **User answer:** 選擇1，但要有提示說明模式的取樣率
- **Explicit rationale:** User explicitly requires a message describing the model sampling rate.
- **Resulting impact:** Add REQ-013, DEC-014 and AC-013. Reject incompatible Apply before quiescing or mutating active model/settings; display required model rate and actual effective model-input rate in Hz, and instruct manual compatible setup before retry. Treat 模式 in this sampling context as the selected model. No automatic sampling change or resampling is adopted. Model list/inspection can expose declared rate; exact UI layout remains implementation design.

### DISC-019: Preserve original detector and add collision-model selection

- **Situation:** The device already has a collision algorithm; imported models add alternative collision methods.
- **Question:** 加入匯入模型後，env_sensing 原本的碰撞判斷演算法要如何保留？
- **Options and tradeoffs:** 保留為可選方式（建議）：網頁可選原有碰撞判斷或某個匯入模型，每次只執行選定的一種。方便沿用與比較，也能在尚未匯入模型時使用原有功能；需要清楚區分各方式適用的設定。 / 改為只使用匯入模型：移除原有碰撞判斷的使用入口，沒有有效模型時不能開始碰撞偵測。介面集中於模型部署，但既有使用方式需要遷移。
- **User answer:** 選擇1，新增可以選擇碰撞模型的選項
- **Explicit rationale:** User requests an explicit collision-model selection option while retaining the original algorithm.
- **Resulting impact:** Add REQ-014, DEC-015 and AC-014. Web selects original collision algorithm or an imported retained model; exactly one collision method executes when enabled. The collision enable checkbox governs the selected method. Preserve acceleration-warning independence. Existing per-method parameter semantics remain distinct; the original axis/vector mode is not a replacement for model-family selection. Apply follows confirmed compatibility/quiescence/disabled-after-Apply rules. OD-006 legacy-versus-model scope is resolved; initial selection, saved selection and missing-reference handling remain to be specified.

### DISC-020: One selector entry per loadable imported model

- **Situation:** User emphasizes multiple imported artifacts, including differing sample rates, rather than one option per model family.
- **Question:** 若選定的匯入模型無法載入，而且沒有可繼續使用的原模型，例如開機發現檔案損毀，要怎麼處理？
- **Options and tradeoffs:** 停止碰撞偵測並明確顯示原因（建議）：不自行換演算法，由使用者修復模型或選擇原有演算法。保留選擇的明確性，但處理完成前沒有碰撞判斷；加速度警告仍依自身設定運作。 / 自動改用原有碰撞演算法並明確提示：在原有演算法的設定有效且已就緒時繼續判斷。減少等待人工處理的時間，但實際判斷方式及門檻會改變，效果不等同原先選定模型。
- **User answer:** 我的想法是匯入多少模型，就有多少選項，因為取樣率都不相同。如果發現無法載入，就不要顯示在碰撞模型的選項內
- **Explicit rationale:** Imported models may require different sample rates; unloadable models should not appear as choices.
- **Resulting impact:** Add REQ-015, DEC-016 and AC-015; refine REQ-014. Each independently loadable imported model gets its own entry, including same-family/different-rate artifacts. Show identity and required Hz. Unloadable artifacts are omitted from collision selection; this does not authorize deletion or silent error suppression elsewhere. A valid artifact with only a mismatch to current model-input sampling rate remains listed; REQ-013 rejects Apply with both rates. Original algorithm remains an additional entry under DEC-015. User has not selected fallback for an already-active/saved reference that later becomes unloadable; keep that narrow recovery issue open rather than infer a fallback.

### DISC-021: Select original method but keep detection disabled on model-load failure

- **Situation:** Previously selected model A can become unloadable and is excluded from the selection list. Device active/selected state must remain coherent.
- **Question:** 若裝置原先選定 A，重新載入時 A 失敗、因此已從選單排除，此時碰撞判斷要怎麼處理？
- **Options and tradeoffs:** 維持停用並提示重新選擇（建議）：不自動選另一個模型；使用者選原有演算法或其他有效模型後再啟用。行為明確，但需要人工處理後才恢復碰撞判斷。 / 自動選原有碰撞演算法並提示：在原有設定有效且就緒時，依碰撞偵測開關決定是否執行。操作較省事，但判斷方式會從 A 改成原有演算法。
- **User answer:** 維持停用，並選擇原有碰撞演算法
- **Explicit rationale:** User explicitly combines disabled judgment with original-method selection.
- **Resulting impact:** Add REQ-016, DEC-017 and AC-016. When the selected model cannot load, omit it from choices, select original method, force collision detection disabled and explain cause. No automatic execution of original method. User explicitly enables through checkbox Apply subject to validity/readiness. Acceleration warning stays independent. Preserve separate Save semantics; no automatic Flash write is inferred. This resolves missing-reference operational fallback but not already-active alarm-output cleanup.

### DISC-022: Automatically apply original method during disabled fallback

- **Situation:** The prior recovery decision selected the original method while keeping collision detection disabled. User now explicitly requires automatic application and asks for an explanation of the separate active-alarm question.
- **Question:** Clarify automatic original-method application and the situation behind pending Q-016.
- **Options and tradeoffs:** Automatic application completes the fallback runtime method change without a second manual method Apply; selection-only would leave the runtime change pending. Applying a method and enabling collision judgment are separate controls under the previously adopted disabled recovery.
- **User answer:** 自動套用原有碰撞演算法；不懂問題情境
- **Explicit rationale:** User explicitly requests automatic application. No new choice about an already-triggered alarm or explicit reversal of the previous disabled-state requirement was supplied.
- **Resulting impact:** Refine REQ-016, DEC-017 and AC-016 to require automatic runtime application of the original method, not only selector change. Preserve collision disabled, independent warning settings and explicit Save. Preserve unanswered Q-016; explain the difference between stopping future detections and ending an already-active alarm output.

### DISC-023: Let an already-triggered collision alarm finish after disabling

- **Situation:** Collision alarm output can already be active when collision detection is disabled. Stopping new detections and terminating an active output are separate actions.
- **Question:** 如果碰撞警報已經觸發，此時停用碰撞偵測，現有警報輸出要如何處理？
- **Options and tradeoffs:** 立即解除碰撞警報輸出，停止後續碰撞判斷；既有事件紀錄保留。 / 讓已觸發的碰撞警報依原本持續時間結束，只停止後續碰撞判斷；既有事件紀錄保留。
- **User answer:** 2
- **Explicit rationale:** User selected the second option; no additional rationale supplied.
- **Resulting impact:** Add REQ-017, DEC-018 and AC-017. Disabling prevents new collision detections and retriggers while the previously triggered output finishes its existing remaining hold duration; do not clear it early or restart its timer. Preserve event records and independent warning behavior. Refine REQ-008 and OD-005; this policy also applies to disabled state introduced by model Apply or fallback.

### DISC-024: Delete the applied model and preserve collision enable state

- **Situation:** User deletes model A while it is the applied collision method. The runtime must switch away from the deleted model.
- **Question:** 如果使用者刪除目前已套用的模型 A，要如何處理？
- **Options and tradeoffs:** 允許刪除，並自動套用原有碰撞演算法、停用碰撞偵測；網頁提示切換結果。 / 拒絕刪除，提示先選擇並套用其他模型或原有演算法，再刪除 A。
- **User answer:** 選擇1，並自動套用原有碰撞演算法、如果原本啟用碰撞偵測則要維持啟用狀態。
- **Explicit rationale:** User adopts deletion and automatic original-method application but overrides the option's forced disable with preservation of the prior enable state.
- **Resulting impact:** Add REQ-018, DEC-019 and AC-018; refine REQ-006/007/012 and AC-007/012 to distinguish deletion-driven automatic fallback from ordinary model Apply and load-failure fallback. On successful deletion of the applied model, automatically apply the original method and retain the previous collision switch value, including automatic judgment resumption when enabled and ready; warning settings stay independent. REQ-016 still disables on load failure. Persisted selection repair remains open; do not infer a general Save of device settings from deletion.

### DISC-025: Persist replacement selection on deletion and preserve enable state on load failure

- **Situation:** Deleting applied A can leave a saved reference to A. User also explicitly corrects the previous load-failure forced-disable policy.
- **Question:** 若已儲存的模型選擇也是 A，刪除目前套用的 A 時，要同步更新這個儲存值嗎？
- **Options and tradeoffs:** 自動將已儲存的模型選擇改為原有碰撞演算法；其他設定仍依原本 Save 規則。 / 保留手動 Save；若刪除後未 Save 就重開機，依模型載入失敗規則改用原有演算法並停用碰撞偵測。
- **User answer:** 選擇1
- **Explicit rationale:** In the same message user explicitly corrected load failure: 模型載入失敗時，自動套用原有碰撞演算法、如果原本啟用碰撞偵測則要維持啟用狀態。
- **Resulting impact:** Add REQ-019, DEC-020 and AC-019 to repair saved model selection on deletion without saving unrelated settings. Revise REQ-016, DEC-017 and AC-016: load failure now preserves collision enable state, automatically using the valid/ready original method if enabled, and remains disabled if previously disabled. This supersedes the forced-disable portions of DISC-021/022/024; their records remain historical. Refine REQ-007/012/018 and DEC-019 to recognize both automatic-fallback exceptions. The selected option's unchosen disabled-at-boot alternative is obsolete. Load-failure recovery still does not implicitly Save under the existing contract; deletion-specific persistence must not silently broaden it.

### DISC-026: Import stores a model without activating it

- **Situation:** A device may use model A while the user imports another model B, including one requiring a different sampling rate.
- **Question:** 新增匯入一個有效模型後，要立即切換目前使用的碰撞模型嗎？
- **Options and tradeoffs:** 只儲存模型並加入選單，維持目前演算法與開關狀態；使用者選擇並 Apply 後才切換。 / 儲存後立即嘗試套用新模型；通過取樣率等檢查才切換，成功後依一般模型 Apply 規則停用碰撞偵測。
- **User answer:** 1
- **Explicit rationale:** User chose storage/listing without automatic activation; no additional rationale supplied.
- **Resulting impact:** Add REQ-020, DEC-021 and AC-020; clarify REQ-003 and REQ-006. Successful new-model import persists the model and adds its eligible selection entry without changing the applied method or collision/warning enable values. Selecting and Apply is a later explicit operation; import itself is not device-configuration Save. Current sampling-rate mismatch remains an Apply eligibility issue, not automatic activation or catalog exclusion. Replacement/duplicate imports remain a separate catalog policy.

### DISC-027: Confirm same-name replacement and editable export names

- **Situation:** A new artifact can share an existing device model display name while containing different parameters. User chooses confirmation before replacement and requests an editable export name plus a proposed default.
- **Question:** 匯入模型的顯示名稱與裝置內既有模型相同，但參數內容不同時，要如何處理？
- **Options and tradeoffs:** 保留兩個模型，選單加上可區分的標示；目前套用的模型不變。 / 拒絕匯入，提示先修改新模型名稱，再重新匯入。 / 提示是否取代既有模型，使用者確認後才更新；取消則保留舊模型。
- **User answer:** 選擇3，所以軟體在匯出時，要可以輸入名稱。預設名稱是什麼?
- **Explicit rationale:** User explicitly links replacement by name with the ability to enter a model name at export. No default naming formula was selected yet.
- **Resulting impact:** Add REQ-021/022, DEC-022/023 and AC-021/022. Same display name with changed parameters prompts confirmation before replacing; cancellation preserves old artifact. Software export exposes an editable name carried in JSON and used in Web display/replacement matching, separate from filesystem filename. Existing FIR header default is dual_imu_collision_profile_{kernel_id}.h in ProfileExportService.default_filename; this is not a JSON-model-name default. Naming default and active-model replacement lifecycle remain open.

### DISC-028: Stable default model name and separately editable JSON filename

- **Situation:** User chooses default naming option 1 and asks whether the two names can both be entered at export. The surrounding discussion distinguishes embedded model name from filesystem filename.
- **Question:** JSON 模型的預設名稱要採哪一種？兩者都允許匯出前修改。
- **Options and tradeoffs:** 模型類型_取樣率_模型編號，例如 FIR_1000Hz_k001（建議）；重複匯出名稱穩定，同名時提示取代。 / 模型類型_取樣率_匯出日期時間，例如 FIR_1000Hz_20260916_143025；方便區分每次匯出，但通常會新增不同名稱的模型。
- **User answer:** 1。那模型名稱呢?匯出時，同時可以輸入這輛個名稱?
- **Explicit rationale:** User selects option 1 and requests clarification about entering both names. Interpret the two names as model display name and JSON filename based on the immediately preceding discussion.
- **Resulting impact:** Refine REQ-022, DEC-023 and AC-022. Model default is model-type_required-Hz_model-number, with FIR_1000Hz_k001 as illustrative example. Export allows editing both embedded model name and JSON filename. Filename initially defaults to model name plus .json, a routine UI default proposed by the assistant to make the distinction concrete; filename edits do not affect embedded name. Same-name replacement is based on the embedded name, not the file basename. Default naming is resolved; shared name validation and active replacement remain open.

### DISC-029: Replacement of the running model waits for manual Apply

- **Situation:** Same-name import can replace the stored artifact of the model that is currently running. Storage update and execution update must be distinguished.
- **Question:** 如果同名取代的模型正是目前正在使用的模型，確認取代後何時改用新參數？
- **Options and tradeoffs:** 先更新儲存的模型，執行中仍使用舊參數，網頁標示待套用；手動 Apply 後才切換。 / 確認取代後立即嘗試套用新參數；通過相容性檢查才切換，成功後依一般 Apply 規則停用碰撞偵測。
- **User answer:** 1
- **Explicit rationale:** User selects deferred activation after replacement; no additional rationale supplied.
- **Resulting impact:** Add REQ-023, DEC-024 and AC-023 and refine REQ-021/AC-021. Confirmed replacement updates storage while the current runtime continues its old parameter snapshot and existing switch values. Web marks pending Apply and distinguishes stored versus executing versions. Only explicit successful Apply switches runtime, subject to ordinary readiness/rate gates and disabled-after-Apply behavior. Whether pending activation survives a restart requires a separate boot/persistence decision.

### DISC-030: Pending replacement survives reboot without activation

- **Situation:** New same-name parameters can be stored while the old version is still applied; loss of power must not accidentally activate pending parameters.
- **Question:** 同名新版本已儲存但尚未 Apply，且開機設定仍選用這個模型時，重開機後要使用哪個版本？
- **Options and tradeoffs:** 繼續使用舊版本，新版本維持待套用；必須保留可跨重開機恢復的舊版本，直到手動 Apply。 / 載入已儲存的新版本，通過開機相容性檢查後使用；依已儲存的碰撞偵測開關決定是否執行。
- **User answer:** 1
- **Explicit rationale:** User selected retention of the old version across restart until manual Apply.
- **Resulting impact:** Add REQ-024, DEC-025 and AC-024; refine REQ-023. Persist both recoverable old parameters and pending replacement with explicit version state. Boot selecting that model restores its pre-Apply version, leaves replacement pending and honors separately saved device switches. Budget simultaneous old/pending storage and avoid deleting the recoverable old version merely because import succeeds. Power-loss recovery must not promote the pending version; existing validation/failure fallback still applies to actual load failures.

### DISC-031: All model families included; reopen pending-version boot behavior

- **Situation:** Pending Q-024 asks which model families first-release JSON export and device loading cover. In the same reply the user asks whether the pending-version design implies separate import files, parameters and RAM, and explicitly requests re-discussion of Q-023.
- **Question:** 第一版 JSON 匯出與 ESP32 載入，要涵蓋哪些模型種類？
- **Options and tradeoffs:** 全部納入：雙 IMU FIR／Ridge、雙 IMU MLP、單 IMU Ridge；各種類分別定義參數與驗證規則。 / 第一版先支援雙 IMU FIR／Ridge，MLP 與單 IMU Ridge 留待後續版本。
- **User answer:** 1
- **Explicit rationale:** User selected all families and annotated the previous boot-version question with 這個意思，表示你規劃區分成匯入檔案、參數、RAM的意思? and 重新討論. No new boot-version choice was supplied.
- **Resulting impact:** Add REQ-025, DEC-026 and AC-025; resolve first-release family scope while retaining per-family compatibility/resource limits. Reopen REQ-024, DEC-025 and AC-024 and remove their confirmed persistent-old-version mandate until a new answer. REQ-023 still requires old runtime parameters until Apply during the current powered session. Explain that JSON is the exchange artifact, parameters are its model content, persistent storage retains a device representation, and RAM is volatile execution state; three independently stored permanent copies are not decided. Restoring old parameters after power loss requires a durable old version somewhere, not merely RAM. Storage encoding and exact memory layout remain undecided.

### DISC-032: Reboot loads the latest stored replacement

- **Situation:** User reopened the former cross-reboot old-version retention choice after clarification of JSON parameters, persistent Flash and volatile RAM. Q-025 now offers explicit storage/runtime behavior.
- **Question:** 重新討論：同名新參數已匯入但未 Apply，重開機仍選用這個模型時，你希望哪種行為？
- **Options and tradeoffs:** 重開機仍用舊參數：Flash 保留舊版及待套用新版，直到手動 Apply；需要較多儲存空間。 / 重開機載入新參數：匯入更新 Flash，當次執行的 RAM 舊參數可用到 Apply 或重開機；不要求為待套用狀態跨重開機保留舊版。
- **User answer:** 2
- **Explicit rationale:** User selects loading new stored parameters on restart, replacing the prior old-version-across-reboot choice.
- **Resulting impact:** Resolve reopened REQ-024, DEC-025 and AC-024 and reconcile REQ-021/023. Confirmed import updates persistent model content while the current runtime stays on its old snapshot until explicit Apply or reboot. Boot uses saved method selection and independently saved switches; when that selection names the replaced model, load its latest valid stored parameters after compatibility checks. No permanent old/pending pair is mandated merely for deferred activation. Transaction safety/temporary update overhead remains required and is not eliminated. JSON versus binary persistent representation remains undecided. Previous DISC-030/031 remain historical, not current boot policy.

### DISC-033: Preserve verified numerical precision and explain device admission

- **Situation:** Q-026 concerns numerical precision for ESP32 model deployment. User chooses preserving verified model precision and asks how unsupported devices or insufficient resources are detected.
- **Question:** 模型部署到 ESP32 時，數值精度要採哪種規則？
- **Options and tradeoffs:** 沿用該模型已驗證的 float32 或 float64，不自動降精度；裝置不支援或資源不足時明確拒絕。 / 部署統一使用 float32；原本為 float64 的模型須先轉換並重新驗證，通過後才可匯出。
- **User answer:** 1
- **Explicit rationale:** User additionally asks 如何判斷? about unsupported device/resource rejection. No resource thresholds or timing-admission policy have been selected by that question.
- **Resulting impact:** Add REQ-026, DEC-027 and AC-026. Preserve declared verified float32/float64 semantics across export/load without silent narrowing; mismatch with device capability must be rejected explicitly. Explain proposed admission layers: schema/family/operator/numeric capability, derived shape and workspace requirements, current persistent-storage and eligible-memory availability/reservation, and target-specific execution-time evidence. Existing software ProfileExportService validates numeric type and parameter shapes; firmware Web adapter reports internal free/minimum/largest heap and LittleFS usage. These are building blocks, not implemented model admission or proof of timing/RAM sufficiency. Precise support bounds, reserves and timing evidence remain OD-002/004/005; never assert JSON byte size or a one-shot allocation/timing check proves long-run resource adequacy.

### DISC-034: User judges deployment suitability; remove automatic resource admission

- **Situation:** Q-027 proposes prevalidated support envelopes and load-time capability/Flash/RAM checks as automatic admission criteria. User rejects automatic judgment and assigns suitability judgment to the user.
- **Question:** 第一版是否採用「先實測建立裝置支援範圍，每次載入再檢查能力、Flash 與 RAM；超出已驗證範圍就拒絕並說明原因」？
- **Options and tradeoffs:** Open-text proposal; no authored options. Proposed automatic admission would limit deployment to prevalidated bounds; user instead chooses operator judgment.
- **User answer:** 我認為不需要自動判斷，這是使用者要判斷的
- **Explicit rationale:** User explicitly assigns assessment to the user and annotates 裝置不支援或資源不足時明確拒絕. This supersedes earlier automatic suitability/resource rejection language.
- **Resulting impact:** Add REQ-027, DEC-028 and AC-027; revise REQ-025/026, DEC-027 and AC-025/026. Remove model admission based on estimated memory, predicted execution time, tested support envelopes or device-suitability scoring. Preserve chosen numeric type with no automatic downgrade. Actual parse/load/allocation/write failures remain ordinary operation errors and must not be reported as success; retain existing old-state/fallback rules according to the failure stage. This does not reopen explicit sampling-rate equality checks under REQ-013, basic artifact integrity or existing hide-unloadable behavior. Runtime test evidence is engineering evidence, not a whitelist blocking user models. Do not introduce an extra suitability confirmation workflow as a substitute.

### DISC-035: Store imported JSON in device Flash

- **Situation:** Exchange format is already JSON, but device persistent representation remained undecided. Q-028 compares storing JSON with conversion to a separate binary parameter format.
- **Question:** 模型在 ESP32 的 Flash 中，要以哪種形式保存？
- **Options and tradeoffs:** 保存匯入的 JSON，套用或開機載入時再解析成執行參數（建議）。 / 匯入時轉成二進位參數格式保存，套用或開機時載入；需另外定義裝置儲存格式。
- **User answer:** 1
- **Explicit rationale:** User selects persistent JSON; no additional rationale supplied.
- **Resulting impact:** Add REQ-028, DEC-029 and AC-028; refine REQ-004/AC-004. Persist imported model content as JSON in Flash, parse it into execution parameters at Apply or boot, and retain precision under REQ-026. Do not introduce a separate binary model-storage format. Import-time validation remains compatible with later activation parsing. Preserve storage/runtime separation, same-name replacement confirmation, boot-latest behavior, actual operation-error handling, and user-owned resource suitability. Existing 1024-byte general-configuration envelope is not a model JSON capacity limit.

### DISC-036: Fixed single-IMU source from the exported training configuration

- **Situation:** Single-IMU training records the source as internal or external. Deployment must decide whether the device can override this source.
- **Question:** 單 IMU 模型部署後，輸入來源要固定沿用訓練設定，還是允許在裝置網頁改選？
- **Options and tradeoffs:** JSON 帶入訓練時選定的 internal／external 來源，裝置固定沿用；要換來源就重新匯出對應模型。 / JSON 保留訓練來源供參考，但裝置網頁允許另選 internal／external；由使用者判斷更換來源後是否適用。
- **User answer:** 1
- **Explicit rationale:** User selects fixed input-source semantics from the trained/exported model.
- **Resulting impact:** Add REQ-029, DEC-030 and AC-029. Software serializes the selected source and firmware executes that source without a Web override or silent substitution. Changing source requires exporting the corresponding model configuration; editing only the filename/display name does not change source. Input source is model execution metadata, not acceleration-warning configuration. Actual unavailable-input behavior must not be disguised as successful inference on the other sensor.

### DISC-037: Base threshold from JSON multiplied by device sensitivity setting

- **Situation:** Q-030 asks whether imported-model thresholds can be adjusted on the device. User selects adjustment and specifies a base-times-multiplier contract spanning physical knob, Web and CANopen.
- **Question:** 匯入模型的碰撞判斷門檻，要固定使用 JSON 內的值，還是允許在装置網頁調整？
- **Options and tradeoffs:** 固定使用 JSON 內的模型門檻，網頁只顯示；要調整就由軟體重新匯出模型。 / JSON 提供初始門檻，裝置網頁可另外調整各模型的門檻，並依 Apply／Save 規則套用及儲存。
- **User answer:** 選擇2，我在想基板上的旋鈕跟web、及CANOpen設定的值，感覺要使用JSON 提供初始門檻  ，然後基板上的旋鈕跟web、及CANOpen設定的值是倍率。最後程式的threshold就是JSON 提供初始門檻 乘倍率
- **Explicit rationale:** User defines final threshold as JSON initial threshold multiplied by the multiplier configured through knob/Web/CANopen, rather than direct edits of the model threshold.
- **Resulting impact:** Add REQ-030, DEC-031 and AC-030. Keep exported baseline threshold as model content; device controls a dimensionless multiplier, effective threshold equals baseline times effective multiplier. Do not rewrite the baseline or multiply three independent control values. Device Web changes retain Apply/Save semantics. Preserve independent warning configuration. Existing firmware source uses collision_alarm_threshold_g shared by Web/CANopen and zero selects physical selector; this legacy sentinel is not a confirmed zero multiplier. Source arbitration, knob-position mapping/range/default, cross-model multiplier ownership, boot persistence and legacy-mode/CAN object compatibility remain to be resolved before implementation.

### DISC-038: Last effective multiplier operation wins; preserve legacy control semantics

- **Situation:** Three control paths can set the effective imported-model multiplier. User selects last-operation-wins and clarifies that zero selects the knob only in the original collision algorithm.
- **Question:** 旋鈕、Web 與 CANopen 都能調整倍率時，要如何決定目前生效的倍率？
- **Options and tradeoffs:** 區分控制來源：旋鈕模式使用旋鈕倍率；軟體模式由 Web／CANopen 設定共同倍率，旋鈕不覆蓋它（建議）。 / 最後一次生效操作為準：旋鈕實際轉動、Web Apply 或 CANopen 有效設定都更新同一倍率，後者覆蓋前者。
- **User answer:** 2
- **Explicit rationale:** User additionally clarifies 這個是原本碰撞判斷的設定方式 about zero selecting the physical knob. This legacy behavior must not be conflated with imported-model multiplier authority.
- **Resulting impact:** Add REQ-031, DEC-032 and AC-031; refine REQ-030 and OD-007. All three paths update one effective multiplier in effective-operation order, without selecting a knob/software mode for imported models. Only actual knob changes are control updates; polling an unchanged knob cannot erase Web/CANopen changes. Web Draft is not yet an effective operation. Preserve the original collision algorithm's existing zero-means-knob semantics, separately from imported-model multiplier rules. Default/range, persistence, per-model/global multiplier ownership and exact CANopen representation remain open.

### DISC-039: One shared multiplier for all imported models

- **Situation:** A and B can have different JSON baseline thresholds. Q-032 asks whether switching models restores separate multiplier values or retains one shared value.
- **Question:** 倍率要由各模型分別記住，還是所有匯入模型共用一個？
- **Options and tradeoffs:** 各模型分別記住倍率，切換時恢復該模型的倍率；旋鈕／Web／CANopen 只更新目前模型的倍率。 / 所有匯入模型共用一個倍率，切換模型仍沿用最近設定的倍率；只有 JSON 基準門檻隨模型改變。
- **User answer:** 2
- **Explicit rationale:** User chooses a shared multiplier across imported models.
- **Resulting impact:** Add REQ-032, DEC-033 and AC-032; refine REQ-030 and OD-007. Maintain one device-level imported-model multiplier, not per-model tuning records. Changing selected imported model retains the effective multiplier and recomputes threshold from the newly applied baseline. Knob/Web/CANopen still use last-effective-operation arbitration. Model JSON remains the source of baseline only, and original-algorithm controls remain separate. Boot value/default and knob mapping still require resolution.

### DISC-040: Restore saved multiplier on boot

- **Situation:** Saved multiplier and physical knob position can disagree at startup. The first knob read must be distinguished from a deliberate change.
- **Question:** 重開機時，共用倍率要使用已儲存的值，還是旋鈕目前位置？
- **Options and tradeoffs:** 恢復上次 Save 的倍率；開機讀取旋鈕只建立位置基準，之後真的轉動才更新倍率。 / 以旋鈕目前位置決定開機倍率；開機後仍由旋鈕、Web、CANopen 最後生效的操作更新。
- **User answer:** 1
- **Explicit rationale:** User chooses restoring saved multiplier and treating initial knob observation only as the change-detection baseline.
- **Resulting impact:** Add REQ-033, DEC-034 and AC-033; resolve saved-value boot precedence in REQ-030/032 and OD-007. Save persists the applied shared multiplier; startup restores it without substituting current knob position. Actual later knob movement competes with effective Web/CANopen updates under last-operation-wins. Unsaved runtime multiplier updates do not replace the previously saved boot value. Defaults for missing/new configuration and numeric mapping/range remain open.

### DISC-041: Knob multiplier starts at 0.5 with 0.25 steps

- **Situation:** Physical selector has 16 positions. User specifies a custom linear multiplier sequence rather than either proposed range. Existing SPEC-0045 orders the positions as 1..15 followed by raw selector 0 interpreted as position 16.
- **Question:** 新模型的旋鈕 16 個位置，要採哪組倍率？也可以直接指定其他對照表。
- **Options and tradeoffs:** 0.25～4.00，每段增加 0.25；調整範圍較大，步幅較粗。 / 0.50～2.00，每段增加 0.10；調整範圍較小，步幅較細。
- **User answer:** 0.5開始，每段增加0.25
- **Explicit rationale:** User explicitly specifies starting multiplier 0.5 and increment 0.25; 16 positions imply endpoint 4.25. No additional rationale supplied.
- **Resulting impact:** Add REQ-034, DEC-035 and AC-034. Use m(n)=0.5+(n-1)*0.25 for positions 1..16; preserve the existing selector-numbering convention n=raw 1..15, n=16 for raw 0, made explicit to the user. Thus raw 1 maps to 0.5, raw 3 to 1.0, raw F to 4.0 and raw 0 to 4.25. This applies only to imported-model multiplier control and does not alter original algorithm calibration mapping. Physical knob range does not automatically constrain Web/CANopen input granularity/range; those remain open along with missing/default value and exact CAN encoding.

### DISC-042: Remote multiplier is not limited to physical knob values

- **Situation:** Physical knob maps to 16 discrete values from 0.50 to 4.25. Remote controls need their own numeric input contract.
- **Question:** Web／CANopen 設定倍率時，也要限制成旋鈕的 16 個值嗎？
- **Options and tradeoffs:** 與旋鈕一致：只接受 0.50～4.25、每隔 0.25 的 16 個倍率。 / 允許任意可表示的有限正倍率，不限制為 0.25 步進，也不限定旋鈕範圍；旋鈕仍使用固定 16 段。
- **User answer:** 2
- **Explicit rationale:** User chooses unrestricted representable finite positive remote multipliers, independent of the knob's range and step.
- **Resulting impact:** Add REQ-035, DEC-036 and AC-035; refine REQ-030/034 and OD-007. Web/CANopen accept values such as 1.1 and 5 without rounding/clamping to knob detents. Zero, negative, NaN/infinity and unrepresentable values are outside the chosen numeric contract, not deployment-resource admission. Physical knob updates still set their fixed mapped values only on a real change. Exact CANopen object/type mapping and missing/default value remain open; existing ShockAlarmThreshold at 0x2007:00 is REAL32 and currently controls the original threshold, so do not silently repurpose it.

### DISC-043: Same setting field interpreted by the collision algorithm

- **Situation:** The proposed CANopen question introduced a separate multiplier object, but the user clarifies that the intended design already uses one field interpreted by the selected collision algorithm.
- **Question:** CANopen 的新模型倍率，要使用獨立物件，還是沿用原有碰撞門檻物件？
- **Options and tradeoffs:** 新增獨立倍率物件，0x2007:00 保持原有門檻語意；控制端需新增倍率物件的讀寫（建議）。 / 沿用 0x2007:00：原有演算法時代表原門檻，匯入模型時代表倍率；控制端需依目前演算法解讀與寫入。
- **User answer:** 為什麼會有這個問題?我的認知是都是同個欄位，只是對應不同碰撞演算法而有不同算法。
- **Explicit rationale:** The user expects one common setting field, with the computation depending on the collision algorithm. This is explicit adoption of shared-field behavior, not an unanswered factual query.
- **Resulting impact:** Add REQ-036, DEC-037 and AC-036. Resolve CANopen object/type mapping by retaining existing 0x2007:00 REAL32. Distinct legacy versus multiplier semantics do not require separate transport fields. Preserve original zero-means-knob behavior only in original mode; model mode uses finite positive multiplier. Keep JSON baseline, independent acceleration warning, and last-effective-operation arbitration unchanged. Missing/default multiplier remains open.

### DISC-044: Default multiplier is neutral

- **Situation:** Saved multiplier restoration is settled, but first-use and missing-field initialization need a value.
- **Question:** 裝置尚未儲存過模型倍率時，預設使用 1.0 倍（直接使用 JSON 初始門檻），是否符合你的預期？
- **Options and tradeoffs:** Open-text confirmation of a neutral 1.0 default; user may specify another value. A neutral value preserves the exported baseline without scaling.
- **User answer:** 符合
- **Explicit rationale:** User confirms the proposed 1.0 default without additional conditions.
- **Resulting impact:** Add REQ-037, DEC-038 and AC-037. Default only when no saved multiplier exists; keep valid saved values and initial-knob baseline behavior. Exact value continuity when switching between original and imported algorithms remains to be reconciled with the newly confirmed shared field under REQ-036; switching among imported models already retains one common multiplier under REQ-032.

### DISC-045: Retain numeric value across algorithm switches

- **Situation:** The shared field has algorithm-dependent meaning. The user asked why the original algorithm had a multiplier; clarification established that original example 2 is its legacy setting, not a multiplier. The remaining question concerns numeric continuity.
- **Question:** 假設原有演算法的欄位目前是 2，而上次模型倍率是 1.5；切換到匯入模型時，這個欄位要顯示哪個值？
- **Options and tradeoffs:** 恢復模型倍率 1.5：共用同一欄位，但分別記住原有演算法設定與所有匯入模型共用的倍率；沒有舊倍率時用 1.0。 / 保留欄位數字 2，直接改成 2 倍：切換演算法不換數字；原值若是模型不接受的 0 等數值，需另定處理方式。
- **User answer:** 2
- **Explicit rationale:** User selects value retention after the legacy-setting versus multiplier distinction was explained; no additional rationale stated.
- **Resulting impact:** Add REQ-038, DEC-039 and AC-038; refine REQ-032/033/036/037 to remove any implication of separate remembered values for original and imported algorithms. Retain existing mode-specific computation, saved-value restoration, no-implicit-Save behavior and neutral default when initialization is needed. Default 1.0 does not override a retained valid field merely because an imported model is selected. OD-007 now concerns handling a retained value invalid for the destination, notably legacy zero on entry to model mode.

### DISC-046: Convert legacy zero on entry into model mode

- **Situation:** Retain the common numeric value across algorithm switches, except original zero is a knob sentinel and is not a positive model multiplier.
- **Question:** 原有演算法的設定值是 0（使用旋鈕）時，切換到匯入模型要如何處理？
- **Options and tradeoffs:** 自動改成 1.0 倍，並在 Web 提示已調整；可直接完成切換。 / 提示使用者輸入正倍率後才能 Apply；修改前維持原有演算法與設定。
- **User answer:** 1
- **Explicit rationale:** User selects automatic neutral conversion with Web notice; no additional rationale stated.
- **Resulting impact:** Add REQ-039, DEC-040 and AC-039. Refine REQ-038 with the specific zero-transition exception; retain direct model-mode zero rejection, valid positive numeric retention, normal Apply behavior and explicit Save. OD-007 numeric continuity/default/control decisions are resolved for the confirmed valid original-setting domain; verify legacy domain against source before final consolidation.

### DISC-047: Retain software qualification before JSON export

- **Situation:** Current ProfileExportService._validate rejects unqualified Profiles; earlier resource-suitability decisions did not decide whether to retain this model-quality gate for the new JSON path.
- **Question:** 新 JSON 匯出是否只允許通過軟體驗證的模型？
- **Options and tradeoffs:** 保留現有限制：只有通過軟體驗證的模型才能匯出；未通過者需先調整或重新訓練。 / 只要模型參數完整且格式有效，就允許匯出；明確標示驗證狀態，由使用者決定是否部署。
- **User answer:** 1
- **Explicit rationale:** User selects retaining the existing software qualification requirement; no additional rationale stated.
- **Resulting impact:** Add REQ-040, DEC-041 and AC-040. Extend software qualification admission consistently to the JSON exports of all three model families, preserving applicable frozen-model validation. Keep REQ-027 resource suitability user-controlled and do not infer that software test qualification proves target RAM or timing. No on-device replay of the training dataset is required. Existing src/dual_imu_collision_studio/domain/profile_export/service.py _validate is factual evidence for the current gate, not evidence of new implementation completion.

### DISC-048: Model names distinguish letter case

- **Situation:** Same-name replacement is confirmed, while name matching still needs case sensitivity to distinguish catalog identities.
- **Question:** 匯入時，模型名稱只有英文大小寫不同，要視為同名嗎？例如 Model_A 與 model_a。
- **Options and tradeoffs:** 視為同名：參數不同時提示是否替換，不新增另一個選項；可避免僅大小寫不同的名稱混淆。 / 視為不同名：各自保留並顯示兩個選項；可以用大小寫區分模型，但選擇時需留意。
- **User answer:** 2
- **Explicit rationale:** User selects distinct names and independent catalog entries for letter-case differences; no further rationale stated.
- **Resulting impact:** Add REQ-041, DEC-042 and AC-041; refine REQ-021/022 matching to case-sensitive embedded names. JSON filenames and case-insensitive desktop filesystem behavior must not merge device model identities. Other shared format/structural details remain technical consolidation work.

### DISC-049: Deploy already-filtered single-IMU models

- **Situation:** SingleImuSettings distinguishes already_filtered from application_filtered. The former bypasses application filtering and has no external-filter coefficients for the exporter to transfer.
- **Question:** 單 IMU 模型若使用「已濾波資料」訓練，通過軟體驗證後，是否仍允許匯出部署？
- **Options and tradeoffs:** 允許：沿用不追加模型濾波的方式，由使用者確保裝置輸入與訓練資料的前處理一致；保留此模式的部署能力。 / 不允許此模式匯出：只部署由軟體保存完整濾波係數的單 IMU 模型；既有已濾波資料模型需改用該流程重新訓練與驗證。
- **User answer:** 1
- **Explicit rationale:** User selects deployment with unchanged model-filter bypass and user responsibility for matching input preprocessing.
- **Resulting impact:** Add REQ-042, DEC-043 and AC-042. Preserve both source modes from SPEC-0030: already_filtered bypasses extra application filtering/warmup but still needs strict-past history; application_filtered exports adopted SOS and warmup. Do not introduce an external-filter reproduction gate or silently fabricate coefficients. src/dual_imu_collision_studio/domain/learning/preprocessing.py and SPEC-0030 REQ-026/033 provide the existing mode semantics.

### DISC-050: Suspend collision processing to reduce CPU use

- **Situation:** Collision disable semantics had suppressed new detections but had not determined whether model-specific preprocessing/history should keep running.
- **Question:** 取消勾選碰撞偵測後，已選模型的濾波與歷史資料要繼續更新嗎？
- **Options and tradeoffs:** 繼續更新，只停止碰撞判斷（建議）：仍有前處理負擔，但重新啟用時，資料已足夠便可開始判斷，不因停用而重新暖機。 / 暫停模型前處理：減少停用期間的運算；重新啟用時清除舊狀態，重新暖機並累積足夠歷史資料後才開始判斷。
- **User answer:** 採用2，我的想法是可以減少一些處理，如果不需要碰撞的功能。也不會佔用CPU資源
- **Explicit rationale:** The user wants to avoid unnecessary collision processing/CPU work when that function is unused. The selected annotation repeats option 2; no separate policy correction is introduced.
- **Resulting impact:** Add REQ-043, DEC-044 and AC-043. Model-specific filters/history/inference/decisions stop while disabled. Re-enable resets transient state and waits for applicable warmup/fresh history; already_filtered keeps its no-extra-filter-warmup semantics. Preserve independent acquisition, telemetry, warning and existing-alarm timing. Clarify that eliminating collision processing does not mean zero whole-device CPU or automatic RAM unloading. Normal model Apply leaves this processing suspended until collision is explicitly enabled; enabled automatic fallback still initializes a ready original detector before judgment.

### DISC-051: Continue UI and architecture design

- **Situation:** Functional and shared artifact contracts were materialized, but the user asks whether UI and architecture still need discussion; detailed screen composition and concrete architecture ownership were not completed by functional SPEC consolidation.
- **Question:** UI、程式架構還有需要討論的?
- **Options and tradeoffs:** The response identified remaining desktop/Web UI layout and software/firmware architecture design, and recommended UI sketches before concrete module/state ownership. No numeric alternatives were presented.
- **User answer:** 繼續討論
- **Explicit rationale:** User requests continued design discussion; no product implementation authorization or reversal of established functional rules is expressed.
- **Resulting impact:** Reopen SPEC-0039 and SPEC-0057 in place and add OD-008/009 to refine the UI realization and design of REQ-002, REQ-003, REQ-009, REQ-014 and REQ-048. Preserve all accepted functional requirements. First discuss firmware Web model-management placement; desktop and firmware ownership remain separate, with shared discussion context mirrored. Missing verification matrix remains an implementation planning prerequisite, not a new user-facing product choice.

### DISC-052: Dedicated Web model-management page

- **Situation:** Current Web has Device Configuration for operational settings; import persists artifacts separately from Apply and Save. A UI location decision is needed for model management.
- **Question:** env_sensing Web 的模型匯入、清單、替換與刪除，要放在哪裡？
- **Options and tradeoffs:** 新增「碰撞模型」頁（建議）：集中管理模型檔案；Device Configuration 保留模型選擇、倍率與兩個開關。匯入與 Apply 的用途較清楚，但管理後需切頁設定。 / 全部放在 Device Configuration：新增模型管理區塊，匯入後可在同頁選擇與 Apply；操作集中，但頁面較長，需要明確區分匯入、Apply 與 Save。
- **User answer:** 1
- **Explicit rationale:** User adopts the dedicated page option; no additional rationale stated.
- **Resulting impact:** Add REQ-050, DEC-046 and AC-050. Resolve model-management placement portion of OD-008 while preserving established import/Apply/Save and deletion/fallback rules. Firmware owns the page implementation; software records counterpart workflow only. Remaining UI presentation and architecture responsibilities remain open.

### DISC-053: Hide original-only configuration fields

- **Situation:** Original vector/individual-axis and envelope settings do not configure imported-model inference; the common threshold/multiplier field continues to apply with method-dependent meaning.
- **Question:** 在 Device Configuration 選擇匯入模型時，原有演算法專用欄位要如何顯示？例如向量／分軸模式、Envelope samples。
- **Options and tradeoffs:** 隱藏不適用的欄位（建議）：畫面只呈現目前方法需要的設定；原設定保留，切回原有演算法時再顯示。 / 保留但灰化：仍可查看原設定，標示「僅原有演算法使用」並禁止編輯；畫面資訊較多。
- **User answer:** 1
- **Explicit rationale:** User adopts hiding inapplicable fields while retaining their settings; no additional rationale stated.
- **Resulting impact:** Add REQ-051, DEC-047 and AC-051. Visibility follows the draft selection as part of the existing Draft/Apply/Save interaction; it does not silently activate a different algorithm or clear hidden settings. The shared setting and independent warning controls stay visible. Firmware owns this Web behavior; the software SPEC mirrors the shared operation context. Continue remaining UI and architecture discussion under OD-008/009.

### DISC-054: Per-model export dialogs and Web parameter visibility question

- **Situation:** Model name and filename are independently editable; one JSON per model is established. The UI must support multiple selected models without conflating their names and destinations.
- **Question:** 桌面軟體一次匯出多個模型時，要如何編輯各模型的名稱與 JSON 檔名？
- **Options and tradeoffs:** 同一視窗用表格逐列編輯（建議）：每列一個模型，列出類型、取樣率、模型名稱與檔名；選一個輸出資料夾後批次匯出，方便一起核對。 / 逐個模型開啟匯出視窗：每次編輯一個模型名稱與檔名，並選擇儲存位置；可分別存到不同資料夾，但多個模型需重複操作。
- **User answer:** 選擇2，我在想web有需要看這些參數嗎
- **Explicit rationale:** User selects individual export dialogs and asks whether Web should expose these parameters. The question is not approval of a Web display/editing policy.
- **Resulting impact:** Add REQ-052, DEC-048 and AC-052 for the selected desktop workflow. Preserve the Web visibility question within OD-008: explain operational model/name/rate/threshold summaries versus full weights/bias/filter coefficients; do not infer permission to edit frozen model coefficients on-device. Existing required runtime/model metadata remains visible per prior requirements.

### DISC-055: Summary only in Device Configuration

- **Situation:** Q-047 asks whether Web should display summaries only or also full coefficients. The user asks whether summaries can be confined to Device Configuration and then limits placement accordingly.
- **Question:** Web 的模型參數要顯示到什麼程度？
- **Options and tradeoffs:** 只顯示模型摘要與運作設定（建議）：名稱、類型、取樣率、輸入來源、版本／狀態及門檻資訊；不展開大量權重與係數，日常操作較清楚。 / 摘要之外，提供「完整參數」唯讀詳情：需要時展開權重、bias、濾波係數等，便於核對與除錯，但增加畫面及資料載入量。
- **User answer:** 先只要在**Device Configuration**內顯示摘要就可以了
- **Explicit rationale:** The user explicitly requests summary display only in Device Configuration for now. No full-coefficient viewer or additional summary placement is requested.
- **Resulting impact:** Add REQ-053, DEC-049 and AC-053. Resolve summary/detail scope and placement within OD-008. Preserve REQ-050 dedicated model management, shared numeric settings and accepted Apply/Save semantics. This decision does not authorize product changes or cancel the remaining architecture discussion.

### DISC-056: Complete collision algorithm callback

- **Situation:** User proposes callback dispatch inside collision_detector_.Process while retaining acceleration_warning_.Process independently. Discussion compares a complete algorithm callback with prediction-only callbacks.
- **Question:** 是否採用方案 1，讓 callback 執行完整碰撞演算法，並回傳統一的判斷結果？
- **Options and tradeoffs:** 1. 完整演算法（建議）：callback 負責各自需要的前處理、推論、分數與碰撞判斷；Process 呼叫目前選中的 callback，接收共同結果。 / 2. 只有模型推論：callback 計算預測值；Process 負責前處理、殘差、門檻及碰撞判斷。
- **User answer:** 方案1
- **Explicit rationale:** User adopts option 1; no additional rationale was supplied. The preceding proposal preserves separate original and model-specific calculation semantics.
- **Resulting impact:** Add REQ-054, DEC-050 and AC-054. Refine OD-009 with a complete synchronous algorithm callback boundary. Detailed result/type/state ownership remains design work; no product implementation or new task/core allocation is authorized.

### DISC-057: Boolean-only callback result

- **Situation:** After adopting a complete-algorithm callback, the assistant proposed exposing validity/readiness, trigger and source timing in the common result. User rejects this additional return information.
- **Question:** Assistant proposed a common result including validity, collision trigger and data time/sequence; this was not an accepted requirement.
- **Options and tradeoffs:** Proposed structured result would expose readiness; user instead requires only true/false with warm-up handled inside each algorithm.
- **User answer:** 仍只回傳`true／false`  ，原本碰撞演算法也是有暖機。
- **Explicit rationale:** The original collision algorithm already has warm-up; user wants the callback return to remain boolean.
- **Resulting impact:** Add REQ-055, DEC-051 and AC-055; clarify REQ-054 and DEC-050 common result as bool. Reject the unaccepted structured-result proposal, preserve REQ-017 alarm hold and REQ-043 internal reset/warm-up. No product changes authorized.

### DISC-058: One common collision callback invocation site

- **Situation:** Q-048 proposed separating native/single-source invocation from paired dual-source invocation. User instead requests moving the original collision callback location so all algorithms execute callbacks at the same location. Assistant clarifies a common post-input-preparation entry accepting available single-source or complete paired data, with private algorithm readiness and bool return.
- **Question:** 雙 IMU 模型的資料配對要放在哪裡？ Clarifying question after user correction: 這樣是否符合你的意思：所有演算法共用同一個 callback 呼叫位置，但不要求每次都必須取得完整雙 IMU 配對？
- **Options and tradeoffs:** Original Q-048 options: 1. 沿用既有配對結果，再呼叫雙 IMU 模型 callback（建議）；原有演算法與單 IMU 模型維持逐筆處理，需驗證配對語意符合訓練資料。 / 2. 把兩顆 IMU 的逐筆資料交給模型 callback，由模型內部管理配對；可以獨立定義配對規則，但會多一套配對狀態與驗證工作。 User corrects this framing to a single common invocation site; neither original option is adopted as written.
- **User answer:** 採用
- **Explicit rationale:** User wants the original algorithm and every model to execute callbacks at the same location, and accepts that complete dual-IMU input need not be present for every invocation.
- **Resulting impact:** Resolve Q-048 by the user's correction and adoption, add REQ-056, DEC-052 and AC-056. Preserve REQ-054 complete-algorithm callbacks and REQ-055 bool-only return. OD-009 still covers detailed ownership, input contract and execution design. No product implementation or scheduling change is authorized.

### DISC-059: Separate initialization, reset and execution

- **Situation:** After adopting a common callback invocation site, discussion separates algorithm lifecycle from per-sample execution and explains switching between two MLP artifacts sharing one implementation.
- **Question:** Adopt distinct initialize, reset and bool execute operations, with common family code and selected model parameters?
- **Options and tradeoffs:** Initialize prepares loaded parameters and working storage; reset clears private runtime but retains parameters; execute performs collision computation and returns bool. Same-family artifacts share code rather than generating one callback implementation per imported file.
- **User answer:** 採用，繼續討論不要停下
- **Explicit rationale:** User adopts the proposed lifecycle division and requests continued discussion; no additional rationale supplied.
- **Resulting impact:** Add REQ-057, DEC-053 and AC-057, refining REQ-054 through REQ-056. Preserve existing switch/fallback rules and keep OD-009 detailed ownership and interface design open. No product implementation is authorized.

### DISC-060: Single-score trigger and state-preserving multiplier updates

- **Situation:** Q-049 used an illustrative three-consecutive-score trigger and asked whether multiplier changes clear or retain pending confirmation counts. User corrects the premise to one above-threshold score and chooses option 2.
- **Question:** 只調整模型倍率、沒有切換模型時，尚未觸發的連續超標計數要如何處理？
- **Options and tradeoffs:** 1. 清除尚未觸發的連續超標計數（建議）；保留濾波與歷史資料，不重新暖機，後續依新門檻重新累積。 / 2. 保留連續超標計數；保留濾波與歷史資料，不重新暖機，下一筆直接用新門檻接續判斷。
- **User answer:** 2
- **Explicit rationale:** Annotation correction: score超過門檻一筆就觸發. Therefore the consecutive-count premise is inapplicable; option 2 retains existing runtime and applies the new threshold on the next evaluation.
- **Resulting impact:** Resolve Q-049; add REQ-058, DEC-054 and AC-058. Reconcile shared detector/export/reference wording to single-sample triggering, preserve prior warm-up, bool return, release/re-arm and output-hold behavior. No product implementation authorized.

### DISC-061: Common setting authority and per-computation snapshot

- **Situation:** After agreeing single-score triggering and state-preserving multiplier changes, discussion proposes supplying the common setting through collision processing instead of reading knob/Web/CANopen in the callback.
- **Question:** Adopt a common device setting updated by knob/Web/CANopen, fixed for each collision computation, with updates during computation effective next time?
- **Options and tradeoffs:** Use the existing setting authority and per-computation snapshot; preserve original threshold semantics versus imported-model baseline times multiplier. Avoid direct callback access to control-source adapters and mixed thresholds within one computation.
- **User answer:** 採用
- **Explicit rationale:** User adopts the proposal; no additional rationale supplied.
- **Resulting impact:** Add REQ-059, DEC-055 and AC-059, refining the common-field/arbitration and multiplier-update contracts. No new per-source settings or implicit Save; no product implementation authorized.

### DISC-062: Algorithm-owned private runtime state

- **Situation:** User requests explicit options after the assistant described a proposed state ownership division without choices. Assistant presents local algorithm ownership versus centralized CollisionDetector ownership.
- **Question:** 濾波器、歷史資料與暖機狀態由誰管理？
- **Options and tradeoffs:** 1. 各演算法管理自己的狀態（建議）：外層只呼叫初始化、重設與執行；新增類型主要修改該演算法。 / 2. 由 CollisionDetector 集中管理各演算法狀態：callback 接收對應狀態並更新；CollisionDetector 必須知道每種演算法的資料，新增類型也要修改它。
- **User answer:** 1
- **Explicit rationale:** User selects option 1; no additional rationale supplied. Subsequent unselected proposals remain proposals.
- **Resulting impact:** Add REQ-060, DEC-056 and AC-060, refining REQ-057 lifecycle ownership without changing the selected common entry or bool return. Detailed interface design remains within OD-009. No product implementation authorized.

### DISC-063: Function-pointer operation table

- **Situation:** Following algorithm-owned private runtime, Q-050 compares explicit lifecycle callback tables against a C++ virtual interface.
- **Question:** 初始化、重設與執行介面，要採用哪種寫法？
- **Options and tradeoffs:** 1. 函式指標組（建議）：提供 initialize、reset、process 三個 callback，搭配不透明的實例識別；符合你提出的 callback 方式，不需類別繼承，但要確保函式與實例正確配對。 / 2. C++ 共用介面：各演算法實作 initialize、reset、process，由 CollisionDetector 透過介面呼叫；型別檢查較直接，但需採用虛擬函式與類別繼承。
- **User answer:** 1
- **Explicit rationale:** User selects option 1; no additional rationale supplied.
- **Resulting impact:** Resolve Q-050; add REQ-061, DEC-057 and AC-061, refining lifecycle and private state contracts. Detailed type ownership and instance lifetime remain within OD-009; no product implementation authorized.

### DISC-064: No inactive-model RAM cache

- **Situation:** Q-051 compares keeping only the current parsed model against additionally caching the previous model parameters. User selects no cache and then explains the RAM constraint.
- **Question:** 切換模型完成後，RAM 是否保留上一個模型的參數快取？
- **Options and tradeoffs:** 1. 不保留（建議）：穩定運作時只保留目前模型的已解析參數與運算狀態；切換回其他模型時重新讀取其 Flash JSON。 / 2. 額外保留上一個模型的參數快取：切回且儲存版本未變時可省去 JSON 讀取與解析，但增加 RAM 使用與快取管理；仍須重新初始化及暖機。
- **User answer:** 1
- **Explicit rationale:** Follow-up user message: 目前RAM已經很緊繃了. Treat this as a design constraint, not a measured remaining-byte budget.
- **Resulting impact:** Resolve Q-051; add REQ-062, DEC-058 and AC-062. Refine lifecycle memory retention while keeping transient old/new overlap as an unresolved OD-009 detail. No product implementation authorized.

### DISC-065: Release old model before loading replacement

- **Situation:** User reports tight RAM and rejects inactive-model caching. Q-052 distinguishes steady-state retention from old/new overlap during switching.
- **Question:** 切換模型時，舊模型的 RAM 要在何時釋放？
- **Options and tradeoffs:** 1. 先釋放舊模型，再載入新模型（建議）：完成前置檢查與暫停後，釋放舊模型參數及狀態，避免兩套模型常駐資料重疊；新模型載入失敗則按既定規則套用原有碰撞演算法。 / 2. 新模型準備完成後才釋放舊模型：切換前保留舊實例完整，但準備期間兩套模型資料同時占用 RAM；載入失敗仍遵循既定回退規則。
- **User answer:** 1
- **Explicit rationale:** User selects option 1 following the stated tight-RAM constraint; no additional rationale supplied.
- **Resulting impact:** Resolve Q-052; add REQ-063, DEC-059 and AC-063. Refine REQ-062 transient lifetime and Technical Contract Apply ordering. Preserve preflight rejection, ordinary successful Apply disabled state and failure fallback enable preservation. JSON parsing peak-memory design remains to be resolved; no product implementation authorized.

### DISC-066: Bounded streaming JSON loader

- **Situation:** After release-before-load is selected, Q-053 compares incremental JSON loading against retaining a full JSON document representation while creating model arrays.
- **Question:** 模型 JSON 載入要採用哪種方式？
- **Options and tradeoffs:** 1. 串流解析（建議）：使用有界讀取緩衝，將參數寫入最終運算陣列，避免完整 JSON 文件樹與模型陣列同時存在；必要時多次掃描檔案，解析與驗證較複雜。 / 2. 完整文件解析：先建立整份 JSON 的記憶體表示，再轉成模型陣列；實作較直觀，但解析期間會額外占用完整文件的空間。
- **User answer:** 1
- **Explicit rationale:** User selects option 1 following the stated tight-RAM constraint; no additional rationale supplied.
- **Resulting impact:** Resolve Q-053; add REQ-064, DEC-060 and AC-064. Refine REQ-045/063 validation and load mechanics while preserving complete JSON exchange, exact numeric semantics and failure recovery. No product implementation authorized.

### DISC-067: Add destroy lifecycle callback

- **Situation:** Streaming loading and release-before-load require a clear cleanup operation distinct from reset, which retains model parameters.
- **Question:** 切換時釋放演算法實例及其記憶體，要放在哪個介面？
- **Options and tradeoffs:** 1. 在 callback 組新增 destroy（建議）：由演算法提供配對的釋放函式，與 initialize、reset、process 一起管理；外層不需知道私有狀態結構。 / 2. 保留原本三個 callback，另設實例建立／銷毀介面：由建立實例的元件負責銷毀；運算 callback 組較小，但多一個生命週期介面。
- **User answer:** 1
- **Explicit rationale:** User selects option 1; no additional rationale supplied.
- **Resulting impact:** Resolve Q-054; add REQ-065, DEC-061 and AC-065; refine REQ-061 to include destroy and preserve REQ-057 reset semantics and REQ-063 release ordering. No product implementation authorized.

### DISC-068: Pause acquisition during JSON import

- **Situation:** Model import stores an artifact without Apply; Flash read/write exclusion alone does not establish acquisition quiescence. Q-055 compares paused import with concurrent sampling and storage.
- **Question:** 只匯入並儲存模型 JSON、尚未 Apply 時，是否暫停 IMU？
- **Options and tradeoffs:** 1. 暫停 IMU 後匯入（建議）：串流寫入及驗證期間停止取樣，結束或失敗後恢復原本取樣與功能啟用狀態，重新累積必要歷史；不切換目前模型。 / 2. 匯入期間繼續取樣與偵測：背景串流寫入及驗證，不主動暫停 IMU；需額外驗證 Flash 寫入對取樣、判斷與傳輸的影響，不能先保證不中斷。
- **User answer:** 1
- **Explicit rationale:** User selects option 1; no additional rationale supplied.
- **Resulting impact:** Resolve Q-055; add REQ-066, DEC-062 and AC-066, refining REQ-020/023/046 import execution without activation or persistent setting changes. Temporary interruption and subsequent history reset are explicit, while applied model identity remains unchanged. No product implementation authorized.

### DISC-069: Inline import-pause explanation

- **Situation:** After pausing IMU during import is accepted, Q-056 compares a permanently visible explanation and explicit action label against an additional pause-confirmation modal.
- **Question:** Web 要如何提示匯入會暫停 IMU？
- **Options and tradeoffs:** 1. 匯入區固定顯示說明，按鈕標示「暫停 IMU 並匯入」（建議）；選檔後由使用者按下才開始，不另加暫停確認對話框。 / 2. 按下匯入後顯示暫停確認對話框；使用者再次確認才開始，提醒較明確，但每次匯入多一步操作。
- **User answer:** 1
- **Explicit rationale:** User selects option 1; no additional rationale supplied.
- **Resulting impact:** Resolve Q-056; add REQ-067, DEC-063 and AC-067, refining REQ-050/066 UI and preserving REQ-021 replacement confirmation. No product implementation authorized.

### DISC-070: Single Device Configuration model workflow

- **Situation:** Q-057 incorrectly assumes a separate collision-model management page and asks where to navigate after import. User corrects the premise: no management page; import and immediate model summary belong in Device Configuration.
- **Question:** 模型匯入成功後，Web 要停留在哪裡？
- **Options and tradeoffs:** 1. 留在碰撞模型管理頁（建議）：更新清單並顯示「已儲存，尚未套用」，提供前往 Device Configuration 的連結，方便繼續匯入其他模型。 / 2. 自動前往 Device Configuration：方便接著選擇模型與 Apply，但不自動改變模型選項或套用；連續匯入時需要返回管理頁。 Both options are withdrawn because their separate-page premise is rejected.
- **User answer:** 上各討論不是不需要碰撞模型管理頁，只在Device Configuration  匯入模型即顯示摘要
- **Explicit rationale:** User expects one Device Configuration workflow with summary immediately after import, not a separate collision-model page. Treat this latest explicit clarification as authoritative without attributing the earlier written split to the user's current intent.
- **Resulting impact:** Resolve Q-057 by correction/withdrawal. Add REQ-068, DEC-064 and AC-068; reconcile REQ-050/053/067 and AC-050/053/067 and OD-008 placement. DEC-064 explicitly supersedes earlier page-split decisions while preserving their immutable historical records and existing import/Apply/Save rules. No product implementation authorized.

### DISC-071: Two summaries with selection-sensitive preview

- **Situation:** Q-058 compares one new-model summary plus an applied identity line against two full summaries. User selects two summaries and adds that changing the selected model must update its summary, with only imported/selected and applied summary areas.
- **Question:** 剛匯入的模型與目前已套用模型不同時，摘要要如何呈現？
- **Options and tradeoffs:** 1. 單一摘要加上目前已套用標示（建議）：匯入後顯示新模型摘要及「尚未套用」，另用一行標示目前已套用的模型名稱／版本；畫面較精簡。 / 2. 兩份摘要並列：同時顯示目前已套用模型與剛匯入模型的完整摘要，方便比較取樣率、來源與門檻，但占用較多畫面。
- **User answer:** 選擇2。還有切換選擇的模型摘要。我的想法是模型部分只要顯示匯入模型摘要、及目前已套用的模型摘要。
- **Explicit rationale:** User wants a summary for the changed selection, but only two model summary areas: imported/selected model and currently applied model.
- **Resulting impact:** Resolve Q-058; add REQ-069, DEC-065 and AC-069, refining REQ-053/068 summary layout and preview transitions. Preserve explicit Apply and existing recovery behavior without extra summary panels. No product implementation authorized.

### DISC-072: No manual import cancellation

- **Situation:** Q-059 asks whether an active import, during which IMU is paused, should offer a user cancellation control before storage commitment.
- **Question:** 匯入模型期間，是否提供「取消匯入」？
- **Options and tradeoffs:** 1. 提供（建議）：尚未提交儲存結果時可取消，清理未完成的匯入並恢復原本取樣／功能狀態；目前已套用模型不變，需增加取消與完成競態的處理。 / 2. 不提供：開始後等待成功或失敗，再恢復原本取樣／功能狀態；介面與流程較簡單，但使用者不能主動中止此次匯入。
- **User answer:** 2
- **Explicit rationale:** User selects option 2; no additional rationale supplied.
- **Resulting impact:** Resolve Q-059; add REQ-070, DEC-066 and AC-070. Refine REQ-066/067 import UI while retaining fault-driven cleanup/restoration and the distinct REQ-021 replacement-confirmation cancellation. No product implementation authorized.

### DISC-073: Directly expanded model section

- **Situation:** Q-060 consolidates the previously selected Device Configuration controls and compares a directly expanded model section against a collapsible one.
- **Question:** Device Configuration 的模型區要直接展開，還是可收合？
- **Options and tradeoffs:** 1. 直接展開（建議）：匯入、模型選擇與兩份摘要直接呈現在同頁，操作較直接，但頁面較長。 / 2. 可收合：模型區可折疊以縮短頁面；匯入成功或切換模型後自動展開摘要，確保結果立即可見，但多一個展開／收合操作。
- **User answer:** 1
- **Explicit rationale:** User selects option 1; no additional rationale supplied.
- **Resulting impact:** Resolve Q-060; add REQ-071, DEC-067 and AC-071. Resolve OD-008 user-facing UI composition through the accumulated desktop export dialog, same-page import, two-summary preview/applied layout and directly expanded presentation decisions. OD-009 concrete architecture ownership/dependency/execution design remains open; this is not implementation or full SPEC completion.

### DISC-074: Algorithms remain inside collision component

- **Situation:** Q-061 compares private algorithm implementations inside the existing collision component against a separate model-collision module connected through parent orchestration.
- **Question:** 原有演算法與匯入模型的碰撞運算，要如何劃分模組？
- **Options and tradeoffs:** 1. 放在既有 collision 模組內（建議）：各演算法使用獨立檔案與私有狀態，共用已確認的 callback 契約；集中維護碰撞功能，不增加跨模組協調。 / 2. 將匯入模型的完整碰撞演算法另設模組：原有演算法留在 collision，由上層協調 callback 連接；邊界更獨立，但增加介面與資料映射，仍維持單一呼叫位置。
- **User answer:** 採用
- **Explicit rationale:** Annotation selects: 我建議放在既有 collision 模組中，但每種演算法分開檔案：. User adopts this recommendation; no additional rationale supplied.
- **Resulting impact:** Resolve Q-061; add REQ-072, DEC-068 and AC-072. Refine OD-009 component placement while preserving private state, complete callbacks, single invocation and tight-RAM decisions. Detailed ownership/mapping design remains outstanding; no product implementation authorized.

### DISC-075: Independent model-storage component

- **Situation:** Q-062 compares separate model storage with a widened configuration store. User asks whether this means different files in Flash; assistant clarifies both options separate the files and the choice concerns managing components, not Flash hardware/partition separation.
- **Question:** 模型 JSON 的儲存管理，要如何與既有裝置設定儲存分工？
- **Options and tradeoffs:** 1. 新增獨立模型儲存元件（建議）：管理模型清單、串流讀寫、替換與刪除；裝置設定儲存維持負責選用模型、開關與共同設定值，可共用底層 Flash 存取協調。 / 2. 擴充既有設定儲存元件：由同一元件提供裝置設定與模型檔案兩組介面，檔案與交易仍分開；元件數較少，但同時承擔兩種不同的儲存生命週期。
- **User answer:** 1
- **Explicit rationale:** User selects option 1 after the file-versus-component clarification; no additional rationale supplied.
- **Resulting impact:** Resolve Q-062; add REQ-073, DEC-069 and AC-073. Refine OD-009 storage ownership while preserving independent Save/import semantics and tight-RAM constraints. Exact component parent/type/mapping remains to be documented before source changes; no product implementation authorized.

### DISC-076: Derive catalog from committed model JSON

- **Situation:** After choosing a separate model-storage component, Q-063 compares deriving the model list from JSON metadata against maintaining a separate persistent index.
- **Question:** 装置的模型清單，要從哪裡建立？
- **Options and tradeoffs:** 1. 從已完成儲存的模型 JSON 建立（建議）：串流讀取名稱、類型、取樣率等必要資訊，不另存一份模型清單檔；少一份需要同步的資料，但重建清單需讀取各模型檔案。 / 2. 另外保存模型索引檔：索引記錄模型名稱、檔案位置與摘要資訊，建立清單時可先讀索引；匯入、替換、刪除與斷電恢復都需維持索引和模型檔案一致。
- **User answer:** 1
- **Explicit rationale:** User selects option 1; no additional rationale supplied.
- **Resulting impact:** Resolve Q-063; add REQ-074, DEC-070 and AC-074, refining REQ-046/073 catalog authority and tight-RAM behavior. Preserve transaction/loadability rules. OD-009 concrete ownership and execution coordination remain to be documented; no product implementation authorized.

### DISC-077: Original force calibration while a model is applied

- **Situation:** Existing two-point calibration maps legacy collision acceleration peaks to force; imported models use score and JSON baseline times multiplier.
- **Question:** 目前已套用匯入模型時，原有碰撞演算法的 Calibration 頁要如何呈現？
- **Options and tradeoffs:** 1. 保留唯讀頁面（建議）：顯示原有校正係數與說明，停用取樣及 Save & Apply Calibration；需要校正時，先切回並 Apply 原有演算法。方便查閱，但頁面會有不能操作的項目。 2. 隱藏校正入口：套用匯入模型時不顯示原有碰撞校正功能；切回並 Apply 原有演算法後才恢復。畫面較簡單，但無法在模型使用期間查閱係數。
- **User answer:** 1
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** Add REQ-075, DEC-071 and AC-075. Firmware owns read-only UI and backend enforcement; desktop exports remain independent of original force coefficients. Behavior follows actual applied algorithm. Active calibration versus model switching remains to be resolved.

### DISC-078: Preserve calibration collection on model switch request

- **Situation:** Switching algorithms replaces the data producer while original force calibration may still be collecting samples.
- **Question:** 正在收集原有碰撞校正樣本時，切換模型並按 Apply，要如何處理？
- **Options and tradeoffs:** 1. 暫時拒絕切換（建議）：提示先完成或取消校正，再按 Apply。保留目前取樣工作與演算法，但需要使用者多一步操作。 / 2. 自動中止校正再切換：Apply 通過前置檢查後，取消本次尚未完成的取樣工作，再切換模型；既有已套用校正係數保留。操作較快，但本次未完成的取樣會失去。
- **User answer:** 1
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** Add REQ-076, DEC-072 and AC-076, refining REQ-075 calibration integration and REQ-063 switch preflight. Preserve current calibration and algorithm on rejection. OD-009 concrete architecture remains open.

### DISC-079: Reject competing mutations during model import

- **Situation:** A second browser can submit model Apply or deletion while another browser is importing; client-side control disabling alone cannot serialize operations.
- **Question:** 模型匯入進行中，若另一個頁面送來 Apply 或刪除模型要求，要如何處理？
- **Options and tradeoffs:** 1. 立即拒絕（建議）：顯示「模型匯入中，請完成後重試」，不保存待執行要求。沿用既有 Busy 處理方式，減少狀態與記憶體需求；使用者需重新操作。 / 2. 保留一筆等待要求：匯入結束後重新檢查，再執行 Apply 或刪除；等待期間顯示待執行狀態，超出一筆則拒絕。少一次手動重試，但需要額外狀態，操作也可能延後發生。
- **User answer:** 1
- **Explicit rationale:** No additional rationale supplied; limited RAM is an earlier confirmed constraint.
- **Resulting impact:** Add REQ-077, DEC-073 and AC-077. Extend existing immediate-rejection operation admission to model import conflicts without deferred commands. Keep REQ-076 calibration conflict handling and OD-009 architecture work.

### DISC-080: Fallback on actual non-finite model computation

- **Situation:** Successful parameter loading does not itself guarantee every later arithmetic result is finite. This is a hypothetical actual execution-failure policy, not an observed device fault or a predictive resource check.
- **Question:** 模型已載入，且有效輸入下的實際運算產生 NaN／無限大時，要如何處理？
- **Options and tradeoffs:** 1. 切回原有碰撞演算法（建議）：顯示錯誤原因，由外層協調切換並重新暖機，保留原本碰撞偵測啟用狀態。延續載入失敗的處理方向，但目前使用的演算法會改變。 / 2. 停用碰撞偵測：保留模型選擇並顯示錯誤，由使用者重新套用模型或改選原有演算法。避免自動改變演算法，但人工處理前不再進行碰撞判斷。
- **User answer:** 1
- **Explicit rationale:** No rationale supplied. Follow-up annotation asks 不懂問題情境. Explain arithmetic overflow or an invalid numeric result; distinguish ordinary warmup, absent history and sensor invalidity. No withdrawal stated.
- **Resulting impact:** Add REQ-078, DEC-074 and AC-078. Extend actual runtime fault handling, retaining REQ-055 bool return and coordinated retirement. OD-009 remains open for concrete ownership and fault handoff design.

### DISC-081: Replace runtime numeric-fault fallback with disable and log

- **Situation:** Q-067 option 1 was previously recorded; after clarification the user explicitly changes to option 2 and adds abnormal logging.
- **Question:** 模型已載入，且有效輸入下的實際運算產生 NaN／無限大時，要如何處理？
- **Options and tradeoffs:** 1. 切回原有碰撞演算法（建議）：顯示錯誤原因，由外層協調切換並重新暖機，保留原本碰撞偵測啟用狀態。延續載入失敗的處理方向，但目前使用的演算法會改變。 / 2. 停用碰撞偵測：保留模型選擇並顯示錯誤，由使用者重新套用模型或改選原有演算法。避免自動改變演算法，但人工處理前不再進行碰撞判斷。
- **User answer:** 改選擇2，要輸出異常log。
- **Explicit rationale:** User adds abnormal logging; no further rationale supplied.
- **Resulting impact:** Revise REQ-078 and AC-078; add REQ-079, DEC-075 and AC-079. DEC-075 supersedes DEC-074 runtime-fault behavior. Keep historical discussion intact and keep load-failure fallback distinct. Log once per fault transition to avoid per-sample repetition while collision processing is stopped. Concrete fault handoff remains OD-009.

### DISC-082: Structured process result replaces bool-only fault side channel

- **Situation:** Persisted Q-068 offered error-state querying or a separate error callback while preserving bool. User then requested changing the bool-only restriction, agreed with direct status reporting and asked for alternatives. The latest visible comparison offered enum, small result structure or bool plus output parameter. That comparison was not persisted before presentation; Superseded saved question: 維持 process() 回傳 bool，模型運算異常要如何交給外層處理？ Superseded options: 記錄錯誤狀態，呼叫後檢查（建議）：演算法保存固定大小的錯誤代碼，process() 回傳 false；外層在呼叫返回後查詢，停用碰撞並安排輸出 log。流程集中、沒有錯誤通知的巢狀呼叫，但每次處理後多一次狀態檢查。 / 另設錯誤通知 callback：演算法只在首次異常時通知外層，接著回傳 false。外層 callback 僅記錄待處理錯誤，待 process() 返回後再完成停用與 log；不用每次查詢演算法狀態，但多一條 callback 與綁定生命週期。  this record explicitly repairs the context without interpreting the answer against the obsolete two-option list.
- **Question:** 你想採用 1、2，還是 3？（最新三方案：單一 enum、小型結果結構、bool＋錯誤輸出參數。）
- **Options and tradeoffs:** 1. 單一 enum：NoCollision、Collision、NumericError；最簡單，細分原因需增加 enum 值。 / 2. 小型結果結構（建議）：判斷狀態＋錯誤代碼；方便精確 log，但比單一 enum 多一個欄位。 / 3. bool＋錯誤輸出參數：接近原介面，但呼叫端可能漏查錯誤。
- **User answer:** 方案2
- **Explicit rationale:** User previously requested changing the bool-only restriction and asked for alternatives; no additional rationale supplied for selecting the result structure.
- **Resulting impact:** Resolve obsolete Q-068 by the latest explicit replacement decision, not its old option-number mapping. Revise REQ-054/055/056/057/058/060/061/078 and AC-055/056/061; add DEC-076. Keep historical DEC-051/053 and discussions as history. ProcessResult owns no dynamic allocation, model arrays or text; outer caller owns logging and disable action. No product code or architecture manifest modified; concrete named-type ownership and mappings remain OD-009.

### DISC-083: Model storage belongs under Device Management

- **Situation:** Independent model storage was accepted in REQ-073; its logical parent remained open. Existing Device Management owns device settings and operation admission, while Data Services coordinates Flash leases.
- **Question:** 獨立的模型儲存元件，要由哪個上層模組管理？
- **Options and tradeoffs:** 1. Device Management（建議）：模型儲存與裝置設定是分開的子元件，由同一上層協調模型清單、選擇與刪除後的設定修正；Data Services 維持 Flash 存取協調。設定關聯較集中，但 Device Management 的職責會增加。 / 2. Data Services：模型檔案與清單由資料服務管理，Device Management 只管理模型選擇及裝置設定。檔案管理較集中，但涉及模型與設定的操作需要 firmware_system 跨上層協調，且 Data Services 不再只管理 Flash 存取。
- **User answer:** 1
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** Add REQ-080, DEC-077 and AC-080; refine REQ-073 logical parenting. Model storage and configuration remain independent siblings. Cross-L1 flow mapping stays with firmware_system. OD-009 still requires detailed boundary/type/state/dependency matrices and applicable validation; no architecture manifest or product source modified.

### DISC-084: Separate parameter validation and loading from model storage

- **Situation:** User found the original explanation confusing because parameter checking and loading were described together. Clarification explained checking fields/counts/numeric validity versus reading unchanged coefficients into RAM, and that only code responsibility is being selected.
- **Question:** 模型參數的格式檢查與載入流程，要獨立於模型儲存元件嗎？ Clarified wording: 檢查與載入模型參數的程式，要獨立成一個元件，還是放在模型儲存元件裡？
- **Options and tradeoffs:** 1. 獨立成模型載入元件（建議）：儲存元件負責檔案及清單，載入元件負責格式、維度、精度檢查與參數交付；演算法仍擁有自己的參數與工作狀態。修改模型格式時責任較集中，但多一個元件及交接介面。 / 2. 納入模型儲存元件：由儲存元件一併負責格式檢查與參數交付，再經上層交給演算法。元件較少，但儲存元件需要了解各模型的參數格式，新增模型類型時也要修改它。 Clarified options retain the same meaning: independent checking/loading component versus storage also owning checking/loading. User-visible operation and model calculations remain the same.
- **User answer:** 1
- **Explicit rationale:** No rationale supplied for the choice. Prior clarification request: 我看不懂問題。感覺上是要檢查參數，但問題卻寫把 JSON 轉成模型可使用的參數.
- **Resulting impact:** Add REQ-081, DEC-078 and AC-081, refining REQ-064/073/080. Preserve streaming and private algorithm ownership without a second full model allocation. No product source or architecture manifest changes. Detailed parent and boundary mappings remain OD-009.

### DISC-085: Parameter validation and loading belongs under Sensor Pipeline

- **Situation:** REQ-081 establishes a separate loader. Its parent must coordinate parameter delivery, initialization and failure cleanup while model files remain owned by Device Management storage.
- **Question:** 獨立的參數檢查／載入元件，由哪個上層協調？
- **Options and tradeoffs:** 1. Sensor Pipeline（建議）：與 collision 演算法同屬一個上層，方便協調參數載入、初始化及失敗清理；匯入時由 firmware_system 串接模型儲存與只檢查流程。執行端責任集中，但匯入檢查需要跨上層協調。 / 2. Device Management：與模型儲存同屬一個上層，匯入檢查集中處理；Apply 時由 firmware_system 把載入流程接到 Sensor Pipeline 的參數接收介面。檔案與格式處理集中，但載入及演算法初始化的協調跨越兩個上層。
- **User answer:** 1
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** Add REQ-082, DEC-079 and AC-082. Refine REQ-080/081 with Sensor Pipeline parenting and parent-mediated loader/collision interaction; firmware_system coordinates storage, Flash admission and execution parents. Preserve import-only validation, Apply ordering and memory limits. Concrete type/state/boundary mappings and validation remain OD-009; no product implementation authorized.

### DISC-086: Algorithm owns parameter allocation and partial-load cleanup

- **Situation:** Loader and collision are siblings under Sensor Pipeline. Final parameters must have a single owner throughout streaming load without a second full parameter copy; partial failure needs clear cleanup responsibility.
- **Question:** 模型參數需要的 RAM，由誰配置並負責載入失敗時的清理？
- **Options and tradeoffs:** 1. 演算法配置，載入元件填入（建議）：演算法先建立尚未啟用的實例與最終參數空間，載入元件經受控介面逐段填入；失敗就由該演算法銷毀未完成實例。配置與釋放責任一致，但需要參數填入及完成檢查介面。 / 2. 載入元件配置，成功後移交：載入元件先配置並填入參數，成功後把同一份記憶體的管理責任交給演算法，不複製資料。載入階段較集中，但必須明確處理交接前後的釋放責任，避免重複釋放或遺漏。
- **User answer:** 1
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** Add REQ-083, DEC-080 and AC-083, refining REQ-060/063/064/065/081/082. Algorithm owns allocations before, during and after fill. Sensor Pipeline maps checked fill/completion interfaces; loader cannot access private layout. Preserve import-only validation and existing failure fallback. OD-009 concrete boundary/type/state tables remain open; no source changes.

### DISC-087: Model score and threshold reuse selected collision registers

- **Situation:** Original collision registers 536-545 expose g-valued collision curves/magnitude/thresholds/peaks. User confirms this address range, then replaces the offered all-unavailable versus all-zero choice with per-register model semantics.
- **Question:** 套用匯入模型後，外部讀取原有演算法專用的碰撞曲線／門檻／峰值暫存器時，要如何回應？
- **Options and tradeoffs:** 1. 回報不適用（建議）：明確表示這些欄位在目前模型下沒有有效數值，不回傳 score 或保留舊值。語義清楚，但讀取這些欄位的既有客戶端需處理不適用回應。 / 2. 保留欄位並回傳 0：維持原有數值欄位格式，文件與可用狀態標示此模式下的 0 只是占位值。較方便維持固定資料布局，但未檢查模式或狀態的舊客戶端可能誤認為真實量測為零。
- **User answer:** score使用536、threshold使用540，其餘回報不適用。應該說可以訂閱的訊號仍要可以輸出
- **Explicit rationale:** 可以訂閱的訊號仍要可以輸出. User requires continued output of subscribable/applicable signals rather than dropping all collision signal output.
- **Resulting impact:** Add REQ-084, DEC-081 and AC-084. For imported models, 536 is score; 540 is the effective detector threshold under REQ-030/035/059; the other listed collision registers are not applicable. Original mode retains its mapping. This explicit semantic remapping supersedes the unaccepted premise that no model quantity may use any existing collision register; no score is mislabeled as original force or g. Other signal subscriptions remain supported. Keep REQ-055 result structure and REQ-043 disabled processing; detailed projection contracts remain OD-009. No product source changes.

### DISC-088: Fixed Float32 model score and threshold output

- **Situation:** Existing 536/540 registers are Float32, while supported models can compute in Float32 or Float64. Projection precision and internal decision precision must be distinguished.
- **Question:** 536 的 score 與 540 的 threshold，對外輸出要使用哪種精度？
- **Options and tradeoffs:** 1. 固定 Float32（維持既有格式）：每個值仍為 4 bytes；Float64 模型只在輸出時轉換，內部判斷不變。客戶端格式變動較少，但輸出可能捨入，甚至看起來 score 等於 threshold 而內部已判定超過；超出 Float32 範圍需回報輸出無效。 / 2. 跟隨模型精度：Float32 模型輸出 4 bytes，Float64 模型輸出 8 bytes，保留實際計算數值的精度。較方便核對判斷結果，但訊號型別描述與客戶端解析必須支援切換；原有演算法維持原格式。
- **User answer:** 1
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** Add REQ-085, DEC-082 and AC-085; refine REQ-084 fixed external encoding without narrowing REQ-045 model precision. Keep consumer-visible rounding explicit and report Float32 range overflow as invalid output, not an internal arithmetic fault. No source changes; detailed availability/transport mapping remains OD-009.

### DISC-089: Binary missing-value marker is distinct from model arithmetic error

- **Situation:** Current TCP subscription publication aborts a packet when any selected projection fails. User requires valid fields to keep outputting, so unavailable collision floats need an explicit wire representation.
- **Question:** 二進位訂閱封包中的碰撞浮點欄位不適用或暫無有效值時，要用哪種表示方式，讓其他有效欄位繼續輸出？
- **Options and tradeoffs:** 1. 使用固定的 NaN 標記（建議）：欄位仍占原本 4 bytes，以指定的 quiet NaN 表示沒有有效值；訂閱端顯示空值或曲線斷點，不當成碰撞或零值。封包布局不用增加欄位，但接收端必須辨識此標記，單靠它不能區分無效原因。 / 2. 新增每欄位有效狀態：封包另外攜帶狀態，明確區分有效、不適用、尚未就緒或輸出超範圍；無效欄位的數字不可當量測使用。原因較清楚，但需要調整封包版本、增加狀態資料並同步修改接收端。
- **User answer:** 1，但不是有NaN異常?有異常不是直接return?
- **Explicit rationale:** User asks whether actual NaN arithmetic should immediately return. Clarified that the algorithm returns Error and outer control disables collision/logs, while independent telemetry inserts the missing-value marker only during encoding. Latest user says 了解，繼續討論.
- **Resulting impact:** Add REQ-086, DEC-083 and AC-086; refine REQ-055/078/079/084/085 without changing computation precision or packet field widths. Receiving software must preserve valid signal fields and render unavailable fields as gaps. No product source modified; exact transport/consumer mapping remains OD-009.

### DISC-090: Coherent score and threshold output pair

- **Situation:** A setting change between model evaluation and telemetry publication could otherwise pair an old score with a threshold that was not used to judge it. Per-evaluation setting coherence was already settled; this question concerns output projection.
- **Question:** 536 的 score 與 540 的 threshold，要一起取自同一次模型計算嗎？
- **Options and tradeoffs:** 1. 使用同一次計算的數值（建議）：輸出 score 時，540 一起輸出該次判斷實際使用的 threshold。方便核對碰撞結果；倍率變更後，新 threshold 要等下一次有效計算才反映在這組輸出，設定頁仍可顯示已套用的新設定。 / 2. 540 隨設定立即更新：536 輸出最近有效 score，540 輸出最新已套用的 threshold。能立即看到門檻設定變更，但兩者可能不是同一次判斷使用的數值，不能直接用它們還原當次結果。
- **User answer:** 1
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** Add REQ-087, DEC-084 and AC-087, refining REQ-059/084/085/086. Pair output values from the same evaluation; retain immediate device-setting display separately. Preserve Float32 rounding limitations and invalid-output markers. Concrete snapshot ownership remains part of OD-009; no product code changes.

### DISC-091: Retain existing downsample behavior

- **Situation:** Existing OutputWindowReducer emits the last frame at each configured output window boundary. A higher model evaluation rate can produce intermediate score peaks not shown in lower-rate telemetry.
- **Question:** 訂閱輸出率低於模型計算率時，每次輸出的 score 要選哪一筆？
- **Options and tradeoffs:** 1. 輸出當下最新有效結果（維持現有取樣方式）：536 取最新 score，540 取同次計算的 threshold。符合現有輸出視窗選取最後一筆的方式，但兩次輸出之間的短暫 score 尖峰可能看不到。 / 2. 輸出該區間最大 score：536 取本次輸出區間內最大的有效 score，540 取該筆 score 同次計算的 threshold。較容易看到短暫尖峰，但數值代表區間峰值，不是輸出當下最新值，需保存一份區間最大值快照。
- **User answer:** 沿用目前down sample方式就可以了
- **Explicit rationale:** User requests existing downsample behavior, rather than a new maximum-score selection rule.
- **Resulting impact:** Add REQ-088, DEC-085 and AC-088; retain current last-frame selection and paired REQ-087 score/threshold, with REQ-086 missing values. No new peak aggregation, computation cadence change or packet layout. OD-009 concrete mapping remains open; no source changes.

### DISC-092: Accept integrated design and finalize both project specifications

- **Situation:** User reviewed the integrated import/Apply/process/publish responsibilities, then asked whether the original algorithm already captures a result. Source inspection showed projection_ and latest_collision_ retain the latest result; explanation distinguished this from historical capture. User then asked whether more discussion was needed; remaining work was document consolidation and validation planning.
- **Question:** 這份整合後的匯入、Apply、演算法與訂閱輸出分工，是否採用為 SPEC 的整體設計？
- **Options and tradeoffs:** 1. 採用整體設計：保留目前元件分工與參數單一擁有者，collision 保存輸出快照，由 Sensor Pipeline 讀取並映射到訂閱資料；接著整理兩份 SPEC 的正式版本。這是設計確認，不代表程式或效能已驗證。 / 2. 先調整整體設計：指出要改的流程或責任分工，草稿先保留現況，再核對其影響；暫不定稿，避免把不符合預期的交接方式寫成最終契約。
- **User answer:** 採用
- **Explicit rationale:** No additional rationale supplied. Previous clarification was acknowledged as understood.
- **Resulting impact:** Resolve Q-078 and OD-009 at logical SPEC design level; add REQ-089, DEC-086 and AC-089. Confirm integrated flow, boundary, type/state owner and dependency mappings. Update current summaries and counterpart canonical links; preserve superseded decisions as history. Materialize both project-local specifications. Pre-code manifest validation, exact source catalog, AST coverage, verification matrix and physical/desktop runtime evidence remain mandatory implementation work, not completed evidence or new unresolved user choices. No product execution authority is granted.


### DISC-093: Synchronize FIR-only fixed-capacity deployment after document recovery

- **Situation:** Earlier three-family dynamically sized deployment contract remained on disk after later scope decisions. Firmware canonical file was deleted; a finalization snapshot was recovered byte-for-byte (SHA256 6dd2a2475bb6707a8a6e7b3813e368f7417be20b4cf6950146cf6c9c14c4376a); its working revision 90 is not the lost confirmed revision 91.
- **Question:** Which adopted scope must be synchronized, and which limits remain undecided?
- **Options and tradeoffs:** Earlier three-family per-model allocation versus user-selected FIR-only reusable fixed storage. Fixed reservation bounds memory but consumes its reserved capacity even for shorter models.
- **User answer:** 我比較傾向固定RAM，軟體也只能選取適合的時間長度; 目前ESP32只要實作FIR/Ridge 就可以了。之前軟體模擬MLP跟single IMU結果都不理想; 幫我整理同步。
- **Explicit rationale:** RAM is tight and MLP/single-IMU simulation results were unsatisfactory. User requests separate synchronized desktop/firmware specifications after accidental deletion.
- **Resulting impact:** DEC-087/088/089 supersede historical family/allocation policies; REQ-025/027/063/065 and REQ-090/091/092 govern current scope. Preserve historical rows as history, not current contrary requirements. OD-010 remains open; 65 taps and the previous export RAM-estimate UI suggestion were not adopted. No product execution authorization is inferred.

### DISC-094: User-controlled software options

- **Situation:** The previous synchronization restricted desktop history by ESP32 capacity and a deployment-purpose selector was suggested.
- **Question:** Restrict history only under an ESP32 deployment purpose, or restrict all FIR training?
- **Options and tradeoffs:** A target-purpose selector preserves unrestricted simulation; a global restriction reduces choices. The user rejects the restriction itself.
- **User answer:** 不需要限制。使用者要知道自己的功能選項。
- **Explicit rationale:** User owns the choice and understanding of functionality.
- **Resulting impact:** DEC-090 and revised REQ-027/091, AC-027/091 remove software capacity filtering and export gating. Existing qualification checks and FIR-only ESP32 scope remain. Firmware bounds checks remain necessary for fixed storage; no numeric capacity is adopted.


### DISC-095: Complete RAM proposal and paired acceptance planning

- **Situation:** User selected the two outstanding planning tasks.
- **Question:** Complete total RAM accounting, propose acceptance thresholds, synchronize both SPECs and fill acceptance mappings.
- **Options and tradeoffs:** PP-001 budgets all fixed pools, parser/I/O/control storage, transient heap and existing stack headroom; thresholds are proposed rather than inferred from historical heap snapshots.
- **User answer:** 先完成這兩個項目 (annotation: 核算完整 RAM 預算，提出驗收門檻。同步兩端 SPEC，補齊驗收對照。).
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** Synchronize 96 REQ/AC pairs and shared Technical Contract; correct residual AC-044/054 deployment-family wording. Add PP-001 and a 96-row owner/layer/evidence crosswalk. Decision entries 090 through 104 in the counterpart firmware SPEC-0062 are the source of the already adopted shared history/rate/static-storage/Draft/Orientation/Float32/FIR-only decisions; desktop local decision IDs are independent and not renumbered. PP-001 awaits adoption; no implementation or device test requested or claimed.
- **Source:** user:01a0c301-5c83-77e0-b598-4b5fcb90fcf1:complete-two-planning-items; firmware SPEC-0062 revision 32 and desktop SPEC-0039 revision 177.

### DISC-096: Authorize desktop JSON export independently of firmware RAM planning

- **Situation:** OD-010 belongs to the firmware RAM design and does not determine desktop serialization or export eligibility.
- **Question:** Execute desktop JSON export while leaving ESP32 memory configuration to firmware?
- **Options and tradeoffs:** The user explicitly selects desktop delivery; firmware capacity and device validation remain independently required without blocking desktop export.
- **User answer:** 執行桌面端 JSON 匯出，
- **Explicit rationale:** Annotation 1: 把 ESP32 記憶體配置的決定留給韌體專案。
- **Resulting impact:** DEC-091 scopes current delivery to desktop JSON export, export UI and their tests. Preserve FIR/Ridge-only export, qualification, frozen execution settings, numeric precision, independent display name/filename editing and one model per file. Do not add ESP32 capacity restrictions, warnings or queries. Firmware implementation, RAM proposal adoption, target tests and receiver telemetry changes are outside this execution slice; retained cross-project criteria are not claimed implemented.
- **Source:** Current user message in task 01a0c356-d77c-7421-935c-72e5a478a492; no host message ID is exposed in the supplied message.

### DISC-097: Recover omitted Export Profile UI requirements and proposal

- **Situation:** The user supplied a screenshot of Export Profile with no selected kernels and requested accessible kernel-level JSON export. The assistant replied with a UI plan without persisting it. The user then asked why SPEC was not updated.
- **Question:** UI你會如何規劃; 為什麼沒有寫入spec?
- **Options and tradeoffs:** Page-local selection supports chosen subsets; an all-qualified list with per-row actions makes each available model directly discoverable. Detailed assistant recommendations remain unconfirmed.
- **User answer:** Kernel selection on Export Profile or a list of all qualified kernels with Export JSON at the right; show Kernel ID, History/taps, threshold, qualified range; remove Header Format and Export Headers. Persisted as REQ-097/098, DEC-092 and AC-097/098.
- **Assistant proposal, not adopted:** Full-width all-qualified list with count, individual per-row export instead of a batch toolbar; remove Header Preview and Selected Kernels sidebar; retain name/file dialogs; display noncontiguous passing speeds explicitly; retain JSON-ineligible qualified rows with a disabled action and reason; fixed table headings and vertical scrolling; empty-state return to Replay & Qualify. These are recommendations and are not user confirmation.
- **Explicit rationale:** User wants kernel selection and key model information on the export page. No additional user rationale was supplied.
- **Resulting impact:** Add REQ-097/098, DEC-092 and AC-097/098; reopen SPEC-0039 in place and save the requested UI change. No product source is changed by this recovery. UI proposal confirmation and execution state are not inferred from the user's question about persistence. Existing JSON semantics and firmware-owned RAM decisions remain unchanged.
- **Source:** Actual user and assistant messages in current task on 2026-09-22, including screenshot codex-clipboard-ac491188-82f6-4612-a6d6-1171b8474c04.png. Host read_thread returned empty item arrays for recent turns; this is a manual conversation-source reference, not an invented host message ID.

### DISC-098: Execute the presented kernel-list UI

- **Situation:** User asks whether further discussion is needed; the assistant recommends the all-qualified per-row layout and states no functional ambiguity remains.
- **Question:** Execute the presented UI plan?
- **Options and tradeoffs:** Adopt the list so export does not depend on a previous-page selection; preserve JSON validation and individually explain unavailable actions.
- **User answer:** 開始執行
- **Explicit rationale:** No further rationale supplied.
- **Resulting impact:** DEC-093 settles the proposed layout, clarifies REQ-097 and AC-097, and authorizes implementation of REQ-097/098 with existing JSON semantics. Header serialization APIs remain available to existing callers. The previous assistant proposal is now adopted through this execution request.
- **Source:** user:01a0c6d2-2051-7b23-b2da-271b6992fb8f:execute-ui; actual current-turn text 開始執行. Host exposed the turn ID but no message item ID; source is caller-attested.

### DISC-099: Explicit desktop-only scope and continued execution

- **Situation:** The prior materialization gate incorrectly made cross-project acceptance prerequisites for a desktop UI change.
- **Question:** Which delivery scope should continue?
- **Options and tradeoffs:** Preserve all historical discussion while narrowing current normative requirements and acceptance to the requested software output; excluded firmware work is neither required nor claimed verified.
- **User answer:** 只要處理軟體輸出JSON; 這些不需要; 繼續執行.
- **Explicit rationale:** The user does not need firmware import, ESP32 memory configuration or device verification in this task.
- **Resulting impact:** DEC-094 narrows active requirements and acceptance to desktop REQ-004/005/022/025/026/027/040/044/045/049/058/097/098. Add machine-readable host semantic and adapter acceptance selectors; retain the current user execution instruction for this same requested UI.
- **Source:** user:01a0c6e1-3f04-7e23-8fbe-6bbdb153c03d:continue-desktop; actual current annotation and request. Caller-attested turn reference; no invented host message ID.

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-004 | REQ-004 | Verify: Desktop export produces a strict UTF-8 JSON artifact for one qualified model. Firmware import and runtime are not deliverables of this specification. | Desktop JSON/controller regression fixtures and reference roundtrip checks | Pending current UI revision verification |
| AC-005 | REQ-005 | Verify: Each JSON file contains exactly one frozen model and its complete execution settings. Exporting different kernels produces independent files. | Desktop JSON/controller regression fixtures and reference roundtrip checks | Pending current UI revision verification |
| AC-022 | REQ-022 | Verify: Allow independent editing of model name and filename. Default name is model type, required sampling rate and stable kernel number, such as FIR_1000Hz_k001, without a timestamp. Suggest name plus .json; changing filename does not change embedded name. | Desktop JSON/controller regression fixtures and reference roundtrip checks | Pending current UI revision verification |
| AC-025 | REQ-025 | Verify: JSON export supports qualified dual-IMU FIR/Ridge only. Preserve existing desktop training and simulation for other families; explain unsupported JSON export without silently changing model family. | Desktop JSON/controller regression fixtures and reference roundtrip checks | Pending current UI revision verification |
| AC-026 | REQ-026 | Verify: Preserve the declared Float32 or Float64 model precision, exact selected-type numeric values including signed zero, array shapes and ordering. Never narrow precision for export. | Desktop JSON/controller regression fixtures and reference roundtrip checks | Pending current UI revision verification |
| AC-027 | REQ-027 | Verify: Desktop export adds no ESP32 RAM, taps, rate or capacity gate, warning or capability query. Keep qualification and JSON semantic validation. | Desktop JSON/controller regression fixtures and reference roundtrip checks | Pending current UI revision verification |
| AC-040 | REQ-040 | Verify: Export only current qualified profiles with the same frozen parameters, preprocessing, detector settings and numeric precision. Recheck current availability when preparing and saving; reject stale, failed, incomplete and invalid results. | Desktop JSON/controller regression fixtures and reference roundtrip checks | Pending current UI revision verification |
| AC-044 | REQ-044 | Verify: Export a complete frozen execution snapshot including format/version, name, family, numeric type, required rate, input identities, model coefficients, preprocessing, residual, detector and provenance. Do not rerun training or Qualification during export. | Desktop JSON/controller regression fixtures and reference roundtrip checks | Pending current UI revision verification |
| AC-045 | REQ-045 | Verify: Validate finite numbers, dimensions, rates, positive scales and thresholds, Unicode model names and local JSON filenames. Internal/External XYZ units are user-confirmed g, without conversion. Preserve provenance identity independently of display name and filename. | Desktop JSON/controller regression fixtures and reference roundtrip checks | Pending current UI revision verification |
| AC-049 | REQ-049 | Verify: Restore exported arrays and settings on the desktop and verify reference prediction and strict threshold behavior in the declared numeric precision. This is desktop roundtrip evidence, with no firmware or device parity claim. | Desktop JSON/controller regression fixtures and reference roundtrip checks | Pending current UI revision verification |
| AC-058 | REQ-058 | Verify: Preserve frozen single-sample 1_OF_1 detector semantics, threshold, release ratio and quiet time. Do not silently rewrite multi-sample confirmation. Show a reason for an otherwise qualified row that cannot be exported as JSON. | Desktop JSON/controller regression fixtures and reference roundtrip checks | Pending current UI revision verification |
| AC-097 | REQ-097 | Verify: Export Profile lists all qualified kernels independently of previous-page selection. Each row shows Kernel ID, History/taps, threshold and qualified range, with Export JSON at the far right. Use actual passing speeds when available without inventing continuous coverage. Keep fixed headings, a scrolling body, per-row eligibility reasons and empty-state guidance to Replay & Qualify. Each action opens the existing name and save dialogs for that row alone. | QML interaction, controller tests and visual inspection | Pending current UI revision verification |
| AC-098 | REQ-098 | Verify: Remove Header Format, Header Preview, Export Headers and Selected Kernels sidebar from Export Profile. Preserve existing header serialization APIs for other callers. Keep JSON filename validation, explicit overwrite confirmation, atomic commit and failure cleanup; show actionable save errors. | QML interaction, controller tests and visual inspection | Pending current UI revision verification |

| AC-001 | REQ-001 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-002 | REQ-002 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-003 | REQ-003 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-006 | REQ-006 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-007 | REQ-007 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-008 | REQ-008 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-009 | REQ-009 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-010 | REQ-010 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-011 | REQ-011 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-012 | REQ-012 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-013 | REQ-013 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-014 | REQ-014 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-015 | REQ-015 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-016 | REQ-016 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-017 | REQ-017 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-018 | REQ-018 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-019 | REQ-019 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-020 | REQ-020 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-021 | REQ-021 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-023 | REQ-023 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-024 | REQ-024 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-028 | REQ-028 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-029 | REQ-029 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-030 | REQ-030 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-031 | REQ-031 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-032 | REQ-032 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-033 | REQ-033 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-034 | REQ-034 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-035 | REQ-035 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-036 | REQ-036 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-037 | REQ-037 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-038 | REQ-038 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-039 | REQ-039 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-041 | REQ-041 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-042 | REQ-042 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-043 | REQ-043 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-046 | REQ-046 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-047 | REQ-047 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-048 | REQ-048 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-050 | REQ-050 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-051 | REQ-051 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-052 | REQ-052 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-053 | REQ-053 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-054 | REQ-054 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-055 | REQ-055 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-056 | REQ-056 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-057 | REQ-057 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-059 | REQ-059 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-060 | REQ-060 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-061 | REQ-061 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-062 | REQ-062 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-063 | REQ-063 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-064 | REQ-064 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-065 | REQ-065 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-066 | REQ-066 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-067 | REQ-067 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-068 | REQ-068 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-069 | REQ-069 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-070 | REQ-070 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-071 | REQ-071 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-072 | REQ-072 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-073 | REQ-073 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-074 | REQ-074 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-075 | REQ-075 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-076 | REQ-076 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-077 | REQ-077 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-078 | REQ-078 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-079 | REQ-079 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-080 | REQ-080 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-081 | REQ-081 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-082 | REQ-082 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-083 | REQ-083 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-084 | REQ-084 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-085 | REQ-085 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-086 | REQ-086 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-087 | REQ-087 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-088 | REQ-088 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-089 | REQ-089 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-090 | REQ-090 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-091 | REQ-091 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-092 | REQ-092 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-093 | REQ-093 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-094 | REQ-094 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-095 | REQ-095 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |
| AC-096 | REQ-096 | Verify the desktop change adds no implementation or device-validation dependency for this retired cross-project obligation; no firmware behavior is claimed. | Desktop scope and change review | Pending scope review |

## Acceptance Mapping

```json
{
  "AC-004": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Desktop-only Desktop export produces a strict UTF-8 JSON artifact for one qualified model. Firmware import and runtime are not deliverables of this specification.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-005": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Desktop-only Each JSON file contains exactly one frozen model and its complete execution settings. Exporting different kernels produces independent files.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-022": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "rationale": "Desktop-only Allow independent editing of model name and filename. Default name is model type, required sampling rate and stable kernel number, such as FIR_1000Hz_k001, without a timestamp. Suggest name plus .json; changing filename does not change embedded name.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-025": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Desktop-only JSON export supports qualified dual-IMU FIR/Ridge only. Preserve existing desktop training and simulation for other families; explain unsupported JSON export without silently changing model family.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-026": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Desktop-only Preserve the declared Float32 or Float64 model precision, exact selected-type numeric values including signed zero, array shapes and ordering. Never narrow precision for export.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-027": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Desktop-only Desktop export adds no ESP32 RAM, taps, rate or capacity gate, warning or capability query. Keep qualification and JSON semantic validation.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-040": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "rationale": "Desktop-only Export only current qualified profiles with the same frozen parameters, preprocessing, detector settings and numeric precision. Recheck current availability when preparing and saving; reject stale, failed, incomplete and invalid results.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-044": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Desktop-only Export a complete frozen execution snapshot including format/version, name, family, numeric type, required rate, input identities, model coefficients, preprocessing, residual, detector and provenance. Do not rerun training or Qualification during export.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-045": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Desktop-only Validate finite numbers, dimensions, rates, positive scales and thresholds, Unicode model names and local JSON filenames. Internal/External XYZ units are user-confirmed g, without conversion. Preserve provenance identity independently of display name and filename.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-049": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Desktop-only Restore exported arrays and settings on the desktop and verify reference prediction and strict threshold behavior in the declared numeric precision. This is desktop roundtrip evidence, with no firmware or device parity claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-058": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Desktop-only Preserve frozen single-sample 1_OF_1 detector semantics, threshold, release ratio and quiet time. Do not silently rewrite multi-sample confirmation. Show a reason for an otherwise qualified row that cannot be exported as JSON.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-097": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "rationale": "Desktop-only Export Profile lists all qualified kernels independently of previous-page selection. Each row shows Kernel ID, History/taps, threshold and qualified range, with Export JSON at the far right. Use actual passing speeds when available without inventing continuous coverage. Keep fixed headings, a scrolling body, per-row eligibility reasons and empty-state guidance to Replay & Qualify. Each action opens the existing name and save dialogs for that row alone.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-098": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "rationale": "Desktop-only Remove Header Format, Header Preview, Export Headers and Selected Kernels sidebar from Export Profile. Preserve existing header serialization APIs for other callers. Keep JSON filename validation, explicit overwrite confirmation, atomic commit and failure cleanup; show actionable save errors.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-001": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-002": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-003": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-006": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-007": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-008": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-009": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-010": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-011": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-012": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-013": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-014": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-015": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-016": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-017": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-018": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-019": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-020": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-021": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-023": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-024": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-028": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-029": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-030": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-031": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-032": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-033": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-034": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-035": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-036": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-037": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-038": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-039": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-041": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-042": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-043": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-046": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-047": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-048": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-050": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-051": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-052": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-053": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-054": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-055": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-056": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-057": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-059": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-060": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-061": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-062": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-063": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-064": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-065": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-066": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-067": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-068": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-069": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-070": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-071": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-072": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-073": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-074": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-075": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-076": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-077": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-078": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-079": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-080": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-081": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-082": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-083": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-084": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-085": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-086": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-087": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-088": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-089": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-090": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-091": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-092": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-093": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-094": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-095": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  },
  "AC-096": {
    "evidence_claims": [
      "host-semantics"
    ],
    "rationale": "Explicitly retired cross-project obligation: inspect desktop change scope only; no target behavior or physical evidence claim.",
    "contract_dimensions": [],
    "execution_changes": [],
    "scenario_layers": {}
  }
}
```

## Technical Contract

The existing desktop JSON version-1 contract remains unchanged: one frozen qualified dual-IMU FIR/Ridge per file, selected numeric precision, current-to-past lag order and explicit input/output axes, as-recorded calibration assumptions, preprocessing, residual, strict score > threshold detector and provenance. The desktop owns name/file dialogs and atomic UTF-8 writing. The controller owns current-result lookup and eligibility, independent of prior row selection. Firmware support policies and defaults are not inferred.

## Relationships

Current desktop obligations are REQ/AC-004,005,022,025,026,027,040,044,045,049,058,097,098. DEC-094 supersedes earlier cross-project delivery scope; retained DEC/DISC history records earlier discussion and is not current acceptance scope.

## Out of Scope

Firmware JSON import, Web configuration, Apply/Save, ESP32 memory/storage/timing design, telemetry and physical-device verification. No removal of existing desktop learning or header serializer APIs. No new JSON schema version.

## Integrated Architecture Contract

Preserve existing module owners and dependencies: StudioController in studio_application maps frozen profile_export-owned SemanticProfile to desktop_adapter QML rows and JSON file operations. No new module, named type, thread or state owner; existing dialog state is reused. Update architecture manifest descriptions and render generated views through architecture_cli.

## RAM Budget Proposal — PP-001

Excluded from this desktop-only specification by explicit user instruction. Earlier proposal discussion is retained in history; no RAM budget is required or adopted by this delivery.

## Acceptance Crosswalk

The active desktop acceptance IDs match their same-numbered requirement IDs. Existing desktop JSON regression tests cover serialization and file safety; new QML/controller cases cover page-local discoverability, exact row identity, metadata, empty states and eligibility. Prior 96-item cross-project planning is superseded for this scope; no target evidence is claimed.

## Open Decisions

None.

## Routing/Gates

User explicitly instructs continue execution of desktop JSON export and the presented kernel-list UI. Verify the active desktop SPEC, formatting, architecture design/development gates and desktop regressions. Firmware checks are out of scope, not substituted by desktop evidence.

## Question Record

```json
{
  "question_id": "Q-004",
  "history": [
    {
      "action": "revise",
      "question": {
        "id": "Q-004",
        "version": 8,
        "question": "第一版 ESP32 是否只保留一個可使用的模型，換模型時由網頁匯入新 JSON，驗證成功後再替換？",
        "options": [],
        "kind": "open-text"
      },
      "source_ref": "current-user-message response-annotations[1]",
      "user_text": "我不懂這個問題情境，沒有其他選項?"
    }
  ],
  "failed_surfaces": {}
}
```

## Revision History

| Revision | Date | Summary |
|---|---|---|
| 1 | 2026-09-16 | Record parameter direction and separate project-local specification ownership; open deployment decisions. |
| Next | 2026-09-16 | Record accepted workflow and factual questions; JSON and validation details remain proposals. |

| Next | 2026-09-16 | Confirm JSON exchange; explain runtime checks and application-owned 1024-byte setting envelope. |

| Next | 2026-09-16 | Confirm one complete model per JSON; distinguish storage wrapper bytes from signal envelope samples. |

| Next | 2026-09-16 | Select multiple persisted models and one active model; preserve unresolved capacity and activation rules. |

| Next | 2026-09-16 | Adopt no-reboot Apply with explicit post-Apply IMU stop; reopen exact lifecycle details. |

| Next | 2026-09-16 | Correct post-Apply stop to collision judgment; record current lack of independent detector disable controls. |

| Next | 2026-09-16 | Reference TCP update quiescence; distinguish physical acquisition resume from publication remaining stopped. |

| Next | 2026-09-16 | Add independent collision and acceleration-warning switches, preserving unresolved persistence and lifecycle details. |

| Next | 2026-09-16 | Adopt two Web checkboxes with Orientation-equivalent Draft/Apply/Save and saved boot state. |

| Next | 2026-09-16 | Explicitly reaffirm switch persistence as device configuration; defaults question remains unanswered. |

| Next | 2026-09-16 | Confirm both switches default enabled; preserve saved false values and define missing-field migration. |

| Next | 2026-09-16 | Confirm collision-model scope and preserve independent acceleration-warning settings on all model operations. |

| Next | 2026-09-16 | Confirm model Apply success resumes acquisition, preserves warning settings and leaves collision disabled until explicit re-enable. |

| Next | 2026-09-16 | Reject model input-rate mismatch before mutation and require explanatory model/current Hz values. |

| Next | 2026-09-16 | Retain original collision method and add Web collision-model selection with exclusive execution. |

| Next | 2026-09-16 | One selector entry per loadable artifact with rate; hide unloadable artifacts, distinguish current-rate mismatch. |

| Next | 2026-09-16 | Selected-model load failure selects original algorithm while collision detection remains disabled. |

| Next | 2026-09-16 | Automatic original-method runtime application during disabled fallback; active-alarm question remains open. |

| Next | 2026-09-16 | Disabled collision detection lets an already-triggered alarm finish without retrigger or record deletion. |

| Next | 2026-09-16 | Deleting applied model automatically applies original algorithm while preserving collision-enable value. |

| Next | 2026-09-16 | Repair saved selection on deletion; load failure now preserves collision-enable state. |

| Next | 2026-09-16 | New-model import stores and lists without changing active collision method or switch values. |

| Next | 2026-09-16 | Confirm same-name replacement prompt and editable export model name; default naming remains open. |

| Next | 2026-09-16 | Stable model default name and separately editable model name/JSON filename. |

| Next | 2026-09-16 | Running model replacement stores new parameters and waits for manual Apply; Web indicates pending version. |

| Next | 2026-09-16 | Preserve old applied model and pending replacement across restart until manual Apply. |

| Next | 2026-09-16 | Include all three families; reopen pre-Apply reboot-version decision and clarify exchange content/storage/RAM roles. |

| Next | 2026-09-16 | Resolve reopened boot policy: load latest stored parameters; old runtime persists only until Apply or restart. |

| Next | 2026-09-16 | Preserve verified model precision and distinguish admission checks from unverified target-resource claims. |

| Next | 2026-09-16 | User judges deployment suitability; remove automatic resource/support-envelope admission, retain actual operation errors. |

| Next | 2026-09-16 | Store model JSON in Flash and parse execution parameters at Apply or boot. |

| Next | 2026-09-16 | Single-IMU input source is fixed to the trained/exported internal or external selection. |

| Next | 2026-09-16 | Imported collision threshold is JSON baseline multiplied by a device-controlled multiplier; source arbitration remains open. |

| Next | 2026-09-16 | Imported-model multiplier uses last effective operation; preserve original collision control semantics separately. |

| Next | 2026-09-16 | One shared multiplier persists across imported-model switching; baseline follows the selected model. |

| Next | 2026-09-16 | Boot restores saved shared multiplier; initial knob read establishes position baseline only. |

| Next | 2026-09-16 | Knob multipliers 0.50..4.25 in 0.25 steps, preserving existing selector position numbering. |

| Next | 2026-09-16 | Remote multiplier accepts representable finite positive values without knob range/step restrictions. |

| Next | 2026-09-16 | Reuse existing collision-setting field and CANopen object with algorithm-dependent interpretation. |

| Next | 2026-09-16 | Confirm default imported-model multiplier 1.0; preserve saved values. |

| Next | 2026-09-16 | Retain common numeric setting across algorithm switches; resolve invalid-destination value separately. |

| Next | 2026-09-16 | Convert retained legacy zero to model multiplier 1.0 with Web notice; preserve transaction and Save behavior. |

| Next | 2026-09-16 | Retain software qualification gate for JSON export across supported model families. |

| Next | 2026-09-16 | Distinguish model names by letter case; preserve exact-name replacement behavior. |

| Next | 2026-09-16 | Allow qualified already-filtered single-IMU deployment with unchanged preprocessing assumptions. |

| Next | 2026-09-16 | Suspend collision-specific processing while disabled; reset and warm up on re-enable. |

| Next | 2026-09-16 | Consolidate confirmed decisions into complete artifact, lifecycle and verification contracts; resolve OD-002 through OD-006 without product changes. |
| 94 | 2026-09-16 | Reopened before clarification: 使用者要求繼續UI與程式架構討論；保留功能契約，補齊桌面匯出與env_sensing Web操作配置及設計責任。尚未授權實作。 |

| Next | 2026-09-16 | Reopen detailed UI and architecture design at user request; keep accepted functional contracts. |

| Next | 2026-09-16 | Add dedicated Web Collision Models management page; retain operational controls in Device Configuration. |

| Next | 2026-09-16 | Hide and retain original-only collision settings while selecting an imported model. |

| Next | 2026-09-16 | Adopt individual model export dialogs; discuss Web model-parameter visibility separately. |

| Next | 2026-09-16 | Confine model summary to Device Configuration; no full parameter viewer. |

| Next | 2026-09-17 | Adopt complete collision-algorithm callback dispatch; preserve independent warning and existing lifecycle rules. |

| Next | 2026-09-17 | Require bool-only collision callback result; retain warm-up/readiness inside each algorithm. |

| Next | 2026-09-17 | Use one common collision callback invocation site with available single-source or paired input; resolve Q-048 through user clarification. |

| Next | 2026-09-17 | Separate algorithm initialize/reset/execute; retain parameters across reset and share implementation by family. |

| Next | 2026-09-17 | Single above-threshold score triggers; multiplier-only updates preserve runtime and apply next evaluation. |

| Next | 2026-09-17 | Supply coherent per-computation setting snapshots from the common device-setting authority. |

| Next | 2026-09-17 | Each algorithm privately owns filter/history/warm-up state; outer orchestration uses lifecycle operations. |

| Next | 2026-09-17 | Select lifecycle callback table with opaque instance identity and coherent binding. |

| Next | 2026-09-17 | No inactive model RAM cache; record user-reported tight RAM and separate transient switch peak design. |

| Next | 2026-09-17 | Release old model after preflight/quiescence and before loading new runtime; retain accepted fallback rules. |

| Next | 2026-09-17 | Stream model JSON with bounded scratch directly into final arrays; preserve validation and precision. |

| Next | 2026-09-17 | Add algorithm-owned destroy callback for retired and partially initialized model resources. |

| Next | 2026-09-17 | Pause IMU for model import and restore prior acquisition/function state; keep applied model unchanged. |

| Next | 2026-09-17 | Show inline import-pause explanation and explicit action without a redundant pause modal. |

| Next | 2026-09-17 | Correct model UI to Device Configuration only; import immediately displays summary; withdraw separate-page navigation question. |

| Next | 2026-09-17 | Use two model summaries: imported/selected preview and actual applied model; selection refreshes the preview. |

| Next | 2026-09-17 | No manual Cancel Import action; preserve terminal-failure cleanup and prior-state restoration. |

| Next | 2026-09-17 | Directly expand the model section; resolve UI composition decisions while retaining concrete architecture work. |

| Next | 2026-09-17 | Keep all collision algorithms inside the existing component with separate files and private state. |

| Next | 2026-09-17 | Separate model-storage responsibility from device-configuration storage while sharing Flash coordination. |

| Next | 2026-09-17 | Derive model catalog from committed JSON metadata without a separate persistent index. |

| Next | 2026-09-17 | Retain original force calibration read-only while an imported model is applied. |

| Next | 2026-09-17 | Reject model switch during active original calibration collection without discarding work. |

| Next | 2026-09-17 | Reject competing model Apply and deletion during import without queueing. |

| Next | 2026-09-17 | Fall back to original algorithm on actual non-finite model computation, preserving enable state. |

| Next | 2026-09-17 | Replace runtime numeric-fault fallback with collision disable, retained model, and abnormal logging. |

| Next | 2026-09-17 | Adopt structured process status plus error code; supersede bool-only callback restriction. |

| Next | 2026-09-17 | Place independent model storage under Device Management; retain Flash and cross-parent orchestration boundaries. |

| Next | 2026-09-17 | Separate model-parameter validation/loading from model storage after clarifying their distinct responsibilities. |

| Next | 2026-09-17 | Place parameter validation/loading under Sensor Pipeline alongside collision, coordinated by their parent. |

| Next | 2026-09-17 | Algorithm allocates final parameter RAM; parent-mediated loader fills it and owning lifecycle cleans partial failures. |

| Next | 2026-09-17 | Reuse 536/540 for model score/effective threshold; mark other legacy collision registers inapplicable and preserve supported signal output. |

| Next | 2026-09-17 | Keep 536/540 output Float32 while preserving native model calculation precision and explicit output-range invalidity. |

| Next | 2026-09-17 | Use binary quiet-NaN missing-output marker while keeping model Error handling and independent valid signal output separate. |

| Next | 2026-09-17 | Keep model score and effective-threshold telemetry coherent with the same evaluation. |

| Next | 2026-09-17 | Retain existing last-frame downsample selection for model score/threshold telemetry. |

| Next | 2026-09-17 | Add integrated architecture review draft with flow, boundary, type/state ownership and dependency mappings. |

| Next | 2026-09-17 | User accepts integrated design; close logical design questions, consolidate current rules and prepare both canonical specifications. |
| 174 | 2026-09-21 | Reopened before clarification: User requests synchronization: FIR/Ridge-only ESP32 deployment, reusable fixed-capacity RAM, supported history choices; capacity unresolved; restore separate firmware contract under non-conflicting identity. |
| 181 | 2026-09-21 | Reopened before clarification: Bind the user-selected desktop JSON delivery continuation to the current task; preserve DEC-091 and all requirements. |
| 182 | 2026-09-22 | Reopened before clarification: User requests Export Profile kernel rows, required metadata and per-row JSON export; remove Header Format and Export Headers. Recover previously omitted UI discussion without treating assistant suggestions as adopted requirements. |

## Current Specification

See Problem, Solution, Requirements and Acceptance Criteria above.

## Decision History

See Decisions, Discussion Context and the sourced Discussion History below.

## Pending Discussion

None.

## Completeness Gaps

None.

<!-- spec-audit:start -->
## Discussion History

- user-spec-review-20260921: 我想確認軟體spec跟韌體的spec；唯讀核對目前文件與最近FIR-only固定RAM決策差異
- 01a0c35a-f51b-72a3-9394-ff212f3939a7: 執行桌面端 JSON 匯出，
- 01a0c35a-f51b-72a3-9394-ff212f3939a7: User desktop-only execution scope was reconciled in DEC-091 and DISC-096, with firmware RAM decisions remaining in firmware. SPEC confirmed and continuation bound to current task. No product changes. Managed execution admission is still being diagnosed; local venv resolves yaml dependency, but runtime verification matrix is missing.
- 01a0c364-7ddb-7cb1-8309-6737802bf033: 開始執行 SPEC-0039
- 01a0c364-7ddb-7cb1-8309-6737802bf033: User explicitly requests 開始執行 SPEC-0039 for the unchanged confirmed desktop JSON export scope. No new requirements. Proceed through current-scope validation preparation and implementation.
- user:01a0c6d2-2051-7b23-b2da-271b6992fb8f:execute-ui: 開始執行
- user:01a0c6e1-3f04-7e23-8fbe-6bbdb153c03d:continue-desktop: 只要處理軟體輸出JSON；韌體匯入、ESP32記憶體配置及裝置驗證這些不需要。繼續執行

### Source and Revision Audit

```jsonl
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"fe6177f824506fbad1ff2d8c921a803ed4d5bdade22e6ba3c9bfe39ab0ba0fb4","event_type":"start","event_version":1,"open_decisions":["OD-001: User workflow and transfer entry point.","OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence."],"previous_event_hash":null,"previous_snapshot_hash":null,"recorded_at":"2026-09-16T00:53:21.790189+00:00","relationships":[],"revision":1,"snapshot_hash":"c1a65685f9c906cf3067958d345665bd0260fe5a1a1a35f7698556edfe7218fb","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"fc11f7ea4b27219e98cd536488d91522e789f9368fee58c4f0c250ba5db4e0e2","event_type":"reconcile","event_version":1,"open_decisions":["OD-001: User workflow and transfer entry point.","OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","Q-001@2"],"previous_event_hash":"fe6177f824506fbad1ff2d8c921a803ed4d5bdade22e6ba3c9bfe39ab0ba0fb4","previous_snapshot_hash":"c1a65685f9c906cf3067958d345665bd0260fe5a1a1a35f7698556edfe7218fb","recorded_at":"2026-09-16T00:54:38.525936+00:00","relationships":[],"revision":2,"snapshot_hash":"905f72ecf56b411fcc876727c22aa5295ccb5d04998dc10cc11325fb0931bf87","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-003","DEC-003","DISC-002","DISC-003","REQ-003"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-003","DEC-003","DISC-002","DISC-003","REQ-003"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"6fb6866ff9e060b3d7c5b1b73d7bc1380f92263af1a61f0aa17bb4412b6d5f1a","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence."],"previous_event_hash":"fc11f7ea4b27219e98cd536488d91522e789f9368fee58c4f0c250ba5db4e0e2","previous_snapshot_hash":"905f72ecf56b411fcc876727c22aa5295ccb5d04998dc10cc11325fb0931bf87","recorded_at":"2026-09-16T02:16:02.438725+00:00","relationships":[],"revision":3,"snapshot_hash":"b1ec6b53f4a37fc9e9a9ecfdc08127952b4b62c2ee7c2339cc9f2c4bbc30c7f6","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"76a60848075bea02dc4ebce683730419cb50337bd6c0e863b5ce18c508513b94","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","Q-002@4"],"previous_event_hash":"6fb6866ff9e060b3d7c5b1b73d7bc1380f92263af1a61f0aa17bb4412b6d5f1a","previous_snapshot_hash":"b1ec6b53f4a37fc9e9a9ecfdc08127952b4b62c2ee7c2339cc9f2c4bbc30c7f6","recorded_at":"2026-09-16T02:16:45.386004+00:00","relationships":[],"revision":4,"snapshot_hash":"60e14b82fb3b57d015679e20f04e353d8879d52fe4740b8cb7599d5de4747806","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-004","DEC-004","DISC-004","DISC-005","REQ-001","REQ-004"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-004","DEC-004","DISC-004","DISC-005","REQ-004"],"changed_ids":["REQ-001"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"e6f1b4d1f83d2806adb1887b0a507221277c73d7afcda5500505c9b0945c75e9","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence."],"previous_event_hash":"76a60848075bea02dc4ebce683730419cb50337bd6c0e863b5ce18c508513b94","previous_snapshot_hash":"60e14b82fb3b57d015679e20f04e353d8879d52fe4740b8cb7599d5de4747806","recorded_at":"2026-09-16T02:46:39.454151+00:00","relationships":[],"revision":5,"snapshot_hash":"3eaa1a1246c1bbb7b838f62bd0d2babbb104ba723022d2e7880885997c234241","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"952c94e1efe3663140992bf5984c9f2595ef0000f3da82316d6d63cbff548996","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","Q-003@6"],"previous_event_hash":"e6f1b4d1f83d2806adb1887b0a507221277c73d7afcda5500505c9b0945c75e9","previous_snapshot_hash":"3eaa1a1246c1bbb7b838f62bd0d2babbb104ba723022d2e7880885997c234241","recorded_at":"2026-09-16T02:47:32.858444+00:00","relationships":[],"revision":6,"snapshot_hash":"42f5b08663146dfd42db6404da12f7325ab53752f20e0ef4a486b32e1fc5d84a","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-005","DEC-005","DISC-006","DISC-007","REQ-005"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-005","DEC-005","DISC-006","DISC-007","REQ-005"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4a6737c83f3222e92776ab9d91d87c92b6e2ae3c1acc63f40bca2b82a5de20a7","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence."],"previous_event_hash":"952c94e1efe3663140992bf5984c9f2595ef0000f3da82316d6d63cbff548996","previous_snapshot_hash":"42f5b08663146dfd42db6404da12f7325ab53752f20e0ef4a486b32e1fc5d84a","recorded_at":"2026-09-16T02:53:01.334647+00:00","relationships":[],"revision":7,"snapshot_hash":"400ade5844d6ed00303539d5a2b62ac2beacf6e9879878f16800a0f18cd3d0eb","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4e69445b94a04321dea06474aecea1abf11749e632d6817b10081e237193071d","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","Q-004@8"],"previous_event_hash":"4a6737c83f3222e92776ab9d91d87c92b6e2ae3c1acc63f40bca2b82a5de20a7","previous_snapshot_hash":"400ade5844d6ed00303539d5a2b62ac2beacf6e9879878f16800a0f18cd3d0eb","recorded_at":"2026-09-16T02:53:52.300433+00:00","relationships":[],"revision":8,"snapshot_hash":"ba26bc9a5e3b3365f2bd921e90a8917253ed6c66cd4f79c5f759f3d70ae06368","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"6c14992c77b663cbcfff65250be080261e0fd5188f074cade4657562ffa7655b","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","Q-004@9"],"previous_event_hash":"4e69445b94a04321dea06474aecea1abf11749e632d6817b10081e237193071d","previous_snapshot_hash":"ba26bc9a5e3b3365f2bd921e90a8917253ed6c66cd4f79c5f759f3d70ae06368","recorded_at":"2026-09-16T02:57:56.687136+00:00","relationships":[],"revision":9,"snapshot_hash":"97c884801fbbc46523989cfc93aeb4024e28c30d1042bbba391f0d1133a9cdc6","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-006","DEC-006","DISC-008","REQ-006"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-006","DEC-006","DISC-008","REQ-006"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"cfcbaf075333da285a79fe50f996e3c1bdcde45a4ee076b92de1c41979fb69f2","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence."],"previous_event_hash":"6c14992c77b663cbcfff65250be080261e0fd5188f074cade4657562ffa7655b","previous_snapshot_hash":"97c884801fbbc46523989cfc93aeb4024e28c30d1042bbba391f0d1133a9cdc6","recorded_at":"2026-09-16T03:01:18.909108+00:00","relationships":[],"revision":10,"snapshot_hash":"b4dffc9137d14a771f9a2e12fdf1aebea8346cd8f6e61fac3f0107cb4d617aea","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4518bf490de9bcfeb0cd30c536f74dc333bc6a87595aa738a1794b0265397770","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","Q-005@11"],"previous_event_hash":"cfcbaf075333da285a79fe50f996e3c1bdcde45a4ee076b92de1c41979fb69f2","previous_snapshot_hash":"b4dffc9137d14a771f9a2e12fdf1aebea8346cd8f6e61fac3f0107cb4d617aea","recorded_at":"2026-09-16T03:02:19.884235+00:00","relationships":[],"revision":11,"snapshot_hash":"155dd28578d6fcb05c82c410563d9b492e5f31fe09c2e4843f1510bc1ae55c9b","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-007","DEC-007","DISC-009","REQ-007"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-007","DEC-007","DISC-009","REQ-007"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"bd0804b7f3595c2b8ae4b02415a7c1d10238c09f371fbf683c386a379cb06aa0","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Clarify what stopping IMU means, transition sequencing and restart behavior."],"previous_event_hash":"4518bf490de9bcfeb0cd30c536f74dc333bc6a87595aa738a1794b0265397770","previous_snapshot_hash":"155dd28578d6fcb05c82c410563d9b492e5f31fe09c2e4843f1510bc1ae55c9b","recorded_at":"2026-09-16T03:10:04.496694+00:00","relationships":[],"revision":12,"snapshot_hash":"4ae8091bfab4d463bf20cfa41e25c4b5a89533d26a1d936b12401854d408f11f","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"5b3b9353e77e75c4573178da91f164dbcc8477db2f4009c3539b898aa5aae7de","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Clarify what stopping IMU means, transition sequencing and restart behavior.","Q-006@13"],"previous_event_hash":"bd0804b7f3595c2b8ae4b02415a7c1d10238c09f371fbf683c386a379cb06aa0","previous_snapshot_hash":"4ae8091bfab4d463bf20cfa41e25c4b5a89533d26a1d936b12401854d408f11f","recorded_at":"2026-09-16T03:10:55.451556+00:00","relationships":[],"revision":13,"snapshot_hash":"d4f3e084f607883069df6536349a53c948da0e1a97155b74f395cb4398de5ccd","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-007","DEC-008","DISC-010","REQ-007"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["DEC-008","DISC-010"],"changed_ids":["AC-007","REQ-007"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"2d49d99cd13772bf437bf7cc5f51b0215534a53c1ab23867e5e89b02cd00b168","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Collision judgment stop/restart, transition sequencing, detector/output state, and independent acceleration-warning behavior."],"previous_event_hash":"5b3b9353e77e75c4573178da91f164dbcc8477db2f4009c3539b898aa5aae7de","previous_snapshot_hash":"d4f3e084f607883069df6536349a53c948da0e1a97155b74f395cb4398de5ccd","recorded_at":"2026-09-16T03:20:42.367021+00:00","relationships":[],"revision":14,"snapshot_hash":"33569179a31ba5a7cb70ce35c9ef8fdcdb8100e9d964618827d59dac54f66d67","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-007","DISC-011","REQ-007"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["DISC-011"],"changed_ids":["AC-007","REQ-007"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"ec705101a752df6c91908a692b1986349c0bdefdef969000dee815b4b07e2011","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Post-Apply acquisition resumes versus remains stopped; collision judgment stop/restart, transition sequencing, detector/output state, and independent acceleration-warning behavior."],"previous_event_hash":"2d49d99cd13772bf437bf7cc5f51b0215534a53c1ab23867e5e89b02cd00b168","previous_snapshot_hash":"33569179a31ba5a7cb70ce35c9ef8fdcdb8100e9d964618827d59dac54f66d67","recorded_at":"2026-09-16T03:22:26.292236+00:00","relationships":[],"revision":15,"snapshot_hash":"200e94a1ae4af333956fac0ea393d37fcac8a64436b357735e797e69b78d6fbf","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"a67c7420b32cce8316d8d82ada53a8b9611dda06279118e51e8f3cb664c9627e","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Post-Apply acquisition resumes versus remains stopped; collision judgment stop/restart, transition sequencing, detector/output state, and independent acceleration-warning behavior.","Q-007@16"],"previous_event_hash":"ec705101a752df6c91908a692b1986349c0bdefdef969000dee815b4b07e2011","previous_snapshot_hash":"200e94a1ae4af333956fac0ea393d37fcac8a64436b357735e797e69b78d6fbf","recorded_at":"2026-09-16T03:23:20.658694+00:00","relationships":[],"revision":16,"snapshot_hash":"2ceeec7f4eb21dbd701090f01f83e61c3db0d42b6ecf0d3705732ff0e73f4848","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-008","DEC-009","DISC-012","REQ-008"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-008","DEC-009","DISC-012","REQ-008"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0db4c8c47604cc1c64b83959125711731a7714bb604415e8ee4d0dbf84b38d81","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Post-Apply acquisition resumes versus remains stopped; collision judgment stop/restart, transition sequencing, detector/output state, and independent acceleration-warning behavior.","OD-006: Switch persistence, boot defaults, legacy/model collision scope, UI/transports and whether switch settings belong outside model JSON."],"previous_event_hash":"a67c7420b32cce8316d8d82ada53a8b9611dda06279118e51e8f3cb664c9627e","previous_snapshot_hash":"2ceeec7f4eb21dbd701090f01f83e61c3db0d42b6ecf0d3705732ff0e73f4848","recorded_at":"2026-09-16T03:29:10.989314+00:00","relationships":[],"revision":17,"snapshot_hash":"4d574445506f6f2498583c2c6f23728282632a11a9b3148bb04ef749d17d373a","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"9a960868fa0eac06b0d016c9b5dae0facd084e5dda599f21bd6ba87104db9537","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Post-Apply acquisition resumes versus remains stopped; collision judgment stop/restart, transition sequencing, detector/output state, and independent acceleration-warning behavior.","OD-006: Switch persistence, boot defaults, legacy/model collision scope, UI/transports and whether switch settings belong outside model JSON.","Q-008@18"],"previous_event_hash":"0db4c8c47604cc1c64b83959125711731a7714bb604415e8ee4d0dbf84b38d81","previous_snapshot_hash":"4d574445506f6f2498583c2c6f23728282632a11a9b3148bb04ef749d17d373a","recorded_at":"2026-09-16T03:30:28.131401+00:00","relationships":[],"revision":18,"snapshot_hash":"c87551d21e2ba3720e2be4206459c9a9b6037eccf15cd29183ea13deb45044b4","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-009","DEC-010","DISC-013","REQ-009"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-009","DEC-010","DISC-013","REQ-009"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"94fe5028b76db7d591ab4a9a200eb16aacd28a784094a6def00d9e869f14e8af","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Post-Apply acquisition resumes versus remains stopped; collision judgment stop/restart, transition sequencing, detector/output state, and independent acceleration-warning behavior.","OD-006: Switch default values and old-configuration migration, legacy/model collision scope, remaining transports and model-JSON separation details. Web checkbox and Draft/Apply/Save persistence are confirmed."],"previous_event_hash":"9a960868fa0eac06b0d016c9b5dae0facd084e5dda599f21bd6ba87104db9537","previous_snapshot_hash":"c87551d21e2ba3720e2be4206459c9a9b6037eccf15cd29183ea13deb45044b4","recorded_at":"2026-09-16T03:32:19.869050+00:00","relationships":[],"revision":19,"snapshot_hash":"bf344f18cab244fd6a1239245bf2afe207729b5e022678ebe4e87bc66ce48eb7","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"c4e7865fafbe6fd0380c3a11d3c08b06e060638522a1013575b34434055eba02","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Post-Apply acquisition resumes versus remains stopped; collision judgment stop/restart, transition sequencing, detector/output state, and independent acceleration-warning behavior.","OD-006: Switch default values and old-configuration migration, legacy/model collision scope, remaining transports and model-JSON separation details. Web checkbox and Draft/Apply/Save persistence are confirmed.","Q-009@20"],"previous_event_hash":"94fe5028b76db7d591ab4a9a200eb16aacd28a784094a6def00d9e869f14e8af","previous_snapshot_hash":"bf344f18cab244fd6a1239245bf2afe207729b5e022678ebe4e87bc66ce48eb7","recorded_at":"2026-09-16T03:33:05.700480+00:00","relationships":[],"revision":20,"snapshot_hash":"19382c9dd1f0a06f1b0431165bb47594e4aed642c7e8566cb33b3013325b5087","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["DISC-014"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["DISC-014"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"8b21cdcbda9ae79d26a1fd22709c90f1f59e5312f2eeb4fe95e977b69ad512bb","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Post-Apply acquisition resumes versus remains stopped; collision judgment stop/restart, transition sequencing, detector/output state, and independent acceleration-warning behavior.","OD-006: Switch default values and old-configuration migration, legacy/model collision scope, remaining transports and model-JSON separation details. Web checkbox and Draft/Apply/Save persistence are confirmed.","Q-009@20"],"previous_event_hash":"c4e7865fafbe6fd0380c3a11d3c08b06e060638522a1013575b34434055eba02","previous_snapshot_hash":"19382c9dd1f0a06f1b0431165bb47594e4aed642c7e8566cb33b3013325b5087","recorded_at":"2026-09-16T03:34:52.429166+00:00","relationships":[],"revision":21,"snapshot_hash":"0b8719dca1b2940313fc4c2aefdc2519fde02dcb824beb792284429703909fde","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-010","DEC-011","DISC-015","REQ-010"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-010","DEC-011","DISC-015","REQ-010"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"ecb87ac0884d508998d3b0c1f3c2eec081b0b693bf653b197a7481f28920d9bc","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Post-Apply acquisition resumes versus remains stopped; collision judgment stop/restart, transition sequencing, detector/output state, and independent acceleration-warning behavior.","OD-006: Legacy/model collision scope, remaining transports and model-JSON separation details. Web checkboxes, Draft/Apply/Save persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"8b21cdcbda9ae79d26a1fd22709c90f1f59e5312f2eeb4fe95e977b69ad512bb","previous_snapshot_hash":"0b8719dca1b2940313fc4c2aefdc2519fde02dcb824beb792284429703909fde","recorded_at":"2026-09-16T03:37:15.729971+00:00","relationships":[],"revision":22,"snapshot_hash":"0c8282b2d111a633b700041bf6cb67953acc1ddbd83629dc4fbd5a2ce0722ffa","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"15b828d9c71e9b3bd4ab71ba6dbe6305980a984886d3a8e0cc379808785e81ff","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Post-Apply acquisition resumes versus remains stopped; collision judgment stop/restart, transition sequencing, detector/output state, and independent acceleration-warning behavior.","OD-006: Legacy/model collision scope, remaining transports and model-JSON separation details. Web checkboxes, Draft/Apply/Save persistence and enabled defaults/missing-field migration are confirmed.","Q-010@23"],"previous_event_hash":"ecb87ac0884d508998d3b0c1f3c2eec081b0b693bf653b197a7481f28920d9bc","previous_snapshot_hash":"0c8282b2d111a633b700041bf6cb67953acc1ddbd83629dc4fbd5a2ce0722ffa","recorded_at":"2026-09-16T03:38:00.694011+00:00","relationships":[],"revision":23,"snapshot_hash":"61d0e09633f5aa59b666a733bb71b2349be0ae9384a5a368bf206c544fab06f4","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-011","DEC-012","DISC-016","REQ-011"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-011","DEC-012","DISC-016","REQ-011"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"39c34558be88b4cd637ed95e2b679ca36c68c90daedbe1a1d706c62d8bd5b932","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Post-Apply acquisition resumes versus remains stopped; collision judgment stop/restart, transition sequencing, detector/output state. Acceleration-warning settings remain independent under REQ-011.","OD-006: Legacy/model collision scope, remaining transports and model-JSON separation details. Web checkboxes, Draft/Apply/Save persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"15b828d9c71e9b3bd4ab71ba6dbe6305980a984886d3a8e0cc379808785e81ff","previous_snapshot_hash":"61d0e09633f5aa59b666a733bb71b2349be0ae9384a5a368bf206c544fab06f4","recorded_at":"2026-09-16T03:41:57.928163+00:00","relationships":[],"revision":24,"snapshot_hash":"1f9756a1cbf1c663971988d96d6a04a0aa4908045da79b48630870eb0a038272","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"3de487278e98f5e97cac8978563ac70bb6a0e23b23673c7ee505680bc6d7bb5e","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Post-Apply acquisition resumes versus remains stopped; collision judgment stop/restart, transition sequencing, detector/output state. Acceleration-warning settings remain independent under REQ-011.","OD-006: Legacy/model collision scope, remaining transports and model-JSON separation details. Web checkboxes, Draft/Apply/Save persistence and enabled defaults/missing-field migration are confirmed.","Q-011@25"],"previous_event_hash":"39c34558be88b4cd637ed95e2b679ca36c68c90daedbe1a1d706c62d8bd5b932","previous_snapshot_hash":"1f9756a1cbf1c663971988d96d6a04a0aa4908045da79b48630870eb0a038272","recorded_at":"2026-09-16T03:42:53.844287+00:00","relationships":[],"revision":25,"snapshot_hash":"7409a9abc53fc6e4802c172b416034a97eab6bf5fa726a61b75b2f928b6a23be","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-007","AC-012","DEC-013","DISC-017","REQ-007","REQ-012"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-012","DEC-013","DISC-017","REQ-012"],"changed_ids":["AC-007","REQ-007"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"e3868d78d133789ed33a82e9d416f6f5e516078fddf9e22462d729fc81eb3d4c","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness and existing-output handling. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Legacy/model collision scope, remaining transports and model-JSON separation details. Web checkboxes, Draft/Apply/Save persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"3de487278e98f5e97cac8978563ac70bb6a0e23b23673c7ee505680bc6d7bb5e","previous_snapshot_hash":"7409a9abc53fc6e4802c172b416034a97eab6bf5fa726a61b75b2f928b6a23be","recorded_at":"2026-09-16T03:53:53.519141+00:00","relationships":[],"revision":26,"snapshot_hash":"1d612f7a5165543d6e0fce78a5c5100af9763ec4882183ef813f76967e32fb12","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"e216836eda640f4aca9d06fa6dd0b872f13caa93a27b704f2cf268b651a39788","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness and existing-output handling. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Legacy/model collision scope, remaining transports and model-JSON separation details. Web checkboxes, Draft/Apply/Save persistence and enabled defaults/missing-field migration are confirmed.","Q-012@27"],"previous_event_hash":"e3868d78d133789ed33a82e9d416f6f5e516078fddf9e22462d729fc81eb3d4c","previous_snapshot_hash":"1d612f7a5165543d6e0fce78a5c5100af9763ec4882183ef813f76967e32fb12","recorded_at":"2026-09-16T03:55:03.974130+00:00","relationships":[],"revision":27,"snapshot_hash":"6d219081e0830843a4339476af5ee6a45eb1fba48e7a574d09fd67e94435f80c","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-013","DEC-014","DISC-018","REQ-013"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-013","DEC-014","DISC-018","REQ-013"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"7543835fc7120c0c5d3e29fcfe1f6768ea4a354851d9456af88d1a7c72468356","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness and existing-output handling. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Legacy/model collision scope, remaining transports and model-JSON separation details. Web checkboxes, Draft/Apply/Save persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"e216836eda640f4aca9d06fa6dd0b872f13caa93a27b704f2cf268b651a39788","previous_snapshot_hash":"6d219081e0830843a4339476af5ee6a45eb1fba48e7a574d09fd67e94435f80c","recorded_at":"2026-09-16T03:59:39.959089+00:00","relationships":[],"revision":28,"snapshot_hash":"4b44e2ead6dcd9b1d4230aae83f877b328004faf702296cbb06c7e5fa163014e","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4c2cc81e836048de47bf4e4a682d01b60bba2e2e54313adc62e5c3d96cf97e38","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness and existing-output handling. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Legacy/model collision scope, remaining transports and model-JSON separation details. Web checkboxes, Draft/Apply/Save persistence and enabled defaults/missing-field migration are confirmed.","Q-013@29"],"previous_event_hash":"7543835fc7120c0c5d3e29fcfe1f6768ea4a354851d9456af88d1a7c72468356","previous_snapshot_hash":"4b44e2ead6dcd9b1d4230aae83f877b328004faf702296cbb06c7e5fa163014e","recorded_at":"2026-09-16T04:00:36.223178+00:00","relationships":[],"revision":29,"snapshot_hash":"dcba7f45d8616b5a01610f99a2aa0e3ef8e2dc265c691572d86411d23ed3fa2e","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-014","DEC-015","DISC-019","REQ-014"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-014","DEC-015","DISC-019","REQ-014"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"7dac6fff52ef0bea910cbf9a5f8acc49d4964da6da8bdcc5f3e89aeb27c67950","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness and existing-output handling. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, missing-reference behavior, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"4c2cc81e836048de47bf4e4a682d01b60bba2e2e54313adc62e5c3d96cf97e38","previous_snapshot_hash":"dcba7f45d8616b5a01610f99a2aa0e3ef8e2dc265c691572d86411d23ed3fa2e","recorded_at":"2026-09-16T04:08:20.890714+00:00","relationships":[],"revision":30,"snapshot_hash":"dc6aac0ff937ff45f45a0612609c72da37767493883e3193fee367890fa0ba56","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"bf6de8db7e8185ca721b9aaa31df56c2eb4df65ccee90fb8505f1679f23a9b50","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness and existing-output handling. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, missing-reference behavior, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-014@31"],"previous_event_hash":"7dac6fff52ef0bea910cbf9a5f8acc49d4964da6da8bdcc5f3e89aeb27c67950","previous_snapshot_hash":"dc6aac0ff937ff45f45a0612609c72da37767493883e3193fee367890fa0ba56","recorded_at":"2026-09-16T04:09:40.650139+00:00","relationships":[],"revision":31,"snapshot_hash":"a9e73d0c8c66df30f0e207abf1a9d2f6fa0623d4dbba1afd4642bfa6069efbb1","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-015","DEC-016","DISC-020","REQ-014","REQ-015"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-015","DEC-016","DISC-020","REQ-015"],"changed_ids":["REQ-014"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"c1bd7dc370980bf0e6bc38537a3ae08761f556b244b550eea9baf28eebf4544e","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness and existing-output handling. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, missing-reference behavior, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"bf6de8db7e8185ca721b9aaa31df56c2eb4df65ccee90fb8505f1679f23a9b50","previous_snapshot_hash":"a9e73d0c8c66df30f0e207abf1a9d2f6fa0623d4dbba1afd4642bfa6069efbb1","recorded_at":"2026-09-16T04:19:50.066906+00:00","relationships":[],"revision":32,"snapshot_hash":"2df1ce28987998a8e6859b8fc4e83f0dcf44a78b109490ba3b705b9933d2bad1","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"a248d93c2596c69d6e0371d28595633861a0fbe28d667afb54ab91b3b8124168","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness and existing-output handling. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, missing-reference behavior, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-015@33"],"previous_event_hash":"c1bd7dc370980bf0e6bc38537a3ae08761f556b244b550eea9baf28eebf4544e","previous_snapshot_hash":"2df1ce28987998a8e6859b8fc4e83f0dcf44a78b109490ba3b705b9933d2bad1","recorded_at":"2026-09-16T04:20:45.724091+00:00","relationships":[],"revision":33,"snapshot_hash":"f4675bc3f6cd600af509e73d07534df715e6136b8fbbfc7f79be71c148c6200c","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-016","DEC-017","DISC-021","REQ-015","REQ-016"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-016","DEC-017","DISC-021","REQ-016"],"changed_ids":["REQ-015"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"09380f43124c0f23b5f778853aa996a410d9ca5960b422b2191da34aa30aedee","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness and existing-output handling. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"a248d93c2596c69d6e0371d28595633861a0fbe28d667afb54ab91b3b8124168","previous_snapshot_hash":"f4675bc3f6cd600af509e73d07534df715e6136b8fbbfc7f79be71c148c6200c","recorded_at":"2026-09-16T04:25:42.047650+00:00","relationships":[],"revision":34,"snapshot_hash":"acdbb76ab64e9ba5b7588c69b96fa23ec31a9160b0ab9ffe29473c34dcc2bb70","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"2b48d098b1fc12d4739a88971058b555b2eed24cf05ea395c876e85efb18a48d","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness and existing-output handling. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-016@35"],"previous_event_hash":"09380f43124c0f23b5f778853aa996a410d9ca5960b422b2191da34aa30aedee","previous_snapshot_hash":"acdbb76ab64e9ba5b7588c69b96fa23ec31a9160b0ab9ffe29473c34dcc2bb70","recorded_at":"2026-09-16T04:28:39.263726+00:00","relationships":[],"revision":35,"snapshot_hash":"034ed15774fabe34541fa600fa4150731c7b8c3951f09f7d57ddbc4ed41cabae","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-016","DEC-017","DISC-022","REQ-016"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["DISC-022"],"changed_ids":["AC-016","DEC-017","REQ-016"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"2c2d3f9dec48c2515c7218c727ff44dcf7222ed54c2e23584d6f5536c3202eeb","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness and existing-output handling. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-016@35"],"previous_event_hash":"2b48d098b1fc12d4739a88971058b555b2eed24cf05ea395c876e85efb18a48d","previous_snapshot_hash":"034ed15774fabe34541fa600fa4150731c7b8c3951f09f7d57ddbc4ed41cabae","recorded_at":"2026-09-16T05:28:10.474248+00:00","relationships":[],"revision":36,"snapshot_hash":"3aceb03cb07dade3ffaffeef3a08a195f853288210cee1cd4ec01d450d17fca4","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-017","DEC-018","DISC-023","REQ-008","REQ-017"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-017","DEC-018","DISC-023","REQ-017"],"changed_ids":["REQ-008"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"c01bcc03204eaa159331443c1a350eaeaab74eb491b2dfc9bba87d999f036dbc","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"2c2d3f9dec48c2515c7218c727ff44dcf7222ed54c2e23584d6f5536c3202eeb","previous_snapshot_hash":"3aceb03cb07dade3ffaffeef3a08a195f853288210cee1cd4ec01d450d17fca4","recorded_at":"2026-09-16T05:46:25.578721+00:00","relationships":[],"revision":37,"snapshot_hash":"04c51c0ca42f1cc5be9a5aed661f6eacdc7457926b10c674d9578eab6e342263","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"d982af0a9fdc220983611aad43eefc93fb79d9dd564309748189c817b5cf2f88","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Successful Apply resumes acquisition with collision disabled until explicit checkbox Apply; acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-017@38"],"previous_event_hash":"c01bcc03204eaa159331443c1a350eaeaab74eb491b2dfc9bba87d999f036dbc","previous_snapshot_hash":"04c51c0ca42f1cc5be9a5aed661f6eacdc7457926b10c674d9578eab6e342263","recorded_at":"2026-09-16T05:47:12.119003+00:00","relationships":[],"revision":38,"snapshot_hash":"60e04a07bdc718952fc099b0f80df50434a0bb70b7f4f0e6ec866d34826be1b8","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-007","AC-012","AC-018","DEC-019","DISC-024","REQ-006","REQ-007","REQ-012","REQ-018"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-018","DEC-019","DISC-024","REQ-018"],"changed_ids":["AC-007","AC-012","REQ-006","REQ-007","REQ-012"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"628e2f8e5a5612ecceb063be6f13381efb21345ab11add982f2bc0987bb1a269","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; deletion-driven application under REQ-018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"d982af0a9fdc220983611aad43eefc93fb79d9dd564309748189c817b5cf2f88","previous_snapshot_hash":"60e04a07bdc718952fc099b0f80df50434a0bb70b7f4f0e6ec866d34826be1b8","recorded_at":"2026-09-16T05:54:41.386791+00:00","relationships":[],"revision":39,"snapshot_hash":"bda8dbea3a7ddc754044eba4fa185761b171db9928ac0b5304d98031e9a7973b","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"9b64cd55b3a154f5da8dcc931634e6b8e91a0b8d135a9a57489f9ae8876af89a","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; deletion-driven application under REQ-018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-018@40"],"previous_event_hash":"628e2f8e5a5612ecceb063be6f13381efb21345ab11add982f2bc0987bb1a269","previous_snapshot_hash":"bda8dbea3a7ddc754044eba4fa185761b171db9928ac0b5304d98031e9a7973b","recorded_at":"2026-09-16T05:56:00.746991+00:00","relationships":[],"revision":40,"snapshot_hash":"ac90b0a688133f592bebf56188049ee9753e5fe14ff845f9bc29ba9326b5a754","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-007","AC-012","AC-016","AC-019","DEC-017","DEC-019","DEC-020","DISC-025","REQ-007","REQ-012","REQ-016","REQ-018","REQ-019"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-019","DEC-020","DISC-025","REQ-019"],"changed_ids":["AC-007","AC-012","AC-016","DEC-017","DEC-019","REQ-007","REQ-012","REQ-016","REQ-018"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"af2d8728fd765e1f410ea9e03fd5acc6400a22192f2e9810919d27b140a14c11","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"9b64cd55b3a154f5da8dcc931634e6b8e91a0b8d135a9a57489f9ae8876af89a","previous_snapshot_hash":"ac90b0a688133f592bebf56188049ee9753e5fe14ff845f9bc29ba9326b5a754","recorded_at":"2026-09-16T06:00:38.152092+00:00","relationships":[],"revision":41,"snapshot_hash":"b9642706f041445e0b7da70cbf009539271ce5f145f21e574eccb0b3c72448d0","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"058c2fe028a5fce4d6d6619a3d82fd49f3608299b41901419e4dec150bd579eb","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-019@42"],"previous_event_hash":"af2d8728fd765e1f410ea9e03fd5acc6400a22192f2e9810919d27b140a14c11","previous_snapshot_hash":"b9642706f041445e0b7da70cbf009539271ce5f145f21e574eccb0b3c72448d0","recorded_at":"2026-09-16T06:01:33.553820+00:00","relationships":[],"revision":42,"snapshot_hash":"cdc3e228851cb6b1a363260ded088689ab8bf5aa23c33deb8abe20406e7e3306","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-020","DEC-021","DISC-026","REQ-003","REQ-006","REQ-020"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-020","DEC-021","DISC-026","REQ-020"],"changed_ids":["REQ-003","REQ-006"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"3bae591ac8965584f66c3b15af29d313f815753746fcf07172ee0fcdafab6954","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"058c2fe028a5fce4d6d6619a3d82fd49f3608299b41901419e4dec150bd579eb","previous_snapshot_hash":"cdc3e228851cb6b1a363260ded088689ab8bf5aa23c33deb8abe20406e7e3306","recorded_at":"2026-09-16T06:13:41.611167+00:00","relationships":[],"revision":43,"snapshot_hash":"77763dda14654ed855e21f9890715be529653da6f4eb72f88587c9247dcad243","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"e23686c0f55ac90d019fae954f7d8d8c3e4a022ebd55f74948d69ded85bd5c3f","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-020@44"],"previous_event_hash":"3bae591ac8965584f66c3b15af29d313f815753746fcf07172ee0fcdafab6954","previous_snapshot_hash":"77763dda14654ed855e21f9890715be529653da6f4eb72f88587c9247dcad243","recorded_at":"2026-09-16T06:14:33.706202+00:00","relationships":[],"revision":44,"snapshot_hash":"3728646a7ad4792268e87c7741fc4ec4013ecadf5b4a790b60fd6ac7919d9f09","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-021","AC-022","DEC-022","DEC-023","DISC-027","REQ-021","REQ-022"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-021","AC-022","DEC-022","DEC-023","DISC-027","REQ-021","REQ-022"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"d2f12ffa1b1bb6749141753231de270ef0fa502f320b5901406c6912cc8a126d","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; default model name and shared name validation.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence; replacing an already-applied model after same-name confirmation.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"e23686c0f55ac90d019fae954f7d8d8c3e4a022ebd55f74948d69ded85bd5c3f","previous_snapshot_hash":"3728646a7ad4792268e87c7741fc4ec4013ecadf5b4a790b60fd6ac7919d9f09","recorded_at":"2026-09-16T06:21:11.415637+00:00","relationships":[],"revision":45,"snapshot_hash":"b64b3582e28c5ffd3fb94dad68f4898596934351f58855208363d47124629cd7","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"ffe3f10f8856d064ba3bbb167ff285f369ad3f44b79c5986a764505db623ffcb","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; default model name and shared name validation.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence; replacing an already-applied model after same-name confirmation.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-021@46"],"previous_event_hash":"d2f12ffa1b1bb6749141753231de270ef0fa502f320b5901406c6912cc8a126d","previous_snapshot_hash":"b64b3582e28c5ffd3fb94dad68f4898596934351f58855208363d47124629cd7","recorded_at":"2026-09-16T06:22:29.066600+00:00","relationships":[],"revision":46,"snapshot_hash":"531c5457cb375d267738a461b73706659f10f0c0c2fa46a58068f38b8df68e0c","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-022","DEC-023","DISC-028","REQ-022"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["DISC-028"],"changed_ids":["AC-022","DEC-023","REQ-022"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"363a4334d7ebd50d851d4d41820d91e1b99ccf1369b69ba965967d58f35f6122","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence; replacing an already-applied model after same-name confirmation.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"ffe3f10f8856d064ba3bbb167ff285f369ad3f44b79c5986a764505db623ffcb","previous_snapshot_hash":"531c5457cb375d267738a461b73706659f10f0c0c2fa46a58068f38b8df68e0c","recorded_at":"2026-09-16T06:25:37.211694+00:00","relationships":[],"revision":47,"snapshot_hash":"902dffb7b5d58e39009d1abc846c3655c45c598449ed34477961d353d6a3974b","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"1c46886fb672c0aa4de5d76fcecc7aa4d2aa0d1a7ba2e7d0eb645e09180f2295","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence; replacing an already-applied model after same-name confirmation.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-022@48"],"previous_event_hash":"363a4334d7ebd50d851d4d41820d91e1b99ccf1369b69ba965967d58f35f6122","previous_snapshot_hash":"902dffb7b5d58e39009d1abc846c3655c45c598449ed34477961d353d6a3974b","recorded_at":"2026-09-16T06:26:26.885702+00:00","relationships":[],"revision":48,"snapshot_hash":"d92e20f075fb1aac92e7c6d6abc0b9b1c9622ac22bf23b615cdcdc6a3eb3f0b5","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-021","AC-023","DEC-024","DISC-029","REQ-021","REQ-023"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-023","DEC-024","DISC-029","REQ-023"],"changed_ids":["AC-021","REQ-021"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"cc8edaf971d89790489b567c4090b5099f35bf6f67bbfab0954f28cb85125d8d","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence; restart behavior for a stored replacement that has not yet been manually applied. Running-model replacement timing is resolved by REQ-023.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"1c46886fb672c0aa4de5d76fcecc7aa4d2aa0d1a7ba2e7d0eb645e09180f2295","previous_snapshot_hash":"d92e20f075fb1aac92e7c6d6abc0b9b1c9622ac22bf23b615cdcdc6a3eb3f0b5","recorded_at":"2026-09-16T06:30:38.503310+00:00","relationships":[],"revision":49,"snapshot_hash":"b8673d82fe97c14766cec1246038fe80a9e23d75185a91dbe1faa14f40b175d0","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"33cf8a3ef4f3793b600c3281048569c591424566a9beedaf25429defcb011dd5","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence; restart behavior for a stored replacement that has not yet been manually applied. Running-model replacement timing is resolved by REQ-023.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-023@50"],"previous_event_hash":"cc8edaf971d89790489b567c4090b5099f35bf6f67bbfab0954f28cb85125d8d","previous_snapshot_hash":"b8673d82fe97c14766cec1246038fe80a9e23d75185a91dbe1faa14f40b175d0","recorded_at":"2026-09-16T06:31:21.981516+00:00","relationships":[],"revision":50,"snapshot_hash":"030badba8008ab8e2e3767810dd54eb21bf09fd432a8201b356cb5d52c1346c8","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-024","DEC-025","DISC-030","REQ-023","REQ-024"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-024","DEC-025","DISC-030","REQ-024"],"changed_ids":["REQ-023"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"ddf6c588dd3b9276eca81b9444f83a2b207e1deee55d27a33d46f85dfdec8f2b","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence. Replacement activation and pre-Apply restart behavior are resolved by REQ-023/024; capacity must include old and pending artifacts.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"33cf8a3ef4f3793b600c3281048569c591424566a9beedaf25429defcb011dd5","previous_snapshot_hash":"030badba8008ab8e2e3767810dd54eb21bf09fd432a8201b356cb5d52c1346c8","recorded_at":"2026-09-16T06:34:51.466999+00:00","relationships":[],"revision":51,"snapshot_hash":"7ac9baf325b810374c63a409ec38b154bdefe797a50ecd29d7d7e50e8e127c1e","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"d92bbfc5c4c542de66e4eb4b4eab2e738c7e2944ab900e38fa06dc9ef7a7dc48","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: First-release model families and compatibility boundary.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence. Replacement activation and pre-Apply restart behavior are resolved by REQ-023/024; capacity must include old and pending artifacts.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-024@52"],"previous_event_hash":"ddf6c588dd3b9276eca81b9444f83a2b207e1deee55d27a33d46f85dfdec8f2b","previous_snapshot_hash":"7ac9baf325b810374c63a409ec38b154bdefe797a50ecd29d7d7e50e8e127c1e","recorded_at":"2026-09-16T06:35:36.138041+00:00","relationships":[],"revision":52,"snapshot_hash":"a8037fc6dcce5c4b294a2f027ebe376b28a2324bfbc4721f2bffa0bee0b5154b","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-024","AC-025","DEC-025","DEC-026","DISC-031","REQ-023","REQ-024","REQ-025"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-025","DEC-026","DISC-031","REQ-025"],"changed_ids":["AC-024","DEC-025","REQ-023","REQ-024"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"28ad25962c944b92c9809ac21ab814a832ea17da072175d30d47d3d1c48d21f8","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family compatibility/resource boundaries; first-release coverage of all three families is confirmed by REQ-025.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior, persistent version retention and corresponding capacity are REOPENED under REQ-024 at user request.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"d92bbfc5c4c542de66e4eb4b4eab2e738c7e2944ab900e38fa06dc9ef7a7dc48","previous_snapshot_hash":"a8037fc6dcce5c4b294a2f027ebe376b28a2324bfbc4721f2bffa0bee0b5154b","recorded_at":"2026-09-16T06:37:58.515540+00:00","relationships":[],"revision":53,"snapshot_hash":"52fa0d91dac2726bf04a8efd0840f2cbdaf2fee48064bc8c7ad88c604a38086c","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"ee6adcf1077e460bd10fcc9a489f74ecc30a10ca203a1f2719422f96a3fc0242","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family compatibility/resource boundaries; first-release coverage of all three families is confirmed by REQ-025.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior, persistent version retention and corresponding capacity are REOPENED under REQ-024 at user request.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-025@54"],"previous_event_hash":"28ad25962c944b92c9809ac21ab814a832ea17da072175d30d47d3d1c48d21f8","previous_snapshot_hash":"52fa0d91dac2726bf04a8efd0840f2cbdaf2fee48064bc8c7ad88c604a38086c","recorded_at":"2026-09-16T06:39:18.906569+00:00","relationships":[],"revision":54,"snapshot_hash":"b5460ec33e0643c24e8c7bd9b20331133960915a08b982902ed6f4029a5c181a","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-024","DEC-025","DISC-032","REQ-021","REQ-023","REQ-024"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["DISC-032"],"changed_ids":["AC-024","DEC-025","REQ-021","REQ-023","REQ-024"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"44f488923258e6f01d59c2dae6ce32ebd652b65153fb554020cc628a3f46042c","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family compatibility/resource boundaries; first-release coverage of all three families is confirmed by REQ-025.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Safe-update storage overhead remains to be bounded.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"ee6adcf1077e460bd10fcc9a489f74ecc30a10ca203a1f2719422f96a3fc0242","previous_snapshot_hash":"b5460ec33e0643c24e8c7bd9b20331133960915a08b982902ed6f4029a5c181a","recorded_at":"2026-09-16T06:43:16.690801+00:00","relationships":[],"revision":55,"snapshot_hash":"f77766098429e3dfb94a7de1d5bd76be614c9203af486005efedad83961912d7","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"5cbedeb651bc7042c1b46b981eb4b931dd401d64f34586f12c2fb3a01d366e8b","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family compatibility/resource boundaries; first-release coverage of all three families is confirmed by REQ-025.","OD-003: Shared parameter schema, numeric representation, preprocessing and detector semantics; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Safe-update storage overhead remains to be bounded.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-026@56"],"previous_event_hash":"44f488923258e6f01d59c2dae6ce32ebd652b65153fb554020cc628a3f46042c","previous_snapshot_hash":"f77766098429e3dfb94a7de1d5bd76be614c9203af486005efedad83961912d7","recorded_at":"2026-09-16T06:44:31.107757+00:00","relationships":[],"revision":56,"snapshot_hash":"dd4b53fb3bfd06e92094820610dd12e8516926fcc51125a703c4e54ff58a90de","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-026","DEC-027","DISC-033","REQ-026"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-026","DEC-027","DISC-033","REQ-026"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"cf8afd418d34873f69452e0e432ae349e18d5016c76f98bd5fb5d3ec898032a4","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family compatibility/resource boundaries; first-release coverage of all three families is confirmed by REQ-025.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Safe-update storage overhead remains to be bounded.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"5cbedeb651bc7042c1b46b981eb4b931dd401d64f34586f12c2fb3a01d366e8b","previous_snapshot_hash":"dd4b53fb3bfd06e92094820610dd12e8516926fcc51125a703c4e54ff58a90de","recorded_at":"2026-09-16T06:48:03.726893+00:00","relationships":[],"revision":57,"snapshot_hash":"05c311172697acf42eea71cb4d6484234420dcc896d781e461ffc2143b1ebb44","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4906db68669fdc9c9809dcf530e2b73642d4768c3892f9669ee1a3eef3c6d689","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family compatibility/resource boundaries; first-release coverage of all three families is confirmed by REQ-025.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Safe-update storage overhead remains to be bounded.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-027@58"],"previous_event_hash":"cf8afd418d34873f69452e0e432ae349e18d5016c76f98bd5fb5d3ec898032a4","previous_snapshot_hash":"05c311172697acf42eea71cb4d6484234420dcc896d781e461ffc2143b1ebb44","recorded_at":"2026-09-16T06:49:16.922009+00:00","relationships":[],"revision":58,"snapshot_hash":"336e0b928345e421893bf105fb4ffa686fbff2c4d7af6aefea14d464106904af","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-025","AC-026","AC-027","DEC-027","DEC-028","DISC-034","REQ-025","REQ-026","REQ-027"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-027","DEC-028","DISC-034","REQ-027"],"changed_ids":["AC-025","AC-026","DEC-027","REQ-025","REQ-026"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"14383bf809f681ae50fa04997e8a18fa24d20331b29ccfa81d9f64ec46c02b55","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"4906db68669fdc9c9809dcf530e2b73642d4768c3892f9669ee1a3eef3c6d689","previous_snapshot_hash":"336e0b928345e421893bf105fb4ffa686fbff2c4d7af6aefea14d464106904af","recorded_at":"2026-09-16T06:55:18.062812+00:00","relationships":[],"revision":59,"snapshot_hash":"65f109c3bf33b93961873a3306c3cd5df83be084009a1a39de7b328bb89490b1","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"10eaac8fe9e48757ad3e501999da6760c94eee107a652be99235193240f36f22","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Firmware capacity, persistence, activation, failure recovery and verification evidence. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-028@60"],"previous_event_hash":"14383bf809f681ae50fa04997e8a18fa24d20331b29ccfa81d9f64ec46c02b55","previous_snapshot_hash":"65f109c3bf33b93961873a3306c3cd5df83be084009a1a39de7b328bb89490b1","recorded_at":"2026-09-16T06:56:39.407720+00:00","relationships":[],"revision":60,"snapshot_hash":"4f6e3adc4509554ad8aaaf2382fbf99b6bab9ac6ee15ddc5f2735c9e766b3ea8","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-004","AC-028","DEC-029","DISC-035","REQ-004","REQ-028"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-028","DEC-029","DISC-035","REQ-028"],"changed_ids":["AC-004","REQ-004"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"8a5184eec1b44944173585c5d19d2c277c8e61f15767fc3405750cd1849d29bb","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"10eaac8fe9e48757ad3e501999da6760c94eee107a652be99235193240f36f22","previous_snapshot_hash":"4f6e3adc4509554ad8aaaf2382fbf99b6bab9ac6ee15ddc5f2735c9e766b3ea8","recorded_at":"2026-09-16T06:59:27.031816+00:00","relationships":[],"revision":61,"snapshot_hash":"26f3d6e51b1f21a5e7246aaae99e216bf9321ae76add3c1f5b46b7cb87a7f011","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"b7d8771906623c560b2830b7419b08f41400278b2b7ce991365c9ed8f88d542f","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-029@62"],"previous_event_hash":"8a5184eec1b44944173585c5d19d2c277c8e61f15767fc3405750cd1849d29bb","previous_snapshot_hash":"26f3d6e51b1f21a5e7246aaae99e216bf9321ae76add3c1f5b46b7cb87a7f011","recorded_at":"2026-09-16T07:00:11.712182+00:00","relationships":[],"revision":62,"snapshot_hash":"bb02f32c63820406d0be67d5edb74975a14a900612d9da2b74f1bced143b0476","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-029","DEC-030","DISC-036","REQ-029"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-029","DEC-030","DISC-036","REQ-029"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"c3aef8a5122eaef3422002d1305046e4c72fbb0176e18213f6168fdcc2a1cc9e","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"b7d8771906623c560b2830b7419b08f41400278b2b7ce991365c9ed8f88d542f","previous_snapshot_hash":"bb02f32c63820406d0be67d5edb74975a14a900612d9da2b74f1bced143b0476","recorded_at":"2026-09-16T07:04:54.846042+00:00","relationships":[],"revision":63,"snapshot_hash":"cff042cd1385ab30d294cf9d30873ea42aa2019a7d13e7ab3d80e8446a55629e","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4a5548e93d612017898bc0b62f1e71a73ee9d0d6d556ca04bcaad93752c59ec5","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-030@64"],"previous_event_hash":"c3aef8a5122eaef3422002d1305046e4c72fbb0176e18213f6168fdcc2a1cc9e","previous_snapshot_hash":"cff042cd1385ab30d294cf9d30873ea42aa2019a7d13e7ab3d80e8446a55629e","recorded_at":"2026-09-16T07:05:48.146362+00:00","relationships":[],"revision":64,"snapshot_hash":"12cc1b87a8d9bf9f02562659055a85a8cb8747b224f0eccd0b00cc7a4aac27e0","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-030","DEC-031","DISC-037","REQ-030"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-030","DEC-031","DISC-037","REQ-030"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"fa1ceeab6d74a3ceceaa53675e54e6fa0300107bc2fcd8c7c454d054f5e2850f","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier control-source arbitration, knob mapping and allowed/default values, per-model/global ownership, boot persistence and compatibility with original collision mode and existing CANopen objects. Base-times-multiplier formula is confirmed by REQ-030."],"previous_event_hash":"4a5548e93d612017898bc0b62f1e71a73ee9d0d6d556ca04bcaad93752c59ec5","previous_snapshot_hash":"12cc1b87a8d9bf9f02562659055a85a8cb8747b224f0eccd0b00cc7a4aac27e0","recorded_at":"2026-09-16T07:11:46.528611+00:00","relationships":[],"revision":65,"snapshot_hash":"a77b12a56bbf1f002598c91370c162915a0c3aa8004427e8914096c09037b95e","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"237adb94bd5c7b6042b12049b29db831a5775cd9573d8eef0430933eaa804e64","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier control-source arbitration, knob mapping and allowed/default values, per-model/global ownership, boot persistence and compatibility with original collision mode and existing CANopen objects. Base-times-multiplier formula is confirmed by REQ-030.","Q-031@66"],"previous_event_hash":"fa1ceeab6d74a3ceceaa53675e54e6fa0300107bc2fcd8c7c454d054f5e2850f","previous_snapshot_hash":"a77b12a56bbf1f002598c91370c162915a0c3aa8004427e8914096c09037b95e","recorded_at":"2026-09-16T07:12:33.074520+00:00","relationships":[],"revision":66,"snapshot_hash":"dfb7ad7194b502c94b6ccac751969bae66f2e132ba0aa700c068573b933151d0","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-031","DEC-032","DISC-038","REQ-030","REQ-031"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-031","DEC-032","DISC-038","REQ-031"],"changed_ids":["REQ-030"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"b777fc3663b89433f93dc2e392de6f98f0396d83e8928ace6f9da52a905a6fdb","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier knob mapping and allowed/default values, per-model/global ownership, boot persistence and exact CANopen representation. Formula and last-effective-operation arbitration are confirmed by REQ-030/031. Original collision control semantics remain separate."],"previous_event_hash":"237adb94bd5c7b6042b12049b29db831a5775cd9573d8eef0430933eaa804e64","previous_snapshot_hash":"dfb7ad7194b502c94b6ccac751969bae66f2e132ba0aa700c068573b933151d0","recorded_at":"2026-09-16T07:40:12.680675+00:00","relationships":[],"revision":67,"snapshot_hash":"062846b41c1e346c865b7a16acf77c14733663c2d6167f01a900da03e992773a","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"34523bc04c71455dc5f1849a52d558278a0553a9b1f4a4d787f5cb223916b2dd","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier knob mapping and allowed/default values, per-model/global ownership, boot persistence and exact CANopen representation. Formula and last-effective-operation arbitration are confirmed by REQ-030/031. Original collision control semantics remain separate.","Q-032@68"],"previous_event_hash":"b777fc3663b89433f93dc2e392de6f98f0396d83e8928ace6f9da52a905a6fdb","previous_snapshot_hash":"062846b41c1e346c865b7a16acf77c14733663c2d6167f01a900da03e992773a","recorded_at":"2026-09-16T07:41:24.539929+00:00","relationships":[],"revision":68,"snapshot_hash":"6650c0bad38ff0f542815161b7ec8abcaf30f40066a00219c900fbb4f33ab7dd","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-032","DEC-033","DISC-039","REQ-030","REQ-032"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-032","DEC-033","DISC-039","REQ-032"],"changed_ids":["REQ-030"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"73ef546b7229288489892c5104e5f8fe231adcc71a482fe88bc56eb05752cf9d","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier knob mapping and allowed/default values, boot initialization/persistence and exact CANopen representation. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate."],"previous_event_hash":"34523bc04c71455dc5f1849a52d558278a0553a9b1f4a4d787f5cb223916b2dd","previous_snapshot_hash":"6650c0bad38ff0f542815161b7ec8abcaf30f40066a00219c900fbb4f33ab7dd","recorded_at":"2026-09-16T07:46:27.810003+00:00","relationships":[],"revision":69,"snapshot_hash":"8a6f3859ad28b4ea6d025c7f589b2fadeb17746500b62a7ca48f3d09398807d8","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"b28dea97785e4778616f885d5d2756e818f1874584955fff9922ac609be8b0ac","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier knob mapping and allowed/default values, boot initialization/persistence and exact CANopen representation. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate.","Q-033@70"],"previous_event_hash":"73ef546b7229288489892c5104e5f8fe231adcc71a482fe88bc56eb05752cf9d","previous_snapshot_hash":"8a6f3859ad28b4ea6d025c7f589b2fadeb17746500b62a7ca48f3d09398807d8","recorded_at":"2026-09-16T07:47:16.018918+00:00","relationships":[],"revision":70,"snapshot_hash":"0378afdc94f512fe632e13bde9d5b4bac3653f1bcec020bc57f975522f6394ef","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-033","DEC-034","DISC-040","REQ-030","REQ-032","REQ-033"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-033","DEC-034","DISC-040","REQ-033"],"changed_ids":["REQ-030","REQ-032"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"622eedfae71694cef6f44f57a330087bb2df65dde082d4994cf31435b757ae45","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier knob mapping, allowed/default values and exact CANopen representation. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate."],"previous_event_hash":"b28dea97785e4778616f885d5d2756e818f1874584955fff9922ac609be8b0ac","previous_snapshot_hash":"0378afdc94f512fe632e13bde9d5b4bac3653f1bcec020bc57f975522f6394ef","recorded_at":"2026-09-16T07:49:33.741949+00:00","relationships":[],"revision":71,"snapshot_hash":"53c1c8f3eccc8668438bb9e2c89e7e1ffe5ba451691ee1e8000b065273728e12","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"5c96dc17ca9f19f58d19c58a19c8de1c1d92836ca6e904d0534b6bbe8d042833","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier knob mapping, allowed/default values and exact CANopen representation. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate.","Q-034@72"],"previous_event_hash":"622eedfae71694cef6f44f57a330087bb2df65dde082d4994cf31435b757ae45","previous_snapshot_hash":"53c1c8f3eccc8668438bb9e2c89e7e1ffe5ba451691ee1e8000b065273728e12","recorded_at":"2026-09-16T07:50:56.799327+00:00","relationships":[],"revision":72,"snapshot_hash":"15546f1d1981b5005f9690ba3ac80d82d73dfc6ca523b0a27b0c766bc063f419","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-034","DEC-035","DISC-041","REQ-030","REQ-034"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-034","DEC-035","DISC-041","REQ-034"],"changed_ids":["REQ-030"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0dc10e4a3ab54cdbc1b2c6ce867e517926f989ec234c64c5b1c5a2a3959bf2c3","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Web/CANopen multiplier allowed values, missing/default value and exact CANopen representation. Knob mapping is confirmed by REQ-034. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate."],"previous_event_hash":"5c96dc17ca9f19f58d19c58a19c8de1c1d92836ca6e904d0534b6bbe8d042833","previous_snapshot_hash":"15546f1d1981b5005f9690ba3ac80d82d73dfc6ca523b0a27b0c766bc063f419","recorded_at":"2026-09-16T08:01:29.725734+00:00","relationships":[],"revision":73,"snapshot_hash":"3ca5bb1bd7e640d30e33e2b281a4b40da8208a3f69575853c77a2e6aef0c454e","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"d6a07b78dbe315e6f9b5c026d93bee332f85ed8539ecb28ca3371cc5d1a26c52","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Web/CANopen multiplier allowed values, missing/default value and exact CANopen representation. Knob mapping is confirmed by REQ-034. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate.","Q-035@74"],"previous_event_hash":"0dc10e4a3ab54cdbc1b2c6ce867e517926f989ec234c64c5b1c5a2a3959bf2c3","previous_snapshot_hash":"3ca5bb1bd7e640d30e33e2b281a4b40da8208a3f69575853c77a2e6aef0c454e","recorded_at":"2026-09-16T08:02:51.720526+00:00","relationships":[],"revision":74,"snapshot_hash":"10d48e48d9b034f2c3fe7f2e91e31b2d9f99d714a2dd957d88f7d8c451dfef3d","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-035","DEC-036","DISC-042","REQ-030","REQ-034","REQ-035"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-035","DEC-036","DISC-042","REQ-035"],"changed_ids":["REQ-030","REQ-034"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"2ede41b52c7b753e67f52b340dc789a64d0ec86da55a983bb198cd215fb8adfc","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier missing/default value and exact CANopen representation. Remote value domain is confirmed by REQ-035. Knob mapping is confirmed by REQ-034. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate."],"previous_event_hash":"d6a07b78dbe315e6f9b5c026d93bee332f85ed8539ecb28ca3371cc5d1a26c52","previous_snapshot_hash":"10d48e48d9b034f2c3fe7f2e91e31b2d9f99d714a2dd957d88f7d8c451dfef3d","recorded_at":"2026-09-16T08:07:26.769532+00:00","relationships":[],"revision":75,"snapshot_hash":"c31c86df3a77c4185d99dd2e097990d1bade0ab548639ef37a18d3e3bb0d4e81","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"07e4d97cd8acfd16d5437402cdf6903bb2717ecdde53cd5326f0116acbee4db9","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier missing/default value and exact CANopen representation. Remote value domain is confirmed by REQ-035. Knob mapping is confirmed by REQ-034. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate.","Q-036@76"],"previous_event_hash":"2ede41b52c7b753e67f52b340dc789a64d0ec86da55a983bb198cd215fb8adfc","previous_snapshot_hash":"c31c86df3a77c4185d99dd2e097990d1bade0ab548639ef37a18d3e3bb0d4e81","recorded_at":"2026-09-16T08:08:44.754739+00:00","relationships":[],"revision":76,"snapshot_hash":"7d0718d565b4411bb7b46c5849cca44a40745e71bad93af4d47ce66190f2c3d1","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-036","DEC-037","DISC-043","REQ-030","REQ-036"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-036","DEC-037","DISC-043","REQ-036"],"changed_ids":["REQ-030"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"6bfa471b7053738e117b00901fcaaf57df98985d6025c70ae1aac3d83a41ccf8","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier missing/default value; CANopen representation is resolved by REQ-036 using the existing 0x2007:00 REAL32 object with algorithm-dependent meaning. Remote value domain is confirmed by REQ-035. Knob mapping is confirmed by REQ-034. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate."],"previous_event_hash":"07e4d97cd8acfd16d5437402cdf6903bb2717ecdde53cd5326f0116acbee4db9","previous_snapshot_hash":"7d0718d565b4411bb7b46c5849cca44a40745e71bad93af4d47ce66190f2c3d1","recorded_at":"2026-09-16T08:19:28.323489+00:00","relationships":[],"revision":77,"snapshot_hash":"7b916eeeee95facc91196e810d5717a6b5598b6b17d7dedb7ca645d72e99b102","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"6d5e06f3f5644ac4fd0d39892223e3d136873e69d5310ba4c48170300f9d4ada","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Multiplier missing/default value; CANopen representation is resolved by REQ-036 using the existing 0x2007:00 REAL32 object with algorithm-dependent meaning. Remote value domain is confirmed by REQ-035. Knob mapping is confirmed by REQ-034. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate.","Q-037@78"],"previous_event_hash":"6bfa471b7053738e117b00901fcaaf57df98985d6025c70ae1aac3d83a41ccf8","previous_snapshot_hash":"7b916eeeee95facc91196e810d5717a6b5598b6b17d7dedb7ca645d72e99b102","recorded_at":"2026-09-16T08:20:37.896123+00:00","relationships":[],"revision":78,"snapshot_hash":"b6f7d80d3839b0e703c14ae15fb262dea9b2996201a2150cdda832f84bf47283","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-037","DEC-038","DISC-044","REQ-030","REQ-032","REQ-033","REQ-037"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-037","DEC-038","DISC-044","REQ-037"],"changed_ids":["REQ-030","REQ-032","REQ-033"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0d1b189559b23cf2c74d457244b5fdd3612ab963675b781f45a52eaf88ecdb87","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Numeric value continuity when switching between original and imported collision algorithms through the shared setting field; missing/default multiplier is resolved by REQ-037; CANopen representation is resolved by REQ-036 using the existing 0x2007:00 REAL32 object with algorithm-dependent meaning. Remote value domain is confirmed by REQ-035. Knob mapping is confirmed by REQ-034. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate."],"previous_event_hash":"6d5e06f3f5644ac4fd0d39892223e3d136873e69d5310ba4c48170300f9d4ada","previous_snapshot_hash":"b6f7d80d3839b0e703c14ae15fb262dea9b2996201a2150cdda832f84bf47283","recorded_at":"2026-09-16T08:23:34.797063+00:00","relationships":[],"revision":79,"snapshot_hash":"046ae63269a2d40dfba6fb4f1d577f2fcfad987faece74b091d6b2bf715e9409","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"08cd8fd06848d161c62c89808773169738fcfc6fd7d91fcbf19c6486d2e7be1b","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Numeric value continuity when switching between original and imported collision algorithms through the shared setting field; missing/default multiplier is resolved by REQ-037; CANopen representation is resolved by REQ-036 using the existing 0x2007:00 REAL32 object with algorithm-dependent meaning. Remote value domain is confirmed by REQ-035. Knob mapping is confirmed by REQ-034. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate.","Q-038@80"],"previous_event_hash":"0d1b189559b23cf2c74d457244b5fdd3612ab963675b781f45a52eaf88ecdb87","previous_snapshot_hash":"046ae63269a2d40dfba6fb4f1d577f2fcfad987faece74b091d6b2bf715e9409","recorded_at":"2026-09-16T08:24:19.765250+00:00","relationships":[],"revision":80,"snapshot_hash":"7359954d42bc14e93342734f15c03cb7ebac9775eb2ac6b303cf1429983eb143","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-038","DEC-039","DISC-045","REQ-032","REQ-033","REQ-036","REQ-037","REQ-038"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-038","DEC-039","DISC-045","REQ-038"],"changed_ids":["REQ-032","REQ-033","REQ-036","REQ-037"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"c007303b295a5d448b7f83bb17edaf18274927bf8eaf00af9b1bfe5e095f94da","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Handling a retained common value invalid for the destination algorithm, particularly legacy zero when switching to an imported model. Numeric continuity is confirmed by REQ-038; missing/default multiplier is resolved by REQ-037; CANopen representation is resolved by REQ-036 using the existing 0x2007:00 REAL32 object with algorithm-dependent meaning. Remote value domain is confirmed by REQ-035. Knob mapping is confirmed by REQ-034. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate."],"previous_event_hash":"08cd8fd06848d161c62c89808773169738fcfc6fd7d91fcbf19c6486d2e7be1b","previous_snapshot_hash":"7359954d42bc14e93342734f15c03cb7ebac9775eb2ac6b303cf1429983eb143","recorded_at":"2026-09-16T08:34:35.736771+00:00","relationships":[],"revision":81,"snapshot_hash":"682e8e6b4e874c097c16fea601f37d974380d6dd6e5ec6585eb9252c2116839a","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"25b7a3a6c3bf5d9be59e26113afb85d86950094d991a938b8bce09809721cfc1","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","OD-007: Handling a retained common value invalid for the destination algorithm, particularly legacy zero when switching to an imported model. Numeric continuity is confirmed by REQ-038; missing/default multiplier is resolved by REQ-037; CANopen representation is resolved by REQ-036 using the existing 0x2007:00 REAL32 object with algorithm-dependent meaning. Remote value domain is confirmed by REQ-035. Knob mapping is confirmed by REQ-034. Boot restores saved multiplier under REQ-033. Formula, last-effective-operation arbitration and shared ownership are confirmed by REQ-030/031/032. Original collision control semantics remain separate.","Q-039@82"],"previous_event_hash":"c007303b295a5d448b7f83bb17edaf18274927bf8eaf00af9b1bfe5e095f94da","previous_snapshot_hash":"682e8e6b4e874c097c16fea601f37d974380d6dd6e5ec6585eb9252c2116839a","recorded_at":"2026-09-16T08:35:22.615972+00:00","relationships":[],"revision":82,"snapshot_hash":"0e415759992e2b196187f64989bee29edee92454c806413c88ef8ead9942c405","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-038","AC-039","DEC-040","DISC-046","REQ-038","REQ-039"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-039","DEC-040","DISC-046","REQ-039"],"changed_ids":["AC-038","REQ-038"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"da649c42eaef689400c1b993b78774904d521e90561c10deaf9e9c385a8e2ee9","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"25b7a3a6c3bf5d9be59e26113afb85d86950094d991a938b8bce09809721cfc1","previous_snapshot_hash":"0e415759992e2b196187f64989bee29edee92454c806413c88ef8ead9942c405","recorded_at":"2026-09-16T08:38:24.872073+00:00","relationships":[],"revision":83,"snapshot_hash":"4d07bd4cc63cb16efa4f8f3f2e376787796ec95b2bc8aa182f14f7dd561f1862","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"2f906cd78d5c3c7351b58562fcdce33bc2aea7b955c812288983c44389b02729","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-040@84"],"previous_event_hash":"da649c42eaef689400c1b993b78774904d521e90561c10deaf9e9c385a8e2ee9","previous_snapshot_hash":"4d07bd4cc63cb16efa4f8f3f2e376787796ec95b2bc8aa182f14f7dd561f1862","recorded_at":"2026-09-16T08:40:23.737071+00:00","relationships":[],"revision":84,"snapshot_hash":"01105dabaeabe21bd1505f1f326776a243c8c8ca885fce7b6da675716b2b00f1","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-040","DEC-041","DISC-047","REQ-040"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-040","DEC-041","DISC-047","REQ-040"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"c60ee2592c36702ade4c43d676f52a751b21ec16ee2ff2df7549fa3729700584","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"2f906cd78d5c3c7351b58562fcdce33bc2aea7b955c812288983c44389b02729","previous_snapshot_hash":"01105dabaeabe21bd1505f1f326776a243c8c8ca885fce7b6da675716b2b00f1","recorded_at":"2026-09-16T08:43:25.753605+00:00","relationships":[],"revision":85,"snapshot_hash":"a56831aedec3af2f690773e17dce3704958734459b5a63474569300ca90c5eae","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"3924de42849cb7c4f78a9285b0651ff69763b814182cb49eb2e5b8b176f7ed91","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-041@86"],"previous_event_hash":"c60ee2592c36702ade4c43d676f52a751b21ec16ee2ff2df7549fa3729700584","previous_snapshot_hash":"a56831aedec3af2f690773e17dce3704958734459b5a63474569300ca90c5eae","recorded_at":"2026-09-16T08:44:10.230419+00:00","relationships":[],"revision":86,"snapshot_hash":"7c92eb1ce8f6485315dccfac11f974216139701803326b8148e8e6e30a58004a","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-041","DEC-042","DISC-048","REQ-021","REQ-041"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-041","DEC-042","DISC-048","REQ-041"],"changed_ids":["REQ-021"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"8b1f7e915cbed224a8ddc1a032925602919c134b176648112a3851ce594b940e","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"3924de42849cb7c4f78a9285b0651ff69763b814182cb49eb2e5b8b176f7ed91","previous_snapshot_hash":"7c92eb1ce8f6485315dccfac11f974216139701803326b8148e8e6e30a58004a","recorded_at":"2026-09-16T08:48:05.395669+00:00","relationships":[],"revision":87,"snapshot_hash":"702ff48917d5cb4e0618f488f7ec55761fee8e1dcf119af58e2201cf8db51055","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"61e09746b69fa5da675019472a262c5d11da1d8a083b43117d04e49d231cf778","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-042@88"],"previous_event_hash":"8b1f7e915cbed224a8ddc1a032925602919c134b176648112a3851ce594b940e","previous_snapshot_hash":"702ff48917d5cb4e0618f488f7ec55761fee8e1dcf119af58e2201cf8db51055","recorded_at":"2026-09-16T08:50:10.396426+00:00","relationships":[],"revision":88,"snapshot_hash":"fa792eef97825ade72641d3286e7d1a3b17b2db5f69f77c283b1f814555df8a2","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-042","DEC-043","DISC-049","REQ-042"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-042","DEC-043","DISC-049","REQ-042"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"15ed5d19b40b5de8d2f64b10b314f3f85020970c23582221428db78e48eb2c4c","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"61e09746b69fa5da675019472a262c5d11da1d8a083b43117d04e49d231cf778","previous_snapshot_hash":"fa792eef97825ade72641d3286e7d1a3b17b2db5f69f77c283b1f814555df8a2","recorded_at":"2026-09-16T08:53:16.188537+00:00","relationships":[],"revision":89,"snapshot_hash":"b743561c5b4cc77d4aef4b790be2abef547de3a33c0faaa6214e48508c2cb2db","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"5a59ad67eb101197aed679f51576d847e67e131efe8a182baef6ccc5e996a38f","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed.","Q-043@90"],"previous_event_hash":"15ed5d19b40b5de8d2f64b10b314f3f85020970c23582221428db78e48eb2c4c","previous_snapshot_hash":"b743561c5b4cc77d4aef4b790be2abef547de3a33c0faaa6214e48508c2cb2db","recorded_at":"2026-09-16T08:55:01.514285+00:00","relationships":[],"revision":90,"snapshot_hash":"f38d8c3b4e03a5f7d9c4a1509f0550ac9b1198be717ce2e365cb61a8f4fba00a","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-043","DEC-044","DISC-050","REQ-012","REQ-043"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-043","DEC-044","DISC-050","REQ-043"],"changed_ids":["REQ-012"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"32fcc03d634644bcc4d91e46a3ca3fe062dc8d036b80eae47b54a89631cc33ab","event_type":"reconcile","event_version":1,"open_decisions":["OD-002: Per-family structural/input compatibility; resource suitability belongs to the user under REQ-027; first-release coverage of all three families is confirmed by REQ-025; single-IMU source is fixed by REQ-029.","OD-003: Shared parameter schema, precise numeric serialization/parity, preprocessing and detector semantics; numeric type preservation is confirmed by REQ-026; shared model-name and filename validation. Default naming is defined by REQ-022.","OD-004: Remaining firmware persistence/transaction recovery and verification details. Persistent model format is JSON under REQ-028; resource suitability belongs to the user. Current-session replacement activation is resolved by REQ-023. Pre-Apply restart behavior is resolved by REQ-024: load latest committed parameters, without permanent old-version retention solely for deferred activation. Actual update/write failures need transaction recovery; no predictive capacity admission is authorized under REQ-027.","OD-005: Failure recovery, precise quiescence/publication coordination, detector/history readiness. Existing collision-alarm output handling is resolved by REQ-017. Ordinary model Apply resumes acquisition with collision disabled until explicit checkbox Apply; automatic fallback under REQ-016/018 preserves the enable value. Acceleration warning remains independent.","OD-006: Initial/saved collision-method selection, remaining transports and model-JSON separation details. Original plus imported model selection, Web checkboxes, Draft/Apply/Save switch persistence and enabled defaults/missing-field migration are confirmed."],"previous_event_hash":"5a59ad67eb101197aed679f51576d847e67e131efe8a182baef6ccc5e996a38f","previous_snapshot_hash":"f38d8c3b4e03a5f7d9c4a1509f0550ac9b1198be717ce2e365cb61a8f4fba00a","recorded_at":"2026-09-16T08:59:48.672300+00:00","relationships":[],"revision":91,"snapshot_hash":"c383046ce8854378fecb5a1e695e7b9c187147ec283a0928ebf761051d18219f","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-007","AC-030","AC-031","AC-044","AC-045","AC-046","AC-047","AC-048","AC-049","DEC-045","REQ-001","REQ-004","REQ-006","REQ-007","REQ-008","REQ-009","REQ-012","REQ-014","REQ-022","REQ-026","REQ-035","REQ-044","REQ-045","REQ-046","REQ-047","REQ-048","REQ-049"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-044","AC-045","AC-046","AC-047","AC-048","AC-049","DEC-045","REQ-044","REQ-045","REQ-046","REQ-047","REQ-048","REQ-049"],"changed_ids":["AC-007","AC-030","AC-031","REQ-001","REQ-004","REQ-006","REQ-007","REQ-008","REQ-009","REQ-012","REQ-014","REQ-022","REQ-026","REQ-035"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"05de4521c255168959fc87ea7ae0b056fc1544806d604830efb77af759fc2830","event_type":"reconcile","event_version":1,"open_decisions":["None. User decisions are recorded in DISC-001 through DISC-050; remaining verification-plan bindings are implementation prerequisites under REQ-049."],"previous_event_hash":"32fcc03d634644bcc4d91e46a3ca3fe062dc8d036b80eae47b54a89631cc33ab","previous_snapshot_hash":"c383046ce8854378fecb5a1e695e7b9c187147ec283a0928ebf761051d18219f","recorded_at":"2026-09-16T09:05:05.325150+00:00","relationships":[],"revision":92,"snapshot_hash":"d9670ca385d8239a3742a49dd0fcf50af36afa1e2a5645ae74b32a890ce70905","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"a61441431443235af1216b8e38fdf609533004b6cdbb264c01211613bfd92680","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"05de4521c255168959fc87ea7ae0b056fc1544806d604830efb77af759fc2830","previous_snapshot_hash":"d9670ca385d8239a3742a49dd0fcf50af36afa1e2a5645ae74b32a890ce70905","recorded_at":"2026-09-16T09:05:19.504304+00:00","relationships":[],"revision":93,"snapshot_hash":"3bb28cf907dfaf1431e6ed5e73808bf67f9f9bcfa298143a186149748135a5bd","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"ba6de193d658c6cad7176ab5932e5049831a48741e65a587de498c6fd223e978","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"a61441431443235af1216b8e38fdf609533004b6cdbb264c01211613bfd92680","previous_snapshot_hash":"3bb28cf907dfaf1431e6ed5e73808bf67f9f9bcfa298143a186149748135a5bd","recorded_at":"2026-09-16T09:05:50.661750+00:00","relationships":[],"revision":93,"snapshot_hash":"d5d4522d1b6a77809f878ba74f56a751863dee8d791aeaf14463731a920176f6","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"baseline_contract_hash":"b726067911f63b9cc278b3de0fbfc979186a27220bb32f2b79ce73d6573a19db","conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"346f50275f52d74833b7a8c11a26c6285f56db14785486f91ab5da1636684531","event_type":"reopen","event_version":1,"open_decisions":[],"previous_event_hash":"ba6de193d658c6cad7176ab5932e5049831a48741e65a587de498c6fd223e978","previous_snapshot_hash":"d5d4522d1b6a77809f878ba74f56a751863dee8d791aeaf14463731a920176f6","recorded_at":"2026-09-16T09:17:08.214011+00:00","relationships":[],"revision":94,"snapshot_hash":"4d65acd234bda73ca9ea271bcf936ffe4cbc7eef51afce20f891de60955889cf","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["DISC-051"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["DISC-051"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0f4c39f3f5eba9eb9f0b5a818e7d05da2e2b3df9da160176c3e851861a44394f","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: model-management placement, export/name interaction and visible operation/state layout. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"346f50275f52d74833b7a8c11a26c6285f56db14785486f91ab5da1636684531","previous_snapshot_hash":"4d65acd234bda73ca9ea271bcf936ffe4cbc7eef51afce20f891de60955889cf","recorded_at":"2026-09-16T09:18:19.015148+00:00","relationships":[],"revision":95,"snapshot_hash":"c00ff2f0efb4a42d9f4956058fdbf4132606d8e538fd4a2cc8bd6f6f8708f7e9","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"9a85abeaa3249b61ef8f8df892e9ce5d1787c71826a90132ac3998e158c7aa39","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: model-management placement, export/name interaction and visible operation/state layout. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-044@96"],"previous_event_hash":"0f4c39f3f5eba9eb9f0b5a818e7d05da2e2b3df9da160176c3e851861a44394f","previous_snapshot_hash":"c00ff2f0efb4a42d9f4956058fdbf4132606d8e538fd4a2cc8bd6f6f8708f7e9","recorded_at":"2026-09-16T09:19:33.625649+00:00","relationships":[],"revision":96,"snapshot_hash":"a0742f1ec8e881747b0f7e79277c9a48bcc78a448b701f70c46f691083030d99","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-050","DEC-046","DISC-052","REQ-050"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-050","DEC-046","DISC-052","REQ-050"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"dc5816d76c8f0bc9ccfabc951bf6cc8e3351a33949d6b99a32af03e98e5cab33","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"9a85abeaa3249b61ef8f8df892e9ce5d1787c71826a90132ac3998e158c7aa39","previous_snapshot_hash":"a0742f1ec8e881747b0f7e79277c9a48bcc78a448b701f70c46f691083030d99","recorded_at":"2026-09-16T09:24:17.242264+00:00","relationships":[],"revision":97,"snapshot_hash":"9f9ec36a611cf5dcaf4a37c63970550a98c99f383933d5fdaf2c0cef4d4da4a8","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"3e281c232b2649784e2d9a05e72acc908f25a479043826041d44a75cd8e88580","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-045@98"],"previous_event_hash":"dc5816d76c8f0bc9ccfabc951bf6cc8e3351a33949d6b99a32af03e98e5cab33","previous_snapshot_hash":"9f9ec36a611cf5dcaf4a37c63970550a98c99f383933d5fdaf2c0cef4d4da4a8","recorded_at":"2026-09-16T09:25:11.407940+00:00","relationships":[],"revision":98,"snapshot_hash":"617c197ec831239f0bb558e74138999217c68c12121b977e9206099e5bc37caa","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-051","DEC-047","DISC-053","REQ-051"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-051","DEC-047","DISC-053","REQ-051"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"86f297ec4a2550ee139d799337a1249aa487953030d9d8ad6d147dfcbc558d54","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"3e281c232b2649784e2d9a05e72acc908f25a479043826041d44a75cd8e88580","previous_snapshot_hash":"617c197ec831239f0bb558e74138999217c68c12121b977e9206099e5bc37caa","recorded_at":"2026-09-16T09:27:45.695306+00:00","relationships":[],"revision":99,"snapshot_hash":"75e67b753eb08d2ba12c15dd60563e151a49da7d88409dc3d6d12d551d041221","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"a5cdca3eb294acf5c112d4d508a21c7ca63de033269caa256aa96c625519b5fe","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-046@100"],"previous_event_hash":"86f297ec4a2550ee139d799337a1249aa487953030d9d8ad6d147dfcbc558d54","previous_snapshot_hash":"75e67b753eb08d2ba12c15dd60563e151a49da7d88409dc3d6d12d551d041221","recorded_at":"2026-09-16T09:28:58.397098+00:00","relationships":[],"revision":100,"snapshot_hash":"94298ead795fbbcdccd9a4667c2b73fbde4ddd6485f1a36bab0f8cf77c4ca8ba","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-052","DEC-048","DISC-054","REQ-052"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-052","DEC-048","DISC-054","REQ-052"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4adfd11f8406c86daa199a529556490940d6ecabee001e6fb49e2fa4441b7f37","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"a5cdca3eb294acf5c112d4d508a21c7ca63de033269caa256aa96c625519b5fe","previous_snapshot_hash":"94298ead795fbbcdccd9a4667c2b73fbde4ddd6485f1a36bab0f8cf77c4ca8ba","recorded_at":"2026-09-16T12:19:24.565916+00:00","relationships":[],"revision":101,"snapshot_hash":"c45f761a8c7e9ae1db97a2a777c91002d2e97db97c99375755e4405b436161d0","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"82edb5f5ac2e12379391b5ecd2bcaa0fbd5cca4a7814a0bc9b17b36debefb61d","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-047@102"],"previous_event_hash":"4adfd11f8406c86daa199a529556490940d6ecabee001e6fb49e2fa4441b7f37","previous_snapshot_hash":"c45f761a8c7e9ae1db97a2a777c91002d2e97db97c99375755e4405b436161d0","recorded_at":"2026-09-16T12:21:06.704364+00:00","relationships":[],"revision":102,"snapshot_hash":"46fd9402522fe6ca901c5f5a8b8f8194bba4feb15e9345b10df4fe279eab26f1","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-053","DEC-049","DISC-055","REQ-053"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-053","DEC-049","DISC-055","REQ-053"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"fab50e6574796685dd30e6c9a11b2af2a085ce2bed6d154e7b369a8079fca415","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"82edb5f5ac2e12379391b5ecd2bcaa0fbd5cca4a7814a0bc9b17b36debefb61d","previous_snapshot_hash":"46fd9402522fe6ca901c5f5a8b8f8194bba4feb15e9345b10df4fe279eab26f1","recorded_at":"2026-09-16T14:46:09.297362+00:00","relationships":[],"revision":103,"snapshot_hash":"cbaadc6f23981554fe9b0ded956b0398f1e18d72970da64725d88ecf275537c2","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-054","DEC-050","DISC-056","REQ-054"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-054","DEC-050","DISC-056","REQ-054"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"02e86c6c2cfe1081612de3453084e163880f74900b66cb290d354532c8bd3811","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"fab50e6574796685dd30e6c9a11b2af2a085ce2bed6d154e7b369a8079fca415","previous_snapshot_hash":"cbaadc6f23981554fe9b0ded956b0398f1e18d72970da64725d88ecf275537c2","recorded_at":"2026-09-17T01:15:59.693448+00:00","relationships":[],"revision":104,"snapshot_hash":"d914923e13c83e561a2ec4da4865615942e6396a34cd4ffd181f525aa73e27ca","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-055","DEC-051","DISC-057","REQ-054","REQ-055"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-055","DEC-051","DISC-057","REQ-055"],"changed_ids":["REQ-054"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"9a01a5faa306131f021884b220a38a9281da225f7b3a421b9a2aeb7a4a9b7f83","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"02e86c6c2cfe1081612de3453084e163880f74900b66cb290d354532c8bd3811","previous_snapshot_hash":"d914923e13c83e561a2ec4da4865615942e6396a34cd4ffd181f525aa73e27ca","recorded_at":"2026-09-17T01:20:29.533382+00:00","relationships":[],"revision":105,"snapshot_hash":"bebc0fec7b306fa9f9f6f59728a8d676a500d933221adb6d3f8ea235d507cf3a","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"bb06be30a6cff1abeebc19819e7e8cdf7744a5be2dd9522f0e297a0424c76765","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-048@106"],"previous_event_hash":"9a01a5faa306131f021884b220a38a9281da225f7b3a421b9a2aeb7a4a9b7f83","previous_snapshot_hash":"bebc0fec7b306fa9f9f6f59728a8d676a500d933221adb6d3f8ea235d507cf3a","recorded_at":"2026-09-17T01:24:56.138846+00:00","relationships":[],"revision":106,"snapshot_hash":"cf737386f1fbdf5e67fc21be46dad80af4e778f942278c8906ca8e72f7bb8172","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-056","DEC-052","DISC-058","REQ-056"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-056","DEC-052","DISC-058","REQ-056"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"c39d6e31306d734e8f197f7f475afa4ddf4d5f4d3ef992bdfe45ca3cd7b60d7d","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"bb06be30a6cff1abeebc19819e7e8cdf7744a5be2dd9522f0e297a0424c76765","previous_snapshot_hash":"cf737386f1fbdf5e67fc21be46dad80af4e778f942278c8906ca8e72f7bb8172","recorded_at":"2026-09-17T01:31:23.446277+00:00","relationships":[],"revision":107,"snapshot_hash":"5b960105f112576380d936d2b7404c6189756d43d0cea4a08459d7d4ed439413","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-057","DEC-053","DISC-059","REQ-057"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-057","DEC-053","DISC-059","REQ-057"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"7823087d8038a030560bdb10fa15bf8875d1f557727df8bd32b08fd2673c9e7f","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"c39d6e31306d734e8f197f7f475afa4ddf4d5f4d3ef992bdfe45ca3cd7b60d7d","previous_snapshot_hash":"5b960105f112576380d936d2b7404c6189756d43d0cea4a08459d7d4ed439413","recorded_at":"2026-09-17T01:34:33.711798+00:00","relationships":[],"revision":108,"snapshot_hash":"6ac240f52cf1a13c3b955affc43a44b0400d3d33b7b30a4618422c135b278776","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0d0ddeed751054e6da3f0c9ffd886946e3dbe6a9c22a22e7b618029256b38216","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-049@109"],"previous_event_hash":"7823087d8038a030560bdb10fa15bf8875d1f557727df8bd32b08fd2673c9e7f","previous_snapshot_hash":"6ac240f52cf1a13c3b955affc43a44b0400d3d33b7b30a4618422c135b278776","recorded_at":"2026-09-17T01:35:18.279197+00:00","relationships":[],"revision":109,"snapshot_hash":"373784ab297f2a04194439f73880fe109fd3e57d29b2275b0e4b03fac0ce6392","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-058","DEC-054","DISC-060","REQ-054","REQ-058"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-058","DEC-054","DISC-060","REQ-058"],"changed_ids":["REQ-054"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"5a290f96194da1352e811e666015c619b3a405fe0711e9121f521be7c04326e3","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"0d0ddeed751054e6da3f0c9ffd886946e3dbe6a9c22a22e7b618029256b38216","previous_snapshot_hash":"373784ab297f2a04194439f73880fe109fd3e57d29b2275b0e4b03fac0ce6392","recorded_at":"2026-09-17T01:39:02.752384+00:00","relationships":[],"revision":110,"snapshot_hash":"808990125ebd16696494afa40ba1bf80565766c7743013bf39ee77d337dff604","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-059","DEC-055","DISC-061","REQ-059"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-059","DEC-055","DISC-061","REQ-059"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"1bf8e096d45d5af88281aaae2833952485d542972d07efd163cadfc8b3175335","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"5a290f96194da1352e811e666015c619b3a405fe0711e9121f521be7c04326e3","previous_snapshot_hash":"808990125ebd16696494afa40ba1bf80565766c7743013bf39ee77d337dff604","recorded_at":"2026-09-17T01:41:26.639929+00:00","relationships":[],"revision":111,"snapshot_hash":"c63baa2940516c5bce9a2b28a86563d5bdc178a494a62e2855dd9941d930e542","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-060","DEC-056","DISC-062","REQ-060"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-060","DEC-056","DISC-062","REQ-060"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"c6956129107c991abb55ea5a5e70698b1d2ef116f404baf6bc5e786a981df1d2","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"1bf8e096d45d5af88281aaae2833952485d542972d07efd163cadfc8b3175335","previous_snapshot_hash":"c63baa2940516c5bce9a2b28a86563d5bdc178a494a62e2855dd9941d930e542","recorded_at":"2026-09-17T01:44:21.229741+00:00","relationships":[],"revision":112,"snapshot_hash":"26311fad73f33d21bb9819399dc7cdf09014f953594ec7949e02c22cf41f350f","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"b3c56f3adaa4a59e7569383b01b2f09ad15b393372850c70f45cb91369f990fa","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-050@113"],"previous_event_hash":"c6956129107c991abb55ea5a5e70698b1d2ef116f404baf6bc5e786a981df1d2","previous_snapshot_hash":"26311fad73f33d21bb9819399dc7cdf09014f953594ec7949e02c22cf41f350f","recorded_at":"2026-09-17T01:45:09.481504+00:00","relationships":[],"revision":113,"snapshot_hash":"449c5c9ee4979a53b53dea1587205f138169ca6318e123e6ec9b61f8d0279dc6","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-061","DEC-057","DISC-063","REQ-061"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-061","DEC-057","DISC-063","REQ-061"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"6f63b334806dbc07e9bbd3bd3ecf238ff4d127b6923e7a1952d1d98ee62d9603","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"b3c56f3adaa4a59e7569383b01b2f09ad15b393372850c70f45cb91369f990fa","previous_snapshot_hash":"449c5c9ee4979a53b53dea1587205f138169ca6318e123e6ec9b61f8d0279dc6","recorded_at":"2026-09-17T01:48:10.886921+00:00","relationships":[],"revision":114,"snapshot_hash":"ce8821ffd5a650785f24680ed7e0e35daf92d4a5452bc1bc1e704364082a43f8","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"aec7d9410b0a0d0840bf7a31c54df511bbd6e5a4bea9d7dd15fc42f0339e39bc","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-051@115"],"previous_event_hash":"6f63b334806dbc07e9bbd3bd3ecf238ff4d127b6923e7a1952d1d98ee62d9603","previous_snapshot_hash":"ce8821ffd5a650785f24680ed7e0e35daf92d4a5452bc1bc1e704364082a43f8","recorded_at":"2026-09-17T01:48:57.475679+00:00","relationships":[],"revision":115,"snapshot_hash":"dd37b867d299fd82995bf6fac60ee8ade31a88f8076bfdc0770e61234c406546","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-062","DEC-058","DISC-064","REQ-062"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-062","DEC-058","DISC-064","REQ-062"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"b1f1d104b3035d08484a559814459bb2e0768388ec8a3f9a4986f63b869e2a28","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"aec7d9410b0a0d0840bf7a31c54df511bbd6e5a4bea9d7dd15fc42f0339e39bc","previous_snapshot_hash":"dd37b867d299fd82995bf6fac60ee8ade31a88f8076bfdc0770e61234c406546","recorded_at":"2026-09-17T01:51:18.547524+00:00","relationships":[],"revision":116,"snapshot_hash":"229f19a51e1092935ffbb66e8f9326139193c28ba0014a9a42717ece5cc4c4eb","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4b5fe227231cef05ac5b1c19184791cf5eb259bca770df1a40f03d1d3c8b90b1","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-052@117"],"previous_event_hash":"b1f1d104b3035d08484a559814459bb2e0768388ec8a3f9a4986f63b869e2a28","previous_snapshot_hash":"229f19a51e1092935ffbb66e8f9326139193c28ba0014a9a42717ece5cc4c4eb","recorded_at":"2026-09-17T01:52:02.033661+00:00","relationships":[],"revision":117,"snapshot_hash":"ba22713e88faba65f06d996c828a51e8e5aa54e1e5df5c91c5fea18bf5282191","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-063","DEC-059","DISC-065","REQ-062","REQ-063"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-063","DEC-059","DISC-065","REQ-063"],"changed_ids":["REQ-062"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"a9f78a7dd454d65e5ea91d429f82a5d2a9c74030443331a7bbfcfcebaf5157e0","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"4b5fe227231cef05ac5b1c19184791cf5eb259bca770df1a40f03d1d3c8b90b1","previous_snapshot_hash":"ba22713e88faba65f06d996c828a51e8e5aa54e1e5df5c91c5fea18bf5282191","recorded_at":"2026-09-17T03:24:37.459087+00:00","relationships":[],"revision":118,"snapshot_hash":"d459a256788638272c77c1446121d8e90bbb1a338ce5e5c4752e4f325500526d","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"9866489c5613e0a2a888bcd0638469a8f1f0da0ac1385f89bffe7cef069273e5","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-053@119"],"previous_event_hash":"a9f78a7dd454d65e5ea91d429f82a5d2a9c74030443331a7bbfcfcebaf5157e0","previous_snapshot_hash":"d459a256788638272c77c1446121d8e90bbb1a338ce5e5c4752e4f325500526d","recorded_at":"2026-09-17T03:25:30.341077+00:00","relationships":[],"revision":119,"snapshot_hash":"e09a2f2e30aa9f3b5c75736195313b3e3b217e09934da8d19494456a70072733","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-064","DEC-060","DISC-066","REQ-064"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-064","DEC-060","DISC-066","REQ-064"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"679a2c5c25fcff3c69b581190866a796acbcdeb42ba7566c5b21451f12f4c391","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"9866489c5613e0a2a888bcd0638469a8f1f0da0ac1385f89bffe7cef069273e5","previous_snapshot_hash":"e09a2f2e30aa9f3b5c75736195313b3e3b217e09934da8d19494456a70072733","recorded_at":"2026-09-17T03:27:35.305598+00:00","relationships":[],"revision":120,"snapshot_hash":"4f8da726ca9d10c5a629c9447bfe6ff32b14132b3c312738cc062370d6f72bbb","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"81753f8067798ab486a0c091d7812dbc3def9c544059d3754878ec440df41827","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-054@121"],"previous_event_hash":"679a2c5c25fcff3c69b581190866a796acbcdeb42ba7566c5b21451f12f4c391","previous_snapshot_hash":"4f8da726ca9d10c5a629c9447bfe6ff32b14132b3c312738cc062370d6f72bbb","recorded_at":"2026-09-17T03:28:42.078873+00:00","relationships":[],"revision":121,"snapshot_hash":"4eb28d370bbad11e9a34361bcdde6cda63466f9caa135a2c79dd847acf80a6b3","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-065","DEC-061","DISC-067","REQ-061","REQ-065"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-065","DEC-061","DISC-067","REQ-065"],"changed_ids":["REQ-061"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"37270d34b352e3b432b82b16c1e1b343c08e477cf0745816634ab7e8e86ca900","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"81753f8067798ab486a0c091d7812dbc3def9c544059d3754878ec440df41827","previous_snapshot_hash":"4eb28d370bbad11e9a34361bcdde6cda63466f9caa135a2c79dd847acf80a6b3","recorded_at":"2026-09-17T03:31:38.322061+00:00","relationships":[],"revision":122,"snapshot_hash":"975137e00e194d839698b36d8d380385ba5f8d6707c0f6bec3a8140d757250cd","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"37da53c67ba01e35434b69d93c44fef70be27d6967ce09b92c75bde14a97b447","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-055@123"],"previous_event_hash":"37270d34b352e3b432b82b16c1e1b343c08e477cf0745816634ab7e8e86ca900","previous_snapshot_hash":"975137e00e194d839698b36d8d380385ba5f8d6707c0f6bec3a8140d757250cd","recorded_at":"2026-09-17T03:32:29.132583+00:00","relationships":[],"revision":123,"snapshot_hash":"cdbb15f7a0204f7291a36e6c7047902187376de903676a7e62c30f06ce7ee12e","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-066","DEC-062","DISC-068","REQ-066"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-066","DEC-062","DISC-068","REQ-066"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"9929c816c423c0d7f0da28e375110c2025ff887403c92764047d621981e3610d","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"37da53c67ba01e35434b69d93c44fef70be27d6967ce09b92c75bde14a97b447","previous_snapshot_hash":"cdbb15f7a0204f7291a36e6c7047902187376de903676a7e62c30f06ce7ee12e","recorded_at":"2026-09-17T03:34:16.119900+00:00","relationships":[],"revision":124,"snapshot_hash":"1143a6538b4a587c7a0cbdc9c3c5c5d03a5a507e3a108b85bc859e6975a67a88","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"18032d49afbe60a7acbb582a013cc1bf1747b77fbdb31e9c6db15f79ad5e314e","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-056@125"],"previous_event_hash":"9929c816c423c0d7f0da28e375110c2025ff887403c92764047d621981e3610d","previous_snapshot_hash":"1143a6538b4a587c7a0cbdc9c3c5c5d03a5a507e3a108b85bc859e6975a67a88","recorded_at":"2026-09-17T03:35:38.123381+00:00","relationships":[],"revision":125,"snapshot_hash":"f9645276c0bb6a86d7b30fcec1aa6a3107bbcc34adc7855541fb7919d8393673","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-067","DEC-063","DISC-069","REQ-066","REQ-067"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-067","DEC-063","DISC-069","REQ-067"],"changed_ids":["REQ-066"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"f85264872446de7ad584ba2fa80597974310608977ed191de11cb99549f02825","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"18032d49afbe60a7acbb582a013cc1bf1747b77fbdb31e9c6db15f79ad5e314e","previous_snapshot_hash":"f9645276c0bb6a86d7b30fcec1aa6a3107bbcc34adc7855541fb7919d8393673","recorded_at":"2026-09-17T03:38:29.917646+00:00","relationships":[],"revision":126,"snapshot_hash":"8570bfb62cfc73bf96b64b3f9cdb53ba549125dd6255656c6e4604a1de87abfc","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"102ad55d21489ae356706eabafa4246e33292d8cd73e88867c2fd841842fcb91","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; dedicated Web model-management placement is settled by REQ-050. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-057@127"],"previous_event_hash":"f85264872446de7ad584ba2fa80597974310608977ed191de11cb99549f02825","previous_snapshot_hash":"8570bfb62cfc73bf96b64b3f9cdb53ba549125dd6255656c6e4604a1de87abfc","recorded_at":"2026-09-17T03:39:44.359758+00:00","relationships":[],"revision":127,"snapshot_hash":"923b6823d5e138460d95727c55daf568ac56c5328e1608071a7e128e97a762c3","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-050","AC-053","AC-067","AC-068","DEC-064","DISC-070","REQ-050","REQ-053","REQ-067","REQ-068"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-068","DEC-064","DISC-070","REQ-068"],"changed_ids":["AC-050","AC-053","AC-067","REQ-050","REQ-053","REQ-067"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0ab6ba5c818f8378e57a26d6cca9ddc37c390ec1ba3a0b43aae22a53c9818093","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; single-page Device Configuration placement and import-summary behavior are settled by REQ-068; no dedicated model-management page. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"102ad55d21489ae356706eabafa4246e33292d8cd73e88867c2fd841842fcb91","previous_snapshot_hash":"923b6823d5e138460d95727c55daf568ac56c5328e1608071a7e128e97a762c3","recorded_at":"2026-09-17T03:48:21.666501+00:00","relationships":[],"revision":128,"snapshot_hash":"4e86c32730b2f78614b5e9ebcd675796866b2cae53bffe81bbb2bd38eb394a77","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"6f2f9de1ba21ce8cb7fc0e74aa23a1d941b9b68ade70e90772da4891698acf0a","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; single-page Device Configuration placement and import-summary behavior are settled by REQ-068; no dedicated model-management page. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-058@129"],"previous_event_hash":"0ab6ba5c818f8378e57a26d6cca9ddc37c390ec1ba3a0b43aae22a53c9818093","previous_snapshot_hash":"4e86c32730b2f78614b5e9ebcd675796866b2cae53bffe81bbb2bd38eb394a77","recorded_at":"2026-09-17T03:50:42.636535+00:00","relationships":[],"revision":129,"snapshot_hash":"d2d734fca7f26ca6110205c7ef4d0a0fa357a842448f9fd7c7c5ac72d3d2a481","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-069","DEC-065","DISC-071","REQ-069"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-069","DEC-065","DISC-071","REQ-069"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"d7513e240a61a9d3d6cc64bc65789b41fc0c2917db996a6154cefc109b015b3d","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; single-page Device Configuration placement and import-summary behavior are settled by REQ-068; no dedicated model-management page. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"6f2f9de1ba21ce8cb7fc0e74aa23a1d941b9b68ade70e90772da4891698acf0a","previous_snapshot_hash":"d2d734fca7f26ca6110205c7ef4d0a0fa357a842448f9fd7c7c5ac72d3d2a481","recorded_at":"2026-09-17T03:56:06.282134+00:00","relationships":[],"revision":130,"snapshot_hash":"c33acf297eef4e7ff12bcc5ec1bb6d2a822c318d776acd80e9b7ec55fdca30b1","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0f5e64e6c2204ddcda9dd5fa5ec9e0a4de2422df96ed4b2e828b029c2aa40f44","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; single-page Device Configuration placement and import-summary behavior are settled by REQ-068; no dedicated model-management page. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-059@131"],"previous_event_hash":"d7513e240a61a9d3d6cc64bc65789b41fc0c2917db996a6154cefc109b015b3d","previous_snapshot_hash":"c33acf297eef4e7ff12bcc5ec1bb6d2a822c318d776acd80e9b7ec55fdca30b1","recorded_at":"2026-09-17T03:59:06.957715+00:00","relationships":[],"revision":131,"snapshot_hash":"971147f66a8ea5745ef9fb26b1a62c4b261719897d41d2f19f02a81cfc74ef6a","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-070","DEC-066","DISC-072","REQ-070"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-070","DEC-066","DISC-072","REQ-070"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4e4b3447519ce91d6537a51497c2a563191ef526a6d796da8cbc2062a97d2bcc","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; single-page Device Configuration placement and import-summary behavior are settled by REQ-068; no dedicated model-management page. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"0f5e64e6c2204ddcda9dd5fa5ec9e0a4de2422df96ed4b2e828b029c2aa40f44","previous_snapshot_hash":"971147f66a8ea5745ef9fb26b1a62c4b261719897d41d2f19f02a81cfc74ef6a","recorded_at":"2026-09-17T04:01:28.755796+00:00","relationships":[],"revision":132,"snapshot_hash":"bb7084764f2b46d16e4eed76fc4dae2d0cf42d7119921f68f32aa693697b20cd","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"57fe44a0ddae01b206f557e461e478abdfca871de09fd0d1a184f0afd9b47430","event_type":"reconcile","event_version":1,"open_decisions":["OD-008: User-facing desktop export and env_sensing Web UI composition: export/name interaction and visible operation/state layout; single-page Device Configuration placement and import-summary behavior are settled by REQ-068; no dedicated model-management page. Preserve confirmed import versus Apply versus Save behavior.","OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-060@133"],"previous_event_hash":"4e4b3447519ce91d6537a51497c2a563191ef526a6d796da8cbc2062a97d2bcc","previous_snapshot_hash":"bb7084764f2b46d16e4eed76fc4dae2d0cf42d7119921f68f32aa693697b20cd","recorded_at":"2026-09-17T04:04:03.383504+00:00","relationships":[],"revision":133,"snapshot_hash":"16733e0d3266c5a900bc5e4e3c1b2693c651679e0d8d72df8b68b9fac0eb440b","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-071","DEC-067","DISC-073","REQ-071"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-071","DEC-067","DISC-073","REQ-071"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"58f0b85095cde46e8b7a00553b7c142272bae772d93bd61a7f6a5530c3c7faf7","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"57fe44a0ddae01b206f557e461e478abdfca871de09fd0d1a184f0afd9b47430","previous_snapshot_hash":"16733e0d3266c5a900bc5e4e3c1b2693c651679e0d8d72df8b68b9fac0eb440b","recorded_at":"2026-09-17T04:07:10.150239+00:00","relationships":[],"revision":134,"snapshot_hash":"1ebfb495b8228c00ca9028e73ca632ccee20779c3b7ce7b66713da8ed978f860","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"fc94515ffc46e1d5fc4a74eb3bbf6ea45500348bc642ccc82def57fd8d41e338","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-061@135"],"previous_event_hash":"58f0b85095cde46e8b7a00553b7c142272bae772d93bd61a7f6a5530c3c7faf7","previous_snapshot_hash":"1ebfb495b8228c00ca9028e73ca632ccee20779c3b7ce7b66713da8ed978f860","recorded_at":"2026-09-17T04:09:26.028632+00:00","relationships":[],"revision":135,"snapshot_hash":"0b6b0c310e28d7c5b3098b559ccaa69fd79882448b947b74adc30b824353286d","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-072","DEC-068","DISC-074","REQ-072"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-072","DEC-068","DISC-074","REQ-072"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"5adb1ab24474560bef248838104ca84aa8285448c45b5b24a0bfb689ac3194c9","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"fc94515ffc46e1d5fc4a74eb3bbf6ea45500348bc642ccc82def57fd8d41e338","previous_snapshot_hash":"0b6b0c310e28d7c5b3098b559ccaa69fd79882448b947b74adc30b824353286d","recorded_at":"2026-09-17T04:12:43.142960+00:00","relationships":[],"revision":136,"snapshot_hash":"6018c98a0642f2c73c9b33702bd3054f42cf47f85bdfb1689be580385d942556","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0190d2253d0a00d020729b725908ca3d763ddc7487e6a6f0168da5c157912fef","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-062@137"],"previous_event_hash":"5adb1ab24474560bef248838104ca84aa8285448c45b5b24a0bfb689ac3194c9","previous_snapshot_hash":"6018c98a0642f2c73c9b33702bd3054f42cf47f85bdfb1689be580385d942556","recorded_at":"2026-09-17T04:15:21.848272+00:00","relationships":[],"revision":137,"snapshot_hash":"aca0e2e323272eb77afdd8aa261129501bab05f92036a3ff8124bc548e97eeb4","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-073","DEC-069","DISC-075","REQ-073"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-073","DEC-069","DISC-075","REQ-073"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0db4903997a2919d0cd152ed37ef096ca9911604377b930e4db235d1f28ccc33","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"0190d2253d0a00d020729b725908ca3d763ddc7487e6a6f0168da5c157912fef","previous_snapshot_hash":"aca0e2e323272eb77afdd8aa261129501bab05f92036a3ff8124bc548e97eeb4","recorded_at":"2026-09-17T04:20:14.383442+00:00","relationships":[],"revision":138,"snapshot_hash":"c4f0d272a2b3a37b6d61f036a7e52997f609c1d4a1b10c9d5a03e511a7272587","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"11476de1296ab84ca03a4059e0012ad7ddf9c9295d839099b2e6e0df6db95794","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-063@139"],"previous_event_hash":"0db4903997a2919d0cd152ed37ef096ca9911604377b930e4db235d1f28ccc33","previous_snapshot_hash":"c4f0d272a2b3a37b6d61f036a7e52997f609c1d4a1b10c9d5a03e511a7272587","recorded_at":"2026-09-17T04:21:09.278433+00:00","relationships":[],"revision":139,"snapshot_hash":"310e2fcdcd525f490a53c05abf50f7efd43d11da24365bb5f03b7661353ea020","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-074","DEC-070","DISC-076","REQ-074"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-074","DEC-070","DISC-076","REQ-074"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"50e197d2677d85fcfc1d5a420daf75ec033d57006c2ad746d8e9ddba24712864","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"11476de1296ab84ca03a4059e0012ad7ddf9c9295d839099b2e6e0df6db95794","previous_snapshot_hash":"310e2fcdcd525f490a53c05abf50f7efd43d11da24365bb5f03b7661353ea020","recorded_at":"2026-09-17T04:24:22.176831+00:00","relationships":[],"revision":140,"snapshot_hash":"d760af05832a20915a5083140d8a23c95616ef3e5d31aef00f7b4ff9fc060902","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"582dcd2c45a8d85300a876dd721c74563b1bba12b283f2050e35c8560ab88693","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-064@141"],"previous_event_hash":"50e197d2677d85fcfc1d5a420daf75ec033d57006c2ad746d8e9ddba24712864","previous_snapshot_hash":"d760af05832a20915a5083140d8a23c95616ef3e5d31aef00f7b4ff9fc060902","recorded_at":"2026-09-17T04:30:49.275481+00:00","relationships":[],"revision":141,"snapshot_hash":"fed5e3fae951983c7d4e378b615ba58e3bbe9329a5836817d6740aa002aff3cb","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-075","DEC-071","DISC-077","REQ-075"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-075","DEC-071","DISC-077","REQ-075"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0a2a228d6f13ef0d92b9fe1f973dbdff80ff32db7cc074fcf91d47a568abdb97","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"582dcd2c45a8d85300a876dd721c74563b1bba12b283f2050e35c8560ab88693","previous_snapshot_hash":"fed5e3fae951983c7d4e378b615ba58e3bbe9329a5836817d6740aa002aff3cb","recorded_at":"2026-09-17T04:49:02.980379+00:00","relationships":[],"revision":142,"snapshot_hash":"e90673b12e262c46c126761a858e6eb775eaa89469dd98f2fd87335ad1f6403f","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"adfc21b045c073246b44370d26a7665f45be4eb9d81e990c97534ea783af2df6","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-065@143"],"previous_event_hash":"0a2a228d6f13ef0d92b9fe1f973dbdff80ff32db7cc074fcf91d47a568abdb97","previous_snapshot_hash":"e90673b12e262c46c126761a858e6eb775eaa89469dd98f2fd87335ad1f6403f","recorded_at":"2026-09-17T04:50:14.875035+00:00","relationships":[],"revision":143,"snapshot_hash":"6c2eb72d8b8c714282d837fec315b3828d649095416cdb10c7f71c450c3630b6","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-076","DEC-072","DISC-078","REQ-076"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-076","DEC-072","DISC-078","REQ-076"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"28046a8d4c823168a0252ed1bac3b50009e491035b2daedd7851ee35fb0d2007","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"adfc21b045c073246b44370d26a7665f45be4eb9d81e990c97534ea783af2df6","previous_snapshot_hash":"6c2eb72d8b8c714282d837fec315b3828d649095416cdb10c7f71c450c3630b6","recorded_at":"2026-09-17T04:54:16.505960+00:00","relationships":[],"revision":144,"snapshot_hash":"1691a5b668e9f6b249060491a0df72197be809d6240526677ea95ab89361e129","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"c68307e9dc75f7752e7a128757077404d51a2bb345ae01ec30b934adab90732d","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-066@145"],"previous_event_hash":"28046a8d4c823168a0252ed1bac3b50009e491035b2daedd7851ee35fb0d2007","previous_snapshot_hash":"1691a5b668e9f6b249060491a0df72197be809d6240526677ea95ab89361e129","recorded_at":"2026-09-17T04:55:06.223627+00:00","relationships":[],"revision":145,"snapshot_hash":"287ba886a91990efa5299bf0a226a82b41c4f3b62803b789cc90c5b4affae03a","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-077","DEC-073","DISC-079","REQ-077"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-077","DEC-073","DISC-079","REQ-077"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"57c966de6ef1a12a511062432e1948464dcd08328b2c16f329452d94c3382797","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"c68307e9dc75f7752e7a128757077404d51a2bb345ae01ec30b934adab90732d","previous_snapshot_hash":"287ba886a91990efa5299bf0a226a82b41c4f3b62803b789cc90c5b4affae03a","recorded_at":"2026-09-17T05:28:20.588441+00:00","relationships":[],"revision":146,"snapshot_hash":"a7e451004b9183d7848976259ae164cdaad3b5d0ed301b7f206a75b6154191ee","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"1a425ce70cbdc3c246a1213e4c72e3f9d4d589add8b72cb6e63ea35a51176e96","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-067@147"],"previous_event_hash":"57c966de6ef1a12a511062432e1948464dcd08328b2c16f329452d94c3382797","previous_snapshot_hash":"a7e451004b9183d7848976259ae164cdaad3b5d0ed301b7f206a75b6154191ee","recorded_at":"2026-09-17T05:29:13.044340+00:00","relationships":[],"revision":147,"snapshot_hash":"4016fa545f5644fcfb3e5ac342a1f1c4311b672567945ebf8e2954a6d0dff822","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-078","DEC-074","DISC-080","REQ-078"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-078","DEC-074","DISC-080","REQ-078"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"3d992e20fd01191487d2aeee175ebdfca6437dd12c07e150249515fcfafb79af","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"1a425ce70cbdc3c246a1213e4c72e3f9d4d589add8b72cb6e63ea35a51176e96","previous_snapshot_hash":"4016fa545f5644fcfb3e5ac342a1f1c4311b672567945ebf8e2954a6d0dff822","recorded_at":"2026-09-17T05:45:50.317375+00:00","relationships":[],"revision":148,"snapshot_hash":"697d0fbd1c13eedd5972fc256943a482816c33c80a851a5334ed6927a813b0af","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-078","AC-079","DEC-075","DISC-081","REQ-078","REQ-079"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-079","DEC-075","DISC-081","REQ-079"],"changed_ids":["AC-078","REQ-078"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4e465df33387ffbd11e3ec5e9defe8080b06994e2a4686e6e1323d1def3c74dd","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"3d992e20fd01191487d2aeee175ebdfca6437dd12c07e150249515fcfafb79af","previous_snapshot_hash":"697d0fbd1c13eedd5972fc256943a482816c33c80a851a5334ed6927a813b0af","recorded_at":"2026-09-17T05:51:03.546379+00:00","relationships":[],"revision":149,"snapshot_hash":"02e4bfb210fc99fef9a2f54b307e8874f4d058650abad2c208d42e7524db1bed","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"69b809ab5464b9d533089121fe67740471431270f89e1224554cc08ea42ba8df","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-068@150"],"previous_event_hash":"4e465df33387ffbd11e3ec5e9defe8080b06994e2a4686e6e1323d1def3c74dd","previous_snapshot_hash":"02e4bfb210fc99fef9a2f54b307e8874f4d058650abad2c208d42e7524db1bed","recorded_at":"2026-09-17T05:54:05.192873+00:00","relationships":[],"revision":150,"snapshot_hash":"fdab58bd2e8407bd83a6eb769230ccf1aa184b28ce53cc0779ea0e0922a58afa","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-055","AC-056","AC-061","DEC-076","DISC-082","REQ-054","REQ-055","REQ-056","REQ-057","REQ-058","REQ-060","REQ-061","REQ-078"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["DEC-076","DISC-082"],"changed_ids":["AC-055","AC-056","AC-061","REQ-054","REQ-055","REQ-056","REQ-057","REQ-058","REQ-060","REQ-061","REQ-078"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"253d32b6188a68acea22b15f6af2e89543053c8c36cbf1a652805fc786d3d7fb","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"69b809ab5464b9d533089121fe67740471431270f89e1224554cc08ea42ba8df","previous_snapshot_hash":"fdab58bd2e8407bd83a6eb769230ccf1aa184b28ce53cc0779ea0e0922a58afa","recorded_at":"2026-09-17T06:01:23.896382+00:00","relationships":[],"revision":151,"snapshot_hash":"b1df30db694fa8075635f8ee311bfddb2f604e9fae2c07bbb6223ca6d9ddc299","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"e2c39fa94df88c40afee8bb0d2a57c44beaa516c725b039e0deb252ec50e4398","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-069@152"],"previous_event_hash":"253d32b6188a68acea22b15f6af2e89543053c8c36cbf1a652805fc786d3d7fb","previous_snapshot_hash":"b1df30db694fa8075635f8ee311bfddb2f604e9fae2c07bbb6223ca6d9ddc299","recorded_at":"2026-09-17T06:03:38.947099+00:00","relationships":[],"revision":152,"snapshot_hash":"8aa3fca665f8fe8404eb80a7e0c1aa2b3b1d5374f809a28c51c690325a831c43","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-080","DEC-077","DISC-083","REQ-080"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-080","DEC-077","DISC-083","REQ-080"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"872f351da537916f8c76689fcd28e66e8f30f938ed65670650410ebdf4e8fa5f","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"e2c39fa94df88c40afee8bb0d2a57c44beaa516c725b039e0deb252ec50e4398","previous_snapshot_hash":"8aa3fca665f8fe8404eb80a7e0c1aa2b3b1d5374f809a28c51c690325a831c43","recorded_at":"2026-09-17T06:07:13.486065+00:00","relationships":[],"revision":153,"snapshot_hash":"82f40d8fa84a4592fdc628da4c558e9cc115d63f5986b933b09ac47b44b1ac26","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"e5f6c7168bdc033ad709fa82b227c0da0c4b25926847e8c70419f2de38305cee","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-070@154"],"previous_event_hash":"872f351da537916f8c76689fcd28e66e8f30f938ed65670650410ebdf4e8fa5f","previous_snapshot_hash":"82f40d8fa84a4592fdc628da4c558e9cc115d63f5986b933b09ac47b44b1ac26","recorded_at":"2026-09-17T06:10:11.955989+00:00","relationships":[],"revision":154,"snapshot_hash":"f71fa11f0fd3546ea72f41d8e3e9b1edf86a68332dbe3928a12ab09a264dcda2","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-081","DEC-078","DISC-084","REQ-081"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-081","DEC-078","DISC-084","REQ-081"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"8a2cc7402b958be5d357595c2ca7ef772024cc6c4f103c52f6816e33796b7393","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"e5f6c7168bdc033ad709fa82b227c0da0c4b25926847e8c70419f2de38305cee","previous_snapshot_hash":"f71fa11f0fd3546ea72f41d8e3e9b1edf86a68332dbe3928a12ab09a264dcda2","recorded_at":"2026-09-17T06:23:33.362270+00:00","relationships":[],"revision":155,"snapshot_hash":"cd9cc24d69ab91e0f9e12cc7721508c54a7241d63a2443167075c75bf1a1f03d","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"c8c141557bfa2bbcf57824611c1a6cb17d3bbd79cb66dcd333ad96878982d7eb","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-071@156"],"previous_event_hash":"8a2cc7402b958be5d357595c2ca7ef772024cc6c4f103c52f6816e33796b7393","previous_snapshot_hash":"cd9cc24d69ab91e0f9e12cc7721508c54a7241d63a2443167075c75bf1a1f03d","recorded_at":"2026-09-17T06:26:19.256988+00:00","relationships":[],"revision":156,"snapshot_hash":"a2387385dce1f785cf3f90a6d5ab93ef5b1c5c35ee73648b293939be0719c981","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-082","DEC-079","DISC-085","REQ-082"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-082","DEC-079","DISC-085","REQ-082"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"c38795e35fc6e38ed78b06b814bbcef6b57be835e4b29d5897d6179e42106ca1","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"c8c141557bfa2bbcf57824611c1a6cb17d3bbd79cb66dcd333ad96878982d7eb","previous_snapshot_hash":"a2387385dce1f785cf3f90a6d5ab93ef5b1c5c35ee73648b293939be0719c981","recorded_at":"2026-09-17T06:29:22.233363+00:00","relationships":[],"revision":157,"snapshot_hash":"eac18e18265afac30226871939c97ffc622fa25c96dfefcb318af26ebcaaa63e","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"d5240d91e096b5d2feb3ad29fb36a09d6e5ec116bc9b060db892fd975c0820e7","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-072@158"],"previous_event_hash":"c38795e35fc6e38ed78b06b814bbcef6b57be835e4b29d5897d6179e42106ca1","previous_snapshot_hash":"eac18e18265afac30226871939c97ffc622fa25c96dfefcb318af26ebcaaa63e","recorded_at":"2026-09-17T06:34:14.495453+00:00","relationships":[],"revision":158,"snapshot_hash":"fad0b1b78ed4c411a1bd4942afb61be24b251b4a30155f66094c9897422f5213","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-083","DEC-080","DISC-086","REQ-083"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-083","DEC-080","DISC-086","REQ-083"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"2d396a8aa0a1159ce18836719d19e3ec2a6ebf9b32a22254dd4be9c87575e2d5","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"d5240d91e096b5d2feb3ad29fb36a09d6e5ec116bc9b060db892fd975c0820e7","previous_snapshot_hash":"fad0b1b78ed4c411a1bd4942afb61be24b251b4a30155f66094c9897422f5213","recorded_at":"2026-09-17T06:38:03.192207+00:00","relationships":[],"revision":159,"snapshot_hash":"dccbd67fd4201ca24a89ff292015ef5e176f695faa3f4deb8d96e49f223c53ae","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"02aff509483e07ae3524a15345b1f7d9ed741c12f7c9e33a93a153e9761e6b45","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-073@160"],"previous_event_hash":"2d396a8aa0a1159ce18836719d19e3ec2a6ebf9b32a22254dd4be9c87575e2d5","previous_snapshot_hash":"dccbd67fd4201ca24a89ff292015ef5e176f695faa3f4deb8d96e49f223c53ae","recorded_at":"2026-09-17T06:42:22.504178+00:00","relationships":[],"revision":160,"snapshot_hash":"5e9bd45b0c0d6fa02b08639c0f7ffbc75cadc365d762b605b1f06068581760cb","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-084","DEC-081","DISC-087","REQ-084"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-084","DEC-081","DISC-087","REQ-084"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"5c92c833a582d06fb140106a396ef72aa1d4850fdb5afd197e5d5c11d8dd8e54","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"02aff509483e07ae3524a15345b1f7d9ed741c12f7c9e33a93a153e9761e6b45","previous_snapshot_hash":"5e9bd45b0c0d6fa02b08639c0f7ffbc75cadc365d762b605b1f06068581760cb","recorded_at":"2026-09-17T06:56:05.429675+00:00","relationships":[],"revision":161,"snapshot_hash":"66b51dcb13a3b3de4e3061e01eb3345701812caf8c308404ad22ac64233b5928","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"f708c1d6cafef3e639d128af3bde2782d3adc3fc7aa89588e931cb0da51a8c06","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-074@162"],"previous_event_hash":"5c92c833a582d06fb140106a396ef72aa1d4850fdb5afd197e5d5c11d8dd8e54","previous_snapshot_hash":"66b51dcb13a3b3de4e3061e01eb3345701812caf8c308404ad22ac64233b5928","recorded_at":"2026-09-17T06:58:02.673294+00:00","relationships":[],"revision":162,"snapshot_hash":"8727b4785b74570f4fe318428a143242df99294e8dcb3524f12d058b24cab7ac","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-085","DEC-082","DISC-088","REQ-085"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-085","DEC-082","DISC-088","REQ-085"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"80b9c07cc9a4164e7c0829172794b37e8641c4b4cb72d43df9ee2ae74b60287a","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"f708c1d6cafef3e639d128af3bde2782d3adc3fc7aa89588e931cb0da51a8c06","previous_snapshot_hash":"8727b4785b74570f4fe318428a143242df99294e8dcb3524f12d058b24cab7ac","recorded_at":"2026-09-17T07:00:25.439620+00:00","relationships":[],"revision":163,"snapshot_hash":"24b1a1e06cf46af4e3235b1d5ea06c435cad3e83de589bcf4d949377c5cafa57","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"adaa710b69ff15c139f3cf94cec6707b07eb2ecc02f7e7db2c7fa8ca55fa8627","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-075@164"],"previous_event_hash":"80b9c07cc9a4164e7c0829172794b37e8641c4b4cb72d43df9ee2ae74b60287a","previous_snapshot_hash":"24b1a1e06cf46af4e3235b1d5ea06c435cad3e83de589bcf4d949377c5cafa57","recorded_at":"2026-09-17T07:03:23.370960+00:00","relationships":[],"revision":164,"snapshot_hash":"d53696b13db6d7cdd03b478c20e446af833dc513c1303aef09aa773644758440","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-086","DEC-083","DISC-089","REQ-086"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-086","DEC-083","DISC-089","REQ-086"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"388111558eac0dc60c4b0d99fa34409daac7d9d519cf896abc95045606863924","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"adaa710b69ff15c139f3cf94cec6707b07eb2ecc02f7e7db2c7fa8ca55fa8627","previous_snapshot_hash":"d53696b13db6d7cdd03b478c20e446af833dc513c1303aef09aa773644758440","recorded_at":"2026-09-17T07:21:23.941864+00:00","relationships":[],"revision":165,"snapshot_hash":"d90e171393d1875020e5fc5d2215b52010d7bec10b1d12ed3b0e255fc1350bea","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"759e4702492fbc2ec7eadd7fe37c01919d392c4c45cbfefe2277083cd499626f","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-076@166"],"previous_event_hash":"388111558eac0dc60c4b0d99fa34409daac7d9d519cf896abc95045606863924","previous_snapshot_hash":"d90e171393d1875020e5fc5d2215b52010d7bec10b1d12ed3b0e255fc1350bea","recorded_at":"2026-09-17T07:22:15.294071+00:00","relationships":[],"revision":166,"snapshot_hash":"9f97ca82ff9196d23256ca2024f4b28c69dae1bef1969774d8b13f1cf766daa2","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-087","DEC-084","DISC-090","REQ-087"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-087","DEC-084","DISC-090","REQ-087"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"ec7fe00ca5283d5ca730ecb3b21fa279e2bddbee2b1c835cca843b653b4b52bf","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"759e4702492fbc2ec7eadd7fe37c01919d392c4c45cbfefe2277083cd499626f","previous_snapshot_hash":"9f97ca82ff9196d23256ca2024f4b28c69dae1bef1969774d8b13f1cf766daa2","recorded_at":"2026-09-17T07:35:18.146493+00:00","relationships":[],"revision":167,"snapshot_hash":"dae3c8f980335c85f0baac15add147cfefc9c1cc4ae4b474e31a724105da4877","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"6ca7f7fc1cbd0136546bd2a148856b23980405ac93fe35d2d020ae9ca99a7f82","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-077@168"],"previous_event_hash":"ec7fe00ca5283d5ca730ecb3b21fa279e2bddbee2b1c835cca843b653b4b52bf","previous_snapshot_hash":"dae3c8f980335c85f0baac15add147cfefc9c1cc4ae4b474e31a724105da4877","recorded_at":"2026-09-17T07:38:01.967350+00:00","relationships":[],"revision":168,"snapshot_hash":"5cb89fe6997145b5164be7b394b4fc3109c0769765ff9e8b066c6425918daf61","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-088","DEC-085","DISC-091","REQ-088"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-088","DEC-085","DISC-091","REQ-088"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"b8d9da9c4ba3aee61e7dc3c391e024b7cc4a0e61ed32dd52b225c0affec3d5d5","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"6ca7f7fc1cbd0136546bd2a148856b23980405ac93fe35d2d020ae9ca99a7f82","previous_snapshot_hash":"5cb89fe6997145b5164be7b394b4fc3109c0769765ff9e8b066c6425918daf61","recorded_at":"2026-09-17T07:43:26.013899+00:00","relationships":[],"revision":169,"snapshot_hash":"a1cb7a9344b6a1c17112c41050f759b44386a2136f8f8006c61f2fa9893f22d5","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"d91e115d5f60fd522bcd88aa0f093afccece8ff0edce9b4deb0425398704704b","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details."],"previous_event_hash":"b8d9da9c4ba3aee61e7dc3c391e024b7cc4a0e61ed32dd52b225c0affec3d5d5","previous_snapshot_hash":"a1cb7a9344b6a1c17112c41050f759b44386a2136f8f8006c61f2fa9893f22d5","recorded_at":"2026-09-17T07:48:47.464047+00:00","relationships":[],"revision":170,"snapshot_hash":"4e7e7ad237a0a21649af0fbb5e24f5e9fa7f6f31f2b398adbd08fe451b410055","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"ad3854b2bf3c82b5cbe401103936d880097d19f6daec344d0c0ae6e7acabac5c","event_type":"reconcile","event_version":1,"open_decisions":["OD-009: Concrete software/firmware architecture design for the confirmed behavior: boundary/type/state ownership, dependencies and execution coordination. Inspect manifests/adoption/ADRs/baselines and design tables before proposing architecture changes; do not reopen accepted product rules merely to name implementation details.","Q-078@171"],"previous_event_hash":"d91e115d5f60fd522bcd88aa0f093afccece8ff0edce9b4deb0425398704704b","previous_snapshot_hash":"4e7e7ad237a0a21649af0fbb5e24f5e9fa7f6f31f2b398adbd08fe451b410055","recorded_at":"2026-09-17T07:49:41.868102+00:00","relationships":[],"revision":171,"snapshot_hash":"c0420e1d7d1c903f3f621c711f8f03f15f6b0780c2b4c5a3f7393bf1df47269e","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-089","DEC-086","DISC-092","REQ-081","REQ-084","REQ-089"],"conflicts":[],"continuity":"continuous","delta":{"added_ids":["AC-089","DEC-086","DISC-092","REQ-089"],"changed_ids":["REQ-081","REQ-084"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"cad347b869bc3e83338fb0a282125b3e1953e44337e9455e6147e43ee8be7409","event_type":"reconcile","event_version":1,"open_decisions":["None. Logical design is confirmed; pending implementation gates and acceptance evidence are tracked in Routing/Gates and Acceptance Criteria."],"previous_event_hash":"ad3854b2bf3c82b5cbe401103936d880097d19f6daec344d0c0ae6e7acabac5c","previous_snapshot_hash":"c0420e1d7d1c903f3f621c711f8f03f15f6b0780c2b4c5a3f7393bf1df47269e","recorded_at":"2026-09-17T08:10:35.791910+00:00","relationships":[],"revision":172,"snapshot_hash":"95741daa82a68781aed8800228f37a64bd3544e5f9977d0a67d6c1d0d7cab747","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"b5302ee955b5d40565ba36edc9083209258774c15db43e284260f0cf020494bc","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"cad347b869bc3e83338fb0a282125b3e1953e44337e9455e6147e43ee8be7409","previous_snapshot_hash":"95741daa82a68781aed8800228f37a64bd3544e5f9977d0a67d6c1d0d7cab747","recorded_at":"2026-09-17T08:11:02.095994+00:00","relationships":[],"revision":173,"snapshot_hash":"2d4e7e9ad60bb15d1e17e812ef1688a5fb41fa091ef1ba793422938ac6772600","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"ff65ae68f93de5566a13e7c40bd4eab57a890fbfc98e5cf8aa3bc03876167c44","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"b5302ee955b5d40565ba36edc9083209258774c15db43e284260f0cf020494bc","previous_snapshot_hash":"2d4e7e9ad60bb15d1e17e812ef1688a5fb41fa091ef1ba793422938ac6772600","recorded_at":"2026-09-17T08:11:41.332482+00:00","relationships":[],"revision":173,"snapshot_hash":"08ace2c8ca757829ca49bb6f6f7d6d73c008bf204fef4294cdcae6e133c2c753","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"legacy_journal":"spec-governance/WORKING-SPEC-01a0a7a57a23-model-parameter-export.journal.jsonl","legacy_notes":[],"legacy_snapshot":"spec-governance/WORKING-SPEC-01a0a7a57a23-model-parameter-export.md","removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"13ba0c8e4f69344966de1d3de49a523968ba3cf29aad0d2ef17bd650b097a5e5","event_type":"migration","event_version":1,"open_decisions":[],"previous_event_hash":"ff65ae68f93de5566a13e7c40bd4eab57a890fbfc98e5cf8aa3bc03876167c44","previous_snapshot_hash":"08ace2c8ca757829ca49bb6f6f7d6d73c008bf204fef4294cdcae6e133c2c753","recorded_at":"2026-09-21T06:52:26.301517+00:00","relationships":[],"revision":173,"snapshot_hash":"318de72338d9832b7135f0790f0652a16ea37b42e2be7b917b090762f0383c59","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"我想確認軟體spec跟韌體的spec；唯讀核對目前文件與最近FIR-only固定RAM決策差異","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user-spec-review-20260921","task_ref":"01a0a7a5-7a23-79c3-99c5-ba374eef801b","turn_id":"spec-review-20260921"},"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"5961a595e0b3ea84b18fd223fb893a43d1de8c243abd315a7b81b1db809513cc","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"13ba0c8e4f69344966de1d3de49a523968ba3cf29aad0d2ef17bd650b097a5e5","previous_snapshot_hash":"318de72338d9832b7135f0790f0652a16ea37b42e2be7b917b090762f0383c59","recorded_at":"2026-09-21T06:52:27.612039+00:00","relationships":[],"revision":173,"snapshot_hash":"318de72338d9832b7135f0790f0652a16ea37b42e2be7b917b090762f0383c59","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"baseline_contract_hash":"629751e8400430a5e3a72a0c1243d5364f02a6406edd347d2d5ac63196e45d5c","conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0da6ce170a9e8157d1075b3c6f6bc05196ca31dcd8a17d7d5e6530cd9dfdd211","event_type":"reopen","event_version":1,"open_decisions":[],"previous_event_hash":"5961a595e0b3ea84b18fd223fb893a43d1de8c243abd315a7b81b1db809513cc","previous_snapshot_hash":"318de72338d9832b7135f0790f0652a16ea37b42e2be7b917b090762f0383c59","recorded_at":"2026-09-21T08:00:16.586564+00:00","relationships":[],"revision":174,"snapshot_hash":"95bde3e7ad6993a15bbd257726e612f80abdb5e65e625d14d4e91914bf31994a","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-025","AC-027","AC-063","AC-065","AC-082","AC-083","AC-090","AC-091","AC-092","DEC-087","DEC-088","DEC-089","DISC-093","REQ-025","REQ-027","REQ-040","REQ-049","REQ-056","REQ-062","REQ-063","REQ-065","REQ-081","REQ-082","REQ-090","REQ-091","REQ-092"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":["AC-025","AC-027","AC-063","AC-065","AC-082","AC-083"],"added_ids":["AC-090","AC-091","AC-092","DEC-087","DEC-088","DEC-089","DISC-093","REQ-090","REQ-091","REQ-092"],"changed_ids":["AC-025","AC-027","AC-063","AC-065","AC-082","AC-083","REQ-025","REQ-027","REQ-040","REQ-049","REQ-056","REQ-062","REQ-063","REQ-065","REQ-081","REQ-082"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"d50e196dccfe92eaecc9dc360b21fd9ae18e608d0479e42287e025c092ded02b","event_type":"reconcile","event_version":1,"open_decisions":["OD-010: Fixed FIR/Ridge RAM budget and layout (including numeric/preprocessing states and transient allowance), maximum taps, per-rate history options, capacity delivery/versioning to the software, reservation placement (static or once at startup), and quantitative target memory/stack acceptance margins are not yet decided. 65 taps is an unaccepted candidate, not a default."],"previous_event_hash":"0da6ce170a9e8157d1075b3c6f6bc05196ca31dcd8a17d7d5e6530cd9dfdd211","previous_snapshot_hash":"95bde3e7ad6993a15bbd257726e612f80abdb5e65e625d14d4e91914bf31994a","recorded_at":"2026-09-21T08:03:26.766620+00:00","relationships":[],"revision":175,"snapshot_hash":"ad6ca818d7f99a39e257810aecaf41dc5b634948752562c53aa704582812f2e0","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-029","AC-042","AC-083","REQ-029","REQ-042","REQ-064","REQ-083"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":["AC-029","AC-042","AC-083"],"added_ids":[],"changed_ids":["AC-029","AC-042","AC-083","REQ-029","REQ-042","REQ-064","REQ-083"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"e24accf4fac3232cda97425345345f190cca0713e700fc430933540d31fab91d","event_type":"reconcile","event_version":1,"open_decisions":["OD-010: Fixed FIR/Ridge RAM budget and layout (including numeric/preprocessing states and transient allowance), maximum taps, per-rate history options, capacity delivery/versioning to the software, reservation placement (static or once at startup), and quantitative target memory/stack acceptance margins are not yet decided. 65 taps is an unaccepted candidate, not a default."],"previous_event_hash":"d50e196dccfe92eaecc9dc360b21fd9ae18e608d0479e42287e025c092ded02b","previous_snapshot_hash":"ad6ca818d7f99a39e257810aecaf41dc5b634948752562c53aa704582812f2e0","recorded_at":"2026-09-21T08:06:12.973685+00:00","relationships":[],"revision":176,"snapshot_hash":"bf7c2ae2c9d6dfbba729c7fb7cb733c0e3cb8f12869226b5624349475765a4d6","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-027","AC-091","DEC-090","DISC-094","REQ-027","REQ-091"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":["AC-027","AC-091"],"added_ids":["DEC-090","DISC-094"],"changed_ids":["AC-027","AC-091","REQ-027","REQ-091"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"91e01c834f9303429d047bc390a7c01a8e0f6a13a56f592d4f63f4842fb8a3f5","event_type":"reconcile","event_version":1,"open_decisions":["OD-010: Fixed FIR/Ridge RAM budget and layout (including numeric/preprocessing states and transient allowance), maximum taps, reservation placement (static or once at startup), and quantitative target memory/stack acceptance margins are not yet decided. 65 taps is an unaccepted candidate, not a default."],"previous_event_hash":"e24accf4fac3232cda97425345345f190cca0713e700fc430933540d31fab91d","previous_snapshot_hash":"bf7c2ae2c9d6dfbba729c7fb7cb733c0e3cb8f12869226b5624349475765a4d6","recorded_at":"2026-09-21T09:18:02.395675+00:00","relationships":[],"revision":177,"snapshot_hash":"df119098f313a2bf2c8b62ef550fb8937e48e74664394061b092a25d2c10aa9b","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-013","AC-026","AC-027","AC-043","AC-044","AC-045","AC-054","AC-085","AC-090","AC-091","AC-092","AC-093","AC-094","AC-095","AC-096","DISC-095","REQ-002","REQ-013","REQ-026","REQ-027","REQ-028","REQ-043","REQ-045","REQ-049","REQ-064","REQ-085","REQ-090","REQ-091","REQ-092","REQ-093","REQ-094","REQ-095","REQ-096"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":["AC-013","AC-026","AC-027","AC-043","AC-044","AC-045","AC-054","AC-085","AC-090","AC-091","AC-092"],"added_ids":["AC-093","AC-094","AC-095","AC-096","DISC-095","REQ-093","REQ-094","REQ-095","REQ-096"],"changed_ids":["AC-013","AC-026","AC-027","AC-043","AC-044","AC-045","AC-054","AC-085","AC-090","AC-091","AC-092","REQ-002","REQ-013","REQ-026","REQ-027","REQ-028","REQ-043","REQ-045","REQ-049","REQ-064","REQ-085","REQ-090","REQ-091","REQ-092"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4939449a97df6663c391429f114401b53ec45e764381f42a8618386d3246993b","event_type":"reconcile","event_version":1,"open_decisions":["OD-010: Review/adopt or revise the completed PP-001 RAM envelopes and quantitative acceptance thresholds. Arithmetic, scope and the 96-row acceptance plan are now documented; whole-device feasibility still requires implementation and matched target measurements. PP-001 is a proposal, not an adopted limit or a measured PASS."],"previous_event_hash":"91e01c834f9303429d047bc390a7c01a8e0f6a13a56f592d4f63f4842fb8a3f5","previous_snapshot_hash":"df119098f313a2bf2c8b62ef550fb8937e48e74664394061b092a25d2c10aa9b","recorded_at":"2026-09-21T09:45:14.784141+00:00","relationships":[],"revision":178,"snapshot_hash":"b38dc779112431a2ff3fcbe80149af5c451d5911c92968af3e16e773d1d31099","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["DEC-091","DISC-096"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["DEC-091","DISC-096"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"5828c43dc0c5f5ec6590e765bae8363585cbff4ace8de642cdd4d199144524e5","event_type":"reconcile","event_version":1,"open_decisions":["None for the desktop JSON export delivery slice. OD-010 (PP-001 RAM envelopes and target memory/stack acceptance thresholds) is deferred to the firmware project by DEC-091; no proposal is adopted and no target feasibility is claimed."],"previous_event_hash":"4939449a97df6663c391429f114401b53ec45e764381f42a8618386d3246993b","previous_snapshot_hash":"b38dc779112431a2ff3fcbe80149af5c451d5911c92968af3e16e773d1d31099","recorded_at":"2026-09-21T09:48:39.653379+00:00","relationships":[],"revision":179,"snapshot_hash":"ace2e31d168a2cefe963d30ebacfc53e098b626f4b44c5b3ccd4261fe1440fc9","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"27c15e322afbf432318e98119969503e3d274263a495e5146cbe9f46308379c9","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"5828c43dc0c5f5ec6590e765bae8363585cbff4ace8de642cdd4d199144524e5","previous_snapshot_hash":"ace2e31d168a2cefe963d30ebacfc53e098b626f4b44c5b3ccd4261fe1440fc9","recorded_at":"2026-09-21T09:49:08.957703+00:00","relationships":[],"revision":180,"snapshot_hash":"1b44778c67aca862dd446aabac7d365af0fd126655d2c195dda79cef51f68fbd","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"13d91dd5adef55c386b4a5e6c826b407a423a71cf04d158edcd24d37a2a1e152","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"27c15e322afbf432318e98119969503e3d274263a495e5146cbe9f46308379c9","previous_snapshot_hash":"1b44778c67aca862dd446aabac7d365af0fd126655d2c195dda79cef51f68fbd","recorded_at":"2026-09-21T09:49:20.832598+00:00","relationships":[],"revision":180,"snapshot_hash":"df27392178eac6df53609b461cedbde9a32ad68a3c402932dfe1de21f2df6b97","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"baseline_contract_hash":"fd05c30e23052d6ba0ecec9d94544ad214b095dddc822a13a488b0406afa001f","conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"0b90bad412455d56fccec2e179ee26e4b634118f744e7a19986fb1d351dbe382","event_type":"reopen","event_version":1,"open_decisions":[],"previous_event_hash":"13d91dd5adef55c386b4a5e6c826b407a423a71cf04d158edcd24d37a2a1e152","previous_snapshot_hash":"df27392178eac6df53609b461cedbde9a32ad68a3c402932dfe1de21f2df6b97","recorded_at":"2026-09-21T09:50:50.370101+00:00","relationships":[],"revision":181,"snapshot_hash":"d8feedd149798f8aef7844b13b63b78968a01d03899d50b2931bc13ccaa41eb3","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"a764af4002d0a800ad3cc4c79ae2d1d5a093c2566ec4c8acdf7c2ab589f6ab43","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"0b90bad412455d56fccec2e179ee26e4b634118f744e7a19986fb1d351dbe382","previous_snapshot_hash":"d8feedd149798f8aef7844b13b63b78968a01d03899d50b2931bc13ccaa41eb3","recorded_at":"2026-09-21T09:51:02.876165+00:00","relationships":[],"revision":181,"snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"執行桌面端 JSON 匯出，","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"01a0c35a-f51b-72a3-9394-ff212f3939a7","task_ref":"01a0c356-d77c-7421-935c-72e5a478a492","turn_id":"01a0c35a-f485-70c3-989d-6f7eeb78fd31"},"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"5ad419dc59d15acf897a743779efd5b268d6927ac6671537127e08eeda7998b4","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"a764af4002d0a800ad3cc4c79ae2d1d5a093c2566ec4c8acdf7c2ab589f6ab43","previous_snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","recorded_at":"2026-09-21T09:51:21.046995+00:00","relationships":[],"revision":181,"snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":181,"snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"5a2c8baf1277baa126e83c16abfd8ea1cd62f39626a8b3d0205360ace1008288","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a0c35a-f51b-72a3-9394-ff212f3939a7"],"source_ref":"01a0c35a-f51b-72a3-9394-ff212f3939a7","summary":"User desktop-only execution scope was reconciled in DEC-091 and DISC-096, with firmware RAM decisions remaining in firmware. SPEC confirmed and continuation bound to current task. No product changes. Managed execution admission is still being diagnosed; local venv resolves yaml dependency, but runtime verification matrix is missing.","task_ref":"01a0c356-d77c-7421-935c-72e5a478a492","turn_id":"01a0c35a-f485-70c3-989d-6f7eeb78fd31"},"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"2aa41baf429fe8c03bf819ff018bf0ad4742e95d8b83a1da2cab18c45e766f7f","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"5ad419dc59d15acf897a743779efd5b268d6927ac6671537127e08eeda7998b4","previous_snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","recorded_at":"2026-09-21T09:52:31.003574+00:00","relationships":[],"revision":181,"snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"開始執行 SPEC-0039","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"01a0c364-7ddb-7cb1-8309-6737802bf033","task_ref":"01a0c356-d77c-7421-935c-72e5a478a492","turn_id":"01a0c364-7d5b-72a1-af47-9274f5f7d7a6"},"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"b5a53cd62056682177368c300907598d1420ab1c67e4915ca2443241ab9beab2","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"2aa41baf429fe8c03bf819ff018bf0ad4742e95d8b83a1da2cab18c45e766f7f","previous_snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","recorded_at":"2026-09-21T09:56:14.941692+00:00","relationships":[],"revision":181,"snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":181,"snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"2491f0a335240c51c255e6713c11033d4f88652e2168415a9ba076cb535071b1","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a0c364-7ddb-7cb1-8309-6737802bf033"],"source_ref":"01a0c364-7ddb-7cb1-8309-6737802bf033","summary":"User explicitly requests 開始執行 SPEC-0039 for the unchanged confirmed desktop JSON export scope. No new requirements. Proceed through current-scope validation preparation and implementation.","task_ref":"01a0c356-d77c-7421-935c-72e5a478a492","turn_id":"01a0c364-7d5b-72a1-af47-9274f5f7d7a6"},"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"dc6da10e8d05167d208d5a435a3a40738825ca1d04bb60f6590a9fd52e610a79","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"b5a53cd62056682177368c300907598d1420ab1c67e4915ca2443241ab9beab2","previous_snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","recorded_at":"2026-09-21T09:56:51.953957+00:00","relationships":[],"revision":181,"snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"baseline_contract_hash":"fd05c30e23052d6ba0ecec9d94544ad214b095dddc822a13a488b0406afa001f","conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4e76a75b59f07ba0b1768f1bb0b25f327ce5329966e2e2b3f5ec4d243f92209e","event_type":"reopen","event_version":1,"open_decisions":[],"previous_event_hash":"dc6da10e8d05167d208d5a435a3a40738825ca1d04bb60f6590a9fd52e610a79","previous_snapshot_hash":"c1cb60255161d230082a80456aeaa08351d646c592f40a1a9a1aeb32ba1b19c3","recorded_at":"2026-09-22T01:51:17.672115+00:00","relationships":[],"revision":182,"snapshot_hash":"a57ab06b427c07b6983dd16ac3b8dc2b54ab2c6c7a75e5a3346e6d3cc7547074","verdict":"BLOCKED","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-097","AC-098","DEC-092","DISC-097","REQ-097","REQ-098"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["AC-097","AC-098","DEC-092","DISC-097","REQ-097","REQ-098"],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"03a4c1702be1000edfe55ef1559cea3d281208161d577f66426568bdb2c3cb2d","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"4e76a75b59f07ba0b1768f1bb0b25f327ce5329966e2e2b3f5ec4d243f92209e","previous_snapshot_hash":"a57ab06b427c07b6983dd16ac3b8dc2b54ab2c6c7a75e5a3346e6d3cc7547074","recorded_at":"2026-09-22T01:52:40.460871+00:00","relationships":[],"revision":183,"snapshot_hash":"cd615ea33d737bbd17c26a8e5919b6f64b9aef4e873490f4b165d6b3b560e5fa","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"開始執行","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:01a0c6d2-2051-7b23-b2da-271b6992fb8f:execute-ui","task_ref":"01a0c356-d77c-7421-935c-72e5a478a492","turn_id":"01a0c6d2-2051-7b23-b2da-271b6992fb8f"},"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"d414e070c95d955cfdf9fca7f8b8323be91fc79c899e711d4933b56762bcd21f","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"03a4c1702be1000edfe55ef1559cea3d281208161d577f66426568bdb2c3cb2d","previous_snapshot_hash":"cd615ea33d737bbd17c26a8e5919b6f64b9aef4e873490f4b165d6b3b560e5fa","recorded_at":"2026-09-22T01:55:04.507735+00:00","relationships":[],"revision":183,"snapshot_hash":"cd615ea33d737bbd17c26a8e5919b6f64b9aef4e873490f4b165d6b3b560e5fa","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-097","DEC-093","DISC-098","REQ-097"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":["AC-097"],"added_ids":["DEC-093","DISC-098"],"changed_ids":["AC-097","REQ-097"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"a61d2dc217c88d9624c192710d5fec8ecc2c5cc56149461813533cdeed5b5952","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"d414e070c95d955cfdf9fca7f8b8323be91fc79c899e711d4933b56762bcd21f","previous_snapshot_hash":"cd615ea33d737bbd17c26a8e5919b6f64b9aef4e873490f4b165d6b3b560e5fa","recorded_at":"2026-09-22T01:55:56.461784+00:00","relationships":[],"revision":184,"snapshot_hash":"9c1f521633d846cdbc53012c5b875d2743f4d131aebd5e6c668496a44c5c672b","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"只要處理軟體輸出JSON；韌體匯入、ESP32記憶體配置及裝置驗證這些不需要。繼續執行","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:01a0c6e1-3f04-7e23-8fbe-6bbdb153c03d:continue-desktop","task_ref":"01a0c356-d77c-7421-935c-72e5a478a492","turn_id":"01a0c6e1-3f04-7e23-8fbe-6bbdb153c03d"},"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"4b921925fae28b011ef932aebc25834533f1baaf6ec3521a562626214ee6fe21","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"a61d2dc217c88d9624c192710d5fec8ecc2c5cc56149461813533cdeed5b5952","previous_snapshot_hash":"9c1f521633d846cdbc53012c5b875d2743f4d131aebd5e6c668496a44c5c672b","recorded_at":"2026-09-22T02:11:29.187073+00:00","relationships":[],"revision":184,"snapshot_hash":"9c1f521633d846cdbc53012c5b875d2743f4d131aebd5e6c668496a44c5c672b","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":["AC-001","AC-002","AC-003","AC-004","AC-005","AC-006","AC-007","AC-008","AC-009","AC-010","AC-011","AC-012","AC-013","AC-014","AC-015","AC-016","AC-017","AC-018","AC-019","AC-020","AC-021","AC-022","AC-023","AC-024","AC-025","AC-026","AC-027","AC-028","AC-029","AC-030","AC-031","AC-032","AC-033","AC-034","AC-035","AC-036","AC-037","AC-038","AC-039","AC-040","AC-041","AC-042","AC-043","AC-044","AC-045","AC-046","AC-047","AC-048","AC-049","AC-050","AC-051","AC-052","AC-053","AC-054","AC-055","AC-056","AC-057","AC-058","AC-059","AC-060","AC-061","AC-062","AC-063","AC-064","AC-065","AC-066","AC-067","AC-068","AC-069","AC-070","AC-071","AC-072","AC-073","AC-074","AC-075","AC-076","AC-077","AC-078","AC-079","AC-080","AC-081","AC-082","AC-083","AC-084","AC-085","AC-086","AC-087","AC-088","AC-089","AC-090","AC-091","AC-092","AC-093","AC-094","AC-095","AC-096","AC-097","AC-098","DEC-094","DISC-099","REQ-001","REQ-002","REQ-003","REQ-004","REQ-005","REQ-006","REQ-007","REQ-008","REQ-009","REQ-010","REQ-011","REQ-012","REQ-013","REQ-014","REQ-015","REQ-016","REQ-017","REQ-018","REQ-019","REQ-020","REQ-021","REQ-022","REQ-023","REQ-024","REQ-025","REQ-026","REQ-027","REQ-028","REQ-029","REQ-030","REQ-031","REQ-032","REQ-033","REQ-034","REQ-035","REQ-036","REQ-037","REQ-038","REQ-039","REQ-040","REQ-041","REQ-042","REQ-043","REQ-044","REQ-045","REQ-046","REQ-047","REQ-048","REQ-049","REQ-050","REQ-051","REQ-052","REQ-053","REQ-054","REQ-055","REQ-056","REQ-057","REQ-058","REQ-059","REQ-060","REQ-061","REQ-062","REQ-063","REQ-064","REQ-065","REQ-066","REQ-067","REQ-068","REQ-069","REQ-070","REQ-071","REQ-072","REQ-073","REQ-074","REQ-075","REQ-076","REQ-077","REQ-078","REQ-079","REQ-080","REQ-081","REQ-082","REQ-083","REQ-084","REQ-085","REQ-086","REQ-087","REQ-088","REQ-089","REQ-090","REQ-091","REQ-092","REQ-093","REQ-094","REQ-095","REQ-096","REQ-097","REQ-098"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":["AC-001","AC-002","AC-003","AC-004","AC-005","AC-006","AC-007","AC-008","AC-009","AC-010","AC-011","AC-012","AC-013","AC-014","AC-015","AC-016","AC-017","AC-018","AC-019","AC-020","AC-021","AC-022","AC-023","AC-024","AC-025","AC-026","AC-027","AC-028","AC-029","AC-030","AC-031","AC-032","AC-033","AC-034","AC-035","AC-036","AC-037","AC-038","AC-039","AC-040","AC-041","AC-042","AC-043","AC-044","AC-045","AC-046","AC-047","AC-048","AC-049","AC-050","AC-051","AC-052","AC-053","AC-054","AC-055","AC-056","AC-057","AC-058","AC-059","AC-060","AC-061","AC-062","AC-063","AC-064","AC-065","AC-066","AC-067","AC-068","AC-069","AC-070","AC-071","AC-072","AC-073","AC-074","AC-075","AC-076","AC-077","AC-078","AC-079","AC-080","AC-081","AC-082","AC-083","AC-084","AC-085","AC-086","AC-087","AC-088","AC-089","AC-090","AC-091","AC-092","AC-093","AC-094","AC-095","AC-096","AC-097","AC-098"],"added_ids":["DEC-094","DISC-099"],"changed_ids":["AC-001","AC-002","AC-003","AC-004","AC-005","AC-006","AC-007","AC-008","AC-009","AC-010","AC-011","AC-012","AC-013","AC-014","AC-015","AC-016","AC-017","AC-018","AC-019","AC-020","AC-021","AC-022","AC-023","AC-024","AC-025","AC-026","AC-027","AC-028","AC-029","AC-030","AC-031","AC-032","AC-033","AC-034","AC-035","AC-036","AC-037","AC-038","AC-039","AC-040","AC-041","AC-042","AC-043","AC-044","AC-045","AC-046","AC-047","AC-048","AC-049","AC-050","AC-051","AC-052","AC-053","AC-054","AC-055","AC-056","AC-057","AC-058","AC-059","AC-060","AC-061","AC-062","AC-063","AC-064","AC-065","AC-066","AC-067","AC-068","AC-069","AC-070","AC-071","AC-072","AC-073","AC-074","AC-075","AC-076","AC-077","AC-078","AC-079","AC-080","AC-081","AC-082","AC-083","AC-084","AC-085","AC-086","AC-087","AC-088","AC-089","AC-090","AC-091","AC-092","AC-093","AC-094","AC-095","AC-096","AC-097","AC-098","REQ-001","REQ-002","REQ-003","REQ-004","REQ-005","REQ-006","REQ-007","REQ-008","REQ-009","REQ-010","REQ-011","REQ-012","REQ-013","REQ-014","REQ-015","REQ-016","REQ-017","REQ-018","REQ-019","REQ-020","REQ-021","REQ-022","REQ-023","REQ-024","REQ-025","REQ-026","REQ-027","REQ-028","REQ-029","REQ-030","REQ-031","REQ-032","REQ-033","REQ-034","REQ-035","REQ-036","REQ-037","REQ-038","REQ-039","REQ-040","REQ-041","REQ-042","REQ-043","REQ-044","REQ-045","REQ-046","REQ-047","REQ-048","REQ-049","REQ-050","REQ-051","REQ-052","REQ-053","REQ-054","REQ-055","REQ-056","REQ-057","REQ-058","REQ-059","REQ-060","REQ-061","REQ-062","REQ-063","REQ-064","REQ-065","REQ-066","REQ-067","REQ-068","REQ-069","REQ-070","REQ-071","REQ-072","REQ-073","REQ-074","REQ-075","REQ-076","REQ-077","REQ-078","REQ-079","REQ-080","REQ-081","REQ-082","REQ-083","REQ-084","REQ-085","REQ-086","REQ-087","REQ-088","REQ-089","REQ-090","REQ-091","REQ-092","REQ-093","REQ-094","REQ-095","REQ-096","REQ-097","REQ-098"],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"5e1b8b0d62d327f61b6d23f20f38246ae3d711def8934c4c25082b82a9de7b5b","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"4b921925fae28b011ef932aebc25834533f1baaf6ec3521a562626214ee6fe21","previous_snapshot_hash":"9c1f521633d846cdbc53012c5b875d2743f4d131aebd5e6c668496a44c5c672b","recorded_at":"2026-09-22T02:14:13.493462+00:00","relationships":[],"revision":185,"snapshot_hash":"620d577dd46dd0d431b3820649ee94a14d652cad64fec389fb7bb24565a1180e","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"14279fcb58aa4e74adace9126eef777e","event_hash":"892b957efe2757ca51316ea7ee5f336ef1ea5a1bfc8dd52579f60b1959ecd0a7","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"5e1b8b0d62d327f61b6d23f20f38246ae3d711def8934c4c25082b82a9de7b5b","previous_snapshot_hash":"620d577dd46dd0d431b3820649ee94a14d652cad64fec389fb7bb24565a1180e","recorded_at":"2026-09-22T02:14:37.172701+00:00","relationships":[],"revision":185,"snapshot_hash":"2034ba6b675e5b20a17b4e135a02f02504f80887e961cbc0c0a476cd517d1355","verdict":"PASS","working_id":"WORKING-SPEC-01a0a7a57a23-model-parameter-export"}
```
<!-- spec-audit:end -->
