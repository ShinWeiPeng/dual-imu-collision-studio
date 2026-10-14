# SPEC-0041 implementation verification

Scope: Accelerometer/Gyroscope checkbox mapping, 3/6-channel joint training and one collision detector, session-only exact mapping-name recall. Canonical requirements: [SPEC-0041](../specs/SPEC-0041-accelerometer-gyroscope-joint-training.md).

Implementation preserves separate IMU/signal/raw-filtered roles and the fixed ax,ay,az,gx,gy,gz selected order. Missing selected groups and mixed source identities are rejected. Each signal group is preprocessed separately; warmup eligibility reaches self-IMU history. Model weights fold Training-only normalization into native-unit parameters; mixed-unit joint model selection uses Training-only scales. Legacy three-channel loss and frozen replay arithmetic remain compatible.

Project storage preserves selected channels, source choices and preprocessing. JSON schema 2 and gyro TXT schema 2 identify Gyroscope-only and joint models. JSON records the captured source and preprocessing; legacy C-header export remains acceleration-only. Existing MLP/self-IMU standalone export restrictions remain; their trained parameters and replay remain available through project storage.

Session suggestions remember only successful mapping names and selections. Missing names stay blank; saved recording mappings win; failed/cancelled drafts cannot change the template. The suggestion template is not persisted.

Verification evidence is local under artifacts/tests/. The final whole-project run is [SPEC-0041-20261008-full-02](../artifacts/tests/SPEC-0041-20261008-full-02/pytest.log); its result.json and junit.xml provide the actual exit status, elapsed time and case outcomes. This note does not substitute for those results. The earlier full-01 run is retained as failure evidence for the repaired filter-adoption feedback regression.

Targeted checks passed: 43 numerical/detector/TXT regressions; 28 Mapping/source/export regressions; 4 new boundary cases including the controller JSON path; 5 Qt filter-adoption/checkbox cases after the final UI repair. Six-channel FIR/MLP/self-IMU batch and frozen project replay passed.

Both development and release architecture gates returned VERIFIED/PASS, with the existing SHOULD SYM004 desktop analyzer warning. Formatter check passed for all 17 touched/new Python files. Standards and Spec reviewers' concrete findings were repaired and rechecked.

Formal managed acceptance is not claimed. The complete operation reported compatibility requires diagnosis: the layout assessment has pre-existing root-level tests, historical outputs and run metadata violations. The new studio_application tests' missing layout classification has been repaired. The canonical SPEC remains confirmed until required formal acceptance evidence and layout checks pass. No ADR was accepted and no Git commit was made.
