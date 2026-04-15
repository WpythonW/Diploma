---
title: Project Structure
description: Organizational principles, naming conventions, and project concepts
---

# Skill: project-structure

## General Principles

This is a **thesis-plus-analysis workbench**: a diploma thesis combined with integrated tooling for reviewing, verifying, analyzing, and tracking experiments.

**Key principles:**
- All agents and skills are registered locally in this repository — not global or system-level
- Structure is self-contained and reproducible
- Each component has a clear, focused responsibility
- Naming conventions are consistent and predictable

---

## Directory Organization Concepts

### Thesis Sources: `Diploma_latex/`

All LaTeX sources for the diploma thesis live here:
- Master file: `main.tex`
- Chapter files: `chapter*.tex`, `intro.tex`, `conclusion.tex`
- Bibliography: `bibliography.bib`
- Image configuration: `config-images.tex`
- Output: `main.pdf` (compiled)

**Key rule:** Do not read the entire thesis at once. Use targeted searches via skills instead.

To see the actual contents, run:
```bash
ls -la Diploma_latex/
```

---

### Experiment Data: `experiments_raw_results/`

Raw experimental results from cognitive bias studies with LLMs.

**Structure concept:**
```
experiments_raw_results/
├── common_config.py       # Shared config across ALL experiments
├── RULES.md               # Rules and patterns for experiment work
├── <experiment_1>/        # Each experiment is a self-contained directory
│   ├── config.py          # Experiment-specific configuration
│   ├── PROGRESS.md        # Status matrix (CRITICAL to keep updated)
│   ├── data/              # Input datasets
│   ├── output/            # Results from runs
│   ├── figures/           # Generated plots
│   └── [scripts]          # Python scripts for this experiment
├── <experiment_2>/
└── ...
```

To see actual structure:
```bash
ls -la experiments_raw_results/
tree -L 2 experiments_raw_results/
```

---

## Configuration Concepts

### `common_config.py` — Shared Across All Experiments

Global settings that apply to every experiment:

- **Model lists** — which models are available for testing (gpt-4, claude-3-sonnet, qwen, etc.)
- **API endpoints** — OpenRouter URL, authentication, rate limiting
- **Output paths** — where to save results
- **Common constants** — shared prompt templates, scoring rules, default values

**Example usage:** `from common_config import MODEL_LIST, API_URL, OUTPUT_DIR`

### `config.py` (per experiment) — Experiment-Specific Settings

Each experiment has its own `config.py` with unique settings:

- **Subset of models** — which models to actually run for this experiment
- **Content conditions** — different framings, prompt variants, contexts
- **Dataset configuration** — data source, filtering, size
- **Metrics to compute** — which metrics matter for this specific experiment

**Important:** Experiment-specific `config.py` **can override or extend** `common_config.py`, but doesn't duplicate it.

---

## Experiment Tracking: `PROGRESS.md`

Each experiment has a `PROGRESS.md` file. **CRITICAL to keep updated.**

**Format concept:** Status matrix showing which model + condition combinations are:
- ✓ Done (data generated, metrics computed, figures created)
- 🔄 In progress (running, debugging, or waiting for results)
- ✗ Failed (error logs available)
- ? Planned but not started

**Rule:** Update PROGRESS.md immediately after each run so future sessions know the state.

To view actual PROGRESS files:
```bash
find experiments_raw_results -name PROGRESS.md
```

---

## Skill Organization Concepts

### Naming Convention: Agent Prefix + `__` + Skill Name

Skills that belong to an agent follow the pattern:

```
<agent_name>__<skill_function>
```

**Examples:**
- `build-publish__build-thesis` → Build agent
- `stats-reporter__thesis-stats` → Stats agent
- `thesis-searcher__find-in-thesis` → Searcher agent

**Why?** Makes it immediately clear which agent depends on which skills.

### Standalone Skills

Some skills are **completely independent** and don't belong to any agent:

- `thesis-writing` — Core principles, hard rules, academic integrity
- `experimenter` — Context and rules for LLM cognitive bias experiments
- `check-citations` — Bibliography verification (REAL/FAKE/UNCERTAIN)
- `check-context` — Citation contextual correctness (OK/WARNING/ERROR)

These are loaded on demand and are NOT orchestrated by agents.

---

## Figure Naming Convention

All figures generated from experiment data follow:

```
<experiment_name>_<graph_name>.png
```

Where:
- `<experiment_name>`: short experiment ID (`linda`, `wason`, `wason246`, etc.)
- `<graph_name>`: descriptive name in snake_case

**Examples:**
- `linda_delta_bias_bar.png`
- `linda_accuracy_by_condition.png`
- `wason_response_rates_by_condition.png`
- `wason246_rule_discovery_heatmap.png`

**Storage:** All figures live in `experiments_raw_results/<experiment_name>/figures/`

**Rule:** This naming makes it easy to:
- Find all figures for an experiment (`ls linda_*.png`)
- Understand what each figure shows (name is descriptive)
- Organize figures in the thesis by experiment

---

## Viewing Project Structure

To see the actual layout at any time:

```bash
# Root level
ls -la

# Thesis sources
ls -la Diploma_latex/

# Skills and agents
ls -la .claude/skills/
ls -la .claude/agents/

# Experiment data
ls -la experiments_raw_results/
tree -L 3 experiments_raw_results/

# Or full repo overview
tree -L 3 -I '__pycache__|*.pyc|.git'
```

---

## Key Rules Summary

1. **Thesis is read-targeted** — use skills for searches, don't browse entire thesis
2. **Configs are hierarchical** — `common_config.py` is global, `config.py` is per-experiment
3. **Skills are named predictably** — `<agent>__<skill>` makes dependencies clear
4. **Figures follow strict naming** — `<experiment>_<graph>.png` is the only acceptable pattern
5. **PROGRESS.md is critical** — update it after every run so the next session knows the state
6. **Structure is discoverable** — use `ls`, `tree`, and `find` to explore; don't hardcode paths

---

## Diploma Evaluation Criteria

For any review or improvement task, align with official criteria in `DIPLOMA_CRITERIA.md` at the repository root.
