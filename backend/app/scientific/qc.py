from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import numpy as np

try:
    import cyclonesense_core as cs_core
    HAS_RUST_CORE = True
except ImportError:
    cs_core = None
    HAS_RUST_CORE = False


class QCStatus(str, Enum):
    PASSED = "PASSED"
    DEGRADED = "DEGRADED"
    REJECTED = "REJECTED"


@dataclass
class QCResult:
    status: QCStatus
    physical_bounds_passed: bool
    missing_pixel_percentage: float
    dqf_summary: Dict[str, Any] = field(default_factory=dict)
    anomalies: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "physical_bounds_passed": self.physical_bounds_passed,
            "missing_pixel_percentage": round(self.missing_pixel_percentage, 2),
            "dqf_summary": self.dqf_summary,
            "anomalies": self.anomalies,
            "metrics": self.metrics,
        }


class QualityControlEngine:
    """
    Scientific validation and physical sanity gate for meteorological satellite arrays.
    Powered by the high-performance Rust scientific core (`cyclonesense_core`) with
    strict algorithmic parity fallback in pure NumPy.
    """

    DEFAULT_LIMITS = {
        "brightness_temperature": {"min": 160.0, "max": 340.0, "unit": "K"},
        "radiance": {"min": 0.0, "max": 250.0, "unit": "mW/(m2 sr cm-1)"},
        "wind_speed": {"min": 0.0, "max": 120.0, "unit": "m/s"},
        "central_pressure": {"min": 850.0, "max": 1050.0, "unit": "hPa"},
    }

    @classmethod
    def evaluate_array(
        cls,
        data: np.ndarray,
        variable_name: str,
        units: str = "",
        dqf_mask: Optional[np.ndarray] = None,
        max_missing_pct: float = 15.0,
    ) -> QCResult:
        """
        Evaluate an extracted numerical array against physical sanity laws and missing pixel limits.
        Dispatches to single-pass Rust Welford engine when available, releasing the GIL.
        """
        total_elements = data.size
        if total_elements == 0:
            return QCResult(
                status=QCStatus.REJECTED,
                physical_bounds_passed=False,
                missing_pixel_percentage=100.0,
                anomalies=["Array has 0 elements"],
            )

        # Resolve variable physical limits
        norm_var = variable_name.lower()
        limit_key = None
        if any(term in norm_var for term in ["temp", "tb", "bt", "cmi", "band14", "band13", "band15"]):
            limit_key = "brightness_temperature"
        elif any(term in norm_var for term in ["rad", "radiance"]):
            limit_key = "radiance"
        elif any(term in norm_var for term in ["wind", "vmax", "speed"]):
            limit_key = "wind_speed"
        elif any(term in norm_var for term in ["pres", "pressure", "pmin"]):
            limit_key = "central_pressure"

        min_limit, max_limit = None, None
        unit = units
        if limit_key and limit_key in cls.DEFAULT_LIMITS:
            limits = cls.DEFAULT_LIMITS[limit_key]
            min_limit, max_limit = limits["min"], limits["max"]
            if not unit:
                unit = limits["unit"]

        if HAS_RUST_CORE and cs_core is not None:
            # Single-pass Rayon/Welford Rust core evaluation (releases GIL)
            c_data = np.ascontiguousarray(data, dtype=np.float32)
            rust_res = cs_core.evaluate_array_qc(
                c_data,
                variable_name=variable_name,
                min_limit=min_limit,
                max_limit=max_limit,
                unit=unit,
                max_missing_pct=float(max_missing_pct),
            )
            status = QCStatus(rust_res["status"])
            bounds_passed = bool(rust_res["physical_bounds_passed"])
            missing_pct = float(rust_res["missing_pixel_percentage"])
            anomalies = list(rust_res["anomalies"])
            metrics = {
                "total_pixels": int(rust_res["total_pixels"]),
                "valid_pixels": int(rust_res["valid_pixels"]),
                "missing_pixels": int(rust_res["missing_pixels"]),
                "missing_percentage": round(missing_pct, 2),
            }
            if metrics["valid_pixels"] > 0:
                metrics.update({
                    "min": round(float(rust_res["min"]), 3),
                    "max": round(float(rust_res["max"]), 3),
                    "mean": round(float(rust_res["mean"]), 3),
                    "std": round(float(rust_res["std"]), 3),
                })
        else:
            # Algorithmic parity fallback in pure NumPy
            nan_mask = np.isnan(data) | np.isinf(data)
            nan_count = int(np.sum(nan_mask))
            missing_pct = (nan_count / total_elements) * 100.0

            anomalies = []
            bounds_passed = True
            status = QCStatus.PASSED

            valid_data = data[~nan_mask]

            metrics = {
                "total_pixels": total_elements,
                "valid_pixels": int(valid_data.size),
                "missing_pixels": nan_count,
                "missing_percentage": round(missing_pct, 2),
            }

            if valid_data.size > 0:
                data_min = float(np.min(valid_data))
                data_max = float(np.max(valid_data))
                data_mean = float(np.mean(valid_data))
                data_std = float(np.std(valid_data))

                metrics.update({
                    "min": round(data_min, 3),
                    "max": round(data_max, 3),
                    "mean": round(data_mean, 3),
                    "std": round(data_std, 3),
                })

                if min_limit is not None and data_min < min_limit:
                    bounds_passed = False
                    u = f" {unit}" if unit else ""
                    anomalies.append(f"Physical lower bound violated for {variable_name}: min {data_min:.2f} < {min_limit}{u}")
                if max_limit is not None and data_max > max_limit:
                    bounds_passed = False
                    u = f" {unit}" if unit else ""
                    anomalies.append(f"Physical upper bound violated for {variable_name}: max {data_max:.2f} > {max_limit}{u}")
            else:
                bounds_passed = False
                anomalies.append(f"All {total_elements} pixels in {variable_name} are NaN/missing")

            # Missing pixel percentage check
            if missing_pct > max_missing_pct:
                if missing_pct >= 50.0:
                    status = QCStatus.REJECTED
                    anomalies.append(f"Excessive missing pixels: {missing_pct:.1f}% exceeds rejection limit (50%)")
                else:
                    status = QCStatus.DEGRADED
                    anomalies.append(f"Elevated missing pixels: {missing_pct:.1f}% exceeds nominal threshold ({max_missing_pct}%)")

            if not bounds_passed and status == QCStatus.PASSED:
                status = QCStatus.DEGRADED

        # DQF Evaluation if provided
        dqf_summary: Dict[str, Any] = {}
        if dqf_mask is not None and dqf_mask.size == total_elements:
            unique_flags, counts = np.unique(dqf_mask, return_counts=True)
            for flag, count in zip(unique_flags, counts):
                flag_pct = (int(count) / total_elements) * 100.0
                dqf_summary[f"flag_{int(flag)}"] = {
                    "count": int(count),
                    "percentage": round(flag_pct, 2)
                }
            good_pixels = int(np.sum(dqf_mask == 0))
            good_pct = (good_pixels / total_elements) * 100.0
            dqf_summary["nominal_good_percentage"] = round(good_pct, 2)
            if good_pct < (100.0 - max_missing_pct) and status == QCStatus.PASSED:
                status = QCStatus.DEGRADED
                anomalies.append(f"Data Quality Flags indicate non-nominal instrument state (good pixels: {good_pct:.1f}%)")

        return QCResult(
            status=status,
            physical_bounds_passed=bounds_passed,
            missing_pixel_percentage=missing_pct,
            dqf_summary=dqf_summary,
            anomalies=anomalies,
            metrics=metrics,
        )
