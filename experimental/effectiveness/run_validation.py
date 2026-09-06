"""Convenience runner for the Table 2 reference-implementation effectiveness study.

This regenerates every effectiveness metric on the documented synthetic cohort and
then renders the accompanying figures. It is equivalent to running, in order:

    python experimental/effectiveness/run_all.py
    python experimental/effectiveness/generate_manuscript_figures.py

NOTE: these effectiveness numbers ARE reported in Table 2 of the TRI-X (JIIS)
manuscript, as an illustrative reference-implementation comparison rather than a
validated clinical-effectiveness claim. For the governance-framework artefacts the
paper's Results section body reports (safety-gate compliance, missingness stability,
trace completeness, G1-G5 schema), run instead:

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
