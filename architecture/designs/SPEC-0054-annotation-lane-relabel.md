# SPEC-0054 跨列拖曳換事件類型

父層流程為 `prepare-workspace`。既有 `StudioController` 維持標記編輯、選取、歷史與確認狀態的唯一寫入權。下方事件列判斷放開位置和可用目標；事件時間以原始樣本起訖為準，時間軸的顯示範圍維持原值。

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Release over another event lane | desktop_adapter | studio_application | studio_application | Qt mouse release and lane hit test | Existing StudioController context binding with relabelAnnotation(recording, intervalId, label, reason) returning success | studio_application | QML drag preview, annotationIntervals, pending Ignore target | studio_application composes desktop_adapter and provides the binding | QML writes model or invokes data_workspace directly |
| Commit one label update | studio_application | data_workspace | studio_application | Look up interval by recording and ID and request validated replacement | Existing AnnotationInterval constructor and ActivityKind values | studio_application | Current interval plus edit history, selection and confirmed evidence | studio_application imports data_workspace model | data_workspace depends on Qt, controller or desktop_adapter |

The existing `stateChanged` publishes the new projection once after a successful commit. Invalid targets, stale recording or annotation IDs, and cancellation exit before mutation. The existing export guard applies. The existing Ignore dialog owns the proposed conversion until the user confirms a reason.

## Type Ownership Matrix

| Type or representation | Owner | Declaration and role | Visibility, lifetime, authority and consumers | ABI, wire and storage |
| --- | --- | --- | --- | --- |
| ActivityKind | data_workspace | model.py, annotation category | Existing public domain enum, immutable, used by controller | Existing values and serialized representation |
| AnnotationInterval | data_workspace | model.py, ID, sample interval and reason | Existing immutable domain value. The controller replaces one interval through its constructor validation | Existing storage fields and representation |
| StudioController | studio_application | controller.py, existing Qt context binding | One application instance, QML invokes the slot with existing primitive int/string types | Private Qt invocation surface, no persisted data format changes |
| Ignore relabel request | desktop_adapter | Main.qml, private dialog property with recording index and interval ID | Dialog lifetime, written and read only by the QML adapter | Transient QML value with primitive fields |

## State Object Ownership Matrix

| State | Owner | Lifetime | Read and write authority |
| --- | --- | --- | --- |
| Drag preview, shared viewport and pending Ignore relabel | desktop_adapter | Pointer gesture, annotation page, and modal interaction respectively | QML reads and writes preview and pending state. Relabel reads pane geometry and leaves viewport at its existing values |
| Annotation tuple, selection and edit history | studio_application | Current project and recording | Controller writes once on success. QML consumes the annotationIntervals projection |
| Confirmed workspace and results readiness | studio_application | Until annotation evidence changes | Controller invalidates through the existing edit path after a successful commit |

## Actual and intended edges

The composition root already provides the `studio` QML context and owns the dependency on the desktop adapter. The controller already uses `data_workspace` for annotation values and snapshots. The new slot uses those existing edges and UI-thread execution context. No new domain or external-technology dependency, queue, worker, persistent representation, output port or event type is introduced.

## Flow cost review

The current same-lane path previews X displacement and commits a single edit on mouse release. Cross-lane release uses lane hit testing and an existing-controller command. A delete-plus-create sequence would change identity and could split undo history, so the plan replaces the interval in one controller transaction. There is one bounded lane hit test at each relevant UI event and one interval lookup and tuple replacement at commit. The work runs on the existing Windows GUI event loop. Qt tests exercise the lane, dialog and controller with known sample ranges. This is interaction routing and immutable value replacement. It introduces no product algorithm or hard or soft real-time scheduling decision.

## Verification

AC-001 uses drag and wheel input on a zoomed viewport. AC-002 uses a cross-lane drag plus Undo and Redo, checking sample range and event ID. AC-003 uses the Ignore dialog and non-event drop targets. Architecture validation uses the repository development gate and the planned manifest design gate.
