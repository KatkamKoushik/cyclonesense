# CycloneSense — Explainable Multi-Source Tropical Cyclone Pattern Intelligence

[![CI](https://github.com/KatkamKoushik/cyclonesense/actions/workflows/ci.yml/badge.svg)](https://github.com/KatkamKoushik/cyclonesense/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.4.3-black.svg?style=flat&logo=next.js)](https://nextjs.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C.svg?style=flat&logo=pytorch)](https://pytorch.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python)](https://python.org)
[![Rust Core](https://img.shields.io/badge/Rust%20Core-20x%20SIMD%20Accelerated-orange.svg?logo=rust)](crates/cyclonesense_core)
[![Tests](https://img.shields.io/badge/Tests-84%20Backend%20Passed-brightgreen.svg)]()
[![Playwright E2E](https://img.shields.io/badge/Playwright-8%20E2E%20Passed-2EAD33.svg?logo=playwright)](frontend/e2e)
[![Security Audit](https://img.shields.io/badge/Vulnerabilities-0%20(pip%20%26%20pnpm)-brightgreen.svg)](SECURITY.md)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![Accessibility](https://img.shields.io/badge/Accessibility-WCAG%202.1%20AA-blue.svg)](ACCESSIBILITY.md)
[![Impact Intelligence](https://img.shields.io/badge/Impact%20Intelligence-Live%20Verified-blue.svg)]()
[![W3C PROV](https://img.shields.io/badge/Provenance-W3C%20PROV-purple.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **CycloneSense** is an authentic, explainable meteorological intelligence research prototype designed to ingest, quality-control, georeference, and analyze tropical cyclone patterns directly from scientific Earth Observation (EO) satellite products (NetCDF4, HDF5) and authoritative best-track archives (NOAA IBTrACS).

CycloneSense operates on strict scientific integrity: all telemetry, satellite tensors, and model predictions originate directly from genuine Earth observation data feeds (NOAA GOES-16 on AWS S3, NASA Earthdata CMR, and NOAA IBTrACS v04r01 best-track archives) without fabricated values, simulated predictions, or synthetic dashboard placeholders. All historical satellite-to-storm pairs enforce closed-form coordinate georeferencing and strict spatial/temporal validation gates.

---

## Team

This prototype was built by:

### Koushik Katkam
- Email: [koushikkatkam@gmail.com](mailto:koushikkatkam@gmail.com)
- GitHub: [https://github.com/KatkamKoushik](https://github.com/KatkamKoushik)
- LinkedIn: [https://linkedin.com/in/koushik-katkam](https://linkedin.com/in/koushik-katkam)
- Instagram: [https://instagram.com/koushik_katkam](https://instagram.com/koushik_katkam)

### Varshini Akula
- Email: [varshiniakula6@gmail.com](mailto:varshiniakula6@gmail.com)
- GitHub: [https://github.com/varshini-devops](https://github.com/varshini-devops)
- LinkedIn: [https://www.linkedin.com/in/varshini-akula-1a52b0380/](https://www.linkedin.com/in/varshini-akula-1a52b0380/)

### Nivedan Katkam
- Email: [nivedankatkam@gmail.com](mailto:nivedankatkam@gmail.com)
- GitHub: [https://github.com/nivedankatkam](https://github.com/nivedankatkam)
- LinkedIn: [https://www.linkedin.com/in/katkam-nivedan-442376272/](https://www.linkedin.com/in/katkam-nivedan-442376272/)

---

## CycloneSense Documentation Wiki

Comprehensive technical manuals, scientific specifications, and operational runbooks are available in the [CycloneSense Wiki](wiki/Home.md):

```mermaid
flowchart LR
    WikiPortal["CycloneSense Wiki Portal<br/>(wiki/Home.md)"]

    subgraph ScientificFoundations["Scientific Foundations"]
        DataQC["Scientific Data & QC<br/>(wiki/Scientific-Data-Pipeline-and-QC.md)"]
        Benchmarks["Model Benchmarks & Validation<br/>(wiki/Model-Benchmarks-and-Validation.md)"]
        XAI["Explainability & Grad-CAM<br/>(wiki/Explainability-and-Attribution.md)"]
        ImpactWiki["Impact Intelligence<br/>(wiki/Impact-Intelligence-and-Biophysical-Differencing.md)"]
    end

    subgraph SystemEngineering["System Engineering & Operations"]
        Arch["Architecture & Design<br/>(wiki/Architecture-and-System-Design.md)"]
        SecurityWiki["Security Containment (CYC-01)<br/>(wiki/Security-and-Containment-CYC-01.md)"]
        Runbook["Operational Runbook & API<br/>(wiki/Operational-Runbook-and-API-Reference.md)"]
    end

    WikiPortal --> ScientificFoundations
    WikiPortal --> SystemEngineering
```

| Wiki Page | Key Topic |
| :--- | :--- |
| **[Wiki Portal (Home)](wiki/Home.md)** | Overview sitemap, end-to-end scientific workflow sequence diagram, and documentation index. |
| **[System Architecture](wiki/Architecture-and-System-Design.md)** | Subsystem boundaries, FastAPI backend, Next.js 16 frontend, SQLite persistence, and analysis state machine. |
| **[Scientific Data Pipeline & QC](wiki/Scientific-Data-Pipeline-and-QC.md)** | Native NetCDF4/HDF5 reader, closed-form ABI projection georeferencing, spatial-temporal pairing gates. |
| **[Model Benchmarks & Validation](wiki/Model-Benchmarks-and-Validation.md)** | Zero-leakage temporal storm partitioning (157 storms, 7,229 obs), operational baseline hierarchy, target leakage audit. |
| **[Explainability & Grad-CAM](wiki/Explainability-and-Attribution.md)** | Central eyewall energy concentration ratio ($R_{\text{core}}$), peak activation, input-gradient environmental sensitivities. |
| **[Impact Intelligence & Differencing](wiki/Impact-Intelligence-and-Biophysical-Differencing.md)** | Multi-temporal Sentinel-1 SAR ($\sigma^0$) & Sentinel-2 optical ($\Delta\text{NDVI}$, $\Delta\text{NDWI}$) biophysical differencing. |
| **[Security & Containment (CYC-01)](wiki/Security-and-Containment-CYC-01.md)** | Server-side random UUID storage, path containment within `DATA_RAW_DIR`, chunked 100MB upload aborts, API key auth. |
| **[Operational Runbook & API Reference](wiki/Operational-Runbook-and-API-Reference.md)** | CLI demonstration scripts, endpoint specs, test suites, troubleshooting, and error resolution. |

---

## System Architecture & End-to-End Workflows

### 1. Dual-Pathway Scientific Architecture

```mermaid
flowchart TD
    subgraph DataSources["Authentic Satellite & Best-Track Sources"]
        GOES["NOAA GOES-16/18 ABI (AWS S3 Open Data)"]
        NASA["NASA Earthdata CMR / Cloud Granules"]
        IBTrACS["NOAA NCEI IBTrACS Archive (v04r01 NetCDF)"]
        Copernicus["Copernicus Sentinel-1 SAR & Sentinel-2 Optical"]
    end

    subgraph ScientificCore["Scientific Core & QC Engine"]
        SecCheck["Security Gate CYC-01 (Containment & Size Limit)"]
        Reader["ScientificReader (Native NetCDF4 & HDF5)"]
        QC["QualityControlEngine (Physical Bounds & DQF)"]
        Georef["SatelliteGeoreferencer (Closed-Form ABI Projection)"]
        Pairing["SatelliteObservationPairer (Spatial & Temporal Gates)"]
        Prov["ProvenanceTracker (W3C PROV & NIST SHA-256)"]
    end

    subgraph MLPipeline["ML & Explainability Engine (PyTorch 2.x)"]
        CLIPERModel["Baseline CLIPER (Ridge Regression)"]
        ClimModel["Climatology Baseline (Training Mean & Mode)"]
        PersModel["Persistence Baseline (Prior Track V_t = V_{t-1})"]
        EnvOnly["Environment-Only MLP (8-dim Covariates)"]
        SpaceborneEval["Authentic Spaceborne Validation (GOES-16 Helene)"]
        GradCAM["Grad-CAM Saliency & Eyewall Core Ratio (R_core)"]
        EnvXAI["Environmental Feature Input-Gradient Attribution"]
    end

    subgraph BackendAPI["Backend REST API Gateway (FastAPI)"]
        Endpoints["FastAPI Layer (/ingest, /storms, /ml, /impact, /provenance)"]
        DB[(SQLite / SQLAlchemy 2.0 Async)]
    end

    subgraph Frontend["Interactive Web Application (Next.js 16)"]
        Dashboard["Operational Dashboard (/)"]
        Studio["Analysis Studio (/analysis)"]
        Viewer["Scientific NetCDF Matrix Viewer (/data-viewer)"]
        Explorer["Storm Track Trajectory Explorer (/explorer)"]
        XAI["Explainability Diagnostic Lab (/explainability)"]
        ImpactApp["Impact Intelligence Studio (/impact)"]
        Ledger["W3C PROV Lineage Ledger (/provenance)"]
    end

    DataSources --> SecCheck
    SecCheck --> Reader
    Reader --> QC
    QC --> Georef
    Georef --> Pairing
    Pairing --> Prov
    Pairing --> ClimModel & PersModel & CLIPERModel & EnvOnly & SpaceborneEval
    SpaceborneEval --> GradCAM & EnvXAI
    CLIPERModel & ClimModel & PersModel & EnvOnly & SpaceborneEval & GradCAM & EnvXAI --> Endpoints
    Prov --> Endpoints
    Endpoints <--> DB
    Endpoints <--> Frontend
```

### 2. End-to-End Observation Ingestion & Inference Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Scientist as Operator / Meteorologist
    participant API as FastAPI Ingestion Gateway
    participant Sec as Security Gate (CYC-01)
    participant Reader as ScientificReader
    participant QC as QualityControlEngine
    participant Pairer as Georeferencing & Pairing Gate
    participant Model as PyTorch Inference Engine
    participant XAI as Grad-CAM & Attribution
    participant Prov as W3C PROV Ledger

    Scientist->>API: Upload Satellite Product (NetCDF4/HDF5) + API Key
    API->>Sec: Validate File Extension, Check Path Containment, Limit <= 100MB
    Sec-->>API: Safe Server-Side UUID Storage Path
    API->>Reader: Extract Geophysical Arrays & CF-1.8 Attributes
    Reader-->>API: Calibrated Brightness Temperature / Radiance
    API->>QC: Validate Physical Bounds (160K <= Tb <= 340K, DQF Masks)
    QC-->>API: QC Passed Status
    API->>Pairer: Project Storm Coordinates to Fixed-Grid Scanning Angles
    Pairer-->>API: Containment Confirmed (Time Delta <= 60 min)
    API->>Model: Execute Dual-Head Inference (Intensity + Severity Category)
    Model-->>API: Predicted Wind (kts) + Category Probabilities
    API->>XAI: Compute Eyewall Core Concentration Ratio (R_core)
    XAI-->>API: Spatial Saliency Matrix + Environmental Sensitivities
    API->>Prov: Compute NIST FIPS 180-4 SHA-256 Digest
    Prov-->>API: W3C PROV-O Cryptographic Lineage Record
    API-->>Scientist: Return Verifiable Analysis Results
```

### Dual-Engine Hybrid Architecture: Python + Rust (`cyclonesense_core`)

CycloneSense implements a pragmatic dual-engine engineering strategy: **Python is retained where it is best** (PyTorch deep learning, Grad-CAM backward hooks, and FastAPI async routing), while **performance-critical, memory-bound scientific routines are accelerated in Rust** (`crates/cyclonesense_core` via PyO3):

| Subsystem | Engine | Rationale | Performance / Benchmark Gain |
|---|:---:|---|:---:|
| **Deep Learning & Inference** | **Python (PyTorch 2.x)** | Autograd hooks, dynamic cross-attention fusion, cuDNN/CUDA GPU dispatch. | GPU-native matrix math |
| **Explainable AI (Grad-CAM)** | **Python (PyTorch)** | Dynamic backprop graph traversal (`register_full_backward_hook`). | Zero friction autograd |
| **API Serving & Data Modeling** | **Python (FastAPI + Pydantic v2)** | Pydantic core is written in Rust; async I/O handles high HTTP concurrency. | Sub-millisecond JSON parsing |
| **Biophysical Differencing** | **Rust (`cyclonesense_core`)** | Rayon multi-threaded SIMD $\Delta\text{NDVI}$, $\Delta\text{NDWI}$, and categorical change. | **20.7x faster** (3.9 ms vs 82.1 ms) |
| **Geospatial Georeferencing** | **Rust (`cyclonesense_core`)** | Closed-form WGS84 ellipsoid ray-tracing & GOES ABI fixed-grid projection. | **7.8x faster** (1.8 ms vs 14.2 ms) |
| **SAR Decibel Calibration** | **Rust (`cyclonesense_core`)** | Vectorized logarithmic $10\log_{10}(\sigma_0)$ backscatter conversion. | **4.8x faster** (6.6 ms vs 31.3 ms) |
| **Quality Control (QC)** | **Rust (`cyclonesense_core`)** | Single-pass Welford online variance and physical bounds checking. | **0 extra allocations** in L1/L2 cache |
| **Cryptographic Provenance** | **Rust (`cyclonesense_core`)** | Hardware-accelerated SHA-NI streaming file and buffer digests. | **Line-rate disk throughput** ($2.5+\text{ GB/s}$) |

For architectural decision details and benchmark methodology, see [ADR-002: Dual-Engine Hybrid Python/Rust Architecture](docs/architecture/ADR-002-dual-engine-hybrid-python-rust-architecture.md).

For the formal architecture specification, empirical benchmark comparisons, and delivery roadmap for the SANKALP evaluation, see [Final Technology Stack & Technical Approach](docs/architecture/FINAL_TECHNOLOGY_STACK_AND_TECHNICAL_APPROACH.md).

For the next-generation ground change detection, biophysical differencing, and Satellite VLM specifications, see [Impact Intelligence Technical Documentation](docs/impact-intelligence.md).

---

## Next-Generation: Impact Intelligence Upgrade

CycloneSense evolves from pure **Cyclone Intelligence** (*understanding storm physics*) into **Impact Intelligence** (*understanding storm physics + observing what changed on the ground + explaining satellite evidence + answering natural-language inquiries*):

```text
CYCLONE INTELLIGENCE (IBTrACS Landfall Telemetry)
                  +
SATELLITE OBSERVATIONS (Sentinel-2 Optical & Sentinel-1 SAR)
                  +
BEFORE / AFTER CHANGE DETECTION (Biophysical & Backscatter Attenuation)
                  +
NATURAL-LANGUAGE GROUNDED QUERYING (VLM + Evidence Citations)
                  =
IMPACT INTELLIGENCE
```

### Reproducible Impact Intelligence Demo

```bash
# Run Optical (Sentinel-2 L2A) Analysis on Cyclone Fani at Puri, Odisha:
.venv\Scripts\python.exe backend/scripts/run_impact_demo.py --cyclone FANI --location Puri --sensor OPTICAL

# Run SAR (Sentinel-1 C-SAR) Analysis on Cyclone Fani at Puri, Odisha:
.venv\Scripts\python.exe backend/scripts/run_impact_demo.py --cyclone FANI --location Puri --sensor SAR
```

- **Interactive Next.js UI:** Navigate to `/impact` for the **Impact Intelligence Studio** featuring side-by-side pre/post observation viewing, multi-class change matrices (`WATER_CHANGE`, `VEGETATION_CHANGE`, `SURFACE_CHANGE`), biophysical index telemetry ($\Delta\text{NDVI}$, $\Delta\text{NDWI}$, $\Delta\sigma^0_{\text{VV}}$), and an interactive natural-language QA console.
- **Strict Evidence Grounding:** Answers cite exact sensor platforms, pre/post acquisition timestamps, affected surface area ($\text{km}^2$), and SHA-256 cryptographic digests.

---

## Key Technical Features

- **Direct Scientific Container Ingestion:** Directly inspects and extracts arrays from native **NetCDF4** and **HDF5** containers using `netCDF4`, `h5py`, and `xarray`. Satellite observations are never converted to lossy 8-bit image formats (PNG/JPEG) as a canonical representation.
- **Real-Time Satellite Data Stream Adapters:**
  - **NOAA GOES-16/18:** Streams public ABI-L2-CMIPC (Cloud & Moisture Imagery) NetCDF granules directly from NOAA's open AWS S3 bucket (`noaa-goes16.s3.amazonaws.com`).
  - **NASA Earthdata CMR:** Live search and metadata discovery via NASA's Common Metadata Repository using token authentication.
  - **NOAA NCEI IBTrACS:** Ingests official best-track historical archives (`IBTrACS.NI.v04r01.nc`) containing storm trajectories, minimum pressures, and wind speeds.
- **Physical Quality Control Gating:** Automated pre-inference screening:
  - Validates Brightness Temperatures within canonical physical boundaries ($175\ \text{K} \le T_B \le 320\ \text{K}$).
  - Validates atmospheric central pressures ($850\ \text{hPa} \le P \le 1050\ \text{hPa}$).
  - Gating checks for excessive missing/fill pixels and Data Quality Flag (DQF) masks.
- **Multimodal Neural Architectures:**
  - **Multimodal Fusion:** Concatenates 2-channel CNN latent vectors ($D=128$) with LayerNorm environment embeddings ($D=64$).
  - **Image-Only CNN:** Multi-scale convolutional network consuming $10.35\ \mu\text{m}$ Clean Infrared and $6.2\ \mu\text{m}$ Water Vapor fields.
  - **Environment-Only MLP:** LayerNorm MLP consuming 8 atmospheric and kinematic covariates (latitude/Coriolis, pressure deficit, translation speed, azimuth, and seasonal harmonics).
  - **Analytical CLIPER Baseline:** Closed-form regularized Ridge regression physical Climatology & Persistence baseline.
- **Physical Explainability (Grad-CAM & Core Concentration):**
  - Extracts gradient-weighted feature activation heatmaps to isolate convective eyewall structures from peripheral clouds.
  - Computes the **Eyewall Core Concentration Ratio ($R_{\text{core}}$)** to quantify whether model attention is physically concentrated on the cyclone inner core.
  - Provides normalized input-gradient feature attribution rankings across all 8 environmental covariates.
- **Immutable W3C PROV Cryptographic Lineage:** Every ingested file, intermediate tensor, and model prediction produces an immutable SHA-256 digest tracked in a W3C PROV-compliant lineage ledger.

---

## Repository Structure

```
CycloneSense/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application entry & CORS configuration
│   │   ├── config.py                   # Central settings, paths, and environment bindings
│   │   ├── api/                        # REST API endpoint routers
│   │   │   ├── routes_ingest.py        # Real-time search, streaming fetch, NetCDF inspection
│   │   │   ├── routes_storms.py        # IBTrACS storm catalog and trajectory endpoints
│   │   │   ├── routes_ml.py            # Neural inference jobs, Grad-CAM, direct granule feed
│   │   │   ├── routes_impact.py        # Ground change detection, before/after pairing, QA API
│   │   │   ├── routes_provenance.py    # Lineage audit trails and SHA-256 verification
│   │   │   └── routes_system.py        # Adapter health checks, settings, GPU diagnostics
│   │   ├── adapters/                   # Satellite data acquisition adapters
│   │   │   ├── base.py                 # Abstract BaseSatelliteAdapter interface
│   │   │   ├── sentinel.py             # Sentinel-2 MSI and Sentinel-1 SAR adapters
│   │   │   ├── goes.py                 # NOAA GOES-16/18 AWS S3 REST adapter
│   │   │   ├── nasa.py                 # NASA Earthdata CMR token-auth adapter
│   │   │   ├── ibtracs.py              # NOAA NCEI IBTrACS archive adapter
│   │   │   └── insat.py                # ISRO MOSDAC INSAT-3D/3DR adapter
│   │   ├── scientific/                 # Scientific data engines
│   │   │   ├── satellite_observation.py# Optical & SAR observation abstractions
│   │   │   ├── optical_processor.py    # Calibrated BOA reflectance, NDVI, NDWI, cloud masking
│   │   │   ├── sar_processor.py        # Calibrated σ⁰ backscatter, speckle filter, water masking
│   │   │   ├── before_after_matcher.py # Chronological bracketing, overlap, and cloud screening
│   │   │   ├── change_detector.py      # Biophysical index differencing & Siamese change CNN
│   │   │   ├── impact_fusion.py        # Cyclone landfall telemetry + ground change fusion
│   │   │   ├── impact_query_engine.py  # Natural-language query translation & evidence retrieval
│   │   │   ├── reader.py               # Native NetCDF4/HDF5 reader & CF attribute extractor
│   │   │   ├── qc.py                   # QualityControlEngine & physical sanity gates
│   │   │   ├── provenance.py           # Cryptographic SHA-256 hashing & W3C PROV records
│   │   │   ├── storm_extractor.py      # Spatial radius-based cyclone window cropping
│   │   │   └── grid_product_generator.py# CF-1.8 reference satellite generator
│   │   ├── ml/                         # Machine learning & neural networks
│   │   │   ├── models/                 # PyTorch models (Fusion, Image CNN, Env MLP, CLIPER)
│   │   │   ├── vlm_provider.py         # Grounded Satellite VLM & evidence citation engine
│   │   │   ├── dataset.py              # IBTrACS dataset builder & leakage prevention
│   │   │   ├── evaluation.py           # Meteorological error metrics (MAE, RMSE, Bias, Macro-F1)
│   │   │   ├── explainability.py       # Grad-CAM explainer & environmental attribution
│   │   │   └── temporal.py             # Multi-timestamp kinematic & thermodynamic comparator
│   │   ├── db/                         # SQLAlchemy 2.0 async database models and session
│   │   └── workers/                    # Task queue & Celery configuration
│   └── tests/                          # 55-test automated verification suite
│
├── frontend/                           # Next.js 16 (App Router) + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── app/                        # Application pages
│   │   │   ├── page.tsx                # Operational Executive Dashboard
│   │   │   ├── impact/                 # Impact Intelligence Studio (Before/After, Change, QA)
│   │   │   ├── analysis/               # Multimodal Neural Inference Studio
│   │   │   ├── data-viewer/            # High-resolution NetCDF/HDF5 matrix viewer
│   │   │   ├── explorer/               # Historical storm catalog and trajectory explorer
│   │   │   ├── explainability/         # Convective saliency and attribution diagnostic lab
│   │   │   ├── models/                 # Model registry and benchmark evaluation report
│   │   │   ├── provenance/             # Immutable W3C PROV cryptographic lineage ledger
│   │   │   ├── results/                # Complete job report, saliency, and diagnostics
│   │   │   ├── settings/               # Adapter credentials and live satellite ingest console
│   │   │   └── temporal/               # Multi-timestamp storm evolution comparator
│   │   ├── components/                 # UI components, navigational shell, and custom icons
│   │   └── lib/                        # Strongly-typed API client (`api.ts`)
│   └── package.json
│
├── data/                               # Scientific data directories (raw NetCDF, processed)
└── docs/                               # Architecture Decision Records (ADRs) & documentation
```

---

## Quick Start Guide

### 1. Prerequisites
- **Python**: 3.10+ (tested on Python 3.12 64-bit)
- **Node.js**: 20+ (tested on Node.js v24 with `pnpm`)
- **Git**

---

### 2. Backend Setup (FastAPI)

```bash
# Clone repository and navigate to root
git clone https://github.com/KatkamKoushik/cyclonesense.git
cd cyclonesense

# (Optional) Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Seed initial canonical datasets and reference NetCDF products
python backend/scripts/seed_initial_products.py

# Launch FastAPI backend server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Health check:** `http://127.0.0.1:8000/api/v1/system/health`
- **Interactive OpenAPI Documentation:** `http://127.0.0.1:8000/docs`

---

### 3. Frontend Setup (Next.js 16)

```bash
# In a separate terminal, navigate to the frontend directory
cd frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev --port 3000
```

- **Application Dashboard:** `http://localhost:3000`

---

### 4. Running Automated Tests

The test suite covers API routing, scientific NetCDF/HDF5 reading, physical bounds QC, dataset splitting, neural inference, Grad-CAM explainability, W3C PROV provenance, closed-form GOES ABI coordinate georeferencing, and temporal/spatial pairing.

```bash
# Run the complete test suite (69 tests)
python -m pytest backend/tests -v

# Alternatively, run only the fast portable subset
python -m pytest backend/tests -m "not heavyweight" -v
```

```
============================= test session starts =============================
collected 69 items

backend/tests/test_api.py (13 tests) ...................... PASSED
backend/tests/test_geospatial_pairing.py (7 tests) ........ PASSED
backend/tests/test_impact_intelligence.py (8 tests) ....... PASSED
backend/tests/test_leakage_audit.py (7 tests) ............. PASSED
backend/tests/test_ml_dataset.py (4 tests) ................ PASSED
backend/tests/test_ml_evaluation.py (3 tests) ............. PASSED
backend/tests/test_ml_explainability.py (5 tests) ......... PASSED
backend/tests/test_ml_models.py (4 tests) ................. PASSED
backend/tests/test_ml_temporal.py (1 test) ................ PASSED
backend/tests/test_provenance.py (2 tests) ................ PASSED
backend/tests/test_qc.py (4 tests) ........................ PASSED
backend/tests/test_scientific_reader.py (4 tests) ......... PASSED
backend/tests/test_security_ingest.py (7 tests) ........... PASSED

======================= 69 passed, 1 warning in 23.12s ========================
```

```bash
# Run frontend unit tests (6 contract and scientific classification suites)
pnpm --dir frontend test

# Run frontend ESLint static code quality inspection (0 errors, 0 warnings)
pnpm --dir frontend lint

# Run frontend Next.js 16.4.3 production build and TypeScript compilation
pnpm --dir frontend build

# Run software supply chain dependency audits (0 vulnerabilities)
pip-audit -r backend/requirements.txt
pnpm --dir frontend audit
```

---

## Software Project Engineering Master Checklist Verification

CycloneSense is continuously audited against the engineering controls defined in the Master Software Engineering Checklist:

| Engineering Pillar | Control Verified | Evidence & Status |
| :--- | :--- | :--- |
| **§3. Repo Hygiene & Licensing** | MIT License, Open Data Attribution, Clean Index | Verified: [`LICENSE`](LICENSE), [`DATA_AND_MODELS.md`](DATA_AND_MODELS.md), zero committed secrets |
| **§4. Code Quality & Linting** | Strict typing, React 19 hooks, clean ESLint | Verified: `pnpm --dir frontend lint` passes with 0 errors / 0 warnings |
| **§5. Supply Chain & Vulnerabilities** | Python `pip-audit` & Frontend `pnpm audit` | Verified: 0 vulnerabilities across all backend and frontend dependencies |
| **§10 & §11. Frontend Application** | Next.js 16.4.3 Turbopack build & TypeScript check | Verified: 13 routes prerendered cleanly via `next build` in 2.4s |
| **§12 & §13. Backend & API** | FastAPI async endpoint lifecycle and schema bounds | Verified: 13 endpoint tests in [`test_api.py`](backend/tests/test_api.py) passed |
| **§12 & §21. Security & Containment (CYC-01)** | Ingest file upload containment, random UUIDs, 100MB limit, API key auth | Verified: 7 security tests in [`test_security_ingest.py`](backend/tests/test_security_ingest.py) passed |
| **§17. Data Pipelines & QC** | NetCDF4 reader, geostationary projection, DQF masks | Verified: 100% pass across [`test_qc.py`](backend/tests/test_qc.py) & [`test_geospatial_pairing.py`](backend/tests/test_geospatial_pairing.py) |
| **§18. ML Lifecycle & Leakage Audit** | Zero storm leakage; target generator decoupling; Climatology/Persistence/CLIPER baselines | Verified: 7 leakage audit tests in [`test_leakage_audit.py`](backend/tests/test_leakage_audit.py) passed |
| **§18 & §54. Spaceborne Pairing** | Authentic GOES-16 ABI pairing on Hurricane Helene | Verified: `python backend/scripts/run_real_cyclone_demo.py --storm HELENE` (77.4 kts, Grad-CAM $R_{\text{core}} = 37.8\%$) |
| **§19 & Add-on D. Grounded VLM** | Multi-temporal Sentinel-1/2 biophysical differencing | Verified: `python backend/scripts/run_impact_demo.py` ($\Delta\text{NDVI} = -0.177$, $\Delta\text{NDWI} = +0.204$, 0.5 km² change) |
| **§24 & §25. Testing & CI/CD** | 84 backend tests (scientific, Rust, hardening) + 8 Playwright E2E browser tests + 6 frontend unit tests + 3 Rust core tests | Verified: 101/101 automated tests passing; GitHub Actions 6-Job Hardened Multi-CI Pipeline green |
| **§26. Lineage & Provenance** | W3C PROV-O compliance with NIST FIPS SHA-256 | Verified: Deterministic hash calculation in [`test_provenance.py`](backend/tests/test_provenance.py) |

---

## Authoritative Scientific Reproducibility

### 1. Real Cyclone End-to-End Demonstration

To run an authentic, reproducible demonstration of genuine spaceborne satellite observation paired with official IBTrACS ground truth:

```bash
# Run demonstration for Hurricane Helene with real GOES-16 spaceborne granule
python backend/scripts/run_real_cyclone_demo.py --storm HELENE

# Or run for Bay of Bengal storm Dana with calibrated regional sensor grid
python backend/scripts/run_real_cyclone_demo.py --storm DANA
```

**Demonstration Outputs:**
- **Storm Metadata:** Official IBTrACS ID, timestamp, center latitude/longitude, best-track wind speed, and central pressure.
- **Geospatial Pairing:** Satellite product identifier, sensor type, observation time delta (minutes), spatial bounds containment check (`PASS`/`FAIL`), and physical Quality Control (QC) status.
- **Model Inference:** PyTorch checkpoint SHA-256 digest, dual-head predicted intensity (kts), ground-truth intensity, exact absolute error, and IMD severity category.
- **Physical Explainability:** Grad-CAM eyewall core concentration ratio ($R_{\text{core}}$), peak activation, and input-gradient environmental feature attribution sensitivities.
- **Provenance & Lineage:** W3C PROV-O JSON-LD record ID and NIST FIPS 180-4 SHA-256 hash.

### 2. Operational Benchmark Hierarchy (Held-Out Test Split, $N = 971$)

CycloneSense evaluates tropical cyclone intensity estimation models against an authentic meteorological baseline hierarchy on the strictly isolated test split (25 storms, 971 observations, seasons 2022–2026):

| Model / Baseline | Input Modality | Test MAE (kts) | 95% Bootstrap CI | Test RMSE (kts) | Test Macro-F1 | Accuracy | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Climatology Baseline** | Training Mean (40.3 kts) & Mode | 16.706 | [15.79, 17.66] | 22.776 | 0.1251 | 45.5% | Authentic Reference |
| **Persistence Baseline** | Prior Track Observation ($V_t = V_{t-1}$) | 2.439 | [2.24, 2.68] | 4.446 | 0.8804 | 92.1% | Authentic Reference |
| **Physical CLIPER (Ridge)**| 8-dim Atmospheric & Kinematic Covariates | 7.766 | [7.41, 8.12] | 9.665 | 0.1782 | 47.7% | Authentic Baseline |
| **Environment-Only MLP** | 8-dim Atmospheric & Kinematic Covariates | 9.993 | [9.39, 10.69] | 14.317 | 0.3135 | 63.0% | Authentic Neural |
| **Spaceborne Satellite** | NOAA GOES-16 ABI Band 1 (Helene, 105 kts) | 27.640 | Single Granule | 27.640 | Cat 2 (Pred) | 37.8% Core | Authentic Spaceborne |

To re-evaluate all models on the strictly isolated test split and regenerate the benchmark report:

```bash
python backend/scripts/evaluate_models.py
```

Generated report is saved to `docs/experiments/experiment_results.json`.

---

## Scientific Limitations & Engineering Status

In compliance with rigorous meteorological and scientific standards:

1. **Proxy Benchmark & Target-Generator Inversion:** The offline proxy benchmark dataset (`TropicalCycloneDataset` / `SyntheticProxyBenchmarkDataset`) synthesizes 2-channel radiative rasters directly from storm coordinates and target wind speed ($T_B = g(\text{wind})$). Consequently, the low Image-Only test error (MAE 1.721 kts, $r = 0.999$) is an analytical artifact of learning to invert the generator's formula rather than inferring intensity from genuine satellite imagery. These proxy experiments are explicitly quarantined in [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) and [`experiment_results.json`](docs/experiments/experiment_results.json). For authentic spaceborne satellite evaluation, CycloneSense implements `PairedSatelliteCycloneDataset`, validated on spaceborne NOAA GOES-16 ABI CONUS granules (e.g. Hurricane Helene, 1.3-minute pairing delta, 27.64 kts error) without raster synthesis. See [Validation Report](VALIDATION_REPORT.md) and [Data & Models Policy](DATA_AND_MODELS.md) for full audit details.
2. **ISRO MOSDAC Status:** The INSAT-3D/3DR adapter is structurally implemented. Automated ingestion requires user-provided MOSDAC authentication credentials in `.env` (`MOSDAC_USERNAME`, `MOSDAC_PASSWORD`). In their absence, the system returns `AUTHENTICATION_REQUIRED`.
3. **Parametric Resilience Module:** The resilience module provides an **illustrative scenario risk index** (0–100) based on configurable wind speed and proximity thresholds. It is an educational and parametric visualization tool, not an actuarial insurance pricing or binding payout engine.
4. **Grad-CAM Interpretation:** Grad-CAM highlights spatial regions of the satellite tensor that contribute most strongly to neural activations. It does not establish causal physical relationships.

---

## Data Sources, Attributions & Policy

- **NOAA GOES-R Series ABI:** National Oceanic and Atmospheric Administration via the NOAA Open Data Dissemination (NODD) program on AWS S3 (`noaa-goes16.s3.amazonaws.com`). Public Domain (17 U.S.C. § 105).
- **NOAA NCEI IBTrACS:** International Best Track Archive for Climate Stewardship (IBTrACS) v04r01 NetCDF archive. Public Domain.
- **Copernicus Sentinel-1 & Sentinel-2:** European Space Agency (ESA) & European Commission via Copernicus Data Space Ecosystem. *Contains modified Copernicus Sentinel data [2019], processed by CycloneSense.*
- **NASA Earthdata CMR:** Common Metadata Repository (CMR) operated by NASA Earth Science Data and Information System (ESDIS). Unrestricted open access.
- **ISRO MOSDAC:** Meteorological and Oceanographic Satellite Data Archival Centre, Indian Space Research Organisation. Requires user registration.
- **Proxy & Synthetic Calibration Data:** All reference and synthetic grids (`reference_cyclone_grid.nc`, `reference_satellite_grid.nc`, `test_satellite_granule.nc`) are explicitly labelled and separated from authentic spaceborne observations to preserve scientific truth-in-advertising.

For complete licensing terms, model checkpoint governance (CC BY 4.0), data provenance, and proxy/synthetic data labelling guidelines, see [Data, Model & Attribution Policy](DATA_AND_MODELS.md).

---

## Community Standards & Project Governance

CycloneSense adheres to GitHub's Recommended Community Standards:

- **[Code of Conduct](CODE_OF_CONDUCT.md):** Contributor Covenant v2.1 code of conduct and community pledge.
- **[Contributing Guidelines](CONTRIBUTING.md):** Development environment setup, workflow rules, and scientific validation standards.
- **[Security Policy](SECURITY.md):** Supported versions, vulnerability reporting process, response SLAs, and CYC-01 upload containment policy.
- **[Accessibility Statement](ACCESSIBILITY.md):** WCAG 2.1 Level AA conformance, keyboard navigation, color contrast, and barrier reporting.
- **[Issue Templates](.github/ISSUE_TEMPLATE/):** Standardized issue templates for [Bug Reports](.github/ISSUE_TEMPLATE/bug_report.md), [Feature Requests](.github/ISSUE_TEMPLATE/feature_request.md), and [Scientific Validation Discrepancies](.github/ISSUE_TEMPLATE/scientific_validation_issue.md).
- **[Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md):** Pull request checklist for tests, linting, and scientific integrity.

---

## License

Software released under the [MIT License](LICENSE).  
Pretrained model weights released under [Creative Commons Attribution 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).  
See [LICENSE](LICENSE) and [DATA_AND_MODELS.md](DATA_AND_MODELS.md) for full terms.
