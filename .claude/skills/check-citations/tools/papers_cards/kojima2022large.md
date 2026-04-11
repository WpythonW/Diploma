---
key: kojima2022large
title: Large language models are zero-shot reasoners
authors: Kojima, T. and Gu, S. S. and Reid, M. and Matsuo, Y. and Iwasawa, Y.
year: 2022
venue: Advances in Neural Information Processing Systems
doi: 10.52202/068431-1613
arxiv_id: 2205.11916
pdf_url: 
semantic_scholar_id: e7ad08848d5d7c5c47673ffe0da06af443643bda
paper_url: https://www.semanticscholar.org/paper/e7ad08848d5d7c5c47673ffe0da06af443643bda
citation_count: 6734
verified: true
confidence: 100
source_used: semantic_scholar
---

## Goal
The authors aim to demonstrate that large language models (LLMs) can perform complex reasoning tasks without any in-context examples or fine-tuning—i.e., in a zero-shot setting. They observe that traditional prompting methods often fail to elicit logical, step-by-step reasoning in LLMs, leading to suboptimal performance on reasoning benchmarks. To address this, they propose a simple yet effective method to unlock the inherent reasoning capabilities of LLMs by modifying the prompt structure. The scope includes evaluating this approach across diverse reasoning tasks such as arithmetic, symbolic, and commonsense reasoning.

## Gap Addressed
Prior work on prompting LLMs for reasoning tasks primarily relied on few-shot learning with chain-of-thought (CoT) examples, which require carefully designed demonstrations and consume valuable input tokens. This limits scalability and generalizability, especially when suitable examples are unavailable. The authors identify a key gap: the assumption that LLMs cannot reason in a zero-shot manner may stem not from model limitations but from inadequate prompting strategies. They challenge the prevailing reliance on few-shot CoT and show that even without examples, LLMs can generate coherent reasoning traces when properly prompted.

## Method
The authors introduce "zero-shot chain-of-thought" (Zero-Shot CoT) prompting, which involves appending a simple phrase—"Let's think step by step"—to the end of the input question. This verbal cue triggers the model to generate an intermediate reasoning chain before producing the final answer. The method requires no additional training, hand-crafted examples, or model modifications. They evaluate this approach on a range of reasoning tasks using off-the-shelf LLMs, particularly focusing on PaLM and other decoder-based architectures, comparing zero-shot performance with standard prompting and few-shot CoT baselines.

## Datasets and Metrics
**Datasets:** The study evaluates on multiple public benchmarks: GSM8K (8.5K grade school math word problems), MultiArith, MathQA, SVAMP (arithmetic reasoning); Date Understanding, Last Letters, and Coin Flip (symbolic and commonsense reasoning from BIG-Bench); and StrategyQA (multi-hop reasoning). Dataset sizes vary: GSM8K has ~7.5K training and 1K test examples; others are smaller, often in the hundreds. Exact splits follow original dataset conventions.

**Metrics:** Primary metric is accuracy (exact match) on final answers. For GSM8K, they report accuracy with and without CoT supervision. Zero-Shot CoT achieves 71.8% on GSM8K with PaLM 540B (vs. 33.6% with standard prompting). On MultiArith: 60.7% (vs. 40.7%); MathQA: 78.7% (vs. 60.5%); SVAMP: 66.9% (vs. 41.3%). Gains across symbolic tasks range from +15% to +25%. Specific values for StrategyQA and BIG-Bench tasks also show consistent improvements.

## Results
Zero-Shot CoT significantly improves reasoning performance across arithmetic, symbolic, and multi-step tasks. On GSM8K, it boosts PaLM 540B accuracy by over 38 percentage points compared to standard prompting. The method outperforms zero-shot baselines across all datasets, often approaching or exceeding the performance of few-shot CoT with manually designed examples. The effect is most pronounced in larger models (e.g., 540B > 62B > 8B), suggesting emergent reasoning behavior at scale. The verbal prompt reliably induces step-by-step reasoning traces, which are interpretable and logically coherent. The results indicate that LLMs possess latent reasoning abilities that can be activated without explicit demonstrations.

## Limitations
The effectiveness of Zero-Shot CoT depends heavily on model scale, with smaller models showing minimal gains. The method does not guarantee correct reasoning traces, and hallucinated or illogical steps can still lead to wrong answers. The approach is also sensitive to phrasing—alternative prompts may not yield the same results—and lacks formal guarantees about reasoning validity.

## Verification Verdict
REAL (100%) — Paper confirmed by both Semantic Scholar and web search via Perplexity. Matching title, authors, year, and venue (NeurIPS 2022). Supported by arXiv ID (2205.11916), official proceedings link, and high citation count (6,734).

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/e7ad08848d5d7c5c47673ffe0da06af443643bda)
- [DOI](https://doi.org/10.52202/068431-1613)
- [arXiv](https://arxiv.org/abs/2205.11916)
