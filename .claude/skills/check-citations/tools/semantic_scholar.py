"""
semantic_scholar.py — thin async wrapper around the Semantic Scholar Graph API.

Public API (no key required, rate-limited to 1 req/s).
With S2_API_KEY in env: 10 req/s.

Exports:
    search_semantic_scholar(title, authors, year) -> SemanticScholarResult | None
"""

import os
import asyncio
import httpx
from dataclasses import dataclass, field

S2_BASE = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "title,authors,year,venue,externalIds,openAccessPdf,url,publicationTypes,citationCount"

# Optional API key — set S2_API_KEY in .env for higher rate limits
_API_KEY = os.environ.get("S2_API_KEY", "")
_HEADERS = {"x-api-key": _API_KEY} if _API_KEY else {}

# Semaphore: 1 req/s without key, 5/s with key
_SEM = asyncio.Semaphore(1 if not _API_KEY else 5)
_DELAY = 2.0 if not _API_KEY else 0.2   # seconds between requests


@dataclass
class SemanticScholarResult:
    paper_id: str
    title: str
    authors: list[str]
    year: int | None
    venue: str
    doi: str | None
    arxiv_id: str | None
    pdf_url: str | None
    paper_url: str          # canonical S2 URL
    citation_count: int
    found: bool = True
    raw: dict = field(default_factory=dict, repr=False)


async def _get(client: httpx.AsyncClient, path: str, params: dict, retries: int = 3) -> dict | None:
    for attempt in range(retries):
        async with _SEM:
            try:
                r = await client.get(f"{S2_BASE}{path}", params=params, headers=_HEADERS, timeout=15)
                await asyncio.sleep(_DELAY)
                if r.status_code == 429:
                    wait = 10 * (attempt + 1)
                    await asyncio.sleep(wait)
                    continue
                r.raise_for_status()
                return r.json()
            except httpx.HTTPStatusError:
                return None
            except Exception:
                return None
    return None


def _parse_hit(hit: dict) -> SemanticScholarResult:
    ext = hit.get("externalIds") or {}
    oap = hit.get("openAccessPdf") or {}
    authors = [a.get("name", "") for a in (hit.get("authors") or [])]
    return SemanticScholarResult(
        paper_id=hit.get("paperId", ""),
        title=hit.get("title", ""),
        authors=authors,
        year=hit.get("year"),
        venue=hit.get("venue") or "",
        doi=ext.get("DOI"),
        arxiv_id=ext.get("ArXiv"),
        pdf_url=oap.get("url"),
        paper_url=f"https://www.semanticscholar.org/paper/{hit.get('paperId', '')}",
        citation_count=hit.get("citationCount") or 0,
        raw=hit,
    )


def _title_similarity(a: str, b: str) -> float:
    """Simple token-overlap similarity in [0, 1]."""
    ta = set(a.lower().split())
    tb = set(b.lower().split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta), len(tb))


async def search_semantic_scholar(
    title: str,
    authors: str = "",
    year: str | int | None = None,
    verbose: bool = False,
) -> SemanticScholarResult | None:
    """
    Search Semantic Scholar for a paper.

    Strategy:
    1. Title search → pick best hit by title similarity + year match.
    2. If no good match (sim < 0.6), try query with author surname appended.
    3. Return None if nothing found.
    """
    if not title:
        return None

    first_author_surname = ""
    if authors:
        # "Kahneman, D. and Tversky, A." → "Kahneman"
        first_author_surname = authors.split(",")[0].split(" and ")[0].strip().split()[-1]

    async with httpx.AsyncClient() as client:
        # ── Pass 1: title only ────────────────────────────────────────────────
        data = await _get(client, "/paper/search", {
            "query": title,
            "fields": S2_FIELDS,
            "limit": 5,
        })
        best = _pick_best(data, title, year, verbose)

        # ── Pass 2: title + author surname ────────────────────────────────────
        if best is None and first_author_surname:
            query2 = f"{title} {first_author_surname}"
            if verbose:
                print(f"    [s2 pass2] {query2[:80]}")
            data2 = await _get(client, "/paper/search", {
                "query": query2,
                "fields": S2_FIELDS,
                "limit": 5,
            })
            best = _pick_best(data2, title, year, verbose)

    if verbose:
        if best:
            print(f"    [s2 found] {best.title} ({best.year}) — cit={best.citation_count}")
        else:
            print(f"    [s2] not found: {title[:60]}")
    return best


def _pick_best(
    data: dict | None,
    title: str,
    year: str | int | None,
    verbose: bool,
) -> SemanticScholarResult | None:
    if not data:
        return None
    hits = data.get("data") or []
    if not hits:
        return None

    scored = []
    for hit in hits:
        sim = _title_similarity(title, hit.get("title", ""))
        hit_year = hit.get("year")
        year_ok = (str(hit_year) == str(year)) if (year and hit_year) else True
        score = sim + (0.2 if year_ok else 0)
        scored.append((score, hit))

    scored.sort(key=lambda x: -x[0])
    best_score, best_hit = scored[0]

    if best_score < 0.45:          # too dissimilar — don't trust
        return None
    return _parse_hit(best_hit)
