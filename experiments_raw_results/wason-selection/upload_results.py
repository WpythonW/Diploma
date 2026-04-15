from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import gspread
import pandas as pd
from google.auth import default as google_auth_default

from config import EXPERIMENT_SHEETS, OUTPUT_DIR, SHEET_ID, SHEET_URL


def init_gspread() -> gspread.Client:
    try:
        from google.colab import auth as colab_auth  # type: ignore

        colab_auth.authenticate_user()
    except Exception:
        pass

    creds, _ = google_auth_default()
    return gspread.authorize(creds)


def upload_to_sheet(sh: gspread.Spreadsheet, df: pd.DataFrame, sheet_title: str, color: str) -> None:
    worksheets = [ws.title for ws in sh.worksheets()]

    if sheet_title in worksheets:
        ws = sh.worksheet(sheet_title)
    else:
        ws = sh.add_worksheet(title=sheet_title, rows=1000, cols=50)

    ws.clear()
    ws.update([df.columns.values.tolist()] + df.values.tolist())
    ws.update_tab_color(color)


def upload_all_results(
    sheet_url: str,
    sheets_config: dict[str, dict[str, Any]],
    output_dir: Path,
) -> None:
    gc = init_gspread()
    sh = gc.open_by_url(sheet_url)

    for dataset_name, config in sheets_config.items():
        dataset_dir = output_dir / dataset_name
        if not dataset_dir.exists():
            print(f"[{dataset_name}] Skip missing folder: {dataset_dir}")
            continue

        results_path = dataset_dir / "results.csv"
        metrics_path = dataset_dir / "metrics.csv"
        stats_path = dataset_dir / "stats.csv"

        if not results_path.exists() or not metrics_path.exists():
            print(f"[{dataset_name}] Skip missing required files")
            continue

        results_df = pd.read_csv(results_path)
        metrics_df = pd.read_csv(metrics_path)
        stats_df = pd.read_csv(stats_path) if stats_path.exists() else pd.DataFrame()

        print(f"[{dataset_name}] Uploading to Google Sheets")
        upload_to_sheet(sh, results_df, config["results_sheet"], config["color"])
        if not stats_df.empty:
            upload_to_sheet(sh, stats_df, config["stats_sheet"], config["color"])
        upload_to_sheet(sh, metrics_df, config["metrics_sheet"], config["color"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload Wason Selection local results to Google Sheets")
    parser.add_argument("--sheet-id", default=SHEET_ID, help="Google Sheet ID where results are uploaded")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Directory with local experiment artifacts")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sheet_url = f"https://docs.google.com/spreadsheets/d/{args.sheet_id}/edit"
    if args.sheet_id == SHEET_ID:
        sheet_url = SHEET_URL
    upload_all_results(sheet_url, EXPERIMENT_SHEETS, args.output_dir)


if __name__ == "__main__":
    main()
