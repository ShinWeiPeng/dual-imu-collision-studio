## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | 新增 mapping 初始狀態正確；兩類可同選，依選項顯示各 XYZ 欄位，缺欄及重複映射提供明確錯誤。 | Qt UI 操作與 mapping contract 測試。 | 尚未執行 |
| AC-002 | REQ-002, REQ-003 | acceleration-only、gyro-only、combined 的每 IMU 3/3/6 通道身份正確，選取的通道實際進入適用 FIR/MLP/self-IMU 訓練與 replay。 | 數值合成資料、通道順序及訓練/重播整合測試。 | 尚未執行 |
| AC-003 | REQ-003 | fold 正規化不使用 validation rows；單一 detector 保留原有事件判斷及時序規則。 | fold 隔離、凍結模型 replay 與 detector 邊界測試。 | 尚未執行 |
| AC-004 | REQ-001, REQ-002, REQ-003 | 新專案 round-trip 保留設定；舊專案與舊模型 acceleration-only 相容；匯出可重現對應模型並辨識版本。 | 保存/載入、舊資料回歸及匯出重播等價性測試。 | 尚未執行 |

| AC-005 | REQ-004, REQ-005 | A 成功完成 Mapping 後，B 未設定且有相同欄位名称時自動帶入各角色；改變欄位順序仍正確；名稱缺少者留空；兩顆 IMU、兩類訊號及 raw/filtered 不互相混用。 | Qt 連續開啟 recordings 操作及欄位配對測試。 | 尚未執行 |
| AC-006 | REQ-004, REQ-005 | 已設定的 B 保留自身 Mapping；取消或失敗不更新暫存；後續成功完成 C 更新最近記憶；新程式實例不取得前次暫存，但已保存的 recording Mapping 正常還原。 | Qt 更新/取消/失敗流程、新實例隔離及專案保存回歸測試。 | 尚未執行 |

## Acceptance Mapping

```json
{
  "AC-001": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "state-transition",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Qt checkbox and mapping validation require host behavior and desktop adapter checks."
  },
  "AC-002": {
    "evidence_claims": [
      "host-semantics"
    ],
    "contract_dimensions": [
      "input-output-units"
    ],
    "execution_changes": [],
    "rationale": "Synthetic 3/6 channel matrices verify algorithm inputs and ordered signal identity on the host."
  },
  "AC-003": {
    "evidence_claims": [
      "host-semantics"
    ],
    "contract_dimensions": [
      "state-transition",
      "call-order"
    ],
    "execution_changes": [],
    "rationale": "Training-fold isolation and replay detector transitions are verified by numerical host tests."
  },
  "AC-004": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "contract_dimensions": [
      "input-output-units",
      "external-port"
    ],
    "execution_changes": [],
    "rationale": "Project roundtrip and model export require host equality and filesystem/desktop adapter checks."
  },
  "AC-005": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "execution_changes": [],
    "contract_dimensions": [
      "state-transition",
      "call-order",
      "external-port"
    ],
    "rationale": "Verify session-only mapping-name reuse, exact column identity, saved-recording precedence and process-lifetime reset through Qt and host tests."
  },
  "AC-006": {
    "evidence_claims": [
      "host-semantics",
      "adapter-conformance"
    ],
    "execution_changes": [],
    "contract_dimensions": [
      "state-transition",
      "call-order",
      "external-port"
    ],
    "rationale": "Verify session-only mapping-name reuse, exact column identity, saved-recording precedence and process-lifetime reset through Qt and host tests."
  }
}
```

## Validation Plan

完成 UI、mapping、fit/replay、serialization、export 的相關測試，執行 architecture_cli.py development gate（含既有 baseline），交付前執行 release gate 與 generated-view 比對。目前尚無執行或 PASS 證據。先前 router 報告多規格識別衝突、test layout FAIL 及 validation planning BLOCKED，需以明確本 SPEC reference 重查及處理。6 軸成本隨矩陣及模型維度改變，需實測訓練時間、記憶體與 replay，不提出未量測的速度或即時性保證。

