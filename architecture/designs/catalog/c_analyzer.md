# CAT-c_analyzer

## Identity

| Field | Value |
|---|---|
| format_version | 1 |
| id | CAT-c_analyzer |
| version | 1 |
| kind | catalog |

## Design Data

<!-- design-data:1 -->
```yaml
manifest_field: c_analyzer
value:
  ast:
    status: not-applicable
    rationale: Product implementation is Python and QML; generated C/C++ headers are
      verified development artifacts, not governed translation units.
  functional_boundary:
    status: not-applicable
    rationale: There are no maintained C/C++ adapter source files.
    forbidden_includes: []
    forbidden_symbols: []
  forbidden_public_includes: []
  forbidden_public_symbols: []
  forbidden_source_symbols: []
```
