---
title: Thesis Statistics
description: Quick statistics on thesis: word counts, citation distribution, bibliography coverage, unused entries
---

# Skill: thesis_statistics

Autonomous tool that generates a statistical snapshot of the thesis in one run.

## Quick Run

```bash
cd /Users/andrejustinov/Desktop/Diploma&research/Diploma
uv run python .claude/skills/thesis-stats/tools/stats.py
```

## Output

Generates `thesis_stats.txt` (human-readable) and `thesis_stats.json` (machine-readable) with:

- **Total word count** (overall and per-chapter)
- **Total citations** (overall count)
- **Citation density** (cites per 1000 words by chapter)
- **Bibliography coverage:**
  - Keys in `.bib` but NOT used in `.tex` (unused entries)
  - Keys used in `.tex` but NOT in `.bib` (ERROR!)
- **Citation distribution** (number of uses per key)
- **Status integration:** Shows FAKE/ERROR/WARNING keys (from check-citations and check-context results if available)

## Running from Repo Root

**Always run from repo root**, not from within the skill directory:

```bash
cd /Users/andrejustinov/Desktop/Diploma&research/Diploma
uv run python .claude/skills/thesis-stats/tools/stats.py
```

The script auto-discovers `Diploma_latex/` and `bibliography.bib`.
