"""EXPLORATORY effectiveness pipeline for TRI-X (seed = 42) — OUTSIDE manuscript scope.

This script is SUPPLEMENTARY. The TRI-X manuscript (JIIS) is a methodological /
governance framework and reports *no quantitative effectiveness claims*. It evaluates
decision behaviour (safety-gate compliance, stability under missingness, trace
completeness), not diagnostic accuracy. The numbers produced here (multiclass accuracy,
sensitivity/specificity/PPV/NPV, McNemar, SHAP/LIME/DiCE) are an exploratory ML study
on a synthetic cohort and are NOT part of the paper's claims. See
``experimental/effectiveness/README.md``.

For the artefacts the paper DOES report, run the primary entry point instead:

    python scripts/run_framework.py

What this exploratory pipeline does, from REAL reproducible computation on a documented
SYNTHETIC cohort:

1. Generate a synthetic ED vestibular triage cohort (``trix.empirical.cohort``).
2. Train the real ensemble: Random Forest + (XGBoost | GradientBoosting) + MLP
   (``trix.empirical.ensemble``).
3. Evaluate diagnostic accuracy (+ bootstrap 95% CI), stroke/TIA sensitivity, NPV,
   specificity, PPV; compare against a rule-based baseline and a standalone single ML
   model with McNemar's test (``trix.empirical.metrics``).
4. Compute genuine explainability (SHAP global importance; LIME and DiCE on a sample
   instance when those libraries are installed) (``trix.empirical.explain``).
5. Measure per-case inference latency.

All numeric outputs are written to ``results/``. The model fit and the bootstrap CIs
are seeded, so the numeric results reproduce byte-for-byte across runs.

DATA DISCLOSURE: every record is synthetic. No real patient data and no human ratings
are used anywhere in this pipeline.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

# This file lives at <repo>/experimental/effectiveness/run_all.py, so the repository
# root is three levels up.
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sklearn.model_selection import train_test_split  # noqa: E402

from trix.constants import DEFAULT_RANDOM_SEED  # noqa: E402
from trix.empirical import (  # noqa: E402
    CENTRAL_DANGEROUS,
    DIAGNOSES,
    RuleBasedTriage,
    TRIXEnsemble,
    generate_cohort,
)
from trix.empirical import explain as xai  # noqa: E402
from trix.empirical import metrics as M  # noqa: E402

RESULTS_DIR = ROOT / "results"
SEED = DEFAULT_RANDOM_SEED  # 42
N_CASES = 5000
N_BOOT = 10000


def _write_json(name: str, payload: dict) -> None:
    (RESULTS_DIR / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_csv(name: str, header: list[str], rows: list[dict]) -> None:
    import csv

    with (RESULTS_DIR / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    print("[run_all] EXPLORATORY effectiveness study — outside manuscript scope.")
    print(f"[run_all] seed={SEED} n_cases={N_CASES}")

    # --- 1. cohort -----------------------------------------------------------
    cohort = generate_cohort(n=N_CASES, seed=SEED)
    X, y, y_central = cohort.X, cohort.y, cohort.y_central
    central_idx = [i for i, name in enumerate(DIAGNOSES) if name in CENTRAL_DANGEROUS]

    X_tr, X_te, y_tr, y_te, yc_tr, yc_te = train_test_split(
        X, y, y_central, test_size=0.3, random_state=SEED, stratify=y
    )
    print(f"[run_all] train={len(X_tr)} test={len(X_te)} central_in_test={int(yc_te.sum())}")

    # cohort distribution + feature summary
    counts = Counter(int(v) for v in y)
    dist_rows = [
        {
            "diagnosis": DIAGNOSES[i],
            "group": "central_dangerous" if DIAGNOSES[i] in CENTRAL_DANGEROUS else "benign_peripheral",
            "count": counts.get(i, 0),
            "proportion_pct": round(100.0 * counts.get(i, 0) / N_CASES, 4),
        }
        for i in range(len(DIAGNOSES))
    ]
    _write_csv("cohort_distribution.csv", ["diagnosis", "group", "count", "proportion_pct"], dist_rows)

    feat_rows = [
        {
            "feature": cohort.feature_names[j],
            "mean": round(float(X[:, j].mean()), 6),
            "std": round(float(X[:, j].std()), 6),
            "min": round(float(X[:, j].min()), 6),
            "max": round(float(X[:, j].max()), 6),
        }
        for j in range(X.shape[1])
    ]
    _write_csv("feature_summary.csv", ["feature", "mean", "std", "min", "max"], feat_rows)

    # --- 2. train models -----------------------------------------------------
    ens = TRIXEnsemble(seed=SEED).fit(X_tr, y_tr, y_central=yc_tr)
    rules = RuleBasedTriage()
    print(f"[run_all] ensemble components: {ens.info.component_names} (xgboost={ens.info.has_xgboost})")

    # --- 3. predictions on held-out test set --------------------------------
    pred_hybrid = ens.predict(X_te)
    pred_ml = ens.standalone_predict(X_te)        # standalone single ML (RF)
    pred_rules = rules.predict(X_te)              # rule-based multiclass

    # multiclass accuracy (+ CI) and macro-F1
    acc_hybrid, lo_h, hi_h = M.bootstrap_accuracy_ci(y_te, pred_hybrid, N_BOOT, SEED)
    acc_ml, lo_m, hi_m = M.bootstrap_accuracy_ci(y_te, pred_ml, N_BOOT, SEED)
    acc_rules, lo_r, hi_r = M.bootstrap_accuracy_ci(y_te, pred_rules, N_BOOT, SEED)

    f1_hybrid = M.macro_f1(y_te, pred_hybrid)
    f1_ml = M.macro_f1(y_te, pred_ml)
    f1_rules = M.macro_f1(y_te, pred_rules)

    mc_h_vs_rules = M.mcnemar_test(y_te, pred_hybrid, pred_rules)
    mc_h_vs_ml = M.mcnemar_test(y_te, pred_hybrid, pred_ml)

    diagnostic = {
        "test_n": int(len(y_te)),
        "hybrid_ensemble": {
            "accuracy": round(acc_hybrid, 6),
            "accuracy_ci95": [round(lo_h, 6), round(hi_h, 6)],
            "macro_f1": round(f1_hybrid, 6),
        },
        "standalone_ml_rf": {
            "accuracy": round(acc_ml, 6),
            "accuracy_ci95": [round(lo_m, 6), round(hi_m, 6)],
            "macro_f1": round(f1_ml, 6),
        },
        "rule_based": {
            "accuracy": round(acc_rules, 6),
            "accuracy_ci95": [round(lo_r, 6), round(hi_r, 6)],
            "macro_f1": round(f1_rules, 6),
        },
        "mcnemar_hybrid_vs_rules": mc_h_vs_rules,
        "mcnemar_hybrid_vs_ml": mc_h_vs_ml,
    }
    _write_json("diagnostic_performance.json", diagnostic)

    # --- critical scenario (binary central/dangerous) -----------------------
    bin_hybrid = ens.predict_central(X_te)                       # dedicated binary safety head
    bin_ml = ens.standalone_predict_central(X_te, central_idx)   # single-model argmax
    bin_rules = rules.predict_central(X_te)                      # rule-based

    m_hybrid = M.binary_metrics(yc_te, bin_hybrid)
    sens_lo, sens_hi = M.bootstrap_metric_ci(yc_te, bin_hybrid, "sensitivity", N_BOOT, SEED)
    npv_lo, npv_hi = M.bootstrap_metric_ci(yc_te, bin_hybrid, "npv", N_BOOT, SEED)
    m_ml = M.binary_metrics(yc_te, bin_ml)
    m_rules = M.binary_metrics(yc_te, bin_rules)

    mc_bin_h_vs_rules = M.mcnemar_test(yc_te, bin_hybrid, bin_rules)
    mc_bin_h_vs_ml = M.mcnemar_test(yc_te, bin_hybrid, bin_ml)

    critical = {
        "central_positive_n": int(yc_te.sum()),
        "benign_n": int(len(yc_te) - yc_te.sum()),
        "hybrid_ensemble": {
            **{k: (round(v, 6) if isinstance(v, float) else v) for k, v in m_hybrid.items()},
            "sensitivity_ci95": [round(sens_lo, 6), round(sens_hi, 6)],
            "npv_ci95": [round(npv_lo, 6), round(npv_hi, 6)],
        },
        "standalone_ml_rf": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in m_ml.items()},
        "rule_based": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in m_rules.items()},
        "mcnemar_hybrid_vs_rules": mc_bin_h_vs_rules,
        "mcnemar_hybrid_vs_ml": mc_bin_h_vs_ml,
    }
    _write_json("critical_scenario.json", critical)

    # --- 4. explainability ---------------------------------------------------
    bg = X_tr[: min(200, len(X_tr))]
    shap_res = xai.compute_shap(ens.rf, bg, X_te[: min(300, len(X_te))], cohort.feature_names)
    sample = X_te[0]
    lime_res = xai.compute_lime(
        ens.predict_proba, X_tr, sample, cohort.feature_names,
        [str(c) for c in ens.classes_], seed=SEED,
    )
    dice_res = xai.compute_dice(
        ens, X_tr, y_tr, sample, cohort.feature_names, list(DIAGNOSES)
    )
    explain_payload = {
        "shap": shap_res,
        "lime": {k: v for k, v in lime_res.items() if k != "local_weights"} | (
            {"local_weights": lime_res.get("local_weights", [])[:10]} if lime_res.get("available") else {}
        ),
        "dice": dice_res,
        "explainers_available": {
            "shap": shap_res.get("available", False),
            "lime": lime_res.get("available", False),
            "dice": dice_res.get("available", False),
        },
    }
    _write_json("explainability.json", explain_payload)

    # --- 5. latency ----------------------------------------------------------
    lat = []
    for i in range(min(500, len(X_te))):
        t0 = time.perf_counter()
        ens.predict(X_te[i : i + 1])
        lat.append((time.perf_counter() - t0) * 1000.0)
    lat_sorted = sorted(lat)
    latency = {
        "n_timed": len(lat),
        "mean_ms": round(statistics.fmean(lat), 4),
        "median_ms": round(statistics.median(lat), 4),
        "p95_ms": round(lat_sorted[min(len(lat) - 1, int(0.95 * len(lat)))], 4),
        "mean_s": round(statistics.fmean(lat) / 1000.0, 4),
        "note": "Single-case ensemble inference latency; hardware dependent, not byte-stable.",
    }
    _write_json("latency_summary.json", latency)

    # --- manifest ------------------------------------------------------------
    manifest = {
        "package": "trix",
        "pipeline": "trix.empirical (real synthetic-cohort ML pipeline) — EXPLORATORY, outside manuscript scope",
        "scope_note": "Supplementary effectiveness study; the JIIS manuscript reports no quantitative effectiveness.",
        "seed": SEED,
        "n_cases": N_CASES,
        "data_disclosure": "All data synthetic; no real patient data; no human ratings.",
        "models_used": ens.info.component_names,
        "gradient_model": ens.info.gradient_model,
        "xgboost_available": ens.info.has_xgboost,
        "explainers_available": explain_payload["explainers_available"],
        "deterministic_outputs": [
            "results/cohort_distribution.csv",
            "results/feature_summary.csv",
            "results/diagnostic_performance.json",
            "results/critical_scenario.json",
            "results/explainability.json",
        ],
        "non_deterministic_outputs": ["results/latency_summary.json"],
        "headline_numbers": {
            "hybrid_accuracy": diagnostic["hybrid_ensemble"]["accuracy"],
            "hybrid_accuracy_ci95": diagnostic["hybrid_ensemble"]["accuracy_ci95"],
            "rule_based_accuracy": diagnostic["rule_based"]["accuracy"],
            "standalone_ml_accuracy": diagnostic["standalone_ml_rf"]["accuracy"],
            "central_sensitivity": critical["hybrid_ensemble"]["sensitivity"],
            "central_npv": critical["hybrid_ensemble"]["npv"],
            "central_specificity": critical["hybrid_ensemble"]["specificity"],
            "central_ppv": critical["hybrid_ensemble"]["ppv"],
            "latency_s": latency["mean_s"],
        },
    }
    _write_json("manifest.json", manifest)

    print("[run_all] === EXPLORATORY RESULTS (outside manuscript scope) ===")
    print(f"  hybrid accuracy : {acc_hybrid:.4f}  CI95 [{lo_h:.4f}, {hi_h:.4f}]")
    print(f"  rule-based acc  : {acc_rules:.4f}")
    print(f"  standalone ML   : {acc_ml:.4f}")
    print(f"  McNemar hybrid vs rules p={mc_h_vs_rules['p_value']:.3e}")
    print(f"  McNemar hybrid vs ML    p={mc_h_vs_ml['p_value']:.3e}")
    print(f"  central sensitivity: {m_hybrid['sensitivity']:.4f}  NPV: {m_hybrid['npv']:.4f}")
    print(f"  central spec: {m_hybrid['specificity']:.4f}  PPV: {m_hybrid['ppv']:.4f}")
    print(f"  latency mean: {latency['mean_s']:.4f} s")
    print(f"  explainers: {explain_payload['explainers_available']}")
    print(f"[run_all] wrote results to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
