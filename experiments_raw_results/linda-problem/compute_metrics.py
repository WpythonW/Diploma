from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from scipy.stats import binomtest, ttest_rel, wilcoxon

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import LINDA_MODELS, OUTPUT_DIR
from run_experiments import get_model_output_paths, slugify_model_name


def mcnemar_exact(n12: int, n21: int) -> dict[str, float]:
    discordant = n12 + n21
    exact_pvalue = 1.0 if discordant == 0 else float(binomtest(min(n12, n21), discordant, 0.5).pvalue)
    statistic = 0.0 if discordant == 0 else ((abs(n12 - n21) - 1) ** 2) / discordant
    return {
        "n12": float(n12),
        "n21": float(n21),
        "discordant": float(discordant),
        "mcnemar_statistic_cc": float(statistic),
        "mcnemar_exact_pvalue": exact_pvalue,
    }


def apply_bh(pvalues: list[float]) -> list[float]:
    if not pvalues:
        return []
    indexed = sorted(enumerate(pvalues), key=lambda item: item[1])
    adjusted = [0.0] * len(pvalues)
    running_min = 1.0
    total = len(pvalues)
    for rank, (original_idx, pvalue) in enumerate(reversed(indexed), start=1):
        adjusted_value = min(1.0, pvalue * total / (total - rank + 1))
        running_min = min(running_min, adjusted_value)
        adjusted[original_idx] = running_min
    return adjusted


def paired_bias_tests(pair_df: pd.DataFrame) -> dict[str, Any]:
    correlated = pair_df["bias_score_correlated"].astype(float)
    uncorrelated = pair_df["bias_score_uncorrelated"].astype(float)

    t_stat, t_pvalue = ttest_rel(correlated, uncorrelated)
    nonzero = (correlated - uncorrelated) != 0
    if nonzero.any():
        w_stat, w_pvalue = wilcoxon(correlated[nonzero], uncorrelated[nonzero], zero_method="wilcox")
    else:
        w_stat, w_pvalue = 0.0, 1.0

    return {
        "mean_bias_correlated": float(correlated.mean()),
        "mean_bias_uncorrelated": float(uncorrelated.mean()),
        "delta_bias": float(correlated.mean() - uncorrelated.mean()),
        "paired_t_statistic": float(t_stat),
        "paired_t_pvalue": float(t_pvalue),
        "wilcoxon_statistic": float(w_stat),
        "wilcoxon_pvalue": float(w_pvalue),
    }


def summarize_demographics(pair_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []

    group_specs = [("race", "race"), ("age", "age")]
    for variable_name, column in group_specs:
        for group_value, group_df in pair_df.groupby(column):
            correlated_correct = group_df["correct_correlated"].astype(int)
            uncorrelated_correct = group_df["correct_uncorrelated"].astype(int)
            n12 = int(((correlated_correct == 1) & (uncorrelated_correct == 0)).sum())
            n21 = int(((correlated_correct == 0) & (uncorrelated_correct == 1)).sum())
            mcnemar = mcnemar_exact(n12, n21)

            summary_rows.append(
                {
                    "group_variable": variable_name,
                    "group_value": group_value,
                    "n_pairs": int(len(group_df)),
                    "fallacy_rate_correlated": float(1.0 - correlated_correct.mean()),
                    "fallacy_rate_uncorrelated": float(1.0 - uncorrelated_correct.mean()),
                    "mean_bias_score_correlated": float(group_df["bias_score_correlated"].mean()),
                    "mean_bias_score_uncorrelated": float(group_df["bias_score_uncorrelated"].mean()),
                    "delta_bias": float(
                        group_df["bias_score_correlated"].mean() - group_df["bias_score_uncorrelated"].mean()
                    ),
                }
            )
            test_rows.append(
                {
                    "group_variable": variable_name,
                    "group_value": group_value,
                    "n12": n12,
                    "n21": n21,
                    "discordant": int(mcnemar["discordant"]),
                    "mcnemar_statistic_cc": mcnemar["mcnemar_statistic_cc"],
                    "mcnemar_exact_pvalue": mcnemar["mcnemar_exact_pvalue"],
                }
            )

    tests_df = pd.DataFrame(test_rows)
    tests_df["bh_fdr_pvalue"] = apply_bh(tests_df["mcnemar_exact_pvalue"].tolist())
    return pd.DataFrame(summary_rows), tests_df


def compute_summary(trial_csv: Path, pair_csv: Path, output_dir: Path) -> dict[str, Any]:
    trial_df = pd.read_csv(trial_csv)
    pair_df = pd.read_csv(pair_csv)

    n_counts = pair_df["n_type"].value_counts().to_dict()
    mcnemar = mcnemar_exact(int(n_counts.get("n12", 0)), int(n_counts.get("n21", 0)))
    bias = paired_bias_tests(pair_df)
    demographic_df, tests_df = summarize_demographics(pair_df)

    output_dir.mkdir(parents=True, exist_ok=True)
    demographic_df.to_csv(output_dir / "demographic_summary.csv", index=False)
    tests_df.to_csv(output_dir / "demographic_mcnemar_tests.csv", index=False)

    summary = {
        "n_trials": int(len(trial_df)),
        "n_pairs": int(len(pair_df)),
        "n11": int(n_counts.get("n11", 0)),
        "n12": int(n_counts.get("n12", 0)),
        "n21": int(n_counts.get("n21", 0)),
        "n22": int(n_counts.get("n22", 0)),
        **mcnemar,
        **bias,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summaries: dict[str, Any] = {}
    models = LINDA_MODELS
    if not models:
        print(json.dumps({}, ensure_ascii=False, indent=2))
        return
    for model in models:
        paths = get_model_output_paths(model)
        summary = compute_summary(
            trial_csv=paths["trial_results_csv"],
            pair_csv=paths["pair_results_csv"],
            output_dir=paths["model_dir"],
        )
        summaries[slugify_model_name(model)] = summary
    print(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
