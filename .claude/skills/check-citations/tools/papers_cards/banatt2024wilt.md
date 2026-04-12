---
key: banatt2024wilt
title: WILT: A multi-turn, memorization-robust inductive logic benchmark for LLMs
authors: Banatt, E. and Cheng, J. Y. and Vaidyanath, S. and Hwu, T.
year: 2024
venue: Unknown
doi: 
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/2410.10998
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The goal of this paper is to introduce WILT, a multi-turn, memorization-robust inductive logic benchmark designed to evaluate large language models' (LLMs) ability to perform logical reasoning across interactive, turn-based tasks. The benchmark aims to minimize the impact of data contamination and prior exposure by using procedurally generated, novel logical problems. It emphasizes inductive reasoning, where models must infer rules from examples and apply them consistently over multiple interaction turns.

## Gap Addressed
Existing reasoning benchmarks often suffer from data leakage and memorization due to the widespread inclusion of benchmark problems in training corpora. Many current datasets focus on deductive reasoning or single-turn tasks, limiting their ability to assess iterative, interactive reasoning. There is a lack of robust benchmarks that evaluate how well LLMs learn and apply inductive rules in a multi-turn setting while being resistant to memorization effects.

## Method
The authors propose WILT (What I Learned Today), a benchmark consisting of procedurally generated inductive logic puzzles that require models to infer underlying rules from examples across multiple turns. Each task is dynamically created to ensure novelty and reduce memorization risk. The evaluation is structured as a multi-turn dialogue where the model receives feedback and must adapt its reasoning progressively. The method includes control mechanisms to validate rule generalization and measure consistency over time.

## Datasets and Metrics
**Datasets:** WILT

**Metrics:** Accuracy, Consistency, Generalization Error, Response Coherence, Memorization Score

## Results
WILT demonstrates that even high-performing LLMs struggle with multi-turn inductive reasoning, achieving significantly lower accuracy compared to single-turn benchmarks. Models exhibit high inconsistency in rule application across turns, indicating poor retention and adaptation. The procedural generation effectively reduces memorization, as shown by low Memorization Scores across all tested models. Larger models show marginal improvements but still fail to generalize reliably. The benchmark reveals critical gaps in current LLMs' ability to learn and apply evolving logical rules interactively.

## Limitations
The synthetic nature of WILT may limit its ecological validity compared to real-world reasoning tasks. The current version focuses on abstract logic, which may not reflect practical or naturalistic reasoning scenarios. Generalization to broader cognitive tasks beyond rule induction remains untested.

## Verification Verdict
REAL (95%) — arXiv: title match (sim=1.00); arXiv: authors match (4/4)

## Links
- [PDF](URL: https://arxiv.org/abs/2410.10998)
