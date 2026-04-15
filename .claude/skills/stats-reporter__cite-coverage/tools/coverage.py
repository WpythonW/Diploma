#!/usr/bin/env python3
"""
Citation coverage analysis: which keys are cited where, with quality status.

Usage:
    uv run python coverage.py

Output:
    - cite_coverage.txt (human-readable table)
    - cite_coverage.json (machine-readable)
"""

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
OUTPUT_DIR = Path(__file__).parent

def find_all_tex_files():
    """Find all .tex files in Diploma_latex/"""
    return sorted(LATEX_DIR.glob("*.tex"))

def extract_citations_by_chapter(tex_files):
    """Extract all citations, grouped by chapter and key."""
    chapters = {}  # filename -> {key: count}
    all_cites = defaultdict(list)  # key -> [files where used]

    cite_pattern = r'\\cite\{([^}]+)\}'

    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            chapter_cites = defaultdict(int)

            for match in re.finditer(cite_pattern, content):
                key = match.group(1).strip()
                chapter_cites[key] += 1
                all_cites[key].append(tex_file.name)

            if chapter_cites:
                chapters[tex_file.name] = dict(chapter_cites)

        except Exception as e:
            print(f"Warning: Could not read {tex_file}: {e}")

    return chapters, all_cites

def load_check_results():
    """Load papers_results.json if available."""
    results_file = REPO_ROOT / ".claude" / "skills" / "check-citations" / "tools" / "papers_results.json"
    if results_file.exists():
        try:
            return json.loads(results_file.read_text())
        except:
            return {}
    return {}

def load_context_results():
    """Load all context_check_results/*.json if available."""
    context_dir = REPO_ROOT / ".claude" / "skills" / "check-context" / "tools" / "context_check_results"
    results = {}
    if context_dir.exists():
        for json_file in context_dir.glob("*.json"):
            try:
                results[json_file.stem] = json.loads(json_file.read_text())
            except:
                pass
    return results

def determine_verdict(key, check_results, context_results):
    """Determine combined verdict for a key."""
    verdicts = []

    if key in check_results:
        check_verdict = check_results[key].get('verdict', 'UNKNOWN')
        if check_verdict in ('FAKE', 'UNCERTAIN'):
            verdicts.append(f"BCHECK:{check_verdict}")

    if key in context_results:
        context_overall = context_results[key].get('overall', 'OK')
        if context_overall in ('ERROR', 'WARNING'):
            verdicts.append(f"CONTEXT:{context_overall}")

    if verdicts:
        return " | ".join(verdicts)
    return "OK"

def build_coverage():
    """Build citation coverage data."""
    tex_files = find_all_tex_files()
    chapters, all_cites = extract_citations_by_chapter(tex_files)
    check_results = load_check_results()
    context_results = load_context_results()

    # Build per-key coverage
    coverage = {}
    for key in all_cites.keys():
        usage_count = sum(
            chapters[chapter].get(key, 0)
            for chapter in chapters
        )
        chapters_used = sorted(set(all_cites[key]))
        verdict = determine_verdict(key, check_results, context_results)

        coverage[key] = {
            'usage_count': usage_count,
            'chapters_used': chapters_used,
            'verdict': verdict,
        }

    return {
        'chapters': chapters,
        'coverage': coverage,
        'total_keys': len(coverage),
    }

def format_txt(data):
    """Format coverage as human-readable table."""
    lines = [
        "CITATION COVERAGE ANALYSIS",
        "",
        f"Total keys cited: {data['total_keys']}",
        "",
        "COVERAGE TABLE (sorted by usage count)",
        f"{'Key':30s} | {'Status':40s} | {'Chapters':30s} | {'Count':5s}",
    ]

    # Sort by usage count descending
    sorted_coverage = sorted(
        data['coverage'].items(),
        key=lambda x: x[1]['usage_count'],
        reverse=True
    )

    for key, info in sorted_coverage:
        verdict = info['verdict']
        chapters_str = ", ".join(info['chapters_used'][:3])
        if len(info['chapters_used']) > 3:
            chapters_str += f", +{len(info['chapters_used']) - 3}"

        lines.append(
            f"{key:30s} | {verdict:40s} | {chapters_str:30s} | {info['usage_count']:5d}"
        )

    lines.extend([
        "",
        "PER-CHAPTER BREAKDOWN",
    ])

    for chapter in sorted(data['chapters'].keys()):
        cites = data['chapters'][chapter]
        lines.append(f"\n{chapter}:")
        for key in sorted(cites.keys(), key=lambda k: cites[k], reverse=True):
            count = cites[key]
            verdict = data['coverage'].get(key, {}).get('verdict', 'UNKNOWN')
            marker = "⚠️" if "FAKE" in verdict or "ERROR" in verdict or "UNCERTAIN" in verdict else "✓"
            lines.append(f"  {marker} {key:30s} | {count:2d}x | {verdict[:50]}")

    lines.append("")

    return "\n".join(lines)

if __name__ == "__main__":
    print("📊 Analyzing citation coverage...", end=" ", flush=True)
    data = build_coverage()
    print("Done!")

    # Write JSON
    json_output = OUTPUT_DIR / "cite_coverage.json"
    json_output.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"✓ JSON saved: {json_output}")

    # Write human-readable
    txt_output = OUTPUT_DIR / "cite_coverage.txt"
    txt_output.write_text(format_txt(data))
    print(f"✓ Report saved: {txt_output}")

    # Print to stdout
    print("\n" + format_txt(data))
