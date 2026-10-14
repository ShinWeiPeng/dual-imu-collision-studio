---
spec_version: 1
spec_id: SPEC-0044
revision: 3
status: confirmed
change_set: unified-qualification-json-export
working_id: WORKING-SPEC-82e0b3056dc6-unified-qualification-json-export
task_ref: 01a115a7-d434-7871-9b00-b96c7f3c17f3
---
# 統一資格判定事件規則與簡化 JSON 匯出流程

## Problem
Training 的資格判定仍使用 0.5／50 ms 與舊回放狀態處理；SPEC-0040 另在 Export Profile 使用 0.8／50 ms 共同事件回放並要求独立部署驗證。造成模型已合格但仍被匯出頁阻擋。Export JSON… 為固定文字，容易被誤認為正在匯出。

## Solution
Training 的 Qualification 與 Replay & Qualify 共用完整 0.8／50 ms 事件規則。資格判定負責驗證，Export Profile 只匯出目前已合格模型；移除独立部署驗證入口與門檻。建立真實匯出生命週期，僅在產生及寫入 JSON 時顯示 Exporting…。保留舊模型與歷史證據，舊規則結果必須在資格判定頁重新驗證後才能作為目前可匯出資格。

## User Stories
- 使用者在資格判定通過後可直接匯出模型，不必到 Export Profile 再按一次 Validate deployment。
- 使用者能分辨可匯出、選擇檔名與路徑、正在匯出、成功及失敗。
- 使用者開啟舊專案時保留模型，並能明確知道哪些結果需重新 Qualification。

## Requirements
| ID | Requirement |
|---|---|
| REQ-001 | 所有支援模型的 Training Qualification 與 Replay & Qualify 共用同一完整事件規則，解除比例 0.8、連續有效安靜時間 50 ms；不得只修改常數而保留兩套不同狀態機。已定義的新模型碰撞事件採嚴格 score > threshold 觸發並鎖定，持續超限不重複觸發。 |
| REQ-002 | 已鎖定時連續 score < threshold × 0.8 達 50 ms 才解除；等於或高於解除門檻清除計時。無效資料、明確斷點、時間倒退／重複及依既有共同事件規則辨識的取樣中斷清除計時，已鎖定者保持鎖定；中斷不算入連續有效時間。數值精度與時間邊界沿共同事件契約驗證，不放寬容差。 |
| REQ-003 | 沿用既有 Qualification 的通過標準、條件覆蓋與指標計算；使用新規則評估事件後，資格、保留候選與可匯出集合須一致。模型權重、特徵與訓練數學不因本次変更而另行改寫，但事件結果改變可影響門檻搜尋、候選選擇及合格範圍。 |
| REQ-004 | Export Profile 移除 Validate deployment／Cancel validation、Deployment 狀態、独立部署回放工作及其額外匯出門檻。僅目前新規則資格有效且原本支援 JSON 匯出的模型可直接匯出；保留完整性、有限值、維度、精度、來源／模型一致性及格式檢查，不擴大模型格式支援。 |
| REQ-005 | 待命按鈕顯示 Export JSON。名稱輸入、路徑選擇及覆寫確認不算匯出中。確認存檔後從產生內容至實際寫檔完成顯示 Exporting…；停用重複匯出操作且 UI 保持可回應。成功、錯誤及取消流程均釋放 busy 並還原按鈕，另顯示結果；極短工作不刻意延遲。 |
| REQ-006 | 維持原子寫入、安全覆寫、錯誤清理及原檔保護。取消名稱／存檔／覆寫對話框不得寫入；本次不新增寫檔途中取消功能。背景工作以不可變輸入快照執行，保護工作生命週期與關閉／切換專案時的結果歸屬。 |
| REQ-007 | 資格證據必須識別事件政策版本並綁定模型、資料、門檻及有效條件。旧專案缺少新版證據時保留原模型與歷史結果，標示需重新 Qualification，不能自動標為新版 PASS，也不列入可匯出模型。來源足夠時在 Replay & Qualify 以原模型重新驗證，不強制重訓；來源不足或不相容時明確說明原因。輸入修改使目前資格失效。 |
| REQ-008 | JSON 維持 SPEC-0040 的 model-only schema_version 1，仍不輸出 release_ratio／release_quiet_time_s，不新增舊韌體或舊格式入口。與本次無關的映射、訓練 worker、其他匯出格式契約保持。 |

## Decisions
| ID | Decision | Rationale | Source |
|---|---|---|---|
| DEC-001 | 統一 Training／Replay & Qualify 使用 0.8／50 ms 完整事件規則，取消 Export 頁再次驗證。 | 使用者明確表示這是預期流程。 | 本聊天使用者註解「這是我預期想要的」，引用統一資格判定與移除再次驗證方案。 |
| DEC-002 | Exporting… 僅代表實際匯出中，待命使用 Export JSON。 | 使用者要求區分匯出與正在匯出。 | 本聊天使用者註解「要區分匯出跟正在匯出」及「這個就是匯出中」。 |
| DEC-003 | 以上一則完整修改方案建立獨立 SPEC；保留舊模型但重驗資格、保留安全存檔及驗收範圍。 | 使用者要求建立新 spec；此要求不授權產品程式修改。 | 本聊天使用者於 2026-10-12 在完整修改方案後要求「建立新的spec」。 |

## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | 同一模型／資料／門檻／精度，Training 資格與 Replay 產生相同觸發索引及鎖定狀態；不再使用舊 0.5 路徑。 | 共同事件單元與兩流程整合測試，涵蓋既有支援模型及精度。 | Pending |
| AC-002 | REQ-002 | score 門檻及 0.8 邊界、50 ms 前／等於／後、持續超限、NaN、斷點與時間中斷符合共同規則。 | 確定性序列與原有容差的邊界測試；中斷後保持鎖定並重新累計有效安靜時間。 | Pending |
| AC-003 | REQ-003, REQ-004, REQ-008 | 新規則通過的原有可匯出模型可直接匯出，Export 頁無再次驗證控制；資格失敗不得匯出；JSON 與支援格式保持。 | Qualification 至 Export 整合、Qt/QML 與 JSON 契約測試。 | Pending |
| AC-004 | REQ-005, REQ-006 | 各對話框不是匯出中；實際工作期間呈現 Exporting…、UI 可回應且無重複工作；成功／失敗／取消後恢復。 | 可控延遲寫入、Qt 事件迴圈與工作生命週期測試；涵蓋關閉／專案切換。 | Pending |
| AC-005 | REQ-006 | 拒絕覆寫、取消、I/O 失敗及成功路徑均符合原子寫入與原檔保護。 | 暫存目錄與故障注入；核對檔案內容及暫存清理。 | Pending |
| AC-006 | REQ-007 | 舊專案模型可保留；舊證據需重驗，來源不足明確報錯；以原模型重驗可建立新版資格且不重新訓練；輸入變更不可沿用舊 PASS。 | 新舊專案載入／儲存、證據失效、重驗成功／失敗與禁止重訓測試。 | Pending |
| AC-007 | REQ-001, REQ-003, REQ-004, REQ-008 | 除已說明事件政策與資格結果改變外，模型數學、JSON 格式及其他流程無未核准回歸；架構與審查符合。 | 相關回歸、architecture_cli development/release、規範與 Spec code review；不放寬既有門檻。 | Pending |

## Relationships
| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0040 |
| REQ-004 | supersedes | SPEC-0040 |
| REQ-007 | refines | SPEC-0040 |
| REQ-008 | refines | SPEC-0040 |
| REQ-008 | refines | SPEC-0041 |

取代範圍僅為 SPEC-0040 REQ-007 的獨立部署資格門檻及 REQ-008 的部署驗證 UI；其餘 model-only JSON、安全檢查與證據追溯契約保持。

## Out of Scope
實機部署／硬體驗收、重寫模型擬合演算法、新增 JSON 模型家族支援、修改韌體、恢復舊韌體格式、放寬 Qualification 判定標準、擴充 worker 選項、寫檔途中取消、提交或推送 Git。不將桌面資格通過宣稱為實機已驗收。

## Architecture impact
事件政策與資格證據由 learning_qualification 擁有；profile_export 維持模型序列化與完整性契約；studio_application 管理資格與匯出工作的組合及生命週期；desktop_adapter 投影 UI 狀態與檔案 I/O；project_session 映射政策版本及證據。實作前核對現有架構、建立 boundary/type/state ownership 表、依賴與 parent mapping，將維護描述置於 architecture/designs，經生成及單一 architecture_cli gate。不得手改 generated manifest/views 或自行接受 ADR。

## Open Decisions
None.

## Routing/Gates
本回合僅建立並驗證 SPEC。使用 governed-engineering-skills 0.20.0；未取得本次產品修改的「開始執行」授權。實作前完成架構與 formatter preflight、驗收映射及執行授權；本文件沒有宣稱任何功能測試已通過。既有全專案布局違規與 History 回收時序波動須如實區分，不藉本 SPEC 放寬或隱藏。

## Discussion Context
### DISC-001: 統一資格判定與匯出職責
- **Situation:** 使用者發現 Export Profile 多了 Validate deployment，而且固定 Export JSON… 文字像正在匯出。
- **Question:** 是否改為統一資格判定規則，Export 直接匯出已合格模型？
- **Options and tradeoffs:** 保留兩階段造成重複操作；統一到 Qualification 可清楚區分驗證與匯出，但舊資格需重驗，事件指標及合格範圍可能改變。
- **User answer:** 「這是我預期想要的」；要求「提出修改方案」，完整方案呈現後要求「建立新的spec」。
- **Explicit rationale:** 使用者認為模型已經過資格判定，Export 應只匯出模型；Exporting… 才代表匯出中。
- **Resulting impact:** DEC-001 至 DEC-003，REQ-001 至 REQ-008，AC-001 至 AC-007；獨立建立新 SPEC，不修改 SPEC-0043 的 worker 範圍。

## Revision History
| Revision | Change | Source |
|---|---|---|
| 1 | 2026-10-12 建立已呈現並要求建檔的完整方案，尚未開始產品實作。 | 本聊天使用者「建立新的spec」。 |

## Acceptance Mapping

```json
{
  "AC-001": {
    "evidence_claims": [
      "host-semantics"
    ],
    "contract_dimensions": [
      "state-transition",
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "Shared event semantics and Qualification parity require deterministic host evidence, not hardware timing claims."
  },
  "AC-002": {
    "evidence_claims": [
      "host-semantics"
    ],
    "contract_dimensions": [
      "state-transition",
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "Threshold, quiet-time and discontinuity boundaries are host algorithm semantics."
  },
  "AC-003": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "input-output-units",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Qt export availability and JSON serialization require host and adapter contract evidence."
  },
  "AC-004": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "input-output-units",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Asynchronous export lifecycle and responsive Qt bindings require host and adapter evidence."
  },
  "AC-005": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "input-output-units",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Atomic filesystem writes and injected failures require adapter contract evidence."
  },
  "AC-006": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "input-output-units",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Project evidence migration and requalification require persistence adapter and host lifecycle evidence."
  },
  "AC-007": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "input-output-units",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Regression and architecture review cover existing host contracts; no physical deployment assurance claimed."
  }
}
```

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

- msg_01a12d91-5c15-7fa0-b035-68e2b9a6586b: 開始執行spec-0043/0044；先處理 confirmed SPEC-0044，SPEC-0043 已實作待結案，沒有新決策
- msg_01a12d91-5c15-7fa0-b035-68e2b9a6586b: 使用者原文「開始執行spec-0043/0044」，授權已呈現的 SPEC-0043 revision 6 與 SPEC-0044 revision 3，沒有新增需求或未決決策。保留原文，工具只將規格 ID 正規化為大寫以匹配同一範圍。

### Source and Revision Audit

```jsonl
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"332b55e969db4a3b854146b8779c96e6","event_hash":"53e305db0025341a78ef3b3a94f5ff0e42f8c80cf1901e297f333865c2fec833","event_type":"start","event_version":1,"open_decisions":[],"previous_event_hash":null,"previous_snapshot_hash":null,"recorded_at":"2026-10-12T00:41:49.142180+00:00","relationships":[{"relation":"refines","source":"REQ-001","target":"SPEC-0040:REQ-003"},{"relation":"supersedes","source":"REQ-004","target":"SPEC-0040:REQ-007"},{"relation":"supersedes","source":"REQ-004","target":"SPEC-0040:REQ-008"},{"relation":"refines","source":"REQ-007","target":"SPEC-0040:REQ-006"},{"relation":"refines","source":"REQ-008","target":"SPEC-0040:REQ-004"},{"relation":"refines","source":"REQ-008","target":"SPEC-0041"}],"revision":1,"snapshot_hash":"9007c0af1fad20b758ff86562c9a6ff5226398cb3780a6cb194229fc235d5253","verdict":"PASS","working_id":"WORKING-SPEC-82e0b3056dc6-unified-qualification-json-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"332b55e969db4a3b854146b8779c96e6","event_hash":"3b5c842e693b4156e4e476db8c6eda12e768fb11ecfdffa9abbd7c6f353104ae","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"53e305db0025341a78ef3b3a94f5ff0e42f8c80cf1901e297f333865c2fec833","previous_snapshot_hash":"9007c0af1fad20b758ff86562c9a6ff5226398cb3780a6cb194229fc235d5253","recorded_at":"2026-10-12T00:42:31.388033+00:00","relationships":[{"relation":"refines","source":"REQ-001","target":"SPEC-0040"},{"relation":"supersedes","source":"REQ-004","target":"SPEC-0040"},{"relation":"supersedes","source":"REQ-004","target":"SPEC-0040"},{"relation":"refines","source":"REQ-007","target":"SPEC-0040"},{"relation":"refines","source":"REQ-008","target":"SPEC-0040"},{"relation":"refines","source":"REQ-008","target":"SPEC-0041"}],"revision":2,"snapshot_hash":"de21344db5b42a95657cc892c1cc6219e82816fb43b75cad24024481b7e43c98","verdict":"PASS","working_id":"WORKING-SPEC-82e0b3056dc6-unified-qualification-json-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"332b55e969db4a3b854146b8779c96e6","event_hash":"22402e0a99a8701fddf7c12fbdd6d18f6abefde863d31224eeffef7198d98ecc","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"3b5c842e693b4156e4e476db8c6eda12e768fb11ecfdffa9abbd7c6f353104ae","previous_snapshot_hash":"de21344db5b42a95657cc892c1cc6219e82816fb43b75cad24024481b7e43c98","recorded_at":"2026-10-12T00:43:03.759569+00:00","relationships":[{"relation":"refines","source":"REQ-001","target":"SPEC-0040"},{"relation":"supersedes","source":"REQ-004","target":"SPEC-0040"},{"relation":"refines","source":"REQ-007","target":"SPEC-0040"},{"relation":"refines","source":"REQ-008","target":"SPEC-0040"},{"relation":"refines","source":"REQ-008","target":"SPEC-0041"}],"revision":3,"snapshot_hash":"0adee59a9ff76dad47cb4db1fb763a6e48624cd2b8cbd567c36bbfe2a169adac","verdict":"PASS","working_id":"WORKING-SPEC-82e0b3056dc6-unified-qualification-json-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"332b55e969db4a3b854146b8779c96e6","event_hash":"73026f94c7598ed2c29bc55269f7fa0b213682b30f01be8540133cd61b3ee630","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"22402e0a99a8701fddf7c12fbdd6d18f6abefde863d31224eeffef7198d98ecc","previous_snapshot_hash":"0adee59a9ff76dad47cb4db1fb763a6e48624cd2b8cbd567c36bbfe2a169adac","recorded_at":"2026-10-12T00:43:16.257907+00:00","relationships":[],"revision":3,"snapshot_hash":"e430367e3dc61783cc348a74c642b2045b2debbf8429ecfdab9e1e9aa01e1577","verdict":"PASS","working_id":"WORKING-SPEC-82e0b3056dc6-unified-qualification-json-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"開始執行spec-0043/0044；先處理 confirmed SPEC-0044，SPEC-0043 已實作待結案，沒有新決策","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"msg_01a12d91-5c15-7fa0-b035-68e2b9a6586b","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a12d91-5bca-7942-aff2-6a1cb00a9f10"},"removed_ids":[]},"epoch":"332b55e969db4a3b854146b8779c96e6","event_hash":"02d76720f96c16ef1a900cfca5f76f85e835c1f7605676b39b6bcffddef7f37d","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"73026f94c7598ed2c29bc55269f7fa0b213682b30f01be8540133cd61b3ee630","previous_snapshot_hash":"e430367e3dc61783cc348a74c642b2045b2debbf8429ecfdab9e1e9aa01e1577","recorded_at":"2026-10-12T00:45:48.468458+00:00","relationships":[],"revision":3,"snapshot_hash":"e430367e3dc61783cc348a74c642b2045b2debbf8429ecfdab9e1e9aa01e1577","verdict":"PASS","working_id":"WORKING-SPEC-82e0b3056dc6-unified-qualification-json-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":3,"snapshot_hash":"e430367e3dc61783cc348a74c642b2045b2debbf8429ecfdab9e1e9aa01e1577","working_id":"WORKING-SPEC-82e0b3056dc6-unified-qualification-json-export"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"34980d6274446407fd89827cbb709606c457f2d9019c937c9c5566d02441906c","reply_stage":"prepared-until-host-stop","reviewed_sources":["msg_01a12d91-5c15-7fa0-b035-68e2b9a6586b"],"source_ref":"msg_01a12d91-5c15-7fa0-b035-68e2b9a6586b","summary":"使用者原文「開始執行spec-0043/0044」，授權已呈現的 SPEC-0043 revision 6 與 SPEC-0044 revision 3，沒有新增需求或未決決策。保留原文，工具只將規格 ID 正規化為大寫以匹配同一範圍。","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a12d91-5bca-7942-aff2-6a1cb00a9f10"},"removed_ids":[]},"epoch":"332b55e969db4a3b854146b8779c96e6","event_hash":"939388bfc74ea311c0c24ec9efa8a8de0139f9af78c01bb8d2e312b4aa3b5839","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"02d76720f96c16ef1a900cfca5f76f85e835c1f7605676b39b6bcffddef7f37d","previous_snapshot_hash":"e430367e3dc61783cc348a74c642b2045b2debbf8429ecfdab9e1e9aa01e1577","recorded_at":"2026-10-12T00:52:31.632400+00:00","relationships":[],"revision":3,"snapshot_hash":"e430367e3dc61783cc348a74c642b2045b2debbf8429ecfdab9e1e9aa01e1577","verdict":"PASS","working_id":"WORKING-SPEC-82e0b3056dc6-unified-qualification-json-export"}
```
<!-- spec-audit:end -->
