---
spec_version: 1
spec_id: SPEC-0032
revision: 2
status: implemented
change_set: independent-windows-launcher
---

# Independent application after successful Windows startup

## Problem
SPEC-0031 waits for application exit and shares its console. The user supplied a screenshot of a ready main window with the launcher still open, and confirmed closing that console also closes the software. The desired success boundary is main-window readiness, not application shutdown.

## Solution
Keep environment checks visible and synchronous. Start the application detached from the command console with stdin disconnected and stdout/stderr redirected directly to its own UTF-8 log. Observe an actual visible main window belonging to this launch, then let the launcher exit successfully. Preserve the existing error pause when environment checks fail, the child exits before readiness, or readiness cannot be confirmed. Production application imports and algorithms remain unchanged.

## User Stories
- As a user, the command window closes automatically when the software opens successfully, and the software runs independently.
- As a user, I can still read startup errors in the command window and logs.

## Requirements
| ID | Requirement |
|---|---|
| REQ-001 | A visible main window belonging to the newly launched application, not merely creation of a process or a pre-existing instance, completes startup and permits the command window to close with exit 0. |
| REQ-002 | The application must have no launcher console association or stdin/stdout/stderr pipe dependency. It must remain running when the launcher exits or its command console closes. |
| REQ-003 | Preserve failed environment/bootstrap checks and failure-only pause. Treat any child exit before readiness, including exit 0 with no window, as a startup failure. Print the failed stage and application log so import/QML failures remain readable. |
| REQ-004 | Keep per-launch UTF-8 launcher/application logs and safe console rendering. Application output continues to its file after launcher exit. A 120-second readiness observation limit reports unconfirmed startup, PID and log path, keeps the error console, and does not assert a crash or kill the detached application. |
| REQ-005 | Keep installed dependencies, application composition, training algorithms, and project data unchanged. Use the existing psutil package and Windows window APIs only in launch tooling to match the new process family, including the venv interpreter child. |

## Decisions
| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Close the console on visible application readiness; retain it only on startup errors. | User explicitly corrected the previous console lifetime. |
| DEC-002 | Use Windows detached process creation and direct log-file handles, with native window ownership checks. | Makes console lifetime independent without changing product startup callbacks or domain behavior. |

## Discussion Context
None.

## Acceptance Criteria
| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001, REQ-002 | Real Windows batch returns 0 while its newly launched window/process remains live; detached child has no console and no inherited pipe dependence. Existing other windows cannot satisfy readiness. | Native controlled window/Qt subprocess checks and PID-filter fixtures. | PASS: native batch return while own window survives; actual WM_CLOSE of test console leaves detached app alive; PID filtering and clean bootstrap. build/detach-native-final.xml. |
| AC-002 | REQ-003, REQ-004 | Environment failures, import errors and early clean exits fail visibly and pause; timeout is distinguished from crash; Unicode logs survive launcher exit. | Focused subprocess/Windows batch tests and simulated readiness timeout. | PASS: failed environment, import and early clean exit, error pause, Unicode output, unique logs and non-destructive timeout. 17 focused tests in build/detach-native-final.xml. |
| AC-003 | REQ-005 | Real Qt composition opens and survives launcher exit; relevant regression, formatter, architecture and two-axis review pass. | Bounded native probe, pytest, Ruff, architecture_cli.py development/release and review. | PASS: real run.bat returns0 with real mainwindow alive; test-owned close0; 38 QML/diagnostics regressions, Ruff, dev/release architecture gates, Standards and Spec reviews. docs/validation/SPEC-0032-launcher-detachment.md. |

## Relationships
| Source | Relation | Target |
|---|---|---|
| DEC-001 | refines | REQ-001 |
| DEC-002 | refines | REQ-002 |
| AC-001 | depends_on | REQ-001 |
| AC-001 | depends_on | REQ-002 |
| AC-002 | depends_on | REQ-003 |
| AC-002 | depends_on | REQ-004 |
| AC-003 | depends_on | REQ-005 |

## Out of Scope
No splash screen, startup-speed promise, production algorithm/source changes, or automatic reopening of a console for errors occurring after successful startup. Later errors remain in application/startup log files and existing application diagnostics. SPEC-0031 is historical and remains immutable.

## Open Decisions
None.

## Routing/Gates
Spec review: PASS
User correction continues the explicitly authorized launcher repair. Higher-priority session instructions preserve authorization and require acting on corrective requests; no renewed exact-phrase approval or fabricated user-event identity is required. Record lifecycle/validation evidence and perform scoped edits under that authority rather than reuse an obsolete SPEC-0031 receipt. No source-boundary change inside src; tooling-only native readiness observation and detached process handles are owned by the launch helper. Validate design before edits. Preserve scoped Ruff and CRLF. No new dependency, port, product callback, domain state or generated architecture view.

## Revision History
| Revision | Date | Change |
|---|---|---|
| 1 | 2026-09-12 | Record user correction: console closes after ready main window, application remains independent. |
| 2 | 2026-09-12 | Recorded implementation PASS evidence. |
