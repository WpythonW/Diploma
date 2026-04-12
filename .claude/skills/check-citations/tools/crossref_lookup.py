"""
crossref_lookup.py — thin wrapper around the CrossRef REST API.

Free, no API key required. Rate limit: ~50 req/s with polite pool.
Best for: journal articles, books, book chapters — anything with a DOI.

Exports:
    search_crossref(title, authors, year) -> list[CrossRefResult]
    search_crossref_sync(title, authors, year) -> list[CrossRefResult]
"""

from __future__ import annotations
import asyncio
import html
from dataclasses import dataclass, field

import httpx

_BASE = "https://api.crossref.org/works"
_HEADERS = {"User-Agent": "diploma-citation-checker/1.0 (mailto:academic@use.org)"}


@dataclass
class CrossRefResult:
    doi: str
    title: str
    authors: list[str]
    year: int | None
    pub_type: str        # "journal-article", "book", "book-chapter", etc.
    publisher: str
    venue: str           # journal or book title
    citation_count: int
    url: str


async def search_crossref(
    title: str,
    authors: str = "",
    year: str | int | None = None,
    max_results: int = 3,
) -> list[CrossRefResult]:
    """Search CrossRef by title (+ optional first author surname and year)."""
    if not title:
        return []

    params: dict = {
        "query.title": title,
        "rows": max_results,
        "select": "title,author,published,DOI,type,publisher,container-title,is-referenced-by-count",
    }
    if authors:
        first_surname = authors.split(",")[0].split(" and ")[0].strip().split()[-1]
        params["query.author"] = first_surname

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(_BASE, params=params, headers=_HEADERS, timeout=15)
            r.raise_for_status()
    except Exception:
        return []

    items = r.json().get("message", {}).get("items") or []
    results = []
    for item in items:
        raw_title = (item.get("title") or [""])[0]
        clean_title = html.unescape(raw_title)
        authors_found = [
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in (item.get("author") or [])[:6]
        ]
        pub_parts = (item.get("published") or {}).get("date-parts") or [[None]]
        item_year = pub_parts[0][0] if pub_parts[0] else None
        venue = html.unescape((item.get("container-title") or [""])[0])
        doi = item.get("DOI", "")
        results.append(CrossRefResult(
            doi=doi,
            title=clean_title,
            authors=authors_found,
            year=item_year,
            pub_type=item.get("type", ""),
            publisher=item.get("publisher", ""),
            venue=venue,
            citation_count=item.get("is-referenced-by-count", 0),
            url=f"https://doi.org/{doi}" if doi else "",
        ))
    return results


def search_crossref_sync(
    title: str,
    authors: str = "",
    year: str | int | None = None,
    max_results: int = 3,
) -> list[CrossRefResult]:
    """Synchronous wrapper for search_crossref."""
    return asyncio.run(search_crossref(title, authors, year, max_results))
