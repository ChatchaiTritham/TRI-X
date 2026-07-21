# TRI-X: Decision Governance for Clinical Triage under Uncertainty (TRI-X)

> Code and synthetic-data artefacts that let a reader replay how the TRI-X framework structures, constrains, and audits a triage decision when a definitive diagnosis is not yet available.

![License](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Reproducible](https://img.shields.io/badge/reproducible-seed--42-success)

## Overview

Dizziness and vertigo are hard to triage because the uncertainty sits in the presentation itself, not only in the data record. The same complaint can trace back to a harmless inner-ear problem or to a posterior-circulation stroke, and the first disposition usually has to be chosen before any confirmatory test comes back. TRI-X (Triage–TiTrATE–Explainable AI) responds to that situation by asking how a decision should be governed rather than which label to assign. It places an emergency safety gate first, organises bedside reasoning along the TiTrATE pattern (Timing, Triggers, Targeted Examination), and keeps an auditable rationale attached to every routing choice.

The paper this repository supports is methodological. Its claims are about decision behaviour — does the safety gate ever miss a red flag, does routing stay stable when fields go missing, does each decision leave a complete trace — and it makes no claim of diagnostic or clinical effectiveness. This repository mirrors that stance: the parts that matter for the paper are the formalised guideline logic, the five-group (G1–G5) routing schema, the synthetic-cohort generators, and the deterministic replay that lets the safety properties be checked before any real patient record is involved.

A second, exploratory layer also lives here, fenced off under `experimental/effectiveness/`. It fits a small machine-learning ensemble on the synthetic cohort and prints accuracy, sensitivity, and explainability numbers. Those numbers are not part of the manuscript and should not be read as effectiveness evidence — they are kept as supplementary tooling, and the caveat is spelled out below so the boundary stays clear.

## Concept & Methodology

The canonical concept and methodology specification — the three-layer Triage–TiTrATE–XAI design, the uncertainty-as-decision-control-signal principle, the synthetic-data-first stance, the five-group (G1–G5) decision-behaviour schema, and the §5 governance checklist that **both this repository and the manuscript must conform to** — is in [docs/CONCEPT_METHODOLOGY.md](docs/CONCEPT_METHODOLOGY.md). Treat that document as the source of truth; reconcile any drift in prose, claims, figures, or code against it.

## Key results (framework behaviour — what the paper reports)

These are the decision-behaviour artefacts the framework runner regenerates; they are properties of the specification and the synthetic cohort, not performance claims. Run `python scripts/run_framework.py` to write them to `results/framework/`.

- A deterministic mapping from published guidelines (GRACE-3, HINTS/HINTS-Plus, AAO-HNS BPPV, APTA, ESI) into structured decision rules and escalation thresholds that replay identically across runs.
- The five-group routing schema (G1 immediate emergency through G5 reassurance), expressed so that safety-gate compliance and routing stability can be tested without a definitive diagnosis label (`results/framework/behaviour_schema_g1g5.json`).
- Safety-gate / escalation compliance: whether the triage-first gate ever misses a central/dangerous (red-flag) presentation (`results/framework/safety_gate_compliance.json`).
- Monotone-escalation behaviour: rising uncertainty cannot route a case to a less urgent group, and low-risk presentations never escalate — the formal invariant the safety checks exercise (`results/framework/monotone_escalation.json`).
- Stability under missingness: the rate at which the safety-gate decision flips when input fields are dropped (`results/framework/missingness_stability.json`).
- Trace completeness: every routed decision carries a complete, schema-valid audit trace (`results/framework/trace_completeness.json`).
- A synthetic ED vestibular cohort generated under seed 42, with central/dangerous presentations enriched to roughly 15%, used purely for stress-testing the decision logic.

### Supplementary (exploratory ML — outside manuscript scope)

The exploratory ML layer under `experimental/effectiveness/` computes accuracy/sensitivity/SHAP outputs (e.g. multiclass accuracy near 79.6%, central-condition sensitivity near 96.6% on the held-out synthetic split) via `experimental/effectiveness/run_all.py`. These are **outside the manuscript's scope**, which reports no quantitative effectiveness. Treat them as exploratory only; see `experimental/effectiveness/README.md`.

## Repository structure

```text
scripts/run_framework.py   PRIMARY entry point — framework decision-behaviour artefacts
src/trix/                  framework logic: triage, titrate, governance, pipeline, xai
src/trix/empirical/        reusable library: synthetic cohort, rule baseline, ensemble,
                           metrics, explainers (shared by framework + effectiveness layers)
experimental/effectiveness/  SUPPLEMENTARY exploratory ML study (run_all, figures,
                           run_validation) — outside manuscript scope; see its README
scripts/                   thin redirect stubs for the relocated effectiveness scripts
examples/                  structural framework diagrams (drawn, not fitted)
results/framework/         framework behaviour artefacts (JSON), written by run_framework
results/                   exploratory ML outputs (JSON/CSV), written by the effectiveness run
figures/, outputs/         rendered figure artefacts
tests/                     unit + determinism checks
```

## Installation

```bash
git clone https://github.com/ChatchaiTritham/TRI-X.git
cd TRI-X
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
pip install -r requirements.txt
```

## Reproducing the results

Framework behaviour (what the manuscript reports):

```bash
python scripts/run_framework.py                 # PRIMARY; seed 42; writes results/framework/
python scripts/demo.py                          # walk one case through the TRI-X pipeline
python -m pytest -q                             # unit + determinism tests
```

`run_framework.py` exercises only the deterministic governance logic — no ML model is trained — and writes the safety-gate compliance, G1–G5 schema, monotone-escalation invariant, missingness-stability, and trace-completeness artefacts to `results/framework/`. All values are deterministic given seed 42.

Supplementary effectiveness study (exploratory; outside manuscript scope):

```bash
python experimental/effectiveness/run_all.py                     # seed 42; populates results/
python experimental/effectiveness/generate_manuscript_figures.py # render exploratory figures
python experimental/effectiveness/run_validation.py              # convenience: both of the above
```

The old paths `python scripts/run_all.py`, `scripts/generate_manuscript_figures.py`, and `scripts/run_validation.py` still work — they are thin stubs that forward to `experimental/effectiveness/`. Scientific outputs are deterministic: with seed 42 the cohort, the rule logic, the fitted ensemble, and the bootstrap intervals reproduce the same numeric values in `results/*.json` and `results/*.csv` on every run. The single exception is per-case inference latency in `results/latency_summary.json`, which depends on the host machine and is labelled as not byte-stable. Note that `results/` ships empty (only a placeholder) — the JSON/CSV files appear once the relevant runner has been executed.

## Results and figures

The repository carries two figure families. The first is structural — hand-drawn schematics of the framework, with no numbers in them. The second is rendered from computed `results/` and belongs to the exploratory ML layer in `experimental/effectiveness/`; read those with the effectiveness caveat above.

Structural diagrams (`examples/`, output to `outputs/figures/`):

- `outputs/figures/fig1_srgl_flow_diagram.png` — the three-gate screening path (red-flag check, then risk factors, then uncertainty), showing how a case falls through to a routing band. No quantitative content; it is a logic diagram.
- `outputs/figures/fig2_framework_architecture.png` — the Triage / TiTrATE / XAI layers stacked over the governance logic, ending in a routed decision with rationale. Structural only.

For tier/diagnosis counts in the cohort, use the computed figure `figures/manuscript/fig4_cohort_distribution.png` (from `results/cohort_distribution.csv`, n=5,000) listed below; the earlier `fig5_risk_tier_distribution` artefact — which read a `results/risk_tier_distribution.csv` the pipeline no longer writes and carried a stale "n=500" framing — has been removed.

Computed ML figures (exploratory; `experimental/effectiveness/generate_manuscript_figures.py`, output to `figures/manuscript/`):

- `figures/manuscript/fig1_diagnostic_accuracy.png` — multiclass accuracy with bootstrap 95% CIs, read from `results/diagnostic_performance.json`. Numbers are computed, not hardcoded, but the quantity itself sits outside the manuscript's claims.
- `figures/manuscript/fig2_critical_scenario.png` — sensitivity/specificity/PPV/NPV for central-vs-benign detection, from `results/critical_scenario.json`. Computed; supplementary.
- `figures/manuscript/fig3_shap_importance.png` — top-10 SHAP feature importances from the fitted forest, from `results/explainability.json`. Computed; supplementary.
- `figures/manuscript/fig4_cohort_distribution.png` — diagnosis counts in the synthetic cohort, from `results/cohort_distribution.csv`. Computed; descriptive.

Hardcode audit. The exploratory figure script (`experimental/effectiveness/generate_manuscript_figures.py`) reads every value from `results/` — no literals. The same holds for `examples/trix_visualizations.py`, which now renders only the two structural diagrams (fig1, fig2) and keeps guarded skip-stubs for the panels that have no computed source (performance dashboard, 3D performance grid, XAI-method comparison, decision-time analysis). The earlier `_disabled_*` functions — which hardcoded figures such as 98% critical-alert detection, a fixed SHAP table, an age×risk accuracy grid, and randomly synthesised latencies — have been deleted, since their literals did not correspond to anything the pipeline computes.

## Data

Every record is synthetic, generated from guideline-derived, archetype-conditioned feature distributions (see `src/trix/empirical/cohort.py`). No real patient data and no human ratings are used anywhere. Because there are no human subjects, institutional review board approval did not apply. The synthetic distributions encode clinically motivated priors, not exact epidemiological frequencies, so they support reproducible stress-testing but not external validity.

## Citation

```bibtex
@article{tritham_trix,
  title   = {TRI-X: A Safety-First Explainable Framework for Decision-Centric
             Clinical Triage under Diagnostic Uncertainty},
  author  = {Tritham, Chatchai and Snae Namahoot, Chakkrit},
  journal = {Journal of Intelligent Information Systems},
  note    = {to appear},
  year    = {2026}
}
```

## License

Released under the MIT License (see `LICENSE`).

## Contact

**Chatchai Tritham** — Department of Computer Science and Information Technology, Faculty of Science, Naresuan University, Phitsanulok 65000, Thailand. Email: chatchait66@nu.ac.th · ORCID: 0000-0001-7899-228X
**Chakkrit Snae Namahoot** — same affiliation. Email: chakkrits@nu.ac.th · ORCID: 0000-0003-4660-4590

## Portfolio relationship

| Repository | Role |
|---|---|
| BASICS-CDSS | Beyond-accuracy evaluation methodology |
| TRI-X | Framework-level package |
| ORASR | Routing and safety-action component |
| DRAS-5 | Dynamic risk-state component |
| SAFE-Gate | Safety-gated ensemble framework |
| SynDX | Synthetic validation and explainability evidence |
| SURgul | SRGL/governance reproducibility component |
| Selective-CDSS | Risk-controlled selective-prediction (abstention) component |
| Causal-CDSS | Causal-inference evaluation component |
| Beyond-Accuracy | Simulation-based safety/calibration evaluation framework |
