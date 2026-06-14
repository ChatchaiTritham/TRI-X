"""Smoke + determinism tests for the TRI-X empirical pipeline."""

import numpy as np

from trix.empirical import (
    CENTRAL_DANGEROUS,
    DIAGNOSES,
    FEATURE_NAMES,
    RuleBasedTriage,
    TRIXEnsemble,
    generate_cohort,
)
from trix.empirical import explain as xai
from trix.empirical import metrics as M


def test_cohort_is_deterministic() -> None:
    a = generate_cohort(n=400, seed=42)
    b = generate_cohort(n=400, seed=42)
    assert np.array_equal(a.X, b.X)
    assert np.array_equal(a.y, b.y)
    assert a.X.shape == (400, len(FEATURE_NAMES))
    assert set(a.y_central.tolist()) <= {0, 1}


def test_central_label_matches_diagnosis() -> None:
    c = generate_cohort(n=300, seed=42)
    central_idx = {i for i, n in enumerate(DIAGNOSES) if n in CENTRAL_DANGEROUS}
    expected = np.array([1 if int(d) in central_idx else 0 for d in c.y])
    assert np.array_equal(expected, c.y_central)


def test_ensemble_trains_and_predicts() -> None:
    c = generate_cohort(n=800, seed=42)
    ens = TRIXEnsemble(seed=42).fit(c.X[:600], c.y[:600], y_central=c.y_central[:600])
    preds = ens.predict(c.X[600:])
    assert preds.shape[0] == 200
    central = ens.predict_central(c.X[600:])
    assert set(central.tolist()) <= {0, 1}
    assert "RandomForest" in ens.info.component_names


def test_rule_baseline_runs() -> None:
    c = generate_cohort(n=300, seed=42)
    rules = RuleBasedTriage()
    assert rules.predict(c.X).shape[0] == 300
    assert set(rules.predict_central(c.X).tolist()) <= {0, 1}


def test_binary_metrics_and_mcnemar() -> None:
    y = np.array([1, 0, 1, 0, 1, 0])
    a = np.array([1, 0, 1, 0, 1, 1])
    b = np.array([0, 0, 1, 0, 1, 0])
    m = M.binary_metrics(y, a)
    assert 0.0 <= m["sensitivity"] <= 1.0
    out = M.mcnemar_test(y, a, b)
    assert "p_value" in out


def test_real_shap_runs() -> None:
    c = generate_cohort(n=400, seed=42)
    ens = TRIXEnsemble(seed=42).fit(c.X[:300], c.y[:300], y_central=c.y_central[:300])
    res = xai.compute_shap(ens.rf, c.X[:50], c.X[300:330], c.feature_names)
    assert res["available"] is True
    assert len(res["global_importance"]) == len(c.feature_names)
