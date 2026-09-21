---
spec_version: 1
spec_id: SPEC-0020
revision: 3
status: implemented
change_set: kernel-training-loss-di-icon
---

# Kernel summary Training loss and DI application icon

## Problem

The retained-kernel summary does not show the selected kernel's Training loss, so users cannot inspect the fitting-selection score from Replay & Qualify. The Windows title-bar icon is the generic application icon instead of the blue `DI` brand mark already used in the application header.

## Solution

Expose one explicitly labeled Training loss value for the selected retained kernel and display a blue rounded-square `DI` application icon in the Windows title bar and taskbar, visually matching the existing header mark.

## User Stories

- As an analyst, I can see the Training loss of the retained kernel beside its other summary parameters.
- As a Windows user, I can identify the application by the same DI brand mark in the window chrome and taskbar.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | The retained-kernel parameter summary shall display the selected retained kernel's existing `KernelTrainingEvidence.kernel_loss` value, explicitly labeled `Training loss`, without changing its calculation or selection semantics. The numeric value shall use compact deterministic formatting with sufficient precision to distinguish materially different stored loss values. |
| REQ-002 | The running Windows application's title-bar and taskbar icon shall use a blue rounded-square `DI` mark that visually matches the existing in-app header mark and remains legible at small icon sizes. |
| REQ-003 | Historical or otherwise unavailable Training loss evidence shall display `N/A` rather than a fabricated numeric value. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Apply the DI icon at application level so both title-bar and taskbar surfaces receive the same identity. | The screenshot's generic title-bar icon is OS window chrome, and application-level ownership keeps the small-icon surfaces consistent with the existing header brand. |
| DEC-002 | Define the summary's `Training loss` as the selected retained kernel's existing `KernelTrainingEvidence.kernel_loss`. | The user selected option 1 because the requested value is the loss of the final selected kernel, not a separate cross-validation aggregate. |

## Discussion Context

### DISC-001: Meaning of Training loss
- **Situation:** The existing model exposes both `kernelLoss` from `KernelTrainingEvidence` and cross-validation summary fields (`worstConditionMse` / `pooledMse`). The selected-kernel summary needs one clearly defined value.
- **Question:** Which existing metric should the new `Training loss` field display?
- **Options and tradeoffs:** `Kernel Loss` directly identifies the final selected kernel but does not expose the full cross-validation distribution; worst-condition MSE emphasizes conservative parameter selection but is not the final kernel loss; showing both is complete but consumes more space in the compact summary.
- **User answer:** Option 1: `Kernel Loss`.
- **Explicit rationale:** The user selected the recommended direct representation of the final selected kernel's Training loss; no additional rationale was stated.
- **Resulting impact:** DEC-002 closes OD-001. REQ-001 and AC-001 bind the compact summary to `KernelTrainingEvidence.kernel_loss` and retain a single new value.

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-003 | Selecting retained kernels updates `Training loss` deterministically from the confirmed metric; a kernel without that evidence displays `N/A`. | Controller and QML regression tests. | PASS: controller/QML selection and fallback tests; complete suite 406 passed on 2026-09-02. |
| AC-002 | REQ-002 | The application provides a packaged DI icon, applies it before the main window is shown, and renders a recognizable blue `DI` mark at Windows small-icon sizes. | Resource, startup, and rendered-icon checks. | PASS: 32 px Qt pixmap color/render check, visual preview inspection, and wheel-content verification of `qml/di-icon.svg` on 2026-09-02. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-001 | refines | SPEC-0014 |
| REQ-002 | refines | SPEC-0001 |
| REQ-001 | depends_on | DEC-002 |
| AC-001 | depends_on | REQ-001 |
| AC-002 | depends_on | REQ-002 |

## Out of Scope

- Changing Training optimization, loss computation, kernel selection, qualification, or export semantics.
- Redesigning the full application header or other workflow icons.
- Introducing a new loss calculation when an existing governed metric satisfies the selected meaning.

## Open Decisions

None.

## Routing/Gates

- Governed route: grilling, spec-governance, TDD, implementation, architecture development gate, and code review.
- Product implementation was authorized by the user's exact `開始執行`; TDD, architecture development gate, package-resource verification, and independent Standards/Spec reviews passed on 2026-09-02.
- Standards review: PASS — no hard violations or material judgement-call smells; fixed-point diff unavailable because the workspace has no Git metadata.
- Spec review: PASS — no uncovered requirements or acceptance criteria, incorrect behavior, or scope creep.

## Revision History

| Revision | Change |
|---|---|
| 1 | Started the Training-loss summary and DI application-icon change set from the user's screenshot and request. |
| 2 | Selected the retained kernel's existing `kernel_loss` as the single `Training loss` value and closed OD-001. |
| 3 | Implemented and verified the Training-loss summary, shared DI icon, package resource, architecture manifest/views, and regression coverage. |
