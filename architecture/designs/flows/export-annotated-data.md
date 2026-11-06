# export-annotated-data

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | export-annotated-data |
| version | 1 |
| kind | flow |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: export-annotated-data
  owner: studio_application
  description: Export every confirmed recording as an independently analyzable JSONL
    without Training or model inputs.
  trigger:
    kind: command
    ref: workspace.annotated-export
    description: User chooses an existing output parent folder after Confirm All.
  steps:
  - id: export-annotated-data.step-1
    order: 1
    module: studio_application
    action: Reject unconfirmed/busy inputs; capture current immutable metadata and
      borrowed arrays once, lock mutation and dispatch one background job.
    receives:
    - workspace.annotated-export
    emits: []
    state_changes: []
    side_effects:
    - Schedule a worker and guard mutation.
  - id: export-annotated-data.step-2
    order: 2
    module: data_workspace
    action: Validate complete confirmed recordings and provenance, and derive existing-policy
      Normal evidence without altering annotations.
    receives:
    - workspace.annotated-export
    emits: []
    state_changes: []
    side_effects: []
  - id: export-annotated-data.step-3
    order: 3
    module: desktop_adapter
    action: Stream each self-contained JSONL with end/count/digest into one new staging
      directory; cancel or fail safely; publish only after all files finish.
    receives:
    - workspace.annotated-file-output
    emits: []
    state_changes: []
    side_effects:
    - Create and publish a new job-owned batch directory.
  - id: export-annotated-data.step-4
    order: 4
    module: studio_application
    action: Receive queued outcome for current export_id, clear busy and references,
      then publish exactly one terminal result; deferred close can resume.
    receives: []
    emits:
    - annotations.exported
    - annotations.export-failed
    - annotations.export-cancelled
    state_changes: []
    side_effects: []
  success:
    result: Every confirmed recording has one complete self-contained file in a new
      visible batch folder.
    events:
    - annotations.exported
  errors:
  - condition: Confirmation is unavailable or work is mutually exclusive.
    event: annotations.export-failed
    handling: Reject before work; preserve the session.
  - condition: Validation, file output or publication fails.
    event: annotations.export-failed
    handling: Clean only verified job-owned staging files; preserve sources and existing
      exports.
  - condition: Cancellation is observed before publication.
    event: annotations.export-cancelled
    handling: Release job resources and do not publish a partial batch.
```
