# Project Overview

This repository is a diploma thesis workspace centered on a LaTeX thesis and a small agent/tooling layer used to review the thesis, verify citations, and support academic quality checks.

The repository has two main parts:

- `Diploma_latex/`: the thesis sources in `.tex`. Do not read this folder wholesale. Only inspect narrowly targeted fragments when needed.
- `diploma_agents/`: helper scripts, prompts, and workflows for thesis review, citation verification, web-assisted paper lookup, and logging.

There is also a local Claude skill area:

- `.claude/skills/`: local skills for thesis-related tasks, currently including citation checking.
- All agents and skills for this project must be registered locally inside the repository, not globally in user-level or system-level Claude/Codex directories.

# Hard Rules

- Do not read the entire thesis.
- Do not recursively inspect `Diploma_latex/`.
- Only read small, targeted snippets from LaTeX files when explicitly needed for a focused task.
- Treat `Diploma_latex/` as the source of truth for the diploma text, but not as a folder for broad exploration.
- Keep edits minimal and scoped.
- Register project-specific agents and skills locally in this repository only. Do not install or register them globally.
- Write all skills, agent instructions, and prompts in English.
- Reply to the user in Russian unless the user explicitly requests another language.

# Build Command

Compile the thesis from inside `Diploma_latex/` with:

```bash
latexmk -xelatex -f -interaction=nonstopmode main.tex
```

# Repository Structure

- `Diploma_latex/`
  - Main LaTeX thesis sources.
- `diploma_agents/AGENTS.md`
  - Agent architecture and orchestration rules.
- `diploma_agents/SKILL_review_diploma.md`
  - Workflow for reviewing the diploma against academic criteria.
- `diploma_agents/SKILL_check_citations.md`
  - Workflow for checking bibliography quality and citation correctness.
- `diploma_agents/diploma_criteria.txt`
  - Official evaluation criteria for the diploma.
- `diploma_agents/tools/`
  - `check_papers.py`: async bibliography verification.
  - `openrouter_ask.py`: proxy-model analysis through OpenRouter.
  - `perplexity_search.py`: live search for relevant papers.
  - `semantic_scholar.py`: free reference lookup via Semantic Scholar.
  - `log_io.py`: logging of long prompts and responses.
- `.claude/skills/check-citations/SKILL.md`
  - Local Claude skill for citation-check workflows.

# How To Work In This Project

When helping in this repository:

1. Start from repository-level context and tooling.
2. Avoid broad thesis reading.
3. Use targeted grep, section headers, or narrowly scoped excerpts when thesis context is required.
4. Prefer existing workflows in `diploma_agents/` and `.claude/skills/` over inventing ad hoc processes.
5. Preserve reproducibility and academic traceability.

# Diploma Evaluation Criteria

Any review or improvement task should be aligned with the official diploma criteria documented in `DIPLOMA_CRITERIA.md` at the repository root.

# Agent Workflow Notes

The existing review setup assumes an orchestrator model plus specialized tools:

- Orchestrator reads only short, structured data directly.
- Long thesis passages and long external search results should be delegated to the proxy model.
- Proxy model fixed in project docs: `qwen/qwen3-235b-a22b-2507`.
- Search backend fixed in project docs: Perplexity `sonar`.

If long texts are sent to tools, log them with `diploma_agents/tools/log_io.py` as required by the project’s own workflow docs.

# Useful Commands

Citation verification:

```bash
cd diploma_agents
uv run python tools/check_papers.py
uv run python tools/check_papers.py --test
uv run python tools/check_papers.py --recheck key1 key2 --prompt "Pay extra attention to venue and year"
```

Token usage summary:

```bash
python -c "import sys; sys.path.insert(0,'diploma_agents'); from tools.log_io import print_token_summary; print_token_summary()"
```

# Working Assumption For Future Tasks

This repository is not just a thesis source tree. It is a thesis-plus-review-workbench. The expected mode of work is:

- improve the thesis carefully,
- verify academic claims and citations,
- align the document with the seven diploma criteria,
- keep all work reproducible and review-friendly,
- and avoid unnecessary full-document reading.
