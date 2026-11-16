import io
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.config import settings
from backend.app.main import app
from backend.app.db.session import init_db
from backend.app.scientific.grid_product_generator import create_reference_satellite_grid_netcdf


@pytest.fixture(autouse=True)
async def setup_database():
    await init_db()


@pytest.mark.asyncio
async def test_unauthenticated_ingest_rejected(tmp_path):
    """CYC-01: Ingestion without authentication must be rejected with 401."""
    nc_path = tmp_path / "valid_test.nc"
    create_reference_satellite_grid_netcdf(nc_path, num_lats=40, num_lons=40, center_lat=15.0, center_lon=85.0)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(nc_path, "rb") as f:
            files = {"file": ("valid_test.nc", io.BytesIO(f.read()), "application/x-netcdf")}
        resp = await ac.post("/api/v1/ingest/file", files=files)
        assert resp.status_code == 401
        assert "Authentication required" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_api_key_rejected(tmp_path):
    """CYC-01: Ingestion with invalid credentials must be rejected with 401."""
    nc_path = tmp_path / "valid_test.nc"
    create_reference_satellite_grid_netcdf(nc_path, num_lats=40, num_lons=40, center_lat=15.0, center_lon=85.0)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(nc_path, "rb") as f:
            files = {"file": ("valid_test.nc", io.BytesIO(f.read()), "application/x-netcdf")}
        headers = {"X-API-Key": "completely-invalid-attacker-key"}
        resp = await ac.post("/api/v1/ingest/file", files=files, headers=headers)
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_path_traversal_filename_rejected(tmp_path):
    """CYC-01: Path traversal in filename ('../', '..\\') must be rejected with 400 and no escape."""
    nc_path = tmp_path / "test.nc"
    create_reference_satellite_grid_netcdf(nc_path, num_lats=40, num_lons=40, center_lat=15.0, center_lon=85.0)
    with open(nc_path, "rb") as f:
        file_bytes = f.read()

    # Capture files before upload attempt to verify sandbox integrity
    parent_files_before = set(settings.DATA_RAW_DIR.parent.glob("*"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"X-API-Key": settings.INGEST_API_KEY}

        # Traversal pattern 1: Unix style ../
        files_unix = {"file": ("../../escape_unix.nc", io.BytesIO(file_bytes), "application/x-netcdf")}
        resp1 = await ac.post("/api/v1/ingest/file", files=files_unix, headers=headers)
        assert resp1.status_code == 400
        assert "Invalid filename" in resp1.json()["detail"]

        # Traversal pattern 2: Windows style ..\
        files_win = {"file": ("..\\..\\escape_win.nc", io.BytesIO(file_bytes), "application/x-netcdf")}
        resp2 = await ac.post("/api/v1/ingest/file", files=files_win, headers=headers)
        assert resp2.status_code == 400

        # Subdirectory traversal
        files_subdir = {"file": ("subdir/nested.nc", io.BytesIO(file_bytes), "application/x-netcdf")}
        resp3 = await ac.post("/api/v1/ingest/file", files=files_subdir, headers=headers)
        assert resp3.status_code == 400

    # Verify no files were created outside DATA_RAW_DIR
    parent_files_after = set(settings.DATA_RAW_DIR.parent.glob("*"))
    assert parent_files_before == parent_files_after


@pytest.mark.asyncio
async def test_absolute_path_filename_rejected(tmp_path):
    """CYC-01: Absolute path filenames must be rejected with 400."""
    nc_path = tmp_path / "test.nc"
    create_reference_satellite_grid_netcdf(nc_path, num_lats=40, num_lons=40, center_lat=15.0, center_lon=85.0)
    with open(nc_path, "rb") as f:
        file_bytes = f.read()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"X-API-Key": settings.INGEST_API_KEY}
        files = {"file": ("/etc/passwd.nc", io.BytesIO(file_bytes), "application/x-netcdf")}
        resp = await ac.post("/api/v1/ingest/file", files=files, headers=headers)
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_unsupported_extension_rejected():
    """CYC-01: Non-scientific formats (.exe, .sh, .txt) must be rejected with 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"X-API-Key": settings.INGEST_API_KEY}
        files = {"file": ("malicious_script.sh", io.BytesIO(b"echo 'pwned'"), "application/x-sh")}
        resp = await ac.post("/api/v1/ingest/file", files=files, headers=headers)
        assert resp.status_code == 400
        assert "Unsupported scientific file format" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_payload_size_limit_enforced_and_unlinked(monkeypatch):
    """CYC-01: Uploads exceeding size limits must be rejected with 413 and unlinked immediately."""
    # Temporarily set max upload size to 10 KB for test
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_BYTES", 10 * 1024)

    # 50 KB dummy payload
    oversized_data = b"X" * (50 * 1024)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"X-API-Key": settings.INGEST_API_KEY}
        files = {"file": ("oversized_file.nc", io.BytesIO(oversized_data), "application/x-netcdf")}
        resp = await ac.post("/api/v1/ingest/file", files=files, headers=headers)
        assert resp.status_code == 413
        assert "Payload Too Large" in resp.json()["detail"]

    # Verify no partial temporary files matching ingest_* remain in DATA_RAW_DIR
    leftover = [f for f in settings.DATA_RAW_DIR.glob("ingest_*") if f.stat().st_size == len(oversized_data)]
    assert len(leftover) == 0


@pytest.mark.asyncio
async def test_valid_authenticated_upload_server_side_naming(tmp_path):
    """CYC-01: Legitimate upload is authenticated, stored under random server-side filename, and contained."""
    nc_path = tmp_path / "valid_goes16.nc"
    create_reference_satellite_grid_netcdf(nc_path, num_lats=40, num_lons=40, center_lat=18.0, center_lon=88.0)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test Bearer token auth support
        headers = {"Authorization": f"Bearer {settings.INGEST_API_KEY}"}
        with open(nc_path, "rb") as f:
            files = {"file": ("valid_goes16.nc", io.BytesIO(f.read()), "application/x-netcdf")}
        resp = await ac.post("/api/v1/ingest/file", files=files, headers=headers)
        assert resp.status_code in [200, 201]
        data = resp.json()
        assert "product_id" in data
        assert data["filename"] == "valid_goes16.nc"

        # Check product in DB has a safe server-side storage path
        detail_resp = await ac.get(f"/api/v1/ingest/{data['product_id']}")
        assert detail_resp.status_code == 200
        stored_path = Path(detail_resp.json()["file_path"]).resolve()
        assert stored_path.is_relative_to(settings.DATA_RAW_DIR.resolve())
        assert stored_path.name.startswith("ingest_")
        assert stored_path.exists()
