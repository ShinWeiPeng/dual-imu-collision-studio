# CAT-platform_variants

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-platform_variants |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: platform_variants
value:
- id: windows-desktop-minimum
  profile: windows-desktop
  units:
  - qt-ui-thread
  - analysis-worker
  - fold-process-workers
  - qualification-process-workers
  - replay-export-worker
  data_access_profiles:
  - waveform-viewport-buckets
  - history-fir-matrices
  microarchitecture_profiles:
  - waveform-projection-python-numpy
  - history-training-python-numpy
  parameters:
    minimum_logical_cores: 4
    minimum_ram_gb: 8
    maximum_search_workers: 8
    maximum_qualification_workers: 4
    maximum_ram_fraction: 0.9
  release: false
```
