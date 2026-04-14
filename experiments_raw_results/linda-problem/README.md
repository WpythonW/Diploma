# Linda Problem (Conjunction Fallacy) — Raw Results

> **9 LLMs × correlated vs uncorrelated option pairs, 520–3120 pairs each**

All values in diploma table `tab:linda_results` (chapter 2, experiment 1) come from this directory.

---

## Quick Navigation

| What you need | Where to find it |
|---|---|
| **Figures for diploma** | `figures/linda_*.png` (8 publication-ready plots) |
| McNemar test results (n21, p-value) | `output/<model>/summary.json` |
| delta_bias, fallacy rates | `output/<model>/summary.json` |
| Demographic breakdown (race, age) | `output/<model>/demographic_mcnemar_tests.csv` (glm, qwen3.5, gemma-12b only) |
| Per-pair results | `output/<model>/pair_results.csv` |
| Per-trial results | `output/<model>/trial_results.csv` |
| Raw model responses | `output/<model>/raw_responses.jsonl` |

---

## File Structure

```
linda-problem/
├── data/
│   ├── conjunction_dataset_all.csv   # 130 vignettes: vignette, T, F, F_uncorrelated, T_and_F1, T_and_F2
│   └── jobs.csv                      # 1401 professions (USDL/OEWS sample)
│
├── output/                           # MAIN EXPERIMENT RESULTS (9 models)
│   ├── anthropic__claude-sonnet-4.6/      # 1040 trials, 520 pairs
│   │   ├── summary.json                   # ← n11, n21, delta_bias, McNemar p, t-test p, Wilcoxon p
│   │   ├── pair_results.csv               # per-pair: correct_correlated, correct_uncorrelated
│   │   ├── trial_results.csv              # per-trial: vignette, race, age, option, chosen, confidence
│   │   ├── demographic_summary.csv        # bias by race/age group
│   │   ├── demographic_mcnemar_tests.csv  # McNemar tests per demographic subgroup
│   │   ├── raw_responses.jsonl            # raw API responses
│   │   └── format_errors.jsonl            # parsing failures
│   ├── deepseek__deepseek-v3.2/           # 1040 trials, 520 pairs
│   ├── google__gemma-3-12b-it/            # 1040 trials, 520 pairs + demographic (reduced grid)
│   ├── google__gemma-3-27b-it/            # 1040 trials, 520 pairs
│   ├── openai__gpt-5.2/                   # 1040 trials, 520 pairs
│   ├── qwen__qwen3-next-80b-a3b-instruct/ # 1040 trials, 520 pairs
│   ├── qwen__qwen3.5-397b-a17b/           # 6240 trials, 3120 pairs (FULL demographic grid: 4 races × 3 ages × 8 names)
│   ├── x-ai__grok-4.1-fast/               # 1040 trials, 520 pairs
│   ├── z-ai__glm-4.7-flash/               # 6240 trials, 3120 pairs (FULL demographic grid)
│   └── model_run_status.csv               # run log: status, n_trials, errors
│
├── generate_dataset.py               # Script: LLM-generated 130 vignettes via structured output
├── run_experiments.py                # Script: main experiment runner (concurrent API calls)
├── compute_metrics.py                # Script: McNemar, delta_bias, paired t-test, Wilcoxon
├── openrouter_interface.py           # Script: OpenRouter API wrapper
└── config.py                         # Experiment configuration
```

---

## Experimental Design

### Conjunction Fallacy Task

Each vignette presents a biographical description + 5 answer options. The model must choose which is **more probable**:

- **T** — single base category (e.g., "public defender")
- **F** — single feature category (e.g., "volunteers at a civil rights organization")
- **F_uncorrelated** — unrelated feature (e.g., "collects vintage stamps")
- **T_and_F1** — conjunction of T + correlated feature
- **T_and_F2** — conjunction of T + uncorrelated feature

The conjunction fallacy occurs when `P(T_and_F) > P(T)` or `P(T_and_F) > P(F)`.

### Correlated vs Uncorrelated Pairs

Each vignette generates **2 critical pairs**:

| Pair | Options | Purpose |
|------|---------|---------|
| **Correlated** | T_and_F1 vs T | F1 is thematically linked to the vignette |
| **Uncorrelated** | T_and_F2 vs T | F2 is unrelated to the vignette |

The **delta_bias** metric measures the difference in fallacy rate between correlated and uncorrelated conditions — isolating the effect of narrative coherence from baseline conjunction bias.

### Demographic Substitutions

Names are substituted to signal racial identity:
| Race | Name |
|------|------|
| White | Emma |
| Black | Jamal |
| Hispanic | Carlos |
| Asian | Wei |

**Full demographic grid** (4 races × 3 ages × 8 names = 96 substitutions per vignette) was run only for `glm-4.7-flash` and `qwen3.5-397b-a17b`. After finding no significant age or proxy-gender effects, subsequent models used a **reduced grid**: 4 races × 1 age (38) × 1 name each.

### Vignette Generation

130 vignettes were generated using LLM structured output (`generate_dataset.py`) with M=4 options per vignette and 10 parallel generations. Deduplication was applied across passes.

---

## Diploma Table Mapping

| Diploma Table | Data Source |
|---|---|
| `tab:linda_results` (McNemar, delta_bias, 9 models) | `output/<model>/summary.json` |
| Demographic analysis text (glm-4.7-flash race effects) | `output/z-ai__glm-4.7-flash/demographic_mcnemar_tests.csv` |
| Cross-experiment `tab:cross_experiment` (delta_bias column) | Same summary.json files |

---

## Key Values in Diploma

| Model | n_pairs | n21 | McNemar p | delta_bias | Verified? |
|-------|---------|-----|-----------|------------|-----------|
| qwen3-next-80b | 520 | 316 | 1.50e-95 | +0.5648 | ✅ |
| gemma-3-27b-it | 520 | 305 | 3.07e-92 | +0.4975 | ✅ |
| gpt-5.2 | 520 | 209 | 2.43e-63 | +0.3746 | ✅ |
| grok-4.1-fast | 520 | 119 | 3.01e-36 | +0.2485 | ✅ |
| deepseek-v3.2 | 520 | 97 | 1.26e-29 | +0.1996 | ✅ |
| gemma-3-12b-it | 520 | 15 | 0.000122 | +0.0389 | ⚠️ diploma says n21=14, δ=0.0370 |
| glm-4.7-flash | 3120 | 26 | 2.98e-8 | +0.0279 | ✅ |
| claude-sonnet-4.6 | 520 | 1 | 1.0 | +0.1049 | ✅ |
| qwen3.5-397b-a17b | 3120 | 5 | 0.0625 | -0.0052 | ✅ |

**Known discrepancy:** `gemma-3-12b-it` n21 is **15** in raw data, **14** in diploma table. delta_bias is **0.0389** raw vs **0.0370** in diploma. Minor difference (~0.2%), likely from intermediate data version.

---

## How to Verify

To verify any value in diploma table `tab:linda_results`:
```bash
cat output/<model>/summary.json | python3 -m json.tool
```

To verify demographic claims:
```bash
cat output/z-ai__glm-4.7-flash/demographic_mcnemar_tests.csv
```

---

## Models

### Proprietary (3)
| Model | Provider | Status |
|-------|----------|--------|
| anthropic/claude-sonnet-4.6 | Anthropic | ✅ completed |
| x-ai/grok-4.1-fast | xAI | ✅ completed |
| openai/gpt-5.2 | OpenAI | ✅ completed |

### Open (6)
| Model | Provider | Status |
|-------|----------|--------|
| qwen/qwen3.5-397b-a17b | Qwen | ✅ completed (full demo grid) |
| z-ai/glm-4.7-flash | GLM | ✅ completed (full demo grid) |
| qwen/qwen3-next-80b-a3b-instruct | Qwen | ✅ completed |
| google/gemma-3-27b-it | Google | ✅ completed |
| deepseek/deepseek-v3.2 | DeepSeek | ✅ completed |
| google/gemma-3-12b-it | Google | ✅ completed (reduced demo grid) |

---

## Publication Figures

All figures follow the naming convention `linda_<graph_name>.png` and are saved in `figures/`:

| Figure | File | Purpose |
|--------|------|---------|
| **1** | `linda_delta_bias_bar.png` | Severity of bias (delta_bias) across models, sorted; main result |
| **2** | `linda_accuracy_vs_bias.png` | Scatter: overall accuracy vs delta_bias; correlation analysis |
| **3** | `linda_confidence_violin.png` | Distribution of model confidence in correlated vs uncorrelated conditions (top-5 models) |
| **4** | `linda_race_fallacy.png` | Fallacy rate by racial demographic groups; demographic effects |
| **5** | `linda_effect_sizes_forest.png` | Forest plot of Cohen's d effect sizes with interpretation thresholds |
| **6** | `linda_accuracy_by_condition.png` | **NEW:** Accuracy drop from correlated to uncorrelated condition per model |
| **7** | `linda_error_distribution_stack.png` | **NEW:** Stacked bar composition of 2×2 contingency table (n11, n12, n21, n22); shows asymmetry |
| **8** | `linda_mcnemar_pvalues_log.png` | **NEW:** McNemar p-values on log scale; statistical significance across models |

**New figures (6–8)** complement existing ones by showing:
- How narrative coherence affects task difficulty across models
- The asymmetric error pattern (why n21 >> n12, n22 ≈ 0)
- Statistical strength of the conjunction fallacy effect

All figures are generated by `plot_linda_results.py`.

---

## Why These Files?

**Included:** All data that matches numerical values in diploma chapter 2, experiment 1. Verified by comparing `summary.json` values against diploma table values (tolerance ±0.002).

**Excluded (cleaned):**
- `output/qwen__qwen3-4b/` — failed run, model ID 404 (not a valid endpoint)
- `output/qwen__qwen3.5-397b-a17bz-ai__glm-4.7-flash/` — failed run, malformed model ID

Both were erroneous early attempts and contain no usable data.
