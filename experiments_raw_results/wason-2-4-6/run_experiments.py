from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common_config import OPENROUTER_API_ENV_VAR, get_openrouter_api_key
from config import (
    CATEGORY_COLUMN,
    DEFAULT_MAX_TURNS,
    DEFAULT_MODELS,
    MAX_TEST_VALUE,
    MIN_TEST_VALUE,
    OUTPUT_DIR,
    RULES_COLUMN,
    RULES_SHEET_GID,
    SHEET_ID,
)
from prompts import SYSTEM_PROMPT_ADAPTIVE, SYSTEM_PROMPT_BASELINE, SYSTEM_PROMPT_JSON_SUFFIX
from src.common.google_sheets import download_google_sheet_csv
from src.common.openrouter import create_async_openrouter_client, create_openrouter_completion


@dataclass
class Step:
    turn: int
    hypothesis: str
    test: list[int]
    expected: bool
    actual: bool
    surprised: bool
    h_in_r: float
    r_in_h: float
    distance: float
    delta: float
    iou: float
    tokens: dict[str, int]


@dataclass
class Trial:
    model: str
    rule_code: str
    success: bool
    turns: int
    steps: list[Step]
    tokens: dict[str, int]
    error: str | None = None


@dataclass(frozen=True)
class RuleSpec:
    code: str
    category: str


def slugify_model_name(model: str) -> str:
    return model.replace("/", "__").replace(":", "_")


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


RULES_MANIFEST_FILENAME = "rules_manifest.csv"


def get_run_output_dir(output_dir: Path, prompt_style: str, reasoning_effort: str) -> Path:
    return output_dir / prompt_style / reasoning_effort


def get_output_paths(output_dir: Path) -> dict[str, Path]:
    return {
        "root": output_dir,
        "status_registry_csv": output_dir / "model_run_status.csv",
        "metrics_csv": output_dir / "metrics_246.csv",
        "per_turn_csv": output_dir / "per_turn_246.csv",
        "category_metrics_csv": output_dir / "metrics_246_by_category.csv",
        "per_turn_category_csv": output_dir / "per_turn_246_by_category.csv",
        "rules_manifest_csv": output_dir / RULES_MANIFEST_FILENAME,
    }


def get_model_output_paths(output_dir: Path, model: str) -> dict[str, Path]:
    model_dir = output_dir / slugify_model_name(model)
    return {
        "model_dir": model_dir,
        "trial_results_json": model_dir / "trial_results.json",
        "summary_json": model_dir / "summary.json",
        "raw_responses_jsonl": model_dir / "raw_responses.jsonl",
        "format_errors_jsonl": model_dir / "format_errors.jsonl",
        "stats_csv": model_dir / "stats.csv",
    }


def load_status_registry(status_csv: Path) -> pd.DataFrame:
    if status_csv.exists():
        return pd.read_csv(status_csv)
    return pd.DataFrame(
        columns=[
            "model",
            "model_slug",
            "prompt_style",
            "reasoning_effort",
            "status",
            "updated_at",
            "n_rules",
            "summary_path",
            "message",
        ]
    )


def save_status_registry(status_csv: Path, registry_df: pd.DataFrame) -> None:
    status_csv.parent.mkdir(parents=True, exist_ok=True)
    registry_df.sort_values(by=["model_slug"], inplace=True)
    registry_df.to_csv(status_csv, index=False)


def upsert_status(
    registry_df: pd.DataFrame,
    *,
    model: str,
    prompt_style: str,
    reasoning_effort: str,
    status: str,
    n_rules: int | None = None,
    summary_path: Path | None = None,
    message: str = "",
) -> pd.DataFrame:
    row = {
        "model": model,
        "model_slug": slugify_model_name(model),
        "prompt_style": prompt_style,
        "reasoning_effort": reasoning_effort,
        "status": status,
        "updated_at": utc_now_iso(),
        "n_rules": n_rules,
        "summary_path": str(summary_path) if summary_path is not None else "",
        "message": message,
    }
    key_columns = ["model_slug", "prompt_style", "reasoning_effort"]
    if registry_df.empty:
        return pd.concat([registry_df, pd.DataFrame([row])], ignore_index=True)

    updated = registry_df.copy()
    if not all(column in updated.columns for column in key_columns):
        for column in key_columns:
            if column not in updated.columns:
                updated[column] = ""

    mask = (
        (updated["model_slug"].astype(str) == row["model_slug"])
        & (updated["prompt_style"].astype(str) == row["prompt_style"])
        & (updated["reasoning_effort"].astype(str) == row["reasoning_effort"])
    )
    if not mask.any():
        return pd.concat([updated, pd.DataFrame([row])], ignore_index=True)

    for key, value in row.items():
        updated.loc[mask, key] = value
    return updated


def is_model_run_complete(output_dir: Path, model: str, expected_rules: int) -> tuple[bool, str]:
    paths = get_model_output_paths(output_dir, model)
    required_files = [
        paths["trial_results_json"],
        paths["summary_json"],
        paths["raw_responses_jsonl"],
        paths["format_errors_jsonl"],
        paths["stats_csv"],
    ]
    missing = [path.name for path in required_files if not path.exists()]
    if missing:
        return False, f"missing files: {', '.join(missing)}"

    try:
        data = json.loads(paths["trial_results_json"].read_text(encoding="utf-8"))
        summary = json.loads(paths["summary_json"].read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"could not validate cached outputs: {exc}"

    processed_rules = int(summary.get("n_processed_rules", -1))
    if processed_rules != expected_rules:
        return False, f"summary n_processed_rules mismatch: {summary.get('n_processed_rules')}"

    max_turns = int(summary.get("max_turns", DEFAULT_MAX_TURNS))
    stop_iou = float(summary.get("stop_iou", 0.95))
    failed_rules = load_failed_rules(paths["format_errors_jsonl"])
    completed_rules, _, invalid_rules, recomputed_processed, _ = summarize_results(
        data,
        failed_rules,
        stop_iou=stop_iou,
        max_turns=max_turns,
    )
    if invalid_rules != int(summary.get("n_invalid_rules", -1)):
        return False, f"summary n_invalid_rules mismatch: {summary.get('n_invalid_rules')}"
    if recomputed_processed != expected_rules:
        return False, f"processed rules mismatch: {completed_rules} valid + {invalid_rules} invalid"
    return True, "validated existing outputs"


def safe_eval(func: Any, x: int, y: int, z: int) -> bool:
    try:
        return bool(func(x, y, z))
    except Exception:
        return False


def generate_samples(n: int = 50_000) -> np.ndarray:
    return np.random.randint(MIN_TEST_VALUE, MAX_TEST_VALUE + 1, (n, 3))


def compute_iou(r_vec: np.ndarray, h_vec: np.ndarray) -> float:
    intersection = int((r_vec & h_vec).sum())
    union = int((r_vec | h_vec).sum())
    return intersection / max(union, 1)


def compare_sets(R: Any, H: Any, n: int = 200_000) -> tuple[float, float, float, float]:
    samples = generate_samples(n)
    r_vec = np.array([safe_eval(R, *s) for s in samples], dtype=bool)
    h_vec = np.array([safe_eval(H, *s) for s in samples], dtype=bool)

    both = int((r_vec & h_vec).sum())
    h_in_r = both / max(int(h_vec.sum()), 1)
    r_in_h = both / max(int(r_vec.sum()), 1)
    dist = float(np.sqrt((1 - h_in_r) ** 2 + (1 - r_in_h) ** 2))
    iou = compute_iou(r_vec, h_vec)
    return round(h_in_r, 4), round(r_in_h, 4), round(dist, 4), round(iou, 4)


def parse_response(text: str) -> tuple[str, list[int]]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines_raw = stripped.splitlines()
        if len(lines_raw) >= 3 and lines_raw[0].startswith("```") and lines_raw[-1].strip() == "```":
            stripped = "\n".join(lines_raw[1:-1]).strip()

    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    hypothesis = next((line[2:].strip() for line in lines if line.startswith("H:")), None)
    test_str = next((line[2:].strip() for line in lines if line.startswith("T:")), None)
    if not hypothesis or not test_str:
        raise ValueError(f"Failed to parse response: {text}")

    test_obj = eval(test_str)
    if not isinstance(test_obj, list) or len(test_obj) != 3:
        raise ValueError(f"Invalid test triple: {test_obj}")

    test = [int(v) for v in test_obj]
    if any(v < MIN_TEST_VALUE or v > MAX_TEST_VALUE for v in test):
        raise ValueError(f"Test values must be in [{MIN_TEST_VALUE}..{MAX_TEST_VALUE}], got {test}")
    return hypothesis, test


def parse_json_response(text: str) -> tuple[str, list[int]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse JSON response: {text}") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"JSON response must be an object, got: {type(payload).__name__}")

    hypothesis = payload.get("hypothesis")
    test_obj = payload.get("test")
    if not isinstance(hypothesis, str) or not hypothesis.strip():
        raise ValueError(f"JSON response missing valid 'hypothesis': {payload}")
    if not isinstance(test_obj, list) or len(test_obj) != 3:
        raise ValueError(f"JSON response missing valid 'test': {payload}")

    try:
        test = [int(v) for v in test_obj]
    except Exception as exc:
        raise ValueError(f"JSON response has non-integer test values: {payload}") from exc
    if any(v < MIN_TEST_VALUE or v > MAX_TEST_VALUE for v in test):
        raise ValueError(f"Test values must be in [{MIN_TEST_VALUE}..{MAX_TEST_VALUE}], got {test}")
    return hypothesis.strip(), test


def parse_model_response(text: str, response_mode: str) -> tuple[str, list[int]]:
    if response_mode == "json":
        return parse_json_response(text)
    return parse_response(text)


def compile_hypothesis(hyp_code: str) -> Any:
    try:
        return eval(hyp_code)
    except Exception as exc:
        raise ValueError(f"Failed to compile hypothesis: {hyp_code}") from exc


def resolve_column_name(df: pd.DataFrame, preferred: str, aliases: list[str] | None = None) -> str | None:
    candidates = [preferred] + (aliases or [])
    normalized = {str(column).strip().casefold(): column for column in df.columns}
    for candidate in candidates:
        resolved = normalized.get(candidate.strip().casefold())
        if resolved is not None:
            return str(resolved)
    return None


def load_rule_specs(
    sheet_id: str,
    gid: int,
    rules_column: str,
    category_column: str | None,
    limit: int | None = None,
) -> list[RuleSpec]:
    df: pd.DataFrame = download_google_sheet_csv(sheet_id, gid)
    if rules_column not in df.columns:
        raise KeyError(f"Column '{rules_column}' not found. Available columns: {list(df.columns)}")

    resolved_category_column = None
    if category_column:
        resolved_category_column = resolve_column_name(
            df,
            category_column,
            aliases=["Тип", "Категория", "Rule Category", "Rule Type", "Type"],
        )

    specs: list[RuleSpec] = []
    for _, row in df.iterrows():
        rule_code = str(row[rules_column]).strip()
        if not rule_code or rule_code.lower() == "nan":
            continue
        category = "Uncategorized"
        if resolved_category_column is not None:
            raw_category = str(row[resolved_category_column]).strip()
            if raw_category and raw_category.lower() != "nan":
                category = raw_category
        specs.append(RuleSpec(code=rule_code, category=category))

    return specs[:limit] if limit is not None else specs


def load_rule_filter(path: Path) -> list[str]:
    rules: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        rule = line.strip()
        if not rule or rule.startswith("#"):
            continue
        rules.append(rule)
    return rules


def read_results(path: Path) -> dict[str, list[dict[str, Any]]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_results(path: Path, payload: dict[str, list[dict[str, Any]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_failed_rules(path: Path) -> set[str]:
    if not path.exists():
        return set()
    failed_rules: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("fatal", True) is not True:
                continue
            rule = row.get("rule")
            if isinstance(rule, str) and rule:
                failed_rules.add(rule)
    return failed_rules


def is_terminal_trial(steps: list[Step], stop_iou: float, max_turns: int) -> bool:
    if not steps:
        return False
    return steps[-1].iou > stop_iou or len(steps) >= max_turns


def summarize_results(
    result_json: dict[str, list[dict[str, Any]]],
    failed_rules: set[str],
    *,
    stop_iou: float,
    max_turns: int,
) -> tuple[int, int, int, int, dict[str, int]]:
    completed_rules = 0
    successes = 0
    total_turns = 0
    total_tokens = {"prompt": 0, "completion": 0, "reasoning": 0}

    for rule_code, raw_steps in result_json.items():
        steps = convert_raw_steps(raw_steps)
        if not steps:
            continue
        if rule_code not in failed_rules and is_terminal_trial(steps, stop_iou, max_turns):
            completed_rules += 1
            total_turns += len(steps)
            if steps[-1].iou > stop_iou:
                successes += 1

        for step in steps:
            step_tokens = step.tokens
            total_tokens["prompt"] += int(step_tokens.get("prompt", 0))
            total_tokens["completion"] += int(step_tokens.get("completion", 0))
            total_tokens["reasoning"] += int(step_tokens.get("reasoning", 0))

    invalid_rules = len(failed_rules)
    processed_rules = completed_rules + invalid_rules
    return completed_rules, successes, invalid_rules, processed_rules, total_tokens


def get_system_prompt(style: str, response_mode: str = "text") -> str:
    if style == "baseline":
        prompt = SYSTEM_PROMPT_BASELINE
    elif style == "adaptive":
        prompt = SYSTEM_PROMPT_ADAPTIVE
    else:
        raise ValueError(f"Unsupported prompt style: {style}")
    if response_mode == "json":
        return f"{prompt}{SYSTEM_PROMPT_JSON_SUFFIX}"
    if response_mode == "text":
        return prompt
    raise ValueError(f"Unsupported response mode: {response_mode}")


def build_response_format(response_mode: str) -> dict[str, Any] | None:
    if response_mode == "text":
        return None
    if response_mode != "json":
        raise ValueError(f"Unsupported response mode: {response_mode}")
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "wason_246_turn",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "hypothesis": {"type": "string"},
                    "test": {
                        "type": "array",
                        "items": {"type": "integer"},
                    },
                },
                "required": ["hypothesis", "test"],
                "additionalProperties": False,
            },
        },
    }


def normalize_provider_list(values: list[str] | None) -> list[str] | None:
    if not values:
        return None
    normalized: list[str] = []
    for value in values:
        parts = [part.strip().lower() for part in value.split(",")]
        normalized.extend(part for part in parts if part)
    return normalized or None


def build_provider_config(args: argparse.Namespace) -> dict[str, Any] | None:
    provider_order = normalize_provider_list(args.provider_order)
    provider_only = normalize_provider_list(args.provider_only)
    if provider_order and provider_only:
        raise ValueError("Use either --provider-order or --provider-only, not both")

    provider: dict[str, Any] = {}
    if provider_order:
        provider["order"] = provider_order
    if provider_only:
        provider["only"] = provider_only
    if args.provider_allow_fallbacks is not None:
        provider["allow_fallbacks"] = args.provider_allow_fallbacks == "true"
    return provider or None


def build_repair_prompt(error: str) -> str:
    return (
        "Your previous answer was invalid.\n"
        f"Error: {error}\n"
        "Re-answer ONLY with a fenced ```python``` block containing exactly:\n"
        "H: lambda x,y,z: <boolean expression>\n"
        "T: [x, y, z]\n"
        "Use only integers from 1 to 1000."
    )


def build_json_repair_prompt(error: str) -> str:
    return (
        "Your previous answer was invalid.\n"
        f"Error: {error}\n"
        "Re-answer ONLY with a JSON object of exactly this shape:\n"
        '{"hypothesis":"lambda x,y,z: <boolean expression>","test":[x,y,z]}\n'
        "Use only integers from 1 to 1000. Do not add markdown fences."
    )


async def call_model(
    client: Any,
    model: str,
    messages: list[dict[str, str]],
    response_format: dict[str, Any] | None,
    reasoning_effort: str,
    provider: dict[str, Any] | None = None,
) -> tuple[str, dict[str, int]]:
    response = await create_openrouter_completion(
        client,
        model=model,
        messages=messages,
        temperature=0,
        response_format=response_format,
        reasoning_effort=reasoning_effort,
        provider=provider,
    )
    choices = getattr(response, "choices", None)
    if not choices:
        dump = response.model_dump() if hasattr(response, "model_dump") else repr(response)
        raise ValueError(f"OpenRouter returned no choices: {dump}")

    message = getattr(choices[0], "message", None)
    if message is None:
        dump = response.model_dump() if hasattr(response, "model_dump") else repr(response)
        raise ValueError(f"OpenRouter returned choice without message: {dump}")

    content = message.content or ""
    usage = response.usage
    details = getattr(usage, "completion_tokens_details", None)
    tokens = {
        "prompt": int(getattr(usage, "prompt_tokens", 0) or 0),
        "completion": int(getattr(usage, "completion_tokens", 0) or 0),
        "reasoning": int(getattr(details, "reasoning_tokens", 0) or 0),
    }
    return content, tokens


async def run_trial(
    client: Any,
    *,
    model: str,
    rule_code: str,
    system_prompt: str,
    reasoning_effort: str,
    response_mode: str,
    response_format: dict[str, Any] | None,
    provider: dict[str, Any] | None,
    max_turns: int,
    stop_iou: float,
    request_timeout_seconds: float,
    repair_attempts: int,
    existing_steps: list[Step] | None = None,
    raw_responses_path: Path,
    format_errors_path: Path,
    on_step: Any | None = None,
) -> Trial:
    R = eval(rule_code)
    steps: list[Step] = list(existing_steps or [])

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "True"},
    ]
    for s in steps:
        messages.append({"role": "assistant", "content": f"H: {s.hypothesis}\nT: {s.test}"})
        messages.append(
            {
                "role": "user",
                "content": f"({s.test[0]}, {s.test[1]}, {s.test[2]}) -> {'True' if s.actual else 'False'}",
            }
        )

    total_tokens = {
        "prompt": sum(s.tokens.get("prompt", 0) for s in steps),
        "completion": sum(s.tokens.get("completion", 0) for s in steps),
        "reasoning": sum(s.tokens.get("reasoning", 0) for s in steps),
    }
    prev_dist = steps[-1].distance if steps else 1.4142
    start_turn = len(steps) + 1

    for turn in range(start_turn, max_turns + 1):
        turn_messages = list(messages)
        raw_content: str | None = None
        step_tokens = {"prompt": 0, "completion": 0, "reasoning": 0}
        last_error: str | None = None
        hypothesis: str | None = None
        test: list[int] | None = None
        H: Any | None = None

        for attempt in range(repair_attempts + 1):
            try:
                raw_content, attempt_tokens = await asyncio.wait_for(
                    call_model(
                        client,
                        model,
                        turn_messages,
                        response_format,
                        reasoning_effort=reasoning_effort,
                        provider=provider,
                    ),
                    timeout=request_timeout_seconds,
                )
                append_jsonl(
                    raw_responses_path,
                    {
                        "model": model,
                        "rule": rule_code,
                        "turn": turn,
                        "attempt": attempt + 1,
                        "response_text": raw_content,
                        "tokens": attempt_tokens,
                    },
                )
                for key in total_tokens:
                    total_tokens[key] += attempt_tokens[key]
                    step_tokens[key] += attempt_tokens[key]

                hypothesis, test = parse_model_response(raw_content, response_mode)
                H = compile_hypothesis(hypothesis)
                last_error = None
                break
            except Exception as exc:
                last_error = f"API error: {exc}" if raw_content is None else str(exc)
                append_jsonl(
                    format_errors_path,
                    {
                        "model": model,
                        "rule": rule_code,
                        "turn": turn,
                        "attempt": attempt + 1,
                        "response_text": raw_content,
                        "error": last_error,
                        "fatal": attempt >= repair_attempts,
                    },
                )
                if attempt >= repair_attempts:
                    return Trial(
                        model=model,
                        rule_code=rule_code,
                        success=False,
                        turns=len(steps),
                        steps=steps,
                        tokens=total_tokens,
                        error=last_error,
                    )
                if raw_content is not None:
                    turn_messages.append({"role": "assistant", "content": raw_content})
                repair_prompt = (
                    build_json_repair_prompt(last_error)
                    if response_mode == "json"
                    else build_repair_prompt(last_error)
                )
                turn_messages.append({"role": "user", "content": repair_prompt})
                raw_content = None

        assert hypothesis is not None and test is not None and H is not None

        expected = safe_eval(H, *test)
        actual = safe_eval(R, *test)
        h_in_r, r_in_h, dist, iou = compare_sets(R, H)

        step = Step(
            turn=turn,
            hypothesis=hypothesis,
            test=test,
            expected=expected,
            actual=actual,
            surprised=(expected != actual),
            h_in_r=h_in_r,
            r_in_h=r_in_h,
            distance=dist,
            delta=round(dist - prev_dist, 4),
            iou=iou,
            tokens=step_tokens,
        )
        steps.append(step)
        if on_step is not None:
            on_step(rule_code, steps)

        messages.append({"role": "assistant", "content": f"H: {hypothesis}\nT: {test}"})
        messages.append(
            {"role": "user", "content": f"({test[0]}, {test[1]}, {test[2]}) -> {'True' if actual else 'False'}"}
        )

        prev_dist = dist
        if iou > stop_iou:
            break

    success = bool(steps and steps[-1].iou > stop_iou)
    return Trial(
        model=model,
        rule_code=rule_code,
        success=success,
        turns=len(steps),
        steps=steps,
        tokens=total_tokens,
        error=None,
    )


async def run_rule_task(
    *,
    idx: int,
    rule_code: str,
    client: Any,
    model: str,
    system_prompt: str,
    reasoning_effort: str,
    response_mode: str,
    response_format: dict[str, Any] | None,
    provider: dict[str, Any] | None,
    max_turns: int,
    stop_iou: float,
    request_timeout_seconds: float,
    repair_attempts: int,
    existing_steps: list[Step],
    raw_responses_path: Path,
    format_errors_path: Path,
    on_step: Any | None = None,
) -> tuple[int, str, Trial]:
    trial = await run_trial(
        client,
        model=model,
        rule_code=rule_code,
        system_prompt=system_prompt,
        reasoning_effort=reasoning_effort,
        response_mode=response_mode,
        response_format=response_format,
        provider=provider,
        max_turns=max_turns,
        stop_iou=stop_iou,
        request_timeout_seconds=request_timeout_seconds,
        repair_attempts=repair_attempts,
        existing_steps=existing_steps,
        raw_responses_path=raw_responses_path,
        format_errors_path=format_errors_path,
        on_step=on_step,
    )
    return idx, rule_code, trial


def convert_raw_steps(raw_steps: list[dict[str, Any]]) -> list[Step]:
    normalized: list[Step] = []
    for raw in raw_steps:
        if "tokens" not in raw and "step_tokens" in raw:
            raw["tokens"] = raw["step_tokens"]
        normalized.append(Step(**raw))
    return normalized


async def run_experiments_for_model(
    *,
    model: str,
    rule_specs: list[RuleSpec],
    api_key: str,
    output_dir: Path,
    system_prompt: str,
    prompt_style: str,
    reasoning_effort: str,
    response_mode: str,
    response_format: dict[str, Any] | None,
    provider: dict[str, Any] | None,
    max_turns: int,
    stop_iou: float,
    request_timeout_seconds: float,
    repair_attempts: int,
    max_concurrency: int,
) -> dict[str, Any]:
    model_paths = get_model_output_paths(output_dir, model)
    model_paths["model_dir"].mkdir(parents=True, exist_ok=True)
    result_json = read_results(model_paths["trial_results_json"])
    model_paths["raw_responses_jsonl"].touch(exist_ok=True)
    model_paths["format_errors_jsonl"].touch(exist_ok=True)
    failed_rules = load_failed_rules(model_paths["format_errors_jsonl"])
    rules = [spec.code for spec in rule_specs]

    client = create_async_openrouter_client(api_key)
    _, _, _, processed_before, _ = summarize_results(
        result_json,
        failed_rules,
        stop_iou=stop_iou,
        max_turns=max_turns,
    )
    progress = tqdm(
        total=len(rules),
        initial=processed_before,
        desc=slugify_model_name(model),
        unit="rule",
    )

    tqdm.write(f"[{model}] Output: {model_paths['model_dir']}")
    pending_rules: list[tuple[int, str, list[Step]]] = []
    for idx, rule_code in enumerate(rules, start=1):
        existing_raw = result_json.get(rule_code, [])
        existing_steps = convert_raw_steps(existing_raw)
        if rule_code in failed_rules:
            continue
        if existing_steps and (existing_steps[-1].iou > stop_iou or len(existing_steps) >= max_turns):
            continue
        pending_rules.append((idx, rule_code, existing_steps))

    def persist_partial(rule_code: str, steps: list[Step]) -> None:
        result_json[rule_code] = [asdict(step) for step in steps]
        write_results(model_paths["trial_results_json"], result_json)

    try:
        semaphore = asyncio.Semaphore(max(1, max_concurrency))

        async def run_bounded_task(idx: int, rule_code: str, existing_steps: list[Step]) -> tuple[int, str, Trial]:
            async with semaphore:
                return await run_rule_task(
                    idx=idx,
                    rule_code=rule_code,
                    client=client,
                    model=model,
                    system_prompt=system_prompt,
                    reasoning_effort=reasoning_effort,
                    response_mode=response_mode,
                    response_format=response_format,
                    provider=provider,
                    max_turns=max_turns,
                    stop_iou=stop_iou,
                    request_timeout_seconds=request_timeout_seconds,
                    repair_attempts=repair_attempts,
                    existing_steps=existing_steps,
                    raw_responses_path=model_paths["raw_responses_jsonl"],
                    format_errors_path=model_paths["format_errors_jsonl"],
                    on_step=persist_partial,
                )

        tasks = [
            asyncio.create_task(run_bounded_task(idx, rule_code, existing_steps))
            for idx, rule_code, existing_steps in pending_rules
        ]

        for task in asyncio.as_completed(tasks):
            idx, rule_code, trial = await task
            result_json[rule_code] = [asdict(step) for step in trial.steps]
            write_results(model_paths["trial_results_json"], result_json)
            last_iou = trial.steps[-1].iou if trial.steps else 0.0
            if trial.error:
                failed_rules.add(rule_code)
                tqdm.write(
                    f"[{model}] ({idx}/{len(rules)}) invalid response, turns={trial.turns} "
                    f"last_iou={last_iou:.3f} error={trial.error}"
                )
            else:
                tqdm.write(
                    f"[{model}] ({idx}/{len(rules)}) turns={trial.turns} success={trial.success} "
                    f"last_iou={last_iou:.3f} tokens={trial.tokens}"
                )
            progress.update(1)
    finally:
        progress.close()

    completed_rules, successes, invalid_rules, processed_rules, total_tokens = summarize_results(
        result_json,
        failed_rules,
        stop_iou=stop_iou,
        max_turns=max_turns,
    )
    total_turns = sum(
        len(convert_raw_steps(steps))
        for rule_code, steps in result_json.items()
        if rule_code not in failed_rules
        and is_terminal_trial(convert_raw_steps(steps), stop_iou, max_turns)
    )

    stats = {
        "n_rules": completed_rules,
        "n_success": successes,
        "n_invalid_rules": invalid_rules,
        "n_processed_rules": processed_rules,
        "mean_turns": round(total_turns / max(completed_rules, 1), 4),
        "prompt_tokens": total_tokens["prompt"],
        "completion_tokens": total_tokens["completion"],
        "reasoning_tokens": total_tokens["reasoning"],
    }
    pd.DataFrame([stats]).to_csv(model_paths["stats_csv"], index=False)

    summary = {
        "model": model,
        "prompt_style": prompt_style,
        "reasoning_effort": reasoning_effort,
        "provider": provider,
        "response_mode": response_mode,
        "n_rules": completed_rules,
        "n_success": successes,
        "n_invalid_rules": invalid_rules,
        "n_processed_rules": processed_rules,
        "max_turns": max_turns,
        "stop_iou": stop_iou,
        "stats": stats,
    }
    model_paths["summary_json"].write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run 2-4-6 Wason experiments and save JSON traces")
    parser.add_argument("--sheet-id", default=SHEET_ID)
    parser.add_argument("--gid", type=int, default=RULES_SHEET_GID)
    parser.add_argument("--rules-column", default=RULES_COLUMN)
    parser.add_argument("--category-column", default=CATEGORY_COLUMN)
    parser.add_argument("--rule-limit", type=int, default=None)
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument(
        "--prompt-style",
        choices=["baseline", "adaptive"],
        default="baseline",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=["none", "low", "medium", "high"],
        default="none",
    )
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    parser.add_argument("--stop-iou", type=float, default=0.95)
    parser.add_argument(
        "--request-timeout-seconds",
        type=float,
        default=120.0,
        help="Per-request timeout before a rule is marked invalid",
    )
    parser.add_argument(
        "--repair-attempts",
        type=int,
        default=2,
        help="How many repair retries to allow after an invalid response",
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument(
        "--rules-file",
        type=Path,
        default=None,
        help="Optional newline-delimited list of exact rule codes to run",
    )
    parser.add_argument(
        "--provider-order",
        nargs="+",
        default=None,
        help="Ordered OpenRouter provider slugs, e.g. crusoe cloudflare",
    )
    parser.add_argument(
        "--provider-only",
        nargs="+",
        default=None,
        help="Restrict OpenRouter routing to these provider slugs",
    )
    parser.add_argument(
        "--provider-allow-fallbacks",
        choices=["true", "false"],
        default=None,
        help="Whether OpenRouter may fall back outside the requested provider list",
    )
    parser.add_argument(
        "--api-key",
        default=get_openrouter_api_key() or "",
        help=f"OpenRouter API key (or set {OPENROUTER_API_ENV_VAR})",
    )
    parser.add_argument("--force", action="store_true", help="Rerun even if completed outputs already exist")
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=50,
        help="Maximum number of rules to query concurrently per model",
    )
    parser.add_argument(
        "--response-mode",
        choices=["text", "json"],
        default="text",
        help="Whether to ask the model for the legacy text block or structured JSON output",
    )
    return parser.parse_args()


async def async_main(args: argparse.Namespace) -> None:
    if not args.api_key:
        raise ValueError(f"Missing OpenRouter API key. Use --api-key or {OPENROUTER_API_ENV_VAR}")

    rule_specs = load_rule_specs(
        args.sheet_id,
        args.gid,
        args.rules_column,
        args.category_column,
        limit=args.rule_limit,
    )
    if not rule_specs:
        raise ValueError("No rules found in source sheet")

    if args.rules_file is not None:
        requested_rules = load_rule_filter(args.rules_file)
        requested_rule_set = set(requested_rules)
        rule_specs = [spec for spec in rule_specs if spec.code in requested_rule_set]
        missing_rules = [rule for rule in requested_rules if rule not in {spec.code for spec in rule_specs}]
        if missing_rules:
            raise ValueError(f"Requested rules not found in source sheet: {missing_rules[:3]}")
        if not rule_specs:
            raise ValueError("No rules left after applying --rules-file")

    system_prompt = get_system_prompt(args.prompt_style, args.response_mode)
    response_format = build_response_format(args.response_mode)
    provider = build_provider_config(args)
    run_output_dir = get_run_output_dir(args.output_dir, args.prompt_style, args.reasoning_effort)
    output_paths = get_output_paths(run_output_dir)
    run_output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([asdict(spec) for spec in rule_specs]).to_csv(output_paths["rules_manifest_csv"], index=False)
    registry_df = load_status_registry(output_paths["status_registry_csv"])

    print(f"Loaded {len(rule_specs)} rules")
    if provider:
        print(f"Using OpenRouter provider routing: {provider}")
    for model in args.models:
        model_paths = get_model_output_paths(run_output_dir, model)
        if not args.force:
            is_complete, reason = is_model_run_complete(run_output_dir, model, len(rule_specs))
            if is_complete:
                registry_df = upsert_status(
                    registry_df,
                    model=model,
                    prompt_style=args.prompt_style,
                    reasoning_effort=args.reasoning_effort,
                    status="completed",
                    n_rules=len(rule_specs),
                    summary_path=model_paths["summary_json"],
                    message=f"skipped rerun: {reason}",
                )
                save_status_registry(output_paths["status_registry_csv"], registry_df)
                print(f"[{model}] skip completed model")
                continue

        registry_df = upsert_status(
            registry_df,
            model=model,
            prompt_style=args.prompt_style,
            reasoning_effort=args.reasoning_effort,
            status="running",
            n_rules=len(rule_specs),
            summary_path=model_paths["summary_json"],
            message="run started",
        )
        save_status_registry(output_paths["status_registry_csv"], registry_df)

        try:
            summary = await run_experiments_for_model(
                model=model,
                rule_specs=rule_specs,
                api_key=args.api_key,
                output_dir=run_output_dir,
                system_prompt=system_prompt,
                prompt_style=args.prompt_style,
                reasoning_effort=args.reasoning_effort,
                response_mode=args.response_mode,
                response_format=response_format,
                provider=provider,
                max_turns=args.max_turns,
                stop_iou=args.stop_iou,
                request_timeout_seconds=args.request_timeout_seconds,
                repair_attempts=args.repair_attempts,
                max_concurrency=args.max_concurrency,
            )
        except Exception as exc:
            registry_df = upsert_status(
                registry_df,
                model=model,
                prompt_style=args.prompt_style,
                reasoning_effort=args.reasoning_effort,
                status="failed",
                n_rules=None,
                summary_path=model_paths["summary_json"],
                message=str(exc),
            )
            save_status_registry(output_paths["status_registry_csv"], registry_df)
            raise

        registry_df = upsert_status(
            registry_df,
            model=model,
            prompt_style=args.prompt_style,
            reasoning_effort=args.reasoning_effort,
            status="completed",
            n_rules=int(summary["n_rules"]),
            summary_path=model_paths["summary_json"],
            message=(
                f"run completed successfully; invalid_rules={summary.get('n_invalid_rules', 0)}"
            ),
        )
        save_status_registry(output_paths["status_registry_csv"], registry_df)


def main() -> None:
    args = parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
