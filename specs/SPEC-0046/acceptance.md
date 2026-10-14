## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | 同一固定資料、設定與單一 worker 的修改前後完整 FIR fold 實測，新實作的程序樹尖峰與正增量低於舊實作；覆蓋建立、擬合、校準、評分階段，不以 estimated bytes 代替。保留原始紀錄、seed、版本、程序生命週期及每階段觀測。 | 有界原生 Windows 記憶體驗證；先用雙方都可安全完成的固定 fixture 做對照，再對約 207 萬列、33 taps 的代表範圍驗證新實作可完成。真實來源未確認前不宣稱已重現使用者完整資料。 | Pending |
| AC-002 | REQ-002 | 啟動與 UI 不呼叫估算器、沒有 estimate refresh/cancel/busy 依賴；不存在 estimated budget admission rejection。 | 估算器設為失敗 sentinel 的 executor/controller 契約測試與 Qt UI 檢查。 | Pending |
| AC-003 | REQ-003 | 3/6 channels、短長 History、斷點、排除區段、非有限值、零變異通道、robust on/off 及 target float32/float64 的有效列、特徵順序、模型與預測符合原有契約；代表 folds 的校準、loss、排名與匯出無回歸。 | 固定 seed 舊新差分、Learning/FIR 與整合回歸；既有容差不得放寬。 | Pending |
| AC-004 | REQ-004, REQ-005 | 受控實際記憶體讀值下保留 ceiling 停止；MemoryError、啟動失敗、取消與回收無回歸。介面沒有 Auto／Manual 切換；新實例預設 1，可選 1–8，非法 0／9 拒絕；實際數量不超過 jobs 數，執行中鎖定且不持久化。 | executor 故障注入、取消／回收與 worker 設定契約測試。 | Pending |

## Acceptance Mapping

```json
{
  "AC-001": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "latency-resource",
      "batch-capacity",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "原生 Windows Python FIR 訓練程序樹 RSS 與完整 fold 對照；實際成本由原生桌面量測支持，不宣稱嵌入式目標時間或硬即時保證。"
  },
  "AC-002": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "call-order",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Python executor/controller 及 Qt/QML 桌面入口不再使用估算，透過 sentinel 與介面檢查驗證。"
  },
  "AC-003": {
    "evidence_claims": [
      "host-semantics"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "FIR float64 數值與資料契約由固定 seed 差分與既有容差驗證，不涉及硬體。"
  },
  "AC-004": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "error-reset",
      "batch-capacity",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "原生桌面 worker 設定、實際監控、啟動失敗及回收由契約注入與 Qt 介面檢查驗證。"
  }
}
```

