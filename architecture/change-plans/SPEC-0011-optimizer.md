# SPEC-0011 implementation authoring record

Specification: `specs/SPEC-0011-qualification-result-clarity.md`, revision 150.
User execution authorization: current task, 2026-08-29, exact `開始執行`.
This record does not accept ADR-0001/0002 or claim runtime acceptance.

## Responsibility and boundary design

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Capture settings and annotated evidence | studio_application | learning_qualification | studio_application | application snapshot | LearningRequest, LearningSettings, LearningDataset | studio_application | private controller snapshot only | application -> learning | learning -> Qt/controller |
| Fit candidate by fold | learning_qualification | history_worker_adapter | studio_application | FoldJob | LearningExecutionPort | studio_application | immutable dataset/groups; adapter-private processes | adapter -> learning contracts | learning -> multiprocessing/psutil |
| Replay whole recording | learning_qualification | history_worker_adapter | studio_application | RecordingJob | LearningExecutionPort | studio_application | frozen kernel/scores | adapter -> learning contracts | worker-local threshold selection |
| Save/open settings and evidence | studio_application | project_session | studio_application | parent-owned mapping | ProjectDocument | studio_application | immutable result and next-run settings separately | application -> project/learning | project -> learning or Qt |

## Type ownership matrix

All new named types are cataloged in the manifest before source edits. LearningSettings,
ParameterPoint, ConditionLoss, FoldJob, FoldResult, ParameterResult, KernelTrainingEvidence,
RoundProvenance, RunProvenance, ExecutionBatch, RecordingJob, RecordingResult and the
two domain error types belong solely to learning_qualification. All values are immutable,
with job/run/result lifetimes and no mutation authority. Referenced project types are
listed in the manifest. NumPy arrays are logically immutable transferred values; no
shared-memory writes. LearningExecutionPort is demand-owned by learning_qualification.
SpawnLearningExecutor owns private multiprocessing bindings and consumes domain values.
No native ABI change; Python process payloads and optional project provenance/settings
change. Historical models/settings are never inferred from new defaults.

## State object ownership matrix

| State | Owner / lifetime | Readers | Writers | Cross-boundary access |
|---|---|---|---|---|
| Search centers, step tuples, cache, pending frontiers | learning_qualification / round | coordinator | coordinator only | immutable jobs/results only |
| Fold maps and settings | learning_qualification / run | coordinator and job snapshots | constructed once | immutable values |
| Processes, pipes, active job map | history_worker_adapter / batch | adapter | adapter only | no handles in domain contracts |
| Next-run settings and displayed result | studio_application / session | controller/UI projections | controller only | captured LearningSettings / explicit ProjectDocument mappings |

No new mutable module globals, thread-local objects or shared singleton state are planned.
Function-local dictionaries remain confined to their owner; array mutation during fitting
must not change dataset or cached result arrays.

## Dependencies and parent mappings

Actual and intended edges remain application -> learning/project/worker-adapter;
worker-adapter -> learning demand contracts. The new optimizer is private implementation
within learning_qualification, not a sibling domain. Existing workspace/project/profile
mappings remain parent-owned. No new domain-to-adapter edge or additional output event sink.

## Flow review and alternatives

As-is: Qt -> one coordinator -> four History spawn processes -> per-History grouped
CV and all-data refit -> worker-local threshold Qualification -> one retained round winner.
Baseline: 332 tests pass; development architecture gate passes (QML analyzer SHOULD only).

Selected functional structure: Qt -> captured settings/evidence -> constrained Cycle plan
-> coordinator coarse/fine frontier -> bounded candidate-fold jobs -> full-N aggregate ->
best parameter groups -> Validation-filtered original fold kernels -> whole-recording
Score/Qualification -> retained results. User approved eight search workers and four
Qualification workers; completion order is not ranking order.

Alternative: one process performs every fit/fold and Qualification serially. It remains
a functional reference/fake-port test path, with fewer dataset copies but no parallel
fold execution. The production path uses bounded batches of reusable spawn workers,
with one dataset copy per worker/batch instead of sending waveform data per fold job.
Neither topology is asserted to be faster without representative measurements.

Time estimate per candidate is N fits plus two common-mask evaluations per condition;
Ridge width is 3*taps plus bias, matrix storage O(rows*3*taps), normal-equation solve
O((3*taps)^3). Coarse jobs are N*35 off or N*210 on before alias reuse. Fine work depends
on accepted ties and convergence; no invented wall-clock cutoff. Peak memory includes
parent dataset, up to eight dataset copies, active FIR matrices and cached fold kernels.
Retain existing 85%-of-launch-available-RAM admission; confirmed shortage cancels, never
downsizes/retries. Runtime capacity/performance assurance remains pending; baseline tests
are functional evidence, not scheduler or memory proof. Workload is best-effort; no RT
deadline, affinity/cache tuning or new platform-performance claim is introduced.

## Validation seams and order

Use the specification's existing seams: LearningService public plan/evaluation/run APIs,
LearningExecutionPort fake and real adapter, controller setting/Start Learning APIs,
ProjectSessionService/explicit save-open, and existing Replay/Profile export interfaces.
Extend the existing tests at those seams; do not test private optimizer state directly.
Red/green slices: Cycle allocation; fitting/target metrics; ranking/search boundaries;
worker and cancellation; controller persistence and qualified-result preservation.
Final checks include full pytest, architecture development/release gates and Windows
spawn/application runtime scenarios. Native scheduler/resource evidence is required for
performance claims; missing evidence is BLOCKED, never a fabricated PASS.

Evolution: adding a new search parameter changes learning-owned values/search/tests and
their serializer mapping; replacing spawn affects the adapter/port suite; adding a
recording source stays in workspace and parent mapping; UI subscribers remain outside
the domain. No new direct sibling dependency is needed.
