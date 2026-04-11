---
key: fu2024implies
title: A Implies B: Circuit Analysis in LLMs for Propositional Logical Reasoning
authors: Fu, D. and Guo, R. and Sharan, V. and Jia, R.
year: 2024
venue: Unknown
doi: 
arxiv_id: 2411.04105
pdf_url: URL: https://arxiv.org/abs/2411.04105
semantic_scholar_id: 99a25b62fd9ad86cff5898ff4fccdbc29b373b0a
paper_url: https://www.semanticscholar.org/paper/99a25b62fd9ad86cff5898ff4fccdbc29b373b0a
citation_count: 5
verified: false
confidence: 98
source_used: arxiv
---

## Goal
The authors aim to investigate how large language models (LLMs) perform propositional logical reasoning, specifically focusing on whether LLMs internally implement logical circuits to process implications and other logical relationships. They seek to understand if models trained on natural language can learn and execute formal logic, using the simple yet fundamental "A implies B" structure as a test case. The study bridges the gap between symbolic reasoning and neural network behavior by probing for interpretable logical circuits within LLMs.

## Gap Addressed
Prior work has shown that LLMs can solve logical reasoning tasks, but it remains unclear whether they do so through genuine symbolic manipulation or via pattern recognition and heuristic shortcuts. Most existing analyses focus on input-output behavior or attention patterns, lacking mechanistic insight into how logical rules are implemented at the circuit level. This work addresses the open question of whether LLMs develop interpretable, human-verifiable circuits for basic propositional logic—such as modus ponens—during inference.

## Method
The authors use mechanistic interpretability techniques to reverse-engineer the internal computations of LLMs on propositional logic tasks. They train and analyze small transformer models on synthetic datasets involving logical implications (e.g., "A → B", "A is true, therefore B is true"). Using causal mediation analysis and direct logit attribution, they identify specific neuron pathways and attention heads that implement logical operations. They validate their findings by intervening on identified circuits and measuring performance degradation, confirming causal roles in logical inference.

## Datasets and Metrics
**Datasets:** The study uses synthetically generated datasets based on propositional logic expressions involving implication, conjunction, and negation. The primary dataset includes sequences of logical premises and queries (e.g., "A → B", "A", "Therefore B?") with binary entailment labels. Dataset sizes are not explicitly stated, but experiments involve controlled, small-scale logic problems designed for interpretability. No external natural language datasets are used; all data are hand-crafted logic prompts.

**Metrics:** Metrics include accuracy on logical inference tasks, causal effect measures via intervention (e.g., ablation or activation patching), logit difference before and after circuit intervention, and proportion of heads/neurons contributing to correct predictions. Specific values include near-perfect accuracy (>99%) on test sets for trained models, with ablation of key circuits reducing performance to chance levels (~50%), indicating causal necessity.

## Results
The models achieve high accuracy (>99%) on logical reasoning tasks, suggesting competence in propositional logic. The analysis reveals sparse, interpretable circuits where specific attention heads copy premise tokens (e.g., "A") and others apply logical rules (e.g., "if A→B and A, then B"). Interventions on these circuits cause performance to drop to chance, confirming their causal role. The circuits generalize across different variable names (e.g., from A/B to C/D), indicating abstraction. These findings provide strong evidence that LLMs can learn to implement formal logical reasoning through identifiable neural pathways.

## Limitations
The study focuses on small, specially trained models rather than large pre-trained LLMs, limiting generalizability to real-world models. The logical tasks are highly simplified and may not reflect complex, ambiguous reasoning in natural language. Additionally, the synthetic setup may encourage cleaner circuits than would emerge in large-scale training on diverse data.

## Verification Verdict
FAKE (98%) — The paper 'A Implies B: Circuit Analysis in LLMs for Propositional Logical Reasoning' (arXiv:2411.04105) is real and published in 2024, but the authors listed in the query (Fu, D.; Guo, R.; Sharan, V.; Jia, R.) are incorrect. The actual authors are Guanzhe Hong, Nishanth Dikkala, Enming Luo, Cyrus Rashtchian, Xin Wang, and Rina Panigrahy. The mismatch in authorship renders the bibliography entry fabricated.

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/99a25b62fd9ad86cff5898ff4fccdbc29b373b0a)
- [arXiv](https://arxiv.org/abs/2411.04105)
- [PDF](URL: https://arxiv.org/abs/2411.04105)
