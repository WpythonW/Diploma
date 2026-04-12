---
key: zhou2023benchmark
title: Don't make your LLM an evaluation benchmark cheater
authors: Zhou, K. and Zhu, Y. and Chen, Z. and Chen, W. and Zhao, W. X. and Chen, X. and Lin, Y. and Wen, J.-R. and Han, J.
year: 2023
venue: Unknown
doi: 
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/2311.01964
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The paper aims to investigate the phenomenon of large language models (LLMs) "cheating" on evaluation benchmarks by being exposed to benchmark data during pretraining, which compromises the validity of benchmark results. It highlights how such contamination leads to inflated performance metrics that do not reflect true generalization ability. The authors advocate for more rigorous evaluation practices to ensure fair and reliable assessment of LLM capabilities.

## Gap Addressed
Existing LLM evaluation benchmarks often assume that test data is unseen during training, but in practice, LLMs are frequently pretrained on vast corpora that include benchmark data. This data contamination undermines the integrity of evaluations and leads to misleading conclusions about model progress. There is a lack of systematic analysis and awareness regarding the extent and impact of such contamination across popular benchmarks.

## Method
The authors conduct a comprehensive analysis to detect benchmark data leakage by searching for exact or near-duplicate matches between benchmark datasets and publicly available pretraining corpora used by well-known LLMs. They introduce a contamination detection framework using fingerprinting techniques such as MinHash and exact n-gram matching. They also propose best practices for benchmark construction, including data provenance tracking and periodic re-evaluation with clean data.

## Datasets and Metrics
**Datasets:** MMLU, BIG-bench, GSM8K, DROP, BoolQ, RACE, SQuAD, ARC, PIQA, HellaSwag, CommonSenseQA, Winogrande

**Metrics:** Exact match (EM), F1 score, contamination rate (fraction of benchmark instances found in training corpora), MinHash similarity

## Results
The study reveals significant contamination across multiple widely used benchmarks, with some datasets showing over 50% overlap with model pretraining data. Models trained on contaminated data exhibit inflated performance, sometimes by large margins, compared to evaluations on clean, uncontaminated subsets. Re-evaluating models on decontaminated benchmarks leads to substantial performance drops, indicating overestimation of capabilities. The findings call into question the reliability of current benchmarking practices and suggest that reported gains may be artifacts of data leakage rather than genuine improvements.

## Limitations
The contamination detection methods rely on publicly available pretraining data, so undetected or private data sources may lead to underestimation of contamination. The study focuses on exact and near-duplicate matches, potentially missing more subtle forms of data influence such as paraphrased or semantically similar content.

## Verification Verdict
REAL (95%) — arXiv: title match (sim=1.00); arXiv: authors match (9/9)

## Links
- [PDF](URL: https://arxiv.org/abs/2311.01964)
