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
import json
from datetime import datetime
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

# This file lives at <repo>/experimental/effectiveness/, so the repo root is two up.
ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"
DEFAULT_OUTPUT_DIR = ROOT / "figures" / "manuscript"
DEFAULT_MANIFEST = ROOT / "FIGURE_MANIFEST.csv"
DPI = 300

SOURCE_SCRIPT = "experimental/effectiveness/generate_manuscript_figures.py"

# Canonical Top-Tier figure style (shared across all PhD repos; see
# _management/FIGURE_STYLE.md). Color-blind-safe Okabe-Ito palette, used in order.
PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000"]

# Semantic series -> Okabe-Ito palette colour (consistent across every figure/repo).
COLORS = {
    "hybrid": PALETTE[0],   # Blue
    "ml": PALETTE[5],       # Sky blue
    "rules": PALETTE[1],    # Vermillion
    "central": PALETTE[1],  # Vermillion (central / dangerous)
    "benign": PALETTE[2],   # Green (benign peripheral)
    "gray": "#666666",
}


def apply_pub_style() -> None:
    """Apply the shared publication rcParams + Okabe-Ito cycler. Call once."""
    mpl.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": DPI, "savefig.bbox": "tight",
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
        # Embed fonts as TrueType for camera-ready vector PDFs.
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })


# Backward-compatible alias (old callers used configure_plotting()).
configure_plotting = apply_pub_style


def require_results() -> None:
    if not (RESULTS_DIR / "manifest.json").exists():
        raise SystemExit(
            "results/ not found. Run 'python experimental/effectiveness/run_all.py' "
            "first to compute the data these figures are built from."
        )


def load_json(name: str) -> dict:
    return json.loads((RESULTS_DIR / name).read_text(encoding="utf-8"))


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> tuple[Path, Path]:
    png_path = output_dir / f"{stem}.png"
    pdf_path = output_dir / f"{stem}.pdf"
    fig.savefig(png_path, dpi=DPI, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


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
    for bar, a in zip(bars, accs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                f"{a:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_ylabel("Multiclass diagnostic accuracy (%)")
    ax.set_title(f"Diagnostic accuracy on held-out synthetic test set (n={diag['test_n']})")
    ax.set_ylim(0, 105)
    ax.grid(axis="y")
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
        ax.bar(x + (i - 1) * width, vals, width, label=lab, color=colors[i],
               edgecolor="#1a202c", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels)
    ax.set_ylabel("Score (%)")
    ax.set_ylim(0, 110)
    ax.set_title(
        f"Critical scenario detection: central/dangerous vs benign "
        f"(positives n={crit['central_positive_n']})"
    )
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    ax.grid(axis="y")
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
    ax.barh(names, vals, color=COLORS["hybrid"], edgecolor="#1a202c", linewidth=0.5)
    ax.set_xlabel("Mean |SHAP value|")
    ax.set_title("Global feature importance (SHAP, Random Forest)")
    ax.grid(axis="x")
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

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.bar(labels, counts, color=colors, edgecolor="#1a202c", linewidth=0.5)
    ax.set_ylabel("Synthetic cases (n)")
    ax.set_title(f"Synthetic cohort diagnosis distribution (n={total})")
    ax.tick_params(axis="x", rotation=40)
    for lab in ax.get_xticklabels():
        lab.set_ha("right")
    ax.grid(axis="y")
    ax.spines[["top", "right"]].set_visible(False)
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=COLORS["central"]),
        plt.Rectangle((0, 0), 1, 1, color=COLORS["benign"]),
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
    rows = [
        figure1_accuracy(args.output_dir),
        figure2_critical(args.output_dir),
        figure3_shap(args.output_dir),
        figure4_cohort(args.output_dir),
    ]
    write_manifest(rows, args.manifest)
    sheet_path = make_contact_sheet(args.output_dir)

    print(f"Generated {len(rows)} exploratory figures in {args.output_dir}")
    print(f"Wrote manifest: {args.manifest}")
    print(f"Wrote visual QA contact sheet: {sheet_path}")


if __name__ == "__main__":
    main()
