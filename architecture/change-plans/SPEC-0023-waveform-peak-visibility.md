# SPEC-0023 pre-code architecture gate

## Responsibility and observable behavior

`data_workspace` owns deterministic viewport projection from original mapped samples. `studio_application` requests the same viewport and pixel budget for Internal and External IMUs and maps the immutable result to Qt primitives. `desktop_adapter` draws existing raw polylines when visible samples fit the width, otherwise one thin vertical Min/Max stroke per bucket and channel overlaid with a continuous same-color polyline through bucket arithmetic means. Annotation ranges remain original half-open sample indexes. No module, port, event, dependency, execution unit, queue, persistent schema, or mutable runtime state is added.

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Project selected waveform viewport | `data_workspace` | `studio_application` | `studio_application` | Immutable `WaveformViewportProjection` | `StudioController`-owned primitive QVariant map consumed downstream by `WaveformItem` | `studio_application` | Existing selected `ImportedSamples`, read-only; QML-owned viewport and item geometry | `studio_application->data_workspace` | `data_workspace->studio_application`; `data_workspace->desktop_adapter`; original arrays entering QML |

## Type Ownership Matrix

| Type | Owner / level | Declaration | Semantic role and visibility | Lifetime / mutability / authority | Consumers and referenced project types | Field impact | ABI / wire / storage impact |
|---|---|---|---|---|---|---|---|
| `WaveformViewportProjection` | `data_workspace` / L1 | `src/dual_imu_collision_studio/domain/data_workspace/model.py` | Domain value / cross-module | One projection call / immutable / constructed only by `WorkspaceService` | L0; no referenced project types | Add three-channel arithmetic means beside existing mode, positions, minima/maxima, and covered half-open original index range | Python in-process only; no ABI, wire, or storage impact |
| `WorkspaceService` | `data_workspace` / L1 | `src/dual_imu_collision_studio/domain/data_workspace/service.py` | Domain service / module-public | Application process / stateless / data workspace algorithm authority | L0; returns `WaveformViewportProjection` | Add pure projection query | No ABI, wire, or storage impact |
| `StudioController` | `studio_application` / L0 | `src/dual_imu_collision_studio/adapters/desktop/controller.py` | Composition mapping / module-public | Application lifetime / existing owner-mutable controller / L0 | QML and data workspace public value | Add bounded viewport query returning primitives | Qt-facing presentation only; no storage impact |
| `WaveformItem` | `desktop_adapter` / L3+ | `src/dual_imu_collision_studio/adapters/desktop/waveform_item.py` | Framework adapter / module-public | One QML item / existing owner-mutable presentation state / adapter only | QML | Add a bounded projection property and envelope drawing branch | Qt-private representation only |

## State Object Ownership Matrix

| State object | Definition / type | Owner | Lifetime | Mutability and authority | Linkage / public leakage / pointer escape |
|---|---|---|---|---|---|
| Selected imported samples | Existing controller-private `_samples` mapping of `ImportedSamples` | `studio_application` coordinates; values semantically owned by `data_workspace` | Application session | Existing L0 replacement; projection reads arrays without mutation | Instance-private; full arrays do not cross into QML |
| Annotation viewport | Existing QML `viewportStart` / `viewportEnd` properties | `desktop_adapter` | Annotation page instance | QML gestures mutate; both panels read the same values | QML-private primitives; no pointer escape |
| Waveform render inputs | Existing/new `WaveformItem` private Python lists/dict | `desktop_adapter` | QML item instance | Replaced through Qt property setters by adapter authority | Instance-private bounded values only |

No mutable file-scope, static, thread-local, external-linkage, or address-crossing state is added.

## Dependency edges and parent mapping

- Actual edges: `studio_application -> data_workspace`; `studio_application -> desktop_adapter`; QML -> `StudioController`.
- Intended edges: unchanged.
- Parent mapping: L0 selects Internal or External original values, invokes the L1 pure query with the shared viewport and plot width, then converts the immutable projection to Qt primitives.
- Forbidden: data workspace imports PySide6; waveform item reads workspace arrays; QML receives complete original arrays; Internal and External use different bucket formulas.

## Flow review

| Field | Selected: viewport-aware Min/Max | Rejected: uniform point sampling |
|---|---|---|
| Identity | `prepare-workspace`; best-effort interactive display; owner `data_workspace` | Existing display path |
| Ordered path | Selected original array -> shared clamped half-open range -> raw values or contiguous integer buckets -> extrema plus arithmetic means -> immutable bounded projection -> L0 primitive map -> vertical strokes plus continuous mean polyline | Selected original array -> 800 evenly spaced indexes -> QML list -> renderer slices the already reduced list -> zigzag polyline |
| Functional admission | Every visible sample belongs to exactly one bucket; extrema and original annotation index semantics are preserved; both IMUs use identical boundaries | A one-sample impact between selected indexes can disappear and zoom cannot recover it |
| Data and cost | `O(3V)` traversal and `O(3W)` extrema, means, and positions for visible samples `V` and pixel width `W`; no queue, process, lock, retry, full-array Qt copy, or persistence | `O(3N)` indexing setup with at most 800 points, but loses user-visible extrema before viewport selection |
| Build and budget | Existing CPython/PySide6/NumPy Windows composition; maximum dataset p95 must be <=100 ms | Existing approach is fast but fails peak visibility |
| Assurance | Initially `estimated`; deterministic tests plus the declared Windows benchmark must calibrate/validate the 100 ms claim | Rejected on functional admission |
| Evolution | Projection policy and tests remain in one L1 owner; renderer remains a thin mode-specific adapter | Future peak-preserving changes remain entangled with controller/QML sampling |

No hard/soft real-time scheduling study is triggered: `interactive-workspace` remains best-effort. The explicit 100 ms p95 budget and million-row input trigger a Windows runtime benchmark before completion.

## Algorithm screening

Peak-preserving waveform projection requires a full record because filtering/downsampling changes a user-visible result and is constrained by latency and payload budgets. `data_workspace` owns [ALG-0008](../algorithms/ALG-0008-viewport-min-max-waveform.md), status `proposed`; user execution authorization confirms implementation scope but does not mark the algorithm record accepted.

## Planned manifest and Description Views impact

- Catalog `WaveformViewportProjection` and the L0 boundary mapping.
- Extend `data_workspace`, `desktop_adapter`, `prepare-workspace`, and the Windows data/microarchitecture profiles.
- Regenerate all Architecture Description Views only through `architecture_cli.py render`.

## Validation matrix

| Gate | Method | Pass condition |
|---|---|---|
| Spec | Validate `specs/SPEC-0023-waveform-peak-visibility.md` | PASS, no uncovered REQ/AC or scope creep |
| Design | Architecture CLI design gate | Exit 0 / VERIFIED before source edits |
| Domain | Unit/property tests | Exact bucket coverage, extrema, arithmetic means, endpoints, boundaries, invalid/empty/single cases, determinism |
| Mapping/UI | Controller, renderer, and QML tests | Width-bounded primitives, shared buckets, raw/envelope modes, continuous mean line, annotation indexes unchanged |
| Runtime | Maximum one-million-row Windows projection benchmark | p95 <=100 ms for envelope computation |
| Regression | Full pytest suite | Exit 0 |
| Architecture | Required development gate | Exit 0 / VERIFIED and generated views current |
| Review | Standards and SPEC-0023 axes | No hard finding, uncovered requirement, or scope creep |
