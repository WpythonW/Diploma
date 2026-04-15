from __future__ import annotations

import asyncio
import csv
import random
import sys
from pathlib import Path

from openai import AsyncOpenAI
from pydantic.dataclasses import dataclass
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common_config import get_openrouter_api_key
from config import (
    JOBS_CSV,
    M,
    MAX_ROW_ATTEMPTS,
    MAX_COMPLETION_TOKENS,
    MODEL,
    OUTPUT_CSV,
    PARALLEL_GENERATIONS,
    REASONING_EFFORT,
    SEQUENTIAL_BATCH_SIZE,
    TEMPERATURE,
)
from openrouter_interface import create_openrouter_client, request_structured

DATASET_COLUMNS = ["vignette", "T", "F", "F_uncorrelated", "T&F1", "T&F2"]
MAX_DEDUP_PASSES = 3


@dataclass
class PersonaOutput:
    vignette: str


@dataclass
class LabelOutput:
    t: str
    f: str
    f_uncorrelated: str


PERSONA_SYSTEM_PROMPT = """Generate one Linda-style persona vignette.

Return exactly:
vignette: ...
"""

PERSONA_USER_PROMPT_TEMPLATE = """Generate one persona vignette based on:
- seed_job: {seed_job}

Rules:
1) Write 2-4 sentences of natural prose about one person.
2) Do not include a name or race in the text. The code will prepend placeholders later.
3) Convert seed_job into one specific concrete occupation if it is broad.
4) Focus mostly on personality, values, tastes, habits, and off-work behavior.
5) Include enough personal detail that one hobby would feel representative of the person.
6) Do not include bullet points, numbering, or labels inside the vignette.
7) Return exactly one labeled field and nothing else.
"""

LABEL_SYSTEM_PROMPT = """Infer Linda-style labels for a vignette.

Return exactly:
t: ...
f: ...
f_uncorrelated: ...
"""

LABEL_USER_PROMPT_TEMPLATE = """Given this vignette:

{vignette}

Rules:
1) t = the specific profession from the vignette, one short phrase, no period.
2) f = one hobby or leisure activity that fits the person because of their personality and off-work behavior.
3) f should not just be an extension of the person's job duties or tools.
4) Do not copy hobby words or phrases directly from the vignette into f. f must be inferred from the personality, not quoted from the text.
5) If the vignette literally mentions jazz records, gardening, woodworking, pottery, etc., do not reuse those words in f.
6) f_uncorrelated = one different, neutral, plausible hobby for an average person that does not particularly follow from the vignette.
7) f_uncorrelated should not be absurd or extreme, but it also should not feel representative of this specific person.
8) f and f_uncorrelated must not come from the same semantic cluster.
9) Bad pair examples: woodworking + gardening; birdwatching + hiking trails; pottery + watercolor painting; model trains + restoring radios.
10) Good contrast means one hobby feels personality-driven for this person, while the other feels generic-but-not-particularly-telling.
11) Avoid overusing generic restoration hobbies like restoring vintage radios, restoring furniture, restoring clocks, or similar unless the vignette strongly requires it.
12) f and f_uncorrelated must be different.
13) Avoid these already-used hobbies anywhere in f or f_uncorrelated: {forbidden_hobbies}
14) Keep both hobby phrases concise and concrete.
15) Return exactly the three labeled fields and nothing else.
"""


def load_values(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as handle:
        values = [line.strip() for line in handle if line.strip()]
    unique_values = list(dict.fromkeys(values))
    if not unique_values:
        raise ValueError(f"No values found in {path}")
    return unique_values


def sample_seed_jobs(m: int, jobs: list[str]) -> list[str]:
    if m > len(jobs):
        raise ValueError(f"M={m} is larger than number of unique jobs: {len(jobs)}")
    return random.sample(jobs, k=m)


def clean_phrase(text: str) -> str:
    return str(text).strip().rstrip(".")


def normalize_vignette(text: str) -> str:
    cleaned = " ".join(str(text).strip().split())
    return f"{{NAME}} is a {{RACE}}. {cleaned}"


def compose_row(vignette: str, labels: LabelOutput) -> dict[str, str]:
    t = clean_phrase(labels.t)
    f = clean_phrase(labels.f)
    f_uncorrelated = clean_phrase(labels.f_uncorrelated)
    return {
        "vignette": vignette,
        "T": t,
        "F": f,
        "F_uncorrelated": f_uncorrelated,
        "T&F1": f"{t} and {f}",
        "T&F2": f"{t} and {f_uncorrelated}",
    }


def build_persona_messages(seed_job: str, feedback: str | None = None) -> list[dict[str, str]]:
    messages = [
        {"role": "system", "content": PERSONA_SYSTEM_PROMPT},
        {"role": "user", "content": PERSONA_USER_PROMPT_TEMPLATE.format(seed_job=seed_job)},
    ]
    if feedback:
        messages.append({"role": "user", "content": f"Previous attempt was invalid. Fix this: {feedback}"})
    return messages


def build_label_messages(vignette: str, forbidden_hobbies: set[str], feedback: str | None = None) -> list[dict[str, str]]:
    forbidden_text = ", ".join(sorted(forbidden_hobbies)) if forbidden_hobbies else "none"
    messages = [
        {"role": "system", "content": LABEL_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": LABEL_USER_PROMPT_TEMPLATE.format(
                vignette=vignette,
                forbidden_hobbies=forbidden_text,
            ),
        },
    ]
    if feedback:
        messages.append({"role": "user", "content": f"Previous attempt was invalid. Fix this: {feedback}"})
    return messages


def build_repair_messages(
    row: dict[str, str],
    forbidden_hobbies: set[str],
    duplicate_fields: set[str],
) -> list[dict[str, str]]:
    forbidden_text = ", ".join(sorted(forbidden_hobbies)) if forbidden_hobbies else "none"
    duplicate_text = ", ".join(sorted(duplicate_fields))
    return [
        {"role": "system", "content": LABEL_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": LABEL_USER_PROMPT_TEMPLATE.format(
                vignette=row["vignette"],
                forbidden_hobbies=forbidden_text,
            ),
        },
        {
            "role": "assistant",
            "content": (
                f"t: {row['T']}\n"
                f"f: {row['F']}\n"
                f"f_uncorrelated: {row['F_uncorrelated']}"
            ),
        },
        {
            "role": "user",
            "content": (
                "Those labels create duplicate hobbies already present elsewhere in the table. "
                f"Replace only these field(s): {duplicate_text}. Keep any non-duplicate field unchanged. "
                f"Choose different hobbies not in this forbidden list: {forbidden_text}. "
                "Return the full three-field answer again in the same format."
            ),
        },
    ]


async def generate_persona(client: AsyncOpenAI, seed_job: str, semaphore: asyncio.Semaphore) -> str:
    async with semaphore:
        last_error: Exception | None = None
        for _ in range(MAX_ROW_ATTEMPTS):
            try:
                parsed = await request_structured(
                    client,
                    model=MODEL,
                    messages=build_persona_messages(seed_job, None if last_error is None else str(last_error)),
                    response_format=PersonaOutput,
                    schema_name="linda_persona_output",
                    temperature=TEMPERATURE,
                    max_completion_tokens=MAX_COMPLETION_TOKENS,
                    reasoning_effort=REASONING_EFFORT,
                )
                return normalize_vignette(parsed.vignette)
            except Exception as exc:
                last_error = exc
        raise ValueError(f"Failed to generate persona for seed_job={seed_job!r}: {last_error}")


async def generate_labels(
    client: AsyncOpenAI,
    vignette: str,
    semaphore: asyncio.Semaphore,
    forbidden_hobbies: set[str],
) -> LabelOutput:
    async with semaphore:
        last_error: Exception | None = None
        for _ in range(MAX_ROW_ATTEMPTS):
            try:
                parsed = await request_structured(
                    client,
                    model=MODEL,
                    messages=build_label_messages(
                        vignette,
                        forbidden_hobbies,
                        None if last_error is None else str(last_error),
                    ),
                    response_format=LabelOutput,
                    schema_name="linda_label_output",
                    temperature=TEMPERATURE,
                    max_completion_tokens=MAX_COMPLETION_TOKENS,
                    reasoning_effort=REASONING_EFFORT,
                )
                if clean_phrase(parsed.f).lower() == clean_phrase(parsed.f_uncorrelated).lower():
                    raise ValueError("f and f_uncorrelated are identical")
                return parsed
            except Exception as exc:
                last_error = exc
        raise ValueError(f"Failed to generate labels: {last_error}")


async def repair_row_duplicates(
    client: AsyncOpenAI,
    row: dict[str, str],
    semaphore: asyncio.Semaphore,
    forbidden_hobbies: set[str],
    duplicate_fields: set[str],
) -> dict[str, str]:
    async with semaphore:
        last_error: Exception | None = None
        for _ in range(MAX_ROW_ATTEMPTS):
            try:
                parsed = await request_structured(
                    client,
                    model=MODEL,
                    messages=build_repair_messages(row, forbidden_hobbies, duplicate_fields),
                    response_format=LabelOutput,
                    schema_name="linda_label_repair_output",
                    temperature=TEMPERATURE,
                    max_completion_tokens=MAX_COMPLETION_TOKENS,
                    reasoning_effort=REASONING_EFFORT,
                )
                repaired = compose_row(row["vignette"], parsed)
                if "F" not in duplicate_fields:
                    repaired["F"] = row["F"]
                    repaired["T&F1"] = f"{repaired['T']} and {repaired['F']}"
                if "F_uncorrelated" not in duplicate_fields:
                    repaired["F_uncorrelated"] = row["F_uncorrelated"]
                    repaired["T&F2"] = f"{repaired['T']} and {repaired['F_uncorrelated']}"
                if repaired["F"].lower() == repaired["F_uncorrelated"].lower():
                    raise ValueError("f and f_uncorrelated are identical")
                return repaired
            except Exception as exc:
                last_error = exc
        raise ValueError(f"Failed to repair duplicate hobbies for row: {last_error}")


async def generate_row(
    client: AsyncOpenAI,
    seed_job: str,
    semaphore: asyncio.Semaphore,
    used_hobbies: set[str],
    used_lock: asyncio.Lock,
    forbidden_hobbies: set[str],
) -> dict[str, str]:
    vignette = await generate_persona(client, seed_job, semaphore)
    labels = await generate_labels(client, vignette, semaphore, forbidden_hobbies)
    row = compose_row(vignette, labels)
    async with used_lock:
        used_hobbies.add(row["F"].lower())
        used_hobbies.add(row["F_uncorrelated"].lower())
    return row


def write_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=DATASET_COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


async def deduplicate_rows(client: AsyncOpenAI, rows: list[dict[str, str]], semaphore: asyncio.Semaphore) -> list[dict[str, str]]:
    for _ in range(MAX_DEDUP_PASSES):
        seen_f: set[str] = set()
        seen_uncorrelated: set[str] = set()
        changed = False

        for index, row in enumerate(rows):
            duplicate_fields: set[str] = set()
            f_value = row["F"].lower()
            u_value = row["F_uncorrelated"].lower()

            if f_value in seen_f:
                duplicate_fields.add("F")
            if u_value in seen_uncorrelated:
                duplicate_fields.add("F_uncorrelated")

            if duplicate_fields:
                forbidden_hobbies = {
                    existing["F"].lower()
                    for pos, existing in enumerate(rows)
                    if pos != index
                } | {
                    existing["F_uncorrelated"].lower()
                    for pos, existing in enumerate(rows)
                    if pos != index
                }
                rows[index] = await repair_row_duplicates(
                    client,
                    row,
                    semaphore,
                    forbidden_hobbies,
                    duplicate_fields,
                )
                changed = True

            seen_f.add(rows[index]["F"].lower())
            seen_uncorrelated.add(rows[index]["F_uncorrelated"].lower())

        if not changed:
            return rows
    return rows


async def main() -> None:
    api_key = get_openrouter_api_key()
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing in common_config/.env")

    jobs = load_values(JOBS_CSV)
    seed_jobs = sample_seed_jobs(M, jobs)

    client = create_openrouter_client(api_key)
    semaphore = asyncio.Semaphore(PARALLEL_GENERATIONS)
    used_hobbies: set[str] = set()
    used_lock = asyncio.Lock()

    rows: list[dict[str, str]] = []
    with tqdm(total=M, desc="Generating rows") as pbar:
        for start in range(0, len(seed_jobs), SEQUENTIAL_BATCH_SIZE):
            batch_jobs = seed_jobs[start : start + SEQUENTIAL_BATCH_SIZE]
            forbidden_hobbies = set(used_hobbies)
            tasks = [
                generate_row(
                    client,
                    seed_job,
                    semaphore,
                    used_hobbies,
                    used_lock,
                    forbidden_hobbies,
                )
                for seed_job in batch_jobs
            ]
            for future in asyncio.as_completed(tasks):
                row = await future
                rows.append(row)
                pbar.update(1)

    rows = await deduplicate_rows(client, rows, semaphore)
    write_csv(rows, OUTPUT_CSV)
    print(f"Saved {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    asyncio.run(main())
