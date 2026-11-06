---
spec_version: 1
spec_id: SPEC-0052
revision: 5
status: confirmed
change_set: ignore-reason-heading
working_id: WORKING-SPEC-87089bf924dc-ignore-reason-heading
task_ref: ignore-reason-heading-20261104
---
# Ignore 事件窗格標題修改方案

## Problem
使用者要求 Annotate & Classify 的 Ignore 事件窗格左上標題改為 ignore reason，並於後續要求提出修改方案。

## Solution
本次補充：波形標註區塊左上角依既有 modelData.reason 顯示 Ignore 原因，例如 flip；兩個 IMU 共用 WavePanel 繫結。使用者已明確指定原因文字，無待選方案。

事件時間軸左側標題採用 Ignore reason，保留既有首字大寫樣式。修改位置為 src/dual_imu_collision_studio/qml/Main.qml 的 annotationLanes 顯示標籤。

## User Stories
使用者由標題辨識 Ignore 事件窗格的原因語意。

## Requirements
| ID | Requirement | Source |
|---|---|---|
| REQ-001 | 事件時間軸 Ignore 窗格的左側標題顯示 Ignore reason。 | user:initial-ignore-reason-request |
| REQ-002 | 本次僅整理修改方案；未提出額外產品修改需求。 | user:ignore-reason-proposal-repeat |

| REQ-003 | Internal IMU 與 External IMU 波形區塊左上角的 Ignore 標籤顯示該事件填寫的 reason，例如 flip；沿用非 Ignore 標籤與既有 Anchor / Suggested 前綴。 | user:waveform-reason-answer |

## Decisions
| ID | Decision | Source |
|---|---|---|
| DEC-001 | 建議保留既有首字大寫；方案整理不新增產品修改。 | assistant:proposal-candidate |

| DEC-002 | 使用者於方案呈現後指示「開始執行」，採用 Ignore reason 標題並完成既定驗證；保留先前方案與修改歷史。 | user:current-start-execution-message |

| DEC-003 | 使用者以截圖圈選波形區塊左上角，並明確選擇顯示填寫的原因（例如 flip），不是固定 Reason 字樣；此為先前標題修改的範圍補充。 | user:waveform-reason-answer |

## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | Ignore 事件窗格標題為 Ignore reason，常用與最小支援視窗寬度下文字完整且不重疊。 | 開啟 Annotate & Classify，檢查事件窗格，記錄視窗大小與截圖。 | 2026-11-04：Qt offscreen 軟體渲染與幾何斷言完成，1366x820 與 1180x720 皆顯示完整標題且未侵入事件軌道；截圖已檢視。證據：artifacts/ignore-reason-heading-61357faeb489/result.json 及同目錄 PNG。 |
| AC-002 | REQ-001, REQ-002 | 修改集中於顯示標籤，QML 正常載入，方案整理未再修改產品。 | 檢視該字串差異並使用既有 QML 冒煙測試。 | 本次重跑 3 項既有 QML 冒煙測試，3 passed，退出碼 0；核對差異仍為一個顯示字串。保留其他既有未提交修改。 |

| AC-003 | REQ-003 | 以實際 Ignore reason=flip 的標註資料，兩個 IMU 波形左上皆顯示 flip；Cycle 等非 Ignore 名稱及 Anchor / Suggested 前綴保留。 | 真實 Controller 建立標註，於 Qt/QML 檢查兩個波形的文字並截圖；檢查共用顯示繫結。 | 2026-11-04：以真實 Controller 與合成錄波資料驗證兩個 IMU 的 flip / sensor reset、非 Ignore 名稱與 Anchor / Suggested 前綴，共 20 項文字/繫結檢查完成。1366x820 實際 Qt 截圖已檢視，原因標籤可讀。1180x720 僅確認繫結，既有頁首配置使波形區高度不足，不宣稱該尺寸的波形標籤可視驗收。證據：artifacts/waveform-ignore-reason-e0fd03bcf0f9/result.json 與 1366x820.png。既有 4 項 QML 測試通過，退出碼 0。 |

## Acceptance Mapping

```json
{
  "AC-001": {
    "evidence_claims": [
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "僅 QML 靜態顯示文字；以既有冒煙測試及 Qt 軟體渲染確認標題和幾何，沒有硬體、時序或效能主張。"
  },
  "AC-002": {
    "evidence_claims": [
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "僅 QML 靜態顯示文字；以既有冒煙測試及 Qt 軟體渲染確認標題和幾何，沒有硬體、時序或效能主張。"
  },
  "AC-003": {
    "evidence_claims": [
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "以既有 reason 資料調整 QML 顯示繫結；不變更型別、狀態、事件或介面。"
  }
}
```

## Relationships
無其他規格依賴；不修改其他既有變更集。

## Out of Scope
事件種類值、工具按鈕、資料格式、標註處理、架構與演算法。

## Open Decisions
None

## Routing/Gates
純顯示文字方案，無架構、命名型別、狀態、依賴或演算法變更。無需新增硬體驗證或效能主張。先前自動化測試不等同實際視窗視覺驗收。

## Revision History
- r5，2026-11-04：完成共用 WavePanel 標籤繫結修改，記錄雙 IMU 原因文字、既有前綴與 4 項相關 QML 測試結果。
- r4，2026-11-04：依使用者截圖及原因文字選項回答，新增 REQ-003 / DEC-003 / AC-003；保留原下方列標題修改。
- r2，2026-11-04：記錄使用者本次「開始執行」，修正無待決事項的格式並附上 Qt 渲染與測試證據；產品標題先前已完成，本回合未重寫其他產品內容。
- r1，2026-11-04：依使用者要求整理方案，記錄先前已修改事實；不回溯宣稱存在規格或額外執行授權。
| 3 | 2026-11-04 | Reopened before clarification: 使用者以截圖補充波形區塊左上標籤，並確認應顯示事件填寫的原因，例如 flip；保留已完成的下方 Ignore reason 列標題。 |

## Discussion Context
本次使用者指出波形區塊左上 Ignore 標籤，並回答「顯示填寫的原因（例如 flip）」。應使用實際 reason 值，不是固定 Reason 字樣。

本回合使用者在方案後指示「開始執行」。該授權適用已呈現的單一標題更名與驗證，不擴大至其他功能。已以明確載入 Segoe UI 的 Qt offscreen 渲染檢查預設與最小支援尺寸；畫面無錄製資料，僅驗收標題顯示與配置。

使用者已先要求標題更名，前一回合修改為 Ignore reason 並完成三項既有冒煙測試。本回合要求提出方案，僅補充方案文件；未新增產品操作授權。

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



### Source and Revision Audit

```jsonl
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a8bb5afcf4a5419ca01b90fa93a4f3e7","event_hash":"14575281d10b782938de4d2dee366cca0c302d7b6db16ded83ce69d63a06538b","event_type":"start","event_version":1,"open_decisions":["無需新增產品決策；首字大小寫沿用現有介面風格，屬建議呈現。"],"previous_event_hash":null,"previous_snapshot_hash":null,"recorded_at":"2026-11-04T03:26:57.364944+00:00","relationships":[],"revision":1,"snapshot_hash":"3e472b22a6f3db387bd893204d6ba43761216b6e6f434fe55e984cc3ef4072ac","verdict":"BLOCKED","working_id":"WORKING-SPEC-87089bf924dc-ignore-reason-heading"}
{"affected_ids":["AC-001","AC-002","DEC-002"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["DEC-002"],"changed_ids":["AC-001","AC-002"],"removed_ids":[]},"epoch":"a8bb5afcf4a5419ca01b90fa93a4f3e7","event_hash":"3d3550911c67b1a13ac8e248712f304191a9ef5dcdf64ea122759842f4e2b1af","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"14575281d10b782938de4d2dee366cca0c302d7b6db16ded83ce69d63a06538b","previous_snapshot_hash":"3e472b22a6f3db387bd893204d6ba43761216b6e6f434fe55e984cc3ef4072ac","recorded_at":"2026-11-04T03:31:24.372628+00:00","relationships":[],"revision":2,"snapshot_hash":"a72a022e6bf947ebb8bd444415abdee5fa30d2717f81d5de0fe02f04cb5f636e","verdict":"PASS","working_id":"WORKING-SPEC-87089bf924dc-ignore-reason-heading"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a8bb5afcf4a5419ca01b90fa93a4f3e7","event_hash":"e278c6d36631b97e146906979f1256f500511192ec6076c28a2c6ea0fbbd2297","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"3d3550911c67b1a13ac8e248712f304191a9ef5dcdf64ea122759842f4e2b1af","previous_snapshot_hash":"a72a022e6bf947ebb8bd444415abdee5fa30d2717f81d5de0fe02f04cb5f636e","recorded_at":"2026-11-04T03:31:59.959231+00:00","relationships":[],"revision":2,"snapshot_hash":"5bcafd75e2cb65f64ed254aed97268c808efea7d60be21e823d9439f35aa75d3","verdict":"PASS","working_id":"WORKING-SPEC-87089bf924dc-ignore-reason-heading"}
{"affected_ids":[],"baseline_contract_hash":"46bba61d4244fbd4014872cd9a1c59a9ccf63c7dc84a8ea8a1c9c69f7dbfb995","conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a8bb5afcf4a5419ca01b90fa93a4f3e7","event_hash":"e4b73afaef27e814b3c7d2408af98b955b68f0258f63a7b176b6f7f85db1a14c","event_type":"reopen","event_version":1,"open_decisions":[],"previous_event_hash":"e278c6d36631b97e146906979f1256f500511192ec6076c28a2c6ea0fbbd2297","previous_snapshot_hash":"5bcafd75e2cb65f64ed254aed97268c808efea7d60be21e823d9439f35aa75d3","recorded_at":"2026-11-04T03:52:41.565267+00:00","relationships":[],"revision":3,"snapshot_hash":"323e95d6c267813e7317915fbf951c4ca218f3160db056b09f79925948dd4a49","verdict":"BLOCKED","working_id":"WORKING-SPEC-87089bf924dc-ignore-reason-heading"}
{"affected_ids":["AC-003","DEC-003","REQ-003"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["AC-003","DEC-003","REQ-003"],"changed_ids":[],"removed_ids":[]},"epoch":"a8bb5afcf4a5419ca01b90fa93a4f3e7","event_hash":"b69c12dca3148b56b4897c4293cd4eabbe32838157fbc58ae95927e44aa42cf7","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"e4b73afaef27e814b3c7d2408af98b955b68f0258f63a7b176b6f7f85db1a14c","previous_snapshot_hash":"323e95d6c267813e7317915fbf951c4ca218f3160db056b09f79925948dd4a49","recorded_at":"2026-11-04T03:53:10.661591+00:00","relationships":[],"revision":4,"snapshot_hash":"f1029fa5ea7bf558f9933dfad13ec447ccd6b8a79554a17f00a0b5480cabbe20","verdict":"PASS","working_id":"WORKING-SPEC-87089bf924dc-ignore-reason-heading"}
{"affected_ids":["AC-003"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":["AC-003"],"removed_ids":[]},"epoch":"a8bb5afcf4a5419ca01b90fa93a4f3e7","event_hash":"5d90090948412b153cdc81cc9c2ceb737496a33facc2775339339f6814479df9","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"b69c12dca3148b56b4897c4293cd4eabbe32838157fbc58ae95927e44aa42cf7","previous_snapshot_hash":"f1029fa5ea7bf558f9933dfad13ec447ccd6b8a79554a17f00a0b5480cabbe20","recorded_at":"2026-11-04T03:56:17.240202+00:00","relationships":[],"revision":5,"snapshot_hash":"7aa0653fbb10cee63ed7fa7f5ab0472241042c80e801261a1bcc0ef57dcad9f0","verdict":"PASS","working_id":"WORKING-SPEC-87089bf924dc-ignore-reason-heading"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a8bb5afcf4a5419ca01b90fa93a4f3e7","event_hash":"e9854be68b8900c96992635f7f3039858c2a4f3ebc6aa35d22fb729964e767cd","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"5d90090948412b153cdc81cc9c2ceb737496a33facc2775339339f6814479df9","previous_snapshot_hash":"7aa0653fbb10cee63ed7fa7f5ab0472241042c80e801261a1bcc0ef57dcad9f0","recorded_at":"2026-11-04T03:56:29.498224+00:00","relationships":[],"revision":5,"snapshot_hash":"3aa1949ee34e84e2b2c407bae622a842dcfe4daed65aeab0251eb21a226483fb","verdict":"PASS","working_id":"WORKING-SPEC-87089bf924dc-ignore-reason-heading"}
```
<!-- spec-audit:end -->
