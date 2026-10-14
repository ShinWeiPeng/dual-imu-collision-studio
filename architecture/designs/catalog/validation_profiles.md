# CAT-validation_profiles

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-validation_profiles |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: validation_profiles
value:
- id: windows-application-validation
  applicability: required
  rationale: SPEC-0001 makes Windows runtime, responsiveness, memory, cancellation,
    and generated-header compatibility claims.
  target_claims:
  - Windows 10 and 11 startup
  - Clean and unclean process shutdown diagnostics
  - Last bounded Learning stage, progress, Speed, and Offset evidence after an unclean
    exit
  - Qt/QML warning capture without analytical payload persistence
  - UI responsiveness
  - worker progress and cancellation
  - memory preflight
  - up to eight candidate-fold workers and four complete-recording workers with no
    retries
  - terminal MemoryError cancellation and insufficient-hardware message
  - Training, Qualification and total durations with immutable run settings and Cycle-fold
    provenance
  - Fixed-grid or optimized captured Training mode, exact fixed selections, legacy
    default behavior and independent next-run versus completed-run project provenance
  - Session-only structured Loss log capped at 10,000 entries with deterministic overflow
    accounting and smart-follow presentation
  - Selected retained kernel exposes one exact ordered Qualification result row per
    supplied recording with row-bound Replay CSV export
  - Selected retained kernel exposes discrete active and excluded supplied speeds
    separately from Training and Qualified ranges, and preserves PASS, FAIL, and COVERAGE_GAP
    result meaning with an explicit reason
  - Cancelled Learning retains only fully qualified completed candidates, or the existing
    minimum-total-error diagnostic subset when none qualifies, and exposes the result
    through Candidate Dashboard and Analytical Replay without changing the Cancelled
    terminal state
  - Mapping Wizard completion preserves the Recordings ListView pixel viewport with
    legal-range clamping
  - Mapping Wizard Next and Finish reject invalid current-step or final inputs without
    losing selections and show every recoverable configuration, mapping, source-data,
    or file-read error inline
  - Reopened projects preserve stored annotation identities, allocate collision-free
    later manual annotation identities, and keep Replace Reference available for a
    newly selected valid Cycle
  - Successful reference activation clears stale visible and primary annotation selection
    state consistently
  - Active Learning admits estimated MLP batch bytes within available RAM minus 10
    percent of total physical RAM and terminates above sampled 90 percent system occupancy;
    aggregate process-tree Peak RSS remains diagnostic evidence
  - C99 and C++17 header compilation
  evidence_plan: tests and bounded Windows application smoke/performance evidence
    recorded before release
```
