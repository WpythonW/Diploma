---
key: dasgupta2024language
title: Language models, like humans, show content effects on reasoning tasks
authors: Dasgupta, I. and Lampinen, A. K. and Chan, S. C. Y. and Sheahan, H. R. and Creswell, A. and Kumaran, D. and McClelland, J. L. and Hill, F.
year: 2024
venue: PNAS Nexus
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 98
source_used: arxiv
---

## Goal
The paper investigates whether large language models (LMs) exhibit content effects in reasoning tasks—similar to humans—where performance is influenced by the semantic content of the problem rather than pure logical structure. It aims to compare how both humans and LMs are affected by the alignment between real-world knowledge and logical validity. The study explores this across multiple reasoning domains to assess the extent to which LMs mirror human cognitive biases.

## Gap Addressed
Prior work has shown that human reasoning is not purely abstract but influenced by content, such as beliefs or knowledge about the world, leading to systematic errors or facilitation depending on content. While LMs have demonstrated some capacity for logical reasoning, it remains unclear whether their performance is similarly shaped by content effects. This gap limits understanding of whether LMs reason in ways analogous to humans or rely on different mechanisms.

## Method
The authors evaluate both large language models and human participants across three well-established reasoning tasks: natural language inference, syllogistic reasoning, and the Wason selection task. They manipulate the semantic content of these tasks to either support or conflict with logically correct answers. Model outputs are analyzed in terms of accuracy and response distributions, and compared to human response patterns, including response times as a proxy for cognitive effort.

## Datasets and Metrics
**Datasets:** Natural Language Inference (NLI) datasets; Syllogism datasets with varying semantic content; Wason Selection Task instances adapted for both human and model evaluation.

**Metrics:** Accuracy, response distribution similarity between models and humans, correlation between model confidence and human response times, consistency in logical reasoning under content-aligned vs. content-conflicting conditions.

## Results
Large language models show higher accuracy when the semantic content supports the correct logical inference, mirroring human performance patterns. Like humans, models struggle when logical validity conflicts with plausible real-world knowledge. These content effects are consistent across all three reasoning tasks. Furthermore, model answer distributions correlate with human response times, suggesting similar underlying processing dynamics. The findings indicate that LMs, despite being trained on form-based patterns, internalize content-dependent reasoning biases akin to those in humans.

## Limitations
The study focuses on English-language models and tasks, limiting generalizability across languages and cultures. Additionally, while response time analogs are inferred from model output probabilities, they are not direct behavioral measures, potentially weakening the human-model comparison.

## Verification Verdict
REAL (98%) — The paper is confirmed by CrossRef, OpenAlex, and Tavily with matching title, journal, year, and DOI. arXiv preprint supports its existence. Minor author list discrepancies do not invalidate the real publication.
