---
title: Find in Thesis
description: Search thesis with context — find patterns, citations, TODOs, undefined references
---

# Skill: find_in_thesis

Autonomous search tool that finds patterns, citations, and issues in the thesis with surrounding context.

## Commands

All from repo root:

```bash
# Search for a pattern with context
uv run python .claude/skills/find-in-thesis/tools/find.py --pattern "bias" --context 10

# Find all uses of a specific citation key
uv run python .claude/skills/find-in-thesis/tools/find.py --cite "kahneman2011"

# Find all TODOs, FIXMEs, XXXs, PLACEHOLDERs
uv run python .claude/skills/find-in-thesis/tools/find.py --todo

# Find citations used in .tex but not in .bib
uv run python .claude/skills/find-in-thesis/tools/find.py --undefined-cite

# Find all matches in a specific chapter
uv run python .claude/skills/find-in-thesis/tools/find.py --pattern "conjunction fallacy" --chapter 1
```

## Output

Generates `find_results.json` with:

```json
{
  "matches": [
    {
      "file": "chapter1.tex",
      "line": 42,
      "matched_text": "the actual matched text",
      "context_before": "...",
      "context_after": "...",
      "full_line": "..."
    }
  ],
  "total": 5,
  "query": "pattern searched"
}
```

Also prints results to stdout in readable format.

## Use Cases

- **Find all citations of a key:** `--cite kahneman2011` → all uses with line numbers
- **Find unfinished work:** `--todo` → all marked TODOs in thesis
- **Check for undefined refs:** `--undefined-cite` → catch citation errors
- **Search by topic:** `--pattern "conjunction fallacy"` → all mentions with context
