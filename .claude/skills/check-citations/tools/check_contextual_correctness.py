"""
check_contextual_correctness.py — Contextual relevance checker.

For each bibliography key in papers_cards/:
  1. Extract all paragraphs from .tex files that cite the key.
  2. Send card + paragraphs to Qwen via OpenRouter.
  3. Save structured verdict to context_check_results/.

Usage:
    uv run python check_contextual_correctness.py
    uv run python check_contextual_correctness.py --keys kahneman2011thinking wei2022chain
    uv run python check_contextual_correctness.py --out custom_results/
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# ── Paths ─────────────────────────────────────────────────────────────────────

TOOLS_DIR = Path(__file__).parent
CARDS_DIR = TOOLS_DIR / "papers_cards"
RESULTS_DIR = TOOLS_DIR / "context_check_results"
LATEX_DIR = TOOLS_DIR.parents[3] / "Diploma_latex"

# .tex files to scan (skip config/preamble/abbreviations/terms)
_SKIP_TEX = {"preamble", "abbreviations", "terms", "config-formulas",
              "config-images", "config-lists", "config-tables"}

# ── Model ─────────────────────────────────────────────────────────────────────

load_dotenv(TOOLS_DIR / ".env")
load_dotenv(TOOLS_DIR.parents[3] / ".env", override=False)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
QWEN_MODEL = "qwen/qwen3-235b-a22b-2507"

# ── Citation extraction ───────────────────────────────────────────────────────

_CITE_RE = re.compile(r"\\cite\{([^}]+)\}")


def _extract_paragraphs_with_cite(tex_path: Path, key: str) -> list[dict]:
    """
    Return list of {"file": str, "paragraph": str} for every paragraph
    in the .tex file that cites `key`.
    A paragraph is defined as a block of non-empty lines.
    """
    text = tex_path.read_text(encoding="utf-8", errors="replace")
    # Split into paragraphs (double newline or blank line)
    raw_paras = re.split(r"\n\s*\n", text)
    results = []
    for para in raw_paras:
        para = para.strip()
        if not para:
            continue
        # Find all cite keys in this paragraph
        all_keys: list[str] = []
        for m in _CITE_RE.finditer(para):
            all_keys.extend(k.strip() for k in m.group(1).split(","))
        if key in all_keys:
            results.append({"file": tex_path.name, "paragraph": para})
    return results


def collect_mentions(key: str, latex_dir: Path) -> list[dict]:
    """Collect all paragraphs citing `key` across all relevant .tex files."""
    mentions = []
    for tex_path in sorted(latex_dir.glob("*.tex")):
        stem = tex_path.stem
        if stem in _SKIP_TEX:
            continue
        mentions.extend(_extract_paragraphs_with_cite(tex_path, key))
    return mentions


# ── Card loading ──────────────────────────────────────────────────────────────

def load_card(key: str) -> str | None:
    path = CARDS_DIR / f"{key}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


# ── LLM call ─────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are an academic reviewer checking whether citations in a diploma thesis \
are used in relevant, contextually appropriate ways.

You will receive:
1. A structured paper card (title, goal, method, results, limitations).
2. One or more paragraphs from the thesis that cite this paper.

For each paragraph, assess:
- Is the citation contextually appropriate? Does the thesis paragraph correctly \
  represent or use the cited paper's content?
- Is the citation misleading, over-generalised, or unrelated to the paper?

Respond in JSON with this exact structure:
{
  "key": "<citation_key>",
  "overall": "OK" | "WARNING" | "ERROR",
  "mentions": [
    {
      "file": "<tex_filename>",
      "snippet": "<first 120 chars of paragraph>",
      "verdict": "OK" | "WARNING" | "ERROR",
      "comment": "<brief explanation in Russian>"
    }
  ],
  "summary": "<overall summary in Russian, 1-3 sentences>"
}

Verdict definitions:
- OK: Citation is relevant and correctly used.
- WARNING: Citation is tangentially relevant but potentially misleading or \
  imprecise; the thesis claim is plausible but stretched.
- ERROR: Citation is irrelevant to the paragraph or the thesis claim directly \
  contradicts the paper's content.

Reply with ONLY the JSON object, no markdown fences.
"""


async def check_key(
    key: str,
    mentions: list[dict],
    card_text: str,
    client: ChatOpenAI,
    semaphore: asyncio.Semaphore,
) -> dict:
    """Call Qwen to check contextual relevance. Returns parsed dict."""
    mentions_text = "\n\n".join(
        f"[{i+1}] File: {m['file']}\n{m['paragraph']}"
        for i, m in enumerate(mentions)
    )
    user_msg = (
        f"## Paper card for `{key}`\n\n{card_text}\n\n"
        f"---\n\n## Thesis mentions ({len(mentions)} total)\n\n{mentions_text}"
    )

    async with semaphore:
        response = await client.ainvoke([
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ])

    raw = response.content.strip()
    # Strip markdown fences if model adds them anyway
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    # Strip <think>...</think> tags (Qwen3 reasoning traces)
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "key": key,
            "overall": "ERROR",
            "mentions": [],
            "summary": f"[Parse error] Raw response: {raw[:300]}",
        }
    return result


# ── Main pipeline ─────────────────────────────────────────────────────────────

async def run(keys: list[str], results_dir: Path) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)

    client = ChatOpenAI(
        model=QWEN_MODEL,
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        temperature=0.3,
    )
    semaphore = asyncio.Semaphore(5)  # max 5 parallel LLM calls

    total = len(keys)
    ok_count = warn_count = err_count = skip_count = 0

    print(f"Checking contextual correctness for {total} keys...")
    print(f"LaTeX dir: {LATEX_DIR}")
    print()

    for i, key in enumerate(keys, 1):
        out_path = results_dir / f"{key}.json"

        card_text = load_card(key)
        if card_text is None:
            print(f"[{i}/{total}] {key} — SKIP (no card found)")
            skip_count += 1
            continue

        mentions = collect_mentions(key, LATEX_DIR)
        if not mentions:
            print(f"[{i}/{total}] {key} — SKIP (not cited in tex files)")
            skip_count += 1
            # Still save a record
            result = {
                "key": key,
                "overall": "NOT_CITED",
                "mentions": [],
                "summary": "Ключ присутствует в библиографии, но не встречается в тексте диплома.",
            }
            out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
            continue

        result = await check_key(key, mentions, card_text, client, semaphore)
        result.setdefault("key", key)
        result.setdefault("mention_count", len(mentions))

        verdict = result.get("overall", "ERROR")
        if verdict == "OK":
            ok_count += 1
        elif verdict == "WARNING":
            warn_count += 1
        else:
            err_count += 1

        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"[{i}/{total}] {key} — {verdict} ({len(mentions)} mention(s))")

    print()
    print("=" * 60)
    print(f"Done. Total: {total}")
    print(f"  OK:         {ok_count}")
    print(f"  WARNING:    {warn_count}")
    print(f"  ERROR:      {err_count}")
    print(f"  Skipped:    {skip_count}")
    print(f"Results saved to: {results_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check contextual correctness of citations.")
    parser.add_argument(
        "--keys", nargs="*", metavar="KEY",
        help="Specific citation keys to check (default: all keys in papers_cards/)."
    )
    parser.add_argument(
        "--out", default=str(RESULTS_DIR), metavar="DIR",
        help=f"Output directory for results (default: {RESULTS_DIR})."
    )
    args = parser.parse_args()

    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    if args.keys:
        keys = args.keys
    else:
        keys = sorted(p.stem for p in CARDS_DIR.glob("*.md"))

    if not keys:
        print("No keys found. Run check_papers.py first to generate cards.")
        sys.exit(0)

    results_dir = Path(args.out)
    asyncio.run(run(keys, results_dir))


if __name__ == "__main__":
    main()
