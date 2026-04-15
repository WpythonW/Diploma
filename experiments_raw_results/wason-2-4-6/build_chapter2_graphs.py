"""
Generate 5 non-overlapping figures for Chapter 2, Experiment 3 (2-4-6 task).

Figure 1: IOU learning curves — baseline vs adaptive (aggregated across non-reasoning models)
Figure 2: CTR dynamics by turn — selected models (baseline vs adaptive)
Figure 3: Success Rate by rule category (heatmap)
Figure 4: SR vs CTR scatter — all models, reasoning highlighted
Figure 5: Reasoning vs non-reasoning comparison (grouped bar, 4 metrics)
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MODEL_SHORT = {
    "anthropic__claude-sonnet-4.6": "Claude Sonnet 4.6",
    "deepseek__deepseek-v3.2": "DeepSeek v3.2",
    "google__gemma-3-12b-it": "Gemma 3 12B",
    "google__gemma-3-27b-it": "Gemma 3 27B",
    "openai__gpt-5.2": "GPT-5.2",
    "qwen__qwen3-next-80b-a3b-instruct": "Qwen3-Next 80B",
    "qwen__qwen3.5-397b-a17b": "Qwen3.5 397B",
    "x-ai__grok-4.1-fast": "Grok 4.1 Fast",
    "z-ai__glm-4.7-flash": "GLM 4.7 Flash",
}

COLOR_PALETTE = sns.color_palette("tab10", 10)


def short_name(model: str) -> str:
    return MODEL_SHORT.get(model, model)


# ---------------------------------------------------------------------------
# Figure 1: IOU learning curves — baseline vs adaptive (aggregated)
# ---------------------------------------------------------------------------

def plot_iou_curves_baseline_vs_adaptive(
    per_turn_base: pd.DataFrame,
    per_turn_adapt: pd.DataFrame,
    out: Path,
) -> None:
    """Average IOU per turn across all non-reasoning models, two lines."""
    fig, ax = plt.subplots(figsize=(9, 5.5))

    # Aggregate: mean IOU per turn across models
    base_agg = per_turn_base.groupby("turn")["mean_iou"].mean()
    adapt_agg = per_turn_adapt.groupby("turn")["mean_iou"].mean()

    # Also add std bands
    base_std = per_turn_base.groupby("turn")["mean_iou"].std()
    adapt_std = per_turn_adapt.groupby("turn")["mean_iou"].std()

    turns = base_agg.index
    ax.plot(turns, base_agg.values, "o-", linewidth=2.5, markersize=5,
            color="#2980b9", label="Baseline")
    ax.fill_between(turns, base_agg - base_std, base_agg + base_std,
                    color="#2980b9", alpha=0.15)

    ax.plot(turns, adapt_agg.values, "s-", linewidth=2.5, markersize=5,
            color="#27ae60", label="Adaptive")
    ax.fill_between(turns, adapt_agg - adapt_std, adapt_agg + adapt_std,
                    color="#27ae60", alpha=0.15)

    ax.set_xlabel("Turn")
    ax.set_ylabel("Mean IOU")
    ax.set_title("IOU Learning Curves: Baseline vs Adaptive\n(aggregated across 9 non-reasoning models)")
    ax.legend()
    ax.grid(True, alpha=0.25)
    ax.set_xlim(0.5, 19.5)

    plt.tight_layout()
    plt.savefig(out / "fig1_iou_learning_curves.png", dpi=300, bbox_inches="tight")
    plt.savefig(out / "fig1_iou_learning_curves.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] fig1_iou_learning_curves")


# ---------------------------------------------------------------------------
# Figure 2: CTR dynamics by turn — 3 key models, baseline vs adaptive
# ---------------------------------------------------------------------------

def plot_ctr_dynamics(
    per_turn_base: pd.DataFrame,
    per_turn_adapt: pd.DataFrame,
    out: Path,
) -> None:
    """CTR per turn for 3 selected models: Qwen3.5, GPT-5.2, GPT-5.2-reasoning."""
    models = [
        ("qwen__qwen3.5-397b-a17b", "Qwen3.5 397B"),
        ("openai__gpt-5.2", "GPT-5.2"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5), sharey=True)

    colors_base = "#c0392b"
    colors_adapt = "#27ae60"

    for idx, (model_id, label) in enumerate(models):
        ax = axes[idx]
        base_sub = per_turn_base[per_turn_base["model"] == model_id]
        adapt_sub = per_turn_adapt[per_turn_adapt["model"] == model_id]

        if not base_sub.empty:
            ax.plot(base_sub["turn"], base_sub["confirming_test_rate"],
                    "o-", linewidth=2, markersize=4, color=colors_base,
                    label="Baseline")
        if not adapt_sub.empty:
            ax.plot(adapt_sub["turn"], adapt_sub["confirming_test_rate"],
                    "s-", linewidth=2, markersize=4, color=colors_adapt,
                    label="Adaptive")

        ax.set_title(label)
        ax.set_xlabel("Turn")
        ax.set_xlim(0.5, 19.5)
        ax.grid(True, alpha=0.25)
        if idx == 0:
            ax.set_ylabel("Confirming Test Rate")
            ax.legend()

    # Reasoning model on a separate axis since data is in different dirs
    # GPT-5.2 reasoning: baseline/high and adaptive/high
    ax_r = axes[2]
    try:
        base_high_turn = pd.read_csv(OUTPUT_DIR / "baseline/high/per_turn_246.csv")
        adapt_high_turn = pd.read_csv(OUTPUT_DIR / "adaptive/high/per_turn_246.csv")
        base_r = base_high_turn[base_high_turn["model"] == "openai__gpt-5.2"]
        adapt_r = adapt_high_turn[adapt_high_turn["model"] == "openai__gpt-5.2"]
        if not base_r.empty:
            ax_r.plot(base_r["turn"], base_r["confirming_test_rate"],
                      "o-", linewidth=2, markersize=4, color=colors_base,
                      label="Baseline (reasoning)")
        if not adapt_r.empty:
            ax_r.plot(adapt_r["turn"], adapt_r["confirming_test_rate"],
                      "s-", linewidth=2, markersize=4, color=colors_adapt,
                      label="Adaptive (reasoning)")
    except FileNotFoundError:
        pass

    ax_r.set_title("GPT-5.2 (reasoning)")
    ax_r.set_xlabel("Turn")
    ax_r.set_xlim(0.5, 19.5)
    ax_r.grid(True, alpha=0.25)
    ax_r.legend()

    fig.suptitle("Confirming Test Rate Dynamics per Turn", fontweight="bold", fontsize=14)
    plt.tight_layout()
    plt.savefig(out / "fig2_ctr_dynamics.png", dpi=300, bbox_inches="tight")
    plt.savefig(out / "fig2_ctr_dynamics.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] fig2_ctr_dynamics")


# ---------------------------------------------------------------------------
# Figure 3: Success Rate by rule category (heatmap)
# ---------------------------------------------------------------------------

def plot_category_heatmap(cat_df: pd.DataFrame, out: Path) -> None:
    """Heatmap of Success Rate by model × category (adaptive/none condition)."""
    # Filter to adaptive/none
    adapt = cat_df[
        (cat_df["prompt_style"] == "adaptive") &
        (cat_df["reasoning"] == "none")
    ].copy()
    adapt["model_short"] = adapt["model"].apply(short_name)

    pivot = adapt.pivot_table(
        index="model_short", columns="category", values="success_rate"
    )

    # Reorder categories
    cat_order = ["Порядок", "Арифметика", "Паттерн", "Чётность", "Смешанные"]
    pivot = pivot[[c for c in cat_order if c in pivot.columns]]

    # Reorder models by overall SR descending
    sr_totals = adapt.groupby("model_short")["success_rate"].mean().sort_values(ascending=False)
    pivot = pivot.reindex(sr_totals.index)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(
        pivot, annot=True, fmt=".2f", cmap="YlOrRd",
        vmin=0, vmax=0.6, linewidths=0.8,
        cbar_kws={"label": "Success Rate"},
        ax=ax,
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title("Success Rate by Model and Rule Category (Adaptive, non-reasoning)",
                 fontweight="bold", fontsize=13)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right")

    plt.tight_layout()
    plt.savefig(out / "fig3_category_heatmap.png", dpi=300, bbox_inches="tight")
    plt.savefig(out / "fig3_category_heatmap.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] fig3_category_heatmap")


# ---------------------------------------------------------------------------
# Figure 4: SR vs CTR scatter — reasoning highlighted
# ---------------------------------------------------------------------------

def plot_sr_vs_ctr_scatter(metrics_all: pd.DataFrame, out: Path) -> None:
    """Scatter: SR (x) vs CTR (y), size=AUC-IOU, color=reasoning, annotate models."""
    df = metrics_all.copy()
    df["is_reasoning"] = df["reasoning"] == "high"
    df["model_short"] = df["model"].apply(short_name)

    fig, ax = plt.subplots(figsize=(10, 7))

    # Non-reasoning adaptive
    nr = df[(df["reasoning"] == "none") & (df["prompt_style"] == "adaptive")]
    r = df[df["reasoning"] == "high"]

    # Baseline non-reasoning (hollow markers)
    nr_base = df[(df["reasoning"] == "none") & (df["prompt_style"] == "baseline")]
    if not nr_base.empty:
        sc_base = ax.scatter(
            nr_base["success_rate"] * 100,
            nr_base["confirming_test_rate"] * 100,
            s=nr_base["mean_auc_iou"] * 800,
            facecolors="none", edgecolors="#7f8c8d", linewidths=2,
            alpha=0.7, label="Baseline (non-reasoning)",
        )

    # Adaptive non-reasoning (filled)
    if not nr.empty:
        sc_nr = ax.scatter(
            nr["success_rate"] * 100,
            nr["confirming_test_rate"] * 100,
            s=nr["mean_auc_iou"] * 800,
            c=COLOR_PALETTE[:len(nr)], alpha=0.85, edgecolors="white", linewidths=1.5,
            label="Adaptive (non-reasoning)",
        )

    # Reasoning (star markers)
    if not r.empty:
        colors_r = ["#e74c3c", "#e67e22"]  # baseline-high, adaptive-high
        for i, (_, row) in enumerate(r.iterrows()):
            lbl = f"{row['model_short']} ({row['prompt_style']})"
            ax.scatter(
                row["success_rate"] * 100,
                row["confirming_test_rate"] * 100,
                s=row["mean_auc_iou"] * 800,
                marker="*", c=[colors_r[i % len(colors_r)]],
                edgecolors="black", linewidths=1.5, s=400,
                label=lbl,
            )

    # Annotate all points
    for _, row in df.iterrows():
        label = row["model_short"].replace("GPT-5.2", "GPT").replace("Qwen3.5 397B", "Qwen3.5").replace("Qwen3-Next 80B", "Qwen3-Next")
        ax.annotate(
            label,
            (row["success_rate"] * 100, row["confirming_test_rate"] * 100),
            textcoords="offset points", xytext=(8, 5),
            fontsize=8, alpha=0.8,
        )

    ax.set_xlabel("Success Rate (%)")
    ax.set_ylabel("Confirming Test Rate (%)")
    ax.set_title("Success Rate vs Confirming Test Rate\n(bubble size = AUC-IOU)",
                 fontweight="bold", fontsize=13)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(out / "fig4_sr_ctr_scatter.png", dpi=300, bbox_inches="tight")
    plt.savefig(out / "fig4_sr_ctr_scatter.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] fig4_sr_ctr_scatter")


# ---------------------------------------------------------------------------
# Figure 5: Reasoning vs non-reasoning comparison (4 metrics grouped bar)
# ---------------------------------------------------------------------------

def plot_reasoning_comparison(metrics_all: pd.DataFrame, out: Path) -> None:
    """Grouped bar: 4 metrics for non-reasoning best, reasoning baseline, reasoning adaptive."""
    # Pick GPT-5.2 as the model that has all 4 conditions
    gpt = metrics_all[metrics_all["model"] == "openai__gpt-5.2"].copy()

    conditions = [
        ("baseline", "none", "Non-reasoning\nbaseline"),
        ("adaptive", "none", "Non-reasoning\nadaptive"),
        ("baseline", "high", "Reasoning\nbaseline"),
        ("adaptive", "high", "Reasoning\nadaptive"),
    ]

    metrics_list = ["success_rate", "mean_auc_iou", "confirming_test_rate", "hypothesis_change_rate"]
    metric_labels = ["Success Rate", "AUC-IOU", "CTR", "HCR"]

    fig, ax = plt.subplots(figsize=(10, 5.5))

    x = np.arange(len(metric_labels))
    width = 0.18
    colors = ["#95a5a6", "#3498db", "#e74c3c", "#27ae60"]

    for i, (ps, re, label) in enumerate(conditions):
        row = gpt[(gpt["prompt_style"] == ps) & (gpt["reasoning"] == re)]
        if row.empty:
            continue
        vals = [row[m].values[0] * 100 for m in metrics_list]
        ax.bar(x + i * width, vals, width, label=label, color=colors[i])

    ax.set_ylabel("Score (%)", fontweight="bold")
    ax.set_title("GPT-5.2: Reasoning vs Non-Reasoning Across Conditions",
                 fontweight="bold", fontsize=13)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(metric_labels)
    ax.legend()
    ax.grid(axis="y", alpha=0.25)

    # Add reference line at 0
    ax.axhline(y=0, color="black", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(out / "fig5_reasoning_comparison.png", dpi=300, bbox_inches="tight")
    plt.savefig(out / "fig5_reasoning_comparison.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] fig5_reasoning_comparison")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    out = OUTPUT_DIR / "chapter2_figures"
    out.mkdir(parents=True, exist_ok=True)

    # Load data
    per_turn_adapt = pd.read_csv(OUTPUT_DIR / "adaptive/none/per_turn_246.csv")
    per_turn_base = pd.read_csv(OUTPUT_DIR / "baseline/none/per_turn_246.csv")
    metrics_adapt = pd.read_csv(OUTPUT_DIR / "adaptive/none/metrics_246.csv")
    metrics_base = pd.read_csv(OUTPUT_DIR / "baseline/none/metrics_246.csv")
    cat_adapt = pd.read_csv(OUTPUT_DIR / "adaptive/none/metrics_246_by_category.csv")

    # Combine for scatter
    metrics_all = pd.concat([metrics_adapt, metrics_base], ignore_index=True)

    # Also add reasoning conditions
    try:
        base_high = pd.read_csv(OUTPUT_DIR / "baseline/high/metrics_246.csv")
        adapt_high = pd.read_csv(OUTPUT_DIR / "adaptive/high/metrics_246.csv")
        base_high["prompt_style"] = "baseline"
        adapt_high["prompt_style"] = "adaptive"
        metrics_all = pd.concat([metrics_all, base_high, adapt_high], ignore_index=True)
    except FileNotFoundError:
        print("  [WARN] reasoning metrics not found, skipping scatter reasoning points")

    print("Generating Chapter 2 figures...")

    plot_iou_curves_baseline_vs_adaptive(per_turn_base, per_turn_adapt, out)
    plot_ctr_dynamics(per_turn_base, per_turn_adapt, out)
    plot_category_heatmap(cat_adapt, out)
    plot_sr_vs_ctr_scatter(metrics_all, out)
    plot_reasoning_comparison(metrics_all, out)

    print(f"\nAll figures saved to: {out}")


if __name__ == "__main__":
    main()
