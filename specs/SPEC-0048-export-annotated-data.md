---
spec_version: 1
spec_id: SPEC-0048
revision: 7
status: confirmed
change_set: export-annotated-data
working_id: WORKING-SPEC-6bfcf59ad980-export-annotated-data
task_ref: 01a17cb2-f497-74b2-9249-15b21a1071fc
---
# 匯出已標記資料：具體修改方案

2026-10-27 建立；2026-10-29 依註解及單筆自含檔案討論修訂。**使用者已採用每筆錄波自含JSONL方案，保留確認後才可匯出；尚未授權產品實作。** 本次僅保存方案與規格，不修改產品程式、不執行模型訓練。

## Problem

使用者要求在 Annotate & Classify 的 `Confirm All Annotation Sets` 旁增加匯出所有已標記資料，供另一分析任務先用一筆 recording 確認碰撞／正常動作區段。一般 `.dicsproj` 不內嵌完整波形；Replay CSV 依賴模型與目前所選 recording，無法直接滿足需求。

來源：`codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input`。委派明確要求先提出方案。ZIP為最初候選；使用者於2026-10-29明確回覆「採用」，採用上一輪每筆自含JSONL檔案規劃（Source: user:adopt-jsonl-file-plan）。

## Solution

新增 `Export Annotated Data…`，匯出**當前 session 中，至少有一個顯式 annotation 的全部 recordings，各自完整的對齊量測**，連同標記、mapping、確認狀態及來源追溯資訊，每筆錄波各自輸出一個自含 `.annotated.jsonl`，同檔包含完整量測及完整區間標記；全部錄波放入一次匯出的新資料夾。這是使用者已採用的交付規格，取代原本CSV+JSON分檔ZIP候選。僅在 Confirm All Annotation Sets 已成功、確認狀態仍有效時開放匯出；未確認或仍有 provisional 不得匯出。匯出本身不呼叫 Confirm，不依賴 Learning 或 Qualification。

每個檔案均可單獨交付分析，不需要同批其他檔案、原始CSV、manifest或README sidecar；不宣稱可由Studio直接Open、不取代`.dicsproj`。匯出操作仍是全部已確認recordings；分析者只需挑其中一個檔案分析，無須增加匯出範圍選項。

## User Stories

- 人工標記者不必先訓練即可交付每個事件前後完整量測。
- 分析者能對回 sample index、來源訊號、速度／offset、插值點，區分 provisional、整組確認、Ignore、推導 Normal 與未標記背景。
- 失敗／取消不改動標記、來源或先前成功匯出的目的檔。

## Requirements

REQ-001…REQ-003保留原方案任務邊界，REQ-004為確認後匯出限制，REQ-005…REQ-010將本次已採用的檔案與交付行為正式化。P-001…P-008描述對應方案；平台／效能與pre-code架構仍須後續gate，採用不等於已實作或已驗證。

| ID | Requirement |
|---|---|
| REQ-001 | 提出在 Confirm All Annotation Sets 旁匯出所有已標記資料的具體方案與規格。 |
| REQ-002 | 交付可連結標記與對應量測的資料，保留 IMU／訊號／索引與標記狀態，供後續分析。 |
| REQ-003 | 本輪只做文件，不改產品、訓練或來源，不延伸模型／韌體／其他 UI 重構；保留現有未提交修改。 |
| REQ-004 | Export Annotated Data 只在 Confirm All Annotation Sets 成功且確認狀態仍有效後可執行；此前灰色禁用。標記／mapping 修改使確認失效後立即再次禁用，須重新確認；controller 入口亦拒絕未確認請求。 |
| REQ-005 | 每筆recording輸出一個獨立.annotated.jsonl；同檔包含header、annotation records、完整samples blocks、end/count/digest，無須其他recording、原始CSV、manifest或README sidecar即可解讀。 |
| REQ-006 | 檔案保存來源basename/worksheet、rate、速度/offset、實際單/雙IMU與Accel/Gyro通道、mapping與primary view、單位可信度、確認狀態及插值/來源row追溯；未知資訊明列unknown/null，不推測或補零。 |
| REQ-007 | 保存完整primary時間軸全部樣本、有限數值精度與原時間起點，不降採樣、不正規化、不重新濾波；區間採0-based半開索引，保留顯式多重語意及既有政策推導Normal，Ignore/未標記/Normal互相區別。 |
| REQ-008 | 每檔JSONL採UTF-8/LF；header及end恰一次，annotation在samples之前；樣本分塊位置陣列，欄名僅在header對應，不逐樣本重複標記文字。end的count/digest須覆蓋header至end前bytes；缺end、錯序、錯count/hash或索引不連續均不得當完整有效檔案。 |
| REQ-009 | 一次匯出涵蓋全部有效confirmed recordings到新批次資料夾；每檔可單獨交付，不受目前selector限制。只有全部檔案完成後才發佈新目錄，不覆寫既有輸出；失敗/取消不得留下宣稱成功的部分批次。 |
| REQ-010 | 背景逐筆逐塊匯出、顯示進度並提供取消；不在UI thread逐樣本格式化，不建全量文字/波形副本。快照期間拒絕會改資料的命令及互斥工作，terminal清理busy；不更改來源、標記、確認狀態、Learning結果或既有project/Replay/model格式。 |

## Decisions

| ID | Decision | Source |
|---|---|---|
| DEC-001 | 在本專案建立獨立方案規格，不沿用其他演算法研究或 SPEC-0047。 | codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input |
| DEC-002 | 本輪不改產品、不訓練、不改來源，保留 dirty changes。 | codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input |
| DEC-003 | 匯出 eligibility 必須依目前有效的整組確認狀態；取代原候選「draft/provisional 可匯出」。使用者所述反白解讀為灰色 disabled。 | user:response-annotations-confirm-gate；Annotation 1 |
| DEC-004 | 採用每筆錄波一個自含.annotated.jsonl：基本資訊、完整區間、完整量測與完整性資料同檔，全部匯出到新批次目錄，任一單檔可獨立交付。原分檔ZIP推薦被取代；採用不授權產品實作。 | user:adopt-jsonl-file-plan（使用者：採用） |

## Current state and source evidence

下列路徑相對 `src/dual_imu_collision_studio/`，本輪重新核對，行號會隨後續修改移動。

| 位置 | 事實與影響 |
|---|---|
| `qml/Main.qml:625` | Confirm 在頁首 RowLayout 右端，呼叫 studio.confirmAnnotations()；新按鈕可緊接其後。 |
| `adapters/desktop/controller.py:3290` | confirmAnnotations 驗證所有 recording、將 provisional=false、清除提案來源並建立 confirmed workspace。途中失敗也可能已替換前面的 tuple；匯出須保存當下真實狀態，不自行修正。 |
| `controller.py:5001,5551,6020` | project serializer fingerprint 所有來源但不存波形；annotation serializer 有完整 identity/provenance；recording builder 可讀整段 arrays。不得直接用整個 project document 代替資料包。 |
| `domain/data_workspace/model.py` | AnnotationInterval 有索引、reason、provisional、source_recording_id/source_cycle_index、interval_id；Normal 不能顯式建立。Recording 支援單 IMU，每 sensor 3/6 軸；ImportedSamples 有 interpolated_indices。 |
| `domain/data_workspace/service.py:283,335` | 完整確認至少兩 Cycle且各事件數一致，禁止非法重疊／跨中斷；Normal 在 Cycle 內扣除事件、Ignore與碰撞起點後含截止樣本的150ms response。依本次使用者限制，完整確認成功且仍有效才允許匯出；不再提供 draft 匯出路徑。 |
| `controller.py:835` | 只有 confirmed workspace 才顯示 derived Normal。 |
| `adapters/tabular/reader.py:65–194` | 轉秒／固定率時間、修補1–3缺樣、可裁末尾不完整列並保留warning。Studio 索引對應 repaired timeline，不能直接當原檔列號。 |
| `controller.py:2543–2574,2687–2809` | mapping 保留 raw/filtered欄位、per-signal設定；primary選 raw或缺raw時filtered。signal mapping有source_sha256，legacy未必有。沒有權威逐訊號單位欄位。 |
| `controller.py:1902`、`adapters/desktop/replay_writer.py` | 既有QRunnable／queued completion與same-folder tmp、fsync、replace模式可參考；Replay admission依賴candidate且限制部分single-IMU，不適用本功能。 |

已讀 AGENTS.md、manifest/adoption/ARCHITECTURE/baseline、designs來源、兩份 proposed ADR，及 SPEC-0006、0024、0041、0047。現有schema/standard=2.2.0、baseline零項；不把任何 proposed ADR 改accepted。env_sensing/SPEC-0105不是本功能契約。

## Recommended improvements

### P-001：按鈕及啟用（已採用）

在 Confirm 右側新增 `Export Annotated Data…`，objectName建議`exportAnnotatedDataButton`，沿用PaddedButton。窄視窗允許頁首動作區換行，保留Confirm後的閱讀順序，需確認文字完整可見。

只有 Confirm All Annotation Sets 已成功、`annotationsReady=true`、存在一致的 confirmed workspace、mapping／樣本可用且無互斥工作時啟用。未確認、確認失敗、只有局部非 provisional 標記、或 provisional-only 時，按鈕一律灰色 disabled；tooltip 提示先完成 Confirm All Annotation Sets。標記／mapping 修改使既有確認失效後立即禁用，重新確認成功才恢復。**不要求 Learning、數值型別、模型或 Qualification**。QML 與 controller command 都執行相同確認 guard；對話框回傳後及快照建立前重新檢查，不能用舊狀態放行。任何 session 項目造成 Confirm All 失敗時，不能以略過該項目或只匯出局部資料規避條件。

開本機輸出資料夾選擇對話框；在選定位置建立新的`<project-stem>_annotated_<YYYYMMDD_HHmmss>_<export-id-short>`資料夾，未命名用studio。避免覆寫既有批次，名稱已存在時換唯一suffix。取消不改state；回傳後重新檢查admission，accepted時捕捉快照。顯示recording/rows數量、確認完成狀態、進度、取消及完成資料夾完整路徑；不提供含provisional的匯出模式。

### P-002：所有已標記的範圍（已採用行為；實作設計待gate）

「所有」是當前session全部已匯入recordings／worksheets，不是硬碟搜尋，也不限目前selector。每份有顯式annotation者輸出0…N-1全部樣本及所有實際mapped primary channels；不截事件／Cycle、不降採樣、不取畫面envelope、不刪Ignore或未標記背景。

由目前有效的 confirmed workspace 與對應 session metadata 建立快照，保留 identity、reason 與當下已保存的 provenance 欄位。schema 可保留 provisional 等欄位以明確表示狀態，但正常匯出必須 `session.annotations_ready=true`、`has_provisional=false`，且完整驗證通過。Confirm 已清除的舊提案來源不能重建或宣稱仍保存。另存 mapping_confirmed 與逐recording完整驗證狀態。**provisional=false只代表不是自動提案，不能單獨當作整組已確認或ground truth**；系統無獨立持久per-recording confirmation，不捏造此旗標。有效的局部validation不能冒稱Confirm All完成。

有效 Confirm All 已要求所有 recording 有完整標記，正常包應涵蓋整份已確認 workspace；每檔 header 中 batch 的 excluded_recordings 正常為空，不得藉排除尚未確認項目開放匯出。既有 schema 的 source reference 欄位如仍有資料須忠實保存，不重建 Confirm 已清除的內容。不更改project dirty、選取、history、模板或Learning結果。未提交的拖拉先完成／取消才捕捉。

### P-003：每筆錄波一個自含 JSONL（已採用行為；實作設計待gate）

每筆使用一個UTF-8 `.annotated.jsonl`。JSONL採每一實體行一個可獨立解析的JSON物件，可用Python標準json模組逐行處理；不需新的Parquet/HDF5/streaming JSON依賴。這是給程式分析用，Excel直接檢視不是本期的優先用途。

```text
project_annotated_20261029_153000_a12b34/
  r0001_recording_A.annotated.jsonl
  r0002_recording_B_worksheet_1.annotated.jsonl
  r0003_recording_C.annotated.jsonl
```

檔名保留清理過的來源stem與worksheet，前置export-local序號避免同名衝突與不安全路徑字元。session recording_id、原basename、worksheet仍完整寫入header；export_id+recording_id是該包穩定鍵。使用者只交付其中一個檔案，分析者就能取得該筆的量測、標記與解讀必要資訊；不用再尋找CSV/JSON配對。

每檔固定順序，只有一個header及end，中間零或多個annotation與至少一個samples block：

| record type | 出現位置／數量 | 內容 |
|---|---|---|
| `header` | 第一行，恰一次 | 版本、來源／條件、確認狀態、通道描述、mapping／處理方式、索引／Normal政策、batch摘要 |
| `annotation` | header後、第一個samples前，一區間一行 | 原顯式Cycle/Pick/Put/Collision/Ignore及獨立derived Normal、identity、半開範圍、reason與provenance |
| `samples` | annotation結束後，依時間順序分塊 | `rows`二維數字／布林／null陣列，依header.columns順序，不在每樣本重複長欄名 |
| `end` | 最後一行，恰一次 | 實際row/interval/block counts、前面全部LF結尾位元組的SHA-256及完成標記 |

沒有end、digest/count不符、end後仍有內容、重複header/end、annotation出現在samples後、sample index缺號或重複，reader均拒絕當作完整有效檔案。end不能包含自身hash，digest範圍精確定義為第一行起至end之前（含各行LF）的UTF-8 bytes；所有行以LF結尾。JSON文字中的換行須escaped，不能產生額外record。拒絕NaN/Infinity，保留可round-trip的有限浮點精度。

每個檔案不依賴批次總manifest、README或另一筆recording；全部解讀規則放入header的版本化欄位。batch只保留export_id、recordings_total、ordinal、session確認狀態等摘要，不作讀取本檔所必需的外部reference。

V1仍只輸出annotation使用的**primary view**；raw/filtered已映射但未匯出的view在header明列exported=false與理由。application-filtered只保存設定／係數與warmup，不重算濾波、不匯出模型／prediction／Score／threshold。

### P-004：header、samples與完整性契約（已採用行為；實作設計待gate）

| 區塊 | 必要欄位／語意 |
|---|---|
| schema | type=header、format=studio-annotated-recording、schema_version=1、export_id、UTC created_at、Studio version、snapshot時刻 |
| batch/confirmation | recordings_total、ordinal、session.annotations_ready=true、mapping_confirmed=true、has_provisional=false、完整validation結果；所有批次檔案均複製自同一快照 |
| recording/source | recording_id、display_name、source basename、worksheet、row_count、sample_rate_hz、robot_speed_mm_s、collision_offset_mm、single_sensor；來源歷史指紋與capture stage，缺少則null/not_recorded；不重新hash後冒充import指紋 |
| timeline/provenance | data_view=studio_imported_aligned、header_row/data_start_row、原time_column/unit/fixed_rate、time_origin、import warnings、插值政策與source row定義 |
| columns | 每個row位置對應column_id、value_type、unit/unit_status/evidence；IMU欄另有sensor、signal_kind、axis、source_column、source_mapping_role與configured_preprocessing |
| mapping/views | 原primary/signals/raw/filtered選擇、single-IMU、已存filter設定；明列alternate view是否實際匯出，不計算新訊號 |
| policy | index_base=0、interval_convention=[start_index,end_index)、同一imported timeline、Normal政策與collision_response_window_s=0.150；Cycle是容器、Ignore是排除、未標記背景不自動當Normal |
| end | type=end、complete=true、sample_count、annotation_count、sample_block_count、content_sha256；數量須等於header預期與實際stream |

不預設輸出絕對來源路徑。只要已載入且確認仍有效，即使原檔在磁碟變更／缺失，仍交付當下已確認的完整快照；歷史指紋capture stage如實標示，不冒稱已重新比對磁碟來源。樣本及區間同檔且digest覆蓋兩者。

samples.rows按columns排列，前五個位置固定：

```text
sample_index, time_s, source_data_row, is_interpolated, discontinuity_before,
internal.ax, internal.ay, internal.az, internal.gx, internal.gy, internal.gz,
external.ax, external.ay, external.az, external.gx, external.gy, external.gz
```

這是**位置對應示意，非CSV header**；真正columns只列存在的IMU與訊號。每sensor加速度XYZ後角速度XYZ的已選子集；single-IMU不補另一顆零值，gyro-only是gx/gy/gz。不依3欄shape猜種類；legacy無證據時c0/c1/c2+unknown。未知物理單位null+unknown，不能猜g、m/s²或deg/s。

數值取完整`_samples`，不降採樣／正規化／換單位／轉target float32。time_s保留原起點，固定率生成時間標generated。sample_index連續0…N-1，對應annotation同一修補時間軸。每個block的rows長度上限K，暫以4096 rows作候選benchmark起點，實際選值待量測；**block分塊不是降採樣**，所有row均保留。

非插值index i：source_data_row=`data_start_row+i-count(inserted_index<i)`；插值點該值為JSON null，is_interpolated=true。來源row為1-based表格row而非CSV實體換行數。裁切末尾不完整列與warnings保留，discontinuity_before原樣；缺marker用false並說明默認來源。

分析讀取可先讀header及小量annotation lines，知道條件、碰撞區間與Normal，再逐塊計算或擷取時間窗。檔案沒有隨機存取index，找後段仍可能需順序掃描；這是程式I/O成本，不需要把全部樣本逐行呈現在模型上下文。若完整性尚未掃到end，只能稱preview，不能宣稱整檔digest已驗證。

### P-005：標記與Normal（已採用行為；實作設計待gate）

同一JSONL檔案以`type=annotation`、`origin=explicit|derived`區分來源。每區間保留`interval_id,kind,start_index,end_index,reason,provisional,source_recording_id,source_cycle_index`，derived Normal另附policy；不壓成每列單一class，以保留Cycle+事件等多重語意。以索引[start,end)對應同檔samples，不重複為每個樣本填入長標記或Ignore原因。

僅在session.annotations_ready=true、有一致confirmed workspace且snapshot仍通過完整驗證時，呼叫現有workspace Normal推導，附derived=true、policy identity與collision_response_window_s=0.150。未確認時整個匯出 command 拒絕，不交付缺 Normal 的 draft 包；ready=true 卻仍有 provisional／不一致或無法完整推導時整包失敗，不降級為未確認輸出，不把未標記樣本補成 Normal。

Normal只在有效Cycle內，扣掉Pick/Put/Collision/Ignore及Collision onset至+150ms含截止樣本的response；現有方法也排除更長的Collision annotation，並clip至Cycle／中斷邊界。**不修改Collision本身end_index**。Ignore是有原因的排除；未標記事件背景不新增假annotation；Cycle本身不代表正常或碰撞真值。

索引權威採0-based半開`[start,end)`。輔助時間可寫start_time_s=time[start]、last_included_time_s=time[end-1]、end_boundary_time_s=time[end]；end=N時後者null，不以+1/fs假造邊界。

結構無效（id空／重複、0≤start<end≤N不成立、通道／時間不對齊或非有限值、mapping不一致）整包失敗。完整確認條件（至少兩 Cycle、事件數一致、無 Ignore/Collision 非法重疊／跨中斷等）仍須通過；任何 snapshot 不符合時整包失敗，不交付 annotation_validation=invalid 的降級包。**使用者已確認仍不等於模型有效或碰撞判定正確**；匯出不呼叫 confirm、不修理或刪除疑義標記。

### P-006：背景串流、互斥與失敗（已採用行為；實作設計待gate）

一個QRunnable逐recording/chunk串流JSONL至同批新資料夾內的檔案，節流progress；不建全量Python list、大字串、全量sample labels或額外波形副本。metadata/annotation tuples複製成immutable snapshot，arrays借用只讀，worker不讀寫controller dictionary。詳細owner與Port見架構方案。

匯出期間可閱讀、切換recording、zoom；會改資料／mapping／annotations的command、Confirm/reference/undo/redo、Import、Open/New/Save project、Learning/Qualification與其他artifact exports互斥。controller入口和QML都guard，避免只disable按鈕可被呼叫繞過。native dialog回傳後才commit busy，不持鎖等使用者選檔。

- 非本機folder URL、目的父目錄不存在／無寫權、目標與來源路徑不安全／重疊、busy或樣本／mapping不一致，接受前拒絕，列原因。只建立新的批次資料夾，不覆寫既有檔案或目錄。
- 在選定父目錄建立唯一隱藏staging目錄；每筆在其中exclusive create，寫header/annotations/samples、增量digest、最後end，flush/fsync並close。全部recordings成功後，在同一父目錄將staging rename為先前不存在的最終目錄；rename成功才報整批完成，不以多個os.replace假稱跨檔交易。資料夾發佈前只存在未完成暫存名稱；並不宣稱斷電後目錄更新具有跨平台durability保證。
- 任一recording或write/close/fsync/rename/disk-full失敗，整批失敗，不發佈部分成品目錄；只清理由本job在已驗證staging絕對路徑內建立的檔案／目錄，既有輸出不變，顯示recording／階段／錯誤。cleanup也失敗需顯示殘留staging，不能誤報成功。禁止自動retry，不承諾強制終止／斷電後必清除。
- 取消每chunk及整批rename前檢查；rename前取消勝出，成功發佈後為已完成，不能假稱rollback。關窗先取消、defer close至terminal，不在UI thread等整段寫入。強制kill可能留tmp，不承諾crash後必清。
- terminal校驗export_id，UI thread先清busy/state再publish一次completed/failed/cancelled，成功／失敗／取消都釋放借用；不改標記與project dirty。

### P-007：取捨、效能與替代（已採用行為；實作設計待gate）

| 選項 | 收益 | 成本／犧牲 | 建議 |
|---|---|---|---|
| 每recording單一JSONL（推薦） | 同檔自含量測/標記/metadata，逐行標準json解析，先看標記再掃樣本，無新依賴 | 給程式讀取；Excel非直接表格；無random access index；數字文字略有括號成本 | 本輪新推薦候選 |
| ZIP + CSV + interval JSON | 一次打包、通用CSV | 單筆CSV不自含標記，交付單筆仍需配對檔案 | 原推薦已被單筆自含候選取代 |
| 單一JSON物件 | metadata/annotations/samples能放同檔，常見格式 | 標準json.load通常建整個document；大samples的串流及截取較不直接 | JSONL較符合本次順序分析 |
| 單一CSV每列一個class | 結構簡單 | 不能無損表達Cycle+事件、Ignore reason、provenance；仍需sidecar | 不推薦 |
| 只切事件片段 | 較小 | 遺失事件前後背景、重編index，難確認正常／假觸發 | 不滿足交付目的 |
| dicsproj+原檔 | 保留來源全部欄位 | 需重新讀取／修補對照、帶不相關結果，可能漏檔 | 現有project保留，本功能另交付 |
| Parquet/HDF5 | 二進位／型別與大型讀取有優勢 | 新依賴及reader／部署契約，目前下游未指定 | 本期不採用 |

另一任務提供10份、2,985,537rows作為規模線索，本輪未讀那些來源。N×13×8約296MiB只是最多12個IMU channels+time的既有float64數值payload估算，非CSV/ZIP大小或實測RSS。串流避免再複製同級payload，但Python格式化GIL、JSON編碼與磁碟仍可能影響互動；不宣稱背景thread必不卡。

線性O(N×C+A)時間；額外O(K×C+A+R+G)，K=chunk大小，A=annotations，R=recordings，G=插值metadata；磁碟須容納完整新批次staging與既有輸出共存；新目錄發佈不覆寫舊批次。V1不增加壓縮選項，chunk大小在對照量測前不稱最佳。沿用既有interactive-workspace p95≤100ms作互動回歸目標；新export沒有已採用的完成時間／MB/s／額外記憶體／取消延遲門檻，需後續量測與人類確認。

### P-008：實作順序（已採用行為；實作設計待gate）

1. 採用方案後確認canonical契約及Acceptance Mapping；處理已發現治理blockers，完成architecture/designs來源、render與候選design gate。
2. 先完成workspace純匯出語意、Fake/Real output Port契約、3/6channels、確認前拒絕／編輯失效／重新確認及 Normal 邊界 fixtures。
3. 實作JSONL writer、每檔end/digest及整批staging發佈與fault injection，再接snapshot worker／互斥guards，最後接QML按鈕、dialog、progress與取消。
4. 先用一筆已確認recording的單一JSONL獨立對照全部samples／intervals，再做多筆、失敗／取消、代表大資料runtime／資源測試；不訓練模型。
5. regression、single CLI architecture/render/release檢查及來源／現有dirty hashes對照。

## Architecture impact

見 [架構候選方案](../architecture/designs/SPEC-0048-annotated-export-proposal.md)：Boundary Design Table、Type/State Ownership Matrices、actual/intended edges與parent mappings、Execution/Flow/Evolution/Algorithm及Description Views影響。

L1 data_workspace擁有snapshot語意與demand-side output Port，L0協調，L3 desktop_adapter負責JSONL storage及批次staging發佈；不新增domain、不新增Learning依賴、不改project/model/Replay格式。預計新增export-annotated-data Flow、snapshot/worker型別及job state。本輪只寫rationale，未改design-data catalogs、manifest或generated pages；**候選manifest未建立／未驗證，不宣稱design PASS**。

## Acceptance Criteria

此表同時涵蓋方案及已採用產品契約；目前尚未實作，所有產品驗證均未執行。

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | 保存獨立方案，描述按鈕、admission、全session範圍與格式。 | 原始需求對照及Markdown檢視。 | 本文件P-001…P-004；方案已採用，產品驗收未執行。 |
| AC-002 | REQ-002 | 說明primary timeline／通道單位、標記狀態／Normal語意、失敗／效能及驗證。 | 對照程式證據、架構matrices與下表。 | P-004…P-008；未執行產品驗收。 |
| AC-003 | REQ-003 | 不改產品、來源或訓練，保留其他工作。 | git status/diff及產品檔SHA-256對照。 | 2026-10-29 本輪僅改兩份方案文件；原三項變更先前已 commit/push。 |
| AC-004 | REQ-004 | 方案與架構的 admission／Normal／驗證計畫均明定確認前禁用、成功確認後可用、修改後失效須再確認；不殘留 draft 可匯出的有效規則。 | 對照使用者 Annotation 1 及文件一致性檢查；產品實作後用 controller/QML 狀態轉移測試。 | 本輪只驗文件；產品測試尚未執行。 |
| AC-005 | REQ-005, REQ-009 | 在多筆已確認匯出中單獨取任一JSONL，移除同批其他檔案後，獨立reader仍能重建該筆完整metadata、intervals與N筆samples，無sidecar需求。 | PAC-002的獨立reader與scope integration tests。 | NOT RUN |
| AC-006 | REQ-006, REQ-007 | 單/雙IMU、3/6channels及gyro-only、raw/filtered primary、固定率/非零時間、缺樣修補與尾列裁切fixtures round-trip值/欄位/row provenance正確；未知單位保留unknown、缺sensor不補零。 | PAC-003/PAC-004的semantic snapshot與Real writer contract、浮點round-trip assertions。 | NOT RUN |
| AC-007 | REQ-007 | explicit interval id/kind/reason/range原樣，半開end=N合法；Normal與現有150ms含截止樣本政策等價、不改Collision end；區分Cycle/Ignore/未標記，未確認或不一致快照不降級輸出。 | PAC-004/PAC-005邊界golden fixtures與既有workspace對照。 | NOT RUN |
| AC-008 | REQ-008 | streaming reader接受正常record順序與完整counts/hash；截斷、缺end、重複header/end、end後有內容、錯digest/count、非有限值、樣本缺號/重複等均拒絕；分塊不丟任何row。 | PAC-002/PAC-006的獨立parser與故障/邊界fixtures。 | NOT RUN |
| AC-009 | REQ-009, REQ-010 | 多筆成功才出現新成品目錄；任一write/close/fsync/rename故障及commit前取消皆不發佈部分批次，既有輸出/來源byte-identical；commit後僅回完成，每job恰一次terminal且busy清除。 | PAC-006/PAC-007的Fake與Real filesystem/Qt整合、fault injection與cancel-before/after-publication tests。 | NOT RUN |
| AC-010 | REQ-010 | Export不要求Learning/model/Qualification；讀取與selector/zoom不改快照，資料mutation與互斥工作受controller/QML guard；匯出後來源、annotations與既有project/replay/model/qualification行為不變，逐塊格式化不在UI thread。 | PAC-001/PAC-007/PAC-009的call interception、QML/native smoke、來源hash與regression tests。 | NOT RUN |

## Acceptance Mapping

```json
{
  "AC-001": {
    "evidence_claims": [
      "host-semantics"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "規格/文件與host語意以結構化檢查、確定性fixture及標準reader驗證；不構成產品PASS。"
  },
  "AC-002": {
    "evidence_claims": [
      "host-semantics"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "規格/文件與host語意以結構化檢查、確定性fixture及標準reader驗證；不構成產品PASS。"
  },
  "AC-003": {
    "evidence_claims": [
      "host-semantics"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "規格/文件與host語意以結構化檢查、確定性fixture及標準reader驗證；不構成產品PASS。"
  },
  "AC-004": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units",
      "state-transition",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Windows Python/Qt與本機filesystem之匯出語意，以domain/parent契約、Fake/Real adapter及獨立reader驗證；不宣稱硬體、即時或已量測效能。"
  },
  "AC-005": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units",
      "state-transition",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Windows Python/Qt與本機filesystem之匯出語意，以domain/parent契約、Fake/Real adapter及獨立reader驗證；不宣稱硬體、即時或已量測效能。"
  },
  "AC-006": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units",
      "state-transition",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Windows Python/Qt與本機filesystem之匯出語意，以domain/parent契約、Fake/Real adapter及獨立reader驗證；不宣稱硬體、即時或已量測效能。"
  },
  "AC-007": {
    "evidence_claims": [
      "host-semantics"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "Windows Python/Qt與本機filesystem之匯出語意，以domain/parent契約、Fake/Real adapter及獨立reader驗證；不宣稱硬體、即時或已量測效能。"
  },
  "AC-008": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units",
      "state-transition",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Windows Python/Qt與本機filesystem之匯出語意，以domain/parent契約、Fake/Real adapter及獨立reader驗證；不宣稱硬體、即時或已量測效能。"
  },
  "AC-009": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units",
      "state-transition",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Windows Python/Qt與本機filesystem之匯出語意，以domain/parent契約、Fake/Real adapter及獨立reader驗證；不宣稱硬體、即時或已量測效能。"
  },
  "AC-010": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units",
      "state-transition",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Windows Python/Qt與本機filesystem之匯出語意，以domain/parent契約、Fake/Real adapter及獨立reader驗證；不宣稱硬體、即時或已量測效能。"
  }
}
```

## Validation and acceptance plan（尚未執行）

已採用行為正式對應下列AC與Acceptance Mapping；PAC保留細分測試設計，均不代表已有測試或runtime PASS。

| Proposed AC | 方案／邊界 | 可重現方法 | 明確通過條件 | Evidence |
|---|---|---|---|---|
| PAC-001 | P-001/P-002；L0/QML | 新tests/modules/studio_application/test_annotated_data_export.py及test_annotated_data_export_qml.py；native desktop窄視窗／font scale | empty／draft／provisional／Confirm失敗均灰色禁用且controller拒絕；一筆含至少兩有效Cycle的recording確認成功後無模型也可匯出；編輯後再禁用，重新確認後恢復；對話框期間失效亦拒絕；Confirm右側可見、文字不截斷 | JUnit、native screenshot／步驟 |
| PAC-002 | P-002/P-003；workspace/writer | 新tests/flows/export-annotated-data；多份已全部確認、同檔多worksheet，選第二份；另建一份未確認致Confirm All失敗案例；獨立逐行json reader（單獨讀一個JSONL，不載入同批其他檔案） | 恰包含全部confirmed recordings的完整N rows；不受selector影響，excluded正常為空；Confirm All失敗時完全拒絕；每檔header/annotations/完整rows/end自含且counts/digest一致；不需sidecar；移走其他檔案仍可解析 | artifact hash、獨立reader assertions |
| PAC-003 | P-004；snapshot/Port | 新tests/modules/data_workspace/test_annotated_export_snapshot.py與writer contract：single internal/external、accel、gyro-only、6ch、raw/filtered三模式、unknown units | round-trip等於primary arrays；無換單位／濾波／補零；descriptor及alternate-view未匯出理由正確 | golden JSONL header/sample blocks、array assertions |
| PAC-004 | P-004/P-005；indices | fixed-rate、非零time、1–3缺樣、尾列裁切、end=N、非法range/id fixtures | index連續，source row正確、插值null；warnings保留；半開無off-by-one；非法結構失敗 | boundary/property assertions |
| PAC-005 | P-005；truth | draft、provisional-only、未滿兩Cycle／非法overlap、確認後修改及再確認、confirmed150ms含截止樣本及長Collision | 未確認／失效一律拒絕；snapshot不一致整包失敗不降級；已確認explicit原樣、匯出不confirm；Normal等於既有方法、Collision end不改 | semantic assertions、前後snapshot對照 |
| PAC-006 | P-006；writer/fault | Fake與Real adapter reusable contract：disk-full/write/close/fsync/rename失敗、同名批次目錄、非localURL、來源path/case alias、cancel before/after publish、缺end/錯digest/錯序 | 每job一次terminal；不發佈部分batch、不覆寫既有輸出；每檔無end/錯digest reader拒絕；cleanup失敗可見；不寫來源 | fault fixtures、file hashes、事件捕捉 |
| PAC-007 | P-006；session concurrency | accepted後呼叫各mutation／Open/New/Save／Learning/Qualification／其他exports，另select/zoom，native關窗取消 | controller及QML互斥；閱讀可用；busy每terminal清；snapshot穩定；無worker改UI／懸空callback | interaction tests與native smoke |
| PAC-008 | P-007；large export | 一筆單檔先對照；再用2,985,537-row規模或等價synthetic、固定C/A/G，鄰近chunk／bulk baseline比較；Windows ETW/WPR+domain markers | zero dropped rows／labels；無全量copy／文字；依既有p95≤100ms回歸目標；完整記錄peak/throughput/cancel。機型及新資源門檻未定者BLOCKED | immutable run、native trace、parser結果 |
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
| REQ-004 | depends_on | DEC-003 |
| AC-004 | depends_on | REQ-004 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |
| AC-003 | depends_on | REQ-003 |
| REQ-005 | depends_on | DEC-004 |
| REQ-006 | depends_on | DEC-004 |
| REQ-007 | depends_on | DEC-004 |
| REQ-008 | depends_on | DEC-004 |
| REQ-009 | depends_on | DEC-004 |
| REQ-010 | depends_on | DEC-004 |
| AC-005 | depends_on | REQ-005 |
| AC-005 | depends_on | REQ-009 |
| AC-006 | depends_on | REQ-006 |
| AC-006 | depends_on | REQ-007 |
| AC-007 | depends_on | REQ-007 |
| AC-008 | depends_on | REQ-008 |
| AC-009 | depends_on | REQ-009 |
| AC-009 | depends_on | REQ-010 |
| AC-010 | depends_on | REQ-010 |

SPEC-0006為原子匯出模式參照、SPEC-0024為identity、SPEC-0041為通道契約；均不重開。SPEC-0047與外部env_sensing/SPEC-0105不是此功能採用／執行依據。

## Out of Scope

本輪產品source/tests/runtime/generated執行內容或訓練；模型改造、旋轉補償、韌體；來源錄波修改、硬碟搜尋、原檔bytes／未映射欄位備份；匯出檔直接Open Studio；project schema migration；重建已遺失歷史proposal來源；其他標記UI重構或分析報告。

## Open Decisions

None.

## Remaining uncertainties

使用者於本輪明確回覆「採用」（user:adopt-jsonl-file-plan），確認上一輪單筆自含JSONL與完整資料交付方案；REQ-004與REQ-005…REQ-010為已採用功能契約，沒有待答的格式選擇。這不代表產品開始執行、演算法/架構例外已批准或功能已通過驗收。

chunk大小（4096僅benchmark起點）、Windows機型/profile及實際RSS/throughput/取消延遲仍待執行階段量測；不將未採用的效能數值當功能承諾，不宣稱效能winner或runtime PASS。功能要求完整、正確、可取消、背景分塊與不變更來源；若實作發現需要改動可見行為再依同一SPEC重開討論。新Flow/Type/State/Port及validation profile仍須在產品修改前通過治理gate。

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

### DISC-002：確認後才可匯出與單一交付檔案澄清
- Source：user:response-annotations-confirm-gate；Annotation 1／2。
- User answer：Confirm All Annotation Sets 後才可執行 export；確認前反白。將反白解讀為灰色 disabled，寫入 REQ-004／DEC-003。
- Impact：取代原 draft/provisional 可匯出候選，連同編輯後失效、Normal與snapshot拒絕、測試案例一起修訂；不改產品。
- User question：這樣方便閱讀嗎？原以為一個檔案就含區間標記。
- Response：單一ZIP已含CSV量測及JSON區間，程式可直接按index對齊，使用者無須手動合併；單獨CSV尚無標記欄。沒有將此詢問當成改單一CSV的採用決策。
- Superseded：DISC-001 中 draft/provisional 可匯出的候選僅留歷史，已不適用。

### DISC-003：每筆錄波單一完整檔案的具體規劃
- Source：user:self-contained-file-layout；承接使用者上一輪關於token及只給其中一筆的詢問。
- User request：這樣檔案你會如何規劃？要求具體方案，不是採用或實作授權。
- Candidate：每筆.annotated.jsonl含header、區間records、完整samples blocks及end/digest；全部confirmed recordings放新批次目錄，任一檔可單獨交付；取代原分檔ZIP推薦。
- Rationale：不用配對sidecar；區間只存一次，保留多重語意；標準json逐行讀取，不需把原始數據全貼進上下文。token與耗時不保證固定上限，仍取決實際送入模型內容與處理方式。
- Delta：P-001目的地選擇、P-003/P-004格式、P-005標記records、P-006整批發佈、比較與驗證同步；既有確認後才匯出限制不變。
- Status：candidate，未採用、未實作、未commit/push。DISC-002對原ZIP的說明僅作歷史。

### DISC-004：使用者採用單筆自含JSONL方案
- Source：user:adopt-jsonl-file-plan。
- User answer：採用。
- Scope：指向上一輪完整呈現的每筆.annotated.jsonl，基本資訊/區間/完整量測/完整性同檔、任一檔可單獨交付；保留Confirm All後才可匯出。
- Result：DEC-004與REQ-005…REQ-010正式化，新增AC-005…AC-010並補Acceptance Mapping；原CAND-FILE-001已採用，原ZIP候選被取代。
- Authorization：只有規格採用，未收到本次「開始執行」；不修改產品、不訓練、不自動commit/push。

## Scope and Authorization

使用者已明確採用本規格的JSONL檔案與交付行為；本輪執行spec-governance reconcile/materialize保存同一SPEC。採用不是產品實作授權。規格確認完成後，等待使用者「開始執行」才能修改產品；既有architecture/validation blockers保留，不能用規格確認取代design/runtime/release gates。

## Revision History

| Revision | Change |
|---|---|
| 1 | 本任務獨立開始：匯出所有已標記資料，僅方案。 |
| 2 | 保存ZIP v1／primary timeline、draft/provisional／Normal、欄位／索引、原子背景匯出、架構矩陣與驗證方案；未採用、未授權實作。 |
| 3 | 區分本輪方案交付無待答問題，與未來採用／效能驗證的未知項；不強迫澄清或升格候選。 |
| 4 | 將方案後續未知項維持獨立段落，符合owner對Open Decisions空集合的解析格式。 |
| 5 | 2026-10-29：採用確認後才可匯出／確認前灰色禁用，修正編輯失效、snapshot/Normal及驗證案例；當時澄清原ZIP含量測與標記。 |
| 6 | 2026-10-29：提出每筆自含JSONL候選與對應架構/驗證計畫。 |
| 7 | 2026-10-29：使用者「採用」；正式化每筆自含JSONL交付契約、DEC-004、REQ-005…REQ-010、AC-005…AC-010與Acceptance Mapping，規格確認不授權產品實作。 |

## Current Specification

See Problem, Solution, Requirements and Acceptance Criteria above.

## Decision History

See Decisions, Discussion Context and the sourced Discussion History below.

## Pending Discussion

None.

## Completeness Gaps

- AC-001: required layer 'sil' has no project contract
- AC-002: required layer 'sil' has no project contract
- AC-003: required layer 'sil' has no project contract
- AC-004: required layer 'sil' has no project contract
- AC-005: required layer 'sil' has no project contract
- AC-006: required layer 'sil' has no project contract
- AC-007: required layer 'sil' has no project contract
- AC-008: required layer 'sil' has no project contract
- AC-009: required layer 'sil' has no project contract
- AC-010: required layer 'sil' has no project contract

<!-- spec-audit:start -->
## Discussion History

- codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input: 請在專案提出匯出已標記資料的具體修改方案；只保存方案與規格，不修改產品程式、不訓練模型；保留既有 qualified offset 修改。
- codex_delegation:01a17c53-b931-7be0-a601-a2f81c74a560/input: 提出匯出已標記資料修改方案，僅文件規格，禁止產品修改及訓練
- spec-governance/REPLY-annotated-export.md: 完成本輪初步方案文件；ZIP完整primary量測與標記候選、真值/索引/來源/單位、原子背景匯出、架構matrices及驗證規劃。使用者僅要求先提案；候選未採用，無產品授權。現況gate通過而新功能與較新layout/validation gates未通過；三項既有修改hash未變。
- spec-governance/REPLY-annotated-export.md: 完成本輪初步方案文件；ZIP完整primary量測與標記候選、真值/索引/來源/單位、原子背景匯出、架構matrices及驗證規劃。使用者僅要求先提案；候選未採用，無產品授權。現況gate通過而新功能與較新layout/validation gates未通過；三項既有修改hash未變。
- user:response-annotations-confirm-gate: 註解1：只有Confirm All Annotation Sets成功後可執行Export Annotated Data，未確認前反白。註解2：這樣方便你閱讀嗎？我以為一個檔案就包含區間標記。
- user:response-annotations-confirm-gate: Update SPEC-0048 proposal only from user annotation: allow export only after Confirm All Annotation Sets; clarify one ZIP contains samples and interval labels. No product implementation.
- spec-governance/REPLY-confirm-gate.md: 依Annotation 1新增REQ-004/DEC-003/AC-004並改P-001/P-002/P-005與測試、架構admission；確認前拒絕、確認後放行、編輯後失效。Annotation 2回答單一ZIP已含完整數據與區間，CSV本身不含標記欄。保持working、無產品修改或訓練。
- user:self-contained-file-layout: 使用者先問大量分析token，認為給其中一筆即可；上一輪答覆建議每筆錄波自含量測與標記。現在問：這樣檔案你會如何規劃？本輪具體提案，不實作、不推定格式已採用。
- user:self-contained-file-layout: Propose file layout only: one self-contained JSONL per confirmed recording, samples and annotations together. No product implementation; user asks how to plan files.
- spec-governance/REPLY-self-contained-layout.md: 回答具體檔案規劃，保存JSONL每筆自含候選；metadata/annotations置前、samples分塊位置陣列、end/count/hash，同批新目錄staging發佈，單檔獨立。保留confirmed-only，未採用格式、未改產品、未訓練。
- user:adopt-jsonl-file-plan: 採用。指向上一輪每筆錄波一個自含.annotated.jsonl、內含基本資訊/完整區間/完整量測/完整性資料的檔案方案。採用不等於產品開始執行。
- user:adopt-jsonl-file-plan: 採用。確認上一輪SPEC-0048每筆自含JSONL檔案方案；僅規格確認，不授權產品實作。
- spec-governance/REPLY-adopt-jsonl.md: 使用者採用已保存並materialize為SPEC-0048 revision7 confirmed；正式JSONL交付契約與AC/Acceptance Mapping完整，補規劃缺少的SIL layer。materialize PASS只確認規格，功能未實作/測試，產品授權false。
- 01a18593-4b40-7cb1-820e-518869e51ba1: 開始執行
- msg_0abcf28bf2889b24016ae2b515387481918ad8670e7cf5afe0: 本輪取得實際userMessage開始執行授權，依已確認SPEC-0048 r7實作JSONL匯出，不訓練/改來源。先完成admission/formatter/architecture與驗證準備，再依public seams測試和實作。

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
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"註解1：只有Confirm All Annotation Sets成功後可執行Export Annotated Data，未確認前反白。註解2：這樣方便你閱讀嗎？我以為一個檔案就包含區間標記。","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:response-annotations-confirm-gate","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"response-annotations-confirm-gate"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"c9f6adf026f8681bdc7978cc48b555554a3bf819d4bee198abe305fda249e980","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"4c79148b648939a9243f9b9dda290de62aad23ea6cd522bafe520b82d623ab47","previous_snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","recorded_at":"2026-10-29T01:50:59.028974+00:00","relationships":[],"revision":4,"snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"Update SPEC-0048 proposal only from user annotation: allow export only after Confirm All Annotation Sets; clarify one ZIP contains samples and interval labels. No product implementation.","kind":"entry-update","source_ref":"user:response-annotations-confirm-gate","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"response-annotations-confirm-gate"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"eaca12c113625773792f7ed3dad0ab30e67219ae668db380f5d26fcdb3f01d5e","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"c9f6adf026f8681bdc7978cc48b555554a3bf819d4bee198abe305fda249e980","previous_snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","recorded_at":"2026-10-29T01:51:46.543734+00:00","relationships":[],"revision":4,"snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":["AC-003","AC-004","DEC-003","REQ-004"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":["AC-003"],"added_ids":["AC-004","DEC-003","REQ-004"],"changed_ids":["AC-003"],"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"08515dfb72e77dc3d9e429ff321f1315a84c4bc7920ffeeeeaff88ecf917a9b2","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"eaca12c113625773792f7ed3dad0ab30e67219ae668db380f5d26fcdb3f01d5e","previous_snapshot_hash":"e8d9526ef95fc71292f0793ea81465537d0a6fce56bde5dc020635a2f0366cd4","recorded_at":"2026-10-29T01:53:42.248230+00:00","relationships":[{"relation":"depends_on","source":"REQ-001","target":"DEC-001"},{"relation":"depends_on","source":"REQ-003","target":"DEC-002"},{"relation":"depends_on","source":"REQ-004","target":"DEC-003"},{"relation":"depends_on","source":"AC-004","target":"REQ-004"},{"relation":"depends_on","source":"AC-001","target":"REQ-001"},{"relation":"depends_on","source":"AC-002","target":"REQ-002"},{"relation":"depends_on","source":"AC-003","target":"REQ-003"}],"revision":5,"snapshot_hash":"4d3a56af045dd9e6d8fc4dc653b829b3f66f5a8c1b9ac70ff36c15c61b08fccf","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":5,"snapshot_hash":"4d3a56af045dd9e6d8fc4dc653b829b3f66f5a8c1b9ac70ff36c15c61b08fccf","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"},"candidates":[],"completeness_review":null,"identified_items":{"ANNOTATION-1":{"id":"ANNOTATION-1","kind":"accepted","source_ref":"user:response-annotations-confirm-gate","text":"只有Confirm All Annotation Sets成功且確認仍有效後可匯出；確認前灰色disabled，取代draft/provisional匯出候選。"},"ANNOTATION-2":{"id":"ANNOTATION-2","kind":"question","source_ref":"user:response-annotations-confirm-gate","text":"詢問一檔含標記是否方便閱讀；本輪回答單一ZIP已含CSV數據與JSON區間，可直接按index讀取；不把詢問當改成單一CSV授權。"}},"item_bindings":{"ANNOTATION-1":["REQ-004","DEC-003","AC-004"],"ANNOTATION-2":[]},"kind":"saved","reply_sha256":"ebb578af500dbc2bf45a78761c517230e1afa465f4bde1da64f0910ac42ce0b4","reply_stage":"prepared-until-host-stop","reviewed_sources":["user:response-annotations-confirm-gate"],"source_ref":"spec-governance/REPLY-confirm-gate.md","summary":"依Annotation 1新增REQ-004/DEC-003/AC-004並改P-001/P-002/P-005與測試、架構admission；確認前拒絕、確認後放行、編輯後失效。Annotation 2回答單一ZIP已含完整數據與區間，CSV本身不含標記欄。保持working、無產品修改或訓練。","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"response-annotations-confirm-gate"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"690967f37393dd42cbe22ad60ce3028086250914e78080f67ba196ab37f18261","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"08515dfb72e77dc3d9e429ff321f1315a84c4bc7920ffeeeeaff88ecf917a9b2","previous_snapshot_hash":"4d3a56af045dd9e6d8fc4dc653b829b3f66f5a8c1b9ac70ff36c15c61b08fccf","recorded_at":"2026-10-29T01:54:34.782671+00:00","relationships":[],"revision":5,"snapshot_hash":"4d3a56af045dd9e6d8fc4dc653b829b3f66f5a8c1b9ac70ff36c15c61b08fccf","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"使用者先問大量分析token，認為給其中一筆即可；上一輪答覆建議每筆錄波自含量測與標記。現在問：這樣檔案你會如何規劃？本輪具體提案，不實作、不推定格式已採用。","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:self-contained-file-layout","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"self-contained-file-layout"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"7a04e14e274cc5b6dcb99bbc932d8ecb4a73f1f9075bea5c38fa8b8a469d5c5b","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"690967f37393dd42cbe22ad60ce3028086250914e78080f67ba196ab37f18261","previous_snapshot_hash":"4d3a56af045dd9e6d8fc4dc653b829b3f66f5a8c1b9ac70ff36c15c61b08fccf","recorded_at":"2026-10-29T02:01:02.568247+00:00","relationships":[],"revision":5,"snapshot_hash":"4d3a56af045dd9e6d8fc4dc653b829b3f66f5a8c1b9ac70ff36c15c61b08fccf","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"Propose file layout only: one self-contained JSONL per confirmed recording, samples and annotations together. No product implementation; user asks how to plan files.","kind":"entry-update","source_ref":"user:self-contained-file-layout","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"self-contained-file-layout"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"18c10cf074d4564fbc1913003f238dcc73a69ac7a7756b56daa9ab6310ba038c","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"7a04e14e274cc5b6dcb99bbc932d8ecb4a73f1f9075bea5c38fa8b8a469d5c5b","previous_snapshot_hash":"4d3a56af045dd9e6d8fc4dc653b829b3f66f5a8c1b9ac70ff36c15c61b08fccf","recorded_at":"2026-10-29T02:04:21.747841+00:00","relationships":[],"revision":5,"snapshot_hash":"4d3a56af045dd9e6d8fc4dc653b829b3f66f5a8c1b9ac70ff36c15c61b08fccf","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"b61ad57cbd266609d68813f2eec13da8aa7d164ff222b19d3673cc49ac067b39","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"18c10cf074d4564fbc1913003f238dcc73a69ac7a7756b56daa9ab6310ba038c","previous_snapshot_hash":"4d3a56af045dd9e6d8fc4dc653b829b3f66f5a8c1b9ac70ff36c15c61b08fccf","recorded_at":"2026-10-29T02:05:09.801824+00:00","relationships":[{"relation":"depends_on","source":"REQ-001","target":"DEC-001"},{"relation":"depends_on","source":"REQ-003","target":"DEC-002"},{"relation":"depends_on","source":"REQ-004","target":"DEC-003"},{"relation":"depends_on","source":"AC-004","target":"REQ-004"},{"relation":"depends_on","source":"AC-001","target":"REQ-001"},{"relation":"depends_on","source":"AC-002","target":"REQ-002"},{"relation":"depends_on","source":"AC-003","target":"REQ-003"}],"revision":6,"snapshot_hash":"1475d0fac384e642b7147ee95caa0d677861f433df9b977728c67e2a94149fef","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":6,"snapshot_hash":"1475d0fac384e642b7147ee95caa0d677861f433df9b977728c67e2a94149fef","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"},"candidates":[{"id":"CAND-FILE-001","impact":"取代CSV/JSON分檔ZIP推薦；改folder destination、每檔完整性及整批發佈；主流程與confirmed-only不變。","reason":"符合只交一筆及單檔含量測與標記，適合程式逐段讀取；仍需使用者採用。","source_ref":"specs/SPEC-0048-export-annotated-data.md#p-003每筆錄波一個自含-jsonlcandidate","status":"candidate"}],"completeness_review":null,"identified_items":{"CAND-FILE-001":{"id":"CAND-FILE-001","kind":"candidate","source_ref":"specs/SPEC-0048-export-annotated-data.md#p-003每筆錄波一個自含-jsonlcandidate","text":"推薦每筆.annotated.jsonl：header、區間annotation records、完整samples blocks、end/count/digest；同批新資料夾staging後發佈。任一單檔可獨立交付，未採用或授權實作。"},"FILE-QUESTION":{"id":"FILE-QUESTION","kind":"question","source_ref":"user:self-contained-file-layout","text":"使用者詢問每筆錄波同檔包含量測與標記時，檔案要如何具體規劃。"}},"item_bindings":{"CAND-FILE-001":[],"FILE-QUESTION":[]},"kind":"saved","reply_sha256":"769d6f56a619614bcc1cde14b5ac6fa52213de886319db4fe4867c5331ff6ade","reply_stage":"prepared-until-host-stop","reviewed_sources":["specs/SPEC-0048-export-annotated-data.md#p-003每筆錄波一個自含-jsonlcandidate","user:self-contained-file-layout"],"source_ref":"spec-governance/REPLY-self-contained-layout.md","summary":"回答具體檔案規劃，保存JSONL每筆自含候選；metadata/annotations置前、samples分塊位置陣列、end/count/hash，同批新目錄staging發佈，單檔獨立。保留confirmed-only，未採用格式、未改產品、未訓練。","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"self-contained-file-layout"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"a1e5350add4e5d6be8970fbd89a9adc21c403754ea0aacfe1e3ab1bf28a9a68b","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"b61ad57cbd266609d68813f2eec13da8aa7d164ff222b19d3673cc49ac067b39","previous_snapshot_hash":"1475d0fac384e642b7147ee95caa0d677861f433df9b977728c67e2a94149fef","recorded_at":"2026-10-29T02:06:18.711361+00:00","relationships":[],"revision":6,"snapshot_hash":"1475d0fac384e642b7147ee95caa0d677861f433df9b977728c67e2a94149fef","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"採用。指向上一輪每筆錄波一個自含.annotated.jsonl、內含基本資訊/完整區間/完整量測/完整性資料的檔案方案。採用不等於產品開始執行。","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"user:adopt-jsonl-file-plan","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"adopt-jsonl-file-plan"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"84ee1e2913cd079309d6e546d1ef70bad65d2784d09b48addc0a168e0989a9e2","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"a1e5350add4e5d6be8970fbd89a9adc21c403754ea0aacfe1e3ab1bf28a9a68b","previous_snapshot_hash":"1475d0fac384e642b7147ee95caa0d677861f433df9b977728c67e2a94149fef","recorded_at":"2026-10-29T02:41:31.846527+00:00","relationships":[],"revision":6,"snapshot_hash":"1475d0fac384e642b7147ee95caa0d677861f433df9b977728c67e2a94149fef","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"採用。確認上一輪SPEC-0048每筆自含JSONL檔案方案；僅規格確認，不授權產品實作。","kind":"entry-update","source_ref":"user:adopt-jsonl-file-plan","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"adopt-jsonl-file-plan"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"4263c791998ccce328ef49beb85bc77fa9c5e69d0f584c431506b27f1ba00017","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"84ee1e2913cd079309d6e546d1ef70bad65d2784d09b48addc0a168e0989a9e2","previous_snapshot_hash":"1475d0fac384e642b7147ee95caa0d677861f433df9b977728c67e2a94149fef","recorded_at":"2026-10-29T02:42:44.253460+00:00","relationships":[],"revision":6,"snapshot_hash":"1475d0fac384e642b7147ee95caa0d677861f433df9b977728c67e2a94149fef","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":["AC-001","AC-005","AC-006","AC-007","AC-008","AC-009","AC-010","DEC-004","REQ-005","REQ-006","REQ-007","REQ-008","REQ-009","REQ-010"],"conflicts":[],"continuity":"continuous","delta":{"acceptance_changes":[],"added_ids":["AC-005","AC-006","AC-007","AC-008","AC-009","AC-010","DEC-004","REQ-005","REQ-006","REQ-007","REQ-008","REQ-009","REQ-010"],"changed_ids":["AC-001"],"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"21a1979fe36915b0c1a8a9941ff861af9d16638db6235c5d063297593d5dd0a4","event_type":"reconcile","event_version":1,"open_decisions":[],"previous_event_hash":"4263c791998ccce328ef49beb85bc77fa9c5e69d0f584c431506b27f1ba00017","previous_snapshot_hash":"1475d0fac384e642b7147ee95caa0d677861f433df9b977728c67e2a94149fef","recorded_at":"2026-10-29T02:45:38.304892+00:00","relationships":[{"relation":"depends_on","source":"REQ-001","target":"DEC-001"},{"relation":"depends_on","source":"REQ-003","target":"DEC-002"},{"relation":"depends_on","source":"REQ-004","target":"DEC-003"},{"relation":"depends_on","source":"AC-004","target":"REQ-004"},{"relation":"depends_on","source":"AC-001","target":"REQ-001"},{"relation":"depends_on","source":"AC-002","target":"REQ-002"},{"relation":"depends_on","source":"AC-003","target":"REQ-003"},{"relation":"depends_on","source":"REQ-005","target":"DEC-004"},{"relation":"depends_on","source":"REQ-006","target":"DEC-004"},{"relation":"depends_on","source":"REQ-007","target":"DEC-004"},{"relation":"depends_on","source":"REQ-008","target":"DEC-004"},{"relation":"depends_on","source":"REQ-009","target":"DEC-004"},{"relation":"depends_on","source":"REQ-010","target":"DEC-004"},{"relation":"depends_on","source":"AC-005","target":"REQ-005"},{"relation":"depends_on","source":"AC-005","target":"REQ-009"},{"relation":"depends_on","source":"AC-006","target":"REQ-006"},{"relation":"depends_on","source":"AC-006","target":"REQ-007"},{"relation":"depends_on","source":"AC-007","target":"REQ-007"},{"relation":"depends_on","source":"AC-008","target":"REQ-008"},{"relation":"depends_on","source":"AC-009","target":"REQ-009"},{"relation":"depends_on","source":"AC-009","target":"REQ-010"},{"relation":"depends_on","source":"AC-010","target":"REQ-010"}],"revision":7,"snapshot_hash":"656157205ec1e7681fe4507e91111e15eb7ab94c1f286c27d562e39c5b14ac8f","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"6e533e3f397520ffc9c0d863098235cc20a487ab1f3e2f276d95dd0e5191d3ca","event_type":"materialize","event_version":1,"open_decisions":[],"previous_event_hash":"21a1979fe36915b0c1a8a9941ff861af9d16638db6235c5d063297593d5dd0a4","previous_snapshot_hash":"656157205ec1e7681fe4507e91111e15eb7ab94c1f286c27d562e39c5b14ac8f","recorded_at":"2026-10-29T02:47:07.056250+00:00","relationships":[],"revision":7,"snapshot_hash":"a5ad686914a168963ec6b5ba6d0f242a932190e4dba15d6460fc5dab5f27731e","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":7,"snapshot_hash":"a5ad686914a168963ec6b5ba6d0f242a932190e4dba15d6460fc5dab5f27731e","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"},"candidates":[{"id":"CAND-FILE-001","impact":"單筆錄波自含量測/標記/完整性，全部已確認錄波輸出新批次目錄，保留確認限制；沒有產品執行授權。","reason":"使用者在完整JSONL方案呈現後明確回覆採用。","reconciliation_ref":"specs/SPEC-0048-export-annotated-data.md#revision-7","source_ref":"specs/SPEC-0048-export-annotated-data.md","status":"accepted","user_source_ref":"user:adopt-jsonl-file-plan"}],"completeness_review":{"acceptance":{"evidence":"正式REQ-005至010對應AC-005至010，逐條方法與嵌入Acceptance Mapping；實際執行NOT RUN，平台與設計gate另待實作前完成。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"behavior":{"evidence":"header/annotations/full samples/end同檔，各recording獨立；metadata及index/units/Normal語意。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"exceptions":{"evidence":"未確認拒絕，錯序/缺end/錯digest拒絕，失敗/取消不發佈部分新目錄，不覆寫來源或舊輸出。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"goal":{"evidence":"單筆即可交付分析，量測與標記不拆檔。","source_ref":"specs/SPEC-0048-export-annotated-data.md"},"scope":{"evidence":"採用JSONL檔案方案，保留已確認後匯出；不訓練/改來源/改模型或韌體。","source_ref":"specs/SPEC-0048-export-annotated-data.md"}},"identified_items":{"CAND-FILE-001":{"id":"CAND-FILE-001","kind":"accepted","source_ref":"user:adopt-jsonl-file-plan","text":"使用者明確回覆採用，採用上一輪每筆自含JSONL、基本資訊/完整區間/完整量測/完整性同檔及單檔獨立交付方案；保留Confirm All後匯出。不授權產品實作。"}},"item_bindings":{"CAND-FILE-001":["DEC-004","REQ-005","REQ-006","REQ-007","REQ-008","REQ-009","REQ-010","AC-005","AC-006","AC-007","AC-008","AC-009","AC-010"]},"kind":"saved","reply_sha256":"6221969057ab456d9d0404f225c39eb3d72b9bd6a7210b635903e66c27a5e09a","reply_stage":"prepared-until-host-stop","reviewed_sources":["user:adopt-jsonl-file-plan"],"source_ref":"spec-governance/REPLY-adopt-jsonl.md","summary":"使用者採用已保存並materialize為SPEC-0048 revision7 confirmed；正式JSONL交付契約與AC/Acceptance Mapping完整，補規劃缺少的SIL layer。materialize PASS只確認規格，功能未實作/測試，產品授權false。","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"adopt-jsonl-file-plan"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"7f3aee81d31ffe18375d852f836e456bdb818ed9b41004f6f10368324355f6b2","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"6e533e3f397520ffc9c0d863098235cc20a487ab1f3e2f276d95dd0e5191d3ca","previous_snapshot_hash":"a5ad686914a168963ec6b5ba6d0f242a932190e4dba15d6460fc5dab5f27731e","recorded_at":"2026-10-29T02:48:44.428794+00:00","relationships":[],"revision":7,"snapshot_hash":"a5ad686914a168963ec6b5ba6d0f242a932190e4dba15d6460fc5dab5f27731e","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"goal":"開始執行","historical_entry_evidence":"not-inferred","kind":"entry","source_ref":"01a18593-4b40-7cb1-820e-518869e51ba1","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"01a18593-4ae9-7722-a397-ddd72fa2ca2a"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"8e62fd61589ab8ee7515eb3cf794736ec288762eb8407c3812a68129b28007b2","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"7f3aee81d31ffe18375d852f836e456bdb818ed9b41004f6f10368324355f6b2","previous_snapshot_hash":"a5ad686914a168963ec6b5ba6d0f242a932190e4dba15d6460fc5dab5f27731e","recorded_at":"2026-10-29T02:54:45.172614+00:00","relationships":[],"revision":7,"snapshot_hash":"a5ad686914a168963ec6b5ba6d0f242a932190e4dba15d6460fc5dab5f27731e","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
{"affected_ids":[],"conflicts":[],"continuity":"continuous","delta":{"added_ids":[],"changed_ids":[],"discussion":{"binding":{"revision":7,"snapshot_hash":"a5ad686914a168963ec6b5ba6d0f242a932190e4dba15d6460fc5dab5f27731e","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"},"candidates":[],"completeness_review":null,"identified_items":{"EXECUTE-0048":{"id":"EXECUTE-0048","kind":"fact","source_ref":"01a18593-4b40-7cb1-820e-518869e51ba1","text":"實際本輪userMessage內容為開始執行；授權SPEC-0048 revision7，非新需求。"}},"item_bindings":{"EXECUTE-0048":[]},"kind":"saved","reply_sha256":"8fa92fd2fc12fd8384920c1c502c8f7a4c6ddb9b259a3219309b6ad861a551e7","reply_stage":"prepared-until-host-stop","reviewed_sources":["01a18593-4b40-7cb1-820e-518869e51ba1"],"source_ref":"msg_0abcf28bf2889b24016ae2b515387481918ad8670e7cf5afe0","summary":"本輪取得實際userMessage開始執行授權，依已確認SPEC-0048 r7實作JSONL匯出，不訓練/改來源。先完成admission/formatter/architecture與驗證準備，再依public seams測試和實作。","task_ref":"01a17cb2-f497-74b2-9249-15b21a1071fc","turn_id":"01a18593-4ae9-7722-a397-ddd72fa2ca2a"},"removed_ids":[]},"epoch":"a47d248f7bc04da2a1a08a170a230298","event_hash":"152d9d1cef781c63f6fbb1e4dcadfe729947c4d0092c6c5e301fad3dd09ed3f2","event_type":"discussion","event_version":1,"open_decisions":[],"previous_event_hash":"8e62fd61589ab8ee7515eb3cf794736ec288762eb8407c3812a68129b28007b2","previous_snapshot_hash":"a5ad686914a168963ec6b5ba6d0f242a932190e4dba15d6460fc5dab5f27731e","recorded_at":"2026-10-29T02:54:52.958641+00:00","relationships":[],"revision":7,"snapshot_hash":"a5ad686914a168963ec6b5ba6d0f242a932190e4dba15d6460fc5dab5f27731e","verdict":"PASS","working_id":"WORKING-SPEC-6bfcf59ad980-export-annotated-data"}
```
<!-- spec-audit:end -->
