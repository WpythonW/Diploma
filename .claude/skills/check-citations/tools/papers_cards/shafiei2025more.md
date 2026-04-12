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
The paper aims to investigate and quantify directional bias in large language models (LLMs) during comparative reasoning tasks—specifically, whether models exhibit systematic errors when evaluating "more" versus "less" comparisons. It introduces a benchmark designed to test the consistency and accuracy of LLMs when the direction of comparison is reversed, seeking to uncover whether models favor one direction (e.g., "more") over the other, leading to logically inconsistent judgments.

## Gap Addressed
Prior evaluations of LLM reasoning have largely focused on factual accuracy or logical consistency in non-directional tasks, with limited attention to how the phrasing of comparative statements affects model performance. There is a lack of standardized benchmarks that isolate and measure directional bias in comparative language understanding, making it difficult to diagnose and correct such biases in downstream applications.

## Method
The authors construct a controlled benchmark called "More or Less Wrong" (MoLW), consisting of symmetric comparison pairs where the direction of comparison is reversed (e.g., "X is more Y than Z" vs. "Z is less Y than X"). They evaluate multiple state-of-the-art LLMs by measuring consistency in responses across these reversed pairs. Inconsistencies indicate directional bias. The benchmark includes both factual and counterfactual comparisons across various domains (e.g., size, intelligence, temperature).

## Datasets and Metrics
**Datasets:** MoLW (More or Less Wrong) benchmark

**Metrics:** Response consistency rate, accuracy, directional bias score, logical contradiction rate

## Results
The study reveals significant directional bias across all tested LLMs, with consistency rates below 80% on average, meaning models often give contradictory answers to logically equivalent reversed comparisons. Models perform better on "more" statements than "less" statements, indicating a systematic asymmetry in reasoning. The bias persists across model sizes and architectures, suggesting it is not easily mitigated by scale. The MoLW benchmark effectively discriminates between models in terms of logical robustness, revealing that even high-performing models struggle with directional symmetry in reasoning.

## Limitations
The MoLW benchmark is limited to binary comparative statements and does not cover gradable adjectives with more than two entities or continuous scales. The current version focuses primarily on English and may not generalize to other languages or cultural contexts.

## Verification Verdict
REAL (95%) — arXiv: title match (sim=1.00); arXiv: authors match (3/3)

## Links
- [PDF](URL: https://arxiv.org/abs/2506.03923)
