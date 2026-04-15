---
title: Search Guide
description: Quick reference for searching and analyzing thesis — when to use each tool, examples, and quick commands
---

# Skill: search-guide

## Overview

All thesis search/analysis tools are available as **simple commands** from `.claude/bin/`:

```bash
find-thesis      # Search with context
thesis-structure # Map of chapters, sections, figures
thesis-sections  # Read whole sections
cite-coverage    # Citation analysis
thesis-stats     # Word count, citations, coverage
sanity-check     # Check for broken refs, images, cites
check-citations  # Verify bibliography (REAL/FAKE/UNCERTAIN)
check-context    # Check citation contextual correctness
build-thesis     # Compile LaTeX to PDF
```

These wrappers are short, chainable, and always available from anywhere in the project.

---

## When to Use Each Tool

### 1. **find-thesis** — Search for patterns, citations, TODOs

**Use when:** You need to find specific text, a citation, or TODO notes in the thesis.

**Examples:**
```bash
find-thesis --pattern "bias"              # Find all mentions of "bias"
find-thesis --cite "Tversky1974"          # Find where citation is used
find-thesis --todo                        # Find all TODO/FIXME/XXX
find-thesis --undefined-cite              # Find broken \cite{...} references
find-thesis --pattern "bias" --chapter 2  # Search only Chapter 2
find-thesis --pattern "method" --context 5  # Show 5 lines of context
```

**Output:** Matching lines with file paths and line numbers. Perfect for targeted edits.

---

### 2. **thesis-structure** — Map of entire thesis organization

**Use when:** You need to understand the overall structure, list all chapters/sections/figures.

**Examples:**
```bash
thesis-structure              # Full map
thesis-structure --chapters   # Just chapter list
thesis-structure --figures    # All figures with paths
thesis-structure --sections   # All sections with levels
```

**Output:** Hierarchical map of thesis organization. Use this to understand where things are before deep dives.

---

### 3. **thesis-sections** — Read whole sections

**Use when:** You want to read an entire section (not just snippets).

**Examples:**
```bash
thesis-sections --chapter 1               # Read all of Chapter 1
thesis-sections --chapter 2               # Read Chapter 2 (all experiments)
thesis-sections --section "Introduction"  # Read by section name
thesis-sections --cite "Tversky1974"      # Read section discussing this citation
```

**Output:** Complete section text, formatted for reading. Great for understanding context before editing.

---

### 4. **cite-coverage** — Citation analysis

**Use when:** You need to understand citation distribution, check what's cited where, or find coverage gaps.

**Examples:**
```bash
cite-coverage                 # Full coverage matrix (by chapter)
cite-coverage --chapter 1     # Citations used in Chapter 1 only
cite-coverage --cite "Kahneman1979"  # Where is this citation used?
cite-coverage --missing       # Find chapters with few/no citations
cite-coverage --unused        # Bibliography entries not cited
```

**Output:** Matrix showing citation usage by chapter, status flags (cited/unused/undefined).

---

### 5. **thesis-stats** — Word count, citation distribution, bibliography coverage

**Use when:** You need metrics — how many words, how many citations, coverage %.

**Examples:**
```bash
thesis-stats                  # Full stats (word count, cite count, coverage %)
thesis-stats --per-chapter    # Stats broken down by chapter
thesis-stats --citations      # Just citation stats
```

**Output:** Numbers: total words, total citations, % bibliography coverage, per-chapter breakdown.

---

### 6. **sanity-check** — Broken references, images, citations

**Use when:** You've made structural changes and want to verify nothing is broken.

**Examples:**
```bash
sanity-check                  # Full check
sanity-check --citations      # Check for broken \cite{} references
sanity-check --images         # Check for missing image files
sanity-check --refs           # Check for broken \ref{} references
sanity-check --includes       # Check for missing \input{} files
```

**Output:** List of errors (if any). Empty output = all good.

---

### 7. **check-citations** — Bibliography verification (REAL/FAKE/UNCERTAIN)

**Use when:** You want to verify that citations are real papers (not hallucinated).

**Examples:**
```bash
check-citations               # Verify all bibliography entries
check-citations --chapter 2   # Verify cites used in Chapter 2
check-citations --detailed    # Show what's known about each entry
```

**Output:** Each entry marked as REAL / FAKE / UNCERTAIN with notes. Use before finalizing thesis.

---

### 8. **check-context** — Citation contextual correctness (OK/WARNING/ERROR)

**Use when:** You've cited a paper and want to verify the context is accurate (not stretched/misused).

**Examples:**
```bash
check-context                 # Check all citations
check-context --chapter 2     # Check citations in Chapter 2
check-context --cite "Wason1966"  # Check this citation specifically
```

**Output:** Each cite marked OK / WARNING / ERROR. Warnings = paper is cited correctly but edge cases exist. Errors = cite is wrong or stretched.

---

### 9. **build-thesis** — Compile LaTeX to PDF

**Use when:** You've edited `.tex` files and want to see the compiled PDF.

**Examples:**
```bash
build-thesis                  # Compile main.tex → main.pdf
build-thesis -pvc             # Watch mode (auto-recompile on file change)
```

**Output:** `Diploma_latex/main.pdf` (updated). Check it in your PDF reader.

---

## Quick Decision Tree

**"I need to find X in the thesis"**
- Text pattern? → `find-thesis --pattern "..."`
- Specific citation? → `find-thesis --cite "KEY"`
- TODO notes? → `find-thesis --todo`
- Broken references? → `sanity-check --citations`

**"I need to understand the structure"**
- Overall map? → `thesis-structure`
- All figures? → `thesis-structure --figures`
- Just chapters? → `thesis-structure --chapters`

**"I need to read a section"**
- Full chapter? → `thesis-sections --chapter N`
- By name? → `thesis-sections --section "Name"`
- Around citation? → `thesis-sections --cite "KEY"`

**"I need metrics"**
- Word count / citation count? → `thesis-stats`
- Per-chapter? → `thesis-stats --per-chapter`
- Where is citation X used? → `cite-coverage --cite "KEY"`

**"I need to verify quality"**
- Broken refs/images/includes? → `sanity-check`
- Bibliography entries real? → `check-citations`
- Citations contextually correct? → `check-context`

**"I've edited files"**
- Compile to PDF → `build-thesis`

---

## Combining Commands: Common Workflows

### Workflow 1: Add a new citation
```bash
find-thesis --pattern "topic-you-want-to-cite"  # Find the section
thesis-sections --section "that section"         # Read full context
# [Edit the .tex file with new \cite{KEY}]
check-context --cite "KEY"                       # Verify context is correct
build-thesis                                     # Compile and preview
```

### Workflow 2: Fix broken citations
```bash
sanity-check --citations                         # List broken references
find-thesis --undefined-cite                     # Show which \cite{} are broken
# [Edit or remove broken citations]
check-citations                                  # Verify all entries are real
build-thesis                                     # Compile
```

### Workflow 3: Audit citation coverage
```bash
cite-coverage                                    # Full matrix
cite-coverage --unused                           # What in bib is not cited?
thesis-stats --citations                         # How many citations total?
# [Decide if coverage is adequate]
```

### Workflow 4: Prepare for review
```bash
thesis-stats                                     # Overall metrics
sanity-check                                     # Structural integrity
check-citations                                  # All entries real?
check-context                                    # All contexts correct?
build-thesis                                     # Final PDF
```

---

## Tips for Agents

1. **Start with `thesis-structure`** — orient yourself before deep dives.
2. **Use `find-thesis` for targeted searches** — faster than reading entire chapters.
3. **Combine tools** — use `thesis-structure` → `find-thesis` → `thesis-sections` → edit.
4. **Verify before editing** — use `sanity-check` before and after structural changes.
5. **Always run `build-thesis`** before reporting changes — verify the PDF compiles.
6. **Check bibliography quality** — run `check-citations` + `check-context` before claiming citations are correct.

---

## Command Reference (Quick Copy-Paste)

```bash
# Search
find-thesis --pattern "PATTERN"
find-thesis --cite "KEY"
find-thesis --todo
find-thesis --undefined-cite

# Structure
thesis-structure
thesis-structure --figures

# Read sections
thesis-sections --chapter N
thesis-sections --section "NAME"

# Citations
cite-coverage
cite-coverage --cite "KEY"
cite-coverage --unused
check-citations
check-context

# Stats
thesis-stats
thesis-stats --per-chapter

# Quality
sanity-check
sanity-check --citations
sanity-check --images

# Build
build-thesis
```
