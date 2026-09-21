# ALG-0009: Single-IMU causal preprocessing and Ridge self-prediction

## Metadata

- Status: proposed
- Owner: learning_qualification; desktop_adapter owns mapping interaction, data_workspace owns original samples, project_session owns inert serialization validation.
- Specification: specs/SPEC-0030-single-imu-self-prediction.md
- Execution: existing Windows desktop best-effort Learning workers and replay; no device deployment or hard real-time claim.
- Sources: domain/learning/preprocessing.py, domain/learning/self_imu.py, domain/learning/optimization.py, adapters/desktop/controller.py, qml/MappingWizard.qml.
- Tests: tests/test_single_imu_preprocessing.py plus existing workspace, Learning, project-session and QML regressions.

## Problem and selected method

One selected physical sensor supplies both past inputs and measured current targets. Reusing dual-IMU lag zero would disclose the target. Use linear VAR Ridge with lags 1..L; preserve existing fold allocation, robust refit option, Loss, candidate ranking and qualification. Nonlinear self models and deployment exports are deferred. A second physical sensor is never fabricated or required.

## Inputs, formula and boundaries

Input is finite mapped XYZ, effective sample rate, true discontinuity markers and labeled intervals. Existing short-gap interpolation is preserved with provenance. Existing filtered XYZ bypasses software filtering. Otherwise derive Butterworth high-pass, low-pass, band-pass or band-stop SOS from user edge specifications using gpass=20log10(Rp), gstop=-20log10(As). Validate Nyquist, edge nesting, finite coefficients, normalized stable sections and actual final order; band transforms have order 2N. Users preview and adopt an ordered cascade; edits invalidate adoption. Saved coefficients and designer version are retained.

Apply forward SOS with independent axis states, zero-initialized at recording start and true gaps. Cascade order is sum of stage orders, not a claim of globally minimal order or cascade band compliance. Filter arithmetic is float64; original samples are unchanged. Exclude the manually configured startup sample count, default 500, from application-filter training; already-filtered input has no such exclusion.

L=max(1,floor(history_ms*Fs/1000)). Prediction is b+sum(lag=1..L) W[lag]*a[t-lag], residual=a[t]-prediction. The shared solver receives shifted measured input and current filtered target, never recursive predictions. Training requires all inputs and target in eligible contiguous segments. Fold evaluation shares a 128 ms horizon; fitting retains candidate-specific valid rows. Measured history and filter state continue across Ignore, whose samples cannot fit or trigger. Inference resumes immediately after Ignore when history already exists.

## Calibration, numerical behavior and compatibility

Retain existing Ridge objective, numeric target replay operation order, frozen fold selection and no final all-data refit. float32/float64 model execution is explicit. Current and optimized searches use one-sensor history semantics. Project schema 2 adds an explicit self_ridge model branch, model_schema 1 and lag_start 1 plus source preprocessing configuration. Existing dual-IMU FIR/MLP branches remain unchanged. New-algorithm export controls explain desktop simulation only.

## Resource behavior and failure policy

Filtering costs O(N*S*3) for S SOS sections with O(N*3) materialization. Prediction costs O(N*9*L). Existing bounded fold-worker memory policy applies; no new thread pool is introduced. Nonfinite output or invalid design fails visibly; no automatic redesign, resampling or silently shortened history. A collision response window with no usable score has coverage gap status, never PASS. Actual-recording false-positive, miss-rate and latency acceptance remains pending user data; controlled tests establish software behavior only.


## SPEC-0036: Shared high/low-pass design

Status remains proposed. The execution instruction authorizes implementation of SPEC-0036, not ADR or algorithm-record acceptance.

The editor infers explicit highpass when fp > fs and lowpass when fp < fs from finite positive single-edge drafts. Equal/invalid edges cannot produce an adopted design. A single High / Low pass selector avoids contradictory direction and edge-order controls; separate manual direction was rejected in the confirmed scope. Existing buttord and butter with the actual btype produce the SOS design; both single-edge kinds use order N, while band transforms retain 2N. No new filter family, dependency, worker, timing budget or coefficient regeneration on reopen is introduced.

Inputs remain positive finite Hz below sampling Nyquist, Rp > 1, 0 < As < 1 and stop attenuation greater than pass attenuation. Tests independently inspect frequency response at DC, declared edges and near Nyquist. For Fs=1000, fp=50, fs=100, Rp=1.3 and As=0.3, the Butterworth order formula gives N=2, pass-edge amplitude >= 1/1.3 and stop-edge amplitude <= 0.3, with 1e-8 numerical tolerance. Tests also retain zero startup/gap reset, prefix causality and saved coefficient identity.

Parameter-template reuse is deterministic presentation state, not a numerical algorithm: copy scalar roles from the same editor's latest focused/edited stage, repair the private index on move/delete, and reset on load. No cross-IMU or persistent preference store is used. Verification seams: tests/test_lowpass_filter.py, tests/test_filter_parameter_reuse.py, tests/test_single_imu_preprocessing.py and tests/test_filter_adoption_flow.py. Full change evidence is recorded separately after tests finish.
