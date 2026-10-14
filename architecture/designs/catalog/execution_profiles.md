# CAT-execution_profiles

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-execution_profiles |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: execution_profiles
value:
- id: windows-desktop
  status: proposed
  assurance_scope:
  - functional-compatibility
  - performance
  target:
    platform: Windows 10 or Windows 11 x64
    cpu: Four or more logical CPU cores
    runtime: Python 3.11+ with PySide6 Qt Quick
    compiler: Python interpreter; generated headers target external C99 or C++17 compilers
    cache_topology: {}
    scheduler_capabilities:
    - Operating-system preemptive threads
    - Qt queued signals
    - Windows multiprocessing spawn processes
```
