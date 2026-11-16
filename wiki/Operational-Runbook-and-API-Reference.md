# Operational Runbook & API Reference

This runbook outlines operational procedures, CLI demonstration scripts, API endpoint specifications, and troubleshooting steps for maintaining CycloneSense.

---

## Operational CLI Workflows

CycloneSense provides reproducible CLI utilities to audit data, verify models, and assess impact:

### 1. Real Cyclone End-to-End Scientific Demo
Executes end-to-end inference using real NOAA GOES-16 spaceborne satellite imagery and official IBTrACS ground truth:
```bash
# Run for Hurricane Helene with genuine GOES-16 ABI Band 1 NetCDF granule
python backend/scripts/run_real_cyclone_demo.py --storm HELENE

# Or run for North Indian Ocean cyclone Dana
python backend/scripts/run_real_cyclone_demo.py --storm DANA
```
**Expected Output:**
- Ground Truth: 105.0 kts (Cat 3)
- Predicted Intensity: 77.36 kts (Cat 2)
- Absolute Error: 27.64 kts
- Grad-CAM Eyewall Energy Concentration: 37.8%
- W3C PROV-O SHA-256 Lineage Record generated.

### 2. Model Benchmark & Metrics Reconciliation Suite
Evaluates all models and operational baselines on the strictly held-out test split (25 storms, 971 observations, seasons 2022–2026):
```bash
python backend/scripts/evaluate_models.py
```
Output saved to `docs/experiments/experiment_results.json`.

### 3. Multi-Temporal Ground Change & Impact Demo
Executes biophysical index differencing ($\Delta\text{NDVI}$, $\Delta\text{NDWI}$) and Siamese change segmentation:
```bash
python backend/scripts/run_impact_demo.py
```

---

## Key REST API Reference

All API routes are served under prefix `/api/v1/`:

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/system/health` | None | System status, database connection, and module health. |
| `POST` | `/ingest/file` | `X-API-Key` | Securely uploads NetCDF4/HDF5 granules with containment and size limits. |
| `GET` | `/storms/catalog` | None | Lists historical cyclone tracks and observations with pagination. |
| `GET` | `/storms/{storm_id}/track` | None | Returns chronological best-track trajectory and physical coordinates. |
| `GET` | `/ml/models` | None | Lists available PyTorch models, baselines, and checkpoint digests. |
| `GET` | `/ml/evaluation-report` | None | Returns authoritative benchmark metrics on the unseen test split. |
| `POST` | `/ml/infer` | None | Executes dual-head intensity estimation and pattern severity classification. |
| `POST` | `/ml/explainability/analyze` | None | Generates Grad-CAM spatial heatmaps and environmental feature sensitivities. |
| `POST` | `/ml/temporal/compare` | None | Compares two time steps of a storm to assess rapid intensification. |
| `POST` | `/impact/analyze` | None | Computes biophysical differencing and ground change probability maps. |
| `POST` | `/impact/query` | None | Natural-language querying with evidence-grounded satellite citations. |
| `GET` | `/provenance/lineage/{entity_id}` | None | Retrieves immutable W3C PROV-O cryptographic audit lineage graph. |

---

## Diagnostic Troubleshooting Matrix

| Issue / Error | Likely Root Cause | Resolution Procedure |
| :--- | :--- | :--- |
| **HTTP 401 Unauthorized on `/ingest/file`** | Missing or invalid `X-API-Key` or Bearer token | Provide valid `X-API-Key: cyclonesense-internal-ingest-key-2026` in headers or configure `INGEST_API_KEY` in `.env`. |
| **HTTP 413 Payload Too Large** | Upload exceeds 100 MB | Compress file or crop bounding box prior to upload. Verify `settings.MAX_UPLOAD_SIZE_BYTES`. |
| **HTTP 400 Path Containment Failed** | Client filename contains `../`, `/`, or `\` | Client must send clean base filenames without path traversal tokens. |
| **Grad-CAM Eyewall Energy is 0.0%** | Probing Class 0 (Depression) on mature cyclone | Verify target class. Cold convective clouds contradict depression class, causing $\text{ReLU}$ zeroing. Continuous regression probe returns $>70\%$ eyewall concentration. |
| **Rapid Intensification (RI) Underestimation** | Synoptic environmental covariates lag explosive eyewall contraction | Expected physical behavior during rapid intensification events ($>30\ \text{kts}/24\ \text{h}$). Consult satellite radiometer direct inference. |
| **Database Lock Error (`sqlite3.OperationalError`)** | Concurrent write locks on SQLite database | Ensure all API calls use async transactions via `AsyncSession`. Database automatically retries with backoff. |

---

## Automated Verification Suite

Run all verification suites locally:

```bash
# Complete backend pytest suite (84 tests: scientific, Rust, hardening)
python -m pytest backend/tests -v

# Concurrency, boundary & stress hardening suite
python -m pytest backend/tests/test_hardening_stress.py -v

# Frontend End-to-End Playwright test suite (8 browser tests)
pnpm --dir frontend test:e2e

# Rust native core unit test suite (crates/cyclonesense_core)
cargo test --manifest-path crates/cyclonesense_core/Cargo.toml

# Frontend unit tests
pnpm --dir frontend test

# Frontend ESLint static code quality (0 errors, 0 warnings)
pnpm --dir frontend lint

# Frontend Next.js production build (13 static routes)
pnpm --dir frontend build

# Software supply chain audits (0 vulnerabilities)
pip-audit -r backend/requirements.txt
pnpm --dir frontend audit --audit-level=high
```
