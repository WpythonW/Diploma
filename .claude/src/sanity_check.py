#!/usr/bin/env python3
"""
Thesis Sanity Check: Quick validation of images, citations, structure, and references.
Reports ONLY problems (broken paths, undefined citations, empty sections, etc.).

Usage:
    uv run python sanity_check.py

Output:
    - sanity_report.txt (errors only, or "all ok")
    - sanity_report.json (machine-readable)
    - Exit code: 0=PASS, 1=FAIL, 2=ERROR
"""

import json
import sys
from pathlib import Path
from checks import (
    check_images, check_citations, check_labels_and_refs, check_todos,
    check_empty_sections, check_main_tex_includes, check_unused_tex_files
)


def find_thesis_root():
    """Find repo root containing Diploma_latex/"""
    cwd = Path.cwd()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "Diploma_latex").exists():
            return candidate
    raise FileNotFoundError("Could not find Diploma_latex/")


def parse_bib(filepath):
    """Parse .bib file, extract all entry keys."""
    import re
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    pattern = r'@\w+\s*\{\s*([^,\s]+)'
    return set(re.findall(pattern, content))


def find_all_tex_files(latex_dir):
    """Find all .tex files in Diploma_latex/"""
    return sorted(latex_dir.glob("*.tex"))


def run_checks():
    """Run all checks. Return results dict."""
    repo_root = find_thesis_root()
    latex_dir = repo_root / "Diploma_latex"
    main_tex = latex_dir / "main.tex"
    bib_file = latex_dir / "bibliography.bib"

    tex_files = find_all_tex_files(latex_dir)
    bib_keys = parse_bib(bib_file) if bib_file.exists() else set()

    # Run all checks
    broken_images = check_images(tex_files, latex_dir, repo_root)
    undefined_cites, unused_entries = check_citations(tex_files, bib_keys)
    broken_refs, duplicate_labels = check_labels_and_refs(tex_files)
    todos = check_todos(tex_files)
    short_sections = check_empty_sections(tex_files)
    broken_includes = check_main_tex_includes(main_tex, latex_dir)
    unused_tex_files = check_unused_tex_files(main_tex, latex_dir)

    has_issues = bool(
        broken_images or undefined_cites or unused_entries or
        broken_refs or duplicate_labels or todos or
        short_sections or broken_includes or unused_tex_files
    )

    return {
        'pass': not has_issues,
        'broken_images': broken_images,
        'undefined_cites': undefined_cites,
        'unused_entries': unused_entries,
        'broken_refs': broken_refs,
        'duplicate_labels': duplicate_labels,
        'todos': todos,
        'empty_sections': short_sections,
        'broken_includes': broken_includes,
        'unused_tex_files': unused_tex_files,
    }


def format_report(results):
    """Format report. Show only errors, or 'all ok'."""
    if results['pass']:
        return "✅ All checks passed"

    lines = []

    if results['broken_images']:
        lines.append("BROKEN IMAGE PATHS:")
        for img in results['broken_images']:
            lines.append(f"  {img['file']}:{img['line']} → {img['path']}")
        lines.append("")

    if results['undefined_cites']:
        lines.append("UNDEFINED CITATIONS (used but not in bibliography):")
        for cite in results['undefined_cites']:
            lines.append(f"  {cite['key']} (used {cite['count']}x)")
        lines.append("")

    if results['unused_entries']:
        lines.append("UNUSED BIBLIOGRAPHY ENTRIES:")
        for entry in results['unused_entries'][:15]:
            lines.append(f"  {entry['key']}")
        if len(results['unused_entries']) > 15:
            lines.append(f"  ... and {len(results['unused_entries']) - 15} more")
        lines.append("")

    if results['broken_refs']:
        lines.append("BROKEN REFERENCES (\\ref to non-existent \\label):")
        for ref in results['broken_refs']:
            lines.append(f"  {ref['file']}:{ref['line']} → \\ref{{{ref['ref']}}}")
        lines.append("")

    if results['duplicate_labels']:
        lines.append("DUPLICATE LABELS:")
        for dup in results['duplicate_labels']:
            lines.append(f"  {dup['label']} (defined {dup['count']}x):")
            for file, line in dup['locations']:
                lines.append(f"    - {file}:{line}")
        lines.append("")

    if results['todos']:
        lines.append(f"TODO/FIXME COMMENTS ({len(results['todos'])} found):")
        for todo in results['todos']:
            lines.append(f"  {todo['file']}:{todo['line']} → {todo['content']}")
        lines.append("")

    if results['empty_sections']:
        lines.append("VERY SHORT SECTIONS (< 10 words):")
        for sec in results['empty_sections']:
            lines.append(f"  {sec['file']}:{sec['line']} [{sec['word_count']} words] → {sec['section']}")
        lines.append("")

    if results['broken_includes']:
        lines.append("BROKEN \\input/\\include IN main.tex:")
        for inc in results['broken_includes']:
            lines.append(f"  {inc['path']} (line {inc['line']})")
        lines.append("")

    if results['unused_tex_files']:
        lines.append("UNUSED .tex FILES (not included in main.tex):")
        for tex in results['unused_tex_files']:
            lines.append(f"  {tex['file']}")

    return "\n".join(lines).rstrip()


if __name__ == "__main__":
    print("🔍 Running sanity checks...", end=" ", flush=True)
    try:
        results = run_checks()
        print("Done!")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(2)

    # Write JSON
    output_dir = Path(__file__).parent
    json_output = output_dir / "sanity_report.json"
    json_output.write_text(json.dumps(results, indent=2, ensure_ascii=False))

    # Write TXT
    report_text = format_report(results)
    txt_output = output_dir / "sanity_report.txt"
    txt_output.write_text(report_text)

    # Print to stdout
    print(report_text)

    # Exit code
    sys.exit(0 if results['pass'] else 1)
