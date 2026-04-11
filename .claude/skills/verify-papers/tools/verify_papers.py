"""
Tool: verify_papers.py
Парсит bibliography.bib, параллельно верифицирует каждую статью через qwen3+Perplexity,
и создаёт подробную карточку для каждой статьи в papers_cards/<key>.md

Claude (оркестратор) НЕ читает статьи сам. Весь анализ — через qwen3-235b.

Usage:
  uv run python tools/verify_papers.py                         # полный прогон
  uv run python tools/verify_papers.py --test                  # тест (5 статей, verbose)
  uv run python tools/verify_papers.py --recheck key1 key2     # перепроверить конкретные ключи
  uv run python tools/verify_papers.py --recheck key1 key2 \\
      --prompt "Focus on venue and year" \\
      --hints key1:"check arXiv" key2:"may be book chapter"

Кеш: .cache/<md5(key)>.json — инвалидируется только для --recheck ключей.
Карточки: papers_cards/<key>.md — перезаписываются при каждом успешном прогоне.
Output: papers_results.json
"""

import asyncio
import json
import os
import re
import sys
import hashlib
import argparse
import textwrap
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
from openai import AsyncOpenAI

# ── Пути ─────────────────────────────────────────────────────────────────────

def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "bibliography.bib").exists():
            return candidate
        if (candidate / "Diploma_latex" / "bibliography.bib").exists():
            return candidate / "Diploma_latex"
    raise FileNotFoundError("Could not find repository root with bibliography.bib")

SKILL_ROOT  = Path(__file__).parent.parent
REPO_ROOT   = find_repo_root(SKILL_ROOT)

load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT.parent / ".env", override=False)

OPENROUTER_API_KEY  = os.environ["OPENROUTER_API_KEY"]
PERPLEXITY_API_KEY  = os.environ["PERPLEXITY_API_KEY"]

BIB_FILE     = str(REPO_ROOT / "bibliography.bib")
OUTPUT_FILE  = Path(__file__).parent / "papers_results.json"
CACHE_DIR    = Path(__file__).parent / ".cache"
CARDS_DIR    = SKILL_ROOT / "papers_cards"

RESEARCHER_MODEL  = "qwen/qwen3-235b-a22b-2507"
PERPLEXITY_MODEL  = "sonar"

openrouter_client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)
perplexity_client = AsyncOpenAI(
    api_key=PERPLEXITY_API_KEY,
    base_url="https://api.perplexity.ai",
)

# ── Системный промпт ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a critical academic research verifier and analyst.

Your task has TWO parts:

## PART 1 — Verify the paper exists
1. Use search_perplexity to search for the paper. Start with: title + authors + year.
2. If confidence < 85%, search again with different queries:
   - Title only
   - Authors + year + journal/venue
   - DOI or arXiv URL if present
   - Alternate phrasing of the title
3. Keep searching (up to 7 calls total) until confidence >= 85% or strategies exhausted.
4. Verdict: REAL | FAKE | UNCERTAIN

## PART 2 — Fill the paper card (ONLY if REAL or high-confidence UNCERTAIN)
After verifying, extract and analyze the following from search results and any available content:
- Goal: What problem did the authors want to solve?
- Gap closed: What scientific gap existed before this work?
- Metrics and datasets: What benchmarks/datasets were used, what metrics reported?
- Results: Concrete numbers and findings.

IMPORTANT: Base the card on actual search results and available content (PDF, arXiv, Semantic Scholar).
DO NOT invent or paraphrase from memory. If a field cannot be determined, write "Не удалось определить".

## Output format
End your FINAL response with this JSON block:
```json
{
  "verdict": "REAL|FAKE|UNCERTAIN",
  "confidence": 0-100,
  "reason": "...",
  "pdf_url": "url or null",
  "arxiv_id": "arXiv:XXXX.XXXXX or null",
  "semantic_scholar_id": null,
  "doi": "doi or null",
  "venue": "journal/conference name or null",
  "goal": "What the paper aimed to solve",
  "gap": "What gap was closed",
  "metrics": "Datasets and metrics used",
  "results": "Concrete findings and numbers"
}
```
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_perplexity",
            "description": "Search the web via Perplexity to verify an academic paper and find its content (PDF, arXiv, Semantic Scholar).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query. Include title, authors, year, venue, arXiv ID."}
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
        ("DOI", "doi"), ("Note", "note"),
    ]:
        if field in f:
            parts.append(f"{label}: {f[field]}")
    return "\n".join(parts)

# ── Perplexity ────────────────────────────────────────────────────────────────

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
                "Report: does it exist, exact title, authors, venue, year, DOI, arXiv ID, PDF URL, "
                "abstract summary, key contributions, datasets used, metrics reported, main results."
            )},
            {"role": "user", "content": query},
        ],
    )
    result = response.choices[0].message.content or ""
    _pplx_cache[query] = result
    return result

# ── Карточка статьи ───────────────────────────────────────────────────────────

def write_card(entry: dict, result: dict):
    """Записать карточку статьи в papers_cards/<key>.md"""
    CARDS_DIR.mkdir(exist_ok=True)
    f = entry["fields"]
    key = entry["key"]

    frontmatter = textwrap.dedent(f"""\
        ---
        key: {key}
        title: {f.get('title', 'Unknown')}
        authors: {f.get('author', 'Unknown')}
        year: {f.get('year', 'Unknown')}
        venue: {result.get('venue') or f.get('journal') or f.get('booktitle') or 'Unknown'}
        doi: {result.get('doi') or f.get('doi') or 'null'}
        arxiv_id: {result.get('arxiv_id') or 'null'}
        pdf_url: {result.get('pdf_url') or 'null'}
        semantic_scholar_id: {result.get('semantic_scholar_id') or 'null'}
        verified: {'true' if result['verdict'] == 'REAL' else 'false'}
        confidence: {result['confidence']}
        source_used: {result.get('source_used', 'perplexity')}
        last_checked: {datetime.now().strftime('%Y-%m-%d')}
        ---
    """)

    body = textwrap.dedent(f"""\
        ## Цель работы
        {result.get('goal') or 'Не удалось определить'}

        ## Закрытый гэп
        {result.get('gap') or 'Не удалось определить'}

        ## Метрики и датасеты
        {result.get('metrics') or 'Не удалось определить'}

        ## Результаты
        {result.get('results') or 'Не удалось определить'}

        ## Верификационный вердикт
        **{result['verdict']}** ({result['confidence']}%) — {result['reason']}
    """)

    card_path = CARDS_DIR / f"{key}.md"
    card_path.write_text(frontmatter + "\n" + body, encoding="utf-8")

# ── Агент-верификатор ─────────────────────────────────────────────────────────

async def researcher_agent(
    entry: dict,
    semaphore: asyncio.Semaphore,
    system_prompt: str = SYSTEM_PROMPT,
    extra_hint: str = "",
    verbose: bool = False,
) -> dict:
    key = entry["key"]
    description = entry_to_description(entry)

    async with semaphore:
        if verbose:
            print(f"\n{'─'*60}\nAGENT: {key}\n{'─'*60}\n{description}\n")

        user_message = f"Verify this bibliography entry and fill the paper card:\n\n{description}"
        if extra_hint:
            user_message += f"\n\nAdditional focus: {extra_hint}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        tool_call_count = 0

        for _ in range(10):
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
                            print(f"  [result] {result[:400]}{'...' if len(result) > 400 else ''}")
                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        })
                messages.extend(tool_results)

            else:
                final_text = msg.content or ""
                # Дефолтные значения
                out = {
                    "key": key, "type": entry["type"], "description": description,
                    "verdict": "UNCERTAIN", "confidence": 50,
                    "reason": "Could not parse verdict",
                    "tool_calls": tool_call_count,
                    "pdf_url": None, "arxiv_id": None,
                    "semantic_scholar_id": None, "doi": None, "venue": None,
                    "goal": None, "gap": None, "metrics": None, "results": None,
                    "source_used": "perplexity",
                }

                m = re.search(r'```json\s*(.*?)\s*```', final_text, re.DOTALL)
                if m:
                    try:
                        data = json.loads(m.group(1))
                        out.update({k: v for k, v in data.items() if v is not None})
                    except json.JSONDecodeError:
                        pass

                if verbose:
                    print(f"\n  [verdict] {out['verdict']} ({out['confidence']}%) — {tool_call_count} searches")
                    print(f"  [reason] {out['reason']}")
                    if out.get('goal'):
                        print(f"  [goal] {out['goal'][:120]}")

                # Записываем карточку для реальных статей
                if out["verdict"] in ("REAL", "UNCERTAIN") and out["confidence"] >= 50:
                    write_card(entry, out)
                    if verbose:
                        print(f"  [card] written → papers_cards/{key}.md")

                cache_set(key, out)
                return out

        # Превышен лимит итераций
        out = {
            "key": key, "type": entry["type"], "description": description,
            "verdict": "UNCERTAIN", "confidence": 0,
            "reason": "Agent loop exceeded max iterations",
            "tool_calls": tool_call_count,
            "source_used": "perplexity",
        }
        cache_set(key, out)
        return out

# ── Прогон списка записей ─────────────────────────────────────────────────────

async def run_entries(
    entries: list[dict],
    semaphore: asyncio.Semaphore,
    system_prompt: str = SYSTEM_PROMPT,
    hints: dict[str, str] | None = None,
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
    parser = argparse.ArgumentParser(description="Verify bibliography entries and generate paper cards")
    parser.add_argument("--test", action="store_true", help="Run on 5 test entries (verbose)")
    parser.add_argument("--recheck", nargs="+", metavar="KEY", help="Keys to recheck (invalidates cache and card)")
    parser.add_argument("--prompt", default="", help="Custom system prompt suffix for --recheck")
    parser.add_argument("--hints", nargs="+", metavar="KEY:HINT",
                        help='Per-key hints, e.g. key1:"check arXiv" key2:"look for PDF"')
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
    print(f"Cards directory: {CARDS_DIR}/")

    system_prompt = SYSTEM_PROMPT
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

        for e in recheck_entries:
            cache_invalidate(e["key"])
            # Удалить старую карточку если есть
            card = CARDS_DIR / f"{e['key']}.md"
            if card.exists():
                card.unlink()
                print(f"  [card] removed old card for {e['key']}")

        semaphore = asyncio.Semaphore(5)
        new_results = await run_entries(recheck_entries, semaphore, system_prompt, hints, verbose=True)

        existing: list[dict] = []
        if OUTPUT_FILE.exists():
            existing = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))

        existing_map = {r["key"]: r for r in existing}
        for r in new_results:
            existing_map[r["key"]] = r
        merged = list(existing_map.values())

        OUTPUT_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nUpdated {len(new_results)} entries → {OUTPUT_FILE}")
        return

    # ── Режим --test ──────────────────────────────────────────────────────────
    if args.test:
        test_keys = ["tversky1983extensional", "suri2024large", "binz2023using",
                     "banatt2024wilt", "macmillan2024irrationality"]
        entries = [entry_map[k] for k in test_keys if k in entry_map]
        if not entries:
            # Берём первые 5 если тестовые ключи не найдены
            entries = all_entries[:5]
        print(f"TEST MODE: {[e['key'] for e in entries]}\n")
        semaphore = asyncio.Semaphore(3)
        results = await run_entries(entries, semaphore, verbose=True)

    # ── Полный прогон ─────────────────────────────────────────────────────────
    else:
        to_run = [e for e in all_entries if not cache_get(e["key"])]
        cached_results = [cache_get(e["key"]) for e in all_entries if cache_get(e["key"])]
        print(f"Cached: {len(cached_results)}  To run: {len(to_run)}")

        semaphore = asyncio.Semaphore(5)
        new_results = await run_entries(to_run, semaphore) if to_run else []
        results = cached_results + new_results

    # ── Сохраняем и печатаем сводку ───────────────────────────────────────────
    OUTPUT_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    real      = [r for r in results if r.get("verdict") == "REAL"]
    fake      = [r for r in results if r.get("verdict") == "FAKE"]
    uncertain = [r for r in results if r.get("verdict") == "UNCERTAIN"]
    cards     = list(CARDS_DIR.glob("*.md")) if CARDS_DIR.exists() else []

    print(f"\n{'='*60}\nRESULTS SUMMARY\n{'='*60}")
    print(f"REAL:      {len(real):3d}")
    print(f"FAKE:      {len(fake):3d}")
    print(f"UNCERTAIN: {len(uncertain):3d}")
    print(f"TOTAL:     {len(results):3d}")
    print(f"Cards written: {len(cards)}")

    for label, group in [("POTENTIALLY FAKE", fake), ("UNCERTAIN", uncertain)]:
        if group:
            print(f"\n{'='*60}\n{label}\n{'='*60}")
            for r in group:
                print(f"\n[{r['key']}] {r['verdict']} {r['confidence']}%  searches={r.get('tool_calls','?')}")
                print(f"  {r['reason']}")

    print(f"\nResults → {OUTPUT_FILE}")
    print(f"Cards   → {CARDS_DIR}/")
    print(f"Cache   → {CACHE_DIR}/")

if __name__ == "__main__":
    asyncio.run(main())
