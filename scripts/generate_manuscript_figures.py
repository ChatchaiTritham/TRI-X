"""Generate curated manuscript figures for TRI-X.

The broad ``outputs/figures`` directory contains complete demo exports. This
script promotes a compact, article-ready subset into ``figures/manuscript`` and
splits the dense performance dashboard into readable panels.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "figures" / "manuscript"
DEFAULT_MANIFEST = ROOT / "FIGURE_MANIFEST.csv"
DPI = 600

METRICS = {
    "Critical alert\ndetection": 98.0,
    "Safety boundary\nviolations": 0.0,
    "Guideline\nalignment": 100.0,
    "TiTrATE\ncompliance": 96.5,
    "ESI triage\naccuracy": 95.2,
    "Red-flag\ndetection": 100.0,
    "Explanation\nconsistency": 92.0,
}

TARGETS = {
    "Critical alert\ndetection": 95.0,
    "Safety boundary\nviolations": 0.0,
    "Guideline\nalignment": 95.0,
    "TiTrATE\ncompliance": 90.0,
    "ESI triage\naccuracy": 90.0,
    "Red-flag\ndetection": 95.0,
    "Explanation\nconsistency": 85.0,
}

COLORS = {
    "safe": "#2ca25f",
    "monitor": "#fdd049",
    "alert": "#fdae61",
    "critical": "#de2d26",
    "emergency": "#54278f",
    "blue": "#2b6cb0",
    "orange": "#dd6b20",
    "gray": "#4a5568",
}


def configure_plotting() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": DPI,
            "savefig.dpi": DPI,
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "axes.titleweight": "bold",
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.linewidth": 0.8,
            "grid.linewidth": 0.4,
            "grid.alpha": 0.25,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> tuple[Path, Path]:
    png_path = output_dir / f"{stem}.png"
    pdf_path = output_dir / f"{stem}.pdf"
    fig.savefig(png_path, dpi=DPI, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def copy_pair(source_stem: str, output_dir: Path, target_stem: str) -> tuple[Path, Path]:
    source_dir = ROOT / "outputs" / "figures"
    png_source = source_dir / f"{source_stem}.png"
    pdf_source = source_dir / f"{source_stem}.pdf"
    png_target = output_dir / f"{target_stem}.png"
    pdf_target = output_dir / f"{target_stem}.pdf"
    shutil.copy2(png_source, png_target)
    shutil.copy2(pdf_source, pdf_target)
    return png_target, pdf_target


def figure1_architecture(output_dir: Path) -> dict[str, str]:
    png_path, pdf_path = copy_pair("fig2_framework_architecture", output_dir, "fig1_framework_architecture")
    return {
        "figure_id": "TRIX-F1",
        "role": "manuscript",
        "png": str(png_path.relative_to(ROOT)),
        "pdf": str(pdf_path.relative_to(ROOT)),
        "source_script": "scripts/generate_manuscript_figures.py",
        "source_data": "outputs/figures/fig2_framework_architecture.png; outputs/figures/fig2_framework_architecture.pdf",
        "caption": "TRI-X framework architecture linking triage, TiTrATE reasoning, SRGL governance, and XAI output.",
        "article_section": "Framework architecture",
    }


def figure2_performance_bar(output_dir: Path) -> dict[str, str]:
    labels = list(METRICS.keys())
    actual = np.array(list(METRICS.values()))
    target = np.array([TARGETS[label] for label in labels])
    x = np.arange(len(labels))
    width = 0.38

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.bar(x - width / 2, actual, width, label="Achieved", color=COLORS["blue"])
    ax.bar(x + width / 2, target, width, label="Target", color=COLORS["orange"])
    ax.set_ylabel("Performance (%)")
    ax.set_title("A. Achieved vs target TRI-X performance")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylim(0, 110)
    ax.grid(axis="y")
    ax.legend(loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    png_path, pdf_path = save_figure(fig, output_dir, "fig2_performance_targets")
    return {
        "figure_id": "TRIX-F2",
        "role": "manuscript",
        "png": str(png_path.relative_to(ROOT)),
        "pdf": str(pdf_path.relative_to(ROOT)),
        "source_script": "scripts/generate_manuscript_figures.py",
        "source_data": "examples/trix_visualizations.py:create_performance_dashboard_2d",
        "caption": "Focused achieved-versus-target performance panel split from the dense TRI-X dashboard.",
        "article_section": "Performance validation",
    }


def figure3_validation_status(output_dir: Path) -> dict[str, str]:
    labels = list(METRICS.keys())
    passed = [METRICS[label] >= TARGETS[label] for label in labels]
    y = np.arange(len(labels))
    colors = [COLORS["safe"] if ok else COLORS["critical"] for ok in passed]

    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    ax.barh(y, [1] * len(labels), color=colors, edgecolor="#2d3748", linewidth=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xticks([])
    ax.set_xlim(0, 1)
    ax.set_title("B. Validation gate status")
    for index, ok in enumerate(passed):
        ax.text(0.5, index, "PASS" if ok else "REVIEW", va="center", ha="center", color="white", fontweight="bold")
    ax.spines[["top", "right", "bottom", "left"]].set_visible(False)
    fig.tight_layout()

    png_path, pdf_path = save_figure(fig, output_dir, "fig3_validation_gate_status")
    return {
        "figure_id": "TRIX-F3",
        "role": "manuscript",
        "png": str(png_path.relative_to(ROOT)),
        "pdf": str(pdf_path.relative_to(ROOT)),
        "source_script": "scripts/generate_manuscript_figures.py",
        "source_data": "examples/trix_visualizations.py:create_performance_dashboard_2d",
        "caption": "Readable validation-gate status panel replacing the compressed dashboard table.",
        "article_section": "Validation results",
    }


def figure4_risk_distribution(output_dir: Path) -> dict[str, str]:
    png_path, pdf_path = copy_pair("fig5_risk_tier_distribution", output_dir, "fig4_risk_tier_distribution")
    return {
        "figure_id": "TRIX-F4",
        "role": "manuscript",
        "png": str(png_path.relative_to(ROOT)),
        "pdf": str(pdf_path.relative_to(ROOT)),
        "source_script": "scripts/generate_manuscript_figures.py",
        "source_data": "outputs/figures/fig5_risk_tier_distribution.png; outputs/figures/fig5_risk_tier_distribution.pdf",
        "caption": "Risk-tier distribution for the TRI-X validation cohort.",
        "article_section": "Risk stratification",
    }


def write_manifest(rows: list[dict[str, str]], manifest_path: Path) -> None:
    fieldnames = [
        "figure_id",
        "role",
        "png",
        "pdf",
        "source_script",
        "source_data",
        "caption",
        "article_section",
        "generated_at",
        "dpi",
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
    sheet = Image.new("RGB", (cols * 540, rows * 405), "white")
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % cols) * 540, (index // cols) * 405))
    sheet_path = output_dir / "visual_qa_contact_sheet.png"
    sheet.save(sheet_path)
    return sheet_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate curated TRI-X manuscript figures")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    configure_plotting()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        figure1_architecture(args.output_dir),
        figure2_performance_bar(args.output_dir),
        figure3_validation_status(args.output_dir),
        figure4_risk_distribution(args.output_dir),
    ]
    write_manifest(rows, args.manifest)
    sheet_path = make_contact_sheet(args.output_dir)

    print(f"Generated {len(rows)} curated figures in {args.output_dir}")
    print(f"Wrote manifest: {args.manifest}")
    print(f"Wrote visual QA contact sheet: {sheet_path}")


if __name__ == "__main__":
    main()
