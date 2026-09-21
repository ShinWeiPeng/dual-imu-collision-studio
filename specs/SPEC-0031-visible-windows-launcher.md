---
spec_version: 1
spec_id: SPEC-0031
revision: 3
status: implemented
change_set: visible-windows-launcher
---

# Visible Windows launcher and startup diagnostics

## Problem
Double-clicking run.bat closes the command window immediately after starting pythonw. Startup errors before application diagnostics are installed are invisible. A detached startup probe took approximately 30 seconds to import the application, then completed normally; this is not proof of a crash or a guaranteed import-order optimization.

## Solution
Keep the launcher console for the application lifetime, execute Python synchronously, stream merged subprocess output to the console and a per-launch UTF-8 log, and stop on the first failed stage. Failure preserves the console until a key is pressed; ordinary application exit closes normally. Retain existing application and training behavior.

## User Stories
- As a Windows user, I can see startup progress and read a failure instead of losing the command window.
- As a maintainer, I can inspect startup errors that occur before application diagnostics begin.

## Requirements
| ID | Requirement |
|---|---|
| REQ-001 | run.bat resolves its own directory, uses console Python synchronously, and keeps the command window available throughout application execution. Show environment-check, environment-creation when needed, dependency-check/update and application-start stages. |
| REQ-002 | Stop after the first failed environment creation, dependency update, or application process. Return a nonzero exit code, display the failed stage and code, and pause on failure only. Missing bootstrap Python must produce a readable error and pause. |
| REQ-003 | Create and display a unique per-launch log path before importing the application. Record stage timestamps, elapsed times, merged stdout/stderr and exit codes in UTF-8. Preserve import and QML failures. If logging cannot be initialized, report the error and fail visibly. |
| REQ-004 | Preserve existing editable dependency-check semantics, Qt application entrypoint, analytical behavior, and installed-project compatibility. Scope is launcher/tooling, tests and documentation; no import-order or training algorithm changes. |
| REQ-005 | Validate real Windows batch success and failure paths in isolated controlled fixtures, actual application startup with a bounded test-owned shutdown, and appropriate regression and architecture gates. Report fixture and real application evidence separately. |

## Decisions
| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Implement the recommended launcher-first scope with a visible console; startup speed optimization remains separate. | The user requested execution immediately after the launcher-first recommendation. |
| DEC-002 | Use a standard-library launcher helper to stream child output and retain exit status. Keep the batch wrapper responsible for failure pause. | Windows batch pipelines alone obscure exit codes and cannot reliably tee output without extra runtime tooling. |

## Discussion Context
None.

## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | Successful batch execution prints stages and exits without pause; failed stages prevent later stages and reach failure pause with the original nonzero code. | Windows cmd fixture integration plus helper subprocess tests. | PASS: real Windows success, dependency/app failure and bootstrap failure; genuine pause and stop ordering. build/launcher-final.xml, 13 focused tests. |
| AC-002 | REQ-003 | Each launch has a distinct readable log containing stage boundaries, Unicode child output, errors and codes from before application imports. Logging failures remain visible. | Controlled success/import-error/logging-error tests. | PASS: UTF-8 Unicode logs, CP950 console, unique launches, pre-import errors and log failure tests. build/launcher-final.xml. |
| AC-003 | REQ-004, REQ-005 | Real application creates its main window and exits cleanly under bounded test-owned shutdown; existing tests and architecture gates pass. | Native Python/Qt startup probe, pytest and architecture_cli.py development/release. | PASS: visible real Qt window and clean exit0 in build/launcher-native-final.log; 507 regressions and final 13 focused tests; Ruff, development/release gates, independent reviews. docs/validation/SPEC-0031-launcher-validation.md. |

## Relationships
| Source | Relation | Target |
|---|---|---|
| DEC-001 | refines | REQ-001 |
| DEC-002 | refines | REQ-003 |
| AC-001 | depends_on | REQ-001 |
| AC-001 | depends_on | REQ-002 |
| AC-002 | depends_on | REQ-003 |
| AC-003 | depends_on | REQ-004 |
| AC-003 | depends_on | REQ-005 |

## Out of Scope
No import-order performance claim, splash screen, new dependency, model or filter change, installer redesign, or global TEMP override. SPEC-0030 remains immutable. Current console lifetime means closing that console can also end the launched application.

## Open Decisions
None.

## Routing/Gates
Spec review: PASS
The user authorized execution with the current message: 開始執行. The host read_thread reports current turn 01a0941c-ec9d-7232-824d-da2ef7a85045; individual user-message IDs are unavailable, so the authorization reference identifies that actual turn and is caller-attested, not host-authenticated message evidence. New specification resolves the initial resume route's lack of an active confirmed launcher contract. Preserve existing Ruff Python style and batch CRLF. Review boundary/type/state ownership before edits. Tooling is outside src production modules; no production module, port, event or state contract changes. Test launcher orchestration through controlled subprocesses and isolated batch fixtures, then actual Qt composition. Run development/release architecture gates and Spec/Standards review. No hardware or scheduler-resource claim is made.

## Revision History
| Revision | Date | Change |
|---|---|---|
| 1 | 2026-09-12 | Record the launcher-first proposal accepted for execution by the current user instruction. |
| 3 | 2026-09-12 | Recorded implementation PASS evidence. |
