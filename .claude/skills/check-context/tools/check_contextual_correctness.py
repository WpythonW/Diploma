"""
check_contextual_correctness.py — Two-phase citation checker.

Phase 1 (fast, fully parallel):
  - Card-only LLM check for all keys → OK / WARNING / ERROR
  - No web requests, pure inference

Phase 2 (ERROR only, parallel):
  - Tavily search by exact title+authors+year → verify we found the right paper
  - Tavily extract on best URL → re-check only the ERROR mentions
  - WARNING stays as-is (card is sufficient)

Usage:
    uv run python check_contextual_correctness.py
    uv run python check_contextual_correctness.py --keys binz2023using kahneman2011thinking
    uv run python check_contextual_correctness.py --recheck
    uv run python check_contextual_correctness.py --phase1-only
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from tavily import AsyncTavilyClient

# ── Paths ─────────────────────────────────────────────────────────────────────

TOOLS_DIR = Path(__file__).parent
REPO_ROOT = TOOLS_DIR.parents[3]
CITATIONS_TOOLS_DIR = REPO_ROOT / ".claude/skills/check-citations/tools"
CARDS_DIR = CITATIONS_TOOLS_DIR / "papers_cards"
RESULTS_DIR = TOOLS_DIR / "context_check_results"
EXTRACT_DIR = TOOLS_DIR / "papers_extract"   # cached Tavily extracts for ERROR keys
LATEX_DIR = REPO_ROOT / "Diploma_latex"

_SKIP_TEX = {"preamble", "abbreviations", "terms", "config-formulas",
              "config-images", "config-lists", "config-tables"}

# ── Config ────────────────────────────────────────────────────────────────────

load_dotenv(CITATIONS_TOOLS_DIR / ".env")
load_dotenv(REPO_ROOT / ".env", override=False)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
TAVILY_API_KEY     = os.environ.get("TAVILY_API_KEY", "")
QWEN_MODEL         = "qwen/qwen3-235b-a22b-2507"

PHASE1_CONCURRENCY = 8
PHASE2_CONCURRENCY = 4
EXTRACT_MAX_CHARS  = 20_000   # enough for abstract + intro + key sections

# ── Citation extraction ───────────────────────────────────────────────────────

_CITE_RE = re.compile(r"\\cite\{([^}]+)\}")


def _extract_paragraphs_with_cite(tex_path: Path, key: str) -> list[dict]:
    text = tex_path.read_text(encoding="utf-8", errors="replace")
    results = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        all_keys: list[str] = []
        for m in _CITE_RE.finditer(para):
            all_keys.extend(k.strip() for k in m.group(1).split(","))
        if key in all_keys:
            results.append({"file": tex_path.name, "paragraph": para})
    return results


def collect_mentions(key: str) -> list[dict]:
    mentions = []
    for tex_path in sorted(LATEX_DIR.glob("*.tex")):
        if tex_path.stem in _SKIP_TEX:
            continue
        mentions.extend(_extract_paragraphs_with_cite(tex_path, key))
    return mentions


# ── Card loading ──────────────────────────────────────────────────────────────

def load_card(key: str) -> str | None:
    path = CARDS_DIR / f"{key}.md"
    return path.read_text(encoding="utf-8") if path.exists() else None


def _card_meta(card_text: str) -> dict:
    meta: dict = {}
    in_front = False
    for line in card_text.splitlines():
        if line.strip() == "---":
            if not in_front:
                in_front = True
                continue
            else:
                break
        if in_front and ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta


# ── Tavily helpers (Phase 2) ──────────────────────────────────────────────────

async def _tavily_search_and_extract(
    title: str,
    authors: str,
    year: str,
    key: str,
) -> tuple[str | None, str]:
    """
    Search Tavily for the paper by exact title+authors+year.
    Verify the top result actually matches (title similarity check).
    Extract up to EXTRACT_MAX_CHARS from the best URL.
    Returns (extracted_text_or_None, source_url).
    """
    # Check cache
    cache_path = EXTRACT_DIR / f"{key}.txt"
    if cache_path.exists():
        text = cache_path.read_text(encoding="utf-8")
        if len(text) > 200:
            return text, "cache"

    client = AsyncTavilyClient(api_key=TAVILY_API_KEY)
    query = f'"{title}" {authors} {year}'

    try:
        search_resp = await client.search(
            query,
            max_results=5,
            include_domains=["arxiv.org", "semanticscholar.org", "scholar.google.com",
                             "aclanthology.org", "openreview.net", "pnas.org"],
        )
    except Exception as e:
        return None, f"tavily_search_error: {e}"

    hits = search_resp.get("results", [])
    if not hits:
        return None, "no_results"

    # Verify: check that the top result title contains key words from our title
    title_words = set(title.lower().split()) - {"the", "a", "an", "of", "in", "on", "for", "and"}
    best_url = None
    for hit in hits:
        hit_title = hit.get("title", "").lower()
        hit_url   = hit.get("url", "")
        overlap = sum(1 for w in title_words if w in hit_title)
        if overlap >= max(2, len(title_words) // 2):
            best_url = hit_url
            break

    if not best_url:
        # Fallback: use first result but flag it
        best_url = hits[0].get("url", "")

    # Extract text from the best URL
    try:
        extract_resp = await client.extract(urls=[best_url])
        results = extract_resp.get("results") or []
        if not results:
            return None, f"extract_empty:{best_url}"
        raw = results[0].get("raw_content", "")
        if len(raw) < 200:
            return None, f"extract_too_short:{best_url}"

        # Verify extracted text mentions the paper title or authors
        raw_lower = raw.lower()
        title_match = any(w in raw_lower for w in list(title_words)[:5])
        if not title_match:
            return None, f"extract_mismatch:{best_url}"

        text = raw[:EXTRACT_MAX_CHARS]
        EXTRACT_DIR.mkdir(exist_ok=True)
        cache_path.write_text(text, encoding="utf-8")
        return text, best_url

    except Exception as e:
        return None, f"extract_error: {e}"


# ── JSON parsing ──────────────────────────────────────────────────────────────

def _parse_verdict(text: str, key: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    for pattern in [r"```json\s*(.*?)\s*```", r"```\s*(.*?)\s*```"]:
        m = re.search(pattern, text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
    m2 = re.search(r"\{.*\}", text, re.DOTALL)
    if m2:
        try:
            return json.loads(m2.group(0))
        except json.JSONDecodeError:
            pass
    return {
        "key": key,
        "overall": "ERROR",
        "mentions": [],
        "summary": f"[Parse error] Raw: {text[:300]}",
    }


# ── Phase 1: fast card-only check ────────────────────────────────────────────

_PHASE1_SYSTEM = """\
You are a strict academic reviewer checking whether citations in a diploma thesis \
are contextually correct and accurate.

You receive a paper card (structured summary: goal, method, key findings, limitations) \
and thesis paragraphs that cite this paper.

Rules:
- Judge based on the card ONLY. Do not invent information not in the card.
- Be strict: if the thesis overstates, misattributes, or misrepresents the paper → ERROR.
- If the claim is vague, tangential, or slightly imprecise → WARNING.
- Only OK if the thesis accurately represents what the card says the paper actually found.

Output ONLY valid JSON, no markdown fences, no explanation outside the JSON:

{
  "key": "<key>",
  "overall": "OK" | "WARNING" | "ERROR",
  "phase": 1,
  "mentions": [
    {
      "file": "<filename>",
      "snippet": "<first 120 chars of paragraph>",
      "verdict": "OK" | "WARNING" | "ERROR",
      "comment": "<1-2 sentences in Russian>"
    }
  ],
  "summary": "<2-3 sentence summary in Russian>"
}
"""


async def phase1_check(
    key: str,
    mentions: list[dict],
    card_text: str,
    client: ChatOpenAI,
    semaphore: asyncio.Semaphore,
) -> dict:
    mentions_text = "\n\n".join(
        f"[{i+1}] File: {m['file']}\n{m['paragraph']}"
        for i, m in enumerate(mentions)
    )
    user_msg = (
        f"## Paper card for `{key}`\n\n{card_text}\n\n"
        f"---\n\n## Thesis mentions ({len(mentions)} total)\n\n{mentions_text}"
    )

    t0 = time.perf_counter()
    async with semaphore:
        resp = await client.ainvoke([
            {"role": "system", "content": _PHASE1_SYSTEM},
            HumanMessage(content=user_msg),
        ])
    elapsed = round(time.perf_counter() - t0, 1)

    verdict = _parse_verdict(resp.content, key)
    verdict["key"] = key
    verdict["phase"] = 1
    verdict["mention_count"] = len(mentions)
    verdict["elapsed_sec"] = elapsed
    verdict["fulltext_available"] = False
    return verdict


# ── Phase 2: Tavily research for ERROR keys only ──────────────────────────────

_PHASE2_SYSTEM = """\
You are a strict academic reviewer doing a deep re-check of citations marked ERROR.

You receive:
1. A paper card (structured summary).
2. Web-extracted text from the actual paper (or a related page).
3. Thesis paragraphs flagged as ERROR in a preliminary check.

Your job:
- Re-verify each ERROR mention using the extracted text.
- If the extracted text confirms the error → keep ERROR with a verbatim quote.
- If the extracted text shows the thesis claim is actually correct → downgrade to OK or WARNING.
- For every non-OK verdict: provide a verbatim quote from the extracted text.

Output ONLY valid JSON, no markdown fences:

{
  "key": "<key>",
  "overall": "OK" | "WARNING" | "ERROR",
  "phase": 2,
  "fulltext_available": true | false,
  "fulltext_source": "<url or 'cache' or 'not_found'>",
  "mentions": [
    {
      "file": "<filename>",
      "snippet": "<first 120 chars>",
      "verdict": "OK" | "WARNING" | "ERROR",
      "comment": "<explanation in Russian>",
      "paper_quote": "<verbatim quote from extracted text, or null if OK>"
    }
  ],
  "summary": "<2-4 sentence summary in Russian>"
}
"""


async def phase2_check(
    key: str,
    mentions: list[dict],
    card_text: str,
    phase1_result: dict,
    client: ChatOpenAI,
    semaphore: asyncio.Semaphore,
) -> dict:
    meta = _card_meta(card_text)
    title   = meta.get("title", key)
    authors = meta.get("authors", "")
    year    = meta.get("year", "")

    # Fetch via Tavily (cached after first run)
    t_fetch = time.perf_counter()
    extracted, source = await _tavily_search_and_extract(title, authors, year, key)
    fetch_elapsed = round(time.perf_counter() - t_fetch, 1)

    # Only pass ERROR mentions to phase 2
    error_snippets = {
        m.get("snippet", "")[:60]
        for m in phase1_result.get("mentions", [])
        if m.get("verdict") == "ERROR"
    }
    error_mentions = [
        m for m in mentions
        if any(
            snip in m["paragraph"][:120] or m["paragraph"][:60] in snip
            for snip in error_snippets
        )
    ] or mentions  # fallback: all if matching fails

    mentions_text = "\n\n".join(
        f"[{i+1}] File: {m['file']}\n{m['paragraph']}"
        for i, m in enumerate(error_mentions)
    )

    extract_section = (
        f"\n\n## Extracted paper text ({len(extracted):,} chars, source: {source})\n\n{extracted}"
        if extracted
        else "\n\n## Extracted paper text: NOT AVAILABLE — use card only."
    )

    user_msg = (
        f"## Paper card for `{key}`\n\n{card_text}\n\n"
        f"---\n\n## ERROR mentions to re-check ({len(error_mentions)} total)\n\n"
        f"{mentions_text}"
        + extract_section
    )

    t_llm = time.perf_counter()
    async with semaphore:
        resp = await client.ainvoke([
            {"role": "system", "content": _PHASE2_SYSTEM},
            HumanMessage(content=user_msg),
        ])
    llm_elapsed = round(time.perf_counter() - t_llm, 1)

    verdict = _parse_verdict(resp.content, key)
    verdict["key"] = key
    verdict["phase"] = 2
    verdict["mention_count"] = len(mentions)
    verdict["fulltext_available"] = extracted is not None
    verdict["fulltext_source"] = source
    verdict["elapsed_sec"] = round(fetch_elapsed + llm_elapsed, 1)
    verdict["timing"] = {"fetch_sec": fetch_elapsed, "llm_sec": llm_elapsed}

    # Merge: keep OK/WARNING mentions from phase1, replace ERROR mentions with phase2 result
    p2_by_snippet: dict[str, dict] = {}
    for m in verdict.get("mentions", []):
        p2_by_snippet[m.get("snippet", "")[:60]] = m

    merged_mentions = []
    for m1 in phase1_result.get("mentions", []):
        snip = m1.get("snippet", "")[:60]
        if m1.get("verdict") == "ERROR" and snip in p2_by_snippet:
            merged_mentions.append(p2_by_snippet[snip])
        else:
            merged_mentions.append(m1)
    verdict["mentions"] = merged_mentions or verdict.get("mentions", [])

    # Recompute overall from merged mentions
    verdicts_set = {m.get("verdict") for m in verdict["mentions"]}
    if "ERROR" in verdicts_set:
        verdict["overall"] = "ERROR"
    elif "WARNING" in verdicts_set:
        verdict["overall"] = "WARNING"
    else:
        verdict["overall"] = "OK"

    return verdict


# ── Main pipeline ─────────────────────────────────────────────────────────────

async def run(
    keys: list[str],
    results_dir: Path,
    recheck: bool = False,
    phase1_only: bool = False,
) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    client = ChatOpenAI(
        model=QWEN_MODEL,
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        temperature=0.3,
    )

    sem1 = asyncio.Semaphore(PHASE1_CONCURRENCY)
    sem2 = asyncio.Semaphore(PHASE2_CONCURRENCY)

    total = len(keys)

    # ── Collect work items ────────────────────────────────────────────────────
    work: list[tuple[str, list[dict], str]] = []
    cached: dict[str, dict] = {}

    for key in keys:
        out_path = results_dir / f"{key}.json"
        if out_path.exists() and not recheck:
            r = json.loads(out_path.read_text())
            cached[key] = r
            continue
        card_text = load_card(key)
        if card_text is None:
            print(f"  SKIP {key} — no card", flush=True)
            continue
        mentions = collect_mentions(key)
        if not mentions:
            print(f"  SKIP {key} — not cited in .tex", flush=True)
            r = {"key": key, "overall": "NOT_CITED", "phase": 0, "mentions": [],
                 "summary": "Ключ есть в библиографии, но не встречается в тексте."}
            out_path.write_text(json.dumps(r, ensure_ascii=False, indent=2))
            continue
        work.append((key, mentions, card_text))

    # ── Phase 1 ───────────────────────────────────────────────────────────────
    print(f"{'='*60}", flush=True)
    print(f"PHASE 1 — card-only ({len(work)} to run, {len(cached)} cached, "
          f"concurrency={PHASE1_CONCURRENCY})", flush=True)
    print(f"{'='*60}", flush=True)

    phase1: dict[str, dict] = {}

    if work:
        async def _p1(key: str, mentions: list[dict], card: str) -> tuple[str, dict]:
            return key, await phase1_check(key, mentions, card, client, sem1)

        tasks = [_p1(k, m, c) for k, m, c in work]
        done = 0
        for coro in asyncio.as_completed(tasks):
            key, result = await coro
            phase1[key] = result
            done += 1
            v = result.get("overall", "?")
            n = result.get("mention_count", 0)
            t = result.get("elapsed_sec", 0)
            print(f"  [{done}/{len(work)}] {key} — {v} ({n} mentions, {t}s)", flush=True)
            out_path = results_dir / f"{key}.json"
            out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    if phase1_only:
        _print_summary(results_dir)
        return

    # ── Phase 2: ERROR keys only ──────────────────────────────────────────────
    all_p1: dict[str, dict] = {**cached, **phase1}

    error_keys = [k for k, r in all_p1.items() if r.get("overall") == "ERROR"]

    print(flush=True)
    print(f"{'='*60}", flush=True)
    print(f"PHASE 2 — Tavily re-check ({len(error_keys)} ERROR keys, "
          f"concurrency={PHASE2_CONCURRENCY})", flush=True)
    print(f"{'='*60}", flush=True)

    if not error_keys:
        print("  Nothing to re-check.", flush=True)
    else:
        p2_work = []
        for key in error_keys:
            existing = all_p1[key]
            if existing.get("phase", 1) >= 2 and not recheck:
                print(f"  CACHED-P2 {key} — {existing.get('overall')}", flush=True)
                continue
            card_text = load_card(key)
            if card_text is None:
                continue
            mentions = collect_mentions(key)
            p2_work.append((key, mentions, card_text, existing))

        if p2_work:
            async def _p2(
                key: str, mentions: list[dict], card: str, p1: dict
            ) -> tuple[str, dict]:
                return key, await phase2_check(key, mentions, card, p1, client, sem2)

            tasks2 = [_p2(k, m, c, p1) for k, m, c, p1 in p2_work]
            done2 = 0
            for coro in asyncio.as_completed(tasks2):
                key, result = await coro
                done2 += 1
                v  = result.get("overall", "?")
                t  = result.get("elapsed_sec", 0)
                ft = "✓" if result.get("fulltext_available") else "✗"
                src = result.get("fulltext_source", "?")
                timing = result.get("timing", {})
                print(
                    f"  [{done2}/{len(p2_work)}] {key} — {v} | "
                    f"fetch={timing.get('fetch_sec',0)}s "
                    f"llm={timing.get('llm_sec',0)}s | "
                    f"extract={ft} ({src})",
                    flush=True,
                )
                out_path = results_dir / f"{key}.json"
                out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    _print_summary(results_dir)


def _print_summary(results_dir: Path) -> None:
    counts: dict[str, int] = {}
    for p in results_dir.glob("*.json"):
        try:
            v = json.loads(p.read_text()).get("overall", "?")
            counts[v] = counts.get(v, 0) + 1
        except Exception:
            pass
    total = sum(counts.values())
    print(flush=True)
    print(f"DONE — {total} keys", flush=True)
    print(f"  OK:         {counts.get('OK', 0)}", flush=True)
    print(f"  WARNING:    {counts.get('WARNING', 0)}", flush=True)
    print(f"  ERROR:      {counts.get('ERROR', 0)}", flush=True)
    print(f"  NOT_CITED:  {counts.get('NOT_CITED', 0)}", flush=True)
    print(f"Results: {results_dir}", flush=True)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Two-phase citation checker: card-only + Tavily re-check for ERRORs."
    )
    parser.add_argument("--keys", nargs="*", metavar="KEY")
    parser.add_argument("--out", default=str(RESULTS_DIR), metavar="DIR")
    parser.add_argument("--recheck", action="store_true",
                        help="Force re-run both phases.")
    parser.add_argument("--phase1-only", action="store_true",
                        help="Run phase 1 only (no Tavily re-check).")
    args = parser.parse_args()

    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    keys = args.keys if args.keys else sorted(p.stem for p in CARDS_DIR.glob("*.md"))
    if not keys:
        print("No keys found.")
        sys.exit(0)

    asyncio.run(run(keys, Path(args.out), recheck=args.recheck, phase1_only=args.phase1_only))


if __name__ == "__main__":
    main()
