# Reproducibility

This document records exactly what the committed TRI-X code reproduces relative to
the manuscript. The manuscript (JIIS) is a methodological / governance framework and
reports **no quantitative effectiveness claims**; it evaluates decision *behaviour*.
The repository's **primary** runner reproduces those behaviour artefacts. A separate,
**supplementary** ML effectiveness pipeline (outside the manuscript's scope) lives in
`experimental/effectiveness/`; its numbers are computed by committed code on a
documented **synthetic** cohort and reproduce byte-for-byte, but they are exploratory
and must not be read as effectiveness evidence.

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

# SUPPLEMENTARY — exploratory ML effectiveness study (outside manuscript scope)
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

## Manuscript headline claims vs. repository code (real, reproduced)

All values below are produced by `scripts/run_all.py` on the synthetic test set
(n = 1,500) and stored in `results/`.

| Metric | Value | Source file |
|---|---|---|
| Multiclass diagnostic accuracy (hybrid) | 79.6% (95% CI 77.5–81.6) | `diagnostic_performance.json` |
| Standalone single-ML accuracy | 78.2% | `diagnostic_performance.json` |
| Rule-based accuracy | 34.5% | `diagnostic_performance.json` |
| Macro-F1 (hybrid) | 0.658 | `diagnostic_performance.json` |
| McNemar hybrid vs rules | χ²=578.2, p < 1e-100 | `diagnostic_performance.json` |
| McNemar hybrid vs ML | χ²=3.60, p = 0.057 (n.s.) | `diagnostic_performance.json` |
| Central-condition sensitivity | 96.6% (95% CI 94.2–98.7) | `critical_scenario.json` |
| Central-condition NPV | 99.3% (95% CI 98.9–99.8) | `critical_scenario.json` |
| Central-condition specificity / PPV | 96.6% / 84.2% | `critical_scenario.json` |
| McNemar (central) hybrid vs rules / ML | p < 1e-100 / p = 0.0021 | `critical_scenario.json` |
| Single-case inference latency | ~34 ms (hardware dependent) | `latency_summary.json` |
| Explainers exercised | SHAP, LIME, DiCE (all `available: true`) | `explainability.json` |

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
The manuscript LaTeX source still uses the Elsevier `elsarticle` class; converting to the
Springer `sn-jnl` template is a separate, human-reviewed step.
