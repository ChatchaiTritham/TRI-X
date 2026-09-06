# Reproducibility

This document records exactly what the committed TRI-X code reproduces relative to
the manuscript. The manuscript (JIIS) is primarily a methodological / governance
framework and its headline contribution is decision *behaviour* (safety-gate
compliance, monotone escalation, missingness stability, trace completeness), reported
in `results/framework/`. In addition, Section "Reference-implementation validation"
of the manuscript reports a secondary reference-implementation exercise — realisability
metrics (accuracy, sensitivity/specificity, confidence intervals) on a synthetic
cohort — explicitly framed as **a check that the specification behaves as intended,
not a validated clinical-effectiveness claim**. Those numbers ARE cited in the
manuscript (Table "refimpl") and are produced by `experimental/effectiveness/run_all.py`
on a documented **synthetic** cohort with pinned dependencies (`requirements.txt`).

> Data disclosure: all data are synthetic. No real patient records and no human
> ratings are used anywhere in this repository or its results.

## How to run

```bash
python -m venv .venv
# Windows:  .\.venv\Scripts\Activate.ps1
# POSIX:    source .venv/bin/activate
pip install -e .
pip install -r requirements.txt

# PRIMARY — framework decision-behaviour artefacts the manuscript reports (seed = 42)
python scripts/run_framework.py               # writes results/framework/*.json
python -m pytest -q                            # unit + determinism tests

# SECONDARY — reference-implementation realisability check (cited in the manuscript,
# Section "Reference-implementation validation", Table "refimpl"; not an
# effectiveness claim). Requires pinned dependencies: pip install -r requirements.txt
python scripts/measure_latency.py                                # results/latency_summary_measured.json
python experimental/effectiveness/run_all.py                     # compute results/ (seed = 42)
python experimental/effectiveness/generate_manuscript_figures.py # render figures from results/
python experimental/effectiveness/run_validation.py              # convenience: run_all + figures
```

`run_framework.py` trains no model: it exercises the deterministic governance logic and
writes safety-gate compliance, the G1–G5 schema, the monotone-escalation invariant,
missingness stability, and trace completeness to `results/framework/`. The exploratory
`experimental/effectiveness/run_all.py` is deterministic too: with the fixed seed (42)
every numeric output in `results/*.json|csv` reproduces byte-for-byte. Single-case
inference latency is the only hardware-dependent, non-byte-stable output. The old
`scripts/run_all.py`, `scripts/generate_manuscript_figures.py`, and
`scripts/run_validation.py` paths still work as thin redirect stubs.

## Framework behaviour artefacts (manuscript scope)

`scripts/run_framework.py` writes, to `results/framework/`:

| Artefact | Property checked |
|---|---|
| `safety_gate_compliance.json` | Escalation compliance — central/dangerous cases the safety gate escalates; missed red flags |
| `behaviour_schema_g1g5.json` | G1–G5 routing distribution over the cohort |
| `monotone_escalation.json` | "Low-risk never escalates" + urgency cannot drop under removed fields |
| `missingness_stability.json` | Gate-decision flip rate when fields are dropped |
| `trace_completeness.json` | Every decision carries a complete, schema-valid audit trace |

## What the pipeline does

The empirical pipeline lives in `src/trix/empirical/`:

- `cohort.py` — generates a synthetic ED vestibular triage cohort (n = 5,000) from
  documented, archetype-conditioned feature distributions following the TiTrATE/HINTS
  framework. Eleven diagnoses; central/dangerous conditions enriched to ~15%.
- `rule_baseline.py` — a deterministic forward-chaining rule classifier (the rule-based
  baseline) over the HINTS/TiTrATE features.
- `ensemble.py` — the real ensemble: Random Forest + XGBoost + a multi-layer perceptron
  (soft voting), plus a dedicated cost-sensitive binary detector for central conditions.
- `explain.py` — genuine post-hoc explainability: SHAP (`shap.TreeExplainer`), LIME
  (`lime.LimeTabularExplainer`), and DiCE (`dice-ml`) computed from the fitted models.
- `metrics.py` — accuracy + bootstrap CI, binary sensitivity/specificity/PPV/NPV, and
  McNemar's test.

The original governance scaffold (`triage.py`, `governance.py`, `titrate.py`,
`pipeline.py`, `xai.py`) is retained; `xai.py` now computes genuine SHAP/LIME when a
fitted model is attached (no more normalized-input placeholders).

## Reference-implementation realisability check (secondary — cited in manuscript Table "refimpl")

> These numbers ARE cited in the manuscript, in Section "Reference-implementation
> validation" (Table "refimpl"), explicitly framed as a secondary realisability check
> that the specification behaves as intended — **not** a validated clinical-effectiveness
> claim. Re-run under pinned dependencies (see `requirements.txt`); the earlier
> unpinned run's numbers below this table are kept as a historical record only.

All values below are produced by `experimental/effectiveness/run_all.py` on the
synthetic test set (n = 1,500), under pinned dependencies, and stored in `results/`.

| Metric | Value | Source file |
|---|---|---|
| Multiclass diagnostic accuracy (hybrid) | 79.8% (95% CI 77.8–81.8) | `diagnostic_performance.json` |
| Standalone single-ML accuracy | 78.3% (95% CI 76.2–80.3) | `diagnostic_performance.json` |
| Rule-based accuracy | 34.5% (95% CI 32.2–36.9) | `diagnostic_performance.json` |
| Macro-F1 (hybrid) | 0.660 | `diagnostic_performance.json` |
| McNemar hybrid vs rules | χ²=585.6, p ≈ 2.3×10⁻¹²⁹ | `diagnostic_performance.json` |
| McNemar hybrid vs ML | χ²=4.79, p = 0.029 (significant) | `diagnostic_performance.json` |
| Central-condition sensitivity (hybrid) | 97.0% (95% CI 94.7–99.1) | `critical_scenario.json` |
| Central-condition specificity (hybrid) | 95.3% | `critical_scenario.json` |
| Central-condition NPV (hybrid) | 99.4% | `critical_scenario.json` |
| Single-case inference latency (pooled, 2500 calls) | mean 45.2 ms, p95 60.4 ms | `latency_summary_measured.json` |
| Explainers exercised | SHAP, LIME, DiCE (all `available: true`) | `explainability.json` |

**Historical note (pre-pin, unpinned `requirements.txt`, kept for audit trail only —
do NOT cite these):** accuracy 79.6%/78.2%/34.5%, McNemar hybrid-vs-ML χ²=3.60,
p=0.057 (not significant), latency ~34 ms single unwarmed measurement. Pinning
dependencies flipped the hybrid-vs-standalone-ML significance result from
not-significant to significant (p=0.057 → p=0.029); this is documented rather than
silently overwritten because it demonstrates why the pin was necessary.

## Outputs (`results/`)

| Output | File |
|---|---|
| Cohort diagnosis distribution | `cohort_distribution.csv` |
| Per-feature summary statistics | `feature_summary.csv` |
| Diagnostic performance + McNemar | `diagnostic_performance.json` |
| Critical-scenario (central vs benign) | `critical_scenario.json` |
| Explainability (SHAP/LIME/DiCE) | `explainability.json` |
| Latency | `latency_summary.json` |
| Manifest (headline numbers) | `manifest.json` |

## Honest scope notes

- The manuscript's broader architecture also describes a Bayesian belief network and a
  case-based-reasoning module. These are **not** implemented in this pipeline; the paper
  marks them as design/future work and reports no numbers for them.
- The synthetic feature distributions are clinically motivated priors, not
  epidemiologically exact frequencies. Real-world validity requires prospective
  validation on real patients; this repository establishes reproducibility, not clinical
  validity.
- There is no human-subject (physician) study; no physician ratings are reported anywhere.

## Target journal

The portfolio target is the *Journal of Intelligent Information Systems (JIIS, Springer)*.
The manuscript LaTeX source is on the Springer `sn-jnl` template (migration complete).
