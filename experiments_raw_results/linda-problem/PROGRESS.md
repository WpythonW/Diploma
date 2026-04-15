# Linda Problem — Progress

> **9 LLMs × correlated vs uncorrelated pairs — ALL COMPLETE**

---

## Axes

| Axis | Values | Count |
|------|--------|-------|
| **Model** | 3 proprietary + 6 open | 9 |
| **Condition** | correlated, uncorrelated | 2 |
| **Demographic grid** | Full (4×3×8) / Reduced (4×1×1) | varies |

---

## Status: All 9 Models Completed ✅

| # | Model | n_trials | n_pairs | Demographic grid | Output Dir |
|---|-------|----------|---------|------------------|------------|
| 1 | claude-sonnet-4.6 | 1040 | 520 | Reduced | `output/anthropic__claude-sonnet-4.6/` |
| 2 | grok-4.1-fast | 1040 | 520 | Reduced | `output/x-ai__grok-4.1-fast/` |
| 3 | gpt-5.2 | 1040 | 520 | Reduced | `output/openai__gpt-5.2/` |
| 4 | qwen3.5-397b-a17b | 6240 | 3120 | **Full** (4 races × 3 ages × 8 names) | `output/qwen__qwen3.5-397b-a17b/` |
| 5 | glm-4.7-flash | 6240 | 3120 | **Full** (4 races × 3 ages × 8 names) | `output/z-ai__glm-4.7-flash/` |
| 6 | qwen3-next-80b-a3b-instruct | 1040 | 520 | Reduced | `output/qwen__qwen3-next-80b-a3b-instruct/` |
| 7 | gemma-3-27b-it | 1040 | 520 | Reduced | `output/google__gemma-3-27b-it/` |
| 8 | deepseek-v3.2 | 1040 | 520 | Reduced | `output/deepseek__deepseek-v3.2/` |
| 9 | gemma-3-12b-it | 1040 | 520 | Reduced | `output/google__gemma-3-12b-it/` |

**Done: 9/9 models**

---

## Remaining: None

All experiment data for diploma chapter 2, experiment 1 is present and verified.

---

## Diploma Coverage

All values in `tab:linda_results` (chapter 2) are sourced from `output/<model>/summary.json` files. Demographic analysis text is sourced from `demographic_mcnemar_tests.csv` for glm-4.7-flash, qwen3.5-397b-a17b, and gemma-3-12b-it.

See **[README.md](./README.md)** for file structure and data sources.
