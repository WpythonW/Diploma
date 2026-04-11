# Diploma Review System

## Architecture

**Orchestrator** = Claude (me).
- I read only short data: keys, numbers, verdict/confidence, section headers
- Long texts (thesis paragraphs, Perplexity responses) → delegated to proxy model
- I decide: which tool to call, when to stop, when to recheck with a new prompt

**Proxy model** = `qwen/qwen3-235b-a22b-2507` (this one only, no substitutes)
- Reads thesis paragraphs and Perplexity responses
- Checks whether citation context matches the actual paper meaning
- Issues verdict on disputed cases

**Tools** = scripts in `tools/`. API clients, not processes.

```
Claude (orchestrator)
    │
    ├── tools/perplexity_search.py   → live web search for papers
    ├── tools/openrouter_ask.py      → proxy model analysis (qwen3-235b)
    ├── tools/check_papers.py        → async bib verification agent
    ├── tools/semantic_scholar.py    → free reference lookup
    └── tools/log_io.py              → orchestrator I/O logging
```

## Tools

### perplexity_search.py
```bash
python tools/perplexity_search.py "cognitive biases LLM 2024 papers"
```
Uses: Perplexity `sonar` (~$0.005/request, live web search)

### openrouter_ask.py
```bash
python tools/openrouter_ask.py --model qwen/qwen3-235b-a22b-2507 --system "..." --user "..."
```
**Proxy model: always `qwen/qwen3-235b-a22b-2507`. No other model.**

### check_papers.py
```bash
uv run python tools/check_papers.py                  # full run
uv run python tools/check_papers.py --test           # 5 entries, verbose
uv run python tools/check_papers.py --recheck k1 k2 --prompt "..." --hints k1:"..." k2:"..."
```
Async agent: qwen3-235b + Perplexity. Cache in `tools/.cache/`.

### semantic_scholar.py
```bash
python tools/semantic_scholar.py --bib bibliography.bib --check-all
python tools/semantic_scholar.py "Extensional versus intuitive reasoning" 1983
```
Uses: Semantic Scholar API (free, no key needed)

### log_io.py
```python
from tools.log_io import log_in, log_out, print_token_summary
log_out("openrouter_ask prompt", prompt_text)
log_in("openrouter_ask result", result_text)
```
Logs orchestrator I/O to `tools/orchestrator_io.log` (JSONL).
```bash
# Token usage summary:
python -c "import sys; sys.path.insert(0,'diploma_agents'); from tools.log_io import print_token_summary; print_token_summary()"
```

## Keys
Copy `.env.example` → `.env` and fill in:
```
PERPLEXITY_API_KEY=pplx-...
OPENROUTER_API_KEY=sk-or-...
```

## Logging rule
Every time I (Claude) send or receive a long text — I log it via `log_io.py`.
On request "how many tokens did you use" — I run `print_token_summary()` and report.

## Skills
- Thesis review: `SKILL_review_diploma.md`
- Citation checking: `SKILL_check_citations.md`
