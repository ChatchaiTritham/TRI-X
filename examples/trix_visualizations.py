#!/usr/bin/env python3
"""
TRI-X Framework Structural Visualizations

Generates manuscript-preparation STRUCTURAL diagrams only:
- SRGL Logic Flow Diagram (fig1)
- Framework Architecture (fig2)

These figures contain no quantitative claims; they hardcode only box/arrow
layout coordinates. Quantitative figures rendered from computed ``results/`` are
produced by ``scripts/generate_manuscript_figures.py`` instead. Panels that have
no computed source (performance dashboard, 3D performance grid, XAI-method
comparison, decision-time analysis) are intentionally not rendered here; see
REPRODUCIBILITY.md for the manuscript-vs-code gap.

Author: Chatchai Tritham
Date: 2026-01-28
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches

import warnings

warnings.filterwarnings('ignore')

# Canonical Top-Tier figure style (shared across all PhD repos; see
# _management/FIGURE_STYLE.md). Color-blind-safe Okabe-Ito palette, used in order.
PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000"]


def apply_pub_style():
    """Apply the shared publication rcParams + Okabe-Ito cycler. Call once."""
    mpl.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
        "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.8, "axes.grid": True,
        "grid.alpha": 0.3, "grid.linewidth": 0.6,
        "lines.linewidth": 1.6, "lines.markersize": 5,
        "legend.frameon": False, "figure.constrained_layout.use": True,
        "axes.prop_cycle": mpl.cycler(color=PALETTE),
    })


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
    """
    Figure 1: SRGL Logic Flow Diagram
    Shows the three-gate sequential screening process.

    Structural diagram only: hardcodes box/arrow layout coordinates, no numbers.
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Title
    ax.text(
        5,
        11.5,
        'Screening-First Risk Governance Logic (SRGL)',
        ha='center',
        va='top',
        fontsize=16,
        fontweight='bold',
    )

    # Input box
    input_box = FancyBboxPatch(
        (3.5, 10),
        3,
        0.8,
        boxstyle="round,pad=0.1",
        edgecolor='black',
        facecolor='#E8E8E8',
        linewidth=2,
    )
    ax.add_patch(input_box)
    ax.text(
        5,
        10.4,
        'Patient Input\n(Demographics, Symptoms, Vitals)',
        ha='center',
        va='center',
        fontsize=10,
        fontweight='bold',
    )

    # Arrow to Gate 1
    arrow1 = FancyArrowPatch(
        (5, 10),
        (5, 9.2),
        arrowstyle='->',
        mutation_scale=20,
        linewidth=2,
        color='black',
    )
    ax.add_patch(arrow1)

    # Gate 1: Critical Red Flags
    gate1_box = FancyBboxPatch(
        (2, 7.5),
        6,
        1.5,
        boxstyle="round,pad=0.1",
        edgecolor=COLORS['gate1'],
        facecolor='#FFE5E5',
        linewidth=3,
    )
    ax.add_patch(gate1_box)
    ax.text(
        5,
        8.7,
        'Gate G1: Critical Red Flag Screening',
        ha='center',
        va='center',
        fontsize=12,
        fontweight='bold',
        color=COLORS['gate1'],
    )
    ax.text(
        5,
        8.2,
        'Focal weakness | Thunderclap headache | Acute hearing loss\n'
        'Diplopia | Dysarthria | Severe ataxia',
        ha='center',
        va='center',
        fontsize=9,
    )

    # Decision diamond for Gate 1
    decision1 = mpatches.FancyBboxPatch(
        (4.2, 6.8),
        1.6,
        0.5,
        boxstyle="round,pad=0.05",
        edgecolor='black',
        facecolor='#FFF9E5',
        linewidth=2,
        transform=ax.transData,
    )
    ax.add_patch(decision1)
    ax.text(
        5,
        7.05,
        'Red Flag\nDetected?',
        ha='center',
        va='center',
        fontsize=9,
        fontweight='bold',
    )

    # YES path (Red Flag detected) -> R1/R2
    arrow_yes1 = FancyArrowPatch(
        (6, 7),
        (7.5, 7),
        arrowstyle='->',
        mutation_scale=15,
        linewidth=2,
        color=COLORS['danger'],
    )
    ax.add_patch(arrow_yes1)
    ax.text(6.7, 7.3, 'YES', fontsize=9, fontweight='bold', color=COLORS['danger'])

    # R1/R2 outcome box
    outcome_r1 = FancyBboxPatch(
        (7.5, 6.5),
        1.8,
        1,
        boxstyle="round,pad=0.1",
        edgecolor=COLORS['danger'],
        facecolor='#FFE5E5',
        linewidth=2,
    )
    ax.add_patch(outcome_r1)
    ax.text(
        8.4,
        7.3,
        'R1/R2',
        ha='center',
        va='center',
        fontsize=11,
        fontweight='bold',
        color=COLORS['danger'],
    )
    ax.text(
        8.4,
        6.85,
        'Critical/High Risk\nImmediate Care',
        ha='center',
        va='center',
        fontsize=8,
    )

    # NO path -> Gate 2
    arrow_no1 = FancyArrowPatch(
        (5, 6.8),
        (5, 6.0),
        arrowstyle='->',
        mutation_scale=15,
        linewidth=2,
        color='black',
    )
    ax.add_patch(arrow_no1)
    ax.text(5.3, 6.4, 'NO', fontsize=9, fontweight='bold')

    # Gate 2: Risk Factor Assessment
    gate2_box = FancyBboxPatch(
        (2, 4.5),
        6,
        1.3,
        boxstyle="round,pad=0.1",
        edgecolor=COLORS['gate2'],
        facecolor='#FFF4E5',
        linewidth=3,
    )
    ax.add_patch(gate2_box)
    ax.text(
        5,
        5.5,
        'Gate G2: Risk Factor Assessment',
        ha='center',
        va='center',
        fontsize=12,
        fontweight='bold',
        color=COLORS['gate2'],
    )
    ax.text(
        5,
        5.0,
        'Age >65 | Hypertension | Diabetes | CVD | Atrial fibrillation\n'
        'Previous stroke/TIA | Vascular risk factors',
        ha='center',
        va='center',
        fontsize=9,
    )

    # Decision diamond for Gate 2
    decision2 = mpatches.FancyBboxPatch(
        (4.2, 3.8),
        1.6,
        0.5,
        boxstyle="round,pad=0.05",
        edgecolor='black',
        facecolor='#FFF9E5',
        linewidth=2,
        transform=ax.transData,
    )
    ax.add_patch(decision2)
    ax.text(
        5,
        4.05,
        'High Risk\nFactors?',
        ha='center',
        va='center',
        fontsize=9,
        fontweight='bold',
    )

    # YES path (High risk) -> R2/R3
    arrow_yes2 = FancyArrowPatch(
        (6, 4),
        (7.5, 4),
        arrowstyle='->',
        mutation_scale=15,
        linewidth=2,
        color=COLORS['warning'],
    )
    ax.add_patch(arrow_yes2)
    ax.text(6.7, 4.3, 'YES', fontsize=9, fontweight='bold', color=COLORS['warning'])

    # R2/R3 outcome box
    outcome_r2 = FancyBboxPatch(
        (7.5, 3.5),
        1.8,
        1,
        boxstyle="round,pad=0.1",
        edgecolor=COLORS['warning'],
        facecolor='#FFF9E5',
        linewidth=2,
    )
    ax.add_patch(outcome_r2)
    ax.text(
        8.4,
        4.3,
        'R2/R3',
        ha='center',
        va='center',
        fontsize=11,
        fontweight='bold',
        color=COLORS['warning'],
    )
    ax.text(
        8.4,
        3.85,
        'High/Moderate Risk\nUrgent Evaluation',
        ha='center',
        va='center',
        fontsize=8,
    )

    # NO path -> Gate 3
    arrow_no2 = FancyArrowPatch(
        (5, 3.8),
        (5, 3.0),
        arrowstyle='->',
        mutation_scale=15,
        linewidth=2,
        color='black',
    )
    ax.add_patch(arrow_no2)
    ax.text(5.3, 3.4, 'NO', fontsize=9, fontweight='bold')

    # Gate 3: Uncertainty Quantification
    gate3_box = FancyBboxPatch(
        (2, 1.5),
        6,
        1.3,
        boxstyle="round,pad=0.1",
        edgecolor=COLORS['gate3'],
        facecolor='#E5F2FF',
        linewidth=3,
    )
    ax.add_patch(gate3_box)
    ax.text(
        5,
        2.5,
        'Gate G3: Uncertainty Quantification',
        ha='center',
        va='center',
        fontsize=12,
        fontweight='bold',
        color=COLORS['gate3'],
    )
    ax.text(
        5,
        2.0,
        'Symptom clarity | Diagnosis confidence | Temporal pattern consistency\n'
        'Vital sign stability | Comorbidity complexity',
        ha='center',
        va='center',
        fontsize=9,
    )

    # Decision diamond for Gate 3
    decision3 = mpatches.FancyBboxPatch(
        (4.2, 0.8),
        1.6,
        0.5,
        boxstyle="round,pad=0.05",
        edgecolor='black',
        facecolor='#FFF9E5',
        linewidth=2,
        transform=ax.transData,
    )
    ax.add_patch(decision3)
    ax.text(
        5,
        1.05,
        'High\nUncertainty?',
        ha='center',
        va='center',
        fontsize=9,
        fontweight='bold',
    )

    # YES path (High uncertainty) -> R3
    arrow_yes3 = FancyArrowPatch(
        (6, 1),
        (7.5, 1),
        arrowstyle='->',
        mutation_scale=15,
        linewidth=2,
        color=COLORS['info'],
    )
    ax.add_patch(arrow_yes3)
    ax.text(6.7, 1.3, 'YES', fontsize=9, fontweight='bold', color=COLORS['info'])

    # R3 outcome box
    outcome_r3 = FancyBboxPatch(
        (7.5, 0.5),
        1.8,
        1,
        boxstyle="round,pad=0.1",
        edgecolor=COLORS['info'],
        facecolor='#E5F2FF',
        linewidth=2,
    )
    ax.add_patch(outcome_r3)
    ax.text(
        8.4,
        1.3,
        'R3',
        ha='center',
        va='center',
        fontsize=11,
        fontweight='bold',
        color=COLORS['info'],
    )
    ax.text(
        8.4, 0.85, 'Moderate Risk\nObservation', ha='center', va='center', fontsize=8
    )

    # NO path -> R4/R5
    arrow_no3 = FancyArrowPatch(
        (4, 1),
        (2.5, 1),
        arrowstyle='->',
        mutation_scale=15,
        linewidth=2,
        color=COLORS['success'],
    )
    ax.add_patch(arrow_no3)
    ax.text(3.3, 1.3, 'NO', fontsize=9, fontweight='bold', color=COLORS['success'])

    # R4/R5 outcome box
    outcome_r4 = FancyBboxPatch(
        (0.7, 0.5),
        1.8,
        1,
        boxstyle="round,pad=0.1",
        edgecolor=COLORS['success'],
        facecolor='#E5F9F0',
        linewidth=2,
    )
    ax.add_patch(outcome_r4)
    ax.text(
        1.6,
        1.3,
        'R4/R5',
        ha='center',
        va='center',
        fontsize=11,
        fontweight='bold',
        color=COLORS['success'],
    )
    ax.text(
        1.6,
        0.85,
        'Low/Minimal Risk\nOutpatient Care',
        ha='center',
        va='center',
        fontsize=8,
    )

    # Legend
    legend_elements = [
        mpatches.Patch(
            facecolor='#FFE5E5',
            edgecolor=COLORS['gate1'],
            label='Gate G1: Critical Screening',
            linewidth=2,
        ),
        mpatches.Patch(
            facecolor='#FFF4E5',
            edgecolor=COLORS['gate2'],
            label='Gate G2: Risk Assessment',
            linewidth=2,
        ),
        mpatches.Patch(
            facecolor='#E5F2FF',
            edgecolor=COLORS['gate3'],
            label='Gate G3: Uncertainty Check',
            linewidth=2,
        ),
    ]
    ax.legend(
        handles=legend_elements, loc='lower left', fontsize=9, frameon=True, shadow=True
    )

    # Save figure (vector PDF + 300-dpi PNG via shared rcParams)
    plt.savefig(f'{output_dir}/fig1_srgl_flow_diagram.png', bbox_inches='tight')
    plt.savefig(f'{output_dir}/fig1_srgl_flow_diagram.pdf', bbox_inches='tight')
    print("[OK] Saved: fig1_srgl_flow_diagram.png/pdf")
    plt.close()


def create_framework_architecture(output_dir='outputs/figures'):
    """
    Figure 2: TRI-X Framework Architecture
    Shows the complete system architecture with all components.

    Structural diagram only: hardcodes box/arrow layout coordinates, no numbers.
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(
        7,
        9.5,
        'TRI-X Framework Architecture',
        ha='center',
        va='top',
        fontsize=18,
        fontweight='bold',
    )

    # Three main components
    # Triage
    triage_box = FancyBboxPatch(
        (0.5, 6.5),
        3.5,
        2.5,
        boxstyle="round,pad=0.15",
        edgecolor='#CC3311',
        facecolor='#FFE5E5',
        linewidth=3,
    )
    ax.add_patch(triage_box)
    ax.text(
        2.25,
        8.5,
        'TRIAGE',
        ha='center',
        va='center',
        fontsize=14,
        fontweight='bold',
        color='#CC3311',
    )
    ax.text(
        2.25,
        7.8,
        'Clinical Guidelines',
        ha='center',
        va='center',
        fontsize=10,
        fontweight='bold',
    )
    ax.text(
        2.25,
        7.3,
        '- ACEP Dizziness/Vertigo\n- AHA/ASA Stroke\n- AAO-HNS BPPV\n- Red Flag Detection',
        ha='center',
        va='center',
        fontsize=9,
    )

    # TiTrATE
    titrate_box = FancyBboxPatch(
        (5.25, 6.5),
        3.5,
        2.5,
        boxstyle="round,pad=0.15",
        edgecolor='#DE8F05',
        facecolor='#FFF4E5',
        linewidth=3,
    )
    ax.add_patch(titrate_box)
    ax.text(
        7,
        8.5,
        'TiTrATE',
        ha='center',
        va='center',
        fontsize=14,
        fontweight='bold',
        color='#DE8F05',
    )
    ax.text(
        7,
        7.8,
        'Diagnostic Framework',
        ha='center',
        va='center',
        fontsize=10,
        fontweight='bold',
    )
    ax.text(
        7,
        7.3,
        '- Symptom Patterns\n- Risk Factor Scoring\n- Temporal Analysis\n- Comorbidity Assessment',
        ha='center',
        va='center',
        fontsize=9,
    )

    # XAI
    xai_box = FancyBboxPatch(
        (10, 6.5),
        3.5,
        2.5,
        boxstyle="round,pad=0.15",
        edgecolor='#0173B2',
        facecolor='#E5F2FF',
        linewidth=3,
    )
    ax.add_patch(xai_box)
    ax.text(
        11.75,
        8.5,
        'XAI',
        ha='center',
        va='center',
        fontsize=14,
        fontweight='bold',
        color='#0173B2',
    )
    ax.text(
        11.75,
        7.8,
        'Explainability Layer',
        ha='center',
        va='center',
        fontsize=10,
        fontweight='bold',
    )
    ax.text(
        11.75,
        7.3,
        '- SHAP Values\n- LIME\n- NMF Phenotypes\n- Counterfactuals\n- Rule Extraction',
        ha='center',
        va='center',
        fontsize=9,
    )

    # Arrows connecting components
    arrow1 = FancyArrowPatch(
        (4, 7.75),
        (5.25, 7.75),
        arrowstyle='->',
        mutation_scale=20,
        linewidth=2.5,
        color='black',
    )
    ax.add_patch(arrow1)

    arrow2 = FancyArrowPatch(
        (8.75, 7.75),
        (10, 7.75),
        arrowstyle='->',
        mutation_scale=20,
        linewidth=2.5,
        color='black',
    )
    ax.add_patch(arrow2)

    # SRGL Layer (underneath)
    srgl_box = FancyBboxPatch(
        (1, 4.5),
        12,
        1.5,
        boxstyle="round,pad=0.15",
        edgecolor='#029E73',
        facecolor='#E5F9F0',
        linewidth=3,
    )
    ax.add_patch(srgl_box)
    ax.text(
        7,
        5.7,
        'SRGL (Screening-First Risk Governance Logic)',
        ha='center',
        va='center',
        fontsize=13,
        fontweight='bold',
        color='#029E73',
    )
    ax.text(
        7,
        5.1,
        'Gate G1: Critical Red Flags  ->  Gate G2: Risk Factors  ->  '
        'Gate G3: Uncertainty Quantification',
        ha='center',
        va='center',
        fontsize=10,
    )

    # Arrows from components to SRGL
    for x_pos in [2.25, 7, 11.75]:
        arrow = FancyArrowPatch(
            (x_pos, 6.5),
            (x_pos, 6.0),
            arrowstyle='->',
            mutation_scale=15,
            linewidth=2,
            color='black',
        )
        ax.add_patch(arrow)

    # Output box
    output_box = FancyBboxPatch(
        (3, 2.5),
        8,
        1.5,
        boxstyle="round,pad=0.15",
        edgecolor='black',
        facecolor='#F5F5F5',
        linewidth=3,
    )
    ax.add_patch(output_box)
    ax.text(
        7,
        3.7,
        'DECISION OUTPUT',
        ha='center',
        va='center',
        fontsize=13,
        fontweight='bold',
    )
    ax.text(
        7,
        3.1,
        'Risk Tier (R1-R5) + Urgency Level + Explanation + Care Pathway + Confidence Score',
        ha='center',
        va='center',
        fontsize=10,
    )

    # Arrow from SRGL to Output
    arrow_out = FancyArrowPatch(
        (7, 4.5),
        (7, 4.0),
        arrowstyle='->',
        mutation_scale=20,
        linewidth=2.5,
        color='black',
    )
    ax.add_patch(arrow_out)

    # Input (top)
    input_box = FancyBboxPatch(
        (4.5, 9.8),
        5,
        0.8,
        boxstyle="round,pad=0.1",
        edgecolor='black',
        facecolor='#E8E8E8',
        linewidth=2,
    )
    ax.add_patch(input_box)
    ax.text(
        7,
        10.2,
        'PATIENT INPUT: Demographics, Symptoms, Vitals, Medical History',
        ha='center',
        va='center',
        fontsize=11,
        fontweight='bold',
    )

    # Arrows from input to components
    for x_pos in [2.25, 7, 11.75]:
        arrow = FancyArrowPatch(
            (7, 9.8),
            (x_pos, 9.0),
            arrowstyle='->',
            mutation_scale=15,
            linewidth=2,
            color='black',
        )
        ax.add_patch(arrow)

    # DRAS-5 side note
    dras_box = FancyBboxPatch(
        (0.3, 1.5),
        2.5,
        0.8,
        boxstyle="round,pad=0.1",
        edgecolor='#56B4E9',
        facecolor='#E5F9FF',
        linewidth=2,
    )
    ax.add_patch(dras_box)
    ax.text(
        1.55,
        1.9,
        'DRAS-5 States',
        ha='center',
        va='center',
        fontsize=9,
        fontweight='bold',
        color='#56B4E9',
    )
    ax.text(
        1.55, 1.6, '5 Decision-Risk-Action States', ha='center', va='center', fontsize=8
    )

    # ORASR side note
    orasr_box = FancyBboxPatch(
        (11.2, 1.5),
        2.5,
        0.8,
        boxstyle="round,pad=0.1",
        edgecolor='#D55E00',
        facecolor='#FFE5D9',
        linewidth=2,
    )
    ax.add_patch(orasr_box)
    ax.text(
        12.45,
        1.9,
        'ORASR Routing',
        ha='center',
        va='center',
        fontsize=9,
        fontweight='bold',
        color='#D55E00',
    )
    ax.text(
        12.45,
        1.6,
        'Safety Routing & Care Pathways',
        ha='center',
        va='center',
        fontsize=8,
    )

    # Bottom note
    ax.text(
        7,
        0.8,
        'Transparent | Auditable | Safety-First | Clinically-Grounded',
        ha='center',
        va='center',
        fontsize=11,
        fontweight='bold',
        style='italic',
        color='#555555',
    )

    # Save figure (vector PDF + 300-dpi PNG via shared rcParams)
    plt.savefig(f'{output_dir}/fig2_framework_architecture.png', bbox_inches='tight')
    plt.savefig(f'{output_dir}/fig2_framework_architecture.pdf', bbox_inches='tight')
    print("[OK] Saved: fig2_framework_architecture.png/pdf")
    plt.close()


def create_performance_dashboard_2d(output_dir='outputs/figures'):
    """
    Performance metrics dashboard.

    Not rendered: the committed package computes no diagnostic-performance metrics
    (accuracy, sensitivity, F1, ROC-AUC, etc.), so there is no computed source for
    this panel. See REPRODUCIBILITY.md for the manuscript-vs-code gap.
    """
    print(
        "[SKIP] create_performance_dashboard_2d: no computed performance metrics "
        "available (see REPRODUCIBILITY.md)."
    )
    return


def create_performance_3d(output_dir='outputs/figures'):
    """
    3D performance visualization.

    Not rendered: the per-cell accuracy values this panel requires (by age group
    and risk level) are not computed anywhere in the package. See REPRODUCIBILITY.md.
    """
    print(
        "[SKIP] create_performance_3d: no computed accuracy grid available "
        "(see REPRODUCIBILITY.md)."
    )
    return


def create_xai_methods_comparison(output_dir='outputs/figures'):
    """
    Explainability-method comparison.

    Not rendered: SHAP/LIME/NMF/counterfactual attribution values and
    explanation-consistency percentages are not produced by the package (no fitted
    explainers exist here). For computed SHAP importances, see
    scripts/generate_manuscript_figures.py. See REPRODUCIBILITY.md.
    """
    print(
        "[SKIP] create_xai_methods_comparison: no computed explainer outputs "
        "available (see REPRODUCIBILITY.md)."
    )
    return


def create_decision_time_analysis(output_dir='outputs/figures'):
    """
    Decision-time analysis.

    Not rendered: measured per-case latency is computed by scripts/run_all.py into
    results/latency_summary.json; this module does not synthesize timings.
    See REPRODUCIBILITY.md.
    """
    print(
        "[SKIP] create_decision_time_analysis: use results/latency_summary.json "
        "for measured latency (see REPRODUCIBILITY.md)."
    )
    return


def main():
    """Generate the TRI-X structural diagrams."""

    print("\n" + "=" * 60)
    print("TRI-X STRUCTURAL DIAGRAM GENERATOR")
    print("=" * 60 + "\n")

    apply_pub_style()  # shared publication style: serif fonts + Okabe-Ito palette

    output_dir = 'outputs/figures'

    print(f"Output directory: {output_dir}\n")
    print("Generating structural diagrams...\n")

    create_srgl_flow_diagram(output_dir)
    create_framework_architecture(output_dir)

    print("\n" + "=" * 60)
    print("[DONE] STRUCTURAL DIAGRAM PASS COMPLETE")
    print("=" * 60)
    print("Output formats: PNG (600 DPI) + PDF (vector)")
    print(f"Location: {output_dir}/")
    print("\nRendered (structural, no quantitative content):")
    print("  - fig1_srgl_flow_diagram      (logic diagram)")
    print("  - fig2_framework_architecture (architecture diagram)")
    print("\nFor computed, data-driven figures run:")
    print("  python scripts/run_all.py")
    print("  python scripts/generate_manuscript_figures.py")
    print("\nNot rendered here (no computed source; see REPRODUCIBILITY.md):")
    print("  - performance dashboard, 3D performance, XAI comparison, decision time")
    print("\n" + "=" * 60 + "\n")


if __name__ == '__main__':
    main()
