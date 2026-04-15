from __future__ import annotations

import io

import pandas as pd
import requests


def build_gviz_csv_url(sheet_id: str, gid: int) -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"


def download_google_sheet_csv(sheet_id: str, gid: int, *, timeout: int = 30) -> pd.DataFrame:
    url = build_gviz_csv_url(sheet_id, gid)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    response.encoding = "utf-8"
    return pd.read_csv(io.StringIO(response.text), usecols=lambda col: "Unnamed:" not in col)
