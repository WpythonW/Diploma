---
title: Thesis Sections Reader
description: Read whole sections by chapter, citation key, or line range — get structured output with preserved formatting
---

# Skill: thesis_sections_reader

Autonomous tool for reading thesis sections with proper structure and context.

## Commands

All from repo root:

```bash
# Read entire chapter
uv run python .claude/skills/thesis-sections/tools/read_section.py --chapter 1

# Read all paragraphs containing a citation key
uv run python .claude/skills/thesis-sections/tools/read_section.py --cite "kahneman2011"

# Read by chapter and section title
uv run python .claude/skills/thesis-sections/tools/read_section.py --chapter 1 --section "Introduction"

# Read by paragraph number (across all .tex files)
uv run python .claude/skills/thesis-sections/tools/read_section.py --paragraph 5

# Read by line range (file:start:end format)
uv run python .claude/skills/thesis-sections/tools/read_section.py --lines "chapter1.tex:10:50"
```

## Output

Generates `section_content.txt` (formatted as Markdown) showing:

- **Chapter/section header** with metadata
- **Full text** with preserved structure (commands, sections, citations)
- **Metadata:** word count, citation count, figures referenced

## Use Cases

- Read full chapter without opening file editor
- Extract all paragraphs discussing a specific paper
- Get clean, formatted output ready for analysis
- Understand section context without manually parsing LaTeX
