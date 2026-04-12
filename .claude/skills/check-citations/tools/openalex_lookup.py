"""
openalex_lookup.py — thin wrapper around the OpenAlex REST API.

Free, no API key required. 250M+ works. Polite pool: add email to User-Agent.
Best for: rich metadata, concepts/topics, citation counts, open access status.

Exports:
    search_openalex(title, authors, year) -> list[OpenAlexResult]
    search_openalex_sync(title, authors, year) -> list[OpenAlexResult]
"""

from __future__ import annotations
import asyncio
from dataclasses import dataclass, field

import httpx

_BASE = "https://api.openalex.org/works"
_HEADERS = {"User-Agent": "diploma-citation-checker/1.0 (mailto:academic@use.org)"}
_SELECT = (
    "id,title,authorships,publication_year,primary_location,"
    "cited_by_count,open_access,concepts,doi,type"
)


@dataclass
class OpenAlexResult:
    openalex_id: str        # e.g. "W4292157289"
    doi: str | None
    title: str
    authors: list[str]
    year: int | None
    venue: str              # journal / conference name
    pub_type: str           # "article", "book", "dataset", etc.
    citation_count: int
    is_open_access: bool
    concepts: list[str]     # top-5 topic tags
    url: str                # canonical OpenAlex URL


async def search_openalex(
    title: str,
    authors: str = "",
    year: str | int | None = None,
    max_results: int = 3,
) -> list[OpenAlexResult]:
    """Search OpenAlex by title (+ optional first author surname)."""
    if not title:
        return []

    params: dict = {
        "search": title,
        "per_page": max_results,
        "select": _SELECT,
    }

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(_BASE, params=params, headers=_HEADERS, timeout=15)
            r.raise_for_status()
    except Exception:
        return []

    items = r.json().get("results") or []
    results = []
    for item in items:
        authors_found = [
            a["author"].get("display_name", "")
            for a in (item.get("authorships") or [])[:6]
        ]
        loc = item.get("primary_location") or {}
        source = loc.get("source") or {}
        concepts = [c["display_name"] for c in (item.get("concepts") or [])[:5]]
        oa_id = item.get("id", "").replace("https://openalex.org/", "")
        raw_doi = item.get("doi") or ""
        doi = raw_doi.replace("https://doi.org/", "") if raw_doi else None
        results.append(OpenAlexResult(
            openalex_id=oa_id,
            doi=doi,
            title=item.get("title") or "",
            authors=authors_found,
            year=item.get("publication_year"),
            venue=source.get("display_name") or "",
            pub_type=item.get("type") or "",
            citation_count=item.get("cited_by_count") or 0,
            is_open_access=(item.get("open_access") or {}).get("is_oa", False),
            concepts=concepts,
            url=f"https://openalex.org/{oa_id}" if oa_id else "",
        ))
    return results


def search_openalex_sync(
    title: str,
    authors: str = "",
    year: str | int | None = None,
    max_results: int = 3,
) -> list[OpenAlexResult]:
    """Synchronous wrapper for search_openalex."""
    return asyncio.run(search_openalex(title, authors, year, max_results))
