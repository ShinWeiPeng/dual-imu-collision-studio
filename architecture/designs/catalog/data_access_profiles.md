# CAT-data_access_profiles

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-data_access_profiles |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: data_access_profiles
value:
- id: waveform-viewport-buckets
  profile: windows-desktop
  workload: interactive-workspace
  tier: tier-1
  element_size_bytes: 8
  layout: Contiguous row-major NumPy float64 view over three axes with bounded position,
    minimum, maximum, and arithmetic-mean output vectors.
  active_working_set_bytes: 24109280
  stride_bytes: 24
  reuse: Each viewport projection traverses the selected visible slice once; Internal
    and External projections reuse identical integer bucket boundaries.
  alignment_bytes: 8
  sharing: Original arrays are read-only by contract; only bounded immutable projection
    values cross into Qt/QML.
  cache_target: Windows desktop CPU memory hierarchy and installed NumPy implementation.
  candidates:
  - Uniformly sample one point per display column.
  - Reduce every contiguous display bucket to its minimum, maximum, and arithmetic
    mean.
- id: history-fir-matrices
  profile: windows-desktop
  workload: analysis-run
  tier: tier-1
  element_size_bytes: 8
  layout: Row-major NumPy float64 fitting matrices private to one candidate-fold worker,
    with target-dtype evaluation arithmetic.
  active_working_set_bytes: 1
  stride_bytes: 8
  reuse: Effective parameter results are cached per round; dataset inputs are copied
    once per batch worker. Qualification score arrays are computed once per frozen
    fold model and recording and reused across configurations.
  alignment_bytes: 8
  sharing: No writable sharing between workers; immutable job inputs are copied by
    Windows spawn.
  cache_target: Worker process memory hierarchy and NumPy BLAS implementation.
  candidates:
  - Rebuild FIR rows for every rule.
  - Cache complete FIR matrices per History and fold role.
```
