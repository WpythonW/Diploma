"""
check_papers.py — CLI entry point for bibliography verification.
Thin wrapper around modular sub-packages (parser, cache, card_builder, agent, workflow).

Uses LangChain + LangGraph for agent orchestration.

Usage:
  uv run python check_papers.py                        # full run
  uv run python check_papers.py --n 5                  # partial: first 5
  uv run python check_papers.py --keys k1 k2           # specific keys
  uv run python check_papers.py --recheck k1 k2        # recheck specific
  uv run python check_papers.py --cards-only           # cards from cache
  uv run python check_papers.py --no-cards             # skip card gen
  uv run python check_papers.py --reset                # clear everything
"""

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# ── Modular imports ──────────────────────────────────────────────────────────
from parser import parse_bib, entry_to_description
from cache import CACHE_DIR, CARDS_DIR, cache_get, cache_set, cache_invalidate
from cache import card_path, card_exists_and_verified, card_invalidate
from card_builder import build_card
from agent import researcher_agent

# ── Backward-compat re-exports (for tests / external scripts) ────────────────
from parser import parse_bib, entry_to_description
from cache import (
    cache_get, cache_set, cache_invalidate,
    card_path, card_exists_and_verified, card_invalidate,
    CACHE_DIR, CARDS_DIR,
)
from card_builder import build_card
from semantic_scholar import SemanticScholarResult

# ── Config ───────────────────────────────────────────────────────────────────

def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "bibliography.bib").exists():
            return candidate
        if (candidate / "Diploma_latex" / "bibliography.bib").exists():
            return candidate / "Diploma_latex"
    raise FileNotFoundError("Could not find bibliography.bib")

SKILL_ROOT = Path(__file__).parent
REPO_ROOT = find_repo_root(SKILL_ROOT)

load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT.parent / ".env", override=False)

import os
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

BIB_FILE = str(REPO_ROOT / "bibliography.bib")
OUTPUT_FILE = str(Path(__file__).parent / "papers_results.json")

RESEARCHER_MODEL = "qwen/qwen3-235b-a22b-2507"

DEFAULT_SYSTEM_PROMPT = (
    "You are a critical academic research verifier. "
    "Your task: determine if a bibliography entry is a REAL published work or a FABRICATED/HALLUCINATED reference.\n\n"
    "You have TWO search tools:\n"
    "  • search_tavily_tool — web search returning real URLs from arxiv.org and semanticscholar.org\n"
    "  • search_s2_tool — structured academic database, returns DOI/arXiv/URL/citation count\n\n"
    "Process:\n"
    "1. Call BOTH tools in parallel at the start.\n"
    "2. Cross-check results: title, authors, year, venue must match.\n"
    "3. If confidence < 85%, search again with different queries.\n"
    "4. Keep searching (up to 8 calls total) until confidence >= 85% or strategies exhausted.\n"
    "5. Final verdict: REAL / FAKE / UNCERTAIN\n\n"
    "Do NOT give a verdict after one search if not confident. Keep searching!\n"
    "End your final response with:\n"
    "```json\n{\"verdict\": \"REAL|FAKE|UNCERTAIN\", \"confidence\": 0-100, \"reason\": \"...\"}\n```"
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def parse_hints(raw: list[str] | None) -> dict[str, str]:
    if not raw:
        return {}
    result = {}
    for item in raw:
        if ":" in item:
            k, _, v = item.partition(":")
            result[k.strip()] = v.strip().strip('"')
    return result


# ── S2 result converter (backward compat) ───────────────────────────────────

def _s2_to_dict(s2) -> dict:
    if s2 is None:
        return {}
    return {
        "paper_id": s2.paper_id, "title": s2.title,
        "authors": s2.authors, "year": s2.year,
        "venue": s2.venue, "doi": s2.doi,
        "arxiv_id": s2.arxiv_id, "pdf_url": s2.pdf_url,
        "paper_url": s2.paper_url, "citation_count": s2.citation_count,
    }


# ── Pipeline runner ─────────────────────────────────────────────────────────

async def run_entries(
    entries: list[dict],
    semaphore: asyncio.Semaphore,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    hints: dict[str, str] | None = None,
    generate_cards: bool = True,
    cards_only: bool = False,
) -> list[dict]:
    """Run verification + card generation pipeline."""
    hints = hints or {}
    results = []
    pbar = __import__("tqdm").tqdm(total=len(entries), desc="Verifying", unit="paper")
    card_semaphore = asyncio.Semaphore(3)

    openrouter_client = ChatOpenAI(
        model=RESEARCHER_MODEL, api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1", temperature=0.3,
    )

    async def _run(entry):
        key = entry["key"]

        if cards_only:
            cached = cache_get(key)
            if cached:
                results.append(cached)
                if generate_cards:
                    await _generate_card(entry, cached, openrouter_client, card_semaphore)
            pbar.set_postfix_str(f"card {key[:25]}")
            pbar.update(1)
            return

        r = await researcher_agent(
            entry, semaphore, openrouter_client, TAVILY_API_KEY,
            system_prompt, hints.get(key, ""),
        )
        # Cache immediately so partial runs are resumable
        cache_set(key, {k: v for k, v in r.items() if not k.startswith("_")})
        results.append(r)
        icon = {"REAL": "✓", "FAKE": "✗", "UNCERTAIN": "?"}.get(r["verdict"], "?")
        layer_tag = "det" if r.get("layer") == "deterministic" else "llm"
        pbar.set_postfix_str(f"{icon}[{layer_tag}] {r['key'][:20]}")
        pbar.update(1)

        if generate_cards:
            await _generate_card(entry, r, openrouter_client, card_semaphore)

    await asyncio.gather(*[_run(e) for e in entries])
    pbar.close()
    return results


async def _generate_card(entry, result, openrouter_client, semaphore):
    """Generate a paper card from verification results."""
    description = entry_to_description(entry)
    search_context = "\n\n---\n\n".join(result.get("_search_results", []))

    card_system = (
        "You are an academic paper analyst. Generate a structured paper card in English. "
        "Use only information from search results. Output:\n\n"
        "GOAL: <3-5 sentences>\nGAP: <3-5 sentences>\nMETHOD: <3-5 sentences>\n"
        "DATASETS: <datasets>\nMETRICS: <metrics>\nRESULTS: <4-6 sentences>\n"
        "LIMITATIONS: <2-3 sentences>\nSOURCE_USED: pdf | arxiv | perplexity | semantic_scholar"
    )

    user_message = (
        f"Paper: {description}\n\n"
        f"Verdict: {result['verdict']} ({result['confidence']}%)\n"
        f"Reason: {result['reason']}\n\n"
        f"Search results:\n{search_context[:6000]}"
    )

    async with semaphore:
        response = await openrouter_client.ainvoke([
            {"role": "system", "content": card_system},
            {"role": "user", "content": user_message},
        ])
    card_body = response.content or ""
    card_content = build_card(entry, result, card_body)
    p = card_path(entry["key"])
    p.write_text(card_content, encoding="utf-8")


# ── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="Verify bibliography entries")
    parser.add_argument("--n", type=int, metavar="N", help="First N entries")
    parser.add_argument("--keys", nargs="+", metavar="KEY", help="Specific keys")
    parser.add_argument("--recheck", nargs="+", metavar="KEY", help="Recheck keys")
    parser.add_argument("--prompt", default="", help="Custom prompt suffix")
    parser.add_argument("--hints", nargs="+", metavar="KEY:HINT", help="Per-key hints")
    parser.add_argument("--no-cards", action="store_true", help="Skip card generation")
    parser.add_argument("--cards-only", action="store_true", help="Cards from cache only")
    parser.add_argument("--reset", action="store_true", help="Clear cache/cards/results")
    return parser.parse_args()


async def main():
    args = parse_args()
    hints = parse_hints(args.hints)
    generate_cards = not args.no_cards

    if args.reset:
        print("[reset] Clearing cache, cards and results...")
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
        if CARDS_DIR.exists():
            shutil.rmtree(CARDS_DIR)
        if Path(OUTPUT_FILE).exists():
            Path(OUTPUT_FILE).unlink()

    system_prompt = DEFAULT_SYSTEM_PROMPT
    if args.prompt:
        system_prompt += f"\n\nAdditional instructions: {args.prompt}"

    print(f"Parsing {BIB_FILE}...")
    all_entries = parse_bib(BIB_FILE)
    entry_map = {e["key"]: e for e in all_entries}
    print(f"Found {len(all_entries)} entries.")

    # ── --recheck ────────────────────────────────────────────────────────
    if args.recheck:
        missing = [k for k in args.recheck if k not in entry_map]
        if missing:
            print(f"[WARN] Keys not found in bib: {missing}")
        recheck_entries = [entry_map[k] for k in args.recheck if k in entry_map]
        for e in recheck_entries:
            cache_invalidate(e["key"])
            if generate_cards:
                card_invalidate(e["key"])

        semaphore = asyncio.Semaphore(10)
        new_results = await run_entries(
            recheck_entries, semaphore, system_prompt, hints,
            generate_cards=generate_cards,
        )

        existing_map = {}
        if Path(OUTPUT_FILE).exists():
            existing = json.loads(Path(OUTPUT_FILE).read_text(encoding="utf-8"))
            existing_map = {r["key"]: r for r in existing}
        for r in new_results:
            existing_map[r["key"]] = {k: v for k, v in r.items() if not k.startswith("_")}
        Path(OUTPUT_FILE).write_text(
            json.dumps(list(existing_map.values()), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nUpdated {len(new_results)} entries → {OUTPUT_FILE}")
        return

    # ── --keys ───────────────────────────────────────────────────────────
    if args.keys:
        entries = [entry_map[k] for k in args.keys if k in entry_map]
        print(f"PARTIAL RUN ({len(entries)} keys): {[e['key'] for e in entries]}")
        semaphore = asyncio.Semaphore(10)
        results = await run_entries(entries, semaphore, system_prompt, hints,
                                    generate_cards=generate_cards)

    # ── --n N ────────────────────────────────────────────────────────────
    elif args.n:
        entries = all_entries[:args.n]
        print(f"PARTIAL RUN (first {len(entries)} entries)")
        semaphore = asyncio.Semaphore(10)
        results = await run_entries(entries, semaphore, system_prompt, hints,
                                    generate_cards=generate_cards)

    # ── --cards-only ─────────────────────────────────────────────────────
    elif args.cards_only:
        to_run = [e for e in all_entries if cache_get(e["key"])]
        no_cache = [e for e in all_entries if not cache_get(e["key"])]
        print(f"CARDS-ONLY: {len(to_run)} cached  |  {len(no_cache)} skipped")
        semaphore = asyncio.Semaphore(10)
        results = await run_entries(to_run, semaphore, cards_only=True,
                                    generate_cards=generate_cards)

    # ── Full run ─────────────────────────────────────────────────────────
    else:
        def needs_run(e):
            if not cache_get(e["key"]):
                return True
            if generate_cards and not card_exists_and_verified(e["key"]):
                return True
            return False

        to_run = [e for e in all_entries if needs_run(e)]
        cached_results = [cache_get(e["key"]) for e in all_entries if not needs_run(e)]
        print(f"Cached: {len(cached_results)}  To run: {len(to_run)}")

        semaphore = asyncio.Semaphore(10)
        new_results = await run_entries(
            to_run, semaphore, generate_cards=generate_cards,
        ) if to_run else []
        results = cached_results + new_results

    # ── Save & summary ───────────────────────────────────────────────────
    clean = [{k: v for k, v in r.items() if not k.startswith("_")} for r in results]
    Path(OUTPUT_FILE).write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")

    real = [r for r in results if r["verdict"] == "REAL"]
    fake = [r for r in results if r["verdict"] == "FAKE"]
    uncertain = [r for r in results if r["verdict"] == "UNCERTAIN"]

    print(f"\n{'='*60}\nRESULTS SUMMARY\n{'='*60}")
    print(f"REAL:      {len(real):3d}")
    print(f"FAKE:      {len(fake):3d}")
    print(f"UNCERTAIN: {len(uncertain):3d}")
    print(f"TOTAL:     {len(results):3d}")

    if generate_cards:
        cards_written = len(list(CARDS_DIR.glob("*.md"))) if CARDS_DIR.exists() else 0
        print(f"Cards:     {cards_written:3d}  → papers_cards/")

    # ── API usage stats ──────────────────────────────────────────────────
    def _sum_api(key):
        return sum(r.get("api_calls", {}).get(key, 0) for r in results)

    det_count = sum(1 for r in results if r.get("layer") == "deterministic")
    llm_count = sum(1 for r in results if r.get("layer") == "llm")

    print(f"\n{'='*60}\nAPI USAGE\n{'='*60}")
    print(f"Layer breakdown:   deterministic={det_count}  llm={llm_count}")
    print(f"arXiv lookups:     {_sum_api('arxiv'):4d}")
    print(f"S2 prefetch:       {_sum_api('s2_prefetch'):4d}")
    print(f"arXiv title search:{_sum_api('arxiv_title'):4d}")
    print(f"S2 tool (LLM):     {_sum_api('s2_tool'):4d}")
    print(f"CrossRef calls:    {_sum_api('crossref'):4d}")
    print(f"OpenAlex calls:    {_sum_api('openalex'):4d}")
    print(f"Tavily calls:      {_sum_api('tavily'):4d}")
    print(f"Tavily extract:    {_sum_api('tavily_extract'):4d}")
    print(f"LLM (qwen) calls:  {_sum_api('llm'):4d}")

    # Per-paper medians for LLM path only
    llm_results = [r for r in results if r.get("layer") == "llm"]
    if llm_results:
        import statistics
        tav_per = [r.get("api_calls", {}).get("tavily", 0) for r in llm_results]
        s2t_per = [r.get("api_calls", {}).get("s2_tool", 0) for r in llm_results]
        print(f"\nFor LLM-path papers (n={len(llm_results)}):")
        print(f"  Tavily/paper:      median={statistics.median(tav_per)}  max={max(tav_per)}")
        print(f"  S2 tool/paper:     median={statistics.median(s2t_per)}   max={max(s2t_per)}")

    for label, group in [("POTENTIALLY FAKE", fake), ("UNCERTAIN", uncertain)]:
        if group:
            print(f"\n{'='*60}\n{label}\n{'='*60}")
            for r in group:
                print(f"\n[{r['key']}] {r['verdict']} {r['confidence']}%  searches={r.get('tool_calls','?')}")
                print(f"  {r['reason']}")

    print(f"\nResults → {OUTPUT_FILE}  |  Cache → {CACHE_DIR}/  |  Cards → {CARDS_DIR}/")

    table_script = Path(__file__).parent / "generate_summary_table.py"
    subprocess.run([sys.executable, str(table_script)], check=False)


if __name__ == "__main__":
    asyncio.run(main())
