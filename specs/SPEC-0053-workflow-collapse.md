---
spec_version: 1
spec_id: SPEC-0053
revision: 4
status: implemented
change_set: workflow-collapse
task_ref: workflow-collapse-20261104
---
# WORKFLOW 導覽欄展開與縮合

## Problem
使用者要求「workdlow增加可以縮合的功能」。專案對應 Main.qml 左側 WORKFLOW 導覽欄。

## Requirements
| ID | Requirement | Source |
|---|---|---|
| REQ-001 | 左側 WORKFLOW 可由常駐按鈕展開與縮合，預設展開。 | user:workdlow-collapse |
| REQ-002 | 縮合時保留步驟編號／完成圖示、選取高亮、可用狀態與頁面切換；滑鼠提示顯示完整步驟名稱。 | assistant:bounded-implementation-default |
| REQ-003 | 縮合隱藏步驟名稱及 Session limits，工作區取得釋出的寬度；展開可恢復。 | assistant:bounded-implementation-default |

## Decisions
| ID | Decision | Source |
|---|---|---|
| DEC-001 | 以 Main.qml 的 adapter 私有 Boolean 表示縮合；展開 238 px、縮合 72 px；保留當前頁面，狀態不寫入專案。 | assistant:bounded-implementation-default |
| DEC-002 | 使用既有 Qt 控制項與字型樣式，切換按鈕支援滑鼠及鍵盤，提供可存取名稱與提示。 | assistant:bounded-implementation-default |

## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-003 | 1366x820、1180x720 皆可往返縮合／展開；工作區寬度增加 166 px，沒有重疊。 | Qt offscreen 真實滑鼠／鍵盤互動、幾何檢查與截圖。 | Qt 真實互動通過；1366×820／1180×720 皆為 238→72 px，workspace +166 px；截圖見 artifacts/workflow-collapse-20261104-qt03。 |
| AC-002 | REQ-002 | 縮合保留導航，禁用步驟仍不可點選；當前頁面、資料與 dirty 狀態不被切換改變。 | 真實 Controller 與 QML 互動、既有 smoke tests。 | 實際匯入與 Mapping 後可於窄欄切換 Annotation；禁用步驟 click 受阻而 hover 顯示名稱，選取／資料／dirty 狀態保留，Space 可展開。兩項參數化整合測試通過。 |
| AC-003 | REQ-001, REQ-002, REQ-003 | QML 載入無新增錯誤；架構 render、design 及 development gate 通過。 | 專案 architecture_cli 與既有 QML tests。 | 完整既有 QML smoke 33 passed；新增 Qt 整合 2 passed；沒有 QML runtime warnings。render、design gate、development gate、ruff check、git diff --check 退出碼皆 0。 |

## Out of Scope
跨視窗記憶、專案格式、Controller 或 domain 行為、其他未提交變更。

## Open Decisions
None. 使用者已於概念圖呈現後明確回覆「採用」。

## Concept Review
2026-11-04：使用者補充「我想確認展開/縮合的概念圖」。先呈現可互動概念預覽，產品實作尚未開始，等待對概念的回饋。預覽不是正式產品畫面。

概念驗證：headless Chrome 實際點擊展開／縮合、步驟切換、禁用步驟與恢復，共 9 項互動／可視檢查通過；桌面實際側欄 238→72 px、工作區 +166 px；360 px 預覽無水平溢位。這些結果只驗證概念圖，不代替產品驗收。架構 design gate 通過；工程路由另報既有 layout 與 validation planning 阻擋，尚未進入產品修改。

## Verification
2026-11-04：已完成採用範圍；測試共 35 項通過。結果索引 artifacts/workflow-collapse-20261104-summary/result.json。正式產品改動僅 Main.qml 側欄與 window-local Boolean；治理來源、產生檔及互動測試同步更新。保留其他既有未提交變更。

測試在 Qt offscreen software rendering 執行；明確載入 Segoe UI／symbol fonts 後檢視截圖。沒有實體裝置或桌面操作效能主張。專案指定 architecture_cli gates 通過，保留 SHOULD SYM004（部分 QML 符號無 analyzer）提示。外掛工程 router 75 秒逾時，先前 layout/planning findings 未宣稱修復；不以其取代專案 gate。

## Adopted Concept
2026-11-04 user:adopt-workflow-concept: 採用。確認展開 238 px／縮合 72 px、保留圖示導航、同視窗記憶的已展示方向；本次實作沿用原始功能要求的授權。

## Execution Authority
使用者直接要求實作本功能；依本次上層開發指示，必要且可逆的修改已在授權範圍。沒有聲稱使用者說過「開始執行」或逐項確認預設值。

## Discussion History
2026-11-04 user:workdlow-collapse: workdlow增加可以縮合的功能。
2026-11-04 assistant:bounded-implementation-default: 將需求對應左側 WORKFLOW；採窄欄保留導航與同視窗狀態，準備治理與 Qt 驗證。

2026-11-04 user:concept-review: 我想確認展開/縮合的概念圖。

2026-11-04 user:adopt-workflow-concept: 採用。

2026-11-04 assistant:completion: 依 user:adopt-workflow-concept 實作並完成 35 項測試、架構 gate 與差異檢查；r4 implemented。
