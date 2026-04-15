---
title: Citation Coverage
description: Analyze which citations are used where, show FAKE/ERROR/WARNING status per chapter
---

# Skill: cite_coverage

Autonomous tool that analyzes citation usage across chapters and integrates quality verdicts.

## Quick Run

```bash
cd /Users/andrejustinov/Desktop/Diploma&research/Diploma
uv run python .claude/skills/cite-coverage/tools/coverage.py
```

## Output

Generates `cite_coverage.txt` (human-readable) and `cite_coverage.json` with:

- **Per-chapter citation list:**
  - Which keys are cited in each chapter
  - How many times each key is used
- **Citation quality status:**
  - REAL / FAKE / UNCERTAIN (from `check-citations`)
  - OK / WARNING / ERROR (from `check-context`)
  - Combined verdict
- **Coverage table:**
  - Key | Verdict | Chapters | Usage Count

## Integrates With

- `check-citations` — checks if papers exist
- `check-context` — checks if citations are used correctly

If both tools have been run, this shows unified verdict. Otherwise shows what's available.

## Use Cases

- Which chapters have FAKE citations?
- Which keys are over-cited (5+ uses)?
- Which keys are under-cited (only 1 use)?
- Quick audit of citation quality across thesis
