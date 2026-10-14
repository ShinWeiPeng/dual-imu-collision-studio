# manage-project

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | manage-project |
| version | 1 |
| kind | flow |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: manage-project
  owner: studio_application
  description: Save or transactionally reopen one strict external-reference project
    without mutating active state on failure.
  trigger:
    kind: command
    ref: project.command
    description: The user chooses Open Project, Save Project, or Save Project As.
  steps:
  - id: manage-project.step-1
    order: 1
    module: studio_application
    action: Map sibling-owned stable values to or from project_session, verify every
      source identity before commit, restore collision-free session-local manual annotation
      identity allocation without rewriting persisted identities, and invoke project.file-storage
      for strict JSON I/O. Restore frozen model and saved schema-versioned Qualification
      values without Training, Qualification or score replay; preserve legacy aggregate
      summaries and explicitly unavailable missing details.
    receives:
    - project.command
    - project.file-storage
    emits: []
    state_changes: []
    side_effects:
    - Read referenced recording files and one project file, or atomically replace
      one project file.
  success:
    result: The saved artifact is deterministic, or the complete validated project
      replaces the active session, exposes the restored stage, and safely allocates
      later manual annotation identities.
    events: []
  errors: []
```
