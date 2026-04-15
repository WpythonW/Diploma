# Thesis Command-Line Tools

Quick wrappers for all thesis analysis, search, and build commands.

## Installation

The PATH is already configured in `.zshrc`. Just use the commands from anywhere in the project:

```bash
find-thesis --pattern "bias"
thesis-structure
thesis-sections --chapter 1
cite-coverage
thesis-stats
sanity-check
check-citations
check-context
build-thesis
```

## Available Commands

All commands are short wrappers that automatically cd to the correct directory and run the underlying Python tool.

| Command | Purpose |
|---------|---------|
| `find-thesis` | Search thesis with patterns, citations, TODOs |
| `thesis-structure` | Map chapters, sections, figures, experiments |
| `thesis-sections` | Read whole sections by chapter or citation |
| `cite-coverage` | Analyze citations — where used, by chapter |
| `thesis-stats` | Word count, citation distribution, coverage % |
| `sanity-check` | Check for broken refs, images, cites |
| `check-citations` | Verify bibliography entries (REAL/FAKE/UNCERTAIN) |
| `check-context` | Verify citation context is accurate |
| `build-thesis` | Compile LaTeX thesis to PDF |

## Examples

```bash
# Search
find-thesis --pattern "bias"
find-thesis --cite "Tversky1974"
find-thesis --todo

# Understand structure
thesis-structure
thesis-structure --figures

# Read sections
thesis-sections --chapter 1
thesis-sections --section "Introduction"

# Citations
cite-coverage
check-citations
check-context

# Stats
thesis-stats
thesis-stats --per-chapter

# Build
build-thesis
```

## Help

Each command has built-in help:

```bash
find-thesis --help
thesis-structure --help
thesis-sections --help
# ... etc
```

For detailed guidance on when to use each command and common workflows, see the **`search-guide`** skill:

```bash
# Load in Claude Code:
# /search-guide
```

Or read directly:
```bash
cat .claude/skills/search-guide/SKILL.md
```
