from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import EXPERIMENT_SHEETS, INPUT_DIR, SHEET_ID
from src.common.google_sheets import download_google_sheet_csv


def load_sheet(sheet_id: str, gid: int) -> pd.DataFrame:
    return download_google_sheet_csv(sheet_id, gid)


def download_all_inputs(
    sheet_id: str,
    sheets_config: dict[str, dict[str, Any]],
    input_dir: Path,
    force: bool,
) -> None:
    input_dir.mkdir(parents=True, exist_ok=True)

    for dataset_name, config in sheets_config.items():
        csv_path = input_dir / f"{dataset_name}.csv"
        if csv_path.exists() and not force:
            print(f"[{dataset_name}] Skip existing file: {csv_path}")
            continue

        df = load_sheet(sheet_id, config["gid"])
        df.to_csv(csv_path, index=False)
        print(f"[{dataset_name}] Saved: {csv_path} ({len(df)} rows)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Wason Selection input CSVs from Google Sheets")
    parser.add_argument("--sheet-id", default=SHEET_ID, help="Google Sheet ID with source datasets")
    parser.add_argument("--input-dir", type=Path, default=INPUT_DIR, help="Directory for local input CSV files")
    parser.add_argument("--force", action="store_true", help="Overwrite existing local CSV files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    download_all_inputs(args.sheet_id, EXPERIMENT_SHEETS, args.input_dir, args.force)


if __name__ == "__main__":
    main()
