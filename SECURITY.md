# Security Policy

## Supported Versions

We actively maintain and provide security updates for the following versions of **CycloneSense**:

| Version | Supported | Security Maintenance Status |
| :--- | :--- | :--- |
| **3.x (Current)** | :white_check_mark: | Active security monitoring and vulnerability patching |
| **2.x** | :white_check_mark: | Critical security patches only |
| **1.x** | :x: | End-of-life (unsupported) |

---

## Reporting a Vulnerability

The CycloneSense team takes security and data containment seriously, particularly regarding scientific file uploads, remote raster ingestion, and server-side execution.

If you discover a security vulnerability, **please do not disclose it publicly or open a public GitHub issue**.

### Responsible Disclosure Process

1. **Email Details:** Send an encrypted or confidential report to **[koushikkatkam@gmail.com](mailto:koushikkatkam@gmail.com)**.
2. **Subject Line:** `[SECURITY] CycloneSense Vulnerability Report - <Brief Description>`
3. **Information to Include:**
   - Type of vulnerability (e.g., path traversal, unauthenticated write, injection, denial of service).
   - Component affected (e.g., `routes_ingest.py`, NetCDF reader, API authentication).
   - Step-by-step reproduction instructions, Proof-of-Concept (PoC) payload, or script.
   - Potential impact on system integrity, scientific data confidentiality, or hosting infrastructure.
   - Any proposed mitigations or remediation patches.

### Response Timelines

- **Initial Acknowledgment:** Within **24 hours** of receipt.
- **Triage & Assessment:** Within **72 hours** with severity classification.
- **Remediation & Patch:** Within **14 business days** for high/critical vulnerabilities.
- **Public Disclosure:** Coordinated disclosure after the patch has been verified and released. Credit will be publicly acknowledged in release notes.

---

## File Ingestion & Containment Security Policy (CYC-01)

CycloneSense enforces strict server-side safeguards on all external and scientific file uploads:

1. **Path Traversal Prevention:**
   - Client-provided filenames are strictly validated to reject directory traversal tokens (`..`, `/`, `\`) and absolute file paths.
   - Physical storage paths are generated using server-side random UUIDs (`ingest_{uuid.hex}{ext}`) within `settings.DATA_RAW_DIR`.
   - File containment is verified prior to write using `target_path.resolve().is_relative_to(raw_dir.resolve())`.
2. **Streaming Payload Limits:**
   - Ingestion endpoints stream file uploads in chunks, enforcing an absolute hard limit of **100 MB** (`settings.MAX_UPLOAD_SIZE_BYTES`).
   - If an upload exceeds this limit, streaming immediately aborts, all partial temporary files are unlinked, and HTTP 413 Payload Too Large is returned.
3. **Whitelisted Extensions:**
   - Only validated scientific container extensions are permitted: `.nc`, `.nc4`, `.h5`, `.hdf5`, `.hdf`.
4. **API Authentication:**
   - Ingestion endpoints require valid API credentials (`X-API-Key` or `Authorization: Bearer <key>`) validated by `verify_ingest_auth`.
5. **Continuous Verification:**
   - Ingestion security is audited by automated negative tests in `backend/tests/test_security_ingest.py`.

---

## Security Practices & Hygiene

- **Dependency Auditing:** Automated CI workflows enforce zero known vulnerabilities using `pip-audit` for Python and `pnpm audit` for Node.js.
- **Secret Hygiene:** Zero committed API keys, tokens, or credentials. All secrets are configured via `.env` variables and excluded in `.gitignore`.
- **Memory Safety & NetCDF Parsing:** All NetCDF4 and HDF5 readers operate under isolated context managers with strict memory bounds and shape verification.
