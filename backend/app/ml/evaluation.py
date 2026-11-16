from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score


class EvaluationMetrics:
    """
    Standard meteorological and statistical metrics for tropical cyclone pattern intelligence.
    Computes intensity metrics (MAE, RMSE, Bias, R2) and classification metrics (Precision, Recall, Macro-F1).
    """

    @staticmethod
    def compute_intensity_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Computes regression metrics for intensity (knots):
        - MAE: Mean Absolute Error
        - RMSE: Root Mean Squared Error
        - Bias: Mean Signed Error (y_pred - y_true)
        - Correlation: Pearson correlation coefficient
        """
        y_true = np.asarray(y_true, dtype=np.float64)
        y_pred = np.asarray(y_pred, dtype=np.float64)

        if len(y_true) == 0:
            return {"sample_count": 0, "mae": 0.0, "rmse": 0.0, "bias": 0.0, "correlation": 0.0}

        diff = y_pred - y_true
        mae = float(np.mean(np.abs(diff)))
        rmse = float(np.sqrt(np.mean(diff ** 2)))
        bias = float(np.mean(diff))

        # Pearson correlation
        if len(y_true) > 1 and np.std(y_true) > 1e-6 and np.std(y_pred) > 1e-6:
            corr = float(np.corrcoef(y_true, y_pred)[0, 1])
        else:
            corr = 0.0

        return {
            "sample_count": len(y_true),
            "mae_kts": round(mae, 3),
            "rmse_kts": round(rmse, 3),
            "bias_kts": round(bias, 3),
            "pearson_r": round(corr, 3),
        }

    @staticmethod
    def compute_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """
        Computes multi-class pattern classification metrics:
        - Accuracy
        - Precision (Macro & Weighted)
        - Recall (Macro & Weighted)
        - Macro-F1
        - Confusion Matrix
        """
        y_true = np.asarray(y_true, dtype=np.int64)
        y_pred = np.asarray(y_pred, dtype=np.int64)

        if len(y_true) == 0:
            return {
                "sample_count": 0,
                "accuracy": 0.0,
                "precision_macro": 0.0,
                "recall_macro": 0.0,
                "f1_macro": 0.0,
            }

        acc = float(accuracy_score(y_true, y_pred))
        p_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
        r_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
        f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        p_weighted = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
        r_weighted = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
        f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

        return {
            "sample_count": len(y_true),
            "accuracy": round(acc, 4),
            "precision_macro": round(p_macro, 4),
            "recall_macro": round(r_macro, 4),
            "f1_macro": round(f1_macro, 4),
            "f1_weighted": round(f1_weighted, 4),
        }

    @staticmethod
    def compute_confidence_intervals(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        n_bootstraps: int = 500,
        ci: float = 0.95,
        seed: int = 42,
    ) -> Dict[str, Dict[str, float]]:
        y_true = np.asarray(y_true, dtype=np.float64)
        y_pred = np.asarray(y_pred, dtype=np.float64)
        n = len(y_true)
        if n < 2:
            return {"mae_ci": {"low": 0.0, "high": 0.0}, "rmse_ci": {"low": 0.0, "high": 0.0}}

        rng = np.random.RandomState(seed)
        diff = y_pred - y_true
        abs_diff = np.abs(diff)
        sq_diff = diff ** 2

        mae_samples, rmse_samples = [], []
        for _ in range(n_bootstraps):
            idx = rng.randint(0, n, size=n)
            mae_samples.append(float(np.mean(abs_diff[idx])))
            rmse_samples.append(float(np.sqrt(np.mean(sq_diff[idx]))))

        alpha = (1.0 - ci) / 2.0
        low_idx = int(alpha * n_bootstraps)
        high_idx = int((1.0 - alpha) * n_bootstraps)
        mae_sorted = sorted(mae_samples)
        rmse_sorted = sorted(rmse_samples)
        return {
            "mae_ci": {"low": round(mae_sorted[low_idx], 3), "high": round(mae_sorted[high_idx], 3)},
            "rmse_ci": {"low": round(rmse_sorted[low_idx], 3), "high": round(rmse_sorted[high_idx], 3)},
        }

    @staticmethod
    def compute_stratified_metrics(
        y_true_wind: np.ndarray,
        y_pred_wind: np.ndarray,
        y_true_cat: np.ndarray,
    ) -> Dict[str, Dict[str, Any]]:
        category_names = {
            0: "Depression (< 34 kts)",
            1: "Cyclonic Storm (34-63 kts)",
            2: "Very Severe CS (64-89 kts)",
            3: "Extremely Severe CS (90-119 kts)",
            4: "Super Cyclonic Storm (>= 120 kts)",
        }
        y_true_w = np.asarray(y_true_wind, dtype=np.float64)
        y_pred_w = np.asarray(y_pred_wind, dtype=np.float64)
        y_true_c = np.asarray(y_true_cat, dtype=np.int64)

        stratified = {}
        for cat_idx, cat_name in category_names.items():
            mask = y_true_c == cat_idx
            count = int(np.sum(mask))
            if count == 0:
                stratified[cat_name] = {"sample_count": 0, "mae_kts": None, "rmse_kts": None}
                continue

            sub_diff = y_pred_w[mask] - y_true_w[mask]
            stratified[cat_name] = {
                "sample_count": count,
                "mae_kts": round(float(np.mean(np.abs(sub_diff))), 3),
                "rmse_kts": round(float(np.sqrt(np.mean(sub_diff ** 2))), 3),
                "bias_kts": round(float(np.mean(sub_diff)), 3),
            }
        return stratified


class ModelEvaluator:
    """
    Evaluates neural and baseline models on test DataLoader without temporal or frame-level leakage.
    Collects real predictions, ground truths, and metrics.
    """

    @classmethod
    @torch.no_grad()
    def evaluate_pytorch_model(
        cls,
        model: nn.Module,
        data_loader: torch.utils.data.DataLoader,
        model_type: str = "fusion",  # 'image', 'environment', or 'fusion'
        device: torch.device = torch.device("cpu"),
    ) -> Dict[str, Any]:
        model.eval()
        model.to(device)

        y_true_wind: List[float] = []
        y_pred_wind: List[float] = []
        y_true_cat: List[int] = []
        y_pred_cat: List[int] = []

        total_batches = 0
        total_samples = 0

        for batch in data_loader:
            target_wind = batch["target_intensity"].cpu().numpy()
            target_cat = batch["target_category"].cpu().numpy()

            if model_type == "image":
                imgs = batch["image"].to(device)
                out = model(imgs)
            elif model_type == "environment":
                env = batch["environment"].to(device)
                out = model(env)
            elif model_type == "fusion":
                imgs = batch["image"].to(device)
                env = batch["environment"].to(device)
                out = model(imgs, env)
            else:
                raise ValueError(f"Unknown model_type: {model_type}")

            pred_w = out["pred_intensity"].cpu().numpy()
            pred_logits = out["category_logits"].cpu().numpy()
            pred_c = np.argmax(pred_logits, axis=-1)

            y_true_wind.extend(target_wind.tolist())
            y_pred_wind.extend(pred_w.tolist())
            y_true_cat.extend(target_cat.tolist())
            y_pred_cat.extend(pred_c.tolist())

            total_batches += 1
            total_samples += len(target_wind)

        arr_true_w = np.array(y_true_wind)
        arr_pred_w = np.array(y_pred_wind)
        arr_true_c = np.array(y_true_cat)
        arr_pred_c = np.array(y_pred_cat)

        intensity_metrics = EvaluationMetrics.compute_intensity_metrics(arr_true_w, arr_pred_w)
        intensity_metrics.update(EvaluationMetrics.compute_confidence_intervals(arr_true_w, arr_pred_w))
        classification_metrics = EvaluationMetrics.compute_classification_metrics(arr_true_c, arr_pred_c)
        stratified_metrics = EvaluationMetrics.compute_stratified_metrics(arr_true_w, arr_pred_w, arr_true_c)

        return {
            "model_type": model_type,
            "total_samples_evaluated": total_samples,
            "intensity_metrics": intensity_metrics,
            "classification_metrics": classification_metrics,
            "stratified_metrics": stratified_metrics,
        }

    @classmethod
    def evaluate_baseline_model(
        cls,
        baseline_model: Any,
        data_loader: torch.utils.data.DataLoader,
    ) -> Dict[str, Any]:
        """Evaluates tabular baseline model on data loader."""
        all_env: List[np.ndarray] = []
        y_true_w: List[float] = []
        y_true_c: List[int] = []

        for batch in data_loader:
            all_env.append(batch["environment"].cpu().numpy())
            y_true_w.extend(batch["target_intensity"].cpu().numpy().tolist())
            y_true_c.extend(batch["target_category"].cpu().numpy().tolist())

        X = np.vstack(all_env)
        arr_true_w = np.array(y_true_w)
        arr_true_c = np.array(y_true_c)

        pred_w, pred_c = baseline_model.predict(X)

        intensity_metrics = EvaluationMetrics.compute_intensity_metrics(arr_true_w, pred_w)
        intensity_metrics.update(EvaluationMetrics.compute_confidence_intervals(arr_true_w, pred_w))
        classification_metrics = EvaluationMetrics.compute_classification_metrics(arr_true_c, pred_c)
        stratified_metrics = EvaluationMetrics.compute_stratified_metrics(arr_true_w, pred_w, arr_true_c)

        return {
            "model_type": "baseline_cliper",
            "total_samples_evaluated": len(arr_true_w),
            "intensity_metrics": intensity_metrics,
            "classification_metrics": classification_metrics,
            "stratified_metrics": stratified_metrics,
        }
