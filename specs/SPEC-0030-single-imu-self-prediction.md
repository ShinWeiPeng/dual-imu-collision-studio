---
spec_version: 1
spec_id: SPEC-0030
revision: 60
status: implemented
change_set: single-imu-self-prediction
---

# Single IMU self-prediction for collision detection

## Problem

The user asks to record the discussed single-IMU algorithm and continue deciding how to add it to the current project. Internal IMU is a candidate reference, not a proven physical ground truth. Single Internal and single External detection must not be excluded without comparative evidence. Existing FIR and MLP workflows predict current External XYZ from Internal XYZ including lag zero; copying that input construction for self-prediction would leak the target.

## Solution

Confirmed conceptual basis: predict measured current XYZ from strictly earlier measured XYZ of the same sensor. Measured current XYZ supplies the training target. Residual is actual minus predicted; data loss is mean squared residual over samples and three axes. The confirmed first version uses linear vector autoregressive predictors fitted with Ridge for one selected sensor XYZ per training configuration, whether sourced from an Internal or External IMU, preserving existing dual-IMU methods. Single-IMU ingestion does not require another sensor. Self-prediction MLP is excluded from this version. Self-prediction training uses filtered acceleration for both past inputs and current targets; no unfiltered comparison results are required. Mapping Wizard supports two source paths: select existing filtered XYZ columns and bypass additional filtering, or select source Accel XYZ columns for application filtering before training. The wizard maps exactly one sensor XYZ set for a single-IMU configuration. When application filtering is required, the user supplies passband/stopband edge frequencies and linear gain specifications. The application derives the required Butterworth order and design, displays the actual final filter order, and requires user adoption before using the design for training. This supersedes fixed-order selection and direct critical-cutoff entry; it is filter specification solving, not training-based parameter search. High-pass, band-pass and band-stop remain supported. Passband input is the maximum amplitude attenuation ratio R_p under REQ-011, converted to SciPy gpass in dB. Stopband input is maximum retained amplitude ratio A_s under REQ-012, converted to gstop in dB. Band modes expose four independently entered edges (passband lower/upper, stopband lower/upper) under REQ-013. Multiple filters may be applied in a user-defined ordered cascade under REQ-014; self-prediction uses the cascade final output. XYZ shares filter-chain parameters and order, while each axis maintains independent filter state under REQ-015. Cascade numerical and adoption behavior follows REQ-032.

For sensor vector a(t), a_hat(t) = b + sum(lag=1..L) W_lag a(t-lag). Residual r(t) = a(t) - a_hat(t). MSE = sum(t,axis) r_axis(t)^2 / (3*N). A Ridge optimizer may add lambda * sum_lag ||W_lag||_F^2; the exact scaling must match the selected solver contract. Training objective, model selection Loss and detector Score are separate quantities.

## User Stories

- As an analyst, I want to determine whether one IMU suffices using measured collision evidence.
- As a project user, I want a selectable self-prediction configuration whose data source and result meaning remain clear during training, replay and reopening.

## Requirements

| ID | Requirement |
|---|---|
| REQ-001 | A self-predictor shall use only past measured XYZ of the chosen sensor to predict its current measured XYZ. Current and future target samples shall never enter the input. Observed past values, not recursive predicted values, supply runtime history. |
| REQ-002 | Preserve residual = actual current XYZ minus predicted current XYZ. Distinguish sample residual from aggregate XYZ/sample MSE, optional regularized fitting objective and normalized detector Score. |
| REQ-003 | Prediction accuracy shall not establish collision detection validity. Collision claims require independent event labels, false-trigger counts, missed-event counts and detection latency, with disclosed data roles and no unsupported independent-test claim. |
| REQ-004 | Preserve the confirmed concepts and unresolved integration decisions in a working specification; existing implemented specifications are historical contracts, not silently rewritten by this discussion. |

| REQ-005 | Provide a single-IMU linear Ridge predictor that accepts one sensor XYZ set from either an Internal or External source without requiring the other sensor. These are alternative source choices, not simultaneous mandatory inputs. Preserve existing dual-IMU methods. Self-prediction MLP is outside this version. |

| REQ-006 | Self-prediction shall train on filtered acceleration XYZ: past filtered samples are inputs and the current filtered sample is the target. Residual and MSE compare actual and predicted filtered values. Do not generate an unfiltered comparison branch. Training and runtime preprocessing semantics must match; filter execution path is selected in Mapping Wizard under REQ-007; filter design follows REQ-008 through REQ-015 and REQ-032. |

| REQ-007 | Mapping Wizard shall ask whether filtered acceleration data is available. If yes, allow selection of its XYZ columns and pass the selected values into self-prediction without another filter. If no, allow selection of source Accel XYZ columns and apply application filtering before self-prediction training. Both paths supply filtered inputs and targets; neither creates an unfiltered comparison candidate. The choice applies to the one XYZ set being trained, without requiring another IMU. Filter cutoff follows REQ-008; remaining execution behavior follows REQ-032. |

| REQ-008 | The user manually supplies filter design requirements; training shall not optimize or search these requirements. Deriving a filter order and critical frequencies from the supplied requirements is allowed under REQ-010. Already-filtered source data remains exempt from application filtering. |

| REQ-009 | Application preprocessing supports Butterworth high-pass, band-pass and band-stop. Filter order is derived from user-specified passband/stopband requirements under REQ-010, not fixed to two or four. No unfiltered comparison branch or training-based filter search is generated. Gain definitions follow REQ-011/REQ-012 and four-edge band inputs follow REQ-013. |

| REQ-010 | Expose passband and stopband edge frequencies in Hz and passband/stopband gain requirements labelled linear. Compute the required Butterworth order from validated requirements and the recording sample rate, display the actual final digital filter order, and let the user adopt the design or return to editing. A design must not silently become active before adoption. Passband ratio meaning and conversion follow REQ-011. Stopband maximum amplitude ratio and dB conversion follow REQ-012. The example 900/800 Hz and 1.3/0.3 is illustrative, not a confirmed default or complete computable contract until sample rate is known; no default frequencies are inferred. |

| REQ-011 | Interpret the selected passband linear input as maximum amplitude attenuation ratio R_p relative to unity passband reference. The amplitude lower bound is 1/R_p; convert gpass = 20*log10(R_p) dB for scipy.signal.buttord. Example R_p=1.3 means amplitude at least about 0.76923 and maximum loss about 2.27887 dB, not 1.3 dB or output gain 1.3. Label the field as attenuation ratio; do not pass its linear value directly to gpass. Stopband interpretation follows REQ-012. |

| REQ-012 | Interpret stopband input A_s as maximum retained amplitude relative to the same unity reference. Convert gstop=-20*log10(A_s) dB for scipy.signal.buttord. Example A_s=0.3 means at most 30 percent amplitude and about 10.45757 dB minimum attenuation. Label this field maximum stopband amplitude ratio, distinct from passband maximum attenuation ratio R_p. Neither value is directly a SciPy dB argument. |

| REQ-013 | For band-pass and band-stop, expose four independently entered Hz fields: passband lower/upper (fp1, fp2) and stopband lower/upper (fs1, fs2). Do not infer a shared transition width or require symmetric transitions. Band-pass requires 0 < fs1 < fp1 < fp2 < fs2 < sample_rate/2. Band-stop requires 0 < fp1 < fs1 < fs2 < fp2 < sample_rate/2. Invalid/nonfinite edges must not yield an adoptable design; identify the offending constraint. These are design-specification boundaries, not a substitution for the natural critical frequencies returned by the designer. |

| REQ-014 | Application preprocessing shall support an ordered cascade of multiple configured Butterworth filter stages using the supported high-pass, band-pass and band-stop designs. Apply each stage to the preceding stage output in the configured order; feed the final filtered XYZ into both self-prediction histories and targets. Preserve stage order/settings and keep training/replay processing consistent. Do not interpret the cascade as parallel candidates, an ensemble or an unfiltered comparison. Expose individual actual filter orders and the sum of configured stage orders as cascade order before adoption; do not claim global minimum order or overall band compliance from per-stage design alone. XYZ sharing follows REQ-015. Numerical/resource rejection and adoption behavior follow REQ-032. |

| REQ-015 | For one single-IMU configuration, X/Y/Z shall share one ordered filter-chain configuration: identical stage types, order, frequency/gain requirements and designed coefficients at the same recording sample rate. Each axis retains independent stage delay/state values; do not mix signals or share mutable filtering state across axes. Do not expose separate per-axis chain configuration in this version. |

| REQ-016 | When application filtering starts or restarts after a true acquisition discontinuity, establish a warmup interval. Continue updating independent axis filter states and measured history during warmup, but exclude warmup samples from Training and suppress collision triggers. Show not-ready/warmup status. Do not count unobserved warmup coverage as successful collision validation; explicitly disclose affected collision coverage. Application-filtered warmup length follows REQ-022 through REQ-025; already-filtered sources bypass this exclusion under REQ-026. Initialization and readiness follow REQ-033/034/036. |

| REQ-017 | Warmup length is specified directly by the user under REQ-022; automatic duration estimation, estimated/adopted dual values and transient-tolerance controls are removed from this version. For application-filtered sources, use the manually adopted length consistently for Training and runtime/replay warmup, subject to valid prediction History. Already-filtered sources follow REQ-026. |

| REQ-018 | After a filter design change, do not claim a previous warmup length has been validated for the changed design. Automatic re-estimation/reset-to-estimate no longer applies. Retain the currently entered manual sample count after filter edits under REQ-025; keep it editable and do not reset it to 500. |

| REQ-019 | First delivery is desktop software simulation: single-IMU wizard/import, filtering/adoption, warmup, Ridge Training, collision Qualification, result presentation, analytical Replay and project save/reopen preserving frozen configuration/results. Defer new-algorithm export features (including standalone C/C++, model artifacts and new replay CSV export work); the user explicitly says simulation only. Existing dual-IMU exports remain intact. Desktop evidence does not establish physical-device timing, memory or detection validity. |

| REQ-020 | Single-IMU Ridge Training shall offer both existing fixed-combination and optimized parameter-search modes, reusing their current parameter generation, grouped cross-validation, Loss selection, fold admission and Qualification workflow where compatible with the confirmed single-IMU contract. Adapt input construction to lags 1..L, filtered target identity and warmup/history eligibility; do not reintroduce lag-zero leakage. Filter specifications and manually adopted warmup are not searched by Training. Preserve existing dual-IMU behavior and current superseding search/selection contracts; do not revive obsolete rounded-loss or final-refit rules from historical specs. |

| REQ-021 | Within one single-IMU Training run, recordings requiring application preprocessing shall share one filter-chain design configuration: stage types/order and frequency/gain requirements. Maintain independent filter/history states for each recording and axis; never carry state between recordings. Do not permit distinct per-recording chain designs within the same run. All recordings in the same single-IMU Training run require the same effective sample rate under REQ-031. Source provenance and shared warmup scope follow REQ-033/035. |

| REQ-022 | Replace the automatic warmup-estimation proposal with direct manual warmup-length entry. Remove the 0.1% versus 1% decision and automatic estimator acceptance work. Keep startup/true-discontinuity warmup exclusion from Training and collision triggering. Input unit is samples under REQ-023; default is 500 samples under REQ-024; filter edits retain the current value under REQ-025; valid range is a positive integer under REQ-033. |

| REQ-023 | Enter manual warmup length as a sample count N. Display corresponding duration N / Fs seconds using the applicable sample rate. 500 samples at 1000 Hz displays 0.5 seconds; the 500-sample default is adopted separately under REQ-024; 1000 Hz remains illustrative. |

| REQ-024 | Prefill manual warmup length with 500 samples for a new configuration. The user can edit the value; show its duration using the applicable sample rate under REQ-023. This default is a UI starting value, not a validated guarantee of filter settling. |

| REQ-025 | After editing the filter configuration, preserve the currently entered manual warmup sample count and keep it editable. Do not reset it to 500 or estimate a replacement. Retaining the value does not certify settling for the changed filter. |

| REQ-026 | When the wizard maps already-filtered XYZ columns, do not apply an additional application warmup exclusion or use the application-filtered 500-sample setting. Continue bypassing application filtering. Require sufficient valid, strictly past measured History before producing a prediction or eligible training row; with L=32 and otherwise valid data, the first possible target is sample 33 (one-based). This choice does not establish that external preprocessing was causal or free of transients. |

| REQ-027 | Across a complete, continuous interval marked Ignore, continue application filtering and preserve its state. Suppress Training rows and collision triggering within Ignore. Do not reset or repeat filter warmup merely because Ignore ends. This does not remove startup or true-acquisition-discontinuity warmup. Continue measured inference history during Ignore and resume judgment immediately when it ends if sufficient valid history is available under REQ-028; Training input windows must still avoid excluded evidence. |

| REQ-028 | During Ignore, continue updating measured inference history as well as filter state. Once Ignore ends, resume collision judgment on the first sample with sufficient valid history, including past measurements from Ignore; do not clear history, repeat warmup or add a recovery exclusion solely due to Ignore. The user determines the Ignore interval length. Training remains separate: do not fit on targets or input windows containing Ignore samples. Actual acquisition gaps and initial insufficient-history conditions remain governed separately. |

| REQ-029 | Within one single-IMU candidate comparison, calculate validation Loss on the same eligible target sample identities across compared History lengths. Each model still uses only its own lag 1..L input window. Common eligibility must respect warmup, exclusions and required history for all compared candidates. Do not apply this comparison-only alignment as an added Replay readiness delay. Fitting-row and cross-validation/search integration follow REQ-034, preserving the existing implementation contracts. |

| REQ-030 | First-delivery acceptance uses controlled datasets and regression tests to verify the desktop software workflow. A user recording need not be specified to start or complete this software acceptance scope. Evaluate false positives, misses and latency on actual user recordings in subsequent work; software-test PASS must not be represented as validated real-recording detection performance. Preserve the existing Qualification rules and disclose data roles when actual recordings are evaluated. |

| REQ-031 | Require the same effective sample rate for all recordings entering one single-IMU Training run, including already-filtered and application-filtered sources. Validate compatibility before fitting; identify incompatible recordings and direct the user to separate Training runs. Do not introduce automatic resampling for this version. Use the common rate consistently for History time-to-sample conversion, filter design and warmup duration display. Preserve existing dual-IMU behavior. Exact comparison uses the existing effective-rate representation where possible; no new arbitrary tolerance is adopted by this user decision. |

| REQ-032 | Use causal forward-only Butterworth second-order sections (SOS), never forward/backward filtering, for application preprocessing. Design with scipy.signal.buttord and butter(output="sos"); validate finite positive Fs, legal edges, Rp > 1, 0 < As < 1, and gstop > gpass before design. Check finite coefficients and stable poles; validate stage and cascade frequency response against the displayed per-stage requirements. No arbitrary maximum stage count is introduced: reject unsupported numerical designs and report allocation failures rather than silently truncating stages/order. A draft remains inactive until adopted; editing a design invalidates adoption and prior derived results without changing raw samples. |

| REQ-033 | Initialize each application-filter stage/axis to zero delay state at the start of a recording or a true acquisition discontinuity. Warmup is a positive integer sample count, default 500, common to application-filtered recordings in a run. First N samples advance filter state but are not training targets, training history or detector input. Training resumes only with a complete eligible input/target window; Replay history readiness follows each model. Preserve the existing import policy for repairing 1..3 missing samples with provenance and rejecting larger/invalid gaps; accepted repairs remain continuous and do not trigger new warmup. Ignore behavior follows REQ-027/028 and must not be implemented by cutting/rejoining the waveform. |

| REQ-034 | For the single-IMU model define L=max(1,floor(History_ms*Fs/1000)); inputs are a[t-1] through a[t-L], effective oldest lag is 1000*L/Fs ms, and width is 3L. Deduplicate History aliases by L and show requested/effective values. Adapt the existing 128 ms common-evaluation horizon to lag 1..Lmax for both Training-MSE and Validation-MSE scoring; fitting retains each candidate own eligible rows, as in the existing optimizer. Grouped Cycle allocation, condition weighting, retained fold kernels, no final all-data refit, threshold search and fallback stay unchanged. Never combine raw Loss from different physical target identities or model families into one new ranking. |

| REQ-035 | Preserve raw mapped values and explicit single-sensor identity throughout import, annotation, Training and Replay. Single-sensor mapping accepts only the selected three distinct XYZ columns plus optional time; absent second-sensor columns are not required or synthesized as another physical measurement. Existing dual-IMU mapping and models keep their semantics. Store source mode, selected sensor/columns, filter requirements, adopted SOS and designer version/Fs, warmup count, model lag convention and frozen weights/scales in validated inert project data. New single-IMU projects/results receive explicit versioned identities; existing schema-2 projects reopen through a legacy-compatible path. Never silently read a self predictor as a legacy lag-zero FIR. Reopen uses source fingerprints and saved coefficients/model, without retraining or redesigning filters. |

| REQ-036 | Integrate self-Ridge as an explicitly selected single-sensor algorithm using the existing Ridge fixed-grid/optimized controls and downstream Qualification. Keep source role and preprocessing identity visible; do not require simultaneous internal/external models. Wizard offers existing-filtered bypass or application-filtered Accel mapping with ordered editable stages, computed final order, design adoption and manual warmup. Reuse existing detector threshold/confirmation rules; Ignore masks suppress emitted triggers while filter/measured history continue. No additional Ignore recovery wait is introduced. Disable new-algorithm C/C++, model/TXT and CSV export actions with a specific unsupported reason; retain project save/reopen and existing dual-IMU exports. |

## Decisions

| ID | Decision | Status |
|---|---|---|
| DEC-001 | Record the discussed self-prediction principle and continue discussing project integration. | Confirmed by user request. |
| DEC-002 | The measured current sample is the prediction target; residual and aggregate loss are distinct. | Confirmed discussion understanding. |
| DEC-003 | First version provides linear Ridge Internal-self and External-self configurations while preserving existing dual-IMU methods; no self-prediction MLP in this version. | Confirmed: Q-001 option 1. |

| DEC-004 | Use filtered acceleration for self-prediction training without comparing unfiltered results. Filter execution path is refined by DEC-005. | Confirmed by corrected Q-002 answer. |

| DEC-005 | Offer already-filtered column mapping and application-filtered source column mapping through the wizard. | Confirmed by combined Q-003 answer. |

| DEC-006 | Single-IMU training requires one selected XYZ set only; withdraw the simultaneous Internal/External wizard premise. | Confirmed by user correction of Q-004; refines DEC-003. |
| DEC-007 | User manually specifies filter frequency settings; no automatic cutoff search. | Confirmed by user answer. |

| DEC-008 | Select option 2 (second-order Butterworth high-pass) and extend configurable filtering to band-pass and band-stop. | Confirmed by Q-005 answer; refines DEC-004 and DEC-007. |

| DEC-009 | Replace manual/fixed filter-order selection with user-entered passband/stopband requirements, calculated order preview and explicit adoption. | Confirmed by Q-006 premise-replacing answer; supersedes fixed-order part of DEC-008 and direct-cutoff part of DEC-007. |

| DEC-010 | User identifies Python signal and selects the maximum attenuation ratio interpretation for passband 1.3. Preserve their tentative wording; stopband semantics remain unconfirmed. | Q-007 answer recorded. |

| DEC-011 | Stopband 0.3 means amplitude at most 30 percent of the unattenuated reference. | Confirmed by Q-008 answer. |

| DEC-012 | Independently enter all four passband/stopband boundaries for band-pass and band-stop. | Confirmed: Q-009 option 1. |

| DEC-013 | Support multiple filters in an ordered cascade rather than selecting exactly one preprocessing mode. | Confirmed: Q-010 option 2. |

| DEC-014 | XYZ shares the same filter-chain settings with independent axis filter states. | Confirmed: Q-011 option 1. |

| DEC-015 | Adopt a warmup interval for application filter startup/restart, excluding it from Training and collision triggering while states continue to advance. | Confirmed: Q-012 option 1. |

| DEC-016 | Estimate warmup first and permit a user-edited adopted duration after displaying the estimate. | Confirmed by Q-013 combined answer. |

| DEC-017 | A filter design change clears the previous manual warmup override and adopts the recomputed estimate; the new value remains editable. | Confirmed: Q-014 option 1. |

| DEC-018 | Deliver desktop software simulation first; defer exports for the new algorithm. | Confirmed by Q-015 option 1 plus annotation narrowing export scope. |

| DEC-019 | Retain both fixed-combination and optimized Ridge Training modes for single-IMU simulation, with existing validation/selection workflow. | Confirmed: Q-016 option 1. |

| DEC-020 | All application-filtered recordings in the same Training run share filter-chain settings with independent states. | Confirmed by latest Q-017 correction: 改1; supersedes the unpersisted answer 2. |

| DEC-021 | Use directly specified warmup length instead of automatic estimation/tolerance selection. | Confirmed by Q-018 premise replacement; supersedes DEC-016 and automatic-estimation portion of DEC-017. |

| DEC-022 | Warmup length input uses samples with a converted time display. | Confirmed by Q-019 option 1. |

| DEC-023 | Default manual warmup length to 500 editable samples. | Confirmed by Q-020 answer. |

| DEC-024 | Preserve the current manual warmup sample count after filter edits. | Confirmed by Q-021 option 1; supersedes the remaining reset behavior of DEC-017. |

| DEC-025 | Already-filtered XYZ sources need no additional warmup exclusion; valid prediction History is still required. | Confirmed by Q-022 follow-up answer: 不需要. The proposed zero-entry control was not adopted. |

| DEC-026 | Choose continued filtering and no filter warmup after Ignore. | Confirmed by Q-023 follow-up option 1; inference-history eligibility is resolved by DEC-027 and REQ-028. |

| DEC-027 | Retain inference history across Ignore and resume immediately; user chooses Ignore duration. | Confirmed by Q-024 answer. Supersedes the earlier proposed post-Ignore inference-history rebuild. |

| DEC-028 | Compare single-IMU candidate validation Loss using common eligible target samples. | Confirmed by Q-025 answer. Does not change each model input length or Replay readiness. |

| DEC-029 | Accept the desktop workflow first with controlled data and regression tests; defer real-recording detection-performance evaluation. | Confirmed by annotation selecting the revised acceptance arrangement; replaces Q-026 premise that an actual recording scope must be selected now. |

| DEC-030 | A single-IMU Training run accepts one common effective sample rate; differing rates train separately without new automatic resampling. | Confirmed by Q-027 answer. |

| DEC-031 | Reconcile implementation details against current repository contracts: causal SOS preprocessing, strict past-only rows, existing import repair and grouped-fold behavior, explicit single-sensor persistence and UI identity. | Engineering synthesis under current execution request; does not attribute new product preferences to the user. |

## Acceptance Criteria

| ID | Requirements | Criterion | Validation Method | Evidence |
|---|---|---|---|---|
| AC-001 | REQ-001 | At fixed past history, changing current/future samples cannot change the current prediction; oldest/newest input indexes match lags L and 1. | Production feature-builder and replay causal-index tests after implementation. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |
| AC-002 | REQ-002 | Known XYZ examples reproduce residual and MSE; reported data loss is distinct from regularization and Score. | Hand-calculated fixture and fit/replay parity checks. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |
| AC-003 | REQ-003 | Reports distinguish regression evidence from labelled collision evidence and document model/threshold selection exposure. | Validation report audit on selected recording partitions. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |
| AC-004 | REQ-004 | Working document preserves discussed principles, proposed choices and open decisions distinctly. | Working-spec lifecycle validation. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-005 | REQ-005 | A recording with only one mapped XYZ set can train a linear Ridge model regardless of Internal/External source; no self-prediction MLP is offered; existing dual-IMU methods remain available. | Configuration dispatch, source-identity and existing-workflow regression checks. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-006 | REQ-006 | Past input and current target use the same specified filtered signal; residual and MSE refer to filtered units; no unfiltered comparison candidates appear. | Feature/target fixtures and training/replay preprocessing parity after filter contract is finalized. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-007 | REQ-007 | Already-filtered selected XYZ bypasses application filtering; source Accel selected XYZ is filtered before training. Verify selected-column identity and prevent automatic double filtering. | Wizard branch, column mapping and training pipeline integration fixtures after filter definition. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-008 | REQ-008 | Manual cutoff is used for application preprocessing without adding cutoff search candidates; already-filtered input bypasses filtering. | Wizard capture and preprocessing dispatch checks. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-009 | REQ-009 | Supported modes use requirement-derived actual final order, including band transformations; no fixed-order constraint, automatic training search or unfiltered comparison branch remains. | Design fixtures and mode-dispatch checks after gain definitions are finalized. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-010 | REQ-010 | Valid design requirements produce a reviewable final-order result; declining adoption does not activate it. Test edge validity versus sample rate and gain conversion only after exact gain semantics are settled. | Designer reference fixtures and wizard adoption/state tests. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-011 | REQ-011 | Passband ratio 1.3 converts to amplitude bound 1/1.3 and gpass=20*log10(1.3); the UI labels distinguish ratio and dB. | Numeric conversion fixture and UI label check. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-012 | REQ-012 | Stopband amplitude ratio 0.3 maps to gstop=-20*log10(0.3); paired with R_p=1.3, conversion gives approximately 10.45757 and 2.27887 dB respectively. Labels distinguish the two ratio meanings. | Numeric conversion and UI label fixtures. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-013 | REQ-013 | Four fields preserve asymmetric transition widths and map to the correct wp/ws arrays. Reject wrong nesting, equal edges, nonfinite/nonpositive frequencies and Nyquist violations before adoption. | Wizard and designer-boundary fixtures for both modes and multiple sample rates. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-014 | REQ-014 | A configured multi-stage cascade feeds each preceding output into the next stage and the final output into self-prediction. Training/replay reproduce the configured sequence; displayed aggregate order equals the stage-order sum, without claiming global response compliance. | Reference sequential filtering, configuration round-trip and training/replay parity fixtures. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-015 | REQ-015 | One chain setting configures all three axes; modifying one axis input leaves other-axis preprocessed outputs unchanged. Persist one shared configuration and reproduce three independent filtered streams in replay. | Configuration capture/round-trip and axis-isolation filtering tests. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-016 | REQ-016 | Startup and true-discontinuity restart advance filter/history state but produce no training rows or triggers within the configured warmup interval; UI shows not-ready and validation does not silently convert warmup collisions into passes. | Startup/restart integration fixtures after duration/readiness details are resolved. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-017 | REQ-017 | Only the manual warmup control is offered; no estimated duration or tolerance controls remain. Persist and use the adopted length consistently. | UI/configuration and Training/Replay eligibility fixtures. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-018 | REQ-018 | Filter edits do not trigger automatic warmup estimation or imply warmup validation. Verify the adopted value is retained under REQ-025 and remains editable. | Filter-edit settings transition fixtures. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-019 | REQ-019 | A single-sensor recording can complete the desktop workflow and save/reopen frozen settings/results; new self-prediction export is unavailable rather than mislabeled as legacy output. Existing export regressions remain intact. | Desktop end-to-end, frozen project round-trip and export availability/regression checks. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-020 | REQ-020 | Both modes dispatch through the existing search/selection/Qualification workflow using strictly past filtered inputs and eligible targets; fixed mode evaluates only selected combinations and optimized mode retains its existing generation semantics. Filter settings remain unchanged by search. | Search dispatch, no-leakage/eligibility integration and existing dual-IMU regression fixtures. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-021 | REQ-021 | A multi-recording Training request captures one common filter design. Changing data/state in one recording does not change another recording filtered outputs; incompatible per-recording designs cannot silently enter one run. | Multi-recording capture, state isolation and configuration validation fixtures. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-022 | REQ-022 | A user-provided length drives warmup without invoking an estimator; changing the adopted length changes eligibility/readiness accordingly. No 0.1%/1% selection exists; the explicitly adopted default is 500 samples under REQ-024. | Manual control and warmup integration fixtures after unit/range decisions. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-023 | REQ-023 | A 500-sample entry displays 0.5 seconds at 1000 Hz and 1 second at 500 Hz; sample count remains the configured value. | Unit conversion and UI checks. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-024 | REQ-024 | A new configuration displays 500 samples; editing this value changes adopted warmup eligibility and the duration display. The UI does not present the default as an estimated or verified settling length. | Default, edit and integration checks. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-025 | REQ-025 | Set warmup to 800 samples, change a filter edge and adopt the changed design: the setting remains 800, remains editable and is not labelled automatically validated. | Settings transition and persistence checks. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-026 | REQ-026 | With valid already-filtered data and L=32, sample 33 is eligible based on samples 1..32; no automatic 500-sample exclusion or duplicate filtering occurs. Application-filtered sources retain their configured warmup. | Source-path eligibility and preprocessing integration checks. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-027 | REQ-027 | Filtering across an Ignore label matches uninterrupted filtering of the same complete signal; ending Ignore neither resets filter state nor starts another warmup interval. No Training targets or collision triggers occur inside Ignore. | Label-mask and state-continuity integration checks; post-Ignore inference history follows REQ-028. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-028 | REQ-028 | With continuous valid samples and L=32 already available, the first target after Ignore is judged using the preceding 32 measured samples, even when they overlap Ignore. No extra warmup/history wait is inserted. The same overlap remains ineligible for fitting. | Inference continuity and separate Training eligibility fixtures. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-029 | REQ-029 | For History 32 and 64 on an already-filtered uninterrupted segment without other exclusions, both validation comparisons begin no earlier than target 65 (one-based) and use identical target identities; the shorter model reads only 32 past samples. Verify exclusions and warmup affect the common mask and Replay retains individual readiness. | Common-target mask, feature-window and Replay independence fixtures. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-030 | REQ-030 | Delivery evidence identifies controlled fixtures and regression coverage for single-sensor import, preprocessing, training, Qualification, Replay and save/reopen; includes known collision/normal cases and preserves legacy regression behavior. Report actual-recording performance as not yet evaluated without blocking this software scope on a missing user file. | Controlled end-to-end fixtures, focused numerical/eligibility tests, regression suite and evidence report audit. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-031 | REQ-031 | Same-effective-rate recordings can proceed; a mixed 1000 Hz / 500 Hz run is rejected before fitting with the incompatible recordings identified. Verify no automatic resampling occurs and existing dual-IMU workflows remain unchanged. History, filter design and warmup display consume the agreed effective rate. | Training admission, configuration propagation and regression checks. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-032 | REQ-032 | Reference SOS response, causal prefix invariance, axis isolation, multistage order, invalid edges/gains/poles and edit/adopt invalidation checks. | Focused contract/integration fixtures and controlled regression evidence. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-033 | REQ-033 | Zero-state startup and true-gap fixtures; exact N/L eligibility, continuous repaired-gap provenance, and Ignore state-continuity checks. | Focused contract/integration fixtures and controlled regression evidence. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-034 | REQ-034 | Hand-calculated lag-index fixtures, alias deduplication, per-candidate fitting versus common evaluation identities, frozen-fold/no-refit and old-family regression tests. | Focused contract/integration fixtures and controlled regression evidence. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-035 | REQ-035 | Three-column CSV/XLSX import, source identity and raw-value preservation, schema-2 legacy reopen, single-model save/reopen prediction equality, incompatible schema/shape/fingerprint rejection. | Focused contract/integration fixtures and controlled regression evidence. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

| AC-036 | REQ-036 | Controlled desktop workflow from wizard through training, Qualification, Replay and project reopen; both Ridge modes, masked Ignore triggers, explicit result identity and export availability regressions. | Focused contract/integration fixtures and controlled regression evidence. | PASS — docs/validation/SPEC-0030-validation.md acceptance mapping; 497-test final regression, focused numerical checks and reviewed desktop/process evidence. |

## Relationships

- refines: specs/SPEC-0001-dual-imu-collision-studio-ui.md (additive self-prediction semantics; existing cross-sensor behavior preserved).
- depends_on: specs/SPEC-0025-small-mlp-no-psram.md (current model-family context, not automatic adoption of MLP for self-prediction).
- conflicts_with: None in confirmed conceptual requirements; future schema and fold-policy changes require reconciliation.
- supersedes: DEC-009 replaces the fixed-order portion of DEC-008 and direct-cutoff portion of DEC-007 within this working change set; historical discussion remains preserved.
- DEC-003 refines REQ-005; AC-005 validates REQ-005.
- DEC-004 refines REQ-006; AC-006 validates REQ-006.
- DEC-005 refines REQ-006 through REQ-007; AC-007 validates REQ-007.
- DEC-006 refines DEC-003, REQ-005 and REQ-007; DEC-007 defines REQ-008, validated by AC-008.
- DEC-008 refines DEC-004 and DEC-007 through REQ-009; AC-009 validates REQ-009.

- DEC-009 defines REQ-010 and refines REQ-008/REQ-009; AC-010 validates REQ-010.

- DEC-010 refines REQ-010 through REQ-011; AC-011 validates REQ-011.

- DEC-011 defines REQ-012 and refines REQ-010/REQ-011; AC-012 validates REQ-012.

- DEC-012 defines REQ-013 and refines REQ-009/REQ-010; AC-013 validates REQ-013.

- DEC-013 defines REQ-014 and refines REQ-009/REQ-010; AC-014 validates REQ-014.

- DEC-014 defines REQ-015 and refines REQ-014; AC-015 validates REQ-015.

- DEC-015 defines REQ-016; AC-016 validates REQ-016.

- DEC-016 defines REQ-017 and refines REQ-016; AC-017 validates REQ-017.

- DEC-017 defines REQ-018 and refines REQ-017; AC-018 validates REQ-018.

- DEC-018 defines REQ-019; AC-019 validates REQ-019.

- DEC-019 defines REQ-020; AC-020 validates REQ-020.

- DEC-020 defines REQ-021 and refines REQ-014/REQ-015; AC-021 validates REQ-021.

- DEC-021 supersedes DEC-016 and the automatic-estimation portion of DEC-017; REQ-022 revises REQ-017/REQ-018 with AC-017/AC-018/AC-022.

- DEC-029 resolves OD-007 through REQ-030 and AC-030; real-recording performance evaluation is deferred.

## Out of Scope

Automatic warmup estimation and its transient tolerance selection are removed by DEC-021; historical discussion records remain unchanged.

New single-IMU export artifacts and physical-device delivery are deferred under REQ-019; project save/reopen is retained as desktop persistence, not a deployment export.

This turn changes specification documents only. No product implementation or hardware validity claim is made. Reverse cross-sensor prediction, high-pass-only baselines and self-prediction MLP are discussed possibilities, not accepted scope.

## Open Decisions

None.

## Integration Considerations

REQ-007 adds application preprocessing beyond the existing mapping pass-through invariant. Preserve mapped source values and distinguish derived training signals; exact module ownership and mappings require the architecture design gate before source edits. No architecture artifact is changed by this specification update.

Read-only evidence: domain/learning/service.py constructs input with range(tap_count) and replays internal[index-lag]; it names replay columns actual_external_imu and fir_predicted_external_imu. SPEC-0025 defines FIR and MLP as families with independent fold allocations and retained frozen models. Prediction configuration must be distinguished from model family; labels and serialized provenance cannot silently keep External meaning for Internal-self output.

Candidate reuse: Ridge fitting, residual normalization, scalar Score and confirmation/re-arm algorithms. Required impact audit: learning request and frozen-model identity; history feature construction and fold eligibility; qualification and fallback scope; replay evidence; Learning Settings and result labels; project save/reopen; worker cache keys and memory estimates; TXT/CSV/C/C++ export availability and semantics. These are proposed impact areas, not approved named types or architecture edits.

Verification considerations: compare against previous-sample prediction; evaluate false triggers and missed collisions at agreed latency; keep all fitting statistics training-only; include timestamp boundaries and numeric precision. A linear self-predictor produces a prediction-error filter and may not outperform high-pass. Past collision samples can reduce subsequent residual even with frozen weights, making onset detection and confirmation duration consequential. Training excludes collisions but that does not guarantee collision sensitivity.


### Implementation design and repository evidence

The current importer requires six columns (`domain/data_workspace/model.py` ColumnMapping/HeaderProposal and `adapters/tabular/reader.py`), current learning matrices include lag zero (`domain/learning/service.py` _fir_rows), and `domain/learning/optimization.py` already separates candidate fitting from common Training/Validation scoring. These are the integration seams; adding a standalone estimator alone is not delivery.

- Preprocess the complete chronological selected source once per immutable recording/configuration, before constructing Cycle evidence. Keep raw arrays untouched and make the derived signal and eligibility explicit. Filtering across folds is a deterministic causal transformation with no learned parameters; fitting and residual center/scale still use only Training rows.
- Existing effective-rate validation compares recording rates to their median with 0.5% tolerance. Retain this established nominal-rate/jitter definition, report mismatches, and use one session rate for History/design. This is not permission to mix materially different rates or resample.
- Confirmed Collision annotations already remove their 150 ms response windows from derived Normal regions. Keep that exclusion in fitting; after exclusion require a full valid history window. Do not invent automatic post-Collision tail lengths: the user can extend Ignore. Actual collisions hidden by startup warmup are unavailable coverage, not successful detections.
- A positive integer warmup entry avoids adding the unadopted zero-warmup option to application filtering. Already-filtered sources bypass this control entirely. Filtered-column provenance is recorded as user-supplied; no unsupported causal/settling claim is inferred about external preprocessing.
- New model identity uses a separate self-Ridge discriminator and lag contract, not a legacy FIR weight file. Source mode and sensor role are independent of the algebraic solver. Single-sensor and dual-sensor contexts remain distinct; no joint raw-MSE ranking is added.
- Use SciPy as a new declared dependency; its numerical signal routines stay private to Learning. No new operating-system worker topology, scheduling promise, real-time deadline claim or hardware export is introduced. Existing Windows worker execution and cancellation contracts remain.

### Boundary Design Table

| Interaction | Producer | Consumer | Parent / mapping owner | Producer contract | Consumer contract | State accessed | Allowed edges | Forbidden edges |
|---|---|---|---|---|---|---|---|---|
| Confirm one XYZ source | data_workspace | studio_application | studio_application | ColumnMapping, ImportedSamples, Recording | controller snapshot | workspace recording state via commands | parent -> workspace; tabular_adapter -> workspace contracts | workspace -> Learning or UI |
| Preview/adopt filter design | learning_qualification | studio_application | studio_application | filter specification and adopted design values | wizard primitive presentation | Learning-owned design values; UI draft only | parent -> Learning | Learning -> Qt/parent |
| Prepare self-prediction request | data_workspace | learning_qualification | studio_application | committed raw Recording/mapping | LearningRecording, single-sensor settings | immutable input snapshots | parent -> both domains | workspace <-> Learning |
| Execute fold and replay | learning_qualification | history_worker_adapter | studio_application wires port | FoldJob / RecordingJob, frozen result | existing Learning execution port | per-job private buffers | worker adapter -> Learning contracts | Learning -> worker implementation |
| Save/reopen | workspace and Learning/Profile domains | project_session | studio_application | domain-owned immutable values | ProjectDocument inert data | parent mappings only | parent -> child domains | sibling-domain imports |
| Display result / guard export | learning_qualification | studio_application | studio_application | frozen self-model and Replay evidence | Qt primitive values / export availability | no shared mutable model state | parent -> Learning; existing export port | self-model mislabeled as legacy export |

### Type Ownership Matrix

| Type / change | Owner / level | Declaration | Kind, visibility and field roles | Lifetime / mutability / authority | Consumers and referenced project types | Storage impact |
|---|---|---|---|---|---|---|
| ColumnMapping, HeaderProposal, ImportedSamples, Recording | data_workspace / L1 | existing model.py | public source identity, selected axes, timestamps and provenance | immutable recording/session values | parent and tabular adapter; existing workspace types | explicit source mode and optional absent axes; legacy defaults remain dual |
| SingleImuSettings, FilterStageSpec, FilterDesign | learning_qualification / L1 | Learning model or preprocessing module | public immutable configuration/design; no SciPy object exposed | captured per run; replaced through owner API | parent, frozen-model metadata, Learning internals | source path, gain/edge requirements, SOS values, Fs/version, warmup |
| FrozenSelfImuModel | learning_qualification / L1 | Learning model.py | public frozen model with weights, biases, residual scales, lag convention and preprocessing identity | immutable selected fold lifetime | parent, worker adapter, Replay; HistorySpec/learning-owned settings | tagged self-model contract; no standalone export |
| Existing LearningRecording / FitEvidence / FirMatrixEvidence / ReplayEvidence | learning_qualification / L1 | Learning model.py | public immutable evidence with source identity and eligibility | per run/job; array mutation confined to private calculation | existing workers and parent mappings | internal evidence adaptations; stored results carry explicit target identity |
| ProjectDocument / source references | project_session / L1 | existing project model.py | inert validated storage values, no executable filters/models | detached immutable document | parent and project-file adapter only | new versioned single-IMU branch; schema-2 legacy decoding retained |
| StudioController and QML draft controls | studio_application L0 / desktop_adapter L3 | controller.py / MappingWizard.qml | controller maps domain values; UI holds user-editable draft only | UI/session; no UI ownership of filter delay state | legal child public contracts / primitive Qt values | save through existing parent-owned mappings |

### State Object Ownership Matrix

| State | Owner | Lifetime and mutation authority | Readers / boundary handling | Reset policy |
|---|---|---|---|---|
| SOS delay values per stage and axis | learning_qualification private preprocessing | recording-local calculation, Learning alone mutates | only immutable output leaves owner; no global cache | zero at start / true gap; continuous through Ignore |
| Measured prediction history | learning_qualification private inference | recording/replay-local; owner only | frozen prediction/evidence output | clear on true gap; retain through Ignore |
| Warmup counter and readiness mask | learning_qualification private preprocessing | per continuous recording segment | immutable eligibility mapped into evidence | initialize from adopted N at start/true gap |
| Fit/CV eligibility masks and feature arrays | learning_qualification private fold job | job-local, no sharing between workers | immutable job/result contracts | new job/segment; never concatenate across excluded boundaries |
| Filter-stage draft and preview | desktop_adapter; validated design owned by Learning | wizard instance; UI mutates only draft | parent maps draft to design query | edit invalidates preview/adoption; retained warmup count |
| Captured run configuration | learning_qualification | immutable run; parent passes snapshot | existing worker port and persistence mapping | next accepted run only; edits mark prior results stale |

### Actual and intended dependencies

Keep existing L0 parent mappings and L1 sibling isolation. `studio_application -> data_workspace, learning_qualification, project_session, profile_export`; `tabular_adapter -> data_workspace`; `history_worker_adapter -> learning_qualification`; existing desktop storage adapters implement their demand-side ports. The intended addition is a private Learning dependency on SciPy signal numerical functions, not a sibling or framework dependency. No new composition root or worker pool.

### Verification and delivery sequence

1. Materialize/validate this SPEC, declare all changed/new types, state and mappings in the manifest, validate the planned manifest with the design gate before editing source. Keep ADRs proposed unless separately approved.
2. Add focused numerical and source-contract fixtures, then implement single-source importer/mapping, causal preprocessing and self-model feature/replay path. Verify against direct mathematical and SciPy references, including current/future-sample non-leakage and raw-source preservation.
3. Integrate both Ridge modes/common targets, source admission, frozen results, Ignore/warmup coverage, project compatibility and wizard/result UI. Exercise controlled complete-Cycle data and legacy fixtures.
4. Run focused tests, Windows worker/persistence/UI integration where affected, full regression once after integration, formatter checks and development/release architecture gates. Render architecture views solely from the manifest. Record exact results and limitations; do not claim real-recording or hardware performance.

## Discussion Context

### DISC-001: Record algorithm understanding and begin integration discussion
- **Situation:** The user questioned the basis for Internal as reference, identified the omitted Internal-only baseline, and discussed self-prediction and loss.
- **Question:** Record the self-prediction algorithm in SPEC and continue discussing how to add it and what implementation must consider.
- **Options and tradeoffs:** Linear self-prediction can reuse regression machinery; single-sensor high-pass/statistical detection is another baseline; neither is established as superior. Broader scope increases comparison coverage and implementation cost.
- **User answer:** 我理解了，loss就是現在點跟估測現在點的差。幫我寫入SPEC，並繼續討論這個演算法要如何新增到目前專案，以及實作要考慮什麼。
- **Explicit rationale:** The user wants the understanding persisted and integration decisions discussed; no specific sensor scope or implementation authorization was stated.
- **Resulting impact:** DEC-001 and DEC-002 establish REQ-001 through REQ-004 and AC-001 through AC-004; DEC-003 remains proposed.

### DISC-002: First-version model scope
- **Situation:** Choose the first self-prediction model scope before specifying preprocessing and training integration.
- **Question:** 第一版單顆自我預測，要先支援哪個模型範圍？兩個選項都提供內部與外部各自預測，並保留既有雙 IMU 方法。
- **Options and tradeoffs:** 先做線性 Ridge（建議）：內部與外部各自使用過去 XYZ 預測現在 XYZ；較容易隔離輸入模式效應、驗證因果索引與資源需求，但不涵蓋非線性自我預測，適合先建立可信基準。 / 同時做 Ridge 與 MLP：兩顆感測器各提供兩種模型；比較範圍完整，但候選數、訓練時間、記憶體與驗證組合增加，適合第一版就需要比較非線性效果。
- **User answer:** 1
- **Explicit rationale:** No additional rationale supplied; user selected the recommended linear Ridge option.
- **Resulting impact:** DEC-003 confirmed; REQ-005 and AC-005 added; OD-001 resolved. Existing dual-IMU behavior is preserved.

### DISC-003: Filtered training without an unfiltered comparison
- **Situation:** The proposed optional high-pass comparison exceeded the requested comparison scope.
- **Question:** 第一版自我預測，程式是否額外對匯入訊號做 high-pass？來源資料本身是否已濾波，與程式額外濾波是不同事情。
- **Options and tradeoffs:** 不額外 high-pass（建議）：直接使用映射後的 XYZ，先建立自我預測基準；減少截止頻率和濾波狀態等變因，但低頻漂移需由模型處理，來源若已濾波則保留其結果。 / 新增可選 high-pass：可比較同一資料有無額外濾波的效果，但需再定義截止頻率、階數、啟動及中斷狀態，增加驗證與匯出成本；適合本階段就需要研究濾波效果。
- **User answer:** 2，但不用比較沒有高通的結果。就是詢問是否是對Accel經過高通後，在對高通後的資料進行training
- **Explicit rationale:** The user explicitly excludes comparing unfiltered results and asks to train on high-pass-filtered Accel. No cutoff, order or execution-location answer is inferred.
- **Resulting impact:** DEC-004, REQ-006 and AC-006 capture filtered-only training; OD-002 narrows to filter ownership and parameters.

### DISC-004: Wizard selects filtered source or application filtering
- **Situation:** The user wants both source paths selectable in Mapping Wizard rather than one fixed project-wide ingestion path.
- **Question:** 高通要由目前專案執行，還是要求匯入前已完成？兩者都只訓練高通後的資料，不比較未高通結果。
- **Options and tradeoffs:** 由專案執行（建議）：匯入未高通 Accel，由程式使用保存的高通設定處理後訓練與 Replay；較容易重現，但需新增濾波設定及狀態處理，已高通資料不能直接再套用。 / 匯入前完成：專案直接使用來源已高通的 Accel；程式較簡單，但來源端必須固定並記錄濾波設定，未來部署也要重現該前處理，適合既有擷取流程已提供高通資料。
- **User answer:** 在使用小精靈時，可以增加是否有高通濾波器的數據，如果有就繼續選擇欄位。沒有就使用要用哪個數據經過高通。來training。
- **Explicit rationale:** Existing high-pass data should be mapped directly; otherwise select data for application filtering before training. Per-sensor granularity and filter settings were not stated.
- **Resulting impact:** DEC-005 and REQ-007 refine REQ-006; AC-007 verifies both paths; OD-002 retains granularity and filter parameters.

### DISC-005: Correct the simultaneous-sensor premise
- **Situation:** Q-004 incorrectly assumed both IMUs must be present in a single-IMU configuration.
- **Question:** 小精靈中的「是否已有高通資料」，內部與外部 IMU 要各自設定，還是整份錄製共用一個設定？
- **Options and tradeoffs:** 各自設定（建議）：內部、外部分別選已高通欄位或原始 Accel 欄位，可處理一顆已高通而另一顆未高通的資料；多一組選擇與驗證，但資料來源較有彈性。 / 整份錄製共用：只選一次，兩顆都視為已高通或都由程式高通；操作較少，但不支援混合狀態，適合兩顆資料來源處理始終一致的情況。
- **User answer:** 在單IMU演算法怎麼會有內部跟外部同時存在的問題
- **Explicit rationale:** User rejects the simultaneous Internal/External premise for a single-IMU algorithm.
- **Resulting impact:** DEC-006 refines REQ-005 and REQ-007 and AC-005; Q-004 is withdrawn through the explicit premise correction.

### DISC-006: Manual cutoff frequency
- **Situation:** After the single-sensor correction, the assistant asked whether cutoff is manually specified or searched during training; the question was displayed without prior lifecycle persistence, which is recorded here without inventing a versioned question.
- **Question:** 程式需要執行高通時，你希望自行指定截止頻率，還是提供多個截止頻率讓訓練流程挑選？
- **Options and tradeoffs:** Manual cutoff is controlled by the user; cutoff search increases candidate and validation costs.
- **User answer:** 自行指定截止頻率
- **Explicit rationale:** No additional rationale supplied.
- **Resulting impact:** DEC-007 establishes REQ-008 and AC-008; OD-002 no longer includes cutoff search policy.

### DISC-007: Butterworth and configurable band filters
- **Situation:** User selects second-order Butterworth high-pass and expands filtering to band-pass and band-stop.
- **Question:** 由程式執行高通時，第一版採用哪一種固定階數？兩者都由你手動指定截止頻率。
- **Options and tradeoffs:** 一階高通（建議先作基準）：結構與狀態較少，容易驗證和部署，但低頻抑制較緩；適合先控制實作複雜度，若有嚴格阻帶要求可能不足。 / 二階 Butterworth 高通：低頻衰減較陡且通帶平坦，但係數、狀態與暫態驗證較多；適合需要較強低頻抑制的情況，仍須實測是否保留碰撞特徵。
- **User answer:** 2，可自訂設定band pass、band stop
- **Explicit rationale:** No further rationale supplied; customizable band-pass and band-stop are explicitly requested. Do not infer filter cascades or band-filter final order.
- **Resulting impact:** DEC-008 establishes REQ-009 and AC-009; REQ-006 through REQ-008 generalize high-pass-only wording to configurable filtering; OD-002 retains precise band semantics.

### DISC-008: Requirement-driven filter order with adoption
- **Situation:** The user replaces the fixed two/four-order choice with passband/stopband design requirements and adoption after viewing order.
- **Question:** 帶通與帶阻的階數，要採最終二階，還是最終四階？高通維持已確認的二階。
- **Options and tradeoffs:** 最終二階（建議先採用）：每軸一個二階節，與高通的階數及資源規模一致，驗證較簡單；帶外抑制較緩，適合先建立有限成本的版本。 / 最終四階：使用二階 Butterworth 原型轉換成帶通或帶阻，每軸兩個二階節，帶外抑制較陡；運算、狀態及暫態驗證增加，適合需要更強頻帶選擇性的情況。
- **User answer:** 我認為應該是可以設定
*// Enter passband edge frequency(Hz): 900*
*// Enter stopband edge frequency(Hz): 800*
*// Enter passband gain(linear): 1.3*
*// Enter stopband gain(linear): 0.3*
然後顯示率波器階數。讓使用者決定是否採用
- **Explicit rationale:** Display the calculated filter order and let the user decide whether to adopt. Linear gain definitions are not yet supplied beyond example labels/values.
- **Resulting impact:** DEC-009 establishes REQ-010 and AC-010; revises REQ-008, REQ-009 and AC-009; withdraws the fixed-order premise while retaining Butterworth and the requested modes.

### DISC-009: Passband attenuation ratio and SciPy conversion
- **Situation:** The passband value exceeds unity and cannot be blindly supplied as a linear gain to SciPy buttord, which expects dB losses.
- **Question:** 範例 passband gain(linear)=1.3 代表什麼？這會決定增益基準與階數計算；也可以直接提供你使用的定義。
- **Options and tradeoffs:** 通帶目標放大倍率 1.3：保留實際放大需求，但仍需指定通帶允許下降多少及阻帶增益基準，才能推導所需階數。 / 通帶最大衰減比 1.3：相對基準的幅度下限為 1/1.3，約 0.769；可作為通帶損失限制，但不是輸出放大 1.3 倍，介面名稱需改為衰減比。
- **User answer:** 是使用python signal的函式，應該是最大衰減比
- **Explicit rationale:** The user references Python signal and says it should mean maximum attenuation ratio. Official scipy.signal.buttord documentation defines gpass/gstop in dB; conversion is required for a linear-ratio UI. Stopband meaning is not inferred.
- **Resulting impact:** DEC-010 and REQ-011 refine REQ-010; AC-011 verifies conversion; OD-002 retains stopband interpretation.

### DISC-010: Stopband maximum retained amplitude
- **Situation:** Confirm the stopband ratio independently of the passband reciprocal attenuation ratio.
- **Question:** 阻帶的 0.3 是否指相對於未衰減基準，輸出幅度最多保留 30%？這會換算成 SciPy gstop 約 10.46 dB。
- **Options and tradeoffs:** 是，最多保留 30%（符合原本 linear 標示）：採用幅度上限 0.3，換算 gstop=-20*log10(0.3)；介面需明確區分通帶衰減比與阻帶幅度上限。 / 不是，原本指 SciPy 的 dB 參數：先重新定義數值與單位；0.3 dB 不能與目前約 2.28 dB 的通帶損失組成有效的這組設計要求。
- **User answer:** 是
- **Explicit rationale:** User confirms the annotated statement that 0.3 permits at most 30 percent output amplitude.
- **Resulting impact:** DEC-011 and REQ-012 complete stopband meaning; AC-012 validates conversion; REQ-010 and REQ-011 reference the resolved meaning.

### DISC-011: Independent band edges
- **Situation:** Band-pass and band-stop design requires both passband and stopband boundary pairs.
- **Question:** 帶通與帶阻的頻率條件，要直接輸入四個邊界，還是輸入通帶兩個邊界與共用過渡帶寬度？
- **Options and tradeoffs:** 直接輸入四個邊界（建議）：通帶下限/上限、阻帶下限/上限皆可自訂，對應 SciPy wp/ws，兩側過渡帶可不同；欄位較多且需檢查順序，適合你要的完整設計條件。 / 通帶兩個邊界加共用過渡寬度：自動推導阻帶兩個邊界，少一個欄位，但限制兩側過渡帶同寬；適合對稱需求，不適合兩側需獨立設定的資料。
- **User answer:** 1
- **Explicit rationale:** User selects four independent boundary fields; no additional rationale supplied. Frequency nesting and Nyquist checks are mathematical validity constraints of this selection.
- **Resulting impact:** DEC-012 establishes REQ-013 and AC-013; OD-002 no longer contains band-edge entry choice.

### DISC-012: Ordered filter cascade
- **Situation:** Determine whether application preprocessing can combine multiple filter designs before self-prediction.
- **Question:** 第一版前處理一次選一種濾波模式，還是支援多個濾波器串接，例如先高通再帶阻？
- **Options and tradeoffs:** 一次選一種（建議）：高通、帶通、帶阻三選一，每次只設定及採用一個設計；操作與驗證較簡單，但不能同時去除低頻及另一個獨立干擾頻帶。 / 支援串接：可依序套用多個濾波器，能組合高通與帶阻；需要設定每級條件、順序與整體響應，增加總階數、狀態及驗證成本，適合明確需要多重頻率處理的情況。
- **User answer:** 2
- **Explicit rationale:** User selected cascade support without additional rationale or a stage-count limit.
- **Resulting impact:** DEC-013 establishes REQ-014 and AC-014; OD-002 resolves mode composition and retains chain configuration details.

### DISC-013: Shared XYZ chain settings
- **Situation:** Decide whether one sensor three axes share filter configuration or need independent user settings.
- **Question:** 單顆 IMU 的 XYZ 要共用同一套濾波鏈設定，還是每軸各自設定？
- **Options and tradeoffs:** XYZ 共用設定（建議）：三軸使用相同濾波種類、順序及頻率條件，各軸保留獨立濾波狀態；設定與驗證較簡單，但無法單獨調整某一軸的干擾頻帶。 / XYZ 各自設定：每軸可有不同濾波鏈及頻率條件，能針對各軸干擾調整；增加操作、保存及驗證組合，適合已知三軸需要不同處理的資料。
- **User answer:** 1
- **Explicit rationale:** User selects shared XYZ configuration; no additional rationale supplied.
- **Resulting impact:** DEC-014 establishes REQ-015 and AC-015, refining REQ-014; OD-002 no longer contains axis configuration sharing.

### DISC-014: Warmup adoption and skill reload
- **Situation:** Filter startup transients require a policy before defining readiness and validation coverage.
- **Question:** 程式濾波器啟動或真正資料中斷後重啟時，是否設置暖機區段，暫不參與 Training 與碰撞判斷？
- **Options and tradeoffs:** 設置暖機區段（建議）：先持續更新濾波與歷史狀態，暖機段不參與訓練或觸發，畫面標示尚未就緒；降低把啟動暫態當異常的風險，但形成偵測空窗，碰撞覆蓋缺口須明確呈現。暖機長度另行定義。 / 不增加濾波暖機區段：依後續定義的初始化與預測歷史規則盡早判斷；沒有額外濾波等待時間，但需將啟動暫態造成的誤報納入驗證，不保證啟動結果可靠。
- **User answer:** 採用1。重新載入技能
- **Explicit rationale:** User adopts warmup and requests skill reload. Relevant installed 0.11.0 ask-matt, spec-governance, grilling and Decision Question Contract were reread. No duration is inferred.
- **Resulting impact:** DEC-015 establishes REQ-016 and AC-016; OD-005 retains duration, initialization/readiness and coverage detail.

### DISC-015: Estimated warmup with manual override
- **Situation:** Define how warmup duration is selected after adopting startup exclusion.
- **Question:** 暖機長度要依濾波鏈估算，還是由你手動輸入時間？兩者都要滿足預測 History 的有效資料需求。
- **Options and tradeoffs:** 依濾波鏈估算（建議）：依完整濾波鏈的暫態收斂準則計算並顯示暖機時間，修改濾波設計後重新計算；適合可變階數及串接，但需定義容許誤差與估算上限，可能得到較長等待時間。 / 手動輸入毫秒：直接控制等待時間並保存設定，實作較簡單；需要自行驗證是否足夠，太短可能殘留暫態、太長會增加偵測空窗，修改濾波設計後需重新檢查。
- **User answer:** 採用1。估算顯示後，使用者也可以自行修改
- **Explicit rationale:** User accepts calculation but explicitly permits editing the displayed estimate. Attached plugin screenshot shows version 0.12.0; filesystem confirms the release plugin is 0.12.0 while development remains 0.11.0. Release ask-matt, spec-governance, grilling, Decision Question Contract and managed-delivery contract were read; screenshot text is context, not execution authority.
- **Resulting impact:** DEC-016 establishes REQ-017 and AC-017, refining REQ-016. OD-005 retains estimator and override behavior details.

### DISC-016: Reset warmup override after filter edits
- **Situation:** A user-edited duration may become inappropriate when the filter design changes.
- **Question:** 使用者改過暖機時間後，如果又修改濾波鏈，原本的手動暖機值要如何處理？
- **Options and tradeoffs:** 重新估算並重設採用值（建議）：改動濾波設計後清除舊覆寫，採用新的估算值，使用者仍可再改；可避免舊值誤用，但要重新輸入手動調整。 / 保留手動值並顯示新估算：保留使用者設定，提示它來自舊濾波設計，要求重新確認後採用；不用重填，但需要使用者判斷舊值是否仍適合。
- **User answer:** 1
- **Explicit rationale:** User selects re-estimation and resetting the adopted value; no additional rationale supplied.
- **Resulting impact:** DEC-017 establishes REQ-018 and AC-018, refining REQ-017; filter-change override policy is resolved.

### DISC-017: Desktop simulation only
- **Situation:** Decide whether this version includes deployment export in addition to the desktop analysis workflow.
- **Question:** 單 IMU 演算法第一版，要先完成桌面端流程，還是同時提供完整 C/C++ 執行流程匯出？
- **Options and tradeoffs:** 先完成桌面端（建議）：包含小精靈、濾波鏈、暖機、Training、Qualification、Replay、CSV 與專案保存重開；先取得偵測效果證據，新增演算法的部署匯出留待下一階段，既有雙 IMU 匯出保留。 / 同時提供 C/C++ 匯出：除完整桌面流程外，匯出濾波鏈、暖機、自我預測與 detector 的一致執行流程；能較快銜接裝置，但增加數值一致性、狀態及資源驗證工作，實際裝置效能仍需另外量測。
- **User answer:** 1
- **Explicit rationale:** The same message annotates the C/C++ export discussion with: 先不用完成匯出，只要軟體模擬即可. Treat that correction as narrowing the selected option to software simulation; new export work is deferred, including CSV work in the originally broader option. Existing functionality is preserved.
- **Resulting impact:** DEC-018 establishes REQ-019 and AC-019; OD-006 resolves delivery scope and retains project persistence compatibility.

### DISC-018: Reuse both Ridge Training modes
- **Situation:** Decide which existing parameter-search modes are available for self-prediction simulation.
- **Question:** 單 IMU 的 Ridge Training 要沿用目前兩種參數搜尋模式，還是第一版只提供勾選組合？這裡搜尋的是 History 與 Ridge 參數，濾波條件仍由你指定。
- **Options and tradeoffs:** 沿用兩種模式（建議）：保留固定組合與自動最佳化，接入既有交叉驗證、Loss 選模及 Qualification；操作一致，但需要驗證兩條搜尋路徑的自我預測資料索引與暖機資格。 / 只提供固定組合：勾選 History 與 Ridge alpha 後訓練比較，保留交叉驗證與 Qualification；候選範圍易控制、整合較少，但本版不能自動探索未勾選的參數。
- **User answer:** 1
- **Explicit rationale:** User selects both existing modes; no additional rationale supplied. Existing behavior means current superseding contracts, not obsolete historical selection details.
- **Resulting impact:** DEC-019 establishes REQ-020 and AC-020; OD-003 resolves search-mode scope and retains causal eligibility/index alignment.

### DISC-019: Common preprocessing across a Training run
- **Situation:** Determine whether recordings in one Training run share preprocessing settings.
- **Question:** 多份錄製一起訓練同一個單 IMU 模型時，由程式濾波的資料要共用同一套濾波鏈設定，還是各份錄製可不同？
- **Options and tradeoffs:** 同次 Training 共用設定（建議）：各份錄製使用相同濾波種類、順序及頻率/增益條件，濾波狀態各自獨立；模型的前處理條件較清楚，但不能替單一錄製單獨調整。已有濾波資料的相容性另行定義。 / 各份錄製可不同：保留各自濾波設定後一起訓練，彈性較高；但同一模型混用不同前處理條件，須保存每份設定且不能宣稱結果對應一條通用濾波鏈，驗證與重現較複雜。
- **User answer:** 改1
- **Explicit rationale:** User first answered 2, then corrected to option 1 before any decision persistence. The latest correction controls; no per-recording-different-design requirement was committed. No additional rationale supplied.
- **Resulting impact:** DEC-020 establishes REQ-021 and AC-021; OD-002 resolves same-run design consistency while retaining already-filtered source compatibility.

### DISC-020: Direct manual warmup length
- **Situation:** Following explanations of estimator percentages versus sample counts, user replaces tolerance-based estimation with warmup-length entry.
- **Question:** 暖機估算使用的暫態殘留門檻，要先採 0.1% 還是 1%？百分比相對標準化測試暫態的最大偏差，非碰撞 Score；估算值仍可手動修改，計算方法需驗證。
- **Options and tradeoffs:** 0.1%（建議作較保守起點）：要求估算暫態殘留更小，通常需要較長暖機，減少可用資料；適合優先抑制啟動暫態，並非已驗證最適值或實際訊號穩定保證。 / 1%：允許較大的估算暫態殘留，通常可縮短暖機並保留較多資料；適合重視較短等待，但需更留意啟動後殘差及誤報。
- **User answer:** 我覺得還是採用暖機長度 好了。
- **Explicit rationale:** User prefers warmup length after discussing examples such as the first 500 samples. Do not infer that 500 is a selected default or that the manual unit is already finalized.
- **Resulting impact:** DEC-021 and REQ-022 remove automatic estimation; REQ-017/REQ-018 and AC-017/AC-018 are reconciled. AC-022 covers manual warmup and OD-005 retains unit/default/range and filter-change treatment.

### DISC-021: Warmup sample-count unit
- **Situation:** Direct manual warmup length is settled; its input unit remains open.
- **Question:** 暖機長度的輸入單位要採用哪一種？建議使用筆數，並同步顯示換算時間；例如取樣率 1000 Hz 時，500 筆就是 0.5 秒。500 只是例子，尚未設定為預設值。
- **Options and tradeoffs:** 筆數（建議）：直接設定前幾筆作為暖機，同步顯示換算時間。 / 毫秒：直接設定暖機時間，再依取樣率換算為筆數。
- **User answer:** 筆數（建議）：直接設定前幾筆作為暖機，同步顯示換算時間。
- **Explicit rationale:** User selected sample-count entry with converted time displayed; no default value was selected.
- **Resulting impact:** DEC-022, REQ-023 and AC-023 settle the unit; REQ-022 and OD-005 retain default/range and filter-change handling as open decisions.

### DISC-022: Default warmup length
- **Situation:** Sample-count input and converted time display are settled; default remains open.
- **Question:** 暖機筆數的初始欄位要如何呈現？目前沒有驗證過的通用暖機長度。
- **Options and tradeoffs:** 留白，首次訓練前必填（建議）：由使用者明確指定，儲存專案後保留設定。 / 預填 500 筆，可修改：方便開始操作，但 500 筆只是起始設定，並非已驗證足夠。
- **User answer:** 預設500筆
- **Explicit rationale:** User explicitly specified 500 samples as the default. No additional rationale was provided.
- **Resulting impact:** DEC-023, REQ-024 and AC-024 adopt the editable default; REQ-022, REQ-023, AC-022 and OD-005 are reconciled. Filter-change handling remains open.

### DISC-023: Retain warmup length after filter edits
- **Situation:** Manual warmup defaults to 500 samples; handling of an existing edited value after filter changes remains open.
- **Question:** 修改濾波器設定後，已填入的暖機筆數要如何處理？例如你已將 500 改為 800 筆，之後又改了截止頻率。
- **Options and tradeoffs:** 保留目前筆數（建議）：仍為 800 筆，可自行修改；保留不代表已驗證新濾波器的暖機需求。 / 重設為預設 500 筆：每次修改濾波器後恢復預設值，再由使用者調整。
- **User answer:** 保留目前筆數（建議）：仍為 800 筆，可自行修改；保留不代表已驗證新濾波器的暖機需求。
- **Explicit rationale:** User selected retaining the current editable count, without claiming validation for the new filter.
- **Resulting impact:** DEC-024, REQ-025 and AC-025 settle filter-edit handling; REQ-018, REQ-022, AC-018 and OD-005 are reconciled. No source code is changed.

### DISC-024: No additional warmup for already-filtered data
- **Situation:** Q-022 remained pending. The assistant subsequently proposed a shared editable 500-sample warmup with zero allowed for already-filtered data and asked whether the user accepted; that explanatory follow-up was not separately versioned.
- **Question:** 小精靈若選擇「已有濾波後的 XYZ 欄位」，還要排除開頭的暖機筆數嗎？這條路徑不會再套用軟體濾波器，但輸入檔可能保留原濾波器的啟動暫態。
- **Options and tradeoffs:** 仍套用暖機筆數（建議）：預設排除前 500 筆，可修改；兩種資料來源採一致的起始排除規則。 / 不套用暖機排除：假設輸入已去除啟動暫態，只等待足夠的預測歷史資料。
- **User answer:** 不需要
- **Explicit rationale:** User states that additional warmup is unnecessary in the immediate already-filtered-source discussion. No additional reason was supplied. The unaccepted proposal to allow zero does not determine the application-filtered valid range.
- **Resulting impact:** DEC-025, REQ-026 and AC-026 settle already-filtered warmup applicability; REQ-016 and REQ-017 are reconciled. History eligibility still applies.

### DISC-025: Continued filtering without post-Ignore warmup
- **Situation:** Q-023 remained pending while the user could not see option cards. An unversioned text follow-up offered 1) continued filtering plus rebuilding valid history, 2) reset and warmup plus history, 3) continued filtering plus an extra excluded recovery interval and history. User selected 1 and emphasized immediate subsequent judgment.
- **Question:** 遇到手動標記的 Ignore 區段時，濾波器要繼續運作嗎？這裡指資料完整、只是指定不分析的區段；真正斷訊仍依已確認規則重啟。兩個方案都排除 Ignore 的訓練與觸發，並在區段後重新累積有效預測歷史。
- **Options and tradeoffs:** 繼續濾波（建議）：保持訊號連續性；Ignore 結束後累積有效歷史即可，不因標記本身重新暖機。 / 重設濾波器：Ignore 結束後重新暖機，再累積有效歷史；避免沿用區段內濾波狀態，但排除更多資料。
- **User answer:** 1，我認為不需要對濾波器進行暖機，直接進行後續判斷即可
- **Explicit rationale:** User considers further filter warmup unnecessary and wants subsequent judgment directly. This settles no filter reset/warmup, but does not unambiguously settle whether Ignore samples may remain in inference history, since option 1 previously described rebuilding history.
- **Resulting impact:** DEC-026, REQ-027 and AC-027 confirm continued filtering without post-Ignore warmup. OD-005 retains the narrow inference-history clarification. Startup and real-gap rules remain unchanged.

### DISC-026: Immediate post-Ignore inference
- **Situation:** No filter reset or warmup after Ignore is settled; use of measured history from Ignore requires clarification.
- **Question:** 你說的「直接進行後續判斷」，是否包含保留 Ignore 期間的預測歷史，讓區段結束後第一筆就恢復碰撞判斷，不再等待新的 History 視窗？這只影響推論；訓練仍排除包含 Ignore 資料的視窗。
- **Options and tradeoffs:** 是：沿用連續的實測歷史，已有足夠歷史時立即恢復判斷。 / 否：濾波器不暖機，但仍重新累積不含 Ignore 的預測歷史。
- **User answer:** 對。我ignore會自己判斷要多長
- **Explicit rationale:** User confirms immediate inference and states that they will determine how long the Ignore interval should be.
- **Resulting impact:** DEC-027, REQ-028 and AC-028 settle inference continuity and user-controlled Ignore length; REQ-027, DEC-026, AC-027 and OD-005 are reconciled. Training still excludes Ignore-containing windows.

### DISC-027: Common validation targets for candidate comparison
- **Situation:** Different History lengths can otherwise be scored on different target samples.
- **Question:** 同一輪單 IMU 模型比較，是否採用相同的有效驗證目標樣本計算 Loss？例如比較 History 32 與 64 筆，在已濾波、無其他排除的資料段中，都從第 65 筆開始計算驗證 Loss，避免兩者因評分資料不同而難以比較。這只對齊驗證評分樣本，不讓短 History 多讀資料，也不延後 Replay 的實際可判斷時間。
- **Options and tradeoffs:** 採用（建議）：以共同有效的驗證目標樣本比較 Loss；會捨棄部分僅短 History 可評分的樣本。 / 不採用：各自使用所有有效驗證目標樣本；保留更多資料，但 Loss 的評分樣本可能不同。
- **User answer:** 採用
- **Explicit rationale:** User adopted the proposed common validation-target comparison; no further rationale was supplied.
- **Resulting impact:** DEC-028, REQ-029 and AC-029 settle validation sample alignment. OD-004 retains exact fitting/partition integration; model input lengths and Replay readiness are unchanged.

### DISC-028: Controlled-data software acceptance first
- **Situation:** Q-026 originally asked about real recording selection. The assistant clarified previous MLP acceptance evidence, then proposed controlled fixtures and regression tests first with real-recording evaluation later; this premise-replacing follow-up was not separately versioned.
- **Question:** 第一版是否先使用你現有、已標註正常動作與碰撞的資料做桌面模擬驗收？會沿用現有 Qualification 規則，記錄實際資料用途；若資料參與訓練或模型／門檻選擇，結果不標示為獨立測試。具體專案或檔案仍需指定或從工作區確認。
- **Options and tradeoffs:** 先用現有已標註資料（建議）：先完成桌面流程與結果驗收，清楚揭露資料用途。 / 先指定另一批獨立資料：作為未參與訓練及選擇的測試集，需先確認檔案及標註。
- **User answer:** 採用這個安排
- **Explicit rationale:** Annotation 1 selects the arrangement: 用受控資料與回歸測試驗證軟體流程，完成後再用你的實際資料評估誤報、漏報及延遲。這樣目前不用先指定資料檔，也不會把軟體測試通過當成實際偵測效果已達標。 No additional rationale was supplied.
- **Resulting impact:** DEC-029, REQ-030 and AC-030 settle acceptance scope and resolve OD-007. Real recordings are not a first-delivery prerequisite; remaining engineering integration items are not reopened user choices.

### DISC-029: Common effective sample rate
- **Situation:** Shared filter configuration and model History require consistent time semantics across recordings.
- **Question:** 第一版單 IMU 的同一次 Training，是否要求各錄製檔使用相同的有效取樣率？我建議先採用這個限制；遇到不同取樣率就提示分開訓練，不自動重取樣，以維持模型 History 與濾波器的時間尺度一致。
- **Options and tradeoffs:** 採用相同有效取樣率限制（建議）：不同取樣率分開訓練，第一版不新增自動重取樣。 / 需要混合取樣率訓練：需另外定義共同取樣率、重取樣與防混疊規則。
- **User answer:** 採用
- **Explicit rationale:** User adopted the proposed common-effective-rate restriction; no additional rationale was supplied.
- **Resulting impact:** DEC-030, REQ-031 and AC-031 settle single-IMU rate compatibility and the absence of new automatic resampling; REQ-021 is reconciled. No product code is changed.

### DISC-030: Execution preparation and technical reconciliation
- **Situation:** User authorizes execution after product decisions are settled. The working SPEC still contains technical items that repository facts and existing contracts can resolve.
- **Question:** No new user decision; reconcile outstanding integration details before product edits.
- **Options and tradeoffs:** Reuse the existing grouped-fold and parent-mapping workflow with an explicit self-model branch, or create a separate training stack. Reuse avoids duplicating selection/fallback while explicit lag/source identity prevents legacy ambiguity.
- **User answer:** 開始執行
- **Explicit rationale:** No additional rationale supplied. Implementation details are engineering synthesis, not new user quotations. Current turn identity was observed via the desktop task reader.
- **Resulting impact:** DEC-031 and REQ-032 through REQ-036 with AC-032 through AC-036 resolve OD-002 through OD-006. Implementation design, boundary/type/state matrices and verification seams are recorded. No architecture or product files are changed by this reconciliation.

## Routing/Gates

Spec review: PASS
Standards review: PASS
Architecture design, development and release gates: PASS. Rendered views are current; zero baseline entries. Changed Python formatter check: PASS (12 files).

Implementation is complete for desktop software simulation. Final complete regression: 497 passed in 142.20 seconds. Validation report: [SPEC-0030 validation](../docs/validation/SPEC-0030-validation.md). Real-recording detection performance is not claimed. ADRs remain proposed. No Git commit was created.

## Revision History

- Revision 1: Capture user-confirmed conceptual discussion, proposed integration path and open decisions on 2026-09-10.

- Revision 3: Confirm Q-001 option 1: both single-sensor Ridge predictors; resolve OD-001.

- Revision 5: Persist corrected Q-002 answer and continue one decision at a time.

- Revision 7: Persist wizard dual-source decision from Q-003.

- Revision 9: Reconcile single-sensor correction and manual cutoff answer; preserve the unversioned-question provenance gap.

- Revision 11: Confirm second-order Butterworth high-pass and requested band-pass/band-stop extension.

- Revision 13: Persist passband/stopband requirement design and explicit adoption; linear gain meaning remains open.

- Revision 15: Record passband attenuation ratio and explicit SciPy dB conversion; preserve pending stopband interpretation.

- Revision 17: Confirm Q-008 stopband maximum retained amplitude and conversion.

- Revision 19: Confirm four independent frequency boundaries and required band-mode validity checks.

- Revision 21: Confirm ordered multi-filter cascade and final-output self-prediction.

- Revision 23: Confirm XYZ shared ordered filter configuration and independent axis states.

- Revision 25: Confirm warmup exclusion and reread installed governance skills.

- Revision 27: Confirm estimated warmup with manual override; continue lifecycle with release skill 0.12.0.

- Revision 29: Confirm clearing manual warmup override and adopting a fresh estimate after filter changes.

- Revision 31: Reconcile desktop-only option and explicit export deferral annotation together.

- Revision 33: Confirm reuse of both existing Ridge Training modes with self-prediction eligibility adaptations.

- Revision 35: Apply latest Q-017 correction to shared same-run filter design; unpersisted option 2 is discarded.

- Revision 37: Replace automatic warmup estimation with manual length; withdraw Q-018 tolerance choice.
| 60 | 2026-09-10 | Recorded implementation PASS evidence. |
