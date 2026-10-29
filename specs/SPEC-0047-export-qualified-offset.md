---
spec_version: 1
spec_id: SPEC-0047
revision: 1
status: working
change_set: export-qualified-offset
task_ref: 01a14438-8bed-7612-9450-a4e731e429e7
---
# Export Profile 合格範圍顯示 offset

## Current Specification

使用者於 2026-10-16 要求「欄位 qualified range(mm/s, offset)，也要有 offset」，並提供 Export Profile 畫面。

| ID | Requirement |
|---|---|
| REQ-001 | Export Profile 欄名顯示 `Qualified range (mm/s, offset)`。 |
| REQ-002 | 每個可匯出模型在既有合格速度文字下一行顯示 `Offset: …`，讀取該 profile 的 `covered_offsets_mm`，沿用既有 mm 格式與空集合 `None` 顯示。 |
| REQ-003 | 維持資格判定、可匯出集合、JSON 內容、專案格式及其他頁面的既有行為。 |

## Decisions and Discussion

| ID | Decision | Source |
|---|---|---|
| DEC-001 | 在同一欄分兩行顯示速度及 offset；沿用現有 `qualifiedRange` 顯示字串與 QML 換行支援。 | 本聊天使用者直接修改要求及現有畫面。 |
| DEC-002 | 使用合格 profile 已儲存的 covered offsets，不以 excluded offsets 或所有輸入條件取代。 | 現有 `_profile_from_candidate` 將 candidate.active_offsets 映射為 profile.covered_offsets_mm。 |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method |
|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | 匯出列同時呈現合格速度、offset 及單位，QML 可載入。 | 既有 JSON 匯出列測試與 QML smoke checks。 |
| AC-002 | REQ-003 | 原有資格與 JSON 匯出測試通過。 | JSON 與 export-profile 流程回歸測試。 |

## Scope and Authorization

本次依使用者直接修改要求完成欄位顯示調整。此檔保留 working 狀態，未另行取得規格確認或技能特定的「開始執行」字樣。

## Architecture Impact

僅變更既有顯示字串與欄名；不新增或修改 named types、runtime state、modules、dependencies、ports、callbacks 或 events。既有 profile 擁有合格 offset 資料；既有 application controller 將其格式化給 desktop QML。無架構 manifest 或 generated views 變更。

## Pending Discussion

None.

## Validation

- JSON、export-profile 與 QML 回歸測試：85 passed（19.69 秒）。既有匯出列測試核對 `500, 800 mm/s\nOffset: 5 mm`。
- 測試命令：`.venv/Scripts/python.exe -m pytest tests/test_model_json_export.py tests/flows/export-profile tests/test_qml_smoke.py -q -p no:cacheprovider --basetemp artifacts/qualified-offset-20261016/pytest-final`。
- Formatter：`ruff format --check src/dual_imu_collision_studio/adapters/desktop/controller.py` 通過。
- Architecture：`architecture_cli.py gate --phase development --manifest architecture/manifest.yaml --adoption architecture/adoption.yaml --baseline architecture/baseline.yaml --format text`，exit 0、PASS: VERIFIED；既有非阻擋 SHOULD SYM004 訊息保留。
- 首次測試因測試暫存父目錄未建立而 setup 失敗；建立目錄後以新 run 路徑重新執行，85 項全數通過。
- 技能路由工具在 UTF-8 重試後回報多份 working/confirmed SPEC 與 layout 檢查 timeout，未取得該技能 managed-delivery PASS；不將此工具結果宣稱為通過。直接需求及本次顯示修改採本回合授權執行，架構 gate 與功能檢查結果如上。
