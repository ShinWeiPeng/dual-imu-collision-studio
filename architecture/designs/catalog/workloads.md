# CAT-workloads

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-workloads |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: workloads
value:
- id: project-io
  flow: manage-project
  steps:
  - manage-project.step-1
  timing_class: best-effort
  activation:
    kind: command
  data:
    volume: One bounded metadata/result JSON document plus sequential SHA-256 reads
      of referenced CSV/XLSX source files.
  budgets: []
- id: process-diagnostics
  flow: record-process-diagnostics
  steps:
  - record-process-diagnostics.step-1
  timing_class: best-effort
  activation:
    kind: lifecycle
  data:
    volume: One bounded metadata-only record per lifecycle, stage, progress, failure,
      or Qt/QML warning observation.
  budgets: []
- id: interactive-workspace
  flow: prepare-workspace
  steps:
  - prepare-workspace.step-1
  - prepare-workspace.step-2
  timing_class: best-effort
  activation:
    kind: command
  data:
    volume: Up to 50 recordings and 10 million total rows
    with viewport-bounded rendering.: null
  budgets:
  - metric: interaction_latency_p95
    operator: <=
    threshold: 100
    unit: ms
    method: Windows application benchmark
- id: analysis-run
  flow: learn-and-qualify
  steps:
  - learn-and-qualify.step-1
  - learn-and-qualify.step-2
  - learn-and-qualify.step-3
  timing_class: best-effort
  activation:
    kind: command
  data:
    volume: A bounded user-selected fixed grid or optimized coarse/fine candidate
      search over the validated annotated workspace, with one target-type score value
      per supplied sample cached for the active frozen model, ordered per-recording
      result metadata, and at most 10,000 session log entries.
  budgets:
  - metric: progress_interval
    operator: <=
    threshold: 500
    unit: ms
    method: worker integration test
  - metric: cancellation_observation
    operator: <=
    threshold: 2
    unit: s
    method: worker integration test
  - metric: fallback_round_elapsed
    operator: <=
    threshold: 1800
    unit: s
    method: supplied-dataset Windows process benchmark excluding a one-time retry
  - metric: system_memory_pressure_stop_fraction
    operator: <=
    threshold: 0.9
    unit: ratio
    method: Refresh total and available physical RAM at existing resource-check points;
      stop when (total - available) / total exceeds this threshold. This is sampled
      protection, not a hard allocation cap; process-tree RSS remains diagnostic.
- id: profile-write
  flow: export-profile
  steps:
  - export-profile.step-1
  timing_class: best-effort
  activation:
    kind: command
  data:
    volume: One generated header file.
  budgets: []
- id: replay-csv-write
  flow: export-replay-csv
  steps:
  - export-replay-csv.step-1
  - export-replay-csv.step-2
  - export-replay-csv.step-3
  timing_class: best-effort
  activation:
    kind: command
  data:
    volume: One selected recording with up to the governed session row limit and twenty-two
      deterministic CSV columns.
  budgets: []
- id: model-txt-write
  flow: export-model-txt
  steps:
  - export-model-txt.step-1
  - export-model-txt.step-2
  - export-model-txt.step-3
  timing_class: best-effort
  activation:
    kind: command
  data:
    volume: One selected candidate with scalar metadata, nine times tap_count FIR
      coefficients, and three three-axis vector sections.
  budgets: []
```
