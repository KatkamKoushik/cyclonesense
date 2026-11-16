use numpy::{IntoPyArray, PyArray1, PyReadonlyArrayDyn};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use rayon::prelude::*;

pub const CLASS_NO_CHANGE: u8 = 0;
pub const CLASS_WATER_CHANGE: u8 = 1;
pub const CLASS_VEGETATION_CHANGE: u8 = 2;
pub const CLASS_SURFACE_CHANGE: u8 = 3;
pub const CLASS_UNCERTAIN: u8 = 4;

/// Computes Normalized Difference Index: (band_a - band_b) / (band_a + band_b)
/// Clamped to [-1.0, 1.0]. Non-finite / zero-denominator results in NaN.
#[pyfunction]
#[pyo3(signature = (band_a, band_b))]
pub fn compute_normalized_difference<'py>(
    py: Python<'py>,
    band_a: PyReadonlyArrayDyn<'py, f32>,
    band_b: PyReadonlyArrayDyn<'py, f32>,
) -> PyResult<Bound<'py, PyArray1<f32>>> {
    let a_slice = band_a.as_slice()?;
    let b_slice = band_b.as_slice()?;

    if a_slice.len() != b_slice.len() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Array lengths must match",
        ));
    }

    let mut output: Vec<f32> = vec![0.0; a_slice.len()];

    py.allow_threads(|| {
        output
            .par_iter_mut()
            .zip(a_slice.par_iter().zip(b_slice.par_iter()))
            .for_each(|(out, (&a, &b))| {
                let denom = a + b;
                if denom.abs() > 1e-6 && a.is_finite() && b.is_finite() {
                    let val = (a - b) / denom;
                    *out = val.clamp(-1.0, 1.0);
                } else {
                    *out = f32::NAN;
                }
            });
    });

    Ok(output.into_pyarray_bound(py))
}

/// Converts SAR linear intensity to decibels: 10 * log10(max(x, eps))
/// Clamped to [-35.0, 5.0] dB.
#[pyfunction]
#[pyo3(signature = (linear_intensity, eps=1e-6))]
pub fn sar_linear_to_db<'py>(
    py: Python<'py>,
    linear_intensity: PyReadonlyArrayDyn<'py, f32>,
    eps: f32,
) -> PyResult<Bound<'py, PyArray1<f32>>> {
    let slice = linear_intensity.as_slice()?;
    let mut output: Vec<f32> = vec![0.0; slice.len()];

    py.allow_threads(|| {
        output
            .par_iter_mut()
            .zip(slice.par_iter())
            .for_each(|(out, &val)| {
                if val.is_finite() {
                    let clamped = val.max(eps);
                    let db = 10.0 * clamped.log10();
                    *out = db.clamp(-35.0, 5.0);
                } else {
                    *out = f32::NAN;
                }
            });
    });

    Ok(output.into_pyarray_bound(py))
}

/// Fused multi-temporal optical change detection kernel.
/// Evaluates NDVI and NDWI deltas, spectral RGB shifts, and produces:
/// - Categorical classification mask (uint8: 0..4)
/// - Pixel count statistics per class
/// - Mean deltas
/// Executes in a single cache-friendly pass with multi-threaded Rayon parallelism.
#[pyfunction]
#[pyo3(signature = (
    ndvi_pre,
    ndvi_post,
    ndwi_post,
    delta_ndwi,
    rgb_diff,
    water_threshold=0.15,
    water_ndwi_min=-0.05,
    veg_threshold=-0.15,
    rgb_shift_threshold=0.25
))]
pub fn fast_classify_optical_change<'py>(
    py: Python<'py>,
    ndvi_pre: PyReadonlyArrayDyn<'py, f32>,
    ndvi_post: PyReadonlyArrayDyn<'py, f32>,
    ndwi_post: PyReadonlyArrayDyn<'py, f32>,
    delta_ndwi: PyReadonlyArrayDyn<'py, f32>,
    rgb_diff: PyReadonlyArrayDyn<'py, f32>,
    water_threshold: f32,
    water_ndwi_min: f32,
    veg_threshold: f32,
    rgb_shift_threshold: f32,
) -> PyResult<(Bound<'py, PyArray1<u8>>, Bound<'py, PyDict>)> {
    let n_pre = ndvi_pre.as_slice()?;
    let n_post = ndvi_post.as_slice()?;
    let w_post = ndwi_post.as_slice()?;
    let d_w = delta_ndwi.as_slice()?;
    let r_diff = rgb_diff.as_slice()?;

    let total_len = n_pre.len();
    if n_post.len() != total_len || w_post.len() != total_len || d_w.len() != total_len || r_diff.len() != total_len {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "All input arrays must have the same length",
        ));
    }

    let mut mask = vec![CLASS_UNCERTAIN; total_len];

    let (valid_count, water_count, veg_count, surf_count, uncertain_count, sum_d_ndvi, sum_d_ndwi) = py.allow_threads(|| {
        let mut v_cnt = 0usize;
        let mut w_cnt = 0usize;
        let mut vg_cnt = 0usize;
        let mut s_cnt = 0usize;
        let mut u_cnt = 0usize;
        let mut s_d_ndvi = 0.0f64;
        let mut s_d_ndwi = 0.0f64;

        for i in 0..total_len {
            let pre_v = n_pre[i];
            let post_v = n_post[i];
            let post_w = w_post[i];
            let delta_w = d_w[i];
            let shift = r_diff[i];

            let is_valid = pre_v.is_finite() && post_v.is_finite();

            if !is_valid {
                mask[i] = CLASS_UNCERTAIN;
                u_cnt += 1;
            } else {
                v_cnt += 1;
                let delta_n = post_v - pre_v;
                s_d_ndvi += delta_n as f64;
                s_d_ndwi += delta_w as f64;

                // 1. Water condition: delta_ndwi > threshold AND post_ndwi > water_ndwi_min
                let is_water = delta_w > water_threshold && post_w > water_ndwi_min;
                // 2. Vegetation condition: delta_ndvi < veg_threshold and NOT water
                let is_veg = !is_water && (delta_n < veg_threshold);
                // 3. Surface condition: rgb spectral shift > threshold and NOT water and NOT veg
                let is_surf = !is_water && !is_veg && (shift > rgb_shift_threshold);

                if is_water {
                    mask[i] = CLASS_WATER_CHANGE;
                    w_cnt += 1;
                } else if is_veg {
                    mask[i] = CLASS_VEGETATION_CHANGE;
                    vg_cnt += 1;
                } else if is_surf {
                    mask[i] = CLASS_SURFACE_CHANGE;
                    s_cnt += 1;
                } else {
                    mask[i] = CLASS_NO_CHANGE;
                }
            }
        }

        (v_cnt, w_cnt, vg_cnt, s_cnt, u_cnt, s_d_ndvi, s_d_ndwi)
    });

    let dict = PyDict::new_bound(py);
    dict.set_item("total_pixels", total_len)?;
    dict.set_item("valid_pixels", valid_count)?;
    dict.set_item("water_pixels", water_count)?;
    dict.set_item("vegetation_pixels", veg_count)?;
    dict.set_item("surface_pixels", surf_count)?;
    dict.set_item("uncertain_pixels", uncertain_count)?;
    dict.set_item("mean_delta_ndvi", if valid_count > 0 { sum_d_ndvi / valid_count as f64 } else { 0.0 })?;
    dict.set_item("mean_delta_ndwi", if valid_count > 0 { sum_d_ndwi / valid_count as f64 } else { 0.0 })?;

    let py_mask = mask.into_pyarray_bound(py);
    Ok((py_mask, dict))
}
