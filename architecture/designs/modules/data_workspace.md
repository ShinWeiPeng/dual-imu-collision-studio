# data_workspace

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | data_workspace |
| version | 1 |
| kind | module |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: data_workspace
  level: L1
  role: domain
  implementation_status: implemented
  paths:
  - src/dual_imu_collision_studio/domain/data_workspace
  parent: studio_application
  depends_on: []
  implements_ports: []
  description:
    purpose: Own imported recordings, mappings, test conditions, cycles, annotations,
      and derived Normal regions.
    input_ports:
    - workspace.command
    output_ports:
    - workspace.tabular-input
    - workspace.events
    emitted_events:
    - workspace.changed
    owned_state: []
    side_effects: []
    errors: []
    invariants:
    - Collision truth is determined only by waveform interval annotation.
    - Normal regions are derived and read-only.
    - After annotation confirmation, derived Normal regions exclude each Collision
      onset-through-150-ms inclusive response window, clipped at the containing Cycle,
      without changing the user's persisted Collision interval. Existing confirmation
      validation rejects Cycles that cross a true acquisition discontinuity; the derivation
      also defensively stops a response window at the first such discontinuity.
    - Every valid Cycle matches its reference template's non-negative Pick, Put, and
      Fork Collision count tuple; each class may be absent, but the total event count
      is at least one.
    - Use as Reference atomically confirms one valid source Cycle and its contained
      labels before activating a template for exactly one Robot Speed.
    - One manually confirmed destination Anchor Cycle deterministically generates
      remaining provisional Cycles from the reference cadence before event and Ignore
      projection.
    - Reference Ignore intervals retain their non-empty reasons, and every generated
      destination interval remains provisional until explicit confirmation.
    - Manual annotations take precedence over projected proposals and different Robot
      Speeds never share a template.
    - Every annotation interval has one non-empty session identity that is unique
      within its recording and survives confirmation-state replacement.
    - Reopening a project preserves every stored interval identity and allocates later
      manual interval identities without collision.
    - Ignore intervals carry a non-empty user reason.
    - Ignore/Collision overlap invalidates annotation confirmation and Learning; half-open
      adjacency and Ignore/Pick/Put overlap retain existing semantics.
    - Tabular input preserves measured rows and source bytes and linearly interpolates
      one through three missing samples on all six raw axes. The nearest nominal interval
      count determines missing count; four missing samples or repaired periods outside
      inclusive two-percent tolerance reject the recording.
    - Inserted samples carry index provenance and retain continuous FIR/detector state
      and ordinary activity-based eligibility. Annotation views show repair positions
      and counts without per-gap confirmation.
    - Internal and External IMU mappings pass selected source values through unchanged;
      acquisition-specific transforms remain outside the application.
    - Viewport waveform projection reads original mapped samples without mutation,
      uses shared contiguous half-open buckets for Internal and External IMUs, and
      emits a pixel-bounded immutable raw or Min/Max plus arithmetic-mean representation
      without changing annotation indexes.
  entrypoints:
  - path: src/dual_imu_collision_studio/domain/data_workspace/service.py
    symbol: WorkspaceService
    kind: class
  public_symbols:
  - path: src/dual_imu_collision_studio/domain/data_workspace/contracts.py
    symbol: WorkspaceCommandPort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/data_workspace/contracts.py
    symbol: TabularInputPort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/data_workspace/contracts.py
    symbol: WorkspaceEventPort
    kind: protocol
  - path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: WaveformViewportProjection
    kind: class
```
