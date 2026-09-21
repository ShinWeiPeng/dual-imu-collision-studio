---
spec_version: 1
spec_id: SPEC-0023
revision: 7
status: implemented
change_set: waveform-peak-visibility
---

# Preserve impact peaks in annotation waveforms

## Problem

Annotate & Classify originally reduced every imported Internal and External IMU channel to at most 800 uniformly selected source samples before rendering. The viewport-aware Min/Max implementation preserves narrow impulses, but runtime screenshots show that envelope-mode zoom ratios appear visually discontinuous because the renderer draws only independent vertical bucket strokes. Raw-mode zoom ratios remain continuous, so the display changes abruptly across the mode boundary.

## Solution

Replace fixed whole-recording uniform sampling with a viewport-aware Min/Max projection owned by `data_workspace`. For a requested original-sample viewport and positive bucket count derived from plot width, use deterministic contiguous half-open buckets shared by Internal and External IMU axes. Return each non-empty bucket's horizontal position, finite per-axis extrema, and arithmetic mean. `StudioController` maps this framework-free projection into bounded Qt values; in envelope mode `WaveformItem` draws both one colored vertical minimum-to-maximum stroke per bucket and a continuous same-colored polyline through bucket means. When visible sample count is no greater than plot width, return original samples and render the existing colored polyline. Viewport, dimensions, or selected recording changes regenerate the projection. Preserve the current sample-index x-axis, per-channel visible-range y autoscaling, annotations, persistence, and Learning values. Meet the existing 100 ms p95 interaction requirement.

## User Stories

- As an annotator, I can see narrow positive and negative collision impulses in a full-recording overview.
- As an annotator, zooming reveals additional source detail instead of enlarging the initial reduced series.
- As an annotator, intervals continue to snap to and persist original recording sample indexes.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | The annotation waveform display shall use viewport-aware Min/Max buckets that preserve every non-empty bucket's finite positive and negative extrema so a narrow collision impulse cannot be omitted solely by display reduction. |
| REQ-002 | Changing the shared annotation viewport, plot width, or selected recording shall regenerate visible waveform data from the corresponding original-sample range rather than slice a fixed whole-recording reduction; when visible samples fit the horizontal pixel capacity, the display shall render the original-sample polyline. |
| REQ-003 | Internal and External IMU waveforms shall use identical bucket boundaries and remain synchronized to the same viewport and original sample-index timeline. |
| REQ-004 | Annotation creation, movement, resizing, confirmation, persistence, and Learning truth shall retain original-sample semantics and shall not consume display-reduced indexes. |
| REQ-005 | Projection payload size and rendered primitives shall be bounded by plot width and channel count rather than total recording length; full original waveform arrays shall not cross into QML. |
| REQ-006 | At the SPEC-0001 maximum supported session envelope on its minimum Windows reference system, waveform pan/zoom shall retain the existing p95 input-to-visible-update latency of no more than 100 ms. |
| REQ-007 | In envelope mode, each channel shall draw one thin channel-colored vertical stroke from minimum to maximum at each bucket position and one continuous same-colored polyline through the arithmetic mean of every bucket; in raw mode, it shall draw the existing channel-colored polyline. Neither mode shall use a filled band or chronological Min/Max zigzag. |
| REQ-008 | The projection shall use deterministic clamped viewport-to-sample conversion and contiguous half-open buckets that cover every selected sample exactly once, preserve first and last visible samples, and produce identical output for identical input, viewport, and bucket count. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Use a viewport-aware Min/Max envelope per horizontal display bucket, falling back to the original-sample polyline when visible samples fit the pixel capacity. | The user selected option 1. It prevents positive or negative collision extrema from being skipped, bounds display work by viewport width, and lets zoom reveal original detail. |
| DEC-002 | Retain the existing 100 ms p95 waveform interaction threshold at the maximum supported session envelope and minimum reference system. | SPEC-0001 REQ-012, REQ-039, DEC-093, AC-012, and AC-058 already define this threshold. |
| DEC-003 | Draw every channel's envelope as thin vertical Min-to-Max strokes overlaid with a continuous polyline through bucket arithmetic means, switching to the existing raw polyline when visible samples fit the plot width. | After runtime screenshots showed that stroke-only envelope ratios look discontinuous, the user selected option 1. Means provide a stable trend line without inventing Min/Max chronology, while the strokes retain collision extrema. |
| DEC-004 | Put the deterministic projection in the existing `data_workspace` L1 module, map its framework-free result in `StudioController`, and keep raster drawing in `desktop_adapter.WaveformItem`. | `data_workspace` already owns imported samples and `StudioController` already depends on `WorkspaceService`; this preserves dependency direction, prevents full arrays crossing into QML, and keeps Qt types out of the domain contract. |

## Discussion Context

### DISC-001: Waveform display-reduction strategy

- **Situation:** Fixed 800-point whole-recording uniform sampling can omit a narrow collision impulse, and later zoom only enlarges that lossy representation.
- **Question:** Which peak-preserving display strategy should replace the fixed sampling?
- **Options and tradeoffs:** Viewport-aware Min/Max guarantees bucket extrema with bounded output; all-visible raw rendering can stall on long views; LTTB preserves general shape but does not guarantee every extremum.
- **User answer:** Option 1: viewport-aware Min/Max envelope.
- **Explicit rationale:** No additional rationale was stated; the selection matches the need to make collision points visible.
- **Resulting impact:** DEC-001 closes OD-001 and fixes REQ-001, REQ-002, and REQ-005.

### DISC-002: Existing performance contract

- **Situation:** The initial working spec treated acceptable pan/zoom latency as unresolved.
- **Question:** Does the repository already define a quantitative waveform interaction threshold?
- **Options and tradeoffs:** A new threshold would require user selection; inheriting a valid existing threshold avoids conflicting acceptance contracts.
- **User answer:** Not applicable; this was resolved from repository evidence rather than asked.
- **Explicit rationale:** SPEC-0001 already fixes the maximum dataset envelope, minimum reference system, and 100 ms p95 waveform interaction threshold.
- **Resulting impact:** DEC-002 closes OD-002 and binds REQ-006 and AC-004 to the existing contract.

### DISC-003: Envelope drawing style

- **Situation:** Min/Max calculation alone does not define how extrema appear when several source samples map to one horizontal bucket.
- **Question:** How should each channel's bucket be drawn?
- **Options and tradeoffs:** A vertical Min–Max stroke exposes the exact range without implied chronology; a chronological extrema polyline retains continuity but can create sawtooth artifacts; filled bands become visually muddy when three axes overlap.
- **User answer:** Option 1: vertical Min–Max strokes.
- **Explicit rationale:** No additional rationale was stated; the selected style most directly exposes collision peaks while preserving three-axis readability.
- **Resulting impact:** DEC-003 closes OD-003 and adds REQ-007 and AC-005.

### DISC-004: Continuous envelope trend

- **Situation:** Runtime screenshots after implementation showed envelope-mode zoom ratios as disconnected vertical marks, while raw-mode ratios remained continuous.
- **Question:** Which continuous representation should accompany peak-preserving Min/Max strokes?
- **Options and tradeoffs:** Add a bucket-mean polyline while retaining extrema strokes; connect Min/Max chronologically with sawtooth risk; or switch to raw earlier while leaving wide views discontinuous and increasing payload.
- **User answer:** 1.
- **Explicit rationale:** No additional rationale was stated; the selected mean line preserves a continuous trend while retaining Min/Max collision visibility.
- **Resulting impact:** DEC-003, REQ-007, and AC-005 now require a bucket-mean continuous overlay in envelope mode.

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-008 | Synthetic recordings with one-sample positive and negative impulses placed between the legacy 800 indexes retain both extrema; bucket boundary, endpoint, empty-view, one-sample, and identical-value fixtures are deterministic. | Focused pure projection unit and property tests. | PASS: `tests/test_workspace.py`; exact extrema, arithmetic-mean, coverage, boundary, raw, empty, invalid, determinism, and immutability fixtures. |
| AC-002 | REQ-002, REQ-005 | Zooming, panning, resizing, and recording switching regenerate from the requested original range; output contains no more than one bucket per plot-width unit per channel and never passes full arrays into QML. | Controller/component integration tests with payload-size assertions and spies. | PASS: controller/QML integration tests and maximum-session benchmark; live numeric payload 34,400 equals its width-derived bound. |
| AC-003 | REQ-003, REQ-004 | Both IMU panels use identical viewport/bucket boundaries, while drag-created and edited intervals resolve to the same original sample indexes as before the display change and persisted/Learning snapshots are unchanged. | Offscreen QML interaction regressions and before/after semantic hashes. | PASS: shared-position, annotation interaction, persistence regression, and workspace/Learning SHA-256 tests. |
| AC-004 | REQ-005, REQ-006 | At the maximum supported session envelope on the minimum Windows reference system, repeated pan and zoom achieve p95 input-to-visible-update latency no greater than 100 ms without UI-thread stalls or unbounded display payloads. | SPEC-0001 Windows application benchmark with percentile input-to-frame traces, dataset/build identity, and primitive-count evidence. | PASS: Windows 11 four-core-affinity benchmark, domain 17.236 ms, two-panel raster 67.324 ms, QML input-to-frame 77.739 ms p95; all below 100 ms. |
| AC-005 | REQ-007 | Envelope mode raster output contains channel-colored vertical strokes reaching each known Min/Max value plus a same-colored continuous line through literal bucket arithmetic means, without a filled band or extrema-zigzag; raw mode preserves the existing three colored polylines. | Pure projection mean fixtures and waveform image regression with pixel/geometry assertions across representative zoom ratios. | PASS: literal bucket means plus exact non-constant mean-line midpoint geometry at 2/4/8 buckets; extrema extent, all colors, raw polylines, and single-point rendering pass. |
| AC-006 | REQ-001, REQ-004 | Display projection changes no imported arrays, annotations, saved project content, detector inputs, or Learning results. | Immutability assertions and end-to-end regression hashes. | PASS: projection source immutability and before/after workspace/Learning semantic hashes; full 431-test regression passes. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0001 |
| REQ-001 | depends_on | DEC-001 |
| REQ-002 | depends_on | REQ-001 |
| REQ-002 | depends_on | DEC-001 |
| REQ-003 | depends_on | REQ-002 |
| REQ-004 | refines | SPEC-0001 |
| REQ-005 | depends_on | REQ-002 |
| REQ-005 | depends_on | DEC-004 |
| REQ-006 | refines | SPEC-0001 |
| REQ-006 | depends_on | DEC-002 |
| REQ-007 | depends_on | DEC-003 |
| REQ-008 | depends_on | DEC-001 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |
| AC-003 | depends_on | REQ-003 |
| AC-004 | depends_on | REQ-006 |
| AC-005 | depends_on | REQ-007 |
| AC-006 | depends_on | REQ-004 |

## Out of Scope

- Changing imported waveform values, detector arithmetic, collision deadlines, or Learning data.
- Changing annotation persistence schema, project documents, or the current sample-index x-axis.
- Adding automatic collision detection or automatically creating collision annotations.
- Changing existing per-channel visible-range y autoscaling.
- Redesigning non-annotation waveform surfaces.

## Open Decisions

None.

## Routing/Gates

- Risk: R2 governed change; matched hard triggers are algorithm and architecture/named-type ownership.
- Proposal gates: clarify-improvement-proposals and govern-modular-event-architecture.
- Implementation gates: spec verification, architecture pre-code design tables and planned-manifest PASS, TDD, focused performance/runtime evidence, architecture CLI development gate, and Standards/Spec code review.
- Add a proposed `ALG-0008` owned by `data_workspace`; it cannot become accepted without explicit non-AI approval metadata.
- No product implementation, architecture edit, generated-view edit, or ADR acceptance is authorized by this specification alone.
- Standards review: PASS — no remaining documented-standard violation or smell-baseline finding; the missing boundary mapping found on first review was added and re-verified.
- Spec review: PASS — no uncovered requirement, unverified acceptance criterion, incorrect behavior, or scope creep; the initial AC-005 geometry/evidence gap was corrected and re-reviewed.

## Revision History

| Revision | Change |
|---|---|
| 1 | Started the waveform peak-visibility improvement interview from the confirmed fixed 800-point uniform display sampling. |
| 2 | Selected viewport-aware Min/Max envelope with an original-sample polyline at sufficiently narrow zoom. |
| 3 | Inherited SPEC-0001's 100 ms p95 interaction threshold and opened the drawing-style decision. |
| 4 | Selected vertical Min–Max strokes, completed ownership and deterministic behavior, and closed all decisions. |
| 5 | Reopened after runtime evidence showed stroke-only envelope ratios as discontinuous; selected a bucket-mean continuous polyline over retained Min/Max strokes. |
| 6 | Confirmed the revised arithmetic-mean continuity contract with no open decisions or conflicts. |
| 7 | Implemented the arithmetic-mean projection and continuous envelope overlay; focused 100-test, full 431-test, Windows p95 benchmark, architecture development gate, and independent Standards/Spec reviews pass. |
