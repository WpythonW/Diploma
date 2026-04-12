---
key: bazigaran2025concept
title: Concept generalization in humans and large language models: Insights from the number game
authors: Bazigaran, A. and Sohn, H.
year: 2025
venue: Unknown
doi: 
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/2512.20162
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The paper aims to investigate how humans and large language models (LLMs) generalize concepts, using a "number game" framework where participants infer underlying rules from numerical examples. It seeks to compare the inductive biases and generalization patterns of humans and LLMs when faced with abstract concept learning tasks. The study is inspired by classic cognitive science experiments on human concept learning, adapted to evaluate machine learning models.

## Gap Addressed
While prior work has explored concept learning in humans and machines separately, there is limited direct comparison of how both generalize from minimal examples, especially in structured numerical domains. Existing studies often focus on visual or linguistic tasks, leaving a gap in understanding rule-based numerical concept generalization across humans and LLMs. The paper addresses this by using a controlled, cognitively inspired task to highlight similarities and differences in generalization behavior.

## Method
The authors design a number game where participants (humans and LLMs) are given a set of example numbers and asked to infer the underlying rule (e.g., "powers of two"). Human subjects provide free-text explanations and next-number predictions, while LLMs are prompted similarly in a zero-shot or few-shot setup. The study analyzes both prediction choices and verbalized rules to assess generalization patterns and inductive biases.

## Datasets and Metrics
**Datasets:** Synthetic number rule datasets based on mathematical concepts (e.g., arithmetic sequences, prime numbers, powers, divisibility) inspired by the original number game from cognitive science literature.

**Metrics:** Prediction accuracy, rule consistency, semantic similarity of generated rules to human responses, and overlap in generalization patterns between humans and LLMs.

## Results
Humans show strong preference for simple, mathematically meaningful rules, consistent with previous cognitive studies. LLMs often mimic plausible rules but exhibit less consistency and are more sensitive to prompt formatting. While LLMs can reproduce common patterns (e.g., even numbers), they struggle with less frequent or abstract rules (e.g., Fibonacci). The study finds moderate alignment between human and model generalizations, but LLMs show higher variability and occasional reliance on superficial patterns. Fine-tuned models perform better than zero-shot ones, yet still lag behind human coherence.

## Limitations
The number game is a simplified abstraction of real-world concept learning, potentially limiting ecological validity. LLM evaluations are constrained to text-based interaction, which may not fully capture their reasoning processes.

## Verification Verdict
REAL (95%) — arXiv: title match (sim=1.00); arXiv: authors match (2/2)

## Links
- [PDF](URL: https://arxiv.org/abs/2512.20162)
