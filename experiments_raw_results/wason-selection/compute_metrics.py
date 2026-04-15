from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import OUTPUT_DIR


def parse_list_cell(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    if isinstance(value, float) and pd.isna(value):
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return [item.strip() for item in text.split(",") if item.strip()]
    return []


def parse_cards(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(card).strip() for card in value if str(card).strip()]
    if isinstance(value, str):
        parsed = parse_list_cell(value)
        if parsed:
            return parse_cards(parsed)
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def compute_row_fraction(categories_cell: Any, target_category: str) -> float:
    categories = [str(item) for item in parse_list_cell(categories_cell)]
    if not categories:
        return 0.0
    return sum(category == target_category for category in categories) / len(categories)


def compute_row_consistency(responses_cell: Any) -> float:
    responses = parse_list_cell(responses_cell)
    if not responses:
        return 0.0

    canonical = []
    for response in responses:
        cards = parse_cards(response)
        canonical.append(tuple(sorted(cards)))

    return 1.0 if len(set(canonical)) == 1 else 0.0


def detect_model_names(results_df: pd.DataFrame) -> list[str]:
    names: set[str] = set()
    for col in results_df.columns:
        if col.endswith("_categories"):
            names.add(col[: -len("_categories")])
        elif col.endswith("_responses"):
            names.add(col[: -len("_responses")])
    return sorted(names)


def compute_metrics_for_results(results_df: pd.DataFrame) -> pd.DataFrame:
    model_names = detect_model_names(results_df)
    metrics_list: list[dict[str, float | str]] = []

    for model_name in model_names:
        categories_col = f"{model_name}_categories"
        responses_col = f"{model_name}_responses"

        if categories_col not in results_df.columns or responses_col not in results_df.columns:
            continue

        ema = results_df[categories_col].map(lambda cell: compute_row_fraction(cell, "CORRECT")).mean()
        mbi = results_df[categories_col].map(lambda cell: compute_row_fraction(cell, "MATCHING_BIAS")).mean()
        cbr = results_df[categories_col].map(lambda cell: compute_row_fraction(cell, "CONFIRMATION_BIAS")).mean()
        consistency_rate = results_df[responses_col].map(compute_row_consistency).mean()

        metrics_list.append(
            {
                "model": model_name,
                "EMA": float(ema),
                "MBI": float(mbi),
                "CBR": float(cbr),
                "consistency_rate": float(consistency_rate),
            }
        )

    if not metrics_list:
        return pd.DataFrame()

    return pd.DataFrame(metrics_list).set_index("model")


def compute_metrics(output_dir: Path) -> None:
    for sheet_dir in output_dir.iterdir():
        if not sheet_dir.is_dir():
            continue

        results_path = sheet_dir / "results.csv"
        if not results_path.exists():
            continue

        results_df = pd.read_csv(results_path)
        metrics_df = compute_metrics_for_results(results_df)
        if metrics_df.empty:
            continue

        metrics_df.to_csv(sheet_dir / "metrics.csv")
        print(f"[{sheet_dir.name}] Metrics updated for {len(metrics_df)} models")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute Wason Selection metrics from local results.csv files")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Experiment output directory containing sheet subfolders",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    compute_metrics(args.output_dir)


if __name__ == "__main__":
    main()
