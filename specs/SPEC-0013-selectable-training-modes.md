---
spec_version: 1
spec_id: SPEC-0013
revision: 7
status: confirmed
change_set: selectable-training-modes
---

# Selectable Training modes

## Problem

The current desktop learning flow trains a linear FIR model with Ridge-related parameter optimization. An earlier working plan expanded this into FIR, MLP and Extra Trees model-family selection, but that plan was not completed or implemented. The user now wants Learning Settings to select between a user-bounded linear-regression comparison mode and an optimized linear-regression Training mode, with settings fields that change according to the selected mode.

## Solution

Provide exactly two linear-regression Training modes in Learning Settings. The fixed-grid mode fits FIR + Ridge without automatic coarse/fine History/alpha search: the user checks one or more History candidates from 4, 8, 16, 32, 64 and 128 ms and one or more Ridge alpha candidates from 0.000001, 0.0001, 0.01, 1 and 100, then the system evaluates that Cartesian product. Each selected combination enters the existing grouped-CV evaluation and Parameter Loss aggregation; only the minimum rounded Parameter Loss group or ties continue to the existing Validation-allowance fold filtering and surviving-fold Collision Qualification pipeline. The optimized mode retains the same downstream pipeline but automatically generates candidates through its unchanged coarse/fine search. N-fold, Include Training MSE and Validation allowed increase are visible common settings in both modes. Use Robust refit and Loss improvement tolerance remain visible and active only in optimized mode; fixed-grid uses no robust refit or Robust K search and has no fine-search convergence step. New projects and older project files without the new fields default to fixed-grid mode with neither group selected; Start Learning remains unavailable until both groups contain a selection. Project save/open persists and restores the selected Training mode and fixed-grid selections. Training results identify the captured mode, and project results retain immutable run provenance separately from editable next-run settings. Existing Replay CSV, Model TXT and Profile Header formats remain unchanged. MLP, Extra Trees and other nonlinear model families are excluded. This work is governed as a new independent selectable-training-modes SPEC rather than the unfinished multi-family scope.

## User Stories

- As an analyst, I want to choose a user-bounded linear comparison or an optimized linear training process before starting Training so that I can control whether History candidates are explicitly selected or automatically searched.
- As an analyst, I want Learning Settings to show only the parameters relevant to the selected Training mode so that inactive settings are not ambiguous.
- As an analyst, I want to check the History and Ridge alpha values to compare in fixed-grid mode so that the run evaluates only the explicit parameter combinations I selected.

## Requirements

| ID | Requirement |
|---|---|
| REQ-052 | Learning Settings shall expose exactly two mutually exclusive Training modes: fixed-grid FIR + Ridge comparison and optimized linear regression. Both modes remain linear prediction models. The unfinished MLP and Extra Trees plan is removed from this change set. |
| REQ-053 | Selecting fixed-grid FIR + Ridge shall expose History and Ridge alpha multi-selection controls and shall not run an automatic coarse/fine History/alpha search. It shall evaluate the Cartesian product of distinct selected effective Histories and selected alpha values through the existing grouped-CV Parameter Loss selection, fold filtering and Qualification pipeline. Selecting optimized linear regression shall hide fixed-grid controls and use its unchanged automatic coarse/fine candidate generation before that same downstream pipeline. Inactive mode-specific fields shall not affect the captured Training request. |
| REQ-054 | Fixed-grid mode shall present exactly six History checkboxes in ascending order: 4, 8, 16, 32, 64 and 128 ms. The user may select one or more values for comparison; arbitrary History entry and 0 ms are not offered. Preserve the existing sample-rate conversion from requested milliseconds to FIR tap count and deduplicate selected values that map to the same effective tap count while retaining their requested aliases. |
| REQ-055 | Fixed-grid mode shall present exactly five Ridge alpha checkboxes in ascending numeric order: 0.000001, 0.0001, 0.01, 1 and 100. The user may select one or more values for comparison. Each selected alpha shall be crossed with every distinct selected effective History, yielding at most 30 combinations before later detector Qualification dimensions. Arbitrary alpha entry and alpha 0 are not offered. |
| REQ-056 | A new project shall default to fixed-grid mode and initialize all fixed-grid History and Ridge alpha checkboxes unchecked. If fixed-grid mode is active and either group has no selection, Start Learning shall be disabled and the UI shall identify which selection is required; the application shall not silently select a value. Project save shall persist the selected Training mode plus both fixed-grid selection sets, including empty sets, and project open shall restore them. Switching modes shall preserve the inactive selections for later switching. A project file created before this schema extension, with no mode or selection fields, shall also load into fixed-grid mode with both sets empty; this intentional compatibility default changes the previous immediately configurable optimized presentation and requires explicit fixed-grid selection before Training. |
| REQ-057 | N-fold, Include Training MSE and Validation allowed increase shall be visible, editable common settings in both Training modes with their existing domains and defaults because they control shared fold allocation, Parameter/Kernel Loss and fold admission. Optimized linear regression shall additionally show and retain Use Robust refit and Loss improvement tolerance with their existing domains, defaults and behavior. Fixed-grid mode shall hide and ignore those two optimized-only controls, shall use robust_k=0 with no robust refit/Robust K search, and shall perform no fine-search convergence step. Optimized mode shall hide the fixed-grid History and alpha checkbox groups. No existing optimized-mode behavior or control shall be changed or removed. |
| REQ-058 | Each completed Training result shall identify its captured Training mode in the UI. Fixed-grid candidate rows shall continue to expose their effective/requested History and Ridge alpha. Project results shall persist immutable run provenance containing the captured mode and, for fixed-grid runs, the exact requested History and alpha selection sets, separately from editable settings for the next run. Reopening a project shall restore both the completed-run provenance and independent next-run settings without rewriting one from the other. This change shall not alter Replay CSV columns or suggested filenames, Model TXT format, or generated Profile Header format. |
| REQ-059 | In fixed-grid mode, every distinct selected effective History × selected Ridge alpha combination shall enter the existing grouped cross-validation membership plan. For each combination, every fold shall fit using the other folds' Cycle groups and evaluate Training/Validation MSE on common evidence. Existing Parameter Loss aggregation shall rank the selected combinations, and only the minimum decimal-half-up four-place Parameter Loss group plus exact rounded ties shall continue. Existing Validation allowance, `select_fold_kernels` survivor selection and candidate-local numerical-failure handling shall then apply unchanged. Every surviving fold model shall proceed through the existing Collision Qualification path; evaluated combinations removed by Parameter Loss or with no surviving fold shall remain visible with their CV disposition and shall not enter Qualification. Optimized mode retains its existing coarse/fine candidate generation, minimum-loss parameter selection and the same downstream fold filtering/Qualification behavior. |

## Decisions

| ID | Decision | Status |
|---|---|---|
| DEC-058 | Narrow the unfinished selectable-model work to two linear-regression Training modes rather than retaining FIR + Ridge, MLP and Extra Trees together. | Confirmed by the user's selection of option 1. |
| DEC-059 | Define the non-automatic-search mode as a user-selected fixed grid of FIR + Ridge candidates with mode-specific controls. | Confirmed by the annotated answers and follow-up request. |
| DEC-060 | Offer History values 4, 8, 16, 32, 64 and 128 ms as checkboxes so the user selects which fixed-alpha FIR candidates to train and compare. | Confirmed by the user's correction. |
| DEC-061 | Offer Ridge alpha as a checkbox set so the user selects which values to compare, crossing them with the selected Histories. | Confirmed by the user's annotation. |
| DEC-062 | Use the existing complete Ridge alpha set 0.000001, 0.0001, 0.01, 1 and 100 for fixed-grid comparison. | Confirmed by the user's selection of option 1. |
| DEC-063 | Start new projects with no fixed-grid checks, block Training until both groups have selections, and persist the mode plus selections in project files. | Confirmed by the user's selection of option 3 and persistence request. |
| DEC-064 | Retain all five existing settings in optimized mode. | Confirmed by the user's selection of option 1. |
| DEC-065 | Govern Training mode selection as a new independent selectable-training-modes SPEC rather than merging it into the unfinished multi-family plan. | Explicitly requested by the user. |
| DEC-066 | Default both new projects and legacy project files without the new fields to fixed-grid mode with empty History and alpha selections. | Confirmed by the user's selection of option 2. |
| DEC-067 | Expose mode/parameter identity in UI results and saved immutable run provenance while leaving all existing exported artifact formats unchanged. | Confirmed by the user's selection of option 1. |
| DEC-068 | In fixed-grid mode, use grouped CV only as informational evidence and send every valid user-selected History × alpha combination to Collision Qualification without CV pruning; optimized mode retains CV-driven search and pruning. | Confirmed by the user's adoption of the explained flow. |
| DEC-069 | Reuse the existing CV, Loss aggregation, Validation-allowance fold filtering and Qualification pipeline for fixed-grid mode; fixed-grid differs only by user-selected candidate generation, while optimized candidate generation and downstream behavior remain unchanged. | Confirmed by the user's selection of option 1; supersedes DEC-068. |
| DEC-070 | Make N-fold, Include Training MSE and Validation allowed increase common to both modes; keep Use Robust refit and Loss improvement tolerance optimized-only, with fixed-grid robust refit disabled and no convergence step. | Confirmed by the user's selection of option 1. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-055 | REQ-052 | Learning Settings presents exactly the two confirmed linear Training mode choices and does not present MLP or Extra Trees choices. | QML/controller integration tests plus architecture-gate evidence. | Pending |
| AC-056 | REQ-053 | Switching to fixed-grid mode shows and enables History and Ridge alpha selection, hides optimized-only fields, and captures only active selections. Switching to optimized mode hides fixed-grid controls, shows optimized-only fields, and does not allow inactive selections to change the run request. | QML visibility/enabled-state tests, controller request-capture tests and domain dispatch tests. | Pending |
| AC-057 | REQ-054, REQ-053 | Fixed-grid mode displays exactly the six ordered History checkboxes, dispatches only selected History values, and deduplicates equal effective tap counts with aliases preserved. | QML checkbox tests and candidate-plan tests across representative sample rates. | Pending |
| AC-058 | REQ-055, REQ-053 | Fixed-grid mode displays exactly the five confirmed ordered alpha checkboxes and dispatches exactly the Cartesian product of selected distinct effective Histories and selected alphas, with no alpha 0, arbitrary entry or automatic neighborhood expansion. Selecting all six Histories and five alphas plans exactly 30 combinations before later detector Qualification dimensions. | QML checkbox tests, candidate-plan combination tests and Training integration tests. | Pending |
| AC-059 | REQ-056 | A new project shows fixed-grid mode with all eleven checkboxes unchecked. Fixed-grid Start Learning remains disabled with a specific missing-selection prompt until at least one History and alpha are selected. Save/open round-trips the mode and both selection sets exactly, including empty and multiple selections, and mode switching preserves inactive choices without dispatching them. | Controller readiness tests and project-session round-trip/schema tests. | Pending |
| AC-060 | REQ-057 | Optimized mode displays all five existing controls with unchanged validation/default behavior, hides fixed-grid checkbox groups, persists edited optimized values as before, and captures those values in the immutable Training request. | QML visibility tests, existing settings-validation tests and controller request-capture tests. | Pending |
| AC-061 | REQ-056 | Opening a valid pre-extension project that lacks mode and fixed-grid selection fields succeeds, defaults to fixed-grid mode with both groups empty, preserves unrelated project data and qualified results, and blocks a new Training run until explicit selections are made. | Legacy project fixture migration/compatibility tests and controller readiness tests. | Pending |
| AC-062 | REQ-058 | Completed fixed-grid and optimized runs display the correct captured mode. Fixed-grid candidates display their History and alpha. Save/open round-trips immutable captured mode and selected grid independently from subsequently edited next-run settings, including after mode switching. Byte/schema comparison confirms no new Replay CSV columns or filename components, Model TXT fields, or Profile Header fields are introduced. | UI result tests, project-session provenance independence tests and existing export golden/schema tests. | Pending |
| AC-063 | REQ-059 | For a fixture selecting two effective Histories and two alphas, all four combinations enter the same grouped fold membership plan with no coarse/fine neighbor. Their Training/Validation MSE and Parameter Loss match existing aggregation; only the minimum four-place rounded Parameter Loss group plus ties reaches Validation-allowance fold selection, while other evaluated combinations remain visible as CV rejected. Surviving fold models enter the unchanged Qualification path. The existing optimized-mode fixture produces unchanged candidates, survivors and Qualification results. | Candidate-plan, grouped-CV, parameter/fold-selection, Qualification-dispatch and optimized-regression integration tests. | Pending |
| AC-064 | REQ-057 | Both modes display and capture N-fold, Include Training MSE and Validation allowed increase. Fixed-grid hides Use Robust refit and Loss improvement tolerance, captures robust refit false/robust_k 0 and performs no fine-search convergence. Optimized mode displays all five current controls and produces unchanged request, search and result behavior. Switching modes preserves inactive optimized values without allowing them to affect fixed-grid execution. | QML visibility/state tests, immutable request-capture tests and optimized-regression comparison tests. | Pending |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-052 | depends_on | DEC-058 |
| REQ-053 | depends_on | DEC-059 |
| REQ-054 | depends_on | DEC-060 |
| REQ-055 | depends_on | DEC-061 |
| DEC-062 | refines | REQ-055 |
| REQ-056 | depends_on | DEC-063 |
| REQ-057 | depends_on | DEC-064 |
| DEC-065 | refines | DEC-058 |
| DEC-066 | refines | REQ-056 |
| REQ-058 | depends_on | DEC-067 |
| REQ-059 | depends_on | DEC-069 |
| DEC-069 | supersedes | DEC-068 |
| REQ-057 | depends_on | DEC-070 |
| REQ-053 | refines | REQ-052 |
| REQ-054 | refines | REQ-053 |
| REQ-055 | refines | REQ-053 |
| REQ-056 | refines | REQ-053 |
| REQ-057 | refines | REQ-053 |
| REQ-058 | refines | REQ-052 |
| REQ-059 | refines | REQ-053 |
| AC-055 | depends_on | REQ-052 |
| AC-056 | depends_on | REQ-053 |
| AC-057 | depends_on | REQ-054 |
| AC-057 | depends_on | REQ-053 |
| AC-058 | depends_on | REQ-055 |
| AC-058 | depends_on | REQ-053 |
| AC-059 | depends_on | REQ-056 |
| AC-060 | depends_on | REQ-057 |
| AC-061 | depends_on | REQ-056 |
| AC-062 | depends_on | REQ-058 |
| AC-063 | depends_on | REQ-059 |
| AC-064 | depends_on | REQ-057 |

## Out of Scope

- MLP, Extra Trees, Random Forest, Gradient Boosting and other nonlinear model families.
- Arbitrary fixed-mode History entry outside the six confirmed choices.
- Device firmware implementation and new C/C++ model formats.
- Ensemble inference.
- Product, test, architecture or generated-file changes before exact `開始執行` authorization.

## Open Decisions

None

## Routing/Gates

- Authoritative route: grilling, then spec-governance.
- Risk: R2 governed change because this introduces persistent settings and changes the training algorithm path.
- Required before implementation: clarify-improvement-proposals, govern-modular-event-architecture, spec verification, TDD, architecture gate and code review.
- Product execution remains blocked until the specification is decision-complete, materialized and the user says exact `開始執行`.

## Discussion Context

### DISC-059: Narrow model selection to two linear modes

- **Situation:** The existing working specification had grown into a three-family FIR + Ridge, MLP and Extra Trees design, while the new request asks for two linear-regression Training modes.
- **Question:** Should the new two-mode request replace the unfinished multi-family direction or be added alongside it?
- **Options and tradeoffs:** Option 1 replaces the nonlinear plan with two linear modes, reducing implementation and runtime complexity but abandoning the pending nonlinear comparison work. Option 2 retains the nonlinear families and adds a linear baseline, preserving prior decisions but increasing UI, persistence, training and ranking complexity.
- **User answer:** 1
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-058 defines REQ-052 and AC-055 validates the narrowed two-mode scope; earlier unresolved multi-family requirements and decisions are removed from the active snapshot while their history remains in the hash-linked journal.

### DISC-060: Fixed FIR + Ridge fields by selected mode

- **Situation:** The exact meaning of the non-search linear mode and its Learning Settings presentation were unresolved. The current optimized path searches History/Ridge-related candidates with grouped cross-validation.
- **Question:** Which non-search algorithm should be used, and how should its parameters be presented?
- **Options and tradeoffs:** Instantaneous OLS is a pure but potentially unstable baseline; fixed-History FIR + OLS preserves memory but adds a History decision; fixed-parameter FIR + Ridge is numerically safer but remains regularized. Mode-specific fields can keep inactive parameters from appearing applicable.
- **User answer:** Select fixed-parameter FIR + Ridge, with specified values for the bounded History and Ridge alpha; after selecting a mode, provide the fields needed by that mode.
- **Explicit rationale:** The user wants explicit fixed History and Ridge alpha values rather than a fully automatic parameter search in the non-optimized mode.
- **Resulting impact:** DEC-059 defines REQ-053, REQ-053 refines REQ-052, and AC-056 validates conditional field presentation and request capture.

### DISC-061: User-selected History comparison set

- **Situation:** Fixed mode needed an exact History control and domain. A single fixed History would train one candidate, while the user wanted to select several Histories for comparison.
- **Question:** Which History values should be available and how should users choose them?
- **Options and tradeoffs:** A bounded checkbox set supports explicit multi-candidate comparison and predictable workload; free numeric entry is more flexible but complicates validation and comparability; tap-count entry is exact but sampling-rate dependent and less usable.
- **User answer:** Provide 4, 8, 16, 32, 64 and 128 and let the user check which values to compare.
- **Explicit rationale:** The user wants direct control over the bounded History candidates included in comparison.
- **Resulting impact:** DEC-060 defines REQ-054, REQ-054 refines REQ-053, and AC-057 validates the exact checkbox set, dispatch and comparison behavior.

### DISC-062: User-selected Ridge alpha comparison set

- **Situation:** Fixed-grid mode still treated Ridge alpha as one specified value after History became multi-select, which prevented the user from explicitly comparing several regularization strengths.
- **Question:** Should Ridge alpha remain one entered value or become a bounded multi-select comparison set?
- **Options and tradeoffs:** One value bounds workload but prevents direct alpha comparison; a checkbox set makes the requested comparison explicit and predictable but multiplies candidates by the selected History count.
- **User answer:** Also provide Ridge alpha options and let the user check the values to compare.
- **Explicit rationale:** The user wants direct control over which alpha values participate in comparison.
- **Resulting impact:** DEC-061 defines REQ-055, REQ-055 refines REQ-053, and AC-058 validates Cartesian-product dispatch without automatic expansion.

### DISC-063: Complete existing Ridge alpha values

- **Situation:** Ridge alpha multi-selection was confirmed, but its exact bounded values were still open. The existing optimized implementation uses 0.000001, 0.0001, 0.01, 1 and 100.
- **Question:** Should fixed-grid mode reuse the full existing alpha set, use a smaller middle subset, or add alpha 0 as an OLS baseline?
- **Options and tradeoffs:** The full existing set preserves direct comparison and spans weak through strong regularization at up to 30 History/alpha combinations; the smaller set lowers work but removes extremes; adding zero provides OLS but changes numerical-failure handling and is not Ridge.
- **User answer:** 1
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-062 refines REQ-055 and AC-058 validates the exact five values, ordering and maximum fixed-grid combination count.

### DISC-064: Empty defaults and project persistence

- **Situation:** Fixed-grid History and alpha sets needed initial selections and zero-selection behavior. Without persistence, saved projects would lose the user's comparison grid.
- **Question:** Should a new project select all, select one middle combination, or select nothing initially, and should selections be stored with the project?
- **Options and tradeoffs:** All selected gives an immediate complete comparison at maximum workload; one middle combination starts quickly but is not a comparison by default; none forces explicit intent and blocks Training until configured. Persisting the selections preserves reproducibility but extends the project schema.
- **User answer:** 3, and save the selected items together when saving the project.
- **Explicit rationale:** The user wants explicit initial selection and reproducible project settings.
- **Resulting impact:** DEC-063 defines REQ-056 and AC-059 validates empty initialization, readiness blocking, mode-switch preservation and exact project round-trip.

### DISC-065: Preserve optimized controls and create a new SPEC

- **Situation:** Optimized mode could retain all five existing controls, expose only a subset, or become fully automatic. The Training-mode work was also still carried in an old multi-family working topic.
- **Question:** How much optimized-mode control should remain, and should Training-mode selection be governed independently?
- **Options and tradeoffs:** Retaining all controls preserves behavior and compatibility but keeps a denser UI; retaining a subset simplifies the card but removes adjustment capability; fully automatic operation is simplest but removes all current control. A separate SPEC isolates this two-mode change from the abandoned nonlinear-model exploration.
- **User answer:** Select option 1 and open a new SPEC for the Training mode selection discussions.
- **Explicit rationale:** The user wants existing optimized controls preserved and the new change isolated from the prior model-family topic.
- **Resulting impact:** DEC-064 defines REQ-057 and AC-060 validates all five optimized controls; DEC-065 records the independent selectable-training-modes SPEC boundary.

### DISC-066: Fixed-grid default for new and legacy projects

- **Situation:** The new mode field needs a default for new projects and for older project files that do not contain the field. Defaulting to optimized preserves prior behavior, while defaulting to fixed-grid makes the new explicit-comparison workflow primary but blocks Training until selections are made.
- **Question:** Should new and legacy projects default to optimized mode, both default to fixed-grid mode, or use different defaults?
- **Options and tradeoffs:** Optimized for both maximizes behavioral compatibility; fixed-grid for both applies one rule and foregrounds explicit selection but changes old-project behavior; different defaults preserve legacy behavior but create context-dependent initialization.
- **User answer:** 2
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-066 refines REQ-056, AC-059 validates the new-project default and AC-061 validates the intentional legacy-project compatibility behavior.

### DISC-067: UI and project provenance without export changes

- **Situation:** Training mode and selected parameters could be shown only in the app/project or added to one or all exported artifact formats. Export changes would improve standalone traceability but create compatibility costs outside the requested settings feature.
- **Question:** Where should captured mode, selected Histories and alpha values be recorded?
- **Options and tradeoffs:** UI plus immutable project provenance preserves run traceability without altering exports; adding Model TXT/Profile metadata changes those consumers; changing every artifact also affects Replay CSV schemas and scripts.
- **User answer:** 1
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-067 defines REQ-058 and AC-062 validates UI identity, independent project provenance and unchanged exported artifact contracts.

### DISC-068: Fixed-grid CV is informational and does not prune

- **Situation:** The confirmed fixed-grid contract dispatched every selected combination but did not explicitly state whether grouped CV could prune combinations before Collision Qualification.
- **Question:** Should fixed-grid CV only report evidence for every selected combination, or automatically retain only lower-Loss combinations as optimized mode does?
- **Options and tradeoffs:** Informational-only CV preserves the user's explicit comparison set at higher Qualification workload; CV pruning reduces work but makes fixed-grid mode perform automatic optimization and hides selected combinations.
- **User answer:** Adopt informational-only CV for fixed-grid mode and retain CV search/pruning for optimized mode.
- **Explicit rationale:** The user adopted the explained flow in which every selected combination reaches Collision Qualification for comparison.
- **Resulting impact:** DEC-068 defines REQ-059 and AC-063 validates common grouped-CV evidence, absence of pruning and Qualification dispatch for every valid selected combination.

### DISC-069: Reuse the existing CV and Qualification pipeline

- **Situation:** Informational-only fixed-grid CV would require a separate final-fit and Qualification branch, while the user's intent was to avoid changing the optimized flow and share its established validation behavior.
- **Question:** Should fixed-grid mode reuse the existing CV pruning pipeline, keep informational-only CV with a separate final fit, or skip CV entirely?
- **Options and tradeoffs:** Full reuse changes only candidate generation and preserves comparability but may reject selected combinations; informational-only CV keeps every valid combination but adds a distinct final-fit branch; no CV is simplest but removes comparable validation evidence.
- **User answer:** Select option 1.
- **Explicit rationale:** The user expected the optimized flow to remain unchanged and asked whether sharing the flow implies sharing CV淘汰 behavior.
- **Resulting impact:** DEC-069 supersedes DEC-068 and defines the revised REQ-059/AC-063 shared-pipeline contract; OD-018 is resolved because surviving fold models follow the existing Qualification behavior.

### DISC-070: Common and optimized-only CV settings

- **Situation:** Reusing the CV pipeline makes N-fold, Loss composition and Validation allowance relevant to fixed-grid mode, while robust refit expands a Robust K dimension and convergence tolerance only controls optimized fine search.
- **Question:** Which current settings should remain visible in fixed-grid mode?
- **Options and tradeoffs:** Sharing N-fold, Include Training MSE and Validation allowed increase exposes every rule that affects shared CV selection while keeping irrelevant search controls hidden; sharing all five exposes controls with misleading or grid-expanding effects; hiding all CV settings uses invisible fixed defaults.
- **User answer:** Select option 1.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-070 defines REQ-057 and AC-064 validates three common controls, two optimized-only controls, fixed-grid robust_k=0 and unchanged optimized behavior.

## Revision History

| Revision | Date | Change |
|---|---|---|
| 1 | 2026-08-31 | Created the independent selectable-training-modes working SPEC from the confirmed two-mode discussion. |
| 2 | 2026-08-31 | Defaulted new and pre-extension projects to fixed-grid mode with empty selections. |
| 3 | 2026-08-31 | Finalized UI/project provenance and preserved existing export formats. |
| 4 | 2026-08-31 | Normalized acceptance and relationship fields for the canonical SPEC contract without behavioral changes. |
| 5 | 2026-08-31 | Reopened and defined informational-only fixed-grid CV without candidate pruning. |
| 6 | 2026-08-31 | Superseded informational-only CV with reuse of the existing CV/filtering/Qualification pipeline. |
| 7 | 2026-08-31 | Defined shared CV settings and optimized-only search controls. |
