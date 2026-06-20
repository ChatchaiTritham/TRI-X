"""MOVED — exploratory effectiveness figures now live in experimental/effectiveness/.

This stub forwards to the relocated script so old commands keep working. These
accuracy/sensitivity/SHAP figures are SUPPLEMENTARY and outside the TRI-X manuscript's
scope (the paper reports no quantitative effectiveness).

  python experimental/effectiveness/generate_manuscript_figures.py
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = (
    Path(__file__).resolve().parents[1]
    / "experimental" / "effectiveness" / "generate_manuscript_figures.py"
)


def main() -> None:
    print("[generate_manuscript_figures] NOTE: relocated to "
          "experimental/effectiveness/ (exploratory; outside manuscript scope).")
    sys.argv = [str(_TARGET), *sys.argv[1:]]
    runpy.run_path(str(_TARGET), run_name="__main__")


if __name__ == "__main__":
    main()
