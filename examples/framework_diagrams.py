#!/usr/bin/env python3
"""
TRI-X Framework Component Diagrams

Detailed visualizations for:
- DRAS-5 (Decision-Risk-Action States)
- ORASR (Operational Reasoning-Action Safety Routing)
- TiTrATE Logic Flow
- Gate Decision Trees

Author: Chatchai Tritham
Date: 2026-01-28
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch, Circle, Wedge
from matplotlib.patches import Arc
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

# Publication settings
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 600
plt.rcParams['savefig.bbox'] = 'tight'

# Color palette
COLORS = {
    'S1': '#CC3311',  # Critical
    'S2': '#DE8F05',  # High
    'S3': '#ECA400',  # Moderate
    'S4': '#029E73',  # Low
    'S5': '#0173B2',  # Minimal
}


def create_dras5_state_machine(output_dir='outputs/figures'):
    """
    Figure 8: DRAS-5 State Machine Diagram
    Shows 5 Decision-Risk-Action States with transitions
    """
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Title
    ax.text(8, 11.5, 'DRAS-5: Decision-Risk-Action States',
            ha='center', va='top', fontsize=18, fontweight='bold')
    ax.text(8, 11.0, '5-State Risk Machine for Emergency Triage Decision Support',
            ha='center', va='top', fontsize=13, style='italic', color='#555555')

    # State positions (circular layout with central input)
    state_positions = {
        'Input': (8, 9),
        'S1': (8, 6.5),     # Top center (Critical)
        'S2': (11.5, 5),     # Right (High)
        'S3': (11.5, 2.5),   # Bottom right (Moderate)
        'S4': (4.5, 2.5),    # Bottom left (Low)
        'S5': (4.5, 5),      # Left (Minimal)
    }

    # State definitions
    states = {
        'S1': {
            'name': 'State 1: Critical',
            'decision': 'Red Flag Detected',
            'risk': 'Imminent Danger',
            'action': 'Immediate Intervention\nActivate Emergency Protocol',
            'tier': 'R1',
            'color': COLORS['S1'],
            'examples': ['Stroke', 'CVA', 'Acute MI']
        },
        'S2': {
            'name': 'State 2: High Risk',
            'decision': 'High Risk Factors',
            'risk': 'Significant Risk',
            'action': 'Urgent Evaluation\nSpecialist Consultation',
            'tier': 'R2',
            'color': COLORS['S2'],
            'examples': ['TIA', 'Central Vertigo', 'AF']
        },
        'S3': {
            'name': 'State 3: Moderate Risk',
            'decision': 'Moderate Risk or Uncertainty',
            'risk': 'Moderate Risk',
            'action': 'Observation & Monitoring\nRe-evaluation in 4-6h',
            'tier': 'R3',
            'color': COLORS['S3'],
            'examples': ['Vestibular Migraine', 'BPPV (atypical)']
        },
        'S4': {
            'name': 'State 4: Low Risk',
            'decision': 'Low Risk, Clear Diagnosis',
            'risk': 'Low Risk',
            'action': 'Outpatient Management\nPrimary Care Follow-up',
            'tier': 'R4',
            'color': COLORS['S4'],
            'examples': ['BPPV (typical)', 'Vestibular Neuritis']
        },
        'S5': {
            'name': 'State 5: Minimal Risk',
            'decision': 'Minimal Risk, Benign',
            'risk': 'Minimal Risk',
            'action': 'Self-Care Instructions\nPRN Follow-up',
            'tier': 'R5',
            'color': COLORS['S5'],
            'examples': ['Orthostatic Hypotension', 'Anxiety-related']
        },
    }

    # Draw states
    for state_id, state_info in states.items():
        x, y = state_positions[state_id]

        # State circle
        circle = Circle((x, y), 0.9, color=state_info['color'], alpha=0.3, edgecolor=state_info['color'], linewidth=4)
        ax.add_patch(circle)

        # State name
        ax.text(x, y + 0.5, state_info['name'], ha='center', va='center',
                fontsize=11, fontweight='bold', color=state_info['color'])

        # Decision label
        ax.text(x, y + 0.2, state_info['decision'], ha='center', va='center',
                fontsize=9, fontweight='bold')

        # Action
        ax.text(x, y - 0.15, state_info['action'], ha='center', va='center',
                fontsize=8, style='italic')

        # Risk tier
        tier_box = FancyBboxPatch((x-0.25, y-0.6), 0.5, 0.3,
                                   boxstyle="round,pad=0.05",
                                   edgecolor='black', facecolor=state_info['color'], linewidth=2, alpha=0.7)
        ax.add_patch(tier_box)
        ax.text(x, y-0.45, state_info['tier'], ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')

    # Draw input box
    x_in, y_in = state_positions['Input']
    input_box = FancyBboxPatch((x_in-1.5, y_in-0.4), 3, 0.8,
                                boxstyle="round,pad=0.1",
                                edgecolor='black', facecolor='#E8E8E8', linewidth=3)
    ax.add_patch(input_box)
    ax.text(x_in, y_in, 'PATIENT INPUT\nScreening Results + Risk Assessment',
            ha='center', va='center', fontsize=11, fontweight='bold')

    # Draw transitions (arrows from input to each state)
    transitions = [
        ('Input', 'S1', 'Red\nFlag', 'red'),
        ('Input', 'S2', 'High\nRisk', 'orange'),
        ('Input', 'S3', 'Moderate/\nUncertain', 'gold'),
        ('Input', 'S4', 'Low\nRisk', 'green'),
        ('Input', 'S5', 'Minimal\nRisk', 'blue'),
    ]

    for from_state, to_state, label, color in transitions:
        x1, y1 = state_positions[from_state]
        x2, y2 = state_positions[to_state]

        # Adjust start point (bottom of input box)
        if from_state == 'Input':
            y1 = y1 - 0.5

        # Arrow
        arrow = FancyArrowPatch((x1, y1), (x2, y2 + 0.9),
                                 arrowstyle='->', mutation_scale=25,
                                 linewidth=3, color=color, alpha=0.7,
                                 connectionstyle="arc3,rad=0.1")
        ax.add_patch(arrow)

        # Label
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2 + 0.9) / 2
        ax.text(mid_x, mid_y, label, ha='center', va='center',
                fontsize=9, fontweight='bold', color=color,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, linewidth=2))

    # Add state transition table below
    table_y = 1.0
    ax.text(8, table_y + 0.3, 'State Transition Rules', ha='center', va='center',
            fontsize=12, fontweight='bold')

    table_data = [
        ['State', 'Entry Condition', 'Risk Tier', 'Urgency', 'Action Required', 'Next Step'],
        ['S1', 'Red flag detected', 'R1', 'Emergency', 'Immediate intervention', 'ER admission'],
        ['S2', '≥2 high risk factors', 'R2', 'Urgent', 'Specialist evaluation', 'Imaging + consult'],
        ['S3', '1 risk OR unclear', 'R3', 'Semi-urgent', 'Observation', 'Re-assess in 4-6h'],
        ['S4', 'Clear diagnosis, low risk', 'R4', 'Non-urgent', 'Outpatient care', 'PCP follow-up'],
        ['S5', 'Benign, minimal risk', 'R5', 'Routine', 'Self-care', 'PRN follow-up'],
    ]

    # Draw table
    cell_width = [1.2, 2.5, 1.0, 1.2, 2.0, 1.8]
    cell_height = 0.35
    table_x_start = 1.5

    for i, row in enumerate(table_data):
        x_offset = table_x_start
        for j, cell in enumerate(row):
            # Header row
            if i == 0:
                cell_box = Rectangle((x_offset, table_y - (i+1)*cell_height), cell_width[j], cell_height,
                                      facecolor='#333333', edgecolor='black', linewidth=1)
                text_color = 'white'
                fontweight = 'bold'
            else:
                # Color first column by state
                if j == 0:
                    state_id = cell
                    cell_color = states[state_id]['color'] if state_id in states else '#F0F0F0'
                    alpha = 0.3
                else:
                    cell_color = '#FFFFFF'
                    alpha = 1.0

                cell_box = Rectangle((x_offset, table_y - (i+1)*cell_height), cell_width[j], cell_height,
                                      facecolor=cell_color, edgecolor='black', linewidth=0.5, alpha=alpha)
                text_color = 'black'
                fontweight = 'normal'

            ax.add_patch(cell_box)
            ax.text(x_offset + cell_width[j]/2, table_y - (i+0.5)*cell_height, cell,
                    ha='center', va='center', fontsize=7, fontweight=fontweight, color=text_color)
            x_offset += cell_width[j]

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['S1'], edgecolor='black', label='S1: Critical (R1)', alpha=0.6),
        mpatches.Patch(facecolor=COLORS['S2'], edgecolor='black', label='S2: High Risk (R2)', alpha=0.6),
        mpatches.Patch(facecolor=COLORS['S3'], edgecolor='black', label='S3: Moderate Risk (R3)', alpha=0.6),
        mpatches.Patch(facecolor=COLORS['S4'], edgecolor='black', label='S4: Low Risk (R4)', alpha=0.6),
        mpatches.Patch(facecolor=COLORS['S5'], edgecolor='black', label='S5: Minimal Risk (R5)', alpha=0.6),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9, frameon=True, shadow=True, ncol=2)

    # Save figure
    plt.savefig(f'{output_dir}/fig8_dras5_state_machine.png', dpi=600, bbox_inches='tight')
    plt.savefig(f'{output_dir}/fig8_dras5_state_machine.pdf', bbox_inches='tight')
    print(f"[OK] Saved: fig8_dras5_state_machine.png/pdf")
    plt.close()


def create_orasr_routing_diagram(output_dir='outputs/figures'):
    """
    Figure 9: ORASR Routing Diagram
    Shows Operational Reasoning-Action Safety Routing
    """
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(8, 9.5, 'ORASR: Operational Reasoning-Action Safety Routing',
            ha='center', va='top', fontsize=18, fontweight='bold')
    ax.text(8, 9.0, 'Safe Care Pathway Routing with Audit Trails and Safety Nets',
            ha='center', va='top', fontsize=13, style='italic', color='#555555')

    # Input box
    input_box = FancyBboxPatch((6, 7.8), 4, 0.8,
                                boxstyle="round,pad=0.1",
                                edgecolor='black', facecolor='#E8E8E8', linewidth=3)
    ax.add_patch(input_box)
    ax.text(8, 8.2, 'DECISION OUTPUT from DRAS-5\nRisk Tier + State + Explanation',
            ha='center', va='center', fontsize=11, fontweight='bold')

    # Arrow to reasoning module
    arrow1 = FancyArrowPatch((8, 7.8), (8, 7.0),
                              arrowstyle='->', mutation_scale=20,
                              linewidth=3, color='black')
    ax.add_patch(arrow1)

    # Reasoning Module
    reasoning_box = FancyBboxPatch((5.5, 5.5), 5, 1.3,
                                    boxstyle="round,pad=0.15",
                                    edgecolor='#0173B2', facecolor='#E5F2FF', linewidth=3)
    ax.add_patch(reasoning_box)
    ax.text(8, 6.6, 'REASONING MODULE', ha='center', va='center',
            fontsize=13, fontweight='bold', color='#0173B2')
    ax.text(8, 6.15, 'Clinical Logic + Guideline Mapping + Constraint Checking',
            ha='center', va='center', fontsize=10)
    ax.text(8, 5.75, 'Safety Verification: Validate pathway against clinical guidelines',
            ha='center', va='center', fontsize=9, style='italic', color='#555555')

    # Safety Checkpoint (side box)
    safety_box = FancyBboxPatch((0.5, 5.5), 3.5, 1.3,
                                 boxstyle="round,pad=0.15",
                                 edgecolor='#CC3311', facecolor='#FFE5E5', linewidth=3)
    ax.add_patch(safety_box)
    ax.text(2.25, 6.6, 'SAFETY CHECKPOINT', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#CC3311')
    ax.text(2.25, 6.1, 'Red Flag Monitor\nConstraint Validator\nBoundary Checker',
            ha='center', va='center', fontsize=9)

    # Bidirectional arrow
    arrow_safety = FancyArrowPatch((4, 6.15), (5.5, 6.15),
                                    arrowstyle='<->', mutation_scale=15,
                                    linewidth=2, color='#CC3311')
    ax.add_patch(arrow_safety)

    # Explanation Generator (side box)
    explain_box = FancyBboxPatch((12, 5.5), 3.5, 1.3,
                                  boxstyle="round,pad=0.15",
                                  edgecolor='#029E73', facecolor='#E5F9F0', linewidth=3)
    ax.add_patch(explain_box)
    ax.text(13.75, 6.6, 'EXPLANATION GEN', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#029E73')
    ax.text(13.75, 6.1, 'SHAP + LIME\nCounterfactuals\nAudit Trail',
            ha='center', va='center', fontsize=9)

    # Bidirectional arrow
    arrow_explain = FancyArrowPatch((10.5, 6.15), (12, 6.15),
                                     arrowstyle='<->', mutation_scale=15,
                                     linewidth=2, color='#029E73')
    ax.add_patch(arrow_explain)

    # Arrow to action routing
    arrow2 = FancyArrowPatch((8, 5.5), (8, 4.7),
                              arrowstyle='->', mutation_scale=20,
                              linewidth=3, color='black')
    ax.add_patch(arrow2)

    # Action Routing
    routing_box = FancyBboxPatch((5, 3.5), 6, 1.0,
                                  boxstyle="round,pad=0.15",
                                  edgecolor='#DE8F05', facecolor='#FFF4E5', linewidth=3)
    ax.add_patch(routing_box)
    ax.text(8, 4.3, 'ACTION ROUTING', ha='center', va='center',
            fontsize=13, fontweight='bold', color='#DE8F05')
    ax.text(8, 3.85, 'Map State → Care Pathway → Clinical Action',
            ha='center', va='center', fontsize=10)

    # Five care pathways
    pathways = [
        {'name': 'Emergency\nProtocol', 'x': 2, 'y': 1.5, 'color': '#CC3311', 'tier': 'R1/S1'},
        {'name': 'Urgent\nEvaluation', 'x': 4.5, 'y': 1.5, 'color': '#DE8F05', 'tier': 'R2/S2'},
        {'name': 'Observation\nUnit', 'x': 7, 'y': 1.5, 'color': '#ECA400', 'tier': 'R3/S3'},
        {'name': 'Outpatient\nClinic', 'x': 9.5, 'y': 1.5, 'color': '#029E73', 'tier': 'R4/S4'},
        {'name': 'Self-Care\nDischarge', 'x': 12, 'y': 1.5, 'color': '#0173B2', 'tier': 'R5/S5'},
    ]

    for pathway in pathways:
        # Pathway box
        path_box = FancyBboxPatch((pathway['x']-0.9, pathway['y']-0.5), 1.8, 1.0,
                                   boxstyle="round,pad=0.1",
                                   edgecolor=pathway['color'], facecolor=pathway['color'], linewidth=2, alpha=0.3)
        ax.add_patch(path_box)

        ax.text(pathway['x'], pathway['y']+0.3, pathway['name'], ha='center', va='center',
                fontsize=10, fontweight='bold', color=pathway['color'])
        ax.text(pathway['x'], pathway['y']-0.1, pathway['tier'], ha='center', va='center',
                fontsize=9, fontweight='bold')

        # Arrow from routing to pathway
        arrow = FancyArrowPatch((8, 3.5), (pathway['x'], pathway['y']+0.5),
                                 arrowstyle='->', mutation_scale=15,
                                 linewidth=2, color=pathway['color'], alpha=0.7,
                                 connectionstyle="arc3,rad=0.2")
        ax.add_patch(arrow)

    # Audit trail (bottom)
    audit_box = FancyBboxPatch((1, 0.2), 14, 0.6,
                                boxstyle="round,pad=0.1",
                                edgecolor='#555555', facecolor='#F5F5F5', linewidth=2)
    ax.add_patch(audit_box)
    ax.text(8, 0.5, 'AUDIT TRAIL: Decision ID + Timestamp + State + Pathway + Explanation + Clinician Override (if any)',
            ha='center', va='center', fontsize=9, fontweight='bold', color='#333333', family='monospace')

    # Key features annotation
    features_text = """
    Key Safety Features:
    • Constraint Validation at every step
    • Guideline Compliance Checking
    • Explanation Generation (XAI)
    • Audit Trail (full traceability)
    • Human Override Option
    • Safety Net for edge cases
    """

    ax.text(14.5, 4.0, features_text.strip(), ha='left', va='center',
            fontsize=8, bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFFFCC', edgecolor='black', linewidth=1))

    # Save figure
    plt.savefig(f'{output_dir}/fig9_orasr_routing_diagram.png', dpi=600, bbox_inches='tight')
    plt.savefig(f'{output_dir}/fig9_orasr_routing_diagram.pdf', bbox_inches='tight')
    print(f"[OK] Saved: fig9_orasr_routing_diagram.png/pdf")
    plt.close()


def create_titrate_decision_tree(output_dir='outputs/figures'):
    """
    Figure 10: TiTrATE Decision Tree
    Shows temporal and symptomatic decision logic
    """
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Title
    ax.text(8, 11.5, 'TiTrATE Decision Tree: Temporal & Symptomatic Classification',
            ha='center', va='top', fontsize=17, fontweight='bold')

    # Root node
    root_box = FancyBboxPatch((6.5, 10), 3, 0.7,
                               boxstyle="round,pad=0.1",
                               edgecolor='black', facecolor='#E8E8E8', linewidth=3)
    ax.add_patch(root_box)
    ax.text(8, 10.35, 'Dizziness/Vertigo Presentation', ha='center', va='center',
            fontsize=12, fontweight='bold')

    # First split: Onset Pattern
    ax.text(8, 9.3, 'Onset Pattern?', ha='center', va='center',
            fontsize=11, fontweight='bold', style='italic')

    # Branches
    onset_nodes = [
        {'label': 'Sudden\n(<1 min)', 'x': 2.5, 'y': 7.5, 'color': '#CC3311'},
        {'label': 'Acute\n(<24h)', 'x': 5.5, 'y': 7.5, 'color': '#DE8F05'},
        {'label': 'Subacute\n(1-7 days)', 'x': 8.5, 'y': 7.5, 'color': '#ECA400'},
        {'label': 'Gradual\n(>1 week)', 'x': 11.5, 'y': 7.5, 'color': '#029E73'},
        {'label': 'Episodic\n(recurrent)', 'x': 14, 'y': 7.5, 'color': '#0173B2'},
    ]

    for node in onset_nodes:
        # Node box
        node_box = FancyBboxPatch((node['x']-0.9, node['y']-0.35), 1.8, 0.7,
                                   boxstyle="round,pad=0.1",
                                   edgecolor=node['color'], facecolor=node['color'], linewidth=2, alpha=0.3)
        ax.add_patch(node_box)
        ax.text(node['x'], node['y'], node['label'], ha='center', va='center',
                fontsize=10, fontweight='bold')

        # Arrow from root
        arrow = FancyArrowPatch((8, 10), (node['x'], node['y']+0.35),
                                 arrowstyle='->', mutation_scale=15,
                                 linewidth=2, color=node['color'], alpha=0.7,
                                 connectionstyle="arc3,rad=0.2")
        ax.add_patch(arrow)

    # Second level: Duration (for Sudden branch as example)
    ax.text(2.5, 6.7, 'Duration?', ha='center', va='center',
            fontsize=10, fontweight='bold', style='italic')

    duration_nodes = [
        {'label': 'Seconds\n(BPPV)', 'x': 1, 'y': 5.5, 'tier': 'R4'},
        {'label': 'Minutes\n(TIA)', 'x': 2.5, 'y': 5.5, 'tier': 'R2'},
        {'label': 'Hours\n(Migraine)', 'x': 4, 'y': 5.5, 'tier': 'R3'},
    ]

    for node in duration_nodes:
        node_box = FancyBboxPatch((node['x']-0.6, node['y']-0.3), 1.2, 0.6,
                                   boxstyle="round,pad=0.05",
                                   edgecolor='black', facecolor='#FFFFCC', linewidth=1.5)
        ax.add_patch(node_box)
        ax.text(node['x'], node['y']+0.1, node['label'], ha='center', va='center',
                fontsize=9)
        ax.text(node['x'], node['y']-0.15, node['tier'], ha='center', va='center',
                fontsize=8, fontweight='bold', color='red' if node['tier']=='R2' else 'green')

        # Arrow
        arrow = FancyArrowPatch((2.5, 7.15), (node['x'], node['y']+0.3),
                                 arrowstyle='->', mutation_scale=12,
                                 linewidth=1.5, color='gray')
        ax.add_patch(arrow)

    # Third level: Associated Symptoms (for Minutes/TIA branch)
    ax.text(2.5, 4.7, 'Associated\nSymptoms?', ha='center', va='center',
            fontsize=9, fontweight='bold', style='italic')

    symptom_nodes = [
        {'label': 'Focal\nWeakness\n→ Stroke (R1)', 'x': 1, 'y': 3.5, 'color': '#CC3311'},
        {'label': 'Headache\n+ Nausea\n→ Migraine (R3)', 'x': 2.5, 'y': 3.5, 'color': '#ECA400'},
        {'label': 'Hearing Loss\n→ Meniere (R3)', 'x': 4, 'y': 3.5, 'color': '#ECA400'},
    ]

    for node in symptom_nodes:
        node_box = FancyBboxPatch((node['x']-0.6, node['y']-0.4), 1.2, 0.8,
                                   boxstyle="round,pad=0.05",
                                   edgecolor=node['color'], facecolor=node['color'], linewidth=2, alpha=0.4)
        ax.add_patch(node_box)
        ax.text(node['x'], node['y'], node['label'], ha='center', va='center',
                fontsize=8)

        # Arrow
        arrow = FancyArrowPatch((2.5, 5.2), (node['x'], node['y']+0.4),
                                 arrowstyle='->', mutation_scale=10,
                                 linewidth=1.5, color=node['color'], alpha=0.7)
        ax.add_patch(arrow)

    # Parallel branch for Acute onset
    ax.text(5.5, 6.7, 'Red Flags?', ha='center', va='center',
            fontsize=10, fontweight='bold', style='italic')

    redflag_nodes = [
        {'label': 'YES\n→ Central (R1/R2)', 'x': 5.5, 'y': 5.5, 'color': '#CC3311'},
        {'label': 'NO\n→ Peripheral (R4)', 'x': 7, 'y': 5.5, 'color': '#029E73'},
    ]

    for node in redflag_nodes:
        node_box = FancyBboxPatch((node['x']-0.7, node['y']-0.3), 1.4, 0.6,
                                   boxstyle="round,pad=0.05",
                                   edgecolor=node['color'], facecolor=node['color'], linewidth=2, alpha=0.4)
        ax.add_patch(node_box)
        ax.text(node['x'], node['y'], node['label'], ha='center', va='center',
                fontsize=9, fontweight='bold')

        # Arrow
        arrow = FancyArrowPatch((5.5, 7.15), (node['x'], node['y']+0.3),
                                 arrowstyle='->', mutation_scale=12,
                                 linewidth=1.5, color=node['color'])
        ax.add_patch(arrow)

    # Episodic branch
    ax.text(14, 6.7, 'Trigger?', ha='center', va='center',
            fontsize=10, fontweight='bold', style='italic')

    trigger_nodes = [
        {'label': 'Head\nMovement\n→ BPPV (R4)', 'x': 13, 'y': 5.5},
        {'label': 'Stress/Food\n→ Migraine (R3)', 'x': 15, 'y': 5.5},
    ]

    for node in trigger_nodes:
        node_box = FancyBboxPatch((node['x']-0.7, node['y']-0.4), 1.4, 0.8,
                                   boxstyle="round,pad=0.05",
                                   edgecolor='black', facecolor='#E8F4E8', linewidth=1.5)
        ax.add_patch(node_box)
        ax.text(node['x'], node['y'], node['label'], ha='center', va='center',
                fontsize=8)

        # Arrow
        arrow = FancyArrowPatch((14, 7.15), (node['x'], node['y']+0.4),
                                 arrowstyle='->', mutation_scale=10,
                                 linewidth=1.5, color='gray')
        ax.add_patch(arrow)

    # TiTrATE principles box (bottom)
    principles_box = FancyBboxPatch((1, 0.3), 14, 2.0,
                                     boxstyle="round,pad=0.15",
                                     edgecolor='#0173B2', facecolor='#E5F2FF', linewidth=3)
    ax.add_patch(principles_box)

    ax.text(8, 2.0, 'TiTrATE Classification Principles', ha='center', va='center',
            fontsize=13, fontweight='bold', color='#0173B2')

    principles_text = """
    1. Temporal Pattern: Onset (sudden/acute/gradual) + Duration (seconds/minutes/hours/days/chronic)
    2. Symptomatic Pattern: Type (vertigo/dizziness/lightheadedness) + Triggers (positional/spontaneous)
    3. Associated Features: Red flags (focal signs) + Risk factors (age, CVD, diabetes)
    4. Progression: Improving/stable/worsening + Previous episodes
    5. Constraint Satisfaction: All clinical rules must be satisfied before classification
    """

    ax.text(8, 1.0, principles_text.strip(), ha='center', va='center',
            fontsize=9, family='monospace')

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#CC3311', edgecolor='black', label='Critical Risk (R1/R2)', alpha=0.5),
        mpatches.Patch(facecolor='#ECA400', edgecolor='black', label='Moderate Risk (R3)', alpha=0.5),
        mpatches.Patch(facecolor='#029E73', edgecolor='black', label='Low Risk (R4/R5)', alpha=0.5),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10, frameon=True, shadow=True)

    # Save figure
    plt.savefig(f'{output_dir}/fig10_titrate_decision_tree.png', dpi=600, bbox_inches='tight')
    plt.savefig(f'{output_dir}/fig10_titrate_decision_tree.pdf', bbox_inches='tight')
    print(f"[OK] Saved: fig10_titrate_decision_tree.png/pdf")
    plt.close()


def main():
    """Generate all framework component diagrams"""

    print("\n" + "="*60)
    print("TRI-X FRAMEWORK COMPONENT DIAGRAMS")
    print("="*60 + "\n")

    output_dir = 'outputs/figures'
    print(f"Output directory: {output_dir}\n")
    print("Generating framework diagrams...\n")

    create_dras5_state_machine(output_dir)
    create_orasr_routing_diagram(output_dir)
    create_titrate_decision_tree(output_dir)

    print("\n" + "="*60)
    print("[SUCCESS] ALL FRAMEWORK DIAGRAMS GENERATED!")
    print("="*60)
    print(f"\nTotal figures: 3")
    print(f"Output formats: PNG (600 DPI) + PDF (vector)")
    print(f"Location: {output_dir}/")
    print("\nFigures created:")
    print("  8. fig8_dras5_state_machine - 5-state decision machine")
    print("  9. fig9_orasr_routing_diagram - Safety routing system")
    print("  10. fig10_titrate_decision_tree - TiTrATE logic tree")
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
