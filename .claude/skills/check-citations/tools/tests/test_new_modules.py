"""
Tests for author_normalize.py and arxiv_lookup.py.
ZERO real network calls — arXiv API is mocked.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import sys
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from author_normalize import (
    Author,
    MatchResult,
    _ascii,
    _clean,
    parse_authors,
    authors_match,
)
from arxiv_lookup import (
    ArxivResult,
    extract_arxiv_id,
    lookup_arxiv,
    _parse_entry,
)
import xml.etree.ElementTree as ET


# ════════════════════════════════════════════════════════════════════════════
# 1. UNICODE / ASCII normalization  (2 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestUnicodeNorm:
    def test_ascii_strips_diacritics(self):
        assert _ascii("Ångström") == "Angstrom"
        assert _ascii("José") == "Jose"

    def test_clean_lowercases_and_strips(self):
        result = _clean("Müller-Koch, F.")
        assert result == "muller-koch f"


# ════════════════════════════════════════════════════════════════════════════
# 2. Author parsing — BibTeX format  (5 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestParseAuthorsBibtex:
    def test_single_bibtex_author(self):
        authors = parse_authors("Bazigaran, A.")
        assert len(authors) == 1
        assert authors[0].last == "bazigaran"
        assert authors[0].first_initial == "a"

    def test_two_bibtex_authors(self):
        authors = parse_authors("Bazigaran, A. and Sohn, H.")
        assert len(authors) == 2
        assert authors[0].last == "bazigaran"
        assert authors[1].last == "sohn"
        assert authors[1].first_initial == "h"

    def test_others_ignored(self):
        authors = parse_authors("Bommasani, R. and Hudson, D. A. and others")
        assert len(authors) == 2
        assert authors[0].last == "bommasani"

    def test_empty_string(self):
        assert parse_authors("") == []

    def test_multiple_initials(self):
        # "Evans, J. St. B. T." — first_initial should be "j"
        authors = parse_authors("Evans, J. St. B. T.")
        assert len(authors) == 1
        assert authors[0].last == "evans"
        assert authors[0].first_initial == "j"


# ════════════════════════════════════════════════════════════════════════════
# 3. Author parsing — natural format  (4 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestParseAuthorsNatural:
    def test_first_last(self):
        authors = parse_authors("Arghavan Bazigaran")
        assert len(authors) == 1
        assert authors[0].last == "bazigaran"
        assert authors[0].first_initial == "a"

    def test_initial_last(self):
        authors = parse_authors("A. Bazigaran")
        assert len(authors) == 1
        assert authors[0].last == "bazigaran"
        assert authors[0].first_initial == "a"

    def test_two_natural_authors(self):
        authors = parse_authors("Arghavan Bazigaran and Hansem Sohn")
        assert len(authors) == 2
        assert authors[1].last == "sohn"
        assert authors[1].first_initial == "h"

    def test_unicode_name(self):
        authors = parse_authors("José García")
        assert authors[0].last == "garcia"
        assert authors[0].first_initial == "j"


# ════════════════════════════════════════════════════════════════════════════
# 4. Author matching  (7 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestAuthorsMatch:
    def test_exact_match_bibtex_vs_natural(self):
        """Core case: bazigaran2025concept false FAKE."""
        result = authors_match(
            "Bazigaran, A. and Sohn, H.",
            ["Arghavan Bazigaran", "Hansem Sohn"],
        )
        assert result.verdict == "MATCH"
        assert result.score == 1.0

    def test_match_with_initials_only(self):
        result = authors_match(
            "Kahneman, D.",
            ["Daniel Kahneman"],
        )
        assert result.verdict == "MATCH"

    def test_mismatch_different_last_names(self):
        result = authors_match(
            "Smith, J. and Jones, A.",
            ["Alice Brown", "Carol White"],
        )
        assert result.verdict == "MISMATCH"
        assert result.score == 0.0

    def test_partial_match_with_others(self):
        """BibTeX has 2 real authors + others; found list has those 2."""
        result = authors_match(
            "Bommasani, R. and Hudson, D. A.",
            ["Rishi Bommasani", "Drew Hudson", "Percy Liang"],
        )
        assert result.verdict == "MATCH"

    def test_unknown_when_no_bib_authors(self):
        result = authors_match("", ["Alice Brown"])
        assert result.verdict == "UNKNOWN"

    def test_unknown_when_no_found_authors(self):
        result = authors_match("Smith, J.", [])
        assert result.verdict == "UNKNOWN"

    def test_last_name_only_match(self):
        """If bib has initial and found has full first name — still matches."""
        result = authors_match("Sohn, H.", ["Hansem Sohn"])
        assert result.verdict == "MATCH"


# ════════════════════════════════════════════════════════════════════════════
# 5. arXiv ID extraction  (6 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestExtractArxivId:
    def test_bare_id(self):
        assert extract_arxiv_id("2512.20162") == "2512.20162"

    def test_url(self):
        assert extract_arxiv_id("https://arxiv.org/abs/2512.20162") == "2512.20162"

    def test_url_with_prefix(self):
        assert extract_arxiv_id("URL: https://arxiv.org/abs/2512.20162") == "2512.20162"

    def test_arxiv_colon(self):
        assert extract_arxiv_id("arxiv:2512.20162v2") == "2512.20162v2"

    def test_no_id_returns_none(self):
        assert extract_arxiv_id("https://example.com/paper") is None

    def test_empty_returns_none(self):
        assert extract_arxiv_id("") is None


# ════════════════════════════════════════════════════════════════════════════
# 6. arXiv XML parsing  (3 tests)
# ════════════════════════════════════════════════════════════════════════════

SAMPLE_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2512.20162v1</id>
    <title>Concept Generalization in Humans and Large Language Models</title>
    <author><name>Arghavan Bazigaran</name></author>
    <author><name>Hansem Sohn</name></author>
    <published>2025-01-15T00:00:00Z</published>
    <summary>Abstract text here.</summary>
    <link rel="alternate" href="https://arxiv.org/abs/2512.20162v1"/>
    <link title="pdf" href="https://arxiv.org/pdf/2512.20162v1"/>
  </entry>
</feed>"""


class TestParseArxivXml:
    def _entry(self):
        root = ET.fromstring(SAMPLE_ATOM)
        ns = "http://www.w3.org/2005/Atom"
        return root.find(f"{{{ns}}}entry")

    def test_title_parsed(self):
        result = _parse_entry(self._entry())
        assert result is not None
        assert "Concept Generalization" in result.title

    def test_authors_parsed(self):
        result = _parse_entry(self._entry())
        assert result is not None
        assert "Arghavan Bazigaran" in result.authors
        assert "Hansem Sohn" in result.authors

    def test_year_parsed(self):
        result = _parse_entry(self._entry())
        assert result is not None
        assert result.year == 2025


# ════════════════════════════════════════════════════════════════════════════
# 7. arXiv API lookup — mocked  (4 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestLookupArxiv:
    @pytest.mark.asyncio
    async def test_lookup_success(self):
        """Happy path: valid ID returns ArxivResult with correct fields."""
        mock_response = MagicMock()
        mock_response.text = SAMPLE_ATOM
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            result = await lookup_arxiv("2512.20162")

        assert result is not None
        assert result.arxiv_id == "2512.20162v1"
        assert result.year == 2025
        assert "Arghavan Bazigaran" in result.authors

    @pytest.mark.asyncio
    async def test_lookup_url_input(self):
        """Input is a full URL — ID should be extracted."""
        mock_response = MagicMock()
        mock_response.text = SAMPLE_ATOM
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            result = await lookup_arxiv("https://arxiv.org/abs/2512.20162")

        assert result is not None
        assert "Bazigaran" in result.authors[0]

    @pytest.mark.asyncio
    async def test_lookup_invalid_id_returns_none(self):
        """No arXiv ID in input → None immediately."""
        result = await lookup_arxiv("https://example.com/noid")
        assert result is None

    @pytest.mark.asyncio
    async def test_lookup_network_error_returns_none(self):
        """Network failure → None (no exception raised)."""
        with patch("httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("timeout")
            )
            result = await lookup_arxiv("2512.20162")
        assert result is None
