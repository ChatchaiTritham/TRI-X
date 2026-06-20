"""Generate EXPLORATORY effectiveness figures for TRI-X from computed results/.

SUPPLEMENTARY — outside the manuscript's scope. The TRI-X (JIIS) paper reports no
quantitative effectiveness; these accuracy/sensitivity/SHAP figures belong to the
exploratory ML layer (see ``experimental/effectiveness/README.md``). Every panel is
derived from ``results/`` produced by ``experimental/effectiveness/run_all.py`` -- no
performance literal is hardcoded here.

Run order:
    python experimental/effectiveness/run_all.py
    python experimental/effectiveness/generate_manuscript_figures.py
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

# Vendor the shared toolkit next to this script so the import works from any cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pubviz import (  # noqa: E402
    apply_pub_style,
    save_fig,
    PALETTE,
    load_results,
    results_dir,
)

# This file lives at <repo>/experimental/effectiveness/, so the repo root is two up.
ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = results_dir(ROOT)
DEFAULT_OUTPUT_DIR = ROOT / "figures" / "manuscript"
DEFAULT_MANIFEST = ROOT / "FIGURE_MANIFEST.csv"
DPI = 300

SOURCE_SCRIPT = "experimental/effectiveness/generate_manuscript_figures.py"

# Semantic series -> Okabe-Ito palette colour (consistent across every figure/repo).
COLORS = {
    "hybrid": PALETTE[0],   # Blue
    "ml": PALETTE[5],       # Sky blue
    "rules": PALETTE[1],    # Vermillion
    "central": PALETTE[1],  # Vermillion (central / dangerous)
    "benign": PALETTE[2],   # Green (benign peripheral)
    "gray": "#666666",
}

# Color-blind-safe redundancy: pair each series colour with a distinct hatch so the
# bar groups are separable in greyscale / for colour-blind readers.
HATCHES = ["//", "..", "xx", "\\\\"]


# Backward-compatible alias (old callers used configure_plotting()).
configure_plotting = apply_pub_style


def require_results() -> None:
    if not (RESULTS_DIR / "manifest.json").exists():
        raise SystemExit(
            "results/ not found. Run 'python experimental/effectiveness/run_all.py' "
            "first to compute the data these figures are built from."
        )


def load_json(name: str) -> dict:
    return load_results(name, ROOT)


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> tuple[Path, Path]:
    """Save via the canonical pubviz save_fig (vector PDF + 300-dpi PNG)."""
    save_fig(fig, stem, output_dir)
    plt.close(fig)
    return output_dir / f"{stem}.png", output_dir / f"{stem}.pdf"


def figure1_accuracy(output_dir: Path) -> dict[str, str]:
    diag = load_json("diagnostic_performance.json")
    labels = ["TRI-X\n(Hybrid)", "Standalone\nML (RF)", "Rule-based"]
    keys = ["hybrid_ensemble", "standalone_ml_rf", "rule_based"]
    accs = [diag[k]["accuracy"] * 100 for k in keys]
    cis = [diag[k]["accuracy_ci95"] for k in keys]
    err = [[a - c[0] * 100 for a, c in zip(accs, cis)],
           [c[1] * 100 - a for a, c in zip(accs, cis)]]
    colors = [COLORS["hybrid"], COLORS["ml"], COLORS["rules"]]

    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    bars = ax.bar(labels, accs, color=colors, yerr=err, capsize=5,
                  edgecolor="#1a202c", linewidth=0.6)
    # Color-blind-safe redundancy: a distinct hatch per bar.
    for bar, hatch in zip(bars, HATCHES):
        bar.set_hatch(hatch)
    for bar, a in zip(bars, accs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                f"{a:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_ylabel("Multiclass diagnostic accuracy (%)")
    ax.set_title(f"Diagnostic accuracy on held-out synthetic test set (n={diag['test_n']})")
    ax.set_ylim(0, 105)
    ax.grid(axis="y", which="both", alpha=0.45)
    ax.minorticks_on()
    ax.tick_params(axis="x", which="minor", bottom=False)
    ax.spines[["top", "right"]].set_visible(False)

    png_path, pdf_path = save_figure(fig, output_dir, "fig1_diagnostic_accuracy")
    return {
        "figure_id": "TRIX-F1",
        "role": "exploratory",
        "png": str(png_path.relative_to(ROOT)),
        "pdf": str(pdf_path.relative_to(ROOT)),
        "source_script": SOURCE_SCRIPT,
        "source_data": "results/diagnostic_performance.json",
        "caption": "Multiclass diagnostic accuracy with bootstrap 95% CIs (synthetic test set). Exploratory; outside manuscript scope.",
        "article_section": "Supplementary (not in manuscript)",
    }


def figure2_critical(output_dir: Path) -> dict[str, str]:
    crit = load_json("critical_scenario.json")
    keys = ["hybrid_ensemble", "standalone_ml_rf", "rule_based"]
    labels = ["TRI-X (Hybrid)", "Standalone ML", "Rule-based"]
    metrics = ["sensitivity", "specificity", "ppv", "npv"]
    metric_labels = ["Sensitivity", "Specificity", "PPV", "NPV"]
    x = np.arange(len(metrics))
    width = 0.26
    colors = [COLORS["hybrid"], COLORS["ml"], COLORS["rules"]]

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    for i, (k, lab) in enumerate(zip(keys, labels)):
        vals = [crit[k][m] * 100 for m in metrics]
        # Per-method hatch + colour = color-blind-safe and greyscale-safe.
        ax.bar(x + (i - 1) * width, vals, width, label=lab, color=colors[i],
               edgecolor="#1a202c", linewidth=0.5, hatch=HATCHES[i])
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels)
    ax.set_ylabel("Score (%)")
    ax.set_ylim(0, 110)
    ax.set_title(
        f"Critical scenario detection: central/dangerous vs benign "
        f"(positives n={crit['central_positive_n']})"
    )
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    ax.grid(axis="y", which="both", alpha=0.45)
    ax.minorticks_on()
    ax.tick_params(axis="x", which="minor", bottom=False)
    ax.spines[["top", "right"]].set_visible(False)

    png_path, pdf_path = save_figure(fig, output_dir, "fig2_critical_scenario")
    return {
        "figure_id": "TRIX-F2",
        "role": "exploratory",
        "png": str(png_path.relative_to(ROOT)),
        "pdf": str(pdf_path.relative_to(ROOT)),
        "source_script": SOURCE_SCRIPT,
        "source_data": "results/critical_scenario.json",
        "caption": "Stroke/TIA detection sensitivity, specificity, PPV and NPV across methods. Exploratory; outside manuscript scope.",
        "article_section": "Supplementary (not in manuscript)",
    }


def figure3_shap(output_dir: Path) -> dict[str, str]:
    expl = load_json("explainability.json")
    top = expl["shap"]["top10"][::-1]
    names = [t[0] for t in top]
    vals = [t[1] for t in top]

    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.barh(names, vals, color=COLORS["hybrid"], edgecolor="#1a202c",
            linewidth=0.5, hatch="//")
    ax.set_xlabel("Mean |SHAP value|")
    ax.set_title("Global feature importance (SHAP, Random Forest)")
    ax.grid(axis="x", which="both", alpha=0.45)
    ax.minorticks_on()
    ax.tick_params(axis="y", which="minor", left=False)
    ax.spines[["top", "right"]].set_visible(False)

    png_path, pdf_path = save_figure(fig, output_dir, "fig3_shap_importance")
    return {
        "figure_id": "TRIX-F3",
        "role": "exploratory",
        "png": str(png_path.relative_to(ROOT)),
        "pdf": str(pdf_path.relative_to(ROOT)),
        "source_script": SOURCE_SCRIPT,
        "source_data": "results/explainability.json",
        "caption": "Top-10 global feature importance from genuine SHAP TreeExplainer attributions. Exploratory; outside manuscript scope.",
        "article_section": "Supplementary (not in manuscript)",
    }


def figure4_cohort(output_dir: Path) -> dict[str, str]:
    rows = list(csv.DictReader((RESULTS_DIR / "cohort_distribution.csv").open(encoding="utf-8")))
    rows = sorted(rows, key=lambda r: int(r["count"]), reverse=True)
    labels = [r["diagnosis"] for r in rows]
    counts = [int(r["count"]) for r in rows]
    colors = [COLORS["central"] if r["group"] == "central_dangerous" else COLORS["benign"] for r in rows]
    total = sum(counts)

    hatches = ["xx" if r["group"] == "central_dangerous" else "//" for r in rows]
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    bars = ax.bar(labels, counts, color=colors, edgecolor="#1a202c", linewidth=0.5)
    for bar, h in zip(bars, hatches):
        bar.set_hatch(h)
    ax.set_ylabel("Synthetic cases (n)")
    ax.set_title(f"Synthetic cohort diagnosis distribution (n={total})")
    ax.tick_params(axis="x", rotation=40)
    for lab in ax.get_xticklabels():
        lab.set_ha("right")
    ax.grid(axis="y", which="both", alpha=0.45)
    ax.minorticks_on()
    ax.tick_params(axis="x", which="minor", bottom=False)
    ax.spines[["top", "right"]].set_visible(False)
    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=COLORS["central"], hatch="xx", edgecolor="#1a202c"),
        plt.Rectangle((0, 0), 1, 1, facecolor=COLORS["benign"], hatch="//", edgecolor="#1a202c"),
    ]
    ax.legend(handles, ["Central / dangerous", "Benign peripheral"], frameon=False)

    png_path, pdf_path = save_figure(fig, output_dir, "fig4_cohort_distribution")
    return {
        "figure_id": "TRIX-F4",
        "role": "data",
        "png": str(png_path.relative_to(ROOT)),
        "pdf": str(pdf_path.relative_to(ROOT)),
        "source_script": SOURCE_SCRIPT,
        "source_data": "results/cohort_distribution.csv",
        "caption": "Diagnosis distribution of the synthetic ED vestibular triage cohort.",
        "article_section": "Methods",
    }


def manuscript_figure_rows() -> list[dict[str, str]]:
    """Provenance rows for the manuscript-scope figures produced by
    examples/trix_visualizations.py (schematic + decision-behaviour). Listed first
    in the manifest because these are the JIIS paper's primary figures.
    """
    viz = "examples/trix_visualizations.py"
    return [
        {
            "figure_id": "TRIX-S1", "role": "schematic",
            "png": "outputs/figures/fig1_srgl_flow_diagram.png",
            "pdf": "outputs/figures/fig1_srgl_flow_diagram.pdf",
            "source_script": viz, "source_data": "(layout only; no numbers)",
            "caption": "SRGL three-gate sequential screening logic flow.",
            "article_section": "Methods",
        },
        {
            "figure_id": "TRIX-S2", "role": "schematic",
            "png": "outputs/figures/fig2_framework_architecture.png",
            "pdf": "outputs/figures/fig2_framework_architecture.pdf",
            "source_script": viz, "source_data": "(layout only; no numbers)",
            "caption": "TRI-X (Triage-TiTrATE-XAI) framework architecture.",
            "article_section": "Methods",
        },
        {
            "figure_id": "TRIX-B1", "role": "behaviour",
            "png": "outputs/figures/fig3_safety_gate_compliance.png",
            "pdf": "outputs/figures/fig3_safety_gate_compliance.pdf",
            "source_script": viz,
            "source_data": "results/framework/safety_gate_compliance.json",
            "caption": "Triage-first safety-gate escalation compliance and benign "
                       "over-escalation (synthetic cohort, seed 42).",
            "article_section": "Results",
        },
        {
            "figure_id": "TRIX-B2", "role": "behaviour",
            "png": "outputs/figures/fig4_missingness_stability.png",
            "pdf": "outputs/figures/fig4_missingness_stability.pdf",
            "source_script": viz,
            "source_data": "results/framework/missingness_stability.json",
            "caption": "Gate-routing stability under dropped red-flag fields with "
                       "zero unsafe de-escalations (seed 42).",
            "article_section": "Results",
        },
    ]


def write_manifest(rows: list[dict[str, str]], manifest_path: Path) -> None:
    fieldnames = [
        "figure_id", "role", "png", "pdf", "source_script", "source_data",
        "caption", "article_section", "generated_at", "dpi",
    ]
    generated_at = datetime.now().isoformat(timespec="seconds")
    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "generated_at": generated_at, "dpi": str(DPI)})


def make_contact_sheet(output_dir: Path) -> Path:
    pngs = sorted(p for p in output_dir.glob("*.png") if not p.name.startswith("visual_qa"))
    thumbs = []
    for path in pngs:
        with Image.open(path) as image:
            thumb = image.convert("RGB")
            original = thumb.size
            thumb.thumbnail((500, 330), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (540, 405), "white")
            canvas.paste(thumb, ((540 - thumb.width) // 2, 42))
            draw = ImageDraw.Draw(canvas)
            draw.text((8, 8), path.name, fill="black")
            draw.text((8, 378), f"{original[0]}x{original[1]}", fill="black")
            thumbs.append(canvas)
    cols = 2
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 540, max(rows, 1) * 405), "white")
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % cols) * 540, (index // cols) * 405))
    sheet_path = output_dir / "visual_qa_contact_sheet.png"
    sheet.save(sheet_path)
    return sheet_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate exploratory TRI-X figures from results/")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    require_results()
    apply_pub_style()  # shared publication style: serif fonts + Okabe-Ito palette
    args.output_dir.mkdir(parents=True, exist_ok=True)
    exploratory_rows = [
        figure1_accuracy(args.output_dir),
        figure2_critical(args.output_dir),
        figure3_shap(args.output_dir),
        figure4_cohort(args.output_dir),
    ]
    # Manuscript-scope figures (schematic + behaviour) listed first; the supplementary
    # exploratory figures follow. Keeps one authoritative FIGURE_MANIFEST.csv.
    rows = manuscript_figure_rows() + exploratory_rows
    write_manifest(rows, args.manifest)
    sheet_path = make_contact_sheet(args.output_dir)

    print(f"Generated {len(exploratory_rows)} supplementary figures in {args.output_dir}")
    print(f"Wrote manifest ({len(rows)} rows incl. manuscript-scope): {args.manifest}")
    print(f"Wrote visual QA contact sheet: {sheet_path}")


if __name__ == "__main__":
    main()
