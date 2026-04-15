"""Individual check modules for sanity-check."""

import re
from pathlib import Path
from collections import defaultdict


def check_images(tex_files, latex_dir, repo_root):
    """Check image paths. Return list of broken paths."""
    broken = []
    pattern = r'\\includegraphics\s*\[[^\]]*\]\s*\{([^}]+)\}'

    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            for line_num, line in enumerate(content.split('\n'), 1):
                for match in re.finditer(pattern, line):
                    img_path = match.group(1).strip()

                    # Skip demo image
                    if 'example.jpg' in img_path:
                        continue

                    # Try to resolve path
                    filepath = latex_dir / img_path
                    if not filepath.exists():
                        filepath = repo_root / img_path

                    if not filepath.exists():
                        broken.append({
                            'file': tex_file.name,
                            'line': line_num,
                            'path': img_path,
                        })
        except Exception as e:
            print(f"Warning: Could not read {tex_file}: {e}")

    return broken


def check_citations(tex_files, bib_keys):
    """Check citations. Return (undefined_list, unused_list)."""
    citations = defaultdict(list)
    cite_pattern = r'\\cite\{([^}]+)\}'

    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            for line_num, line in enumerate(content.split('\n'), 1):
                for match in re.finditer(cite_pattern, line):
                    keys_str = match.group(1).strip()
                    for key in keys_str.split(','):
                        key = key.strip()
                        if key:
                            citations[key].append((tex_file.name, line_num))
        except Exception as e:
            print(f"Warning: Could not read {tex_file}: {e}")

    # Find undefined citations
    undefined = [
        {'key': key, 'count': len(locs)}
        for key in sorted(citations.keys())
        if key not in bib_keys
    ]

    # Find unused entries
    unused = [
        {'key': key}
        for key in sorted(bib_keys)
        if key not in citations
    ]

    return undefined, unused


def check_labels_and_refs(tex_files):
    """Check \\label{} and \\ref{}. Return (broken_refs, duplicate_labels)."""
    labels = defaultdict(list)
    refs = []
    label_pattern = r'\\label\{([^}]+)\}'
    ref_pattern = r'\\ref\{([^}]+)\}'

    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            for line_num, line in enumerate(content.split('\n'), 1):
                # Collect labels
                for match in re.finditer(label_pattern, line):
                    label = match.group(1).strip()
                    if label:
                        labels[label].append((tex_file.name, line_num))
                # Collect refs
                for match in re.finditer(ref_pattern, line):
                    ref = match.group(1).strip()
                    if ref:
                        refs.append({'ref': ref, 'file': tex_file.name, 'line': line_num})
        except Exception as e:
            print(f"Warning: Could not read {tex_file}: {e}")

    # Find broken refs (refs without corresponding label)
    label_keys = set(labels.keys())
    broken_refs = [
        r for r in refs if r['ref'] not in label_keys
    ]

    # Find duplicate labels
    duplicate_labels = [
        {'label': label, 'count': len(locs), 'locations': locs}
        for label, locs in sorted(labels.items())
        if len(locs) > 1
    ]

    return broken_refs, duplicate_labels


def check_todos(tex_files):
    """Check for TODO/FIXME comments. Return list."""
    todos = []
    todo_pattern = r'%\s*(?:TODO|FIXME|XXX|HACK|BUG)'

    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            for line_num, line in enumerate(content.split('\n'), 1):
                if re.search(todo_pattern, line, re.IGNORECASE):
                    todos.append({
                        'file': tex_file.name,
                        'line': line_num,
                        'content': line.strip()[:80]  # First 80 chars
                    })
        except Exception as e:
            print(f"Warning: Could not read {tex_file}: {e}")

    return todos


def check_empty_sections(tex_files):
    """Check for very short/empty sections (excluding chapter titles). Return list."""
    short_sections = []
    section_pattern = r'\\(?:section|subsection|subsubsection)\{([^}]+)\}'

    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            for i, line in enumerate(lines):
                if re.search(section_pattern, line):
                    # Get section name
                    match = re.search(section_pattern, line)
                    section_name = match.group(1)

                    # Count words until next section/chapter or end of file
                    word_count = 0
                    j = i + 1  # Start from next line
                    while j < len(lines):
                        next_line = lines[j]
                        # Stop at next section/chapter/part
                        if re.search(r'\\(?:chapter|section|subsection|subsubsection|part)\{', next_line):
                            break
                        # Skip comments and empty lines
                        if next_line.strip() and not next_line.strip().startswith('%'):
                            word_count += len(next_line.split())
                        j += 1

                    # Report if less than 20 words (very short section with actual content)
                    if word_count < 20 and word_count > 0:
                        short_sections.append({
                            'file': tex_file.name,
                            'line': i + 1,
                            'section': section_name,
                            'word_count': word_count,
                        })
        except Exception as e:
            print(f"Warning: Could not read {tex_file}: {e}")

    return short_sections


def check_main_tex_includes(main_tex, latex_dir):
    """Check if all \\input/\\include in main.tex point to existing files.
    Return list of broken includes."""
    broken_includes = []
    include_pattern = r'\\(?:input|include)\{([^}]+)\}'

    try:
        content = main_tex.read_text(encoding='utf-8', errors='ignore')
        for line_num, line in enumerate(content.split('\n'), 1):
            for match in re.finditer(include_pattern, line):
                filepath = match.group(1).strip()
                # Try with and without .tex extension
                candidates = [
                    latex_dir / filepath,
                    latex_dir / (filepath + '.tex'),
                ]
                if not any(c.exists() for c in candidates):
                    broken_includes.append({
                        'line': line_num,
                        'path': filepath,
                        'tried': [str(c.relative_to(latex_dir.parent)) for c in candidates],
                    })
    except Exception as e:
        print(f"Warning: Could not read main.tex: {e}")

    return broken_includes


def check_unused_tex_files(main_tex, latex_dir):
    """Check for .tex files not included in main.tex (recursively). Return list."""
    unused_files = []

    # Recursively collect all included files
    include_pattern = r'\\(?:input|include)\{([^}]+)\}'
    included = set()

    def collect_includes(tex_file):
        """Recursively collect all included files."""
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            for match in re.finditer(include_pattern, content):
                filepath = match.group(1).strip()
                # Normalize to filename
                if not filepath.endswith('.tex'):
                    filepath += '.tex'

                if filepath not in included:
                    included.add(filepath)
                    # Recurse into this file
                    candidate = latex_dir / filepath
                    if candidate.exists():
                        collect_includes(candidate)
        except Exception as e:
            print(f"Warning: Could not read {tex_file}: {e}")

    # Start from main.tex
    try:
        collect_includes(main_tex)
    except Exception as e:
        print(f"Warning: Could not process main.tex: {e}")
        return unused_files

    # Find all .tex files in latex_dir
    all_tex = set(f.name for f in latex_dir.glob('*.tex'))

    # Files to exclude (utility/generated files)
    exclude = {'main.tex', 'config-images.tex', 'main.bbl', 'preamble.tex'}

    unused = all_tex - included - exclude

    for filename in sorted(unused):
        unused_files.append({
            'file': filename,
            'path': str((latex_dir / filename).relative_to(latex_dir.parent)),
        })

    return unused_files
