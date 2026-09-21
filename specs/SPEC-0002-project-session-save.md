---
spec_version: 1
spec_id: SPEC-0002
revision: 9
status: implemented
change_set: project-session-save
---

# Project Session Save

## Problem

Re-importing recordings and repeating Import & Map and Annotate & Classify makes iterative testing unnecessarily slow. The existing first-release contract explicitly keeps all workflow state session-local, so durable project persistence requires a new scoped change set.

## Solution

Add an explicit project save/open workflow that restores confirmed mappings, test conditions, annotations, selected recording, and any valid completed retained-kernel Qualification results available at save time. Project files reference source recordings rather than copying waveform samples and validate source identity before restored state can be used. Saving is user-initiated and guarded by a visible dirty state and a Save/Discard/Cancel decision before destructive session transitions. Opening is transactional and accepts only complete sets of byte-identical source recordings, with guided relinking for moved files. Persist each project as one human-readable UTF-8 JSON document using the `.dicsproj` extension and an explicit versioned schema.

## User Stories

- As an annotator, I can reopen prior mapping and annotation work without repeating it after every application restart.
- As a user, I am warned before closing or replacing a project that contains unsaved work.
- As an analyst, I cannot accidentally apply saved annotations to changed waveform data.
- As an analyst, I can save before, during, or after Learning; completed retained results are restored when they exist, while unfinished Learning is safely restarted rather than falsely resumed.
- As a maintainer, I can inspect a project file with ordinary text tools and identify its schema and source references without a proprietary database viewer.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | The application shall save and reopen project state needed to resume Import & Map and Annotate & Classify. The project shall store each external source path, worksheet identity, deterministic SHA-256 source-file fingerprint and byte size, confirmed row/time/axis mapping, Sample Rate, Robot Speed, Collision Offset, Cycle/Pick/Put/Fork Collision/Ignore intervals and reasons, reference-Cycle provenance, confirmation state, and selected recording, but shall not copy raw or normalized waveform samples into the project. Reopen shall read the referenced CSV/XLSX sources and shall not silently accept a missing or fingerprint-mismatched source. |
| REQ-002 | The application shall provide Open Project, Save Project, and Save Project As actions and visibly distinguish clean and unsaved/dirty project state. Any persisted-state change shall mark the project dirty. Closing the application, opening another project, or replacing the active session while dirty shall require an application-styled Save, Discard, or Cancel decision. Save shall complete successfully before the requested transition; a cancelled or failed save shall leave the active session open and unchanged. The change set shall not add periodic autosave or recovery files. |
| REQ-003 | Open Project shall resolve each saved source by its recorded path and fingerprint before committing any project state. A missing path shall offer Locate File and Locate Folder actions; folder relinking may match multiple sources only by saved filename plus exact SHA-256 fingerprint and byte size. A moved exact match is accepted and its new path marks the reopened project dirty. A missing source, fingerprint mismatch, ambiguous match, user cancellation, parse error, or unsupported project schema shall block the complete open operation and preserve the prior active session unchanged. Partial project loading and user override of changed source content are prohibited. |
| REQ-004 | Project saving shall be valid before Learning, while Learning/Qualification is running, after a failed run, and after a successful run. If valid completed Learning and Qualification results exist at save time, the project shall persist the selected Target Numeric Type, every retained immutable semantic Profile/kernel, complete per-condition Qualification coverage and denominators, Training and qualified speed/Offset ranges, latency, robustness margins, ranking, and selection state needed to restore Replay & Qualify and Export Profile without rerunning Learning. If no valid completed results exist, those result sections shall be absent and reopening shall restore a Training-ready, not-running state that requires Start Learning. The project shall not persist rejected candidates, candidate-grid intermediates, worker progress, partially completed runs, mutable detector runtime state, or a resumable Training checkpoint. Restored results shall remain usable only while all source fingerprints, mappings, annotations, Sample Rate, target numeric representation, arithmetic contract, and result-schema/algorithm-contract versions match; any upstream edit shall stale and remove restored results under the existing dependency rules. |
| REQ-005 | Every project shall be one deterministic human-readable UTF-8 JSON document with the `.dicsproj` extension. The root shall identify the application format, project schema version, algorithm/result contract versions, and required sections. Saving shall use deterministic key ordering and finite JSON numbers only, shall reject non-finite or unserializable state without replacing the prior file, and shall write by atomic temporary-file replacement. Opening shall reject malformed JSON, duplicate keys, unsupported schema versions, unknown required enum values, missing required fields, invalid numeric ranges, and inconsistent cross-references transactionally. Unknown optional fields from a compatible schema may be ignored while preserved behavior remains explicitly versioned; no ZIP, SQLite, pickle, executable object, or embedded waveform payload shall be accepted as a `.dicsproj` project. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Use external source references with deterministic source fingerprints; do not embed waveform samples in the project file. | Keeps project files small and fast to save while preserving mapping and annotation work. |
| DEC-002 | Use explicit Open/Save/Save As with dirty-state Save/Discard/Cancel protection; do not add autosave or recovery files. | Prevents accidental work loss while keeping persistence behavior deterministic and bounded. |
| DEC-003 | Reopen only after every source resolves to an exact SHA-256/size match; support guided file/folder relinking but prohibit partial load and changed-source override. | Ensures saved sample-index annotations can never be silently applied to different waveform content. |
| DEC-004 | Always save the stable project state available at that moment; include final retained kernels and Qualification results only when a valid completed run exists, and never save a resumable in-progress Training state. | A project may be saved before results exist. This preserves expensive annotation work without pretending that a partial run has produced kernels or Qualification evidence. |
| DEC-005 | Use one deterministic, human-readable UTF-8 JSON file with the custom `.dicsproj` extension and explicit schema/contract versions. | The project stores references and retained results rather than raw waveforms or all candidates, so JSON remains bounded while making diagnostics, migration, and support possible with ordinary text tools. A ZIP or SQLite container would add complexity without a current data-size or query requirement. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | A saved project reopens unchanged external sources and restores all mapping, condition, annotation, template/reference, confirmation, and selected-recording state without requiring re-annotation. Missing or fingerprint-mismatched sources are reported and cannot silently enter Learning. The project artifact contains no waveform sample arrays. | Automated round-trip, artifact inspection, missing-source, changed-source, and Learning-readiness tests. | PASS — `tests/test_project_session.py`; full suite 121 passed. |
| AC-002 | REQ-002 | Every persisted-state edit marks the project dirty; a successful save clears it. Dirty close/open/new transitions expose Save, Discard, and Cancel, and cancel or save failure preserves the current session. No autosave/recovery artifact is created. | Controller state-transition tests plus QML interaction tests. | PASS — `tests/test_project_session.py`, `tests/test_qml_smoke.py`; Spec and Standards reviews PASS. |
| AC-003 | REQ-003 | Exact moved sources can be relinked individually or by folder and reopen successfully; relinking marks the project dirty. Missing, changed, ambiguous, cancelled, malformed, and unsupported projects fail transactionally without changing the active session. | Adapter and controller transaction tests using exact, moved, missing, modified, ambiguous, cancelled, malformed, and future-schema fixtures. | PASS — exact-file, changed-source, missing-source, and ambiguous-folder transactional tests in `tests/test_project_session.py`. |
| AC-004 | REQ-004 | Saving before Learning, during an active run, or after failure produces a valid project with no fabricated kernel/Qualification result and reopens in a Training-ready, not-running state. Saving and reopening a completed project restores every retained kernel and Qualification field byte-for-byte/bit-for-bit as appropriate and allows identical Profile preview/export without rerunning Learning. Rejected candidates and in-progress checkpoints are absent, and any upstream edit invalidates restored results. | Pre-run, active-run, failed-run, and completed-run semantic round trips; artifact inspection; identical-header export; version mismatch; and upstream-staleness tests. | PASS — completed Profile/header round trip and invalid-complete transactional tests in `tests/test_project_session.py`; existing downstream-staleness suite passed. |
| AC-005 | REQ-005 | Save Project and Save Project As produce one deterministic `.dicsproj` UTF-8 JSON file that is parseable by a strict independent JSON parser, contains explicit schema and contract versions, contains no non-finite number or waveform payload, and is byte-identical for unchanged semantic state. Atomic-write failure preserves the previous file. Malformed, duplicate-key, missing-field, unknown-required-enum, invalid-range, cross-reference, incompatible-version, disguised ZIP/SQLite/pickle, and executable-payload fixtures are rejected without mutating the active session. | Golden JSON round trip and determinism tests, independent strict-parser validation, artifact/forbidden-signature scan, atomic-write fault injection, and transactional malformed/schema/security fixture matrix. | PASS — deterministic/duplicate/non-finite/forbidden-payload/strict-grid tests in `tests/test_project_session.py`; architecture gate and both review axes PASS. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| DEC-001 | refines | REQ-001 |
| DEC-002 | refines | REQ-002 |
| DEC-003 | refines | REQ-003 |
| DEC-004 | refines | REQ-004 |
| DEC-005 | refines | REQ-005 |
| REQ-003 | depends_on | REQ-001 |
| REQ-004 | depends_on | REQ-001 |
| REQ-005 | refines | REQ-001 |
| REQ-005 | refines | REQ-002 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |
| AC-003 | depends_on | REQ-003 |
| AC-004 | depends_on | REQ-004 |
| AC-005 | depends_on | REQ-005 |

## Discussion Context

### DISC-001: Project source-data ownership
- **Situation:** Repeating Import & Map and Annotate & Classify is slow, but embedding up to the supported session envelope would duplicate large waveform datasets and make project writes expensive.
- **Question:** Shall project files reference external recordings, embed normalized waveform data, or support both modes?
- **Options and tradeoffs:** External references keep projects small and fast but require the original sources and integrity handling; embedded data is portable and fastest to reopen but can be very large and duplicates source data; dual modes maximize flexibility but add schema, UI, and validation complexity.
- **User answer:** Option 1: use external source references.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-001 refines REQ-001 and AC-001 to require source paths and fingerprints while prohibiting embedded waveform samples.

### DISC-002: Save timing and work-loss protection
- **Situation:** Manual project saving avoids recovery-file complexity, but users can forget to save before closing or replacing a session.
- **Question:** Shall saving be manual only, manual with dirty-close protection, or include autosave and recovery files?
- **Options and tradeoffs:** Manual-only is simplest but permits accidental loss; manual with dirty-state protection prevents unintended loss without recovery lifecycle complexity; autosave offers maximum recovery but adds periodic writes, recovery prompts, cleanup, and failure handling.
- **User answer:** Option 2: manual saving with dirty-state protection.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-002 defines REQ-002 and AC-002 with Open/Save/Save As and Save/Discard/Cancel protection while excluding autosave and recovery files.

### DISC-003: Missing, moved, and changed source handling
- **Situation:** External-reference projects must recover from moved files without ever applying sample-index annotations to changed waveform content.
- **Question:** Shall project open require a complete exact source set, permit partial loading, or allow users to override a fingerprint mismatch?
- **Options and tradeoffs:** Strict complete loading with guided relinking preserves integrity but blocks until every source resolves; partial loading is flexible but creates complex incomplete project states; mismatch override is convenient but can associate annotations with incorrect samples.
- **User answer:** Option 1: strict complete loading with guided relinking and exact fingerprints.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-003 defines REQ-003 and AC-003, including transactional open, exact file/folder relinking, and prohibition of partial or changed-source loading.

### DISC-004: Result availability at save time
- **Situation:** Projects can be saved before or during Learning, when no final kernel or Qualification result exists; a completed run is expensive and should not be repeated.
- **Question:** Shall projects save only pre-Training state, final retained kernels and Qualification results when available, or every candidate and intermediate round?
- **Options and tradeoffs:** Pre-Training-only state is smallest but requires rerunning even completed Learning; conditionally including final retained results permits immediate replay/export after completed runs while still allowing earlier saves; all candidates and partial checkpoints greatly increase size and version coupling and imply unsafe mid-run resume semantics.
- **User answer:** Option 2, clarified that a save made before Training completes has no kernel or Qualification result to store.
- **Explicit rationale:** Kernel and Qualification artifacts do not exist until the run completes.
- **Resulting impact:** DEC-004 and REQ-004 make completed results conditional, preserve stable project inputs at every save stage, and explicitly reopen unfinished runs as Training-ready rather than resumable.

### DISC-005: Project container and readability
- **Situation:** The project format must hold external source references, mappings, annotations, and optional retained results while remaining supportable across schema versions.
- **Question:** Shall `.dicsproj` be a human-readable single JSON file, a ZIP container, or a SQLite database?
- **Options and tradeoffs:** Single JSON is directly inspectable and easiest to diagnose/migrate but uncompressed; ZIP can separate and compress sections but needs container integrity handling; SQLite provides transactions and queries but adds a binary schema and tooling complexity unnecessary for the bounded retained state.
- **User answer:** Option 1: one human-readable UTF-8 JSON `.dicsproj` file.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-005 defines REQ-005 and AC-005 with deterministic strict JSON, explicit versions, atomic writes, and transactional rejection of malformed or incompatible artifacts.

## Out of Scope

- Changing the collision-learning algorithm.
- Embedding raw or normalized waveform samples in the project artifact.
- Autosave and crash-recovery project files.
- Partial project loading or accepting changed source content for existing annotations.
- Persisting rejected candidates or resuming an interrupted Training run.
- ZIP, SQLite, pickle, or executable project containers.

## Open Decisions

None.

## Routing/Gates

- Grilling and spec governance are complete.
- Product implementation requires exact `開始執行` after confirmation.
- Spec review: PASS.

## Revision History

| Revision | Date | Summary |
|---|---|---|
| 1 | 2026-08-25 | Started project/session persistence discussion. |
| 2 | 2026-08-25 | Selected external source references with integrity fingerprints and no embedded waveform samples. |
| 3 | 2026-08-25 | Selected manual Open/Save/Save As with dirty-state transition protection and no autosave. |
| 4 | 2026-08-25 | Selected transactional strict reopen with exact source fingerprints and guided relinking. |
| 5 | 2026-08-25 | Selected persistence of final retained kernels and Qualification results without candidate intermediates or Training resume. |
| 6 | 2026-08-25 | Clarified stage-dependent saving: completed results are conditional, while pre-run and active-run saves contain stable inputs without a resumable checkpoint. |
| 7 | 2026-08-25 | Selected one deterministic human-readable UTF-8 JSON `.dicsproj` file with strict schema validation and atomic replacement. |
| 8 | 2026-08-25 | Added explicit requirement coverage, validation methods, and pending evidence columns required by the canonical specification contract. |
| 9 | 2026-08-25 | Implemented project save/open, strict transactional validation and relinking, optional completed-result restoration, dirty-state UI protection, and recorded passing test/review evidence. |
