# record-process-diagnostics

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | record-process-diagnostics |
| version | 1 |
| kind | flow |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: record-process-diagnostics
  owner: studio_application
  description: Persist bounded process and Learning execution evidence without changing
    analytical behavior.
  trigger:
    kind: command
    ref: diagnostics.output
    description: The process starts or exits, Learning changes stage/progress, an
      exception is observed, or Qt emits a warning.
  steps:
  - id: record-process-diagnostics.step-1
    order: 1
    module: studio_application
    action: Map the observation to primitive privacy-bounded fields and invoke the
      diagnostics output port.
    receives:
    - diagnostics.output
    emits: []
    state_changes: []
    side_effects:
    - Atomically update the clean-shutdown marker and append a bounded rotated diagnostic
      record through desktop_adapter.
  success:
    result: The latest bounded process or Learning state can be inspected after an
      unclean exit.
    events: []
  errors: []
```
