---
spec_version: 1
spec_id: SPEC-0051
revision: 6
status: working
change_set: original-threshold-collision-replay
working_id: WORKING-SPEC-b504291d66da-original-threshold-collision-replay
task_ref: 01a1a0e6-b944-7920-ba7c-5ab8a7ebffb4
---
# Original 免訓練門檻搜尋與碰撞結果

## Problem
使用者希望參考 env_sensing，把 oriental 演算法加入目前 Dual IMU Collision Studio。使用者補充不需要訓練，只需找出 threshold 並顯示碰撞結果。

## Solution
待確認方案：新增免訓練的 Original 判定路徑，參考韌體固定演算法計算特徵、搜尋門檻並重播事件。不可把此路徑當成 FIR/MLP 訓練。oriental 暫按程式中的 Original 對應，保留待使用者更正。

所有已匯入的 Recording／Offset／Speed 使用同一個 threshold，搜尋必須同時滿足全部工況的已採用標準。

## User Stories
使用者匯入及標註錄製資料後，不訓練模型即可取得門檻與碰撞判定結果。

## Requirements
| ID | Requirement | Source |
|---|---|---|
| REQ-001 | 參考 env_sensing 的既有演算法整合到目前 Studio；使用者稱為 oriental，調查對應 Original 尚屬假設。 | user:oriental-request |
| REQ-002 | 本次流程不訓練模型，只找出 threshold 並顯示碰撞結果。 | user:threshold-no-training |

| REQ-003 | 自動 threshold 搜尋以正常動作零誤報且標註碰撞全部檢出為目標；無可行門檻時必須明示並列出誤報與漏報。 | user:adopt-threshold-objective |

| REQ-004 | 所有已匯入的 Recording／Offset／Speed 共用同一個 threshold；不得用分組不同門檻冒充共用門檻成功。 | user:yes-shared-threshold |

## Decisions
| ID | Decision | Source |
|---|---|---|
| DEC-001 | 使用 env_sensing 作為演算法實作參考。 | user:oriental-request |
| DEC-002 | 排除訓練，保留 threshold 搜尋與碰撞結果顯示。 | user:threshold-no-training |

| DEC-003 | 採用正常動作零誤報、標註碰撞全部檢出的搜尋目標；無解時顯示無可行門檻及誤報、漏報。 | user:adopt-threshold-objective |

| DEC-004 | 同意所有已匯入的 Recording／Offset／Speed 共用一個 threshold。 | user:yes-shared-threshold |

## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | 所採演算法與確認的韌體參考行為一致。 | 固定輸入比對濾波、包絡線、EWMA 與事件序列；精確範圍待確認。 | NOT RUN |
| AC-002 | REQ-002 | 無需訓練即可取得 threshold 與碰撞結果。 | 主機流程與結果顯示驗證，搜尋目標待確認。 | NOT RUN |

| AC-003 | REQ-003 | 可行資料回傳符合零誤報與碰撞全檢出的 threshold；不可行資料明示無可行門檻及誤報、漏報，不誤標為通過。 | 可行與不可行受控資料的主機搜尋及事件重播驗證；具體搜尋範圍、時限與診斷候選規則待確認。 | NOT RUN |

| AC-004 | REQ-004, REQ-003 | 多 Recording／Offset／Speed 資料的成功結果以同一 threshold 重播；各組各自可分但沒有共同可行門檻時，總結果顯示無可行門檻。 | 多工況可行交集與無交集受控資料測試，核對所有重播使用同一參數。 | NOT RUN |

## Relationships
depends_on: None
refines: None
conflicts_with: None
supersedes: None

## Out of Scope
模型訓練不屬於本次功能。韌體燒錄、修改 env_sensing、部署與匯出尚未被要求。

## Open Decisions
逐軸或向量模式、資料來源、前處理接入、碰撞檢出時限與無解診斷候選規則需釐清。

## Routing/Gates
討論草稿；產品程式未修改。路由發現既有多份 working/confirmed 規格，因此本次明確建立新 change_set。project_validation: BLOCKED；test-validation-layout: FAIL，既有測試路徑需依後續正式範圍檢查。架構、formatter、正式 SPEC 與執行授權尚未完成。

## Discussion Context
DISC-001: user:oriental-request 提出整合意圖；user:threshold-no-training 明確排除訓練。
唯讀證據：env_sensing/src/modules/collision/collision_detector.cpp 的 ProcessOriginalPrepared、Process、UpdateEwma；acceleration_feature_processor.cpp 的 UpdateEnvelope；collision_filter.cpp 固定 SOS profiles；src/modules/event_policy/event_policy.h 的 EvaluateRearm。
原始特徵流程為濾波、包絡線、EWMA，逐軸或向量大於 threshold 觸發；低於 0.8 倍 threshold 持續 50 ms 解除鎖存。Original 優先 remote，其次 base。這些是來源事實，尚非所有模式均納入本次的承諾。
候選 CAND-001 已由 user:adopt-threshold-objective 採納為 REQ-003、DEC-003；採用回答不構成產品執行授權。

### DISC-002: 採用門檻搜尋標準
- **Situation:** 免訓練碰撞流程需要明確門檻選擇目標與無解呈現。
- **Question:** 是否採用「正常動作零誤報、標註碰撞全部檢出」作為 threshold 搜尋標準，找不到時就顯示無可行門檻並列出誤報、漏報？
- **Options and tradeoffs:** 單一開放問題；建議以兩項條件同時滿足為可行，無解需保留診斷，不保證資料必然可分。
- **User answer:** 採用
- **Explicit rationale:** 使用者未另述理由。來源 user:adopt-threshold-objective。
- **Resulting impact:** 新增 REQ-003、DEC-003、AC-003，落實 threshold 目標與無解顯示；產品執行尚未授權。

### DISC-003: 全部工況共用門檻
- **Situation:** Studio 有 Recording、Offset、Speed 分組，搜尋範圍會影響單一門檻是否可行。
- **Question:** 是否讓所有已匯入的 Recording／Offset／Speed 共用一個 threshold？
- **Options and tradeoffs:** 單一開放問題；建議共用以檢查同一設定涵蓋全部工況，要求較嚴格且可能無共同可行值。
- **User answer:** 是
- **Explicit rationale:** 使用者未另述理由。來源 user:yes-shared-threshold。
- **Resulting impact:** 新增 REQ-004、DEC-004、AC-004；REQ-003 的目標在全部工況共同門檻上判斷，尚未授權產品執行。

## Pending Decision

```json
{
  "id": "Q-003",
  "version": 6,
  "question": "是否沿用現有規則：從碰撞標註起點算起，150 ms 內（含邊界）觸發才算檢出，逾時算漏報？",
  "options": [],
  "kind": "open-text"
}
```

## Revision History
| Revision | Change |
|---|---|
| 1 | 保存整合意圖、免訓練需求、來源調查與待確認範圍。 |
| 3 | user:adopt-threshold-objective 採用 Q-001，新增門檻搜尋目標與無解顯示契約。 |
| 5 | user:yes-shared-threshold 回答 Q-002，確立所有 Recording／Offset／Speed 共用一個 threshold。 |

## Current Specification

See Problem, Solution, Requirements and Acceptance Criteria above.

## Decision History

See Decisions, Discussion Context and the sourced Discussion History below.

## Pending Discussion

- 逐軸或向量模式、資料來源、前處理接入、碰撞檢出時限與無解診斷候選規則需釐清。
- Q-003@6

## Completeness Gaps

- unanswered pending decision prevents canonical verification
- confirmed and implemented specs must have zero open decisions
- Acceptance planning: invalid canonical specification

<!-- spec-audit:start -->
## Discussion History

- user:oriental-request;user:threshold-no-training: 使用者要參考 env_sensing 整合演算法至目前 Studio，不需要訓練，只找 threshold 並顯示碰撞結果。
- assistant:threshold-objective: 保存使用者免訓練需求與 env_sensing Original 調查，等待確認 threshold 搜尋目標；候選尚未採納，未取得產品執行授權。
- assistant:threshold-objective: 保存使用者免訓練需求與 env_sensing Original 調查，等待確認 threshold 搜尋目標；候選尚未採納，未取得產品執行授權。
- user:adopt-threshold-objective: 使用者回覆「採用」，回答 SPEC-0051 Q-001：正常動作零誤報、標註碰撞全部檢出搜尋 threshold；無可行門檻時列出誤報、漏報。
- user:adopt-threshold-objective: 已採用 Q-001；新增 REQ-003、DEC-003、AC-003 及 DISC-002，關係無變更且無衝突。仍待確認 threshold 共用範圍等行為；規格 BLOCKED 為未決事項，尚未取得產品執行授權。
- user:yes-shared-threshold: 是。使用者回答 SPEC-0051 Q-002，同意所有已匯入 Recording／Offset／Speed 共用一個 threshold。
- user:yes-shared-threshold: Q-002 已回答是；新增 REQ-004、DEC-004、AC-004、DISC-003，關係無變更且無衝突；全部工況共用 threshold。規格因其餘未決事項仍為 BLOCKED，下一問確認 150 ms 檢出時限。未取得產品執行授權。

### Source and Revision Audit

```jsonl
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"9e9998d39a18a54bbc2a3eff4c44d1e947d43682fe08f3c650924c20b1e0e8ae","event_type":"start","event_version":1,"open_decisions":["threshold 自動選擇目標與無可行門檻時的行為；Original 名稱對應；逐軸或向量模式、資料來源與前處理接入需釐清。"],"previous_event_hash":null,"previous_snapshot_hash":null,"recorded_at":"2026-11-03T10:19:19.294895+00:00","relationships":[],"revision":1,"snapshot_hash":"c2d521346881126ab4a1a4f44e249bb14e5c6656dca19b3ec3fa835538d41d85","verdict":"BLOCKED","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"使用者要參考 env_sensing 整合演算法至目前 Studio，不需要訓練，只找 threshold 並顯示碰撞結果。","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:oriental-request;user:threshold-no-training","task_ref":"01a1a0e6-b944-7920-ba7c-5ab8a7ebffb4","turn_id":"user-threshold-no-training"},"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"36a13330b7cf0cc821d653935762b1b23c8a8d80eacfa4bb7ee0d8f9e15c5c7f","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"9e9998d39a18a54bbc2a3eff4c44d1e947d43682fe08f3c650924c20b1e0e8ae","previous_snapshot_hash":"c2d521346881126ab4a1a4f44e249bb14e5c6656dca19b3ec3fa835538d41d85","recorded_at":"2026-11-03T10:19:41.382517+00:00","relationships":[],"revision":1,"snapshot_hash":"c2d521346881126ab4a1a4f44e249bb14e5c6656dca19b3ec3fa835538d41d85","verdict":"PASS","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"ec1cbcb903be2952e34b3a95cfedae73a729398100b03867acaeb7f89c5e19d4","event_type":"reconcile","event_version":1,"open_decisions":["threshold 自動選擇目標與無可行門檻時的行為；Original 名稱對應；逐軸或向量模式、資料來源與前處理接入需釐清。","Q-001@2"],"previous_event_hash":"36a13330b7cf0cc821d653935762b1b23c8a8d80eacfa4bb7ee0d8f9e15c5c7f","previous_snapshot_hash":"c2d521346881126ab4a1a4f44e249bb14e5c6656dca19b3ec3fa835538d41d85","recorded_at":"2026-11-03T10:20:02.214280+00:00","relationships":[],"revision":2,"snapshot_hash":"175737c871c9f9e8155b97c3d301d71bbe6ac668392289187a522a6d1248280d","verdict":"BLOCKED","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":2,"snapshot_hash":"175737c871c9f9e8155b97c3d301d71bbe6ac668392289187a522a6d1248280d","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"},"candidates":[],"completeness_review":null,"identified_items":{"I-001":{"id":"I-001","kind":"accepted","source_ref":"user:oriental-request","text":"參考 env_sensing 將演算法加入目前 Studio。"},"I-002":{"id":"I-002","kind":"accepted","source_ref":"user:threshold-no-training","text":"不需要訓練，只找 threshold 並顯示碰撞結果。"},"I-003":{"id":"I-003","kind":"candidate","source_ref":"assistant:threshold-objective","text":"以正常動作零誤報、標註碰撞全檢出搜尋，無可行門檻時明示誤報漏報。"}},"item_bindings":{"I-001":["REQ-001","DEC-001"],"I-002":["REQ-002","DEC-002"],"I-003":[]},"kind":"saved","reply_sha256":"2d8de8697036b1b667fedc387ca3e01ceca4b7fb8641219aa5f2d571dc7160fb","reply_stage":"prepared-until-host-stop","reviewed_sources":["assistant:threshold-objective","user:oriental-request","user:oriental-request;user:threshold-no-training","user:threshold-no-training"],"source_ref":"assistant:threshold-objective","summary":"保存使用者免訓練需求與 env_sensing Original 調查，等待確認 threshold 搜尋目標；候選尚未採納，未取得產品執行授權。","task_ref":"01a1a0e6-b944-7920-ba7c-5ab8a7ebffb4","turn_id":"user-threshold-no-training"},"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"1e1718136a0e805c7a32f1f2b51037e2e522a71a8c16670598126277502539a7","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"ec1cbcb903be2952e34b3a95cfedae73a729398100b03867acaeb7f89c5e19d4","previous_snapshot_hash":"175737c871c9f9e8155b97c3d301d71bbe6ac668392289187a522a6d1248280d","recorded_at":"2026-11-03T10:20:29.860735+00:00","relationships":[],"revision":2,"snapshot_hash":"175737c871c9f9e8155b97c3d301d71bbe6ac668392289187a522a6d1248280d","verdict":"PASS","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":2,"snapshot_hash":"175737c871c9f9e8155b97c3d301d71bbe6ac668392289187a522a6d1248280d","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"},"candidates":[],"completeness_review":null,"identified_items":{"I-001":{"id":"I-001","kind":"accepted","source_ref":"user:oriental-request","text":"參考 env_sensing 將演算法加入目前 Studio。"},"I-002":{"id":"I-002","kind":"accepted","source_ref":"user:threshold-no-training","text":"不需要訓練，只找 threshold 並顯示碰撞結果。"},"I-003":{"id":"I-003","kind":"candidate","source_ref":"assistant:threshold-objective","text":"以正常動作零誤報、標註碰撞全檢出搜尋，無可行門檻時明示誤報漏報。"}},"item_bindings":{"I-001":["REQ-001","DEC-001"],"I-002":["REQ-002","DEC-002"],"I-003":[]},"kind":"saved","reply_sha256":"b31c372756a7594e1fbe2a91349a36e42135609d63b399d1a31a3ba5076e0e21","reply_stage":"prepared-until-host-stop","reviewed_sources":["assistant:threshold-objective","user:oriental-request","user:oriental-request;user:threshold-no-training","user:threshold-no-training"],"source_ref":"assistant:threshold-objective","summary":"保存使用者免訓練需求與 env_sensing Original 調查，等待確認 threshold 搜尋目標；候選尚未採納，未取得產品執行授權。","task_ref":"01a1a0e6-b944-7920-ba7c-5ab8a7ebffb4","turn_id":"user-threshold-no-training"},"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"612d1ab20fdbe3d1075d710389b5ec697c84c02901920e0e9e0cfe2bc9b454ce","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"1e1718136a0e805c7a32f1f2b51037e2e522a71a8c16670598126277502539a7","previous_snapshot_hash":"175737c871c9f9e8155b97c3d301d71bbe6ac668392289187a522a6d1248280d","recorded_at":"2026-11-03T10:22:13.467019+00:00","relationships":[],"revision":2,"snapshot_hash":"175737c871c9f9e8155b97c3d301d71bbe6ac668392289187a522a6d1248280d","verdict":"PASS","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"使用者回覆「採用」，回答 SPEC-0051 Q-001：正常動作零誤報、標註碰撞全部檢出搜尋 threshold；無可行門檻時列出誤報、漏報。","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:adopt-threshold-objective","task_ref":"01a1a0e6-b944-7920-ba7c-5ab8a7ebffb4","turn_id":"user-adopt-threshold-objective"},"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"458dec55b742870ed06aa463052cc264ab10a5da040f2c60d3b5207f3a0131f6","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"612d1ab20fdbe3d1075d710389b5ec697c84c02901920e0e9e0cfe2bc9b454ce","previous_snapshot_hash":"175737c871c9f9e8155b97c3d301d71bbe6ac668392289187a522a6d1248280d","recorded_at":"2026-11-03T10:24:46.594238+00:00","relationships":[],"revision":2,"snapshot_hash":"175737c871c9f9e8155b97c3d301d71bbe6ac668392289187a522a6d1248280d","verdict":"PASS","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":["AC-003","DEC-003","DISC-002","REQ-003"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["AC-003","DEC-003","DISC-002","REQ-003"],"changed_ids":[],"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"a32d772c6423ae34fac7f39c0c3409df790aaed0981270e0fa20f4e0d49e7123","event_type":"reconcile","event_version":1,"open_decisions":["threshold 共用或分組的範圍；逐軸或向量模式、資料來源、前處理接入、碰撞檢出時限與無解診斷候選規則需釐清。"],"previous_event_hash":"458dec55b742870ed06aa463052cc264ab10a5da040f2c60d3b5207f3a0131f6","previous_snapshot_hash":"175737c871c9f9e8155b97c3d301d71bbe6ac668392289187a522a6d1248280d","recorded_at":"2026-11-03T10:26:19.478919+00:00","relationships":[],"revision":3,"snapshot_hash":"5d4fd868d5f7becc36aab1da0e0068ded03dd4cc1da7448033f5cd35f64bccc6","verdict":"BLOCKED","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"a21cd5cb93f54801fe81bfd104b9b4047e44318c1ea3713156edf63c8cc6c9e4","event_type":"reconcile","event_version":1,"open_decisions":["threshold 共用或分組的範圍；逐軸或向量模式、資料來源、前處理接入、碰撞檢出時限與無解診斷候選規則需釐清。","Q-002@4"],"previous_event_hash":"a32d772c6423ae34fac7f39c0c3409df790aaed0981270e0fa20f4e0d49e7123","previous_snapshot_hash":"5d4fd868d5f7becc36aab1da0e0068ded03dd4cc1da7448033f5cd35f64bccc6","recorded_at":"2026-11-03T10:26:54.200228+00:00","relationships":[],"revision":4,"snapshot_hash":"c63b73cbfa134907cf45f74101fd437920c4dbb0c53e76962a26285911b49e18","verdict":"BLOCKED","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":4,"snapshot_hash":"c63b73cbfa134907cf45f74101fd437920c4dbb0c53e76962a26285911b49e18","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"},"candidates":[],"completeness_review":null,"identified_items":{"I-004":{"id":"I-004","kind":"accepted","source_ref":"user:adopt-threshold-objective","text":"使用者回答採用：正常動作零誤報、標註碰撞全部檢出搜尋 threshold；無解時顯示無可行門檻並列出誤報漏報。"}},"item_bindings":{"I-004":["REQ-003","DEC-003","AC-003"]},"kind":"saved","reply_sha256":"c358658c41ee446d729f8ace3705b98fff5096657b9649437afd7cd1b0223421","reply_stage":"prepared-until-host-stop","reviewed_sources":["user:adopt-threshold-objective"],"source_ref":"user:adopt-threshold-objective","summary":"已採用 Q-001；新增 REQ-003、DEC-003、AC-003 及 DISC-002，關係無變更且無衝突。仍待確認 threshold 共用範圍等行為；規格 BLOCKED 為未決事項，尚未取得產品執行授權。","task_ref":"01a1a0e6-b944-7920-ba7c-5ab8a7ebffb4","turn_id":"user-adopt-threshold-objective"},"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"51a768c380ef53443588f1852d2be39a02cea02c7b3065d2e6ac2a2b7e0e4729","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"a21cd5cb93f54801fe81bfd104b9b4047e44318c1ea3713156edf63c8cc6c9e4","previous_snapshot_hash":"c63b73cbfa134907cf45f74101fd437920c4dbb0c53e76962a26285911b49e18","recorded_at":"2026-11-03T10:26:59.597460+00:00","relationships":[],"revision":4,"snapshot_hash":"c63b73cbfa134907cf45f74101fd437920c4dbb0c53e76962a26285911b49e18","verdict":"PASS","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"是。使用者回答 SPEC-0051 Q-002，同意所有已匯入 Recording／Offset／Speed 共用一個 threshold。","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:yes-shared-threshold","task_ref":"01a1a0e6-b944-7920-ba7c-5ab8a7ebffb4","turn_id":"user-yes-shared-threshold"},"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"6bf98de5198eba1c84fd2be51b1dea07b20a5434b98c3d97afa28f56b05ec763","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"51a768c380ef53443588f1852d2be39a02cea02c7b3065d2e6ac2a2b7e0e4729","previous_snapshot_hash":"c63b73cbfa134907cf45f74101fd437920c4dbb0c53e76962a26285911b49e18","recorded_at":"2026-11-03T10:31:34.775621+00:00","relationships":[],"revision":4,"snapshot_hash":"c63b73cbfa134907cf45f74101fd437920c4dbb0c53e76962a26285911b49e18","verdict":"PASS","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":["AC-004","DEC-004","DISC-003","REQ-004"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["AC-004","DEC-004","DISC-003","REQ-004"],"changed_ids":[],"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"9323c6d133b2e591e6bb912fb689731b5843ef9cf944ab6f694dcb12484c63c3","event_type":"reconcile","event_version":1,"open_decisions":["逐軸或向量模式、資料來源、前處理接入、碰撞檢出時限與無解診斷候選規則需釐清。"],"previous_event_hash":"6bf98de5198eba1c84fd2be51b1dea07b20a5434b98c3d97afa28f56b05ec763","previous_snapshot_hash":"c63b73cbfa134907cf45f74101fd437920c4dbb0c53e76962a26285911b49e18","recorded_at":"2026-11-03T10:33:26.071840+00:00","relationships":[],"revision":5,"snapshot_hash":"56f3f655e48e0df330706c6f634471c711e1f24d9237302e107f985fc589327e","verdict":"BLOCKED","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"cae9c9b84a3ed5799ad1a24518510a4c1252b88c4128a9bbd76e6fb4d14ff8a5","event_type":"reconcile","event_version":1,"open_decisions":["逐軸或向量模式、資料來源、前處理接入、碰撞檢出時限與無解診斷候選規則需釐清。","Q-003@6"],"previous_event_hash":"9323c6d133b2e591e6bb912fb689731b5843ef9cf944ab6f694dcb12484c63c3","previous_snapshot_hash":"56f3f655e48e0df330706c6f634471c711e1f24d9237302e107f985fc589327e","recorded_at":"2026-11-03T10:33:31.313006+00:00","relationships":[],"revision":6,"snapshot_hash":"522851273fc24d60eb9223f401a751f6d4247dcc255a51101038b8889a9b22ce","verdict":"BLOCKED","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":6,"snapshot_hash":"522851273fc24d60eb9223f401a751f6d4247dcc255a51101038b8889a9b22ce","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"},"candidates":[],"completeness_review":null,"identified_items":{"I-005":{"id":"I-005","kind":"accepted","source_ref":"user:yes-shared-threshold","text":"使用者回答是，同意所有已匯入的 Recording／Offset／Speed 共用一個 threshold。"},"I-006":{"id":"I-006","kind":"fact","source_ref":"code:LearningService.COLLISION_DETECTION_WINDOW_MS","text":"目前 Studio 的碰撞檢出窗為 150 ms，從標註起點計算且包含邊界。"},"I-007":{"id":"I-007","kind":"candidate","source_ref":"assistant:original-deadline","text":"建議 Original 沿用現有 150 ms 碰撞檢出窗，超時算漏報；尚未採納。"}},"item_bindings":{"I-005":["REQ-004","DEC-004","AC-004"],"I-006":[],"I-007":[]},"kind":"saved","reply_sha256":"998ad32fec007107e679f64b595b691f226b0e473c0aff0e6205f0426e48dbf4","reply_stage":"prepared-until-host-stop","reviewed_sources":["assistant:original-deadline","code:LearningService.COLLISION_DETECTION_WINDOW_MS","user:yes-shared-threshold"],"source_ref":"user:yes-shared-threshold","summary":"Q-002 已回答是；新增 REQ-004、DEC-004、AC-004、DISC-003，關係無變更且無衝突；全部工況共用 threshold。規格因其餘未決事項仍為 BLOCKED，下一問確認 150 ms 檢出時限。未取得產品執行授權。","task_ref":"01a1a0e6-b944-7920-ba7c-5ab8a7ebffb4","turn_id":"user-yes-shared-threshold"},"removed_ids":[]},"epoch":"cc1bdd0df9fb412199b8ced35bd1c0e4","event_hash":"19c7869e4e24d34fba0eb3913febbfa1d81632e629fb42b8ff27987209c75a28","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"cae9c9b84a3ed5799ad1a24518510a4c1252b88c4128a9bbd76e6fb4d14ff8a5","previous_snapshot_hash":"522851273fc24d60eb9223f401a751f6d4247dcc255a51101038b8889a9b22ce","recorded_at":"2026-11-03T10:33:36.710670+00:00","relationships":[],"revision":6,"snapshot_hash":"522851273fc24d60eb9223f401a751f6d4247dcc255a51101038b8889a9b22ce","verdict":"PASS","working_id":"WORKING-SPEC-b504291d66da-original-threshold-collision-replay"}
```
<!-- spec-audit:end -->
