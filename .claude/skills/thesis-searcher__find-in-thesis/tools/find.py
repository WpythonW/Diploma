#!/usr/bin/env python3
"""
Search thesis with context: patterns, citations, TODOs, undefined references.

Usage:
    uv run python find.py --pattern "bias" --context 10
    uv run python find.py --cite "kahneman2011"
    uv run python find.py --todo
    uv run python find.py --undefined-cite
    uv run python find.py --pattern "test" --chapter 1
"""

import argparse
import json
import re
from pathlib import Path
from collections import defaultdict

def find_thesis_root():
    """Find repo root containing Diploma_latex/"""
    cwd = Path.cwd()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "Diploma_latex").exists():
            return candidate
    raise FileNotFoundError("Could not find Diploma_latex/")

REPO_ROOT = find_thesis_root()
LATEX_DIR = REPO_ROOT / "Diploma_latex"
BIB_FILE = LATEX_DIR / "bibliography.bib"
OUTPUT_DIR = Path(__file__).parent

def parse_bib():
    """Extract all keys from .bib file."""
    if not BIB_FILE.exists():
        return set()
    content = BIB_FILE.read_text(encoding='utf-8', errors='ignore')
    pattern = r'@\w+\s*\{\s*([^,\s]+)'
    return set(re.findall(pattern, content))

def find_all_tex_files(chapter_num=None):
    """Find all .tex files, optionally filtered by chapter."""
    all_files = sorted(LATEX_DIR.glob("*.tex"))

    if chapter_num is not None:
        # Filter to chapter file if it exists
        chapter_file = LATEX_DIR / f"chapter{chapter_num}.tex"
        if chapter_file.exists():
            return [chapter_file]
        else:
            print(f"Warning: chapter{chapter_num}.tex not found")
            return []

    return all_files

def extract_context(content, line_num, context_size):
    """Extract context around a line."""
    lines = content.split('\n')
    start = max(0, line_num - 1 - context_size)
    end = min(len(lines), line_num + context_size)

    context_before = '\n'.join(lines[start:line_num - 1])
    context_after = '\n'.join(lines[line_num:end])
    full_line = lines[line_num - 1] if line_num <= len(lines) else ''

    return {
        'context_before': context_before.strip(),
        'context_after': context_after.strip(),
        'full_line': full_line.strip(),
    }

def search_pattern(pattern, context_size=10, chapter_num=None):
    """Search for regex pattern in thesis."""
    tex_files = find_all_tex_files(chapter_num)
    matches = []

    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            for line_num, line in enumerate(content.split('\n'), 1):
                if re.search(pattern, line, re.IGNORECASE):
                    match_obj = re.search(pattern, line, re.IGNORECASE)
                    ctx = extract_context(content, line_num, context_size)
                    matches.append({
                        'file': tex_file.name,
                        'line': line_num,
                        'matched_text': match_obj.group(0),
                        **ctx,
                    })
        except Exception as e:
            print(f"Warning: Could not read {tex_file}: {e}")

    return matches

def search_citation(cite_key, chapter_num=None):
    """Search for \\cite{key}."""
    pattern = rf'\\cite\{{[^}}]*{re.escape(cite_key)}[^}}]*\}}'
    return search_pattern(pattern, context_size=5, chapter_num=chapter_num)

def find_todos():
    """Find all TODOs, FIXMEs, XXXs, etc."""
    pattern = r'(TODO|FIXME|XXX|PLACEHOLDER)'
    return search_pattern(pattern, context_size=3)

def find_undefined_cites(chapter_num=None):
    """Find \\cite{} that are not in .bib."""
    bib_keys = parse_bib()
    tex_files = find_all_tex_files(chapter_num)
    matches = []
    cite_pattern = r'\\cite\{([^}]+)\}'

    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            for line_num, line in enumerate(content.split('\n'), 1):
                for cite_match in re.finditer(cite_pattern, line):
                    key = cite_match.group(1).strip()
                    if key not in bib_keys:
                        ctx = extract_context(content, line_num, 3)
                        matches.append({
                            'file': tex_file.name,
                            'line': line_num,
                            'matched_text': f'\\cite{{{key}}}',
                            'undefined_key': key,
                            **ctx,
                        })
        except Exception as e:
            print(f"Warning: Could not read {tex_file}: {e}")

    return matches

def format_results(matches, query_type, query):
    """Format results as human-readable text."""
    lines = [
        f"SEARCH RESULTS: {query_type.upper()}",
        f"Query: {query}",
        "",
        f"Total matches: {len(matches)}",
        "",
    ]

    if not matches:
        lines.append("No matches found.")
    else:
        for i, match in enumerate(matches, 1):
            lines.extend([
                f"{i}. {match['file']}:{match['line']}",
                f"   Match: {match['matched_text'][:70]}" + ("..." if len(match['matched_text']) > 70 else ""),
                f"   Full line: {match['full_line'][:75]}" + ("..." if len(match['full_line']) > 75 else ""),
                "",
            ])

    return "\n".join(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search thesis with context")
    parser.add_argument("--pattern", help="Regex pattern to search")
    parser.add_argument("--cite", help="Citation key to find")
    parser.add_argument("--todo", action="store_true", help="Find TODOs/FIXMEs/XXXs")
    parser.add_argument("--undefined-cite", action="store_true", help="Find undefined citations")
    parser.add_argument("--context", type=int, default=10, help="Lines of context (default: 10)")
    parser.add_argument("--chapter", type=int, help="Limit search to specific chapter")

    args = parser.parse_args()

    if not any([args.pattern, args.cite, args.todo, args.undefined_cite]):
        parser.print_help()
        exit(1)

    print("🔍 Searching thesis...", flush=True)

    if args.pattern:
        matches = search_pattern(args.pattern, args.context, args.chapter)
        query_type = "pattern"
        query = args.pattern
    elif args.cite:
        matches = search_citation(args.cite, args.chapter)
        query_type = "cite"
        query = args.cite
    elif args.todo:
        matches = find_todos()
        query_type = "todo"
        query = "TODO/FIXME/XXX/PLACEHOLDER"
    elif args.undefined_cite:
        matches = find_undefined_cites(args.chapter)
        query_type = "undefined-cite"
        query = "undefined citations"

    # Output results
    print(format_results(matches, query_type, query))

    # Save JSON
    output_file = OUTPUT_DIR / "find_results.json"
    output_file.write_text(json.dumps({
        'query_type': query_type,
        'query': query,
        'total': len(matches),
        'matches': matches,
    }, indent=2, ensure_ascii=False))
    print(f"✓ Results saved: {output_file}")
