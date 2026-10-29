---
spec_version: 1
spec_id: SPEC-0048
revision: 4
status: working
change_set: export-annotated-data
working_id: WORKING-SPEC-6bfcf59ad980-export-annotated-data
task_ref: 01a17cb2-f497-74b2-9249-15b21a1071fc
---
# 匯出已標記資料：具體修改方案

2026-10-27。**working / 候選方案，尚未採用，沒有產品實作授權。** 本次僅保存方案與規格，不修改產品程式、不執行模型訓練。

## Problem

使用者要求在 Annotate & Classify 的 `Confirm All Annotation Sets` 旁增加匯出所有已標記資料，供另一分析任務先用一筆 recording 確認碰撞／正常動作區段。一般 `.dicsproj` 不內嵌完整波形；Replay CSV 依賴模型與目前所選 recording，無法直接滿足需求。

來源：`codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input`。委派明確要求先提出方案。ZIP 是候選方向，尚非使用者採用規格。

## Solution

推薦新增 `Export Annotated Data…`，匯出**當前 session 中，至少有一個顯式 annotation 的全部 recordings，各自完整的對齊量測**，連同標記、mapping、確認狀態及來源追溯資訊，以單一 ZIP 交付。包含未確認／provisional，保留原狀態，不呼叫 Confirm、不依賴 Learning 或 Qualification。

此包供獨立分析，不宣稱可由 Studio 直接 Open ZIP、不取代 `.dicsproj`。首次只有一筆已標記 recording 的 session 即可驗證；功能不增加「目前選取／全部」範圍選項。

## User Stories

- 人工標記者不必先訓練即可交付每個事件前後完整量測。
- 分析者能對回 sample index、來源訊號、速度／offset、插值點，區分 provisional、整組確認、Ignore、推導 Normal 與未標記背景。
- 失敗／取消不改動標記、來源或先前成功匯出的目的檔。

## Requirements

只記錄來源訊息確定的邊界；P-001…P-008 為待採用候選。

| ID | Requirement |
|---|---|
| REQ-001 | 提出在 Confirm All Annotation Sets 旁匯出所有已標記資料的具體方案與規格。 |
| REQ-002 | 交付可連結標記與對應量測的資料，保留 IMU／訊號／索引與標記狀態，供後續分析。 |
| REQ-003 | 本輪只做文件，不改產品、訓練或來源，不延伸模型／韌體／其他 UI 重構；保留現有未提交修改。 |

## Decisions

| ID | Decision | Source |
|---|---|---|
| DEC-001 | 在本專案建立獨立方案規格，不沿用其他演算法研究或 SPEC-0047。 | codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input |
| DEC-002 | 本輪不改產品、不訓練、不改來源，保留 dirty changes。 | codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input |

## Current state and source evidence

下列路徑相對 `src/dual_imu_collision_studio/`，本輪重新核對，行號會隨後續修改移動。

| 位置 | 事實與影響 |
|---|---|
| `qml/Main.qml:625` | Confirm 在頁首 RowLayout 右端，呼叫 studio.confirmAnnotations()；新按鈕可緊接其後。 |
| `adapters/desktop/controller.py:3290` | confirmAnnotations 驗證所有 recording、將 provisional=false、清除提案來源並建立 confirmed workspace。途中失敗也可能已替換前面的 tuple；匯出須保存當下真實狀態，不自行修正。 |
| `controller.py:5001,5551,6020` | project serializer fingerprint 所有來源但不存波形；annotation serializer 有完整 identity/provenance；recording builder 可讀整段 arrays。不得直接用整個 project document 代替資料包。 |
| `domain/data_workspace/model.py` | AnnotationInterval 有索引、reason、provisional、source_recording_id/source_cycle_index、interval_id；Normal 不能顯式建立。Recording 支援單 IMU，每 sensor 3/6 軸；ImportedSamples 有 interpolated_indices。 |
| `domain/data_workspace/service.py:283,335` | 完整確認至少兩 Cycle且各事件數一致，禁止非法重疊／跨中斷；Normal 在 Cycle 內扣除事件、Ignore與碰撞起點後含截止樣本的150ms response。完整確認條件不應阻擋 draft 匯出。 |
| `controller.py:835` | 只有 confirmed workspace 才顯示 derived Normal。 |
| `adapters/tabular/reader.py:65–194` | 轉秒／固定率時間、修補1–3缺樣、可裁末尾不完整列並保留warning。Studio 索引對應 repaired timeline，不能直接當原檔列號。 |
| `controller.py:2543–2574,2687–2809` | mapping 保留 raw/filtered欄位、per-signal設定；primary選 raw或缺raw時filtered。signal mapping有source_sha256，legacy未必有。沒有權威逐訊號單位欄位。 |
| `controller.py:1902`、`adapters/desktop/replay_writer.py` | 既有QRunnable／queued completion與same-folder tmp、fsync、replace模式可參考；Replay admission依賴candidate且限制部分single-IMU，不適用本功能。 |

已讀 AGENTS.md、manifest/adoption/ARCHITECTURE/baseline、designs來源、兩份 proposed ADR，及 SPEC-0006、0024、0041、0047。現有schema/standard=2.2.0、baseline零項；不把任何 proposed ADR 改accepted。env_sensing/SPEC-0105不是本功能契約。

## Recommended improvements

### P-001：按鈕及啟用（candidate）

在 Confirm 右側新增 `Export Annotated Data…`，objectName建議`exportAnnotatedDataButton`，沿用PaddedButton。窄視窗允許頁首動作區換行，保留Confirm後的閱讀順序，需確認文字完整可見。

至少一份有顯式標記且mapping已完成、已載入樣本可用，且無互斥工作時啟用。只有Cycle、只有Ignore、未確認、provisional-only均算有標記；**不要求annotationsReady、Learning、數值型別、模型或Qualification**。沒有標記則disable並顯示原因。其他未標記recording未完成mapping不阻擋；有標記項目缺樣本／mapping不一致必須列名拒絕，不可靜默漏匯。

開本機ZIP儲存對話框，建議`<project-stem>_annotated_<YYYYMMDD_HHmmss>.zip`，無專案名用studio。系統對話框負責覆寫確認；取消不改state。回傳後重新檢查admission，accepted時捕捉快照。顯示recording/rows/provisional數量、進度、取消及完成完整路徑。

### P-002：所有已標記的範圍（candidate）

「所有」是當前session全部已匯入recordings／worksheets，不是硬碟搜尋，也不限目前selector。每份有顯式annotation者輸出0…N-1全部樣本及所有實際mapped primary channels；不截事件／Cycle、不降採樣、不取畫面envelope、不刪Ignore或未標記背景。

原樣保留provisional、identity、reason、proposal來源。另存session.annotations_ready、mapping_confirmed、has_provisional與逐recording完整驗證狀態／原因。**provisional=false只代表不是自動提案，不能單獨當作整組已確認或ground truth**；系統無獨立持久per-recording confirmation，不捏造此旗標。有效的局部validation不能冒稱Confirm All完成。

manifest列出無標記項目及no_explicit_annotations理由。來源提案reference即使在匯出範圍外也保留id並標outside_export，不刪provenance。不更改project dirty、選取、history、模板或Learning結果。未提交的拖拉先完成／取消才捕捉。

### P-003：ZIP v1格式（candidate）

```text
<name>.zip
  README.md
  manifest.json
  recordings/r0001/samples.csv
  recordings/r0001/annotations.json
  recordings/r0002/samples.csv
  recordings/r0002/annotations.json
```

內部用安全連續代碼，manifest對應原recording_id、basename、worksheet，避免同名檔及路徑字元碰撞。原id僅session-local，以export_id+recording_id識別該包。不新增Parquet/HDF5依賴；代價是CSV容量及解析成本較高，不保存原檔bytes／未映射欄位。

V1只輸出annotation使用的**primary view**。若同時mapping raw與existing-filtered，以`_samples`實際primary為準，各view明列exported及未匯出理由。application-filtered保留設定／係數與warmup資訊，**不重新運算濾波、不匯出prediction/Score/threshold或模型**。不能把只匯出一種view的包宣稱已含所有alternate filtered值。

### P-004：manifest與樣本欄位（candidate）

manifest為UTF-8 JSON：format=`studio-annotated-data`、schema_version=1、export_id、UTC created_at、Studio version、snapshot時刻、session.annotations_ready、total/exported/excluded counts、每member bytes/count/SHA-256。最後才寫manifest；不建立manifest自身循環digest，封存本體有ZIP CRC。

| 區塊 | 欄位與語意 |
|---|---|
| recording | export-local key、session recording_id、display_name、source basename、worksheet、row_count、sample_rate_hz、robot_speed_mm_s、collision_offset_mm、single_sensor、mapping_confirmed、has_provisional、annotation_validation及原因 |
| source | data_view=studio_imported_aligned、data_start_row/header_row、time_column/unit/fixed_rate、import warnings、指紋與capture stage。已有mapping.source_sha256標mapping_confirmation；缺少則null/not_recorded；不在匯出時重新hash後冒稱import指紋。 |
| channels | CSV column、sensor internal/external、signal_kind accelerometer/gyroscope/unknown、axis、source_column、source_mapping_role raw/filtered/legacy、configured_preprocessing、unit、unit_status/evidence。保留來源欄名；header暗示不當權威單位。 |
| mapping | 原primary及signals/raw/filtered選擇、single-IMU設定、filter settings/係數等已有metadata，不計算新輸出。 |
| policy | index_base=0、interval_convention=[start_index,end_index)、timeline=studio_imported_aligned、Normal policy/window/version及確認說明。 |

不預設帶絕對來源路徑。已載入的快照可在來源檔缺失／變更後匯出；README清楚寫歷史指紋未重新驗證磁碟來源。正確標記對應由快照及sample member digest證明，不冒稱原檔bytes即時一致。這也避免重新匯入大型資料導致索引變動。

samples.csv純UTF-8逗號表，不混註解，概念header如下；實際只列存在通道：

```text
sample_index,time_s,source_data_row,is_interpolated,discontinuity_before,internal.ax,internal.ay,internal.az,internal.gx,...,external.gz
```

- 每sensor依mapping已選子集排列accel XYZ再gyro XYZ；single-IMU不補另一顆零值，gyro-only為gx/gy/gz。不能依三欄shape推定加速度；legacy不明種類用c0/c1/c2與unknown descriptor。未知物理單位用null+unknown，不能擅標g、m/s²、deg/s。
- 數值來自完整`_samples`，不正規化、不換單位、不縮為target float32。浮點以有限、可round-trip表示輸出；time_s保留原起點，fixed-rate時間明列generated。這是匯入／修補後資料，非原檔逐字副本，也不是軟體filter輸出。
- sample_index連續0…N-1，annotation引用同一時間軸。is_interpolated取自interpolated_indices。非插值index i的source_data_row=`data_start_row+i-count(inserted_index<i)`；插值點留空。此列是來源表格1-based row，不是CSV引號內換行後的實體line number。尾列裁切及warning保留。
- discontinuity_before原樣；缺marker以false並記default來源，不偽造acquisition gap。未實測單位與未紀錄指紋不阻擋資料交付，但README不得掩飾缺口。

### P-005：標記與Normal（candidate）

annotations.json分開保存explicit_intervals與derived_intervals。explicit逐筆保留`interval_id,kind,start_index,end_index,reason,provisional,source_recording_id,source_cycle_index`；不壓成每列單一class，以保留Cycle+事件等多重語意。

僅在session.annotations_ready=true、有一致confirmed workspace且snapshot仍通過完整驗證時，呼叫現有workspace Normal推導，附derived=true、policy identity與collision_response_window_s=0.150。否則derived_status=unavailable_unconfirmed且derived_intervals=[]，不可把未標記樣本補成Normal。ready=true卻仍有provisional／不一致則整包失敗，不產生假真值。

Normal只在有效Cycle內，扣掉Pick/Put/Collision/Ignore及Collision onset至+150ms含截止樣本的response；現有方法也排除更長的Collision annotation，並clip至Cycle／中斷邊界。**不修改Collision本身end_index**。Ignore是有原因的排除；未標記事件背景不新增假annotation；Cycle本身不代表正常或碰撞真值。

索引權威採0-based半開`[start,end)`。輔助時間可寫start_time_s=time[start]、last_included_time_s=time[end-1]、end_boundary_time_s=time[end]；end=N時後者null，不以+1/fs假造邊界。

結構無效（id空／重複、0≤start<end≤N不成立、通道／時間不對齊或非有限值、mapping不一致）整包失敗。未確認資料的完整性問題（未滿兩Cycle、事件數不同、Ignore/Collision overlap、跨中斷等）可以原樣匯出，必須標annotation_validation=invalid與原因。**匯出成功不等於Learning-ready或真值已驗證**；不呼叫confirm、不修理或刪除疑義標記。

### P-006：背景串流、互斥與失敗（candidate）

一個QRunnable逐recording/chunk串流CSV到ZIP，啟用ZIP64，節流progress；不建全量Python list、大字串、全量sample labels或額外波形副本。metadata/annotation tuples複製成immutable snapshot，arrays借用只讀，worker不讀寫controller dictionary。詳細owner與Port見架構方案。

匯出期間可閱讀、切換recording、zoom；會改資料／mapping／annotations的command、Confirm/reference/undo/redo、Import、Open/New/Save project、Learning/Qualification與其他artifact exports互斥。controller入口和QML都guard，避免只disable按鈕可被呼叫繞過。native dialog回傳後才commit busy，不持鎖等使用者選檔。

- 非本機URL、父目錄不存在／無寫權、來源同路徑（resolved/case-normalized）、busy或樣本／mapping不一致，接受前拒絕，列原因。
- 同目錄唯一tmp exclusive create，增量hash/count，各member完成後寫manifest，關ZIP central directory、flush/fsync，再os.replace；replace成功才報完成，保留先前目的檔到最後提交。
- 任一recording或write/ZIP close/fsync/replace/disk-full失敗，整包失敗，無部分成功；盡力unlink tmp，舊目的檔不變，顯示recording／階段／錯誤。cleanup也失敗需顯示殘留tmp，不誤報成功。禁止自動retry。
- 取消每chunk及commit前檢查；atomic replace前取消勝出，replace後為已完成，不能假稱rollback。關窗先取消、defer close至terminal，不在UI thread等整段寫入。強制kill可能留tmp，不承諾crash後必清。
- terminal校驗export_id，UI thread先清busy/state再publish一次completed/failed/cancelled，成功／失敗／取消都釋放借用；不改標記與project dirty。

### P-007：取捨、效能與替代（candidate）

| 選項 | 收益 | 成本／犧牲 | 建議 |
|---|---|---|---|
| ZIP + 完整CSV + interval JSON | 自含、保留背景與多重標記、無新依賴 | CSV容量／格式化成本、需版本化schema與writer測試 | 推薦 |
| 單一CSV每列一個class | 結構簡單 | 不能無損表達Cycle+事件、Ignore reason、provenance；仍需sidecar | 不推薦 |
| 只切事件片段 | 較小 | 遺失事件前後背景、重編index，難確認正常／假觸發 | 不滿足交付目的 |
| dicsproj+原檔 | 保留來源全部欄位 | 需重新讀取／修補對照、帶不相關結果，可能漏檔 | 現有project保留，本功能另交付 |
| Parquet/HDF5 | 二進位／型別與大型讀取有優勢 | 新依賴及reader／部署契約，目前下游未指定 | 本期不採用 |

另一任務提供10份、2,985,537rows作為規模線索，本輪未讀那些來源。N×13×8約296MiB只是最多12個IMU channels+time的既有float64數值payload估算，非CSV/ZIP大小或實測RSS。串流避免再複製同級payload，但Python格式化GIL、ZIP壓縮與磁碟仍可能影響互動；不宣稱背景thread必不卡。

線性O(N×C+A)時間；額外O(K×C+A+R+G)，K=chunk大小，A=annotations，R=recordings，G=插值metadata；磁碟須容納新完整包與舊目的檔共存至replace。chunk與壓縮設定在對照量測前不稱最佳。沿用既有interactive-workspace p95≤100ms作互動回歸目標；新export沒有已採用的完成時間／MB/s／額外記憶體／取消延遲門檻，需後續量測與人類確認。

### P-008：實作順序（candidate）

1. 採用方案後確認canonical契約及Acceptance Mapping；處理已發現治理blockers，完成architecture/designs來源、render與候選design gate。
2. 先完成workspace純匯出語意、Fake/Real output Port契約、3/6channels及draft/provisional／Normal邊界fixtures。
3. 實作atomic ZIP writer與fault injection，再接snapshot worker／互斥guards，最後接QML按鈕、dialog、progress與取消。
4. 先用一筆已標記recording獨立解包對照全部samples／intervals，再做多筆、失敗／取消、代表大資料runtime／資源測試；不訓練模型。
5. regression、single CLI architecture/render/release檢查及來源／現有dirty hashes對照。

## Architecture impact

見 [架構候選方案](../architecture/designs/SPEC-0048-annotated-export-proposal.md)：Boundary Design Table、Type/State Ownership Matrices、actual/intended edges與parent mappings、Execution/Flow/Evolution/Algorithm及Description Views影響。

L1 data_workspace擁有snapshot語意與demand-side output Port，L0協調，L3 desktop_adapter負責ZIP storage；不新增domain、不新增Learning依賴、不改project/model/Replay格式。預計新增export-annotated-data Flow、snapshot/worker型別及job state。本輪只寫rationale，未改design-data catalogs、manifest或generated pages；**候選manifest未建立／未驗證，不宣稱design PASS**。

## Acceptance Criteria

本表是本輪**方案交付**的檢視範圍，無產品runtime PASS。

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | 保存獨立方案，描述按鈕、admission、全session範圍與格式。 | 原始需求對照及Markdown檢視。 | 本文件P-001…P-004，候選未採用。 |
| AC-002 | REQ-002 | 說明primary timeline／通道單位、標記狀態／Normal語意、失敗／效能及驗證。 | 對照程式證據、架構matrices與下表。 | P-004…P-008；未執行產品驗收。 |
| AC-003 | REQ-003 | 不改產品、來源或訓練，保留已有三項變更。 | git status/diff與原有變更SHA-256對照。 | artifacts/spec0048-proposal-20261027/preserved-hashes.json；結束前核對。 |

## Validation and acceptance plan（尚未執行）

採用後轉正式AC與schema-2 Acceptance Mapping；此表不是已採用行為或測試證據。

| Proposed AC | 方案／邊界 | 可重現方法 | 明確通過條件 | Evidence |
|---|---|---|---|---|
| PAC-001 | P-001/P-002；L0/QML | 新tests/modules/studio_application/test_annotated_data_export.py及test_annotated_data_export_qml.py；native desktop窄視窗／font scale | empty disabled；一筆draft/provisional可匯出且無模型；Confirm右側可見、文字不截斷 | JUnit、native screenshot／步驟 |
| PAC-002 | P-002/P-003；workspace/writer | 新tests/flows/export-annotated-data；兩已標、一未標、同檔多worksheet，選第二份；獨立zipfile/csv/json reader | 恰兩份完整N rows；未標排除理由；不受selector影響；counts/digests一致 | artifact hash、獨立reader assertions |
| PAC-003 | P-004；snapshot/Port | 新tests/modules/data_workspace/test_annotated_export_snapshot.py與writer contract：single internal/external、accel、gyro-only、6ch、raw/filtered三模式、unknown units | round-trip等於primary arrays；無換單位／濾波／補零；descriptor及alternate-view未匯出理由正確 | golden manifest/CSV、array assertions |
| PAC-004 | P-004/P-005；indices | fixed-rate、非零time、1–3缺樣、尾列裁切、end=N、非法range/id fixtures | index連續，source row正確、插值null；warnings保留；半開無off-by-one；非法結構失敗 | boundary/property assertions |
| PAC-005 | P-005；truth | draft、provisional-only、未滿兩Cycle／非法overlap、confirmed150ms含截止樣本及長Collision | explicit原樣，不confirm；draft diagnostics invalid可交付而無Normal；confirmed Normal等於既有方法、Collision end不改 | semantic assertions、前後snapshot對照 |
| PAC-006 | P-006；writer/fault | Fake與Real adapter reusable contract：disk-full/write/close/fsync/replace失敗、覆寫、非localURL、來源path/case alias、cancel before/after commit | 每job一次terminal；失敗舊目的檔byte-identical；無有效partial ZIP；正常tmp清除，cleanup失敗可見；不寫來源 | fault fixtures、file hashes、事件捕捉 |
| PAC-007 | P-006；session concurrency | accepted後呼叫各mutation／Open/New/Save／Learning/Qualification／其他exports，另select/zoom，native關窗取消 | controller及QML互斥；閱讀可用；busy每terminal清；snapshot穩定；無worker改UI／懸空callback | interaction tests與native smoke |
| PAC-008 | P-007；large export | 一筆先解包對照；再用2,985,537-row規模或等價synthetic、固定C/A/G，鄰近chunk／bulk baseline比較；Windows ETW/WPR+domain markers | zero dropped rows／labels；無全量copy／文字；依既有p95≤100ms回歸目標；完整記錄peak/throughput/cancel。機型及新資源門檻未定者BLOCKED | immutable run、native trace、parser結果 |
| PAC-009 | P-008；compatibility/governance | focused後full pytest；single architecture_cli design/development/release、render --check、hash comparison | 舊project/Replay/model/qualification不變；required gates過；zero baseline；release無test injection；來源／既有變更不動 | exit codes/JUnit/gate、build hashes |

預定focused命令（上述新測試尚未建立）：

```powershell
.venv/Scripts/python.exe -m pytest tests/modules/data_workspace/test_annotated_export_snapshot.py tests/modules/desktop_adapter/test_annotated_data_writer.py tests/modules/studio_application/test_annotated_data_export.py tests/modules/studio_application/test_annotated_data_export_qml.py tests/flows/export-annotated-data -q -p no:cacheprovider --basetemp artifacts/<new-run-id>/pytest --junitxml artifacts/<new-run-id>/focused.xml
```

四階段驗證順序：

1. **Validation Enablement**：產品修改前定義tracked validation profile、Flow scenarios/local binding；probe native desktop/filesystem與ETW/WPR，先可執行Fake/Real Port成功／失敗／取消fixtures。host assertions不要求IMU或Serial。provider不可用則該資源驗收BLOCKED，不讓build代替量測。
2. **Development**：domain／parent Fake Port／writer reusable contract／QML focused tests。無firmware/hardware smoke；Qt queued events、native filesystem與關窗需要Windows desktop smoke。
3. **Final Runtime**：獨立run ID分單筆交付、多筆、故障／取消／關窗與大負載，記錄界限、初態、trigger、completion、raw evidence；時間／bytes上限依fixture/capability設定，不虛構通用秒數。
4. **Release**：runtime後驗release composition、完整regression、architecture/render與資源證據；test-only injection不進release；validation/release builds證據分開。

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | depends_on | DEC-001 |
| REQ-003 | depends_on | DEC-002 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |
| AC-003 | depends_on | REQ-003 |

SPEC-0006為原子匯出模式參照、SPEC-0024為identity、SPEC-0041為通道契約；均不重開。SPEC-0047與外部env_sensing/SPEC-0105不是此功能採用／執行依據。

## Out of Scope

本輪產品source/tests/runtime/generated執行內容或訓練；模型改造、旋轉補償、韌體；來源錄波修改、硬碟搜尋、原檔bytes／未映射欄位備份；ZIP直接Open Studio；project schema migration；重建已遺失歷史proposal來源；其他標記UI重構或分析報告。

## Open Decisions

None.

## Remaining uncertainties

本輪交付範圍僅初步方案，沒有必須使用者決定才能完成文件的分歧；下列為後續若採用實作才需處理的候選／未知項。

P-001…P-008均為建議，**尚未取得使用者對完整方案的採用確認**。本次只要求先提案，沒有強迫澄清／pending question。建議預設包含draft/provisional、完整primary timeline、ZIP v1、無範圍選擇UI；正式materialize前需整體審查，不因保存自動升格。

chunk/compression、目標Windows機型/profile、額外記憶體／取消驗收門檻尚未量測或採用。logical proposal可保存，效能winner／execution profile acceptance與產品admission不宣稱PASS。若要求每通道物理單位必須確定，需另討論metadata填寫／確認流程；目前建議忠實unknown。

## Routing/Gates

- ask-matt → spec-governance/grilling保存討論；clarify-improvement-proposals支援候選比較；govern-modular-event-architecture支援ownership與Flow review。implementation/context均present；新format/Port/worker候選屬R2評估，當前只寫文件。
- 首次router因其他任務多份SPEC無法唯一選取；已建立SPEC-0048並綁working reference，不借其他confirmed SPEC取得執行權。
- 系統python不相容，使用專案.venv；設定UTF-8修正cp950。受限執行器R: drive錯誤，已獲准一般執行環境讀取與保存文件。
- 現況development gate exit0：PASS: VERIFIED，保留既有SHOULD SYM004。證據artifacts/spec0048-proposal-20261027/architecture-development.txt；不是新設計／功能PASS。
- router另發現既有test/validation layout FAIL、validation planning BLOCKED；見同run的router.json。不得把project gate當成這些檢查PASS；本輪不擅自搬測試／修產品／降門檻／加baseline。後續實作前調查修復blockers，不擴張目前方案任務。
- 新manifest未產生；新功能design/development/runtime/release gates均NOT RUN。文件完成不表示功能完成。

## Discussion Context

### DISC-001：方案任務範圍
- Situation：分析任務需要人工標記及完整對應量測，缺獨立於模型的交付入口。
- Source：codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input。
- User answer／已確認：先提本專案修改方案與規格；不改產品或訓練。
- Explicit rationale：之後先用一筆recording檢查碰撞／正常區段。
- Candidates：P-001…P-008，全部未採用；沒有開始執行授權。
- Delta：獨立canonical SPEC、程式證據、格式／狀態／錯誤／效能、架構候選矩陣與驗證計畫。沒有重開舊SPEC或替使用者批准ADR。

## Scope and Authorization

僅保存已授權的方案文件。未取得完整候選採用或產品修改授權，本輪不要求使用者立即實作。若之後要進入實作，依current SPEC/execution流程處理，不將本文件當執行許可。

## Revision History

| Revision | Change |
|---|---|
| 1 | 本任務獨立開始：匯出所有已標記資料，僅方案。 |
| 2 | 保存ZIP v1／primary timeline、draft/provisional／Normal、欄位／索引、原子背景匯出、架構矩陣與驗證方案；未採用、未授權實作。 |
| 3 | 區分本輪方案交付無待答問題，與未來採用／效能驗證的未知項；不強迫澄清或升格候選。 |
| 4 | 將方案後續未知項維持獨立段落，符合owner對Open Decisions空集合的解析格式。 |

## Current Specification

See Problem, Solution, Requirements and Acceptance Criteria above.

## Decision History

See Decisions, Discussion Context and the sourced Discussion History below.

## Pending Discussion

None.

## Completeness Gaps

- AC-001: evidence claims (evidence_claims) required
- AC-001: applicability rationale required
- AC-002: evidence claims (evidence_claims) required
- AC-002: applicability rationale required
- AC-003: evidence claims (evidence_claims) required
- AC-003: applicability rationale required

<!-- spec-audit:start -->
## Discussion History

- codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input: 請在專案提出匯出已標記資料的具體修改方案；只保存方案與規格，不修改產品程式、不訓練模型；保留既有 qualified offset 修改。
- codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input: 提出匯出已標記資料修改方案，僅文件規格，禁止產品修改及訓練
- spec-governance/REPLY-annotated-export.md: 完成本輪初步方案文件；ZIP完整primary量測與標記候選、真值/索引/來源/單位、原子背景匯出、架構matrices及驗證規劃。使用者僅要求先提案；候選未採用，無產品授權。現況gate通過而新功能與較新layout/validation gates未通過；三項既有修改hash未變。
- spec-governance/REPLY-annotated-export.md: 完成本輪初步方案文件；ZIP完整primary量測與標記候選、真值/索引/來源/單位、原子背景匯出、架構matrices及驗證規劃。使用者僅要求先提案；候選未採用，無產品授權。現況gate通過而新功能與較新layout/validation gates未通過；三項既有修改hash未變。

### Source and Revision Audit

```jsonl
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"d64113e85edc2fa874312c805dba866b0686882d4163878808feef51453b5451","event_type":"start","event_version":1,"open_decisions":["本次候選方案尚未由使用者採用。"],"previous_event_hash":null,"previous_snapshot_hash":null,"recorded_at":"2026-10-27T09:34:17.871933+00:00","relationships":[],"revision":1,"snapshot_hash":"92dc88308ad410d5eb0059a2ace70610ec8649012dcb70178c2b31aa6786e873","verdict":"BLOCKED","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"請在專案提出匯出已標記資料的具體修改方案；只保存方案與規格，不修改產品程式、不訓練模型；保留既有 qualified offset 修改。","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"initial-delegation"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"8b64d6f4881252cc8a94c09a265a6646740790a3e46cfa0a5470f46bf03f0eae","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"d64113e85edc2fa874312c805dba866b0686882d4163878808feef51453b5451","previous_snapshot_hash":"92dc88308ad410d5eb0059a2ace70610ec8649012dcb70178c2b31aa6786e873","recorded_at":"2026-10-27T09:34:43.489009+00:00","relationships":[],"revision":1,"snapshot_hash":"92dc88308ad410d5eb0059a2ace70610ec8649012dcb70178c2b31aa6786e873","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"提出匯出已標記資料修改方案，僅文件規格，禁止產品修改及訓練","kind":"entry-update","source_ref":"codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"initial-delegation"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"4605d3278a8c74916ff4c54f6031f88028881072097431c084cc9cee1dee37f7","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"8b64d6f4881252cc8a94c09a265a6646740790a3e46cfa0a5470f46bf03f0eae","previous_snapshot_hash":"92dc88308ad410d5eb0059a2ace70610ec8649012dcb70178c2b31aa6786e873","recorded_at":"2026-10-27T09:36:54.398151+00:00","relationships":[],"revision":1,"snapshot_hash":"92dc88308ad410d5eb0059a2ace70610ec8649012dcb70178c2b31aa6786e873","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":["AC-001","AC-002","AC-003","DEC-001","DEC-002","REQ-001","REQ-002","REQ-003"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["AC-001","AC-002","AC-003","DEC-001","DEC-002","REQ-001","REQ-002","REQ-003"],"changed_ids":[],"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"0f75895aa2dd629ccecba7d8a6d3b651dd2df2b1634e0009d09eca1aeafa8592","event_type":"reconcile","event_version":1,"open_decisions":["P-001…P-008均為建議，**尚未取得使用者對完整方案的採用確認**。本次只要求先提案，沒有強迫澄清／pending question。建議預設包含draft/provisional、完整primary timeline、ZIP v1、無範圍選擇UI；正式materialize前需整體審查，不因保存自動升格。","chunk/compression、目標Windows機型/profile、額外記憶體／取消驗收門檻尚未量測或採用。logical proposal可保存，效能winner／execution profile acceptance與產品admission不宣稱PASS。若要求每通道物理單位必須確定，需另討論metadata填寫／確認流程；目前建議忠實unknown。"],"previous_event_hash":"4605d3278a8c74916ff4c54f6031f88028881072097431c084cc9cee1dee37f7","previous_snapshot_hash":"92dc88308ad410d5eb0059a2ace70610ec8649012dcb70178c2b31aa6786e873","recorded_at":"2026-10-27T09:49:15.988136+00:00","relationships":[{"relation":"depends_on","source":"REQ-001","target":"DEC-001"},{"relation":"depends_on","source":"REQ-003","target":"DEC-002"},{"relation":"depends_on","source":"AC-001","target":"REQ-001"},{"relation":"depends_on","source":"AC-002","target":"REQ-002"},{"relation":"depends_on","source":"AC-003","target":"REQ-003"}],"revision":2,"snapshot_hash":"747fde233739ac2400f58bab8c1f02a166e5dc0ab518be5e5701f8c0f1de5545","verdict":"BLOCKED","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"32b2c29af8f21c4ec1bfa3a2441ffc1e77160ce1160e472f9bdfe80380fe727a","event_type":"reconcile","event_version":1,"open_decisions":["None.","本輪交付範圍僅初步方案，沒有必須使用者決定才能完成文件的分歧；下列為後續若採用實作才需處理的候選／未知項。"],"previous_event_hash":"0f75895aa2dd629ccecba7d8a6d3b651dd2df2b1634e0009d09eca1aeafa8592","previous_snapshot_hash":"747fde233739ac2400f58bab8c1f02a166e5dc0ab518be5e5701f8c0f1de5545","recorded_at":"2026-10-27T09:51:01.956702+00:00","relationships":[{"relation":"depends_on","source":"REQ-001","target":"DEC-001"},{"relation":"depends_on","source":"REQ-003","target":"DEC-002"},{"relation":"depends_on","source":"AC-001","target":"REQ-001"},{"relation":"depends_on","source":"AC-002","target":"REQ-002"},{"relation":"depends_on","source":"AC-003","target":"REQ-003"}],"revision":3,"snapshot_hash":"d7b7e17bc9329eb973991bb754227d9223db9ba37981267e8fcdd47e1bd98aa7","verdict":"BLOCKED","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"73713e4a7817495cdb3bf9110026095482df4b23d5a205293d81fe2d044d2763","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"32b2c29af8f21c4ec1bfa3a2441ffc1e77160ce1160e472f9bdfe80380fe727a","previous_snapshot_hash":"d7b7e17bc9329eb973991bb754227d9223db9ba37981267e8fcdd47e1bd98aa7","recorded_at":"2026-10-27T09:51:21.087845+00:00","relationships":[{"relation":"depends_on","source":"REQ-001","target":"DEC-001"},{"relation":"depends_on","source":"REQ-003","target":"DEC-002"},{"relation":"depends_on","source":"AC-001","target":"REQ-001"},{"relation":"depends_on","source":"AC-002","target":"REQ-002"},{"relation":"depends_on","source":"AC-003","target":"REQ-003"}],"revision":4,"snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":4,"snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"},"candidates":[{"id":"PROPOSAL-001","impact":"新增全session已標記資料交付流程；完整primary時間軸、原狀態與來源；無模型訓練。","reason":"使用者要求可審查初步方案，本輪不做採用與實作決策。","source_ref":"specs/SPEC-0048-export-annotated-data.md#recommended-improvements","status":"candidate"}],"completeness_review":{"acceptance":{"evidence":"列九項候選驗證與四階段方法；新功能未測，效能與治理未知項明列。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"behavior":{"evidence":"候選P-001至P-008覆蓋按鈕、ZIP格式、完整時間軸與標記語意；尚未採用。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"exceptions":{"evidence":"結構錯誤拒絕，draft完整性問題記錄，失敗/取消atomic保留舊檔。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"goal":{"evidence":"已依原需求提出資料交付方案。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"scope":{"evidence":"只文件，保留其他修改，不改產品或訓練。","source_ref":"specs/SPEC-0048-export-annotated-data.md"}},"identified_items":{"FACT-001":{"id":"FACT-001","kind":"fact","source_ref":"architecture/designs/SPEC-0048-annotated-export-proposal.md","text":"已核對workspace/index/Normal語意；現有development gate exit0，router另有layout/validation BLOCKED。候選manifest與新功能runtime未驗證。"},"PROPOSAL-001":{"id":"PROPOSAL-001","kind":"candidate","source_ref":"specs/SPEC-0048-export-annotated-data.md#recommended-improvements","text":"P-001至P-008建議：Confirm旁按鈕，全部已標記recordings完整primary samples+intervals+manifest ZIP v1；保留draft/provisional與未知單位；背景串流與原子提交。尚未採用。"},"SCOPE-001":{"id":"SCOPE-001","kind":"accepted","source_ref":"codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input","text":"在Studio專案獨立提出匯出所有已標記資料的方案與規格，供後續一筆recording確認。"},"SCOPE-002":{"id":"SCOPE-002","kind":"accepted","source_ref":"codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input","text":"只做方案文件，不改產品、訓練、來源或其他模型/韌體/UI scope，保留既有dirty changes。"}},"item_bindings":{"FACT-001":[],"PROPOSAL-001":[],"SCOPE-001":["REQ-001","REQ-002","DEC-001"],"SCOPE-002":["REQ-003","DEC-002"]},"kind":"saved","reply_sha256":"14115c2a593f1d683f9528eee30a261b40f82bcaf841fa54976fdbeb93c34c10","reply_stage":"prepared-until-host-stop","reviewed_sources":["architecture/designs/SPEC-0048-annotated-export-proposal.md","codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input","specs/SPEC-0048-export-annotated-data.md#recommended-improvements"],"source_ref":"spec-governance/REPLY-annotated-export.md","summary":"完成本輪初步方案文件；ZIP完整primary量測與標記候選、真值/索引/來源/單位、原子背景匯出、架構matrices及驗證規劃。使用者僅要求先提案；候選未採用，無產品授權。現況gate通過而新功能與較新layout/validation gates未通過；三項既有修改hash未變。","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"initial-delegation"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"f0c66f98730d06967adc564cdc60d29903b970a0347812071abb24c072bb88e6","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"73713e4a7817495cdb3bf9110026095482df4b23d5a205293d81fe2d044d2763","previous_snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","recorded_at":"2026-10-27T09:53:25.329015+00:00","relationships":[],"revision":4,"snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":4,"snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"},"candidates":[{"id":"PROPOSAL-001","impact":"新增全session已標記資料交付流程；完整primary時間軸、原狀態與來源；無模型訓練。","reason":"使用者要求可審查初步方案，本輪不做採用與實作決策。","source_ref":"specs/SPEC-0048-export-annotated-data.md#recommended-improvements","status":"candidate"}],"completeness_review":{"acceptance":{"evidence":"列九項候選驗證與四階段方法；新功能未測，效能與治理未知項明列。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"behavior":{"evidence":"候選P-001至P-008覆蓋按鈕、ZIP格式、完整時間軸與標記語意；尚未採用。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"exceptions":{"evidence":"結構錯誤拒絕，draft完整性問題記錄，失敗/取消atomic保留舊檔。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"goal":{"evidence":"已依原需求提出資料交付方案。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"scope":{"evidence":"只文件，保留其他修改，不改產品或訓練。","source_ref":"specs/SPEC-0048-export-annotated-data.md"}},"identified_items":{"FACT-001":{"id":"FACT-001","kind":"fact","source_ref":"architecture/designs/SPEC-0048-annotated-export-proposal.md","text":"已核對workspace/index/Normal語意；現有development gate exit0，router另有layout/validation BLOCKED。候選manifest與新功能runtime未驗證。"},"PROPOSAL-001":{"id":"PROPOSAL-001","kind":"candidate","source_ref":"specs/SPEC-0048-export-annotated-data.md#recommended-improvements","text":"P-001至P-008建議：Confirm旁按鈕，全部已標記recordings完整primary samples+intervals+manifest ZIP v1；保留draft/provisional與未知單位；背景串流與原子提交。尚未採用。"},"SCOPE-001":{"id":"SCOPE-001","kind":"accepted","source_ref":"codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input","text":"在Studio專案獨立提出匯出所有已標記資料的方案與規格，供後續一筆recording確認。"},"SCOPE-002":{"id":"SCOPE-002","kind":"accepted","source_ref":"codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input","text":"只做方案文件，不改產品、訓練、來源或其他模型/韌體/UI scope，保留既有dirty changes。"}},"item_bindings":{"FACT-001":[],"PROPOSAL-001":[],"SCOPE-001":["REQ-001","REQ-002","DEC-001"],"SCOPE-002":["REQ-003","DEC-002"]},"kind":"saved","reply_sha256":"4be4fa0a3a7dc7cf6b6a34ec59627ff99aa893df8692455948544a6a30ef0246","reply_stage":"prepared-until-host-stop","reviewed_sources":["architecture/designs/SPEC-0048-annotated-export-proposal.md","codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input","specs/SPEC-0048-export-annotated-data.md#recommended-improvements"],"source_ref":"spec-governance/REPLY-annotated-export.md","summary":"完成本輪初步方案文件；ZIP完整primary量測與標記候選、真值/索引/來源/單位、原子背景匯出、架構matrices及驗證規劃。使用者僅要求先提案；候選未採用，無產品授權。現況gate通過而新功能與較新layout/validation gates未通過；三項既有修改hash未變。","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"initial-delegation"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"4c79148b648939a9243f9b9dda290de62aad23ea6cd522bafe520b82d623ab47","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"f0c66f98730d06967adc564cdc60d29903b970a0347812071abb24c072bb88e6","previous_snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","recorded_at":"2026-10-27T09:54:24.266307+00:00","relationships":[],"revision":4,"snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
```
<!-- spec-audit:end -->
