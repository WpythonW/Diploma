# Skill: review_diploma

## Logging (MANDATORY)
Every time I send or receive a long text:
- Before sending: `log_out("destination", text)`
- After receiving: `log_in("source", text)`

Token summary on demand:
```bash
python -c "import sys; sys.path.insert(0,'diploma_agents'); from tools.log_io import print_token_summary; print_token_summary()"
```

---

## My role (Claude = orchestrator)
- I do NOT read the thesis in full
- I do NOT analyze content myself — that's what the proxy model is for
- Short data (headers, keys, numbers) → I read directly
- Long data (paragraphs, Perplexity output) → proxy model

**Proxy model:** `qwen/qwen3-235b-a22b-2507` (only this one)
**Search:** Perplexity `sonar`

---

## Tools

| Script | Purpose | Cost |
|--------|---------|------|
| `perplexity_search.py "query"` | Live web search for papers | ~$0.005/req |
| `openrouter_ask.py --model qwen/qwen3-235b-a22b-2507 --system "..." --user "..."` | Proxy model analysis | ~$0.02/req |
| `check_papers.py` | Async bib verification | ~$1–3 full run |
| `semantic_scholar.py --bib ../../bibliography.bib --check-all` | Free reference lookup | $0 |

---

## Review workflow

### Step 1 — Quick context (I read section headers only)
Grep only `\section`, `\subsection`, `\textbf` from the target chapter.
Build a 10–15 point digest.

### Step 2 — Run tools

**Relevance / novelty check (intro, chapter 1):**
```bash
python tools/perplexity_search.py "cognitive biases LLM conjunction fallacy 2024 2025 papers"
python tools/perplexity_search.py "Wason selection task language models recent research"
```
→ log_in the result, then send to qwen3 to compare against novelty claims from digest

**Proxy model analysis:**
```bash
python tools/openrouter_ask.py \
  --model qwen/qwen3-235b-a22b-2507 \
  --system "You are a critical academic reviewer. Be concise." \
  --user "Novelty claims: [digest]. Recent papers found: [perplexity result].
          Which claims are justified? Which are overstated? Missing citations?"
```

**Bibliography verification:**
```bash
uv run python tools/check_papers.py
```

**Statistics check:**
```bash
python tools/perplexity_search.py "McNemar test paired binary LLM evaluation correct usage"
python tools/openrouter_ask.py --model qwen/qwen3-235b-a22b-2507 \
  --system "You are a statistics expert. Be concise." \
  --user "Is McNemar test correctly applied here: [methodology digest]?"
```

### Step 3 — Final scorecard
```bash
python tools/openrouter_ask.py \
  --model qwen/qwen3-235b-a22b-2507 \
  --system "You are a thesis committee member. Evaluate against all 7 criteria below." \
  --user "[criteria from diploma_criteria.txt] \n\n [aggregated findings]"
```

---

## What I do myself (no tools)
- Read section headers via Grep
- Formulate targeted queries for tools
- Aggregate and interpret short outputs
- Make arbitration decisions

## What I never do
- Read the full thesis
- Analyze long paragraphs myself
- Waste tokens on what costs $0.02 via proxy
