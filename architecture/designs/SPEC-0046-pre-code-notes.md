# SPEC-0046 pre-code design

Authorization: actual userMessage 01a12f36-b182-7380-bd2a-9720745ebff9 (開始執行), confirmed SPEC-0046 revision 6. Existing dirty changes are retained. No ADR is accepted by this change.

## Boundary Design Table
| Interaction | Producer | Consumer | Parent / mapping owner | Contract / state | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|
| Worker selection | QML | StudioController | studio_application | integer 1..8, default 1; locked in run, session only | QML to composition scalar command | automatic sizing, persistence |
| Run capture | StudioController | SpawnLearningExecutor | studio_application | private integer captured per batch, capped by jobs | composition to adapter | domain to adapter |
| FIR rows | LearningService | Learning optimization / fit / prediction | learning_qualification | owner-private borrowed immutable samples, indexes; 8 MiB feature blocks | within owner only | mutable feature representation escaping domain boundary |
| Memory observation | OS adapter | SpawnLearningExecutor | history_worker_adapter | measured system usage and process-tree RSS, existing 90 percent ceiling | existing OS port | estimator admission, retries |

## Type Ownership Matrix
| Type | Declaration | Owner | Visibility / role | Lifetime and references |
|---|---|---|---|---|
| _FirFeatureRows | domain/learning/service.py | learning_qualification L1 | private-helper | one fit/prediction, borrows internal ndarray and owned valid-row indexes; no mutation of borrowed samples |
| FirMatrixEvidence | domain/learning/model.py | learning_qualification L1 | existing domain evidence | existing fields; FIR features are private lazy rows, MLP explicitly materializes float64 |
| LearningService | domain/learning/service.py | learning_qualification L1 | existing public service | existing API, numerical results only cross boundary |
| StudioController / LearningWorker | adapters/desktop/controller.py | studio_application L0 | existing composition bindings | session worker count / per-run cancellation; remove estimate state |
| SpawnLearningExecutor | adapters/parallel/learning_workers.py | history_worker_adapter L3 | existing adapter | integer 1..8; existing batch-local processes/pipes |

## State Object Ownership Matrix
| State | Owner | Lifetime | Read / write authority | Escape / reclamation |
|---|---|---|---|---|
| lazy source and indexes | learning_qualification | one fitting matrix | source borrowed read-only, indexes owned; local rows only | never in FrozenFirModel; released after fold |
| block arrays and Gram/RHS | learning_qualification | one fit pass | fitting function only | block feature capacity 8 MiB; O(P squared) Gram; no full N by P FIR allocation |
| targets/residual/scores | learning_qualification | fit/calibration | fitting function only | O(N times 3 or 6), exact median/MAD retained; temporary arrays released at method return |
| worker preference | studio_application | desktop session | UI-thread owner command while idle | copied integer, no persistence |
| processes and pipes | history_worker_adapter | one batch | adapter only | finally terminate/join/kill/close on success, failure, cancellation; zero retries |

## Actual / intended edges and parent mappings
Unchanged edges: studio_application -> learning_qualification; studio_application composes history_worker_adapter; history_worker_adapter -> learning_qualification. learning_qualification parent is studio_application; concrete parallel adapter parent and wiring remain unchanged. No new dependency/module/event/port/callback. The existing private FirMatrixEvidence feature payload stays within its semantic owner.

## Algorithms and capacities
Use prefix invalid-sample counts and contiguous segment starts to select exactly the old finite history rows, preserving channel-major / newest-to-oldest lag order. Materialize feature blocks only when needed. Ridge uses float64 mean, centered variance, then standardized block Gram/RHS accumulation; alpha and degeneracy rules unchanged. Target prediction preserves scalar Replay column accumulation and target rounding. Exact residual center/scale and robust MAD remain; sorted seed samples with searchsorted produce the same history-support rejection, and lexsort preserves descending score / ascending source-index ties and five-percent cap. Dense compatibility is explicit for MLP and legacy matrix consumers. No data subsampling, precision change or History change.

## Gates and verification
Existing generated manifest design and development gates PASS before source changes (2026-10-12). Record new private helper type in owned catalog and render generated files; re-run project single architecture_cli gate after edits. Ruff 0.16.6 fallback, selected affected Python files checked without mutation; necessary existing worker-file formatting only, no full-program reformat.
Validation: old/new FIR numeric differences within existing tolerances, target rounding exact, 3/6 channels, segment/finite/degenerate/robust/precision coverage, actual Windows RSS before/after fixed single-worker fixture, then representative 2,070,704 rows / 33 taps optimized run. Runtime ceiling, failed startup, cancellation and child cleanup retained. Existing legacy layout violations are recorded by router; do not treat layout FAIL or unavailable evidence as PASS.
