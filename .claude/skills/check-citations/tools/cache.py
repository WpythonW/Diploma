"""
cache.py — verification result caching on disk.
Extracted from check_papers.py for modularity.

Two modes:
  - Global: uses CACHE_DIR constant (for CLI, backward compatible)
  - Explicit: pass cache_dir param (for workflow, testable)
"""

import hashlib
import json
from pathlib import Path

# Global cache dir (set by check_papers.py at startup)
CACHE_DIR: Path = Path(__file__).parent / ".cache"


def _cache_path_for_dir(cache_dir: Path, key: str) -> Path:
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.json"


def _cache_path(key: str) -> Path:
    """Backward-compatible: uses global CACHE_DIR."""
    return _cache_path_for_dir(CACHE_DIR, key)


def cache_get(key: str, *, cache_dir: Path | None = None) -> dict | None:
    d = cache_dir if cache_dir is not None else CACHE_DIR
    p = _cache_path_for_dir(d, key)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def cache_set(key: str, value: dict, *, cache_dir: Path | None = None):
    d = cache_dir if cache_dir is not None else CACHE_DIR
    _cache_path_for_dir(d, key).write_text(
        json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def cache_invalidate(key: str, *, cache_dir: Path | None = None):
    d = cache_dir if cache_dir is not None else CACHE_DIR
    p = _cache_path_for_dir(d, key)
    if p.exists():
        p.unlink()


# ── Card path helpers ──────────────────────────────────────────────────────

CARDS_DIR: Path = Path(__file__).parent / "papers_cards"


def card_path(key: str, *, cards_dir: Path | None = None) -> Path:
    d = cards_dir if cards_dir is not None else CARDS_DIR
    d.mkdir(exist_ok=True)
    return d / f"{key}.md"


def card_exists_and_verified(key: str, *, cards_dir: Path | None = None) -> bool:
    d = cards_dir if cards_dir is not None else CARDS_DIR
    p = card_path(key, cards_dir=d)
    if not p.exists():
        return False
    return "verified: true" in p.read_text(encoding="utf-8")


def card_invalidate(key: str, *, cards_dir: Path | None = None):
    d = cards_dir if cards_dir is not None else CARDS_DIR
    p = card_path(key, cards_dir=d)
    if p.exists():
        p.unlink()
