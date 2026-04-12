---
title: Check Contextual Correctness of Citations
description: Verify that each citation in the diploma thesis is used in a contextually appropriate way — checks whether the thesis paragraph correctly represents the cited paper's content, using Qwen3-235b with full-text cross-validation via arXiv/Tavily
---

# Skill: check_contextual_correctness

## On Load (DO THIS FIRST, IMMEDIATELY)

When this skill is activated, output this question and stop:

> Скилл загружен. Что запустить?
> - `full` — проверить все статьи из papers_cards/
> - `partial key1 key2 ...` — проверить конкретные ключи
> - `recheck` — перезапустить L2 для всех WARNING/ERROR
> - `errors-only` — показать текущие ERROR/WARNING из context_check_results/

Do NOT proceed past this point until the user replies.

---

## What this skill does

For each bibliography key:

1. **Layer 1** — fast check (card + thesis paragraphs → Qwen):
   - Finds all `\cite{key}` paragraphs across all `.tex` files
   - Sends paper card + paragraphs to Qwen3-235b
   - Returns per-paragraph verdict: `OK` / `WARNING` / `ERROR`

2. **Layer 2** — deep cross-check (WARNING/ERROR only):
   - Downloads full paper text **once** via arXiv HTML or Tavily extract
   - Caches in `papers_fulltext/<key>.txt` — never downloads twice
   - Re-checks flagged paragraphs with full text
   - **Mandatory verbatim quotes** from the paper for every non-OK verdict

**Verdict definitions:**
- `OK` — citation is relevant and correctly used
- `WARNING` — tangentially relevant, potentially imprecise or overgeneralised
- `ERROR` — irrelevant, or thesis claim directly contradicts the paper

---

## Working Directory

All commands run from the **repo root** (`Diploma/`):

```bash
cd "/Users/andrejustinov/Desktop/Diploma&research/Diploma"
```

---

## Commands

```bash
# Full run — all keys in papers_cards/
uv run python .claude/skills/check-context/tools/check_contextual_correctness.py

# Specific keys
uv run python .claude/skills/check-context/tools/check_contextual_correctness.py \
  --keys binz2023using wei2022chain kahneman2011thinking

# Force L2 re-check (re-downloads full text, re-runs LLM)
uv run python .claude/skills/check-context/tools/check_contextual_correctness.py \
  --keys binz2023using --recheck

# Custom output directory
uv run python .claude/skills/check-context/tools/check_contextual_correctness.py \
  --out custom_results/
```

---

## Output

- `context_check_results/<key>.json` — per-key verdict with per-mention breakdown
- `papers_fulltext/<key>.txt` — cached full paper text (L2 only)

### Result JSON structure

```json
{
  "key": "binz2023using",
  "overall": "ERROR",
  "layer": 2,
  "fulltext_available": true,
  "mention_count": 8,
  "mentions": [
    {
      "file": "chapter1.tex",
      "snippet": "<first 120 chars of paragraph>",
      "verdict": "ERROR",
      "comment": "Объяснение на русском",
      "paper_quote": "Verbatim quote from the paper that proves the verdict"
    }
  ],
  "summary": "Итоговый вывод на русском, 2-4 предложения."
}
```

---

## My role (Claude = orchestrator)

- I do NOT read thesis paragraphs myself — delegated to Qwen
- I read only short structured data: verdicts, counts, key names
- Long data (full paper text, thesis paragraphs) → handled by the script

**Proxy model:** `qwen/qwen3-235b-a22b-2507` via OpenRouter  
**Full-text source:** arXiv HTML → Tavily extract → Tavily search (fallback chain)

---

## Workflow

### Step 1 — Run full check
```bash
uv run python .claude/skills/check-context/tools/check_contextual_correctness.py
```

### Step 2 — Read summary (I read directly — short data)
```bash
python3 -c "
import json
from pathlib import Path
d = Path('.claude/skills/check-context/tools/context_check_results')
for p in sorted(d.glob('*.json')):
    r = json.loads(p.read_text())
    if r.get('overall') in ('WARNING','ERROR'):
        print(r['overall'], p.stem, '-', r.get('summary','')[:80])
"
```

### Step 3 — Deep-check WARNING/ERROR with L2
```bash
uv run python .claude/skills/check-context/tools/check_contextual_correctness.py \
  --keys key1 key2 --recheck
```

### Step 4 — Report findings to user
For each ERROR: explain what the thesis claims vs. what the paper actually says (use `paper_quote` field).

---

## Cost estimate

| Operation | ~Cost |
|-----------|-------|
| Full run, 46 keys, L1 only | ~$0.30–0.60 |
| L2 for 4 ERROR keys | ~$0.20–0.40 |
| L2 for all 17 WARNING keys | ~$0.80–1.50 |
