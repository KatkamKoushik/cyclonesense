use numpy::{IntoPyArray, PyArray1, PyReadonlyArrayDyn};
use pyo3::prelude::*;
use rayon::prelude::*;
use std::f64::consts::PI;

pub const DEFAULT_REQ: f64 = 6378137.0;
pub const DEFAULT_RPOL: f64 = 6356752.31414;
pub const DEFAULT_HEIGHT: f64 = 35786023.0;

#[inline(always)]
fn deg_to_rad(deg: f64) -> f64 {
    deg * (PI / 180.0)
}

#[inline(always)]
fn rad_to_deg(rad: f64) -> f64 {
    rad * (180.0 / PI)
}

/// Transforms WGS84 geodetic latitude and longitude (degrees) to GOES ABI
/// scanning angles x (E-W) and y (N-S) in radians.
/// Returns None if the point is on the opposite side of Earth or behind satellite horizon.
#[pyfunction]
#[pyo3(signature = (lat_deg, lon_deg, lon_0_deg=-75.0, h=DEFAULT_HEIGHT, req=DEFAULT_REQ, rpol=DEFAULT_RPOL))]
pub fn latlon_to_abi_angles(
    lat_deg: f64,
    lon_deg: f64,
    lon_0_deg: f64,
    h: f64,
    req: f64,
    rpol: f64,
) -> Option<(f64, f64)> {
    let lat_rad = deg_to_rad(lat_deg);
    let lon_rad = deg_to_rad(lon_deg);
    let lon_0_rad = deg_to_rad(lon_0_deg);

    let phi_c = ((rpol * rpol) / (req * req) * lat_rad.tan()).atan();
    let e2 = (req * req - rpol * rpol) / (req * req);
    let r_c = rpol / (1.0 - e2 * phi_c.cos().powi(2)).sqrt();

    let capital_h = h + req;
    let delta_lon = lon_rad - lon_0_rad;

    let sx = capital_h - r_c * phi_c.cos() * delta_lon.cos();
    let sy = -r_c * phi_c.cos() * delta_lon.sin();
    let sz = r_c * phi_c.sin();

    if (capital_h - sx) * capital_h < 0.0 || sx <= 0.0 {
        return None;
    }

    let x = (-sy / sx).atan();
    let y = (sz / (sx * sx + sy * sy).sqrt()).atan();
    Some((x, y))
}

/// Transforms GOES ABI scanning angles (x, y in radians) to WGS84 (latitude, longitude in degrees).
/// Returns None if the ray misses the Earth's ellipsoid (space pixels).
#[pyfunction]
#[pyo3(signature = (x_rad, y_rad, lon_0_deg=-75.0, h=DEFAULT_HEIGHT, req=DEFAULT_REQ, rpol=DEFAULT_RPOL))]
pub fn abi_angles_to_latlon(
    x_rad: f64,
    y_rad: f64,
    lon_0_deg: f64,
    h: f64,
    req: f64,
    rpol: f64,
) -> Option<(f64, f64)> {
    let capital_h = h + req;
    let cos_x = x_rad.cos();
    let sin_x = x_rad.sin();
    let cos_y = y_rad.cos();
    let sin_y = y_rad.sin();

    let a = sin_x.powi(2) + cos_x.powi(2) * (cos_y.powi(2) + (req.powi(2) / rpol.powi(2)) * sin_y.powi(2));
    let b = -2.0 * capital_h * cos_x * cos_y;
    let c = capital_h.powi(2) - req.powi(2);
    let disc = b.powi(2) - 4.0 * a * c;

    if disc < 0.0 {
        return None;
    }

    let rs = (-b - disc.sqrt()) / (2.0 * a);
    let sx = rs * cos_x * cos_y;
    let sy = -rs * sin_x;
    let sz = rs * cos_x * sin_y;

    let denom = ((capital_h - sx).powi(2) + sy.powi(2)).sqrt();
    let lat_rad = ((req.powi(2) / rpol.powi(2)) * (sz / denom)).atan();
    let lon_rad = deg_to_rad(lon_0_deg) - (sy / (capital_h - sx)).atan();

    Some((rad_to_deg(lat_rad), rad_to_deg(lon_rad)))
}

/// High-throughput batch transformation of latitude and longitude arrays to ABI scanning angles.
/// Multi-threaded SIMD execution via Rayon releasing the Python GIL.
/// Returns (xs, ys, valid_mask).
#[pyfunction]
#[pyo3(signature = (lats, lons, lon_0_deg=-75.0, h=DEFAULT_HEIGHT, req=DEFAULT_REQ, rpol=DEFAULT_RPOL))]
pub fn batch_latlon_to_abi_angles<'py>(
    py: Python<'py>,
    lats: PyReadonlyArrayDyn<'py, f64>,
    lons: PyReadonlyArrayDyn<'py, f64>,
    lon_0_deg: f64,
    h: f64,
    req: f64,
    rpol: f64,
) -> PyResult<(Bound<'py, PyArray1<f64>>, Bound<'py, PyArray1<f64>>, Bound<'py, PyArray1<bool>>)> {
    let lat_slice = lats.as_slice()?;
    let lon_slice = lons.as_slice()?;

    if lat_slice.len() != lon_slice.len() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Latitude and longitude array lengths must match",
        ));
    }

    let n = lat_slice.len();
    let mut xs = vec![0.0f64; n];
    let mut ys = vec![0.0f64; n];
    let mut valids = vec![false; n];

    py.allow_threads(|| {
        xs.par_iter_mut()
            .zip(ys.par_iter_mut())
            .zip(valids.par_iter_mut())
            .zip(lat_slice.par_iter().zip(lon_slice.par_iter()))
            .for_each(|(((x_out, y_out), valid_out), (&lat, &lon))| {
                if let Some((x, y)) = latlon_to_abi_angles(lat, lon, lon_0_deg, h, req, rpol) {
                    *x_out = x;
                    *y_out = y;
                    *valid_out = true;
                } else {
                    *x_out = f64::NAN;
                    *y_out = f64::NAN;
                    *valid_out = false;
                }
            });
    });

    Ok((
        xs.into_pyarray_bound(py),
        ys.into_pyarray_bound(py),
        valids.into_pyarray_bound(py),
    ))
}

/// High-throughput batch transformation of ABI scanning angle arrays to WGS84 latitude and longitude.
/// Multi-threaded SIMD execution via Rayon releasing the Python GIL.
/// Returns (lats, lons, valid_mask).
#[pyfunction]
#[pyo3(signature = (xs, ys, lon_0_deg=-75.0, h=DEFAULT_HEIGHT, req=DEFAULT_REQ, rpol=DEFAULT_RPOL))]
pub fn batch_abi_angles_to_latlon<'py>(
    py: Python<'py>,
    xs: PyReadonlyArrayDyn<'py, f64>,
    ys: PyReadonlyArrayDyn<'py, f64>,
    lon_0_deg: f64,
    h: f64,
    req: f64,
    rpol: f64,
) -> PyResult<(Bound<'py, PyArray1<f64>>, Bound<'py, PyArray1<f64>>, Bound<'py, PyArray1<bool>>)> {
    let x_slice = xs.as_slice()?;
    let y_slice = ys.as_slice()?;

    if x_slice.len() != y_slice.len() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "X and Y scanning angle array lengths must match",
        ));
    }

    let n = x_slice.len();
    let mut lats = vec![0.0f64; n];
    let mut lons = vec![0.0f64; n];
    let mut valids = vec![false; n];

    py.allow_threads(|| {
        lats.par_iter_mut()
            .zip(lons.par_iter_mut())
            .zip(valids.par_iter_mut())
            .zip(x_slice.par_iter().zip(y_slice.par_iter()))
            .for_each(|(((lat_out, lon_out), valid_out), (&x, &y))| {
                if let Some((lat, lon)) = abi_angles_to_latlon(x, y, lon_0_deg, h, req, rpol) {
                    *lat_out = lat;
                    *lon_out = lon;
                    *valid_out = true;
                } else {
                    *lat_out = f64::NAN;
                    *lon_out = f64::NAN;
                    *valid_out = false;
                }
            });
    });

    Ok((
        lats.into_pyarray_bound(py),
        lons.into_pyarray_bound(py),
        valids.into_pyarray_bound(py),
    ))
}
