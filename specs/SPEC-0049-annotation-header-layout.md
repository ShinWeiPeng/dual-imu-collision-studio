---
spec_version: 1
spec_id: SPEC-0049
revision: 2
status: confirmed
change_set: annotation-header-layout
working_id: WORKING-SPEC-01a1856a7a54-annotation-header-layout
task_ref: annotation-header-layout-20261030
---
# 標註頁首配置收合

2026-10-30：使用者採用修正後的概念圖。範圍為 Annotate & Classify 頁首佈局；採用圖稿不代表產品已修改或已完成實機驗收。

## Problem

三個標註管理按鈕目前是頁首中的獨立 Flow 列，出現在左側標題下。第一版概念圖雖把按鈕搬到右上 Recording 下方，仍保留原按鈕列的高度，導致左側出現空白斷差。使用者明確要求移走後下方內容往上移，並採用移除佔位的修正版圖稿。

## Solution

頁首使用左右兩個內容區：左側依序排標題、說明、Reference、Recording 進度與統計；右側 Recording 標籤/選擇器的下方放三個管理按鈕，整組靠右。移除獨立的舊管理按鈕列及其空白佔位。頁首高度由兩側實際內容決定，標記工具列、IMU 選擇與波形區依其高度向上收合；不以負位移、覆蓋或保留空列模擬。保留既有窄視窗的內容適應與實際可見進度需求，不把固定上移像素當契約。

採用圖稿：[採用概念圖](../docs/images/annotation-header-layout-adopted-20261030.png)。僅為配置參照，波形外觀不作量測或驗收證據。

## User Stories

使用者在 Recording 區下方找到管理按鈕；移除左側按鈕列後，資訊與下方工具/波形緊接實際內容，增加可視波形空間。

## Requirements

| ID | Requirement | Source |
|---|---|---|
| REQ-001 | 將 Replace Reference（未建立參考時維持 Use as Reference）、Confirm All Annotation Sets、Export Annotated Data 三個既有按鈕置於頁首右側 Recording 標籤/錄波選擇區的正下方，依此前後順序，整組靠右；常用寬度下同列顯示，窄視窗沿既有內容適應原則保持可達且不重疊。 | user:20261030-compact-header-concept-adopt |
| REQ-002 | 移除管理按鈕在左側獨佔列的佔位；左側 Reference、Recording 進度與統計接在標題說明下，以一般內容間距連續排列，不保留原按鈕高度的空白列/固定 spacer。 | user:20261030-compact-header-concept-adopt |
| REQ-003 | 頁首按左右實際內容自然決定高度；下方標記工具列、IMU/訊號控制與所有波形區隨頁首收合而往上移，無遮蔽/重疊/裁切；實際顯示的警告或匯出進度仍納入必要高度，不硬壓成固定高度。 | user:20261030-compact-header-concept-adopt |
| REQ-004 | 本次只變更 QML 版面配置，保留錄波選擇、參考建立/替換、整組確認、確認後才能匯出、匯出中取消/進度、標記工具與波形互動的既有行為、啟用/可見條件、objectName 及事件處理；不改資料、格式、模型或其他功能契約。 | user:20261030-compact-header-concept-adopt |

## Decisions

| ID | Decision | Source |
|---|---|---|
| DEC-001 | 採用三個管理按鈕位於右側 Recording 正下方、由左至右依既有順序排列並靠右的概念圖。 | user:20261030-compact-header-concept-adopt |
| DEC-002 | 採用去除原按鈕列佔位的修正版：左側資訊與下方工具列、波形依實際內容自然向上收合，取代保留空白帶的第一版圖稿。 | user:20261030-compact-header-concept-adopt |
| DEC-003 | 此為 dual_imu_collision_studio 獨立版面變更，不將此處的採用套用到 E84 的 CRC/自動保存啟動資訊待決問題，也不挪用其他功能的執行授權。 | user:20261030-compact-header-concept-adopt |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | 常用寬度下三個管理按鈕在 Recording 區正下方同列靠右、順序正確，未建立參考時名稱仍正確；窄視窗內容可達且無重疊。 | 實作後在實際 Qt/QML 視窗以相同資料比較常用/最低支援寬度截圖與採用圖稿的配置關係。 | NOT RUN；概念圖僅表示設計採用。 |
| AC-002 | REQ-002, REQ-003 | Reference 等左側資訊緊接說明，沒有舊按鈕列的空白佔位；同視窗/同資料下標記工具列與波形隨頁首收合上移；可見警告/進度不被遮蔽。 | 實作後以相同 viewport 比較前後實際截圖並檢查內容邊界及進度可見時的排列。 | NOT RUN |
| AC-003 | REQ-004 | 錄波選擇、既有按鈕 guard/handler/objectName、標記與波形互動維持；未確認不可匯出，匯出中的取消/進度仍可用；不改相關資料格式或來源。 | 實作 diff review、既有 QML smoke 的相關情境及受控資料上的必要互動冒煙檢查；不另建立重複實作的版面單元測試。 | NOT RUN |

## Acceptance Mapping

```json
{
  "AC-001": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Qt/QML桌面配置與既有控制接線，以實際視窗幾何/截圖比較及必要冒煙檢查驗證；概念圖、文件與計畫完整不代表產品執行PASS，不宣稱硬體或效能驗證。"
  },
  "AC-002": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Qt/QML桌面配置與既有控制接線，以實際視窗幾何/截圖比較及必要冒煙檢查驗證；概念圖、文件與計畫完整不代表產品執行PASS，不宣稱硬體或效能驗證。"
  },
  "AC-003": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Qt/QML桌面配置與既有控制接線，以實際視窗幾何/截圖比較及必要冒煙檢查驗證；概念圖、文件與計畫完整不代表產品執行PASS，不宣稱硬體或效能驗證。"
  }
}
```

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-003 | depends_on | REQ-002 |
| REQ-001 | depends_on | REQ-004 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |
| AC-002 | depends_on | REQ-003 |
| AC-003 | depends_on | REQ-004 |

## Out of Scope

匯出格式/准入政策更動、演算法/模型/訓練、資料重寫、E84 韌體規格、其他頁面重構、產品實作或執行授權、Git 操作。當前僅保存採用配置與驗收計畫。

## Open Decisions

None.

## Routing/Gates

ask-matt/spec-governance 管理本獨立配置討論。初次路由發現多份既有 confirmed SPEC，需要本變更的明確 reference；以新 annotation-header-layout 工作規格解除選取歧義，不覆寫其他功能契約。產品執行前仍須依專案現行政策完成適用 formatter/architecture/validation 准入；概念圖採用與計畫完整不表示產品或執行 gate 通過。

## Revision History

| Revision | Change | Source |
|---|---|---|
| 1 | 依使用者採用的緊密配置概念圖建立獨立 UI 規格；保存按鈕位置、原列收合與下方上移要求，產品未修改、驗收未執行。 | user:20261030-compact-header-concept-adopt |

## Discussion Context

### DISC-001: 採用移除空白佔位的概念圖

- **Situation:** 使用者指出按鈕應在 Recording 下方；初版移動按鈕後仍留左側空白，使用者要求下方上移，已產出修正版圖稿。
- **Question:** 是否採用修正後三按鈕靠右、左側及下方自然收合的概念配置。
- **Options and tradeoffs:** 第一版保留原列高度造成浪費；修正版移除舊列佔位、兩側獨立按內容排版並回收垂直空間。這是同一配置的修正，不新增功能。
- **User answer:** 採用。
- **Explicit rationale:** 使用者前一回合明示「我想法是下方會往上移」；採用回覆未另給理由。
- **Resulting impact:** 採用修正版，形成 REQ-001 至 REQ-004、DEC-001 至 DEC-003 與 AC-001 至 AC-003；只保存配置決策，不視為產品已修改。
- **Source:** user:20261030-compact-header-concept-adopt；user:20261030-compact-header-gap-feedback；採用圖稿 exec-ad0bd91c-d14f-4c85-93bb-26b69d37ef28.png。

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

- user:20261030-compact-header-concept-adopt: 採用
- C:\Users\hugo_peng\AppData\Local\Temp\annotation-header-layout-adopt-20261030\reply.md: 在正確dual_imu_collision_studio建立獨立SPEC0049，保存使用者採用去除空白佔位的配置，不誤套E84仍待決的Q272。REQ001-004/DEC001-003/AC001-003與採用圖對齊，保留原接線/guard及匯出進度取消。附圖已原樣保存專案內，原生成檔保留；文件與Mapping完成不代表產品驗證。使用者對修正版概念圖明確採用，本輪提供五面向完整性審查與實際使用者來源，確認既定配置，不另問相同問題；無產品/OD/Git/訓練或執行授權。
- user:01a18aa6-897c-7680-9ea8-7b58b8c741d8: 開始執行
- assistant:msg_09dbee89b81a700b016ae401b140bc8191a085bc68959c3df1: 觀察到本輪實際使用者開始執行指令，對應SPEC0049 revision2；契約未變、產品准入由managed authorize另核對。保留既有dirty變更，只調整QML頁首。
- C:\Users\hugo_peng\AppData\Local\Temp\spec0049-execute-20261030\reply-final.md: 已依實際開始執行訊息完成SPEC0049版面：按鈕右置Recording下方、原列收合及下方上移；最小寬度原工具尾端裁切以Flow/implicitHeight處理，屬原不裁切/適應要求。原handler/guard/objectName及頁首/工具列外Main內容逐一核對不變。最終7項QML smoke/48項受控幾何/非寫入qmlformat/development架構檢查PASS，raw/圖片及來源雜湊保存在固定run。匯出中僅顯示狀態測試，未真實匯出或改使用者資料。驗收投影由owner產生並managed apply，規格需求/修訂不變，授權沿同snapshot有效。全專案既有LAY002等診斷仍未通過，未宣稱完整驗收/Release或改implemented；不擴大處理其他dirty工作。

### Source and Revision Audit

```jsonl
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"083763cac0404db6a7ce42796f8d0f83","event_hash":"1a8cd9084172ea137b65fd7a82faf02d3aa29d6085bd41fd15ef05f6aa694f21","event_type":"start","event_version":1,"open_decisions":[],"previous_event_hash":null,"previous_snapshot_hash":null,"recorded_at":"2026-10-30T02:02:37.790509+00:00","relationships":[{"relation":"depends_on","source":"REQ-003","target":"REQ-002"},{"relation":"depends_on","source":"REQ-001","target":"REQ-004"},{"relation":"depends_on","source":"AC-001","target":"REQ-001"},{"relation":"depends_on","source":"AC-002","target":"REQ-002"},{"relation":"depends_on","source":"AC-002","target":"REQ-003"},{"relation":"depends_on","source":"AC-003","target":"REQ-004"}],"revision":1,"snapshot_hash":"c0ccfcc1429e2cdbee668fc1afc3a97e7a86a67aeeefe16cf7a89b8191a73ca2","verdict":"PASS","working_id":"WORKING-SPEC-01a1856a7a54-annotation-header-layout"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"採用","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:20261030-compact-header-concept-adopt","task_ref":"annotation-header-layout-20261030","turn_id":"20261030-compact-header-concept-adopt"},"removed_ids":[]},"epoch":"083763cac0404db6a7ce42796f8d0f83","event_hash":"1fdd2bae6045b97790bbaab85e0ca83e52a381a8a01a80e3ba406b0fa95f1c74","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"1a8cd9084172ea137b65fd7a82faf02d3aa29d6085bd41fd15ef05f6aa694f21","previous_snapshot_hash":"c0ccfcc1429e2cdbee668fc1afc3a97e7a86a67aeeefe16cf7a89b8191a73ca2","recorded_at":"2026-10-30T02:03:34.276096+00:00","relationships":[],"revision":1,"snapshot_hash":"c0ccfcc1429e2cdbee668fc1afc3a97e7a86a67aeeefe16cf7a89b8191a73ca2","verdict":"PASS","working_id":"WORKING-SPEC-01a1856a7a54-annotation-header-layout"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"083763cac0404db6a7ce42796f8d0f83","event_hash":"81893f96ee7cf6d7d1c6c1239eb3dfc49698b7f8fefa42785eccf678f6ecd1f5","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"1fdd2bae6045b97790bbaab85e0ca83e52a381a8a01a80e3ba406b0fa95f1c74","previous_snapshot_hash":"c0ccfcc1429e2cdbee668fc1afc3a97e7a86a67aeeefe16cf7a89b8191a73ca2","recorded_at":"2026-10-30T02:12:23.928798+00:00","relationships":[{"relation":"depends_on","source":"REQ-003","target":"REQ-002"},{"relation":"depends_on","source":"REQ-001","target":"REQ-004"},{"relation":"depends_on","source":"AC-001","target":"REQ-001"},{"relation":"depends_on","source":"AC-002","target":"REQ-002"},{"relation":"depends_on","source":"AC-002","target":"REQ-003"},{"relation":"depends_on","source":"AC-003","target":"REQ-004"}],"revision":2,"snapshot_hash":"23502695d4f180e22073f5f0f680fb15e22f0d3bf03fa02cd9c37048ec5c974a","verdict":"PASS","working_id":"WORKING-SPEC-01a1856a7a54-annotation-header-layout"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"083763cac0404db6a7ce42796f8d0f83","event_hash":"325d145ddf12c6e5ddd59ba5122d1f3232a5f3d69125495ab42a8fab6fbb031e","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"81893f96ee7cf6d7d1c6c1239eb3dfc49698b7f8fefa42785eccf678f6ecd1f5","previous_snapshot_hash":"23502695d4f180e22073f5f0f680fb15e22f0d3bf03fa02cd9c37048ec5c974a","recorded_at":"2026-10-30T02:15:04.373756+00:00","relationships":[],"revision":2,"snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","verdict":"PASS","working_id":"WORKING-SPEC-01a1856a7a54-annotation-header-layout"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":2,"snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","working_id":"WORKING-SPEC-01a1856a7a54-annotation-header-layout"},"candidates":[],"completeness_review":{"acceptance":{"evidence":"AC001至AC003以真實Qt/QML視窗同資料/同寬度前後比較、既有QML smoke相關情境及必要互動檢查驗證，Acceptance Mapping完整；產品均NOT RUN，圖稿不是runtime PASS。","source_ref":"specs/SPEC-0049-annotation-header-layout.md#acceptance-criteria"},"behavior":{"evidence":"REQ001至REQ003與採用圖一致：右側錄波下方三按鈕同列靠右，左側資訊緊接說明，下方工具和波形依實際高度收合；非固定像素平移。","source_ref":"docs/images/annotation-header-layout-adopted-20261030.png"},"exceptions":{"evidence":"REQ004保留enabled/visible/objectName/handler及匯出中Cancel/進度；窄視窗可達、可見警告/進度自然增加高度，不重疊或裁切。","source_ref":"src/dual_imu_collision_studio/qml/Main.qml:621-709"},"goal":{"evidence":"使用者採用已修正概念圖，目標為管理按鈕歸位Recording下方並回收舊列空白。","source_ref":"user:20261030-compact-header-concept-adopt"},"scope":{"evidence":"只調整QML頁首容器/管理按鈕位置/自然高度，保留控制接線，不動資料/模型/匯出格式/其他SPEC。","source_ref":"src/dual_imu_collision_studio/qml/Main.qml:621-709"}},"identified_items":{"compact-header-adopted-image":{"id":"compact-header-adopted-image","kind":"fact","source_ref":"docs/images/annotation-header-layout-adopted-20261030.png","text":"已將使用者採用的exec-ad0bd91c-d14f-4c85-93bb-26b69d37ef28.png原樣複製為專案內圖稿，SHA256 10e1cca2f6e6166f2497d58baf370a6692c8688d1d03bfc364544533f60756ea；原生成檔保留，圖稿不是實際產品驗證結果。"},"compact-header-concept-adoption":{"id":"compact-header-concept-adoption","kind":"accepted","source_ref":"user:20261030-compact-header-concept-adopt","text":"使用者原話「採用」，對應上一回合去除空白佔位的修正版概念圖：三個管理按鈕維持右側Recording下方、原按鈕列不留白，左側資訊及下方工具/波形依實際內容上移；此為版面採用，不是E84 CRC待決題或開始執行授權。"},"compact-header-existing-qml":{"id":"compact-header-existing-qml","kind":"fact","source_ref":"src/dual_imu_collision_studio/qml/Main.qml:621-709","text":"目前QML把SectionTitle/Recording放同一RowLayout，管理按鈕另為後續獨立Flow，再接Reference/Recording摘要/統計、工具列與波形Card；管理列有既有objectName、enabled/visible/handler與匯出中取消/進度，配置修改須保留。此回合未修改QML。"},"compact-header-gap-feedback":{"id":"compact-header-gap-feedback","kind":"fact","source_ref":"user:20261030-compact-header-gap-feedback","text":"前一回合使用者指出紅圈處移走後仍有斷差，明示「我想法是下方會往上移」。修正版已將資訊/工具/波形依實際內容收合。"}},"item_bindings":{"compact-header-adopted-image":["DEC-001","DEC-002"],"compact-header-concept-adoption":["DEC-001","DEC-002","REQ-001","REQ-002","REQ-003","REQ-004","AC-001","AC-002","AC-003"],"compact-header-existing-qml":["REQ-001","REQ-004"],"compact-header-gap-feedback":["DEC-002","REQ-002","REQ-003"]},"kind":"saved","reply_sha256":"38623c0a45e480320facfdf4dc2d64beab0ea3fc4efa8439b48ef6fe37eec221","reply_stage":"prepared-until-host-stop","reviewed_sources":["docs/images/annotation-header-layout-adopted-20261030.png","src/dual_imu_collision_studio/qml/Main.qml:621-709","user:20261030-compact-header-concept-adopt","user:20261030-compact-header-gap-feedback"],"source_ref":"C:\\Users\\hugo_peng\\AppData\\Local\\Temp\\annotation-header-layout-adopt-20261030\\reply.md","summary":"在正確dual_imu_collision_studio建立獨立SPEC0049，保存使用者採用去除空白佔位的配置，不誤套E84仍待決的Q272。REQ001-004/DEC001-003/AC001-003與採用圖對齊，保留原接線/guard及匯出進度取消。附圖已原樣保存專案內，原生成檔保留；文件與Mapping完成不代表產品驗證。使用者對修正版概念圖明確採用，本輪提供五面向完整性審查與實際使用者來源，確認既定配置，不另問相同問題；無產品/OD/Git/訓練或執行授權。","task_ref":"annotation-header-layout-20261030","turn_id":"20261030-compact-header-concept-adopt"},"removed_ids":[]},"epoch":"083763cac0404db6a7ce42796f8d0f83","event_hash":"4c7a57137291fc9eb3deec898d9ec7842a6b31501dd77d41362da9469d73a858","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"325d145ddf12c6e5ddd59ba5122d1f3232a5f3d69125495ab42a8fab6fbb031e","previous_snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","recorded_at":"2026-10-30T02:15:05.661580+00:00","relationships":[],"revision":2,"snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","verdict":"PASS","working_id":"WORKING-SPEC-01a1856a7a54-annotation-header-layout"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"開始執行","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:01a18aa6-897c-7680-9ea8-7b58b8c741d8","task_ref":"annotation-header-layout-20261030","turn_id":"01a18aa6-8914-78e2-9a76-99e49bd75df9"},"removed_ids":[]},"epoch":"083763cac0404db6a7ce42796f8d0f83","event_hash":"93c98870567936543416f6008d77e834ade3c9874cdd8735e9417f8773078a68","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"4c7a57137291fc9eb3deec898d9ec7842a6b31501dd77d41362da9469d73a858","previous_snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","recorded_at":"2026-10-30T02:35:36.643667+00:00","relationships":[],"revision":2,"snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","verdict":"PASS","working_id":"WORKING-SPEC-01a1856a7a54-annotation-header-layout"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":2,"snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","working_id":"WORKING-SPEC-01a1856a7a54-annotation-header-layout"},"candidates":[],"completeness_review":null,"identified_items":{"spec0049-execution-instruction":{"id":"spec0049-execution-instruction","kind":"fact","source_ref":"user:01a18aa6-897c-7680-9ea8-7b58b8c741d8","text":"本輪使用者實際訊息為「開始執行」。真實userMessage ID 01a18aa6-897c-7680-9ea8-7b58b8c741d8，turn ID 01a18aa6-8914-78e2-9a76-99e49bd75df9，由read_thread取得。授權目前已確認SPEC0049配置實作；沒有新增需求、不延伸其他dirty工作或E84待決題。"}},"item_bindings":{"spec0049-execution-instruction":["DEC-001","DEC-002","REQ-001","REQ-002","REQ-003","REQ-004"]},"kind":"saved","reply_sha256":"5b6bf4c65a7426dd41782ab10a565b45601fec52e6cb5a8653f7d5a6e0ff5096","reply_stage":"prepared-until-host-stop","reviewed_sources":["user:01a18aa6-897c-7680-9ea8-7b58b8c741d8"],"source_ref":"assistant:msg_09dbee89b81a700b016ae401b140bc8191a085bc68959c3df1","summary":"觀察到本輪實際使用者開始執行指令，對應SPEC0049 revision2；契約未變、產品准入由managed authorize另核對。保留既有dirty變更，只調整QML頁首。","task_ref":"annotation-header-layout-20261030","turn_id":"01a18aa6-8914-78e2-9a76-99e49bd75df9"},"removed_ids":[]},"epoch":"083763cac0404db6a7ce42796f8d0f83","event_hash":"040caacfd8a3488da3c4513e778c1b0a3fb7cc0f4d762a459599f61d23c25d41","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"93c98870567936543416f6008d77e834ade3c9874cdd8735e9417f8773078a68","previous_snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","recorded_at":"2026-10-30T02:38:16.435052+00:00","relationships":[],"revision":2,"snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","verdict":"PASS","working_id":"WORKING-SPEC-01a1856a7a54-annotation-header-layout"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":2,"snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","working_id":"WORKING-SPEC-01a1856a7a54-annotation-header-layout"},"candidates":[],"completeness_review":null,"identified_items":{"spec0049-acceptance-definition":{"id":"spec0049-acceptance-definition","kind":"fact","source_ref":"validation/acceptance-SPEC-0049.json","text":"由SPEC owner acceptance_generation_plan自動投影，generation/planning均PASS，透過managed apply保存，不重寫需求或自行減少驗收門檻。定義/局部檢查PASS不等全專案驗收或Release PASS。"},"spec0049-execution-instruction":{"id":"spec0049-execution-instruction","kind":"fact","source_ref":"user:01a18aa6-897c-7680-9ea8-7b58b8c741d8","text":"本輪使用者實際訊息為「開始執行」。真實userMessage ID 01a18aa6-897c-7680-9ea8-7b58b8c741d8，turn ID 01a18aa6-8914-78e2-9a76-99e49bd75df9，由read_thread取得。授權目前已確認SPEC0049配置實作；沒有新增需求、不延伸其他dirty工作或E84待決題。"},"spec0049-global-gate-limit":{"id":"spec0049-global-gate-limit","kind":"fact","source_ref":"artifacts/spec0049-layout-20261030-52182d80/governance-check.json","text":"最近公開managed相容性報告仍BLOCKED，包含既有test/validation檔案位置LAY002及SPEC開啟一致性讀取診斷；保留原診斷，不將此標整體PASS或把SPEC改implemented。本次功能/版面已完成並有局部證據，未擴大搬動既有測試或修改其他功能。"},"spec0049-layout-implemented":{"id":"spec0049-layout-implemented","kind":"fact","source_ref":"src/dual_imu_collision_studio/qml/Main.qml@94131e6f3e33b949f5649549653643140dc2d35b58fbbbec10b588094a007724","text":"依本輪有效授權完成單一Main.qml配置：左右內容區、三管理按鈕在Recording下方靠右、移除原列佔位；工具列窄視窗Flow換行/implicitHeight自然高度以免裁切。所有原handler/guard/objectName及頁面範圍外內容與修改前受保護副本完全相同。未覆寫既有其他工作或改資料/匯出格式。"},"spec0049-local-verification":{"id":"spec0049-local-verification","kind":"fact","source_ref":"artifacts/spec0049-layout-20261030-52182d80/verification-summary.json","text":"最後source SHA94131e6...實際Qt/SegoeUI軟體渲染檢查48項PASS，1920/1366/1180px全部管理/工具可見、無新留白、波形正高度且上移；常用寬度工具列上移47px、內波形46px，最小寬度因工具列換行波形上移6px。受控export-active顯示/guard檢查，沒有真實匯出/使用者資料寫入。既有七項QML smoke PASS、26 deselected；qmlformat非寫入語法檢查PASS，development架構gate PASS VERIFIED，既有SHOULD SYM004保留。"}},"item_bindings":{"spec0049-acceptance-definition":["AC-001","AC-002","AC-003"],"spec0049-execution-instruction":["DEC-001","DEC-002","REQ-001","REQ-002","REQ-003","REQ-004"],"spec0049-global-gate-limit":[],"spec0049-layout-implemented":["DEC-001","DEC-002","REQ-001","REQ-002","REQ-003","REQ-004"],"spec0049-local-verification":["AC-001","AC-002","AC-003"]},"kind":"saved","reply_sha256":"5db4b55c2d231d6fde102d8fb17bb57f96f8fd95badbfce8b95b5e305aa2f705","reply_stage":"prepared-until-host-stop","reviewed_sources":["artifacts/spec0049-layout-20261030-52182d80/governance-check.json","artifacts/spec0049-layout-20261030-52182d80/verification-summary.json","src/dual_imu_collision_studio/qml/Main.qml@94131e6f3e33b949f5649549653643140dc2d35b58fbbbec10b588094a007724","user:01a18aa6-897c-7680-9ea8-7b58b8c741d8","validation/acceptance-SPEC-0049.json"],"source_ref":"C:\\Users\\hugo_peng\\AppData\\Local\\Temp\\spec0049-execute-20261030\\reply-final.md","summary":"已依實際開始執行訊息完成SPEC0049版面：按鈕右置Recording下方、原列收合及下方上移；最小寬度原工具尾端裁切以Flow/implicitHeight處理，屬原不裁切/適應要求。原handler/guard/objectName及頁首/工具列外Main內容逐一核對不變。最終7項QML smoke/48項受控幾何/非寫入qmlformat/development架構檢查PASS，raw/圖片及來源雜湊保存在固定run。匯出中僅顯示狀態測試，未真實匯出或改使用者資料。驗收投影由owner產生並managed apply，規格需求/修訂不變，授權沿同snapshot有效。全專案既有LAY002等診斷仍未通過，未宣稱完整驗收/Release或改implemented；不擴大處理其他dirty工作。","task_ref":"annotation-header-layout-20261030","turn_id":"01a18aa6-8914-78e2-9a76-99e49bd75df9"},"removed_ids":[]},"epoch":"083763cac0404db6a7ce42796f8d0f83","event_hash":"ecba90e5028f300a6be58aa1b633457861ad96348006be4c4042735faf24fecd","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"040caacfd8a3488da3c4513e778c1b0a3fb7cc0f4d762a459599f61d23c25d41","previous_snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","recorded_at":"2026-10-30T03:18:21.107150+00:00","relationships":[],"revision":2,"snapshot_hash":"4818457191183c38740c114341e364702c493fddf23f7d93424ffd2d5a9c867f","verdict":"PASS","working_id":"WORKING-SPEC-01a1856a7a54-annotation-header-layout"}
```
<!-- spec-audit:end -->
