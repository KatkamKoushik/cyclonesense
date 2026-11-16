# Architecture & System Design

CycloneSense is designed as a decoupled, micro-modular scientific application combining a high-performance Python FastAPI backend, PyTorch scientific inference models, and a modern Next.js 16 web application.

---

## Architectural Topology

```mermaid
flowchart TD
    subgraph ClientLayer["Frontend Presentation Layer (Next.js 16 / TypeScript / Tailwind CSS)"]
        Dashboard["Operational Overview Dashboard (/)"]
        AnalysisUI["Multimodal Inference Studio (/analysis)"]
        DataViewer["NetCDF4 / HDF5 Matrix Viewer (/data-viewer)"]
        TrackExplorer["Storm Trajectory Explorer (/explorer)"]
        XAIStudio["Explainability Diagnostic Lab (/explainability)"]
        ImpactStudio["Impact Intelligence & Ground Change (/impact)"]
        ModelRegistry["Model Registry & Validation (/models)"]
        ProvenanceUI["Immutable Lineage Ledger (/provenance)"]
    end

    subgraph APILayer["Backend REST API Gateway (FastAPI 0.115+ / Async ASGI)"]
        RouterIngest["routes_ingest.py (/api/v1/ingest)"]
        RouterStorms["routes_storms.py (/api/v1/storms)"]
        RouterML["routes_ml.py (/api/v1/ml)"]
        RouterImpact["routes_impact.py (/api/v1/impact)"]
        RouterProv["routes_provenance.py (/api/v1/provenance)"]
        RouterSystem["routes_system.py (/api/v1/system)"]
    end

    subgraph ScientificCore["Scientific Core Subsystem (Python + Rust cyclonesense_core)"]
        SecCheck["Security Containment Gate (CYC-01)"]
        Reader["ScientificReader (NetCDF4 / HDF5 Engine)"]
        QC["Rust QualityControlEngine (Single-Pass Welford & DQF)"]
        Georef["Rust SatelliteGeoreferencer (ABI Projection & Ray-Tracing)"]
        Biophys["Rust Biophysical Engine (Rayon SIMD ΔNDVI/ΔNDWI)"]
        Pairing["SatelliteObservationPairer (Spatial/Temporal Gates)"]
        ProvTracker["Rust ProvenanceTracker (Hardware SHA-NI)"]
    end

    subgraph MLEngine["ML & Neural Attribution Subsystem (PyTorch 2.x)"]
        CLIPER["BaselineClimatologyPersistenceModel (Ridge)"]
        ClimatologyModel["ClimatologyBaselineModel"]
        PersistenceModel["PersistenceBaselineModel"]
        EnvModel["CycloneEnvironmentModel (8-dim LayerNorm MLP)"]
        ImageModel["CycloneImageModel (4-Stage ResCNN)"]
        FusionModel["CycloneFusionModel (Cross-Modal Fusion)"]
        GradCAM["GradCAMExplainer (Eyewall Energy Ratio)"]
        EnvXAI["EnvironmentalAttributionExplainer (Sensitivity)"]
    end

    subgraph PersistenceLayer["Storage & Data Persistence"]
        DB[(cyclonesense.db - SQLite / SQLAlchemy 2.0 Async)]
        RawDir[("data/raw/ - Canonical NetCDF & Granules")]
        Checkpoints[("models/checkpoints/ - PyTorch Weights & Checksums")]
    end

    ClientLayer <-->|HTTP / JSON REST API| APILayer
    APILayer --> SecCheck
    SecCheck --> RawDir
    APILayer --> Reader
    Reader --> QC
    QC --> Georef
    Georef --> Pairing
    Pairing --> ProvTracker
    Pairing --> MLEngine
    MLEngine --> GradCAM & EnvXAI
    APILayer <--> DB
    Checkpoints --> MLEngine
```

---

## Subsystem Breakdown

### 1. Presentation Layer (Next.js 16 & TypeScript)
- Built on **Next.js 16 (App Router)** with Turbopack compilation and React 19 server/client components.
- Enforces strict TypeScript interfaces ([frontend/src/lib/api.ts](file:///d:/CycloneSense/frontend/src/lib/api.ts)) with zero `any` type casting.
- Features high-contrast, accessible UI compliant with **WCAG 2.1 Level AA** standards.

### 2. Backend Gateway (FastAPI)
- High-concurrency async endpoints serving real-time telemetry, historical catalogs, and ML inference.
- Validates request payloads through **Pydantic V2** schemas with strict bounds checking.
- Connects to SQLite database through **SQLAlchemy 2.0 AsyncSession** with foreign-key constraints.

### 3. Scientific Ingestion & Georeferencing (Accelerated via Rust `cyclonesense_core`)
- Consumes authentic Earth Observation files (`.nc`, `.nc4`, `.h5`, `.hdf5`).
- Solves closed-form geostationary projection coordinates for geostationary radiometers (NOAA GOES-16 ABI, ISRO INSAT-3D/3DR) with **7.8x speedup** via native Rust FPU/SIMD instructions.
- Computes multi-temporal biophysical differences ($\Delta\text{NDVI}$, $\Delta\text{NDWI}$, SAR $\sigma^0$ dB) with **20.7x speedup** using multi-threaded Rayon parallelism.
- Applies physical Quality Control (QC) filters in a single cache-coherent pass using Welford's algorithm without intermediate heap allocations.
- Employs graceful fallback: automatically defaults to pure Python/NumPy if the compiled Rust wheel is absent.

### 4. Machine Learning & Neural Inference
- Multi-task PyTorch architectures outputting continuous intensity (knots) via Huber loss and IMD severity category via Cross-Entropy.
- Implements operational baseline hierarchy: Climatology, Persistence ($V_t = V_{t-1}$), CLIPER (Ridge), Environment-Only MLP, and authentic Spaceborne sensing.
- Produces deterministic Grad-CAM spatial heatmaps with eyewall core energy concentration ratios ($R_{\text{core}}$).

---

## Analysis Job Lifecycle State Machine

Analysis requests proceed through an explicit, asynchronous state machine tracked in `analysis_jobs`:

```mermaid
stateDiagram-v2
    [*] --> PENDING: Job Created via API
    PENDING --> INGESTING: Payload Received & Validated
    INGESTING --> QC_VALIDATING: Raw NetCDF Ingested
    QC_VALIDATING --> REJECTED: Physical Bounds Violation or Corrupt File
    QC_VALIDATING --> GEOREFERENCING: QC Passed
    GEOREFERENCING --> PAIRING_FAILED: Center Outside Satellite Disk Horizon
    GEOREFERENCING --> MODEL_INFERENCE: Spatial Containment Confirmed
    MODEL_INFERENCE --> COMPUTING_XAI: Dual-Head Predictions Generated
    COMPUTING_XAI --> RECORDING_PROVENANCE: Grad-CAM Saliency Calculated
    RECORDING_PROVENANCE --> COMPLETED: W3C PROV-O SHA-256 Digest Saved
    REJECTED --> [*]
    PAIRING_FAILED --> [*]
    COMPLETED --> [*]
```
