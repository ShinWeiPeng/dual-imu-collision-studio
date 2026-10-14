# CAT-state_objects

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-state_objects |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: state_objects
value:
- id: json-export-queue
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/Main.qml
    symbol: jsonExportQueue
    storage: file-static
  type: var
  visibility: private
  lifetime: One desktop JSON export interaction.
  mutability: owner-mutable
  read_authority:
  - desktop_adapter
  write_authority:
  - desktop_adapter
- id: json-export-current
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/Main.qml
    symbol: jsonExportCurrent
    storage: file-static
  type: var
  visibility: private
  lifetime: One desktop JSON export interaction.
  mutability: owner-mutable
  read_authority:
  - desktop_adapter
  write_authority:
  - desktop_adapter
- id: json-export-target
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/Main.qml
    symbol: jsonExportTarget
    storage: file-static
  type: url
  visibility: private
  lifetime: One desktop JSON export interaction.
  mutability: owner-mutable
  read_authority:
  - desktop_adapter
  write_authority:
  - desktop_adapter
- id: json-export-error
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/Main.qml
    symbol: jsonExportError
    storage: file-static
  type: string
  visibility: private
  lifetime: One desktop JSON export interaction.
  mutability: owner-mutable
  read_authority:
  - desktop_adapter
  write_authority:
  - desktop_adapter
- id: recordings-viewport-before-wizard
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/Main.qml
    symbol: recordingsViewportY
    storage: file-static
  type: real
  visibility: private
  lifetime: One ImportPage QML instance within the main window.
  mutability: owner-mutable
  read_authority:
  - desktop_adapter
  write_authority:
  - desktop_adapter
- id: mapping-wizard-validation-error
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/MappingWizard.qml
    symbol: validationError
    storage: file-static
  type: string
  visibility: private
  lifetime: One Mapping Wizard QML instance within the main window.
  mutability: owner-mutable
  read_authority:
  - desktop_adapter
  write_authority:
  - desktop_adapter
- id: recent-adopted-filter-parameters
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/MappingWizard.qml
    symbol: recentFilterParameters
    storage: file-static
  type: var
  visibility: private
  lifetime: One window-owned Wizard instance; retained across recordings and dialog
    closes, not persisted.
  mutability: owner-mutable
  read_authority:
  - desktop_adapter
  write_authority:
  - desktop_adapter
- id: single-imu-filter-template-index
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/SingleImuFilters.qml
    symbol: templateIndex
    storage: file-static
  type: int
  visibility: private
  lifetime: One per-IMU editor; reset to last stage on load, adjusted on move/delete,
    never persisted.
  mutability: owner-mutable
  read_authority:
  - desktop_adapter
  write_authority:
  - desktop_adapter
- id: single-imu-filterpreview
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/SensorMapping.qml
    symbol: filterPreview
    storage: file-static
  type: var
  visibility: private
  lifetime: One per-sensor mapping component; invalidated by source, time or filter
    edits.
  mutability: owner-mutable
  read_authority:
  - desktop_adapter
  write_authority:
  - desktop_adapter
- id: single-imu-adoptedfilter
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/SensorMapping.qml
    symbol: adoptedFilter
    storage: file-static
  type: var
  visibility: private
  lifetime: One per-sensor mapping component; invalidated by source, time or filter
    edits.
  mutability: owner-mutable
  read_authority:
  - desktop_adapter
  write_authority:
  - desktop_adapter
```
