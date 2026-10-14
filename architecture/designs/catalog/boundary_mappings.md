# CAT-boundary_mappings

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-boundary_mappings |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: boundary_mappings
value:
- id: waveform-projection-to-desktop
  interaction: Map one immutable width-bounded raw or Min/Max plus arithmetic-mean
    waveform viewport projection into StudioController-owned primitive Qt values for
    downstream desktop rendering without exposing original arrays.
  producer: data_workspace
  consumer: studio_application
  parent: studio_application
  producer_contract: waveform-viewport-projection
  consumer_contract: studio-controller
  mapping_owner: studio_application
  state_objects: []
  allowed_edges:
  - studio_application->data_workspace
  forbidden_edges:
  - data_workspace->studio_application
- id: workspace-to-project
  interaction: Map recording mappings, test conditions, annotations, templates, confirmation,
    inserted-sample provenance, and source references into project-owned values without
    waveform arrays; restore identical repaired timeline and markers on reopen.
  producer: data_workspace
  consumer: project_session
  parent: studio_application
  producer_contract: workspace-snapshot
  consumer_contract: project-document
  mapping_owner: studio_application
  state_objects: []
  allowed_edges:
  - studio_application->data_workspace
  - studio_application->project_session
  forbidden_edges:
  - data_workspace->project_session
  - project_session->data_workspace
- id: profile-to-project
  interaction: Map optional completed immutable Profiles and Qualification coverage
    into version-bound project-owned values.
  producer: profile_export
  consumer: project_session
  parent: studio_application
  producer_contract: semantic-profile
  consumer_contract: project-document
  mapping_owner: studio_application
  state_objects: []
  allowed_edges:
  - studio_application->profile_export
  - studio_application->project_session
  forbidden_edges:
  - profile_export->project_session
  - project_session->profile_export
- id: project-to-workspace
  interaction: Transactionally map a validated project recording set back into workspace-owned
    mappings and annotations after every source is re-read and fingerprint-verified,
    preserve all stored interval identities, and restore the application-owned next
    manual annotation identity above every persisted manual annotation-N suffix.
  producer: project_session
  consumer: data_workspace
  parent: studio_application
  producer_contract: project-document
  consumer_contract: workspace-snapshot
  mapping_owner: studio_application
  state_objects: []
  allowed_edges:
  - studio_application->project_session
  - studio_application->data_workspace
  forbidden_edges:
  - project_session->data_workspace
  - data_workspace->project_session
- id: project-to-profile
  interaction: Map compatible completed project Profile values back into profile_export-owned
    immutable semantic Profiles.
  producer: project_session
  consumer: profile_export
  parent: studio_application
  producer_contract: project-document
  consumer_contract: semantic-profile
  mapping_owner: studio_application
  state_objects: []
  allowed_edges:
  - studio_application->project_session
  - studio_application->profile_export
  forbidden_edges:
  - project_session->profile_export
  - profile_export->project_session
- id: workspace-to-learning
  interaction: Convert a committed workspace snapshot into learning-owned recording,
    interval, condition, discontinuity, and array values inside an immutable request;
    derived Normal intervals already subtract the timestamp-based Collision onset-through-150-ms
    response windows used by Qualification.
  producer: data_workspace
  consumer: learning_qualification
  parent: studio_application
  producer_contract: workspace-snapshot
  consumer_contract: learning-request
  mapping_owner: studio_application
  state_objects: []
  allowed_edges:
  - studio_application->data_workspace
  - studio_application->learning_qualification
  forbidden_edges:
  - data_workspace->learning_qualification
  - learning_qualification->data_workspace
- id: learning-settings-to-project
  interaction: Map editable next-run Learning settings and immutable captured run
    provenance to or from project-owned semantic values, applying explicit fixed-grid
    empty defaults only when legacy fields are absent.
  producer: learning_qualification
  consumer: project_session
  parent: studio_application
  producer_contract: learning-settings
  consumer_contract: project-document
  mapping_owner: studio_application
  state_objects: []
  allowed_edges:
  - studio_application->learning_qualification
  - studio_application->project_session
  forbidden_edges:
  - learning_qualification->project_session
  - project_session->learning_qualification
- id: qualification-to-export
  interaction: Convert every user-selected retained round winner into an independent
    semantic profile export command.
  producer: learning_qualification
  consumer: profile_export
  parent: studio_application
  producer_contract: qualification-result
  consumer_contract: profile-export-request
  mapping_owner: studio_application
  state_objects: []
  allowed_edges:
  - studio_application->learning_qualification
  - studio_application->profile_export
  forbidden_edges:
  - learning_qualification->profile_export
  - profile_export->learning_qualification
```
