---
spec_version: 1
spec_id: SPEC-0043
revision: 6
status: confirmed
change_set: training-worker-selection
working_id: WORKING-SPEC-7cdbba1d4873-training-worker-selection
task_ref: 01a115a7-d434-7871-9b00-b96c7f3c17f3
---
# FIR／MLP 訓練 worker 選擇與記憶體估算提示

## Problem
目前使用者無法指定訓練 worker 數；記憶體拒絕顯示大量原始診斷。使用者觀察到一次啟動遭拒後重試可進行，原因尚未確認，不能據此放寬保護。

## Solution
Training 設定提供 Auto（預設）與 Manual。FIR／MLP fold training 手動可選 1 至 8，實際數量上限為待執行工作數。Auto 沿用既有各演算法策略；FIR 依預算建議可容納數量。Manual 不因預算不足而靜默降級：不足時拒絕 spawn，顯示可行較低數量供使用者改選，或重新檢查後重試。每次啟動前重新讀取記憶體；保留既有 90% ceiling、執行中監控、取消及失敗處理。估算不是實測峰值。

## User Stories
- 使用者可在訓練前控制 FIR／MLP 並行數，了解預估記憶體代價。
- 啟動遭拒時可讀取簡潔原因、改選數量或重新檢查，並展開複製詳細診斷。

## Requirements
| ID | Requirement |
|---|---|
| REQ-001 | UI 提供 Auto 預設與 Manual 1–8，標示 FIR／MLP Training workers；實際數量不超過工作數。 |
| REQ-002 | Auto 保留既有演算法策略；Manual 使用指定數量，預算不足不靜默改數且不得 spawn；保留原有 ceiling 與執行中保護。 |
| REQ-003 | 資料或相關設定變更使估算更新或標為待更新；啟動前重新讀取可用記憶體。顯示數量、預估額外用量、預算與估算時間。 |
| REQ-004 | 顯示簡短拒絕原因；詳細資料可展開、複製，記錄來源識別、時間、total/available、reserve、budget、requested/recommended/actual workers 與最大估算項目。 |
| REQ-005 | 執行中鎖定選項並凍結該批數量；取消與程序回收保持既有契約。模式與數量僅在本次程式期間保留，不變更專案或模型匯出格式。 |
| REQ-006 | 所有工作、fold、資料與訓練數值契約保持不變；不同 worker 數的數值結果按既有容差驗證，不放寬既有時間門檻。 |

## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-005 | Auto 預設、手動 1/2/4/8、非法值、少於選定數量的工作、執行中鎖定與新實例重設均正確。 | Qt UI 與 controller 契約測試。 | Pending |
| AC-002 | REQ-002, REQ-003 | 可控記憶體讀值下驗證邊界、拒絕不 spawn、手動不靜默降級；第一次不足而第二次足夠時可啟動。 | executor 故障注入與計數測試。 | Pending |
| AC-003 | REQ-003, REQ-004 | 估算與實測明確區分；輸入變更不沿用過期估算，啟動重新讀值；摘要與可複製診斷含必要欄位。 | UI、來源識別與診斷契約測試。 | Pending |
| AC-004 | REQ-005, REQ-006 | 一個與多個 worker 執行相同工作，結果符合既有數值容差；取消、錯誤與程序回收無回歸。 | FIR/MLP 整合、取消與相關回歸測試及架構 gate。 | Pending |

## Decisions
| ID | Decision | Rationale | Source |
|---|---|---|---|
| DEC-001 | 採用 Auto/Manual、即時估算提示、手動不靜默降級及保留記憶體保護的完整方案。 | 使用者確認上一則完整修改方案。 | 01a12935-47e9-7af3-9d4b-fb352a942797 |
| DEC-002 | 本次涵蓋 FIR／MLP Training；qualification 與 self-IMU 並行設定不在範圍。 | 採用方案明列範圍。 | 01a12935-47e9-7af3-9d4b-fb352a942797 |

| DEC-003 | 記錄先前已採用的訓練前 worker 選擇與估算建議方向；由 DEC-001 完整方案具體化。 | 補齊既有採用註解來源，功能範圍不變。 | 01a1292d-1c6d-77c3-8037-d97bea3f68de |

## Discussion Context
### DISC-001: 採用 worker 選擇方案
- **Situation:** 使用者先遭 FIR 記憶體估算拒絕，回報重試後成功，之後要求修改方案。
- **Question:** 是否採用呈現的 Auto/Manual 與估算提示方案？
- **Options and tradeoffs:** 採用讓使用者控制並行程度；較少 worker 可能延長訓練時間；保留估算拒絕與執行中保護。維持現況則仍由程式決定。
- **User answer:** 採用此方案。
- **Explicit rationale:** 未另述。
- **Resulting impact:** DEC-001、DEC-002 與 REQ-001 至 REQ-006。完整候選保存於 spec-governance/worker-selection-proposal-20261011.md；確認來源 01a12935-47e9-7af3-9d4b-fb352a942797。重試成功是使用者觀察，不是根因證明。

## Relationships
| Source | Relation | Target |
|---|---|---|
| REQ-002 | refines | SPEC-0042 |
| REQ-006 | refines | SPEC-0041 |

## Out of Scope
移除記憶體保護、改寫估算公式、保證提速、調整 qualification 或 self-IMU 並行數、變更模型、碰撞判定或匯出格式；不改寫 SPEC-0042 的其他任務紀錄。

## Architecture impact
影響 QML Training 設定、controller batch 設定、FIR/MLP fold executor capacity/admission 介面与估算顯示。實作前完成 Boundary Design Table、型別與狀態 ownership、dependency edges 與 parent mappings；僅於 architecture/designs 修改描述，透過受控 renderer 生成 manifest/views，執行單一 architecture_cli.py development/release gates。保留既有模組邊界，不自行接受 ADR。worker 策略由既有 executor 負責；訓練數學不變，記憶體數值仍屬 estimated。

## Open Decisions
None.

## Routing/Gates
使用者已確認方案；尚未取得本次新範圍的開始執行授權。實作前需 spec verification、formatter/architecture gates、驗收規劃；本文件不宣稱測試或驗收通過。

## Revision History
| Revision | Change | Source |
|---|---|---|
| 1 | 保存已採用的 worker 選擇與估算提示方案。 | 01a12935-47e9-7af3-9d4b-fb352a942797 |
| 3 | 2026-10-11 | Reopened before clarification: 補齊已採用決策的原始來源連結；需求、行為與驗收條件不變。 |
| 5 | 2026-10-11 | Reopened before clarification: 校正 agent 引入的過強相依：已採用方案要求沿用現有估算與保護，並未要求 SPEC-0042 全部驗收先完成。改為 refines，保留兩份驗收條件。 |

## Acceptance Mapping

```json
{
  "AC-001": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Qt controls and controller lifecycle require host and adapter contract tests."
  },
  "AC-002": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Controlled memory reads and spawn counters verify admission and executor boundaries."
  },
  "AC-003": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "UI presentation and diagnostic metadata require host and adapter checks."
  },
  "AC-004": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Real host fold workers verify numerical regression and cancellation cleanup; no hardware timing performance claim is introduced."
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

- 01a12935-47e9-7af3-9d4b-fb352a942797: 採用此方案
- 01a1293a-d7e2-7f42-a39e-1c298f74e31e: 開始執行
- 01a1293a-d7e2-7f42-a39e-1c298f74e31e: User adopted the complete worker-selection proposal and now explicitly says 開始執行. SPEC-0043 preserves that scope, memory protections, FIR/MLP-only concurrency settings and session-only preference. DEC-003 restores the original adoption source; requirements and acceptance thresholds unchanged.
- 01a1293a-d7e2-7f42-a39e-1c298f74e31e: User adopted the complete worker-selection proposal and now explicitly says 開始執行. SPEC-0043 preserves that scope, memory protections, FIR/MLP-only concurrency settings and session-only preference. DEC-003 restores the original adoption source; requirements and acceptance thresholds unchanged. Corrected agent-added hard completion prerequisite to a refinement reference; no requirements or acceptance thresholds changed.
- 01a12946-5e65-7873-8a40-9408fb29e7fb: 允許先前提出的兩份架構文件格式修復，繼續已授權的 SPEC-0043
- 01a12946-5e65-7873-8a40-9408fb29e7fb: User explicitly permits the previously proposed two-file architecture format repair. Applied preserved appendix extraction into SPEC-0042-pre-code-notes.md and strict-parser-compatible history_worker_adapter.md. No product requirement change; retain original SPEC-0043 開始執行 authorization.
- 01a12946-5e65-7873-8a40-9408fb29e7fb: User explicitly permits the previously proposed two-file architecture format repair. Applied preserved appendix extraction into SPEC-0042-pre-code-notes.md and strict-parser-compatible history_worker_adapter.md. No product requirement change; retain original SPEC-0043 開始執行 authorization. Both repaired files verified byte-equal to approved candidates. Continued execution reports authorization valid but architecture source/manifest drift from existing SPEC-0042 FIR updates. Attempted managed update-documents with unchanged sources; rejected bounded source changes required. Prepared read-only projected manifest candidate and normalized diff under spec-governance. No worker source edits and no full architecture PASS claim.
- 01a12959-f1b6-7d03-a831-aa9222897574: 開始進行：使用 0.20.0 接續已確認 SPEC-0043 的 worker 選擇實作
- 01a12959-f1b6-7d03-a831-aa9222897574: User says 開始進行, clearly authorizing the existing SPEC-0043 scope under 0.20.0. Read-only 0.20.0 admission with that exact text returns BLOCKED because its regex accepts only 開始執行. Prior receipt cannot match after the 0.20.0 materialize event; preserve actual instructions and do not fabricate a new authorization event. No product edits performed. This is a skill tooling limitation, not a missing design decision or automatic approval review rejection.
- 01a1295d-cbc2-7a91-8069-12b0fac0b4bb: 開始執行 SPEC-0043，使用 0.20.0 技能
- 01a1295d-cbc2-7a91-8069-12b0fac0b4bb: User explicitly says 開始執行 for confirmed SPEC-0043 under version 0.20.0. Requirements and acceptance unchanged. Continue implementation and verification.

### Source and Revision Audit

```jsonl
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"3b998cfc605d91341bcc1ea82823b26f09a68978ad817141cb3acd793e412f81","event_type":"start","event_version":1,"open_decisions":[],"previous_event_hash":null,"previous_snapshot_hash":null,"recorded_at":"2026-10-11T04:27:51.063542+00:00","relationships":[{"relation":"depends_on","source":"REQ-002","target":"SPEC-0042"},{"relation":"refines","source":"REQ-006","target":"SPEC-0041"}],"revision":1,"snapshot_hash":"b53ab1c4705eda7013db4b1a3b7452642df4e597cc50ad0f2f17cf086086ecad","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"922b6de062810e3018046da98be6bb0a6689e6fda268b3e4d2676afa24c96b54","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"3b998cfc605d91341bcc1ea82823b26f09a68978ad817141cb3acd793e412f81","previous_snapshot_hash":"b53ab1c4705eda7013db4b1a3b7452642df4e597cc50ad0f2f17cf086086ecad","recorded_at":"2026-10-11T04:29:11.599478+00:00","relationships":[{"relation":"depends_on","source":"REQ-002","target":"SPEC-0042"},{"relation":"refines","source":"REQ-006","target":"SPEC-0041"}],"revision":2,"snapshot_hash":"f6285b99a234f8e66466c7505f3755bbd93732e23e087646a67ec07c6ea8ce53","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"bc521677347b947b36bc89532673df7826d8000dac778c1f98d7f0bfe0f2303e","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"922b6de062810e3018046da98be6bb0a6689e6fda268b3e4d2676afa24c96b54","previous_snapshot_hash":"f6285b99a234f8e66466c7505f3755bbd93732e23e087646a67ec07c6ea8ce53","recorded_at":"2026-10-11T04:29:27.937495+00:00","relationships":[],"revision":2,"snapshot_hash":"1e604b69ccb3c14aa512eb17cc1f0db7ce3b038c812700098cce52c2e1580f0c","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"採用此方案","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"01a12935-47e9-7af3-9d4b-fb352a942797","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a12935-4751-7673-aeb4-0999cdafa613"},"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"8894df10407dce4adbec1bff217d24c4df819d8533610787ce3d0febc0954b92","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"bc521677347b947b36bc89532673df7826d8000dac778c1f98d7f0bfe0f2303e","previous_snapshot_hash":"1e604b69ccb3c14aa512eb17cc1f0db7ce3b038c812700098cce52c2e1580f0c","recorded_at":"2026-10-11T04:30:09.173634+00:00","relationships":[],"revision":2,"snapshot_hash":"1e604b69ccb3c14aa512eb17cc1f0db7ce3b038c812700098cce52c2e1580f0c","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"開始執行","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"01a1293a-d7e2-7f42-a39e-1c298f74e31e","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a1293a-d72b-7fa3-bfab-17ba4d26a771"},"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"46deeb0c5f3778a5078233570b58e5705909c3436b4092d396b088bb0c9a35c2","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"8894df10407dce4adbec1bff217d24c4df819d8533610787ce3d0febc0954b92","previous_snapshot_hash":"1e604b69ccb3c14aa512eb17cc1f0db7ce3b038c812700098cce52c2e1580f0c","recorded_at":"2026-10-11T04:32:27.112847+00:00","relationships":[],"revision":2,"snapshot_hash":"1e604b69ccb3c14aa512eb17cc1f0db7ce3b038c812700098cce52c2e1580f0c","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"baseline_contract_hash":"72df77d5d0f35ba3c83c2984f5bbfd591f305c48574769d7dd371be90a05da0a","conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"2189782a326c11d8f893b87790deea3e690fcfd254071460a455afb9e898e152","event_type":"reopen","event_version":1,"open_decisions":[],"previous_event_hash":"46deeb0c5f3778a5078233570b58e5705909c3436b4092d396b088bb0c9a35c2","previous_snapshot_hash":"1e604b69ccb3c14aa512eb17cc1f0db7ce3b038c812700098cce52c2e1580f0c","recorded_at":"2026-10-11T04:32:54.335828+00:00","relationships":[],"revision":3,"snapshot_hash":"ae4d6ca9f1c0fc842212c22ea9640ecc3f684d375b0004897f9de6ddab5feb9d","verdict":"BLOCKED","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":["DEC-003"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["DEC-003"],"changed_ids":[],"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"4df9fe3e7cf77308f4cf331ff94a43294fd68905cea4c3b05eee7c7898447eff","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"2189782a326c11d8f893b87790deea3e690fcfd254071460a455afb9e898e152","previous_snapshot_hash":"ae4d6ca9f1c0fc842212c22ea9640ecc3f684d375b0004897f9de6ddab5feb9d","recorded_at":"2026-10-11T04:33:28.249191+00:00","relationships":[{"relation":"depends_on","source":"REQ-002","target":"SPEC-0042"},{"relation":"refines","source":"REQ-006","target":"SPEC-0041"}],"revision":4,"snapshot_hash":"24f4afa2d14a5f0786faddf40e026155284e5169beb8c61c4291a33945796e12","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"5a2ed59eb2f557470b5f365fb44c6fd29dc60864b448deee1b9c0caa34594f6e","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"4df9fe3e7cf77308f4cf331ff94a43294fd68905cea4c3b05eee7c7898447eff","previous_snapshot_hash":"24f4afa2d14a5f0786faddf40e026155284e5169beb8c61c4291a33945796e12","recorded_at":"2026-10-11T04:34:15.582538+00:00","relationships":[],"revision":4,"snapshot_hash":"a68b39eb65eadb5c40b7b5d2518579c37dd3abddf6e595aed115c70ff0682327","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":4,"snapshot_hash":"a68b39eb65eadb5c40b7b5d2518579c37dd3abddf6e595aed115c70ff0682327","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"},"candidates":[],"completeness_review":null,"identified_items":{"training-retry-succeeded":{"id":"training-retry-succeeded","kind":"fact","source_ref":"01a1292d-1c6d-77c3-8037-d97bea3f68de","text":"使用者回報重新按 Start Training 後已能進行訓練。這是使用者觀察，不是已確認根因；可能涉及可用記憶體或程序資源狀態變化，須比較兩次紀錄才能判定。"},"worker-selection-adopted":{"id":"worker-selection-adopted","kind":"accepted","source_ref":"01a1292d-1c6d-77c3-8037-d97bea3f68de","text":"使用者採用：訓練前由使用者選擇 worker 數量，程式提供記憶體估算建議。採用註解僅指向這項方案，不推定已採用繞過記憶體檢查。"}},"item_bindings":{"training-retry-succeeded":[],"worker-selection-adopted":["DEC-003","REQ-001"]},"kind":"saved","reply_sha256":"01ab19c55b49fc4598d80c8430d45593c5af7a73b9fd0c21ed87c27db813b4a3","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a1292d-1c6d-77c3-8037-d97bea3f68de","01a12930-ff79-7aa1-929c-20c2b2c86eec","01a12935-47e9-7af3-9d4b-fb352a942797","01a1293a-d7e2-7f42-a39e-1c298f74e31e"],"source_ref":"01a1293a-d7e2-7f42-a39e-1c298f74e31e","summary":"User adopted the complete worker-selection proposal and now explicitly says 開始執行. SPEC-0043 preserves that scope, memory protections, FIR/MLP-only concurrency settings and session-only preference. DEC-003 restores the original adoption source; requirements and acceptance thresholds unchanged.","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a1293a-d72b-7fa3-bfab-17ba4d26a771"},"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"3106be29a507aa7d8a7ba654fa02c329b8b7a1ad0f111fba9782a73bd9618142","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"5a2ed59eb2f557470b5f365fb44c6fd29dc60864b448deee1b9c0caa34594f6e","previous_snapshot_hash":"a68b39eb65eadb5c40b7b5d2518579c37dd3abddf6e595aed115c70ff0682327","recorded_at":"2026-10-11T04:35:08.318422+00:00","relationships":[],"revision":4,"snapshot_hash":"a68b39eb65eadb5c40b7b5d2518579c37dd3abddf6e595aed115c70ff0682327","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"baseline_contract_hash":"8282202b6c67ca5e3d18161e21062c983390bb54c8c589e7291122453730ab34","conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"2eaa25ca2ff34ce5e181ca7e5aa86f0677a7ff1a9cd6cb9e08b0f09893c361b7","event_type":"reopen","event_version":1,"open_decisions":[],"previous_event_hash":"3106be29a507aa7d8a7ba654fa02c329b8b7a1ad0f111fba9782a73bd9618142","previous_snapshot_hash":"a68b39eb65eadb5c40b7b5d2518579c37dd3abddf6e595aed115c70ff0682327","recorded_at":"2026-10-11T04:37:54.791704+00:00","relationships":[],"revision":5,"snapshot_hash":"54247b473fbda4267fa5233718e38f0a2decd68dae8b5ccb5f26efa62b23290f","verdict":"BLOCKED","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"881beb4bd224dd4863a8fd2dfa69e0474405de74af670bbfb975629f6ae518be","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"2eaa25ca2ff34ce5e181ca7e5aa86f0677a7ff1a9cd6cb9e08b0f09893c361b7","previous_snapshot_hash":"54247b473fbda4267fa5233718e38f0a2decd68dae8b5ccb5f26efa62b23290f","recorded_at":"2026-10-11T04:38:14.512266+00:00","relationships":[{"relation":"refines","source":"REQ-002","target":"SPEC-0042"},{"relation":"refines","source":"REQ-006","target":"SPEC-0041"}],"revision":6,"snapshot_hash":"b34b3480d07ec79d5837814c4d9902372a370dc47eb71801c44941e14bb6c07e","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"f78fa3885d064337da2329843ebd3232e6ce8babfe08b858db08e3d2e4f8f1b0","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"881beb4bd224dd4863a8fd2dfa69e0474405de74af670bbfb975629f6ae518be","previous_snapshot_hash":"b34b3480d07ec79d5837814c4d9902372a370dc47eb71801c44941e14bb6c07e","recorded_at":"2026-10-11T04:38:30.994555+00:00","relationships":[],"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"},"candidates":[],"completeness_review":null,"identified_items":{"training-retry-succeeded":{"id":"training-retry-succeeded","kind":"fact","source_ref":"01a1292d-1c6d-77c3-8037-d97bea3f68de","text":"使用者回報重新按 Start Training 後已能進行訓練。這是使用者觀察，不是已確認根因；可能涉及可用記憶體或程序資源狀態變化，須比較兩次紀錄才能判定。"},"worker-selection-adopted":{"id":"worker-selection-adopted","kind":"accepted","source_ref":"01a1292d-1c6d-77c3-8037-d97bea3f68de","text":"使用者採用：訓練前由使用者選擇 worker 數量，程式提供記憶體估算建議。採用註解僅指向這項方案，不推定已採用繞過記憶體檢查。"}},"item_bindings":{"training-retry-succeeded":[],"worker-selection-adopted":["DEC-003","REQ-001"]},"kind":"saved","reply_sha256":"01ab19c55b49fc4598d80c8430d45593c5af7a73b9fd0c21ed87c27db813b4a3","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a1292d-1c6d-77c3-8037-d97bea3f68de","01a12930-ff79-7aa1-929c-20c2b2c86eec","01a12935-47e9-7af3-9d4b-fb352a942797","01a1293a-d7e2-7f42-a39e-1c298f74e31e"],"source_ref":"01a1293a-d7e2-7f42-a39e-1c298f74e31e","summary":"User adopted the complete worker-selection proposal and now explicitly says 開始執行. SPEC-0043 preserves that scope, memory protections, FIR/MLP-only concurrency settings and session-only preference. DEC-003 restores the original adoption source; requirements and acceptance thresholds unchanged. Corrected agent-added hard completion prerequisite to a refinement reference; no requirements or acceptance thresholds changed.","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a1293a-d72b-7fa3-bfab-17ba4d26a771"},"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"82fff7f5e95cad283b0ae43487245ab284dfbd75eecad295a2c829466d7882c1","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"f78fa3885d064337da2329843ebd3232e6ce8babfe08b858db08e3d2e4f8f1b0","previous_snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","recorded_at":"2026-10-11T04:38:58.480351+00:00","relationships":[],"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"允許先前提出的兩份架構文件格式修復，繼續已授權的 SPEC-0043","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"01a12946-5e65-7873-8a40-9408fb29e7fb","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a12946-5dd3-7a71-82a3-6b28b116e576"},"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"b737f45eb2631b53ca14927c8332d0c834f1b415a191396c98a8a87b72b91f96","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"82fff7f5e95cad283b0ae43487245ab284dfbd75eecad295a2c829466d7882c1","previous_snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","recorded_at":"2026-10-11T04:48:11.017851+00:00","relationships":[],"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"54f78d4eed62da4955792851df0ba789f43494e58920847e79796ad3f5d8c615","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a12946-5e65-7873-8a40-9408fb29e7fb"],"source_ref":"01a12946-5e65-7873-8a40-9408fb29e7fb","summary":"User explicitly permits the previously proposed two-file architecture format repair. Applied preserved appendix extraction into SPEC-0042-pre-code-notes.md and strict-parser-compatible history_worker_adapter.md. No product requirement change; retain original SPEC-0043 開始執行 authorization.","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a12946-5dd3-7a71-82a3-6b28b116e576"},"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"74a433bd109acf5a63eb38a53c799f8041a39168b485345bf38ad4561f7f1259","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"b737f45eb2631b53ca14927c8332d0c834f1b415a191396c98a8a87b72b91f96","previous_snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","recorded_at":"2026-10-11T04:49:16.251789+00:00","relationships":[],"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"ef4e7ed1329d6923c37d2e99ea14bdb0040212f4672b3e43932784f052826b33","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a12946-5e65-7873-8a40-9408fb29e7fb"],"source_ref":"01a12946-5e65-7873-8a40-9408fb29e7fb","summary":"User explicitly permits the previously proposed two-file architecture format repair. Applied preserved appendix extraction into SPEC-0042-pre-code-notes.md and strict-parser-compatible history_worker_adapter.md. No product requirement change; retain original SPEC-0043 開始執行 authorization. Both repaired files verified byte-equal to approved candidates. Continued execution reports authorization valid but architecture source/manifest drift from existing SPEC-0042 FIR updates. Attempted managed update-documents with unchanged sources; rejected bounded source changes required. Prepared read-only projected manifest candidate and normalized diff under spec-governance. No worker source edits and no full architecture PASS claim.","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a12946-5dd3-7a71-82a3-6b28b116e576"},"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"cf76cb58c663f0ad51c9c20544ab13962189fc35f6a3c1807b7cf7c4663d48ec","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"74a433bd109acf5a63eb38a53c799f8041a39168b485345bf38ad4561f7f1259","previous_snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","recorded_at":"2026-10-11T04:56:32.873934+00:00","relationships":[],"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"f863db9d7a36e4f38d4c4c2e6529e400607d6e7c3a84d5669e3476420876df3d","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"cf76cb58c663f0ad51c9c20544ab13962189fc35f6a3c1807b7cf7c4663d48ec","previous_snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","recorded_at":"2026-10-11T05:02:43.103779+00:00","relationships":[],"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"開始進行：使用 0.20.0 接續已確認 SPEC-0043 的 worker 選擇實作","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"01a12959-f1b6-7d03-a831-aa9222897574","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a12959-f143-7841-8e6c-3983d24f7247"},"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"7d360b14eeb5c689355f4a2ac7cab050a60d65d6d5eb6081cc6d6b3461bbb1ad","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"f863db9d7a36e4f38d4c4c2e6529e400607d6e7c3a84d5669e3476420876df3d","previous_snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","recorded_at":"2026-10-11T05:06:19.460593+00:00","relationships":[],"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"142b6b1a01845e8e63f0d7685749dff4648ea63f7ad19ac755a7f73913c263f6","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a12959-f1b6-7d03-a831-aa9222897574"],"source_ref":"01a12959-f1b6-7d03-a831-aa9222897574","summary":"User says 開始進行, clearly authorizing the existing SPEC-0043 scope under 0.20.0. Read-only 0.20.0 admission with that exact text returns BLOCKED because its regex accepts only 開始執行. Prior receipt cannot match after the 0.20.0 materialize event; preserve actual instructions and do not fabricate a new authorization event. No product edits performed. This is a skill tooling limitation, not a missing design decision or automatic approval review rejection.","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a12959-f143-7841-8e6c-3983d24f7247"},"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"69c600540a848752554db4d27d041a9cdfa2409d994f6e91c7d6122156f68498","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"7d360b14eeb5c689355f4a2ac7cab050a60d65d6d5eb6081cc6d6b3461bbb1ad","previous_snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","recorded_at":"2026-10-11T05:08:30.870575+00:00","relationships":[],"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"開始執行 SPEC-0043，使用 0.20.0 技能","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"01a1295d-cbc2-7a91-8069-12b0fac0b4bb","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a1295d-cb37-79f3-b5a7-22eaef253fde"},"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"13c169ac4a9a1e713d50d89274b9b38f30553a5f99e75221069a64f2012eba50","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"69c600540a848752554db4d27d041a9cdfa2409d994f6e91c7d6122156f68498","previous_snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","recorded_at":"2026-10-11T05:10:10.367410+00:00","relationships":[],"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"d278867dc05ef3fff56c9e3869f4847206ddb2cc173dcf44e2e307ecf37e4f1d","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a1295d-cbc2-7a91-8069-12b0fac0b4bb"],"source_ref":"01a1295d-cbc2-7a91-8069-12b0fac0b4bb","summary":"User explicitly says 開始執行 for confirmed SPEC-0043 under version 0.20.0. Requirements and acceptance unchanged. Continue implementation and verification.","task_ref":"01a115a7-d434-7871-9b00-b96c7f3c17f3","turn_id":"01a1295d-cb37-79f3-b5a7-22eaef253fde"},"removed_ids":[]},"epoch":"5b9a3fdbbc65473d9ff20733a99e58d5","event_hash":"a7f4624c34f9de72762d2231a6bd0ea4413970c8ba62f9eccfd3a9c661ca5cee","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"13c169ac4a9a1e713d50d89274b9b38f30553a5f99e75221069a64f2012eba50","previous_snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","recorded_at":"2026-10-11T05:10:59.766845+00:00","relationships":[],"revision":6,"snapshot_hash":"b2dae4ebdbd31845e5dab7b715d329853b4def85084bff70219e1acec8d08879","verdict":"PASS","working_id":"WORKING-SPEC-7cdbba1d4873-training-worker-selection"}
```
<!-- spec-audit:end -->
