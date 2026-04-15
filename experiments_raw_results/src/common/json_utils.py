from __future__ import annotations

import ast
import json
from typing import Any


def parse_json_like_dict(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = ast.literal_eval(content)

    if not isinstance(parsed, dict):
        raise ValueError("Response is not a dict")
    return parsed
