# SPEC-0046 驗證紀錄

日期：2026-10-12。SPEC 修訂 6（confirmed）。使用者本輪「開始執行」訊息 `01a12f36-b182-7380-bd2a-9720745ebff9` 已核實，managed continue-execution PASS；授權摘要中的舊「尚未取得」是執行前快照，本輪 discussion journal 與 receipt 記錄目前授權。未宣稱正式整體驗收完成。

## 實作

- FIR 以借用來源資料的有效列索引表示特徵，擬合與預測依 8 MiB 特徵區塊處理，移除完整 N×channels×taps 特徵矩陣及 Python scalar lists 的常駐需求。
- float64 Ridge 分塊累積 mean、variance、Gram、RHS；維持通道／時間順序、有效列、alpha、退化處理、robust 排序與 refit 規則。target 運算維持既有逐欄累加與精度捨入。
- 校準仍保留精確 STD/MAD；其 O(N×channels) 殘差陣列、來源資料、索引及 O(features²) Gram 仍占用記憶體。8 MiB 是特徵區塊容量，並非整體記憶體上限。
- 生產訓練入口及 UI 移除估算／刷新／估算 admission rejection。離線估算相容函式保留，但生產入口無呼叫。
- 移除 Auto／Manual，直接選 1–8 workers，預設 1、只存本次工作階段、執行中鎖定；數量受 jobs 數限制。Qualification 原有最多 4 workers 規則維持。
- 保留實際系統記憶體 90% ceiling、取消、子程序回收及錯誤傳遞；未增加相依套件。

## Windows 實測

固定 seed 46、3 channels、33 taps、float64，修改前後使用各自全新單一 worker，執行完整 FIR fold（建立、擬合、校準、訓練及驗證評分）。舊版來源雜湊存於 comparison.json。相同 OpenBLAS/OMP threads=1。psutil 讀取 Windows 原生程序計數器，20 ms 取樣程序樹 RSS，另保留 peak_wset。

| 訓練列數 | 實作 | 取樣程序樹尖峰 RSS（bytes） | RSS 正增量（bytes） | 原生 peak working set（bytes） | fold 秒數 |
| --- | --- | ---: | ---: | ---: | ---: |
| 100,000 | 修改前 | 723,812,352 | 610,037,760 | 719,241,216 | 6.657 |
| 100,000 | 修改後 | 153,042,944 | 41,222,144 | 148,062,208 | 0.828 |
| 2,070,704 | 修改後 | 817,967,104 | 541,507,584 | 863,387,648 | 21.984 |

10 萬列程序樹尖峰減少約 79%；模型、bias、校準與 loss 差分在 rtol/atol 1e-12 通過。207 萬列新版完成。以上為固定合成 fixture，不能宣稱已重現使用者完整來源資料或保證其實際峰值。

原始證據：[10 萬列修改前後](../artifacts/validation/SPEC-0046-rss-pair-20261012/comparison.json)、[207 萬列新版](../artifacts/validation/SPEC-0046-rss-large-20261012/comparison.json)。各 run 保留 worker 階段、程序生命週期及取樣 observations。這是原生 Windows 計數器實測，`formal_etw_acceptance: false`；未宣稱 ETW/WPR 正式證據組合 PASS。

## 檢查與限制

- 新增 26 項固定 seed 舊新差分通過：3/6 channels、taps 1/9/33、robust on/off、float32/float64、segment 斷點／重複標籤、NaN/Inf、零變異、STD/MAD；強制 4 KiB 小區塊驗證物化容量。
- 記憶體 executor 契約 18 項通過；worker selection／history execution 23 項通過，含實際 spawn、一／二 workers 結果對照、取消與回收。
- 全套回歸執行 751 項：749 PASS、2 FAIL。失敗之一是尚未 render 的架構文件；完成 render、development gate（exit 0）及 architecture smoke 重跑 PASS。另排除的快取監測測試改為監測 lazy preparation 並單獨 PASS。
- 字型尺寸測試 `test_filter_captions_fit_scaled_fonts[10-1]` 45 秒逾時；重跑同檔 7 PASS、1 同樣逾時。該測試載入 SensorMapping.qml，本次未改動該檔；有界 faulthandler trace 停於 `engine.loadData`（test_filter_caption_sizing.py:38）。歸因尚未證實，不能宣稱全套綠燈。
- 已變動 Python 範圍 `ruff format --check` PASS（7 檔）；此為格式檢查。額外 `ruff check` 回報 62 項 lint findings（涵蓋既有來源及測試支援程式），未宣稱 lint PASS。架構採用 Markdown 設計來源與單一 CLI render/gate，baseline 零項。
- Standards review 無 actionable findings；Spec review 未發現實作矛盾／scope creep。部分獨立讀取受 auto-review 429 影響，保留其覆蓋限制。
- managed complete 已實際執行，回報 BLOCKED：compatibility requires diagnosis（詳見 spec-governance/DISCUSSION-REQUEST-fir-complete-result.json）。全專案 legacy layout 與正式 ETW 證據仍未完成；整體 acceptance 不宣稱 PASS，SPEC 未標記 implemented 或 release。無 commit／PR。

完整回歸原始結果：[JUnit](../artifacts/tests/SPEC-0046-full-20261012.xml)；[架構及快取重跑](../artifacts/tests/SPEC-0046-final-recheck.xml)；[字型尺寸重跑](../artifacts/tests/SPEC-0046-caption-recheck.xml)。
