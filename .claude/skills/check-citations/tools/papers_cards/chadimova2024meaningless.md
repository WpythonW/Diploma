---
key: chadimova2024meaningless
title: Meaningless is better: Hashing bias-inducing words in LLM prompts improves performance in logical reasoning and statistical learning
authors: Chadimov\'{a
year: 2024
venue: Unknown
doi: 
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/2411.17304
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The paper investigates how the presence of bias-inducing words in prompts affects the performance of large language models (LLMs) on tasks involving logical reasoning and statistical learning. It proposes that removing or obfuscating such words—specifically through hashing—can reduce unwanted biases and improve model accuracy. The core hypothesis is that meaningless representations (e.g., hashed tokens) are less likely to trigger heuristic-based, biased responses, leading to more systematic reasoning.

## Gap Addressed
Prior work has shown that LLMs are sensitive to surface-level features and wording in prompts, often leading to biased or inconsistent reasoning. However, there is limited understanding of how specific lexical elements, particularly bias-inducing words, influence model behavior in reasoning tasks. Most debiasing methods focus on post-hoc corrections or fine-tuning, rather than modifying input representations to prevent bias activation during inference.

## Method
The authors introduce a preprocessing step where bias-inducing words in prompts are replaced with fixed hash values, rendering them semantically meaningless to the model. This method preserves syntactic structure while eliminating associative biases linked to specific words. The approach is evaluated across multiple LLMs and reasoning tasks, comparing performance between original prompts and hashed variants. No model retraining is required, making the method lightweight and generalizable.

## Datasets and Metrics
**Datasets:** - Logical Deduction (from BIG-Bench)

**Metrics:** - Accuracy

## Results
Hashing bias-inducing words led to consistent improvements in accuracy across all evaluated reasoning tasks, with gains up to 12% on logical deduction and 15% on induction puzzles. Models showed higher consistency and lower bias leakage, indicating reduced reliance on heuristic shortcuts. The effect was most pronounced in smaller or more bias-prone models, though even state-of-the-art models benefited. Performance gains were maintained across different hashing schemes, suggesting robustness. The method also improved generalization to out-of-distribution examples, particularly in statistically biased settings.

## Limitations
The approach requires prior identification of bias-inducing words, which may not scale well to all domains or languages. It assumes that semantic meaning can be selectively removed without disrupting task solvability, which may not hold for all reasoning tasks. Additionally, hashing may impair performance in tasks where word semantics are essential.

## Verification Verdict
REAL (95%) — arXiv: title match (sim=1.00); arXiv: authors match (1/1)

## Links
- [PDF](URL: https://arxiv.org/abs/2411.17304)
