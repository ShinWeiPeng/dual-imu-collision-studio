# ALG-0007: Per-Collision Detector Score SNR

## Metadata

- Status: accepted
- Owner module: `learning_qualification`
- Product feature: Per-Collision SNR in Recording Qualification Results
- Flow IDs: `learn-and-qualify`
- Related ADRs: None
- Source paths: `src/dual_imu_collision_studio/domain/learning/model.py`, `src/dual_imu_collision_studio/domain/learning/service.py`, `src/dual_imu_collision_studio/adapters/desktop/controller.py`, `src/dual_imu_collision_studio/qml/Main.qml`
- Test and benchmark paths: `tests/test_candidate_qualification.py`, `tests/test_controller_export.py`, `tests/test_qml_smoke.py`
- Supersedes: None; ALG-0003 continues to own Collision deadline and detection semantics.

## Problem and observable success

Per-recording Qualification reports detection count and worst latency but not the relative strength of each Collision Score. Success means every annotated Collision produces one chronologically ordered Detector Score SNR entry, valid inputs produce the exact dB result, unavailable ratios produce `N/A`, variable event counts remain truthful, and existing Qualification decisions and exports do not change.

## Inputs, outputs, units, ranges, and data-quality assumptions

- Input Score is the existing finite non-negative detector Score array in target arithmetic for one complete recording.
- Collision truth and Ignore exclusions come from confirmed half-open annotation intervals.
- Signal amplitude is the maximum finite Score in the existing Collision onset-through-150-ms inclusive response window, stopping at an acquisition discontinuity and excluding Ignore samples.
- Noise amplitude is the RMS of finite Scores outside every annotated Collision and Ignore interval in the same recording.
- Output is one immutable tuple ordered by Collision start index. Each entry is a finite dB float or unavailable (`None` in the domain and `N/A` in the UI).

## Constraints and quantitative acceptance thresholds

- `snr_db = 20 * log10(signal_peak / noise_rms)`.
- A ratio is valid only when both amplitudes are finite and strictly positive and the result is finite.
- Zero, non-finite, empty, or unavailable signal/noise yields unavailable for that Collision. Epsilon substitution and positive/negative infinity are forbidden.
- The calculation cannot alter triggers, thresholds, confirmation state, latency, status, candidate ranking, persistence, or export.

## Candidate methods and comparative evidence

1. Detector Score peak versus non-Collision/non-Ignore Score RMS: selected by the user because it directly represents detector separability.
2. External IMU RMS versus Normal IMU RMS: rejected because gravity and ordinary robot motion can dominate and it is not the deployed detector metric.
3. Prediction-residual RMS versus Normal/Pick/Put residual RMS: rejected because it is less directly tied to threshold crossing and needs a separate pooling policy.

One combined chronological column was selected over three fixed columns or dynamic columns so every actual event remains visible without changing table structure. `N/A` was selected over infinities or epsilon clamping to avoid fabricated finite measurements and unstable special values.

## Selected method and reasons for rejecting alternatives

Compute SNR inside `learning_qualification` while the whole-recording Score trace and interval truth are already available. Store only the derived optional floats in `RecordingQualification`. This keeps analytical authority and formula tests in L1; L0 performs formatting only. Recomputing from raw recordings in L0 is rejected because it duplicates target arithmetic and leaks child-domain inputs into presentation orchestration.

## Exact behavior, formula or pseudocode, boundaries, and tie-breaking

```text
noise_samples = finite scores whose indexes are outside every
                Collision annotation and Ignore annotation
noise_rms = sqrt(mean(square(noise_samples)))

for collision in collisions sorted by (start_index, end_index):
    response = finite scores from collision onset through onset + 150 ms inclusive,
               stopping before the first acquisition discontinuity and excluding Ignore
    signal_peak = max(response), if response is non-empty
    if signal_peak > 0 and noise_rms > 0 and both are finite:
        result = 20 * log10(signal_peak / noise_rms)
        emit result only if finite
    else:
        emit unavailable
```

Equal start indexes use end index as the deterministic secondary order. No rounding changes the domain value; the controller uses the repository's existing general numeric formatting and joins values with ` / `.

## Parameters, calibration, versioning, and compatibility

There is no tunable parameter or stored calibration. The 150 ms window and Score semantics reuse ALG-0003/ALG-0005. The new field is trailing; constructors provide one entry per annotated collision, while the empty default remains valid for zero-collision recordings. Project/Profile/Replay CSV/Model TXT schemas are unchanged.

## Time and space complexity and resource budgets

For `N` samples, `C` Collision intervals, and at most `W` samples in one 150 ms window, the added work is `O(N + C*W)` time. Temporary masks are `O(N)` and the retained tuple is `O(C)`. It adds no process, Queue, serialization of waveform arrays, lock, retry, or UI-thread replay. The model-assurance verdict is `estimated`; no product performance threshold or platform-sensitive winner is asserted.

## Errors, degradation, fallback, and forbidden behavior

- No Collision intervals: retain an empty tuple; UI displays `N/A`.
- Invalid signal for one event: retain `None` only at that chronological position; valid siblings remain visible.
- Invalid shared noise: every Collision entry is `None`.
- Forbidden: epsilon, infinity, dropping extra Collisions, padding to three events, sorting by SNR, changing Qualification status, or persisting/exporting SNR outside the requested table.

## Validation cases and evidence

- Golden vector with known Score peaks and noise RMS, asserting independent literal dB values.
- Multiple Collisions supplied out of tuple order, asserting chronological result order.
- Zero, one, three, and more-than-three Collision intervals.
- Empty/zero noise and zero/unavailable signal, preserving valid sibling entries where applicable.
- Controller map asserts ` / ` formatting and per-entry `N/A`; QML asserts one header/binding and unchanged neighboring fields.
- Full regression and architecture development gate.

## Risks and monitoring

Noise taken from the same recording can vary with activity mix; the UI and record explicitly call this Detector Score SNR rather than raw-sensor SNR. The metric is diagnostic evidence only and must not silently become a qualification or ranking gate.

## Human approval

- Approved by: Hugo Peng
- Approval date: 2026-09-01
- Approval reference: `SPEC-0019` revision 4 decisions DEC-001 through DEC-003 and the user's explicit `開始執行` authorization in the current task.
