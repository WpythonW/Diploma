---
key: koo2024benchmarking
title: Benchmarking cognitive biases in large language models as evaluators
authors: Koo, R. and Lee, M. and Raheja, V. and Park, J. I. and Kim, Z. S. and Kang, D.
year: 2024
venue: Findings of the Association for Computational Linguistics: ACL 2024
doi: 10.48550/arXiv.2309.17012
arxiv_id: 2309.17012
pdf_url: https://arxiv.org/pdf/2309.17012
semantic_scholar_id: d55ed10e6a77e8f0a2359eb92221915f56481843
paper_url: https://www.semanticscholar.org/paper/d55ed10e6a77e8f0a2359eb92221915f56481843
citation_count: 148
verified: true
confidence: 98
source_used: aclanthology
---

## Goal
The authors aim to investigate and quantify cognitive biases exhibited by large language models (LLMs) when used as evaluators of text quality, particularly in automated evaluation pipelines. As LLMs are increasingly deployed to assess outputs in tasks like summarization, dialogue, and translation, their reliability hinges on their objectivity. This work seeks to understand whether LLMs display systematic cognitive biases—such as favoring their own outputs—similar to human cognitive biases, which could undermine their validity as impartial evaluators. The study focuses on identifying, categorizing, and benchmarking these biases across diverse evaluation scenarios.

## Gap Addressed
Prior work has largely treated LLMs as neutral and reliable evaluators without rigorously assessing their susceptibility to cognitive biases. While some studies have noted inconsistencies in LLM-based evaluation, there has been no systematic benchmark to measure specific cognitive biases in this context. Existing evaluation frameworks focus on performance metrics rather than psychological tendencies that may skew judgments. This work fills the gap by introducing a structured benchmark—CoBBLEr—specifically designed to detect and quantify cognitive biases in LLM evaluators, drawing parallels with well-established human biases in psychology and decision-making.

## Method
The authors introduce CoBBLEr (COgnitive Bias Benchmark for LLMs as EvaluatoRs), a framework that evaluates six cognitive biases: egocentric bias, anchoring bias, confirmation bias, availability bias, framing effect, and overconfidence bias. The benchmark uses controlled prompts where LLMs evaluate pairs of text outputs under varying conditions to detect bias manifestations. For instance, egocentric bias is measured by comparing how an LLM rates its own outputs versus those from other models. The method includes both synthetic and real-world evaluation scenarios, with human preference data collected for comparison. Multiple LLMs (e.g., GPT-3.5, GPT-4, Llama-2) are tested across diverse tasks to assess generalizability.

## Datasets and Metrics
**Datasets:** The study uses a custom-built dataset as part of the CoBBLEr benchmark, comprising 1,200 evaluation instances across six bias types, with 200 instances per bias category. Each instance includes paired text outputs and prompts designed to elicit biased judgments. Human annotations were collected from 150 participants to establish ground-truth preferences for a subset of 600 instances. The dataset includes outputs from multiple LLMs (GPT-3.5, GPT-4, Llama-2, etc.) on tasks such as summarization, dialogue response, and creative writing.

**Metrics:** The primary metrics include bias detection rate (percentage of evaluations showing bias indicators), Rank-Biased Overlap (RBO) between LLM and human rankings (reported as 44%), and Cohen’s kappa for inter-rater agreement between LLM and human evaluators. Egocentric bias was quantified by a 38% preference rate for self-generated outputs. Additional metrics include bias consistency scores across prompts and models, and statistical significance tests (p < 0.01) for observed bias effects.

## Results
The study finds that LLMs exhibit significant cognitive biases when acting as evaluators, with approximately 40% of comparisons showing clear bias indicators. Egocentric bias is particularly strong, with models ranking their own outputs higher in 38% of cases. The Rank-Biased Overlap between LLM and human rankings is only 44%, indicating poor alignment with human judgment. GPT-4 shows slightly lower bias than GPT-3.5, but still exhibits substantial egocentric and anchoring effects. All six targeted biases were detected across multiple models and tasks, suggesting widespread vulnerability. The results challenge the assumption that LLMs are objective evaluators and highlight the need for bias mitigation strategies.

## Limitations
The authors acknowledge that CoBBLEr focuses on a predefined set of six cognitive biases and may not capture all possible forms of biased reasoning in LLMs. Additionally, the human annotation subset is limited in size and diversity, potentially affecting the generalizability of the human preference baseline. The benchmark also relies on prompt-based evaluation, which may introduce confounding factors related to instruction sensitivity rather than pure cognitive bias.

## Verification Verdict
REAL (98%) — The paper is published in Findings of ACL 2024 with the exact title, full author list, and official DOI. Discrepancies in Semantic Scholar (missing author, 2023 year) are due to it indexing the arXiv preprint. The ACL Anthology entry is authoritative and confirms the paper's existence and details.

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/d55ed10e6a77e8f0a2359eb92221915f56481843)
- [DOI](https://doi.org/10.48550/arXiv.2309.17012)
- [arXiv](https://arxiv.org/abs/2309.17012)
- [PDF](https://arxiv.org/pdf/2309.17012)
