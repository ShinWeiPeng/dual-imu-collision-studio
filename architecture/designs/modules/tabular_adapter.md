# tabular_adapter

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | tabular_adapter |
| version | 1 |
| kind | module |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: tabular_adapter
  level: L3+
  role: adapter
  implementation_status: implemented
  paths:
  - src/dual_imu_collision_studio/adapters/tabular
  parent: null
  depends_on:
  - data_workspace
  implements_ports:
  - workspace.tabular-input
  description:
    purpose: Decode CSV and XLSX files into demand-owned semantic columns and samples.
    input_ports: []
    output_ports: []
    emitted_events: []
    owned_state: []
    side_effects:
    - description: Read selected local CSV and XLSX files.
    errors: []
    invariants:
    - Adapter-specific dataframe or workbook types never cross into the data domain.
    - Header and Data Start Row proposals remain provisional until Mapping Wizard
      confirmation.
    - Internal and External IMU axes use the same direct XYZ mapping interaction.
    - Contiguous trailing rows without all mapped inputs are excluded with exact warnings;
      an interior mapped-value gap remains a blocking error.
  entrypoints:
  - path: src/dual_imu_collision_studio/adapters/tabular/reader.py
    symbol: TabularReader
    kind: class
  public_symbols:
  - path: src/dual_imu_collision_studio/adapters/tabular/reader.py
    symbol: TabularReader
    kind: class
```
