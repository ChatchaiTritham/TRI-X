"""Deterministic evaluation metrics for the TRI-X empirical pipeline."""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(y_true == y_pred))


def bootstrap_accuracy_ci(y_true: np.ndarray, y_pred: np.ndarray,
                          n_boot: int = 10000, seed: int = 42,
                          alpha: float = 0.05) -> Tuple[float, float, float]:
    """Point accuracy and a percentile bootstrap CI (deterministic given seed)."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    correct = (y_true == y_pred).astype(float)
    point = float(correct.mean())
    idx = rng.integers(0, n, size=(n_boot, n))
    boot = correct[idx].mean(axis=1)
    lo = float(np.percentile(boot, 100 * alpha / 2))
    hi = float(np.percentile(boot, 100 * (1 - alpha / 2)))
    return point, lo, hi


def binary_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Sensitivity, specificity, PPV, NPV for a binary (1 = positive) problem."""
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    def _safe(a: int, b: int) -> float:
        return float(a / b) if b > 0 else 0.0

    return {
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "sensitivity": _safe(tp, tp + fn),
        "specificity": _safe(tn, tn + fp),
        "ppv": _safe(tp, tp + fp),
        "npv": _safe(tn, tn + fn),
    }


def bootstrap_metric_ci(y_true: np.ndarray, y_pred: np.ndarray, metric_key: str,
                        n_boot: int = 10000, seed: int = 42,
                        alpha: float = 0.05) -> Tuple[float, float]:
    """Percentile bootstrap CI for one binary metric (sensitivity/npv/...)."""
    rng = np.random.default_rng(seed + 1)
    n = len(y_true)
    vals = []
    for _ in range(n_boot):
        sel = rng.integers(0, n, size=n)
        m = binary_metrics(y_true[sel], y_pred[sel])
        vals.append(m[metric_key])
    lo = float(np.percentile(vals, 100 * alpha / 2))
    hi = float(np.percentile(vals, 100 * (1 - alpha / 2)))
    return lo, hi


def mcnemar_test(y_true: np.ndarray, pred_a: np.ndarray, pred_b: np.ndarray) -> Dict[str, float]:
    """McNemar's test comparing two classifiers' correctness on the same cases.

    Returns the discordant counts (b, c), the (continuity-corrected) chi-square
    statistic, and the exact binomial two-sided p-value (robust for small counts).
    """
    from scipy.stats import binomtest, chi2

    a_correct = (pred_a == y_true)
    b_correct = (pred_b == y_true)
    # b: A correct, B wrong ; c: A wrong, B correct
    b = int(np.sum(a_correct & ~b_correct))
    c = int(np.sum(~a_correct & b_correct))
    n_disc = b + c
    if n_disc == 0:
        return {"b": b, "c": c, "chi2": 0.0, "p_value": 1.0}
    stat = (abs(b - c) - 1) ** 2 / n_disc
    p_chi = float(chi2.sf(stat, df=1))
    p_exact = float(binomtest(min(b, c), n_disc, 0.5, alternative="two-sided").pvalue)
    return {"b": b, "c": c, "chi2": float(stat), "p_value_chi2": p_chi, "p_value": p_exact}


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    from sklearn.metrics import f1_score

    return float(f1_score(y_true, y_pred, average="macro"))
