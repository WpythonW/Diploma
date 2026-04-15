from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import CATEGORY_COLUMN, OUTPUT_DIR, RULES_COLUMN, RULES_SHEET_GID, SHEET_ID
from metrics import compute_category_metrics, compute_metrics, load_and_flatten
from src.common.google_sheets import download_google_sheet_csv


def resolve_column_name(df: pd.DataFrame, preferred: str, aliases: list[str] | None = None) -> str | None:
    candidates = [preferred] + (aliases or [])
    normalized = {str(column).strip().casefold(): column for column in df.columns}
    for candidate in candidates:
        resolved = normalized.get(candidate.strip().casefold())
        if resolved is not None:
            return str(resolved)
    return None


def load_rule_categories(
    sheet_id: str,
    gid: int,
    rules_column: str,
    category_column: str,
) -> dict[str, str]:
    df = download_google_sheet_csv(sheet_id, gid)
    if rules_column not in df.columns:
        raise KeyError(f"Column '{rules_column}' not found. Available columns: {list(df.columns)}")
    resolved_category_column = resolve_column_name(
        df,
        category_column,
        aliases=["Тип", "Категория", "Rule Category", "Rule Type", "Type"],
    )
    if resolved_category_column is None:
        raise KeyError(
            f"Category column '{category_column}' not found. Available columns: {list(df.columns)}"
        )

    mapping: dict[str, str] = {}
    for _, row in df.iterrows():
        rule_code = str(row[rules_column]).strip()
        category = str(row[resolved_category_column]).strip()
        if rule_code and rule_code.lower() != "nan":
            mapping[rule_code] = category if category and category.lower() != "nan" else "Uncategorized"
    return mapping


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute 2-4-6 metrics from experiment JSON files")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory containing per-model output folders",
    )
    parser.add_argument(
        "--metrics-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for generated metrics tables",
    )
    parser.add_argument("--sheet-id", default=None)
    parser.add_argument("--gid", type=int, default=RULES_SHEET_GID)
    parser.add_argument("--rules-column", default=RULES_COLUMN)
    parser.add_argument("--category-column", default=CATEGORY_COLUMN)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.metrics_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted(args.output_dir.glob("**/trial_results.json"))
    if not json_files:
        raise FileNotFoundError(f"No per-model trial_results.json files found in {args.output_dir}")

    fallback_rule_categories: dict[str, str] = {}
    if args.sheet_id:
        fallback_rule_categories = load_rule_categories(
            args.sheet_id,
            args.gid,
            args.rules_column,
            args.category_column,
        )
    elif args.output_dir == OUTPUT_DIR:
        try:
            fallback_rule_categories = load_rule_categories(
                SHEET_ID,
                args.gid,
                args.rules_column,
                args.category_column,
            )
        except Exception:
            fallback_rule_categories = {}

    dataframes = [load_and_flatten(path, fallback_rule_categories) for path in json_files]
    df_all = pd.concat(dataframes, ignore_index=True)

    metrics_df, per_turn_df = compute_metrics(df_all)
    category_metrics_df, per_turn_category_df = compute_category_metrics(df_all)

    metrics_df.to_csv(args.metrics_dir / "metrics_246.csv", index=False)
    per_turn_df.to_csv(args.metrics_dir / "per_turn_246.csv", index=False)
    category_metrics_df.to_csv(args.metrics_dir / "metrics_246_by_category.csv", index=False)
    per_turn_category_df.to_csv(args.metrics_dir / "per_turn_246_by_category.csv", index=False)

    print(f"Saved metrics to {args.metrics_dir}")


if __name__ == "__main__":
    main()
