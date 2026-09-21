# SPEC-0028 pre-code design

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Count and estimate fold | learning_qualification | history_worker_adapter | studio_application composition | FoldMemoryEstimate | learning.execution | Existing adapter binding | Immutable dataset/job | Adapter -> Learning | Learning -> psutil/adapter |
| Budget and runtime sampling | Windows/psutil | history_worker_adapter | None | Native byte counts | Private budget | Adapter | Check-local snapshot | Adapter -> OS | Native object across domain port |
| Report admission | history_worker_adapter | learning_qualification | Existing Learning orchestration | ExecutionBatch diagnostics / existing error | Existing progress path | Learning | Batch-local summary | Existing port return | New global state or waveform logging |

## Type Ownership Matrix

| Type | Owner | References | ABI/storage impact |
|---|---|---|---|
| EvidenceRowCounts | Learning private | Numeric counts | None |
| FoldMemoryEstimate | Learning | Numeric components/rows | Immutable cross-module value; no persistence |
| ExecutionBatch | Learning | Existing results, added tuple of diagnostic strings | Defaulted trailing field preserves callers; no project schema |

## State Object Ownership Matrix

| Object | Owner/authority | Lifetime | Crossing |
|---|---|---|---|
| Eligibility/cycle/finite masks | Learning estimator invocation | One count | None |
| Estimate list and diagnostic strings | Adapter invocation | One batch | Immutable summaries only |
| Windows trace/parser state | Development runner | One bounded capture | Test-only artifacts |

No new global/static/thread-local mutable state or cache. Actual and intended module edges and parent mappings remain unchanged: Learning belongs to studio_application; adapter implements Learning-owned port. New private memory.py belongs to the existing Learning source directory.

## Flow and allocation model

Count selected evidence using the existing precedence and segment rules, without creating features. Account for whole worker dataset copies separately from selected evidence. Include list/NumPy scalar matrix construction, simultaneous dense arrays, validation arrays retained during fitting, preprocessing and Adam/checkpoint state, prediction workspace, and serialization. Reserve independently calibrated Windows/Python startup overhead per worker. Sum largest concurrent job peaks, plus one parent serialization workspace; existing parent resident memory is not charged again.

Model confidence is estimated until the two real-data acceptance cases pass. No training math, matrix allocation, scheduling, retries or system 90% policy change. Admission is a source-derived resource calculation, not a new learned decision algorithm. Runtime overhead constants and allocator accounting must be explained in code/report and calibrated if measurements exceed them. Retaining the old full-row formula is the baseline; matrix allocation rewrites and adaptive workers remain user-deferred. New recordings affect raw-copy and selected evidence terms separately; new interval behavior requires count parity tests. No new platform or real-time performance claim.

## Enablement evidence

Windows ETW PROC_THREAD+PERF_COUNTER capture/export succeeded with zero lost events/buffers. Exported kernel Peak WS covers both a launcher and its actual Python child after exit; the touched 16 MiB fixture produced a 31,838,208-byte subtree envelope. Evidence: build/spec28-enablement/counter-probe.etl, counter-stats.txt, counter-process.txt and counter-perf.csv. ResidentSet alone was insufficient for peak acceptance and is not used as the passing provider. Native counters remain the authoritative resource source.

## Verification

Validate planned manifest with design gate before source; targeted Ruff scope. Add row-count/production-matrix parity, exclusion and component tests, and reproduce captured old estimate. Capture bounded diagnostics. Two representative three-fold real-data batches use the real spawn adapter and native memory evidence; require estimate >= measured conservative subtree peak envelope plus parent increase. Full regression and development/release gates follow. User authorization: exact 開始執行 for SPEC-0028.
