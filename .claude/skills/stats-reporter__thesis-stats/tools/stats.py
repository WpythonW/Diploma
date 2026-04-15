#!/usr/bin/env python3
"""
Thesis statistics: word counts, citation distribution, bibliography coverage.
Autonomous tool — run once, self-contained output.

Usage:
    uv run python stats.py

Output:
    - thesis_stats.txt (human-readable)
    - thesis_stats.json (machine-readable)
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
BIB_FILE = LATEX_DIR / "bibliography.bib"
OUTPUT_DIR = Path(__file__).parent

def parse_bib(filepath):
    """Parse .bib file, extract all entry keys."""
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    # Match @type{key, ...}
    pattern = r'@\w+\s*\{\s*([^,\s]+)'
    return set(re.findall(pattern, content))

def find_all_tex_files():
    """Find all .tex files in Diploma_latex/"""
    return sorted(LATEX_DIR.glob("*.tex"))

def count_words(text):
    """Count words in LaTeX text (rough estimate)."""
    # Remove comments
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
    # Remove commands
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    # Count words
    words = text.split()
    return len(words)

def extract_citations_with_locations(tex_files):
    r"""Extract all \cite{key} with file and line locations."""
    citations = defaultdict(list)  # key -> [(file, line_num)]
    cite_pattern = r'\\cite\{([^}]+)\}'

    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            for line_num, line in enumerate(content.split('\n'), 1):
                for match in re.finditer(cite_pattern, line):
                    key = match.group(1).strip()
                    citations[key].append((tex_file.name, line_num))
        except Exception as e:
            print(f"Warning: Could not read {tex_file}: {e}")

    return citations

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

def generate_stats():
    """Generate comprehensive thesis statistics."""
    tex_files = find_all_tex_files()
    bib_keys = parse_bib(BIB_FILE) if BIB_FILE.exists() else set()
    citations = extract_citations_with_locations(tex_files)
    check_results = load_check_results()
    context_results = load_context_results()

    # Calculate per-chapter stats
    chapter_stats = {}
    total_words = 0
    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            words = count_words(content)
            total_words += words

            # Count citations in this file
            file_cite_count = len(re.findall(r'\\cite\{[^}]+\}', content))

            chapter_stats[tex_file.name] = {
                'words': words,
                'citation_count': file_cite_count,
                'citation_density': round(file_cite_count / words * 1000, 2) if words > 0 else 0,
            }
        except Exception as e:
            print(f"Warning: Could not process {tex_file}: {e}")

    # Bibliography coverage
    cited_keys = set(citations.keys())
    unused_keys = bib_keys - cited_keys
    undefined_keys = cited_keys - bib_keys

    # Citation distribution
    citation_distribution = {key: len(locs) for key, locs in citations.items()}

    # Status integration
    key_statuses = {}
    for key in cited_keys:
        status = "OK"
        if key in check_results:
            verdict = check_results[key].get('verdict', 'UNKNOWN')
            if verdict in ('FAKE', 'UNCERTAIN'):
                status = f"CHECK: {verdict}"
        if key in context_results:
            overall = context_results[key].get('overall', 'OK')
            if overall in ('ERROR', 'WARNING'):
                status = f"CONTEXT: {overall}"
        key_statuses[key] = status

    return {
        'total_words': total_words,
        'total_citations': len(cited_keys),
        'bibliography_entries': len(bib_keys),
        'citation_density': round(len(cited_keys) / total_words * 1000, 2) if total_words > 0 else 0,
        'chapter_stats': chapter_stats,
        'bibliography_coverage': {
            'unused_entries': sorted(unused_keys),
            'undefined_citations': sorted(undefined_keys),
            'coverage_percent': round(len(cited_keys) / len(bib_keys) * 100, 1) if bib_keys else 0,
        },
        'citation_distribution': {
            key: citation_distribution[key]
            for key in sorted(citation_distribution.keys(), key=lambda k: citation_distribution[k], reverse=True)
        },
        'key_statuses': key_statuses,
    }

def format_txt(stats):
    """Format stats as human-readable text."""
    lines = [
        "THESIS STATISTICS",
        "",
        f"Total Words: {stats['total_words']:,}",
        f"Total Citations: {stats['total_citations']}",
        f"Bibliography Entries: {stats['bibliography_entries']}",
        f"Citation Density: {stats['citation_density']:.2f} per 1000 words",
        "",
        "CHAPTER BREAKDOWN",
    ]

    for chapter, data in stats['chapter_stats'].items():
        lines.append(
            f"  {chapter:40s} | {data['words']:6,} words | "
            f"{data['citation_count']:3d} cites | density: {data['citation_density']:6.2f}"
        )

    lines.extend([
        "",
        "BIBLIOGRAPHY COVERAGE",
        f"Coverage: {stats['bibliography_coverage']['coverage_percent']:.1f}% "
        f"({stats['total_citations']}/{stats['bibliography_entries']} entries used)",
        "",
    ])

    if stats['bibliography_coverage']['undefined_citations']:
        lines.append("⚠️  UNDEFINED CITATIONS (in .tex but NOT in .bib):")
        for key in stats['bibliography_coverage']['undefined_citations']:
            lines.append(f"  - {key}")
        lines.append("")

    if stats['bibliography_coverage']['unused_entries']:
        lines.append(f"Unused entries ({len(stats['bibliography_coverage']['unused_entries'])} total):")
        for key in sorted(stats['bibliography_coverage']['unused_entries'])[:20]:  # Show first 20
            lines.append(f"  - {key}")
        if len(stats['bibliography_coverage']['unused_entries']) > 20:
            lines.append(f"  ... and {len(stats['bibliography_coverage']['unused_entries']) - 20} more")
        lines.append("")

    lines.append("TOP CITED ENTRIES (by frequency)")

    for key, count in list(stats['citation_distribution'].items())[:15]:
        status = stats['key_statuses'].get(key, 'OK')
        status_mark = "⚠️" if "CHECK" in status or "CONTEXT" in status else "✓"
        lines.append(f"  {status_mark} {key:30s} | used {count:3d} times | {status}")

    lines.append("")

    return "\n".join(lines)

if __name__ == "__main__":
    print("📊 Generating thesis statistics...", end=" ", flush=True)
    stats = generate_stats()
    print("Done!")

    # Write JSON
    json_output = OUTPUT_DIR / "thesis_stats.json"
    json_output.write_text(json.dumps(stats, indent=2, ensure_ascii=False))
    print(f"✓ JSON saved: {json_output}")

    # Write human-readable
    txt_output = OUTPUT_DIR / "thesis_stats.txt"
    txt_output.write_text(format_txt(stats))
    print(f"✓ Report saved: {txt_output}")

    # Print to stdout
    print("\n" + format_txt(stats))
