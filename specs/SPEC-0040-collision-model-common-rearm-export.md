---
spec_version: 1
spec_id: SPEC-0040
revision: 3
status: confirmed
change_set: collision-model-common-rearm-export
working_id: WORKING-SPEC-b945763a6677-collision-model-common-rearm-export
task_ref: 01a10ee8-1f28-7091-b835-71e36dc2b5c7
branch_ref: main
---

# 碰撞模型 JSON 與共同事件解除政策分工

## Problem

現有桌面 JSON 把 release_ratio 與 release_quiet_time_s 視為模型參數。新版 env_sensing 由共同碰撞模組管理鎖定與解除，固定採用 0.8／50 ms，載入時忽略這兩欄。桌面歷史資格使用的事件政策可能不同，不能直接代表新版部署事件驗證。

## Solution

只支援新版共同政策韌體：JSON 省略兩個解除欄位，不提供舊格式入口。保留碰撞判斷所需的模型參數與精度，依新輸出內容計算識別。部署回放採用固定 0.8／50 ms；凍結模型重新驗證事件結果，無需重訓。保留歷史專案和回放用途。本變更是獨立 SPEC，不修訂 SPEC-0039。

## User Stories

- 使用者匯出的 JSON 描述碰撞判斷方法，共同解除政策由新版部署端管理。
- 使用者可以看出模型是否已在新版政策下完成桌面部署驗證，並查看失敗原因。

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | 本次採用獨立 SPEC，不整合或修訂 SPEC-0039。 |
| REQ-002 | 模型負責判斷值、門檻與結果；鎖定、解除與事件成立由共同事件管理負責，不重複鎖定。保留模型权重、前處理、殘差、計分方式、輸入單位與順序、numeric_type 及 strict score > threshold。 |
| REQ-003 | 桌面新版部署回放採用固定解除比例 0.8 與連續低於解除門檻 50 ms。持續超限不重複觸發；等於或高於解除門檻、無效資料或資料中斷清除解除計時，原先已鎖定時保持鎖定。設定／來源／模型切換沿已確認的共同事件規則重新累計有效資料。 |
| REQ-004 | 新 JSON 不輸出 detector.release_ratio 或 detector.release_quiet_time_s，且匯出不依賴兩欄的值；schema_version 維持 1，僅支援接受缺少兩欄的新版韌體。不提供舊格式匯出入口或過渡欄位。其餘資格、有限數值、維度、精度、門檻及安全存檔檢查保持。 |
| REQ-005 | ProfileCommandPort／ProfileExportService 的 JSON 介面與 controller 不再傳入兩個解除參數；execution_sha256 依實際新內容重新計算，與名稱／檔名無關。其他匯出及歷史回放契約不以全域刪欄或改預設方式破壞。 |
| REQ-006 | 新版部署驗證使用目前凍結模型與其來源資料，不重新訓練、不改寫數值或歷史驗證。新版事件結果與原紀錄分開識別，追溯模型、資料、有效門檻、共同政策及驗證版本；修改任一輸入後既有證據不得作為目前新版 PASS。 |
| REQ-007 | 新 JSON 匯出需有對應新版政策的有效桌面部署資格。未驗證、來源缺失、失敗或已失效時顯示原因與重新驗證入口；不默認合格。使用既有 Qualification 判定標準對凍結模型重新評估事件，不因改政策放寬通過標準。部署驗證可取消，未完成時不留下通過結果。 |
| REQ-008 | Export Profile 顯示目標為新版共同事件政策，說明 0.8／50 ms 由韌體管理並呈現部署驗證狀態；不提供解除參數編輯。仍列出合格 Kernel 與逐列 JSON 匯出，安全覆寫與取消流程保持。 |

## Decisions

| ID | Decision | Source |
|---|---|---|
| DEC-001 | 建立獨立變更，不整合 SPEC-0039。 | 本聊天使用者：不要整合進SPEC-0039。 |
| DEC-002 | 模型僅負責判斷方法；共同解除固定 0.8／50 ms。 | docs/firmware-common-rearm-policy.md；chat 01a0f17f-570b-7fd3-807c-f55d38f3f47d，turn 01a0f1d7-70db-7972-950a-65ac69ec0d58 與 01a0f1d8-bd7a-7653-8c79-01f0c3581723。 |
| DEC-003 | 新韌體忽略舊 JSON 的兩個解除欄位，不要求其存在或參數型別／範圍有效；其餘驗證維持。 | 同來源 chat turn 01a0f1db-c07c-7ae0-99ae-42884c59a9ed；現有 json_parameter_reader.cpp。 |
| DEC-004 | 選擇 Q-001 version 2 選項 1：只支援新版，移除兩欄，部署回放採 0.8／50 ms，不提供舊格式入口。 | user-common-rearm-option1：使用者原文 1。 |
| DEC-005 | 桌面重新驗證不重訓模型，保留歷史用途，不主張實機已驗收。 | REQ-002/003 的必要驗證設計，來源 docs/firmware-common-rearm-policy.md 與前一回合候選方案；本項是設計衍生，非額外使用者回答。 |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | 本次規格與修改獨立，SPEC-0039 不包含本次修訂。 | Git diff、正式 SPEC 對照與 Spec review。 | Pending implementation. |
| AC-002 | REQ-002, REQ-004 | JSON 省略兩欄，保留完整判斷參數、signed zero、Float32／Float64、Unicode 名稱、陣列順序，無數值窄化或新容量 gate；非法模型仍拒絕。 | JSON roundtrip、固定模型參考預測與嚴格門檻比較；缺欄與既有非法輸入 fixtures。 | Pending implementation. |
| AC-003 | REQ-003 | 共同部署事件邏輯涵蓋持續超限不重複、低於解除門檻 49/50 ms、等於門檻重置計時、有效資料恢復後重新計時及再次觸發，模型內不再另做鎖定。 | 固定 score/time 向量與同型精度邊界 assertions；對照現有韌體共同規則，僅聲明 host 語意一致。 | Pending implementation. |
| AC-004 | REQ-005 | JSON 命令／controller 無兩個解除參數依賴，新 hash 可由實際內容重算；名稱／檔名不改執行識別，舊 Header／Model TXT 能力與歷史回放保持。 | Port/controller 回歸、hash 差分、既有匯出與歷史結果回歸。 | Pending implementation. |
| AC-005 | REQ-006, REQ-007 | 凍結模型新版資格可追溯且不重訓；採既有通過標準。舊結果不改標；來源缺失、失敗、取消或输入失效均不可匯出成目前有效新版資格。 | Qualification fixtures 與 revalidation/invalidation/cancellation 測試；spy 保證無 fitting，檢查模型 bytes 與歷史結果不变。 | Pending implementation. |
| AC-006 | REQ-008, REQ-004, REQ-007 | 實際 QML 顯示新版政策與每列部署狀態／原因，沒有舊格式或解除編輯入口；可重新驗證及逐列匯出正確 kernel。取消、覆寫確認與原子失敗保護正常。 | 真實 QML 互動、controller/file tests、視覺檢查；spec/standards review 與 architecture gate。 | Pending implementation. |

## Acceptance Mapping

```json
{
  "AC-001": {"evidence_claims": ["host-semantics"], "contract_dimensions": [], "execution_changes": [], "rationale": "Repository-local specification isolation and reviewed diff; no device claim.", "scenario_layers": {}},
  "AC-002": {"evidence_claims": ["host-semantics"], "contract_dimensions": ["input-output-units"], "execution_changes": [], "rationale": "Deterministic desktop model serialization, numeric roundtrip and validation; firmware acceptance is outside this change.", "scenario_layers": {}},
  "AC-003": {"evidence_claims": ["host-semantics"], "contract_dimensions": ["state-transition", "error-reset"], "execution_changes": [], "rationale": "Desktop event-state vectors with exact sample timestamps; establishes host behavior, not physical timing.", "scenario_layers": {}},
  "AC-004": {"evidence_claims": ["host-semantics", "adapter-conformance"], "contract_dimensions": ["call-order", "external-port"], "execution_changes": [], "rationale": "Desktop encoder/controller boundary and exact projection hash; retain existing export capabilities.", "scenario_layers": {}},
  "AC-005": {"evidence_claims": ["host-semantics"], "contract_dimensions": ["state-transition", "error-reset"], "execution_changes": [], "rationale": "Frozen model replay, qualification provenance and invalidation verified on host with source fixtures; no retraining or target runtime claim.", "scenario_layers": {}},
  "AC-006": {"evidence_claims": ["host-semantics", "adapter-conformance"], "contract_dimensions": ["external-port"], "execution_changes": [], "rationale": "Real local Qt/QML and filesystem interaction with injected failures; desktop runtime evidence only.", "scenario_layers": {}}
}
```

## Modification Plan

先完成 manifest 設計與所有權表；將模型數值評估與共同事件狀態分離於 learning_qualification 內。新部署政策及資格證據由該域管理，studio_application 協調重新驗證與匯出，不由 serializer 執行。移除 JSON 介面兩參數及輸出欄位；保持 schema 1。增加政策識別與目前凍結輸入的驗證關聯，QML 顯示每列狀態與操作。舊歷史資料依原契約還原；未有新版證據時，提示重新驗證。最后一起更新 manifest、生成頁、測試與驗證定義。

## Architecture Impact

| Boundary | Owner | Authority |
|---|---|---|
| Model JSON and content identity | profile_export | Validate and serialize model-only parameters; no fitting/requalification or Qt/filesystem. |
| Deployment event policy and qualification | learning_qualification | Frozen score/time processing, event-state ownership, new evidence provenance and existing qualification rules. |
| Current result and export admission | studio_application | Coordinate validation, invalidation and session/result lookup. |
| UI and atomic files | desktop_adapter | Name/file dialogs, deployment state projection and approved UTF-8 atomic write. |

Type/state ownership: SemanticProfile remains profile_export-owned; FrozenFirModel, existing DetectorConfig and new deployment policy/evidence remain learning_qualification-owned. Model evaluation is stateless relative to event latch; a deployment replay owns its private latch/timer. StudioController session owns current evidence handles and invalidation. QML owns interaction state only. Project persistence maps any new evidence through existing project_session boundary; historical detector settings remain historical, not silently migrated to new success.

Dependency/parent mappings: preserve studio_application -> profile_export/learning_qualification/desktop_adapter/project_session; no profile_export -> learning_qualification sibling edge. No new module or worker. Exact new public symbols and serialized evidence schema are implementation design items subject to pre-code validation, not unresolved product decisions.

Description Views: manifest changes cover JSON port, model-only codec, deployment event/qualification flow and provenance descriptions; render affected profile_export, learning_qualification, studio_application, project_session and System pages only via architecture_cli. No ADR exception proposed.

Algorithm impact: event-state machine is algorithm-bearing and owned by learning_qualification; fixed thresholds/time policy has no calibration decision. Preserve model score algorithm and existing qualification success definition. No thread/task, priority, output rate, performance improvement or physical deadline change is claimed.

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-002 | depends_on | DEC-002 |
| REQ-004 | depends_on | DEC-004 |
| REQ-007 | depends_on | REQ-006 |

Historical context: SPEC-0039 describes the previously delivered JSON/UI contract; this independent spec changes subsequent behavior without editing that document.

## Out of Scope

Firmware modifications or device acceptance, PUB_EVENT PC receiver, retraining or changing learning method/weights, rewriting historical results, legacy firmware export, changes to Header/Model TXT behavior, commit/push. Numeric precision remains as selected by desktop, including Float64; this spec does not claim every firmware accepts both precisions.

## Open Decisions

None.

## Routing/Gates

Before product edits: present complete confirmed proposal and obtain fresh 開始執行 for this scope; validate boundary/type/state/dependency/parent maps and planned manifest; apply formatter governance and event algorithm review. Keep tests under tests/, authored definitions under validation/ and unique evidence under artifacts/. Fill missing project validation/layout.yaml and update applicable acceptance projection/matrix through managed delivery. Run architecture_cli development/release with zero-entry baseline and required runtime/QML checks. Host evidence is not firmware acceptance. No test or implementation PASS is claimed by spec confirmation.

## Discussion Context

### DISC-001: 獨立修改提案
- **Situation:** SPEC-0039 已提交；使用者要求另一項共同解除政策修改使用獨立規格。
- **Question:** 尚需確認舊韌體相容匯出需求。
- **Options and tradeoffs:** 新版單一格式較簡單；雙格式增加相容維護及驗證。
- **User answer:** 提出修改方案。
- **Explicit rationale:** 未提供。
- **Resulting impact:** 保存 REQ-001/002/003 與 DEC-001/002/003 來源，提出獨立方案。

### DISC-002: 新版單一匯出契約
- **Situation:** 共同事件政策已確認；新載入器支援缺少解除欄位，尚需決定是否保留舊格式。
- **Question:** 這次 JSON 匯出是否還需要支援要求兩個解除欄位的舊韌體？
- **Options and tradeoffs:** 只支援新版韌體（建議）：移除兩欄，部署回放以 0.8／50 ms 驗證，不提供舊格式入口。 / 保留兩種匯出格式：新版移除兩欄，舊版保留；各自標示目標韌體與對應驗證結果。 / 採用過渡格式：兩欄固定輸出 0.8／0.05 秒，供舊載入器讀取；新版韌體仍忽略，僅維持格式相容，不宣稱舊韌體事件行為一致。
- **User answer:** 1
- **Explicit rationale:** 未提供额外理由。
- **Resulting impact:** DEC-004 確認新版單一格式與固定政策回放，解決 OD-001；REQ-004/005/006/007/008 與 AC-002/003/004/005/006 將已提出方案具體化。OD-002 的相容性前提已解決，驗收映射由專案事實補齊，未推定新的執行授權。
- **Source:** user-common-rearm-option1，這個聊天的使用者原文 1，對應 Q-001 version 2。

## Revision History

- Revision 1: 建立獨立候選方案。
- Revision 2: 保存 Q-001 的三個相容性選項。
- Revision 3: 記錄選項 1；定義新版 JSON、部署驗證、歷史兼容與驗收方法。

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

- user-propose-independent-rearm: 提出修改方案
- user-common-rearm-option1: 1
- user-common-rearm-option1: 已核對 Q-001 version 2 的回答 1，DEC-004 和 DISC-002 已保存。SPEC-0040 revision 3 已 confirmed，格式與需求追溯 PASS，無未決項目；只支援新版韌體，JSON 移除兩欄、固定 0.8／50 ms 部署驗證、無舊格式入口。SPEC-0039 未修改，產品未執行，驗收投影與實作檢查待開始執行後完成。
- 01a10f17-9627-7573-a4d0-7e55b1b20549: 開始執行
- 01a10f17-9627-7573-a4d0-7e55b1b20549: 使用者原文開始執行，明確授權剛呈現的 confirmed SPEC-0040 revision 3，沒有新增需求或未決項目。繼續該規格的 JSON 模型-only 匯出、固定 0.8／50 ms 部署驗證、狀態／資格與測試及架構治理同步，不含 commit/push。
- 01a10f50-a1e6-73f3-9143-0dbc6dfc395a: 進行驗證：續驗 SPEC-0040 現有功能、目錄治理及 QML 畫面；沒有新增需求或決策。
- 01a10f50-a1e6-73f3-9143-0dbc6dfc395a: 使用者要求接續驗證 SPEC-0040 既有實作，特別是目錄治理與原生視覺驗收；無新增需求或決策，維持 revision 3 與先前開始執行的範圍，不含 SPEC-0039 修改及 commit/push。
- 01a10f50-a1e6-73f3-9143-0dbc6dfc395a: 既有 SPEC-0040 的驗證結果：58項相關測試、兩個架構gate及Windows軟體繪圖下的原生畫面通過。預設繪圖與完整回歸逾時；目錄gate FAIL，正式驗收 BLOCKED。驗證中治理工具由0.20升為0.21，原docs更新因既有SPEC章節相容性被拒絕，結果另存artifacts/validation/spec40-verification-20261006T040352/report.md。SPEC revision 3、範圍與原授權不变；未修改產品來源與測試、未commit/push。

### Source and Revision Audit

```jsonl
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"02b9c857c18c6297ed9c80eff4aa2681be786bdf25b10c2269e37fca9a350632","event_type":"start","event_version":1,"open_decisions":["OD-001: 新版 JSON 是否只支援新版共同政策韌體並省略兩欄，或還需提供舊韌體相容匯出入口？這決定匯出模式與資格證據的範圍。","OD-002: 以上候選桌面部署驗證範圍與 UI／持久化方案尚待採用，需先確認相容性範圍後完成具體驗收投影。"],"previous_event_hash":null,"previous_snapshot_hash":null,"recorded_at":"2026-10-06T02:24:44.371699+00:00","relationships":[{"relation":"refines","source":"REQ-002","target":"SPEC-0039:REQ-044"},{"relation":"depends_on","source":"REQ-003","target":"DEC-002"}],"revision":1,"snapshot_hash":"e7ff14eca3c6f5cd56476755d8b2acffff448f2124d94bf37822d8dbe32129e8","verdict":"BLOCKED","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"提出修改方案","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user-propose-independent-rearm","task_ref":"01a10ee8-1f28-7091-b835-71e36dc2b5c7","turn_id":"user-propose-independent-rearm"},"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"597e39478c136d2e56eb56f4a76136e6cc038c5d8b00f6898f0aafbe5312e76d","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"02b9c857c18c6297ed9c80eff4aa2681be786bdf25b10c2269e37fca9a350632","previous_snapshot_hash":"e7ff14eca3c6f5cd56476755d8b2acffff448f2124d94bf37822d8dbe32129e8","recorded_at":"2026-10-06T02:24:59.345337+00:00","relationships":[],"revision":1,"snapshot_hash":"e7ff14eca3c6f5cd56476755d8b2acffff448f2124d94bf37822d8dbe32129e8","verdict":"PASS","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"0996b490903efb8c03188bf09953ffd361e36a97084f980d645cd3e106c02dd0","event_type":"reconcile","event_version":1,"open_decisions":["OD-001: 新版 JSON 是否只支援新版共同政策韌體並省略兩欄，或還需提供舊韌體相容匯出入口？這決定匯出模式與資格證據的範圍。","OD-002: 以上候選桌面部署驗證範圍與 UI／持久化方案尚待採用，需先確認相容性範圍後完成具體驗收投影。","Q-001@2"],"previous_event_hash":"597e39478c136d2e56eb56f4a76136e6cc038c5d8b00f6898f0aafbe5312e76d","previous_snapshot_hash":"e7ff14eca3c6f5cd56476755d8b2acffff448f2124d94bf37822d8dbe32129e8","recorded_at":"2026-10-06T02:26:09.849606+00:00","relationships":[{"relation":"refines","source":"REQ-002","target":"SPEC-0039:REQ-044"},{"relation":"depends_on","source":"REQ-003","target":"DEC-002"}],"revision":2,"snapshot_hash":"1ff1971946fe3cb95503398342e60c0b8a4cb86203d9b6c3a8d814759c9e4f09","verdict":"BLOCKED","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
{"affected_ids":["AC-001","AC-002","AC-003","AC-004","AC-005","AC-006","DEC-004","DEC-005","DISC-001","DISC-002","REQ-001","REQ-002","REQ-003","REQ-004","REQ-005","REQ-006","REQ-007","REQ-008"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":["AC-001","AC-002","AC-003"],"added_ids":["AC-004","AC-005","AC-006","DEC-004","DEC-005","DISC-002","REQ-004","REQ-005","REQ-006","REQ-007","REQ-008"],"changed_ids":["AC-001","AC-002","AC-003","DISC-001","REQ-001","REQ-002","REQ-003"],"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"2fa11998557e8840c6f5564fbfecb26a41ec65ac4333961d960f38b8ed2b2f11","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"0996b490903efb8c03188bf09953ffd361e36a97084f980d645cd3e106c02dd0","previous_snapshot_hash":"1ff1971946fe3cb95503398342e60c0b8a4cb86203d9b6c3a8d814759c9e4f09","recorded_at":"2026-10-06T02:36:08.243380+00:00","relationships":[{"relation":"depends_on","source":"REQ-002","target":"DEC-002"},{"relation":"depends_on","source":"REQ-004","target":"DEC-004"},{"relation":"depends_on","source":"REQ-007","target":"REQ-006"}],"revision":3,"snapshot_hash":"1ef93c94eb3c1937e314a889ac7d0c235b66670ea59d71009e25c2940e6433a4","verdict":"PASS","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"63340c2142c6eff13e70ef6baa72f9350fd6ed719350e94ff90cce059ae5b702","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"2fa11998557e8840c6f5564fbfecb26a41ec65ac4333961d960f38b8ed2b2f11","previous_snapshot_hash":"1ef93c94eb3c1937e314a889ac7d0c235b66670ea59d71009e25c2940e6433a4","recorded_at":"2026-10-06T02:36:17.456428+00:00","relationships":[],"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","verdict":"PASS","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"1","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user-common-rearm-option1","task_ref":"01a10ee8-1f28-7091-b835-71e36dc2b5c7","turn_id":"user-common-rearm-option1"},"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"fd4bd778e53024b1f5dbc6bd4e7570d3427b0594f894c13f13000fe6d697c1c6","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"63340c2142c6eff13e70ef6baa72f9350fd6ed719350e94ff90cce059ae5b702","previous_snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","recorded_at":"2026-10-06T02:36:53.646813+00:00","relationships":[],"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","verdict":"PASS","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"},"candidates":[],"completeness_review":null,"identified_items":{"common-rearm-option1":{"id":"common-rearm-option1","kind":"accepted","source_ref":"user-common-rearm-option1","text":"使用者回答 1，選擇 Q-001 version 2 新版單一匯出契約：移除解除兩欄、部署回放 0.8／50 ms、不提供舊格式入口。"}},"item_bindings":{"common-rearm-option1":["DEC-004","REQ-004","REQ-003","AC-002","AC-003"]},"kind":"saved","reply_sha256":"0e139d75250f60ad2ca22d36cd1a7d8fc0006947babe4f9f1a7d46fe6001a898","reply_stage":"prepared-until-host-stop","reviewed_sources":["user-common-rearm-option1","user-propose-independent-rearm"],"source_ref":"user-common-rearm-option1","summary":"已核對 Q-001 version 2 的回答 1，DEC-004 和 DISC-002 已保存。SPEC-0040 revision 3 已 confirmed，格式與需求追溯 PASS，無未決項目；只支援新版韌體，JSON 移除兩欄、固定 0.8／50 ms 部署驗證、無舊格式入口。SPEC-0039 未修改，產品未執行，驗收投影與實作檢查待開始執行後完成。","task_ref":"01a10ee8-1f28-7091-b835-71e36dc2b5c7","turn_id":"user-common-rearm-option1"},"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"eb0a9c0b3854d593220ae39ea8e9a71baae0564dec1af2ed8ee68a13e1868746","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"fd4bd778e53024b1f5dbc6bd4e7570d3427b0594f894c13f13000fe6d697c1c6","previous_snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","recorded_at":"2026-10-06T02:37:34.799997+00:00","relationships":[],"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","verdict":"PASS","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"開始執行","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"01a10f17-9627-7573-a4d0-7e55b1b20549","task_ref":"01a10ee8-1f28-7091-b835-71e36dc2b5c7","turn_id":"01a10f17-9582-74c1-8b3b-fa0bf2552b2c"},"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"64a795139977a32c8b078698ad1d0e7bed624ffeeb7539de25293fd0e181b109","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"eb0a9c0b3854d593220ae39ea8e9a71baae0564dec1af2ed8ee68a13e1868746","previous_snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","recorded_at":"2026-10-06T02:43:54.056133+00:00","relationships":[],"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","verdict":"PASS","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"e2c1f32bd2bafecee491471a8fb4546785130dc1b7ac8c781d14d307683bd489","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a10f17-9627-7573-a4d0-7e55b1b20549"],"source_ref":"01a10f17-9627-7573-a4d0-7e55b1b20549","summary":"使用者原文開始執行，明確授權剛呈現的 confirmed SPEC-0040 revision 3，沒有新增需求或未決項目。繼續該規格的 JSON 模型-only 匯出、固定 0.8／50 ms 部署驗證、狀態／資格與測試及架構治理同步，不含 commit/push。","task_ref":"01a10ee8-1f28-7091-b835-71e36dc2b5c7","turn_id":"01a10f17-9582-74c1-8b3b-fa0bf2552b2c"},"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"94ced01c809573c4b859e97678a9bbfe6036da9c52fe29b8ffac59a57642dba2","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"64a795139977a32c8b078698ad1d0e7bed624ffeeb7539de25293fd0e181b109","previous_snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","recorded_at":"2026-10-06T02:44:46.376604+00:00","relationships":[],"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","verdict":"PASS","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"進行驗證：續驗 SPEC-0040 現有功能、目錄治理及 QML 畫面；沒有新增需求或決策。","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"01a10f50-a1e6-73f3-9143-0dbc6dfc395a","task_ref":"01a10ee8-1f28-7091-b835-71e36dc2b5c7","turn_id":"01a10f50-9d6f-7001-8a13-fe2ae9f7261c"},"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"60e9fd4633e645da4daba66416fc3ba5438e4bcebfaad61a5d8ffbfbc365ae41","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"94ced01c809573c4b859e97678a9bbfe6036da9c52fe29b8ffac59a57642dba2","previous_snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","recorded_at":"2026-10-06T03:48:01.448919+00:00","relationships":[],"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","verdict":"PASS","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"846bb94b76a52ef40349876c7d6b22fb6355d3a5fffac03c47d881f307029ef2","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a10f50-a1e6-73f3-9143-0dbc6dfc395a"],"source_ref":"01a10f50-a1e6-73f3-9143-0dbc6dfc395a","summary":"使用者要求接續驗證 SPEC-0040 既有實作，特別是目錄治理與原生視覺驗收；無新增需求或決策，維持 revision 3 與先前開始執行的範圍，不含 SPEC-0039 修改及 commit/push。","task_ref":"01a10ee8-1f28-7091-b835-71e36dc2b5c7","turn_id":"01a10f50-9d6f-7001-8a13-fe2ae9f7261c"},"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"295bce8b09ac9dc87318029c96244dc317c62f534c2edf4c2ec7b9fca9b24636","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"60e9fd4633e645da4daba66416fc3ba5438e4bcebfaad61a5d8ffbfbc365ae41","previous_snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","recorded_at":"2026-10-06T03:49:41.911196+00:00","relationships":[],"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","verdict":"PASS","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"d1e6d5c2cedb569839c74b746bc124ab2e5782654bda24503fe965d16f4cfb98","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a10f50-a1e6-73f3-9143-0dbc6dfc395a"],"source_ref":"01a10f50-a1e6-73f3-9143-0dbc6dfc395a","summary":"既有 SPEC-0040 的驗證結果：58項相關測試、兩個架構gate及Windows軟體繪圖下的原生畫面通過。預設繪圖與完整回歸逾時；目錄gate FAIL，正式驗收 BLOCKED。驗證中治理工具由0.20升為0.21，原docs更新因既有SPEC章節相容性被拒絕，結果另存artifacts/validation/spec40-verification-20261006T040352/report.md。SPEC revision 3、範圍與原授權不变；未修改產品來源與測試、未commit/push。","task_ref":"01a10ee8-1f28-7091-b835-71e36dc2b5c7","turn_id":"01a10f50-9d6f-7001-8a13-fe2ae9f7261c"},"removed_ids":[]},"epoch":"4b0ff1a1bf3240fc8b9a6d5fe817a8aa","event_hash":"ba0ac67607a65fc24dc9e74e1167cbbaaa9e57b218864b8d234144a4da4057c6","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"295bce8b09ac9dc87318029c96244dc317c62f534c2edf4c2ec7b9fca9b24636","previous_snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","recorded_at":"2026-10-06T04:05:26.353518+00:00","relationships":[],"revision":3,"snapshot_hash":"e8bcde5cf128ba6113b99f280661ee85b511a3c6a46716109081af97cc649855","verdict":"PASS","working_id":"WORKING-SPEC-b945763a6677-collision-model-common-rearm-export"}
```
<!-- spec-audit:end -->
