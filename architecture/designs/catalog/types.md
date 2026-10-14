# CAT-types

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-types |
| version | 2 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: types
value:
- id: diagnostic-status
  owner: process_diagnostics
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/process_diagnostics/model.py
    symbol: DiagnosticStatus
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable diagnostic log path and previous-unclean-run summary exposed
    to application presentation.
  lifetime: One application process.
  mutability: immutable
  mutation_authority: []
  consumers:
  - process_diagnostics
  - studio_application
  - desktop_adapter
  references: []
  fields:
  - name: log_path
    type: string
    role: metadata
    meaning: Deterministic per-user rotating diagnostic log path.
  - name: previous_unclean_summary
    type: string
    role: metadata
    meaning: Bounded summary of the prior unclean process stage and progress.
- id: diagnostics-port
  owner: process_diagnostics
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/process_diagnostics/contracts.py
    symbol: DiagnosticsPort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Application-owned protocol for bounded lifecycle, Learning, exception,
    and Qt/QML diagnostics.
  lifetime: Application process.
  mutability: immutable
  mutation_authority: []
  consumers:
  - process_diagnostics
  - studio_application
  - desktop_adapter
  references:
  - diagnostic-status
  - learning-timing-evidence
  fields: []
- id: learning-timing-evidence
  owner: process_diagnostics
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/process_diagnostics/model.py
    symbol: LearningTimingEvidence
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Privacy-bounded fallback-round, cumulative stage, total-run, per-History
    attempt, and process-tree memory evidence.
  lifetime: One diagnostics observation.
  mutability: immutable
  mutation_authority: []
  consumers:
  - process_diagnostics
  - studio_application
  - desktop_adapter
  references: []
  fields: []
- id: null-diagnostics
  owner: process_diagnostics
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/process_diagnostics/contracts.py
    symbol: NullDiagnostics
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Side-effect-free diagnostics port used when persistent diagnostics
    are not composed.
  lifetime: Application process.
  mutability: immutable
  mutation_authority: []
  consumers:
  - studio_application
  references:
  - diagnostics-port
  - diagnostic-status
  fields: []
- id: workspace-snapshot
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: WorkspaceSnapshot
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable recordings, conditions, cycles, and annotations accepted
    for learning.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: []
  consumers:
  - studio_application
  references: []
  fields:
  - name: recordings
    type: tuple
    role: domain-value
    meaning: Validated semantic recordings and annotation partitions.
- id: header-proposal
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: HeaderProposal
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Provisional header/data-start rows and source columns inferred for
    explicit wizard confirmation.
  lifetime: One Mapping Wizard session.
  mutability: immutable
  mutation_authority: []
  consumers:
  - studio_application
  - data_workspace
  - tabular_adapter
  references: []
  fields: []
- id: learning-request
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: LearningRequest
    kind: class
  visibility: cross-module
  semantic_kind: command
  description: Immutable input required to fit and qualify a bounded candidate grid.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: []
  consumers:
  - studio_application
  - learning_qualification
  references:
  - learning-settings
  fields:
  - name: workspace
    type: object
    role: domain-value
    meaning: Application-mapped arrays and event truth.
  - name: numeric_type
    type: str
    role: policy
    meaning: Exact float32 or float64 replay target.
  - name: settings
    type: LearningSettings
    role: policy
    meaning: Immutable Training mode, fixed-grid selections and applicable grouped-CV
      or optimized-search controls captured at Start.
- id: qualification-result
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: QualificationResult
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: One retained winner per completed nested offset and speed fallback
    round plus the minimum-misjudgment diagnostic subset.
  lifetime: From completed learning until application exit.
  mutability: immutable
  mutation_authority: []
  consumers:
  - studio_application
  references:
  - qualified-candidate
  - learning-progress
  fields:
  - name: candidates
    type: tuple
    role: domain-value
    meaning: Retained round winners in deterministic completion order.
  - name: diagnostic_candidates
    type: tuple
    role: domain-value
    meaning: Minimum-error retained round winners ordered by finite worst collision
      latency and stable order, with all exact ties retained.
  - name: unavailable_rounds
    type: tuple
    role: domain-value
    meaning: Immutable LearningProgress snapshots identifying skipped round scopes
      and insufficient-evidence reasons; no fabricated candidates.
- id: learning-cancelled
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: LearningCancelled
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Typed cancellation outcome carrying the last immutable result committed
    at a complete-candidate boundary.
  lifetime: One cancelled Learning call.
  mutability: immutable
  mutation_authority: []
  consumers:
  - learning_qualification
  - studio_application
  references:
  - qualification-result
  fields:
  - name: result
    type: QualificationResult
    role: domain-value
    meaning: Completed candidates and deterministic diagnostic subset available when
      cancellation was observed.
- id: profile-export-request
  owner: profile_export
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/profile_export/model.py
    symbol: ProfileExportRequest
    kind: class
  visibility: cross-module
  semantic_kind: command
  description: Qualified semantic profile and requested header output options.
  lifetime: One export operation.
  mutability: immutable
  mutation_authority: []
  consumers:
  - studio_application
  - profile_export
  references: []
  fields:
  - name: profile
    type: object
    role: domain-value
    meaning: Application-mapped qualified detector profile.
  - name: language
    type: str
    role: policy
    meaning: C99 or C++17 output target.
- id: activity-kind
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: ActivityKind
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Stable explicit and derived annotation labels.
  lifetime: Process lifetime.
  mutability: immutable
  mutation_authority: []
  consumers:
  - studio_application
  - data_workspace
  references: []
  fields: []
- id: annotation-interval
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: AnnotationInterval
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: One half-open explicit or derived sample interval.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: &id001 []
  consumers: &id002
  - studio_application
  - data_workspace
  references: &id003
  - activity-kind
  fields: &id004
  - name: kind
    type: ActivityKind
    role: domain-value
    meaning: Explicit or derived activity class.
  - name: start_index
    type: int
    role: domain-value
    meaning: Inclusive start sample index.
  - name: end_index
    type: int
    role: domain-value
    meaning: Exclusive end sample index.
  - name: reason
    type: optional str
    role: metadata
    meaning: Required reason for an Ignore interval.
  - name: provisional
    type: bool
    role: contract-control
    meaning: Whether this interval is an unconfirmed template proposal.
  - name: source_recording_id
    type: optional str
    role: metadata
    meaning: Reference recording provenance for a proposal.
  - name: source_cycle_index
    type: optional int
    role: metadata
    meaning: Reference Cycle provenance for a proposal.
  - name: interval_id
    type: str
    role: domain-identity
    meaning: Stable session identity preserved while interval confirmation state changes.
- id: annotation-template-event
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: AnnotationTemplateEvent
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: One ordered Pick, Put, Fork Collision, or Ignore interval expressed
    as normalized Cycle phases.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: *id001
  consumers: *id002
  references:
  - activity-kind
  fields:
  - name: kind
    type: ActivityKind
    role: domain-value
    meaning: Explicit projected activity or exclusion class.
  - name: start_phase
    type: float
    role: domain-value
    meaning: Inclusive start position normalized to the reference Cycle.
  - name: end_phase
    type: float
    role: domain-value
    meaning: Exclusive end position normalized to the reference Cycle.
  - name: reason
    type: optional str
    role: metadata
    meaning: Required reason when kind is Ignore and absent otherwise.
- id: annotation-template
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: AnnotationTemplate
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable label phases, reference duration and cadence, Robot Speed,
    and source provenance atomically activated from one confirmed Cycle.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: *id001
  consumers: *id002
  references:
  - annotation-template-event
  fields:
  - name: robot_speed_mm_s
    type: float
    role: domain-value
    meaning: Exact Robot Speed group that may consume the template.
  - name: source_recording_id
    type: str
    role: domain-identity
    meaning: Recording that owns the reference Cycle.
  - name: source_cycle_index
    type: int
    role: domain-identity
    meaning: Ordered reference Cycle index within its recording.
  - name: reference_cycle_length_samples
    type: int
    role: domain-value
    meaning: Confirmed source Cycle duration used for generated destination Cycles.
  - name: cycle_period_samples
    type: float
    role: domain-value
    meaning: Median confirmed source Cycle start-to-start cadence.
  - name: events
    type: tuple of AnnotationTemplateEvent
    role: domain-value
    meaning: Ordered normalized event and Ignore intervals.
- id: test-condition
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: TestCondition
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Robot Speed and Collision Offset metadata for one recording.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: *id001
  consumers: *id002
  references: *id003
  fields: *id004
- id: recording
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: Recording
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: One mapped recording and its explicit annotation truth.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: *id001
  consumers: *id002
  references: *id003
  fields: *id004
- id: column-mapping
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: ColumnMapping
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Confirmed wizard mapping for one CSV or worksheet. Each IMU maps complete
    accelerometer XYZ, gyroscope XYZ, or both in that order; columns remain unique.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: *id001
  consumers: *id002
  references: *id003
  fields: *id004
- id: imported-samples
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: ImportedSamples
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Expanded semantic timestamps and six IMU axes with unchanged measured
    samples and immutable inserted-sample indexes. Repair one through three missing
    samples by time-linear interpolation, require equally divided periods within two
    percent of the inferred nominal period, and reject a recording with four missing
    samples or misalignment.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: *id001
  consumers:
  - studio_application
  - data_workspace
  - tabular_adapter
  references: []
  fields:
  - name: time_s
    type: array
    role: domain-value
    meaning: Expanded chronological timestamps retaining measured endpoints.
  - name: internal_imu
    type: array
    role: domain-value
    meaning: Measured and time-linearly interpolated Internal axes.
  - name: external_imu
    type: array
    role: domain-value
    meaning: Measured and time-linearly interpolated External axes.
  - name: inferred_sample_rate_hz
    type: float
    role: domain-value
    meaning: Nominal rate inferred before repair.
  - name: discontinuity_before
    type: array
    role: metadata
    meaning: Accepted repaired recordings contain no acquisition reset markers.
  - name: warnings
    type: tuple of str
    role: metadata
    meaning: Import diagnostics including repair counts.
  - name: interpolated_indices
    type: tuple of int
    role: metadata
    meaning: Ordered unique inserted row indexes distinct from measured samples.
- id: waveform-viewport-projection
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/model.py
    symbol: WaveformViewportProjection
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable pixel-bounded projection of one original three-axis waveform
    viewport, using raw values or deterministic Min/Max and arithmetic-mean buckets
    shared across both IMUs.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: *id001
  consumers:
  - studio_application
  references: []
  fields:
  - name: mode
    type: str
    role: policy
    meaning: Exact raw or envelope renderer mode selected from visible sample count
      and plot width.
  - name: positions
    type: tuple of float
    role: domain-value
    meaning: Viewport-local horizontal positions for raw samples or bucket centers.
  - name: minimums
    type: tuple of tuple of float
    role: domain-value
    meaning: Three channel minima; equal to raw values in raw mode.
  - name: maximums
    type: tuple of tuple of float
    role: domain-value
    meaning: Three channel maxima; equal to minimums in raw mode.
  - name: means
    type: tuple of tuple of float
    role: domain-value
    meaning: Three channel arithmetic means; equal to raw values in raw mode.
  - name: sample_start
    type: int
    role: metadata
    meaning: Inclusive original sample index covered by the projection.
  - name: sample_end
    type: int
    role: metadata
    meaning: Exclusive original sample index covered by the projection.
- id: workspace-service
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/service.py
    symbol: WorkspaceService
    kind: class
  visibility: module-public
  semantic_kind: domain-value
  description: Public workspace validation, same-speed annotation-template projection,
    and Normal Motion derivation seam.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: *id001
  consumers: *id002
  references: *id003
  fields: *id004
- id: workspace-command-port
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/contracts.py
    symbol: WorkspaceCommandPort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Demand-owned workspace command protocol.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: *id001
  consumers: *id002
  references: *id003
  fields: *id004
- id: tabular-input-port
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/contracts.py
    symbol: TabularInputPort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Demand-owned tabular input protocol.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: *id001
  consumers:
  - data_workspace
  - tabular_adapter
  references: *id003
  fields: *id004
- id: workspace-event-port
  owner: data_workspace
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/data_workspace/contracts.py
    symbol: WorkspaceEventPort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Workspace snapshot event protocol.
  lifetime: One in-memory application session.
  mutability: immutable
  mutation_authority: *id001
  consumers: *id002
  references: *id003
  fields: *id004
- id: history-spec
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: HistorySpec
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Deduplicated tap count with ordered requested-history aliases.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: &id005 []
  consumers: &id006
  - studio_application
  - learning_qualification
  references: &id007
  - single-imu-settings
  fields: &id008 []
- id: candidate-plan
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: CandidatePlan
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable model-rule plan; threshold values and total detector candidate
    count remain unknown until frozen-model scoring.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: history-job
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: HistoryJob
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable dataset, fallback state, target type, and one requested History
    assigned to one worker.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - history_worker_adapter
  references: *id007
  fields: *id008
- id: history-execution-error
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: HistoryExecutionError
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Base typed terminal failure for one History execution batch.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - studio_application
  - learning_qualification
  - history_worker_adapter
  references: *id007
  fields: *id008
- id: hardware-memory-insufficient-error
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: HardwareMemoryInsufficientError
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Terminal insufficient-hardware-memory outcome that forbids retry and
    cancels all workers.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - studio_application
  - learning_qualification
  - history_worker_adapter
  references:
  - history-execution-error
  fields: *id008
- id: insufficient-training-evidence
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: InsufficientTrainingEvidence
    kind: class
  visibility: module-public
  semantic_kind: domain-value
  description: Typed evidence shortage raised only for absent fit samples, insufficient
    Cycle groups, or unsupported FIR windows; never for numerical execution failures.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  references: *id007
  fields: *id008
- id: history-job-result
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: HistoryJobResult
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable ordered candidates, worker timing, and optional explicit
    unavailable reason returned for one requested History. Reasons distinguish Training
    shortage, missing round search evidence, and empty per-model threshold bounds;
    unclassified emptiness remains an execution failure.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - history_worker_adapter
  references: *id007
  fields: *id008
- id: history-batch-result
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: HistoryBatchResult
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Ordered four-History results and aggregate launch-memory and Peak RSS
    evidence.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - history_worker_adapter
  references: *id007
  fields: *id008
- id: history-attempt-timing
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: HistoryAttemptTiming
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable requested History, one-based attempt, and elapsed seconds
    shown in Training evidence.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - studio_application
  - learning_qualification
  - history_worker_adapter
  references: *id007
  fields: *id008
- id: history-worker-progress
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: HistoryWorkerProgress
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Bounded History, attempt, stage, fraction, and elapsed-time observation
    without process handles.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - studio_application
  - learning_qualification
  - history_worker_adapter
  references: *id007
  fields: *id008
- id: fir-matrix-evidence
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: FirMatrixEvidence
    kind: class
  visibility: private
  semantic_kind: domain-value
  description: Worker-local immutable FIR features, targets, and source row indexes
    reusable across model rules.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  references: *id007
  fields: *id008
- id: history-fold-evidence
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: HistoryFoldEvidence
    kind: class
  visibility: private
  semantic_kind: domain-value
  description: Worker-local training and per-condition held-out FIR matrices for one
    grouped fold.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  references: *id007
  fields: *id008
- id: learning-log-evidence
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: LearningLogEvidence
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Typed parameter-search, rounded round-final, admitted fold-kernel,
    fallback, or terminal evidence for the session execution log.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  references:
  - parameter-point
  fields:
  - name: kind
    type: str
    role: domain-value
    meaning: Stable evidence category interpreted by the application presentation
      mapper.
  - name: parameter
    type: optional ParameterPoint
    role: domain-value
    meaning: Exact tap
    Ridge alpha: null
    and Robust K identity when applicable.: null
  - name: parameter_loss
    type: optional float
    role: domain-value
    meaning: Raw or half-up rounded parameter selection Loss according to the evidence
      kind.
  - name: previous_parameter_loss
    type: optional float
    role: domain-value
    meaning: Previous raw best Loss used to calculate relative improvement.
  - name: fold_index
    type: optional int
    role: domain-identity
    meaning: Admitted original fold identity when reporting Kernel Loss.
  - name: kernel_loss
    type: optional float
    role: domain-value
    meaning: Original fold Kernel Loss.
  - name: validation_pass
    type: optional bool
    role: contract-control
    meaning: Per-condition Validation allowance verdict for the fold.
  - name: validation_outcomes
    type: tuple
    role: domain-value
    meaning: Ordered Robot Speed
    Collision Offset: null
    and Validation-allowance verdict tuples without MSE payloads.: null
  - name: evaluated_count
    type: int
    role: metadata
    meaning: Completed effective parameter evaluations or admitted Qualification kernels
      according to the evidence kind.
  - name: pending_count
    type: int
    role: metadata
    meaning: Remaining fold jobs or admitted Qualification kernels according to the
      evidence kind.
  - name: disposition
    type: str
    role: contract-control
    meaning: Fixed-grid CV-selected or CV-rejected outcome when every evaluated point
      is reported.
  - name: reason
    type: str
    role: metadata
    meaning: Stable explanation for the fixed-grid CV disposition.
- id: learning-progress
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: LearningProgress
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable stage, fallback-round, and bounded-work progress snapshot
    emitted during one run, with an optional unavailable reason for proven insufficient
    Training evidence.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references:
  - learning-log-evidence
  fields:
  - name: log_evidence
    type: optional LearningLogEvidence
    role: metadata
    meaning: Structured Loss or lifecycle evidence for the session-only execution
      log.
  - name: evaluated_count
    type: optional int
    role: metadata
    meaning: Completed parameter evaluations or admitted Qualification kernels for
      applicable progress entries.
  - name: pending_count
    type: optional int
    role: metadata
    meaning: Remaining fold jobs or admitted Qualification kernels for applicable
      progress entries; total work is completed plus remaining.
- id: learning-interval
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: LearningInterval
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Learning-owned sample-index evidence interval mapped from confirmed
    annotation truth.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: learning-recording
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: LearningRecording
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Framework-free immutable arrays, condition metadata, and evidence spans
    for one recording.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: learning-dataset
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: LearningDataset
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Complete application-mapped dataset accepted by one Learning run.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: fit-evidence
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: FitEvidence
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Pooled Cycle-contained Normal Robot Motion, Robot Pick, and Robot Put
    arrays with excluded gaps represented as distinct segment identities for one fallback
    state.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: cycle-fold-group
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: CycleFoldGroup
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable recording, condition, and Cycle identity used as the minimum
    cross-validation group.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: cross-validation-fold
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: CrossValidationFold
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: One deterministic held-out set of complete Cycle groups.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: cross-validation-plan
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: CrossValidationPlan
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Three-to-five-fold grouped plan covering every active Cycle exactly
    once as held-out evidence.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: cross-validated-model
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: CrossValidatedModel
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Selected model rules, grouped-fold losses, and final all-active-evidence
    FIR fit for one history.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: detector-config
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: DetectorConfig
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Frozen target-type detector configuration.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: detector-trace
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: DetectorTrace
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Per-sample replay score, state, ratio, and trigger evidence.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: replay-evidence
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: ReplayEvidence
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Full-resolution synchronized target-numeric FIR prediction, residual,
    detector trace, trigger, and selected event latency evidence for one retained
    candidate and recording.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references:
  - detector-trace
  - qualified-candidate
  - learning-recording
  fields: *id008
- id: recording-qualification
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: RecordingQualification
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Exact per-recording activity evidence, false events, collision detections,
    worst latency, chronological per-Collision Detector Score SNR, and status used
    by one retained candidate's condition aggregation; absent Normal, Pick, or Put
    activity is neutral while Collision evidence is mandatory.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  references:
  - collision-qualification
  fields:
  - name: recording_id
    type: str
    role: domain-identity
    meaning: Supplied recording identity.
  - name: robot_speed_mm_s
    type: float
    role: domain-value
    meaning: Recording Robot Speed.
  - name: collision_offset_mm
    type: float
    role: domain-value
    meaning: Recording Collision Offset.
  - name: normal_false_events
    type: int
    role: domain-value
    meaning: False triggers classified as Normal.
  - name: pick_false_events
    type: int
    role: domain-value
    meaning: False triggers classified as Pick.
  - name: put_false_events
    type: int
    role: domain-value
    meaning: False triggers classified as Put.
  - name: collision_detected_count
    type: int
    role: domain-value
    meaning: Collision intervals detected within the governed deadline.
  - name: collision_interval_count
    type: int
    role: domain-value
    meaning: Supplied Collision interval denominator.
  - name: worst_collision_latency_ms
    type: optional float
    role: domain-value
    meaning: Worst finite detected Collision latency.
  - name: status
    type: str
    role: contract-control
    meaning: PASS when present non-Collision activity has no false trigger and every
      mandatory Collision is detected within 150 ms; FAIL for contradictory evidence;
      COVERAGE_GAP when no Collision interval exists.
  - name: collision_snrs_db
    type: tuple of optional float
    role: domain-value
    meaning: Chronologically ordered per-Collision Detector Score SNR in dB; unavailable
      entries are None and an empty tuple means no Collision interval.
  - name: collisions
    type: tuple of CollisionQualification
    role: domain-value
    meaning: Complete chronological collision decisions, empty for legacy unavailable
      details.
  - name: false_trigger_robustness_margin
    type: optional float
    role: domain-value
    meaning: Finite recording false-trigger margin, or unavailable.
  - name: collision_detection_robustness_margin
    type: optional float
    role: domain-value
    meaning: Finite recording collision margin, or unavailable.
- id: qualified-candidate
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: QualifiedCandidate
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Frozen model and detector identity, grouped cross-validation provenance
    and losses, fallback-round provenance, ranking margins, all-supplied misjudgment
    and collision-detection totals, per-offset evidence, and observed qualified suffix
    for one retained round winner.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references:
  - recording-qualification
  fields:
  - name: recording_qualifications
    type: tuple of RecordingQualification
    role: domain-value
    meaning: Ordered exact per-recording Qualification results from the completed
      detector configuration.
  - name: qualification_policy
    type: str
    role: metadata
    meaning: Actual event policy at computation; empty for historical missing provenance.
  - name: qualification_input_sha256
    type: optional str
    role: metadata
    meaning: Immutable identity of the original Qualification, retained independently
      of mutable current export eligibility.
  - name: qualification_profile_sha256
    type: optional str
    role: metadata
    meaning: Immutable identity of the original Qualification, retained independently
      of mutable current export eligibility.
- id: condition-qualification
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: ConditionQualification
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Exact activity denominators, false events, collision detections, latency,
    and status for one supplied speed and offset tuple.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: offset-qualification
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: OffsetQualification
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable all-speed qualification evidence for one collision offset.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: fallback-state
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: FallbackState
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable active offsets, excluded offsets, and current fitting speed
    interval.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: fallback-action
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: FallbackAction
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Explicit stop, offset-exclusion, speed-reduction, or exhaustion decision.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: fallback-transition
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: FallbackTransition
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Selected round winner and deterministic next fallback state.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: frozen-fir-model
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: FrozenFirModel
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Source-scale MIMO FIR with three or six matched input/output channels
    and frozen residual normalization. Selected signal identities remain in the application
    mapping contract.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: learning-service
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/service.py
    symbol: LearningService
    kind: class
  visibility: module-public
  semantic_kind: domain-value
  description: Public learning, replay, fallback, and ranking seam.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: learning-command-port
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: LearningCommandPort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Demand-owned learning command protocol.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: learning-event-port
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: LearningEventPort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Learning progress and completion event protocol.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers: *id006
  references: *id007
  fields: *id008
- id: history-execution-port
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: HistoryExecutionPort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Demand-owned protocol for fixed-four History execution and typed lifecycle
    evidence.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - history_worker_adapter
  references: *id007
  fields: *id008
- id: replay-csv-file-port
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: ReplayCsvFilePort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Demand-owned protocol for one atomic full-resolution Replay CSV write.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - desktop_adapter
  references: *id007
  fields: *id008
- id: model-text-file-port
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: ModelTextFilePort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Demand-owned protocol for one atomic deterministic Model TXT write.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - desktop_adapter
  references: *id007
  fields: *id008
- id: training-mode
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: TrainingMode
    kind: enum
  visibility: cross-module
  semantic_kind: domain-value
  description: Stable fixed-grid or optimized linear Training dispatch identity.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references: []
  fields: []
  values:
  - fixed_grid
  - optimized
- id: learning-settings
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: LearningSettings
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Captured Training mode, fixed-grid selections, common grouped-CV controls,
    and optimized-only Robust and convergence controls.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - training-mode
  fields:
  - name: n_fold
    type: int
    role: configuration
    meaning: Complete-Cycle grouped fold count from two through ten.
  - name: include_training_mse
    type: bool
    role: policy
    meaning: Whether Parameter and Kernel Loss equally combine Training and Validation
      MSE.
  - name: use_robust_refit
    type: bool
    role: policy
    meaning: Optimized-only Robust refit switch; fixed-grid execution always disables
      it.
  - name: convergence_tolerance_percent
    type: float
    role: configuration
    meaning: Optimized-only fine-search relative improvement tolerance.
  - name: validation_allowance_percent
    type: float
    role: configuration
    meaning: Shared per-condition Validation MSE allowance before fold selection.
  - name: training_mode
    type: TrainingMode
    role: policy
    meaning: Fixed-grid or optimized candidate-source selection.
  - name: fixed_history_ms
    type: tuple of int
    role: configuration
    meaning: Ordered checked subset of the six fixed-grid History values.
  - name: fixed_ridge_alphas
    type: tuple of float
    role: configuration
    meaning: Ordered checked subset of the five fixed-grid Ridge alpha values.
- id: parameter-point
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: ParameterPoint
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Exact effective alpha, taps and enabled integer K identity.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references: []
  fields: *id008
- id: condition-loss
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: ConditionLoss
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Separate raw Training and Validation XYZ MSE for one active condition.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references: []
  fields: *id008
- id: fold-job
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: FoldJob
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: One parameter configuration by one fold, with centrally assigned complete
    Cycles.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - parameter-point
  - learning-settings
  - cycle-fold-group
  fields: *id008
- id: fold-result
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: FoldResult
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: One original fold kernel, condition errors or explicit numerical invalidity.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - parameter-point
  - condition-loss
  - frozen-fir-model
  fields: *id008
- id: parameter-result
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: ParameterResult
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Complete N-fold results and their max-condition mean selection Loss.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - parameter-point
  - fold-result
  fields: *id008
- id: kernel-training-evidence
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: KernelTrainingEvidence
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Original fold identity, captured settings, per-condition errors and
    parameter/kernel Loss.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - learning-settings
  - condition-loss
  - cross-validation-plan
  fields: *id008
- id: round-provenance
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: RoundProvenance
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Actual seed and Cycle fold map for one active fallback scope.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - cross-validation-plan
  fields: *id008
- id: run-provenance
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: RunProvenance
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Captured settings, fresh run seed and actual per-round evidence maps.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - learning-settings
  - round-provenance
  fields: *id008
- id: fold-memory-estimate
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/memory.py
    symbol: FoldMemoryEstimate
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable fold-specific allocation counts, phase components and estimated
    peak.
  lifetime: One admission decision.
  mutability: immutable
  mutation_authority: []
  consumers:
  - learning_qualification
  - history_worker_adapter
  references: []
  fields: []
- id: evidence-row-counts
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/memory.py
    symbol: EvidenceRowCounts
    kind: class
  visibility: private
  semantic_kind: domain-value
  description: Selected, feature-valid and common-history row counts without feature
    allocation.
  lifetime: One evidence count.
  mutability: immutable
  mutation_authority: []
  consumers:
  - learning_qualification
  references: []
  fields: []
- id: execution-batch
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: ExecutionBatch
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Ordered immutable job outcomes, process resource measurements and bounded
    admission diagnostics.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - fold-result
  fields: *id008
- id: recording-job
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: RecordingJob
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: One complete recording score or detector replay job without time slicing.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - learning-recording
  - frozen-fir-model
  - detector-config
  fields: *id008
- id: recording-result
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: RecordingResult
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Complete-recording scores or qualification metrics returned to coordinator.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references: []
  fields: *id008
- id: candidate-numerical-error
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: CandidateNumericalError
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Narrow expected invalid candidate; never source, worker or memory failure.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references: []
  fields: *id008
- id: cycle-allocation-error
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: CycleAllocationError
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Terminal Cycle count/allocation preflight failure; no scientific fallback.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references: []
  fields: *id008
- id: learning-execution-port
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/contracts.py
    symbol: LearningExecutionPort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Demand-owned bounded candidate-fold and complete-recording batch execution.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: *id005
  consumers:
  - learning_qualification
  - history_worker_adapter
  references:
  - fold-job
  - recording-job
  - execution-batch
  fields: *id008
- id: condition-coverage
  owner: profile_export
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/profile_export/model.py
    symbol: ConditionCoverage
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Exact supplied tuple denominators stored in the selected Profile.
  lifetime: Selected Profile lifetime.
  mutability: immutable
  mutation_authority: &id009 []
  consumers: &id010
  - studio_application
  - profile_export
  references: &id011 []
  fields: &id012 []
- id: semantic-profile
  owner: profile_export
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/profile_export/model.py
    symbol: SemanticProfile
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Complete immutable qualified Profile, including grouped Training provenance,
    shared by desktop result views and both header generators.
  lifetime: Selected Profile lifetime.
  mutability: immutable
  mutation_authority: *id009
  consumers: *id010
  references: *id011
  fields: *id012
- id: profile-header-artifact
  owner: profile_export
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/profile_export/model.py
    symbol: ProfileHeaderArtifact
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Deterministic default filename, semantic hash, and rendered header
    text for one kernel.
  lifetime: Selected Profile lifetime.
  mutability: immutable
  mutation_authority: *id009
  consumers: *id010
  references: *id011
  fields: *id012
- id: profile-export-service
  owner: profile_export
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/profile_export/service.py
    symbol: ProfileExportService
    kind: class
  visibility: module-public
  semantic_kind: domain-value
  description: Pure deterministic C99, C++17 and version-1 JSON rendering; JSON preserves
    numeric type and rejects non-single-sample detector semantics.
  lifetime: Selected Profile lifetime.
  mutability: immutable
  mutation_authority: *id009
  consumers: *id010
  references: *id011
  fields: *id012
- id: profile-command-port
  owner: profile_export
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/profile_export/contracts.py
    symbol: ProfileCommandPort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Demand-owned profile render protocol.
  lifetime: Selected Profile lifetime.
  mutability: immutable
  mutation_authority: *id009
  consumers: *id010
  references: *id011
  fields: *id012
- id: profile-file-port
  owner: profile_export
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/profile_export/contracts.py
    symbol: ProfileFilePort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Demand-owned approved file output protocol.
  lifetime: Selected Profile lifetime.
  mutability: immutable
  mutation_authority: *id009
  consumers:
  - profile_export
  - desktop_adapter
  references: *id011
  fields: *id012
- id: profile-event-port
  owner: profile_export
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/profile_export/contracts.py
    symbol: ProfileEventPort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Successful export event protocol.
  lifetime: Selected Profile lifetime.
  mutability: immutable
  mutation_authority: *id009
  consumers: *id010
  references: *id011
  fields: *id012
- id: project-source-reference
  owner: project_session
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/project_session/model.py
    symbol: ProjectSourceReference
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: External recording path, worksheet, byte size, and SHA-256 identity
    persisted in .dicsproj.
  lifetime: Active project and save/open transaction.
  mutability: immutable
  mutation_authority: &id013 []
  consumers: &id014
  - studio_application
  - project_session
  - desktop_adapter
  references: &id016 []
  fields: &id015 []
- id: project-document
  owner: project_session
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/project_session/model.py
    symbol: ProjectDocument
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Complete immutable project schema root with recordings, templates,
    UI selection, and optional completed Profile results.
  lifetime: Active project and save/open transaction.
  mutability: immutable
  mutation_authority: *id013
  consumers: *id014
  references:
  - project-source-reference
  fields: *id015
- id: project-session-service
  owner: project_session
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/project_session/service.py
    symbol: ProjectSessionService
    kind: class
  visibility: module-public
  semantic_kind: domain-value
  description: Public semantic validation and source-integrity seam for project save/open.
  lifetime: Active project and save/open transaction.
  mutability: immutable
  mutation_authority: *id013
  consumers: *id014
  references: *id016
  fields: *id015
- id: project-file-port
  owner: project_session
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/project_session/contracts.py
    symbol: ProjectFilePort
    kind: class
  visibility: cross-module
  semantic_kind: port
  description: Demand-owned strict project JSON and source-hash persistence protocol.
  lifetime: Active project and save/open transaction.
  mutability: immutable
  mutation_authority: *id013
  consumers:
  - project_session
  - project_file_adapter
  references: *id016
  fields: *id015
- id: project-source-missing
  owner: studio_application
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/controller.py
    symbol: _ProjectSourceMissing
    kind: class
  visibility: private
  semantic_kind: composition-mapping
  description: Transaction-local signal identifying the next unavailable recording
    source during project restoration.
  lifetime: Active project and save/open transaction.
  mutability: owner-mutable
  mutation_authority:
  - studio_application
  consumers:
  - studio_application
  references: *id016
  fields: *id015
- id: tabular-reader
  owner: tabular_adapter
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/tabular/reader.py
    symbol: TabularReader
    kind: class
  visibility: module-public
  semantic_kind: adapter-binding
  description: CSV and XLSX implementation of the tabular input port.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - tabular_adapter
  consumers:
  - studio_application
  - tabular_adapter
  references:
  - tabular-input-port
  fields: &id017 []
- id: process-diagnostics
  owner: desktop_adapter
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/diagnostics.py
    symbol: ProcessDiagnostics
    kind: class
  visibility: module-public
  semantic_kind: adapter-binding
  description: Thread-serialized rotating log, clean-shutdown marker, faulthandler
    sink, and Qt/Python exception-handler implementation of the application diagnostics
    port.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - desktop_adapter
  consumers:
  - studio_application
  - desktop_adapter
  references:
  - diagnostics-port
  - diagnostic-status
  fields: *id017
- id: waveform-item
  owner: desktop_adapter
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/waveform_item.py
    symbol: WaveformItem
    kind: class
  visibility: module-public
  semantic_kind: adapter-binding
  description: Qt Quick Scene Graph waveform texture item with viewport-aware channel
    rendering and channel, viewport, and geometry-change invalidation.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - desktop_adapter
  consumers:
  - studio_application
  - desktop_adapter
  references: []
  fields: *id017
- id: padded-button
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/PaddedButton.qml
    symbol: PaddedButton
    kind: class
  visibility: module-public
  semantic_kind: adapter-binding
  description: Shared Qt Quick button whose dimensions are governed by centralized
    design tokens.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - desktop_adapter
  consumers:
  - desktop_adapter
  references: []
  fields: *id017
- id: atomic-profile-writer
  owner: desktop_adapter
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/profile_writer.py
    symbol: AtomicProfileWriter
    kind: class
  visibility: module-public
  semantic_kind: adapter-binding
  description: Atomic per-artifact implementation of the approved profile file output
    port.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - desktop_adapter
  consumers:
  - studio_application
  - desktop_adapter
  references:
  - profile-file-port
  - profile-header-artifact
  fields: *id017
- id: atomic-replay-csv-writer
  owner: desktop_adapter
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/replay_writer.py
    symbol: AtomicReplayCsvWriter
    kind: class
  visibility: module-public
  semantic_kind: adapter-binding
  description: Atomic streaming implementation of the Learning-owned Replay CSV file
    output port.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - desktop_adapter
  consumers:
  - studio_application
  - desktop_adapter
  references:
  - replay-csv-file-port
  - replay-evidence
  fields: *id017
- id: atomic-model-text-writer
  owner: desktop_adapter
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/replay_writer.py
    symbol: AtomicModelTextWriter
    kind: class
  visibility: module-public
  semantic_kind: adapter-binding
  description: Atomic streaming implementation of the Learning-owned Model TXT file
    output port.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - desktop_adapter
  consumers:
  - studio_application
  - desktop_adapter
  references:
  - model-text-file-port
  - qualified-candidate
  fields: *id017
- id: atomic-project-store
  owner: project_file_adapter
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/project_store.py
    symbol: AtomicProjectStore
    kind: class
  visibility: module-public
  semantic_kind: adapter-binding
  description: Strict duplicate-rejecting JSON parser, deterministic atomic writer,
    and SHA-256 source identity adapter.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - project_file_adapter
  consumers:
  - studio_application
  - project_file_adapter
  references:
  - project-file-port
  fields: *id017
- id: spawn-history-executor
  owner: history_worker_adapter
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/parallel/history_workers.py
    symbol: SpawnHistoryExecutor
    kind: class
  visibility: module-public
  semantic_kind: adapter-binding
  description: Windows spawn implementation of the fixed-four History execution port
    with typed retry, cancellation, and process-tree RSS policy.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - history_worker_adapter
  consumers:
  - studio_application
  - history_worker_adapter
  references:
  - history-execution-port
  - history-job
  - history-job-result
  - history-batch-result
  - history-worker-progress
  fields: *id017
- id: worker-attempt
  owner: history_worker_adapter
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/parallel/history_workers.py
    symbol: _WorkerAttempt
    kind: class
  visibility: private
  semantic_kind: adapter-binding
  description: Adapter-private mutable process, IPC connection, attempt number, and
    start clock for one History attempt.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - history_worker_adapter
  consumers:
  - history_worker_adapter
  references: []
  fields: *id017
- id: studio-controller
  owner: studio_application
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/controller.py
    symbol: StudioController
    kind: class
  visibility: module-public
  semantic_kind: composition-mapping
  description: Application-owned QML facade and sibling-domain mapper, including direct
    session reset and Open project replacement, collision-free post-open manual annotation
    identity allocation, synchronized reference-selection state, the bounded session-only
    Training log, restored frozen-Profile replay reconstruction, discrete active/excluded
    speed provenance, and semantically distinct per-recording Replay result projection.
    Owns session-local deployment evidence/bindings, worker handle, epoch/cancellation
    and frozen profile identity. Application actions invalidate current evidence;
    actual export recomputes complete input identities.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - studio_application
  consumers:
  - studio_application
  references:
  - single-imu-settings
  - filter-stage-spec
  - filter-design
  - frozen-self-imu-model
  - deployment-qualification
  fields: *id017
- id: learning-worker-signals
  owner: studio_application
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/controller.py
    symbol: _LearningWorkerSignals
    kind: class
  visibility: module-public
  semantic_kind: composition-mapping
  description: Private queued Qt signal bridge for immutable Learning progress, completion,
    and cancelled partial-result handoff. Also carries frozen deployment requalification
    on the existing desktop worker execution path.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - studio_application
  consumers:
  - studio_application
  references:
  - learning-progress
  - qualification-result
  - deployment-qualification
  fields: *id017
- id: learning-worker
  owner: studio_application
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/controller.py
    symbol: LearningWorker
    kind: class
  visibility: module-public
  semantic_kind: composition-mapping
  description: One Qt thread worker that invokes the framework-free Learning command
    and emits immutable progress, completion, or cancelled partial-result values.
    Also carries frozen deployment requalification on the existing desktop worker
    execution path.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - studio_application
  consumers:
  - studio_application
  references:
  - learning-request
  - learning-progress
  - qualification-result
  - learning-cancelled
  - deployment-qualification
  fields: *id017
- id: replay-csv-export-signals
  owner: studio_application
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/controller.py
    symbol: _ReplayCsvExportSignals
    kind: class
  visibility: private
  semantic_kind: composition-mapping
  description: Private queued Qt completion and failure signal bridge for one Replay
    CSV export.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - studio_application
  consumers:
  - studio_application
  references: []
  fields: *id017
- id: replay-csv-export-worker
  owner: studio_application
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/controller.py
    symbol: _ReplayCsvExportWorker
    kind: class
  visibility: private
  semantic_kind: composition-mapping
  description: Private QRunnable that computes one immutable ReplayEvidence from a
    snapshotted selection, streams it as CSV, and invokes atomic output away from
    the UI thread.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - studio_application
  consumers:
  - studio_application
  references:
  - replay-evidence
  - replay-csv-file-port
  fields: *id017
- id: model-text-export-signals
  owner: studio_application
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/controller.py
    symbol: _ModelTextExportSignals
    kind: class
  visibility: private
  semantic_kind: composition-mapping
  description: Private queued Qt completion and failure signal bridge for one Model
    TXT export.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - studio_application
  consumers:
  - studio_application
  references: []
  fields: *id017
- id: model-text-export-worker
  owner: studio_application
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/controller.py
    symbol: _ModelTextExportWorker
    kind: class
  visibility: private
  semantic_kind: composition-mapping
  description: Private QRunnable that renders one snapshotted candidate as deterministic
    Model TXT and invokes atomic output away from the UI thread.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - studio_application
  consumers:
  - studio_application
  references:
  - qualified-candidate
  - model-text-file-port
  fields: *id017
- id: spawn-learning-executor
  owner: history_worker_adapter
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/parallel/learning_workers.py
    symbol: SpawnLearningExecutor
    kind: class
  visibility: module-public
  semantic_kind: adapter-binding
  description: Bounded Windows spawn batch execution with eight fold jobs or four
    whole-recording jobs, zero retries.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - history_worker_adapter
  consumers:
  - studio_application
  - history_worker_adapter
  references:
  - learning-execution-port
  - fold-job
  - recording-job
  - execution-batch
  fields: []
- id: frozen-mlp-model
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: FrozenMlpModel
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Frozen arbitrary-depth ReLU MLP layer arrays and residual normalization,
    in selected numeric precision.
  lifetime: One learning run.
  mutability: immutable
  mutation_authority: []
  consumers:
  - studio_application
  - learning_qualification
  references: []
  fields: []
- id: filter-stage-spec
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/preprocessing.py
    symbol: FilterStageSpec
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Learning-owned immutable filter edges and attenuation ratios; SPEC-0036
    adds explicit lowpass with one passband and stopband edge using the existing Butterworth
    design and stored coefficient contract.
  lifetime: Captured configuration/model or owner service lifetime.
  mutability: immutable
  mutation_authority: []
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references: []
  fields: []
- id: filter-design
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/preprocessing.py
    symbol: FilterDesign
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Single-IMU FilterDesign owned by Learning; SPEC-0030 defines behavior
    and persistence.
  lifetime: Captured configuration/model or owner service lifetime.
  mutability: immutable
  mutation_authority: []
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - filter-stage-spec
  fields: []
- id: single-imu-settings
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/preprocessing.py
    symbol: SingleImuSettings
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Single-IMU SingleImuSettings owned by Learning; SPEC-0030 defines behavior
    and persistence.
  lifetime: Captured configuration/model or owner service lifetime.
  mutability: immutable
  mutation_authority: []
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - filter-design
  fields: []
- id: frozen-self-imu-model
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/self_imu.py
    symbol: FrozenSelfImuModel
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Single-IMU FrozenSelfImuModel owned by Learning; SPEC-0030 defines
    behavior and persistence.
  lifetime: Captured configuration/model or owner service lifetime.
  mutability: immutable
  mutation_authority: []
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - frozen-fir-model
  - single-imu-settings
  fields: []
- id: self-imu-learning-service
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/self_imu.py
    symbol: SelfImuLearningService
    kind: class
  visibility: module-public
  semantic_kind: domain-value
  description: Single-IMU SelfImuLearningService owned by Learning; SPEC-0030 defines
    behavior and persistence.
  lifetime: Captured configuration/model or owner service lifetime.
  mutability: owner-mutable
  mutation_authority:
  - learning_qualification
  consumers:
  - learning_qualification
  - studio_application
  - history_worker_adapter
  references:
  - learning-service
  fields: []
- id: sensor-mapping
  owner: desktop_adapter
  language: qml
  declaration:
    path: src/dual_imu_collision_studio/qml/SensorMapping.qml
    symbol: SensorMapping
    kind: class
  visibility: module-public
  semantic_kind: adapter-binding
  description: Per-IMU raw/filtered column mapping and adopted filter design view;
    no algorithm choice.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - desktop_adapter
  consumers:
  - desktop_adapter
  references: []
  fields: []
- id: deployment-qualification
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/deployment.py
    symbol: DeploymentQualification
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Separate immutable fixed-policy deployment evidence bound to frozen
    model, source, threshold, required coverage and validation version.
  lifetime: One application session until input invalidation.
  mutability: immutable
  mutation_authority: []
  consumers:
  - learning_qualification
  - studio_application
  references:
  - qualified-candidate
  fields:
  - name: input_sha256
    type: str
    role: domain-identity
    meaning: Complete frozen deployment input identity.
  - name: policy
    type: str
    role: contract-control
    meaning: Fixed common event policy and validation version.
  - name: result
    type: QualifiedCandidate
    role: domain-value
    meaning: New policy recording/condition evidence, without rewriting historical
      results.
  - name: passed
    type: bool
    role: contract-control
    meaning: Original supplied qualified coverage passes existing acceptance.
  - name: reason
    type: str
    role: domain-value
    meaning: Failure or acceptance explanation.
- id: json-export-signals
  owner: studio_application
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/controller.py
    symbol: _JsonExportSignals
    kind: class
  visibility: private
  semantic_kind: composition-mapping
  description: Private queued completion result for one asynchronous JSON export.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - studio_application
  consumers:
  - studio_application
  references: []
  fields: []
- id: json-export-worker
  owner: studio_application
  language: python
  declaration:
    path: src/dual_imu_collision_studio/adapters/desktop/controller.py
    symbol: _JsonExportWorker
    kind: class
  visibility: private
  semantic_kind: composition-mapping
  description: Private composition QRunnable for snapshotted JSON generation and atomic
    file commit off the UI thread.
  lifetime: Application session.
  mutability: owner-mutable
  mutation_authority:
  - studio_application
  consumers:
  - studio_application
  references: []
  fields: []
- id: collision-qualification
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/model.py
    symbol: CollisionQualification
    kind: class
  visibility: cross-module
  semantic_kind: domain-value
  description: Immutable per-collision evidence captured during the existing Qualification
    pass; no score or detector-state arrays.
  lifetime: Retained result and persisted restoration.
  mutability: immutable
  mutation_authority: []
  consumers:
  - learning_qualification
  - studio_application
  references: []
  fields:
  - name: recording_id
    type: str
    role: domain-identity
    meaning: Recording identity.
  - name: collision_index
    type: int
    role: domain-value
    meaning: Zero-based chronological collision ordinal.
  - name: start_index
    type: int
    role: domain-value
    meaning: Inclusive annotated onset sample.
  - name: end_index
    type: int
    role: domain-value
    meaning: Exclusive annotated end sample.
  - name: detected
    type: bool
    role: domain-value
    meaning: Existing Qualification decision in the inclusive 150 ms window.
  - name: trigger_index
    type: optional int
    role: domain-value
    meaning: First eligible trigger, or unavailable.
  - name: trigger_time_s
    type: optional float
    role: domain-value
    meaning: Original timestamp at the trigger, or unavailable.
  - name: latency_ms
    type: optional float
    role: domain-value
    meaning: Original onset-to-trigger latency, or unavailable.
  - name: robustness_margin
    type: optional float
    role: domain-value
    meaning: Trigger score minus threshold, or unavailable.
  - name: snr_db
    type: optional float
    role: domain-value
    meaning: Original Detector Score SNR, or unavailable.
  - name: detection_reason
    type: str
    role: domain-value
    meaning: Empty when detected; otherwise why evidence did not detect.
  - name: snr_unavailable_reason
    type: str
    role: domain-value
    meaning: Empty when SNR exists; otherwise its immutable reason.
- id: fir-feature-rows
  owner: learning_qualification
  language: python
  declaration:
    path: src/dual_imu_collision_studio/domain/learning/service.py
    symbol: _FirFeatureRows
    kind: class
  visibility: private
  semantic_kind: private-helper
  description: Owner-private borrowed immutable FIR samples with valid source row indexes; materializes requested blocks only.
  lifetime: One Learning fitting or prediction matrix; never retained in a frozen model.
  mutability: immutable
  mutation_authority: []
  consumers:
  - learning_qualification
  references: []
  fields:
  - name: _internal
    type: ndarray
    role: domain-value
    meaning: Read-only borrowed source samples; owner retains their lifetime.
  - name: _indexes
    type: ndarray
    role: domain-value
    meaning: Ordered eligible source indexes owned by this matrix or selection.
  - name: _taps
    type: int
    role: configuration
    meaning: Existing positive selected lag depth.
  - name: shape
    type: tuple
    role: metadata
    meaning: Logical row count and channel-major lag width; not a dense allocation.
```
