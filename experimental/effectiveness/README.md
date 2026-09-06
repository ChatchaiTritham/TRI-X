# Experimental — Effectiveness study (Table 2 reference implementation)

> **Read this first.** The TRI-X manuscript
> ([JIIS](../../README.md), *A Safety-First Explainable Framework for Decision-Centric
> Clinical Triage under Diagnostic Uncertainty*) is primarily a **methodological / governance
> framework**, evaluating **decision behaviour** — safety-gate compliance, stability under
> missingness, and trace completeness — **not diagnostic accuracy**. However, the manuscript's
> Table 2 *does* report headline numbers from this folder's pipeline (accuracy, sensitivity,
> specificity, PPV/NPV, McNemar), presented explicitly as an **illustrative
> reference-implementation comparison, not a validated clinical-effectiveness claim** — see
> the manuscript text itself for that hedge.

## What lives here

A small, fully reproducible machine-learning effectiveness study fitted on the
synthetic cohort. Its outputs (multiclass accuracy, sensitivity/specificity/PPV/NPV,
McNemar tests, SHAP/LIME/DiCE attributions, latency) are the numeric source for the
manuscript's Table 2 and should be read with the same caveat as the manuscript itself:
**illustrative reference-implementation numbers, not validated clinical-effectiveness
evidence.** They are kept in this separate folder so a reader who opens the repository
sees the governance framework first and this reference-implementation comparison second.

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
