---
spec_version: 1
spec_id: SPEC-0037
revision: 6
status: implemented
change_set: wizard-cross-imu-filter-prefill
---

# Mapping Wizard 跨 IMU 與 recording 帶入已採用濾波參數

## Problem

截圖顯示 Internal 已採用450 Hz/350 Hz、1.2/0.2、warmup500，但 Next 到 External 後參數空白。SPEC-0036 誤將需求限制在同一IMU新增Stage。現有 MappingWizard.qml 成功 Next 僅 step++，沒有轉交設定；兩個SensorMapping/editor各自load。這是需求涵蓋缺口，不是使用者操作錯誤。

## Solution

任何recording任一IMU明確Adopt design時，保留最新完整filter參數快照。開啟其他recording或進入下一IMU的空白設定時帶入，不覆蓋目標已有設定。複製全部stage順序、類型、邊界、衰減比與warmup，各目標草稿/計算/採用獨立。此次範本只在程式執行期間記憶，不新增跨重啟偏好。

## User Stories

- 完成Internal後，External可從相同參數開始，不必重新輸入。
- 返回再Next不會丟失External已填設定。

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | 任意recording的Internal或External明確成功Adopt design，更新本次程式執行期間最近採用參數範本，含完整stage順序、類型、邊界、衰減比與warmup。 |
| REQ-002 | 開啟其他recording Wizard或前進下一IMU時，無級或完全空白佔位級帶入最近範本；已有任何filter參數、非預設warmup或已存/採用設計優先保留。副本獨立，重開/返回不重複追加或覆寫。 |
| REQ-003 | 不複製XYZ、sensor身份、啟用選擇、SOS係數、預覽或採用狀態；未啟用時可預填editor，啟用後顯示。目標仍須以自己的取樣率Calculate及Adopt，無效頻率正常拒絕。 |
| REQ-004 | Calculate、失敗計算、未採用草稿、載入已存設計不更新範本。採用後再編輯不改變已捕捉快照，直到下一次明確採用。無範本時保持空白；關閉Wizard/切换recording不清除範本。保持SPEC-0036同頁新增級與high/low判定。 |
| REQ-005 | 範本僅在程式/視窗生命週期保留，關閉程式即清除；不寫入專案或使用者偏好。範本更新不修改其他recording資料或保存設定。 |

## Decisions

| ID | Decision |
|---|---|
| DEC-001 | 現有Wizard父層轉交只讀參數快照，兩個editor各自擁有可變草稿；不新增全域範本或持久化偏好。 |
| DEC-002 | 只填空白，保護已有輸入，保留各IMU獨立採用及原啟用選擇。 |
| DEC-003 | desktop_adapter持有跨Wizard開關與recording切換的最近明確採用快照；父層傳遞副本，各editor草稿獨立。來源不分IMU或recording，最近一次明確Adopt勝出；此次不持久化範本。 |
| DEC-004 | 所有目標只填空白，保護已有輸入/已存設定與原啟用選擇，各自重新計算採用。載入與預填不算新的Adopt。 |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-003 | A Internal實際採用450/350、1.2/0.2、warmup500後，Next到External帶入同值但不自動採用。 | 真實Wizard Qt滑鼠操作。 | PASS: real Calculate/Adopt/Next prefills External exact values and keeps target unadopted; test_cross_recording_filter_prefill.py. |
| AC-002 | REQ-001, REQ-002, REQ-005 | 關閉A的Wizard再開B，B空白Internal/External帶入完整多級與warmup；部分已有參數/自訂warmup/保存設計不覆寫；副本互不影響，反覆進入不追加。 | 多recording Qt互動及保存回歸。 | PASS: A to B to C multi-stage/warmup transfer, partial/custom/saved guards, independent copies and repeated-entry checks; build/spec37-roundtrip. |
| AC-003 | REQ-003, REQ-004 | 來源/啟用選擇保留；目標未採用不能繼續；取樣率較低時Calculate依目標Nyquist拒絕不適用範本；既有同頁複製及high/low回歸通過。 | 實際Calculate/Adopt/Next及既有回歸。 | PASS: target 500 Hz Calculate rejects inherited edges at Nyquist; 64 existing UI/filter/mapping regressions pass; architecture design/development/release exit 0. |
| AC-004 | REQ-001, REQ-004, REQ-005 | B External採用新值後C取得新範本；單純Calculate/失敗/草稿編輯/載入不更新範本；新程式實例無前次範本。 | Qt事件順序與新實例隔離測試。 | PASS: only explicit adoption updates template; preview/failure/edit/load do not; new-window isolation and actual saved-project roundtrip pass. Total 74 tests pass; architecture/change-plans/SPEC-0037-verification.md. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0036 |
| REQ-003 | refines | SPEC-0034 |
| REQ-002 | depends_on | DEC-004 |
| DEC-003 | supersedes | DEC-001 |
| DEC-004 | supersedes | DEC-002 |

## Out of Scope

SciPy數學、專案格式、跨程式重啟偏好、自動採用、覆寫已有設定。SPEC-0036維持implemented不改寫歷史。

## Open Decisions

None.

## Discussion Context

### DISC-001: 跨頁需求更正
- **Situation:** 使用者提供Internal已採用與External空白的兩張截圖。
- **Question:** 上一個設定與下一個指哪個操作？
- **Options and tradeoffs:** 截圖已明確指向同Wizard跨IMU；參數預填減少重填，獨立採用保留各來源計算驗證。
- **User answer:** 我在上一個設定已經採用了high / low pass。但點選下一個的時候，並沒有跑出相同設定。
- **Explicit rationale:** 下一頁應沿用已設定的參數。
- **Resulting impact:** REQ-001, REQ-002, REQ-003, REQ-004 修正先前只覆蓋同IMU新增級的範圍；本次尚無新的開始執行訊息。

### DISC-002: 跨recording需求
- **Situation:** 先前規格仍限制同recording，使用者補充其他recording也適用。
- **Question:** 是否限同一recording？
- **Options and tradeoffs:** 明確Adopt更新共享參數快照，减少重填且不把未採用草稿作為預設；各副本保持獨立。
- **User answer:** 不只在相同的recording，其他recording也是。
- **Explicit rationale:** 未另述。
- **Resulting impact:** REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, DEC-003, DEC-004, AC-001, AC-002, AC-003, AC-004 擴大至跨recording；DEC-003 supersedes DEC-001，DEC-004 supersedes DEC-002。尚無新執行授權。

## Routing/Gates

Spec review: PASS
Standards review: PASS

本規格已依revision 4的使用者執行授權完成實作；74項測試通過，證據見architecture/change-plans/SPEC-0037-verification.md。需求與決策未變。以下保留原實作計畫。實作前完成Boundary Design Table、Type Ownership Matrix、State Object Ownership Matrix、依賴與parent mappings，並以單一architecture_cli.py驗證planned manifest。改動限desktop_adapter內視窗/Wizard/SensorMapping/editor與採用通知，新增最近採用範本須列明owner/lifetime/read/write及父層映射，維持Learning/Project型別及跨域依賴；若新增UI狀態則登錄owner/read/write/lifetime/reset。更新manifest後render，再跑development/release gates，baseline保持空。保留QML格式與Ruff測試格式，無新演算法、執行單元或效能主張。

## Revision History

- Revision 1: 根據截圖建立跨頁帶入修正範圍，尚未實作。
| 2 | 2026-09-13 | Reopened before clarification: 使用者補充其他 recording 也應沿用最近採用的參數，擴充同Wizard跨IMU範圍。 |

- Revision 3: 依使用者補充擴大至其他recording，保留最近明確採用的參數快照。
| 6 | 2026-09-13 | Recorded implementation PASS evidence. |
