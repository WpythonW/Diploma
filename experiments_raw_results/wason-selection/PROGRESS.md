# Wason Selection Task — Progress

> **9 LLMs × 5 content conditions × 3 prompt variants × 5 permutations**

---

## Axes

| Axis | Values | Count |
|------|--------|-------|
| **Content** | FL Canon, FL Neutral, Conc Facts, Fam Social, Unf Fantasy | 5 |
| **Prompt** | Original (baseline), Neutral, CoT | 3 |
| **Model group** | Proprietary (3), Open (6) | 2 |
| **Permutations** | card orderings per rule | 5 |

**Full grid:** 5 × 3 × 2 = **30 cells** (each = 500 trials)
**Grand total when complete:** 15,000 trials

---

## Status Matrix: Content × Prompt

Each cell = both model groups done (proprietary + open).

| Content \ Prompt | Original | Neutral | CoT |
|---|:---:|:---:|:---:|
| **FL Canon** | ✅ | ✅ | ✅ |
| **FL Neutral** | ✅ | ✅ | ✅ |
| **Conc Facts** | ✅ | ✅ | ✅ |
| **Fam Social** | ✅ | ✅ | ✅ |
| **Unf Fantasy** | ✅ | ✅ | ✅ |



**Done: 15/15 cells** ✅ (Original: 5/5, Neutral: 5/5, CoT: 5/5)
**Remaining: 0/15 cells**

---

## Done (8 cells → 16 sub-runs)

| # | Content | Prompt | Models | Output Dir |
|---|---------|--------|--------|------------|
| 1 | FL Canon | Original | Proprietary | `output/formal_logic/` |
| 2 | FL Canon | Original | Open | `output/formal_logic/` |
| 3 | FL Neutral | Original | Proprietary | `output/formal_logic_neutral/` |
| 4 | FL Neutral | Original | Open | `output/formal_logic_neutral/` |
| 5 | Conc Facts | Original | Proprietary | `output/concrete_facts_extended/` |
| 6 | Conc Facts | Original | Open | `output/concrete_facts_extended/` |
| 7 | Fam Social | Original | Proprietary | `output/familiar_social_contracts_extended/` |
| 8 | Fam Social | Original | Open | `output/familiar_social_contracts_extended/` |
| 9 | Unf Fantasy | Original | Proprietary | `output/unfamiliar_fantasy_social_contracts_extended/` |
| 10 | Unf Fantasy | Original | Open | `output/unfamiliar_fantasy_social_contracts_extended/` |
| 11 | FL Neutral | Neutral | Proprietary | `output_prompt_neutral_minimal_proprietary/` |
| 12 | FL Neutral | Neutral | Open | `output_prompt_neutral_minimal/` |
| 13 | FL Neutral | CoT | Proprietary | `output_prompt_cot_answer_proprietary/` |
| 14 | FL Neutral | CoT | Open | `output_prompt_cot_answer/` |
| 15 | FL Canon | Neutral | Proprietary | `output_prompt_neutral_minimal_proprietary/formal_logic/` |
| 16 | FL Canon | Neutral | Open | `output_prompt_neutral_minimal/formal_logic/` |
| 17 | FL Canon | CoT | Proprietary | `output_prompt_cot_answer_proprietary/formal_logic/` |
| 18 | FL Canon | CoT | Open | `output_prompt_cot_answer/formal_logic/` |
| 19 | Conc Facts | Neutral | Proprietary | `output_prompt_neutral_minimal_proprietary/concrete_facts_extended/` |
| 20 | Conc Facts | Neutral | Open | `output_prompt_neutral_minimal/concrete_facts_extended/` |
| 21 | Conc Facts | CoT | Proprietary | `output_prompt_cot_answer_proprietary/concrete_facts_extended/` |
| 22 | Conc Facts | CoT | Open | `output_prompt_cot_answer/concrete_facts_extended/` |
| 23 | Fam Social | Neutral | Proprietary | `output_prompt_neutral_minimal_proprietary/familiar_social_contracts_extended/` |
| 24 | Fam Social | Neutral | Open | `output_prompt_neutral_minimal/familiar_social_contracts_extended/` |
| 25 | Fam Social | CoT | Proprietary | `output_prompt_cot_answer_proprietary/familiar_social_contracts_extended/` |
| 26 | Fam Social | CoT | Open | `output_prompt_cot_answer/familiar_social_contracts_extended/` |
| 27 | Unf Fantasy | Neutral | Proprietary | `output_prompt_neutral_minimal_proprietary/unfamiliar_fantasy_social_contracts_extended/` |
| 28 | Unf Fantasy | Neutral | Open | `output_prompt_neutral_minimal/unfamiliar_fantasy_social_contracts_extended/` |
| 29 | Unf Fantasy | CoT | Proprietary | `output_prompt_cot_answer_proprietary/unfamiliar_fantasy_social_contracts_extended/` |
| 30 | Unf Fantasy | CoT | Open | `output_prompt_cot_answer/unfamiliar_fantasy_social_contracts_extended/` |

## Remaining

**All cells complete! 🎉**

---

## How to Run

```bash
cd experiments_raw_results/wason-selection/

# Proprietary models
PROPS="anthropic/claude-sonnet-4.6 x-ai/grok-4.1-fast openai/gpt-5.2"
# Open models
OPENS="qwen/qwen3.5-397b-a17b z-ai/glm-4.7-flash qwen/qwen3-next-80b-a3b-instruct google/gemma-3-27b-it deepseek/deepseek-v3.2 google/gemma-3-12b-it"

# Example: CoT on concrete_facts_extended — Proprietary
python3 run_experiments.py --models $PROPS \
  --contexts concrete_facts_extended \
  --system-prompt-file prompt_variants/cot_answer.txt \
  --output-dir output_prompt_cot_answer_proprietary/concrete_facts_extended

# Example: Neutral on concrete_facts_extended — Open
python3 run_experiments.py --models $OPENS \
  --contexts concrete_facts_extended \
  --system-prompt-file prompt_variants/neutral_minimal.txt \
  --output-dir output_prompt_neutral_minimal/concrete_facts_extended
```

Repeat for each remaining cell (16 total).

---

## Diploma Impact

**Current diploma uses:** 7 done cells (Original × 5 conditions + Neutral/CoT × FL Neutral).
**All tables are complete** with existing data.

The remaining 16 sub-runs would add **prompt × content interaction analysis** — showing whether CoT helps/harms equally across all content types, not just FL Neutral. This strengthens the paper but is **NOT blocking for defense**.
