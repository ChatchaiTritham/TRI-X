"""MOVED — the effectiveness study now lives in experimental/effectiveness/.

This stub is kept only so existing commands (`python scripts/run_all.py`) still work.
The reference-implementation effectiveness pipeline (multiclass accuracy,
sensitivity/specificity, SHAP/ensemble) was relocated to make the repository's
centre of gravity the governance framework, but its headline numbers ARE the
ones reported in Table 2 of the JIIS manuscript, as an illustrative
reference-implementation comparison rather than a validated clinical-effectiveness
claim (see results/manifest.json's scope_note).

- Governance-framework behaviour (Results section body): python scripts/run_framework.py
- Table 2 reference-implementation comparison:           python experimental/effectiveness/run_all.py

See experimental/effectiveness/README.md for the scope boundary.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = Path(__file__).resolve().parents[1] / "experimental" / "effectiveness" / "run_all.py"


def main() -> None:
    print("[run_all] NOTE: relocated to experimental/effectiveness/run_all.py "
          "(Table 2 reference-implementation comparison).")
    print("[run_all] For the manuscript's governance-framework artefacts run: python scripts/run_framework.py")
    sys.argv = [str(_TARGET)]
    runpy.run_path(str(_TARGET), run_name="__main__")


if __name__ == "__main__":
    main()
