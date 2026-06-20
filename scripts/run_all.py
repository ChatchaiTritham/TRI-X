"""MOVED — the effectiveness study now lives in experimental/effectiveness/.

This stub is kept only so existing commands (`python scripts/run_all.py`) still work.
The exploratory ML effectiveness pipeline (multiclass accuracy, sensitivity/specificity,
SHAP/ensemble) is SUPPLEMENTARY and *outside the TRI-X manuscript's scope* — the paper
reports no quantitative effectiveness. It was relocated to make the repository's centre
of gravity the governance framework.

- Framework behaviour the paper DOES report:  python scripts/run_framework.py
- Exploratory effectiveness study:            python experimental/effectiveness/run_all.py

See experimental/effectiveness/README.md for the scope boundary.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = Path(__file__).resolve().parents[1] / "experimental" / "effectiveness" / "run_all.py"


def main() -> None:
    print("[run_all] NOTE: relocated to experimental/effectiveness/run_all.py "
          "(exploratory; outside manuscript scope).")
    print("[run_all] For the manuscript's framework artefacts run: python scripts/run_framework.py")
    sys.argv = [str(_TARGET)]
    runpy.run_path(str(_TARGET), run_name="__main__")


if __name__ == "__main__":
    main()
