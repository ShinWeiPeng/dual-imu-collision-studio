# ALG-0008: Viewport Min/Max waveform projection

## Metadata

- Status: proposed
- Owner module: `data_workspace`
- Product feature: Peak-preserving Annotate & Classify waveform display
- Flow IDs: `prepare-workspace`
- Workload IDs: `interactive-workspace`
- Execution Profile IDs: `windows-desktop`
- Data Access Profile IDs: `waveform-viewport-buckets`
- Microarchitecture Profile IDs: `waveform-projection-python-numpy`
- Real-time Scheduling Study IDs: Not applicable; the workload is best-effort.
- Related ADRs: None
- Source paths: `src/dual_imu_collision_studio/domain/data_workspace/model.py`, `src/dual_imu_collision_studio/domain/data_workspace/service.py`, `src/dual_imu_collision_studio/adapters/desktop/controller.py`, `src/dual_imu_collision_studio/adapters/desktop/waveform_item.py`, `src/dual_imu_collision_studio/qml/Main.qml`
- Test and benchmark paths: `tests/test_workspace.py`, `tests/test_annotation_controller.py`, `tests/test_waveform_item.py`, `tests/test_qml_smoke.py`, `tests/benchmark_waveform_projection.py`
- Supersedes: The controller's uncatalogued uniform 800-point display sampling.

## Problem and observable success

Uniform point sampling can omit a short impact peak before the user zooms, while isolated Min/Max strokes can look discontinuous at envelope-mode zoom ratios. Success means every finite visible sample contributes to either a raw polyline or its bucket's vertical Min/Max stroke and arithmetic mean, envelope mode retains a continuous trend line, both IMUs share exact bucket boundaries, output is bounded by plot width, and annotation sample indexes do not change.

## Inputs, outputs, units, ranges, and data-quality assumptions

- Input is an `N x 3` mapped Internal or External IMU array guaranteed finite by the import contract, a finite normalized viewport `start < end`, and integer plot width `W >= 1`; the query defensively rejects non-finite values in the selected visible range without rescanning off-viewport rows.
- The viewport is clamped to `[0, 1]` then mapped to `[floor(start*N), ceil(end*N))`.
- Output contains viewport-local positions, three channel minima, maxima, arithmetic means, and the covered original half-open sample range.
- Empty arrays produce an empty raw projection. Invalid shapes, non-finite visible values, invalid viewport order, and non-positive widths are rejected; imported arrays are already finite by the workspace contract.

## Constraints and quantitative acceptance thresholds

- If visible sample count `V <= W`, output raw samples and identical minima/maxima.
- If `V > W`, output exactly `W` non-empty contiguous buckets.
- Internal and External calls with equal `N`, viewport, and width use identical sample boundaries and positions.
- Output cardinality is at most `W`; complete original arrays never enter QML.
- Maximum supported one-million-row envelope computation has Windows p95 <=100 ms.

## Candidate methods and comparative evidence

1. Uniform one-point-per-bucket sampling: rejected because a narrow peak can fall between selected indexes.
2. Largest-Triangle-Three-Buckets: rejected because it optimizes visual shape but does not guarantee both positive and negative extrema.
3. Contiguous Min/Max envelope: selected because it has exact extrema preservation, deterministic boundaries, linear cost, and bounded output.

Rendering a filled band or connecting alternating extrema was rejected because it obscures the actual impact location or invents chronology. One vertical stroke per bucket makes the horizontal location and amplitude range explicit, while a same-color polyline through bucket arithmetic means preserves visual continuity.

## Selected method and reasons for rejecting alternatives

Use NumPy reductions over deterministic integer bucket edges in `data_workspace`. L0 maps only bounded primitives. The desktop adapter renders existing colored polylines for raw mode and thin colored vertical strokes plus continuous same-color arithmetic-mean polylines for envelope mode. This separates semantic coverage from Qt drawing and keeps complete arrays out of QML.

## Exact behavior, formula or pseudocode, boundaries, and tie-breaking

```text
s = floor(clamp(viewport_start, 0, 1) * N)
e = ceil(clamp(viewport_end, 0, 1) * N)
V = e - s

if V <= W:
    position[i] = (((s+i)+0.5)/N - viewport_start) / viewport_span
    min[channel,i] = max[channel,i] = values[s+i,channel]
else:
    edge[k] = s + floor(k*V/W), for k in [0,W]
    bucket k = [edge[k], edge[k+1])
    position[k] = (((edge[k]+edge[k+1])/2)/N - viewport_start) / viewport_span
    min[channel,k] = minimum(values[bucket k,channel])
    max[channel,k] = maximum(values[bucket k,channel])
    mean[channel,k] = arithmetic_mean(values[bucket k,channel])
```

Positions are clamped to `[0,1]`. Integer edges break all ties and cover `[s,e)` exactly once. Reduction order does not affect finite Min/Max results; arithmetic means use NumPy float64 reduction over each exact bucket.

## Parameters, calibration, versioning, and compatibility

Plot width is the only dynamic budget and is provided by QML geometry. There is no calibration or persisted parameter. Existing sample arrays, annotation intervals, project schema, Learning input, exports, colors, and shared viewport controls remain compatible.

## Time and space complexity and resource budgets

For visible samples `V` and pixel width `W`, time is `O(3V)` and projection output is `O(3*min(V,W))`; the additional mean reduction changes only the constant factor. The selected implementation performs no full-array Qt conversion. The `interactive-workspace` p95 budget is 100 ms on the declared Windows minimum platform; runtime evidence is required because the explicit budget triggers benchmarking.

## Errors, degradation, fallback, and forbidden behavior

- Empty input: empty raw projection.
- One visible sample: raw projection containing that sample.
- Invalid shape, non-finite visible values, non-positive width, or invalid viewport: explicit `ValueError`; off-viewport finiteness remains the importer invariant so narrow projections retain `O(V)` cost.
- Forbidden: uniform skipping, filled envelope band, extrema zigzag, differing IMU boundaries, mutation of source arrays, changing annotation fractions/indexes, or sending full source arrays to QML.

## Validation cases and evidence

- Golden impulse between legacy uniform indexes, positive and negative extrema, first/last sample, exact boundary and partial viewport cases.
- Property cases assert contiguous half-open coverage indirectly through literal extrema, deterministic identical output, and cardinality <= width.
- Controller/component tests assert primitive mapping and absence of full arrays.
- Renderer image tests assert vertical extent/colors and continuous bucket-mean lines in envelope mode, plus existing polyline behavior in raw mode.
- QML tests assert both panels call the same viewport query and zoom/pan/resize regenerate projection while annotation indexes remain unchanged.
- Windows benchmark records at least 20 maximum-size runs and asserts p95 <=100 ms.

## Risks and monitoring

Python object conversion can dominate very wide plots, so cardinality remains width-bounded and benchmark covers the complete service result. Per-channel auto-scaling remains existing behavior; this change improves peak retention but does not introduce shared amplitude scaling.

## Human approval

Not yet approved. The user's SPEC-0023 selection and `開始執行` authorize implementation but do not change this record from `proposed` to `accepted`.
