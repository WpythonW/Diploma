---
key: fu2024implies
title: A Implies B: Circuit Analysis in LLMs for Propositional Logical Reasoning
authors: Hong, G. Z. and Dikkala, N. and Luo, E. and Rashtchian, C. and Wang, X. and Panigrahy, R.
year: 2024
venue: Unknown
doi: 
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/2411.04105
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The paper aims to investigate how large language models (LLMs) perform propositional logical reasoning, specifically focusing on whether LLMs can correctly infer logical implications (e.g., "A implies B") and understand basic propositional logic. It seeks to uncover the internal mechanisms within LLMs that support such reasoning by analyzing model weights and activations. The authors aim to determine if LLMs implement formal logical circuits or rely on heuristic, surface-level pattern matching.

## Gap Addressed
While LLMs show strong performance on various reasoning tasks, it remains unclear whether they perform genuine logical deduction or exploit statistical patterns in training data. Prior work has not thoroughly analyzed the circuit-level mechanisms in LLMs responsible for propositional reasoning. There is a lack of understanding about whether logical implications are encoded explicitly in model weights or emerge implicitly through training.

## Method
The authors perform circuit-level analysis of LLMs by examining weight patterns and activation pathways involved in propositional logic tasks. They construct minimal logical probes and analyze attention and MLP layers to identify components responsible for logical implication. Using synthetic datasets with controlled logical structures, they isolate reasoning behavior and apply causal mediation analysis to trace information flow. The study focuses on small transformer models trained on logical expressions to enable full interpretability.

## Datasets and Metrics
**Datasets:** Synthetic logical expressions datasets containing propositional statements and implications (e.g., "A → B", "A ∧ B", etc.), generated with controlled logical structures and varying complexity.

**Metrics:** Accuracy on logical inference tasks, causal influence scores from mediation analysis, circuit sparsity, and consistency with formal logic rules.

## Results
The study finds that LLMs can learn to perform basic propositional reasoning, but often rely on shallow heuristics rather than systematic logical deduction. Specific circuits in MLP layers are identified that correspond to logical implication operations, suggesting some degree of structured reasoning. However, models frequently fail on out-of-distribution or negated forms, indicating limited generalization. Causal analysis reveals that certain neurons act as logical gates, but their behavior is context-dependent and not fully aligned with formal logic. The results suggest that logical reasoning in LLMs is partially implemented through identifiable circuits but remains fragile and data-dependent.

## Limitations
The analysis is primarily conducted on small, synthetically trained models, limiting generalizability to larger, real-world LLMs. The study focuses on propositional logic only, leaving more complex reasoning (e.g., first-order logic) unexplored. Logical circuits identified may not be robust across different architectures or training regimes.

## Verification Verdict
REAL (95%) — arXiv: title match (sim=1.00); arXiv: authors match (6/6)

## Links
- [PDF](URL: https://arxiv.org/abs/2411.04105)
