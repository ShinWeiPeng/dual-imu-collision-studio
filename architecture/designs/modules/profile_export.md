# profile_export

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | profile_export |
| version | 1 |
| kind | module |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: profile_export
  level: L1
  role: domain
  implementation_status: implemented
  paths:
  - src/dual_imu_collision_studio/domain/profile_export
  parent: studio_application
  depends_on: []
  implements_ports: []
  description:
    purpose: Convert qualified frozen FIR profiles into deterministic C99 or C++17
      headers and version-1 JSON model parameters.
    input_ports:
    - profile.command
    output_ports:
    - profile.file-output
    - profile.events
    emitted_events:
    - profile.exported
    owned_state: []
    side_effects: []
    errors: []
    invariants:
    - Every artifact contains one Profile struct, exact target numeric constants,
      and a machine-readable strict Score-greater-than-Threshold detector contract.
    - Default file names are stable dual_imu_collision_profile_kNNN.h names.
    - Every Profile records kernel depth, worst latency, three robustness margins,
      covered and excluded offsets, qualified speed interval, and exact condition
      tuples.
    - SPEC-0040 schema-1 model JSON omits release_ratio and release_quiet_time_s;
      event release belongs to common firmware policy and execution identity excludes
      display names.
  entrypoints:
  - path: src/dual_imu_collision_studio/domain/profile_export/service.py
    symbol: ProfileExportService
    kind: class
  public_symbols:
  - path: src/dual_imu_collision_studio/domain/profile_export/contracts.py
    symbol: ProfileCommandPort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/profile_export/contracts.py
    symbol: ProfileFilePort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/profile_export/contracts.py
    symbol: ProfileEventPort
    kind: protocol
```
