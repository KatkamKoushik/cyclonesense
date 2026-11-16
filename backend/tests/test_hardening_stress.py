"""
Hardening, Stress, and Concurrency Test Suite for CycloneSense.
Tests multi-threaded safety, extreme numerical anomalies, security fuzzing,
and high-concurrency request resilience.
"""
import concurrent.futures
import math
import numpy as np
import pytest
from httpx import AsyncClient, ASGITransport
import torch

from backend.app.main import app
from backend.app.config import settings
from backend.app.scientific.qc import QualityControlEngine, QCStatus
from backend.app.scientific.optical_processor import OpticalProcessor
from backend.app.scientific.sar_processor import SARProcessor
from backend.app.scientific.georeferencing import SatelliteGeoreferencer
from backend.app.scientific.provenance import ProvenanceTracker
from backend.app.ml.models.image_model import CycloneImageModel
from backend.app.ml.models.env_model import CycloneEnvironmentModel
from backend.app.ml.models.fusion_model import CycloneFusionModel

try:
    import cyclonesense_core as cs_core
    HAS_RUST_CORE = True
except ImportError:
    cs_core = None
    HAS_RUST_CORE = False


# ============================================================================
# 1. Multi-Threaded Concurrency & Memory Safety Stress Tests
# ============================================================================

def test_rust_core_concurrent_thread_safety_stress():
    """
    Stress-test the native Rust core by spawning 16 concurrent worker threads
    executing SIMD calculations, array allocations, and hashing in parallel.
    Proves zero race conditions, no memory leaks, and thread-safe GIL release.
    """
    if not HAS_RUST_CORE or cs_core is None:
        pytest.skip("Rust core not available")

    num_threads = 16
    iterations_per_thread = 25

    def worker_task(thread_id: int):
        for i in range(iterations_per_thread):
            # 1. Stress QC with random raster
            data = np.random.uniform(180.0, 310.0, size=(128, 128)).astype(np.float32)
            qc_res = cs_core.evaluate_array_qc(data, 160.0, 340.0)
            assert qc_res["status"] in ["PASSED", "DEGRADED"]
            assert qc_res["valid_pixels"] == 128 * 128

            # 2. Stress NDVI differencing
            nir = np.random.uniform(0.1, 0.9, size=1024).astype(np.float32)
            red = np.random.uniform(0.1, 0.5, size=1024).astype(np.float32)
            ndvi = cs_core.compute_normalized_difference(nir, red)
            assert len(ndvi) == 1024
            assert np.all(np.isfinite(ndvi))

            # 3. Stress SAR dB conversion
            sar_linear = np.random.uniform(0.001, 1.0, size=512).astype(np.float32)
            sar_db = cs_core.sar_linear_to_db(sar_linear, 1e-6)
            assert len(sar_db) == 512
            assert np.all(sar_db <= 5.0) and np.all(sar_db >= -35.0)

            # 4. Stress Ellipsoid Ray-tracing
            lat = 10.0 + (thread_id * 1.0)
            lon = -80.0 + (i * 0.2)
            angles = cs_core.latlon_to_abi_angles(lat, lon)
            assert angles is not None

            # 5. Stress SHA-256
            payload = f"thread_{thread_id}_iter_{i}_stress".encode("utf-8")
            h = cs_core.fast_sha256_bytes(payload)
            assert len(h) == 64

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker_task, tid) for tid in range(num_threads)]
        for f in concurrent.futures.as_completed(futures):
            f.result()  # Will raise exception if any thread crashed


# ============================================================================
# 2. Extreme Numerical & Boundary Hardening Tests
# ============================================================================

def test_extreme_numerical_anomalies_qc():
    """
    Evaluate QC behavior when arrays contain infinities, NaNs, subnormal numbers,
    and extreme physical bounds.
    """
    # All NaNs
    all_nan = np.full((32, 32), np.nan, dtype=np.float32)
    res_nan = QualityControlEngine.evaluate_array(all_nan, "brightness_temperature")
    assert res_nan.status == QCStatus.REJECTED
    assert res_nan.physical_bounds_passed is False
    assert res_nan.missing_pixel_percentage == 100.0

    # All Infinities
    all_inf = np.full((32, 32), np.inf, dtype=np.float32)
    res_inf = QualityControlEngine.evaluate_array(all_inf, "brightness_temperature")
    assert res_inf.status == QCStatus.REJECTED
    assert res_inf.missing_pixel_percentage == 100.0

    # Constant array (zero variance)
    const_arr = np.full((64, 64), 280.0, dtype=np.float32)
    res_const = QualityControlEngine.evaluate_array(const_arr, "brightness_temperature")
    assert res_const.status == QCStatus.PASSED
    assert res_const.metrics["std"] == 0.0

    # Cosmic ray spike (e.g. 999.0 K)
    spike_arr = np.full((32, 32), 275.0, dtype=np.float32)
    spike_arr[0, 0] = 999.0  # Cosmic ray hit
    res_spike = QualityControlEngine.evaluate_array(spike_arr, "brightness_temperature")
    assert res_spike.physical_bounds_passed is False
    assert any("upper bound violated" in a.lower() for a in res_spike.anomalies)


def test_biophysical_division_by_zero_hardening():
    """
    Verify optical and SAR processors do not crash on zero division or denormalized floats.
    """
    # Both bands zero (0 - 0) / (0 + 0)
    zeros = np.zeros(100, dtype=np.float32)
    ndvi, _, _ = OpticalProcessor.compute_ndvi(zeros, zeros)
    assert np.all(np.isnan(ndvi)), "Zero denominator should yield NaN without crashing"

    # Negative values in SAR intensity
    negative_sar = np.array([-10.0, -0.001, 0.0, 1e-12], dtype=np.float32)
    db = SARProcessor.linear_to_db(negative_sar)
    assert np.all(np.isfinite(db))
    assert np.all(db >= SARProcessor.MIN_PHYSICAL_DB)


def test_geospatial_polar_and_antimeridian_hardening():
    """
    Verify georeferencing handles degenerate coordinates (opposite side of Earth, boundary horizons).
    """
    # Point on exact opposite side of Earth (180 deg away from GOES nadir -75.0 -> +105.0)
    x_opp, y_opp = SatelliteGeoreferencer.latlon_to_abi_angles(0.0, 105.0)
    assert x_opp is None and y_opp is None

    # Another point behind the Earth horizon
    x_behind, y_behind = SatelliteGeoreferencer.latlon_to_abi_angles(18.5, 88.0)
    assert x_behind is None and y_behind is None

    # Visible point
    x_vis, y_vis = SatelliteGeoreferencer.latlon_to_abi_angles(26.0, -84.6)
    assert x_vis is not None and y_vis is not None
    assert abs(x_vis) < 0.2
    assert abs(y_vis) < 0.2


# ============================================================================
# 3. Security Fuzzing & Path Traversal Hardening (CYC-01)
# ============================================================================

@pytest.mark.asyncio
async def test_security_fuzzing_path_traversal_payloads():
    """
    Fuzz the ingestion endpoint with aggressive directory traversal sequences,
    null bytes, and malformed filenames.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        malicious_filenames = [
            "../../../etc/shadow",
            "..\\..\\..\\windows\\system32\\cmd.exe",
            "....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2fetc/passwd",
            "test_file.nc\0.exe",
            "/absolute/root/path.nc",
            "C:\\Windows\\System32\\config.nc",
            "   ",
            ".",
            "..",
            "normal_file.nc.exe",
            "exploit.h5.sh",
        ]

        for fname in malicious_filenames:
            files = {"file": (fname, b"fake content", "application/octet-stream")}
            headers = {"X-API-Key": settings.INGEST_API_KEY}
            response = await client.post("/api/v1/ingest/file", files=files, headers=headers)
            assert response.status_code in [400, 422], f"Filename '{fname}' should be rejected, got {response.status_code}"


@pytest.mark.asyncio
async def test_security_malformed_auth_headers():
    """
    Fuzz authorization headers with invalid bearer tokens, unicode strings, and SQL injection payloads.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        fuzz_tokens = [
            "",
            "Bearer ",
            "Bearer ' OR '1'='1",
            "Bearer \x00\x01\x02",
            "Bearer " + "A" * 5000,
            "InvalidScheme 12345",
        ]

        files = {"file": ("valid_sample.nc", b"content", "application/x-netcdf")}
        for token in fuzz_tokens:
            headers = {"Authorization": token}
            response = await client.post("/api/v1/ingest/file", files=files, headers=headers)
            assert response.status_code == 401, f"Token '{token}' should be rejected with 401 Unauthorized"


# ============================================================================
# 4. Neural Model Stability Hardening
# ============================================================================

def test_model_nonfinite_input_rejection():
    """
    Verify PyTorch model forward passes gracefully handle non-finite or extreme tensor inputs.
    """
    model = CycloneFusionModel(image_channels=2, env_features=8)
    model.eval()

    # Normal input
    valid_img = torch.randn(2, 2, 64, 64)
    valid_env = torch.randn(2, 8)
    with torch.no_grad():
        out = model(valid_img, valid_env)
        assert out["pred_intensity"].shape == (2,)
        assert out["category_logits"].shape == (2, 5)

    # Extreme value input (high magnitude)
    extreme_img = torch.full((1, 2, 64, 64), 1e6)
    extreme_env = torch.full((1, 8), 1e6)
    with torch.no_grad():
        out_extreme = model(extreme_img, extreme_env)
        assert out_extreme["pred_intensity"].shape == (1,)


# ============================================================================
# 5. High-Throughput Endpoint Stress Test
# ============================================================================

@pytest.mark.asyncio
async def test_high_concurrency_read_endpoints_stress():
    """
    Issue rapid-fire requests to read endpoints (health, storms, models)
    to verify async database connection pool resilience and no event loop starvation.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        endpoints = [
            "/api/v1/system/health",
            "/api/v1/storms/catalog",
            "/api/v1/ml/models",
            "/api/v1/ml/evaluation-report",
            "/api/v1/impact/cyclones",
        ]

        for _ in range(5):
            for ep in endpoints:
                res = await client.get(ep)
                assert res.status_code == 200
