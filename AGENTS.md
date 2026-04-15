# Project Overview

This repository is a **thesis-plus-analysis workbench**: a diploma thesis (`Diploma_latex/`) combined with an integrated skill/tooling layer for reviewing content, verifying citations, analyzing structure, and tracking experiments.

All agents and skills for this project are registered locally in this repository only.

---

## Composite Agents (Orchestration Layer)

These agents combine multiple skills into focused, autonomous workflows:

| Agent | Purpose | When to Use | Calls |
|-------|---------|------------|-------|
| **`build-publish`** | Compile LaTeX → commit → push to GitHub | After making significant changes | (built-in) + git |
| **`stats-reporter`** | Generate concise thesis analytics report | On demand for metrics/overview | stats-reporter__* skills |
| **`thesis-searcher`** | Intelligent search + quotation from thesis | When you need to find or cite something | thesis-searcher__* skills |

**Note:** These agents clean up your main context by handling tool orchestration internally. You get one consolidated report instead of juggling multiple skill outputs.

---

## Standalone Commands

**`sanity-check`** — Structural validation (no agent needed)
- Checks: broken images, citations, references, includes, empty sections, TODO markers, unused files
- Run: `sanity-check` or `./.claude/bin/sanity-check`
- Output: `sanity_report.txt` (errors only), `sanity_report.json` (full results)
- Exit codes: 0 = pass, 1 = fail, 2 = error
- **Independent** — does NOT integrate with check-citations or check-context (those are separate skills)
- Implementation: `.claude/src/sanity_check.py`

---

## Where Everything Lives: `.claude/` Directory

All thesis tools, automation, and helpers are organized in `.claude/`:

```
.claude/
├── bin/                           # Executable wrappers (bash scripts)
│   ├── find-thesis
│   ├── thesis-structure
│   ├── thesis-stats
│   ├── sanity-check
│   └── ... (other command wrappers)
│
├── src/                           # Global utility scripts
│   ├── sanity_check.py            # Structural validation (broken refs, images, etc.)
│   └── checks.py                  # Individual check modules
│
├── skills/                        # Autonomous skill modules
│   ├── thesis-writing/            # Core thesis rules, hard requirements
│   ├── project-structure/         # Org principles, naming conventions, concepts
│   ├── search-guide/              # Decision tree for all search commands
│   ├── stats-reporter__thesis-stats/       # Word count & citation metrics
│   ├── stats-reporter__thesis-structure/   # Chapter/section/figure map
│   ├── stats-reporter__cite-coverage/      # Citation usage analysis
│   ├── thesis-searcher__find-in-thesis/    # Full-text search with context
│   ├── thesis-searcher__thesis-sections/   # Read chapter/citation/line ranges
│   ├── check-citations/           # Bibliography verification (STANDALONE)
│   ├── check-context/             # Citation contextual correctness (STANDALONE)
│   └── experimenter/              # Experiment tracking rules (STANDALONE)
│
└── projects/                      # Project-specific metadata
    └── [project-id]/
        └── memory/                # Persistent memory for sessions
```

**Each skill folder** contains:
- `SKILL.md` — Skill documentation and usage
- `tools/` — Python scripts that do the actual work
- Optional: data files, results, caches

**Note:** All skills are **autonomous** (no chaining between them) and can be invoked with `/skill-name` or via the command wrappers in `.claude/bin/`.

---

**For detailed information, load one of these core skills:**
- **`thesis-writing`** — Core principles, goals, and hard rules for maintaining academic integrity
- **`project-structure`** — Organizational principles, naming conventions (agents, skills, figures), config patterns
- **`search-guide`** — Quick reference for all search/analysis commands with decision tree and examples
- **`experimenter`** — Context and rules for LLM cognitive bias experiments

---

## Quick Reference: Skills by Category

### Core Thesis Rules (Reference)
- `thesis-writing` — Thesis goals, hard rules, academic integrity
- `project-structure` — Repository layout, config patterns, directory organization

### Build & Publish Agent
(LaTeX compilation commands embedded in agent)

### Statistics & Analysis Agent
- `stats-reporter__thesis-stats` — Word count, citation metrics, bibliography coverage
- `stats-reporter__thesis-structure` — Chapters, sections, figures, experiments map
- `stats-reporter__cite-coverage` — Citation usage patterns, per-chapter status

### Search & Quotation Agent
- `thesis-searcher__find-in-thesis` — Full-text search with context (patterns, cites, TODOs)
- `thesis-searcher__thesis-sections` — Read whole sections by chapter or citation key

### Standalone Tools & References
- `search-guide` — Quick reference for all search commands, examples, workflows
- `sanity-check` — Broken images, citations, references, includes (command-line tool)
- `check-citations` — Bibliography verification (REAL/FAKE/UNCERTAIN) — **STANDALONE**
- `check-context` — Citation contextual correctness (OK/WARNING/ERROR) — **STANDALONE**
- `experimenter` — Experiment tracking, PROGRESS.md rules — **STANDALONE**

---

# Key References

- **`DIPLOMA_CRITERIA.md`** — Official evaluation criteria (6 criteria + 4-chapter structure + 11 required thesis elements)
- **`.claude/skills/thesis-writing/`** — How to write the thesis (goals, rules, workflow)
- **`.claude/skills/project-structure/`** — Repository layout and tools

---

# Figure Naming Convention

All figures generated from experiment data **must** follow the naming pattern:

```
<experiment_name>_<graph_name>.png
```

Where:
- `<experiment_name>` is the short experiment ID: `linda`, `wason`, `wason246`, etc.
- `<graph_name>` is a descriptive name using snake_case: `delta_bias_bar`, `accuracy_vs_bias`, `confidence_violin`, `race_fallacy`, `effect_sizes_forest`, `accuracy_by_condition`, `error_distribution`, etc.

**Examples:**
- `linda_delta_bias_bar.png`
- `linda_accuracy_by_condition.png`
- `linda_error_distribution_stack.png`
- `wason_response_rates_by_condition.png`
- `wason246_rule_discovery_heatmap.png`

All figures are stored in `experiments_raw_results/<experiment_name>/figures/`.

---

# How to Use Composite Agents

All composite agents live in `.claude/agents/` and can be invoked by the main Claude session:

```bash
# Build and publish thesis
/build-publish "Added Linda experiment analysis, fixed citations"

# Generate statistics report
/stats-reporter

# Search thesis and extract quotes
/thesis-searcher "What does the thesis say about conjunction fallacy?"
```

Each agent:
- Runs independently with its own context window
- Returns a consolidated report (no intermediate noise)
- Has full access to all thesis tools (except destructive commands)
- Uses Haiku model for speed

---

## Command-Line Tools

For quick structural validation, use the standalone command:

```bash
# Run structural sanity checks
sanity-check
```

This is deterministic (no agent overhead) and outputs pass/fail with a report.

---

# Diploma Evaluation Criteria

Any review or improvement task should be aligned with the official diploma criteria documented in `DIPLOMA_CRITERIA.md` at the repository root.
