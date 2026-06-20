"""MOVED — the effectiveness validation runner now lives in experimental/effectiveness/.

This stub forwards to the relocated script so old commands keep working. It runs the
SUPPLEMENTARY effectiveness study (outside the TRI-X manuscript's scope).

  python experimental/effectiveness/run_validation.py

For the framework artefacts the manuscript reports, run instead:
  python scripts/run_framework.py
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = Path(__file__).resolve().parents[1] / "experimental" / "effectiveness" / "run_validation.py"


def main() -> None:
    print("[run_validation] NOTE: relocated to experimental/effectiveness/run_validation.py "
          "(exploratory; outside manuscript scope).")
    print("[run_validation] Framework artefacts: python scripts/run_framework.py")
    sys.argv = [str(_TARGET)]
    runpy.run_path(str(_TARGET), run_name="__main__")


if __name__ == "__main__":
    main()
