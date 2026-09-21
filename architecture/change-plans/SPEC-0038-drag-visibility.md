# SPEC-0038 pre-code design and validation

## Boundary Design Table
| Boundary | Owner | Input/output | Change |
|---|---|---|---|
| AnnotationPage / WavePanel / annotation lanes, Main.qml | desktop_adapter (L3+) | Mouse gestures and page-shared preview; controller edit calls | Keep active dragged delegates visible until release/cancel to prevent mixed endpoint reevaluation from canceling their MouseArea. Plot clipping still applies. |
| StudioController annotation edits | studio_application (L0) | Sample-snapped domain edit and state notification | Unchanged. |

## Type Ownership Matrix
| Type | Owner | Visibility / consumers | ABI/storage change |
|---|---|---|---|
| WavePanel, AnnotationPage QML component and Rectangle/MouseArea delegates | desktop_adapter | Private Qt UI; Main.qml | None; no new named types. |
| StudioController | studio_application | Qt composition mapping | None. |

## State Object Ownership Matrix
| State | Owner / lifetime | Read/write authority | Change |
|---|---|---|---|
| draggingGroup, dragDelta, draggedAnnotationIndex | desktop_adapter; AnnotationPage instance | Page handlers write; both WavePanels and lanes read | No new state. Visibility now explicitly respects active gesture membership. |
| visualStart/End, clippedStart/End, gestureSelected | desktop_adapter; interval delegate | QML bindings; existing resize handlers | No storage or mutation changes. |
| Annotation interval data and undo history | studio_application coordinating data_workspace | Controller/domain authority | Unchanged. |

## Actual/intended dependencies and parent mappings
| Actual edge | Intended edge | Parent |
|---|---|---|
| studio_application -> desktop_adapter | unchanged | L0 composition consumes independent L3+ adapter; adapter parent null |
| Main.qml WavePanel -> AnnotationPage via existing group signals | unchanged | Private nested QML components within desktop_adapter |
| AnnotationPage -> StudioController edit slots | unchanged | Existing L0 Qt context mapping, no L1 public Qt contract |

## Planned manifest
Only append the active-drag visibility invariant to desktop_adapter. No new module, type, state object, port, event, source-set, execution or dependency edge. Existing schema 2.2.0 and zero-entry baseline remain. Both ADRs are proposed and remain unaccepted. The development gate passed before changes with existing SHOULD SYM004 (QML analyzer coverage); validate planned manifest before source editing.

## Verification
Ruff 0.16.6 is the governed Python fallback; existing QML style retained. Existing test_qml_smoke.py formatting check passed. New Qt mouse regression fails all eight selected/unselected, Internal/External, release/cancel combinations before repair because the gesture cancels on large displacement. Validate visibility, ordered bounds, same-side consecutive dragging, cancellation, duration and undo after repair; then run existing annotation/waveform/QML regressions and architecture render/gate.

## Final implementation and evidence

The final product diff is one visibility guard and one explanatory comment in Main.qml WavePanel. While groupDragging and gestureSelected are true, the interval stays visible to retain its MouseArea grab. The plot still clips drawing. Release/cancel uses the existing state reset and controller commit/clamp policy. No new runtime state, types, callbacks or dependencies were added.

Review refinement: leave annotation-lane visibility unchanged. Its existing viewport predicate does not have the waveform clippedEnd > clippedStart transient-inversion problem; extending its visibility outside the lane would change unrelated behavior. The manifest documents the final, waveform-only invariant. This refines implementation within DEC-001/003 without changing SPEC requirements.

Validation on Windows with project Python 3.12 / PySide6 and QT_QPA_PLATFORM=offscreen:
- Red: the new eight-case mouse-event regression failed on original source due to unwanted gesture cancellation.
- Green: eight cases pass for Internal/External, selected/unselected and release/cancel. Assertions cover ordered visible bounds during the drag, unchanged model before commit, same-side consecutive dragging, duration, undo, both edge-resize handles, lane movement and left-boundary clamp.
- Final combined command: `.venv/Scripts/python.exe -m pytest tests/test_annotation_drag_visibility.py tests/test_annotation_controller.py tests/test_waveform_item.py tests/test_qml_smoke.py -q -p no:cacheprovider --tb=short` -> 67 passed in 10.23s.
- Ruff 0.16.6 format check: new test file passes. QML existing style preserved.
- Architecture render completed through architecture_cli.py; final development gate with manifest/adoption/baseline exits 0, PASS VERIFIED. Existing SHOULD SYM004 indicates incomplete installed language-analyzer support for some desktop adapter symbols; actual QML paths were exercised by Qt tests. Baseline remains empty and ADR statuses remain proposed.
- No physical interactive desktop replay, release package rebuild, commit or application restart is claimed. No debug logging or instrumentation was added to production.

Acceptance mapping: AC-001 and AC-002 are covered by the eight-case real QML gesture replay; AC-003 by its duration/undo/boundary assertions and existing controller/group-drag tests; AC-004 by resize/lane assertions, existing pan/zoom/waveform tests, formatter check and development architecture gate.

Implementation review: no changed controller or persistence contract; active delegates remain clipped by plotArea; canceled MouseArea ownership clears before the existing reset handler; released gestures still commit once. The regression observes both views and repeats interaction without counterpart recovery, rather than only testing the visibility expression.
