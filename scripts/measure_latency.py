"""Clean, isolated single-case inference latency measurement for the TRI-X hybrid
ensemble (RandomForest + XGBoost + MLP), seed = 42.

Methodology (addresses the JIIS deep-audit A1 finding of an unsourced latency claim):
  - Runs in its own process, with no other computation (training data generation and
    model fit happen once, before any timing loop starts) and no profiler/tracer
    attached (no ``tracemalloc``, no ``cProfile``) -- avoids the timing-contamination
    class of defect found in the sibling DMKD paper.
  - A warm-up phase of 50 untimed predictions absorbs first-call JIT/cache effects
    (sklearn/XGBoost/MLP first-call overhead) before any timed sample is recorded.
  - 500 single-case predictions are timed with ``time.perf_counter()`` (matches the
    manuscript's stated n=500 evaluation set).
  - The whole warm-up + timing procedure is repeated 5 times in the same process
    (5 x 500 = 2500 timed calls total) to characterize run-to-run variance on this
    machine; mean/median/p95 are reported per repeat and pooled across all repeats.

Run: python scripts/measure_latency.py
Output: results/latency_summary_measured.json. This is a separate file from
experimental/effectiveness/run_all.py's own results/latency_summary.json (a single,
un-warmed-up 500-call measurement); that file is left alone since it is explicitly
documented as non-deterministic/hardware-dependent. This script's pooled 2500-call,
warmed-up measurement is the number cited in the manuscript.
"""

from __future__ import annotations

import json
import platform
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sklearn.model_selection import train_test_split  # noqa: E402

from trix.constants import DEFAULT_RANDOM_SEED  # noqa: E402
from trix.empirical import generate_cohort  # noqa: E402
from trix.empirical.ensemble import TRIXEnsemble  # noqa: E402

SEED = DEFAULT_RANDOM_SEED
N_CASES = 5000
N_WARMUP = 50
N_TIMED = 500
N_REPEATS = 5


def _percentile(sorted_vals, pct):
    idx = min(len(sorted_vals) - 1, int(pct * len(sorted_vals)))
    return sorted_vals[idx]


def main() -> None:
    cohort = generate_cohort(n=N_CASES, seed=SEED)
    X_tr, X_te, y_tr, _y_te, yc_tr, _yc_te = train_test_split(
        cohort.X, cohort.y, cohort.y_central, test_size=0.30, random_state=SEED, stratify=cohort.y
    )
    ens = TRIXEnsemble(seed=SEED).fit(X_tr, y_tr, y_central=yc_tr)

    n_eval = min(N_TIMED, len(X_te))

    repeats = []
    pooled_ms = []
    for r in range(N_REPEATS):
        # Untimed warm-up -- absorb first-call overhead, not part of the measurement.
        for i in range(N_WARMUP):
            ens.predict(X_te[i % len(X_te) : (i % len(X_te)) + 1])

        lat_ms = []
        for i in range(n_eval):
            t0 = time.perf_counter()
            ens.predict(X_te[i : i + 1])
            lat_ms.append((time.perf_counter() - t0) * 1000.0)

        lat_sorted = sorted(lat_ms)
        summary = {
            "repeat": r,
            "n_timed": len(lat_ms),
            "mean_ms": round(statistics.fmean(lat_ms), 4),
            "median_ms": round(statistics.median(lat_ms), 4),
            "p95_ms": round(_percentile(lat_sorted, 0.95), 4),
            "min_ms": round(lat_sorted[0], 4),
            "max_ms": round(lat_sorted[-1], 4),
        }
        repeats.append(summary)
        pooled_ms.extend(lat_ms)

    pooled_sorted = sorted(pooled_ms)
    pooled = {
        "n_timed": len(pooled_ms),
        "mean_ms": round(statistics.fmean(pooled_ms), 4),
        "median_ms": round(statistics.median(pooled_ms), 4),
        "p95_ms": round(_percentile(pooled_sorted, 0.95), 4),
        "min_ms": round(pooled_sorted[0], 4),
        "max_ms": round(pooled_sorted[-1], 4),
    }

    out = {
        "methodology": (
            f"{N_WARMUP} untimed warm-up predictions, then {n_eval} timed single-case "
            f"predictions via time.perf_counter(), repeated {N_REPEATS} times in one "
            "process; no profiler/tracer attached during timing."
        ),
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "python": platform.python_version(),
        },
        "note": (
            "Single-case ensemble inference latency is hardware- and load-dependent and "
            "not byte-stable across machines/runs; this file reports the measurement "
            "procedure and the observed range so the manuscript number is traceable."
        ),
        "per_repeat": repeats,
        "pooled": pooled,
    }

    out_path = ROOT / "results" / "latency_summary_measured.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
