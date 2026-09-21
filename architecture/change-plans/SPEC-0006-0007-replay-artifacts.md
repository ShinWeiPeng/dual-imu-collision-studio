# SPEC-0006 / SPEC-0007 Replay and Model Artifact Pre-Code Design

Status: confirmed for implementation by the user's `開始執行SPEC-0007及SPEC-0006` on 2026-08-27.

## Boundary Design Table

| Boundary | Demand owner | Provider | Input | Output | Failure authority |
|---|---|---|---|---|---|
| `learning.replay-export` | `learning_qualification` | `studio_application` caller | One retained candidate and one complete recording | Immutable full-recording `ReplayEvidence` and exact 22-column row stream | Learning rejects unavailable candidate/recording evidence; the application rejects concurrent work |
| `learning.replay-file-output` | `learning_qualification` | `desktop_adapter` | Destination and deterministic UTF-8 CSV rows | Atomically replaced Replay CSV | Desktop adapter classifies temporary-file, flush, and replace failures |
| `learning.model-export` | `learning_qualification` | `studio_application` caller | One retained candidate and its sample-rate/numeric metadata | Deterministic Model TXT line stream | Learning rejects incomplete model metadata; the application rejects concurrent work |
| `learning.model-file-output` | `learning_qualification` | `desktop_adapter` | Destination and deterministic UTF-8 Model TXT lines | Atomically replaced Model TXT | Desktop adapter classifies temporary-file, flush, and replace failures |
| Qt completion bridges | `studio_application` | Qt queued signals | Terminal path or bounded error text | UI status only | Application owns presentation and concurrency state; Qt types do not enter L1 |

Learning owns replay arithmetic, detector semantics, qualification masks, the CSV schema, and the Model TXT schema. The desktop adapter owns filesystem technology and atomic replacement. The composition root owns selection snapshots, suggested filenames, background dispatch, and UI events.

## Type Ownership Matrix

| Type | Owner | Visibility | Mutability | Consumers |
|---|---|---|---|---|
| `ReplayEvidence` | `learning_qualification` | cross-module | immutable | Learning, application, CSV adapter |
| `ReplayCsvFilePort` | `learning_qualification` | cross-module port | immutable protocol | application, CSV adapter |
| `ModelTextFilePort` | `learning_qualification` | cross-module port | immutable protocol | application, Model TXT adapter |
| `AtomicReplayCsvWriter` | `desktop_adapter` | adapter implementation | stateless | composition root |
| `AtomicModelTextWriter` | `desktop_adapter` | adapter implementation | stateless | composition root |
| `_ReplayCsvExportSignals`, `_ReplayCsvExportWorker` | `studio_application` | private | worker-lifetime | controller only |
| `_ModelTextExportSignals`, `_ModelTextExportWorker` | `studio_application` | private | worker-lifetime | controller only |
| Existing candidate, detector, qualification, and project values | `learning_qualification` / existing owner | unchanged | unchanged | unchanged |

No existing persisted or public named type is removed. Replay selection metadata retained inside `ReplayEvidence` is diagnostic compatibility data and no longer controls the recording-only export.

## State Object Ownership Matrix

| State | Owner | Mutation authority | Lifetime | Release rule |
|---|---|---|---|---|
| Active Replay CSV worker reference | `studio_application` | `StudioController` | one accepted export | cleared on queued success or failure |
| Active Model TXT worker reference | `studio_application` | `StudioController` | one accepted export | cleared on queued success or failure |
| FIR prediction/detector arrays | `learning_qualification` | `LearningService` | one replay/qualification call | released with immutable evidence/result |
| CSV and Model TXT temporary files | `desktop_adapter` | corresponding atomic writer | one write attempt | atomically replace destination on success; remove temporary file on failure |

No new module-global, file-scope mutable, shared singleton, or escaping runtime state object is introduced.

## Dependency Edges

| Edge | Actual before change | Intended | Decision |
|---|---|---|---|
| `studio_application -> learning_qualification` | yes | yes | preserve; add recording-only replay and Model TXT commands |
| `studio_application -> desktop_adapter` | yes | yes | preserve; compose both atomic writers |
| `desktop_adapter -> learning_qualification` | yes | yes | preserve demand-owned file-port direction |
| `learning_qualification -> desktop_adapter` | no | forbidden | domain cannot import filesystem or Qt implementations |
| `learning_qualification -> Qt/filesystem` | no | forbidden | technology remains outside L1 |

No module dependency edge changes are required.

## Parent Mappings

| Interaction | Producer | Consumer | Parent/mapping owner |
|---|---|---|---|
| Selected recording/candidate to full replay | `studio_application` | `learning_qualification` | `studio_application` |
| Replay row stream to atomic CSV | `learning_qualification` | `desktop_adapter` | demand-owned `learning.replay-file-output`, composed by `studio_application` |
| Candidate model stream to atomic TXT | `learning_qualification` | `desktop_adapter` | demand-owned `learning.model-file-output`, composed by `studio_application` |
| Export result to QML | background workers | `desktop_adapter` UI | private queued bridges owned by `studio_application` |

All touched modules retain `studio_application` as their L0 parent. No cross-parent exception or ADR is required.

## Algorithm and Qualification Plan

- Fit rows are Cycle-contained `Normal Robot Motion`, `Robot Pick`, or `Robot Put`; `Collision`, `Ignore`, and Cycle-external rows are excluded from Training.
- Excluded gaps split fit history so FIR feature windows cannot cross an excluded sample.
- FIR prediction, residual, normalized residual, score, collision ratio, detector state, and triggers run across each complete continuous recording segment.
- Only the first `tap_count - 1` rows after the recording start or a real timestamp discontinuity may be invalid.
- Ignore does not reset or pause the detector. Ignore rows and triggers remain in trace evidence but are excluded only from Training and qualification pass/fail counts.
- Collision passes when a trigger occurs within the inclusive 20 ms acceptance window from interval start.
- False triggers in Normal, Pick, Put, and Cycle-external non-Ignore rows count. Cycle-external false events aggregate into the compatibility field `normal_false_events`.

## Flow Candidate Comparison

| Candidate | Boundary depth | Compatibility | Decision |
|---|---|---|---|
| Keep Cycle/Event as export selectors | shallow UI change, wrong semantic command | conflicts with recording-only SPEC-0006 and masks full-domain defects | reject |
| Make replay recording-only and preserve internal evidence shape | deep Learning seam with stable stored types | meets both specs without project/header schema migration | select |
| Add Model TXT to profile header export | conflates diagnostic model artifact with qualified firmware profile | changes unrelated profile contract | reject |
| Add a Learning-owned Model TXT port and desktop atomic writer | symmetric with Replay CSV; one new explicit port | keeps serialization and filesystem ownership clear | select |

## Expected Manifest Diff

- Amend application/Learning invariants for recording-only full-domain replay, detector continuity, Training eligibility, and non-Ignore qualification.
- Add `learning.model-export` and `learning.model-file-output`; publish terminal model export events through the existing single application artifact event sink.
- Add `ModelTextFilePort`, `AtomicModelTextWriter`, `_ModelTextExportSignals`, and `_ModelTextExportWorker` type declarations and mappings.
- Amend `export-replay-csv`; add `export-model-txt`, its workload, execution mapping, and channel.
- Reuse the bounded `replay-export-worker` execution unit for mutually exclusive CSV and TXT export work; no new scheduler or dependency edge is introduced.

## TDD Seams

The confirmed public seams are `LearningService.build_fit_evidence`, `LearningService.replay_candidate`, qualification results produced through Learning, deterministic CSV/Model TXT line generation, both file-port implementations, and `StudioController` recording-only export properties/commands. Tests observe complete-domain validity, discontinuity warm-up, eligibility masks, detector trace continuity, non-Ignore pass/fail accounting, exact artifact schemas, filenames, atomic replacement, and QML-visible APIs without mocking private arithmetic loops.
