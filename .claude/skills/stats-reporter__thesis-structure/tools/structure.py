#!/usr/bin/env python3
"""
Parse thesis structure from main.tex and generate architecture map.

Usage:
    uv run python structure.py

Output:
    - thesis_structure.txt (human-readable map)
    - thesis_structure.json (machine-readable metadata)
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
MAIN_TEX = LATEX_DIR / "main.tex"
OUTPUT_DIR = Path(__file__).parent

def parse_main_tex():
    """Extract chapter includes from main.tex in order."""
    if not MAIN_TEX.exists():
        return []

    content = MAIN_TEX.read_text(encoding='utf-8', errors='ignore')

    # Find all \input{...} and \include{...} commands
    includes = []
    for match in re.finditer(r'\\(?:input|include)\s*\{([^}]+)\}', content):
        filename = match.group(1).strip()
        # Normalize filename
        if not filename.endswith('.tex'):
            filename += '.tex'
        includes.append(filename)

    return includes

def count_words(text):
    """Count words in LaTeX text."""
    # Remove comments
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
    # Remove commands
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    words = text.split()
    return len(words)

def extract_section_titles(content):
    """Extract all section/subsection titles."""
    sections = []
    for match in re.finditer(r'\\(chapter|section|subsection|subsubsection)\*?\{([^}]+)\}', content):
        level = match.group(1)
        title = match.group(2)
        sections.append({'level': level, 'title': title})
    return sections

def extract_figures(content):
    """Extract figure labels and captions."""
    figures = []
    # Look for \label{fig:...} inside figure environments
    for match in re.finditer(r'\\label\{(fig:[^}]+)\}', content):
        figures.append(match.group(1))
    return figures

def extract_tables(content):
    """Extract table labels."""
    tables = []
    for match in re.finditer(r'\\label\{(tab:[^}]+)\}', content):
        tables.append(match.group(1))
    return tables

def extract_citations(content):
    """Extract all citation keys."""
    cites = set()
    for match in re.finditer(r'\\cite\{([^}]+)\}', content):
        key = match.group(1).strip()
        cites.add(key)
    return cites

def detect_chapter_type(filename, sections):
    """Guess chapter type from filename and sections."""
    name = filename.lower()
    if 'intro' in name:
        return 'introduction'
    if 'method' in name or 'experiment' in name:
        return 'methodology'
    if 'result' in name:
        return 'results'
    if 'discuss' in name or 'conclusion' in name:
        return 'discussion'
    if 'exp' in name or '246' in name or 'wason' in name or 'linda' in name:
        return 'experiment'
    return 'content'

def build_structure():
    """Build complete structure metadata."""
    included_files = parse_main_tex()
    structure = []
    figure_map = defaultdict(list)  # figure -> chapters
    table_map = defaultdict(list)
    experiments = set()

    for chapter_idx, filename in enumerate(included_files, 1):
        filepath = LATEX_DIR / filename

        if not filepath.exists():
            print(f"Warning: {filename} not found")
            continue

        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')

            # Extract metadata
            sections = extract_section_titles(content)
            figures = extract_figures(content)
            tables = extract_tables(content)
            citations = extract_citations(content)
            words = count_words(content)

            chapter_type = detect_chapter_type(filename, sections)

            # Track experiments
            if 'exp' in filename or 'linda' in filename or 'wason' in filename:
                if 'linda' in filename:
                    experiments.add('linda-problem')
                if 'wason' in filename and '246' in filename:
                    experiments.add('wason-2-4-6')
                elif 'wason' in filename:
                    experiments.add('wason-selection')

            # Track figures/tables
            for fig in figures:
                figure_map[fig].append(filename)
            for tab in tables:
                table_map[tab].append(filename)

            chapter_info = {
                'order': chapter_idx,
                'filename': filename,
                'type': chapter_type,
                'words': words,
                'citation_count': len(citations),
                'figure_count': len(figures),
                'table_count': len(tables),
                'sections': sections,
                'figures': figures,
                'tables': tables,
            }

            structure.append(chapter_info)

        except Exception as e:
            print(f"Warning: Could not process {filename}: {e}")

    return {
        'chapters': structure,
        'total_chapters': len(structure),
        'figure_map': dict(figure_map),
        'table_map': dict(table_map),
        'experiments': sorted(list(experiments)),
    }

def format_txt(data):
    """Format structure as human-readable text."""
    lines = [
        "THESIS STRUCTURE",
        "",
        f"Total chapters: {data['total_chapters']}",
        "",
    ]

    if data['experiments']:
        lines.extend([
            "Experiments:",
            ", ".join(data['experiments']),
            "",
        ])

    lines.append("CHAPTER BREAKDOWN")

    for ch in data['chapters']:
        type_tag = f"[{ch['type'].upper()}]"
        lines.append(
            f"{ch['order']:2d}. {ch['filename']:30s} {type_tag:20s} | "
            f"{ch['words']:6,} words | {ch['citation_count']:2d} cites | "
            f"fig:{ch['figure_count']} tbl:{ch['table_count']}"
        )

        if ch['sections']:
            for sec in ch['sections']:
                indent = "   " if sec['level'] == 'chapter' else "     "
                lines.append(f"{indent}{sec['level']:12s} {sec['title'][:50]}")

    lines.append("")

    return "\n".join(lines)

if __name__ == "__main__":
    print("📑 Parsing thesis structure...", end=" ", flush=True)
    data = build_structure()
    print("Done!")

    # Write JSON
    json_output = OUTPUT_DIR / "thesis_structure.json"
    json_output.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"✓ JSON saved: {json_output}")

    # Write human-readable
    txt_output = OUTPUT_DIR / "thesis_structure.txt"
    txt_output.write_text(format_txt(data))
    print(f"✓ Report saved: {txt_output}")

    # Print to stdout
    print("\n" + format_txt(data))
