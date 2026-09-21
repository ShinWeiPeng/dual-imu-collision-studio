# SPEC-0027 pre-code ownership and validation plan

## Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Execute jobs | learning_qualification | history_worker_adapter | studio_application composition | Immutable FoldJob/RecordingJob | learning.execution | Existing composition | Batch-local jobs/results | Adapter imports Learning contracts | Domain imports adapter |
| Sample system RAM | psutil OS API | history_worker_adapter | None, adapter private | total/available byte snapshot | Private admission/check | history_worker_adapter | Local snapshot only | Adapter to psutil | OS snapshot leaked into domain state |
| Return failure/evidence | history_worker_adapter | learning_qualification | Existing Learning orchestration | ExecutionBatch or existing error | learning.execution | Identity/no new mapping | Existing resource evidence | Existing return path | New callback or shared mutable state |

## Type Ownership Matrix

| Type | Owner | Referenced types | ABI/wire/storage impact |
|---|---|---|---|
| SpawnLearningExecutor | history_worker_adapter | Learning jobs, ExecutionBatch, existing errors | Default policy changes; no signature or persistence change |
| ExecutionBatch / HardwareMemoryInsufficientError / HistoryExecutionError | learning_qualification | Existing immutable results | None |
| psutil snapshot | External provider, adapter-local use | Numeric byte fields | None; does not cross port |

## State Object Ownership Matrix

| State | Owner/authority | Lifetime | Cross-boundary access |
|---|---|---|---|
| _maximum_ram_fraction | Executor instance | Executor lifetime | Existing constructor only; default becomes 0.90 |
| Memory readings and budget | Adapter invocation | One sample/check | None |
| active/children/results/peak | Existing adapter invocation | Batch | Existing immutable return only |

No new mutable file/static/thread-local objects or address-sharing objects. Actual and intended edges remain history_worker_adapter -> learning_qualification and psutil/multiprocessing; adapter parent remains null, port owner remains learning_qualification. No new named types, ports, events or mappings.

## Flow/resource review

Existing Learning calls bounded synchronous execution; adapter checks admission, starts Windows spawn workers, polls progress/resources, and returns ordered results or cleans up on terminal failure. MLP estimate remains unchanged. As-is compares additional estimated work and total process RSS to 85% of launch available memory; selected policy uses current system occupied memory T-A and ceiling f*T. Additional-work budget A-(1-f)*T avoids charging existing application memory twice. Fraction f=0.90 comes from the user's SPEC-0027 decision. Sampled monitoring cannot guarantee a hard cap between checks. Existing worker capacities, polling cadence, job copies, learning algorithm and retries remain unchanged. No real-time or speed improvement claim.

Alternative adaptive concurrency was deferred by DEC-001; remaining-RAM 95% was rejected in favor of DEC-002. Model assurance: estimated for actual workload memory; controlled predicate and lifecycle acceptance will be tested. No OS scheduler/resource calibration claim. External applications can consume the reserve after admission. Adding a new learning family reuses this adapter policy; a different OS provider needs equivalent snapshot semantics and contract tests; no domain or persistence migration follows.

Algorithm screening: MLP fitting unchanged. Admission is a deterministic adapter resource policy fixed by the confirmed spec, not a new L1/L2 product algorithm. Description change is confined to the existing adapter invariant; regenerate all views using the public CLI. No ADR exception or acceptance is required.

## Validation

Before source: canonical spec validation, targeted Ruff check with unchanged hash, and design gate on planned manifest. Development: real executor-entry controlled memory tests, bounded real Windows spawn completion/cleanup, existing MLP and History regressions. Full regression, deterministic render check and development/release architecture gates follow. Preserve output in build/spec27*.log. No deliberate RAM exhaustion; actual long user run remains unmeasured.
