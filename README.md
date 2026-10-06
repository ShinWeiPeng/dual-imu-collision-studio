# Dual IMU Collision Studio

Python/PySide6 desktop implementation of the confirmed workflow in
[`SPEC-0001`](specs/SPEC-0001-dual-imu-collision-studio-ui.md).

## Run on Windows

Double-click `run.bat` to check/create the environment, update dependencies when
needed, and start the application. The command window closes automatically once
this launch's main window is visible. The application runs independently: closing
the launcher console does not close the started software. Initial module loading
can take some time.

Startup progress and failures appear in the console and in the unique launcher
log printed under `build/launcher-logs/`. The accompanying `.application.log`
receives application output directly and continues recording after the launcher
exits. Logs are retained per launch and can be removed when no longer needed.
Environment failures or application exit before its main window appears keep the
command window open until a key is pressed. If readiness is not confirmed within
120 seconds, the console reports the unconfirmed process and log path; it does
not claim a crash or terminate that detached process. A first launch requires
Python 3.11 or newer on PATH. Errors occurring after successful startup remain in
the logs and existing application diagnostics; they do not reopen a console.

Run it from this repository folder and set the `src` package path first:

```powershell
$env:PYTHONPATH = (Resolve-Path "src").Path
.\.venv\Scripts\python.exe -m dual_imu_collision_studio.app
```

Alternatively, install it once with `.\.venv\Scripts\python.exe -m pip install -e .`;
after that the original command works without setting `PYTHONPATH`.

The current implementation includes:

- a five-stage Qt Quick desktop shell with centralized design tokens;
- a per-recording five-step CSV/XLSX Mapping Wizard;
- a custom `QQuickItem` Scene Graph waveform renderer;
- Cycle/event annotation presentation with derived Normal Motion semantics in the domain;
- deterministic FIR history/tap planning, source-scale MIMO Ridge fitting, exact detector confirmation/re-arm replay, and nested Offset/Speed fallback primitives;
- deterministic per-kernel C99 and C++17 header generation with Offset/speed coverage,
  latency, and robustness metadata.

The annotation screen creates validated sample-index truth with Undo/Redo, required
Ignore reasons, Time Discontinuity protection, and derived Normal Robot Motion. Training
uses configurable complete-Cycle N-fold validation (2-10, default 3). Each recording
requires at least two valid Cycles; each condition needs at least N. Each Start draws
new fold maps, saves the actual map/seed, and keeps every recording represented in
Training. Cycle-count failure stops Learning; absent common 128-ms evaluation targets
skip only that fallback round.

SPEC-0011 searches History through 128 ms and Ridge alpha continuously in [1e-6,100].
Optional Robust refit is off by default; when enabled, integer K is searched in [2,32].
The default Loss mixes Training and Validation MSE equally, averages folds per condition,
then takes the maximum condition. Turn off Include Training MSE to use Validation alone.
Coarse top-two candidates plus ties seed joint fine search. Search stops after full
minimum-step neighborhoods (one tap, one K, alpha factor 1.05) and the configured
improvement tolerance. It does not guarantee a global optimum or impose a time limit.

All best four-decimal half-up parameter ties survive. Their original fold kernels must
pass per-condition Validation allowance (default 20%); each group retains its two
lowest fold Losses plus ties. No all-data refit occurs. All selected kernels enter
Qualification and the existing offset/speed fallback; only qualified kernels export.
Next-run settings are saved separately from immutable historical training evidence.

One shared queue uses at most eight Windows spawn workers for candidate-fold fitting,
and at most four for whole-recording Qualification. Processes reuse the dataset within
a batch. Worker failure, cancellation and insufficient memory stop and clean up the
run without retries or worker-count reduction. Tests verify these functional contracts;
large-data capacity and native scheduler performance require separate runtime acceptance.

Under SPEC-0009, each frozen model's Scores determine its threshold search: N is the
maximum of Normal interval maxima; C is the maximum of Collision onset-through-150-ms
maxima. Search includes positive values in [N,C], starting at N by 0.5 and including C;
Qualification still requires every labeled Collision to be detected.
Empty ranges or missing round evidence skip their model/round and continue fallback.
FIR starts with zero history and includes startup Scores in search and Qualification.
Import repairs one through three missing samples by time-linear interpolation on all
six axes; four missing samples reject the recording. Repair markers appear in the
annotation waveforms and survive save/reopen. Ignore/Collision overlap blocks confirmation.
Both C extraction and Qualification use a fixed inclusive 150-ms deadline. Ignore
samples are excluded without extending the deadline or compressing timestamps; valid
samples after Ignore remain eligible. Actual Collision annotations still cannot
overlap Ignore. A pass under this temporary rule does not establish 20-ms compliance.
New projects use contract version 2; this change does not migrate older projects.

## Desktop MLP comparison

Train now offers independent FIR + Ridge and MLP checkboxes. MLP hidden depth is
customizable (default 2); each layer independently selects 4, 8, 16, 32, 64 or 128
neurons. Select MLP History (4/8/16/32/64/128 ms) and L2 (.0001/.001/.01).
Only the selected Cartesian combinations run. Equal tap counts are deduplicated.
FIR and MLP History selections are saved independently.

Each family independently samples complete-Cycle folds and applies its own existing
Loss/Validation selection before Qualification. Replay selects each frozen retained
kernel; there is no ensemble or all-data refit. MLP uses NumPy Adam, ReLU hidden
layers and a linear XYZ output. Training-only standardization is folded into frozen
float32/float64 parameters and checked against explicit preprocessing on validation
rows. Parameters, detector settings and original family/fold evidence survive project
save/reopen. Old FIR projects remain readable.

Replay displays family, hidden architecture, parameter count, parameter bytes and an
estimated inference buffer size. Buffer estimates cover causal history, two maximum
layer activation buffers and nine residual/score scalars; they exclude runtime,
allocator and framework overhead. These are desktop estimates, not ESP32-S3 RAM or
timing measurements. MLP deployment TXT/header export is deferred; use Save Project
for parameter preservation and Replay CSV for desktop comparison. FIR exports remain
available. Compare normal false events, missed collisions, latency and Score peaks on
your recordings before concluding that MLP improves detection.

## JSON model export

Open **Export Profile** to see every qualified kernel with Kernel ID, History/taps, threshold and qualified range. Choose **Export JSON…** on the desired row; no selection on a previous page is required. Rows that cannot preserve the JSON execution contract show a reason. The page no longer contains header-format or header-export controls.
For each selected model, edit its display name and then choose a `.json` filename in
the save dialog. The filename and embedded name are independent. Existing files require
an explicit replacement confirmation; cancellation stops the remaining export dialogs.
Each file contains one frozen model, its Internal/External XYZ input contract in `g`,
preprocessing, residual normalization, detector settings, and provenance.

JSON export preserves the qualified Float32 or Float64 type. It does not check device
RAM, tap capacity or supported device rates. A profile must already be qualified with
`1_OF_1` confirmation; multi-sample-qualified detectors are rejected with an explanation
instead of silently changing their behavior. MLP and single-IMU JSON deployment are
outside this release. Existing header and Model TXT export remain available.

This desktop export does not establish successful device import or inference parity.
The device independently validates its supported precision, dimensions and rate.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools\architecture\architecture_cli.py gate --phase development
.\.venv\Scripts\python.exe tools\architecture\architecture_cli.py gate --phase release
```

The header smoke tests compile generated C99 and C++17 fixtures with the installed
Visual C++ toolchain when available.


## Single-IMU desktop simulation

In Mapping Wizard choose Single IMU with the Internal or External source identity, then map that sensor's XYZ columns. The other sensor is not required. Choose existing filtered XYZ to bypass software filtering, or raw Accel XYZ to design an ordered Butterworth high-pass/band-pass/band-stop cascade. Enter passband/stopband edges in Hz, maximum passband attenuation ratio and maximum stopband retained amplitude. Preview actual stage/total order and cascade response, then adopt the design. Application-filter startup exclusion defaults to 500 samples and remains editable; changing filters preserves the entered count. Already-filtered input has no filter warmup exclusion.

Single-IMU Ridge predicts current filtered XYZ from measured lags 1..L. Both fixed-grid and optimized Learning are available. Ignore suppresses training/trigger evidence while filtering and measured history continue; judgment resumes immediately afterward when history is available. Results identify the source, preprocessing and startup readiness. Save/reopen the project to retain settings, frozen models and fold provenance. C/C++, model/TXT and Replay CSV export are unavailable for this algorithm in this version.

Software validation uses controlled fixtures; real-recording false-trigger, missed-event and latency performance must be evaluated separately. See [SPEC-0030](specs/SPEC-0030-single-imu-self-prediction.md).
