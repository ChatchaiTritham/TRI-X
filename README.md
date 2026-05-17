# TRI-X

## Overview

TRI-X is the integrated Triage-TiTrATE-XAI research pipeline for accountable
clinical decision support in acute dizziness and vertigo.

## Installation

```bash
pip install -e .
```

## Repository Structure

- `src/trix/`: importable package
- `tests/`: automated tests
- `scripts/`: runnable demos
- `examples/`: example usage
- `notebooks/`: research notebooks

## Tutorials And Demos

- Script demo:
  - `scripts/demo.py`: runnable end-to-end pipeline demo
  - `scripts/generate_manuscript_figures.py`: curated manuscript figure generation
- Example scripts:
  - `examples/trix_visualizations.py`: visualization walkthrough
  - `examples/framework_diagrams.py`: framework illustration generation
- Notebook:
  - `notebooks/01_trix_introduction.ipynb`: introductory interactive walkthrough

## Curated Manuscript Figures

The curated manuscript figure set is maintained for manuscripts that are still
in preparation. This status does not imply publication, acceptance, or final
journal readiness for every raw demo or exploratory image in `outputs/figures/`.

Regenerate the curated figure set:

```bash
python scripts/generate_manuscript_figures.py
```

Outputs:

- `figures/manuscript/`: selected PDF and PNG manuscript figures
- `FIGURE_MANIFEST.csv`: figure role, source script, source artifact, caption,
  and intended article section

The dense `fig3_performance_dashboard_2d` demo output is split into focused
article panels in the curated set so labels remain readable after journal
scaling.

## Cross-Repository Tutorial Charts

- `../tutorial_surface_comparison.png`: scripts vs examples vs notebooks across all repositories
- `../tutorial_asset_density.png`: interactive/tutorial asset density normalized by repository size
- `../tutorial_maturity_report.md`: combined maturity summary

## Package Scope

The package currently includes:

- triage assessment in `src/trix/triage.py`
- TiTrATE execution logic in `src/trix/titrate.py`
- governance/SRGL screening in `src/trix/governance.py`
- integrated orchestration in `src/trix/pipeline.py`
- explanation interfaces in `src/trix/xai.py`

## Source Layout

This repository uses the recommended `src/<package_name>` layout.
Importable code lives in `src/trix/`.

## Testing

```bash
pytest tests -v
```

## Manuscript Alignment

Canonical manuscript package:

- `D:\PhD-NU\Manuscript\Manuscript\HIR_TRI-X-Framework`

Use this repository as implementation and reproducibility support for the TRI-X
framework manuscript while that manuscript remains in progress. The active
manuscript package for alignment notes is the HIR framework package, not the ESA
expert-system package. This keeps the repository claim aligned with TRI-X as a
safety-first framework for decision-centric clinical triage under uncertainty.

The manuscript-level technical content maps to this repository as follows:

- topic ownership: integrated TRI-X framework
- decision logic: triage-first safety gate, TiTrATE patterning, pathway routing,
  and explanation traceability
- formulas: uncertainty and pathway-governance specifications
- pseudocode: five-group decision logic and framework-level implementation
  contracts
- figure artifacts: curated framework architecture, performance targets,
  validation gate status, and risk-tier distribution in `figures/manuscript/`

`TRI-X-CDSS` remains an implementation/integration package and should not be
counted as a standalone TRI-X article.

## Methodological References

The framework is grounded in:

- TiTrATE bedside reasoning for timing, triggers, and targeted examination
- emergency triage principles for safety-first routing
- conservative clinical decision support practice under uncertainty
- transparent audit trails and reproducible decision behavior
- scenario-based validation rather than deployed diagnostic-system claims

## Citation

The associated manuscript is still in preparation. Until its publication status
changes, cite this software repository using `CITATION.cff`.

## Contact

### Contact Author

**Chatchai Tritham** (Author)

- Email: [chatchait66@nu.ac.th](mailto:chatchait66@nu.ac.th)
- ORCID: [0000-0001-7899-228X](https://orcid.org/0000-0001-7899-228X)
- Department of Computer Science and Information Technology
- Faculty of Science, Naresuan University
- Phitsanulok 65000, Thailand

### Supervisor

**Chakkrit Snae Namahoot**

- E-mail: [chakkrits@nu.ac.th](mailto:chakkrits@nu.ac.th)
- ORCID: [0000-0003-4660-4590](https://orcid.org/0000-0003-4660-4590)
- Department of Computer Science and Information Technology
- Faculty of Science, Naresuan University
- Phitsanulok 65000, Thailand
