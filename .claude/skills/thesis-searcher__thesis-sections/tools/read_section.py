#!/usr/bin/env python3
"""
Read thesis sections: by chapter, citation, paragraph number, or line range.

Usage:
    uv run python read_section.py --chapter 1
    uv run python read_section.py --cite "kahneman2011"
    uv run python read_section.py --chapter 1 --section "Introduction"
    uv run python read_section.py --paragraph 5
    uv run python read_section.py --lines "chapter1.tex:10:50"
"""

import argparse
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
    includes = []
    for match in re.finditer(r'\\(?:input|include)\s*\{([^}]+)\}', content):
        filename = match.group(1).strip()
        if not filename.endswith('.tex'):
            filename += '.tex'
        includes.append(filename)

    return includes

def find_all_tex_files():
    """Find all .tex files in Diploma_latex/"""
    return sorted(LATEX_DIR.glob("*.tex"))

def count_words(text):
    """Count words in LaTeX text."""
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    return len(text.split())

def read_chapter(chapter_num):
    """Read entire chapter by number (1-indexed)."""
    included = parse_main_tex()

    # Find chapter file
    chapter_file = LATEX_DIR / f"chapter{chapter_num}.tex"
    if not chapter_file.exists():
        print(f"Error: chapter{chapter_num}.tex not found")
        return None

    try:
        content = chapter_file.read_text(encoding='utf-8', errors='ignore')
        words = count_words(content)
        cite_count = len(re.findall(r'\\cite\{[^}]+\}', content))

        return {
            'type': 'chapter',
            'identifier': f"Chapter {chapter_num}",
            'file': chapter_file.name,
            'content': content,
            'words': words,
            'cite_count': cite_count,
        }
    except Exception as e:
        print(f"Error reading {chapter_file}: {e}")
        return None

def read_by_cite(cite_key):
    """Read all paragraphs containing a citation key."""
    tex_files = find_all_tex_files()
    paragraphs = []
    cite_pattern = rf'\\cite\{{[^}}]*{re.escape(cite_key)}[^}}]*\}}'

    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')

            # Split by double newlines to get paragraphs
            para_blocks = re.split(r'\n\s*\n', content)

            for para_idx, para in enumerate(para_blocks):
                if re.search(cite_pattern, para):
                    words = count_words(para)
                    paragraphs.append({
                        'file': tex_file.name,
                        'paragraph': para_idx,
                        'content': para.strip(),
                        'words': words,
                    })

        except Exception as e:
            print(f"Warning: Could not read {tex_file}: {e}")

    if not paragraphs:
        print(f"No paragraphs found containing citation: {cite_key}")
        return None

    return {
        'type': 'cite',
        'identifier': cite_key,
        'paragraphs': paragraphs,
        'total_count': len(paragraphs),
    }

def read_by_lines(filename, start_line, end_line):
    """Read specific line range from a file."""
    filepath = LATEX_DIR / filename

    if not filepath.exists():
        print(f"Error: {filename} not found")
        return None

    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')

        # Convert to 0-indexed
        start = start_line - 1
        end = min(end_line, len(lines))

        if start < 0 or start >= len(lines):
            print(f"Error: Invalid line range")
            return None

        extracted = '\n'.join(lines[start:end])
        words = count_words(extracted)
        cite_count = len(re.findall(r'\\cite\{[^}]+\}', extracted))

        return {
            'type': 'lines',
            'identifier': f"{filename}:{start_line}:{end_line}",
            'file': filename,
            'lines': (start_line, end_line),
            'content': extracted,
            'words': words,
            'cite_count': cite_count,
        }
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def format_output(data):
    """Format output as Markdown."""
    if data is None:
        return "No content found."

    lines = [
        f"THESIS SECTION: {data['identifier']}",
        "",
    ]

    if data['type'] == 'chapter':
        lines.extend([
            f"**File:** `{data['file']}`  ",
            f"**Words:** {data['words']:,}  ",
            f"**Citations:** {data['cite_count']}  ",
            "",
            "---",
            "",
            data['content'],
        ])

    elif data['type'] == 'cite':
        lines.extend([
            f"**Citation key:** `{data['identifier']}`  ",
            f"**Paragraphs found:** {data['total_count']}  ",
            "",
            "---",
            "",
        ])

        for para_info in data['paragraphs']:
            lines.extend([
                f"**From {para_info['file']} (para {para_info['paragraph']})** — {para_info['words']} words",
                "",
                para_info['content'],
                "",
            ])

    elif data['type'] == 'lines':
        lines.extend([
            f"**File:** `{data['file']}`  ",
            f"**Lines:** {data['lines'][0]}–{data['lines'][1]}  ",
            f"**Words:** {data['words']:,}  ",
            f"**Citations:** {data['cite_count']}  ",
            "",
            "---",
            "",
            data['content'],
        ])

    return "\n".join(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read thesis sections")
    parser.add_argument("--chapter", type=int, help="Read chapter N")
    parser.add_argument("--cite", help="Read all paragraphs with citation KEY")
    parser.add_argument("--lines", help="Read lines: 'filename:start:end'")

    args = parser.parse_args()

    if not any([args.chapter, args.cite, args.lines]):
        parser.print_help()
        exit(1)

    print("📖 Reading section...", end=" ", flush=True)

    if args.chapter:
        data = read_chapter(args.chapter)
    elif args.cite:
        data = read_by_cite(args.cite)
    elif args.lines:
        parts = args.lines.split(':')
        if len(parts) != 3:
            print("Error: Use format 'filename:start:end'")
            exit(1)
        data = read_by_lines(parts[0], int(parts[1]), int(parts[2]))

    print("Done!")

    output = format_output(data)
    print("\n" + output)

    # Save to file
    output_file = OUTPUT_DIR / "section_content.txt"
    output_file.write_text(output)
    print(f"\n✓ Saved to: {output_file}")
