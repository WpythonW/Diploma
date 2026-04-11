# Skill: check_citations

## Logging (MANDATORY)
Every time I send or receive a long text:
- Before sending to tool: `log_out("tool_name prompt", text)`
- After receiving result: `log_in("tool_name result", text)`

Log file: `tools/orchestrator_io.log` (JSONL)

Token usage summary on demand:
```bash
python -c "import sys; sys.path.insert(0,'diploma_agents'); from tools.log_io import print_token_summary; print_token_summary()"
```

---

## My role (Claude = orchestrator)
- I do NOT read the thesis myself
- I do NOT analyze papers myself
- Short data (keys, verdict, confidence, line numbers) → I read directly
- Long data (thesis paragraphs, Perplexity responses) → delegated to qwen3-235b

**Proxy model:** `qwen/qwen3-235b-a22b-2507` via OpenRouter
**Search:** Perplexity `sonar`

---

## Workflow

### Step 1 — Run full verification
```bash
cd diploma_agents
uv run python tools/check_papers.py          # full run (cached entries skipped)
uv run python tools/check_papers.py --test   # quick test, 5 entries, verbose
```
Output: `tools/papers_results.json`

### Step 2 — I read the summary (short data, I read directly)
Read `papers_results.json`, select:
- `verdict == "FAKE"` → must recheck
- `verdict == "UNCERTAIN"` and `confidence < 70` → recheck with new prompt

### Step 3 — Recheck disputed entries (async batch)

One shared prompt + per-key hints:
```bash
uv run python tools/check_papers.py \
  --recheck key1 key2 key3 \
  --prompt "Pay extra attention to publication venue and year accuracy" \
  --hints key1:"may be a book chapter, not journal" key2:"check arXiv:2401.XXXXX"
```
- Cache invalidated only for listed keys
- All listed keys run in parallel

### Step 4 — Context analysis for FAKE/UNCERTAIN entries

For each suspicious paper:

1. **Grep** — find where the citation is used:
```bash
grep -n "key1\|key2" ../intro.tex ../chapter1.tex ../chapter2.tex ../chapter3.tex ../chapter4.tex
```

2. **Read** — read ±10 lines around the citation (short, I read directly)

3. **log_out** the prompt, then **openrouter_ask.py** — send paragraph + paper info to qwen3:
```bash
python tools/openrouter_ask.py \
  --model qwen/qwen3-235b-a22b-2507 \
  --system "You are a citation fact-checker. Be concise." \
  --user "
PAPER (from bib):
[description]

VERDICT: FAKE/UNCERTAIN — [reason from results.json]

USED IN THESIS AS:
[paragraph from .tex]

Does the citation context match the actual paper content?
Any signs of hallucination or misattribution?
Verdict: OK / SUSPICIOUS / WRONG + short explanation.
"
```
4. **log_in** the result.

### Step 5 — Arbitration (I decide)
After receiving qwen3 verdicts:
- `WRONG` → flag as error, write fix recommendation
- `SUSPICIOUS` → rerun `--recheck` with a more targeted `--prompt`
- `OK` → clear suspicion, record in final report

---

## Example calls

```bash
# Quick test:
uv run python tools/check_papers.py --test

# Recheck 3 entries, shared prompt:
uv run python tools/check_papers.py \
  --recheck banatt2024wilt suri2024large shafiei2025more \
  --prompt "These may be preprints. Search arXiv carefully."

# Recheck with per-key hints:
uv run python tools/check_papers.py \
  --recheck banatt2024wilt macmillan2024irrationality \
  --hints banatt2024wilt:"look for 'Wilt' paper about rule discovery tasks" \
          macmillan2024irrationality:"Macmillan-Scott and Musolesi, check Nature/AI journals"
```

---

## Cost estimate
| Operation | Model | ~Cost |
|-----------|-------|-------|
| Full run (~40 papers) | qwen3-235b + sonar | ~$1–3 |
| Recheck 5 papers | qwen3-235b + sonar | ~$0.15–0.50 |
| Context check 1 paragraph | qwen3-235b | ~$0.02 |
| Recheck with new prompt | qwen3-235b + sonar | ~$0.05–0.15 |
