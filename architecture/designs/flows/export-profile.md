# export-profile

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | export-profile |
| version | 1 |
| kind | flow |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: export-profile
  owner: profile_export
  description: List all qualified frozen kernels with history, threshold and coverage
    for independent JSON export by kernel ID, with explicit name and file selection;
    retain header rendering for existing callers. New firmware JSON omits event release
    fields and accepts current shared-policy Qualification evidence without a separate
    deployment validation step. Application-owned background work snapshots inputs,
    checks evidence, renders and writes atomically while projecting real busy state.
    Missing or stale evidence requires Qualification from Replay. Historic headers
    and existing schema-1/schema-2 signal-format contracts remain unchanged.
  trigger:
    kind: command
    ref: profile.command
    description: The user exports any checked qualified kernels to one folder.
  steps:
  - id: export-profile.step-1
    order: 1
    module: profile_export
    action: Validate each qualified frozen profile, preserve execution settings and
      precision, render deterministic header or JSON content, and request individually
      approved atomic file writes.
    receives:
    - profile.command
    emits:
    - profile.exported
    state_changes: []
    side_effects:
    - Write selected header files through profile.file-output, replacing only files
      explicitly approved by the user.
  success:
    result: Separate C99 or C++17 profile headers are saved for all non-skipped kernels.
    events:
    - profile.exported
  errors: []
```
