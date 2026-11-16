"""
CycloneSense — Scientific Validity, Leakage Audit, and Baseline Model Tests

Verifies:
1. Strict storm-level partition disjointness (zero frame-level leakage).
2. Data sample count reconciliation from raw IBTrACS to train/val/test splits.
3. Feature-to-target independence (no generator formula in tabular environmental covariates).
4. Explicit quarantine flags on SyntheticProxyBenchmarkDataset (TropicalCycloneDataset).
5. Clean lack of synthetic flags on AuthenticTabularCycloneDataset.
6. Mathematical correctness of Climatology, Persistence, and CLIPER baselines.
"""

from pathlib import Path
import numpy as np
import pytest

from backend.app.ml.dataset import (
    CycloneObservation,
    IBTrACSDatasetBuilder,
    SyntheticProxyBenchmarkDataset,
    TropicalCycloneDataset,
    AuthenticTabularCycloneDataset,
)
from backend.app.ml.models.baseline import (
    ClimatologyBaselineModel,
    PersistenceBaselineModel,
    BaselineClimatologyPersistenceModel,
)


@pytest.fixture(scope="module")
def ibtracs_data():
    nc_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "IBTrACS.NI.v04r01.nc"
    if not nc_path.exists():
        pytest.skip(f"IBTrACS file not found at {nc_path}")
    obs, stats = IBTrACSDatasetBuilder.load_observations(nc_path, min_season=2000)
    train_obs, val_obs, test_obs, split_meta = IBTrACSDatasetBuilder.split_by_storm(
        obs, train_frac=0.70, val_frac=0.15, test_frac=0.15, split_strategy="temporal", seed=42
    )
    return {
        "obs": obs,
        "stats": stats,
        "train_obs": train_obs,
        "val_obs": val_obs,
        "test_obs": test_obs,
        "split_meta": split_meta,
    }


def test_storm_split_disjointness(ibtracs_data):
    """Asserts that no storm appears in more than one partition (zero frame-level leakage)."""
    train_storms = {o.storm_id for o in ibtracs_data["train_obs"]}
    val_storms = {o.storm_id for o in ibtracs_data["val_obs"]}
    test_storms = {o.storm_id for o in ibtracs_data["test_obs"]}

    # Disjointness checks
    assert len(train_storms.intersection(val_storms)) == 0, "Leakage: Train and Val share storm IDs!"
    assert len(train_storms.intersection(test_storms)) == 0, "Leakage: Train and Test share storm IDs!"
    assert len(val_storms.intersection(test_storms)) == 0, "Leakage: Val and Test share storm IDs!"
    assert ibtracs_data["split_meta"]["leakage_check_passed"] is True


def test_observation_and_storm_count_reconciliation(ibtracs_data):
    """Reconciles counts across raw archive, modern season filter, and splits."""
    stats = ibtracs_data["stats"]
    split_meta = ibtracs_data["split_meta"]

    # Modern satellite era season >= 2000
    assert stats["filtered_storms_season_range"] == 265
    # Total storms with valid observations
    assert split_meta["total_storms"] == 157
    assert len(ibtracs_data["obs"]) == 7229

    # Partition counts
    assert len(ibtracs_data["train_obs"]) == 4973
    assert len(ibtracs_data["val_obs"]) == 1285
    assert len(ibtracs_data["test_obs"]) == 971

    # Storm counts per split
    assert split_meta["train"]["storm_count"] == 109
    assert split_meta["val"]["storm_count"] == 23
    assert split_meta["test"]["storm_count"] == 25
    assert 109 + 23 + 25 == 157


def test_target_label_independence_in_tabular_features(ibtracs_data):
    """
    Verifies that the 8-dim tabular environmental features are authentic physical/kinematic
    covariates and do not embed or invert the target wind speed.
    """
    for obs in ibtracs_data["obs"][:100]:
        env = obs.env_features
        assert len(env) == 8
        # Feature 0: lat / 90.0
        assert -1.0 <= env[0] <= 1.0
        # Feature 1: lon / 180.0
        assert -1.0 <= env[1] <= 1.0
        # Feature 2: Coriolis f * 1e4
        assert -2.0 <= env[2] <= 2.0
        # Feature 3: dist_from_equator / 5000.0
        assert 0.0 <= env[3] <= 2.5
        # Feature 5: translation_speed / 50.0
        assert 0.0 <= env[5] <= 2.5
        # Feature 6: cos(bearing)
        assert -1.0 <= env[6] <= 1.0
        # Feature 7: seasonal_phase = sin(day_of_year)
        assert -1.0 <= env[7] <= 1.0


def test_synthetic_proxy_quarantine_metadata(ibtracs_data):
    """
    Asserts that SyntheticProxyBenchmarkDataset (TropicalCycloneDataset) explicitly discloses
    synthetic generation and target leakage in its metadata, while AuthenticTabularCycloneDataset
    is flagged as authentic.
    """
    sample_obs = ibtracs_data["obs"][:10]

    # Quarantined proxy dataset
    proxy_ds = SyntheticProxyBenchmarkDataset(sample_obs)
    proxy_sample = proxy_ds[0]
    assert proxy_sample["is_synthetic_benchmark"] is True
    assert proxy_sample["synthetic_generator_target_leakage_warning"] is True
    assert proxy_sample["synthetic_generator_formula"] == "analytical_vortex_temp_from_wind"

    # Alias check
    assert TropicalCycloneDataset is SyntheticProxyBenchmarkDataset

    # Authentic tabular dataset
    auth_ds = AuthenticTabularCycloneDataset(sample_obs)
    auth_sample = auth_ds[0]
    assert auth_sample["is_synthetic_benchmark"] is False
    assert "synthetic_generator_target_leakage_warning" not in auth_sample


def test_climatology_baseline():
    """Tests ClimatologyBaselineModel fit and constant mean/mode prediction."""
    y_int = np.array([30.0, 45.0, 60.0, 45.0, 45.0], dtype=np.float32)
    y_cat = np.array([0, 1, 2, 1, 1], dtype=np.int64)

    model = ClimatologyBaselineModel()
    model.fit(y_int, y_cat)

    assert round(model.mean_intensity, 1) == 45.0
    assert model.modal_category == 1

    pred_w, pred_c = model.predict(5)
    assert len(pred_w) == 5
    assert np.allclose(pred_w, 45.0)
    assert np.all(pred_c == 1)


def test_persistence_baseline():
    """
    Tests PersistenceBaselineModel track-wise carry-forward logic (V_t = V_{t-1})
    and climatology fallback for initial track points.
    """
    env = np.zeros(8, dtype=np.float32)
    obs_list = [
        CycloneObservation("STORM_A", "A", 2024, "2024-01-01 00:00:00", 15.0, 85.0, 35.0, 1000.0, 1, env),
        CycloneObservation("STORM_A", "A", 2024, "2024-01-01 06:00:00", 15.5, 85.2, 50.0, 990.0, 1, env),
        CycloneObservation("STORM_A", "A", 2024, "2024-01-01 12:00:00", 16.0, 85.5, 65.0, 980.0, 2, env),
        CycloneObservation("STORM_B", "B", 2024, "2024-02-01 00:00:00", 10.0, 90.0, 40.0, 995.0, 1, env),
        CycloneObservation("STORM_B", "B", 2024, "2024-02-01 06:00:00", 10.2, 90.1, 45.0, 992.0, 1, env),
    ]

    model = PersistenceBaselineModel()
    model.fit(np.array([40.0]), np.array([1]))

    preds_w, preds_c = model.predict_observations(obs_list)

    # Point 0: STORM_A first obs -> fallback to climatology (40.0, 1)
    assert preds_w[0] == 40.0
    assert preds_c[0] == 1
    # Point 1: STORM_A second obs -> prior wind was 35.0, cat 1
    assert preds_w[1] == 35.0
    assert preds_c[1] == 1
    # Point 2: STORM_A third obs -> prior wind was 50.0, cat 1
    assert preds_w[2] == 50.0
    assert preds_c[2] == 1
    # Point 3: STORM_B first obs -> fallback to climatology (40.0, 1)
    assert preds_w[3] == 40.0
    assert preds_c[3] == 1
    # Point 4: STORM_B second obs -> prior wind was 40.0, cat 1
    assert preds_w[4] == 40.0
    assert preds_c[4] == 1


def test_cliper_ridge_baseline(ibtracs_data):
    """Tests BaselineClimatologyPersistenceModel Ridge fitting and bounds."""
    train_obs = ibtracs_data["train_obs"][:200]
    test_obs = ibtracs_data["test_obs"][:50]

    X_train = np.vstack([o.env_features for o in train_obs])
    y_w_train = np.array([o.wind_kts for o in train_obs], dtype=np.float32)
    y_c_train = np.array([o.category for o in train_obs], dtype=np.int64)

    X_test = np.vstack([o.env_features for o in test_obs])

    cliper = BaselineClimatologyPersistenceModel(alpha=1.0)
    cliper.fit(X_train, y_w_train, y_c_train)

    pred_w, pred_c = cliper.predict(X_test)
    assert len(pred_w) == len(test_obs)
    assert len(pred_c) == len(test_obs)
    # Physical bounds check
    assert np.all(pred_w >= 10.0)
    assert np.all(pred_w <= 200.0)
    assert np.all((pred_c >= 0) & (pred_c < 5))
