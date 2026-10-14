# SPEC-0042 驗證紀錄（2026-10-11）

SPEC-0042 revision 4「FIR 記憶體預估與啟動前並行調整」維持 confirmed，執行授權已驗證；尚未完成實際專案驗收，不標記 implemented。

## 已完成實作

FIR fold 在 spawn 前依完整工作集估算配置及重疊峰值，使用新讀取的 RAM 預算選出可容納的最大固定並行數 1..min(8,N)。單一工作也無法容納時，先拒絕再顯示 Failed 與需求、缺口、主導成本。保留全部資料、參數、fold/seed、精度與工作順序；保留執行期 90% RAM 保護及失敗不重試。MLP 與 Qualification 上限未更動。估算仍待原生峰值獨立驗收，不能稱為已校準。

## 已驗證

- 最終全套回歸：656 passed in 532.77s。固定證據：`artifacts/tests/spec42-full-final-20261011/pytest.log`。
- 最終相關回歸：112 passed。證據：`artifacts/tests/spec42-final-targeted/pytest.log`。
- Repo architecture_cli.py development gate：PASS exit 0；既有 SHOULD SYM004 保留。
- 正式版 0.20.0 驗證器合成案例：PASS、FAIL、BLOCKED 均符合預期。證據：`artifacts/validation/spec42-native-fixture-{pass,fail,blocked}-20261011-e/result.json`（三個實際固定目錄）。
- Windows Job Object owner 結束時會回收專用子程序；獨立 1 秒 deadline 實測 exit 124、BLOCKED 紀錄、子程序消失。這是測試工具行為，不代表 FIR 峰值通過。
- 舊版能力 probe-b 曾完成 ETW 擷取：全部子程序生命週期、0 Lost Events / Buffers，實際 Python child Peak WS 28,041,216 bytes，原始 trace SHA256 `3082a1168fdfb5ea727215ca13008623c2cc71b2d5855b4f665113f55602c142`。原始紀錄在 `artifacts/validation/spec42-native-enablement-20261011-b/capture/`。正式 flow evaluation-d PASS 在 `artifacts/validation/spec42-native-enablement-evaluation-20261011-d/result.json`；它綁定舊 profile，不能冒充新版本啟用證據。

## 實際專案與證據界線

原始 FIR.dicsproj SHA256：`42adedd1d7745c82191a99cd29958124052d43f9b28fc40fcd753c93db5cc7d0`。12 筆 recordings，2000 Hz，3 channels，float32，History 4/8/16 ms、alpha 1e-6/1e-4、3 folds，共 18 jobs。

唯讀 admission 檢查選出 1 worker，估算額外 11,471,218,824 bytes；這是估算，不是實測。來源與每工作成本固定在 `artifacts/validation/spec42-actual-admission-20261011-b/result.json`。

未追蹤的功能性試跑於 900 秒測試時限內完成 8/18 jobs，隨後由測試取消，並非產品自行取消或記憶體失敗。該次沒有完整批次結果，不能滿足 AC-003。固定證據：`artifacts/validation/spec42-functional-learning-20261011/result.json` 與 `progress.jsonl`。

原始截圖 Cancelled/0% 根因仍未知；三次 Failed/30% 的 HardwareMemoryInsufficientError 是已重現的獨立問題。撤回的重複點擊假說與 bare InterruptedError 分類修正均不屬本次修復聲稱。

## 本輪原生啟動阻塞

使用者明確允許 bounded administrator ETW tracing；授權來源 `user:etw-permission-20261011` 已保存。安全補強後的 probe-c 啟動收到 Windows `The operation was canceled by the user`，未產生 capture 目錄，沒有啟動管理員 Python 或 ETW。實際 launcher stderr 固定在 `artifacts/validation/spec42-native-enablement-20261011-c/launcher.json`。後續 xperf -loggers：No Active Loggers。

probe-c 是未完成的收集，沒有產品驗收 PASS。其手動 allocation 亦尚未具有 runner 所需的 inputs.profile/effective_profile 與 expected run ID admission；不得修改舊 metadata 後冒稱原生測試通過。後續必須使用新 run，依正式來源配置完整 metadata，保留同一 run identity 至終結，並傳入 --expected-run-id。probe 日誌使用 capture 的父層 run ID，原始紀錄不改寫。

## 尚未通過的門檻

AC-001 至 AC-005 正式映射維持 Pending。AC-001 實際逐 fold 列數、AC-003 兩次完整學習及結果比較、AC-004 4/8/16 ms 獨立 native Peak WS 仍缺證據。已有單元/契約證據不替代實測。

正式版 0.20.0 公開入口 `govern-modular-event-architecture/scripts/architecture_cli.py layout` 的全專案檢查仍 FAIL。固定證據為 `artifacts/validation/spec42-public-layout-audit-20261011/stdout.json`，本次計數 {'LAY003': 263, 'RUN001': 41, 'LAY002': 70}。問題集中在歷史檔案布局與證據歸屬/來源；含本次未正式配置的證據目錄，不能全部稱為既有問題。先前 `tools/architecture/architecture_cli.py layout` 輸出的 459 項不是此公開入口的結果，其中 97 項 CAP001 不在本次結果內；保留舊紀錄但撤回該計數作為目前判定。未搬移或刪除使用者既有檔案，未偽造歷史 run 身份，未放寬 gate。Repository development architecture gate PASS 與此 layout FAIL 是不同結果。

## 繼續方式

使用正式版 0.20.0，既有 SPEC 授權仍有效。先配置新 probe run（inputs.profile=原始profile SHA，inputs.effective_profile=正式 load_profile 後的 profile_sha256；expected_run_id 與 root/run 及日誌一致），在 Windows UAC 實際按「是」後完成新版本 enablement。然後在各自獨立且先配置的 run 中依 profile 執行 FIR history-4/8/16（每次3600秒）、full-one/full-selected（每次7200秒），最多256MiB trace。

將原始 ETW process.csv/perf.csv/stats.txt 正規化，以完整 process_start/process_end QPC 邊界綁定 native.json 與 trace SHA；保存 offline replay provenance，不能偽裝產品直接發出 VAL events。父程序同時記錄 live RSS 與 native peak_wset 基線：估算覆蓋保守上界才可PASS，確定低於下界才FAIL，其餘歸因不足BLOCKED。使用正式 evaluator 的 --native-evidence、--native-source-trace、--prerequisite-result 與同一 --output/--expected-run-id。

比較完整兩次的 jobs、fold groups/seed、models/losses、選模與 Qualification 結論；先要求 exact equality，若數值不同則報告差異，不自行放寬 FIR 容差。單次 helper PASS 只代表該次執行/捕捉完整，不能獨自滿足 AC-003。完成實際驗收及全專案 layout 門檻後再進行 managed complete；本輪未 commit。
