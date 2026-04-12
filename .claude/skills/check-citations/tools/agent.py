"""
agent.py — Researcher agent using LangChain + LangGraph.

Architecture (3 layers):

LAYER 1 — Deterministic lookup (parallel):
  - arXiv API by arxiv_id if present in entry
  - Semantic Scholar by title (always)

LAYER 2 — Rule-based verdict:
  - If arXiv ID found AND title matches AND authors match → REAL (skip LLM)
  - If arXiv ID present but points to different paper → FAKE (skip LLM)
  - Otherwise → UNCERTAIN → proceed to Layer 3

LAYER 3 — LLM ReAct agent (LangGraph):
  - Only called when deterministic layers cannot decide
  - Tools: search_perplexity + search_s2_tool
  - Reduces Perplexity cost by ~60-70% vs. old algorithm
"""

import asyncio
import json
import re
from pathlib import Path
from typing import TypedDict, Annotated, Sequence, Literal

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from semantic_scholar import search_semantic_scholar, SemanticScholarResult
from arxiv_lookup import lookup_arxiv, extract_arxiv_id, ArxivResult, search_arxiv_by_title_sync
from crossref_lookup import search_crossref_sync
from openalex_lookup import search_openalex_sync
from author_normalize import authors_match, MatchResult


# ── Thresholds ────────────────────────────────────────────────────────────────

TITLE_SIM_THRESHOLD = 0.6   # min token-overlap for title match
AUTHOR_SCORE_THRESHOLD = 0.5  # min fraction of bib authors that must match


# ── Internal helpers ─────────────────────────────────────────────────────────

def _title_tokens_overlap(a: str, b: str) -> float:
    """Token overlap similarity in [0, 1]."""
    ta = set(a.lower().split())
    tb = set(b.lower().split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta), len(tb))


def _extract_arxiv_from_entry(fields: dict) -> str | None:
    """Extract arXiv ID from any relevant field in a bib entry."""
    for field in ("arxiv_id", "eprint", "url", "howpublished", "note"):
        val = fields.get(field, "")
        if val:
            arxiv_id = extract_arxiv_id(val)
            if arxiv_id:
                return arxiv_id
    return None


def _layer1_verdict(
    bib_title: str,
    bib_authors: str,
    bib_year: str | None,
    arxiv_result: ArxivResult | None,
    s2_result: SemanticScholarResult | None,
) -> tuple[str, int, str] | None:
    """
    Apply rule-based verdict from deterministic sources.

    Returns (verdict, confidence, reason) or None if LLM needed.
    """
    evidence = []
    title_confirmed = False
    authors_confirmed = False

    # ── Check arXiv result ────────────────────────────────────────────────
    if arxiv_result is not None:
        title_sim = _title_tokens_overlap(bib_title, arxiv_result.title)
        author_match = authors_match(bib_authors, arxiv_result.authors)

        if title_sim < TITLE_SIM_THRESHOLD:
            # arXiv ID exists but points to a different paper → FAKE
            reason = (
                f"arXiv ID found but title mismatch: "
                f"bib='{bib_title[:60]}' vs found='{arxiv_result.title[:60]}' "
                f"(similarity={title_sim:.2f})"
            )
            return ("FAKE", 90, reason)

        title_confirmed = True
        evidence.append(f"arXiv: title match (sim={title_sim:.2f})")

        if author_match.verdict in ("MATCH", "PARTIAL"):
            authors_confirmed = True
            evidence.append(
                f"arXiv: authors match ({author_match.matched}/{author_match.total_bib})"
            )
        elif author_match.verdict == "MISMATCH":
            reason = (
                f"arXiv ID found and title matches, but author mismatch: "
                f"bib='{bib_authors[:80]}' vs found={arxiv_result.authors[:3]}"
            )
            return ("FAKE", 85, reason)
        # UNKNOWN author match → not enough to conclude, continue

    # ── Check S2 result ───────────────────────────────────────────────────
    if s2_result is not None:
        title_sim_s2 = _title_tokens_overlap(bib_title, s2_result.title)
        if title_sim_s2 >= TITLE_SIM_THRESHOLD:
            title_confirmed = True
            evidence.append(f"S2: title match (sim={title_sim_s2:.2f})")

            author_match_s2 = authors_match(bib_authors, s2_result.authors)
            if author_match_s2.verdict in ("MATCH", "PARTIAL"):
                authors_confirmed = True
                evidence.append(
                    f"S2: authors match ({author_match_s2.matched}/{author_match_s2.total_bib})"
                )

    # ── Decide ────────────────────────────────────────────────────────────
    if title_confirmed and authors_confirmed:
        # Year check (soft — not a dealbreaker)
        year_note = ""
        if bib_year and arxiv_result and arxiv_result.year:
            if str(arxiv_result.year) != str(bib_year):
                year_note = f" (year mismatch: bib={bib_year}, found={arxiv_result.year})"

        reason = "; ".join(evidence) + year_note
        confidence = 95 if not year_note else 80
        return ("REAL", confidence, reason)

    # Not enough evidence → let LLM decide
    return None


# ── Tavily helpers ────────────────────────────────────────────────────────────

_tavily_cache: dict[str, str] = {}


def _tavily_search_sync(query: str, api_key: str) -> str:
    """Sync Tavily search — safe to call from thread pool.

    Returns a formatted string with real URLs + snippets so the LLM agent
    can verify titles, authors, and venues deterministically.
    """
    if query in _tavily_cache:
        return _tavily_cache[query]

    from tavily import TavilyClient
    client = TavilyClient(api_key=api_key)
    resp = client.search(
        query,
        max_results=5,
        include_domains=["arxiv.org", "semanticscholar.org"],
    )
    hits = resp.get("results") or []
    if not hits:
        result = "Tavily: no results found."
    else:
        lines = ["Tavily search results:"]
        for i, h in enumerate(hits, 1):
            lines.append(
                f"  [{i}] score={h.get('score', 0):.2f} | {h.get('title', '')[:80]}\n"
                f"       url: {h.get('url', '')}\n"
                f"       {h.get('content', '')[:200]}"
            )
        result = "\n".join(lines)

    _tavily_cache[query] = result
    return result


def _s2_search_sync(title: str, authors: str = "", year: str = "") -> str:
    """Sync S2 search using requests — safe to call from thread pool."""
    import requests
    params = {"query": title, "fields": "title,authors,year,venue,externalIds,openAccessPdf,url,citationCount", "limit": 5}
    try:
        resp = requests.get("https://api.semanticscholar.org/graph/v1/paper/search", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return "Semantic Scholar: request failed."

    hits = (data or {}).get("data") or []
    if not hits:
        return "Semantic Scholar: no matching paper found."

    # Pick best by title similarity
    from semantic_scholar import _title_similarity
    scored = sorted(hits, key=lambda h: -_title_similarity(title, h.get("title", "")))
    hit = scored[0]
    ext = hit.get("externalIds") or {}
    oap = hit.get("openAccessPdf") or {}
    authors_found = ", ".join(a.get("name", "") for a in (hit.get("authors") or [])[:5])
    return (
        f"Semantic Scholar result:\n"
        f"  Title: {hit.get('title','')}\n"
        f"  Authors: {authors_found}\n"
        f"  Year: {hit.get('year','')}\n"
        f"  Venue: {hit.get('venue','')}\n"
        f"  DOI: {ext.get('DOI','n/a')}\n"
        f"  arXiv: {ext.get('ArXiv','n/a')}\n"
        f"  PDF: {oap.get('url','n/a')}\n"
        f"  Citations: {hit.get('citationCount',0)}\n"
        f"  URL: https://www.semanticscholar.org/paper/{hit.get('paperId','')}"
    )


async def _s2_search_impl(title: str, authors: str = "", year: str = "") -> str:
    hit = await search_semantic_scholar(title=title, authors=authors, year=year, verbose=False)
    if hit is None:
        return "Semantic Scholar: no matching paper found."
    return (
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


# ── Agent state ───────────────────────────────────────────────────────────────

class ApiCalls(TypedDict):
    arxiv: int          # arXiv API lookups by ID (Layer 1)
    arxiv_title: int    # arXiv title search calls from LLM tool
    s2_prefetch: int    # S2 calls in Layer 1
    s2_tool: int        # S2 calls from LLM tool
    crossref: int       # CrossRef calls from LLM tool
    openalex: int       # OpenAlex calls from LLM tool
    tavily: int         # Tavily search calls from LLM tool
    tavily_extract: int # Tavily extract (full-text) calls from LLM tool
    llm: int            # qwen LLM invocations (0 or 1)


class VerifyResult(TypedDict):
    key: str
    type: str
    description: str
    verdict: Literal["REAL", "FAKE", "UNCERTAIN"]
    confidence: int
    reason: str
    tool_calls: int
    prompt_variant: str
    layer: str              # "deterministic" | "llm"
    api_calls: ApiCalls
    _search_results: list[str]
    _s2: dict
    _arxiv: dict


# ── Main entry point ─────────────────────────────────────────────────────────

async def researcher_agent(
    entry: dict,
    semaphore: asyncio.Semaphore,
    openrouter_client: ChatOpenAI,
    tavily_api_key: str,
    system_prompt: str = "",
    extra_hint: str = "",
    verbose: bool = False,
) -> VerifyResult:
    """
    Verify a bibliography entry.

    Layer 1: arXiv API + Semantic Scholar (deterministic, parallel).
    Layer 2: Rule-based verdict (author normalization + title similarity).
    Layer 3: LLM ReAct agent (only if layers 1-2 are inconclusive).
    """
    from parser import entry_to_description

    key = entry["key"]
    description = entry_to_description(entry)
    f = entry["fields"]
    bib_title = f.get("title", "")
    bib_authors = f.get("author", "")
    bib_year = f.get("year")

    # ── Layer 1: parallel deterministic lookup ────────────────────────────
    arxiv_raw = _extract_arxiv_from_entry(f)

    async def _fetch_arxiv():
        if not arxiv_raw:
            return None
        try:
            return await asyncio.wait_for(lookup_arxiv(arxiv_raw), timeout=15)
        except Exception:
            return None

    async def _fetch_s2():
        try:
            return await asyncio.wait_for(
                search_semantic_scholar(
                    title=bib_title, authors=bib_authors, year=bib_year, verbose=False
                ),
                timeout=20,
            )
        except Exception:
            return None

    if verbose:
        print(f"  [{key}] Layer 1: fetching arXiv={arxiv_raw or 'none'} + S2...")

    arxiv_result, s2_result = await asyncio.gather(_fetch_arxiv(), _fetch_s2())
    _api_calls: ApiCalls = {
        "arxiv": 1 if arxiv_raw else 0,
        "arxiv_title": 0,
        "s2_prefetch": 1,
        "s2_tool": 0,
        "crossref": 0,
        "openalex": 0,
        "tavily": 0,
        "tavily_extract": 0,
        "llm": 0,
    }

    if verbose:
        print(f"  [{key}] arXiv={'found' if arxiv_result else 'none'}  "
              f"S2={'found' if s2_result else 'none'}")

    # ── Layer 2: rule-based verdict ───────────────────────────────────────
    layer1_decision = _layer1_verdict(bib_title, bib_authors, bib_year, arxiv_result, s2_result)

    arxiv_dict = {}
    if arxiv_result:
        arxiv_dict = {
            "arxiv_id": arxiv_result.arxiv_id,
            "title": arxiv_result.title,
            "authors": arxiv_result.authors,
            "year": arxiv_result.year,
            "pdf_url": arxiv_result.pdf_url,
            "abs_url": arxiv_result.abs_url,
        }

    s2_dict = {}
    if s2_result:
        s2_dict = {
            "paper_id": s2_result.paper_id,
            "title": s2_result.title,
            "authors": s2_result.authors,
            "year": s2_result.year,
            "venue": s2_result.venue,
            "doi": s2_result.doi,
            "arxiv_id": s2_result.arxiv_id,
            "pdf_url": s2_result.pdf_url,
            "paper_url": s2_result.paper_url,
            "citation_count": s2_result.citation_count,
        }

    if layer1_decision is not None:
        verdict, confidence, reason = layer1_decision
        if verbose:
            print(f"  [{key}] Layer 2 verdict: {verdict} ({confidence}%) — {reason[:80]}")
        return VerifyResult(
            key=key, type=entry["type"], description=description,
            verdict=verdict, confidence=confidence, reason=reason,
            tool_calls=0, prompt_variant="deterministic",
            layer="deterministic",
            api_calls=_api_calls,
            _search_results=[], _s2=s2_dict, _arxiv=arxiv_dict,
        )

    # ── Layer 3: LLM ReAct agent ──────────────────────────────────────────
    if verbose:
        print(f"  [{key}] Layer 2 inconclusive → LLM agent")

    # Build context summary from deterministic results
    context_lines = []
    if arxiv_result:
        context_lines.append(
            f"[arXiv pre-fetch: {arxiv_result.arxiv_id}]\n"
            f"  Title: {arxiv_result.title}\n"
            f"  Authors: {', '.join(arxiv_result.authors)}\n"
            f"  Year: {arxiv_result.year}"
        )
    if s2_result:
        context_lines.append(
            f"[S2 pre-fetch]\n"
            f"  Title: {s2_result.title}\n"
            f"  Authors: {', '.join(s2_result.authors[:5])}\n"
            f"  Year: {s2_result.year}\n"
            f"  Venue: {s2_result.venue}\n"
            f"  Citations: {s2_result.citation_count}"
        )

    def _make_tavily_tool():
        @tool
        def search_tavily_tool(query: str) -> str:
            """Search the web via Tavily to verify whether an academic paper exists.
            Returns real URLs and snippets from arxiv.org and semanticscholar.org."""
            _api_calls["tavily"] += 1
            return _tavily_search_sync(query, tavily_api_key)
        return search_tavily_tool

    def _make_tavily_extract_tool():
        @tool
        def extract_page_tool(url: str) -> str:
            """Extract full text content from a URL (arXiv HTML page, DOI page, etc).
            Use arxiv.org/html/<id> for arXiv papers to get abstract + full text.
            Returns up to 3000 chars of content — useful for enriching paper cards
            with abstract, methods, and results."""
            _api_calls["tavily_extract"] += 1
            try:
                from tavily import TavilyClient
                client = TavilyClient(api_key=tavily_api_key)
                r = client.extract(urls=[url])
                results = r.get("results") or []
                failed = r.get("failed_results") or []
                if failed and not results:
                    return f"extract_page: failed to fetch {url}"
                if not results:
                    return "extract_page: no content returned."
                text = results[0].get("raw_content", "")
                # Return first 3000 chars — enough for abstract + intro
                return f"Extracted from {url} ({len(text)} chars total):\n\n{text[:3000]}"
            except Exception as e:
                return f"extract_page: error — {e}"
        return extract_page_tool

    def _make_s2_tool():
        @tool
        def search_s2_tool(title: str, authors: str = "", year: str = "") -> str:
            """Search Semantic Scholar academic database for a paper."""
            _api_calls["s2_tool"] += 1
            return _s2_search_sync(title, authors, year)
        return search_s2_tool

    def _make_arxiv_title_tool():
        @tool
        def search_arxiv_title_tool(title: str) -> str:
            """Search arXiv by paper title (no ID required).
            Returns up to 3 matches with arxiv_id, authors, year, and abstract snippet.
            Useful when the bib entry has no arXiv ID but the paper may be on arXiv."""
            _api_calls["arxiv_title"] += 1
            hits = search_arxiv_by_title_sync(title, max_results=3)
            if not hits:
                return "arXiv title search: no results found."
            lines = ["arXiv title search results:"]
            for i, h in enumerate(hits, 1):
                lines.append(
                    f"  [{i}] {h.arxiv_id} | {h.year} | {h.title}\n"
                    f"       authors: {', '.join(h.authors[:4])}\n"
                    f"       abstract: {h.abstract[:200]}\n"
                    f"       url: {h.abs_url}"
                )
            return "\n".join(lines)
        return search_arxiv_title_tool

    def _make_crossref_tool():
        @tool
        def search_crossref_tool(title: str, authors: str = "") -> str:
            """Search CrossRef DOI database for a paper or book.
            Returns DOI, publisher, venue (journal/book), year, citation count.
            Best for journal articles, books, book chapters — especially older works without arXiv."""
            _api_calls["crossref"] += 1
            hits = search_crossref_sync(title, authors, max_results=3)
            if not hits:
                return "CrossRef: no results found."
            lines = ["CrossRef results:"]
            for i, h in enumerate(hits, 1):
                lines.append(
                    f"  [{i}] DOI: {h.doi}\n"
                    f"       title: {h.title[:80]}\n"
                    f"       authors: {', '.join(h.authors[:4])}\n"
                    f"       year: {h.year} | type: {h.pub_type} | citations: {h.citation_count}\n"
                    f"       venue: {h.venue[:60]}\n"
                    f"       url: {h.url}"
                )
            return "\n".join(lines)
        return search_crossref_tool

    def _make_openalex_tool():
        @tool
        def search_openalex_tool(title: str, authors: str = "") -> str:
            """Search OpenAlex (250M+ works) for a paper.
            Returns citation count, venue, open access status, and topic concepts.
            Especially useful for psychology/cognitive science papers and for
            enriching paper cards with subject area tags."""
            _api_calls["openalex"] += 1
            hits = search_openalex_sync(title, authors, max_results=3)
            if not hits:
                return "OpenAlex: no results found."
            lines = ["OpenAlex results:"]
            for i, h in enumerate(hits, 1):
                lines.append(
                    f"  [{i}] {h.openalex_id} | {h.year} | citations={h.citation_count}\n"
                    f"       title: {h.title[:80]}\n"
                    f"       authors: {', '.join(h.authors[:4])}\n"
                    f"       venue: {h.venue[:60]} | type: {h.pub_type} | OA: {h.is_open_access}\n"
                    f"       doi: {h.doi or 'n/a'}\n"
                    f"       concepts: {', '.join(h.concepts)}\n"
                    f"       url: {h.url}"
                )
            return "\n".join(lines)
        return search_openalex_tool

    tools = [
        _make_tavily_tool(),
        _make_tavily_extract_tool(),
        _make_s2_tool(),
        _make_arxiv_title_tool(),
        _make_crossref_tool(),
        _make_openalex_tool(),
    ]

    system = system_prompt or (
        "You are a critical academic research verifier. "
        "Verify if a bibliography entry is REAL, FAKE, or UNCERTAIN.\n"
        "Use search_tavily_tool, extract_page_tool, search_s2_tool, search_arxiv_title_tool, search_crossref_tool, and search_openalex_tool to search.\n"
        "For arXiv papers: use extract_page_tool with url=https://arxiv.org/html/<id> to get full abstract and text.\n"
        "End your response with:\n"
        "```json\n{\"verdict\": \"REAL|FAKE|UNCERTAIN\", \"confidence\": 0-100, \"reason\": \"...\"}\n```"
    )

    graph = create_react_agent(openrouter_client, tools, prompt=system)

    user_content = f"Verify this bibliography entry:\n\n{description}"
    if context_lines:
        user_content += "\n\nDeterministic pre-fetch results (use these, don't re-search what's already known):\n"
        user_content += "\n\n".join(context_lines)
    else:
        user_content += "\n\n(No pre-fetch results — use both search tools.)"
    if extra_hint:
        user_content += f"\n\nAdditional focus: {extra_hint}"

    _api_calls["llm"] = 1
    async with semaphore:
        result = await graph.ainvoke({"messages": [HumanMessage(content=user_content)]})

    final_text = ""
    tool_call_count = 0
    search_results = []

    for msg in result.get("messages", []):
        if isinstance(msg, AIMessage):
            if msg.content:
                final_text = msg.content
            if msg.tool_calls:
                tool_call_count += len(msg.tool_calls)
        elif isinstance(msg, ToolMessage):
            search_results.append(msg.content)

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

    return VerifyResult(
        key=key, type=entry["type"], description=description,
        verdict=verdict, confidence=confidence, reason=reason,
        tool_calls=tool_call_count,
        prompt_variant=system_prompt[:80] + "..." if len(system_prompt) > 80 else system_prompt,
        layer="llm",
        api_calls=_api_calls,
        _search_results=search_results, _s2=s2_dict, _arxiv=arxiv_dict,
    )
