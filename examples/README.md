# TRI-X Visualization Examples

This directory contains scripts to generate publication-ready figures for the TRI-X framework.

## 📊 Available Visualizations

### Basic Visualizations (7 figures)

Run `python trix_visualizations.py` to generate:

1. **fig1_srgl_flow_diagram** - SRGL Logic Flow with 3 Gates
2. **fig2_framework_architecture** - Complete TRI-X Architecture
3. **fig3_performance_dashboard_2d** - Performance Metrics Dashboard
4. **fig4_performance_3d** - 3D Performance Analysis (Age × Risk × Accuracy)
5. **fig5_risk_tier_distribution** - Risk Tier Distribution (R1-R5)
6. **fig6_xai_methods_comparison** - XAI Methods Comparison (SHAP, NMF, Counterfactuals)
7. **fig7_decision_time_analysis** - Decision Time Performance

### Framework Component Diagrams (3 figures)

Run `python framework_diagrams.py` to generate:

8. **fig8_dras5_state_machine** - 5-State Decision Machine with Transitions
9. **fig9_orasr_routing_diagram** - Safety Routing and Care Pathways
10. **fig10_titrate_decision_tree** - TiTrATE Temporal & Symptomatic Decision Logic

## 🚀 Quick Start

```bash
# Generate all basic visualizations (7 figures)
python examples/trix_visualizations.py

# Generate framework diagrams (3 figures)
python examples/framework_diagrams.py

# Or generate all at once
python examples/trix_visualizations.py && python examples/framework_diagrams.py
```

## 📁 Output

All figures are saved in `outputs/figures/` in two formats:
- **PNG** (600 DPI) - for presentations and web
- **PDF** (vector) - for publications and print

## 🎨 Figure Specifications

- **Resolution:** 600 DPI (publication-ready)
- **Color Palette:** Colorblind-friendly (Okabe-Ito palette)
- **Font:** Arial, 10pt base size
- **Format:** Both raster (PNG) and vector (PDF)
- **Style:** Nature/IEEE/BMJ journal-compliant

## 📋 Dependencies

```bash
pip install numpy matplotlib seaborn
```

## 🔧 Customization

To customize figures, edit the following parameters in the scripts:

```python
# Change DPI
plt.rcParams['savefig.dpi'] = 300  # or 600, 1200

# Change color palette
COLORS = {
    'primary': '#0173B2',    # Blue
    'secondary': '#DE8F05',  # Orange
    'success': '#029E73',    # Green
    'danger': '#CC3311',     # Red
}

# Change figure size
fig, ax = plt.subplots(figsize=(12, 8))  # Width, Height in inches
```

## 📖 Figure Descriptions

### Figure 1: SRGL Flow Diagram
Shows the three sequential gates (G1: Red Flags, G2: Risk Factors, G3: Uncertainty) with decision paths leading to risk tiers R1-R5.

### Figure 2: Framework Architecture
Complete system architecture showing Triage → TiTrATE → XAI flow with SRGL governance layer underneath.

### Figure 3: Performance Dashboard (2D)
Four-panel dashboard: (A) Achieved vs Target metrics, (B) Radar chart, (C) Pass/Fail status, (D) Summary statistics.

### Figure 4: Performance 3D
3D bar chart showing performance across Age Group × Risk Level dimensions.

### Figure 5: Risk Tier Distribution
Pie chart and bar chart showing distribution of 500 test cases across R1-R5 risk tiers.

### Figure 6: XAI Methods Comparison
Four-panel comparison: (A) SHAP importance, (B) NMF factor-disease associations, (C) Counterfactual metrics, (D) Explanation consistency.

### Figure 7: Decision Time Analysis
Histogram of decision times and box plots by risk tier, demonstrating real-time performance (<100ms).

### Figure 8: DRAS-5 State Machine
State diagram with 5 states (S1-S5) showing transitions based on screening results. Includes state transition table.

### Figure 9: ORASR Routing
Safety routing diagram showing Reasoning Module → Safety Checkpoint → Action Routing → Care Pathways with audit trail.

### Figure 10: TiTrATE Decision Tree
Decision tree showing temporal classification logic (Onset → Duration → Symptoms → Diagnosis).

## 🎯 Usage in Papers

### For Manuscript
- Use **PDF format** for main figures (vector graphics scale perfectly)
- Reference figures in text: "as shown in Figure 1"
- Include figure captions in manuscript

### For Presentations
- Use **PNG format** for slides (raster better for projected display)
- High DPI (600) ensures clarity on large screens
- Consider simplifying complex figures for slides

### For Posters
- Use **PDF format** (will be printed at high resolution)
- All figures tested at poster size (A0, A1)

## 📄 Citation

If you use these visualizations in your research, please cite:

```bibtex
@software{trix2026,
  author = {Tritham, Chatchai},
  title = {TRI-X: Triage-TiTrATE-XAI Framework for Explainable Emergency Triage},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/ChatchaiTritham/TRI-X}
}
```

## 📧 Contact

**Questions or customization requests?**

Chatchai Tritham
Email: chatchait66@nu.ac.th
GitHub: [@ChatchaiTritham](https://github.com/ChatchaiTritham)

---

**Last Updated:** 2026-01-28
