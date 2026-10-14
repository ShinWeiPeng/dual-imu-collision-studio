# SPEC-0040 implementation and verification

SPEC-0040 revision 3 remains `confirmed`. Product changes are implemented locally; overall acceptance is **BLOCKED**, so the specification is not marked `implemented`. SPEC-0039 is unchanged.

The schema-1 model JSON no longer includes `detector.release_ratio` or `detector.release_quiet_time_s`. The command port, encoder and controller no longer pass those arguments. Other model parameters, selected numeric precision and execution-content hashing are preserved.

Deployment qualification uses the retained frozen FIR model and its matching source dataset, without fitting. It separately replays strict collision candidates with common rearm 0.8 / 50 ms and the existing Qualification criteria. A complete input identity binds model, data, labels, threshold, coverage and policy/version. Original qualified speed/offset coverage must pass. Historical replay, Header and Model TXT remain under their historical contract.

Export Profile now offers per-kernel deployment validation, cancellation, state/reason and independent JSON export. Missing, failed, cancelled and stale evidence prevents saving. Evidence is session-local; reopening a project requires revalidation. List refresh uses current references; export admission recomputes complete hashes. Session replacement cancels validation and rejects late completion.

| Check | Actual result |
|---|---|
| Initial full regression | 624 passed, 3 failed out of 627. Fixed-run logs: `artifacts/tests/spec40-full-20261006-01/pytest.log` and `junit.xml`. |
| Initial architecture failure | Corrected ambiguous relative import; rendered authoritative manifest views. Development and release gates then PASS, with only the pre-existing optional QML-analyzer warning. |
| Two native Windows launcher failures | Both PASS when rerun outside the restricted desktop environment. `artifacts/tests/spec40-launcher-native-01/junit.xml`. |
| Final focused regression | 62 passed, including architecture smoke, JSON precision/hash/file behavior, frozen Qualification, repeated real Qt/QML interaction and cancellation/session replacement. `artifacts/tests/spec40-final-regression-01/pytest.log`. |
| Formatter | All five changed product Python files pass `ruff format --check`. |
| Standards / Spec source review | Both axes have zero unresolved product findings after fixing repeated UI fingerprint scans and epoch-time early rearm. |

QML interaction is verified through the real engine, row buttons, naming dialog and filesystem. The restricted-environment screenshot rendered missing-font boxes. An additional native visual run produced no completed result and was stopped; native visual readability is **unverified**, not PASS. No physical firmware acceptance is claimed.

The required newer whole-project layout gate returns **FAIL**: existing root/nested tests, legacy output locations, unclassified historical files and non-finalized run records remain. The managed acceptance completion returns **BLOCKED** (`compatibility requires diagnosis`). Details are preserved under `spec-governance/spec40-final-check-summary.json` and `spec40-layout-result-final.json`.

The implement skill requires: “Run the whole-project layout gate for positions, roles, owners and references.” Its shared directory contract also requires migration of legacy tests and outputs with original-byte provenance. These checks have not been waived or hidden with a baseline. The supported managed replacement entrypoint does not provide rename/delete, so a complete migration cannot be performed through that entrypoint in this change set. Further migration and current validation-run/plan evidence are required before overall acceptance.

Changes remain in the working directory; commit/push are outside SPEC-0040 scope.
