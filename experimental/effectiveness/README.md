# Experimental — Effectiveness study (SUPPLEMENTARY, outside the manuscript's scope)

> **Read this first.** Everything in this folder is **exploratory** and is **not part of
> the TRI-X manuscript's claims.** The paper
> ([JIIS](../../README.md), *A Safety-First Explainable Framework for Decision-Centric
> Clinical Triage under Diagnostic Uncertainty*) is a **methodological / governance
> framework**. It explicitly **reports no quantitative effectiveness claims** and
> evaluates **decision behaviour** — safety-gate compliance, stability under missingness,
> and trace completeness — **not diagnostic accuracy**.

## What lives here

A small, fully reproducible machine-learning effectiveness study fitted on the
synthetic cohort. It exists because the code is real and was useful for internal
exploration, but its outputs (multiclass accuracy, sensitivity/specificity/PPV/NPV,
McNemar tests, SHAP/LIME/DiCE attributions, latency) **must not be read as
effectiveness evidence for the framework.** They are kept here, clearly fenced off,
so a reader who opens the repository sees a governance framework first and an optional
exploratory benchmark second.

| File | What it does |
|---|---|
| `run_all.py` | Trains the RF+GB/XGB+MLP ensemble on the synthetic cohort; writes accuracy / critical-scenario / explainability / latency JSON+CSV to `results/`. |
| `generate_manuscript_figures.py` | Renders the four exploratory figures from `results/` into `figures/manuscript/`. No numbers are hardcoded. |
| `run_validation.py` | Convenience wrapper: runs both of the above in order. |

The reusable library these scripts call (`src/trix/empirical/` — cohort generator,
rule baseline, ensemble, metrics, explainers) stays in the package because the
**framework** runner also reuses the deterministic cohort and rule baseline. Only the
**effectiveness entry-point scripts** were relocated here.

## How to run (only if you want the supplementary numbers)

```bash
python experimental/effectiveness/run_all.py                       # seed 42; populates results/
python experimental/effectiveness/generate_manuscript_figures.py   # render exploratory figures
python experimental/effectiveness/run_validation.py                # both of the above
```

Outputs are seeded and reproduce byte-for-byte, except per-case inference latency,
which is hardware dependent.

## For the artefacts the paper actually reports

Use the repository's **primary** entry point instead:

```bash
python scripts/run_framework.py
```

That runner exercises the framework's decision behaviour — the safety gate, the G1–G5
schema, monotone escalation, missingness stability, and audit-trace completeness —
which is what the manuscript evaluates.

## Data disclosure

Every record is synthetic, generated from guideline-derived, archetype-conditioned
feature distributions. No real patient data and no human ratings are used. Because there
are no human subjects, IRB approval did not apply.
