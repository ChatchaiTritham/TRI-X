"""Validation entry point for TRI-X (alias of the full empirical pipeline).

This regenerates every reported metric on the documented synthetic cohort and then
renders the curated figures. It is equivalent to running, in order:

    python scripts/run_all.py
    python scripts/generate_manuscript_figures.py

All data are synthetic; no real patient data and no human ratings are used.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    print("[run_validation] computing metrics ...")
    runpy.run_path(str(ROOT / "scripts" / "run_all.py"), run_name="__main__")
    print("[run_validation] rendering figures ...")
    sys.argv = [str(ROOT / "scripts" / "generate_manuscript_figures.py")]
    runpy.run_path(str(ROOT / "scripts" / "generate_manuscript_figures.py"), run_name="__main__")
    print("[run_validation] done.")


if __name__ == "__main__":
    main()
