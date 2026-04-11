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
        searches  = r.get("tool_calls", "?")
        reason    = r.get("reason", "")[:100].replace("|", "/")
        goal_line = extract_card_field(key, "Goal")[:100].replace("|", "/")

        rows.append(
            f"| `{key}` | {icon} {verdict} | {conf}% | {searches} | {goal_line} | {reason} |"
        )

    header = (
        "| Key | Verdict | Conf | Searches | Goal (first line) | Reason |\n"
        "|-----|---------|------|----------|-------------------|--------|\n"
    )
    return header + "\n".join(rows) + "\n"


def main():
    if not RESULTS_FILE.exists():
        print(f"[error] {RESULTS_FILE} not found. Run check_papers.py first.")
        return

    results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(results)} results from {RESULTS_FILE.name}")

    real      = sum(1 for r in results if r["verdict"] == "REAL")
    fake      = sum(1 for r in results if r["verdict"] == "FAKE")
    uncertain = sum(1 for r in results if r["verdict"] == "UNCERTAIN")

    stats = (
        f"**Total:** {len(results)}  |  "
        f"✅ REAL: {real}  |  "
        f"❌ FAKE: {fake}  |  "
        f"⚠️ UNCERTAIN: {uncertain}\n\n"
    )

    table = generate_table(results)

    output = f"# Bibliography Verification Summary\n\n{stats}{table}"
    OUTPUT_FILE.write_text(output, encoding="utf-8")
    print(f"Table written → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
