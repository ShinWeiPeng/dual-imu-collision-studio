# SPEC-0019 pre-code architecture gate

## Responsibility and observable behavior

`learning_qualification` remains the sole semantic owner of detector Score replay and per-recording Qualification evidence. During the existing whole-recording Qualification pass it derives one immutable chronological tuple of per-Collision SNR values. `studio_application` only formats that tuple as one `Collision SNR (dB)` QML value; it does not recompute or reinterpret analytical evidence. No detector decision, Threshold, event, Queue, execution unit, persistent schema, Replay CSV, or Profile contract changes.

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Publish per-recording Collision SNR evidence with a completed candidate | `learning_qualification` | `studio_application` | `studio_application` | `QualificationResult` containing `RecordingQualification` | Controller-owned immutable QML map with `collisionSnr` display text | `studio_application` | Completed immutable Qualification result only | `studio_application->learning_qualification`; QML -> `StudioController` | `learning_qualification->desktop_adapter`; QML or controller recomputation of detector Score/SNR |

## Type Ownership Matrix

| Type | Owner / level | Declaration | Semantic role and visibility | Lifetime / mutability / authority | Consumers and referenced project types | Field impact | ABI / wire / storage impact |
|---|---|---|---|---|---|---|---|
| `RecordingQualification` | `learning_qualification` / L1 | `src/dual_imu_collision_studio/domain/learning/model.py` | Domain value / cross-module | Completed candidate lifetime / immutable / Learning constructs | Learning and L0; no referenced project types | Add `collision_snrs_db`, an ordered tuple whose entries are finite dB values or `None` for unavailable event evidence | Python in-process value only; no ABI, wire, project, Profile, Model TXT, or Replay CSV change |
| `QualificationResult` | `learning_qualification` / L1 | `src/dual_imu_collision_studio/domain/learning/model.py` | Domain value / cross-module | Completed or cancelled run / immutable / Learning constructs | Learning and L0; references `QualifiedCandidate` and transitively `RecordingQualification` | No direct field change; carries the enriched existing nested result | No ABI, wire, or storage change |
| `StudioController` | `studio_application` / L0 | `src/dual_imu_collision_studio/adapters/desktop/controller.py` | Composition mapping / module-public | Application lifetime / owner-mutable / L0 only | QML and Learning-owned immutable results | Add one derived string key to the existing per-recording QVariant map | Qt-facing presentation only; no storage impact |

## State Object Ownership Matrix

| State object | Definition / type | Owner | Lifetime | Mutability and authority | Linkage / public leakage / pointer escape |
|---|---|---|---|---|---|
| Completed retained candidates | Existing controller-private list of immutable `QualifiedCandidate` values | `studio_application` | Until new run or project replacement | L0 replaces the collection; nested Learning evidence is immutable | Instance-private; no new address or mutable authority crosses a boundary |
| Qualification worker metrics | Existing local `dict` returned for one recording job | `learning_qualification` | One job and aggregation pass | Learning-local construction only | Stack/local process value; serialized only through the existing worker result channel |

No mutable file-scope, static, thread-local, external-linkage, or address-crossing state is added or changed.

## Dependency edges and parent mapping

- Actual edges: `studio_application -> learning_qualification`; QML -> `StudioController`; `history_worker_adapter -> learning_qualification` for the existing execution Port.
- Intended edges: unchanged.
- Parent mapping: `studio_application` receives the Learning-owned immutable result and maps `collision_snrs_db` to a display-only `collisionSnr` string. `learning_qualification` never depends on QML or the desktop adapter.
- Forbidden: SNR calculation in QML/L0, direct Learning dependency on Qt, or persistence/export of this presentation evidence.

## Flow review

| Field | Selected candidate: derive in L1 during existing Qualification | Rejected candidate: recompute in L0 on demand |
|---|---|---|
| Identity | `learn-and-qualify`; best-effort offline analysis; owner `learning_qualification` | Same user trigger, but L0 becomes analytical owner |
| Ordered path | Existing Score cache -> existing recording replay -> Learning-owned SNR derivation -> immutable `RecordingQualification` -> L0 formatting -> QML | Learning result -> L0 reacquires recording/model -> duplicate Score replay/SNR -> QML |
| Functional admission | Preserves semantic ownership, parent mapping, deterministic chronological order, and existing failure propagation | Fails ownership/locality: L0 duplicates target arithmetic and must access child inputs beyond the completed result contract |
| Data and cost | One tuple with `C` optional floats; no new Queue, process, callback, copy of sample arrays, persistence, or fan-out. Static cost `O(N + C*W)` time and `O(N + C)` temporary/result space, where `W` is the existing 150 ms sample window. | Repeats `O(N*L)` FIR/Score replay or requires leaking cached Score arrays across the boundary; increases UI latency and data movement |
| Build and budget | Existing Python/PySide6 Windows desktop composition; no new platform-sensitive choice or performance claim. Added work is within an already completed whole-recording replay. | UI-thread or background orchestration changes would need additional execution and cancellation contracts |
| Assurance | `estimated`; deterministic golden vectors and full-flow regressions are sufficient because no timing/resource acceptance threshold or benchmark trigger changes the recommendation | Rejected on functional admission before performance comparison |
| Evolution | Formula changes remain local to L1 plus its algorithm record/tests; presentation changes remain local to L0/QML | Formula changes require coordinated L0 access to Learning internals and duplicate tests |

No hard/soft real-time workload, Task, Thread, Queue, channel, priority, affinity, scheduler, data-layout optimization, or platform variant changes. The 150 ms interval is an offline Qualification response window, not a scheduling deadline, so no scheduling study or on-device validation is triggered by SPEC-0019.

## Algorithm screening

Per-Collision Detector Score SNR requires a full Algorithm Design Record because it performs a user-visible scoring calculation with exact failure behavior. `learning_qualification` owns [ALG-0007](../algorithms/ALG-0007-per-collision-detector-score-snr.md). The formula changes the nested public output field of `RecordingQualification`, so the manifest Type Catalog, `learn-and-qualify` Flow description, generated System/L0/L1 views, code, and tests change together.

## Planned manifest and Description Views impact

- Extend `recording-qualification` with `collision_snrs_db` ownership, units, order, and unavailable semantics.
- Extend `learning_qualification` invariants and `learn-and-qualify.step-3` to name ALG-0007 and the immutable evidence commit.
- Extend the L0 presentation invariant without adding a Port, Event, state object, mapping type, or dependency edge.
- Regenerate `architecture/ARCHITECTURE.md`, `architecture/generated/system.md`, `architecture/generated/studio_application.md`, `architecture/generated/learning_qualification.md`, and adoption readiness projections only through `architecture_cli.py render`.

## Validation matrix

| Gate | Command / method | Pass condition | Evidence |
|---|---|---|---|
| Spec | `spec_contract.py validate --spec specs/SPEC-0019-recording-collision-snr.md` | PASS with no uncovered REQ/AC or scope creep | JSON console output |
| Design | `python tools/architecture/architecture_cli.py gate --phase design ...` | Exit 0 / VERIFIED | Text console output |
| Domain | Focused `pytest` tests through `LearningService.qualify_model` | Golden SNR vectors, chronological variable counts, and unavailable cases pass | pytest output |
| Mapping/UI | Focused controller and QML smoke tests | Exact combined string and table column binding pass | pytest output / optional screenshot |
| Regression | Full project test suite | Exit 0 | pytest output |
| Architecture | Required development gate from `AGENTS.md` | Exit 0 / VERIFIED, generated views current | Text console output |
| Review | Standards and SPEC-0019 traceability axes | No hard finding, uncovered REQ/AC, incorrect behavior, or scope creep | Two-axis review report |
