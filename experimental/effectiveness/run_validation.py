"""Convenience runner for the EXPLORATORY effectiveness study (outside manuscript scope).

This regenerates every supplementary ML metric on the documented synthetic cohort and
then renders the exploratory figures. It is equivalent to running, in order:

    python experimental/effectiveness/run_all.py
    python experimental/effectiveness/generate_manuscript_figures.py

NOTE: these effectiveness numbers are NOT part of the TRI-X (JIIS) manuscript, which
reports no quantitative effectiveness. For the artefacts the paper reports (safety-gate
compliance, missingness stability, trace completeness, G1-G5 schema), run instead:

    python scripts/run_framework.py

All data are synthetic; no real patient data and no human ratings are used.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    print("[run_validation] computing exploratory effectiveness metrics ...")
    runpy.run_path(str(HERE / "run_all.py"), run_name="__main__")
    print("[run_validation] rendering exploratory figures ...")
    sys.argv = [str(HERE / "generate_manuscript_figures.py")]
    runpy.run_path(str(HERE / "generate_manuscript_figures.py"), run_name="__main__")
    print("[run_validation] done.")


if __name__ == "__main__":
    main()
