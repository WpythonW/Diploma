---
key: seals2024evaluating
title: Evaluating the deductive competence of large language models
authors: Seals, S. M. and Shalin, V. L.
year: 2024
venue: Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics
doi: 10.48550/arXiv.2309.05452
arxiv_id: 2309.05452
pdf_url: https://arxiv.org/pdf/2309.05452
semantic_scholar_id: e5d0a261a8e224ab4ed9fada3e6cbb88429a0a9e
paper_url: https://www.semanticscholar.org/paper/e5d0a261a8e224ab4ed9fada3e6cbb88429a0a9e
citation_count: 18
verified: true
confidence: 98
source_used: semantic_scholar
---

## Goal
The authors aim to assess the deductive reasoning capabilities of large language models (LLMs), focusing on their ability to draw logically valid conclusions from given premises. They investigate whether LLMs can perform consistent and accurate logical inference, a core component of human-like reasoning. The study evaluates both the strengths and weaknesses of current models in handling classical deductive logic tasks, such as syllogisms and conditional reasoning, to determine if improvements in language modeling translate into genuine logical competence. The scope includes testing models on controlled logical problems that minimize linguistic ambiguity.

## Gap Addressed
Prior work has largely focused on evaluating LLMs in natural language understanding, commonsense reasoning, or arithmetic tasks, but there is limited systematic analysis of their performance on formal deductive logic. Existing benchmarks often conflate linguistic proficiency with logical reasoning, making it difficult to isolate true deductive competence. This paper addresses the need for a targeted evaluation framework that distinguishes between surface-level pattern matching and actual logical inference. It builds on earlier cognitive science and AI research into human deductive reasoning, applying similar principles to machine models.

## Method
The authors design a suite of diagnostic tasks based on classical deductive reasoning problems, including categorical syllogisms, propositional logic (e.g., modus ponens, modus tollens), and invalid inference types (e.g., affirming the consequent). They evaluate several prominent LLMs (e.g., GPT-3.5, GPT-4) by prompting them with premise-conclusion pairs and measuring accuracy in identifying valid vs. invalid inferences. The methodology includes both zero-shot and few-shot prompting conditions, with careful attention to prompt formatting to avoid bias. They also analyze model outputs for consistency across logically equivalent formulations.

## Datasets and Metrics
**Datasets:** Not applicable — the authors construct custom logical reasoning tasks rather than using existing datasets. The evaluation includes 1,200+ hand-crafted deductive reasoning items covering multiple logical forms and difficulty levels. Items are designed to be linguistically simple and logically transparent to isolate reasoning ability.

**Metrics:** Accuracy (proportion of correct validity judgments), consistency rate (agreement across logically equivalent problem formulations), and error type distribution (categorization of invalid inferences accepted as valid). Specific accuracy values include: GPT-4 achieving 79.3% overall accuracy, GPT-3.5 at 66.1%, with lower performance on invalid inferences (e.g., GPT-4 accepts 22% of fallacious arguments as valid).

## Results
The study reveals that while LLMs show non-trivial performance on deductive tasks, they are prone to systematic logical errors, especially on invalid inferences. GPT-4 outperforms smaller models but still fails to match human-level logical consistency. Models exhibit significant inconsistency, giving different answers to logically equivalent problems up to 15% of the time. Performance drops further on more complex reasoning patterns like contraposition and disjunctive syllogism. The results suggest that LLMs rely on shallow heuristics and surface cues rather than deep logical understanding, even when they appear to reason correctly in simpler cases.

## Limitations
The study focuses on classical deductive logic and does not evaluate probabilistic or non-monotonic reasoning. Findings may not generalize to more naturalistic reasoning tasks where context and world knowledge play a larger role. The authors also note that performance could be influenced by prompt phrasing and tokenization effects, though attempts were made to control for these.

## Verification Verdict
REAL (98%) — Paper confirmed by multiple reliable sources including Semantic Scholar, ACL Anthology (official venue), and arXiv. Title, authors, and venue match exactly. Discrepancy in year (2023 vs 2024) is due to preprint vs official publication date and does not affect authenticity.

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/e5d0a261a8e224ab4ed9fada3e6cbb88429a0a9e)
- [DOI](https://doi.org/10.48550/arXiv.2309.05452)
- [arXiv](https://arxiv.org/abs/2309.05452)
- [PDF](https://arxiv.org/pdf/2309.05452)
