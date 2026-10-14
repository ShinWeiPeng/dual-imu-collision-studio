# SPEC-0042 pre-code design
Confirmed scope: FIR memory estimation and admission concurrency, with unchanged
90 percent system RAM protection, inputs, results and zero retries. No new Port,
Event, public type, persistent setting, thread or priority/affinity is introduced.

### Boundary Design Table

| Interaction | Producer | Consumer | Parent | Producer contract | Consumer contract | Mapping owner | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|---|
| Fold dispatch/results | learning_qualification | history_worker_adapter | studio_application wires the adapter | FoldJob, LearningDataset | learning.execution | existing L0 composition | immutable job/data snapshot | adapter -> learning public contracts | learning -> concrete adapter |
| Allocation estimate | learning_qualification.memory | history_worker_adapter | no sibling mapping | FoldMemoryEstimate bytes | local admission calculation | direct use allowed | read-only evidence | adapter -> learning_qualification | domain -> psutil/multiprocessing |
| RAM and spawn | Windows/psutil | history_worker_adapter | adapter-private | primitive total/available bytes | local pool state | adapter | private process handles, capacity | adapter -> OS/framework | handles crossing into Learning |

### Type Ownership Matrix

| Type | Owner / level | Declaration | Kind / visibility | Lifetime / mutability / authority | Consumers / referenced types | ABI / wire / storage |
|---|---|---|---|---|---|---|
| EvidenceRowCounts | learning_qualification / L1 | domain/learning/memory.py | existing immutable value | one estimate; frozen; Learning constructs | memory calculations; primitive counts | unchanged |
| FoldMemoryEstimate | learning_qualification / L1 | domain/learning/memory.py | existing immutable value | one job estimate; frozen; Learning constructs | history_worker_adapter; primitive fields | fields and serialization unchanged |
| FoldJob / ParameterPoint | learning_qualification / L1 | domain/learning/model.py | existing immutable contracts | one batch; frozen | adapter and domain; domain settings/groups | unchanged |
| ExecutionBatch | learning_qualification / L1 | domain/learning/model.py | existing immutable result | one batch; frozen | Learning; result values/diagnostic strings | unchanged |
| SpawnLearningExecutor | history_worker_adapter / L3+ | adapters/parallel/learning_workers.py | existing adapter binding | application lifetime; adapter owns worker/config handles | L0 composition; Learning contracts | unchanged |

### State Object Ownership Matrix

| State | Owner / level | Lifetime | Mutation authority | Boundary / concurrency |
|---|---|---|---|---|
| estimates, diagnostic strings, selected capacity | history_worker_adapter / L3+ | one _execute call | calling analysis worker only | never published as mutable objects; immutable diagnostics only |
| active, children, pending, results, sampled peak | history_worker_adapter / L3+ | existing one batch | adapter only | private IPC/process objects; bounded by selected capacity |
| matrix/evidence row counters | learning_qualification / L1 | one estimate call | calculation only | read-only dataset; no file-scope/static/thread-local state added |

Actual/intended dependency edges are unchanged: studio_application composes the
adapter; history_worker_adapter implements demand-owned learning.execution and
may depend on learning_qualification. Learning does not import the adapter.
Existing L0/L1 parent mappings and immutable progress/result paths remain intact.

### Algorithm and Flow cost review

Feature screening: memory estimation and capacity selection trigger algorithm
review because they depend on data size, calibration, limits and failure policy.
Training mathematics is unchanged and is not reselected by this change.

Candidate A retains fixed eight-worker startup and can only refuse too-large
batches. Candidate B retains the same reusable spawn topology and admits the
largest fitting worker count before startup. The user selected B (SPEC-0042
DEC-002). Neither retries or changes model selection. Dynamic runtime resizing
is excluded: it would add pool state transitions and interfere with peak evidence.

Let T/A be freshly measured system total/available bytes after counting.
B=A-0.1T. Sort complete job peaks P descending. For k=min(8,N)..1, admit the
first k with parent serialization + sum(P[0:k] + runtime allowance) <= B.
When no k fits, fail before context/spawn; execution still checks system RAM.
Complexity: evidence counting linear in eligible source rows per fold/History;
capacity selection O(N log N) time and O(N) space, k <= 8. Counting must not
construct History-expanded feature matrices.

FIR phase estimates distinguish dense matrix bytes, CPython scalar/list/view
construction, Ridge feature normalization/Gram/solve, optional robust refit,
calibration prediction, retained fitting matrix and condition-scoring temporaries.
MLP equations and its fixed capacity remain unchanged. Dataset copies include
all recordings, not only the selected fold. Parent serialization and worker
runtime overlap with worker-local peaks and are charged separately.

All byte estimates are provisional until actual Windows full-lifetime native
memory evidence establishes AC-004. The existing 128 MiB loader allowance has
prior calibration provenance, but is not a proof of this new FIR peak. Reserve
is the existing user-confirmed 10 percent of total RAM; no new deadline or SLO.
Assurance: estimated for allocation phases; resource performance validation pending.

Evolution: larger input dimensions affect the Learning-owned width/count model;
a new training family requires its own estimator and validation, not a silent FIR
fallback; a new OS adapter supplies equivalent primitive RAM/spawn semantics
behind the existing Port. No project schema migration is required.

Validation: exact counts vs production matrices; zero/negative/exact admission
budgets; 1..8 capacity; no spawn on refusal; ordering/cancel/failure cleanup; unchanged
MLP/Qualification; actual project complete one-worker and admitted-worker runs,
all 18 jobs and native estimate-margin >= 0. Preserve incomplete evidence as BLOCKED.
