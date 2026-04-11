"""
Tool: semantic_scholar.py
Бесплатная верификация академических ссылок через Semantic Scholar API.

Использование:
    python semantic_scholar.py "Extensional versus intuitive reasoning" 1983
    python semantic_scholar.py --bib ../../bibliography.bib --check-all
"""

import sys
import json
import re
import argparse
import urllib.request
import urllib.parse
from pathlib import Path

S2_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_FIELDS = "title,year,authors,externalIds"


def search_paper(title: str, expected_year: str = "") -> dict:
    query = urllib.parse.urlencode({
        "query": title[:120],
        "limit": 1,
        "fields": S2_FIELDS,
    })
    req = urllib.request.Request(
        f"{S2_SEARCH}?{query}",
        headers={"User-Agent": "diploma-review/1.0"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())

    if not data.get("data"):
        return {"found": False, "title": title}

    paper = data["data"][0]
    found_year = str(paper.get("year", ""))
    year_ok = (found_year == expected_year) if expected_year else True

    return {
        "found": True,
        "title": paper.get("title", ""),
        "year": found_year,
        "year_match": year_ok,
        "authors": [a["name"] for a in paper.get("authors", [])[:3]],
        "doi": paper.get("externalIds", {}).get("DOI", ""),
    }


def parse_bib(bib_path: Path) -> list[dict]:
    text = bib_path.read_text(encoding="utf-8")
    entries = []
    for m in re.finditer(r"@\w+\{([^,]+),([^@]+)", text, re.DOTALL):
        key = m.group(1).strip()
        body = m.group(2)

        def field(name):
            fm = re.search(rf"{name}\s*=\s*\{{([^}}]+)\}}", body, re.IGNORECASE)
            return fm.group(1).strip() if fm else ""

        entries.append({"key": key, "title": field("title"), "year": field("year")})
    return entries


def check_all_bib(bib_path: Path):
    entries = parse_bib(bib_path)
    print(f"Checking {len(entries)} entries from {bib_path.name}...\n")

    ok, warn, fail = [], [], []
    for i, e in enumerate(entries):
        print(f"  [{i+1}/{len(entries)}] {e['key']}...", end=" ", flush=True)
        try:
            result = search_paper(e["title"], e["year"])
        except Exception as ex:
            result = {"found": False, "error": str(ex)}

        if not result["found"]:
            print("NOT FOUND")
            fail.append(e["key"])
        elif not result.get("year_match", True):
            print(f"YEAR MISMATCH (expected {e['year']}, found {result['year']})")
            warn.append(f"{e['key']}: expected {e['year']}, found {result['year']}")
        else:
            print(f"OK ({result['year']})")
            ok.append(e["key"])

    print(f"\n✅ OK: {len(ok)}  ⚠️ Year mismatch: {len(warn)}  ❌ Not found: {len(fail)}")
    if warn:
        print("\nYear mismatches:")
        for w in warn:
            print(f"  {w}")
    if fail:
        print("\nNot found:")
        for f in fail:
            print(f"  {f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("title", nargs="?", help="Paper title to search")
    parser.add_argument("year", nargs="?", default="", help="Expected year")
    parser.add_argument("--bib", help="Path to .bib file")
    parser.add_argument("--check-all", action="store_true")
    args = parser.parse_args()

    if args.bib and args.check_all:
        check_all_bib(Path(args.bib))
    elif args.title:
        result = search_paper(args.title, args.year)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        parser.print_help()
