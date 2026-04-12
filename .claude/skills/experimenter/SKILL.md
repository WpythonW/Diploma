---
title: Experimenter
description: Context and rules for working with LLM cognitive bias experiments in this project
---

# Skill: experimenter

## Purpose

This skill loads when the user wants to discuss, plan, run, or analyze experiments. It provides orientation about where experiments live, how to track progress, and the one rule that matters most.

---

## Where Experiments Live

All experiments are in `experiments_raw_results/`:

```
experiments_raw_results/
├── linda-problem/          # Experiment 1: Linda problem (conjunction fallacy)
├── wason-selection/        # Experiment 2: Wason Selection Task — most mature
│   ├── input/              # CSV datasets (one per content condition)
│   ├── output/             # Baseline (Original prompt) results — 5 conditions, all done
│   ├── output_prompt_cot_answer/             # CoT prompt — open models
│   ├── output_prompt_cot_answer_proprietary/ # CoT prompt — proprietary models
│   ├── output_prompt_neutral_minimal/        # Neutral prompt — open models
│   ├── output_prompt_neutral_minimal_proprietary/ # Neutral prompt — proprietary models
│   ├── PROGRESS.md         # ← authoritative status matrix (keep it updated!)
│   └── README.md           # Full documentation
└── wason-2-4-6/            # Experiment 3: Rule discovery / 2-4-6 task
```

Each experiment directory has its own `README.md` (or TODO if not yet written) and a `PROGRESS.md` where applicable.

---

## The One Rule: Update PROGRESS.md

**Whenever something gets done — update `PROGRESS.md` immediately.**

`PROGRESS.md` is the single source of truth for what's done and what remains. It must be crystal-clear at a glance. After any completed run:

1. Mark the corresponding cell ✅ in the status matrix.
2. Update the "Done" count (e.g. `Done: 8/15 cells`).
3. Move the entry from the **Remaining** table to the **Done** table.
4. If output dirs differ from what was proposed, correct them.

Never leave PROGRESS.md stale. It exists so that anyone (including future-Claude) can read it and know exactly what remains without re-checking the filesystem.

---

## How to Run Wason Selection Experiments

The canonical model lists live in `experiments_raw_results/wason-selection/config.py` — always read them from there, never hardcode here.

```bash
cd experiments_raw_results/wason-selection/

# Template:
python3 run_experiments.py --models <models from config.py> \
  --contexts <condition_dir> \
  --system-prompt-file prompt_variants/<prompt>.txt \
  --output-dir <output_dir>/<condition_dir>
```

Content condition dirs: `formal_logic`, `formal_logic_neutral`, `concrete_facts_extended`, `familiar_social_contracts_extended`, `unfamiliar_fantasy_social_contracts_extended`

Prompt files: `prompt_variants/cot_answer.txt`, `prompt_variants/neutral_minimal.txt`

---

## Current Status Snapshot (as of 2026-04-12)

See `experiments_raw_results/wason-selection/PROGRESS.md` for the live matrix.

**Wason Selection:** 7/15 cells done. All 5 conditions done with Original prompt. Only FL Neutral done for Neutral and CoT prompts. 8 cells (16 sub-runs) remain — all are prompt variants on non-FL-Neutral conditions. Not blocking for defense; adds prompt × content interaction analysis.

**Linda problem:** Raw results exist, README TODO.

**Wason 2-4-6:** Raw results exist, README TODO.
