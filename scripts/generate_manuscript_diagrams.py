"""Draw the four TRI-X manuscript diagrams at the journal text-block width.

The diagrams that shipped with the manuscript were 378-492 pt wide and were
placed in a 372 pt Springer text block at 0.98\\linewidth, so they were shrunk
and their labels landed at 5.5-7.7 pt. They also had no generator in this
repository, which left the manuscript's figures untraceable to the release.

These are conceptual diagrams: no results are plotted, so nothing here reads
from results/. The wording of every box is carried over unchanged from the
figures they replace -- this is a typographic and provenance fix, not a change
of claim.

    python scripts/generate_manuscript_diagrams.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "figures" / "manuscript"

TEXT_PT = 372.0                 # \the\textwidth of the Springer sn-jnl layout
W_IN = TEXT_PT / 72.0
BODY_PT = 8.0
TITLE_PT = 8.5

BLUE = "#0072B2"
GREEN = "#009E73"
ORANGE = "#D55E00"
GREY = "#4D4D4D"
INK = "#1A1A1A"

# layout units: 100 across the text block, so 1 unit = 3.72 pt
XMAX = 100.0
ROW_GAP = 5.4
LINE_H = 4.6
PAD = 3.0


def row_height(nlines: int) -> float:
    return PAD * 2 + nlines * LINE_H


def chain(stem: str, rows, footers=()):
    """rows: (lines, kind) where kind is 'head', 'step' or 'result'."""
    heights = [row_height(len(lines)) for lines, _ in rows]
    total = sum(heights) + ROW_GAP * (len(rows) - 1)
    foot_h = row_height(2) + 6.0 if footers else 0.0
    ymax = total + foot_h + 2.0

    fig, ax = plt.subplots(figsize=(W_IN, W_IN * ymax / XMAX))
    ax.set_xlim(0, XMAX)
    ax.set_ylim(0, ymax)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    style = {
        "head":   dict(face="#DCE9F5", edge=BLUE, lw=1.0, weight="bold", colour=BLUE),
        "step":   dict(face="#FFFFFF", edge=GREY, lw=0.8, weight="normal", colour=INK),
        "result": dict(face="#D9EFE8", edge=GREEN, lw=1.4, weight="bold", colour=GREEN),
    }

    y = ymax - 1.0
    centres = []
    for (lines, kind), h in zip(rows, heights):
        st = style[kind]
        y0 = y - h
        ax.add_patch(FancyBboxPatch((6, y0), XMAX - 12, h,
                                    boxstyle="round,pad=0,rounding_size=1.4",
                                    facecolor=st["face"], edgecolor=st["edge"],
                                    linewidth=st["lw"], zorder=3))
        for i, ln in enumerate(lines):
            first = i == 0
            ax.text(XMAX / 2, y0 + h - PAD - LINE_H * (i + 0.5) + LINE_H * 0.5, ln,
                    ha="center", va="center",
                    fontsize=TITLE_PT if (first and kind != "step") else BODY_PT,
                    fontweight=st["weight"] if first else ("bold" if kind == "result" else "normal"),
                    color=st["colour"] if first else INK,
                    style="italic" if ln.startswith("Decision control") else "normal",
                    zorder=4)
        centres.append((y0, y))
        y = y0 - ROW_GAP

    for (y0, _), (_, y1) in zip(centres[:-1], centres[1:]):
        ax.add_patch(FancyArrowPatch((XMAX / 2, y0), (XMAX / 2, y1), arrowstyle="-|>",
                                     mutation_scale=8, linewidth=1.0, color=GREY, zorder=2))

    if footers:
        fh = row_height(2)
        fw = (XMAX - 12 - 6) / 2
        for i, lines in enumerate(footers):
            x = 6 + i * (fw + 6)
            ax.add_patch(FancyBboxPatch((x, y - fh + ROW_GAP - 2.0), fw, fh,
                                        boxstyle="round,pad=0,rounding_size=1.2",
                                        facecolor="#FFFFFF", edgecolor=ORANGE,
                                        linewidth=0.8, linestyle=(0, (3, 2)), zorder=3))
            for j, ln in enumerate(lines):
                ax.text(x + fw / 2, y - fh + ROW_GAP - 2.0 + fh - PAD - LINE_H * (j + 0.5) + LINE_H * 0.5,
                        ln, ha="center", va="center", fontsize=BODY_PT, color=INK, zorder=4)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUTDIR / f"{stem}.{ext}", dpi=300, facecolor="white")
    plt.close(fig)
    print("  wrote", (OUTDIR / f"{stem}.pdf").relative_to(ROOT))


def main():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": BODY_PT,
        "text.color": INK,
        "pdf.fonttype": 42,
        "savefig.facecolor": "white",
    })

    chain("fig1_framework_overview", [
        (["Specification of uncertain clinical inputs",
          "(symptoms, context, missingness model)"], "head"),
        (["Uncertainty profile u(x)",
          "(information / diagnostic overlap / policy)",
          "Decision control signal"], "step"),
        (["Triage-first safety gate + TiTrATE logic",
          "(rule-based clinical reasoning)"], "step"),
        (["Decision-behaviour groups (G1–G5)",
          "Care pathways + rationale",
          "Screening and routing, not diagnosis"], "result"),
    ], footers=[["XAI-by-design artefacts", "(traceability, auditability)"],
                ["Governance and monitoring", "(safety metrics, regression tests, audits)"]])

    chain("fig2_uncertainty_first", [
        (["Uncertainty-first decision framing (screening / routing)"], "head"),
        (["Symptom report + context", "(missing / ambiguous / conflicting)"], "step"),
        (["Uncertainty profiling u(x)",
          "(information / diagnostic overlap / policy)",
          "Decision control signal"], "step"),
        (["Triage safety gate", "(red flags / unstable vitals)"], "step"),
        (["TiTrATE patterning", "(timing / triggers / targeted exam)"], "step"),
        (["Routing decision groups (G1–G5)",
          "+ care pathway + rationale",
          "Traceable and auditable, not diagnosis"], "result"),
    ], footers=[["XAI artefacts", "(rule path, uncertainty flags, explanations, logs)"],
                ["Governance and monitoring", "(safety metrics, audits, regression tests)"]])

    chain("fig3_screening_logic", [
        (["Screening logic to care pathways (no diagnosis inference)"], "head"),
        (["Uncertain symptom patterns and context"], "step"),
        (["Risk screening u(x)", "(red flags / unstable vitals)"], "step"),
        (["TiTrATE-based routing", "(timing / triggers / targeted examination)"], "step"),
        (["Care pathway outputs (G1–G5)",
          "Emergency / observation / low-acuity / self-care"], "result"),
    ], footers=[["Rationale and traceability", "(rule paths, uncertainty flags, logs)"],
                ["Governance and service management", "(metrics, audits, policy control)"]])

    chain("fig4_reproducibility_pipeline", [
        (["Reproducibility and open-source research workflow"], "head"),
        (["Synthetic data generation", "(controlled uncertainty, Python modules)"], "step"),
        (["Deterministic logic execution", "(TRI-X core inference)"], "step"),
        (["XAI analysis", "(SHAP / NMF / counterfactual / trace)"], "step"),
        (["Safety-oriented evaluation", "(coverage–risk, stability, harm checks)"], "step"),
        (["Regression tests and versioned artefacts",
          "Prevent unsafe drift, ensure reproducibility"], "result"),
    ])

    print("four diagrams at %.0f pt, %.1f pt floor" % (TEXT_PT, BODY_PT))


if __name__ == "__main__":
    main()
