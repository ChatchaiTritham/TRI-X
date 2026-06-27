"""Focused unit tests for TRI-X pure/deterministic logic.

These complement the repo's existing tests and target hand-verifiable
behaviour: triage risk-level thresholds, governance gating, metric
correctness on tiny inputs, and rule-baseline determinism.
"""

import os
import sys

import numpy as np
import pytest

# Ensure the repo `src/` layout is importable regardless of pytest rootdir.
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(os.path.dirname(_HERE), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from trix.triage import TriageModule, RiskLevel  # noqa: E402
from trix.governance import SRGL, ScreeningPolicy  # noqa: E402
from trix.empirical import metrics as M  # noqa: E402
from trix.empirical import RuleBasedTriage, generate_cohort, FEATURE_NAMES  # noqa: E402


# --------------------------------------------------------------------------- #
# Triage threshold / risk-level logic                                         #
# --------------------------------------------------------------------------- #

def test_triage_unweighted_score_is_mean_and_level_correct():
    t = TriageModule(enable_logging=False)
    # mean = (0.9 + 0.9 + 0.9)/3 = 0.9 -> CRITICAL (>= 0.9)
    res = t.assess({"features": {"a": 0.9, "b": 0.9, "c": 0.9}})
    assert res.risk_score == pytest.approx(0.9)
    assert res.risk_level == RiskLevel.CRITICAL


def test_triage_determine_level_monotonic_boundaries():
    t = TriageModule(enable_logging=False)
    # Direct check of the private threshold mapping at exact boundaries.
    assert t._determine_risk_level(0.0) == RiskLevel.MINIMAL
    assert t._determine_risk_level(0.3) == RiskLevel.LOW
    assert t._determine_risk_level(0.5) == RiskLevel.MEDIUM
    assert t._determine_risk_level(0.7) == RiskLevel.HIGH
    assert t._determine_risk_level(0.95) == RiskLevel.CRITICAL


def test_triage_empty_features_yields_zero_score():
    t = TriageModule(enable_logging=False)
    res = t.assess({"features": {}})
    assert res.risk_score == 0.0
    assert res.risk_level == RiskLevel.MINIMAL


def test_triage_weighted_score():
    # weighted_sum / total_weight = (1.0*3 + 0.0*1) / 4 = 0.75
    t = TriageModule(feature_weights={"x": 3.0, "y": 1.0}, enable_logging=False)
    res = t.assess({"features": {"x": 1.0, "y": 0.0}})
    assert res.risk_score == pytest.approx(0.75)
    assert res.risk_level == RiskLevel.HIGH


# --------------------------------------------------------------------------- #
# Governance gating logic                                                      #
# --------------------------------------------------------------------------- #

def test_governance_conservative_blocks_high_risk():
    t = TriageModule(enable_logging=False)
    high = t.assess({"features": {"a": 0.95, "b": 0.95}})  # CRITICAL
    g = SRGL(screening_policy=ScreeningPolicy.CONSERVATIVE, enable_logging=False)
    out = g.screen(high)
    assert out.approved is False
    assert any("human review" in v for v in out.violations)


def test_governance_conservative_approves_clean_low_risk():
    t = TriageModule(enable_logging=False)
    low = t.assess({"features": {"a": 0.1, "b": 0.1}})  # MINIMAL, has features
    g = SRGL(screening_policy=ScreeningPolicy.CONSERVATIVE, enable_logging=False)
    out = g.screen(low)
    assert out.approved is True
    assert out.violations == []
    assert out.constraints_met is True


# --------------------------------------------------------------------------- #
# Metrics correctness on tiny hand-made inputs                                 #
# --------------------------------------------------------------------------- #

def test_binary_metrics_known_confusion_matrix():
    y_true = np.array([1, 1, 0, 0])
    y_pred = np.array([1, 0, 0, 1])  # tp=1, fn=1, tn=1, fp=1
    m = M.binary_metrics(y_true, y_pred)
    assert (m["tp"], m["fn"], m["tn"], m["fp"]) == (1, 1, 1, 1)
    assert m["sensitivity"] == pytest.approx(0.5)
    assert m["specificity"] == pytest.approx(0.5)
    assert m["ppv"] == pytest.approx(0.5)
    assert m["npv"] == pytest.approx(0.5)


def test_accuracy_and_perfect_prediction_metrics():
    y = np.array([1, 0, 1, 0])
    assert M.accuracy(y, y) == pytest.approx(1.0)
    m = M.binary_metrics(y, y)
    assert m["sensitivity"] == pytest.approx(1.0)
    assert m["specificity"] == pytest.approx(1.0)


def test_bootstrap_accuracy_ci_seed_reproducible_and_bounded():
    y_true = np.array([1, 1, 0, 0, 1, 0, 1, 0])
    y_pred = np.array([1, 0, 0, 0, 1, 1, 1, 0])
    p1, lo1, hi1 = M.bootstrap_accuracy_ci(y_true, y_pred, n_boot=500, seed=42)
    p2, lo2, hi2 = M.bootstrap_accuracy_ci(y_true, y_pred, n_boot=500, seed=42)
    assert (p1, lo1, hi1) == (p2, lo2, hi2)  # deterministic given seed
    assert 0.0 <= lo1 <= p1 <= hi1 <= 1.0


# --------------------------------------------------------------------------- #
# Rule-baseline: deterministic, high-sensitivity for central cases            #
# --------------------------------------------------------------------------- #

def test_rule_baseline_predict_central_deterministic_and_binary():
    c = generate_cohort(n=200, seed=42)
    rb = RuleBasedTriage()
    p1 = rb.predict_central(c.X)
    p2 = rb.predict_central(c.X)
    assert np.array_equal(p1, p2)
    assert set(np.unique(p1).tolist()) <= {0, 1}
    assert p1.shape[0] == c.X.shape[0]


def test_rule_baseline_central_score_increases_with_red_flags():
    rb = RuleBasedTriage()
    idx = {n: i for i, n in enumerate(FEATURE_NAMES)}
    benign = np.zeros(len(FEATURE_NAMES))
    danger = np.zeros(len(FEATURE_NAMES))
    for f in ("head_impulse_normal", "skew_deviation", "focal_neuro_deficit",
              "nystagmus_vertical"):
        danger[idx[f]] = 1.0
    assert rb._central_score(danger) > rb._central_score(benign)
    X = np.vstack([benign, danger])
    pred = rb.predict_central(X)
    assert pred[0] == 0 and pred[1] == 1
