"""
Tool: check_papers.py
Парсит bibliography.bib и параллельно верифицирует каждую статью.
Агент: qwen/qwen3-235b-a22b-2507 (через OpenRouter) + Perplexity sonar (веб-поиск).

Usage:
  uv run python tools/check_papers.py                        # полный прогон всех статей
  uv run python tools/check_papers.py --test                 # тест (verbose, 5 статей)
  uv run python tools/check_papers.py --recheck key1 key2   # перепроверить конкретные ключи
  uv run python tools/check_papers.py --recheck key1 key2 \\
      --prompt "Focus on whether the year and venue are correct" \\
      --hints key1:"check if this is really in Psych Review" key2:"look for arXiv version"

Кеш: .cache/<md5(key)>.json — инвалидируется только для --recheck ключей.
Output: papers_results.json
"""

import asyncio
import json
import os
import re
import sys
import hashlib
import argparse
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
from openai import AsyncOpenAI

load_dotenv(Path(__file__).parent.parent / ".env")

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
PERPLEXITY_API_KEY = os.environ["PERPLEXITY_API_KEY"]

BIB_FILE = str(Path(__file__).parent.parent.parent / "bibliography.bib")
OUTPUT_FILE = str(Path(__file__).parent / "papers_results.json")
CACHE_DIR = Path(__file__).parent / ".cache"

RESEARCHER_MODEL = "qwen/qwen3-235b-a22b-2507"
PERPLEXITY_MODEL = "sonar"

openrouter_client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)
perplexity_client = AsyncOpenAI(
    api_key=PERPLEXITY_API_KEY,
    base_url="https://api.perplexity.ai",
)

DEFAULT_SYSTEM_PROMPT = (
    "You are a critical academic research verifier. "
    "Your task: determine if a bibliography entry is a REAL published work or a FABRICATED/HALLUCINATED reference.\n\n"
    "Process:\n"
    "1. Use search_perplexity to search for the paper. Start with: title + authors + year.\n"
    "2. If confidence < 85%, search again with different queries:\n"
    "   - Title only\n"
    "   - Authors + year + journal/venue\n"
    "   - DOI or arXiv URL if present\n"
    "   - Alternate phrasing of the title\n"
    "3. Keep searching (up to 7 calls total) until confidence >= 85% or strategies exhausted.\n"
    "4. Final verdict:\n"
    "   - REAL: Paper exists, key details match\n"
    "   - FAKE: Appears fabricated or details significantly wrong/misattributed\n"
    "   - UNCERTAIN: Cannot determine after exhaustive search\n\n"
    "Do NOT give a verdict after one search if not confident. Keep searching!\n"
    "End your FINAL response with:\n"
    "```json\n{\"verdict\": \"REAL|FAKE|UNCERTAIN\", \"confidence\": 0-100, \"reason\": \"...\"}\n```"
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_perplexity",
            "description": "Search the web via Perplexity to verify whether an academic paper or book exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query. Include title, authors, year, venue."}
                },
                "required": ["query"],
            },
        },
    }
]


# ── Кеш ──────────────────────────────────────────────────────────────────────

def _cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    return CACHE_DIR / f"{hashlib.md5(key.encode()).hexdigest()}.json"

def cache_get(key: str) -> dict | None:
    p = _cache_path(key)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

def cache_set(key: str, value: dict):
    _cache_path(key).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

def cache_invalidate(key: str):
    p = _cache_path(key)
    if p.exists():
        p.unlink()
        print(f"  [cache] invalidated {key}")


# ── Парсер .bib ───────────────────────────────────────────────────────────────

def parse_bib(filepath: str) -> list[dict]:
    content = Path(filepath).read_text(encoding="utf-8")
    entries = []
    for m in re.finditer(r'@(\w+)\{(\w+),\s*(.*?)\n\}', content, re.DOTALL):
        body = m.group(3)
        fields = {}
        for fm in re.finditer(r'(\w+)\s*=\s*\{(.*?)\}(?=\s*[,\n])', body, re.DOTALL):
            k = fm.group(1).lower()
            v = re.sub(r'\{([^{}]*)\}', r'\1', fm.group(2).strip().replace('\n', ' '))
            fields[k] = v
        entries.append({"key": m.group(2), "type": m.group(1).lower(), "fields": fields})
    return entries

def entry_to_description(entry: dict) -> str:
    f = entry["fields"]
    parts = []
    for label, field in [
        ("Authors", "author"), ("Title", "title"), ("Journal", "journal"),
        ("Conference/Book", "booktitle"), ("Year", "year"), ("Volume", "volume"),
        ("Pages", "pages"), ("Publisher", "publisher"), ("URL", "howpublished"),
    ]:
        if field in f:
            parts.append(f"{label}: {f[field]}")
    return "\n".join(parts)


# ── Perplexity (in-memory кеш запросов) ──────────────────────────────────────

_pplx_cache: dict[str, str] = {}

async def search_perplexity(query: str, verbose: bool = False) -> str:
    if query in _pplx_cache:
        if verbose:
            print(f"    [pplx cache] {query[:80]}")
        return _pplx_cache[query]
    if verbose:
        print(f"    [perplexity] {query[:80]}")
    response = await perplexity_client.chat.completions.create(
        model=PERPLEXITY_MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a research assistant. Find information about academic papers/books. "
                "Report: does it exist, exact title, authors, venue, year, DOI or URL. Be factual."
            )},
            {"role": "user", "content": query},
        ],
    )
    result = response.choices[0].message.content or ""
    _pplx_cache[query] = result
    return result


# ── Агент-верификатор ─────────────────────────────────────────────────────────

async def researcher_agent(
    entry: dict,
    semaphore: asyncio.Semaphore,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    extra_hint: str = "",
    verbose: bool = False,
) -> dict:
    key = entry["key"]
    description = entry_to_description(entry)

    async with semaphore:
        if verbose:
            print(f"\n{'─'*60}\nAGENT: {key}\n{'─'*60}\n{description}\n")

        user_message = f"Verify this bibliography entry:\n\n{description}"
        if extra_hint:
            user_message += f"\n\nAdditional focus: {extra_hint}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        tool_call_count = 0

        for _ in range(7):
            response = await openrouter_client.chat.completions.create(
                model=RESEARCHER_MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.3,
            )
            msg = response.choices[0].message
            messages.append(msg)

            if msg.tool_calls:
                tool_results = []
                for tc in msg.tool_calls:
                    if tc.function.name == "search_perplexity":
                        query = json.loads(tc.function.arguments)["query"]
                        tool_call_count += 1
                        result = await search_perplexity(query, verbose=verbose)
                        if verbose:
                            print(f"\n  [search #{tool_call_count}] {query[:70]}")
                            print(f"  [result] {result[:300]}{'...' if len(result) > 300 else ''}")
                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        })
                messages.extend(tool_results)

            else:
                final_text = msg.content or ""
                verdict, confidence, reason = "UNCERTAIN", 50, "Could not parse verdict"
                m = re.search(r'```json\s*(.*?)\s*```', final_text, re.DOTALL)
                if m:
                    try:
                        data = json.loads(m.group(1))
                        verdict = data.get("verdict", "UNCERTAIN")
                        confidence = data.get("confidence", 50)
                        reason = data.get("reason", "")
                    except json.JSONDecodeError:
                        pass

                if verbose:
                    print(f"\n  [verdict] {verdict} ({confidence}%) — {tool_call_count} searches")
                    print(f"  [reason] {reason}")

                out = {
                    "key": key, "type": entry["type"], "description": description,
                    "verdict": verdict, "confidence": confidence,
                    "reason": reason, "tool_calls": tool_call_count,
                    "prompt_variant": system_prompt[:80] + "..." if len(system_prompt) > 80 else system_prompt,
                }
                cache_set(key, out)
                return out

        out = {
            "key": key, "type": entry["type"], "description": description,
            "verdict": "UNCERTAIN", "confidence": 0,
            "reason": "Agent loop exceeded max iterations", "tool_calls": tool_call_count,
        }
        cache_set(key, out)
        return out


# ── Прогон списка записей ─────────────────────────────────────────────────────

async def run_entries(
    entries: list[dict],
    semaphore: asyncio.Semaphore,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    hints: dict[str, str] | None = None,  # key -> extra hint string
    verbose: bool = False,
) -> list[dict]:
    hints = hints or {}
    results = []

    if verbose:
        for entry in entries:
            r = await researcher_agent(entry, semaphore, system_prompt, hints.get(entry["key"], ""), verbose=True)
            results.append(r)
    else:
        pbar = tqdm(total=len(entries), desc="Verifying", unit="paper")

        async def _run(entry):
            r = await researcher_agent(entry, semaphore, system_prompt, hints.get(entry["key"], ""))
            results.append(r)
            icon = {"REAL": "✓", "FAKE": "✗", "UNCERTAIN": "?"}.get(r["verdict"], "?")
            pbar.set_postfix_str(f"{icon} {r['key'][:25]}")
            pbar.update(1)

        await asyncio.gather(*[_run(e) for e in entries])
        pbar.close()

    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="Verify bibliography entries")
    parser.add_argument("--test", action="store_true", help="Run on 5 test entries (verbose)")
    parser.add_argument("--recheck", nargs="+", metavar="KEY", help="Keys to recheck (invalidates cache)")
    parser.add_argument("--prompt", default="", help="Custom system prompt suffix for --recheck")
    parser.add_argument(
        "--hints", nargs="+", metavar="KEY:HINT",
        help='Per-key hints, e.g. key1:"check venue" key2:"look for DOI"'
    )
    return parser.parse_args()


def parse_hints(raw: list[str] | None) -> dict[str, str]:
    if not raw:
        return {}
    result = {}
    for item in raw:
        if ":" in item:
            k, _, v = item.partition(":")
            result[k.strip()] = v.strip().strip('"')
    return result


async def main():
    args = parse_args()
    hints = parse_hints(args.hints)

    print(f"Parsing {BIB_FILE}...")
    all_entries = parse_bib(BIB_FILE)
    entry_map = {e["key"]: e for e in all_entries}
    print(f"Found {len(all_entries)} entries.")

    system_prompt = DEFAULT_SYSTEM_PROMPT
    if args.prompt:
        system_prompt += f"\n\nAdditional instructions: {args.prompt}"

    # ── Режим --recheck ───────────────────────────────────────────────────────
    if args.recheck:
        missing = [k for k in args.recheck if k not in entry_map]
        if missing:
            print(f"[WARN] Keys not found in bib: {missing}")

        recheck_entries = [entry_map[k] for k in args.recheck if k in entry_map]
        print(f"\nRECHECK MODE: {[e['key'] for e in recheck_entries]}")
        if args.prompt:
            print(f"Custom prompt suffix: {args.prompt}")
        if hints:
            print(f"Per-key hints: {hints}")

        # Инвалидируем кеш только для этих ключей
        for e in recheck_entries:
            cache_invalidate(e["key"])

        semaphore = asyncio.Semaphore(5)
        new_results = await run_entries(recheck_entries, semaphore, system_prompt, hints, verbose=True)

        # Мёрджим в существующий results.json
        existing: list[dict] = []
        if Path(OUTPUT_FILE).exists():
            existing = json.loads(Path(OUTPUT_FILE).read_text(encoding="utf-8"))

        existing_map = {r["key"]: r for r in existing}
        for r in new_results:
            existing_map[r["key"]] = r
        merged = list(existing_map.values())

        Path(OUTPUT_FILE).write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nUpdated {len(new_results)} entries → {OUTPUT_FILE}")
        return

    # ── Режим --test ─────────────────────────────────────────────────────────
    if args.test:
        test_keys = ["tversky1983extensional", "suri2024large", "binz2023using",
                     "banatt2024wilt", "macmillan2024irrationality"]
        entries = [entry_map[k] for k in test_keys if k in entry_map]
        print(f"TEST MODE: {[e['key'] for e in entries]}\n")
        semaphore = asyncio.Semaphore(3)
        results = await run_entries(entries, semaphore, verbose=True)

    # ── Полный прогон ─────────────────────────────────────────────────────────
    else:
        # Пропускаем уже закешированные
        to_run = [e for e in all_entries if not cache_get(e["key"])]
        cached_results = [cache_get(e["key"]) for e in all_entries if cache_get(e["key"])]
        print(f"Cached: {len(cached_results)}  To run: {len(to_run)}")

        semaphore = asyncio.Semaphore(5)
        new_results = await run_entries(to_run, semaphore) if to_run else []
        results = cached_results + new_results

    # ── Сохраняем и печатаем сводку ───────────────────────────────────────────
    Path(OUTPUT_FILE).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    real      = [r for r in results if r["verdict"] == "REAL"]
    fake      = [r for r in results if r["verdict"] == "FAKE"]
    uncertain = [r for r in results if r["verdict"] == "UNCERTAIN"]

    print(f"\n{'='*60}\nRESULTS SUMMARY\n{'='*60}")
    print(f"REAL:      {len(real):3d}")
    print(f"FAKE:      {len(fake):3d}")
    print(f"UNCERTAIN: {len(uncertain):3d}")
    print(f"TOTAL:     {len(results):3d}")

    for label, group in [("POTENTIALLY FAKE", fake), ("UNCERTAIN", uncertain)]:
        if group:
            print(f"\n{'='*60}\n{label}\n{'='*60}")
            for r in group:
                print(f"\n[{r['key']}] {r['verdict']} {r['confidence']}%  searches={r.get('tool_calls','?')}")
                print(f"  {r['reason']}")

    print(f"\nResults → {OUTPUT_FILE}  |  Cache → {CACHE_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
