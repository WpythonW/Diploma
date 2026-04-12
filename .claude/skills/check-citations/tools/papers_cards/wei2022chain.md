---
key: wei2022chain
title: Chain-of-thought prompting elicits reasoning in large language models
authors: Wei, J. and Wang, X. and Schuurmans, D. and Bosma, M. and Ichter, B. and Xia, F. and Chi, E. and Le, Q. and Zhou, D.
year: 2022
venue: Advances in Neural Information Processing Systems
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 99
source_used: arxiv
---

## Goal
The paper aims to investigate how large language models (LLMs) can be prompted to perform complex reasoning tasks by generating intermediate reasoning steps, known as a "chain-of-thought" (CoT). It seeks to demonstrate that such reasoning capabilities emerge naturally in sufficiently large models when provided with few-shot examples of step-by-step reasoning. The authors hypothesize that CoT prompting can significantly improve performance on arithmetic, commonsense, and symbolic reasoning tasks compared to standard prompting methods.

## Gap Addressed
Prior work in language modeling primarily focused on direct input-output mappings, where models are prompted to generate answers without intermediate reasoning. This approach often fails on complex reasoning tasks that require decomposition into sub-steps. There was a lack of methods to elicit implicit reasoning abilities in large language models, especially in a few-shot setting without requiring architectural changes or fine-tuning. The paper addresses this gap by proposing a simple yet effective prompting strategy that unlocks latent reasoning capabilities.

## Method
The authors introduce chain-of-thought (CoT) prompting, where a few-shot exemplar includes not only the input and output but also a sequence of intermediate reasoning steps leading to the final answer. These reasoning chains are manually crafted and presented in the prompt to guide the model. The method is applied to large language models (e.g., PaLM) in a few-shot setup, without any parameter updates. The approach is evaluated across multiple reasoning tasks, comparing CoT with standard prompting.

## Datasets and Metrics
**Datasets:** MultiArith, GSM8K, AQuA, CommonsenseQA, StrategyQA

**Metrics:** Accuracy

## Results
Chain-of-thought prompting significantly improves performance on arithmetic reasoning tasks: it achieves a 58% improvement over standard prompting on GSM8K and closes the gap with supervised fine-tuning. On MultiArith, CoT with large models (175B) reaches 74.7% accuracy, far surpassing standard prompting. The method also shows strong gains on commonsense reasoning (e.g., +13% on CommonsenseQA) and symbolic tasks. Performance scales with model size, with minimal benefit observed in smaller models (<6B), indicating that CoT is particularly effective in sufficiently large language models. The results demonstrate that reasoning abilities can be elicited through prompting alone, without architectural modifications.

## Limitations
The effectiveness of chain-of-thought prompting depends heavily on model size, with little to no benefit observed in smaller models. Additionally, the method relies on manually designed reasoning chains, which may introduce human bias and limit generalization to new domains without careful prompt engineering.

## Verification Verdict
REAL (99%) — Multiple authoritative sources (Semantic Scholar, CrossRef, arXiv, OpenAlex) confirm the paper's existence with matching title, authors, year, and venue. The paper is highly cited (over 17k citations) and well-documented in the literature.
