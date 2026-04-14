#!/usr/bin/env python3
"""Generate publication-quality figures for the Linda conjunction fallacy experiment."""

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

matplotlib.use("Agg")
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8,
    "figure.titlesize": 12,
    "figure.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
})

# ---------------------------------------------------------------------------
# Data sources
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent
OUTPUT_DIR = BASE / "output"

MODEL_META = {
    "anthropic__claude-sonnet-4.6":        {"short": "claude-sonnet-4.6",      "size": None},
    "deepseek__deepseek-v3.2":             {"short": "deepseek-v3.2",          "size": None},
    "google__gemma-3-12b-it":              {"short": "gemma-3-12b-it",         "size": 12},
    "google__gemma-3-27b-it":              {"short": "gemma-3-27b-it",         "size": 27},
    "openai__gpt-5.2":                     {"short": "gpt-5.2",                "size": None},
    "qwen__qwen3-next-80b-a3b-instruct":   {"short": "qwen3-next-80b",         "size": 80},
    "qwen__qwen3.5-397b-a17b":             {"short": "qwen3.5-397b",           "size": 397},
    "x-ai__grok-4.1-fast":                 {"short": "grok-4.1-fast",          "size": None},
    "z-ai__glm-4.7-flash":                 {"short": "glm-4.7-flash",          "size": None},
}

FALLBACK_COLORS = {
    "claude-sonnet-4.6": "#1f77b4",
    "deepseek-v3.2": "#ff7f0e",
    "gemma-3-12b-it":  "#2ca02c",
    "gemma-3-27b-it":  "#1a7a1a",
    "gpt-5.2":         "#d62728",
    "qwen3-next-80b":  "#9467bd",
    "qwen3.5-397b":    "#8c564b",
    "grok-4.1-fast":   "#e377c2",
    "glm-4.7-flash":   "#7f7f7f",
}


def load_summaries() -> pd.DataFrame:
    rows = []
    for folder, meta in MODEL_META.items():
        p = OUTPUT_DIR / folder / "summary.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        short = meta["short"]
        accuracy = d["n11"] / d["n_pairs"] if d["n_pairs"] else 0
        fallacy_rate = d["n21"] / d["n_pairs"] if d["n_pairs"] else 0
        cohen_d = d["paired_t_statistic"] / np.sqrt(d["n_pairs"]) if d["n_pairs"] else 0
        rows.append({
            "short": short,
            "n_pairs": d["n_pairs"],
            "n11": d["n11"],
            "n12": d["n12"],
            "n21": d["n21"],
            "n22": d["n22"],
            "accuracy": accuracy,
            "fallacy_rate": fallacy_rate,
            "delta_bias": d["delta_bias"],
            "mean_bias_correlated": d["mean_bias_correlated"],
            "mean_bias_uncorrelated": d["mean_bias_uncorrelated"],
            "t_statistic": d["paired_t_statistic"],
            "t_pvalue": d["paired_t_pvalue"],
            "mcnemar_p": d["mcnemar_exact_pvalue"],
            "cohen_d": cohen_d,
            "size_billions": meta["size"],
        })
    return pd.DataFrame(rows)


def load_pair_data() -> dict[str, pd.DataFrame]:
    result = {}
    for folder, meta in MODEL_META.items():
        p = OUTPUT_DIR / folder / "pair_results.csv"
        if not p.exists():
            continue
        df = pd.read_csv(p)
        result[meta["short"]] = df
    return result


def load_demographics() -> dict[str, pd.DataFrame]:
    result = {}
    for folder, meta in MODEL_META.items():
        p = OUTPUT_DIR / folder / "demographic_summary.csv"
        if not p.exists():
            continue
        df = pd.read_csv(p)
        result[meta["short"]] = df
    return result


# ---------------------------------------------------------------------------
# Figure 1: Delta bias bar plot (sorted)
# ---------------------------------------------------------------------------
def fig1_delta_bias_bar(df: pd.DataFrame, out: Path):
    sorted_df = df.sort_values("delta_bias", ascending=True).reset_index(drop=True)
    colors = [FALLBACK_COLORS.get(r.short, "#1f77b4") for _, r in sorted_df.iterrows()]

    fig, ax = plt.subplots(figsize=(8, 4.2))
    y_pos = np.arange(len(sorted_df))
    bars = ax.barh(y_pos, sorted_df["delta_bias"], color=colors, edgecolor="white", linewidth=0.5, height=0.65)

    for bar, val in zip(bars, sorted_df["delta_bias"]):
        offset = 0.01
        ha = "left" if val >= 0 else "right"
        # For negative values, place text to the left of the bar
        if val < 0:
            x_pos = bar.get_width() - offset
        else:
            x_pos = bar.get_width() + offset
        ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                f"{val:+.3f}", va="center", ha=ha, fontsize=8, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_df["short"])
    ax.set_xlabel("Delta Bias (correlated $-$ uncorrelated)")
    ax.set_title("Figure 1: Severity of Bias across Models (Delta Bias)", fontweight="bold")
    ax.axvline(x=0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))

    # Push right margin to make room for labels
    max_val = sorted_df["delta_bias"].max()
    ax.set_xlim(left=-0.02, right=max_val + 0.08)

    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ---------------------------------------------------------------------------
# Figure 2: Accuracy vs Delta Bias scatter
# ---------------------------------------------------------------------------
def fig2_accuracy_vs_delta(df: pd.DataFrame, out: Path):
    fig, ax = plt.subplots(figsize=(7, 4.2))

    known_sizes = df[df["size_billions"].notna()]
    unknown_sizes = df[df["size_billions"].isna()]

    for _, r in unknown_sizes.iterrows():
        ax.scatter(r["accuracy"], r["delta_bias"],
                   c=[FALLBACK_COLORS.get(r.short, "#1f77b4")], s=80, zorder=5, edgecolors="black", linewidth=0.7)

    scatter = ax.scatter(known_sizes["accuracy"], known_sizes["delta_bias"],
                         c=known_sizes["size_billions"], cmap="viridis",
                         s=120, zorder=5, edgecolors="black", linewidth=0.7)

    # Place annotations on the LEFT side of points to avoid colorbar overlap
    for _, r in df.iterrows():
        ax.annotate(r.short, (r["accuracy"], r["delta_bias"]),
                    textcoords="offset points", xytext=(-6, 6), fontsize=7, alpha=0.85, ha="right")

    # Place colorbar below the plot to avoid any overlap
    cbar_ax = fig.add_axes([0.15, 0.08, 0.7, 0.02])
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation="horizontal")
    cbar.set_label("Model size (B params, where known)", fontsize=9)

    ax.set_xlabel("Accuracy (1 $-$ fallacy rate)")
    ax.set_ylabel("Delta Bias")
    ax.set_title("Figure 2: Accuracy vs Severity of Bias", fontweight="bold")
    ax.grid(alpha=0.2, linestyle="--")

    # Leave room for bottom colorbar
    fig.subplots_adjust(bottom=0.2)

    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ---------------------------------------------------------------------------
# Figure 3: Confidence violin – correlated vs uncorrelated
# ---------------------------------------------------------------------------
def fig3_confidence_violin(pairs: dict[str, pd.DataFrame], summary_df: pd.DataFrame, out: Path):
    top5 = summary_df.nlargest(5, "n21")["short"].tolist()
    if "claude-sonnet-4.6" not in top5:
        top5.append("claude-sonnet-4.6")

    fig, axes = plt.subplots(2, 3, figsize=(10, 5.5))
    axes = axes.flatten()

    for idx, short in enumerate(top5):
        if short not in pairs:
            continue
        df = pairs[short]
        ax = axes[idx]

        corr_conf = df["confidence_correlated"].astype(float)
        uncorr_conf = df["confidence_uncorrelated"].astype(float)

        parts = ax.violinplot([corr_conf, uncorr_conf], positions=[0, 1],
                              showmeans=True, showmedians=True, widths=0.6)
        for pc in parts["bodies"]:
            pc.set_facecolor(FALLBACK_COLORS.get(short, "#1f77b4"))
            pc.set_alpha(0.7)
        parts["cmeans"].set_color("red")
        parts["cmedians"].set_color("white")
        parts["cmedians"].set_linewidth(1.5)

        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Correlated", "Uncorrelated"])
        ax.set_ylabel("Confidence")
        ax.set_title(short, fontsize=9, fontweight="bold")
        ax.set_ylim(0, 105)

    for ax in axes[len(top5):]:
        ax.axis("off")

    fig.suptitle("Figure 3: Confidence Distribution (Correlated vs Uncorrelated)", fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ---------------------------------------------------------------------------
# Figure 4: Fallacy rate by race (grouped bar)
# ---------------------------------------------------------------------------
def fig4_race_fallacy(demog: dict[str, pd.DataFrame], summary_df: pd.DataFrame, out: Path):
    races = ["Asian", "Black", "Hispanic", "White"]
    models_with_race = {s: d for s, d in demog.items() if s in summary_df["short"].values}

    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = np.arange(len(races))
    width = 0.12
    n = min(len(models_with_race), 7)

    selected = summary_df.sort_values("delta_bias").iloc[[0, 2, 4, 6, 7, 8]].index.tolist()
    selected_shorts = summary_df.iloc[selected]["short"].tolist()

    colors_r = plt.cm.RdYlBu_r(np.linspace(0.1, 0.9, n))

    for i, short in enumerate(selected_shorts):
        if short not in models_with_race:
            continue
        rdf = models_with_race[short]
        race_fr = rdf[rdf["group_variable"] == "race"].set_index("group_value")["fallacy_rate_correlated"]
        vals = [race_fr.get(r, 0) for r in races]
        ax.bar(x + i * width, vals, width, label=short, color=colors_r[i], edgecolor="white", linewidth=0.3)

    ax.set_xticks(x + width * (n - 1) / 2)
    ax.set_xticklabels(races)
    ax.set_ylabel("Correlated Fallacy Rate")
    ax.set_title("Figure 4: Fallacy Rate by Race (Selected Models)", fontweight="bold")
    # Place legend outside, above the plot
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=3)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))

    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ---------------------------------------------------------------------------
# Figure 5: Cohen's d forest plot
# ---------------------------------------------------------------------------
def fig5_cohen_d_forest(df: pd.DataFrame, out: Path):
    sorted_df = df.sort_values("cohen_d", ascending=True).reset_index(drop=True)
    colors = [FALLBACK_COLORS.get(r.short, "#1f77b4") for _, r in sorted_df.iterrows()]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    y_pos = np.arange(len(sorted_df))

    ax.barh(y_pos, sorted_df["cohen_d"], color=colors, edgecolor="white", linewidth=0.5, height=0.6)

    # Determine max extent for label placement
    max_d = sorted_df["cohen_d"].abs().max()

    for i, (_, r) in enumerate(sorted_df.iterrows()):
        if r["cohen_d"] >= 0:
            x_pos = r["cohen_d"] + max_d * 0.03
            ha = "left"
        else:
            x_pos = r["cohen_d"] - max_d * 0.03
            ha = "right"
        ax.text(x_pos, i, f"{r['cohen_d']:+.2f}",
                va="center", ha=ha, fontsize=8, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_df["short"])
    ax.set_xlabel("Cohen's d")
    ax.set_title("Figure 5: Effect Sizes (Cohen's d) for Delta Bias", fontweight="bold")
    ax.axvline(x=0, color="black", linewidth=0.8, linestyle="-", alpha=0.5)
    ax.axvline(x=0.2, color="gray", linewidth=0.5, linestyle=":", alpha=0.4)
    ax.axvline(x=0.5, color="gray", linewidth=0.5, linestyle=":", alpha=0.4)
    ax.axvline(x=0.8, color="gray", linewidth=0.5, linestyle=":", alpha=0.4)

    # Extend x-axis to accommodate labels
    xlim_left = min(sorted_df["cohen_d"].min() - max_d * 0.1, -0.05)
    xlim_right = sorted_df["cohen_d"].max() + max_d * 0.15
    ax.set_xlim(xlim_left, xlim_right)

    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ---------------------------------------------------------------------------
# Figure 6: Accuracy by condition (correlated vs uncorrelated)
# ---------------------------------------------------------------------------
def fig6_accuracy_by_condition(df: pd.DataFrame, out: Path):
    """
    Side-by-side bar comparison showing accuracy in correlated vs uncorrelated conditions.
    Demonstrates how narrative coherence affects task difficulty.
    """
    sorted_df = df.sort_values("accuracy", ascending=False).reset_index(drop=True)
    colors = [FALLBACK_COLORS.get(r.short, "#1f77b4") for _, r in sorted_df.iterrows()]

    # Estimate accuracy in each condition from n11, n12, n21, n22
    # Accuracy_correlated ≈ n11 / (n11 + n21) [ignoring n12, n22 which are near zero]
    # Accuracy_uncorrelated ≈ n11 / (n11 + n12) [ignoring n21, n22 which are near zero]
    # Better: use the fallacy_rate relationship
    # fallacy_rate = n21 / n_pairs (error in correlated)
    # accuracy_correlated ≈ (n_pairs - n21) / n_pairs = 1 - fallacy_rate
    # accuracy_uncorrelated ≈ (n11 + n12) / n_pairs ≈ accuracy (overall)

    sorted_df["accuracy_correlated"] = 1.0 - sorted_df["fallacy_rate"]
    sorted_df["accuracy_uncorrelated"] = sorted_df["accuracy"]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    x_pos = np.arange(len(sorted_df))
    width = 0.35

    bars1 = ax.bar(x_pos - width/2, sorted_df["accuracy_correlated"], width,
                   label="Correlated condition", color=[c for c in colors], alpha=0.8, edgecolor="white", linewidth=0.5)
    bars2 = ax.bar(x_pos + width/2, sorted_df["accuracy_uncorrelated"], width,
                   label="Uncorrelated condition", color=[c for c in colors], alpha=0.5, edgecolor="white", linewidth=0.5, hatch="/")

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f"{height:.2f}", ha="center", va="bottom", fontsize=7)

    ax.set_ylabel("Accuracy")
    ax.set_xlabel("Model")
    ax.set_title("Figure 6: Accuracy by Condition (Correlated vs Uncorrelated)", fontweight="bold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(sorted_df["short"], rotation=45, ha="right")
    ax.legend(loc="lower right")
    ax.set_ylim(0, 1.1)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ---------------------------------------------------------------------------
# Figure 7: Error distribution (contingency table composition)
# ---------------------------------------------------------------------------
def fig7_error_distribution(df: pd.DataFrame, out: Path):
    """
    Stacked bar chart showing composition of 2×2 contingency table (n11, n12, n21, n22).
    Visualizes asymmetry: n21 >> n12, and that n22 is always zero.
    """
    sorted_df = df.sort_values("n21", ascending=False).reset_index(drop=True)
    colors = [FALLBACK_COLORS.get(r.short, "#1f77b4") for _, r in sorted_df.iterrows()]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    x_pos = np.arange(len(sorted_df))
    width = 0.6

    # Normalize to show proportions
    n_total = sorted_df["n_pairs"].values
    n11_prop = sorted_df["n11"].values / n_total
    n12_prop = sorted_df["n12"].values / n_total
    n21_prop = sorted_df["n21"].values / n_total
    n22_prop = sorted_df["n22"].values / n_total

    ax.bar(x_pos, n11_prop, width, label="$n_{11}$ (correct both)", color="#2ecc71", alpha=0.8, edgecolor="white", linewidth=0.5)
    ax.bar(x_pos, n12_prop, width, bottom=n11_prop, label="$n_{12}$ (correct only uncorr)", color="#3498db", alpha=0.8, edgecolor="white", linewidth=0.5)
    ax.bar(x_pos, n21_prop, width, bottom=n11_prop+n12_prop, label="$n_{21}$ (error only corr)", color="#e74c3c", alpha=0.8, edgecolor="white", linewidth=0.5)
    ax.bar(x_pos, n22_prop, width, bottom=n11_prop+n12_prop+n21_prop, label="$n_{22}$ (error both)", color="#95a5a6", alpha=0.8, edgecolor="white", linewidth=0.5)

    # Add n21 count labels on top of the red section
    for i, (x, n21_val, n11_val, n12_val) in enumerate(zip(x_pos, sorted_df["n21"], sorted_df["n11"], sorted_df["n12"])):
        y_pos = (n11_val + n12_val + n21_val/2) / n_total[i]
        ax.text(x, y_pos, str(int(n21_val)), ha="center", va="center", fontsize=8, fontweight="bold", color="white")

    ax.set_ylabel("Proportion of pairs")
    ax.set_xlabel("Model")
    ax.set_title("Figure 7: Error Distribution (2×2 Contingency Table Composition)", fontweight="bold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(sorted_df["short"], rotation=45, ha="right")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    ax.grid(axis="y", alpha=0.2, linestyle="--")

    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ---------------------------------------------------------------------------
# Figure 8: McNemar p-values (log scale)
# ---------------------------------------------------------------------------
def fig8_mcnemar_significance(df: pd.DataFrame, out: Path):
    """
    Log-scale bar chart of McNemar p-values, showing statistical significance.
    Demonstrates how strong the conjunction fallacy effect is across models.
    """
    sorted_df = df.sort_values("mcnemar_p", ascending=True).reset_index(drop=True)
    colors = [FALLBACK_COLORS.get(r.short, "#1f77b4") for _, r in sorted_df.iterrows()]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    y_pos = np.arange(len(sorted_df))

    # Ensure no zero values for log scale
    p_values = np.maximum(sorted_df["mcnemar_p"].values, 1e-300)

    bars = ax.barh(y_pos, p_values, color=colors, edgecolor="white", linewidth=0.5, height=0.65)

    # Add value labels
    for bar, p_val in zip(bars, sorted_df["mcnemar_p"]):
        if p_val < 1e-10:
            label = f"<1e-10"
        else:
            label = f"{p_val:.1e}"
        ax.text(p_val * 2, bar.get_y() + bar.get_height() / 2,
                label, va="center", ha="left", fontsize=7, fontweight="bold")

    # Add significance threshold lines
    ax.axvline(x=0.05, color="orange", linewidth=1, linestyle="--", alpha=0.7, label="α=0.05")
    ax.axvline(x=0.001, color="red", linewidth=1, linestyle="--", alpha=0.7, label="α=0.001")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_df["short"])
    ax.set_xlabel("McNemar p-value (log scale)")
    ax.set_title("Figure 8: McNemar Test Significance (Log Scale)", fontweight="bold")
    ax.set_xscale("log")
    ax.set_xlim(left=1e-300, right=1)
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    out_dir = BASE / "figures"
    out_dir.mkdir(exist_ok=True)

    # Remove old fig5 (size vs fallacy) if present
    old_fig5 = out_dir / "fig5_size_vs_fallacy.png"
    if old_fig5.exists():
        old_fig5.unlink()
        print(f"  Deleted old {old_fig5.name}")

    print("Loading data ...")
    summary_df = load_summaries()
    pair_data = load_pair_data()
    demog_data = load_demographics()

    print(f"  {len(summary_df)} models loaded")

    print("Generating figures ...")
    fig1_delta_bias_bar(summary_df, out_dir / "linda_delta_bias_bar.png")
    fig2_accuracy_vs_delta(summary_df, out_dir / "linda_accuracy_vs_bias.png")
    fig3_confidence_violin(pair_data, summary_df, out_dir / "linda_confidence_violin.png")
    fig4_race_fallacy(demog_data, summary_df, out_dir / "linda_race_fallacy.png")
    fig5_cohen_d_forest(summary_df, out_dir / "linda_effect_sizes_forest.png")
    fig6_accuracy_by_condition(summary_df, out_dir / "linda_accuracy_by_condition.png")
    fig7_error_distribution(summary_df, out_dir / "linda_error_distribution_stack.png")
    fig8_mcnemar_significance(summary_df, out_dir / "linda_mcnemar_pvalues_log.png")

    print(f"\nAll figures saved to {out_dir}/")


if __name__ == "__main__":
    main()
