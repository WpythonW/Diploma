"""
Tests for check-citations tools — 19 tests, ZERO LLM calls.

Focus: pipeline integrity, data structures, formats, edge cases.
All external services (OpenRouter, Perplexity, Semantic Scholar) are mocked.
"""

import hashlib
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── Path setup ──────────────────────────────────────────────────────────────
TOOLS_DIR = Path(__file__).parent.parent
SKILL_DIR = TOOLS_DIR.parent  # …/check-citations

import sys
sys.path.insert(0, str(TOOLS_DIR))


# ════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_bib_content():
    return r"""@article{evans2003in,
  author  = {Evans, J. St. B. T.},
  title   = {In two minds: dual-process accounts of reasoning},
  journal = {Trends in Cognitive Sciences},
  year    = {2003},
  volume  = {7},
}

@misc{bommasani2021opportunities,
  author = {Bommasani, R. and Hudson, D. A. and others},
  title  = {On the opportunities and risks of foundation models},
  year   = {2021},
  url    = {https://arxiv.org/abs/2108.07258},
}

@article{oaksford1994rational,
  author  = {Oaksford, M. and Chater, N.},
  title   = {A rational analysis of the selection task as optimal data selection},
  journal = {Psychological Review},
  year    = {1994},
  volume  = {101},
}
"""


@pytest.fixture
def sample_bib_file(sample_bib_content, tmp_path):
    f = tmp_path / "bibliography.bib"
    f.write_text(sample_bib_content, encoding="utf-8")
    return str(f)


@pytest.fixture
def sample_entry():
    return {
        "key": "evans2003in",
        "type": "article",
        "fields": {
            "author": "Evans, J. St. B. T.",
            "title": "In two minds: dual-process accounts of reasoning",
            "journal": "Trends in Cognitive Sciences",
            "year": "2003",
            "volume": "7",
        },
    }


@pytest.fixture
def real_result(sample_entry):
    return {
        "key": "evans2003in",
        "type": "article",
        "description": "Authors: Evans, J. St. B. T.\nTitle: In two minds...",
        "verdict": "REAL",
        "confidence": 100,
        "reason": "Confirmed by Semantic Scholar and Perplexity.",
        "tool_calls": 2,
        "prompt_variant": "You are a critical academic research verifier...",
        "_search_results": ["Perplexity result...", "S2 result..."],
        "_s2": {
            "paper_id": "abc123",
            "title": "In two minds: dual-process accounts of reasoning",
            "authors": ["Evans JStBT"],
            "year": 2003,
            "venue": "Trends in Cognitive Sciences",
            "doi": "10.1016/S1364-6613(03)00001",
            "arxiv_id": None,
            "pdf_url": "https://example.com/paper.pdf",
            "paper_url": "https://www.semanticscholar.org/paper/abc123",
            "citation_count": 1500,
        },
    }


@pytest.fixture
def fake_result():
    return {
        "key": "fake2024paper",
        "type": "misc",
        "description": "Authors: Fake, A.\nTitle: This paper does not exist",
        "verdict": "FAKE",
        "confidence": 98,
        "reason": "Paper not found in any database.",
        "tool_calls": 4,
        "prompt_variant": "default",
        "_search_results": [],
        "_s2": {},
    }


@pytest.fixture
def uncertain_result():
    return {
        "key": "unsure2024paper",
        "type": "article",
        "description": "Authors: Unsure, B.",
        "verdict": "UNCERTAIN",
        "confidence": 45,
        "reason": "Conflicting results from different sources.",
        "tool_calls": 5,
        "prompt_variant": "default",
        "_search_results": ["Perplexity found something...", "S2 returned nothing"],
        "_s2": {},
    }


@pytest.fixture
def card_body_text():
    return (
        "GOAL: Investigate dual-process reasoning in cognitive science.\n"
        "GAP: Prior work focused on single-process models.\n"
        "METHOD: Literature review and theoretical analysis.\n"
        "DATASETS: Not applicable\n"
        "METRICS: Not applicable\n"
        "RESULTS: Dual-process framework successfully explains reasoning biases.\n"
        "LIMITATIONS: Theoretical, no empirical validation.\n"
        "SOURCE_USED: semantic_scholar"
    )


@pytest.fixture
def sample_results_list(real_result, fake_result):
    return [
        {k: v for k, v in real_result.items() if not k.startswith("_")},
        {k: v for k, v in fake_result.items() if not k.startswith("_")},
    ]


# ════════════════════════════════════════════════════════════════════════════
# IMPORTS (after fixtures so env is patched everywhere)
# ════════════════════════════════════════════════════════════════════════════

with patch.dict("os.environ", {
    "OPENROUTER_API_KEY": "test-key",
    "PERPLEXITY_API_KEY": "test-key",
}, clear=False):
    from parser import parse_bib, entry_to_description
    from cache import (
        cache_get, cache_set, cache_invalidate,
        card_path, card_exists_and_verified, card_invalidate,
    )
    from card_builder import build_card
    from semantic_scholar import _title_similarity, SemanticScholarResult
    from log_io import log_in, log_out, _entry
    from generate_summary_table import short_authors, generate_table
    # _s2_to_dict was originally in check_papers.py; now in agent.py
    import check_papers
    parse_hints = check_papers.parse_hints
    _s2_to_dict = check_papers._s2_to_dict


# ════════════════════════════════════════════════════════════════════════════
# 1. BIB PARSING  (5 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestParseBib:
    def test_returns_list_of_dicts(self, sample_bib_file):
        entries = parse_bib(sample_bib_file)
        assert isinstance(entries, list)
        assert all(isinstance(e, dict) for e in entries)

    def test_correct_entry_count(self, sample_bib_file):
        assert len(parse_bib(sample_bib_file)) == 3

    def test_all_keys_present(self, sample_bib_file):
        keys = {e["key"] for e in parse_bib(sample_bib_file)}
        assert keys == {"evans2003in", "bommasani2021opportunities", "oaksford1994rational"}

    def test_entry_has_type_and_fields(self, sample_bib_file):
        evans = next(e for e in parse_bib(sample_bib_file) if e["key"] == "evans2003in")
        assert evans["type"] == "article"
        assert "title" in evans["fields"]
        assert "author" in evans["fields"]
        assert "year" in evans["fields"]

    def test_misc_type_parsed(self, sample_bib_file):
        bommasani = next(e for e in parse_bib(sample_bib_file) if e["key"] == "bommasani2021opportunities")
        assert bommasani["type"] == "misc"


# ════════════════════════════════════════════════════════════════════════════
# 2. ENTRY TO DESCRIPTION  (3 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestEntryToDescription:
    def test_contains_key_fields(self, sample_entry):
        desc = entry_to_description(sample_entry)
        assert "Authors:" in desc
        assert "Evans" in desc
        assert "Year: 2003" in desc

    def test_contains_journal_when_present(self, sample_entry):
        desc = entry_to_description(sample_entry)
        assert "Journal: Trends in Cognitive Sciences" in desc

    def test_omits_missing_fields(self):
        entry = {"key": "x", "type": "misc", "fields": {"title": "Test", "year": "2024"}}
        desc = entry_to_description(entry)
        assert "Authors:" not in desc
        assert "Title: Test" in desc
        assert "Journal:" not in desc


# ════════════════════════════════════════════════════════════════════════════
# 3. CACHE OPERATIONS  (3 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestCache:
    def test_set_and_get(self, sample_entry, tmp_path, monkeypatch):
        monkeypatch.setattr("cache.CACHE_DIR", tmp_path / ".cache")
        cache_set(sample_entry["key"], {"verdict": "REAL", "confidence": 95})
        result = cache_get(sample_entry["key"])
        assert result["verdict"] == "REAL"
        assert result["confidence"] == 95

    def test_get_missing_returns_none(self, sample_entry, tmp_path, monkeypatch):
        monkeypatch.setattr("cache.CACHE_DIR", tmp_path / ".cache")
        assert cache_get("nonexistent") is None

    def test_invalidate_removes(self, sample_entry, tmp_path, monkeypatch):
        monkeypatch.setattr("cache.CACHE_DIR", tmp_path / ".cache")
        cache_set(sample_entry["key"], {"verdict": "REAL"})
        cache_invalidate(sample_entry["key"])
        assert cache_get(sample_entry["key"]) is None


# ════════════════════════════════════════════════════════════════════════════
# 4. CARD OPERATIONS  (3 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestCardOps:
    def test_card_path_correct_name(self, sample_entry, tmp_path, monkeypatch):
        monkeypatch.setattr("cache.CARDS_DIR", tmp_path / "cards")
        p = card_path(sample_entry["key"])
        assert p.name == "evans2003in.md"

    def test_exists_and_verified_true(self, sample_entry, tmp_path, monkeypatch):
        monkeypatch.setattr("cache.CARDS_DIR", tmp_path / "cards")
        p = card_path(sample_entry["key"])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("---\nverified: true\n---\n", encoding="utf-8")
        assert card_exists_and_verified(sample_entry["key"]) is True

    def test_exists_and_verified_false_when_unverified(self, sample_entry, tmp_path, monkeypatch):
        monkeypatch.setattr("cache.CARDS_DIR", tmp_path / "cards")
        p = card_path(sample_entry["key"])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("---\nverified: false\n---\n", encoding="utf-8")
        assert card_exists_and_verified(sample_entry["key"]) is False


# ════════════════════════════════════════════════════════════════════════════
# 5. CARD BUILDING  (3 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestBuildCard:
    def test_real_card_has_verified_true(self, sample_entry, real_result, card_body_text):
        card = build_card(sample_entry, real_result, card_body_text)
        assert "key: evans2003in" in card
        assert "verified: true" in card
        assert "confidence: 100" in card

    def test_fake_card_has_verified_false(self, sample_entry, fake_result, card_body_text):
        fake_entry = {**sample_entry, "key": "fake2024paper"}
        card = build_card(fake_entry, fake_result, card_body_text)
        assert "verified: false" in card
        assert "FAKE" in card

    def test_card_has_all_sections(self, sample_entry, real_result, card_body_text):
        card = build_card(sample_entry, real_result, card_body_text)
        for section in ["Goal", "Gap Addressed", "Method", "Datasets and Metrics", "Results", "Verification Verdict"]:
            assert f"## {section}" in card


# ════════════════════════════════════════════════════════════════════════════
# 6. SEMANTIC SCHOLAR HELPERS  (3 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestS2Helpers:
    def test_s2_to_dict_none(self):
        assert _s2_to_dict(None) == {}

    def test_title_similarity_exact(self):
        assert _title_similarity("Alpha Beta Gamma", "Alpha Beta Gamma") == 1.0

    def test_title_similarity_zero(self):
        assert _title_similarity("alpha beta", "gamma delta") == 0.0


# ════════════════════════════════════════════════════════════════════════════
# 7. HINTS PARSING  (2 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestParseHints:
    def test_basic(self):
        result = parse_hints(["key1:check venue", "key2:look for DOI"])
        assert result == {"key1": "check venue", "key2": "look for DOI"}

    def test_empty(self):
        assert parse_hints(None) == {}
        assert parse_hints([]) == {}


# ════════════════════════════════════════════════════════════════════════════
# 8. SUMMARY TABLE  (3 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestSummaryTable:
    def test_header_present(self, sample_results_list, tmp_path, monkeypatch):
        monkeypatch.setattr("generate_summary_table.CARDS_DIR", tmp_path / "cards")
        table = generate_table(sample_results_list)
        assert "| Key |" in table

    def test_all_entries_in_table(self, sample_results_list, tmp_path, monkeypatch):
        monkeypatch.setattr("generate_summary_table.CARDS_DIR", tmp_path / "cards")
        table = generate_table(sample_results_list)
        assert "evans2003in" in table
        assert "fake2024paper" in table

    def test_fake_entries_sorted_before_real(self, sample_results_list, tmp_path, monkeypatch):
        monkeypatch.setattr("generate_summary_table.CARDS_DIR", tmp_path / "cards")
        table = generate_table(sample_results_list)
        assert table.index("fake2024paper") < table.index("evans2003in")


# ════════════════════════════════════════════════════════════════════════════
# 9. LOG I/O  (2 tests)
# ════════════════════════════════════════════════════════════════════════════

class TestLogIO:
    def test_entry_structure(self):
        entry = _entry("OUT", "test", "hello")
        assert entry["dir"] == "OUT"
        assert entry["label"] == "test"
        assert entry["chars"] == 5
        assert "ts" in entry

    def test_log_writes_file(self, tmp_path, monkeypatch):
        log_file = tmp_path / "test_log.jsonl"
        monkeypatch.setattr("log_io.LOG_FILE", log_file)
        log_out("label", "hello world")
        log_in("label", "response")
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["dir"] == "OUT"
        assert json.loads(lines[1])["dir"] == "IN"
