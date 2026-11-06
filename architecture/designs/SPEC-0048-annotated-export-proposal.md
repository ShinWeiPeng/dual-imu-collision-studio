# SPEC-0048：已標記資料匯出架構候選方案

日期：2026-10-27；2026-10-29 依使用者註解修訂 admission。狀態：**proposed；僅供方案審查**。已確認限制：成功執行 Confirm All Annotation Sets 後才能匯出，未確認／確認失效時灰色禁用。其餘候選見 [SPEC-0048](../../specs/SPEC-0048-export-annotated-data.md)。本文件未加入 design collection，未變更 manifest 或 generated views；不代表已通過新功能的 design gate。

2026-10-29 採用更新：使用者於 `user:adopt-jsonl-file-plan` 明確回覆「採用」，採用每筆自含 JSONL 的功能交付規格及確認後匯出限制。此處 L0/L1/L3 owner、型別／Port／執行細節仍為待 pre-code gate 的設計，不將檔案方案採用冒充 architecture gate、效能驗證或 ADR acceptance；也不授權產品實作。正式需求／AC 以同一 SPEC-0048 confirmed snapshot 為準。

## 現有架構與方案邊界

已讀取 AGENTS.md、manifest/adoption/baseline、ARCHITECTURE.md、designs/modules 與相關 catalogs/flows。現有 schema/standard 均為 2.2.0；baseline 為零項。兩份 ADR 均為 proposed，沒有可冒稱 accepted 的 ADR。

- L0 `studio_application` 的 `StudioController` 持有 session recording rows、ImportedSamples、annotation tuples 與 `_annotations_ready`，協調 QML、workspace、Learning、project persistence。
- L1 `data_workspace` 擁有 Recording、AnnotationInterval、訊號 mapping 語意、驗證與 Normal 推導；parent 是 `studio_application`。
- L3+ `desktop_adapter` 實作 QML 及既有 Replay/Model 原子檔案 writer；L0 以 QRunnable 排程背景匯出，於 UI thread 更新完成／失敗狀態。
- 現有 Replay 匯出依賴 candidate、部分 single-IMU 模式不提供；不能直接把這個入口用作本功能的資格判定。

推薦沿用這些責任：workspace 決定選入範圍及標記語意，L0 建立一次 session 快照並協調，desktop adapter 處理每筆自含 JSONL 及整批新目錄發佈。2026-10-29 依後續檔案規劃詢問，改推薦同檔 header/annotations/sample blocks/end；原分檔 ZIP 僅保留為被取代候選。**不新增功能領域、不連接 Learning、不讓 workspace 依賴 Qt 或檔案格式。** 所有下述新增型別、Port、Event 與名稱都仍是候選。

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| 按鈕請求／拒絕 | desktop_adapter QML | studio_application | studio_application | 目的父資料夾 QUrl；取消不提交 | exportAnnotatedData；accepted/busy/unavailable | studio_application | UI-thread 匯出狀態 | QML → L0 組合入口 | QML 直接讀 ndarray 或檔案 writer |
| 建立可匯出語意快照 | studio_application | data_workspace | studio_application | 現行 Recording、annotations、mapping 的不可變語意值 | prepare_annotated_export 純查詢；不確認標記 | studio_application | 借用唯讀量測、複製 metadata 與 tuples | L0 → workspace 公開契約 | workspace → controller、project_session、Learning |
| 產生自含檔案／發佈完整批次 | data_workspace 語意快照 | desktop_adapter writer | studio_application | AnnotatedDatasetSnapshot；workspace 擁有的 demand-side AnnotatedDataOutputPort | writer 實作該 Port，每recording映射為JSONL v1，全部完成才發佈新批次目錄 | studio_application 配線；writer 擁有儲存表示 | worker-local block buffer、file handle、staging目錄 | desktop_adapter → workspace 公開契約；L0 建構配線 | workspace → json/Qt/具體 writer；共享可變 controller row |
| 回報終止結果 | 私有 worker/Qt signals | StudioController | studio_application | completed/failed/cancelled 及 export_id | UI-thread terminal callback | studio_application | current job、status、cancel token | owner-private queued signal；adapter → demand contract | 背景 worker 改 QML、controller dictionary 或 annotation truth |

Port 宣告於 `domain/data_workspace/contracts.py`，標準字串目的地與 workspace 語意值為輸入；不把 wire JSON dictionary 或 Qt handle 放入 domain 公開型別。純粹的 selection/validation 不另包假 Port。L0 私有 signal 不當成 domain output sink；沿用 workspace 單一事件出口，無 subscriber collection。頂層 `annotations.exported`、`annotations.export-failed`、`annotations.export-cancelled` 歸 L0；同一 export stream at-most-once、無自動 retry。若列為跨模組事件，具備 event_type/source/correlation_id/stream_id/sequence/payload。UI commit busy=false 及結果後才 publish terminal event。

## Type Ownership Matrix

| Type／預定宣告 | Owner / level | Role、fields、references | Visibility / lifetime | Mutability、authority、consumers | ABI / wire / storage impact |
|---|---|---|---|---|---|
| Recording、ImportedSamples、AnnotationInterval、ColumnMapping（既有 model.py） | data_workspace L1 | domain values；time/IMU arrays、索引與 mapping；本功能不改原欄位 | 既有可見度；session | frozen dataclass 不等同 ndarray 不可變；此 Flow 所有借用只讀；workspace、L0 | 不改專案或既有 wire |
| AnnotatedRecordingSnapshot（候選 model.py） | data_workspace L1 | Recording 引用；訊號種類、來源欄位／單位可信度、插值來源、確認／驗證狀態的不可變語意 metadata | cross-module；一個 job | frozen、唯讀借用 arrays；parent 建立一致輸入；workspace 驗證；writer 消費 | 新匯出契約，不改 dicsproj |
| AnnotatedDatasetSnapshot（候選 model.py） | data_workspace L1 | recording snapshots tuple、export identity、快照時間、確認狀態及排除項語意 | cross-module；一個 job | 不可變；不含 source file handle、QUrl、JSONL wire dictionary | 新格式由 adapter 呈現，schema_version=1 |
| AnnotatedDataOutputPort（候選 contracts.py） | data_workspace L1 | demand-side 檔案輸出契約；引用上列 workspace 型別及標準型別 | cross-module；組合生命週期 | 無共享 mutable runtime；adapter 實作 | 新 Port；無外部 ABI 變更 |
| _AnnotatedDataExportWorker / _AnnotatedDataExportSignals（候選 controller.py） | studio_application L0 | private composition mapping；workspace snapshot、port binding、Qt handles、Event cancel token | private；一個 job | UI thread 啟動／收尾；worker 只寫自身進度及 terminal outcome | 不公開、不進 project persistence |
| AtomicAnnotatedDataWriter（候選 adapters/desktop/annotated_data_writer.py） | desktop_adapter L3+ | adapter binding；JSONL編碼、file/staging handles、增量digest與批次rename | module-public implementation；一個 batch write | writer 私有寫入；consumer只透過demand Port | 新self-contained recording v1；不改Replay、Model或JSON deployment格式 |

若實作時需再新增型別或擴增欄位，須先補 owner、欄位角色、reference、生命週期與 analyzer 目錄，不能以此候選表當作無限制授權。

## State Object Ownership Matrix

| Object / definition / type | Owner | Lifetime / storage | Read / write authority | Leakage / reclamation |
|---|---|---|---|---|
| 現有 `_samples`、`_annotations`、`_recordings`、`_annotations_ready` | studio_application（現有 session 組合 state） | controller instance | UI thread 現有 owner；worker 不借 mutable dictionaries | 匯出只持有捕捉的 arrays 與複製 metadata/tuples；不修改原資料 |
| `_annotated_export_worker`、export_id、active/progress/error | studio_application | controller instance，一個 accepted job | UI thread 更新；queued callback 校驗 export_id | private，不存進 project；terminal 清除引用 |
| `_annotated_export_timer`、`_annotated_writer` | studio_application private composition fields | controller instance | UI owns 100ms timer；L0 binds workspace output Port | private framework/binding details，不暴露為StudioController public data fields；terminal停止timer |
| cancel Event、snapshot、進度計數器 | studio_application private worker | 一個 job，instance-local | UI thread 僅 set token；worker read；counter 單一 writer | 無共享 globals/TLS/static；finally 釋放 |
| JSONL block buffer、hash、file handle、staging_path | desktop_adapter writer | write-local，worker thread | writer 單一authority | 不跨Port回傳handle；finally關檔，只清理已驗證job-owned staging路徑；成功rename後清空暫存ownership |

本輪查找未發現此 Flow 的來源 ndarray 原地寫入；實作仍須審查所有 replacement/in-place 路徑。候選保守策略是在匯出期間拒絕 Import、Mapping 修改、Open/New、annotation create/move/delete/undo/redo/confirm/reference、Learning/Qualification、其他 artifact export；允許切換 recording、縮放、閱讀。所有 mutation command 必須在 controller 入口共同防護，不能只 disable QML。不變更原 ndarray writeable flag、不複製整個波形；借用唯讀視圖且 owner 在 job 期間不得原地修改。檔案對話框取消不設 busy；native dialog 回傳後重新檢查 admission，accepted 時才捕捉快照。

## Actual / intended edges、parent mappings

既有：L0 → workspace / Learning / project_session；L0 建構 desktop_adapter。desktop_adapter 目前可依賴 Learning/profile/diagnostics 契約。各 L1 parent 均維持 studio_application；無 sibling 直接依賴。

預期增加：desktop_adapter → data_workspace 公開匯出 Port／snapshot；L0 先要求 `_annotations_ready=true`、存在一致的 `_confirmed_workspace`，並確認目前 metadata／annotations／arrays 與該已確認狀態對應，再映射為匯出快照、配線 writer，沿用 UI thread → QRunnable → UI queued completion。未確認、確認失敗、標記編輯／mapping 變更後 confirmation 失效，均不得匯出；QML 呈灰色 disabled，controller 直接呼叫同樣拒絕。不得只根據非空標記或 provisional=false 放行。workspace 不讀 project JSON；不得呼叫 `_build_project_document()` 以免掃描所有來源、重建結果或混入 unrelated Learning state；匯出本身不呼叫 confirm。

## Flow execution impact

候選 Flow `export-annotated-data`，owner L0，best-effort、user command，無硬／軟即時期限：

1. UI thread admission：Confirm All Annotation Sets 已成功、confirmation 仍有效、整份 confirmed workspace 與現在資料一致、已完成 mapping/量測可用、無互斥工作；取消對話框不產生工作。對話框回傳後再次核對 confirmation，不能靠開窗前的狀態放行。
2. UI thread 捕捉 metadata/annotation tuples/array references，鎖定會改資料的命令，commit active，排程至背景 worker；不在 UI thread 做逐樣本複製、fingerprint 或 JSONL rendering。
3. worker 透過 workspace 純語意方法檢查結構及完整確認條件，呼叫既有 Normal 推導；若發現 provisional／不一致則失敗，不以 draft 模式降級交付；逐 recording、逐塊交給 output Port。
4. adapter在目的父目錄建立唯一staging，各recording串流寫單一JSONL：header、annotation lines、完整samples blocks、end/count/digest，flush/fsync及close。所有檔案成功後，將staging在同父目錄rename至不存在的唯一成品目錄；任何失敗不發佈部分成品，不覆寫既有批次。這是有界final publication設計，沒有虛構跨檔os.replace交易或跨平台斷電durability保證。
5. queued terminal result，UI thread 驗 export_id，先清 busy／釋放 state 再發結果；失敗與取消保留舊目的檔。

| Candidate | Functional admission | Cost model / sacrifice | Assurance |
|---|---|---|---|
| A：UI thread 收集所有 rows/大 JSON 後一次寫檔 | 可保持語意，但長操作阻塞互動，違反現有 long analysis invariant | 額外 O(N×C) Python objects/string；UI 包含整段格式化／I/O | 排除推薦 |
| B：單一背景worker、逐recording串流自含JSONL、全部完成後rename批次staging（推薦） | 借用唯讀快照、單筆active、不重入；一次final publication；每檔獨立end/digest；所有失敗有terminal result | O(N×C+A)時間；額外O(K×C+A+R+G)，K=chunk rows（4096為待benchmark起點），A=annotations、R=recordings、G=插值索引；不建O(N) labels。磁碟保留完整新staging與既有輸出共存，V1不另壓縮 | 方向比較estimated；效能採納BLOCKED待量測 |
| C：獨立 process 匯出 | 同樣可實現隔離與 atomic output | Windows spawn 必須序列化／複製大 waveform，或新增共享記憶體 ownership 與 IPC；增加部署／關閉處理 | 無證據需要，暫不推薦 |

既有完整資料量2,985,537 rows僅是其他聊天規模線索，**本輪未讀取或分析那些來源檔**。最多12 IMU channels+time的N×13×8約296MiB只是已存在float64 payload估算，非JSONL大小或RSS。保留borrowed arrays以免全量copy；chunk須比較鄰近大小，不稱背景thread必不卡。Python formatting GIL、JSON編碼與磁碟均待量測。header欄位名只存一次，samples以位置陣列分塊、每個annotation只存一次；讀檔先取header/annotation，再以程式掃描所需時間窗。無random-access index，後段查找仍需順序I/O，僅預覽header不能宣稱整檔digest已通過。此規劃不承諾固定token或耗時。

既有 interactive-workspace p95 ≤100 ms 可作 export 期間互動的回歸目標，來源為 workloads catalog；尚非本新功能已驗證承諾。觀測輸入延遲、峰值額外記憶體、寫入 throughput、取消延遲與失敗回復。沒有已採用的匯出完成時間或 MB/s 門檻；不可填零或虛構 PASS。Windows CPU/runtime/Qt/磁碟與 workload 需記錄，現有 windows-desktop profile 仍 proposed；平台效能決策需人類確認，效能 evidence 必須 OS-native ETW/WPR，與 release composition/hash 對應。

Execution catalogs 預計新增 best-effort annotated-data-write workload、對映 UI admission／背景序列化／queued completion、容量一個 job 及節流 progress channel；可沿用現有 replay-export-worker 的序列匯出 execution unit，擴大其 artifact 範圍與 mutual exclusion，而非為每個 module 配一個 thread。新增 sequential read/no in-place writes 的 data access profile；不新增 affinity、優先序、SIMD、cache tuning 或微架構效能聲明。不更改現有 real-time 分類，無需新 RT scheduling study。

## Algorithm impact

匯出「確認狀態admission／失效、單筆自含資料、來源列對應、半開區間、分塊串流及整批發佈」會改可觀察輸出且有容量／失敗策略，screening=triggered。實作前由data_workspace擁有`ALG-0010-annotated-data-export` proposed記錄（正式建檔先檢查ID），定義selection、input/range/identity invariants、complexity與fault cases。draft/provisional為拒絕案例。JSONL encoding、end/count/digest、staging/rename技術由L3 adapter實作並交叉引用。依AGENTS，架構authoring仍集中designs；若工具要求algorithm index，先按single CLI正式來源補齊，不手改generated metadata。

Normal 延用 `WorkspaceService.derive_normal_intervals(..., collision_response_window_s=0.150)` 與既有 ALG-0005 契約，不改碰撞 response/判定演算法。模型 fitting/scoring/detector/inference 不適用：沒有候選模型輸入、沒有訓練、沒有產生預測真值。按鈕排版本身不適用算法記錄，因只呈現命令及狀態。

## Evolution impact

| 情境 | 受影響 owner / interface / test | 不需改動的行為與代價 |
|---|---|---|
| 增加來源欄位或第三種訊號 | workspace channel descriptor、L0 metadata mapping、writer schema version及 contract tests | 不讓 Learning 定義匯出資格；新增有意義訊號仍須更新 schema |
| 多一個匯出完成訂閱者 | L0 existing terminal dispatch／fan-out、事件順序測試 | writer 無 subscriber list；at-most-once 失敗彙整 |
| 新增Parquet/HDF5 writer | workspace demand Port新adapter、L0配線、可重用contract suite | JSONL v1 reader保留；另付依賴／部署成本，非本期需求 |
| 新增 application-filtered view | workspace 新明確 view 語意、L0 來源映射、writer schema／golden fixtures | 不改 existing primary view 名義；不能以未宣告濾波輸出覆蓋 raw |
| Linux 平台 | desktop filesystem adapter／Qt 行為、execution profile、atomic writer真實目錄契約 | domain index/labels不變；仍須另收集該平台資源與 filesystem 證據 |

## Description Views / planned manifest diff

實作前才修改 `architecture/designs/` 的 modules/studio_application、data_workspace、desktop_adapter；catalogs/ports、events、types、state_objects、boundary_mappings、workloads、execution_*、data_access_profiles、validation_profiles；新增 flows/export-annotated-data 與 index 引用。保持 source_sets 的 production 分類，新 writer path/symbol 歸 adapter，model/contracts/service 歸 workspace，worker private composition types 歸 L0。更新 module purpose、invariants、entrypoints/public symbols、L0/L1 ordered Flow 與 error semantics。

執行 single CLI render 後，預期 manifest.yaml、ARCHITECTURE.md、generated/system.md、studio_application.md、data_workspace.md、execution-windows-desktop.md、adoption-readiness.{md,json} 會依實際差異改變。不得手編這些 generated 檔案。本文件只記 proposed delta，不修改 design-data catalogs、不把新 Flow 誤列已實作。

不預期需要 MUST exception ADR；若後續選擇形成 durable architectural decision，先建 proposed ADR 再請人類審查，不能將舊 ADR 升 accepted。設計／實作 gates 必須保持 exact 2.1.0 compatibility 並保留 1.0–2.1 累積要求，不擴增 baseline。

## Gate 狀態及進入實作前的必要工作

### 2026-10-29 pre-code 定案（實作授權 userMessage 01a18593-4b40-7cb1-820e-518869e51ba1）

本次實作沿用既有檔案，避免為純功能拆出額外邊界：`model.py`宣告ExportChannel、AnnotatedRecordingSnapshot、AnnotatedDatasetSnapshot及AnnotatedExportCancelled（data_workspace L1）；`contracts.py`宣告AnnotatedDataOutputPort；`service.py`增加純函式prepare_annotated_export，驗證整份confirmed快照及推導Normal。`replay_writer.py`增加AtomicAnnotatedDataWriter（desktop_adapter L3+）。controller新增兩個私有Qt composition types（studio_application L0）。snapshot中mapping為凍結的語意configuration，不含JSON字串／Qt／file handle；writer才轉wire representation。

Boundary mapping定為parent自身參與的`session-to-annotated-snapshot`：producer studio_application / studio-controller → consumer data_workspace / annotated-dataset-snapshot，parent/mapping owner studio_application；允許L0→workspace、禁止反向。writer經workspace demand Port直接消費同一合法producer-owned snapshot，不另造adapter DTO或把L3假設成L1 child。L0沿用`replay.events`作單一artifact事件出口，新增annotations terminal事件；private Qt queued signals不是另一個domain subscriber collection。

Type/State authority維持上述矩陣：export channel的sensor/kind/axis/array_column/source_column/unit是不可變configuration；record snapshot借用既有Recording與annotation tuples並持有frozen mapping、插值索引、warnings與derived Normal；dataset持有一個export_id/UTC capture及recording tuple。controller單獨擁有active worker、progress與job identity；worker單獨擁有cancel Event、demand Port binding及snapshot；writer單獨擁有local files/staging/buffer/digest。沒有新增mutable module-global、file-static、TLS或extern；instance runtime位於owner-private type fields及本State矩陣，不冒用只能分析module-global的Python State Catalog作instance AST證據。

authoring catalog、Port、allowed edges、Flow/workload/execution mapping完成後，single `architecture_cli.py gate --phase design ...` **exit 0、PASS: VERIFIED**。render刻意等型別實作後才執行（renderer會驗證完整AST，尚無新型別時拒絕PYTYPE002）；未手改generated manifest。既有SHOULD SYM004保留。這是pre-code design PASS，不是runtime/Release PASS。

現有 development gate 本輪 **exit 0，PASS: VERIFIED**，含既有 SHOULD SYM004，見 artifacts/spec0048-proposal-20261027/architecture-development.txt。它只證明現況；**候選 manifest 未建立／未驗證，新增設計 gate NOT RUN**。

技能 router 另發現既有 test/validation layout 與 validation planning 問題；不能把 project CLI 的 PASS 當作它們的 PASS，也不能擅自搬動大量既有測試以擴張本次方案任務。新測試規劃置於 tests/modules/<owner>/ 與 tests/flows/export-annotated-data/，definitions 在 validation/、immutable runs 在 artifacts/。實作啟動前要調查並修復實際 gate blocker，保留原功能邊界；沒有以本次 AI 自批 baseline 延後。未確認平台資料、未通過候選 design gate／layout／validation plan 者阻擋相應實作或效能驗收，不妨礙本輪方案保存與審查。

預定命令（使用 `.venv/Scripts/python.exe`；系統 `python` 此機為舊版，不適用）：

```powershell
.venv/Scripts/python.exe tools/architecture/architecture_cli.py render
.venv/Scripts/python.exe tools/architecture/architecture_cli.py gate --phase design --manifest architecture/manifest.yaml --adoption architecture/adoption.yaml --baseline architecture/baseline.yaml --format text
.venv/Scripts/python.exe tools/architecture/architecture_cli.py gate --phase development --manifest architecture/manifest.yaml --adoption architecture/adoption.yaml --baseline architecture/baseline.yaml --format text
.venv/Scripts/python.exe tools/architecture/architecture_cli.py render --check
.venv/Scripts/python.exe tools/architecture/architecture_cli.py gate --phase release --manifest architecture/manifest.yaml --adoption architecture/adoption.yaml --baseline architecture/baseline.yaml --previous-baseline <target-branch-baseline.yaml> --format text
```

以專案 CLI 的實際支援參數為準（此版 CLI 沒有 layout 子命令；router 使用插件版單一 CLI 檢查 layout）。本輪不執行 render，以免寫入與本次 proposal 無關的 generated artifacts。實作時每個命令記錄 executable/argv/exit code、最小 raw output、hash 與 PASS/FAIL/BLOCKED，不以編譯或靜態 gate 代替 export runtime acceptance。


## Review refinement — unchanged SPEC-0048 scope

The desktop writer owns the original staging directory `(st_dev, st_ino)` and each created regular file identity, in addition to their absolute paths. Cleanup rejects changed directory/file identities, reparse points and resolved-parent changes before unlinking; ambiguity reports remaining staging rather than traversing it. These are write-local job state under the existing desktop_adapter authority, O(R) metadata, not new public state or a new named type. The final cancellation observation follows the last destination-existence probe immediately before rename; a successful rename remains completion. Workspace validation checks identity uniqueness across explicit and derived intervals without rewriting the supplied IDs.

Execution is authorized by the current user's 2026-10-29 `開始執行` instruction. The confirmed r7 feature scope is unchanged; document-only statements above describe proposal history. Resource observations and host functional PASS do not discharge the selected ETW resource evidence, which requires an administrator token unavailable in this session.
