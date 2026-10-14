# CAT-microarchitecture_profiles

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-microarchitecture_profiles |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: microarchitecture_profiles
value:
- id: waveform-projection-python-numpy
  profile: windows-desktop
  workload: interactive-workspace
  tier: tier-1
  branches: One deterministic raw-versus-envelope branch plus viewport and input validation.
  simd_eligibility: Min/Max and arithmetic-mean reductions are delegated to the installed
    NumPy backend; no application SIMD claim is made.
  compiler: CPython 3.11+ and installed NumPy binary.
  compiler_flags: Not controlled by the application.
  vectorization_report: Not available for packaged NumPy; the Windows p95 benchmark
    is authoritative.
  pgo: Not controlled by the application.
  lto: Not controlled by the application.
- id: history-training-python-numpy
  profile: windows-desktop
  workload: analysis-run
  tier: tier-1
  branches: FIR segment validation and robust-refit selection remain deterministic
    Python/NumPy branches.
  simd_eligibility: Dense matrix products and linear solves are delegated to the installed
    NumPy backend; Python row construction is not claimed SIMD-vectorized.
  compiler: CPython 3.11+ and installed NumPy binary.
  compiler_flags: Not controlled by the application.
  vectorization_report: Not available for packaged NumPy; runtime benchmark is authoritative.
  pgo: Not controlled by the application.
  lto: Not controlled by the application.
```
