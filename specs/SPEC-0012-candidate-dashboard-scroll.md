---
spec_version: 1
spec_id: SPEC-0012
revision: 22
status: implemented
change_set: candidate-dashboard-scroll
---

# Training and Qualification Retained Winner Drilldown

## Problem

Long Candidate Dashboard messages overflow their card. The area below the Training status currently renders a selected-fold-kernel table, while compact execution summaries and failure text appear in the smaller message region above it; when no selected kernels exist, the large lower area appears blank instead of serving as the requested execution-log display. On Replay & Qualify, the page also needs one ordered drilldown from retained-kernel selection to kernel specifications and then every recording result.

## Solution

Contain every affected panel. Keep Candidate Dashboard controls fixed and dedicate the large region below Training status to a bounded execution-log view; the disposition of the selected-fold-kernel table currently occupying that region remains open. Make Retained Round Winners the single analytical-kernel selection entry point by replacing its horizontal card strip with a Kernel combo box containing every retained kernel, including diagnostic-only kernels. Below that selector, show the selected kernel specifications and then every supplied recording's Qualification result in order. Remove the redundant Supplied Conditions aggregate table and the former Analytical Replay region. Export Model TXT belongs to the selected-kernel specification region, and each recording row owns its Export Replay CSV action.

## User Stories

- As a user monitoring a long learning run, I can reach every Candidate Dashboard message without it drawing outside the dashboard card.
- As a user reading training messages, I can keep the run controls, progress, timing, and candidate results visible while scrolling the messages.
- As a user monitoring Training, I can read the execution log in the large lower Dashboard region instead of seeing an empty selected-kernel table.
- As a user comparing retained winners, I can choose any retained kernel from one explicit selector and inspect its details below.
- As a user exporting analytical evidence, I can choose any retained kernel and see its selected parameters before exporting Replay CSV or Model TXT for that kernel.
- As a user investigating a retained kernel, I can review every supplied recording result under the selected kernel without switching selectors.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | Candidate Dashboard content shall remain visually contained within the dashboard card at supported window sizes. |
| REQ-002 | The growing Candidate Dashboard training status/execution-message region shall have a bounded height and provide vertical scrolling when its content exceeds the available message-region height. |
| REQ-003 | Existing Candidate Dashboard learning actions, progress, timing, summaries, execution state, failure reporting, and application status bar shall retain their behavior; the selected-fold-kernel table is intentionally removed. |
| REQ-004 | The dashboard header, learning action, progress, and timing shall remain outside the execution-log scroll area and remain visible subject to the existing supported-window-size contract; no selected-fold-kernel table or empty placeholder shall remain. |
| REQ-005 | Retained Round Winners shall provide one Kernel combo box containing every visible retained kernel, including qualified and diagnostic-only kernels, and shall not render the former horizontal retained-kernel card strip. |
| REQ-006 | Replay & Qualify shall not display the former Supplied Conditions aggregate table. |
| REQ-007 | The former Supplied Conditions header, rows, synchronized scrolling, and containing card shall be removed without leaving an empty placeholder region. |
| REQ-008 | The Retained Round Winners Kernel combo box shall be the single analytical-kernel selector; the selected kernel shall drive the kernel specification summary, per-recording results, row-bound Replay CSV actions, and Model TXT, and the former Analytical Replay region shall be completely removed without an empty placeholder. |
| REQ-009 | Analytical-kernel selection shall remain distinct from multi-selection for Profile export; only qualified/exportable kernels may be selected for Profile header export, and diagnostic-only kernels shall never become Profile-exportable through analytical selection. |
| REQ-010 | Replay & Qualify shall remove the top summary card that currently displays Qualified Speed Range, Training Speed Range, Kernel Depth, Worst Collision Latency, and Partial Results. |
| REQ-011 | A parameter summary for the currently selected analytical kernel shall appear below the Kernel selector, update atomically on selection changes, and display exactly Kernel ID / Round, Training / Qualified range, Offsets, History / taps, Ridge alpha, Scale method / Robust K, and Threshold; its action area shall contain Export Model TXT for that selected kernel. |
| REQ-012 | Below the selected-kernel specification summary, Replay & Qualify shall display one result row for every supplied recording in deterministic supplied-recording order with exactly these columns in order: Recording, Robot Speed, Collision Offset, Normal / Pick / Put false, Collision detected / total, Worst latency, Pass / Fail, and an Export Replay CSV action bound directly to that row's selected-kernel/recording pair. Values and Pass / Fail shall use the same Qualification evidence and rules as the selected kernel. |
| REQ-013 | Candidate Dashboard shall completely remove the selected-fold-kernel table and use its former large bounded region below Training progress and timing as a chronological structured Learning execution log with vertical scrolling when content exceeds the viewport. Entries shall expose event time, Stage, Round, active Speed / Offset scope when applicable, progress message, evaluated and pending job counts when applicable, round elapsed time when applicable, fallback or skip reason when applicable, and terminal completion, cancellation, or failure reason. Loss-summary entries shall be emitted when Coarse/Fine search obtains a new raw best Parameter Loss and shall include the parameter point's History/taps, Ridge alpha, Robust K mode/value, and relative improvement from the previous best when one exists; each round shall emit its final decimal-half-up four-place best Parameter Loss and every admitted fold kernel's Kernel Loss plus per-condition Validation-allowance Pass/Fail outcome. Discarded non-best parameter candidates and exhaustive per-condition MSE rows shall not produce UI log entries. Peak RSS, launch RAM, raw process-diagnostics, and unrelated Qt/application messages shall not appear in this UI log. |
| REQ-014 | The execution log shall contain exactly one Learning run: completion, cancellation, or failure shall preserve the complete terminal log for inspection, and only a subsequent successful Start Learning transition into a new run shall atomically clear the prior entries before appending the new run's first entry. Merely viewing pages, editing idle settings, or a rejected Start Learning attempt shall not clear the log. |
| REQ-015 | The execution log shall Smart follow: while the viewport is at its bottom, each new entry shall keep the newest entry visible; once the user scrolls upward beyond the bottom tolerance, new entries shall not change the viewport position and a visible `Latest (N)` control shall report the count of unseen entries. Activating that control shall scroll to the newest entry, clear the unseen count, and resume follow mode. Returning to the bottom by ordinary scrolling shall also clear the count and resume follow mode. |
| REQ-016 | The in-app structured execution log shall retain at most 10,000 event entries for one Learning run. When a new event exceeds that bound, the oldest event shall be discarded, the newest event shall be retained, and a persistent non-event marker at the top shall display `Earlier log entries discarded: N` with the cumulative discarded-event count. The marker shall not consume one of the 10,000 event slots and shall reset with the log at the next accepted Start Learning. |
| REQ-017 | The structured execution log shall be App-session-only state and shall never be serialized into `.dicsproj` or any project result. Save Project shall leave the in-memory log unchanged. Application restart, successful New Project, and successful Open Project replacement shall begin with an empty execution log; a rejected or failed New/Open operation shall preserve the current project and its log. No new execution-log export artifact is included. |

## Decisions

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Implement this correction as a new, narrowly scoped UI specification rather than modifying SPEC-0001 or SPEC-0011. | The user selected option 3 so the containment fix has an independent acceptance boundary. |
| DEC-002 | Scroll only the growing training status/execution-message region. | The user selected option 2 so monitoring controls, progress, timing, and candidate results remain fixed while long messages stay reachable. |
| DEC-003 | Replace the Retained Round Winners horizontal card strip with one retained-kernel combo box while keeping Supplied Conditions as a synchronized two-axis table with shared column widths. | The user wants selection-first drilldown rather than horizontally browsing winner cards. |
| DEC-004 | Put the sole analytical-kernel selector in Retained Round Winners and order its dependent content as kernel specifications followed by per-recording results. | One selector prevents divergent selection state and matches the requested top-to-bottom review flow. |
| DEC-005 | Remove the top qualification-summary card and reduce Supplied Conditions to five requested evidence columns. | The user explicitly removed that pane and named the condition evidence that remains useful. |
| DEC-006 | Keep the selected-kernel summary to the exact requested identity, range, offset, fit, scale, and threshold fields without Score, Confirmation, CV, error, or coefficient details. | The user supplied the exact field list instead of choosing a broader preset. |
| DEC-007 | Use the standard per-recording result table: Recording, Robot Speed, Collision Offset, Normal / Pick / Put false, Collision detected / total, Worst latency, and Pass / Fail. | It exposes both false-trigger and missed/late-collision causes while remaining substantially narrower than full detector diagnostics. |
| DEC-008 | Remove the Supplied Conditions aggregate table from Replay & Qualify. | The per-recording table contains the selected outcome fields and the user selected a direct kernel-specification-to-recording-results flow without duplicate Speed x Offset evidence. This supersedes the Supplied Conditions portions of DEC-003 and DEC-005. |
| DEC-009 | Move Export Model TXT into the selected-kernel specification region and put Export Replay CSV at the end of every recording-result row. | Model TXT is a kernel artifact while Replay CSV is a kernel-plus-recording artifact, so each action is colocated with the identity it exports and no second recording lookup is required. |
| DEC-010 | Completely remove the former Analytical Replay region after relocating its selectors, specification summary, and export actions. | The remaining region would contain only explanatory CSV text and would not provide an analytical view or interaction. |
| DEC-011 | Completely remove the Training selected-fold-kernel table and dedicate its full lower Dashboard region to the execution log. | The user identifies that region as the execution-log area, and final retained-kernel inspection remains available in Retained Round Winners without an empty or duplicate Training table. |
| DEC-012 | Display a structured Learning-event log rather than only compact summaries or raw process diagnostics. | Structured events expose actionable Training progress, scope, resource, fallback, and terminal evidence without unrelated application noise. |
| DEC-013 | Retain one complete current/most-recent Learning run and clear it only when a new run successfully starts. | This keeps terminal evidence available for diagnosis while preventing entries from different runs from being mixed. |
| DEC-014 | Use Smart follow with an unseen-entry counter instead of forced or manual-only scrolling. | It keeps live monitoring current without pulling the viewport away while the user reads older entries. |
| DEC-015 | Bound the in-app execution log to 10,000 newest events and expose cumulative oldest-event truncation through a visible marker. | It provides generous per-run history with bounded memory and makes every overflow explicit. |
| DEC-016 | Keep the structured execution log session-only and outside project persistence and artifact export. | It avoids changing `.dicsproj` schema or project size while existing process diagnostics remain the durable troubleshooting source. |
| DEC-017 | Remove Peak RSS and launch RAM from the visible Candidate Dashboard log and prioritize Learning Loss evidence. | The user needs optimization and selection evidence rather than runtime memory-capacity telemetry; resource evidence may remain internal without occupying the UI log. |
| DEC-018 | Display Loss search summaries rather than final-only or exhaustive candidate/fold Loss events. | New-best, final-selection, Kernel Loss, and Validation-gate events reveal how optimization converges without flooding the bounded log with discarded candidates. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | With enough training messages to exceed the available message-region height, no message paints outside the Candidate Dashboard card and all message content is reachable by vertical scrolling. | QML smoke test plus rendered UI inspection. | PASS — `test_train_page_keeps_controls_fixed_and_execution_log_contained`; rendered `train-dashboard-layout.png` inspected. |
| AC-002 | REQ-003, REQ-004 | Dashboard header, learning action, progress, timing, and application status bar remain present and outside the execution-log scroll area; the selected-fold-kernel table, its headers, empty-state text, and placeholder region are absent. | QML smoke tests plus rendered UI inspection. | PASS — QML structure and containment smoke tests; rendered Training page inspected. |
| AC-003 | REQ-005 | With qualified and diagnostic-only fixtures, Retained Round Winners exposes every visible retained kernel through one combo box, renders no horizontal winner-card strip, and remains contained at the supported minimum width. | QML interaction test plus rendered UI inspection. | PASS — retained-kernel selector QML interaction fixture and rendered Qualification page inspection. |
| AC-004 | REQ-006, REQ-007 | Replay & Qualify contains no Supplied Conditions heading, aggregate header, aggregate rows, synchronized scrollers, card, or empty placeholder, while the kernel specification and per-recording result regions remain present. | QML interaction test plus rendered UI inspection. | PASS — QML structural absence assertions and rendered `qualification-layout.png` inspection. |
| AC-005 | REQ-008, REQ-009 | Selecting each retained kernel from the Retained Round Winners combo box, including diagnostic-only fixtures, atomically updates its specification, per-recording results, row-bound Replay CSV actions, and Model TXT; no Analytical Replay region or empty placeholder exists and Profile export remains rejected for non-exportable kernels. | Controller tests and QML interaction tests plus rendered UI inspection. | PASS — controller selection/export tests and retained-kernel QML interaction test. |
| AC-006 | REQ-010, REQ-011 | The old top qualification-summary card is absent, and changing the Retained Round Winners selection updates exactly Kernel ID / Round, Training / Qualified range, Offsets, History / taps, Ridge alpha, Scale method / Robust K, and Threshold before the recording-result region without stale values or unrequested parameter groups; Export Model TXT exports that selected kernel. | Controller and QML interaction tests plus rendered UI inspection. | PASS — exact parameter-map/controller export assertions plus QML interaction and rendered inspection. |
| AC-007 | REQ-012 | A multi-recording fixture produces exactly one visible row per supplied recording in supplied-recording order with the exact columns Recording, Robot Speed, Collision Offset, Normal / Pick / Put false, Collision detected / total, Worst latency, Pass / Fail, and Export Replay CSV; every value agrees with the selected kernel's Qualification evidence, each export uses exactly its row's recording and current kernel, and changing kernels replaces all rows without mixed or stale evidence. | Controller tests and QML interaction tests plus rendered UI inspection. | PASS — `test_selected_kernel_exposes_exact_ordered_recording_qualification_rows`, Qualification service evidence tests, QML row action test, and completed-project restore regression. |
| AC-008 | REQ-013 | During a multi-round fixture with improving and non-improving candidates, the log emits only new-best Coarse/Fine Parameter Loss entries with matching History/taps, Ridge alpha, Robust K, and relative improvement, one final four-place Parameter Loss entry per completed search round, and an entry for each admitted fold's Kernel Loss and Validation Pass/Fail; discarded non-best candidates and exhaustive condition MSE rows are absent. Stage, scope, progress/job counts, elapsed time, fallback/skip, and terminal entries remain ordered and visible, while Peak RSS, launch RAM, raw process/Qt noise, and the candidate-table surface are absent. | Domain progress-contract tests, controller tests, QML interaction tests, and rendered UI inspection. | PASS — typed new-best/final/admitted-kernel tests, explicit speed/offset/exhaustion fallback-reason tests, controller log projection tests, and rendered Training inspection. |
| AC-009 | REQ-014 | Completion, cancellation, and failure preserve the full run log; page navigation, idle setting edits, and rejected starts do not clear it; a successfully accepted new Start Learning clears all prior entries before the first new-run entry, and no displayed log mixes two runs. | Controller tests and QML interaction tests. | PASS — accepted/rejected Start and terminal lifecycle controller/QML regressions. |
| AC-010 | REQ-015 | Under continuous event production, a bottom-positioned viewport follows each newest entry; scrolling upward freezes the viewport and increments `Latest (N)` without losing entries; clicking the control or manually returning to bottom clears the counter and resumes following. | QML interaction tests plus rendered UI inspection. | PASS — live QML `contentY` smart-follow, unseen-count, and Latest-button interaction test. |
| AC-011 | REQ-016 | After 10,005 generated events, exactly the newest 10,000 event entries remain in order, the top marker reads `Earlier log entries discarded: 5`, the newest terminal event is retained, memory does not grow with further overflow beyond the bounded collection, and the marker resets on the next accepted run. | Controller tests and QML interaction tests. | PASS — 10,005-entry bounded-log and reset regression plus QML marker projection. |
| AC-012 | REQ-017 | Save Project writes no execution-log field and preserves the in-memory log; application restart and successful New/Open replacement expose an empty log; rejected or failed New/Open preserves the current log; legacy and current `.dicsproj` schema validation remains unchanged and no execution-log export action exists. | Project-session and controller tests plus schema regression tests. | PASS — Save/Open transactional session-log tests, accepted/rejected New Project test, restart construction, and unchanged project-schema suite. |

## Relationships

| Source | Relation | Target |
|---|---|---|
| REQ-002 | depends_on | REQ-001 |
| REQ-004 | depends_on | DEC-002 |
| REQ-007 | depends_on | REQ-006 |
| REQ-009 | depends_on | REQ-008 |
| REQ-011 | depends_on | REQ-008 |
| REQ-011 | depends_on | DEC-006 |
| REQ-012 | depends_on | REQ-008 |
| REQ-012 | depends_on | DEC-007 |
| REQ-012 | depends_on | DEC-009 |
| AC-001 | depends_on | REQ-001 |
| AC-001 | depends_on | REQ-002 |
| AC-002 | depends_on | REQ-003 |
| AC-002 | depends_on | REQ-004 |
| AC-003 | depends_on | REQ-005 |
| AC-004 | depends_on | REQ-006 |
| AC-004 | depends_on | REQ-007 |
| AC-005 | depends_on | REQ-008 |
| AC-005 | depends_on | REQ-009 |
| AC-006 | depends_on | REQ-010 |
| AC-006 | depends_on | REQ-011 |
| AC-007 | depends_on | REQ-012 |
| AC-008 | depends_on | REQ-013 |
| AC-009 | depends_on | REQ-014 |
| AC-010 | depends_on | REQ-015 |
| AC-011 | depends_on | REQ-016 |
| AC-012 | depends_on | REQ-017 |

## Discussion Context

### DISC-001: Specification ownership
- **Situation:** Candidate Dashboard belongs to broader UI and learning-result areas while several confirmed specifications exist.
- **Question:** Should this correction refine an existing specification or use a new narrowly scoped specification?
- **Options and tradeoffs:** Existing specifications centralize related behavior but broaden their contracts; a new specification adds one document with a clear independent boundary.
- **User answer:** Option 3: create a new small UI correction specification.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-001 and REQ-001 through REQ-003 define an independent change set.

### DISC-002: Candidate Dashboard scroll scope
- **Situation:** The dashboard combines fixed controls, growing messages, and the candidate table.
- **Question:** Which region should scroll when vertical space is insufficient?
- **Options and tradeoffs:** Scrolling the body can hide controls; scrolling only messages keeps controls fixed; scrolling summaries and results together creates a larger nested experience.
- **User answer:** Option 2: scroll only the growing message region.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-002, REQ-002, REQ-004, AC-001, and AC-002 fix the message-only scroll boundary.

### DISC-003: Replay panel containment and table alignment
- **Situation:** Winner cards lack a visible horizontal scrollbar, and independently distributed condition header/row widths create misalignment and clipped columns.
- **Question:** Should these Replay defects be included in this containment change?
- **Options and tradeoffs:** Leaving them separate preserves narrow scope but leaves defects unresolved; including them expands QML work but creates one coherent containment correction.
- **User answer:** Include Winners scrolling, Supplied Conditions scrolling, and aligned Supplied Conditions items and content.
- **Explicit rationale:** Both panels exceed their windows and condition items and content do not align.
- **Resulting impact:** DEC-003, REQ-005 through REQ-007, AC-003, and AC-004 extend the containment boundary.

### DISC-004: Analytical-kernel selection affordance
- **Situation:** Profile checkboxes exclude diagnostic kernels, while the clipped Inspect action does not communicate persistent selection next to analytical exports.
- **Question:** Where should users explicitly select the retained kernel used for Replay CSV and Model TXT?
- **Options and tradeoffs:** A Kernel combo box places selection beside outputs; Analyze radio controls add a second selector on cards; clickable cards are less explicit.
- **User answer:** Option 1: directly add a Kernel combo box and show the selected kernel's parameters below it.
- **Explicit rationale:** The user wants direct kernel selection associated with output results and parameter display.
- **Resulting impact:** DEC-004, REQ-008, REQ-009, REQ-011, AC-005, and AC-006 define the analytical selection flow.

### DISC-005: Selected-kernel parameter summary
- **Situation:** Available model evidence ranges from compact operating parameters to large coefficient arrays and fold diagnostics.
- **Question:** Which fields should the in-app selected-kernel summary display?
- **Options and tradeoffs:** Compact presets balance readability and comparison; full diagnostics add large coefficient/provenance content; a caller-specified subset provides exact information density.
- **User answer:** Display Kernel ID / Round, Training / Qualified range, Offsets, History / taps, Ridge alpha, Scale method / Robust K, and Threshold.
- **Explicit rationale:** The user provided the exact required list and omitted Score, Confirmation, CV Loss, error statistics, and coefficient arrays.
- **Resulting impact:** DEC-006, REQ-011, and AC-006 close the parameter-summary scope.

### DISC-006: Qualification summary and condition columns
- **Situation:** The top card repeats range/depth/latency summary while Supplied Conditions includes more columns than requested.
- **Question:** Which summary pane and condition columns should remain?
- **Options and tradeoffs:** Keeping all preserves current evidence but consumes width; removing the top card and reducing columns frees space but removes aggregate labels from that location.
- **User answer:** Remove the pictured top summary pane. Keep only Robot Speed, Collision Offset, Normal / Pick / Put false, Collision detected, and Collision latency.
- **Explicit rationale:** No additional rationale was stated.
- **Resulting impact:** DEC-005, REQ-006, REQ-010, AC-004, and AC-006 remove the unwanted presentation.

### DISC-007: Per-recording result content
- **Situation:** The user replaces the retained-winner card strip and duplicate Analytical Replay selector with one Retained Round Winners dropdown, followed by the selected kernel specifications and every recording result. Existing Replay selection identifies recordings, but the requested result row can range from a compact outcome summary to full detector diagnostics.
- **Question:** Which exact fields shall each recording-result row display?
- **Options and tradeoffs:** A compact outcome table is easier to scan; detector diagnostics provide more evidence but require substantially more width; a recording selector with one detailed pane does not satisfy the stated all-recordings-at-once ordering.
- **User answer:** Option 1, the standard result table: Recording, Robot Speed, Collision Offset, Normal / Pick / Put false, Collision detected / total, Worst latency, and Pass / Fail.
- **Explicit rationale:** No additional rationale was stated; the selected option was recommended because it exposes both false-trigger and collision-detection outcomes without the width of full detector diagnostics.
- **Resulting impact:** DEC-007, REQ-012, and AC-007 fix the exact per-recording columns and require the displayed outcome to agree with existing Qualification evidence.

### DISC-008: Aggregate Supplied Conditions coexistence
- **Situation:** The requested drilldown now shows kernel specifications followed by every recording result. The current page also shows a Supplied Conditions aggregate table above Analytical Replay, which summarizes multiple recordings by Speed x Offset and can either remain as an additional overview or be removed as redundant.
- **Question:** Shall Supplied Conditions remain between the kernel specification and per-recording results, move after the recording table, or be removed from Replay & Qualify?
- **Options and tradeoffs:** Keeping it before recordings preserves the aggregate-to-detail hierarchy but interrupts the requested specifications-then-recordings order; moving it after recordings preserves that order and retains aggregate evidence; removing it makes the page simplest but loses the fast Speed x Offset overview.
- **User answer:** Option 1: remove Supplied Conditions.
- **Explicit rationale:** No additional rationale was stated; the selected option was recommended because it preserves the requested kernel-specification-to-recording-results order and avoids duplicated outcome evidence.
- **Resulting impact:** DEC-008 supersedes the former table behavior by revising REQ-006, REQ-007, and AC-004 to require complete removal without a placeholder. Replay & Qualify now proceeds from the kernel selector to specifications, per-recording results, and Analytical Replay.

### DISC-009: Recording table interaction with Analytical Replay
- **Situation:** Every recording will be visible in the new result table, while Analytical Replay currently has its own recording combo box for selecting the recording used by Replay CSV. The result table can be read-only, can become the sole recording selector, or can synchronize with the existing selector.
- **Question:** How shall a recording-result row interact with the recording selected for Analytical Replay?
- **Options and tradeoffs:** Read-only rows preserve the current Replay selector but require a second lookup; replacing the Replay selector with table selection creates one entry point but makes selection less explicit in the export toolbar; synchronized clickable rows plus the Replay selector provide both scanability and explicit state at the cost of two coordinated controls.
- **User answer:** Put Export Replay CSV at the end of every recording result.
- **Explicit rationale:** The export belongs to the individual recording result rather than a separate recording selector.
- **Resulting impact:** DEC-009 and REQ-012 bind each Replay CSV action directly to its row's selected-kernel/recording pair, so Replay export does not require a persistent row selection or a second recording lookup.

### DISC-010: Analytical Replay region after action relocation
- **Situation:** The existing Analytical Replay region renders no waveform or per-sample diagnostics. It contains the duplicate kernel selector, recording selector, Export Replay CSV, Export Model TXT, the kernel parameter summary, and explanatory text about the CSV contents. The new contract moves the sole kernel selector and specification summary above, Export Model TXT into the specification region, and Export Replay CSV into each recording row, leaving only explanatory text without a distinct analytical view.
- **Question:** Shall the now-empty Analytical Replay region be removed, retained as an informational CSV-content card, or expanded into a new on-screen detailed Replay view?
- **Options and tradeoffs:** Removing it keeps the requested page concise and avoids an empty concept; an informational card preserves CSV field documentation but consumes space without interaction; a detailed Replay view could expose sample-level evidence but materially expands UI, computation, and validation scope beyond the current request.
- **User answer:** Option 1: completely remove Analytical Replay.
- **Explicit rationale:** No additional rationale was stated; the selected option was recommended because every interactive responsibility has a clearer colocated destination and the residual region would contain only explanatory text.
- **Resulting impact:** DEC-010, REQ-008, and AC-005 require complete removal of the region without a duplicate selector or empty placeholder.

### DISC-011: Qualification population and recording coverage clarification
- **Situation:** The user understands that kernels passing Training are tested for Qualification against every recording. Source inspection shows a narrower admission boundary: each round first retains the rounded-best parameter configurations, filters fold kernels by the Validation allowance, and selects the lowest two Kernel Loss folds plus cutoff ties per retained configuration. Each admitted fold kernel then runs Qualification over all supplied recordings, including recordings outside a later fallback scope, before a retained candidate and its per-recording UI evidence are produced.
- **Question:** Factual clarification only; no unresolved design choice.
- **Options and tradeoffs:** Not applicable.
- **User answer:** The user's intended understanding is that admitted kernels are tested against every recording for Qualification.
- **Explicit rationale:** The per-recording result table must represent actual Qualification coverage rather than a partial or newly invented replay subset.
- **Resulting impact:** REQ-012 and AC-007 continue to require one row per supplied recording using the selected retained kernel's existing Qualification evidence; learning, candidate admission, and Qualification algorithms remain unchanged and out of scope.

### DISC-012: Selected-fold-kernel table disposition in the execution-log region
- **Situation:** The screenshot's red-circled lower Training region is currently `trainingCandidateTable`, with headers for Kernel / Round, History / taps, Ridge alpha, Scale / K, Score / confirm, Fit to refit, Folds / grouping, and Selection / Validation MSE. Existing execution summaries and the failure reason are rendered in a smaller scroll region immediately above. The user identifies the large red-circled region as the execution-log display area.
- **Question:** When the large lower region becomes the execution log, what shall happen to the existing selected-fold-kernel table?
- **Options and tradeoffs:** Replacing it entirely gives the log the full region and avoids the current empty table, while selected retained kernels remain inspectable on Replay & Qualify; retaining a collapsible table preserves during-run parameter evidence but adds vertical complexity; tabs preserve both in one footprint but require a new Log/Candidates navigation state and can hide active log updates.
- **User answer:** Option 1: completely remove the selected-fold-kernel table.
- **Explicit rationale:** No additional rationale was stated; the selected option was recommended because the full region becomes the requested execution log and final kernel inspection remains on Replay & Qualify.
- **Resulting impact:** DEC-011 revises REQ-003, REQ-004, REQ-013, AC-002, and AC-008 to remove the complete table surface and dedicate its footprint to the log.

### DISC-013: Execution-log entry depth
- **Situation:** The large lower region is now exclusively the execution log. Existing controller evidence includes current stage/progress messages, per-round scope and unavailable reasons, round elapsed time, worker batch progress, Peak RSS and launch RAM, completion timing, and failure reasons. The application also has a separate process diagnostics log that can contain lower-level lifecycle and Qt/application messages.
- **Question:** Which level of execution detail shall the Candidate Dashboard log display?
- **Options and tradeoffs:** A structured learning-event log provides actionable stage/round/progress/resource/failure evidence without unrelated application noise; moving only the current compact summaries leaves the large region sparse and omits live event history; exposing raw process diagnostics adds lower-level detail but mixes unrelated application messages and may reveal implementation-oriented noise.
- **User answer:** Option 1: structured Learning log.
- **Explicit rationale:** No additional rationale was stated; the selected option was recommended because it provides actionable run evidence without raw process/Qt noise.
- **Resulting impact:** DEC-012, REQ-013, and AC-008 fix chronological structured entries for Stage, Round, scope, progress/job counts, elapsed/resources, fallback/skip, and terminal outcomes. Run-to-run retention remains separate in DISC-014.

### DISC-014: Execution-log lifecycle across Learning runs
- **Situation:** A structured log can either represent only the current/most recent Learning run or accumulate multiple runs in one UI surface. Existing Training execution summaries are cleared when a new Learning run begins, while completion/failure evidence remains visible until then.
- **Question:** When Start Learning begins a new run, what shall happen to the previous UI execution log?
- **Options and tradeoffs:** Clearing at new-run start keeps one coherent run and preserves the previous terminal log until the user actually starts again; appending every run provides session history but requires run separators and can grow substantially; clearing immediately at terminal completion removes useful failure evidence and is unsuitable for diagnosis.
- **User answer:** Option 1: clear automatically when a new Learning run starts.
- **Explicit rationale:** No additional rationale was stated; the selected option was recommended because it keeps terminal evidence available until the next accepted run while preventing mixed-run logs.
- **Resulting impact:** DEC-013, REQ-014, and AC-009 require one-run retention, terminal visibility, no clearing on unrelated idle actions or rejected starts, and atomic clearing when a new run successfully starts.

### DISC-015: Follow-latest behavior while log events arrive
- **Situation:** The structured execution log can receive frequent events while the user is either monitoring the newest entry or reading older entries. Automatic scrolling must balance live visibility with the ability to inspect history.
- **Question:** How shall the log viewport react when a new event arrives?
- **Options and tradeoffs:** Smart follow scrolls to the newest entry only while the viewport is already at the bottom, pauses when the user scrolls upward, and exposes a return-to-latest cue; forced follow always shows the newest event but interrupts inspection; no automatic follow preserves position but requires continuous manual scrolling during monitoring.
- **User answer:** Option 1: Smart follow.
- **Explicit rationale:** No additional rationale was stated; the selected option was recommended because it preserves live visibility without interrupting inspection of older entries.
- **Resulting impact:** DEC-014, REQ-015, and AC-010 require follow-at-bottom, paused follow during upward inspection, an unseen-entry `Latest (N)` control, and deterministic resume behavior.

### DISC-016: Per-run execution-log capacity
- **Situation:** A Learning run can last for hours and produce many structured progress events. One-run retention prevents cross-run accumulation but does not itself bound memory within a long run. Overflow policy affects whether early evidence remains visible and whether the UI can grow without limit.
- **Question:** What capacity and overflow policy shall the in-app execution log use for one run?
- **Options and tradeoffs:** A 10,000-entry ring keeps the newest events and inserts a visible count marker when oldest entries are discarded, providing generous history with bounded memory; a 5,000-entry log that coalesces repeated same-stage progress updates uses less memory but loses granular timing history; unbounded retention preserves every event but permits UI memory and rendering cost to grow with run duration.
- **User answer:** Option 1: retain at most 10,000 entries and show cumulative discarded count.
- **Explicit rationale:** No additional rationale was stated; the selected option was recommended because it provides generous history with bounded UI memory and visible truncation.
- **Resulting impact:** DEC-015, REQ-016, and AC-011 require a 10,000-event newest-entry ring, a non-slot truncation marker, cumulative discard count, terminal-event retention, and reset on the next accepted run.

### DISC-017: Execution-log persistence outside the current app session
- **Situation:** The log now retains the current or most recent run until the next accepted Start Learning, but its behavior across Project Save/Open and application restart is undefined. Persisting up to 10,000 structured entries would change `.dicsproj` schema, project size, stale-result handling, and validation; session-only state avoids storage changes but terminal UI evidence disappears when the app closes. A separate exported log would add a new artifact workflow.
- **Question:** Shall the structured Candidate Dashboard execution log be session-only, saved inside `.dicsproj`, or exported as a separate artifact?
- **Options and tradeoffs:** Session-only state keeps the current project schema unchanged and relies on existing process diagnostics for durable troubleshooting; `.dicsproj` persistence restores the exact terminal UI log but enlarges and version-changes project storage; a separate export preserves shareable evidence without changing project schema but adds naming, conflict, and export controls.
- **User answer:** Option 1: keep the execution log only in the current App session.
- **Explicit rationale:** No additional rationale was stated; the selected option was recommended because it avoids project schema and file-size changes while existing process diagnostics provide durable troubleshooting evidence.
- **Resulting impact:** DEC-016, REQ-017, and AC-012 exclude `.dicsproj` persistence and a new log-export artifact, preserve in-memory log on Save and failed project replacement, and clear it on restart or successful project replacement.

### DISC-018: Loss evidence depth in the structured Learning log
- **Situation:** The user does not need Peak RSS or launch RAM and instead wants Loss information. Source evidence distinguishes aggregate Parameter Loss, which ranks parameter configurations, from per-fold Kernel Loss, which ranks Validation-passing kernels within each retained configuration; raw per-condition Training/Validation MSE and the Validation allowance gate are separate evidence. Logging every evaluated configuration and fold could consume thousands of entries, while final-only values omit how optimization improved.
- **Question:** Which Loss evidence depth shall the structured Learning log display?
- **Options and tradeoffs:** Progress-summary Loss logs each new current-best Parameter Loss with its H/alpha/K, improvement, final rounded-best Parameter Loss, and each selected fold's Kernel Loss plus Validation gate result, showing optimization without logging every discarded candidate; final-only Loss shows only the per-round winning Parameter and Kernel Loss values, staying concise but hiding the search trajectory; exhaustive Loss logs every evaluated parameter/fold/condition Training and Validation MSE, providing complete detail but rapidly consuming the 10,000-entry UI capacity and making the run difficult to scan.
- **User answer:** Option 1: Loss search summary.
- **Explicit rationale:** No additional rationale was stated; the selected option was recommended because it shows optimization improvement and final selection without logging every discarded candidate.
- **Resulting impact:** DEC-018, REQ-013, and AC-008 require new-best Coarse/Fine Parameter Loss with parameter coordinates and improvement, final four-place Parameter Loss, selected Kernel Loss, and Validation gate outcomes while excluding exhaustive non-best/per-condition entries.

## Out of Scope

- Changing learning, qualification, candidate-ranking, or persistence algorithms.
- Making diagnostic-only kernels eligible for Profile header export.
- Displaying weights, biases, residual arrays, or fold provenance in the selected-kernel summary.
- Redesigning visual styling beyond containment, alignment, scrolling, and analytical-kernel selection feedback.

## Open Decisions

None.

## Routing/Gates

- Risk: R1 standard QML/controller interaction and layout correction.
- Required gates: TDD and code review.
- The earlier product execution authorization is suspended; this contract delta requires a new exact `開始執行` after materialization.
- Standards review: PASS.
- Spec review: PASS.

## Revision History

| Revision | Change |
|---|---|
| 1 | Started an independent Candidate Dashboard scroll-containment change set and recorded the selected specification ownership. |
| 2 | Selected a bounded message-only vertical scroll region while keeping controls, timing, and candidate results outside it. |
| 4 | Reopened the unimplemented specification for Replay panel containment and explicit analytical-kernel selection. |
| 5 | Selected the Analytical Replay Kernel combo box, removed the top summary card, reduced Supplied Conditions to five aligned evidence columns, and opened parameter-summary depth. |
| 6 | Fixed the selected-kernel parameter summary to the exact requested fields and closed all decisions. |
| 7 | Reopened the change set, moved the sole kernel selector to Retained Round Winners, ordered kernel specifications before per-recording results, and opened the per-recording field decision. |
| 9 | Selected the standard per-recording result columns and opened the aggregate Supplied Conditions coexistence decision. |
| 10 | Removed Supplied Conditions and opened the recording-table-to-Analytical-Replay selection decision. |
| 11 | Moved Model TXT export to kernel specifications, bound Replay CSV export to each recording row, and opened the residual Analytical Replay region decision. |
| 12 | Removed Analytical Replay and clarified that each admitted fold kernel's Qualification covers every supplied recording without changing learning or qualification algorithms. |
| 13 | Reopened the change set and designated the large lower Candidate Dashboard region as the execution-log display area, pending the selected-fold-kernel table disposition. |
| 14 | Removed the Training selected-fold-kernel table and opened the execution-log detail-level decision. |
| 15 | Selected a structured Learning-event execution log and opened its cross-run retention lifecycle. |
| 16 | Selected one-run log retention with clearing on the next accepted Start Learning and opened follow-latest behavior. |
| 17 | Selected Smart follow with `Latest (N)` feedback and opened the per-run log-capacity decision. |
| 18 | Bounded the in-app log to 10,000 newest events with visible truncation and opened cross-session persistence. |
| 19 | Kept the execution log session-only, excluded project persistence/export, and closed all decisions. |
| 20 | Removed visible Peak RSS / launch RAM, prioritized Loss evidence, and opened the Loss-depth decision. |
| 21 | Selected Loss search summaries and closed all decisions. |
| 22 | Recorded verified implementation evidence after 365 passing tests, architecture gate PASS, rendered UI inspection, and passing Standards/Spec code-review axes. |
