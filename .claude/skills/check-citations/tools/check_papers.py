"""
Tool: check_papers.py
Парсит bibliography.bib, параллельно верифицирует каждую статью и генерирует карточки.

Usage:
  uv run python tools/check_papers.py                        # полный прогон всех статей
  uv run python tools/check_papers.py --test                 # тест (verbose, 5 статей)
  uv run python tools/check_papers.py --recheck key1 key2   # перепроверить конкретные ключи
  uv run python tools/check_papers.py --recheck key1 key2 \\
      --prompt "Focus on whether the year and venue are correct" \\
      --hints key1:"check if this is really in Psych Review" key2:"look for arXiv version"
  uv run python tools/check_papers.py --cards-only           # только карточки (без верификации)

Кеш: .cache/<md5(key)>.json — инвалидируется только для --recheck ключей.
Карточки: papers_cards/<key>.md — пропускаются если verified=true (если не --recheck).
Output: papers_results.json + papers_cards/<key>.md
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
sys.path.insert(0, str(Path(__file__).parent))
from semantic_scholar import search_semantic_scholar, SemanticScholarResult

def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "bibliography.bib").exists():
            return candidate
        if (candidate / "Diploma_latex" / "bibliography.bib").exists():
            return candidate / "Diploma_latex"
    raise FileNotFoundError("Could not find repository root with bibliography.bib")

SKILL_ROOT = Path(__file__).parent.parent
REPO_ROOT = find_repo_root(SKILL_ROOT)

load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT.parent / ".env", override=False)

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
PERPLEXITY_API_KEY = os.environ["PERPLEXITY_API_KEY"]

BIB_FILE = str(REPO_ROOT / "bibliography.bib")
OUTPUT_FILE = str(Path(__file__).parent / "papers_results.json")
CACHE_DIR = Path(__file__).parent / ".cache"
CARDS_DIR = Path(__file__).parent / "papers_cards"

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
    "You have TWO search tools:\n"
    "  • search_perplexity — broad web search, good for obscure or recent papers\n"
    "  • search_semantic_scholar — structured academic database, returns DOI/arXiv/URL/citation count\n\n"
    "Process:\n"
    "1. Call BOTH tools in parallel (or sequentially) at the start: search_perplexity AND search_semantic_scholar.\n"
    "2. Cross-check results: title, authors, year, venue must match.\n"
    "   - If Semantic Scholar finds the paper with matching details → strong evidence for REAL.\n"
    "   - If only Perplexity finds it or results conflict → lower confidence, search more.\n"
    "3. If confidence < 85%, search again with different queries (title only, DOI, arXiv ID, etc.).\n"
    "4. Keep searching (up to 4 calls total) until confidence >= 85% or strategies exhausted.\n"
    "5. Final verdict:\n"
    "   - REAL: Paper confirmed by at least one reliable source, key details match\n"
    "   - FAKE: Appears fabricated or details significantly wrong/misattributed\n"
    "   - UNCERTAIN: Cannot determine after exhaustive search\n\n"
    "Do NOT give a verdict after one search if not confident. Keep searching!\n"
    "End your FINAL response with:\n"
    "```json\n{\"verdict\": \"REAL|FAKE|UNCERTAIN\", \"confidence\": 0-100, \"reason\": \"...\"}\n```"
)

CARD_SYSTEM_PROMPT = (
    "You are an academic paper analyst. Based on search results about a paper, "
    "generate a detailed structured paper card entirely in English. Be thorough and factual. "
    "Use only information confirmed by the search results — do not hallucinate details.\n\n"
    "Output exactly this structure (fill in each section with as much detail as available):\n\n"
    "GOAL: <what the authors aimed to solve — 3-5 sentences covering motivation and scope>\n"
    "GAP: <what open problem or limitation this work addresses — 3-5 sentences, name prior work if known>\n"
    "METHOD: <key technical approach, architecture, or experimental design — 3-5 sentences>\n"
    "DATASETS: <all datasets used with sizes/splits if known, or 'Not applicable' / 'Unknown'>\n"
    "METRICS: <all evaluation metrics used with values where available, or 'Not applicable' / 'Unknown'>\n"
    "RESULTS: <key findings and numbers — 4-6 sentences, include specific numbers and comparisons>\n"
    "LIMITATIONS: <acknowledged limitations or caveats — 2-3 sentences, or 'Not specified'>\n"
    "SOURCE_USED: pdf | arxiv | perplexity | semantic_scholar\n\n"
    "Do not add any other text outside this structure."
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
    },
    {
        "type": "function",
        "function": {
            "name": "search_semantic_scholar",
            "description": (
                "Search the Semantic Scholar academic database for a paper. "
                "Returns structured metadata: DOI, arXiv ID, PDF URL, citation count, venue, canonical paper URL. "
                "Use this alongside search_perplexity for cross-validation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Paper title (required)."},
                    "authors": {"type": "string", "description": "Author list as a string, e.g. 'Kahneman, D. and Tversky, A.'"},
                    "year": {"type": "string", "description": "Publication year, e.g. '2011'"},
                },
                "required": ["title"],
            },
        },
    },
]


# ── Утилиты S2 ───────────────────────────────────────────────────────────────

def _s2_to_dict(s2: "SemanticScholarResult | None") -> dict:
    if s2 is None:
        return {}
    return {
        "paper_id": s2.paper_id,
        "title": s2.title,
        "authors": s2.authors,
        "year": s2.year,
        "venue": s2.venue,
        "doi": s2.doi,
        "arxiv_id": s2.arxiv_id,
        "pdf_url": s2.pdf_url,
        "paper_url": s2.paper_url,
        "citation_count": s2.citation_count,
    }


# ── Кеш верификации ───────────────────────────────────────────────────────────

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


# ── Карточки ──────────────────────────────────────────────────────────────────

def card_path(key: str) -> Path:
    CARDS_DIR.mkdir(exist_ok=True)
    return CARDS_DIR / f"{key}.md"

def card_exists_and_verified(key: str) -> bool:
    p = card_path(key)
    if not p.exists():
        return False
    content = p.read_text(encoding="utf-8")
    return "verified: true" in content

def card_invalidate(key: str):
    p = card_path(key)
    if p.exists():
        p.unlink()
        print(f"  [card] invalidated {key}")

def build_card(entry: dict, result: dict, card_body: str) -> str:
    """Собирает итоговый markdown файл карточки."""
    f = entry["fields"]
    s2 = result.get("_s2") or {}

    # Парсим поля из card_body
    def extract(label: str) -> str:
        m = re.search(rf'^{label}:\s*(.+?)(?=\n[A-Z_]+:|$)', card_body, re.MULTILINE | re.DOTALL)
        return m.group(1).strip() if m else "Unknown"

    goal        = extract("GOAL")
    gap         = extract("GAP")
    method      = extract("METHOD")
    datasets    = extract("DATASETS")
    metrics     = extract("METRICS")
    results_txt = extract("RESULTS")
    limitations = extract("LIMITATIONS")
    source_used = extract("SOURCE_USED")

    verified_flag = "true" if result["verdict"] == "REAL" else "false"

    # Prefer S2 metadata over bib fields when available
    doi      = s2.get("doi") or f.get("doi", "")
    arxiv_id = s2.get("arxiv_id") or f.get("arxiv_id", f.get("eprint", ""))
    pdf_url  = s2.get("pdf_url") or f.get("url", f.get("howpublished", ""))
    s2_id    = s2.get("paper_id", "")
    s2_url   = s2.get("paper_url", "")
    citations = s2.get("citation_count", "")

    lines = [
        "---",
        f"key: {entry['key']}",
        f"title: {f.get('title', 'Unknown')}",
        f"authors: {f.get('author', 'Unknown')}",
        f"year: {f.get('year', 'Unknown')}",
        f"venue: {f.get('journal') or f.get('booktitle') or f.get('publisher', 'Unknown')}",
        f"doi: {doi}",
        f"arxiv_id: {arxiv_id}",
        f"pdf_url: {pdf_url}",
        f"semantic_scholar_id: {s2_id}",
        f"paper_url: {s2_url}",
        f"citation_count: {citations}",
        f"verified: {verified_flag}",
        f"confidence: {result['confidence']}",
        f"source_used: {source_used}",
        "---",
        "",
        "## Goal",
        goal,
        "",
        "## Gap Addressed",
        gap,
        "",
        "## Method",
        method,
        "",
        "## Datasets and Metrics",
        f"**Datasets:** {datasets}",
        "",
        f"**Metrics:** {metrics}",
        "",
        "## Results",
        results_txt,
        "",
        "## Limitations",
        limitations,
        "",
        "## Verification Verdict",
        f"{result['verdict']} ({result['confidence']}%) — {result['reason']}",
    ]

    # Add paper links section when we have any URLs
    links = []
    if s2_url:
        links.append(f"- [Semantic Scholar]({s2_url})")
    if doi:
        links.append(f"- [DOI](https://doi.org/{doi})")
    if arxiv_id:
        links.append(f"- [arXiv](https://arxiv.org/abs/{arxiv_id})")
    if pdf_url and pdf_url not in (s2_url,):
        links.append(f"- [PDF]({pdf_url})")
    if links:
        lines += ["", "## Links"] + links

    return "\n".join(lines) + "\n"


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
    f = entry["fields"]

    # Always query Semantic Scholar in parallel with the agent — independent of qwen3 tool choices
    s2_prefetch_task = asyncio.create_task(search_semantic_scholar(
        title=f.get("title", ""),
        authors=f.get("author", ""),
        year=f.get("year"),
        verbose=verbose,
    ))

    # Await S2 prefetch before entering semaphore (runs in parallel with other agents)
    try:
        s2_prefetched = await asyncio.wait_for(s2_prefetch_task, timeout=20)
    except Exception:
        s2_prefetched = None
    s2_summary = ""
    if s2_prefetched:
        s2_summary = (
            f"[Semantic Scholar pre-search result]\n"
            f"  Title: {s2_prefetched.title}\n"
            f"  Authors: {', '.join(s2_prefetched.authors[:5])}\n"
            f"  Year: {s2_prefetched.year}\n"
            f"  Venue: {s2_prefetched.venue}\n"
            f"  DOI: {s2_prefetched.doi or 'n/a'}\n"
            f"  arXiv: {s2_prefetched.arxiv_id or 'n/a'}\n"
            f"  PDF: {s2_prefetched.pdf_url or 'n/a'}\n"
            f"  Citations: {s2_prefetched.citation_count}\n"
            f"  URL: {s2_prefetched.paper_url}"
        )

    async with semaphore:
        if verbose:
            print(f"\n{'─'*60}\nAGENT: {key}\n{'─'*60}\n{description}\n")
            if s2_prefetched:
                print(f"  [s2 prefetch] {s2_summary[:300]}")

        user_message = f"Verify this bibliography entry:\n\n{description}"
        if s2_prefetched:
            user_message += f"\n\nSemantic Scholar pre-search (already done, use this):\n{s2_summary}"
        else:
            user_message += "\n\n(Semantic Scholar returned no results — use search_perplexity to verify.)"
        if extra_hint:
            user_message += f"\n\nAdditional focus: {extra_hint}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        tool_call_count = 0
        search_results_accumulated = []
        s2_result: SemanticScholarResult | None = s2_prefetched  # best S2 hit found

        if s2_prefetched:
            search_results_accumulated.append(s2_summary)

        for _ in range(8):
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
                # Run all tool calls in parallel
                async def _dispatch(tc):
                    nonlocal tool_call_count, s2_result
                    tool_call_count += 1
                    if tc.function.name == "search_perplexity":
                        query = json.loads(tc.function.arguments)["query"]
                        result_text = await search_perplexity(query, verbose=verbose)
                        if verbose:
                            print(f"\n  [perplexity #{tool_call_count}] {query[:70]}")
                            print(f"  [result] {result_text[:300]}{'...' if len(result_text) > 300 else ''}")
                        search_results_accumulated.append(result_text)
                        return tc.id, result_text

                    elif tc.function.name == "search_semantic_scholar":
                        args = json.loads(tc.function.arguments)
                        hit = await search_semantic_scholar(
                            title=args.get("title", ""),
                            authors=args.get("authors", ""),
                            year=args.get("year"),
                            verbose=verbose,
                        )
                        if hit and s2_result is None:
                            s2_result = hit
                        if hit:
                            summary = (
                                f"Semantic Scholar result:\n"
                                f"  Title: {hit.title}\n"
                                f"  Authors: {', '.join(hit.authors[:5])}\n"
                                f"  Year: {hit.year}\n"
                                f"  Venue: {hit.venue}\n"
                                f"  DOI: {hit.doi or 'n/a'}\n"
                                f"  arXiv: {hit.arxiv_id or 'n/a'}\n"
                                f"  PDF: {hit.pdf_url or 'n/a'}\n"
                                f"  Citations: {hit.citation_count}\n"
                                f"  URL: {hit.paper_url}"
                            )
                        else:
                            summary = "Semantic Scholar: no matching paper found."
                        if verbose:
                            print(f"\n  [s2 #{tool_call_count}] {summary[:300]}")
                        search_results_accumulated.append(summary)
                        return tc.id, summary

                    return tc.id, "Unknown tool"

                dispatched = await asyncio.gather(*[_dispatch(tc) for tc in msg.tool_calls])
                for tc_id, content in dispatched:
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc_id,
                        "content": content,
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
                    "_search_results": search_results_accumulated,
                    "_s2": _s2_to_dict(s2_result),
                }
                cache_set(key, out)
                return out

        out = {
            "key": key, "type": entry["type"], "description": description,
            "verdict": "UNCERTAIN", "confidence": 0,
            "reason": "Agent loop exceeded max iterations", "tool_calls": tool_call_count,
            "_search_results": search_results_accumulated,
            "_s2": _s2_to_dict(s2_result),
        }
        cache_set(key, out)
        return out


# ── Агент-генератор карточек ──────────────────────────────────────────────────

async def card_agent(
    entry: dict,
    result: dict,
    semaphore: asyncio.Semaphore,
    verbose: bool = False,
) -> None:
    """Генерирует карточку papers_cards/<key>.md на основе результатов верификации."""
    key = entry["key"]
    description = entry_to_description(entry)
    search_context = "\n\n---\n\n".join(result.get("_search_results", []))

    if not search_context:
        # Если нет накопленных результатов поиска — запрашиваем Perplexity напрямую
        f = entry["fields"]
        query = f"{f.get('title', '')} {f.get('author', '')} {f.get('year', '')}"
        async with semaphore:
            search_context = await search_perplexity(query, verbose=verbose)

    user_message = (
        f"Paper bibliography entry:\n{description}\n\n"
        f"Verification verdict: {result['verdict']} ({result['confidence']}%)\n"
        f"Reason: {result['reason']}\n\n"
        f"Search results collected during verification:\n{search_context[:6000]}"
    )

    if verbose:
        print(f"\n  [card_agent] Generating card for {key}...")

    async with semaphore:
        response = await openrouter_client.chat.completions.create(
            model=RESEARCHER_MODEL,
            messages=[
                {"role": "system", "content": CARD_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=1200,
        )
    card_body = response.choices[0].message.content or ""

    card_content = build_card(entry, result, card_body)
    card_path(key).write_text(card_content, encoding="utf-8")

    if verbose:
        print(f"  [card] Written: papers_cards/{key}.md")


# ── Прогон списка записей ─────────────────────────────────────────────────────

async def run_entries(
    entries: list[dict],
    semaphore: asyncio.Semaphore,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    hints: dict[str, str] | None = None,
    generate_cards: bool = True,
    cards_only: bool = False,
) -> list[dict]:
    hints = hints or {}
    results = []
    pbar = tqdm(total=len(entries), desc="Verifying", unit="paper")
    card_semaphore = asyncio.Semaphore(3)

    async def _run(entry):
        if cards_only:
            cached = cache_get(entry["key"])
            if cached:
                results.append(cached)
                await card_agent(entry, cached, card_semaphore)
            else:
                print(f"  [skip] No cache for {entry['key']}")
            pbar.set_postfix_str(f"card {entry['key'][:25]}")
            pbar.update(1)
            return

        r = await researcher_agent(entry, semaphore, system_prompt, hints.get(entry["key"], ""))
        results.append(r)
        icon = {"REAL": "✓", "FAKE": "✗", "UNCERTAIN": "?"}.get(r["verdict"], "?")
        pbar.set_postfix_str(f"{icon} {r['key'][:25]}")
        pbar.update(1)

        if generate_cards:
            await card_agent(entry, r, card_semaphore)

    await asyncio.gather(*[_run(e) for e in entries])
    pbar.close()
    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="Verify bibliography entries and generate paper cards")
    parser.add_argument("--n", type=int, metavar="N", help="Run on first N entries from bib (partial run)")
    parser.add_argument("--keys", nargs="+", metavar="KEY", help="Run on specific keys (partial run)")
    parser.add_argument("--recheck", nargs="+", metavar="KEY", help="Keys to recheck (invalidates cache and card)")
    parser.add_argument("--prompt", default="", help="Custom system prompt suffix for --recheck")
    parser.add_argument(
        "--hints", nargs="+", metavar="KEY:HINT",
        help='Per-key hints, e.g. key1:"check venue" key2:"look for DOI"'
    )
    parser.add_argument("--no-cards", action="store_true", help="Skip card generation")
    parser.add_argument("--cards-only", action="store_true", help="Only generate cards from cached results (no re-verification)")
    parser.add_argument("--reset", action="store_true", help="Clear all cache, cards and results before running (irreversible)")
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
    generate_cards = not args.no_cards

    # ── --reset: очищаем кеш, карточки, результаты ────────────────────────────
    if args.reset:
        import shutil
        print("[reset] Clearing cache, cards and results...")
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
            print(f"  removed {CACHE_DIR}")
        if CARDS_DIR.exists():
            shutil.rmtree(CARDS_DIR)
            print(f"  removed {CARDS_DIR}")
        if Path(OUTPUT_FILE).exists():
            Path(OUTPUT_FILE).unlink()
            print(f"  removed {OUTPUT_FILE}")

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

        for e in recheck_entries:
            cache_invalidate(e["key"])
            if generate_cards:
                card_invalidate(e["key"])

        semaphore = asyncio.Semaphore(5)
        new_results = await run_entries(
            recheck_entries, semaphore, system_prompt, hints,
            generate_cards=generate_cards
        )

        existing: list[dict] = []
        if Path(OUTPUT_FILE).exists():
            existing = json.loads(Path(OUTPUT_FILE).read_text(encoding="utf-8"))

        existing_map = {r["key"]: r for r in existing}
        for r in new_results:
            existing_map[r["key"]] = {k: v for k, v in r.items() if not k.startswith("_")}
        merged = list(existing_map.values())

        Path(OUTPUT_FILE).write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nUpdated {len(new_results)} entries → {OUTPUT_FILE}")
        return

    # ── Режим --keys: конкретные ключи ───────────────────────────────────────
    if args.keys:
        missing = [k for k in args.keys if k not in entry_map]
        if missing:
            print(f"[WARN] Keys not found in bib: {missing}")
        entries = [entry_map[k] for k in args.keys if k in entry_map]
        print(f"PARTIAL RUN ({len(entries)} keys): {[e['key'] for e in entries]}")
        semaphore = asyncio.Semaphore(5)
        results = await run_entries(entries, semaphore, system_prompt, hints, generate_cards=generate_cards)

    # ── Режим --n N ──────────────────────────────────────────────────────────
    elif args.n:
        entries = all_entries[:args.n]
        print(f"PARTIAL RUN (first {len(entries)} entries)")
        semaphore = asyncio.Semaphore(5)
        results = await run_entries(entries, semaphore, system_prompt, hints, generate_cards=generate_cards)

    # ── Режим --cards-only ────────────────────────────────────────────────────
    elif args.cards_only:
        # Только для тех, у кого есть кеш
        to_run = [e for e in all_entries if cache_get(e["key"])]
        no_cache = [e for e in all_entries if not cache_get(e["key"])]
        print(f"CARDS-ONLY MODE: {len(to_run)} cached entries  |  {len(no_cache)} skipped (no cache)")
        semaphore = asyncio.Semaphore(5)
        results = await run_entries(to_run, semaphore, cards_only=True)

    # ── Полный прогон ─────────────────────────────────────────────────────────
    else:
        # Пропускаем уже закешированные (и имеющие карточку если нужна)
        def needs_run(e):
            if not cache_get(e["key"]):
                return True
            if generate_cards and not card_exists_and_verified(e["key"]):
                return True
            return False

        to_run = [e for e in all_entries if needs_run(e)]
        cached_results = [cache_get(e["key"]) for e in all_entries if not needs_run(e)]
        print(f"Cached: {len(cached_results)}  To run: {len(to_run)}")

        semaphore = asyncio.Semaphore(5)
        new_results = await run_entries(
            to_run, semaphore, generate_cards=generate_cards
        ) if to_run else []
        results = cached_results + new_results

    # ── Сохраняем и печатаем сводку ───────────────────────────────────────────
    clean_results = [{k: v for k, v in r.items() if not k.startswith("_")} for r in results]
    Path(OUTPUT_FILE).write_text(json.dumps(clean_results, ensure_ascii=False, indent=2), encoding="utf-8")

    real      = [r for r in results if r["verdict"] == "REAL"]
    fake      = [r for r in results if r["verdict"] == "FAKE"]
    uncertain = [r for r in results if r["verdict"] == "UNCERTAIN"]

    print(f"\n{'='*60}\nRESULTS SUMMARY\n{'='*60}")
    print(f"REAL:      {len(real):3d}")
    print(f"FAKE:      {len(fake):3d}")
    print(f"UNCERTAIN: {len(uncertain):3d}")
    print(f"TOTAL:     {len(results):3d}")

    if generate_cards:
        cards_written = len(list(CARDS_DIR.glob("*.md"))) if CARDS_DIR.exists() else 0
        print(f"Cards:     {cards_written:3d}  → papers_cards/")

    for label, group in [("POTENTIALLY FAKE", fake), ("UNCERTAIN", uncertain)]:
        if group:
            print(f"\n{'='*60}\n{label}\n{'='*60}")
            for r in group:
                print(f"\n[{r['key']}] {r['verdict']} {r['confidence']}%  searches={r.get('tool_calls','?')}")
                print(f"  {r['reason']}")

    print(f"\nResults → {OUTPUT_FILE}  |  Cache → {CACHE_DIR}/  |  Cards → {CARDS_DIR}/")

    # Auto-generate summary table
    import subprocess, sys
    table_script = Path(__file__).parent / "generate_summary_table.py"
    subprocess.run([sys.executable, str(table_script)], check=False)


if __name__ == "__main__":
    asyncio.run(main())
