---
spec_version: 1
spec_id: SPEC-0036
revision: 4
status: implemented
change_set: filter-parameter-reuse-high-low-pass
---

# Filter 參數沿用與 High / Low pass

## Problem

SingleImuFilters.qml 的 Add filter 一律新增空白 highpass。介面與 FilterStageSpec 只接受 highpass、bandpass、bandstop；既有 design_filter 已共用 scipy.signal.buttord 與 butter，但驗證與阶數處理尚未支援 lowpass。

## Solution

新增 filter 複製同一 IMU 最近操作 stage 的欄位值。將 highpass 的介面選項整合為 High / Low pass，依單一通帶與阻帶邊界自動辨別類型，沿用既有 Butterworth SOS 設計流程。以下 DEC 為本次提出的具體建議，未聲稱使用者已批准執行。

## User Stories

- 使用者新增相似 filter 時不需重新填入全部參數。
- 使用者以同一組欄位設定高通或低通，並看見實際判定結果。

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | 同一 IMU 最近取得參數欄位焦點、編輯參數或選擇類型的 stage 為新增範本；新增時複製當下全部欄位與類型，兩級資料彼此獨立。 |
| REQ-002 | 未操作既有 stage 時以最後一級為範本；完全沒有級時保留目前空白預設。刪除範本後退回最後一級，移動級保持範本身份。Internal / External 分開管理；loadSettings 重設範本至載入後最後一級；不增加跨工作階段的偏好儲存。 |
| REQ-003 | 介面顯示 High / Low pass，使用既有四個參數：通帶邊界、阻帶邊界、最大通帶衰減比、最大阻帶振幅比。通帶頻率大於阻帶為 highpass，小於為 lowpass；相等或不完整時不宣稱成功判定。顯示 High pass / Low pass 判定文字。 |
| REQ-004 | 後端接受明確 highpass/lowpass，使用同一 buttord/butter 路徑；兩者均為單邊界且階數不倍增。有效頻率須介於 0 與 Nyquist，保持既有衰減比檢查及邊界響應驗證。無效輸入提供可理解錯誤。 |
| REQ-005 | 儲存實際 highpass/lowpass 而非顯示名稱；既有 highpass/bandpass/bandstop 專案可載入且保留既有係數與行為；lowpass 可儲存、重開、計算及使用。新增或修改仍使原採用狀態失效，必須重新 Calculate filter / Adopt design。 |

## Decisions

| ID | Decision |
|---|---|
| DEC-001 | 參數沿用採同一 editor 目前存在 stage 作為來源，新增時複製值，不維護全域預設或跨 IMU 共用偏好。這避免不同感測器互相覆蓋；首次新增仍需填入參數。 |
| DEC-002 | High / Low pass 依頻率關係自動判斷，避免多一個與參數可能矛盾的方向選項。以判定文字提醒交換頻率將改變類型；相等時拒絕計算。 |
| DEC-003 | 共用現有 SciPy Butterworth 設計，不增加演算法或第三方依賴。舊版本讀取新 lowpass 專案不在相容性承諾內。 |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | 操作 Stage 1 後新增 Stage 3 會複製 Stage 1，即使 Stage 2 存在；後續編輯不連動。刪除、重排、重載、空清單及內外 IMU 均符合來源規則。 | Qt 互動測試：焦點、輸入、Add、Remove、Move、loadSettings 與兩個 editor。 | PASS: five Qt editor tests in build/spec36-recheck cover independent copies, focus, move/delete, reload, band parameters and editor isolation; architecture/change-plans/SPEC-0036-verification.md. |
| AC-002 | REQ-003, REQ-004 | fs=1000 Hz，通帶100/阻帶50判定高通，通帶50/阻帶100判定低通；兩者符合設定衰減比，單級階數正確；相等、負值、NaN、Nyquist及缺值拒絕。 | 數值設計測試、頻率響應檢查及 UI 判定/錯誤互動。 | PASS: seven numerical tests plus real high/low/equal UI and four Wizard cases reject equal/missing/NaN/negative/out-of-range edges through Calculate; architecture/change-plans/SPEC-0036-verification.md. |
| AC-003 | REQ-005 | 舊三種類型回歸通過；lowpass 專案往返保存係數/類型及處理結果；新增/編輯後須重新計算採用才能繼續。 | 專案 round-trip、preprocessing 與既有 filter adoption 測試。 | PASS: all 86 selected cases have passing results across final run and bounded recheck, including project roundtrip and legacy regressions; architecture design/development/release exit 0. Details in architecture/change-plans/SPEC-0036-verification.md. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-005 | refines | SPEC-0034 |
| REQ-005 | refines | SPEC-0035 |
| REQ-004 | depends_on | DEC-003 |

## Out of Scope

新濾波器家族、變更 bandpass/bandstop 數學、共享或持久化最近使用偏好、自動採用設計、學習演算法調整、ADR 接受。

## Open Decisions

None.

## Discussion Context

### DISC-001: 使用者需求與共用函式
- **Situation:** 新增 filter 清空參數；high pass 欄位與 low pass 相同。
- **Question:** 本次修改應涵蓋什麼？
- **Options and tradeoffs:** 複製最近操作級減少重填；合併選項且自動判定減少操作，但須明示目前方向與無效頻率。
- **User answer:** 新增filter時，希望能自動帶入上各點選設定的參數。high pass這個名稱應該是可以改成high /low pass的，這兩個設定參數一樣。後續指出 Python 函式共用，並要求提出修改方案。
- **Explicit rationale:** 兩者設定參數相同且 Python 函式共用。
- **Resulting impact:** REQ-001 through REQ-005；DEC-001 through DEC-003 是本方案提出的具體行為規則，尚無開始執行授權。

## Routing/Gates

Spec review: PASS
Standards review: PASS

Implementation completed under the user execution instruction for revision 2. Final evidence: architecture/change-plans/SPEC-0036-verification.md. No requirement or decision changes. The following paragraph records the original pre-execution plan.

僅建立方案/SPEC；沒有修改產品或執行驗證。實作前驗證 SPEC 與本次執行授權。保持既有格式。UI 編輯與範本狀態由既有 presentation editor 擁有，FilterStageSpec/FilterDesign 與數學由 learning_qualification 擁有，儲存沿既有 application mapping 到 project_session；不增加模組、跨域依賴、port 或背景工作。實作前完成 Boundary Design Table、Type Ownership Matrix、State Object Ownership Matrix、依賴與 parent mappings，驗證 planned manifest；新增 editor 選取狀態須列明擁有者與生命週期。依最終 source/symbol/state 變化更新唯一 manifest 描述來源並透過 architecture_cli.py render；跑 development/release gates，維持 zero-entry baseline。ADR 目前為 proposed，不更改接受狀態。上述驗收 pending，無效能提升主張。

## Revision History

- Revision 1: 依使用者需求提出參數沿用與共用高低通方案；尚未實作。
| 4 | 2026-09-13 | Recorded implementation PASS evidence. |
