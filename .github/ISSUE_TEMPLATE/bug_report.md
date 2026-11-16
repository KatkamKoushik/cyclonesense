---
name: Bug Report
about: Create a report to help us improve CycloneSense software reliability
title: "[BUG] "
labels: ["bug", "triage"]
assignees: ""
---

## Bug Description
A clear and concise description of what the bug is.

## Component Affected
- [ ] API & Backend (`backend/app/api/`)
- [ ] Scientific Ingestion & NetCDF Reader (`backend/app/scientific/`)
- [ ] PyTorch ML Inference / Baselines (`backend/app/ml/`)
- [ ] Geospatial Georeferencing & Pairing (`backend/app/scientific/georeferencing.py`)
- [ ] Explainability & Grad-CAM (`backend/app/ml/explainability.py`)
- [ ] Ground Change & Impact Intelligence (`backend/app/scientific/change_detector.py`)
- [ ] Frontend Application (`frontend/src/`)
- [ ] Other

## Steps to Reproduce
1. Go to '...'
2. Run command or click '...'
3. Provide input payload: `...`
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior & Error Logs
Paste full stack trace, console logs, or HTTP response:
```text
(Paste logs here)
```

## Environment Details
- **Operating System:** (e.g. Ubuntu 22.04 / Windows 11 / macOS 14)
- **Python Version:** (e.g. 3.12.2)
- **Node.js & pnpm Version:** (e.g. Node 22.11 / pnpm 9.15)
- **Branch / Commit SHA:** (e.g. `main` or commit hash)

## Additional Context
Add any other context, screenshots, or NetCDF granule identifiers here.
