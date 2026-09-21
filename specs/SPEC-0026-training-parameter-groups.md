---
spec_version: 1
spec_id: SPEC-0026
revision: 2
status: implemented
change_set: training-parameter-groups
---

# Training parameter groups

## Problem

When FIR and MLP are selected together, their parameters run together visually. FIR optimized settings also appear below the MLP settings, obscuring ownership.

## Solution

Group existing controls into vertically stacked, titled, bordered FIR + Ridge, MLP, and Shared settings panels with internal padding and clear separation. Keep model selection above the panels.

## User Stories

- As a user comparing FIR and MLP, I can immediately identify the model to which each training parameter belongs.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Place all FIR controls and its candidate count in a FIR + Ridge panel, all MLP controls and its candidate count in an MLP panel, and common controls in Shared settings. Model panels follow existing family selection and mode visibility. |
| REQ-002 | Use explicit headings, borders, padding and inter-panel spacing; preserve existing settings, callbacks, locking and vertical scrolling. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Use stacked panels inside Learning Settings. | Fits the existing settings column and makes parameter ownership explicit without narrowing controls. Routine presentation choice within the requested UI correction. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | Mixed, FIR-only, MLP-only and optimized modes show the correct groups and controls; dynamic MLP depths remain contained. | Offscreen Qt interaction and geometry inspection. | PASS: build/inspect_training_groups.py checks widths 1180/1366/1600, depths 1/2/5, single/mixed selections, optimized FIR placement, containment and 16px spacing. Dynamic MLP interaction/locking regression passed. |
| AC-002 | REQ-002 | Groups are visibly separated, controls remain within bounds and enabled/locked behavior is preserved. | Rendered UI inspection and existing QML regression tests. | PASS: 33 QML smoke tests plus one dynamic MLP interaction test; build/spec26-training-groups.png visually inspected with Segoe UI. Existing callbacks remain identical. Architecture development gate exit 0 (existing QML analyzer advisory). |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0025 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |

## Out of Scope

Training algorithms, stored settings, model defaults, new runtime state, types, modules, ports and events.

## Open Decisions

None.

## Routing/Gates

Presentation-only QML change. Existing implementation and durable specifications are present. Preserve the existing compact QML style and indentation without whole-program reformatting. Validate through existing Qt smoke tests, rendered layout inspection and the single architecture CLI development gate.

- Standards review: PASS. Existing QML style and controller callbacks are preserved; no new module, named type or state ownership is introduced.
- Spec review: PASS. Both model panels, shared settings, visibility, containment, spacing and locking meet REQ-001/REQ-002 with the recorded evidence.

### Boundary Design Table

| Boundary | Owner | Change |
|---|---|---|
| TrainPage presentation | desktop_adapter | Reparent existing controls into Qt layout panels. |

### Type Ownership Matrix

No named types added or changed; existing TrainPage and Card inline components remain in Main.qml.

### State Object Ownership Matrix

No state added or changed. Settings remain controller/domain-owned; presentation reads existing bindings.

### Dependencies and parent mappings

Actual and intended edges remain identical: desktop_adapter presents studio_application controller settings and invokes the existing setting callbacks. No sibling-domain edge or architecture description changes.

## Revision History

| Revision | Change |
|---|---|
| 1 | Capture the requested FIR/MLP visual separation and bounded presentation solution. |

| 2 | Implemented grouped panels and verified 34 UI tests, rendered layout, unchanged callbacks, and architecture gate. Standards and Spec review: PASS for this bounded presentation change. |
