# Algorithm inventory

| Product feature | Owner module | Screening | Record |
|---|---|---|---|
| Same-speed annotation template projection | `data_workspace` | Full record required because deterministic phase projection changes user-visible proposals. | [ALG-0001](ALG-0001-same-speed-annotation-template-projection.md) |
| Qualification replay score cache and 0.5 Threshold grid | `learning_qualification` | Full record required because Threshold search, score reuse, runtime, memory, and winner selection are user-visible algorithm behavior. | [ALG-0002](ALG-0002-qualification-replay-score-cache.md) |
| 150 ms collision qualification, diagnostic winner ranking, cancelled-run retention, and analytical Replay | `learning_qualification` | Full record required because the deadline, error metric, ranking, cancellation fallback, and FIR replay change user-visible analytical results. | [ALG-0003](ALG-0003-collision-deadline-diagnostic-replay.md) |
| Pooled Offset/speed fallback and 5-20 threshold search | `learning_qualification` | Full record required because fallback sequencing, qualified coverage ranking, and search bounds change analytical results. | [ALG-0004](ALG-0004-offset-speed-fallback-search.md) |

| Single-IMU causal filtering and Ridge self-prediction | `learning_qualification` | New source, history and preprocessing semantics. | [ALG-0009](ALG-0009-single-imu-self-prediction.md) |
| Score bounds, zero startup and repaired input | `learning_qualification` / `data_workspace` | User-visible score and sampling semantics. | [ALG-0005](ALG-0005-score-bounds-and-repaired-input.md) |
| Selectable fixed-grid or optimized FIR parameter evaluation with configurable Cycle N-folds | `learning_qualification` | Candidate generation, Loss selection, provenance and execution contracts change. | [ALG-0006](ALG-0006-fold-parameter-optimization.md) |
| Execution Log hover-controlled latest following | `desktop_adapter` | Not applicable: deterministic presentation interaction changes no scoring, search, ranking, filtering, inference, scheduling, resource policy, or analytical result. | N/A |
| Per-Collision Detector Score SNR | `learning_qualification` | Full record required because the user-visible Score peak/noise RMS calculation and unavailable-value policy produce analytical evidence. | [ALG-0007](ALG-0007-per-collision-detector-score-snr.md) |
| Viewport Min/Max waveform projection | `data_workspace` | Full record required because peak-preserving filtering and the pixel/latency budget change user-visible waveform evidence. | [ALG-0008](ALG-0008-viewport-min-max-waveform.md) |
