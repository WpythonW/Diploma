from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from common.filesystem import ensure_dir
from common.plotting import configure_plotting
from config import EXPERIMENT_SHEETS, OUTPUT_DIR

CONTEXT_LABELS = {
    "formal_logic": "formal_logic",
    "concrete_facts": "concrete_facts",
    "familiar_social_contracts": "familiar_social_contracts",
    "unfamiliar_fantasy_social_contracts": "unfamiliar_fantasy_social_contracts",
}


def load_dataset(output_dir: Path) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []

    for context_key in EXPERIMENT_SHEETS:
        metrics_path = output_dir / context_key / "metrics.csv"
        if not metrics_path.exists():
            continue
        df = pd.read_csv(metrics_path)
        context_label = CONTEXT_LABELS.get(context_key, context_key)
        parts.append(df.assign(context=context_label))

    if not parts:
        raise FileNotFoundError(
            f"No local metrics.csv files found in {output_dir}. "
            "Run run_experiments.py first."
        )

    return pd.concat(parts, ignore_index=True)


def save_barplot(
    df: pd.DataFrame,
    metric: str,
    title: str,
    filename: str,
    output_dir: Path,
    palette: str,
    higher_is_better: bool | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    data = df.copy()
    data[metric] = data[metric] * 100
    sns.barplot(data=data, x="model", y=metric, hue="context", ax=ax, palette=palette)

    suffix = ""
    if higher_is_better is True:
        suffix = " (HIGHER IS BETTER)"
    elif higher_is_better is False:
        suffix = " (LOWER IS BETTER)"

    ax.set_xlabel("Model", fontweight="bold")
    ax.set_ylabel(f"{metric} (%)", fontweight="bold")
    ax.set_title(f"{title}{suffix}", fontweight="bold", fontsize=14)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_dir / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_heatmap(df: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    metrics = ["EMA", "MBI", "CBR"]
    heatmap_data = df.groupby("model")[metrics].mean() * 100

    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".1f",
        cmap="RdYlGn_r",
        linewidths=0.5,
        cbar_kws={"label": "Value (%)"},
        ax=ax,
        vmin=0,
        vmax=100,
    )
    ax.set_title("All Metrics Heatmap (Average Across Contexts)", fontweight="bold", fontsize=14)
    ax.set_xlabel("Metric", fontweight="bold")
    ax.set_ylabel("Model", fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_dir / "graph7_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_radar(df: pd.DataFrame, output_dir: Path) -> None:
    from math import pi

    categories = ["EMA", "MBI", "CBR"]
    concrete = df[df["context"] == "concrete_facts"].copy()
    if concrete.empty:
        return

    angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": "polar"})
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]

    for idx, model in enumerate(concrete["model"].unique()):
        values = (concrete[concrete["model"] == model][categories].values[0] * 100).tolist()
        values += values[:1]
        color = colors[idx % len(colors)]
        ax.plot(angles, values, "o-", linewidth=2, label=model, color=color)
        ax.fill(angles, values, alpha=0.15, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_title("Bias Profile (concrete_facts)\\nCloser to center = Better", fontweight="bold", fontsize=14)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    plt.savefig(output_dir / "graph8_radar.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_small_multiples(df: pd.DataFrame, output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("All Metrics Overview (Average Across Contexts)", fontsize=16, fontweight="bold")

    metrics_info = [
        ("EMA", "HIGHER IS BETTER", "Greens"),
        ("MBI", "LOWER IS BETTER", "Reds"),
        ("CBR", "LOWER IS BETTER", "Oranges"),
    ]

    for idx, (metric, note, palette) in enumerate(metrics_info):
        ax = axes[idx]
        avg = df.groupby("model")[metric].mean().reset_index()
        avg[metric] *= 100

        sns.barplot(data=avg, x="model", y=metric, hue="model", ax=ax, palette=palette, legend=False)
        ax.set_title(f"{metric}\\n{note}", fontweight="bold", fontsize=11)
        ax.set_xlabel("")
        ax.set_ylabel(f"{metric} (%)", fontweight="bold")
        ax.tick_params(axis="x", rotation=45)
        ax.set_ylim(0, avg[metric].max() * 1.15)

        for patch in ax.patches:
            ax.text(
                patch.get_x() + patch.get_width() / 2,
                patch.get_height(),
                f"{patch.get_height():.1f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    plt.tight_layout()
    plt.savefig(output_dir / "graph9_small_multiples.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_context_effects(df: pd.DataFrame, output_dir: Path) -> None:
    rows = []
    for model in df["model"].unique():
        model_df = df[df["model"] == model]
        required = {
            "concrete_facts",
            "familiar_social_contracts",
            "unfamiliar_fantasy_social_contracts",
        }
        if required.issubset(set(model_df["context"])):
            concrete = model_df[model_df["context"] == "concrete_facts"]["EMA"].iloc[0] * 100
            familiar = model_df[model_df["context"] == "familiar_social_contracts"]["EMA"].iloc[0] * 100
            unfamiliar = (
                model_df[model_df["context"] == "unfamiliar_fantasy_social_contracts"]["EMA"].iloc[0] * 100
            )
            rows.extend(
                [
                    {
                        "model": model,
                        "Effect": "tfe_familiar_minus_concrete",
                        "value": familiar - concrete,
                    },
                    {
                        "model": model,
                        "Effect": "das_unfamiliar_minus_concrete",
                        "value": unfamiliar - concrete,
                    },
                ]
            )

    if not rows:
        return

    effects = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=effects, x="model", y="value", hue="Effect", ax=ax, palette="Set1")
    ax.axhline(0, color="black", linewidth=1.5)
    ax.set_xlabel("Model", fontweight="bold")
    ax.set_ylabel("Effect Size (% points)", fontweight="bold")
    ax.set_title("Contextual Effects (Positive = Human-like)", fontweight="bold", fontsize=14)
    ax.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_dir / "graph10_contextual_effects.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_overview(df: pd.DataFrame, output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(24, 7))
    fig.suptitle("All Metrics Overview (Average Across Contexts)", fontsize=32, fontweight="bold")

    metrics_info = [
        ("EMA", "HIGHER IS BETTER", "Greens"),
        ("MBI", "LOWER IS BETTER", "Reds"),
        ("CBR", "LOWER IS BETTER", "Oranges"),
    ]

    for idx, (metric, note, palette) in enumerate(metrics_info):
        ax = axes[idx]
        avg = df.groupby("model")[metric].mean().reset_index()
        avg[metric] *= 100

        sns.barplot(data=avg, x="model", y=metric, hue="model", ax=ax, palette=palette, legend=False)
        ax.set_title(f"{metric}\\n{note}", fontweight="bold", fontsize=24, pad=20)
        ax.set_xlabel("")
        ax.set_ylabel(f"{metric} (%)", fontweight="bold", fontsize=22)
        ax.tick_params(axis="x", rotation=35, labelsize=18)
        ax.tick_params(axis="y", labelsize=20)
        ax.set_ylim(0, avg[metric].max() * 1.15)

        for label in ax.get_xticklabels():
            label.set_fontweight("bold")

        for patch in ax.patches:
            ax.text(
                patch.get_x() + patch.get_width() / 2,
                patch.get_height(),
                f"{patch.get_height():.1f}",
                ha="center",
                va="bottom",
                fontsize=18,
                fontweight="bold",
            )

    plt.tight_layout()
    plt.savefig(
        output_dir / "wason_overview.jpg",
        dpi=300,
        bbox_inches="tight",
        format="jpg",
        pil_kwargs={"quality": 95},
    )
    plt.close(fig)


def build_graphs(output_dir: Path) -> None:
    ensure_dir(output_dir)
    configure_plotting()

    df = load_dataset(output_dir)

    save_barplot(df, "EMA", "EMA by Context", "graph1_ema.png", output_dir, "Set2", True)
    save_barplot(df, "MBI", "MBI by Context", "graph2_mbi.png", output_dir, "Reds", False)
    save_barplot(df, "CBR", "CBR by Context", "graph3_cbr.png", output_dir, "Oranges", False)

    plot_heatmap(df, output_dir)
    plot_radar(df, output_dir)
    plot_small_multiples(df, output_dir)
    plot_context_effects(df, output_dir)
    plot_overview(df, output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Wason Selection Task graphs from local metrics")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory with experiment folders and generated images",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_graphs(output_dir=args.output_dir)
    print(f"Generated Wason Selection Task graphs in: {args.output_dir}")


if __name__ == "__main__":
    main()
