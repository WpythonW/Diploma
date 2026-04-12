"""
author_normalize.py — Canonical author name normalization and matching.

Handles:
  - BibTeX format: "Bazigaran, A. and Sohn, H."  →  [("bazigaran", "a")]
  - Natural format: "Arghavan Bazigaran"           →  [("bazigaran", "arghavan")]
  - Initials: "J. St. B. T. Evans" or "Evans, J."
  - Unicode/transliteration: é → e
  - Partial match: last name + initial match counts as MATCH

Public API:
    parse_authors(raw: str) -> list[Author]
    authors_match(bib_authors: str, found_authors: list[str]) -> MatchResult
"""

from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass
from typing import Literal


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class Author:
    last: str           # normalized last name (lowercased, ascii)
    first_initial: str  # first initial of first name, or "" if unknown

    def __str__(self):
        if self.first_initial:
            return f"{self.last.title()}, {self.first_initial.upper()}."
        return self.last.title()


@dataclass
class MatchResult:
    matched: int        # number of bib authors matched in found list
    total_bib: int      # total bib authors
    score: float        # matched / total_bib  in [0, 1]
    verdict: Literal["MATCH", "PARTIAL", "MISMATCH", "UNKNOWN"]

    @property
    def is_ok(self) -> bool:
        return self.verdict in ("MATCH", "PARTIAL")


# ── Unicode normalization ────────────────────────────────────────────────────

def _ascii(s: str) -> str:
    """Normalize unicode to closest ASCII (é → e, ü → u, etc.)."""
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()


def _clean(s: str) -> str:
    """Lowercase, ascii-normalize, strip punctuation noise."""
    s = _ascii(s).lower()
    s = re.sub(r"[^a-z\s\-]", "", s)
    return s.strip()


# ── Parsing ──────────────────────────────────────────────────────────────────

def _parse_one_bibtex(token: str) -> Author | None:
    """
    Parse a single BibTeX author token.

    BibTeX canonical: "Last, First" or "Last, F." or "Last, F. M."
    Natural: "First Last" or "F. Last"
    """
    token = token.strip()
    if not token or token.lower() in ("others", "et al", "et al."):
        return None

    if "," in token:
        # "Last, First" or "Last, F."
        parts = token.split(",", 1)
        last = _clean(parts[0])
        first_part = _clean(parts[1]).strip()
        # first initial: first non-space char
        first_initial = first_part[0] if first_part else ""
    else:
        # Natural order: "First Last" or "F. Last"
        words = _clean(token).split()
        if not words:
            return None
        if len(words) == 1:
            return Author(last=words[0], first_initial="")
        # Heuristic: if first word is a single letter (initial), treat as "Initial Last"
        if len(words[0]) == 1:
            last = words[-1]
            first_initial = words[0]
        else:
            last = words[-1]
            first_initial = words[0][0]

    return Author(last=last, first_initial=first_initial)


def parse_authors(raw: str) -> list[Author]:
    """
    Parse any author string into list[Author].

    Handles both BibTeX ("Last, F. and Last2, F2.") and
    natural ("First Last, First2 Last2") formats.
    """
    if not raw or not raw.strip():
        return []

    # Split on " and " (BibTeX standard separator)
    tokens = re.split(r"\s+and\s+", raw, flags=re.IGNORECASE)

    # Also try splitting on "; " or just "," if no " and " found and only one token
    if len(tokens) == 1 and ";" in raw:
        tokens = [t.strip() for t in raw.split(";")]

    authors = []
    for tok in tokens:
        a = _parse_one_bibtex(tok.strip())
        if a and a.last:
            authors.append(a)
    return authors


# ── Matching ─────────────────────────────────────────────────────────────────

def _authors_match_one(bib: Author, candidates: list[Author]) -> bool:
    """
    Check if `bib` author matches any candidate.

    Rules:
    - Last name must match exactly (after normalization).
    - If both have first_initial → initials must match.
    - If one side has no first_initial → last-name-only match is OK.
    """
    for cand in candidates:
        if bib.last != cand.last:
            # Try substring: "sohn" in "sohnhansem" → no, but exact only
            continue
        # Last names match
        if bib.first_initial and cand.first_initial:
            if bib.first_initial == cand.first_initial:
                return True
        else:
            # One side has no initial — last-name-only match
            return True
    return False


def authors_match(bib_authors_raw: str, found_authors: list[str]) -> MatchResult:
    """
    Compare bib author string with a list of found author names.

    Returns MatchResult with verdict:
      MATCH     — all bib authors matched
      PARTIAL   — ≥50% matched (e.g. "et al." case)
      MISMATCH  — <50% matched
      UNKNOWN   — couldn't parse either side
    """
    bib = parse_authors(bib_authors_raw)
    found = [a for raw in found_authors for a in [_parse_one_bibtex(raw)] if a and a.last]

    if not bib:
        return MatchResult(matched=0, total_bib=0, score=0.0, verdict="UNKNOWN")
    if not found:
        return MatchResult(matched=0, total_bib=len(bib), score=0.0, verdict="UNKNOWN")

    matched = sum(1 for b in bib if _authors_match_one(b, found))
    score = matched / len(bib)

    if score >= 1.0:
        verdict = "MATCH"
    elif score >= 0.5:
        verdict = "PARTIAL"
    else:
        verdict = "MISMATCH"

    return MatchResult(matched=matched, total_bib=len(bib), score=score, verdict=verdict)
