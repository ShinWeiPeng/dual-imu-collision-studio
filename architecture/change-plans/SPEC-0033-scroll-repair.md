# SPEC-0033 scrolling regression correction

Date: 2026-09-13. Follow-up repair of the previously authorized Mapping workflow; no new algorithm, source-selection, persistence, or filtering requirement.

The reported screenshot showed filter preview content clipped above the fixed wizard footer and no reachable adoption action. A Qt reproduction confirmed that wheel events over the nested filter ScrollView stopped advancing the outer Mapping view, leaving the adoption button below its viewport.

SensorMapping now owns the single vertical scroll area, explicitly tracks the complete content height, and displays its vertical scrollbar. SingleImuFilters lays out its stages at their natural height, with Frame content height derived from its contentItem. The former fixed 350-pixel editor and nested scroll area are removed.

Ownership remains as defined by the SPEC-0033 design tables: desktop_adapter owns both QML components and local editable state; there are no new domain types, state authorities, dependencies, callbacks, or events. The numerical filter design and adoption payload are unchanged. This corrects usability of existing AC-002/006/007/008; the implemented specification is not rewritten.

Verification:
- Before repair, `spec-governance/mapping_scroll_probe.py` reproduced the inaccessible action after wheel input over the filter editor.
- `tests/test_sensor_mapping_scroll.py` checks one Internal filter and four External filters in a constrained viewport. Actual wheel input reaches the adoption button and an actual mouse click changes it to Design adopted. Waits allow scrolling animations to finish before clicking.
- `.venv/Scripts/python.exe -m pytest tests/test_sensor_mapping_scroll.py tests/test_qml_smoke.py -q --basetemp build/mapping-scroll-final`: 35 passed in 47.90 seconds. Log: build/mapping-scroll-final.log.
- Architecture development and release gates through architecture_cli.py with the existing manifest/adoption/baseline: PASS. Logs: build/mapping-scroll-architecture.log and build/mapping-scroll-release.log. Existing SHOULD SYM004 analyzer notice remains.
- Ruff formatting of the new Python test passed. Runtime screenshot build/mapping-scroll-4.png shows the vertical scrollbar, the fourth filter, and the successfully adopted design above the fixed footer.
