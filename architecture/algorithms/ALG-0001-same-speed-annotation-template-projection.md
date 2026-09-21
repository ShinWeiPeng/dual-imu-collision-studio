# ALG-0001: Same-speed annotation template projection

## Metadata

- Status: accepted
- Owner module: `data_workspace`
- Product feature: Explicit Reference Cycle reuse across recordings with the same Robot Speed
- Flow IDs: `prepare-workspace`
- Related ADRs: None
- Source paths: `src/dual_imu_collision_studio/domain/data_workspace/model.py`, `src/dual_imu_collision_studio/domain/data_workspace/service.py`
- Test and benchmark paths: `tests/test_workspace.py`, `tests/test_annotation_controller.py`, `tests/test_qml_smoke.py`
- Supersedes: None

## Problem and observable success

Repeated Robot programs may contain any non-empty combination of Pick, Put, and Fork Collision plus reason-bearing Ignore ranges at stable positions inside each Cycle, but Collision Offset changes waveform clarity. The user selects a clearly identifiable Cycle once; the application must atomically preserve and confirm that source, propose corresponding intervals in every Cycle of every recording at exactly the same confirmed Robot Speed, and derive destination Cycle proposals from one manually aligned Anchor without asserting generated destination proposals as truth.

Success means source labels never disappear, activation is all-or-nothing, projected sample indexes and generated Cycle boundaries are deterministic, different speeds receive no proposal, Ignore reasons and manual intervals are preserved, and every generated destination proposal displays source recording/Cycle provenance until final confirmation.

## Inputs, outputs, units, ranges, and data-quality assumptions

- Input reference: one selected Cycle whose non-negative Pick, Put, and Fork Collision counts sum to at least one; any individual class may be absent, and zero or more Ignore intervals carry non-empty reasons.
- Input grouping key: exact confirmed Robot Speed in mm/s.
- Cadence source: at least two confirmed source Cycles; the selected Cycle supplies the generated Cycle duration and the source Cycle starts supply the median start-to-start period.
- Destination: recordings at that exact speed with existing Cycle intervals, or one manually drawn first complete Anchor Cycle when no destination Cycle exists yet.
- Event phases are dimensionless values in `[0, 1]`; output uses half-open sample indexes `[start, end)`.
- Cycle boundaries and manual labels remain user-provided ground truth.

## Constraints and quantitative acceptance thresholds

- No automatic waveform classification is performed.
- No cross-speed projection is permitted.
- `Use as Reference` confirms only the selected source Cycle and its contained labels before activation; every generated destination Cycle/event/Ignore remains provisional until `Confirm All Annotation Sets` succeeds.
- A projected positive event never overwrites or overlaps a manual positive event. Ignore overlap is legal and masks the overlapped samples.
- Sample snapping uses the nearest destination sample; an exact half-sample tie selects the earlier sample.

## Candidate methods and comparative evidence

1. Full waveform matching across destination recordings was rejected because it adds a second classification algorithm, false-match review, and data-dependent cost when the user has established identical same-speed timing.
2. Manual creation of every destination Cycle was rejected because it preserves repetitive work and leaves the reported cross-recording workflow gap.
3. One manual destination Anchor plus deterministic source cadence was selected because it resolves capture alignment without waveform-matching uncertainty; absolute timestamp copying and cross-speed normalization remain forbidden.

## Selected method and reasons for rejecting alternatives

Validate the selected source Cycle and every contained label first. On success, atomically convert those source intervals to confirmed values without changing identity, build the template, and only then replace destination proposals. Store each reference label's start and end relative to the selected Cycle, including the Ignore reason. Apply those phases only to destination Cycles whose recording has the exact same Robot Speed. If a destination has only its manually drawn first complete Anchor Cycle, generate subsequent full in-bounds Cycles from the template duration and cadence before projecting inner labels. Existing manual intervals take precedence; remaining legal intervals become provisional proposals with provenance.

## Exact behavior, formula or pseudocode, boundaries, and tie-breaking

For reference Cycle `[C0, C1)` and event `[E0, E1)`:

```text
start_phase = (E0 - C0) / (C1 - C0)
end_phase   = (E1 - C0) / (C1 - C0)
```

For destination Cycle `[D0, D1)`:

```text
projected_start = D0 + nearest_sample(start_phase * (D1 - D0))
projected_end   = D0 + nearest_sample(end_phase   * (D1 - D0))
```

`nearest_sample(x)` selects the nearest integer and chooses the lower integer when the fractional part is exactly `0.5`. Results clamp to the destination Cycle and retain at least one sample. Template events are processed in reference start-time order. An existing manual interval of the same kind and ordinal wins; a remaining positive-event proposal that overlaps a retained positive event is omitted and leaves an annotation blocker. Ignore may overlap another interval because it has masking precedence.

For confirmed source Cycle starts `S[0..n-1]`, `n >= 2`:

```text
cycle_period_samples = median(S[i+1] - S[i])
reference_cycle_length_samples = C1 - C0
generated_start(k) = anchor_start + nearest_sample(k * cycle_period_samples), k in Z, k != 0
generated_end(k) = generated_start(k) + reference_cycle_length_samples
```

Generation extends backward and forward from the Anchor and keeps every complete non-overlapping Cycle within destination sample bounds. The manually drawn Anchor is retained exactly; generated Cycles and all projected inner labels are provisional and independently editable/deletable.

Reference activation computes the confirmed source snapshot, template, and every destination result before committing any controller state. Invalid source data leaves the source, prior template, and all destinations unchanged. Reactivating a valid reference removes only prior provisional proposals in that speed group, regenerates proposals from the new template, and preserves every manual interval.

## Parameters, calibration, versioning, and compatibility

There are no tunable parameters. Group membership uses the confirmed Robot Speed exactly. Cadence is the deterministic median of adjacent confirmed source Cycle starts and may be fractional; generated boundaries use the declared nearest-sample rule. The template exists only for the active application session and is not a saved project format.

## Time and space complexity and resource budgets

For `R` same-speed recordings, `C` Cycles, `T` template intervals, and `A` retained annotations, projection is bounded by `O(R × C × T × A)` with the current overlap check; cadence generation adds `O(C)` work. Expected event cardinality is small; waveform arrays are not copied. The static model is `estimated`; the existing Windows interaction benchmark remains the authority for the 100 ms p95 acceptance claim.

## Errors, degradation, fallback, and forbidden behavior

- Reject an invalid Cycle selection, fewer than two confirmed source Cycles, or a selected Cycle with no Pick, Put, or Fork Collision event at all; zero instances of an individual class are valid.
- Reject direct application to a different Robot Speed.
- Omit a proposal that would overlap manual truth; never delete or move the manual interval.
- If a destination has no Cycle, wait for one manual Anchor; after the Anchor is created, generate only complete in-bounds Cycles and expose all generated ranges as provisional.
- Forbidden: partially committing failed reference activation, confirming destination proposals automatically, waveform-matching Cycle boundaries, copying absolute timestamps, or projecting across speeds.

## Validation cases and evidence

- Golden phase vectors with unequal destination Cycle durations.
- Atomic source-confirmation success/failure vectors that preserve interval identity and never delete Pick/Collision/Ignore labels.
- Non-empty, recording-unique interval identity fixtures across provisional-to-confirmed replacement.
- Ignore reason round-trip and same-speed/different-speed projection fixtures.
- Anchor cadence vectors including fractional median cadence, recording-end truncation, and manual Anchor preservation.
- Dense-cadence vectors where period is shorter than duration and no generated Cycles may overlap.
- Event-count boundary vectors that accept `(1,0,1)`, each single-class tuple, and reject `(0,0,0)`.
- Same-speed/different-Offset and different-speed isolation fixtures.
- Manual-precedence and provenance assertions.
- Explicit activation and no-auto-propagation QML/controller tests.
- Final all-recording confirmation tests that convert destination proposals into confirmed truth only after all gates pass.

Commands:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_workspace.py tests\test_annotation_controller.py tests\test_qml_smoke.py -q
python tools\architecture\architecture_cli.py gate --phase development --manifest architecture\manifest.yaml --adoption architecture\adoption.yaml --baseline architecture\baseline.yaml --format text
```

## Risks and monitoring

The programmed event phase or Cycle cadence may drift despite equal speed. Generated destination Cycles and inner labels therefore remain visually provisional, expose provenance, and require explicit confirmation. A missing proposal is safer than overwriting manual truth.

## Human approval

- Approved by: Hugo Peng
- Approval date: 2026-08-24
- Approval reference: `SPEC-0001` revision 126, `DISC-103` through `DISC-108`, and the user's explicit `開始執行` authorization

## Pre-code architecture gate for revision 126

### Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Activate one same-speed reference and project it across recordings | `studio_application` | `data_workspace` | `studio_application` | Selected recording/Cycle identity from `StudioController` | `workspace.command` using `Recording` and `AnnotationTemplate` values | `studio_application` | Controller-owned session annotation snapshots and speed-template registry; no L1 mutable state | `studio_application->data_workspace`, QML->`StudioController` | `data_workspace->desktop_adapter`, sibling-domain edges |

### Type Ownership Matrix

| Type | Owner/level | Declaration | Semantic kind and visibility | Lifetime/mutability/authority | Consumers | Field impact | ABI/wire/storage impact |
|---|---|---|---|---|---|---|---|
| `AnnotationTemplateEvent` | `data_workspace` / L1 | `model.py` | Domain value / cross-module | Session / immutable / constructor only | `data_workspace`, `studio_application` | Expands kind to Ignore and adds optional reason | Python in-memory only; no ABI, wire, or storage format |
| `AnnotationTemplate` | `data_workspace` / L1 | `model.py` | Domain value / cross-module | Session / immutable / constructor only | `data_workspace`, `studio_application` | Adds reference duration and median period | Python in-memory only; no ABI, wire, or storage format |
| `AnnotationInterval` | `data_workspace` / L1 | `model.py` | Domain value / cross-module | Session / immutable / constructor only | `data_workspace`, `studio_application` | Adds a stable session identity; confirmation clears proposal provenance while preserving that identity | Python in-memory only; no ABI, wire, or storage format |
| `StudioController` | `studio_application` / L0 | `controller.py` | Composition mapping / module-public | Application / owner-mutable / `studio_application` | QML composition | No public named field change | Qt-facing behavior only; no persisted format |

### State Object Ownership Matrix

| State | Type/definition | Owner | Lifetime | Mutability and authority | Linkage/public leakage/pointer escape |
|---|---|---|---|---|---|
| Annotation snapshots and undo/redo maps | Owner-private `StudioController` instance fields | `studio_application` | Application session | Owner-mutable only; committed after full projection succeeds | Instance-private; immutable domain values cross the L0/L1 call only; no pointer escape |
| Speed-to-template registry | Owner-private `StudioController._annotation_templates` | `studio_application` | Application session | Owner-mutable only after atomic domain computations succeed | Instance-private; template snapshots are immutable; no pointer escape |
| Projection working set | Function-local immutable/replacement values | `data_workspace` and `studio_application` in their own scopes | One synchronous command | Local mutation only before commit | No linkage, public leakage, or address escape |

### Dependency and parent mapping

- Actual and intended production edges remain `studio_application -> data_workspace`, `studio_application -> desktop_adapter`, and QML -> `StudioController`; no new dependency edge is introduced.
- `data_workspace` remains the L1 semantic owner of template validation, cadence generation, phase projection, Ignore reasons, and immutable values.
- `studio_application` remains the L0 parent/orchestrator that maps selected recording indexes to domain `Recording` values and atomically commits all same-speed results.
- `desktop_adapter` renders commands and states only; it receives no domain mutation authority.

### Flow review

- As-is flow projects only into pre-existing destination Cycles and deletes provisional source labels before skipping source reconstruction; it fails functional admission for revision 126.
- Selected flow uses one manual Anchor plus source cadence, keeps the existing synchronous best-effort execution unit, performs no waveform copy, and preserves module/Port direction.
- Rejected waveform matching adds a classification stage, data-dependent search, and false-match policy; rejected all-manual Cycle creation keeps the reported usability failure.
- Model assurance is `estimated` for interaction cost. Functional properties are covered by deterministic public-seam tests; the existing Windows p95 benchmark remains required before a performance claim becomes validated.
