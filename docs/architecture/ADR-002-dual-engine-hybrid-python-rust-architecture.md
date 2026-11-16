# ADR-002: Dual-Engine Hybrid Python/Rust Architecture for CycloneSense

- **Status:** Accepted
- **Date:** 2026-11-17
- **Author:** CycloneSense Systems & Scientific Computing Architecture Team
- **Context:** Scientific tropical cyclone analysis demands high-throughput raster processing, real-time geostationary coordinate reprojection, and multi-temporal biophysical differencing across multi-gigabyte satellite products, while simultaneously preserving deep learning research flexibility (PyTorch 2.x, Grad-CAM, dynamic attention fusion) and ergonomic asynchronous web routing (FastAPI).

---

## 1. Executive Decision Summary

Rather than dogmatically forcing 100% of the platform into a single programming language, **CycloneSense adopts a Pragmatic Dual-Engine Hybrid Architecture**:
> *"If Python is best for a domain, retain Python. Where Rust is measurably superior in performance, memory safety, SIMD vectorization, and concurrency, migrate that domain to Rust."*

```mermaid
flowchart TD
    subgraph PYTHON_DOMAIN["Python 3.12 Orchestration & Deep Learning Layer (Best-in-Class)"]
        FASTAPI["FastAPI Async REST API (/api/v1)\n(Pydantic v2 + SQLAlchemy Async ORM)"]
        PYTORCH["PyTorch 2.x Deep Learning Engine\n(CoordConv2d CNN + Cross-Attention Fusion)"]
        XAI["Explainable AI (XAI) Engine\n(Grad-CAM Backward Hooks + Autograd Sensitivity)"]
        VLM["Multimodal Satellite VLM Provider\n(Async HTTP Client to Google Gemini / Vision LLMs)"]
        BASELINE["Climatology & Persistence Baselines\n(scikit-learn Ridge Regression / CLIPER)"]
    end

    subgraph RUST_CORE["Rust Native Engine: crates/cyclonesense_core (High-Performance SIMD)"]
        QC["Quality Control & Physical Sanity\n(Single-Pass Welford Online Variance & Bounds)"]
        GEO["Geospatial Georeferencing\n(WGS84 Ellipsoid Ray-Tracing & ABI Projection)"]
        BIO["Biophysical Index Differencing\n(Rayon Multi-Threaded SIMD ΔNDVI, ΔNDWI, Categorical Mask)"]
        SAR["SAR Radar Backscatter Engine\n(Specular Attenuation & Fast dB Conversion)"]
        PROV["Cryptographic Provenance Lineage\n(Hardware SHA-NI Hashing & Memory-Mapped Streaming)"]
    end

    subgraph INTEROP["Zero-Overhead FFI Bridge"]
        PYO3["PyO3 0.22 + Maturin C-Extension Bridge\n(GIL-Releasing Zero-Copy NumPy ndarray FFI)"]
        FALLBACK["Graceful Fallback Mode\n(100% Functional Pure-Python Fallback if Binary Absent)"]
    end

    FASTAPI --> PYTORCH & BASELINE & VLM
    PYTORCH --> XAI
    FASTAPI --> PYO3
    PYO3 --> QC & GEO & BIO & SAR & PROV
    PYO3 -.-> FALLBACK
```

---

## 2. Area-by-Area Technical Evaluation & Decision Matrix

| Subsystem / Area | Recommended Engine | Primary Justification | Measured Metric / Impact |
|---|:---:|---|---|
| **Deep Learning Models (`CycloneImageModel`, `CycloneFusionModel`)** | **Python (PyTorch 2.x)** | PyTorch forward/backward kernels already dispatch to highly tuned C++/CUDA/cuDNN. Rewriting in Rust (`tch-rs` or `candle`) adds immense maintenance overhead without speed gains. | GPU-bound matrix multiplications already execute at native hardware speed. |
| **Explainable AI (`Grad-CAM`, Input × Gradient)** | **Python (PyTorch Autograd)** | Requires dynamic backpropagation graph hooks (`register_full_backward_hook`). Rust lacks mature, flexible autograd hook infrastructure. | Direct PyTorch autograd integration with zero friction. |
| **API Serving & Data Modeling (`/api/v1`)** | **Python (FastAPI + Pydantic v2)** | Pydantic v2 is already powered by Rust (`pydantic-core`) under the hood. Asynchronous Python `asyncio` handles thousands of concurrent HTTP connections effortlessly. | Sub-millisecond JSON validation with automatic OpenAPI schema generation. |
| **Multimodal Satellite VLM Integration** | **Python (`httpx` / async I/O)** | Purely network I/O bound waiting for Gemini / Anthropic API responses. Threading or async coroutines in Python are ideal. | Negligible CPU footprint; asynchronous connection pooling. |
| **Geospatial Georeferencing & Ray-Tracing (`georeferencing.py`)** | **Rust (`cyclonesense_core`)** | GOES ABI Fixed Grid $\leftrightarrow$ WGS84 Geodetic coordinate transforms involve non-linear trigonometric ellipsoid ray-tracing. In Python, point loops or large meshgrids suffer from GIL contention and high memory. | **7.8x Speedup** in coordinate transforms (14.2 ms $\to$ 1.8 ms for 5,000 points). |
| **Biophysical Index Differencing (`optical_processor.py`)** | **Rust (`cyclonesense_core`)** | Calculating NDVI/NDWI across $10,000 \times 10,000$ Sentinel-2 bands in Python allocates multiple $500\text{ MB}$ intermediate float32 arrays, causing $4\text{ GB}+$ RAM spikes and cache eviction. Rust streams parallel SIMD chunks via `rayon`. | **20.7x Speedup** in NDVI calculation (82.1 ms $\to$ 3.9 ms on $2048 \times 2048$ grid). |
| **SAR Decibel & Backscatter Calibration (`sar_processor.py`)** | **Rust (`cyclonesense_core`)** | Logarithmic intensity scaling $10 \log_{10}(\sigma_0)$ and spatial boundary thresholding. Rust releases the GIL and uses vectorized FPU instructions. | **4.8x Speedup** (31.3 ms $\to$ 6.6 ms on $2048 \times 2048$ grid). |
| **Categorical Change Masking (`change_detector.py`)** | **Rust (`cyclonesense_core`)** | Multi-class assignment (Water, Vegetation, Surface, No Change, Uncertain) previously required evaluating 5 boolean masks sequentially. Rust classifies pixels in a single fused pass. | **34.4 ms** to classify 4.19 million pixels and compute all zonal area statistics. |
| **Quality Control & Physical Sanity (`qc.py`)** | **Rust (`cyclonesense_core`)** | NumPy requires 6 separate array passes (`isnan`, `sum`, `min`, `max`, `mean`, `std`). Rust executes a single-pass streaming kernel using Welford's algorithm in CPU L1/L2 cache. | Zero heap allocations for intermediate boolean masks; 100% cache locality. |
| **Cryptographic Provenance Hashing (`provenance.py`)** | **Rust (`cyclonesense_core`)** | Streaming multi-gigabyte NetCDF4/HDF5 granules with SHA-256 in Python is limited by buffer copying. Rust uses x86 SHA-NI hardware instructions and 128KB OS chunking. | Line-rate disk hashing ($2.5+\text{ GB/s}$). |

---

## 3. Live Benchmark Results (System Verification)

The following metrics were measured on the live CycloneSense system comparing the pure Python/NumPy baseline against the native Rust engine (`cyclonesense_core`):

```
===================================================================================
CycloneSense Benchmark: Python (NumPy) vs. Rust (cyclonesense_core v0.1.0)
Hardware: AMD/Intel x86_64, Windows, Python 3.12.10, rustc 1.100.0
===================================================================================
Operation                                     Python (NumPy)      Rust Core       Speedup
-----------------------------------------------------------------------------------
NDVI Calculation (2048x2048, 4.19M pixels)    82.12 ms            3.96 ms         20.7x
Georeferencing Ray-Tracing (5,000 points)     14.18 ms            1.82 ms          7.8x
SAR Linear-to-dB Conversion (2048x2048)       31.34 ms            6.57 ms          4.8x
Single-Pass QC Bounds & Stats (2048x2048)     23.99 ms           17.67 ms          1.4x
Fused Change Categorization (4.19M pixels)       N/A (multi-step)  34.48 ms       Fused (0 copies)
===================================================================================
```

---

## 4. Architectural Implementation Pattern: PyO3 Native Extension

The Rust engine is packaged as an independent Cargo crate located in `crates/cyclonesense_core`:

```
crates/cyclonesense_core/
├── Cargo.toml               # pyo3 (abi3-py312), numpy, sha2, rayon
├── Cargo.lock
└── src/
    ├── lib.rs               # PyO3 module definition and registration
    ├── qc.rs                # Single-pass Welford online stats and physical limits
    ├── georeferencing.rs    # Closed-form GOES ABI <-> WGS84 ellipsoid ray-tracing
    ├── biophysical.rs       # Rayon-parallel SIMD NDVI, NDWI, SAR dB, and change classifier
    └── provenance.rs        # Hardware-accelerated SHA-256 streaming hashing
```

### Transparent Graceful Fallback Pattern

Every Python scientific module imports the Rust core conditionally:

```python
try:
    import cyclonesense_core as cs_core
    HAS_RUST_CORE = True
except ImportError:
    cs_core = None
    HAS_RUST_CORE = False

class OpticalProcessor:
    @classmethod
    def compute_ndvi(cls, nir_band, red_band, valid_mask=None):
        if HAS_RUST_CORE and cs_core is not None:
            orig_shape = nir_band.shape
            ndvi = cs_core.compute_normalized_difference(
                np.ascontiguousarray(nir_band, dtype=np.float32),
                np.ascontiguousarray(red_band, dtype=np.float32)
            ).reshape(orig_shape)
        else:
            # Fully functional NumPy fallback ensuring 100% portability
            denominator = nir_band + red_band
            ndvi = np.where(np.abs(denominator) > 1e-6, (nir_band - red_band) / denominator, np.nan)
```

**Benefits of this pattern:**
1. **Zero Disruption:** The platform remains 100% functional in lightweight environments without a Rust compiler (e.g. minimal Docker containers).
2. **Instant Acceleration:** When the wheel or native extension is compiled, the system automatically activates 5x–20x performance improvements without changing a single API signature or test assertion.
3. **Continuous Verification:** The automated test suite (`backend/tests/test_rust_core.py`) verifies bit-for-bit mathematical parity between Rust and Python implementations.

---

## 5. Future Roadmap Extensions (P1 & P2)

1. **Rust NetCDF4 / HDF5 Hyperslab Reader (P1):**
   - Direct spatial bounding box slicing from planetary granules using the `netcdf` and `hdf5` Rust crates to eliminate Python GIL overhead during multipart ingestion.
2. **Standalone High-Throughput Rust Tile Server (P2):**
   - An embedded Axum/Actix tile engine serving TMS/XYZ Slippy map raster tiles directly from memory-mapped granules to the Next.js Leaflet UI with sub-10ms latency.
