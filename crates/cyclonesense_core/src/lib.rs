pub mod biophysical;
pub mod georeferencing;
pub mod provenance;
pub mod qc;

use pyo3::prelude::*;

#[pyfunction]
fn rust_core_version() -> &'static str {
    "0.2.0-rust-accelerated"
}

#[pymodule]
fn cyclonesense_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rust_core_version, m)?)?;

    // QC functions
    m.add_function(wrap_pyfunction!(qc::evaluate_array_qc, m)?)?;

    // Georeferencing functions
    m.add_function(wrap_pyfunction!(georeferencing::latlon_to_abi_angles, m)?)?;
    m.add_function(wrap_pyfunction!(georeferencing::abi_angles_to_latlon, m)?)?;
    m.add_function(wrap_pyfunction!(georeferencing::batch_latlon_to_abi_angles, m)?)?;
    m.add_function(wrap_pyfunction!(georeferencing::batch_abi_angles_to_latlon, m)?)?;

    // Biophysical and SAR functions
    m.add_function(wrap_pyfunction!(biophysical::compute_normalized_difference, m)?)?;
    m.add_function(wrap_pyfunction!(biophysical::sar_linear_to_db, m)?)?;
    m.add_function(wrap_pyfunction!(biophysical::fast_sar_flood_inundation_mask, m)?)?;
    m.add_function(wrap_pyfunction!(biophysical::fast_cloud_mask, m)?)?;
    m.add_function(wrap_pyfunction!(biophysical::fast_classify_optical_change, m)?)?;

    // Cryptographic provenance functions
    m.add_function(wrap_pyfunction!(provenance::fast_sha256_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(provenance::fast_sha256_buffer, m)?)?;
    m.add_function(wrap_pyfunction!(provenance::fast_sha256_file, m)?)?;
    m.add_function(wrap_pyfunction!(provenance::fast_sha256_files_batch, m)?)?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rust_core_version_string() {
        assert_eq!(rust_core_version(), "0.2.0-rust-accelerated");
    }

    #[test]
    fn test_native_georeferencing_roundtrip() {
        let lat = 26.0;
        let lon = -84.6;
        let angles = georeferencing::latlon_to_abi_angles(
            lat,
            lon,
            -75.0,
            georeferencing::DEFAULT_HEIGHT,
            georeferencing::DEFAULT_REQ,
            georeferencing::DEFAULT_RPOL,
        );
        assert!(angles.is_some());
        let (x, y) = angles.unwrap();
        let recovered = georeferencing::abi_angles_to_latlon(
            x,
            y,
            -75.0,
            georeferencing::DEFAULT_HEIGHT,
            georeferencing::DEFAULT_REQ,
            georeferencing::DEFAULT_RPOL,
        );
        assert!(recovered.is_some());
        let (rec_lat, rec_lon) = recovered.unwrap();
        assert!((rec_lat - lat).abs() < 0.05);
        assert!((rec_lon - lon).abs() < 0.05);
    }

    #[test]
    fn test_native_sha256_bytes() {
        let data = b"CycloneSense scientific lineage";
        let hash = provenance::fast_sha256_bytes(data);
        assert_eq!(hash.len(), 64);
        assert_eq!(
            hash,
            "5acb1c62963439bf02f2ea7de2fb8b0548dbd8929e1154ca56947598d8e7b3b9"
        );
    }
}
