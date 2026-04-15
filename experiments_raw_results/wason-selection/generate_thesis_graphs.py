#!/usr/bin/env python3
"""
Generate publication-quality Wason Selection graphs for the thesis.
Uses extended datasets, excludes qwen3-8b (trial model).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
RAW = Path("/Users/andrejustinov/Desktop/Diploma&research/Diploma/experiments_raw_results/wason-selection/output")
BASE = Path("/Users/andrejustinov/Desktop/Diploma&research/Diploma/experiments_raw_results/wason-selection")
OUT = RAW / "thesis_graphs"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Style — matches thesis typography (serif, Cyrillic-friendly)
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "axes.linewidth": 1.0,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "legend.fontsize": 9,
    "legend.framealpha": 0.9,
    "figure.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
})

# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------
SHORT_NAMES = {
    "claude-sonnet-4.6": "Claude",
    "gpt-5.2": "GPT-5.2",
    "qwen3.5-397b-a17b": "Qwen-397B",
    "qwen3-next-80b-a3b-instruct": "Qwen-80B",
    "deepseek-v3.2": "DeepSeek",
    "grok-4.1-fast": "Grok",
    "gemma-3-27b-it": "Gemma-27B",
    "gemma-3-12b-it": "Gemma-12B",
    "glm-4.7-flash": "GLM-4.7",
}

CONTENT_LABELS = {
    "formal_logic_canonical": "FL Canonical",
    "formal_logic_neutral": "FL Neutral",
    "concrete_facts_extended": "Conc. Facts",
    "familiar_social_contracts_extended": "Fam. Social",
    "unfamiliar_fantasy_social_contracts_extended": "Unf. Fantasy",
}

# Base contexts (not extended) — used for FL since there's only one version each
FL_CANON_PATH = RAW / "formal_logic_canonical" / "metrics.csv"
FL_NEUT_PATH  = RAW / "formal_logic_neutral" / "metrics.csv"
CONC_FACT_EXT = RAW / "concrete_facts_extended" / "metrics.csv"
FAM_SOC_EXT   = RAW / "familiar_social_contracts_extended" / "metrics.csv"
UNF_FAN_EXT   = RAW / "unfamiliar_fantasy_social_contracts_extended" / "metrics.csv"


def load_csv(path: Path) -> dict:
    """Load metrics.csv into {model: {metric: float}}."""
    data = {}
    if not path.exists():
        return data
    lines = path.read_text().strip().splitlines()
    header = lines[0].split(",")
    for line in lines[1:]:
        vals = line.split(",")
        row = dict(zip(header, vals))
        model = row["model"]
        if "qwen3-8b" in model:
            continue  # skip trial model
        short = SHORT_NAMES.get(model, model)
        data[short] = {
            "EMA": float(row["EMA"]),
            "MBI": float(row["MBI"]),
            "CBR": float(row["CBR"]),
            "consistency": float(row["consistency_rate"]),
        }
    return data


def load_prompt_csv(path: Path) -> dict:
    """Load prompt variant metrics.csv."""
    data = {}
    if not path.exists():
        return data
    lines = path.read_text().strip().splitlines()
    header = lines[0].split(",")
    for line in lines[1:]:
        vals = line.split(",")
        row = dict(zip(header, vals))
        model = row["model"]
        if "qwen3-8b" in model:
            continue
        short = SHORT_NAMES.get(model, model)
        data[short] = {
            "EMA": float(row["EMA"]),
            "MBI": float(row["MBI"]),
            "CBR": float(row["CBR"]),
            "consistency": float(row["consistency_rate"]),
        }
    return data


# ---------------------------------------------------------------------------
# Load all data
# ---------------------------------------------------------------------------
fl_canon   = load_csv(FL_CANON_PATH)
fl_neutral = load_csv(FL_NEUT_PATH)
conc_ext   = load_csv(CONC_FACT_EXT)
fam_ext    = load_csv(FAM_SOC_EXT)
unf_ext    = load_csv(UNF_FAN_EXT)

# Prompt variants (proprietary has Claude, GPT, Grok; open-source has the rest)
prompt_neutral_open   = load_prompt_csv(BASE / "output_prompt_neutral_minimal" / "formal_logic_neutral" / "metrics.csv")
prompt_cot_open       = load_prompt_csv(BASE / "output_prompt_cot_answer" / "formal_logic_neutral" / "metrics.csv")
prompt_neutral_prop   = load_prompt_csv(BASE / "output_prompt_neutral_minimal_proprietary" / "formal_logic_neutral" / "metrics.csv")
prompt_cot_prop       = load_prompt_csv(BASE / "output_prompt_cot_answer_proprietary" / "formal_logic_neutral" / "metrics.csv")

# Merge prompt data
prompt_neutral = {**prompt_neutral_open, **prompt_neutral_prop}
prompt_cot     = {**prompt_cot_open, **prompt_cot_prop}

# Canonical model order (by FL Neutral EMA descending)
MODEL_ORDER = ["GPT-5.2", "Qwen-80B", "Claude", "Qwen-397B", "DeepSeek", "Gemma-27B", "Grok", "GLM-4.7", "Gemma-12B"]


# ---------------------------------------------------------------------------
# GRAPH 1: EMA across all 5 content conditions (grouped bar)
# ---------------------------------------------------------------------------
def graph1_ema_all_conditions():
    fig, ax = plt.subplots(figsize=(14, 6))

    contexts = [
        ("FL Canonical", fl_canon),
        ("FL Neutral", fl_neutral),
        ("Conc. Facts", conc_ext),
        ("Fam. Social", fam_ext),
        ("Unf. Fantasy", unf_ext),
    ]

    x = np.arange(len(MODEL_ORDER))
    n_conds = len(contexts)
    width = 0.14
    colors = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#70AD47"]

    for i, (label, data) in enumerate(contexts):
        vals = [data.get(m, {}).get("EMA", 0) * 100 for m in MODEL_ORDER]
        bars = ax.bar(x + i * width, vals, width, label=label, color=colors[i], edgecolor="white", linewidth=0.5)
        for bar in bars:
            h = bar.get_height()
            if h > 5:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5, f"{h:.0f}",
                        ha="center", va="bottom", fontsize=7, rotation=0)

    ax.set_xlabel("Model", fontweight="bold")
    ax.set_ylabel("EMA (%)", fontweight="bold")
    ax.set_title("EMA by Content Condition", fontweight="bold", fontsize=14)
    ax.set_xticks(x + width * (n_conds - 1) / 2)
    ax.set_xticklabels(MODEL_ORDER, rotation=35, ha="right", fontsize=9)
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(OUT / "fig_waston_ema_conditions.png")
    plt.close(fig)
    print("  Graph 1: EMA all conditions ✓")


# ---------------------------------------------------------------------------
# GRAPH 2: Heatmap EMA — 9 models × 5 conditions
# ---------------------------------------------------------------------------
def graph2_ema_heatmap():
    fig, ax = plt.subplots(figsize=(10, 5.5))

    conditions = [
        ("FL Canonical", fl_canon),
        ("FL Neutral", fl_neutral),
        ("Conc. Facts", conc_ext),
        ("Fam. Social", fam_ext),
        ("Unf. Fantasy", unf_ext),
    ]

    data = np.zeros((len(MODEL_ORDER), len(conditions)))
    for i, m in enumerate(MODEL_ORDER):
        for j, (_, ctx_data) in enumerate(conditions):
            data[i, j] = ctx_data.get(m, {}).get("EMA", 0) * 100

    im = ax.imshow(data, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)

    ax.set_xticks(np.arange(len(conditions)))
    ax.set_xticklabels([c[0] for c in conditions], fontsize=10, fontweight="bold", rotation=20, ha="right")
    ax.set_yticks(np.arange(len(MODEL_ORDER)))
    ax.set_yticklabels(MODEL_ORDER, fontsize=10, fontweight="bold")

    for i in range(len(MODEL_ORDER)):
        for j in range(len(conditions)):
            val = data[i, j]
            color = "black" if 20 < val < 80 else "white"
            ax.text(j, i, f"{val:.0f}", ha="center", va="center",
                    fontsize=11, fontweight="bold", color=color)

    ax.set_title("EMA Heatmap: Models × Content Conditions", fontweight="bold", fontsize=13, pad=15)
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label("EMA (%)", fontweight="bold", fontsize=10)
    plt.tight_layout()
    plt.savefig(OUT / "fig_waston_ema_heatmap.png")
    plt.close(fig)
    print("  Graph 2: EMA heatmap ✓")


# ---------------------------------------------------------------------------
# GRAPH 3: Context effect size (delta from FL Neutral to each social condition)
# ---------------------------------------------------------------------------
def graph3_context_effects():
    fig, ax = plt.subplots(figsize=(12, 5))

    effects = []
    for m in MODEL_ORDER:
        base = fl_neutral.get(m, {}).get("EMA", 0)
        fam = fam_ext.get(m, {}).get("EMA", 0)
        unf = unf_ext.get(m, {}).get("EMA", 0)
        con = conc_ext.get(m, {}).get("EMA", 0)
        effects.append({
            "model": m,
            "Δ Fam − FL Neutral": (fam - base) * 100,
            "Δ Fantasy − FL Neutral": (unf - base) * 100,
            "Δ Facts − FL Neutral": (con - base) * 100,
        })

    x = np.arange(len(MODEL_ORDER))
    w = 0.25
    colors = ["#2ECC71", "#3498DB", "#E67E22"]

    for i, key in enumerate(["Δ Facts − FL Neutral", "Δ Fantasy − FL Neutral", "Δ Fam − FL Neutral"]):
        vals = [e[key] for e in effects]
        bars = ax.bar(x + i * w, vals, w, label=key.replace("Δ ", "").replace(" − FL Neutral", ""),
                       color=colors[i], edgecolor="white", linewidth=0.5)
        for bar in bars:
            h = bar.get_height()
            sign = "+" if h > 0 else ""
            ax.text(bar.get_x() + bar.get_width() / 2, h + (1 if h >= 0 else -3),
                    f"{sign}{h:.0f}", ha="center", va="bottom" if h >= 0 else "top",
                    fontsize=7, color="#333333")

    ax.axhline(0, color="black", linewidth=1.2)
    ax.set_xlabel("Model", fontweight="bold")
    ax.set_ylabel("Effect Size (pp)", fontweight="bold")
    ax.set_title("Context Effects: Δ EMA from FL Neutral Baseline", fontweight="bold", fontsize=13)
    ax.set_xticks(x + w)
    ax.set_xticklabels(MODEL_ORDER, rotation=35, ha="right", fontsize=9)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(OUT / "fig_waston_context_effects.png")
    plt.close(fig)
    print("  Graph 3: Context effects ✓")


# ---------------------------------------------------------------------------
# GRAPH 4: EMA vs Consistency scatter (with model labels, smart positioning)
# ---------------------------------------------------------------------------
def graph4_ema_vs_consistency():
    import seaborn as sns

    fig, ax = plt.subplots(figsize=(10, 8))

    # Use FL Neutral as the reference
    x_vals = []
    y_vals = []
    labels = []
    for m in MODEL_ORDER:
        ema = fl_neutral.get(m, {}).get("EMA", 0) * 100
        cons = fl_neutral.get(m, {}).get("consistency", 0) * 100
        if ema > 0:
            x_vals.append(ema)
            y_vals.append(cons)
            labels.append(m)

    # Use seaborn for cleaner aesthetics
    sns.set_style("darkgrid")
    scatter = ax.scatter(x_vals, y_vals, s=200, c=range(len(x_vals)), cmap="tab10",
                          edgecolors="black", linewidths=1.5, zorder=5, alpha=0.8)

    # Trend line - WITHIN plot limits
    if len(x_vals) > 2:
        z = np.polyfit(x_vals, y_vals, 1)
        p = np.poly1d(z)
        # Trendline from 0 to 110 (stays within limits)
        x_line = np.linspace(0, 110, 100)
        r = np.corrcoef(x_vals, y_vals)[0,1]
        ax.plot(x_line, p(x_line), "--", color="#555555", linewidth=2, alpha=0.7,
                label=f"Trend (r = {r:.2f})", zorder=3)

    # Smart label positioning - avoid overlaps for close dots
    from matplotlib.patches import Rectangle

    # Group nearby points (within distance 5)
    positioned_labels = {}
    for i, label in enumerate(labels):
        x, y = x_vals[i], y_vals[i]

        # Find if there's a nearby point already positioned
        nearby_idx = None
        for j in range(i):
            dist = np.sqrt((x_vals[j] - x)**2 + (y_vals[j] - y)**2)
            if dist < 5:  # Points within distance 5 are "close"
                nearby_idx = j
                break

        # Determine base quadrant position
        if x < 50:
            if y < 50:
                # Bottom-left quadrant
                base_offsets = [(1.5, 2.5), (-2, -2.5)]  # Alternate: right-up vs left-down
            else:
                # Top-left quadrant
                base_offsets = [(1.5, -2.5), (-2, 2.5)]  # Alternate: right-down vs left-up
        else:
            if y < 50:
                # Bottom-right quadrant
                base_offsets = [(-1.5, 2.5), (2, -2.5)]  # Alternate: left-up vs right-down
            else:
                # Top-right quadrant
                base_offsets = [(-1.5, -2.5), (2, 2.5)]  # Alternate: left-down vs right-up

        # If close to another point, use alternate position
        if nearby_idx is not None:
            offset_x, offset_y = base_offsets[1]
            ha = "right" if offset_x < 0 else "left"
            va = "top" if offset_y < 0 else "bottom"
        else:
            offset_x, offset_y = base_offsets[0]
            ha = "right" if offset_x < 0 else "left"
            va = "top" if offset_y < 0 else "bottom"

        ax.text(x + offset_x, y + offset_y, label, fontsize=8, fontweight="bold",
                ha=ha, va=va, zorder=6, bbox=dict(boxstyle="round,pad=0.3",
                facecolor="white", edgecolor="none", alpha=0.8))

    ax.set_xlabel("EMA (%) — FL Neutral", fontweight="bold", fontsize=11)
    ax.set_ylabel("Consistency Rate (%) — FL Neutral", fontweight="bold", fontsize=11)
    ax.set_title("Correctness vs Stability: EMA and Consistency Rate", fontweight="bold", fontsize=13, pad=15)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 110)
    ax.legend(fontsize=10, loc="lower right")
    ax.grid(True, alpha=0.3, linestyle="--", zorder=1)
    plt.tight_layout()
    plt.savefig(OUT / "fig_waston_ema_vs_consistency.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  Graph 4: EMA vs Consistency scatter ✓")


# ---------------------------------------------------------------------------
# GRAPH 5: Radar chart — 3 metrics (EMA, MBI, CBR) for all 9 models
# ---------------------------------------------------------------------------
def graph5_radar():
    from math import pi

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"projection": "polar"})

    categories = ["EMA\n(higher\nbetter)", "MBI\n(lower\nbetter)", "CBR\n(lower\nbetter)"]
    n_vars = len(categories)
    angles = [n / float(n_vars) * 2 * pi for n in range(n_vars)]
    angles += angles[:1]

    # Color palette for 9 models
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
               "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22"]

    for i, m in enumerate(MODEL_ORDER):
        d = fl_neutral.get(m, {})
        if not d:
            continue
        # For radar: EMA good = close to center → invert
        # MBI bad = far from center → as-is
        # CBR bad = far from center → as-is
        ema_inv = (1 - d["EMA"]) * 100
        mbi = d["MBI"] * 100
        cbr = d["CBR"] * 100
        values = [ema_inv, mbi, cbr]
        values += values[:1]

        color = palette[i % len(palette)]
        ax.plot(angles, values, "o-", linewidth=2, label=m, color=color, markersize=4)
        ax.fill(angles, values, alpha=0.1, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8, color="gray")
    ax.set_title("Bias Profile — FL Neutral\\n(Closer to center = better)",
                 fontweight="bold", fontsize=13, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.05), fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(OUT / "fig_waston_radar.png")
    plt.close(fig)
    print("  Graph 5: Radar chart ✓")


# ---------------------------------------------------------------------------
# GRAPH 6: Bias family stacked bar (MBI + CBR = Confirmation bias total)
# ---------------------------------------------------------------------------
def graph6_bias_family():
    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(MODEL_ORDER))
    w = 0.35

    neutral_vals = [fl_neutral.get(m, {}).get("MBI", 0) * 100 for m in MODEL_ORDER]
    cot_vals = [prompt_cot.get(m, {}).get("MBI", 0) * 100 for m in MODEL_ORDER]

    # Grouped: Neutral MBI vs CoT MBI
    bars1 = ax.bar(x - w/2, neutral_vals, w, label="Neutral MBI", color="#E74C3C", edgecolor="white", linewidth=0.5)
    bars2 = ax.bar(x + w/2, cot_vals, w, label="CoT MBI", color="#C0392B", edgecolor="white", linewidth=0.5)

    for bar in bars1 + bars2:
        h = bar.get_height()
        if h > 2:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 1, f"{h:.0f}",
                    ha="center", va="bottom", fontsize=7)

    ax.set_xlabel("Model", fontweight="bold")
    ax.set_ylabel("Matching Bias Index (%)", fontweight="bold")
    ax.set_title("Matching Bias: Neutral vs CoT Prompt", fontweight="bold", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(MODEL_ORDER, rotation=35, ha="right", fontsize=9)
    ax.set_ylim(0, 60)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(OUT / "fig_waston_mbi_prompt.png")
    plt.close(fig)
    print("  Graph 6: MBI prompt comparison ✓")


# ---------------------------------------------------------------------------
# GRAPH 7: CoT delta — how much each model gains from Chain-of-Thought
# ---------------------------------------------------------------------------
def graph7_cot_delta():
    fig, ax = plt.subplots(figsize=(10, 5))

    models_with_cot = list(prompt_neutral_open.keys() & prompt_cot_open.keys()) + \
                      list(prompt_neutral_prop.keys() & prompt_cot_prop.keys())

    deltas = []
    for m in models_with_cot:
        if m in prompt_neutral_prop:
            # Proprietary model
            d = (prompt_cot_prop[m]["EMA"] - prompt_neutral_prop[m]["EMA"]) * 100
            is_proprietary = True
        else:
            # Open-source model
            d = (prompt_cot_open[m]["EMA"] - prompt_neutral_open[m]["EMA"]) * 100
            is_proprietary = False
        deltas.append((m, d, is_proprietary))

    # Sort by delta descending (models with biggest CoT gain on top)
    deltas.sort(key=lambda x: x[1], reverse=True)

    x = np.arange(len(deltas))
    # Blue for proprietary, orange for open-source; green for positive, red for negative
    colors = []
    for m, d, is_prop in deltas:
        if is_prop:
            # Proprietary: darker blue tones
            colors.append("#1F77B4" if d >= 0 else "#1547A0")
        else:
            # Open-source: darker orange tones
            colors.append("#FF7F0E" if d >= 0 else "#D65E0A")

    bars = ax.barh(x, [d[1] for d in deltas], color=colors, edgecolor="white", linewidth=0.5)

    for i, (bar, (_, delta, _)) in enumerate(zip(bars, deltas)):
        sign = "+" if delta >= 0 else ""
        # For positive deltas: label to the right of bar
        # For negative deltas: label to the left of bar (further from axis)
        if delta >= 0:
            ax.text(delta + 1.5, i, f"{sign}{delta:.1f} pp",
                    ha="left", va="center",
                    fontsize=9, fontweight="bold")
        else:
            ax.text(delta - 1.5, i, f"{sign}{delta:.1f} pp",
                    ha="right", va="center",
                    fontsize=9, fontweight="bold")

    ax.set_yticks(x)
    ax.set_yticklabels([d[0] for d in deltas], fontsize=10, fontweight="bold")
    ax.set_xlabel("Δ EMA (CoT − Neutral), percentage points", fontweight="bold")
    ax.set_title("Chain-of-Thought Effect on EMA", fontweight="bold", fontsize=13)
    ax.axvline(0, color="black", linewidth=1.2)
    # Extend x-limits so delta labels don't overflow
    min_delta = min(d[1] for d in deltas)
    max_delta = max(d[1] for d in deltas)
    ax.set_xlim(min_delta - 5, max_delta + 5)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#1F77B4", edgecolor="white", label="Proprietary (positive Δ)"),
        Patch(facecolor="#1547A0", edgecolor="white", label="Proprietary (negative Δ)"),
        Patch(facecolor="#FF7F0E", edgecolor="white", label="Open-source (positive Δ)"),
        Patch(facecolor="#D65E0A", edgecolor="white", label="Open-source (negative Δ)"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=8)

    plt.subplots_adjust(left=0.18, right=0.95)  # Extra space for model names on Y-axis
    plt.savefig(OUT / "fig_waston_cot_delta.png")
    plt.close(fig)
    print("  Graph 7: CoT delta ✓")


# ---------------------------------------------------------------------------
# Generate all
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Generating Wason Selection thesis graphs...")
    print(f"Output: {OUT}")
    graph1_ema_all_conditions()
    graph2_ema_heatmap()
    graph3_context_effects()
    graph4_ema_vs_consistency()
    graph7_cot_delta()
    print(f"\nDone! {len(list(OUT.glob('*.png')))} graphs saved to {OUT}")
