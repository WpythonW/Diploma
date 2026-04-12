"""
Generate a Markdown summary table from papers_results.json.

Usage (from repo root):
    uv run python .claude/skills/check-citations/tools/generate_summary_table.py

Output:
    .claude/skills/check-citations/tools/papers_summary_table.md
"""

import json
from pathlib import Path

RESULTS_FILE = Path(__file__).parent / "papers_results.json"
OUTPUT_FILE  = Path(__file__).parent / "papers_summary_table.md"
CARDS_DIR    = Path(__file__).parent / "papers_cards"


VERDICT_ICON = {"REAL": "✅", "FAKE": "❌", "UNCERTAIN": "⚠️"}


def short_authors(authors: str, max_authors: int = 3) -> str:
    """Shorten author list: 'Last1, Last2 et al.' from 'First Last and First Last...'"""
    parts = [a.strip() for a in authors.replace(" and ", ";").split(";") if a.strip()]
    surnames = []
    for p in parts:
        # handles 'Last, F.' and 'First Last'
        if "," in p:
            surnames.append(p.split(",")[0].strip())
        else:
            tokens = p.split()
            surnames.append(tokens[-1] if tokens else p)
    if len(surnames) > max_authors:
        return ", ".join(surnames[:max_authors]) + " et al."
    return ", ".join(surnames)


def extract_card_field(key: str, field: str) -> str:
    """Read first non-empty line from a card section, return '' if not found."""
    card_file = CARDS_DIR / f"{key}.md"
    if not card_file.exists():
        return ""
    text = card_file.read_text(encoding="utf-8")
    # find the section header
    marker = f"## {field}\n"
    idx = text.find(marker)
    if idx == -1:
        return ""
    rest = text[idx + len(marker):]
    for line in rest.splitlines():
        line = line.strip()
        if line and not line.startswith("##"):
            # truncate long lines
            return line[:120] + ("…" if len(line) > 120 else "")
    return ""


def generate_table(results: list[dict]) -> str:
    rows = []
    for r in sorted(results, key=lambda x: (x["verdict"] != "FAKE", x["verdict"] != "UNCERTAIN", x["key"])):
        key       = r["key"]
        verdict   = r["verdict"]
        conf      = r["confidence"]
        icon      = VERDICT_ICON.get(verdict, "?")
        layer     = r.get("layer", "?")
        layer_tag = "🔍det" if layer == "deterministic" else "🤖llm"
        ac        = r.get("api_calls", {})
        api_summary = (
            f"arXiv:{ac.get('arxiv',0)} "
            f"S2p:{ac.get('s2_prefetch',0)} "
            f"S2t:{ac.get('s2_tool',0)} "
            f"tav:{ac.get('tavily',0)} "
            f"llm:{ac.get('llm',0)}"
        )
        reason    = r.get("reason", "")[:100].replace("|", "/")
        goal_line = extract_card_field(key, "Goal")[:100].replace("|", "/")

        rows.append(
            f"| `{key}` | {icon} {verdict} | {conf}% | {layer_tag} | {api_summary} | {goal_line} | {reason} |"
        )

    header = (
        "| Key | Verdict | Conf | Layer | API calls | Goal (first line) | Reason |\n"
        "|-----|---------|------|-------|-----------|-------------------|--------|\n"
    )
    return header + "\n".join(rows) + "\n"


def generate_api_stats(results: list[dict]) -> str:
    """Build aggregated API usage block for the report."""
    import statistics as _stats

    def _sum(key):
        return sum(r.get("api_calls", {}).get(key, 0) for r in results)

    n = len(results)
    det = sum(1 for r in results if r.get("layer") == "deterministic")
    llm = sum(1 for r in results if r.get("layer") == "llm")

    lines = [
        "## API Usage Statistics\n",
        f"| Metric | Total | Per paper (avg) |",
        f"|--------|-------|-----------------|",
        f"| Papers checked | {n} | — |",
        f"| Deterministic (Layer 1+2) | {det} | {det/n*100:.0f}% of papers |",
        f"| LLM path (Layer 3) | {llm} | {llm/n*100:.0f}% of papers |",
        f"| arXiv API lookups | {_sum('arxiv')} | {_sum('arxiv')/n:.2f} |",
        f"| S2 prefetch calls | {_sum('s2_prefetch')} | {_sum('s2_prefetch')/n:.2f} |",
        f"| S2 tool calls (LLM) | {_sum('s2_tool')} | {_sum('s2_tool')/n:.2f} |",
        f"| Tavily calls | {_sum('tavily')} | {_sum('tavily')/n:.2f} |",
        f"| LLM (qwen) invocations | {_sum('llm')} | {_sum('llm')/n:.2f} |",
    ]

    llm_results = [r for r in results if r.get("layer") == "llm"]
    if llm_results:
        tav = [r.get("api_calls", {}).get("tavily", 0) for r in llm_results]
        s2t = [r.get("api_calls", {}).get("s2_tool", 0) for r in llm_results]
        lines += [
            f"\n**LLM-path papers only (n={len(llm_results)}):**\n",
            f"| Metric | Median | Max |",
            f"|--------|--------|-----|",
            f"| Tavily/paper | {_stats.median(tav)} | {max(tav)} |",
            f"| S2 tool/paper | {_stats.median(s2t)} | {max(s2t)} |",
        ]

    return "\n".join(lines) + "\n"


def main():
    if not RESULTS_FILE.exists():
        print(f"[error] {RESULTS_FILE} not found. Run check_papers.py first.")
        return

    results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(results)} results from {RESULTS_FILE.name}")

    real      = sum(1 for r in results if r["verdict"] == "REAL")
    fake      = sum(1 for r in results if r["verdict"] == "FAKE")
    uncertain = sum(1 for r in results if r["verdict"] == "UNCERTAIN")

    verdict_stats = (
        f"**Total:** {len(results)}  |  "
        f"✅ REAL: {real}  |  "
        f"❌ FAKE: {fake}  |  "
        f"⚠️ UNCERTAIN: {uncertain}\n\n"
    )

    table    = generate_table(results)
    api_stats = generate_api_stats(results)

    output = (
        f"# Bibliography Verification Summary\n\n"
        f"{verdict_stats}"
        f"{table}\n"
        f"{api_stats}"
    )
    OUTPUT_FILE.write_text(output, encoding="utf-8")
    print(f"Table written → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
