# Contributing to CycloneSense

Thank you for your interest in contributing to **CycloneSense**! We welcome contributions from software engineers, meteorologists, earth observation researchers, data scientists, and UI/UX designers.

To ensure scientific integrity, code reliability, and reproducible Earth observation intelligence, please review these guidelines before submitting an issue or pull request.

---

## Code of Conduct

All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any violations to [koushikkatkam@gmail.com](mailto:koushikkatkam@gmail.com).

---

## Development Setup

### Prerequisites
- **Python**: 3.10+ (recommended: Python 3.12 64-bit)
- **Node.js**: 20+ (recommended: Node.js 22 LTS or 24 with `pnpm`)
- **Git**

### 1. Fork & Clone
```bash
git clone https://github.com/KatkamKoushik/cyclonesense.git
cd cyclonesense
```

### 2. Backend Setup (FastAPI & PyTorch)
```bash
# Set up Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Run backend verification suite
python -m pytest backend/tests -v
```

### 3. Frontend Setup (Next.js 16 & TypeScript)
```bash
cd frontend
pnpm install

# Run frontend tests, linting, and build
pnpm test
pnpm lint
pnpm build
```

---

## Scientific Data & Machine Learning Integrity Standards

CycloneSense adheres to strict scientific truth-in-advertising. Contributions touching data pipelines, ML models, or evaluation metrics must comply with these protocols:

1. **Zero Target-to-Input Leakage:**
   - Input rasters, environmental vectors, and features must **never** be synthesized from or parameterized by target labels (`obs.wind_kts`, `obs.category`).
   - Synthetic benchmark rasters (such as `SyntheticProxyBenchmarkDataset`) are strictly quarantined for pipeline diagnostics and must carry explicit `is_synthetic_benchmark: True` metadata.
2. **Authentic Sensor Ingestion:**
   - Operational model evaluation must consume genuine, calibrated Earth observation products (e.g., NOAA GOES-16 ABI Band 1 / Band 13, Sentinel-1/2) paired with official best-track archives (NOAA IBTrACS v04r01).
   - Coordinate transforms must use closed-form geostationary projection equations with boundary checks.
3. **Strict Storm-Level Separation:**
   - Any evaluation split must enforce storm-level separation (`split_by_storm`). All observations of a given cyclone must reside exclusively in one partition.
4. **Physical Sanity Bounds:**
   - Observed physical variables must respect physical limits:
     - Brightness Temperature: $160\ \text{K} \le T_B \le 340\ \text{K}$
     - Central Pressure: $850\ \text{hPa} \le P \le 1040\ \text{hPa}$
     - Maximum Sustained Wind: $0 < V \le 250\ \text{kts}$
5. **W3C PROV-O Lineage:**
   - All scientific transformations and neural inferences must generate deterministic NIST FIPS 180-4 SHA-256 digests and W3C PROV-O lineage records.

---

## Development & Pull Request Workflow

1. **Create a Topic Branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```
2. **Make Focused, Atomic Commits:**
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat(ingest): add support for Himawari-9 AHI NetCDF4 granules`
   - `fix(security): sanitize upload paths and enforce UUID storage containment`
   - `docs(validation): update baseline comparison table and confidence intervals`
3. **Run Pre-Commit Verification:**
   Before pushing, ensure all checks pass locally:
   ```bash
   # Backend tests
   python -m pytest backend/tests -v

   # Frontend verification
   pnpm --dir frontend test
   pnpm --dir frontend lint
   pnpm --dir frontend build

   # Security audits
   pip-audit -r backend/requirements.txt
   pnpm --dir frontend audit
   ```
4. **Submit a Pull Request:**
   - Fill out the provided [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).
   - Ensure your PR references any relevant issue numbers (e.g., `Fixes #12`).
   - Maintainers will review your submission and provide constructive feedback.

---

## Reporting Issues

- **Bug Reports:** Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md) with reproduction steps, environment details, and logs.
- **Scientific Validation Issues:** Use the [Scientific Validation Issue Template](.github/ISSUE_TEMPLATE/scientific_validation_issue.md) if you identify data leakage, physical bounds violations, or discrepancies in benchmark metrics.
- **Feature Requests:** Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md) describing the meteorological or engineering rationale.
- **Security Vulnerabilities:** Do **not** open a public issue. See our [Security Policy](SECURITY.md) for responsible disclosure procedures.
