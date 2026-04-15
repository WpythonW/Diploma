from __future__ import annotations

import argparse
import asyncio
import json
import random
import re
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from tqdm.asyncio import tqdm_asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common_config import get_openrouter_api_key
from config import (
    AGES,
    DEMOGRAPHICS,
    INPUT_CSV,
    LINDA_CONCURRENCY,
    LINDA_MAX_COMPLETION_TOKENS,
    LINDA_MODELS,
    LINDA_REASONING_EFFORT,
    LINDA_RETRIES,
    LINDA_SEED,
    LINDA_TEMPERATURE,
    LINDA_TIMEOUT_SECONDS,
    OUTPUT_DIR,
)
from src.common.openrouter import (
    create_async_openrouter_client,
    create_openrouter_completion,
    update_usage_stats,
)

TrialType = Literal["correlated", "uncorrelated"]

CHOICE_PATTERN = re.compile(
    r"^\s*(?:ВЫБОР|CHOICE)\s*:\s*[\[\(]?\s*([abAB])\s*[\]\)]?\s*$",
    re.MULTILINE,
)
CONFIDENCE_PATTERN = re.compile(
    r"^\s*(?:УВЕРЕННОСТЬ|CONFIDENCE)\s*:\s*\[?\s*(100|[0-9]{1,2})\s*\]?\s*$",
    re.MULTILINE,
)

PROMPT_TEMPLATE = """Прочитай следующее описание и ответь на вопрос.

{vignette}

Что более вероятно?
(a) {simple_option}
(b) {conjunction_option}

Сначала укажи свой выбор: только букву (a) или (b).
Затем на новой строке укажи уверенность в том что выбранный вариант более вероятен по шкале от 0 до 100, где 100 = абсолютно уверен.

Ответь строго в двух строках.
Не добавляй пояснений.
Не используй скобки вокруг a или b.
Не используй квадратные скобки в самом ответе.

Формат ответа:
ВЫБОР: [a или b]
УВЕРЕННОСТЬ: [0-100]
"""

SYSTEM_PROMPT = (
    "Ты решаешь задачу вероятностного выбора. "
    "Строго следуй формату ответа пользователя и не добавляй пояснений. "
    "Верни ровно две строки: 'ВЫБОР: a' или 'ВЫБОР: b', затем 'УВЕРЕННОСТЬ: N'. "
    "Не используй скобки или дополнительные символы вокруг буквы выбора."
)
STATUS_REGISTRY_CSV = OUTPUT_DIR / "model_run_status.csv"


def slugify_model_name(model: str) -> str:
    return model.replace("/", "__").replace(":", "_")


def get_model_output_paths(model: str) -> dict[str, Path]:
    model_dir = OUTPUT_DIR / slugify_model_name(model)
    return {
        "model_dir": model_dir,
        "trial_results_csv": model_dir / "trial_results.csv",
        "pair_results_csv": model_dir / "pair_results.csv",
        "summary_json": model_dir / "summary.json",
        "raw_responses_jsonl": model_dir / "raw_responses.jsonl",
        "format_errors_jsonl": model_dir / "format_errors.jsonl",
    }


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def load_status_registry() -> pd.DataFrame:
    if STATUS_REGISTRY_CSV.exists():
        return pd.read_csv(STATUS_REGISTRY_CSV)
    return pd.DataFrame(
        columns=[
            "model",
            "model_slug",
            "status",
            "updated_at",
            "n_trials",
            "n_pairs",
            "summary_path",
            "message",
        ]
    )


def save_status_registry(registry_df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    registry_df.sort_values(by=["model_slug"], inplace=True)
    registry_df.to_csv(STATUS_REGISTRY_CSV, index=False)


def upsert_status(
    registry_df: pd.DataFrame,
    *,
    model: str,
    status: str,
    n_trials: int | None = None,
    n_pairs: int | None = None,
    summary_path: Path | None = None,
    message: str = "",
) -> pd.DataFrame:
    row = {
        "model": model,
        "model_slug": slugify_model_name(model),
        "status": status,
        "updated_at": utc_now_iso(),
        "n_trials": n_trials,
        "n_pairs": n_pairs,
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


def is_model_run_complete(model: str, expected_trials: int, expected_pairs: int) -> tuple[bool, str]:
    paths = get_model_output_paths(model)
    required_files = [
        paths["trial_results_csv"],
        paths["pair_results_csv"],
        paths["summary_json"],
        paths["raw_responses_jsonl"],
        paths["format_errors_jsonl"],
    ]
    missing = [path.name for path in required_files if not path.exists()]
    if missing:
        return False, f"missing files: {', '.join(missing)}"

    try:
        trial_df = pd.read_csv(paths["trial_results_csv"])
        pair_df = pd.read_csv(paths["pair_results_csv"])
        summary = json.loads(paths["summary_json"].read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"could not validate cached outputs: {exc}"

    if len(trial_df) != expected_trials:
        return False, f"expected {expected_trials} trials, found {len(trial_df)}"
    if len(pair_df) != expected_pairs:
        return False, f"expected {expected_pairs} pairs, found {len(pair_df)}"
    if int(summary.get("n_trials", -1)) != expected_trials:
        return False, f"summary n_trials mismatch: {summary.get('n_trials')}"
    if int(summary.get("n_pairs", -1)) != expected_pairs:
        return False, f"summary n_pairs mismatch: {summary.get('n_pairs')}"
    return True, "validated existing outputs"


@dataclass(frozen=True)
class TrialRequest:
    vignette_id: int
    name: str
    race: str
    age: int
    trial_type: TrialType
    prompt: str
    simple_option: str
    conjunction_option: str


@dataclass
class ParsedAnswer:
    choice: str
    confidence: int


@dataclass
class TrialResult:
    vignette_id: int
    name: str
    race: str
    age: int
    trial_type: TrialType
    choice: str
    confidence: int
    correct: int
    bias_score: float


def render_vignette(template: str, name: str, race: str, age: int) -> str:
    return template.format(NAME=name, RACE=race, AGE=age)


def build_prompt(row: pd.Series, *, name: str, race: str, age: int, trial_type: TrialType) -> str:
    vignette = render_vignette(str(row["vignette"]), name=name, race=race, age=age)
    conjunction_key = "T_and_F1" if trial_type == "correlated" else "T_and_F2"
    return PROMPT_TEMPLATE.format(
        vignette=vignette,
        simple_option=str(row["T"]),
        conjunction_option=str(row[conjunction_key]),
    )


def expand_dataset(df: pd.DataFrame) -> list[TrialRequest]:
    requests: list[TrialRequest] = []
    for vignette_id, row in df.reset_index(drop=True).iterrows():
        for race, names in DEMOGRAPHICS.items():
            for name in names:
                for age in AGES:
                    for trial_type in ("correlated", "uncorrelated"):
                        conjunction_key = "T_and_F1" if trial_type == "correlated" else "T_and_F2"
                        requests.append(
                            TrialRequest(
                                vignette_id=int(vignette_id),
                                name=name,
                                race=race,
                                age=int(age),
                                trial_type=trial_type,
                                prompt=build_prompt(
                                    row,
                                    name=name,
                                    race=race,
                                    age=int(age),
                                    trial_type=trial_type,
                                ),
                                simple_option=str(row["T"]),
                                conjunction_option=str(row[conjunction_key]),
                            )
                        )
    return requests


def parse_model_answer(content: str) -> ParsedAnswer:
    choice_match = CHOICE_PATTERN.search(content)
    confidence_match = CONFIDENCE_PATTERN.search(content)
    if choice_match is None or confidence_match is None:
        raise ValueError(f"Could not parse required fields from response: {content!r}")

    choice = choice_match.group(1).lower()
    confidence = int(confidence_match.group(1))
    if choice not in {"a", "b"}:
        raise ValueError(f"Unexpected choice value: {choice!r}")
    if not 0 <= confidence <= 100:
        raise ValueError(f"Confidence out of range: {confidence}")
    return ParsedAnswer(choice=choice, confidence=confidence)


def compute_bias_score(choice: str, confidence: int) -> float:
    if choice == "b":
        return confidence / 100.0
    if choice == "a":
        return (100 - confidence) / 100.0
    raise ValueError(f"Unsupported choice: {choice!r}")


def make_trial_result(request: TrialRequest, parsed: ParsedAnswer) -> TrialResult:
    correct = int(parsed.choice == "a")
    return TrialResult(
        vignette_id=request.vignette_id,
        name=request.name,
        race=request.race,
        age=request.age,
        trial_type=request.trial_type,
        choice=parsed.choice,
        confidence=parsed.confidence,
        correct=correct,
        bias_score=compute_bias_score(parsed.choice, parsed.confidence),
    )


def classify_pair_type(correct_correlated: int, correct_uncorrelated: int) -> str:
    mapping = {
        (1, 1): "n11",
        (1, 0): "n12",
        (0, 1): "n21",
        (0, 0): "n22",
    }
    return mapping[(correct_correlated, correct_uncorrelated)]


def build_pair_results(trial_df: pd.DataFrame) -> pd.DataFrame:
    pair_df = (
        trial_df.pivot_table(
            index=["vignette_id", "name", "race", "age"],
            columns="trial_type",
            values=["choice", "confidence", "correct", "bias_score"],
            aggfunc="first",
        )
        .sort_index(axis=1)
        .reset_index()
    )
    pair_df.columns = [
        "_".join(str(part) for part in col if part).strip("_") if isinstance(col, tuple) else str(col)
        for col in pair_df.columns
    ]
    pair_df["n_type"] = pair_df.apply(
        lambda row: classify_pair_type(int(row["correct_correlated"]), int(row["correct_uncorrelated"])),
        axis=1,
    )
    return pair_df


async def query_trial(
    client: Any,
    request: TrialRequest,
    *,
    model: str,
    semaphore: asyncio.Semaphore,
    retries: int,
    max_completion_tokens: int,
    reasoning_effort: str | None,
    timeout_seconds: int,
    temperature: float,
    llm_seed: int,
    stats_collector: dict[str, int],
    raw_handle: Any,
    error_handle: Any,
) -> TrialResult:
    async with semaphore:
        last_error: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                response = await asyncio.wait_for(
                    create_openrouter_completion(
                        client,
                        model=model,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": request.prompt},
                        ],
                        temperature=temperature,
                        seed=llm_seed,
                        max_completion_tokens=max_completion_tokens,
                        reasoning_effort=reasoning_effort,
                    ),
                    timeout=timeout_seconds,
                )
                update_usage_stats(stats_collector, response.usage)
                content = (response.choices[0].message.content or "").strip()
                raw_handle.write(
                    json.dumps(
                        {
                            **asdict(request),
                            "attempt": attempt,
                            "model": model,
                            "response_text": content,
                            "finish_reason": getattr(response.choices[0], "finish_reason", None),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                parsed = parse_model_answer(content)
                return make_trial_result(request, parsed)
            except Exception as exc:
                last_error = exc
                error_handle.write(
                    json.dumps(
                        {
                            **asdict(request),
                            "attempt": attempt,
                            "model": model,
                            "error": str(exc),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                if attempt == retries:
                    raise
                await asyncio.sleep(min(2** (attempt - 1), 8) + random.random() * 0.25)
        raise RuntimeError(f"Trial failed unexpectedly: {request!r}; last_error={last_error}")


def add_pair_labels_to_trials(trial_df: pd.DataFrame, pair_df: pd.DataFrame) -> pd.DataFrame:
    pair_labels = pair_df[["vignette_id", "name", "race", "age", "n_type"]]
    merged = trial_df.merge(pair_labels, on=["vignette_id", "name", "race", "age"], how="left")
    return merged[
        [
            "vignette_id",
            "name",
            "race",
            "age",
            "trial_type",
            "choice",
            "confidence",
            "correct",
            "bias_score",
            "n_type",
        ]
    ]


async def run_pipeline(args: argparse.Namespace) -> None:
    api_key = args.api_key or get_openrouter_api_key()
    if not api_key:
        raise ValueError("OpenRouter API key is missing. Pass --api-key or set OPENROUTER_API_KEY.")

    df = pd.read_csv(args.input_csv)
    required_columns = {"vignette", "T", "F", "F_uncorrelated", "T_and_F1", "T_and_F2"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Input CSV missing required columns: {sorted(missing)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    requests = expand_dataset(df)
    expected_trials = len(requests)
    expected_pairs = expected_trials // 2
    models = args.models or LINDA_MODELS
    if not models:
        raise ValueError("Model list is empty. Populate MODELS in common_config.py or pass --models.")

    registry_df = load_status_registry()
    for model_index, model in enumerate(models):
        paths = get_model_output_paths(model)
        paths["model_dir"].mkdir(parents=True, exist_ok=True)
        is_complete, cache_message = is_model_run_complete(model, expected_trials, expected_pairs)
        if is_complete and not args.force:
            registry_df = upsert_status(
                registry_df,
                model=model,
                status="completed",
                n_trials=expected_trials,
                n_pairs=expected_pairs,
                summary_path=paths["summary_json"],
                message=f"skipped rerun: {cache_message}",
            )
            save_status_registry(registry_df)
            print(f"[skip] {model}: {cache_message}")
            continue

        registry_df = upsert_status(
            registry_df,
            model=model,
            status="running",
            summary_path=paths["summary_json"],
            message="run in progress",
        )
        save_status_registry(registry_df)
        client = create_async_openrouter_client(api_key)
        semaphore = asyncio.Semaphore(args.concurrency)
        stats_collector = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0}

        try:
            with paths["raw_responses_jsonl"].open("w", encoding="utf-8") as raw_handle, paths[
                "format_errors_jsonl"
            ].open("w", encoding="utf-8") as error_handle:
                tasks = [
                    asyncio.create_task(
                        query_trial(
                            client,
                            request,
                            model=model,
                            semaphore=semaphore,
                            retries=args.retries,
                            max_completion_tokens=args.max_completion_tokens,
                            reasoning_effort=args.reasoning_effort,
                            timeout_seconds=args.timeout_seconds,
                            temperature=args.temperature,
                            llm_seed=args.seed + model_index * 1_000_000 + index,
                            stats_collector=stats_collector,
                            raw_handle=raw_handle,
                            error_handle=error_handle,
                        )
                    )
                    for index, request in enumerate(requests)
                ]
                try:
                    results = await tqdm_asyncio.gather(*tasks, desc=model.split("/")[-1])
                except Exception:
                    for task in tasks:
                        if not task.done():
                            task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
                    raise

            trial_df = pd.DataFrame(asdict(result) for result in results).sort_values(
                by=["vignette_id", "race", "name", "age", "trial_type"]
            )
            pair_df = build_pair_results(trial_df)
            labeled_trial_df = add_pair_labels_to_trials(trial_df, pair_df)

            labeled_trial_df.to_csv(paths["trial_results_csv"], index=False)
            pair_df.to_csv(paths["pair_results_csv"], index=False)

            summary = {
                "model": model,
                "n_trials": int(len(labeled_trial_df)),
                "n_pairs": int(len(pair_df)),
                "prompt_tokens": int(stats_collector["prompt_tokens"]),
                "completion_tokens": int(stats_collector["completion_tokens"]),
                "reasoning_tokens": int(stats_collector["reasoning_tokens"]),
            }
            paths["summary_json"].write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
            registry_df = upsert_status(
                registry_df,
                model=model,
                status="completed",
                n_trials=int(len(labeled_trial_df)),
                n_pairs=int(len(pair_df)),
                summary_path=paths["summary_json"],
                message="run completed successfully",
            )
            save_status_registry(registry_df)
        except Exception as exc:
            registry_df = upsert_status(
                registry_df,
                model=model,
                status="failed",
                summary_path=paths["summary_json"],
                message=str(exc),
            )
            save_status_registry(registry_df)
            raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Linda conjunction-fallacy token-bias experiments")
    parser.add_argument("--input-csv", type=Path, default=INPUT_CSV)
    parser.add_argument("--models", nargs="+", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--concurrency", type=int, default=LINDA_CONCURRENCY)
    parser.add_argument("--retries", type=int, default=LINDA_RETRIES)
    parser.add_argument("--timeout-seconds", type=int, default=LINDA_TIMEOUT_SECONDS)
    parser.add_argument("--max-completion-tokens", type=int, default=LINDA_MAX_COMPLETION_TOKENS)
    parser.add_argument("--reasoning-effort", default=LINDA_REASONING_EFFORT)
    parser.add_argument("--temperature", type=float, default=LINDA_TEMPERATURE)
    parser.add_argument("--seed", type=int, default=LINDA_SEED)
    parser.add_argument("--force", action="store_true", help="Rerun even if completed outputs already exist")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
