---
spec_version: 1
spec_id: SPEC-0050
revision: 3
status: confirmed
change_set: normal-training-range
working_id: WORKING-SPEC-d40a68276b31-normal-training-range
task_ref: 01a18ba0-7b9a-7be2-ac6f-feca72c89b89
---
# Normal Robot Motion 訓練範圍包含 Pick 與 Put

## Problem

使用者指出 Annotate & Classify 的 Normal Robot Motion 列代表訓練資料範圍，因此 Pick、Put 應包含其中。目前 controller.derivedNormalIntervals 直接顯示 WorkspaceService.derive_normal_intervals 的互斥 Normal 活動區間；該推導會扣掉 Pick、Put，造成畫面與實際訓練來源不一致。

唯讀調查：LearningService.build_fit_evidence 與 _build_group_evidence 已選用 Cycle 內 Normal Robot Motion、Robot Pick、Robot Put 的聯集。tests/test_learning_evidence.py 既有三項測試於 2026-10-30 通過，包含 Pick/Put 樣本與連續 segment 驗證。

## Solution

讓畫面上的 Normal Robot Motion 唯讀列呈現正常訓練來源範圍，包含 Pick、Put；保留 Pick、Put 各自的可編輯標註。訓練的活動範圍顯示與實際 evidence 選取應共用或驗證同一規則，避免漏畫、重複樣本與錯誤銜接。精確 FIR history、前處理 warmup 或數值有效性仍由各模型既有規則決定，此列表示活動來源範圍。

不得直接把互斥 Normal 活動真值擴成重疊 Pick/Put 再送入 threshold/qualification；那會變更活動分類、區間最大值與分母。預定修正範圍是範圍投影及說明，並驗證既有訓練資料選取。資料外的區段、Ignore、Collision 與既有碰撞反應窗排除規則需保留；若實作調查發現投影與實際 evidence 在碰撞尾端例外不一致，先具體記錄及釐清，不默默改學習演算法。

實作保持現行活動選取：Normal/Pick/Put 聯集扣除 Ignore/Collision。learning_qualification 提供純活動來源遮罩，供既有 fit evidence 與 UI 投影共用。原互斥 Normal 的碰撞反應窗推導不變；原訓練已納入的明確 Pick/Put 不新增尾端排除。此列不表示各模型 FIR history/warmup 後的有效列。

## User Stories

使用者在正常訓練範圍列看見 Pick、Put 被涵蓋，並仍能分別編輯它們的活動標註。

## Requirements

| ID | Requirement | Source |
|---|---|---|
| REQ-001 | Normal Robot Motion 唯讀列作為正常訓練活動來源範圍，包含已確認 Cycle 內可用的 Pick、Put。 | user:normal-training-range-request |
| REQ-002 | 保留 Pick、Put 各自的標註與編輯行為；畫面範圍合併不得使訓練樣本重複，不得把同一 Cycle 的普通動作與 Pick/Put 交界誤當成 FIR history 中斷。 | user:normal-training-range-request; code:LearningService._build_group_evidence |
| REQ-003 | 不修改既有訓練演算法、活動真值、Qualification 分類、threshold 區間計算及已保存標註格式；範圍呈現保留既有 Cycle/Ignore/Collision 與碰撞反應窗排除契約，驗證其與訓練端的一致性。 | code:WorkspaceService.derive_normal_intervals; code:LearningService._build_group_evidence |

## Decisions

| ID | Decision | Source |
|---|---|---|
| DEC-001 | Pick 與 Put 都屬於正常訓練資料來源，Normal Robot Motion 範圍列應涵蓋它們。 | user:normal-training-range-request |
| DEC-002 | 實作候選：把訓練範圍投影與互斥活動真值分開，保留原活動標註與 threshold/Qualification 語義。此為待確認技術方案。 | assistant:normal-training-range-investigation |

| DEC-003 | 確認已呈現的修正範圍與概念圖並開始執行：正常訓練範圍列包含 Pick/Put，保留活動真值與原訓練規則；同範圍必要的架構與驗收準備一併執行。取代 DEC-002 的候選狀態。 | user:normal-training-range-execute |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | 含 Pick、Put 的已確認 Cycle，其正常訓練範圍列涵蓋兩者；各自的標註列仍可見可編輯。 | Controller 樣本級範圍測試及 Qt/QML 畫面檢查。 | NOT RUN：尚未實作。 |
| AC-002 | REQ-001, REQ-002 | 對同一受控資料比較來源樣本集合與實際 fit evidence；Pick/Put 樣本各納入一次，普通動作與 Pick/Put 相鄰時 segment 連續。 | 既有 tests/test_learning_evidence.py 及必要的投影整合回歸。 | 既有訓練證據測試 3 passed；投影整合尚未執行。 |
| AC-003 | REQ-003 | Ignore、Collision、Cycle 邊界及碰撞反應窗的既有行為保留，互斥 Normal 活動與 threshold/Qualification 分類及標註匯出不變。 | Workspace、annotation controller、threshold 與 annotation export 相關回歸；架構單一 gate。 | NOT RUN：尚未實作。 |

## Acceptance Mapping

```json
{
  "AC-001": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "已確認的活動來源投影與原訓練保持一致；在主機執行生產 LearningService、StudioController 與 Qt/QML 驗證，不宣稱硬體或效能驗證。"
  },
  "AC-002": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "已確認的活動來源投影與原訓練保持一致；在主機執行生產 LearningService、StudioController 與 Qt/QML 驗證，不宣稱硬體或效能驗證。"
  },
  "AC-003": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "已確認的活動來源投影與原訓練保持一致；在主機執行生產 LearningService、StudioController 與 Qt/QML 驗證，不宣稱硬體或效能驗證。"
  }
}
```

## Relationships

| Source | Relation | Target |
|---|---|---|
| DEC-003 | supersedes | DEC-002 |
| REQ-002 | refines | REQ-001 |
| REQ-003 | refines | REQ-001 |

## Out of Scope

模型更換、參數網格、偵測時限、重新訓練既有專案、匯出格式變更及本次以外的頁首配置；不覆蓋目前工作樹已有的 SPEC-0048/0049 修改。

## Open Decisions

None.

## Routing/Gates

ask-matt → grilling / spec-governance。首次 guided router 因同庫多份工作規格無明確 reference 而 BLOCKED；本檔明確綁定目前 chat，避免挪用其他規格。路由亦回報既有 test-validation-layout FAIL 與 verification-ladder planning BLOCKED，未宣稱通過。產品變更前須完成目前規格、架構計畫與 required gates；僅保存討論與執行既有測試不授權產品修改。

## Revision History

| Revision | Date | Change |
|---|---|---|
| 1 | 2026-10-30 | 保存使用者要求、唯讀調查、候選修正範圍與驗收條件；未修改產品。 |

## Discussion Context

### DISC-002

- **Situation:** 已呈現完整修正範圍與修改後概念圖。
- **Question:** 請確認本次修正範圍：正常訓練範圍列涵蓋 Pick、Put，保留各自標註及既有訓練、threshold/Qualification 語義；若同意並要實作，請回覆「開始執行」。
- **Question ID:** Q-001
- **Question version:** 2
- **Options and tradeoffs:** 採已呈現方案，保留原活動真值與訓練選取語義。
- **User answer:** 開始執行
- **Explicit rationale:** 使用者未另述理由。
- **Resulting impact:** 確認 DEC-003、REQ-001 至 REQ-003 與 AC-001 至 AC-003；目前執行指示來源為 user:normal-training-range-execute。


### DISC-001

- Source: user:normal-training-range-request
- User request: Normal Robot Motion 是拿來訓練用的資料範圍，Pick、Put 都應拿來訓練。
- Facts: 現行 fit evidence 已包含 Pick/Put，但正常範圍顯示直接使用扣掉 Pick/Put 的互斥 Normal 區間。
- Proposal: 修正正常訓練活動來源範圍投影，保留原活動真值與學習演算法。
- Authorization:[REDACTED: credential] exact 開始執行。
- **Situation:** 正常訓練範圍顯示與實際 fit evidence 不一致。
- **Question:** Normal Robot Motion 範圍是否包含 Pick 與 Put？此題由使用者主動指定，沒有另外提問。
- **Options and tradeoffs:** 使用者指定包含 Pick/Put。技術候選為獨立訓練範圍投影，保留互斥活動真值，避免改變 threshold 和 Qualification 語義。
- **User answer:** Normal Robot Motion 是拿來訓練用的資料範圍，Pick、Put 都該拿來訓練。
- **Explicit rationale:** 此列表示訓練資料範圍。
- **Resulting impact:** REQ-001、DEC-001 記錄使用者要求；REQ-002、REQ-003 與 AC-001 至 AC-003 界定待確認修正及驗收。

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

- user:normal-training-range-request: Normal Robot Motion training range must include Pick and Put. Diagnose display and fitting consistency.
- assistant:normal-training-range-final: 保存 Pick/Put 屬正常訓練來源的要求；現行訓練已包含，投影待修正，三項既有訓練證據測試通過。SPEC-0050 r2 working，等待目前完整範圍的確認與執行指示。
- assistant:normal-training-range-final: 保存 Pick/Put 應涵蓋於正常訓練來源範圍的要求；目前訓練已包含，投影待修正，三項既有測試通過。SPEC-0050 r2 working，產品未修改，等待本次範圍確認。
- user:normal-training-range-execute: 開始執行
- assistant:normal-training-range-execute-scope: 同步開始執行，SPEC-0050 r3 confirmed；依已呈現概念圖調整正常訓練活動範圍投影，保留現有訓練及活動分類語義。
- assistant:normal-training-range-execute-final: SPEC-0050 r3 confirmed；產品修改完成，275 項不重複測試與開發架構 gate 通過，Qt/QML 實際渲染通過；正式 complete 因工具 ctime 相容性與歷史佈局債務 BLOCKED。證據封存於 artifacts/tests/SPEC-0050-20261030-normal-training-range，未將 SPEC 誤標 implemented。

### Source and Revision Audit

```jsonl
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a33f832129be4d30b664b4167ce6a37e","event_hash":"a5f782088d13238c1dd1e7cda40407d1cd5cbcdf12d4afb5d3dd8d5fa804c500","event_type":"start","event_version":1,"open_decisions":["使用者的行為需求已明確。技術方案與完整修正範圍待呈現確認；未取得本次 exact 開始執行 授權。"],"previous_event_hash":null,"previous_snapshot_hash":null,"recorded_at":"2026-10-30T07:12:47.018518+00:00","relationships":[{"relation":"refines","source":"REQ-002","target":"REQ-001"},{"relation":"refines","source":"REQ-003","target":"REQ-001"}],"revision":1,"snapshot_hash":"f2c8ed2865d4abb5de299d4f91451117c4d72cffc904740f65291676e974ecde","verdict":"BLOCKED","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"Normal Robot Motion training range must include Pick and Put. Diagnose display and fitting consistency.","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:normal-training-range-request","task_ref":"01a18ba0-7b9a-7be2-ac6f-feca72c89b89","turn_id":"normal-training-range-request"},"removed_ids":[]},"epoch":"a33f832129be4d30b664b4167ce6a37e","event_hash":"d9644cc8e5e5bdd70c3ba28729522f6396d6de71bd31a56497360ece46e6b0bd","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"a5f782088d13238c1dd1e7cda40407d1cd5cbcdf12d4afb5d3dd8d5fa804c500","previous_snapshot_hash":"f2c8ed2865d4abb5de299d4f91451117c4d72cffc904740f65291676e974ecde","recorded_at":"2026-10-30T07:13:18.307845+00:00","relationships":[],"revision":1,"snapshot_hash":"f2c8ed2865d4abb5de299d4f91451117c4d72cffc904740f65291676e974ecde","verdict":"PASS","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a33f832129be4d30b664b4167ce6a37e","event_hash":"269c30ba157a2d508108e4e5fb32a20ed66e949168b2ffb4edc1107d9bcc01e3","event_type":"reconcile","event_version":1,"open_decisions":["使用者的行為需求已明確。技術方案與完整修正範圍待呈現確認；未取得本次 exact 開始執行 授權。","Q-001@2"],"previous_event_hash":"d9644cc8e5e5bdd70c3ba28729522f6396d6de71bd31a56497360ece46e6b0bd","previous_snapshot_hash":"f2c8ed2865d4abb5de299d4f91451117c4d72cffc904740f65291676e974ecde","recorded_at":"2026-10-30T07:15:32.650955+00:00","relationships":[{"relation":"refines","source":"REQ-002","target":"REQ-001"},{"relation":"refines","source":"REQ-003","target":"REQ-001"}],"revision":2,"snapshot_hash":"c367eb6ae61fe0550f226f9e0a5394d401e21ed765ee47fb5f375b6062ea95c3","verdict":"BLOCKED","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":2,"snapshot_hash":"c367eb6ae61fe0550f226f9e0a5394d401e21ed765ee47fb5f375b6062ea95c3","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"},"candidates":[{"id":"TRAIN-PROPOSAL-001","impact":"投影涵蓋 Pick/Put，保留互斥活動真值及訓練規則","reason":"顯示與既有訓練來源一致","source_ref":"assistant:normal-training-range-investigation","status":"candidate"}],"completeness_review":null,"identified_items":{"TRAIN-FACT-001":{"id":"TRAIN-FACT-001","kind":"fact","source_ref":"code:LearningService._build_group_evidence","text":"實際訓練 evidence 已包含 Pick 與 Put，既有三項測試通過。"},"TRAIN-PROPOSAL-001":{"id":"TRAIN-PROPOSAL-001","kind":"candidate","source_ref":"assistant:normal-training-range-investigation","text":"修正範圍投影與說明，保留互斥活動真值與既有訓練語義。"},"TRAIN-RANGE-001":{"id":"TRAIN-RANGE-001","kind":"accepted","source_ref":"user:normal-training-range-request","text":"Normal Robot Motion 是正常訓練資料範圍，包含 Pick 與 Put。"}},"item_bindings":{"TRAIN-FACT-001":["REQ-002","AC-002"],"TRAIN-PROPOSAL-001":[],"TRAIN-RANGE-001":["REQ-001","DEC-001"]},"kind":"saved","reply_sha256":"119d73fdc2a330d7673da8152ec510bcd6a5adfd77a9b501faf943a5221ab41c","reply_stage":"prepared-until-host-stop","reviewed_sources":["assistant:normal-training-range-investigation","code:LearningService._build_group_evidence","user:normal-training-range-request"],"source_ref":"assistant:normal-training-range-final","summary":"保存 Pick/Put 屬正常訓練來源的要求；現行訓練已包含，投影待修正，三項既有訓練證據測試通過。SPEC-0050 r2 working，等待目前完整範圍的確認與執行指示。","task_ref":"01a18ba0-7b9a-7be2-ac6f-feca72c89b89","turn_id":"normal-training-range-request"},"removed_ids":[]},"epoch":"a33f832129be4d30b664b4167ce6a37e","event_hash":"b807044e82806cf4f7d514983bed22d172ea00cc244abd7624e80ee4875c81e2","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"269c30ba157a2d508108e4e5fb32a20ed66e949168b2ffb4edc1107d9bcc01e3","previous_snapshot_hash":"c367eb6ae61fe0550f226f9e0a5394d401e21ed765ee47fb5f375b6062ea95c3","recorded_at":"2026-10-30T07:16:41.288632+00:00","relationships":[],"revision":2,"snapshot_hash":"c367eb6ae61fe0550f226f9e0a5394d401e21ed765ee47fb5f375b6062ea95c3","verdict":"PASS","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":2,"snapshot_hash":"c367eb6ae61fe0550f226f9e0a5394d401e21ed765ee47fb5f375b6062ea95c3","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"},"candidates":[{"id":"TRAIN-PROPOSAL-001","impact":"投影涵蓋 Pick/Put，保留活動真值及訓練規則","reason":"顯示與既有訓練來源一致","source_ref":"assistant:normal-training-range-investigation","status":"candidate"}],"completeness_review":null,"identified_items":{"TRAIN-FACT-001":{"id":"TRAIN-FACT-001","kind":"fact","source_ref":"code:LearningService._build_group_evidence","text":"實際訓練 evidence 已包含 Pick 與 Put，既有三項測試通過。"},"TRAIN-PROPOSAL-001":{"id":"TRAIN-PROPOSAL-001","kind":"candidate","source_ref":"assistant:normal-training-range-investigation","text":"修正範圍投影與說明，保留互斥活動真值與既有訓練語義。"},"TRAIN-RANGE-001":{"id":"TRAIN-RANGE-001","kind":"accepted","source_ref":"user:normal-training-range-request","text":"Normal Robot Motion 是正常訓練資料範圍，包含 Pick 與 Put。"}},"item_bindings":{"TRAIN-FACT-001":["REQ-002","AC-002"],"TRAIN-PROPOSAL-001":[],"TRAIN-RANGE-001":["REQ-001","DEC-001"]},"kind":"saved","reply_sha256":"353168f9120b9d24fc95440e13f0611203906408dcc5604ba2ba54a090a50c35","reply_stage":"prepared-until-host-stop","reviewed_sources":["assistant:normal-training-range-investigation","code:LearningService._build_group_evidence","user:normal-training-range-request"],"source_ref":"assistant:normal-training-range-final","summary":"保存 Pick/Put 應涵蓋於正常訓練來源範圍的要求；目前訓練已包含，投影待修正，三項既有測試通過。SPEC-0050 r2 working，產品未修改，等待本次範圍確認。","task_ref":"01a18ba0-7b9a-7be2-ac6f-feca72c89b89","turn_id":"normal-training-range-request"},"removed_ids":[]},"epoch":"a33f832129be4d30b664b4167ce6a37e","event_hash":"9b5b8db83a0b17e2e06c7117d36dfd959085a7fc808a0ef2d72e34db6178c641","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"b807044e82806cf4f7d514983bed22d172ea00cc244abd7624e80ee4875c81e2","previous_snapshot_hash":"c367eb6ae61fe0550f226f9e0a5394d401e21ed765ee47fb5f375b6062ea95c3","recorded_at":"2026-10-30T07:17:48.998847+00:00","relationships":[],"revision":2,"snapshot_hash":"c367eb6ae61fe0550f226f9e0a5394d401e21ed765ee47fb5f375b6062ea95c3","verdict":"PASS","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"開始執行","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:normal-training-range-execute","task_ref":"01a18ba0-7b9a-7be2-ac6f-feca72c89b89","turn_id":"normal-training-range-execute"},"removed_ids":[]},"epoch":"a33f832129be4d30b664b4167ce6a37e","event_hash":"f7b427d432f95e1365ccd854ca39b113b46a92ffbfc0dd2875e1664232725850","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"9b5b8db83a0b17e2e06c7117d36dfd959085a7fc808a0ef2d72e34db6178c641","previous_snapshot_hash":"c367eb6ae61fe0550f226f9e0a5394d401e21ed765ee47fb5f375b6062ea95c3","recorded_at":"2026-10-30T07:31:36.274284+00:00","relationships":[],"revision":2,"snapshot_hash":"c367eb6ae61fe0550f226f9e0a5394d401e21ed765ee47fb5f375b6062ea95c3","verdict":"PASS","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"}
{"affected_ids":["DEC-003","DISC-002"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["DEC-003","DISC-002"],"changed_ids":[],"removed_ids":[]},"epoch":"a33f832129be4d30b664b4167ce6a37e","event_hash":"0a32afd9799b664ca68297f1e52d92ce1e22194ebfef00712e6b5c5cc36ded6d","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"f7b427d432f95e1365ccd854ca39b113b46a92ffbfc0dd2875e1664232725850","previous_snapshot_hash":"c367eb6ae61fe0550f226f9e0a5394d401e21ed765ee47fb5f375b6062ea95c3","recorded_at":"2026-10-30T07:36:43.690542+00:00","relationships":[{"relation":"supersedes","source":"DEC-003","target":"DEC-002"},{"relation":"refines","source":"REQ-002","target":"REQ-001"},{"relation":"refines","source":"REQ-003","target":"REQ-001"}],"revision":3,"snapshot_hash":"9a61ca9888ccc10bec7f9fa2d351791e62832e52ee8ba810e93e5e5604eaee6f","verdict":"PASS","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a33f832129be4d30b664b4167ce6a37e","event_hash":"2bce19058c18604a2373f0f4c576776993bf32ffeda3a1705f9a862ee5d89ac4","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"0a32afd9799b664ca68297f1e52d92ce1e22194ebfef00712e6b5c5cc36ded6d","previous_snapshot_hash":"9a61ca9888ccc10bec7f9fa2d351791e62832e52ee8ba810e93e5e5604eaee6f","recorded_at":"2026-10-30T07:37:10.246762+00:00","relationships":[],"revision":3,"snapshot_hash":"7562e45bd66243f7e72361fae61811677b3c31a507a9878e0431f9a752905dac","verdict":"PASS","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":3,"snapshot_hash":"7562e45bd66243f7e72361fae61811677b3c31a507a9878e0431f9a752905dac","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"},"candidates":[],"completeness_review":null,"identified_items":{"EXEC-001":{"id":"EXEC-001","kind":"accepted","source_ref":"user:normal-training-range-execute","text":"使用者在已呈現的修正範圍與概念圖之後指示開始執行。"}},"item_bindings":{"EXEC-001":["DEC-003"]},"kind":"saved","reply_sha256":"847006fdcd2920b51970c1a06e9e8fa1dbaeb159889f6432933f7ef295ba526f","reply_stage":"prepared-until-host-stop","reviewed_sources":["user:normal-training-range-execute"],"source_ref":"assistant:normal-training-range-execute-scope","summary":"同步開始執行，SPEC-0050 r3 confirmed；依已呈現概念圖調整正常訓練活動範圍投影，保留現有訓練及活動分類語義。","task_ref":"01a18ba0-7b9a-7be2-ac6f-feca72c89b89","turn_id":"normal-training-range-execute"},"removed_ids":[]},"epoch":"a33f832129be4d30b664b4167ce6a37e","event_hash":"3b01b9024f5bd53f49cfd6c05d016cb42286aef5779a9426d8af0ac63d9c7bf3","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"2bce19058c18604a2373f0f4c576776993bf32ffeda3a1705f9a862ee5d89ac4","previous_snapshot_hash":"7562e45bd66243f7e72361fae61811677b3c31a507a9878e0431f9a752905dac","recorded_at":"2026-10-30T07:38:00.826493+00:00","relationships":[],"revision":3,"snapshot_hash":"7562e45bd66243f7e72361fae61811677b3c31a507a9878e0431f9a752905dac","verdict":"PASS","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":3,"snapshot_hash":"7562e45bd66243f7e72361fae61811677b3c31a507a9878e0431f9a752905dac","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"},"candidates":[],"completeness_review":null,"identified_items":{"EXEC-001":{"id":"EXEC-001","kind":"accepted","source_ref":"user:normal-training-range-execute","text":"使用者在已呈現的修正範圍與概念圖之後指示開始執行。"},"FORMAL-BLOCKER-001":{"id":"FORMAL-BLOCKER-001","kind":"fact","source_ref":"artifacts/tests/SPEC-0050-20261030-normal-training-range/capture/complete-before.json","text":"正式 complete 受 Windows lstat/fstat ctime 差異與歷史證據佈局問題阻擋；未降低規則或宣稱正式驗收通過。"},"HOST-VALIDATION-001":{"id":"HOST-VALIDATION-001","kind":"fact","source_ref":"artifacts/tests/SPEC-0050-20261030-normal-training-range/manifest.json","text":"已完成正常訓練活動範圍投影實作；275 項不重複測試及開發架構 gate 通過，實際 Qt/QML 已以合成資料渲染。"}},"item_bindings":{"EXEC-001":["DEC-003"],"FORMAL-BLOCKER-001":["AC-003"],"HOST-VALIDATION-001":["AC-001","AC-002","AC-003"]},"kind":"saved","reply_sha256":"0fad2e654f55a7dc1da8c17cc3e93aec66e52579e396dd48ffd04a92d98e6a52","reply_stage":"prepared-until-host-stop","reviewed_sources":["artifacts/tests/SPEC-0050-20261030-normal-training-range/capture/complete-before.json","artifacts/tests/SPEC-0050-20261030-normal-training-range/manifest.json","user:normal-training-range-execute"],"source_ref":"assistant:normal-training-range-execute-final","summary":"SPEC-0050 r3 confirmed；產品修改完成，275 項不重複測試與開發架構 gate 通過，Qt/QML 實際渲染通過；正式 complete 因工具 ctime 相容性與歷史佈局債務 BLOCKED。證據封存於 artifacts/tests/SPEC-0050-20261030-normal-training-range，未將 SPEC 誤標 implemented。","task_ref":"01a18ba0-7b9a-7be2-ac6f-feca72c89b89","turn_id":"normal-training-range-execute"},"removed_ids":[]},"epoch":"a33f832129be4d30b664b4167ce6a37e","event_hash":"dfa9a4177faf43285cc469fac7cac200ff0927cec1d0e9524f6a30b7f0477b0d","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"3b01b9024f5bd53f49cfd6c05d016cb42286aef5779a9426d8af0ac63d9c7bf3","previous_snapshot_hash":"7562e45bd66243f7e72361fae61811677b3c31a507a9878e0431f9a752905dac","recorded_at":"2026-10-30T08:06:39.963393+00:00","relationships":[],"revision":3,"snapshot_hash":"7562e45bd66243f7e72361fae61811677b3c31a507a9878e0431f9a752905dac","verdict":"PASS","working_id":"WORKING-SPEC-d40a68276b31-normal-training-range"}
```
<!-- spec-audit:end -->
