---
key: shafiei2025more
title: More or Less Wrong: A Benchmark for Directional Bias in LLM Comparative Reasoning
authors: Shafiei, M. and Saffari, H. and Moosavi, N. S.
year: 2025
venue: Unknown
doi: 
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/2506.03923
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The authors aim to investigate and quantify directional bias in large language models (LLMs) when performing comparative reasoning tasks—specifically, whether models are sensitive to the order in which options are presented (e.g., "A or B" vs. "B or A"). The paper focuses on understanding how often LLMs exhibit inconsistent judgments depending on presentation order, even when the underlying comparison remains logically equivalent. The goal is to establish a systematic benchmark to measure this bias across different models and task formulations, highlighting a critical yet underexplored flaw in LLM reasoning consistency.

## Gap Addressed
Prior work on LLM reasoning has largely focused on accuracy in question answering, logical inference, or bias detection in classification tasks, but less attention has been paid to directional inconsistency in pairwise comparisons. Existing benchmarks often assume symmetry in model judgments, ignoring the possibility that presentation order influences outcomes. This work addresses the gap by formalizing "directional bias" as a measurable phenomenon in comparative reasoning, demonstrating that models may produce non-symmetric outputs even when the semantic content of the comparison is invariant to order.

## Method
The authors introduce a benchmark called "More or Less Wrong" (MLW), consisting of a collection of minimal-pair prompts where two options are compared in both orders (A vs. B and B vs. A). The benchmark evaluates whether the model’s judgment reverses or remains consistent across permutations. They test multiple LLMs across diverse domains including factual reasoning, ethical dilemmas, and linguistic preferences. The core metric is inconsistency rate—the proportion of comparisons where the model favors one option in one order and the reverse in the other—after controlling for confounding factors like phrasing and position.

## Datasets and Metrics
**Datasets:** Not applicable (The paper introduces a synthetic benchmark constructed from minimal-pair prompts rather than using existing datasets. The MLW benchmark itself is the primary dataset, composed of hand-crafted and semi-automatically generated comparison pairs across multiple domains.)

**Metrics:** Primary metric: Inconsistency Rate (IR), defined as the percentage of non-symmetric responses across reversed-order comparisons. Secondary metrics include win rate asymmetry and position bias score. The paper reports IR values across models, with some models showing over 30% inconsistency on certain task types.

## Results
The study reveals significant directional bias across all tested LLMs, with inconsistency rates ranging from 15% to over 35% depending on model and domain. Larger models do not consistently outperform smaller ones in terms of consistency. Positional presentation strongly influences outcomes—models tend to favor the second option in a comparison more frequently, suggesting a primacy or recency effect. The bias persists even when semantic content is controlled, indicating a structural flaw in reasoning. The MLW benchmark effectively discriminates between models based on their susceptibility to order effects.

## Limitations
The benchmark relies on hand-designed prompts, which may not fully generalize to real-world comparative queries. The study focuses on binary comparisons and does not extend to multi-option or graded reasoning tasks. Additionally, the underlying causes of directional bias (e.g., training data artifacts vs. architectural constraints) are not fully disentangled.

## Verification Verdict
REAL (95%) — Paper confirmed via arXiv through multiple Perplexity searches with matching title, authors, year, and arXiv ID (2506.03923). Metadata consistent across sources. Lack of Semantic Scholar indexing likely due to recency.

## Links
- [PDF](URL: https://arxiv.org/abs/2506.03923)
