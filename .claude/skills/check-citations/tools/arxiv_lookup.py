"""
arxiv_lookup.py — Deterministic arXiv paper lookup by arXiv ID.

Uses the arXiv API (no auth required, ~3 req/s limit).
Extracts arXiv ID from common formats:
  - "2512.20162"
  - "https://arxiv.org/abs/2512.20162"
  - "arxiv:2512.20162"
  - "URL: https://arxiv.org/abs/2512.20162"  (howpublished field)

Returns ArxivResult or None.
"""

from __future__ import annotations
import asyncio
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import httpx

ARXIV_API = "https://export.arxiv.org/api/query"
_ARXIV_ID_RE = re.compile(
    r"(?:arxiv[:\s/]+|abs/|/abs/)?(\d{4}\.\d{4,5}(?:v\d+)?)",
    re.IGNORECASE,
)
_NS = "http://www.w3.org/2005/Atom"
_USER_AGENT = "diploma-citation-checker/1.0 (academic use)"


@dataclass
class ArxivResult:
    arxiv_id: str           # clean ID, e.g. "2512.20162"
    title: str
    authors: list[str]      # natural order: "First Last"
    year: int | None        # from published date
    abstract: str
    pdf_url: str
    abs_url: str
    found: bool = True


def extract_arxiv_id(raw: str) -> str | None:
    """
    Extract a clean arXiv ID from any string.

    Examples:
        "https://arxiv.org/abs/2512.20162"  → "2512.20162"
        "arxiv:2512.20162v2"                → "2512.20162v2"
        "URL: https://arxiv.org/abs/2512.20162" → "2512.20162"
    """
    if not raw:
        return None
    m = _ARXIV_ID_RE.search(raw)
    return m.group(1) if m else None


def _parse_entry(entry: ET.Element) -> ArxivResult | None:
    """Parse a single <entry> element from arXiv Atom feed."""
    def tag(name):
        return f"{{{_NS}}}{name}"

    title_el = entry.find(tag("title"))
    title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else ""

    authors = []
    for author_el in entry.findall(tag("author")):
        name_el = author_el.find(tag("name"))
        if name_el is not None and name_el.text:
            authors.append(name_el.text.strip())

    published_el = entry.find(tag("published"))
    year = None
    if published_el is not None and published_el.text:
        m = re.match(r"(\d{4})", published_el.text)
        if m:
            year = int(m.group(1))

    abstract_el = entry.find(tag("summary"))
    abstract = abstract_el.text.strip().replace("\n", " ") if abstract_el is not None and abstract_el.text else ""

    # Find PDF and abs links
    pdf_url = ""
    abs_url = ""
    arxiv_id = ""
    for link_el in entry.findall(tag("link")):
        href = link_el.get("href", "")
        rel = link_el.get("rel", "")
        title_attr = link_el.get("title", "")
        if title_attr == "pdf":
            pdf_url = href
        elif rel == "alternate":
            abs_url = href

    # Extract ID from abs URL or id element
    id_el = entry.find(tag("id"))
    if id_el is not None and id_el.text:
        arxiv_id = extract_arxiv_id(id_el.text) or ""
    if not arxiv_id and abs_url:
        arxiv_id = extract_arxiv_id(abs_url) or ""

    if not title or not arxiv_id:
        return None

    return ArxivResult(
        arxiv_id=arxiv_id,
        title=title,
        authors=authors,
        year=year,
        abstract=abstract,
        pdf_url=pdf_url or f"https://arxiv.org/pdf/{arxiv_id}",
        abs_url=abs_url or f"https://arxiv.org/abs/{arxiv_id}",
    )


async def lookup_arxiv(arxiv_id_or_url: str) -> ArxivResult | None:
    """
    Look up an arXiv paper by ID or URL.

    Args:
        arxiv_id_or_url: raw arXiv ID ("2512.20162"), URL
                         ("https://arxiv.org/abs/2512.20162"),
                         or howpublished value ("URL: https://...")

    Returns:
        ArxivResult if found, None otherwise.
    """
    arxiv_id = extract_arxiv_id(arxiv_id_or_url)
    if not arxiv_id:
        return None

    # Strip version suffix for lookup (vN) — API handles it
    clean_id = re.sub(r"v\d+$", "", arxiv_id)

    params = {"id_list": clean_id, "max_results": "1"}
    headers = {"User-Agent": _USER_AGENT}

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(ARXIV_API, params=params, headers=headers, timeout=15)
            r.raise_for_status()
    except Exception:
        return None

    try:
        root = ET.fromstring(r.text)
    except ET.ParseError:
        return None

    ns = _NS
    entries = root.findall(f"{{{ns}}}entry")
    if not entries:
        return None

    # arXiv returns a "not found" entry with error in title if ID is invalid
    entry = entries[0]
    title_el = entry.find(f"{{{ns}}}title")
    if title_el is not None and title_el.text and "error" in title_el.text.lower():
        return None

    return _parse_entry(entry)


def lookup_arxiv_sync(arxiv_id_or_url: str) -> ArxivResult | None:
    """Synchronous wrapper for use in non-async contexts."""
    return asyncio.run(lookup_arxiv(arxiv_id_or_url))


async def search_arxiv_by_title(title: str, max_results: int = 3) -> list[ArxivResult]:
    """
    Search arXiv by paper title (no ID required).

    Uses ti: field query — more precise than full-text search.
    Returns up to max_results results sorted by relevance.
    """
    import urllib.parse
    query = urllib.parse.quote(f'ti:"{title}"')
    url = f"{ARXIV_API}?search_query={query}&max_results={max_results}"
    headers = {"User-Agent": _USER_AGENT}

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers, timeout=15)
            r.raise_for_status()
    except Exception:
        return []

    try:
        root = ET.fromstring(r.text)
    except ET.ParseError:
        return []

    results = []
    for entry in root.findall(f"{{{_NS}}}entry"):
        parsed = _parse_entry(entry)
        if parsed:
            results.append(parsed)
    return results


def search_arxiv_by_title_sync(title: str, max_results: int = 3) -> list[ArxivResult]:
    """Synchronous wrapper for search_arxiv_by_title."""
    return asyncio.run(search_arxiv_by_title(title, max_results))
