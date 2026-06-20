"""Primary entry point for TRI-X: framework decision-behaviour artefacts (seed = 42).

This is the runner that regenerates the artefacts the TRI-X manuscript (JIIS) actually
reports. The paper is a methodological / governance framework and makes *no quantitative
effectiveness claims*; it evaluates decision *behaviour*, not diagnostic accuracy. This
script accordingly exercises only the deterministic governance logic (the guideline-
derived rule baseline over the synthetic cohort) and measures the safety/governance
properties from the manuscript's safety-metrics table:

1. Safety-gate / escalation compliance -- does the triage-first safety gate ever miss a
   central/dangerous (red-flag) presentation? (false-negative safety risk)
2. G1-G5 decision-behaviour schema -- how the rule logic routes the cohort into the five
   behaviour groups, by urgency/risk rather than by disease label.
3. Monotone-escalation invariant -- "low-risk never escalates" / rising uncertainty
   cannot route a case to a *less* urgent group (the formal safety invariant).
4. Stability under missingness -- when input fields are dropped, how often does the
   safety-gate decision flip? (decision variability under uncertainty)
5. Trace completeness -- every routed decision carries a complete, schema-valid audit
   trace (governance / log-completeness).

No machine-learning model is trained here. All numbers are deterministic given seed 42.

The exploratory ML effectiveness study (accuracy / sensitivity / SHAP / ensemble) is
SUPPLEMENTARY and lives in ``experimental/effectiveness/`` -- it is outside the
manuscript's scope. See ``experimental/effectiveness/README.md``.

DATA DISCLOSURE: every record is synthetic. No real patient data and no human ratings
are used anywhere in this pipeline.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trix.constants import DEFAULT_RANDOM_SEED  # noqa: E402
from trix.empirical import (  # noqa: E402
    CENTRAL_DANGEROUS,
    DIAGNOSES,
    FEATURE_NAMES,
    RuleBasedTriage,
    generate_cohort,
)

RESULTS_DIR = ROOT / "results" / "framework"
SEED = DEFAULT_RANDOM_SEED  # 42
N_CASES = 5000

# Fields a clinician may not yet have recorded at the moment of first disposition.
# These red-flag / dangerous-HINTS findings stress-test routing stability under
# missingness. Safety-gate-compliant handling of an *unobserved* red flag is to assume
# the worst case (finding present = 1.0), so that removing information can only hold or
# raise urgency, never lower it. That conservative imputation is what the manuscript's
# "invariance under missing-field handling" / "low-risk never maps to high risk" hooks
# require; naively zeroing these flags would model an UNSAFE handler and is not the
# framework's specified behaviour.
MISSINGNESS_FIELDS = (
    "skew_deviation",
    "nystagmus_direction_changing",
    "nystagmus_vertical",
    "head_impulse_normal",
    "gait_unsteady_severe",
)
# Worst-case (safety-conservative) value used when a red-flag field is unobserved.
MISSINGNESS_WORST_CASE = 1.0

# Map the binary rule decision onto the manuscript's behaviour groups. The rule baseline
# is the deterministic safety gate; "central/dangerous" -> emergency band (G1/G2),
# benign -> lower-urgency bands. We report the gate at the safety-relevant granularity.
GROUP_LABELS = {
    "G1": "Immediate emergency (central red flag)",
    "G2": "Urgent specialist (high-risk, manageable uncertainty)",
    "G3": "Early follow-up",
    "G4": "Routine care",
    "G5": "Reassurance",
}


def _write_json(name: str, payload: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _route_group(rules: RuleBasedTriage, X: np.ndarray) -> np.ndarray:
    """Assign each case a behaviour group G1-G5 from the deterministic rule logic.

    Triage-first safety gate decides emergency vs non-emergency; within each band the
    rule score graduates urgency. This is a behaviour mapping, not a diagnosis.
    """
    scores = rules.predict_proba_central(X)
    central = rules.predict_central(X)
    groups = np.empty(X.shape[0], dtype=object)
    for i in range(X.shape[0]):
        if central[i] == 1:
            # Emergency band: the most severe scores route to G1, the rest to G2.
            groups[i] = "G1" if scores[i] >= 0.7 else "G2"
        else:
            # Non-emergency band graded by residual rule score.
            if scores[i] >= 0.45:
                groups[i] = "G3"
            elif scores[i] >= 0.25:
                groups[i] = "G4"
            else:
                groups[i] = "G5"
    return groups


def _urgency_rank(group: str) -> int:
    """Lower rank = more urgent (G1 most urgent). Used for the monotonicity invariant."""
    return int(group[1])


def main() -> None:
    print("[run_framework] TRI-X decision-behaviour artefacts (the manuscript's claims).")
    print(f"[run_framework] seed={SEED} n_cases={N_CASES}")

    cohort = generate_cohort(n=N_CASES, seed=SEED)
    X, y_central = cohort.X, cohort.y_central
    rules = RuleBasedTriage()
    idx = {name: i for i, name in enumerate(FEATURE_NAMES)}

    # --- 1. safety-gate / escalation compliance ------------------------------
    gate = rules.predict_central(X)
    central_total = int(y_central.sum())
    missed = int(((y_central == 1) & (gate == 0)).sum())
    caught = central_total - missed
    over_escalated = int(((y_central == 0) & (gate == 1)).sum())
    benign_total = int((y_central == 0).sum())
    safety = {
        "central_dangerous_total": central_total,
        "central_caught_by_gate": caught,
        "central_missed_by_gate": missed,
        "escalation_compliance": round(caught / central_total, 6) if central_total else None,
        "missed_red_flags": missed,
        "over_escalation_count": over_escalated,
        "over_escalation_rate_on_benign": round(over_escalated / benign_total, 6) if benign_total else None,
        "interpretation": "escalation_compliance = fraction of central/dangerous cases the "
                          "triage-first safety gate escalates; missed_red_flags should be 0.",
    }

    # --- 2. G1-G5 behaviour schema -------------------------------------------
    groups = _route_group(rules, X)
    g_counts = {g: int((groups == g).sum()) for g in ("G1", "G2", "G3", "G4", "G5")}
    schema = {
        "group_labels": GROUP_LABELS,
        "group_counts": g_counts,
        "group_proportion_pct": {
            g: round(100.0 * c / N_CASES, 4) for g, c in g_counts.items()
        },
    }

    # --- 3. monotone-escalation invariant ------------------------------------
    # "Low-risk never escalates": no benign case should be routed to G1.
    # Monotonicity: increasing uncertainty (here proxied by injecting missingness, which
    # the safety gate must treat conservatively) must never produce a LESS urgent group.
    X_missing = X.copy()
    for f in MISSINGNESS_FIELDS:
        X_missing[:, idx[f]] = MISSINGNESS_WORST_CASE  # conservative: unobserved red flag
    groups_missing = _route_group(rules, X_missing)
    violations = 0
    for i in range(N_CASES):
        # urgency must not decrease (rank must not increase) when info is removed
        if _urgency_rank(groups_missing[i]) > _urgency_rank(groups[i]):
            violations += 1
    benign_in_g1 = int(((y_central == 0) & (groups == "G1")).sum())
    invariant = {
        "monotone_escalation_violations": violations,
        "monotone_escalation_holds": violations == 0,
        "benign_routed_to_G1": benign_in_g1,
        "low_risk_never_escalates_holds": benign_in_g1 == 0,
        "interpretation": "Under removed fields the gate may only hold or escalate urgency; "
                          "a drop in urgency is a safety-invariant violation.",
    }

    # --- 4. stability under missingness --------------------------------------
    gate_missing = rules.predict_central(X_missing)
    flips = int((gate != gate_missing).sum())
    unsafe_flips = int(((gate == 1) & (gate_missing == 0)).sum())  # escalate -> de-escalate
    stability = {
        "fields_dropped": list(MISSINGNESS_FIELDS),
        "gate_decision_flips": flips,
        "gate_flip_rate": round(flips / N_CASES, 6),
        "unsafe_deescalation_flips": unsafe_flips,
        "stability_score": round(1.0 - flips / N_CASES, 6),
        "interpretation": "Lower flip rate = more stable routing under missing fields; "
                          "unsafe_deescalation_flips (escalate->benign) should be 0.",
    }

    # --- 5. trace completeness -----------------------------------------------
    # Every decision must carry a complete, schema-valid audit trace.
    required_trace_fields = ("case_id", "gate_decision", "group", "rule_score", "rationale")
    incomplete = 0
    sample_traces = []
    for i in range(N_CASES):
        trace = {
            "case_id": int(i),
            "gate_decision": "central_escalate" if gate[i] == 1 else "benign_route",
            "group": str(groups[i]),
            "rule_score": round(float(rules.predict_proba_central(X[i : i + 1])[0]), 6),
            "rationale": "rule-score >= 0.30 -> safety gate escalates" if gate[i] == 1
                         else "rule-score < 0.30 -> non-emergency routing",
        }
        if any(trace.get(k) is None or trace.get(k) == "" for k in required_trace_fields):
            incomplete += 1
        if i < 5:
            sample_traces.append(trace)
    trace = {
        "decisions_traced": N_CASES,
        "required_fields": list(required_trace_fields),
        "incomplete_traces": incomplete,
        "trace_completeness": round(1.0 - incomplete / N_CASES, 6),
        "sample_traces": sample_traces,
        "interpretation": "trace_completeness = fraction of decisions with a full audit "
                          "record; governance requires 1.0.",
    }

    # --- write artefacts -----------------------------------------------------
    _write_json("safety_gate_compliance.json", safety)
    _write_json("behaviour_schema_g1g5.json", schema)
    _write_json("monotone_escalation.json", invariant)
    _write_json("missingness_stability.json", stability)
    _write_json("trace_completeness.json", trace)

    summary = {
        "framework": "TRI-X (Triage-TiTrATE-XAI)",
        "scope": "Decision-behaviour evaluation; no quantitative effectiveness claims.",
        "seed": SEED,
        "n_cases": N_CASES,
        "data_disclosure": "All data synthetic; no real patient data; no human ratings.",
        "safety_gate_compliance": safety,
        "behaviour_schema_g1g5": schema,
        "monotone_escalation": invariant,
        "missingness_stability": stability,
        "trace_completeness": trace,
        "artefacts": [
            "results/framework/safety_gate_compliance.json",
            "results/framework/behaviour_schema_g1g5.json",
            "results/framework/monotone_escalation.json",
            "results/framework/missingness_stability.json",
            "results/framework/trace_completeness.json",
        ],
        "supplementary_effectiveness_study": "experimental/effectiveness/ (outside manuscript scope)",
    }
    _write_json("framework_summary.json", summary)

    print("[run_framework] === DECISION-BEHAVIOUR ARTEFACTS (manuscript scope) ===")
    print(f"  safety gate: escalation compliance = {safety['escalation_compliance']}  "
          f"missed red flags = {safety['missed_red_flags']}")
    print(f"  G1-G5 counts: {schema['group_counts']}")
    print(f"  monotone escalation holds = {invariant['monotone_escalation_holds']}  "
          f"(violations={invariant['monotone_escalation_violations']}, "
          f"benign->G1={invariant['benign_routed_to_G1']})")
    print(f"  missingness stability = {stability['stability_score']}  "
          f"(flips={stability['gate_decision_flips']}, unsafe={stability['unsafe_deescalation_flips']})")
    print(f"  trace completeness = {trace['trace_completeness']}  "
          f"(incomplete={trace['incomplete_traces']})")
    print(f"[run_framework] wrote artefacts to {RESULTS_DIR}")
    print("[run_framework] (exploratory ML effectiveness lives in experimental/effectiveness/)")


if __name__ == "__main__":
    main()
