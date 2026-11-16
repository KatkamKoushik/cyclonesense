# Welcome to the CycloneSense Wiki

> **CycloneSense** is an authentic, explainable meteorological intelligence research platform engineered to ingest, quality-control, georeference, and analyze tropical cyclone patterns directly from scientific Earth Observation (EO) satellite products (NetCDF4, HDF5) and authoritative best-track archives (NOAA IBTrACS).

This Wiki serves as the comprehensive engineering, scientific, and operational reference for CycloneSense, detailing our system architecture, physical validation gates, zero-leakage storm splitting, baseline hierarchies, and security controls.

---

## Technical Wiki Sitemap

```mermaid
flowchart TD
    Home["Wiki Portal (Home.md)"]

    subgraph CoreScience["Scientific Core & Validation"]
        DataPipeline["Data Pipeline & QC (Scientific-Data-Pipeline-and-QC.md)"]
        Benchmarks["Model Benchmarks (Model-Benchmarks-and-Validation.md)"]
        Explainability["Explainability & XAI (Explainability-and-Attribution.md)"]
        Impact["Impact Intelligence (Impact-Intelligence-and-Biophysical-Differencing.md)"]
    end

    subgraph Engineering["System Engineering & Security"]
        Architecture["Architecture & Design (Architecture-and-System-Design.md)"]
        Security["Security & Containment (Security-and-Containment-CYC-01.md)"]
        Runbook["Runbook & API Reference (Operational-Runbook-and-API-Reference.md)"]
    end

    Home --> Architecture
    Home --> DataPipeline
    Home --> Benchmarks
    Home --> Explainability
    Home --> Impact
    Home --> Security
    Home --> Runbook
```

---

## End-to-End Scientific Workflow at a Glance

The following sequence diagram traces an authentic observation from raw Earth observation satellite ingestion to cryptographic provenance recording:

```mermaid
sequenceDiagram
    autonumber
    actor User as Scientist / Operator
    participant API as FastAPI Ingest Gateway
    participant Sec as Security Gate (CYC-01)
    participant Reader as ScientificReader
    participant QC as QualityControlEngine
    participant Pairer as Georeferencing & Pairing
    participant Model as PyTorch Inference Engine
    participant XAI as Grad-CAM & XAI Explainer
    participant Prov as ProvenanceTracker (W3C PROV)

    User->>API: POST /api/v1/ingest/file (NetCDF4 / HDF5 + API Key)
    API->>Sec: Validate Path, Extension (.nc/.h5), Stream Size (<=100MB)
    Sec-->>API: Server-Side UUID Storage Path (DATA_RAW_DIR)
    API->>Reader: Inspect Metadata & CF-1.8 Attributes
    Reader-->>API: Extracted Array & Dimensions
    API->>QC: Check Physical Sanity (160K <= Tb <= 340K, DQF Masks)
    QC-->>API: QC Status (PASS / REJECT)
    API->>Pairer: Match IBTrACS Center (Lat/Lon) with ABI Projection
    Pairer-->>API: Calibrated 64x64 Tensor + Pairing Status (ACCEPTED)
    API->>Model: Dual-Head Forward Pass (Intensity + IMD Severity)
    Model-->>API: Continuous Wind (kts) + Categorical Logits
    API->>XAI: Compute Grad-CAM Saliency & Core Concentration Ratio
    XAI-->>API: Eyewall Energy Ratio (R_core) & Saliency Hash
    API->>Prov: Generate W3C PROV-O Lineage Record (SHA-256)
    Prov-->>API: Provenance UUID & Immutable Record
    API-->>User: Complete Scientific Response Payload
```

---

## Navigation & Quick Reference

| Wiki Guide | Key Capabilities Covered |
| :--- | :--- |
| **[System Architecture](Architecture-and-System-Design.md)** | Subsystem boundaries, FastAPI backend, Next.js 16 frontend, SQLite/SQLAlchemy layer, data-flow topologies, and **Rust Native SIMD Core (`cyclonesense_core`)**. |
| **[Scientific Data Pipeline & QC](Scientific-Data-Pipeline-and-QC.md)** | CF-compliant NetCDF4/HDF5 reader, closed-form geostationary coordinate projection, spatial-temporal pairing gates. |
| **[Model Benchmarks & Validation](Model-Benchmarks-and-Validation.md)** | Zero-leakage temporal storm partitioning (157 storms, 7,229 obs), operational baseline hierarchy, target leakage audit. |
| **[Explainability & Grad-CAM](Explainability-and-Attribution.md)** | Spatial convective core concentration ratio ($R_{\text{core}}$), peak activation, input-gradient environmental sensitivities. |
| **[Impact Intelligence & Differencing](Impact-Intelligence-and-Biophysical-Differencing.md)** | Multi-temporal Sentinel-1 SAR ($\sigma^0$) & Sentinel-2 optical ($\Delta\text{NDVI}$, $\Delta\text{NDWI}$) biophysical change detection. |
| **[Security & Containment (CYC-01)](Security-and-Containment-CYC-01.md)** | Server-side random UUID storage, path containment within `DATA_RAW_DIR`, chunked 100MB upload aborts, API key auth. |
| **[Operational Runbook & API Reference](Operational-Runbook-and-API-Reference.md)** | CLI scripts, endpoint specs, test suites, troubleshooting, and error resolution. |
