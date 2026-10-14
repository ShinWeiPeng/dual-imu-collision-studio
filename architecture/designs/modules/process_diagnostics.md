# process_diagnostics

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | process_diagnostics |
| version | 1 |
| kind | module |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: process_diagnostics
  level: L1
  role: domain
  implementation_status: implemented
  paths:
  - src/dual_imu_collision_studio/domain/process_diagnostics
  parent: studio_application
  depends_on: []
  implements_ports: []
  description:
    purpose: Define privacy-bounded process and Learning diagnostic records independently
      of persistence technology.
    input_ports: []
    output_ports:
    - diagnostics.output
    emitted_events: []
    owned_state: []
    side_effects: []
    errors: []
    invariants:
    - Diagnostic contracts never contain waveform rows, annotations, or model coefficients.
  entrypoints:
  - path: src/dual_imu_collision_studio/domain/process_diagnostics/contracts.py
    symbol: DiagnosticsPort
    kind: protocol
  public_symbols:
  - path: src/dual_imu_collision_studio/domain/process_diagnostics/contracts.py
    symbol: DiagnosticsPort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/process_diagnostics/model.py
    symbol: DiagnosticStatus
    kind: class
  - path: src/dual_imu_collision_studio/domain/process_diagnostics/contracts.py
    symbol: NullDiagnostics
    kind: class
```
