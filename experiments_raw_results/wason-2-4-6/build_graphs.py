from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from common.filesystem import ensure_dir
from common.plotting import configure_plotting
from config import OUTPUT_DIR


def add_labels(df: pd.DataFrame) -> pd.DataFrame:
    labeled = df.copy()
    if "prompt_style" in labeled.columns:
        prompt_style = labeled["prompt_style"].astype(str)
    else:
        prompt_style = pd.Series("baseline", index=labeled.index)
    labeled["label"] = labeled["model"] + "_" + prompt_style + "_" + labeled["reasoning"]
    return labeled


def plot_246_overview(metrics: pd.DataFrame, per_turn: pd.DataFrame, output_dir: Path) -> None:
    metrics = add_labels(metrics)
    per_turn = add_labels(per_turn)

    labels = metrics["label"].tolist()
    x = np.arange(len(labels))
    width = 0.35
    colors = plt.cm.tab10(np.linspace(0, 1, len(labels)))

    fig = plt.figure(figsize=(28, 16))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3, top=0.93)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.bar(x - width / 2, metrics["success_rate"] * 100, width, label="Success Rate", color="#2ecc71")
    ax1.bar(x + width / 2, metrics["mean_auc_iou"] * 100, width, label="Mean AUC IoU", color="#3498db")
    ax1.set_title("Outcome Metrics", fontweight="bold")
    ax1.set_ylabel("Score (%)", fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=25, ha="right")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.bar(
        x - width / 2,
        metrics["confirming_test_rate"] * 100,
        width,
        label="Confirming Test Rate",
        color="#27ae60",
    )
    ax2.bar(
        x + width / 2,
        metrics["hypothesis_change_rate"].fillna(0) * 100,
        width,
        label="Hypothesis Change Rate",
        color="#e67e22",
    )
    ax2.set_title("Process Metrics", fontweight="bold")
    ax2.set_ylabel("Rate (%)", fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=25, ha="right")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)

    ax3 = fig.add_subplot(gs[1, 0])
    for label, color in zip(labels, colors):
        subset = per_turn[per_turn["label"] == label]
        ax3.plot(subset["turn"], subset["mean_iou"], marker="o", linewidth=2, label=label, color=color)
    ax3.set_title("IoU Learning Curve", fontweight="bold")
    ax3.set_xlabel("Turn", fontweight="bold")
    ax3.set_ylabel("Mean IoU", fontweight="bold")
    ax3.grid(True, alpha=0.3)
    ax3.legend()

    ax4 = fig.add_subplot(gs[1, 1])
    heatmap_data = metrics[
        ["label", "success_rate", "mean_auc_iou", "confirming_test_rate", "hypothesis_change_rate"]
    ].copy()
    heatmap_data["hypothesis_change_rate"] = heatmap_data["hypothesis_change_rate"].fillna(0)
    heatmap_data = heatmap_data.set_index("label")
    heatmap_data.columns = ["Success", "AUC IoU", "Confirming", "Hypothesis Change"]
    sns.heatmap(
        heatmap_data.T,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        center=0.5,
        linewidths=1,
        cbar_kws={"label": "Score"},
        ax=ax4,
    )
    ax4.set_title("Four-Metric Overview", fontweight="bold")
    ax4.set_xticklabels(ax4.get_xticklabels(), rotation=25, ha="right")

    fig.suptitle("2-4-6 Rule Discovery", fontweight="bold", fontsize=18)
    plt.savefig(output_dir / "graph_246_overview.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_246_compact(metrics: pd.DataFrame, output_dir: Path) -> None:
    metrics = add_labels(metrics)
    labels = metrics["label"].tolist()
    x = np.arange(len(labels))
    width = 0.2

    fig, ax = plt.subplots(figsize=(18, 10))
    ax.bar(x - 1.5 * width, metrics["success_rate"] * 100, width, label="Success", color="#2ecc71")
    ax.bar(x - 0.5 * width, metrics["mean_auc_iou"] * 100, width, label="AUC IoU", color="#3498db")
    ax.bar(
        x + 0.5 * width,
        metrics["confirming_test_rate"] * 100,
        width,
        label="Confirming",
        color="#27ae60",
    )
    ax.bar(
        x + 1.5 * width,
        metrics["hypothesis_change_rate"].fillna(0) * 100,
        width,
        label="Hypothesis Change",
        color="#e67e22",
    )
    ax.set_ylabel("Score (%)", fontweight="bold")
    ax.set_title("2-4-6: Core Metrics", fontweight="bold", fontsize=22)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "graph_246_compact.png", dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / "graph_246_compact.jpg", dpi=300, bbox_inches="tight")
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build 2-4-6 Rule graphs")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dir(args.output_dir)
    configure_plotting()

    metrics_path = args.output_dir / "metrics_246.csv"
    per_turn_path = args.output_dir / "per_turn_246.csv"
    if not metrics_path.exists() or not per_turn_path.exists():
        raise FileNotFoundError("Run compute_metrics.py before build_graphs.py")

    metrics = pd.read_csv(metrics_path)
    per_turn = pd.read_csv(per_turn_path)

    plot_246_overview(metrics, per_turn, args.output_dir)
    plot_246_compact(metrics, args.output_dir)
    print(f"Generated 2-4-6 graphs in: {args.output_dir}")


if __name__ == "__main__":
    main()
