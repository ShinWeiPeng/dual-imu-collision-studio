## User Stories
使用者需要在保留資料與模型行為的前提下降低 FIR 實際尖峰及常駐用量，訓練不再被推算的預算拒絕。

## Requirements
| ID | Requirement |
|---|---|
| REQ-001 | 修改 FIR 實際配置與資料生命週期以降低實測用量；不得僅修改估算公式、估算常數或估算顯示作為完成依據。 |
| REQ-002 | 生產訓練不再計算記憶體預估、不以預估值拒絕 spawn，移除相關 refresh/cancel estimate UI 與估算 busy 啟動限制；共用 FIR/MLP 路徑一併解除對估算的依賴。 |
| REQ-003 | 保留目前選定的樣本、History、通道順序、finite/segment/eligibility 規則、robust refit 規則、float64 訓練及 target precision、校準、分數／排名、匯出與專案格式；數值比較使用既有容差。 |
| REQ-004 | 保留現有實際記憶體監控、90% ceiling、終止錯誤處理、取消與回收；保留手動 worker 1–8，不新增自動重試或靜默修改使用者手動值。 |

| REQ-005 | 移除 Auto 及 Auto／Manual 模式選擇，直接選擇 worker 1–8、預設 1；實際數量不超過 jobs 數，執行中鎖定且不持久化。 |

