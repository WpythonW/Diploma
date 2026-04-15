from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import auc

from config import MAX_TEST_VALUE, MIN_TEST_VALUE


def load_rules_manifest(json_path: Path) -> dict[str, str]:
    for parent in [json_path.parent, *json_path.parents]:
        manifest_path = parent / "rules_manifest.csv"
        if manifest_path.exists():
            manifest = pd.read_csv(manifest_path)
            if {"code", "category"}.issubset(manifest.columns):
                return {
                    str(row["code"]): str(row["category"])
                    for _, row in manifest[["code", "category"]].iterrows()
                }
    return {}


def load_and_flatten(
    json_path: Path,
    fallback_rule_categories: dict[str, str] | None = None,
) -> pd.DataFrame:
    with json_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    model_dir = json_path.parent.name
    summary_path = json_path.parent / "summary.json"
    reasoning = "none"
    prompt_style = "baseline"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        reasoning = str(summary.get("reasoning_effort", "none"))
        prompt_style = str(summary.get("prompt_style", "baseline"))
    rule_categories = load_rules_manifest(json_path)
    if fallback_rule_categories:
        rule_categories = {**rule_categories, **fallback_rule_categories}

    rows = []
    for rule, steps in data.items():
        for step in steps:
            rows.append(
                {
                    "model": model_dir,
                    "prompt_style": prompt_style,
                    "reasoning": reasoning,
                    "category": rule_categories.get(rule, "Uncategorized"),
                    "rule": rule,
                    "turn": step["turn"],
                    "hypothesis": step["hypothesis"],
                    "expected": step["expected"],
                    "actual": step["actual"],
                    "surprised": step["surprised"],
                    "h_in_r": step["h_in_r"],
                    "r_in_h": step["r_in_h"],
                    "distance": step["distance"],
                    "delta": step["delta"],
                    "iou": step["iou"],
                    "tokens_prompt": step["tokens"]["prompt"],
                    "tokens_completion": step["tokens"]["completion"],
                    "tokens_reasoning": step["tokens"]["reasoning"],
                }
            )

    return pd.DataFrame(rows)


def compute_auc_iou(group: pd.DataFrame) -> float:
    group = group.sort_values("turn")
    if len(group) < 2:
        return float(group["iou"].iloc[-1])
    x = group["turn"].values / group["turn"].max()
    y = group["iou"].values
    x = np.concatenate([[0], x])
    y = np.concatenate([[0], y])
    return float(auc(x, y))


def safe_eval(func: Any, x: int, y: int, z: int) -> bool:
    try:
        return bool(func(x, y, z))
    except Exception:
        return False


def compile_hypothesis(hyp_code: str) -> Any:
    return eval(hyp_code)


def generate_samples(n: int = 50_000) -> np.ndarray:
    return np.random.randint(MIN_TEST_VALUE, MAX_TEST_VALUE + 1, (n, 3))


HYPOTHESIS_CHANGE_SAMPLES = generate_samples(50_000)
HYPOTHESIS_VECTOR_CACHE: dict[str, np.ndarray] = {}


def get_hypothesis_vector(hyp_code: str, samples: np.ndarray = HYPOTHESIS_CHANGE_SAMPLES) -> np.ndarray:
    cached = HYPOTHESIS_VECTOR_CACHE.get(hyp_code)
    if cached is not None:
        return cached
    try:
        hyp = compile_hypothesis(hyp_code)
    except Exception:
        vector = np.zeros(len(samples), dtype=bool)
        HYPOTHESIS_VECTOR_CACHE[hyp_code] = vector
        return vector

    vector = np.array([safe_eval(hyp, *s) for s in samples], dtype=bool)
    HYPOTHESIS_VECTOR_CACHE[hyp_code] = vector
    return vector


def compute_iou_from_code(h1_code: str, h2_code: str, samples: np.ndarray = HYPOTHESIS_CHANGE_SAMPLES) -> float:
    h1_vec = get_hypothesis_vector(h1_code, samples)
    h2_vec = get_hypothesis_vector(h2_code, samples)
    intersection = int((h1_vec & h2_vec).sum())
    union = int((h1_vec | h2_vec).sum())
    return float(intersection / max(union, 1))


def compute_hypothesis_change_rate(group: pd.DataFrame) -> float:
    group = group.sort_values("turn").reset_index(drop=True)
    if len(group) < 2:
        return 0.0

    changed = 0
    comparisons = 0
    previous_hypothesis = str(group.loc[0, "hypothesis"])
    for idx in range(1, len(group)):
        current_hypothesis = str(group.loc[idx, "hypothesis"])
        iou = compute_iou_from_code(previous_hypothesis, current_hypothesis)
        if iou < 0.9:
            changed += 1
        comparisons += 1
        previous_hypothesis = current_hypothesis
    return float(changed / comparisons)


def compute_metrics(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    group_keys = ["model", "prompt_style", "reasoning"]
    success = (
        df.groupby(group_keys + ["rule"]).agg(max_iou=("iou", "max")).reset_index()
    )
    success["success"] = success["max_iou"] > 0.95

    success_rate = (
        success.groupby(group_keys)
        .agg(success_rate=("success", "mean"))
        .reset_index()
    )

    confirming = (
        df.groupby(group_keys).agg(confirming_test_rate=("expected", "mean")).reset_index()
    )

    auc_iou = (
        df.groupby(group_keys + ["rule"], group_keys=False)
        .apply(compute_auc_iou, include_groups=False)
        .reset_index(name="auc_iou")
    )
    auc_mean = (
        auc_iou.groupby(group_keys).agg(mean_auc_iou=("auc_iou", "mean")).reset_index()
    )

    hypothesis_change = (
        df.groupby(group_keys + ["rule"], group_keys=False)
        .apply(compute_hypothesis_change_rate, include_groups=False)
        .reset_index(name="hypothesis_change_rate")
    )
    hypothesis_change_mean = (
        hypothesis_change.groupby(group_keys)
        .agg(hypothesis_change_rate=("hypothesis_change_rate", "mean"))
        .reset_index()
    )

    metrics_df = success_rate.merge(auc_mean, on=group_keys)
    metrics_df = metrics_df.merge(confirming, on=group_keys)
    metrics_df = metrics_df.merge(hypothesis_change_mean, on=group_keys)

    per_turn_df = (
        df.groupby(group_keys + ["turn"])
        .agg(mean_iou=("iou", "mean"), confirming_test_rate=("expected", "mean"))
        .reset_index()
    )

    return metrics_df, per_turn_df


def compute_category_metrics(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    group_keys = ["model", "prompt_style", "reasoning", "category"]
    success = (
        df.groupby(group_keys + ["rule"]).agg(max_iou=("iou", "max")).reset_index()
    )
    success["success"] = success["max_iou"] > 0.95

    success_rate = success.groupby(group_keys).agg(success_rate=("success", "mean")).reset_index()
    confirming = (
        df.groupby(group_keys).agg(confirming_test_rate=("expected", "mean")).reset_index()
    )
    auc_iou = (
        df.groupby(group_keys + ["rule"], group_keys=False)
        .apply(compute_auc_iou, include_groups=False)
        .reset_index(name="auc_iou")
    )
    auc_mean = auc_iou.groupby(group_keys).agg(mean_auc_iou=("auc_iou", "mean")).reset_index()
    hypothesis_change = (
        df.groupby(group_keys + ["rule"], group_keys=False)
        .apply(compute_hypothesis_change_rate, include_groups=False)
        .reset_index(name="hypothesis_change_rate")
    )
    hypothesis_change_mean = (
        hypothesis_change.groupby(group_keys)
        .agg(hypothesis_change_rate=("hypothesis_change_rate", "mean"))
        .reset_index()
    )

    metrics_df = success_rate.merge(auc_mean, on=group_keys)
    metrics_df = metrics_df.merge(confirming, on=group_keys)
    metrics_df = metrics_df.merge(hypothesis_change_mean, on=group_keys)

    per_turn_df = (
        df.groupby(group_keys + ["turn"])
        .agg(mean_iou=("iou", "mean"), confirming_test_rate=("expected", "mean"))
        .reset_index()
    )
    return metrics_df, per_turn_df
