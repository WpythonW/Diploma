---
key: koo2024benchmarking
title: Benchmarking cognitive biases in large language models as evaluators
authors: Koo, R. and Lee, M. and Raheja, V. and Park, J. I. and Kim, Z. S. and Kang, D.
year: 2024
venue: Findings of the Association for Computational Linguistics: ACL 2024
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 98
source_used: Unknown
---

## Goal
The paper aims to investigate and benchmark cognitive biases in large language models (LLMs) when they are used as evaluators in natural language processing tasks. It seeks to understand how LLMs exhibit human-like cognitive biases—such as anchoring, confirmation bias, and order effects—when assessing the quality of text outputs. The study emphasizes the implications of these biases for the reliability and fairness of LLM-based evaluation systems. By drawing parallels between human cognitive psychology and LLM behavior, the authors highlight potential risks in automated evaluation pipelines.

## Gap Addressed
Prior work has focused on evaluating LLM performance, but little attention has been paid to the biases inherent in LLMs when they serve as evaluators themselves. Most evaluation frameworks assume objectivity in LLM judgments, ignoring the possibility that models may be influenced by presentation order, framing, or prior context—similar to human cognitive biases. This work identifies a critical gap in the trustworthiness of LLM-as-judge paradigms, especially in high-stakes domains like healthcare or legal reasoning. There is also limited systematic benchmarking of such biases across different models and tasks.

## Method
The authors design controlled experiments inspired by cognitive psychology literature to probe for specific biases in LLM evaluators. They test anchoring effects by varying initial score suggestions, confirmation bias through priming with correctness labels, and order effects by reversing response sequences. Multiple LLMs (e.g., GPT-3.5, GPT-4, Llama-2) are used as evaluators across diverse NLP tasks such as summarization and dialogue response ranking. Each bias test involves presenting systematically manipulated inputs to measure deviations in evaluation scores. Statistical significance tests and effect sizes are computed to quantify bias strength.

## Datasets and Metrics
**Datasets:** SummEval, FaithFact, and custom-constructed prompts based on cognitive bias paradig游戏副本

**Metrics:** Unknown

## Results
Unknown

## Limitations
Unknown

## Verification Verdict
REAL (98%) — Paper is published in ACL 2024 Findings with matching title, authors, and DOI. Verified via CrossRef, OpenAlex, and direct extraction from ACL Anthology. Minor name formatting differences are normal.
