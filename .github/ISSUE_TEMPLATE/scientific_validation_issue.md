---
name: Scientific Validation Issue
about: Report a methodological discrepancy, target leakage concern, or physical bounds violation
title: "[VALIDATION] "
labels: ["scientific-validation", "audit"]
assignees: ""
---

## Validation Issue Summary
Describe the scientific integrity issue, data leakage pattern, or metrics inconsistency.

## Category
- [ ] Target-to-Input Leakage / Synthetic Raster Fabrication
- [ ] Observation / Storm Partition Overlap across Splits
- [ ] Physical Bounds Violation ($T_B$, Pressure, Wind Speed)
- [ ] Georeferencing / Coordinate Projection Error
- [ ] Baseline Comparison or Statistical Metrics Discrepancy
- [ ] Provenance Hash / Lineage Inconsistency
- [ ] Sensor Calibration / Unit Scaling Error

## Evidence & Affected Code
Reference the exact file path and line numbers:
- **File Path:** `backend/app/...`
- **Line Numbers:** `#L...-L...`

### Description of Discrepancy
Explain why the code or metric contradicts physical laws or rigorous ML protocols:
```python
# Code snippet or mathematical proof
```

### Proposed Resolution
How should the data pipeline, split logic, or metric calculation be corrected?

## Ground Truth / Reference Citation
Provide authoritative citations (NOAA IBTrACS, NHC Best Track, WMO, peer-reviewed meteorological literature):
