use numpy::PyReadonlyArrayDyn;
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[derive(Debug, Clone)]
pub struct FastQCResult {
    pub status: String,
    pub physical_bounds_passed: bool,
    pub missing_pixel_percentage: f64,
    pub total_pixels: usize,
    pub valid_pixels: usize,
    pub missing_pixels: usize,
    pub min_val: f64,
    pub max_val: f64,
    pub mean_val: f64,
    pub std_val: f64,
    pub anomalies: Vec<String>,
}

/// Single-pass streaming evaluation of a float32 satellite raster.
/// Uses Welford's online algorithm for variance/std to avoid multiple passes.
/// Operates without intermediate memory allocations and releases the Python GIL during compute.
/// Enforces complete behavioral parity with Python QualityControlEngine.
#[pyfunction]
#[pyo3(signature = (data, min_limit=None, max_limit=None, variable_name="array", unit="", max_missing_pct=15.0))]
pub fn evaluate_array_qc<'py>(
    py: Python<'py>,
    data: PyReadonlyArrayDyn<'py, f32>,
    min_limit: Option<f64>,
    max_limit: Option<f64>,
    variable_name: &str,
    unit: &str,
    max_missing_pct: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let slice = data.as_slice()?;
    let total_pixels = slice.len();

    if total_pixels == 0 {
        let dict = PyDict::new_bound(py);
        dict.set_item("status", "REJECTED")?;
        dict.set_item("physical_bounds_passed", false)?;
        dict.set_item("missing_pixel_percentage", 100.0)?;
        dict.set_item("anomalies", vec!["Array has 0 elements".to_string()])?;
        dict.set_item("total_pixels", 0)?;
        dict.set_item("valid_pixels", 0)?;
        dict.set_item("missing_pixels", 0)?;
        dict.set_item("min", 0.0)?;
        dict.set_item("max", 0.0)?;
        dict.set_item("mean", 0.0)?;
        dict.set_item("std", 0.0)?;
        return Ok(dict);
    }

    let var_name = variable_name.to_string();
    let unit_str = unit.to_string();

    // Release GIL for compute-heavy pass
    let res = py.allow_threads(move || {
        let mut missing_count = 0usize;
        let mut min_v = f64::INFINITY;
        let mut max_v = f64::NEG_INFINITY;

        // Welford's algorithm variables
        let mut count = 0usize;
        let mut mean = 0.0f64;
        let mut m2 = 0.0f64;

        for &val in slice {
            if val.is_nan() || val.is_infinite() {
                missing_count += 1;
            } else {
                let v = val as f64;
                count += 1;
                if v < min_v {
                    min_v = v;
                }
                if v > max_v {
                    max_v = v;
                }

                // Welford's online update
                let delta = v - mean;
                mean += delta / (count as f64);
                let delta2 = v - mean;
                m2 += delta * delta2;
            }
        }

        let missing_pct = (missing_count as f64 / total_pixels as f64) * 100.0;
        let std_v = if count > 1 {
            (m2 / ((count - 1) as f64)).sqrt()
        } else {
            0.0
        };

        let mut anomalies = Vec::new();
        let mut bounds_passed = true;
        let mut status = "PASSED";

        if count == 0 {
            bounds_passed = false;
            status = "REJECTED";
            anomalies.push(format!("All {} pixels in {} are NaN/missing", total_pixels, var_name));
        } else {
            if let Some(low) = min_limit {
                if min_v < low {
                    bounds_passed = false;
                    let u = if unit_str.is_empty() { "" } else { &unit_str };
                    anomalies.push(format!(
                        "Physical lower bound violated for {}: min {:.2} < {} {}",
                        var_name, min_v, low, u
                    ).trim_end().to_string());
                }
            }
            if let Some(high) = max_limit {
                if max_v > high {
                    bounds_passed = false;
                    let u = if unit_str.is_empty() { "" } else { &unit_str };
                    anomalies.push(format!(
                        "Physical upper bound violated for {}: max {:.2} > {} {}",
                        var_name, max_v, high, u
                    ).trim_end().to_string());
                }
            }

            // Missing pixel percentage check (exact parity with Python QC)
            if missing_pct > max_missing_pct {
                if missing_pct >= 50.0 {
                    status = "REJECTED";
                    anomalies.push(format!(
                        "Excessive missing pixels: {:.1}% exceeds rejection limit (50%)",
                        missing_pct
                    ));
                } else {
                    status = "DEGRADED";
                    anomalies.push(format!(
                        "Elevated missing pixels: {:.1}% exceeds nominal threshold ({:.1}%)",
                        missing_pct, max_missing_pct
                    ));
                }
            }

            if !bounds_passed && status == "PASSED" {
                status = "DEGRADED";
            }
        }

        FastQCResult {
            status: status.to_string(),
            physical_bounds_passed: bounds_passed,
            missing_pixel_percentage: (missing_pct * 100.0).round() / 100.0,
            total_pixels,
            valid_pixels: count,
            missing_pixels: missing_count,
            min_val: if count > 0 { (min_v * 1000.0).round() / 1000.0 } else { 0.0 },
            max_val: if count > 0 { (max_v * 1000.0).round() / 1000.0 } else { 0.0 },
            mean_val: if count > 0 { (mean * 1000.0).round() / 1000.0 } else { 0.0 },
            std_val: if count > 0 { (std_v * 1000.0).round() / 1000.0 } else { 0.0 },
            anomalies,
        }
    });

    let dict = PyDict::new_bound(py);
    dict.set_item("status", res.status)?;
    dict.set_item("physical_bounds_passed", res.physical_bounds_passed)?;
    dict.set_item("missing_pixel_percentage", res.missing_pixel_percentage)?;
    dict.set_item("total_pixels", res.total_pixels)?;
    dict.set_item("valid_pixels", res.valid_pixels)?;
    dict.set_item("missing_pixels", res.missing_pixels)?;
    dict.set_item("min", res.min_val)?;
    dict.set_item("max", res.max_val)?;
    dict.set_item("mean", res.mean_val)?;
    dict.set_item("std", res.std_val)?;
    dict.set_item("anomalies", res.anomalies)?;

    Ok(dict)
}
