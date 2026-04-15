from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sanitize_model_name(model_name: str) -> str:
    sanitized = model_name
    for ch in (":", "/", "."):
        sanitized = sanitized.replace(ch, "-")
    return sanitized


def utc_timestamp_slug() -> str:
    dt = datetime.now(timezone.utc).replace(microsecond=0)
    return dt.strftime("%Y-%m-%d_%H-%M-%S")


def append_json(payload: dict[str, Any], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("a", encoding="utf-8") as handle:
        json.dump(payload, handle)
