use pyo3::prelude::*;
use sha2::{Digest, Sha256};
use std::fs::File;
use std::io::Read;
use std::path::Path;

/// Fast SHA-256 calculation for an in-memory byte buffer.
/// Uses hardware SHA-NI instructions when available.
#[pyfunction]
pub fn fast_sha256_bytes(bytes: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(bytes);
    format!("{:x}", hasher.finalize())
}

/// Fast streaming SHA-256 calculation for a file on disk.
/// Uses 128KB chunks to maximize OS cache and read throughput.
/// Releases Python GIL during hashing.
#[pyfunction]
pub fn fast_sha256_file(py: Python<'_>, filepath: &str) -> PyResult<String> {
    let path = Path::new(filepath);
    if !path.is_file() {
        return Err(pyo3::exceptions::PyFileNotFoundError::new_err(format!(
            "File not found: {}",
            filepath
        )));
    }

    let file_path_str = filepath.to_string();

    py.allow_threads(move || {
        let mut file = File::open(&file_path_str).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to open file: {}", e))
        })?;

        let mut hasher = Sha256::new();
        let mut buffer = [0u8; 131072]; // 128 KB buffer

        loop {
            let bytes_read = file.read(&mut buffer).map_err(|e| {
                pyo3::exceptions::PyIOError::new_err(format!("Error reading file: {}", e))
            })?;
            if bytes_read == 0 {
                break;
            }
            hasher.update(&buffer[..bytes_read]);
        }

        Ok(format!("{:x}", hasher.finalize()))
    })
}
