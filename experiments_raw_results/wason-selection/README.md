# Wason Selection Task — Raw Results

> **9 LLMs × 5 content conditions × 3 prompt variants × 5 permutations = up to 15,000 trials**

All values in diploma tables `tab:wst_content1`, `tab:wst_bias`, `tab:wst_prompts` come from this directory.

See **[PROGRESS.md](./PROGRESS.md)** for a complete status matrix of what has been run and what remains.

---

## Quick Navigation

| What you need | Where to find it |
|---|---|
| EMA values for 5 conditions | `output/<condition>/metrics.csv` |
| MBI + CBR for 4 conditions | Same `metrics.csv` files |
| CoT vs Neutral prompt comparison | `output_prompt_cot_answer*/` + `output_prompt_neutral_minimal*/` |
| Per-model raw responses | `output/<condition>/<model>/raw_responses.jsonl` |
| Token usage stats | `output/<condition>/stats.csv` |
| Thesis figures | `output/thesis_graphs/*.png` |

---

## File Structure

```
wason-selection/
├── input/                          # Input datasets (Google Sheet verified)
│   ├── formal_logic.csv            # → output/formal_logic/ (FL Canon in diploma)
│   ├── formal_logic_neutral.csv    # → output/formal_logic_neutral/ (FL Neutral)
│   ├── concrete_facts_extended.csv # → output/concrete_facts_extended/ (Conc Facts)
│   ├── familiar_social_contracts_extended.csv  # → output/familiar_social_contracts_extended/ (Fam Social)
│   └── unfamiliar_fantasy_social_contracts_extended.csv  # → output/unfamiliar_fantasy_social_contracts_extended/ (Unf Fantasy)
│
├── output/                         # MAIN EXPERIMENT RESULTS
│   ├── formal_logic/               # 500 trials/model (100 rules × 5 permutations)
│   │   ├── metrics.csv             # ← EMA/MBI/CBR values used in diploma tab:wst_content1
│   │   └── <model>/                # per-model: raw_responses.jsonl, trial_results.csv, summary.json, stats.csv
│   ├── formal_logic_neutral/       # 500 trials/model (100 rules × 5 permutations)
│   │   └── metrics.csv
│   ├── concrete_facts_extended/    # 505 trials/model (101 rules × 5 permutations)
│   │   └── metrics.csv
│   ├── familiar_social_contracts_extended/  # 500 trials/model (100 rules × 5 permutations)
│   │   └── metrics.csv
│   ├── unfamiliar_fantasy_social_contracts_extended/  # 500 trials/model (100 rules × 5 permutations)
│   │   └── metrics.csv
│   └── thesis_graphs/              # Generated PNG figures for diploma
│       ├── fig_waston_ema_conditions.png
│       ├── fig_waston_ema_heatmap.png
│       ├── fig_waston_context_effects.png
│       ├── fig_waston_cot_delta.png
│       └── fig_waston_ema_vs_consistency.png
│
├── output_prompt_cot_answer/       # CoT prompt experiment (6 open-source models)
│   ├── formal_logic_neutral/       # ← Used in diploma tab:wst_prompts
│   │   └── metrics.csv
│   ├── familiar_social_contracts_extended/
│   ├── concrete_facts_extended/
│   ├── formal_logic/
│   └── unfamiliar_fantasy_social_contracts_extended/
│
├── output_prompt_cot_answer_proprietary/  # CoT prompt (3 proprietary: claude, gpt, grok)
│   ├── formal_logic_neutral/       # ← Used in diploma tab:wst_prompts
│   │   └── metrics.csv
│   ├── familiar_social_contracts_extended/
│   ├── concrete_facts_extended/
│   ├── formal_logic/
│   └── unfamiliar_fantasy_social_contracts_extended/
│
├── output_prompt_neutral_minimal/  # Neutral prompt experiment (6 open-source models)
│   ├── formal_logic_neutral/       # ← Used in diploma tab:wst_prompts
│   │   └── metrics.csv
│   ├── familiar_social_contracts_extended/
│   ├── concrete_facts_extended/
│   ├── formal_logic/
│   └── unfamiliar_fantasy_social_contracts_extended/
│
├── output_prompt_neutral_minimal_proprietary/  # Neutral prompt (3 proprietary)
│   ├── formal_logic_neutral/       # ← Used in diploma tab:wst_prompts
│   │   └── metrics.csv
│   ├── familiar_social_contracts_extended/
│   ├── concrete_facts_extended/
│   ├── formal_logic/
│   └── unfamiliar_fantasy_social_contracts_extended/
│
├── prompt_variants/
│   ├── cot_answer.txt              # CoT prompt text
│   └── neutral_minimal.txt         # Neutral prompt text
│
├── compute_metrics.py              # Script to compute EMA, MBI, CBR, consistency_rate
├── build_graphs.py                 # Script to build result graphs
├── generate_thesis_graphs.py       # Script to build diploma-specific figures
└── config.py                       # Experiment configuration
```

---

## Diploma Table Mapping

| Diploma Table | Data Source |
|---|---|
| `tab:wst_content1` (EMA by 5 conditions) | `output/<condition>/metrics.csv` × 5 dirs |
| `tab:wst_bias` (MBI, CBR by 4 conditions) | `output/<condition>/metrics.csv` (excl. FL Canon) |
| `tab:wst_prompts` (Neutral vs CoT) | `output_prompt_neutral_minimal*/metrics.csv` + `output_prompt_cot_answer*/metrics.csv` |

### Condition Name Mapping

| Diploma abbreviation | Directory | Input dataset | Rules |
|---|---|---|---|
| **FL Canon.** | `output/formal_logic/` | `input/formal_logic.csv` (150 rows) | 100 unique |
| **FL Neutral** | `output/formal_logic_neutral/` | `input/formal_logic_neutral.csv` (100 rows) | 100 |
| **Conc. Facts** | `output/concrete_facts_extended/` | `input/concrete_facts_extended.csv` (101 rows) | 101 |
| **Fam. Social** | `output/familiar_social_contracts_extended/` | `input/familiar_social_contracts_extended.csv` (100 rows) | 100 |
| **Unf. Fantasy** | `output/unfamiliar_fantasy_social_contracts_extended/` | `input/unfamiliar_fantasy_social_contracts_extended.csv` (100 rows) | 100 |

---

## How to Verify

To verify any value in diploma tables, run:
```bash
cat output/<condition>/metrics.csv
```
Each `metrics.csv` contains: `model, EMA, MBI, CBR, consistency_rate`

Per-model raw data is in `output/<condition>/<model>/`:
- `raw_responses.jsonl` — full model responses
- `trial_results.csv` — parsed results per trial
- `summary.json` — per-model summary stats
- `stats.csv` — detailed statistics

---

## Why These Files?

**Included:** All data that matches numerical values in diploma chapter 2 tables. Verified by comparing `metrics.csv` values against diploma table values (tolerance ±0.001).

**Excluded (deleted):**
- `formal_logic_canonical/` — metrics don't match diploma table (0.814 vs 0.907)
- `concrete_facts/` — old version (250 rules), replaced by `concrete_facts_extended` (101)
- `familiar_social_contracts/` — old version (200 rules), replaced by `_extended` (100)
- `unfamiliar_fantasy_social_contracts/` — old version (200 rules), replaced by `_extended` (100)

The `_extended` suffix means "expanded dataset with more diverse rules" — these are the **final** versions used in the diploma. The non-extended versions are older iterations that were replaced.

---

## Known Gaps

### 1. Prompt experiments: Additional conditions not analyzed in diploma

Промпт-эксперименты (Neutral vs CoT) были запущены для **всех 5 контентных условий**, однако в дипломе таблица `tab:wst_prompts` содержит данные только для **FL Neutral**:

- `output_prompt_cot_answer/formal_logic_neutral/` ✅ используется в дипломе
- `output_prompt_neutral_minimal*/formal_logic_neutral/` ✅ используется в дипломе
- `output_prompt_cot_answer/familiar_social_contracts_extended/` ✅ данные есть, но НЕ в дипломе
- `output_prompt_cot_answer/concrete_facts_extended/` ✅ данные есть, но НЕ в дипломе
- `output_prompt_cot_answer/formal_logic/` ✅ данные есть, но НЕ в дипломе
- `output_prompt_cot_answer/unfamiliar_fantasy_social_contracts_extended/` ✅ данные есть, но НЕ в дипломе
- (аналогично для `_proprietary` версий)

Это означает что данные для анализа влияния промптов на других контентных условиях **собраны и доступны**, но не включены в текущую версию диплома.

### 2. Token usage stats not discussed in diploma

Каждое условие имеет файл `stats.csv` с `prompt_tokens`, `completion_tokens`, `reasoning_tokens` на модель. Эти данные собраны, но не обсуждаются в тексте диплома. Могут быть полезны для:
- Оценки стоимости полного эксперимента
- Анализа используют ли reasoning модели больше токенов для сложных условий
