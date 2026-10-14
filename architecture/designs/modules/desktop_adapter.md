# desktop_adapter

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | desktop_adapter |
| version | 1 |
| kind | module |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_record:
  id: desktop_adapter
  level: L3+
  role: adapter
  implementation_status: implemented
  paths:
  - src/dual_imu_collision_studio/adapters/desktop/diagnostics.py
  - src/dual_imu_collision_studio/adapters/desktop/waveform_item.py
  - src/dual_imu_collision_studio/adapters/desktop/profile_writer.py
  - src/dual_imu_collision_studio/adapters/desktop/replay_writer.py
  - src/dual_imu_collision_studio/qml
  parent: null
  depends_on:
  - process_diagnostics
  - profile_export
  - learning_qualification
  implements_ports:
  - diagnostics.output
  - profile.file-output
  - learning.replay-file-output
  - learning.model-file-output
  description:
    purpose: Present the Qt Quick interface, execute analysis and large artifact exports
      off the UI thread, and atomically write approved header, Replay CSV, and Model
      TXT artifacts.
    input_ports: []
    output_ports: []
    emitted_events: []
    owned_state:
    - ref: recordings-viewport-before-wizard
      name: Recordings viewport before Wizard
      description: Import-page-local pixel viewport captured before Mapping Wizard
        opens and consumed only after successful completion.
    - ref: mapping-wizard-validation-error
      name: Mapping Wizard validation error
      description: Wizard-local recoverable validation feedback replaced on Next or
        Finish and cleared when relevant input changes.
    side_effects:
    - description: Read user gestures, update QML view state, schedule worker jobs,
        and write selected files.
    - description: Persist rotated privacy-bounded process, Qt/QML, and Learning diagnostic
        evidence.
    errors: []
    invariants:
    - Qt framework types never enter L1 public contracts.
    - Long analysis never runs on the UI thread.
    - Waveform scene-graph textures are invalidated when channel data, the shared
      annotation viewport, or item dimensions change.
    - Annotate and Classify renders raw polylines when visible samples fit the plot
      width and otherwise renders one thin vertical Min/Max stroke per shared sample
      bucket and channel overlaid with a continuous same-color arithmetic-mean polyline.
    - Active central-drag interval delegates stay visible until release or cancellation
      so transient endpoint binding order cannot cancel the gesture; plot clipping
      and controller boundary policy remain authoritative. Both IMU overlays share
      this rule; annotation lanes retain their existing shared gesture state and viewport
      visibility policy.
    - Shared control sizing is sourced from centralized QML design tokens.
    - Mapping Wizard validates the current step only when Next or Finish is invoked,
      keeps the active step and inputs unchanged on failure, and presents every recoverable
      configuration, mapping, source-data, or file-read error inside the active Wizard.
    - Each software-filtered IMU mapping presents one shared slot as Calculate filter,
      then Adopt design, then a non-interactive Design adopted label. Relevant edits
      reset preview and adoption; Next reports missing adoption without advancing.
      The slot uses actual control content dimensions and minimum sizes so action
      and status captions remain fully visible with scaled fonts.
    - SPEC-0036 filter editors copy all values from the same IMU most recently focused
      or edited stage; templateIndex tracks that stage through moves and resets on
      load or template deletion. High / Low pass displays the inferred direction from
      passband versus stopband edges; invalid drafts cannot be adopted. Stored designs
      retain explicit highpass or lowpass kinds.
    - SPEC-0037 remembers only the latest explicitly adopted parameter snapshot across
      IMUs and recordings for the window lifetime. Entering a sensor page prefills
      only blank/default editor values; existing drafts and saved settings win. Source
      columns, mode, coefficients and adoption are not copied; every target recalculates
      at its own sample rate. Loading and previewing do not replace the template.
    - Diagnostic persistence never contains source waveform rows, annotation payloads,
      or model coefficients.
    - Replay CSV writes use a same-folder temporary file and atomic replacement; a
      failed write preserves the previous destination.
    - Model TXT writes use a same-folder temporary file and atomic replacement; a
      failed write preserves the previous destination.
    - The Recordings ListView viewport capture is private to the QML desktop adapter,
      is overwritten on each Wizard open, and is restored only after successful Wizard
      completion with legal-range clamping.
    - Sensor mapping has independent per-IMU mutually exclusive existing-filtered/software-filtering
      options with raw bypass. Training names the three methods formally and keeps
      hover explanations available even when an algorithm is unavailable.
  entrypoints:
  - path: src/dual_imu_collision_studio/adapters/desktop/waveform_item.py
    symbol: WaveformItem
    kind: class
  public_symbols:
  - path: src/dual_imu_collision_studio/adapters/desktop/diagnostics.py
    symbol: ProcessDiagnostics
    kind: class
  - path: src/dual_imu_collision_studio/adapters/desktop/waveform_item.py
    symbol: WaveformItem
    kind: class
  - path: src/dual_imu_collision_studio/qml/PaddedButton.qml
    symbol: PaddedButton
    kind: class
  - path: src/dual_imu_collision_studio/adapters/desktop/profile_writer.py
    symbol: AtomicProfileWriter
    kind: class
  - path: src/dual_imu_collision_studio/adapters/desktop/replay_writer.py
    symbol: AtomicReplayCsvWriter
    kind: class
  - path: src/dual_imu_collision_studio/adapters/desktop/replay_writer.py
    symbol: AtomicModelTextWriter
    kind: class
```
