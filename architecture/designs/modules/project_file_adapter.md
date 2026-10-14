# project_file_adapter

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | project_file_adapter |
| version | 1 |
| kind | module |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: project_file_adapter
  level: L3+
  role: adapter
  implementation_status: implemented
  paths:
  - src/dual_imu_collision_studio/adapters/desktop/project_store.py
  parent: null
  depends_on:
  - project_session
  implements_ports:
  - project.file-storage
  description:
    purpose: Implement strict .dicsproj JSON I/O, atomic replacement, and external
      source-file identity hashing.
    input_ports: []
    output_ports: []
    emitted_events: []
    owned_state: []
    side_effects:
    - description: Read project and source files and atomically replace a user-selected
        project file.
    errors: []
    invariants:
    - Duplicate JSON keys, non-finite values, executable objects, and incompatible
      roots are rejected.
    - A failed write never replaces the prior destination.
  entrypoints:
  - path: src/dual_imu_collision_studio/adapters/desktop/project_store.py
    symbol: AtomicProjectStore
    kind: class
  public_symbols:
  - path: src/dual_imu_collision_studio/adapters/desktop/project_store.py
    symbol: AtomicProjectStore
    kind: class
```
