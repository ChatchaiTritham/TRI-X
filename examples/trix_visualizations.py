#!/usr/bin/env python3
"""TRI-X Framework figures (manuscript scope -- JIIS).

Two kinds of figure, all routed through the shared ``pubviz`` toolkit:

Schematic (no quantitative claims; box/arrow layout coordinates only):
  - fig1_srgl_flow_diagram        SRGL three-gate logic flow
  - fig2_framework_architecture   Triage-TiTrATE-XAI architecture

Data-driven decision-behaviour charts (the JIIS paper's core safety/governance
metrics, read from ``results/framework/`` -- never hardcoded):
  - fig3_safety_gate_compliance   escalation compliance / missed red flags
  - fig4_missingness_stability    routing stability when input fields drop

The exploratory ML effectiveness panels (accuracy/sensitivity/SHAP) are
SUPPLEMENTARY and live in ``experimental/effectiveness/`` -- outside this
manuscript's scope. Run ``python scripts/run_framework.py`` first to populate
``results/framework/``.

Author: Chatchai Tritham
Date: 2026-01-28
"""

import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Vendor the shared toolkit next to this script so the import works from any cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pubviz import (  # noqa: E402
    apply_pub_style,
    save_fig,
    PALETTE,
    add_box,
    arrow,
    load_results,
)

warnings.filterwarnings('ignore')

# Semantic role -> Okabe-Ito palette colour (consistent across every figure/repo).
COLORS = {
    'primary': PALETTE[0],    # Blue
    'secondary': PALETTE[4],  # Orange/amber
    'success': PALETTE[2],    # Green
    'danger': PALETTE[1],     # Vermillion
    'warning': PALETTE[4],    # Amber
    'info': PALETTE[5],       # Sky blue
    'critical': PALETTE[1],   # Vermillion
    'neutral': "#666666",     # Gray
    'gate1': PALETTE[1],      # Vermillion (Critical)
    'gate2': PALETTE[4],      # Amber (Risk)
    'gate3': PALETTE[0],      # Blue (Uncertainty)
}


def create_srgl_flow_diagram(output_dir='outputs/figures'):
    """Figure 1: SRGL three-gate sequential screening logic.

    Structural diagram only: box/arrow layout coordinates, no numbers.
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')

    ax.text(5, 11.5, 'Screening-First Risk Governance Logic (SRGL)',
            ha='center', va='top', fontsize=16, fontweight='bold')

    # Input
    add_box(ax, (3.5, 10), 3, 0.8,
            'Patient Input\n(Demographics, Symptoms, Vitals)',
            facecolor='#E8E8E8', edgecolor='black', size=10)
    arrow(ax, (5, 10), (5, 9.0), color='black', lw=2)

    # Gate G1: Critical Red Flags
    add_box(ax, (2, 7.5), 6, 1.5,
            'Gate G1: Critical Red Flag Screening\n\n'
            'Focal weakness | Thunderclap headache | Acute hearing loss\n'
            'Diplopia | Dysarthria | Severe ataxia',
            facecolor='#FFE5E5', edgecolor=COLORS['gate1'], size=10)
    add_box(ax, (4.2, 6.8), 1.6, 0.5, 'Red Flag\nDetected?',
            facecolor='#FFF9E5', edgecolor='black', size=9)

    # YES -> R1/R2
    arrow(ax, (6, 7.05), (7.5, 7.05), color=COLORS['danger'], lw=2)
    ax.text(6.7, 7.35, 'YES', fontsize=9, fontweight='bold', color=COLORS['danger'])
    add_box(ax, (7.5, 6.5), 1.8, 1,
            'R1/R2\nCritical/High Risk\nImmediate Care',
            facecolor='#FFE5E5', edgecolor=COLORS['danger'], size=9)

    # NO -> Gate G2
    arrow(ax, (5, 6.8), (5, 6.0), color='black', lw=2)
    ax.text(5.3, 6.4, 'NO', fontsize=9, fontweight='bold')

    # Gate G2: Risk Factor Assessment
    add_box(ax, (2, 4.5), 6, 1.3,
            'Gate G2: Risk Factor Assessment\n\n'
            'Age >65 | Hypertension | Diabetes | CVD | Atrial fibrillation\n'
            'Previous stroke/TIA | Vascular risk factors',
            facecolor='#FFF4E5', edgecolor=COLORS['gate2'], size=10)
    add_box(ax, (4.2, 3.8), 1.6, 0.5, 'High Risk\nFactors?',
            facecolor='#FFF9E5', edgecolor='black', size=9)

    # YES -> R2/R3
    arrow(ax, (6, 4.05), (7.5, 4.05), color=COLORS['warning'], lw=2)
    ax.text(6.7, 4.35, 'YES', fontsize=9, fontweight='bold', color=COLORS['warning'])
    add_box(ax, (7.5, 3.5), 1.8, 1,
            'R2/R3\nHigh/Moderate Risk\nUrgent Evaluation',
            facecolor='#FFF9E5', edgecolor=COLORS['warning'], size=9)

    # NO -> Gate G3
    arrow(ax, (5, 3.8), (5, 3.0), color='black', lw=2)
    ax.text(5.3, 3.4, 'NO', fontsize=9, fontweight='bold')

    # Gate G3: Uncertainty Quantification
    add_box(ax, (2, 1.5), 6, 1.3,
            'Gate G3: Uncertainty Quantification\n\n'
            'Symptom clarity | Diagnosis confidence | Temporal pattern consistency\n'
            'Vital sign stability | Comorbidity complexity',
            facecolor='#E5F2FF', edgecolor=COLORS['gate3'], size=10)
    add_box(ax, (4.2, 0.8), 1.6, 0.5, 'High\nUncertainty?',
            facecolor='#FFF9E5', edgecolor='black', size=9)

    # YES -> R3
    arrow(ax, (6, 1.05), (7.5, 1.05), color=COLORS['info'], lw=2)
    ax.text(6.7, 1.35, 'YES', fontsize=9, fontweight='bold', color=COLORS['info'])
    add_box(ax, (7.5, 0.5), 1.8, 1, 'R3\nModerate Risk\nObservation',
            facecolor='#E5F2FF', edgecolor=COLORS['info'], size=9)

    # NO -> R4/R5
    arrow(ax, (4.2, 1.05), (2.5, 1.05), color=COLORS['success'], lw=2)
    ax.text(3.3, 1.35, 'NO', fontsize=9, fontweight='bold', color=COLORS['success'])
    add_box(ax, (0.7, 0.5), 1.8, 1, 'R4/R5\nLow/Minimal Risk\nOutpatient Care',
            facecolor='#E5F9F0', edgecolor=COLORS['success'], size=9)

    legend_elements = [
        mpatches.Patch(facecolor='#FFE5E5', edgecolor=COLORS['gate1'],
                       label='Gate G1: Critical Screening', linewidth=2),
        mpatches.Patch(facecolor='#FFF4E5', edgecolor=COLORS['gate2'],
                       label='Gate G2: Risk Assessment', linewidth=2),
        mpatches.Patch(facecolor='#E5F2FF', edgecolor=COLORS['gate3'],
                       label='Gate G3: Uncertainty Check', linewidth=2),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=9,
              frameon=True, shadow=True)

    save_fig(fig, 'fig1_srgl_flow_diagram', output_dir)
    plt.close(fig)


def create_framework_architecture(output_dir='outputs/figures'):
    """Figure 2: TRI-X framework architecture.

    Structural diagram only: box/arrow layout coordinates, no numbers.
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')

    ax.text(7, 10.8, 'TRI-X Framework Architecture',
            ha='center', va='top', fontsize=18, fontweight='bold')

    # Patient input (top)
    add_box(ax, (4.5, 9.8), 5, 0.8,
            'PATIENT INPUT: Demographics, Symptoms, Vitals, Medical History',
            facecolor='#E8E8E8', edgecolor='black', size=11)

    # Three main components
    add_box(ax, (0.5, 6.5), 3.5, 2.5,
            'TRIAGE\nClinical Guidelines\n\n'
            '- ACEP Dizziness/Vertigo\n- AHA/ASA Stroke\n- AAO-HNS BPPV\n- Red Flag Detection',
            facecolor='#FFE5E5', edgecolor=COLORS['danger'], size=9)
    add_box(ax, (5.25, 6.5), 3.5, 2.5,
            'TiTrATE\nDiagnostic Framework\n\n'
            '- Symptom Patterns\n- Risk Factor Scoring\n- Temporal Analysis\n- Comorbidity Assessment',
            facecolor='#FFF4E5', edgecolor=COLORS['gate2'], size=9)
    add_box(ax, (10, 6.5), 3.5, 2.5,
            'XAI\nExplainability Layer\n\n'
            '- SHAP Values\n- LIME\n- NMF Phenotypes\n- Counterfactuals\n- Rule Extraction',
            facecolor='#E5F2FF', edgecolor=COLORS['gate3'], size=9)

    # Input -> components
    for x_pos in [2.25, 7, 11.75]:
        arrow(ax, (7, 9.8), (x_pos, 9.0), color='black', lw=2)
    # Component chaining
    arrow(ax, (4, 7.75), (5.25, 7.75), color='black', lw=2.5)
    arrow(ax, (8.75, 7.75), (10, 7.75), color='black', lw=2.5)

    # SRGL layer
    add_box(ax, (1, 4.5), 12, 1.5,
            'SRGL (Screening-First Risk Governance Logic)\n\n'
            'Gate G1: Critical Red Flags  ->  Gate G2: Risk Factors  ->  '
            'Gate G3: Uncertainty Quantification',
            facecolor='#E5F9F0', edgecolor=COLORS['success'], size=10)
    for x_pos in [2.25, 7, 11.75]:
        arrow(ax, (x_pos, 6.5), (x_pos, 6.0), color='black', lw=2)

    # Decision output
    add_box(ax, (3, 2.5), 8, 1.5,
            'DECISION OUTPUT\n\n'
            'Risk Tier (R1-R5) + Urgency Level + Explanation + Care Pathway + Confidence Score',
            facecolor='#F5F5F5', edgecolor='black', size=10)
    arrow(ax, (7, 4.5), (7, 4.0), color='black', lw=2.5)

    # Side notes
    add_box(ax, (0.3, 1.5), 2.5, 0.8,
            'DRAS-5 States\n5 Decision-Risk-Action States',
            facecolor='#E5F9FF', edgecolor=PALETTE[5], size=8)
    add_box(ax, (11.2, 1.5), 2.5, 0.8,
            'ORASR Routing\nSafety Routing & Care Pathways',
            facecolor='#FFE5D9', edgecolor=COLORS['danger'], size=8)

    ax.text(7, 0.8, 'Transparent | Auditable | Safety-First | Clinically-Grounded',
            ha='center', va='center', fontsize=11, fontweight='bold',
            style='italic', color='#555555')

    save_fig(fig, 'fig2_framework_architecture', output_dir)
    plt.close(fig)


def create_safety_gate_compliance(output_dir='outputs/figures'):
    """Figure 3: triage-first safety-gate escalation compliance.

    Core JIIS safety metric. Reads results/framework/safety_gate_compliance.json
    (falls back to framework_summary.json). Shows how the gate handles the
    central/dangerous cohort (caught vs missed red flags) and its over-escalation
    on benign cases -- the safety/cost trade-off the manuscript reports.
    """
    try:
        sg = load_results("framework/safety_gate_compliance.json")
    except FileNotFoundError:
        sg = load_results("framework/framework_summary.json")["safety_gate_compliance"]

    central_total = sg["central_dangerous_total"]
    caught = sg["central_caught_by_gate"]
    missed = sg["central_missed_by_gate"]
    compliance = sg["escalation_compliance"] * 100.0
    over_rate = sg["over_escalation_rate_on_benign"] * 100.0

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 4.4),
                                   gridspec_kw={"width_ratios": [1.15, 1]})

    # Left: stacked composition of the central/dangerous cohort (caught vs missed).
    bar_caught = axL.bar(["Central / dangerous\ncohort"], [caught],
                         color=COLORS["success"], edgecolor="#1a202c",
                         linewidth=0.6, hatch="//", label="Caught by gate")
    bar_missed = axL.bar(["Central / dangerous\ncohort"], [missed], bottom=[caught],
                         color=COLORS["danger"], edgecolor="#1a202c",
                         linewidth=0.6, hatch="xx", label="Missed red flags")
    axL.text(0, caught / 2, f"{caught}", ha="center", va="center",
             fontsize=10, fontweight="bold", color="white")
    axL.text(0, caught + missed + central_total * 0.02, f"missed = {missed}",
             ha="center", va="bottom", fontsize=9, fontweight="bold",
             color=COLORS["danger"])
    axL.set_ylabel(f"Cases (central/dangerous total n={central_total})")
    axL.set_title("Red-flag escalation by the safety gate")
    axL.set_ylim(0, central_total * 1.18)
    axL.grid(axis="y", which="both")
    axL.legend(loc="upper center", frameon=False, ncol=1, bbox_to_anchor=(0.5, -0.10))
    axL.spines[["top", "right"]].set_visible(False)

    # Right: the two headline rates (compliance vs benign over-escalation).
    rates = [compliance, over_rate]
    rate_labels = ["Escalation\ncompliance", "Over-escalation\non benign"]
    rate_colors = [COLORS["success"], COLORS["warning"]]
    hatches = ["//", ".."]
    bars = axR.bar(rate_labels, rates, color=rate_colors, edgecolor="#1a202c",
                   linewidth=0.6)
    for b, h in zip(bars, hatches):
        b.set_hatch(h)
    for b, v in zip(bars, rates):
        axR.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5,
                 f"{v:.1f}%", ha="center", va="bottom", fontsize=10,
                 fontweight="bold")
    axR.set_ylabel("Rate (%)")
    axR.set_ylim(0, 105)
    axR.set_title("Safety / over-triage trade-off")
    axR.grid(axis="y", which="both")
    axR.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        f"Safety-gate compliance (seed 42, synthetic cohort): "
        f"{caught}/{central_total} red flags escalated",
        fontsize=11,
    )

    save_fig(fig, 'fig3_safety_gate_compliance', output_dir)
    plt.close(fig)


def create_missingness_stability(output_dir='outputs/figures'):
    """Figure 4: routing stability when input fields are unobserved.

    Core JIIS governance metric. Reads results/framework/missingness_stability.json
    (falls back to framework_summary.json). Shows the gate-decision flip rate vs the
    stability score under conservative (worst-case) imputation of dropped red-flag
    fields, and confirms that no unsafe de-escalation flips occur.
    """
    try:
        ms = load_results("framework/missingness_stability.json")
    except FileNotFoundError:
        ms = load_results("framework/framework_summary.json")["missingness_stability"]

    flip_rate = ms["gate_flip_rate"] * 100.0
    stability = ms["stability_score"] * 100.0
    unsafe = ms["unsafe_deescalation_flips"]
    flips = ms["gate_decision_flips"]
    n_fields = len(ms["fields_dropped"])

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 4.4),
                                   gridspec_kw={"width_ratios": [1, 1.1]})

    # Left: stability vs flip-rate (color-blind-safe pair with distinct hatches).
    labels = ["Stable\nrouting", "Decision\nflips"]
    vals = [stability, flip_rate]
    colors = [COLORS["success"], COLORS["secondary"]]
    hatches = ["//", ".."]
    bars = axL.bar(labels, vals, color=colors, edgecolor="#1a202c", linewidth=0.6)
    for b, h in zip(bars, hatches):
        b.set_hatch(h)
    for b, v in zip(bars, vals):
        axL.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5,
                 f"{v:.1f}%", ha="center", va="bottom", fontsize=10,
                 fontweight="bold")
    axL.set_ylabel("Share of decisions (%)")
    axL.set_ylim(0, 105)
    axL.set_title(f"Stability under {n_fields} dropped red-flag fields")
    axL.grid(axis="y", which="both")
    axL.spines[["top", "right"]].set_visible(False)

    # Right: flip composition -- safe (hold or conservative escalate) vs unsafe.
    safe_flips = flips - unsafe
    bar_safe = axR.bar(["Gate-decision\nflips"], [safe_flips],
                       color=COLORS["info"], edgecolor="#1a202c",
                       linewidth=0.6, hatch="//", label="Safe flips (hold/escalate)")
    axR.bar(["Gate-decision\nflips"], [unsafe], bottom=[safe_flips],
            color=COLORS["danger"], edgecolor="#1a202c",
            linewidth=0.6, hatch="xx", label="Unsafe de-escalation")
    axR.text(0, safe_flips / 2, f"{safe_flips}", ha="center", va="center",
             fontsize=10, fontweight="bold", color="white")
    axR.text(0, flips + max(flips * 0.02, 1),
             f"unsafe de-escalations = {unsafe}", ha="center", va="bottom",
             fontsize=9, fontweight="bold",
             color=COLORS["danger"] if unsafe else COLORS["success"])
    axR.set_ylabel("Flipped decisions (n)")
    axR.set_ylim(0, max(flips * 1.15, 1))
    axR.set_title("Flip safety composition")
    axR.legend(loc="upper right", frameon=False)
    axR.grid(axis="y", which="both")
    axR.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        f"Missingness stability (seed 42): stability score {stability:.1f}%, "
        f"{unsafe} unsafe de-escalations",
        fontsize=11,
    )

    save_fig(fig, 'fig4_missingness_stability', output_dir)
    plt.close(fig)


def main():
    """Generate the TRI-X manuscript-scope figures (schematic + behaviour)."""
    print("\n" + "=" * 60)
    print("TRI-X MANUSCRIPT FIGURE GENERATOR (schematic + behaviour)")
    print("=" * 60 + "\n")

    apply_pub_style()  # shared publication style: serif fonts + Okabe-Ito palette

    output_dir = 'outputs/figures'
    print(f"Output directory: {output_dir}\n")

    # Schematic (no quantitative content)
    create_srgl_flow_diagram(output_dir)
    create_framework_architecture(output_dir)

    # Data-driven decision-behaviour charts (results/framework/, seed 42).
    # If the artefacts are missing, run scripts/run_framework.py first.
    try:
        create_safety_gate_compliance(output_dir)
        create_missingness_stability(output_dir)
    except FileNotFoundError as exc:
        print(f"[SKIP] behaviour charts: {exc}")
        print("       run 'python scripts/run_framework.py' (seed 42) first.")

    print("\n" + "=" * 60)
    print("[DONE] FIGURE PASS COMPLETE")
    print("=" * 60)
    print("Vector PDF + 300-dpi PNG written to", output_dir + "/")
    print("  - fig1_srgl_flow_diagram        (schematic)")
    print("  - fig2_framework_architecture   (schematic)")
    print("  - fig3_safety_gate_compliance   (results/framework/safety_gate_compliance.json)")
    print("  - fig4_missingness_stability    (results/framework/missingness_stability.json)")
    print("\nExploratory ML effectiveness figs (SUPPLEMENTARY, outside manuscript scope):")
    print("  python experimental/effectiveness/generate_manuscript_figures.py")
    print("\n" + "=" * 60 + "\n")


if __name__ == '__main__':
    main()
