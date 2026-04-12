---
key: jiang2024peek
title: A peek into token bias: Large language models are not yet genuine reasoners
authors: Jiang, B. and Xie, Y. and Hao, Z. and Wang, X. and Mallick, T. and Su, W. J. and Taylor, C. J. and Roth, D.
year: 2024
venue: Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 98
source_used: pdf
---

## Goal
The paper aims to investigate whether large language models (LLMs) genuinely reason or rely on superficial token-level biases when generating responses. It seeks to determine if LLMs make decisions based on logical inference or exploit statistical patterns in training data. The authors propose a framework to disentangle reasoning from memorization or bias exploitation. This work contributes to the broader understanding of LLM capabilities and limitations in tasks requiring true cognitive reasoning.

## Gap Addressed
Prior studies often evaluate LLMs based on output accuracy without probing the underlying decision-making process, leaving it unclear whether models reason or exploit dataset artifacts. There is a lack of rigorous methods to distinguish genuine reasoning from heuristic-based responses driven by token co-occurrence patterns. Existing benchmarks may inadvertently reward models for leveraging surface-level biases rather than demonstrating logical inference. This gap limits trust and interpretability in high-stakes applications.

## Method
The authors introduce a hypothesis-testing framework that manipulates input token statistics while preserving logical structure to detect reliance on token bias. They design controlled experiments where token frequencies are altered to create conflicting cues between statistical shortcuts and correct reasoning paths. By analyzing model performance under these manipulations, they assess whether predictions align with reasoning or token-level heuristics. The method is applied across multiple reasoning tasks and model sizes.

## Datasets and Metrics
**Datasets:** Synthetic reasoning datasets with controlled token statistics, including variants of arithmetic reasoning, logical deduction, and symbolic manipulation tasks. These datasets are specifically constructed to isolate token bias from valid reasoning pathways.

**Metrics:** Accuracy, consistency under token distribution shifts, sensitivity to misleading token cues, and comparison against baseline models with known reasoning behaviors. The study also uses intervention-based metrics to quantify reliance on biased tokens.

## Results
LLMs show significant performance drops when token biases are altered or removed, indicating heavy reliance on such cues rather than structural reasoning. Models often follow high-frequency token patterns even when they contradict correct solutions. Larger models do not consistently outperform smaller ones in bias-resistant settings, challenging the notion that scale leads to better reasoning. The findings suggest current LLMs lack robust, generalizable reasoning mechanisms and instead exploit shallow statistical regularities in training data.

## Limitations
The synthetic nature of the datasets may not fully capture real-world reasoning complexity. Findings are based on specific task types and may not generalize to all forms of reasoning. The framework assumes clean separation between token bias and reasoning, which may be difficult to maintain in naturalistic language.

## Verification Verdict
REAL (98%) — Multiple authoritative sources (ACL Anthology, arXiv, CrossRef, OpenAlex) confirm the paper's existence, authors, title, and publication at EMNLP 2024. The arXiv preprint explicitly states acceptance. Minor name formatting differences are normal.
