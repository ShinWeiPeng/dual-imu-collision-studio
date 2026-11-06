---
spec_version: 1
spec_id: SPEC-0054
revision: 7
status: confirmed
change_set: annotation-lane-fixed-time-axis
working_id: WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis
task_ref: 01a1ae9d-c179-7010-b682-879af77600dc
---
# 下方事件窗格拖曳換類型與固定時間軸

## Problem

使用者要在下方事件窗格拖曳既有事件，直接變更事件的類型，同時維持目前的時間軸。既有窗格的事件本體拖曳只處理時間位置，缺少拖到另一列換類型的操作。

## Solution

在下方窗格的 Select / Edit 模式，把事件從原本的類型列拖到目標類型列，放開後套用該列的類型。例如把 Pick 拖到 Put 列，原事件變成 Put，保留同一個事件 ID 與起訖樣本。拖曳期間及放開後，共用時間軸的起點和終點都維持原值。

可換類型的事件列為 Pick、Put、Fork Collision 和 Ignore。改為 Ignore 時沿用必填原因的對話框，確認原因才提交。由 Ignore 改為其他類型時清除 Ignore 原因。Cycle 是區段容器，Normal Robot Motion 是唯讀衍生列，兩者均排除在換類型操作之外。放到無效目標或取消時保留原事件。

## User Stories

| ID | Story |
| --- | --- |
| US-001 | 我可以把下方事件窗格的既有事件拖到另一個類型列，直接改分類並保留事件時間。 |

## Requirements

| ID | Requirement | Source |
| --- | --- | --- |
| REQ-001 | 下方事件窗格的拖曳及滾輪操作維持共用時間軸的起點與終點。 | user:annotation-lane-fixed-time-axis |
| REQ-002 | 在 Select / Edit 中，將下方窗格的既有事件本體拖到另一個可換類型的事件列時，放開後將該事件改為目標類型。保留事件 ID、起點與終點，以一次可復原或重做的編輯提交。 | user:annotation-lane-relabel-by-drag |
| REQ-003 | 換類型只適用於 Pick、Put、Fork Collision 和 Ignore。改為 Ignore 需確認非空原因，改離 Ignore 時清除原因。放到無效目標或取消換類型時保留原事件。 | derived from event kinds and Ignore reason validation |

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| DEC-001 | 事件窗格沿用共用時間軸，並將本體平移與端點調整分開。 | user:annotation-lane-fixed-time-axis |
| DEC-002 | 下方窗格須保留已選取短事件的本體拖移和端點調整。 | user:annotation-lane-fixed-time-axis |
| DEC-003 | 下方窗格的主要修改是拖曳編輯事件，並以時間軸起訖在拖曳中保持固定為驗收條件。 | user:annotation-lane-drag-scope-clarification |
| DEC-004 | 本次主要修改是將既有事件拖到另一列以變更事件類型，並保留事件起訖與時間軸。 | user:annotation-lane-relabel-by-drag |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
| --- | --- | --- | --- | --- |
| AC-001 | REQ-001 | 在放大後的視圖拖曳窗格空白處、拖曳事件或使用滾輪，共用時間軸的起點與終點維持原值。 | Qt 滑鼠和滾輪事件 | Pending |
| AC-002 | REQ-001, REQ-002 | 把 Pick 拖到 Put 列放開後，只出現一個同 ID、同起訖樣本的 Put。時間軸範圍維持原值。Undo 還原 Pick，Redo 恢復 Put。 | Qt 滑鼠事件和 controller 的類型、ID、樣本範圍及時間軸 | Pending |
| AC-003 | REQ-003 | 改為 Ignore 時，輸入有效原因並確認才提交，取消則保留原事件。由 Ignore 改為 Pick 時清除原因。拖到 Cycle 或 Normal Robot Motion 不會變更事件。 | Qt 拖放、原因對話框與 controller 狀態 | Pending |

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
    "rationale": "用生產 Qt Quick 控制項在已放大的視野測試拖曳與滾輪，讀取時間軸起訖值。此互動無硬體或執行效能驗收。"
  },
  "AC-002": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "從生產 Qt 事件列操作跨列拖放，再核對控制器公開投影的類型、ID、樣本起訖與復原和重做。"
  },
  "AC-003": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "error-reset"
    ],
    "execution_changes": [],
    "rationale": "用生產 Qt 事件列和原因對話框驗證必填、確認、取消及無效目標，並核對控制器結果。"
  }
}
```

## Relationships

| Source | Relation | Target |
| --- | --- | --- |
| DEC-004 | supersedes | DEC-002 |
| DEC-004 | refines | DEC-003 |

## Out of Scope

波形窗格的平移與縮放、確認標記規則、Normal Robot Motion 的衍生方式，以及同列平移或端點縮放的互動修正。

## Open Decisions

None.

## Routing/Gates

實作範圍為下方 QML 事件列的跨列拖放、標記編輯命令與聚焦的互動驗證。修改拖曳回呼或事件狀態前依 AGENTS.md 完成架構預檢。

## Revision History

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-11-06 | 記錄使用者要求與驗收行為。 |
| 5 | 2026-11-06 | 依使用者更正，將主要修改改為跨列拖曳換事件類型。 |

## Discussion Context

來源為 user:annotation-lane-fixed-time-axis。前一輪以 Qt 重現 5 像素寬的已選取標記中間只會收到端點拖曳。下方空白處拖曳維持 viewport。

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

- user:annotation-lane-fixed-time-axis: 下方事件窗格，不能平移整個時間軸、也不可以調整時間軸。新增可以將事件透過拖拉變更事件，但時間軸要維持相同。
- user:annotation-lane-fixed-time-axis: 依使用者要求建立 SPEC-0054，固定下方窗格的共用時間軸，區分事件本體平移和端點編輯。
- user:annotation-lane-drag-scope-clarification: 我的主要修改內容是拖曳下方事件窗格時，可以透過拖曳變更事件。以及下方事件窗格無法透過拖曳變更時間軸。
- user:annotation-lane-drag-scope-clarification: 使用者釐清主要修改是從下方窗格拖曳編輯事件，拖曳期間時間軸固定。以 DEC-003 保存，對應 REQ-001、REQ-002、AC-001、AC-002。
- user:annotation-lane-relabel-by-drag: 你誤會我的意思了。我要的是拖曳下方事件窗格時，可以透過拖曳變更事件類型。
- user:annotation-lane-relabel-by-drag: 使用者更正主要需求為跨列拖曳既有事件換類型。新規格保留原事件時間與共用時間軸，依事件列與 Ignore 原因規則處理放開。
- user:01a1aec9-9552-7502-aabb-0cd789669a52: 了解。開始執行
- user:01a1aec9-9552-7502-aabb-0cd789669a52: SPEC-0054 已確認。使用者已在本次訊息要求開始執行跨列換事件類型及固定時間軸。現正檢查驗收與架構門檻。
- user:01a1aec9-9552-7502-aabb-0cd789669a52: Implement confirmed SPEC-0054: relabel an existing annotation by dragging it to another event lane without changing samples or the viewport. User execution message: 了解。開始執行
- user:01a1aec9-9552-7502-aabb-0cd789669a52: SPEC-0054 已確認，使用者本輪已授權實作。以跨列滑鼠拖曳換類型，保留事件樣本起訖與畫面時間軸。規劃及架構設計閘門已通過。
- user:01a1aec9-9552-7502-aabb-0cd789669a52: 實作已寫入工作區。Qt 與標記回歸共 58 passed，架構開發 gate exit 0，Ruff 檢查通過。全專案 layout exit 1，既有 600 筆診斷且無本 SPEC 診斷。

### Source and Revision Audit

```jsonl
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"2f507fc3c1790c96dd5e79158636869b8d7d881782625bfae79fa02c2f5f08fd","event_type":"start","event_version":1,"open_decisions":[],"previous_event_hash":null,"previous_snapshot_hash":null,"recorded_at":"2026-11-06T02:24:01.882583+00:00","relationships":[],"revision":1,"snapshot_hash":"c55791f92b830668cf866ac39d8d9eef890a1789b8a470e8cdfbe4cf6faa4390","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"下方事件窗格，不能平移整個時間軸、也不可以調整時間軸。新增可以將事件透過拖拉變更事件，但時間軸要維持相同。","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:annotation-lane-fixed-time-axis","task_ref":"01a1ae9d-c179-7010-b682-879af77600dc","turn_id":"annotation-lane-fixed-time-axis"},"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"151e360e38bffabc5d05095e6ac659dc7d2d20f74ad5288698377e605375c551","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"2f507fc3c1790c96dd5e79158636869b8d7d881782625bfae79fa02c2f5f08fd","previous_snapshot_hash":"c55791f92b830668cf866ac39d8d9eef890a1789b8a470e8cdfbe4cf6faa4390","recorded_at":"2026-11-06T02:24:46.222413+00:00","relationships":[],"revision":1,"snapshot_hash":"c55791f92b830668cf866ac39d8d9eef890a1789b8a470e8cdfbe4cf6faa4390","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":["AC-001","AC-002"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":["AC-001","AC-002"],"added_ids":[],"changed_ids":["AC-001","AC-002"],"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"6adba95d4b8fc326b3998452a96c865bd9d7e4ff8bb2616e1acbeac229d9366f","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"151e360e38bffabc5d05095e6ac659dc7d2d20f74ad5288698377e605375c551","previous_snapshot_hash":"c55791f92b830668cf866ac39d8d9eef890a1789b8a470e8cdfbe4cf6faa4390","recorded_at":"2026-11-06T02:26:30.379858+00:00","relationships":[],"revision":2,"snapshot_hash":"267e584b5f61f6e423764f11b4afa54494d84b19f979e5542ffe76c00420d0bb","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":["DEC-002"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["DEC-002"],"changed_ids":[],"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"505df8db12025da4446fa79b8c1ace0e18ed40716b05964ecf3107123f9558b8","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"6adba95d4b8fc326b3998452a96c865bd9d7e4ff8bb2616e1acbeac229d9366f","previous_snapshot_hash":"267e584b5f61f6e423764f11b4afa54494d84b19f979e5542ffe76c00420d0bb","recorded_at":"2026-11-06T02:28:42.557533+00:00","relationships":[],"revision":3,"snapshot_hash":"3620fa58063c77c366950a8b5857a8f6637b0125b8fb1b7f6150636fd73b603e","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":3,"snapshot_hash":"3620fa58063c77c366950a8b5857a8f6637b0125b8fb1b7f6150636fd73b603e","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"},"candidates":[],"completeness_review":null,"identified_items":{"LANE-AXIS":{"id":"LANE-AXIS","kind":"accepted","source_ref":"user:annotation-lane-fixed-time-axis","text":"下方事件窗格內的拖曳與滾輪維持時間軸的起點及終點。"},"LANE-DRAG":{"id":"LANE-DRAG","kind":"accepted","source_ref":"user:annotation-lane-fixed-time-axis","text":"下方事件窗格可拖曳編輯事件，事件本體平移與端點調整應可操作，已選取的短事件也可拖移。"}},"item_bindings":{"LANE-AXIS":["REQ-001","DEC-001","AC-001"],"LANE-DRAG":["REQ-002","DEC-002","AC-002"]},"kind":"saved","reply_sha256":"a870abcdb5b42569ae169dd5d69a80ad102696593d4e9b79bd50e4b738c818dd","reply_stage":"prepared-until-host-stop","reviewed_sources":["user:annotation-lane-fixed-time-axis"],"source_ref":"user:annotation-lane-fixed-time-axis","summary":"依使用者要求建立 SPEC-0054，固定下方窗格的共用時間軸，區分事件本體平移和端點編輯。","task_ref":"01a1ae9d-c179-7010-b682-879af77600dc","turn_id":"annotation-lane-fixed-time-axis"},"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"50b2f1ba81217e32f0a6bb3a650e9afb5395b5473b145936f82f0d3e11b13e5a","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"505df8db12025da4446fa79b8c1ace0e18ed40716b05964ecf3107123f9558b8","previous_snapshot_hash":"3620fa58063c77c366950a8b5857a8f6637b0125b8fb1b7f6150636fd73b603e","recorded_at":"2026-11-06T02:28:49.859407+00:00","relationships":[],"revision":3,"snapshot_hash":"3620fa58063c77c366950a8b5857a8f6637b0125b8fb1b7f6150636fd73b603e","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"我的主要修改內容是拖曳下方事件窗格時，可以透過拖曳變更事件。以及下方事件窗格無法透過拖曳變更時間軸。","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:annotation-lane-drag-scope-clarification","task_ref":"01a1ae9d-c179-7010-b682-879af77600dc","turn_id":"annotation-lane-drag-scope-clarification"},"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"c4ea3aca3c42cc07b38b818e926e626c1b626334cfb7fb0be85e3f3a67b0be00","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"50b2f1ba81217e32f0a6bb3a650e9afb5395b5473b145936f82f0d3e11b13e5a","previous_snapshot_hash":"3620fa58063c77c366950a8b5857a8f6637b0125b8fb1b7f6150636fd73b603e","recorded_at":"2026-11-06T02:41:29.322197+00:00","relationships":[],"revision":3,"snapshot_hash":"3620fa58063c77c366950a8b5857a8f6637b0125b8fb1b7f6150636fd73b603e","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":["DEC-003"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["DEC-003"],"changed_ids":[],"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"4e74e7d320c420f20942db8a7a15b168bd6e3f6662c32c7b7fdcc39a8c702a04","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"c4ea3aca3c42cc07b38b818e926e626c1b626334cfb7fb0be85e3f3a67b0be00","previous_snapshot_hash":"3620fa58063c77c366950a8b5857a8f6637b0125b8fb1b7f6150636fd73b603e","recorded_at":"2026-11-06T02:42:18.892888+00:00","relationships":[],"revision":4,"snapshot_hash":"926bf8b6265172561ed1cdabc7982e68ac6d7730d9091f4ce7c28f40590cd7d7","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":4,"snapshot_hash":"926bf8b6265172561ed1cdabc7982e68ac6d7730d9091f4ce7c28f40590cd7d7","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"},"candidates":[],"completeness_review":null,"identified_items":{"LANE-PRIMARY-DRAG":{"id":"LANE-PRIMARY-DRAG","kind":"accepted","source_ref":"user:annotation-lane-drag-scope-clarification","text":"主要修改是讓使用者在下方窗格拖曳可編輯事件。下方窗格的拖曳要維持時間軸起訖。"}},"item_bindings":{"LANE-PRIMARY-DRAG":["DEC-003","REQ-001","REQ-002","AC-001","AC-002"]},"kind":"saved","reply_sha256":"b6b4ac1f11e92ffba84c04ca6d35fcaa37999de1bceedc0d15675092ab41d032","reply_stage":"prepared-until-host-stop","reviewed_sources":["user:annotation-lane-drag-scope-clarification"],"source_ref":"user:annotation-lane-drag-scope-clarification","summary":"使用者釐清主要修改是從下方窗格拖曳編輯事件，拖曳期間時間軸固定。以 DEC-003 保存，對應 REQ-001、REQ-002、AC-001、AC-002。","task_ref":"01a1ae9d-c179-7010-b682-879af77600dc","turn_id":"annotation-lane-drag-scope-clarification"},"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"fdcfd2dd450d305150c72f4e1eb3452fb270eb2986194f13da09f7f0cdd6b5b2","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"4e74e7d320c420f20942db8a7a15b168bd6e3f6662c32c7b7fdcc39a8c702a04","previous_snapshot_hash":"926bf8b6265172561ed1cdabc7982e68ac6d7730d9091f4ce7c28f40590cd7d7","recorded_at":"2026-11-06T02:43:03.346030+00:00","relationships":[],"revision":4,"snapshot_hash":"926bf8b6265172561ed1cdabc7982e68ac6d7730d9091f4ce7c28f40590cd7d7","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"你誤會我的意思了。我要的是拖曳下方事件窗格時，可以透過拖曳變更事件類型。","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:annotation-lane-relabel-by-drag","task_ref":"01a1ae9d-c179-7010-b682-879af77600dc","turn_id":"annotation-lane-relabel-by-drag"},"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"06196c3855a25e5a13df57138c32fb7b07af227c7c9f66235ddf7e0c2db4085e","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"fdcfd2dd450d305150c72f4e1eb3452fb270eb2986194f13da09f7f0cdd6b5b2","previous_snapshot_hash":"926bf8b6265172561ed1cdabc7982e68ac6d7730d9091f4ce7c28f40590cd7d7","recorded_at":"2026-11-06T02:47:02.885842+00:00","relationships":[],"revision":4,"snapshot_hash":"926bf8b6265172561ed1cdabc7982e68ac6d7730d9091f4ce7c28f40590cd7d7","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":["AC-002","AC-003","DEC-004","REQ-002","REQ-003"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":["AC-002"],"added_ids":["AC-003","DEC-004","REQ-003"],"changed_ids":["AC-002","REQ-002"],"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"6fa98304aa5f63b2ddfd412ac15c877cb20f8fdcaa361973cefcec375cc17e4b","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"06196c3855a25e5a13df57138c32fb7b07af227c7c9f66235ddf7e0c2db4085e","previous_snapshot_hash":"926bf8b6265172561ed1cdabc7982e68ac6d7730d9091f4ce7c28f40590cd7d7","recorded_at":"2026-11-06T02:49:02.314357+00:00","relationships":[{"relation":"supersedes","source":"","target":""},{"relation":"refines","source":"","target":""}],"revision":5,"snapshot_hash":"a204634dc7ca08f886d514350d01cfb6fac61cdc35c0678c5bc544f07324b853","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"c3b2eee02292d8e4187a8837f6b73e27a879154de0adee52ee08742ed3efc3fb","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"6fa98304aa5f63b2ddfd412ac15c877cb20f8fdcaa361973cefcec375cc17e4b","previous_snapshot_hash":"a204634dc7ca08f886d514350d01cfb6fac61cdc35c0678c5bc544f07324b853","recorded_at":"2026-11-06T02:50:18.369907+00:00","relationships":[{"relation":"supersedes","source":"DEC-004","target":"DEC-002"},{"relation":"refines","source":"DEC-004","target":"DEC-003"}],"revision":6,"snapshot_hash":"7910f3f34a9241093eb2adf1ac020785c16a318f6b50f6f5f082491a09802a65","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":6,"snapshot_hash":"7910f3f34a9241093eb2adf1ac020785c16a318f6b50f6f5f082491a09802a65","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"},"candidates":[],"completeness_review":null,"identified_items":{"LANE-RELABEL":{"id":"LANE-RELABEL","kind":"accepted","source_ref":"user:annotation-lane-relabel-by-drag","text":"主要修改是拖曳下方事件窗格的既有事件以變更事件類型。"}},"item_bindings":{"LANE-RELABEL":["DEC-004","REQ-001","REQ-002","REQ-003","AC-001","AC-002","AC-003"]},"kind":"saved","reply_sha256":"0918039977dee441c7dbb0563bc6bad3cea78ad2ff88682ac0f9b9a07efd90c4","reply_stage":"prepared-until-host-stop","reviewed_sources":["user:annotation-lane-relabel-by-drag"],"source_ref":"user:annotation-lane-relabel-by-drag","summary":"使用者更正主要需求為跨列拖曳既有事件換類型。新規格保留原事件時間與共用時間軸，依事件列與 Ignore 原因規則處理放開。","task_ref":"01a1ae9d-c179-7010-b682-879af77600dc","turn_id":"annotation-lane-relabel-by-drag"},"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"481d965a75c8f1f2c395da548ac033958ab4d878ba4af4c224eff284e924236e","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"c3b2eee02292d8e4187a8837f6b73e27a879154de0adee52ee08742ed3efc3fb","previous_snapshot_hash":"7910f3f34a9241093eb2adf1ac020785c16a318f6b50f6f5f082491a09802a65","recorded_at":"2026-11-06T02:50:24.594664+00:00","relationships":[],"revision":6,"snapshot_hash":"7910f3f34a9241093eb2adf1ac020785c16a318f6b50f6f5f082491a09802a65","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"了解。開始執行","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:01a1aec9-9552-7502-aabb-0cd789669a52","task_ref":"01a1ae9d-c179-7010-b682-879af77600dc","turn_id":"01a1aec9-94e7-75e1-afc1-043fe5776220"},"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"0a8a5a9a41251edb3d8db025af2fadb18eb3c5ea335a3eb45cce654c67b2455a","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"481d965a75c8f1f2c395da548ac033958ab4d878ba4af4c224eff284e924236e","previous_snapshot_hash":"7910f3f34a9241093eb2adf1ac020785c16a318f6b50f6f5f082491a09802a65","recorded_at":"2026-11-06T02:58:36.066596+00:00","relationships":[],"revision":6,"snapshot_hash":"7910f3f34a9241093eb2adf1ac020785c16a318f6b50f6f5f082491a09802a65","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"516437c8149b66827f61c80edd334b9f2591585dc9363e138d2ffcdf860ab5ac","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"0a8a5a9a41251edb3d8db025af2fadb18eb3c5ea335a3eb45cce654c67b2455a","previous_snapshot_hash":"7910f3f34a9241093eb2adf1ac020785c16a318f6b50f6f5f082491a09802a65","recorded_at":"2026-11-06T02:59:53.317084+00:00","relationships":[{"relation":"supersedes","source":"DEC-004","target":"DEC-002"},{"relation":"refines","source":"DEC-004","target":"DEC-003"}],"revision":7,"snapshot_hash":"6308ef3b74d7247f15c4c41525aaa11d076cc771d9fe8255a77c9f76bcef66da","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"83b5fb2d87ac8743ebaeb8f1b2d3731eb87121fb7fa8af2b185520563fc0763c","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"516437c8149b66827f61c80edd334b9f2591585dc9363e138d2ffcdf860ab5ac","previous_snapshot_hash":"6308ef3b74d7247f15c4c41525aaa11d076cc771d9fe8255a77c9f76bcef66da","recorded_at":"2026-11-06T03:00:35.128774+00:00","relationships":[],"revision":7,"snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":7,"snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"cb2ece05d22b2f6d4e2561c9405e196e5f402b9c7e27185c9ebd946482c32b22","reply_stage":"prepared-until-host-stop","reviewed_sources":["user:01a1aec9-9552-7502-aabb-0cd789669a52"],"source_ref":"user:01a1aec9-9552-7502-aabb-0cd789669a52","summary":"SPEC-0054 已確認。使用者已在本次訊息要求開始執行跨列換事件類型及固定時間軸。現正檢查驗收與架構門檻。","task_ref":"01a1ae9d-c179-7010-b682-879af77600dc","turn_id":"01a1aec9-94e7-75e1-afc1-043fe5776220"},"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"809ae129a74aadee80e5030804e8862a81677c99f0636f59dd42e87d04b7a894","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"83b5fb2d87ac8743ebaeb8f1b2d3731eb87121fb7fa8af2b185520563fc0763c","previous_snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","recorded_at":"2026-11-06T03:03:03.450138+00:00","relationships":[],"revision":7,"snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"Implement confirmed SPEC-0054: relabel an existing annotation by dragging it to another event lane without changing samples or the viewport. User execution message: 了解。開始執行","kind":"entry-update","source_ref":"user:01a1aec9-9552-7502-aabb-0cd789669a52","task_ref":"01a1ae9d-c179-7010-b682-879af77600dc","turn_id":"01a1aec9-94e7-75e1-afc1-043fe5776220"},"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"719f04268a9586f255335f541307280e2f69a2ceed901e04b23317d93bd9a689","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"809ae129a74aadee80e5030804e8862a81677c99f0636f59dd42e87d04b7a894","previous_snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","recorded_at":"2026-11-06T03:19:43.918579+00:00","relationships":[],"revision":7,"snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":7,"snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"c1f353f59fdc316985bceb93b0e272cc34ead0c5caf219a49021fa097ff39beb","reply_stage":"prepared-until-host-stop","reviewed_sources":["user:01a1aec9-9552-7502-aabb-0cd789669a52"],"source_ref":"user:01a1aec9-9552-7502-aabb-0cd789669a52","summary":"SPEC-0054 已確認，使用者本輪已授權實作。以跨列滑鼠拖曳換類型，保留事件樣本起訖與畫面時間軸。規劃及架構設計閘門已通過。","task_ref":"01a1ae9d-c179-7010-b682-879af77600dc","turn_id":"01a1aec9-94e7-75e1-afc1-043fe5776220"},"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"f2999adf4d1120561664d7ee40c9d7ecd68b8f13ccf08f4b2a706379badfa745","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"719f04268a9586f255335f541307280e2f69a2ceed901e04b23317d93bd9a689","previous_snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","recorded_at":"2026-11-06T03:23:21.592790+00:00","relationships":[],"revision":7,"snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":7,"snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"},"candidates":[],"completeness_review":null,"identified_items":{},"item_bindings":{},"kind":"saved","reply_sha256":"84646a3d41eecfc5301e1ef3c17e8429e26db82beda280d1978e1e88bf86cdb5","reply_stage":"prepared-until-host-stop","reviewed_sources":["user:01a1aec9-9552-7502-aabb-0cd789669a52"],"source_ref":"user:01a1aec9-9552-7502-aabb-0cd789669a52","summary":"實作已寫入工作區。Qt 與標記回歸共 58 passed，架構開發 gate exit 0，Ruff 檢查通過。全專案 layout exit 1，既有 600 筆診斷且無本 SPEC 診斷。","task_ref":"01a1ae9d-c179-7010-b682-879af77600dc","turn_id":"01a1aec9-94e7-75e1-afc1-043fe5776220"},"removed_ids":[]},"epoch":"24c9ff00d3e54f2c876c3853318bcd3f","event_hash":"c153e5985975b79e8ef481ee1d235566ecd062becac8c2bbf25a9176dc3150c7","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"f2999adf4d1120561664d7ee40c9d7ecd68b8f13ccf08f4b2a706379badfa745","previous_snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","recorded_at":"2026-11-06T03:28:35.645464+00:00","relationships":[],"revision":7,"snapshot_hash":"8b42e4e0fddbaa7cd471597fde6555816e7bc14af28db6167ed35b7460d2a412","verdict":"PASS","working_id":"WORKING-SPEC-2755ff7ef423-annotation-lane-fixed-time-axis"}
```
<!-- spec-audit:end -->
