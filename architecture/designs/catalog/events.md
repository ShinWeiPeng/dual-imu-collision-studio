# CAT-events

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-events |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: events
value:
- id: workspace.changed
  owner: data_workspace
  output_port: workspace.events
  delivery: at-most-once
  envelope:
  - event_type
  - source
  - correlation_id
  - stream_id
  - sequence
  - payload
  lifecycle:
  - received
  - validated
  - processing
  - succeeded
  - failed
  description:
    purpose: Report a committed semantic workspace change.
    emitted_when: Import, mapping, condition, cycle, or annotation validation has
      committed.
    payload_fields:
    - name: snapshot
      type: WorkspaceSnapshot
      meaning: Immutable workspace data for downstream use.
    intended_consumers:
    - studio_application
- id: learning.progressed
  owner: learning_qualification
  output_port: learning.events
  delivery: at-most-once
  envelope:
  - event_type
  - source
  - correlation_id
  - stream_id
  - sequence
  - payload
  lifecycle:
  - received
  - validated
  - processing
  - succeeded
  - failed
  description:
    purpose: Report bounded progress without exposing mutable worker state.
    emitted_when: A progress interval or learning stage boundary is reached.
    payload_fields:
    - name: progress
      type: LearningProgress
      meaning: Current stage, completed work, fallback scope, and optional typed Loss
        evidence.
    intended_consumers:
    - studio_application
    - desktop_adapter
- id: learning.completed
  owner: learning_qualification
  output_port: learning.events
  delivery: at-most-once
  envelope:
  - event_type
  - source
  - correlation_id
  - stream_id
  - sequence
  - payload
  lifecycle:
  - received
  - validated
  - processing
  - succeeded
  - failed
  description:
    purpose: Report deterministic qualification and ranking results.
    emitted_when: Exact typed replay and fallback evaluation have completed.
    payload_fields:
    - name: result
      type: QualificationResult
      meaning: Ranked kernels and accepted speed coverage.
    intended_consumers:
    - studio_application
    - desktop_adapter
- id: learning.cancelled
  owner: learning_qualification
  output_port: learning.events
  delivery: at-most-once
  envelope:
  - event_type
  - source
  - correlation_id
  - stream_id
  - sequence
  - payload
  lifecycle:
  - received
  - validated
  - processing
  - succeeded
  - failed
  - cancelled
  description:
    purpose: Report user cancellation together with the last committed complete-candidate
      result.
    emitted_when: Accepted Learning work observes cancellation after atomically freezing
      its current partial QualificationResult.
    payload_fields:
    - name: result
      type: QualificationResult
      meaning: Immutable candidates completed before cancellation, with either qualified
        Replay candidates or the existing diagnostic fallback subset.
    intended_consumers:
    - studio_application
    - desktop_adapter
- id: profile.exported
  owner: profile_export
  output_port: profile.events
  delivery: at-most-once
  envelope:
  - event_type
  - source
  - correlation_id
  - stream_id
  - sequence
  - payload
  lifecycle:
  - received
  - validated
  - processing
  - succeeded
  - failed
  description:
    purpose: Report that the selected profile header was saved.
    emitted_when: The file adapter confirms the complete write.
    payload_fields:
    - name: path
      type: string
      meaning: Saved header path.
    intended_consumers:
    - studio_application
    - desktop_adapter
- id: replay.exported
  owner: studio_application
  output_port: replay.events
  delivery: at-most-once
  envelope:
  - event_type
  - source
  - correlation_id
  - stream_id
  - sequence
  - payload
  lifecycle:
  - received
  - validated
  - processing
  - succeeded
  - failed
  description:
    purpose: Report that one accepted Replay CSV export committed its destination.
    emitted_when: The background writer has flushed the complete temporary file and
      atomically replaced the destination.
    payload_fields:
    - name: path
      type: string
      meaning: Saved CSV destination path.
    intended_consumers:
    - desktop_adapter
- id: replay.export-failed
  owner: studio_application
  output_port: replay.events
  delivery: at-most-once
  envelope:
  - event_type
  - source
  - correlation_id
  - stream_id
  - sequence
  - payload
  lifecycle:
  - received
  - validated
  - processing
  - succeeded
  - failed
  description:
    purpose: Report that one accepted Replay CSV export failed without replacing its
      destination.
    emitted_when: CSV rendering, temporary-file flushing, or atomic replacement raises
      a bounded failure.
    payload_fields:
    - name: reason
      type: string
      meaning: Bounded user-visible failure message.
    intended_consumers:
    - desktop_adapter
- id: model.exported
  owner: studio_application
  output_port: replay.events
  delivery: at-most-once
  envelope:
  - event_type
  - source
  - correlation_id
  - stream_id
  - sequence
  - payload
  lifecycle:
  - received
  - validated
  - processing
  - succeeded
  - failed
  description:
    purpose: Report that one accepted Model TXT export committed its destination.
    emitted_when: The background writer has flushed the complete temporary file and
      atomically replaced the destination.
    payload_fields:
    - name: path
      type: string
      meaning: Saved Model TXT destination path.
    intended_consumers:
    - desktop_adapter
- id: model.export-failed
  owner: studio_application
  output_port: replay.events
  delivery: at-most-once
  envelope:
  - event_type
  - source
  - correlation_id
  - stream_id
  - sequence
  - payload
  lifecycle:
  - received
  - validated
  - processing
  - succeeded
  - failed
  description:
    purpose: Report that one accepted Model TXT export failed without replacing its
      destination.
    emitted_when: Model rendering, temporary-file flushing, or atomic replacement
      raises a bounded failure.
    payload_fields:
    - name: reason
      type: string
      meaning: Bounded user-visible failure message.
    intended_consumers:
    - desktop_adapter
```
