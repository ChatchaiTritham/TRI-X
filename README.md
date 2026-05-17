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
- Example scripts:
  - `examples/trix_visualizations.py`: visualization walkthrough
  - `examples/framework_diagrams.py`: framework illustration generation
- Notebook:
  - `notebooks/01_trix_introduction.ipynb`: introductory interactive walkthrough

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