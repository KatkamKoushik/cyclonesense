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

/// Computes dual-temporal SAR flood inundation mask and total inundation percentage.
/// Condition: post_vv <= water_threshold AND (post_vv - pre_vv) <= drop_threshold.
/// Executes in a single multi-threaded pass without allocating intermediate delta arrays.
#[pyfunction]
#[pyo3(signature = (pre_vv_db, post_vv_db, water_threshold=-16.0, drop_threshold=-3.0))]
pub fn fast_sar_flood_inundation_mask<'py>(
    py: Python<'py>,
    pre_vv_db: PyReadonlyArrayDyn<'py, f32>,
    post_vv_db: PyReadonlyArrayDyn<'py, f32>,
    water_threshold: f32,
    drop_threshold: f32,
) -> PyResult<(Bound<'py, PyArray1<bool>>, f64)> {
    let pre_slice = pre_vv_db.as_slice()?;
    let post_slice = post_vv_db.as_slice()?;

    if pre_slice.len() != post_slice.len() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Pre-event and post-event SAR arrays must have identical length",
        ));
    }

    let n = pre_slice.len();
    if n == 0 {
        let empty_mask: Vec<bool> = Vec::new();
        return Ok((empty_mask.into_pyarray_bound(py), 0.0));
    }

    let mut mask = vec![false; n];

    let total_inundated: usize = py.allow_threads(|| {
        mask.par_iter_mut()
            .zip(pre_slice.par_iter().zip(post_slice.par_iter()))
            .map(|(out_m, (&pre, &post))| {
                if pre.is_finite() && post.is_finite() {
                    let delta = post - pre;
                    if post <= water_threshold && delta <= drop_threshold {
                        *out_m = true;
                        1usize
                    } else {
                        *out_m = false;
                        0usize
                    }
                } else {
                    *out_m = false;
                    0usize
                }
            })
            .sum()
    });

    let inundation_pct = ((total_inundated as f64 / n as f64) * 100.0 * 100.0).round() / 100.0;

    Ok((mask.into_pyarray_bound(py), inundation_pct))
}

/// High-throughput cloud and shadow masking from multispectral Sentinel-2 imagery.
/// Evaluates SCL classes or RGB reflectance brightness in parallel.
#[pyfunction]
#[pyo3(signature = (red_band, green_band, blue_band, scl_band=None))]
pub fn fast_cloud_mask<'py>(
    py: Python<'py>,
    red_band: PyReadonlyArrayDyn<'py, f32>,
    green_band: PyReadonlyArrayDyn<'py, f32>,
    blue_band: PyReadonlyArrayDyn<'py, f32>,
    scl_band: Option<PyReadonlyArrayDyn<'py, i32>>,
) -> PyResult<Bound<'py, PyArray1<bool>>> {
    let r_slice = red_band.as_slice()?;
    let g_slice = green_band.as_slice()?;
    let b_slice = blue_band.as_slice()?;

    let n = r_slice.len();
    if g_slice.len() != n || b_slice.len() != n {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Red, Green, and Blue bands must have matching lengths",
        ));
    }

    let mut valid_mask = vec![false; n];

    if let Some(scl) = scl_band {
        let scl_slice = scl.as_slice()?;
        if scl_slice.len() != n {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "SCL band must match RGB dimensions",
            ));
        }

        py.allow_threads(|| {
            valid_mask
                .par_iter_mut()
                .zip(scl_slice.par_iter())
                .for_each(|(out_v, &c)| {
                    // SCL classes: 0=No Data, 1=Saturated, 3=Cloud Shadow, 8=Cloud Medium, 9=Cloud High, 10=Cirrus
                    *out_v = c != 0 && c != 1 && c != 3 && c != 8 && c != 9 && c != 10;
                });
        });
    } else {
        py.allow_threads(|| {
            valid_mask
                .par_iter_mut()
                .zip(r_slice.par_iter().zip(g_slice.par_iter().zip(b_slice.par_iter())))
                .for_each(|(out_v, (&r, (&g, &b)))| {
                    if r.is_finite() && g.is_finite() && b.is_finite() {
                        let brightness = (r + g + b) / 3.0;
                        *out_v = brightness < 0.65 && r < 0.70;
                    } else {
                        *out_v = false;
                    }
                });
        });
    }

    Ok(valid_mask.into_pyarray_bound(py))
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
) -> PyResult<Bound<'py, PyDict>> {
    let ndvi_pre_s = ndvi_pre.as_slice()?;
    let ndvi_post_s = ndvi_post.as_slice()?;
    let ndwi_post_s = ndwi_post.as_slice()?;
    let d_ndwi_s = delta_ndwi.as_slice()?;
    let rgb_d_s = rgb_diff.as_slice()?;

    let n = ndvi_pre_s.len();
    if ndvi_post_s.len() != n || ndwi_post_s.len() != n || d_ndwi_s.len() != n || rgb_d_s.len() != n {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Input arrays must all have matching dimensions",
        ));
    }

    let mut class_mask: Vec<u8> = vec![0; n];

    // Single-pass fused classification and statistics reduction with Rayon
    let (counts, (sum_d_ndvi, (sum_d_ndwi, sum_rgb_d))) = py.allow_threads(|| {
        let results: (Vec<usize>, (f64, (f64, f64))) = class_mask
            .par_iter_mut()
            .zip(
                ndvi_pre_s
                    .par_iter()
                    .zip(ndvi_post_s.par_iter())
                    .zip(ndwi_post_s.par_iter().zip(d_ndwi_s.par_iter().zip(rgb_d_s.par_iter()))),
            )
            .fold(
                || (vec![0usize; 5], (0.0f64, (0.0f64, 0.0f64))),
                |(mut local_counts, (mut s_d_ndvi, (mut s_d_ndwi, mut s_rgb))),
                 (mask_out, ((&n_pre, &n_post), (&w_post, (&dw, &rgb))))| {
                    if !n_pre.is_finite() || !n_post.is_finite() || !w_post.is_finite() || !dw.is_finite() || !rgb.is_finite() {
                        *mask_out = CLASS_UNCERTAIN;
                        local_counts[CLASS_UNCERTAIN as usize] += 1;
                        return (local_counts, (s_d_ndvi, (s_d_ndwi, s_rgb)));
                    }

                    let d_ndvi = n_post - n_pre;
                    s_d_ndvi += d_ndvi as f64;
                    s_d_ndwi += dw as f64;
                    s_rgb += rgb as f64;

                    let c = if dw >= water_threshold && w_post >= water_ndwi_min {
                        CLASS_WATER_CHANGE
                    } else if d_ndvi <= veg_threshold && rgb >= 0.05 {
                        CLASS_VEGETATION_CHANGE
                    } else if rgb >= rgb_shift_threshold && d_ndvi.abs() < 0.10 && dw < 0.10 {
                        CLASS_SURFACE_CHANGE
                    } else {
                        CLASS_NO_CHANGE
                    };

                    *mask_out = c;
                    local_counts[c as usize] += 1;
                    (local_counts, (s_d_ndvi, (s_d_ndwi, s_rgb)))
                },
            )
            .reduce(
                || (vec![0usize; 5], (0.0f64, (0.0f64, 0.0f64))),
                |(mut acc_counts, (s1, (s2, s3))), (counts, (b1, (b2, b3)))| {
                    for i in 0..5 {
                        acc_counts[i] += counts[i];
                    }
                    (acc_counts, (s1 + b1, (s2 + b2, s3 + b3)))
                },
            );

        results
    });

    let dict = PyDict::new_bound(py);
    dict.set_item("classification_mask", class_mask.into_pyarray_bound(py))?;

    let counts_dict = PyDict::new_bound(py);
    counts_dict.set_item("no_change", counts[CLASS_NO_CHANGE as usize])?;
    counts_dict.set_item("water_expansion", counts[CLASS_WATER_CHANGE as usize])?;
    counts_dict.set_item("vegetation_loss", counts[CLASS_VEGETATION_CHANGE as usize])?;
    counts_dict.set_item("surface_scouring", counts[CLASS_SURFACE_CHANGE as usize])?;
    counts_dict.set_item("uncertain", counts[CLASS_UNCERTAIN as usize])?;
    dict.set_item("class_pixel_counts", counts_dict)?;

    let valid_count = n - counts[CLASS_UNCERTAIN as usize];
    let mean_d_ndvi = if valid_count > 0 { sum_d_ndvi / valid_count as f64 } else { 0.0 };
    let mean_d_ndwi = if valid_count > 0 { sum_d_ndwi / valid_count as f64 } else { 0.0 };
    let mean_rgb = if valid_count > 0 { sum_rgb_d / valid_count as f64 } else { 0.0 };

    dict.set_item("mean_delta_ndvi", (mean_d_ndvi * 10000.0).round() / 10000.0)?;
    dict.set_item("mean_delta_ndwi", (mean_d_ndwi * 10000.0).round() / 10000.0)?;
    dict.set_item("mean_rgb_shift", (mean_rgb * 10000.0).round() / 10000.0)?;

    Ok(dict)
}
