from __future__ import annotations

import argparse
import ast
import asyncio
import json
import random
import sys
from collections import defaultdict
from datetime import UTC, datetime
from itertools import permutations
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm.asyncio import tqdm_asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common_config import (
    OPENROUTER_API_ENV_VAR,
    EXPERIMENTAL_PROPRIETARY_ENV_VAR,
    EXPERIMENTAL_OPEN_ENV_VAR,
    get_experimental_key,
    get_openrouter_api_key,
)
from src.common.openrouter import (
    create_async_openrouter_client,
    create_openrouter_completion,
    update_usage_stats,
)
from compute_metrics import compute_metrics
from config import (
    CATEGORIES,
    DEFAULT_MODELS,
    EXPERIMENT_CONFIG,
    EXPERIMENT_SHEETS,
    INPUT_DIR,
    OUTPUT_DIR,
)
from prompts import SYSTEM_PROMPT


def slugify_model_name(model: str) -> str:
    return model.replace("/", "__").replace(":", "_")


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def get_context_output_paths(output_dir: Path, sheet_name: str) -> dict[str, Path]:
    sheet_dir = output_dir / sheet_name
    return {
        "sheet_dir": sheet_dir,
        "results_csv": sheet_dir / "results.csv",
        "stats_csv": sheet_dir / "stats.csv",
        "metrics_csv": sheet_dir / "metrics.csv",
        "status_registry_csv": sheet_dir / "model_run_status.csv",
    }


def get_model_output_paths(output_dir: Path, sheet_name: str, model: str) -> dict[str, Path]:
    context_paths = get_context_output_paths(output_dir, sheet_name)
    model_dir = context_paths["sheet_dir"] / slugify_model_name(model)
    return {
        "model_dir": model_dir,
        "trial_results_csv": model_dir / "trial_results.csv",
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
            "status",
            "updated_at",
            "n_trials",
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
    status: str,
    n_trials: int | None = None,
    summary_path: Path | None = None,
    message: str = "",
) -> pd.DataFrame:
    row = {
        "model": model,
        "model_slug": slugify_model_name(model),
        "status": status,
        "updated_at": utc_now_iso(),
        "n_trials": n_trials,
        "summary_path": str(summary_path) if summary_path is not None else "",
        "message": message,
    }
    if registry_df.empty or row["model_slug"] not in set(registry_df["model_slug"].astype(str)):
        return pd.concat([registry_df, pd.DataFrame([row])], ignore_index=True)

    updated = registry_df.copy()
    mask = updated["model_slug"].astype(str) == row["model_slug"]
    for key, value in row.items():
        updated.loc[mask, key] = value
    return updated


def is_model_run_complete(output_dir: Path, sheet_name: str, model: str, expected_trials: int) -> tuple[bool, str]:
    paths = get_model_output_paths(output_dir, sheet_name, model)
    required_files = [
        paths["trial_results_csv"],
        paths["summary_json"],
        paths["raw_responses_jsonl"],
        paths["format_errors_jsonl"],
        paths["stats_csv"],
    ]
    missing = [path.name for path in required_files if not path.exists()]
    if missing:
        return False, f"missing files: {', '.join(missing)}"

    try:
        trial_df = pd.read_csv(paths["trial_results_csv"])
        summary = json.loads(paths["summary_json"].read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"could not validate cached outputs: {exc}"

    if len(trial_df) != expected_trials:
        return False, f"expected {expected_trials} trials, found {len(trial_df)}"
    if int(summary.get("n_trials", -1)) != expected_trials:
        return False, f"summary n_trials mismatch: {summary.get('n_trials')}"
    return True, "validated existing outputs"


def parse_json_mapping(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        parsed = ast.literal_eval(value)
        if isinstance(parsed, dict):
            return parsed
    raise ValueError(f"Unsupported JSON Mapping value: {value!r}")


def get_item_id(df: pd.DataFrame, row_idx: int) -> str:
    if "ID" in df.columns:
        value = df.iloc[row_idx]["ID"]
        if pd.notna(value):
            text = str(value).strip()
            if text:
                return text
    return f"T{row_idx + 1}"


def load_all_sheets(sheets_config: dict[str, dict[str, Any]]) -> dict[str, pd.DataFrame]:
    sheets: dict[str, pd.DataFrame] = {}

    for name in sheets_config:
        csv_path = INPUT_DIR / f"{name}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(
                f"Missing input CSV for '{name}': {csv_path}. "
                "Run download_inputs.py first."
            )
        df = pd.read_csv(csv_path)
        sheets[name] = df

    return sheets


def make_prompt(rule_text: str, ordered_cards: list[str]) -> str:
    return f'''Rule: "{rule_text}"
Cards: {ordered_cards}

Which cards must you turn over?
Your answer:'''


def build_card_permutations(
    mapping: dict[str, str],
    n_permutations: int,
    random_seed: int,
    row_idx: int,
) -> list[list[str]]:
    cards = list(mapping.keys())
    all_orders = [list(order) for order in permutations(cards)]

    rng = random.Random(random_seed + row_idx)
    rng.shuffle(all_orders)

    if n_permutations <= 0:
        raise ValueError("n_prompt_permutations must be >= 1")

    return all_orders[: min(n_permutations, len(all_orders))]


def classify_response(logic_set: frozenset[str], categories: dict[frozenset[str], str]) -> str:
    if logic_set in categories:
        return categories[logic_set]
    return "LOGIC_ERROR" if "not_P" in logic_set else "NOISE"


def parse_response(response_text: str, json_mapping: dict[str, str]) -> tuple[list[str], frozenset[str]]:
    normalized_text = response_text.strip()
    if "\n" in normalized_text:
        non_empty_lines = [line.strip() for line in normalized_text.splitlines() if line.strip()]
        if non_empty_lines:
            normalized_text = non_empty_lines[-1]
    if normalized_text.upper().startswith("ANSWER:"):
        normalized_text = normalized_text.split(":", 1)[1].strip()
    cards = [c.strip() for c in normalized_text.split(",") if c.strip()]
    logic_set = frozenset(
        marker for marker in (json_mapping.get(card) for card in cards) if marker is not None
    )
    return cards, logic_set


async def query_single(
    client: Any,
    model: str,
    prompt: str,
    semaphore: asyncio.Semaphore,
    stats_collector: dict[str, int],
    system_prompt: str,
    max_completion_tokens: int,
    llm_seed: int,
) -> Any:
    async with semaphore:
        try:
            response = await create_openrouter_completion(
                client,
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                seed=llm_seed,
                max_completion_tokens=max_completion_tokens,
                reasoning_effort="none",
            )

            update_usage_stats(stats_collector, response.usage)
            return response
        except Exception as exc:
            return f"ERROR: {str(exc)}"


def extract_response_text(response: Any) -> str:
    if not hasattr(response, "choices"):
        return str(response)

    choices = getattr(response, "choices", None)
    if not choices:
        return "ERROR: empty choices in model response"

    first_choice = choices[0]
    message = getattr(first_choice, "message", None)
    if message is None:
        return "ERROR: missing message in model response"

    content = getattr(message, "content", None)
    if content is None:
        return "ERROR: missing content in model response"

    return str(content)


def build_task_specs(
    result_df: pd.DataFrame,
    *,
    n_prompt_permutations: int,
    random_seed: int,
) -> list[tuple[int, int, str, dict[str, str], int, list[str]]]:
    task_specs: list[tuple[int, int, str, dict[str, str], int, list[str]]] = []
    for row_idx, row in result_df.iterrows():
        mapping = row["JSON Mapping"]
        card_orders = build_card_permutations(
            mapping=mapping,
            n_permutations=n_prompt_permutations,
            random_seed=random_seed,
            row_idx=int(row_idx),
        )
        for perm_idx, ordered_cards in enumerate(card_orders):
            prompt = make_prompt(row["Rule Text"], ordered_cards)
            llm_seed = random_seed + int(row_idx) * 10_000 + perm_idx
            task_specs.append((int(row_idx), perm_idx, prompt, mapping, llm_seed, ordered_cards))
    return task_specs


async def run_single_model(
    *,
    model: str,
    result_df: pd.DataFrame,
    task_specs: list[tuple[int, int, str, dict[str, str], int, list[str]]],
    api_key: str,
    system_prompt: str,
    categories: dict[frozenset[str], str],
    max_completion_tokens: int,
    global_request_semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    model_name = model.split("/")[-1]
    stats_collector: dict[str, int] = defaultdict(int)
    client = create_async_openrouter_client(api_key)

    try:
        tasks = [
            query_single(
                client,
                model,
                prompt,
                global_request_semaphore,
                stats_collector,
                system_prompt,
                max_completion_tokens,
                llm_seed,
            )
            for _, _, prompt, _, llm_seed, _ in task_specs
        ]
        responses = await tqdm_asyncio.gather(*tasks, desc=model_name)

        by_row_responses: list[list[list[str]]] = [[] for _ in range(len(result_df))]
        by_row_categories: list[list[str]] = [[] for _ in range(len(result_df))]
        by_row_card_orders: list[list[list[str]]] = [[] for _ in range(len(result_df))]
        trial_rows: list[dict[str, Any]] = []
        raw_rows: list[dict[str, Any]] = []
        format_error_rows: list[dict[str, Any]] = []

        for (row_idx, perm_idx, prompt, mapping, llm_seed, ordered_cards), response in zip(
            task_specs, responses, strict=False
        ):
            response_text = extract_response_text(response)
            cards, logic_set = parse_response(response_text, mapping)
            category = classify_response(logic_set, categories)
            prompt_tokens = 0
            completion_tokens = 0
            reasoning_tokens = 0
            if hasattr(response, "usage") and response.usage is not None:
                prompt_tokens = int(getattr(response.usage, "prompt_tokens", 0) or 0)
                completion_tokens = int(getattr(response.usage, "completion_tokens", 0) or 0)
                details = getattr(response.usage, "completion_tokens_details", None)
                reasoning_tokens = int(getattr(details, "reasoning_tokens", 0) or 0)

            by_row_responses[row_idx].append(cards)
            by_row_categories[row_idx].append(category)
            by_row_card_orders[row_idx].append(ordered_cards)
            trial_rows.append(
                {
                    "row_idx": row_idx,
                    "item_id": get_item_id(result_df, row_idx),
                    "permutation_idx": perm_idx,
                    "llm_seed": llm_seed,
                    "rule_text": result_df.iloc[row_idx]["Rule Text"],
                    "prompt": prompt,
                    "ordered_cards": ordered_cards,
                    "response_text": response_text,
                    "selected_cards": cards,
                    "logic_set": sorted(logic_set),
                    "category": category,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "reasoning_tokens": reasoning_tokens,
                }
            )
            raw_rows.append(
                {
                    "row_idx": row_idx,
                    "item_id": get_item_id(result_df, row_idx),
                    "permutation_idx": perm_idx,
                    "ordered_cards": ordered_cards,
                    "response_text": response_text,
                }
            )
            if not hasattr(response, "choices") or response_text.startswith("ERROR:"):
                format_error_rows.append(
                    {
                        "row_idx": row_idx,
                        "item_id": get_item_id(result_df, row_idx),
                        "permutation_idx": perm_idx,
                        "response_text": response_text,
                    }
                )

        return {
            "success": True,
            "model": model,
            "model_name": model_name,
            "stats": dict(stats_collector),
            "responses": by_row_responses,
            "categories": by_row_categories,
            "card_orders": by_row_card_orders,
            "trial_rows": trial_rows,
            "raw_rows": raw_rows,
            "format_error_rows": format_error_rows,
        }
    except Exception as exc:
        return {
            "success": False,
            "model": model,
            "model_name": model_name,
            "error": str(exc),
        }


def get_new_models(df: pd.DataFrame, models: list[str]) -> list[str]:
    existing = {
        col.replace("_categories", "")
        for col in df.columns
        if col.endswith("_categories")
    }
    return [model for model in models if model.split("/")[-1] not in existing]


async def run_experiments(
    sheet_name: str,
    df: pd.DataFrame,
    models: list[str],
    api_key: str,
    system_prompt: str,
    categories: dict[frozenset[str], str],
    output_dir: Path,
    max_completion_tokens: int,
    random_seed: int,
    n_prompt_permutations: int,
    max_concurrent_requests: int,
    force: bool,
) -> None:
    context_paths = get_context_output_paths(output_dir, sheet_name)
    sheet_dir = context_paths["sheet_dir"]
    sheet_dir.mkdir(parents=True, exist_ok=True)
    results_path = context_paths["results_csv"]
    status_csv = context_paths["status_registry_csv"]

    if results_path.exists():
        result_df = pd.read_csv(results_path)
    else:
        result_df = df.copy()
        result_df.to_csv(results_path, index=False)

    result_df["JSON Mapping"] = result_df["JSON Mapping"].map(parse_json_mapping)

    expected_trials = len(result_df) * n_prompt_permutations
    registry_df = load_status_registry(status_csv)

    new_models: list[str] = []
    for model in get_new_models(result_df, models):
        if force:
            new_models.append(model)
            continue
        is_complete, reason = is_model_run_complete(output_dir, sheet_name, model, expected_trials)
        model_paths = get_model_output_paths(output_dir, sheet_name, model)
        if is_complete:
            registry_df = upsert_status(
                registry_df,
                model=model,
                status="completed",
                n_trials=expected_trials,
                summary_path=model_paths["summary_json"],
                message=f"skipped rerun: {reason}",
            )
        else:
            new_models.append(model)

    save_status_registry(status_csv, registry_df)
    if not new_models:
        print(f"[{sheet_name}] All models already tested")
        return

    print(f"[{sheet_name}] New models: {new_models}")
    all_stats: dict[str, dict[str, int]] = {}
    task_specs = build_task_specs(
        result_df,
        n_prompt_permutations=n_prompt_permutations,
        random_seed=random_seed,
    )
    global_request_semaphore = asyncio.Semaphore(max_concurrent_requests)
    pending_tasks: list[asyncio.Task[dict[str, Any]]] = []

    for model in new_models:
        model_name = model.split("/")[-1]
        model_paths = get_model_output_paths(output_dir, sheet_name, model)
        model_paths["model_dir"].mkdir(parents=True, exist_ok=True)
        registry_df = upsert_status(
            registry_df,
            model=model,
            status="running",
            n_trials=expected_trials,
            summary_path=model_paths["summary_json"],
            message="run started",
        )
        save_status_registry(status_csv, registry_df)
        print(f"\n{'=' * 60}\n[{sheet_name}] Running: {model}\n{'=' * 60}")
        pending_tasks.append(
            asyncio.create_task(
                run_single_model(
                    model=model,
                    result_df=result_df,
                    task_specs=task_specs,
                    api_key=api_key,
                    system_prompt=system_prompt,
                    categories=categories,
                    max_completion_tokens=max_completion_tokens,
                    global_request_semaphore=global_request_semaphore,
                )
            )
        )

    failures: list[tuple[str, str]] = []
    for completed_task in asyncio.as_completed(pending_tasks):
        model_result = await completed_task
        model = str(model_result["model"])
        model_name = str(model_result["model_name"])
        model_paths = get_model_output_paths(output_dir, sheet_name, model)

        if not bool(model_result["success"]):
            error_message = str(model_result["error"])
            registry_df = upsert_status(
                registry_df,
                model=model,
                status="failed",
                n_trials=None,
                summary_path=model_paths["summary_json"],
                message=error_message,
            )
            save_status_registry(status_csv, registry_df)
            failures.append((model, error_message))
            continue

        result_df[f"{model_name}_responses"] = model_result["responses"]
        result_df[f"{model_name}_categories"] = model_result["categories"]
        result_df[f"{model_name}_card_orders"] = model_result["card_orders"]
        all_stats[model_name] = dict(model_result["stats"])

        trial_df = pd.DataFrame(model_result["trial_rows"])
        trial_df.to_csv(model_paths["trial_results_csv"], index=False)
        pd.DataFrame([dict(model_result["stats"])]).to_csv(model_paths["stats_csv"], index=False)
        with model_paths["raw_responses_jsonl"].open("w", encoding="utf-8") as raw_handle:
            for row in model_result["raw_rows"]:
                raw_handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        with model_paths["format_errors_jsonl"].open("w", encoding="utf-8") as error_handle:
            for row in model_result["format_error_rows"]:
                error_handle.write(json.dumps(row, ensure_ascii=False) + "\n")

        summary = {
            "model": model,
            "context": sheet_name,
            "n_items": int(len(result_df)),
            "n_prompt_permutations": int(n_prompt_permutations),
            "n_trials": int(len(model_result["trial_rows"])),
            "stats": dict(model_result["stats"]),
        }
        model_paths["summary_json"].write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        registry_df = upsert_status(
            registry_df,
            model=model,
            status="completed",
            n_trials=len(model_result["trial_rows"]),
            summary_path=model_paths["summary_json"],
            message="run completed successfully",
        )
        result_df.to_csv(results_path, index=False)
        if all_stats:
            stats_df = pd.DataFrame(all_stats).T
            stats_df.index.name = "model"
            stats_df.to_csv(context_paths["stats_csv"])
        save_status_registry(status_csv, registry_df)

    result_df.to_csv(results_path, index=False)

    if all_stats:
        stats_df = pd.DataFrame(all_stats).T
        stats_df.index.name = "model"
        stats_df.to_csv(context_paths["stats_csv"])

    print(f"[{sheet_name}] Saved to {sheet_dir}")
    if failures:
        failure_lines = ", ".join(f"{model}: {message}" for model, message in failures)
        raise RuntimeError(f"[{sheet_name}] Some model runs failed: {failure_lines}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Wason Selection Task experiments")
    parser.add_argument(
        "--models",
        nargs="+",
        default=DEFAULT_MODELS,
        help="Model IDs for OpenRouter",
    )
    parser.add_argument(
        "--max-completion-tokens",
        type=int,
        default=EXPERIMENT_CONFIG["max_completion_tokens"],
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=EXPERIMENT_CONFIG["random_seed"],
    )
    parser.add_argument(
        "--n-prompt-permutations",
        type=int,
        default=EXPERIMENT_CONFIG["n_prompt_permutations"],
    )
    parser.add_argument(
        "--max-concurrent-requests",
        type=int,
        default=EXPERIMENT_CONFIG["max_concurrent_requests"],
        help="Global cap on simultaneous API requests across all active models",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help=f"Legacy: single OpenRouter API key (otherwise from {OPENROUTER_API_ENV_VAR}). "
        f"Prefer --api-key-proprietary / --api-key-open for experiments.",
    )
    parser.add_argument(
        "--api-key-proprietary",
        default=None,
        help=f"API key for proprietary models (env: {EXPERIMENTAL_PROPRIETARY_ENV_VAR}).",
    )
    parser.add_argument(
        "--api-key-open",
        default=None,
        help=f"API key for open/open-weight models (env: {EXPERIMENTAL_OPEN_ENV_VAR}).",
    )
    parser.add_argument(
        "--model-group",
        choices=["proprietary", "open"],
        default=None,
        help="Which model group the --models belong to. Used to select the correct experimental key.",
    )
    parser.add_argument(
        "--contexts",
        nargs="+",
        choices=sorted(EXPERIMENT_SHEETS.keys()),
        default=list(EXPERIMENT_SHEETS.keys()),
        help="Subset of contexts to run",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory where run outputs and metrics will be written",
    )
    parser.add_argument(
        "--system-prompt-file",
        type=Path,
        default=None,
        help="Optional file with the system prompt to use instead of prompts.SYSTEM_PROMPT",
    )
    parser.add_argument("--force", action="store_true", help="Rerun even if completed outputs already exist")
    return parser.parse_args()


async def async_main(args: argparse.Namespace) -> None:
    system_prompt = SYSTEM_PROMPT
    if args.system_prompt_file is not None:
        system_prompt = args.system_prompt_file.read_text(encoding="utf-8").strip()
        if not system_prompt:
            raise ValueError(f"System prompt file is empty: {args.system_prompt_file}")

    # ------------------------------------------------------------------
    # Resolve API key(s)
    # ------------------------------------------------------------------
    # Priority: explicit CLI args > experimental env vars > legacy env var
    api_key_proprietary = (
        args.api_key_proprietary
        or get_experimental_key("proprietary")
        or args.api_key
        or get_openrouter_api_key()
    )
    api_key_open = (
        args.api_key_open
        or get_experimental_key("open")
        or args.api_key
        or get_openrouter_api_key()
    )

    # If the user passed --api-key (legacy single key), use it for both groups
    if args.api_key and not args.api_key_proprietary and not args.api_key_open:
        api_key_proprietary = args.api_key
        api_key_open = args.api_key

    # If neither experimental key nor legacy key is available, fail
    if not api_key_proprietary and not api_key_open:
        raise ValueError(
            f"Missing experimental API keys. "
            f"Set {EXPERIMENTAL_PROPRIETARY_ENV_VAR} and/or {EXPERIMENTAL_OPEN_ENV_VAR}, "
            f"or pass --api-key-proprietary / --api-key-open / --api-key."
        )

    # Determine which key to use for the current run
    if args.model_group is not None:
        # User explicitly specified the group — use the matching key
        api_key = api_key_proprietary if args.model_group == "proprietary" else api_key_open
        if not api_key:
            raise ValueError(
                f"No API key available for model group '{args.model_group}'. "
                f"Pass --api-key-{args.model_group} or set the corresponding env var."
            )
    else:
        # Auto-detect: if models list contains only proprietary or only open models
        models_lower = [m.lower() for m in args.models]
        from common_config import PROPRIETARY_MODELS, OPEN_MODELS

        prop_lower = [m.lower() for m in PROPRIETARY_MODELS]
        open_lower = [m.lower() for m in OPEN_MODELS]

        all_proprietary = all(m in prop_lower for m in models_lower)
        all_open = all(m in open_lower for m in models_lower)

        if all_proprietary:
            api_key = api_key_proprietary
            group_label = "proprietary"
        elif all_open:
            api_key = api_key_open
            group_label = "open"
        else:
            # Mixed models — use proprietary key if available, else open
            api_key = api_key_proprietary or api_key_open
            group_label = "mixed (using available key)"

        if not api_key:
            raise ValueError(
                "Could not resolve an API key for the given models. "
                f"Models: {args.models}. "
                f"Pass --model-group or set the appropriate env var."
            )

    selected_sheets = {name: EXPERIMENT_SHEETS[name] for name in args.contexts}
    sheets = load_all_sheets(selected_sheets)
    for sheet_name, df in sheets.items():
        await run_experiments(
            sheet_name,
            df,
            args.models,
            api_key,
            system_prompt,
            CATEGORIES,
            args.output_dir,
            args.max_completion_tokens,
            args.random_seed,
            args.n_prompt_permutations,
            args.max_concurrent_requests,
            args.force,
        )

    compute_metrics(args.output_dir)


def main() -> None:
    args = parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
