# SPEC-0029 pre-code boundary review

User authorized 開始執行. The follow-up monitoring question requests explanation;
it does not remove the confirmed admission gate or request a scheduling rewrite.

| Boundary | Producer / owner | Consumer | Mapping | Parent |
|---|---|---|---|---|
| Fold counts / byte components | learning_qualification | history_worker_adapter | Existing FoldMemoryEstimate | studio_application |
| Windows total / available | OS | history_worker_adapter | Existing local budget and runtime checks | Existing execution binding |
| Readable refusal | history_worker_adapter | Learning / desktop | Existing error string | studio_application |

| Type / state | Owner | Intended change |
|---|---|---|
| EvidenceRowCounts / FoldMemoryEstimate | Learning | No new named type or field planned |
| ExecutionBatch | Learning | Existing diagnostic tuple retained |
| Memory snapshot / summary strings | Worker adapter | Invocation-local only; readable summary added |
| Native trace / test case settings | Development runner | Bounded case-local evidence, outside release src |

Actual and intended dependencies remain Adapter -> Learning, Adapter -> Windows;
Learning -> Adapter/psutil is forbidden. No new module, port, event, callback,
cache, persisted state, or parent mapping. Training mathematics, allocation and
parallelism remain unchanged. Inspect long-History accounting and correct only
proven overlap/count errors; a valid expensive allocation is not an estimator bug.
All History contract tests and real 32 ms acceptance precede a validated claim.
64/128 ms receive native coverage only if existing RAM admission permits it.
Monitoring waits at most 20 ms between coordinator checks when idle, but process
startup/job transfer and other synchronous coordinator work can extend that gap;
90% is not an enforced OS reservation or guaranteed instantaneous hard cap.

The adapter owns readable units and shortfall presentation. Any manifest text
change remains in manifest.yaml followed by render and the single architecture
CLI gates. Existing ADRs remain proposed. No algorithm or scheduling replacement
is selected. Description changes are confined to the worker adapter in the
Learning parent view. Evolving History changes matrix width, not ownership;
another runtime requires fresh object-size and native calibration evidence.
