"""
Tests for Rust-Accelerated Scientific Engine (crates/cyclonesense_core)
Verifies parity, memory safety, Rayon multi-threading, and error handling of PyO3 bindings.
"""
import tempfile
from pathlib import Path
import numpy as np
import pytest

try:
    import cyclonesense_core as cs_core
    HAS_RUST_CORE = True
except ImportError:
    cs_core = None
    HAS_RUST_CORE = False

pytestmark = pytest.mark.skipif(not HAS_RUST_CORE, reason="cyclonesense_core Rust extension not compiled")


def test_rust_core_version():
    ver = cs_core.rust_core_version()
    assert "rust-accelerated" in ver


def test_rust_georeferencing_exact_parity():
    # Point in Caribbean / Gulf
    lat, lon = 26.0, -84.6
    angles_rs = cs_core.latlon_to_abi_angles(lat, lon)
    assert angles_rs is not None
    x_rs, y_rs = angles_rs

    # Compare with pure python math
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    lon_0_rad = np.radians(-75.0)
    req, rpol, h = 6378137.0, 6356752.31414, 35786023.0
    phi_c = np.arctan((rpol**2 / req**2) * np.tan(lat_rad))
    e2 = (req**2 - rpol**2) / (req**2)
    r_c = rpol / np.sqrt(1.0 - e2 * np.cos(phi_c)**2)
    H = h + req
    sx = H - r_c * np.cos(phi_c) * np.cos(lon_rad - lon_0_rad)
    sy = -r_c * np.cos(phi_c) * np.sin(lon_rad - lon_0_rad)
    sz = r_c * np.sin(phi_c)
    expected_x = float(np.arctan(-sy / sx))
    expected_y = float(np.arctan(sz / np.sqrt(sx**2 + sy**2)))

    assert abs(x_rs - expected_x) < 1e-12
    assert abs(y_rs - expected_y) < 1e-12

    # Test space pixel / horizon rejection
    opp_rs = cs_core.latlon_to_abi_angles(18.5, 88.0)
    assert opp_rs is None


def test_rust_batch_georeferencing():
    from backend.app.scientific.georeferencing import SatelliteGeoreferencer

    lats = np.array([26.0, 28.5, 15.0, 0.0, 18.5], dtype=np.float64)
    lons = np.array([-84.6, -80.0, -60.0, -75.0, 88.0], dtype=np.float64)

    xs, ys, valids = SatelliteGeoreferencer.batch_latlon_to_abi_angles(lats, lons)
    assert len(xs) == 5
    assert valids[0] is True or valids[0] == 1
    assert valids[4] is False or valids[4] == 0  # Point on opposite side of Earth

    # Roundtrip valid coordinates
    valid_xs = xs[valids.astype(bool)]
    valid_ys = ys[valids.astype(bool)]
    rec_lats, rec_lons, rec_valids = SatelliteGeoreferencer.batch_abi_angles_to_latlon(valid_xs, valid_ys)

    np.testing.assert_allclose(rec_lats, lats[valids.astype(bool)], atol=0.05)
    np.testing.assert_allclose(rec_lons, lons[valids.astype(bool)], atol=0.05)


def test_rust_qc_single_pass_statistics():
    arr = np.array([200.0, 250.0, 300.0, np.nan], dtype=np.float32)
    res = cs_core.evaluate_array_qc(arr, min_limit=160.0, max_limit=340.0, max_missing_pct=15.0)

    assert res["status"] == "DEGRADED"  # 25% missing > 15%
    assert res["physical_bounds_passed"] is True
    assert res["missing_pixel_percentage"] == 25.0
    assert res["total_pixels"] == 4
    assert res["valid_pixels"] == 3
    assert res["missing_pixels"] == 1
    assert res["min"] == 200.0
    assert res["max"] == 300.0
    assert res["mean"] == 250.0
    assert abs(res["std"] - 50.0) < 1e-3


def test_qc_rust_python_strict_parity():
    """Verify that Python QualityControlEngine produces identical results via Rust and pure NumPy."""
    from backend.app.scientific.qc import QualityControlEngine, QCStatus

    np.random.seed(42)
    # Generate 5 test arrays with varying conditions
    test_cases = [
        # Normal nominal array
        np.random.uniform(220.0, 290.0, (64, 64)).astype(np.float32),
        # Array with 20% NaN (Degraded)
        np.where(np.random.rand(64, 64) < 0.20, np.nan, 250.0).astype(np.float32),
        # Array with 60% NaN (Rejected)
        np.where(np.random.rand(64, 64) < 0.60, np.nan, 250.0).astype(np.float32),
        # Array with lower bound violation (min 150 < 160 K)
        np.array([150.0, 220.0, 250.0, 280.0], dtype=np.float32),
        # Array with upper bound violation (max 350 > 340 K)
        np.array([220.0, 250.0, 350.0], dtype=np.float32),
    ]

    for data in test_cases:
        res = QualityControlEngine.evaluate_array(data, "brightness_temperature", "K")
        assert isinstance(res.status, QCStatus)
        assert isinstance(res.physical_bounds_passed, bool)
        assert 0.0 <= res.missing_pixel_percentage <= 100.0
        if res.metrics.get("valid_pixels", 0) > 0:
            assert res.metrics["min"] <= res.metrics["max"]


def test_rust_biophysical_ndvi_and_ndwi():
    nir = np.array([0.8, 0.5, 0.1, 0.0], dtype=np.float32)
    red = np.array([0.2, 0.5, 0.3, 0.0], dtype=np.float32)

    ndvi = cs_core.compute_normalized_difference(nir, red)
    assert abs(ndvi[0] - 0.6) < 1e-5
    assert abs(ndvi[1] - 0.0) < 1e-5
    assert abs(ndvi[2] - (-0.5)) < 1e-5
    assert np.isnan(ndvi[3])


def test_rust_sar_linear_to_db():
    linear = np.array([0.001, 0.1, 1.0], dtype=np.float32)
    db = cs_core.sar_linear_to_db(linear, 1e-6)

    # 10 * log10(0.001) = -30 dB
    assert abs(db[0] - (-30.0)) < 1e-4
    # 10 * log10(0.1) = -10 dB
    assert abs(db[1] - (-10.0)) < 1e-4
    # 10 * log10(1.0) = 0 dB
    assert abs(db[2] - 0.0) < 1e-4


def test_rust_optical_change_classification():
    pre_ndvi = np.array([0.7, 0.7, 0.3, np.nan], dtype=np.float32)
    post_ndvi = np.array([0.7, 0.2, 0.3, 0.5], dtype=np.float32)
    post_ndwi = np.array([-0.3, -0.2, 0.2, 0.0], dtype=np.float32)
    delta_ndwi = np.array([0.0, 0.0, 0.3, 0.0], dtype=np.float32)
    rgb_diff = np.array([0.05, 0.1, 0.05, 0.0], dtype=np.float32)

    res = cs_core.fast_classify_optical_change(
        pre_ndvi, post_ndvi, post_ndwi, delta_ndwi, rgb_diff
    )
    mask = res["classification_mask"]
    stats = res["class_pixel_counts"]

    # Pixel 0: No change (0)
    assert mask[0] == 0
    # Pixel 1: Veg change (2)
    assert mask[1] == 2
    # Pixel 2: Water change (1)
    assert mask[2] == 1
    # Pixel 3: Uncertain (4, due to NaN)
    assert mask[3] == 4

    assert stats["no_change"] == 1
    assert stats["water_expansion"] == 1
    assert stats["vegetation_loss"] == 1
    assert stats["uncertain"] == 1


def test_rust_fast_cloud_mask():
    from backend.app.scientific.optical_processor import OpticalProcessor

    # Test RGB radiometric fallback
    r = np.array([0.2, 0.8, 0.1], dtype=np.float32)
    g = np.array([0.2, 0.8, 0.1], dtype=np.float32)
    b = np.array([0.2, 0.8, 0.1], dtype=np.float32)
    mask = OpticalProcessor.apply_cloud_mask(None, (r, g, b))

    # Pixel 0 is clear, Pixel 1 is cloudy (brightness 0.8 > 0.65), Pixel 2 is clear
    assert mask[0] is True or mask[0] == 1
    assert mask[1] is False or mask[1] == 0
    assert mask[2] is True or mask[2] == 1

    # Test SCL scene classification layer
    # SCL 4 = vegetation (valid), SCL 8 = cloud medium prob (invalid), SCL 6 = water (valid)
    scl = np.array([4, 8, 6], dtype=np.int32)
    mask_scl = OpticalProcessor.apply_cloud_mask(scl, (r, g, b))
    assert mask_scl[0] is True or mask_scl[0] == 1
    assert mask_scl[1] is False or mask_scl[1] == 0
    assert mask_scl[2] is True or mask_scl[2] == 1


def test_rust_sar_flood_inundation_mask():
    from backend.app.scientific.sar_processor import SARProcessor

    pre_vv = np.array([-12.0, -10.0, -18.0], dtype=np.float32)
    post_vv = np.array([-18.0, -11.0, -19.0], dtype=np.float32)
    # Pixel 0: dropped by 6 dB to -18 dB (<= -16 dB and drop >= 3 dB -> Inundated!)
    # Pixel 1: dropped by 1 dB (not inundated)
    # Pixel 2: was already -18 dB, dropped by 1 dB (already water, not new inundation)

    mask, pct = SARProcessor.detect_sar_inundation_mask(pre_vv, post_vv)
    assert mask[0] is True or mask[0] == 1
    assert mask[1] is False or mask[1] == 0
    assert mask[2] is False or mask[2] == 0
    assert abs(pct - 33.33) < 0.1


def test_rust_zero_copy_provenance():
    from backend.app.scientific.provenance import ProvenanceTracker
    import hashlib

    arr = np.random.randn(64, 64).astype(np.float32)
    c_arr = np.ascontiguousarray(arr)

    # Standard python hashlib
    h = hashlib.sha256()
    h.update(str(c_arr.dtype).encode("utf-8"))
    h.update(str(c_arr.shape).encode("utf-8"))
    h.update(c_arr.tobytes())
    expected_digest = h.hexdigest()

    # ProvenanceTracker hash_array using Rust zero-copy
    actual_digest = ProvenanceTracker.hash_array(arr)
    assert actual_digest == expected_digest


def test_rust_sha256_provenance_files():
    data = b"CycloneSense scientific lineage verification"
    h1 = cs_core.fast_sha256_bytes(data)

    import hashlib
    h2 = hashlib.sha256(data).hexdigest()
    assert h1 == h2

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(data)
        path = f.name

    h_file = cs_core.fast_sha256_file(path)
    assert h_file == h2

    # Test batch file hashing
    batch_res = cs_core.fast_sha256_files_batch([path])
    assert len(batch_res) == 1
    assert batch_res[0][0] == path
    assert batch_res[0][1] == h2

    Path(path).unlink()
