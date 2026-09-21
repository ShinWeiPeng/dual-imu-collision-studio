---
spec_version: 1
spec_id: SPEC-0038
revision: 1
status: confirmed
change_set: annotation-fast-drag-visibility
---

# Annotate Classify fast central drag visibility and interaction

## Problem

An already-selected event disappears from one IMU after a fast central drag. Its original position cannot be clicked to recover it; dragging its counterpart restores both. The current-source offscreen Qt reproduction uses a mapped 100-sample recording, interval [0.2, 0.4], prior selection, and a single 325-pixel move from the center. Affected visual bounds become [[REDACTED: personal data], 0.4], visibility becomes false, and stored bounds remain [0.2, 0.4]. Counterpart dragging by 40 pixels restores both at [0.23, 0.43]. Qt reports visualStart and groupDragDelta binding loops. A signal probe observes cancellation state reset while the start has changed and the end is old. A stepped [100, 325] trajectory succeeds. These pixel values are fixture-specific, not a product speed threshold.

## Solution

Make central-drag preview visibility and geometry use coherent bounds, preventing intermediate mixed old/new endpoints from hiding the active event and reentering preview bindings through cancellation. Preserve page-owned shared gesture state and existing controller contracts. Verify continued interaction after release/cancellation and synchronized views.

## User Stories

- As an annotator, I can move a selected event quickly and continue interacting with it without a recovery drag on the other IMU.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Both IMU views shall maintain coherent preview bounds and visibility during valid central moves, including selected and unselected events and single displacements larger than interval width when the destination remains in view. |
| REQ-002 | Release and cancellation shall clear transient state without stale bounds; subsequent selection and dragging on the affected side shall work without counterpart interaction. |
| REQ-003 | Preserve duration, sample snapping, existing boundary policy, multi-selection offset, synchronized IMU/lane display and one undoable commit per completed move. |
| REQ-004 | Test the actual QML mouse path for visibility, ordered bounds, model/display agreement, continued interaction and relevant binding-loop warnings. |

## Decisions

| ID | Decision |
|---|---|
| DEC-001 | Repair the existing QML preview lifecycle and preserve controller contracts and module ownership. |
| DEC-002 | Use large per-event displacement as deterministic reproduction input; do not introduce a speed limit or artificial delay. |
| DEC-003 | Preserve neighboring resize, lane, viewport and multi-selection behavior and verify affected interactions. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-004 | The selected central-drag reproduction fails before repair and passes afterward in both IMU directions; both preview ranges stay ordered and visible during and after valid large moves. | Qt mouse replay with displacement relative to event width; assert both delegates and collect QML warnings. | Current Internal failure reproduced; permanent regression pending authorization. |
| AC-002 | REQ-002, REQ-004 | After the formerly failing gesture, same-side selection and dragging succeed without counterpart interaction; cancellation clears previews coherently. | Consecutive Qt interactions and explicit cancellation; inspect gesture state and model/display agreement. | Same-position click fails before repair; validation pending. |
| AC-003 | REQ-003 | Duration, snapping, shared movement, boundary behavior and undo remain correct. | Annotation controller and QML regressions including multi-selection, recording switch and boundary moves. | Pending. |
| AC-004 | REQ-003, REQ-004 | Resize, lane, zoom and pan remain usable and required governance checks pass. | Related QML tests, formatter checks and architecture_cli.py development gate with baseline. | Pending. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | depends_on | DEC-001 |
| REQ-004 | depends_on | DEC-002 |

## Out of Scope

New tools, event schema/persistence changes, algorithms, new modules/dependencies and global UI redesign. The reproduction confirms the hidden event cannot be clicked; it does not yet prove every other visible event on the same IMU loses interaction.

## Open Decisions

None.

## Discussion Context

### DISC-001: Central drag and interaction failure
- **Situation:** Fast movement hides an event until counterpart dragging restores it.
- **Question:** Is this central movement or edge resizing, and what happens afterward?
- **Options and tradeoffs:** Central movement preserves duration using shared preview state; resizing follows another path.
- **User answer:** The user specified pressing the center to move the whole interval, and added that same-IMU selection fails after disappearance.
- **Explicit rationale:** The reported failure includes display and interaction.
- **Resulting impact:** REQ-001 through REQ-004 cover coherent preview and continued interaction.

### DISC-002: Computation model confirmation
- **Situation:** Qt replay reproduces invalid display bounds, hiding, failed same-position click and counterpart restoration, with stored bounds unchanged.
- **Question:** Is the demonstrated state flow clear?
- **Options and tradeoffs:** Confirm the measured model or identify a misunderstanding before root-cause testing.
- **User answer:** 清楚
- **Explicit rationale:** None additionally supplied.
- **Resulting impact:** REQ-001, REQ-002 and DEC-001 target the confirmed display lifecycle; the diagnostic understanding gate is complete. This does not supply product execution authorization.

## Routing/Gates

Diagnosis and bounded scope review are decision-complete. Before product edits verify this SPEC and fresh execution admission, apply formatter governance, read the manifest and relevant ownership, prepare required boundary/type/state/dependency/parent tables and validate the planned manifest. Generate affected architecture views only through architecture_cli.py and run its development gate with the zero-entry baseline. Do not accept proposed ADRs. No product modification or successful repair validation is claimed.

## Revision History

- Revision 1: Confirm central-drag reproduction and define bounded repair and regression acceptance.
