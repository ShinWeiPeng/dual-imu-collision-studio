# CAT-source_sets

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-source_sets |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: source_sets
value:
- id: product-source
  classification: production
  include:
  - src/**
  exclude: []
  purpose: Govern maintained Python and QML product source.
  provenance: Human-reviewed implementation of SPEC-0001.
- id: development-source
  classification: development
  include:
  - tests/**
  - specs/**
  - spec-governance/**
  - pyproject.toml
  - README.md
  - validation/**
  exclude: []
  purpose: Keep tests, specification evidence, and packaging metadata outside product
    ownership.
  provenance: Project development material.
- id: derived-architecture
  classification: derived-documentation
  include:
  - architecture/generated/**
  - architecture/ARCHITECTURE.md
  exclude: []
  purpose: Keep deterministic architecture views outside product ownership.
  provenance: Architecture renderer output.
- id: build-output
  classification: build-output
  include:
  - build/**
  - dist/**
  - .pytest_cache/**
  - '**/__pycache__/**'
  - .venv/**
  - .ruff_cache/**
  - src/*.egg-info/**
  exclude: []
  purpose: Exclude generated build and interpreter output.
  provenance: Python and packaging tools.
```
