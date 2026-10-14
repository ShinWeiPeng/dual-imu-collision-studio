<!-- document-bundle:1 -->
<!-- document-navigation:start -->
[需求](SPEC-0046/requirements.md) | [驗收](SPEC-0046/acceptance.md) | [討論與決策](SPEC-0046/discussion.md) | [固定設計引用](SPEC-0046/references.yaml)
<!-- document-navigation:end -->
---
spec_version: 1
spec_id: SPEC-0046
revision: 6
status: confirmed
change_set: fir-worker-memory-diagnosis
working_id: WORKING-SPEC-d62083998d26-fir-worker-memory-diagnosis
task_ref: 01a12f0b-6b9c-7d60-8ecf-af27e7456e29
---
# FIR 實際記憶體用量優化與移除預估阻擋

## Problem
使用者明確澄清：要修改的是優化實際使用量；可以不計算預估值，也不需要使用預估值作保護。當初因為實際用量過高才提出需求。先前的估算數字診斷只提供配置線索，不能取代降低實際配置與實測驗收。
提供的 FIR 診斷為單一 worker，最壞 fold 有 2,070,704 training rows、33 taps、3 channels。matrix_construction 10.691 GB、fit 5.549 GB 是歷史估算而非實測；不能作本次修改成果或未來保護依據。

## Solution
已採用目標為降低 FIR 實際記憶體用量，並讓生產訓練流程停止計算與使用預估值作啟動阻擋。共用 FIR/MLP 訓練估算入口與 UI 會受影響；MLP 訓練數學不在本次優化目標。
候選實作採用有界分塊的 FIR 特徵建立、統計／Ridge 累積、robust refit、校準及評分，避免保留完整的樣本數乘 History 特徵矩陣；若共享的矩陣入口仍供 MLP 使用，直接配置連續陣列以消除 scalar/list 暫存。保留資料、History、通道順序、float64 訓練與既有模型／判定契約。
保留現有基於實際系統記憶體讀值的 90% 執行中 ceiling、MemoryError/OS 記憶體錯誤終止、取消、子程序回收與零重試；預估保護的移除不代表移除這些現有行為。
取消 Auto／Manual 模式切換；介面直接選擇 1–8 個 worker，沿用既有手動預設值 1。執行時數量最多為可執行 jobs 數，執行中鎖定設定，設定仍不持久化。預設單 worker 讓 jobs 依序完成；使用者可自行提高並行數，實際用量也會增加。

## Relationships
| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0028 |
| REQ-002 | supersedes | SPEC-0043 |
| REQ-004 | refines | SPEC-0027 |
| REQ-005 | supersedes | SPEC-0043 |

本次 supersedes 取代 SPEC-0043 中預估計算、預估建議、預估拒絕以及 Auto／Manual 模式切換的相關部分；手動 1–8、執行中鎖定、取消與設定非持久化等其他契約維持。替代來源為 user-actual-memory-optimization-20261012 與 user-remove-auto-20261012。

## Out of Scope
不減少資料或 History、不改變模型容量與碰撞判定、不降低訓練精度、不改專案／模型匯出格式。本次不要求優化 MLP 訓練數學，不修改其他現有獨立需求。分塊內部 buffer 尺寸是可驗證的實作細節，不新增持久化使用者參數。未授權自行接受 ADR 或放寬 architecture gate／數值容差。

## Routing/Gates
保持同一 SPEC-0046 與聊天綁定；已記錄完整目標與最後 Auto 決定，尚未取得本輪 exact 開始執行。規格確認不授權產品修改。
實作前完成 architecture/designs 的受影響來源與邊界／型別／狀態 ownership 設計、計畫 manifest 檢查；由專案單一 architecture_cli render/gate 生成並驗證，不能手改 manifest/views。遵循 formatter 與 coding standards、必要數值回歸、實測記憶體驗證及專案 validation layout/verification ladder；目前不宣稱通過。

## Current Specification

See Problem, Solution, Requirements and Acceptance Criteria above.

