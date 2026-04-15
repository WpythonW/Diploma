"""Build 5 expansion graphs for 2-4-6 experiment thesis section."""

import json
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ── Style ──────────────────────────────────────────────────────────────
rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "axes.grid": True,
    "grid.alpha": 0.3,
})

BASE = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE, "output")
IMG_DIR = os.path.join(BASE, "images_expansion")
os.makedirs(IMG_DIR, exist_ok=True)

# ── Helpers ────────────────────────────────────────────────────────────
MODEL_LABELS = {
    "anthropic__claude-sonnet-4.6": "Claude Sonnet 4.6",
    "openai__gpt-5.2": "GPT-5.2",
    "qwen__qwen3.5-397b-a17b": "Qwen3.5-397B",
    "qwen__qwen3-next-80b-a3b-instruct": "Qwen-Next-80B",
    "x-ai__grok-4.1-fast": "Grok 4.1 Fast",
    "deepseek__deepseek-v3.2": "DeepSeek V3.2",
    "google__gemma-3-12b-it": "Gemma-3-12B",
    "google__gemma-3-27b-it": "Gemma-3-27B",
    "z-ai__glm-4.7-flash": "GLM-4.7 Flash",
}

SHORT_LABELS = {
    "anthropic__claude-sonnet-4.6": "Claude",
    "openai__gpt-5.2": "GPT-5.2",
    "qwen__qwen3.5-397b-a17b": "Qwen3.5",
    "qwen__qwen3-next-80b-a3b-instruct": "Qwen-Next",
    "x-ai__grok-4.1-fast": "Grok",
    "deepseek__deepseek-v3.2": "DeepSeek",
    "google__gemma-3-12b-it": "Gemma-12B",
    "google__gemma-3-27b-it": "Gemma-27B",
    "z-ai__glm-4.7-flash": "GLM",
}

COLORS = {
    "anthropic__claude-sonnet-4.6": "#FF7F0E",
    "openai__gpt-5.2": "#1F77B4",
    "qwen__qwen3.5-397b-a17b": "#2CA02C",
    "qwen__qwen3-next-80b-a3b-instruct": "#D62728",
    "x-ai__grok-4.1-fast": "#9467BD",
    "deepseek__deepseek-v3.2": "#8C564B",
    "google__gemma-3-12b-it": "#E377C2",
    "google__gemma-3-27b-it": "#7F7F7F",
    "z-ai__glm-4.7-flash": "#BCBD22",
}


def load_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ======================================================================
# GRAPH 1 — IOU trajectories over turns (key models, baseline)
# ======================================================================
def graph1_iou_trajectories():
    print("Building Graph 1: IOU trajectories...")
    per_turn = load_csv(os.path.join(OUTPUT_DIR, "per_turn_246.csv"))

    # Also load adaptive
    per_turn_adaptive = load_csv(os.path.join(OUTPUT_DIR, "per_turn_246.csv"))

    key_models = [
        "anthropic__claude-sonnet-4.6",
        "openai__gpt-5.2",
        "qwen__qwen3.5-397b-a17b",
        "x-ai__grok-4.1-fast",
    ]

    fig, ax = plt.subplots(figsize=(9, 5))

    for model in key_models:
        rows = [r for r in per_turn if r["model"] == model]
        turns = [int(r["turn"]) for r in rows]
        ious = [float(r["mean_iou"]) for r in rows]
        label = SHORT_LABELS.get(model, model)
        ax.plot(turns, ious, marker="o", markersize=3, linewidth=1.8,
                color=COLORS[model], label=label, alpha=0.85)

    ax.set_xlabel("Turn")
    ax.set_ylabel("Mean IOU")
    ax.set_title("IOU Trajectories Over Turns (Baseline, Key Models)")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(bottom=0)

    plt.savefig(os.path.join(IMG_DIR, "fig1_iou_trajectories.png"))
    plt.close()
    print("  -> saved fig1_iou_trajectories.png")


# ======================================================================
# GRAPH 2 — CTR grouped bar chart (baseline vs adaptive)
# ======================================================================
def graph2_ctr_bars():
    print("Building Graph 2: CTR baseline vs adaptive bars...")

    # Load baseline metrics
    baseline = load_csv(os.path.join(OUTPUT_DIR, "metrics_246.csv"))

    # Load adaptive metrics from each model folder
    adaptive_rows = []
    for model_key in SHORT_LABELS:
        folder = model_key.replace("__", "/")
        path = os.path.join(OUTPUT_DIR, "adaptive", folder, "metrics_246.csv")
        if not os.path.exists(path):
            # try adaptive/high
            path = os.path.join(OUTPUT_DIR, "adaptive", "high", folder, "metrics_246.csv")
        if os.path.exists(path):
            rows = load_csv(path)
            if rows:
                adaptive_rows.append(rows[0])

    fig, ax = plt.subplots(figsize=(10, 5))

    models_in_order = [r["model"] for r in baseline]
    x = np.arange(len(models_in_order))
    width = 0.35

    ctr_base = [float(r["confirming_test_rate"]) for r in baseline]
    ctr_adap = []
    labels_short = []

    for model in models_in_order:
        short = SHORT_LABELS.get(model, model.split("__")[-1][:15])
        labels_short.append(short)
        found = None
        for ar in adaptive_rows:
            if ar["model"] == model:
                found = ar
                break
        if found:
            ctr_adap.append(float(found["confirming_test_rate"]))
        else:
            ctr_adap.append(np.nan)

    bars1 = ax.bar(x - width/2, ctr_base, width, label="Baseline", color="#1F77B4", alpha=0.85)
    bars2 = ax.bar(x + width/2, ctr_adap, width, label="Adaptive", color="#FF7F0E", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(labels_short, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Confirming Test Rate (CTR)")
    ax.set_title("CTR: Baseline vs Adaptive by Model")
    ax.legend()
    ax.set_ylim(0, 1.1)

    plt.savefig(os.path.join(IMG_DIR, "fig2_ctr_bars.png"))
    plt.close()
    print("  -> saved fig2_ctr_bars.png")


# ======================================================================
# GRAPH 3 — Scatter: CTR vs Success Rate
# ======================================================================
def graph3_scatter_ctr_sr():
    print("Building Graph 3: CTR vs Success Rate scatter...")

    baseline = load_csv(os.path.join(OUTPUT_DIR, "metrics_246.csv"))

    # Also gather adaptive
    adaptive_by_model = {}
    for model_key in SHORT_LABELS:
        folder = model_key.replace("__", "/")
        path = os.path.join(OUTPUT_DIR, "adaptive", folder, "metrics_246.csv")
        if os.path.exists(path):
            rows = load_csv(path)
            if rows:
                adaptive_by_model[model_key] = rows[0]

    fig, ax = plt.subplots(figsize=(8, 5))

    for r in baseline:
        model = r["model"]
        sr_b = float(r["success_rate"])
        ctr_b = float(r["confirming_test_rate"])
        label = SHORT_LABELS.get(model, model.split("__")[-1][:12])
        color = COLORS.get(model, "#999999")
        ax.scatter(ctr_b, sr_b, s=120, c=color, zorder=3, edgecolors="black", linewidths=0.8)
        ax.annotate(label, (ctr_b, sr_b), fontsize=8, textcoords="offset points",
                    xytext=(6, 6), color=color, fontweight="bold")

        # Adaptive point
        if model in adaptive_by_model:
            ar = adaptive_by_model[model]
            sr_a = float(ar["success_rate"])
            ctr_a = float(ar["confirming_test_rate"])
            ax.scatter(ctr_a, sr_a, s=120, c=color, zorder=3, marker="^", edgecolors="black", linewidths=0.8)
            ax.annotate(label + " (A)", (ctr_a, sr_a), fontsize=7, textcoords="offset points",
                        xytext=(6, -10), color=color, style="italic")

    ax.set_xlabel("Confirming Test Rate (CTR)")
    ax.set_ylabel("Success Rate")
    ax.set_title("CTR vs Success Rate (○ Baseline, △ Adaptive)")
    ax.grid(True, alpha=0.3)

    plt.savefig(os.path.join(IMG_DIR, "fig3_scatter_ctr_sr.png"))
    plt.close()
    print("  -> saved fig3_scatter_ctr_sr.png")


# ======================================================================
# GRAPH 4 — Heatmap by rule category
# ======================================================================
def graph4_category_heatmap():
    print("Building Graph 4: Category heatmap...")

    cat_data = load_csv(os.path.join(OUTPUT_DIR, "baseline", "high", "metrics_246_by_category.csv"))

    # Also load adaptive categories
    cat_adaptive_path = os.path.join(OUTPUT_DIR, "adaptive", "high", "openai__gpt-5.2", "metrics_246_by_category.csv")
    # Build per-model per-category for baseline
    models = list(dict.fromkeys(r["model"] for r in cat_data))
    categories = ["Порядок", "Чётность", "Арифметика", "Паттерн", "Смешанные"]

    sr_matrix = np.zeros((len(models), len(categories)))
    for i, model in enumerate(models):
        for j, cat in enumerate(categories):
            rows = [r for r in cat_data if r["model"] == model and r["category"] == cat]
            if rows:
                sr_matrix[i, j] = float(rows[0]["success_rate"])

    fig, ax = plt.subplots(figsize=(8, 4.5))
    im = ax.imshow(sr_matrix, aspect="auto", cmap="YlOrRd", vmin=0, vmax=1)

    short_labels = [SHORT_LABELS.get(m, m.split("__")[-1][:15]) for m in models]
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(short_labels, fontsize=9)

    # Annotate
    for i in range(len(models)):
        for j in range(len(categories)):
            val = sr_matrix[i, j]
            color = "white" if val > 0.5 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=9, color=color)

    ax.set_xlabel("Rule Category")
    ax.set_title("Success Rate by Model and Rule Category (Baseline)")
    fig.colorbar(im, ax=ax, fraction=0.03, label="Success Rate")
    fig.tight_layout()

    plt.savefig(os.path.join(IMG_DIR, "fig4_category_heatmap.png"))
    plt.close()
    print("  -> saved fig4_category_heatmap.png")


# ======================================================================
# GRAPH 5 — Distribution of turns to success
# ======================================================================
def graph5_turns_to_success():
    print("Building Graph 5: Distribution of turns to success...")

    # Load trial_results for GPT-5.2 baseline (the only one with full data)
    trial_path = os.path.join(OUTPUT_DIR, "baseline", "high", "openai__gpt-5.2", "trial_results.json")
    if not os.path.exists(trial_path):
        print("  -> No trial_results.json found, skipping.")
        return

    with open(trial_path, encoding="utf-8") as f:
        trials = json.load(f)

    def extract_turns_to_success(trial_data):
        """Extract turns needed for successful rules."""
        results = []
        for rule, turns_data in trial_data.items():
            if not turns_data:
                continue
            last = turns_data[-1]
            if last.get("iou", 0) > 0.95:
                results.append(len(turns_data))
        return results

    gpt_turns = extract_turns_to_success(trials)

    # Also try to load GPT-5.2 reasoning data
    reasoning_path = os.path.join(OUTPUT_DIR, "..", "..", "wason-2-4-6", "data", "openai_gpt-5.2_none.json")
    # Use adaptive GPT-5.2 if available
    adaptive_trial_path = os.path.join(OUTPUT_DIR, "adaptive", "high", "openai__gpt-5.2", "trial_results.json")
    adaptive_turns = []
    if os.path.exists(adaptive_trial_path):
        with open(adaptive_trial_path, encoding="utf-8") as f:
            adaptive_trials = json.load(f)
        adaptive_turns = extract_turns_to_success(adaptive_trials)

    fig, ax = plt.subplots(figsize=(7, 4))
    bins = range(1, 22)
    ax.hist(gpt_turns, bins=bins, alpha=0.6, label="GPT-5.2 (Baseline)", color="#1F77B4", edgecolor="black")
    if adaptive_turns:
        ax.hist(adaptive_turns, bins=bins, alpha=0.6, label="GPT-5.2 (Adaptive)", color="#FF7F0E", edgecolor="black")

    ax.set_xlabel("Turns to Success")
    ax.set_ylabel("Number of Rules")
    ax.set_title("Distribution of Turns to Successful Rule Discovery")
    ax.legend()
    ax.set_xticks(bins)

    plt.savefig(os.path.join(IMG_DIR, "fig5_turns_to_success.png"))
    plt.close()
    print(f"  -> saved fig5_turns_to_success.png (GPT baseline={len(gpt_turns)} successes, adaptive={len(adaptive_turns)})")


# ======================================================================
# GRAPH 6 — IOU trajectories: reasoning models (baseline vs adaptive)
# ======================================================================
def graph6_reasoning_iou_trajectories():
    print("Building Graph 6: Reasoning model IOU trajectories...")

    reasoning_models = [
        "anthropic__claude-sonnet-4.6",
        "openai__gpt-5.2",
    ]

    base_dir = os.path.join(OUTPUT_DIR, "baseline", "high")
    adapt_dir = os.path.join(OUTPUT_DIR, "adaptive", "high")

    base_rows = load_csv(os.path.join(base_dir, "per_turn_246.csv"))
    adapt_rows = load_csv(os.path.join(adapt_dir, "per_turn_246.csv"))

    fig, ax = plt.subplots(figsize=(9, 5))

    linestyles = {"baseline": "-", "adaptive": "--"}
    markers = {"baseline": "o", "adaptive": "s"}

    for model in reasoning_models:
        label = SHORT_LABELS.get(model, model)
        color = COLORS.get(model, "#333333")

        for condition, rows in [("baseline", base_rows), ("adaptive", adapt_rows)]:
            pts = [(int(r["turn"]), float(r["mean_iou"]))
                   for r in rows if r["model"] == model]
            if not pts:
                print(f"  [WARN] no data for {model} / {condition}")
                continue
            pts.sort()
            turns, ious = zip(*pts)
            ax.plot(turns, ious,
                    linestyle=linestyles[condition],
                    marker=markers[condition],
                    markersize=4, linewidth=1.8,
                    color=color, alpha=0.85,
                    label=f"{label} ({condition})")

    ax.set_xlabel("Turn")
    ax.set_ylabel("Mean IOU")
    ax.set_title("IOU Trajectories Over Turns — Reasoning Models\n(baseline vs adaptive, extended thinking)")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(bottom=0)

    out_path = os.path.join(BASE, "figures", "wason246_reasoning_iou_trajectories.png")
    plt.savefig(out_path)
    plt.close()
    print(f"  -> saved {out_path}")


# ======================================================================
# MAIN
# ======================================================================
if __name__ == "__main__":
    graph1_iou_trajectories()
    graph2_ctr_bars()
    graph3_scatter_ctr_sr()
    graph4_category_heatmap()
    graph5_turns_to_success()
    graph6_reasoning_iou_trajectories()
    print("\nAll graphs built successfully.")
