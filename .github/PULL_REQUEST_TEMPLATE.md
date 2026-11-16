## Pull Request Description

### Summary of Changes
Provide a clear, high-level summary of what this pull request modifies, adds, or fixes.

### Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Security fix / containment hardening (CYC-01 or similar)
- [ ] Scientific validation & methodology repair
- [ ] Documentation update
- [ ] Refactoring / performance improvement

---

## Scientific Data & Machine Learning Integrity

CycloneSense enforces strict scientific truth-in-advertising. Please confirm:

- [ ] **Zero Target-to-Input Leakage:** No input features, rasters, or covariates are synthesized from or parameterized by target labels (`wind_kts`, `category`).
- [ ] **Strict Storm-Level Separation:** All storm observations are strictly partitioned by storm ID; no near-duplicate or frame-level overlap occurs across train/val/test splits.
- [ ] **Physical Bounds Compliance:** All meteorological variables obey physical constraints ($160\ \text{K} \le T_B \le 340\ \text{K}$, $850\ \text{hPa} \le P \le 1040\ \text{hPa}$, $0 < V \le 250\ \text{kts}$).
- [ ] **Authentic Sensor Ingestion:** Sensor rasters originate from authentic Earth observation products (NetCDF4/HDF5) or calibrated baselines, not un-disclosed synthetic generators.
- [ ] **W3C PROV-O Lineage:** Deterministic NIST SHA-256 digests and provenance records are preserved.

---

## Verification & Automated Test Checklist

Please confirm that all local tests and static audits pass cleanly:

- [ ] **Backend Tests:** `python -m pytest backend/tests -v` (69/69 passed)
- [ ] **Frontend Tests:** `pnpm --dir frontend test` (All contract & scientific suites passed)
- [ ] **Frontend Static Quality:** `pnpm --dir frontend lint` (0 errors, 0 warnings)
- [ ] **Frontend Production Build:** `pnpm --dir frontend build` (All static routes compile cleanly)
- [ ] **Security Dependency Audits:**
  - `pip-audit -r backend/requirements.txt` (0 vulnerabilities)
  - `pnpm --dir frontend audit` (0 vulnerabilities)

---

## Related Issues
Closes #(issue number)
