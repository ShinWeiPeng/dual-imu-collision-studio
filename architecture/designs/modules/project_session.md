# project_session

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | project_session |
| version | 1 |
| kind | module |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: project_session
  level: L1
  role: domain
  implementation_status: implemented
  paths:
  - src/dual_imu_collision_studio/domain/project_session
  parent: studio_application
  depends_on: []
  implements_ports: []
  description:
    purpose: Own the versioned semantic project document, source-integrity rules,
      and transactional reopen/save contract.
    input_ports:
    - project.command
    output_ports:
    - project.file-storage
    emitted_events: []
    owned_state: []
    side_effects: []
    errors: []
    invariants:
    - Project documents never embed waveform sample arrays.
    - Every referenced source is identified by path, byte size, and SHA-256 before
      restored annotations can be committed.
    - In-progress Learning state is never represented as a resumable checkpoint.
    - Completed retained Profiles are optional and version-bound.
    - New-contract project documents accept finite positive data-derived Profile thresholds
      and restore exact interpolation provenance with source identity checks; old-project
      migration is outside SPEC-0009.
    - Editable Training mode and fixed-grid selections persist independently from
      immutable completed-run provenance. Pre-extension editable settings default
      to fixed-grid with empty selections, while legacy captured runs restore as optimized
      provenance without changing retained results.
    - SPEC-0045 optional schema-1 qualification_results contains validated event-level
      immutable results and model/input/policy bindings. Missing historical details
      remain unavailable; malformed or unsupported results reject the whole transaction.
      No per-sample scores, states or waveforms are persisted.
  entrypoints:
  - path: src/dual_imu_collision_studio/domain/project_session/service.py
    symbol: ProjectSessionService
    kind: class
  public_symbols:
  - path: src/dual_imu_collision_studio/domain/project_session/contracts.py
    symbol: ProjectFilePort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/project_session/service.py
    symbol: ProjectSessionService
    kind: class
```
