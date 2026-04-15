---
title: Thesis Structure
description: Map of chapters, sections, figures, tables, experiments — understand thesis architecture at a glance
---

# Skill: thesis_structure

Autonomous tool that parses the thesis structure from `main.tex` and generates a comprehensive map.

## Quick Run

```bash
cd /Users/andrejustinov/Desktop/Diploma&research/Diploma
uv run python .claude/skills/thesis-structure/tools/structure.py
```

## Output

Generates `thesis_structure.txt` (human-readable) and `thesis_structure.json` (machine-readable) showing:

- **Chapter order:** which `.tex` files in which order
- **Chapter metadata:**
  - Title/section names
  - Approximate word count
  - Subsections
  - Type (intro, methodology, results, discussion)
- **Figures & Tables:** where they're defined, what they reference
- **Experiments:** which experiments are mentioned in which chapters
- **Cross-references:** `\ref{}`, `\cite{}`, `\label{}`

## Use Cases

- Understand overall thesis structure without reading all files
- Identify which chapters discuss which experiments
- Find figures and check if they're all properly referenced
- Quick chapter map for navigation
