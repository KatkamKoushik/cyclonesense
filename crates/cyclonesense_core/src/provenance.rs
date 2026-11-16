use pyo3::buffer::PyBuffer;
use pyo3::prelude::*;
use rayon::prelude::*;
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

/// Zero-copy SHA-256 calculation for an array, memoryview, or buffer-protocol object.
/// Ingests memory directly via the Python buffer protocol without intermediate heap copies.
/// Incorporates dtype and shape metadata for deterministic scientific hashing.
#[pyfunction]
#[pyo3(signature = (obj, dtype_str="", shape_str=""))]
pub fn fast_sha256_buffer(
    obj: &Bound<'_, PyAny>,
    dtype_str: &str,
    shape_str: &str,
) -> PyResult<String> {
    let buf = PyBuffer::<u8>::get_bound(obj)?;
    let slice: &[u8] = unsafe {
        std::slice::from_raw_parts(buf.buf_ptr() as *const u8, buf.len_bytes())
    };
    let mut hasher = Sha256::new();
    if !dtype_str.is_empty() {
        hasher.update(dtype_str.as_bytes());
    }
    if !shape_str.is_empty() {
        hasher.update(shape_str.as_bytes());
    }
    hasher.update(slice);
    Ok(format!("{:x}", hasher.finalize()))
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

/// High-volume multi-file batch SHA-256 calculation executed concurrently across CPU cores.
/// Releases Python GIL and computes digests using Rayon data parallelism.
#[pyfunction]
pub fn fast_sha256_files_batch(
    py: Python<'_>,
    filepaths: Vec<String>,
) -> PyResult<Vec<(String, String)>> {
    let res = py.allow_threads(move || {
        filepaths
            .into_par_iter()
            .map(|fp| {
                let path = Path::new(&fp);
                if !path.is_file() {
                    return (fp, "ERROR_FILE_NOT_FOUND".to_string());
                }
                match File::open(path) {
                    Ok(mut file) => {
                        let mut hasher = Sha256::new();
                        let mut buf = [0u8; 131072];
                        loop {
                            match file.read(&mut buf) {
                                Ok(0) => break,
                                Ok(n) => hasher.update(&buf[..n]),
                                Err(_) => return (fp, "ERROR_IO_READ".to_string()),
                            }
                        }
                        (fp, format!("{:x}", hasher.finalize()))
                    }
                    Err(_) => (fp, "ERROR_IO_OPEN".to_string()),
                }
            })
            .collect()
    });

    Ok(res)
}
