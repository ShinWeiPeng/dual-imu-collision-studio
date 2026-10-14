# prepare-workspace

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | prepare-workspace |
| version | 1 |
| kind | flow |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: prepare-workspace
  owner: data_workspace
  description: Import recordings and produce a validated annotated workspace.
  trigger:
    kind: command
    ref: workspace.command
    description: The user advances the import or annotation workflow.
  steps:
  - id: prepare-workspace.step-1
    order: 1
    module: data_workspace
    action: Map QML drag coordinates to sample-index intervals, preserve session-local
      undo history, atomically confirm and activate a selected reference Cycle, generate
      provisional Cycles from one destination Anchor and the reference cadence, project
      provisional events and Ignore reasons only into equal-speed recordings, then
      validate mapping, samples, test conditions, cycles, Ignore reasons, and interval
      partition rules before committing truth. For annotation display, project the
      shared original-sample viewport through ALG-0008 into raw points or deterministic
      width-bounded Min/Max and arithmetic-mean buckets before L0 maps primitives
      to the desktop renderer.
    receives:
    - workspace.command
    - workspace.tabular-input
    emits:
    - workspace.changed
    state_changes: []
    side_effects: []
  - id: prepare-workspace.step-2
    order: 2
    module: studio_application
    action: After successful reference activation, clear both application-owned annotation
      selection representations before publishing refreshed UI state.
    receives:
    - workspace.changed
    emits: []
    state_changes: []
    side_effects: []
  success:
    result: A complete immutable workspace snapshot is available.
    events:
    - workspace.changed
  errors: []
```
