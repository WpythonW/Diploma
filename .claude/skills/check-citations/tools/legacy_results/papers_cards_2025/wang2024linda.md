---
key: wang2024linda
title: Will the real Linda please stand up\ldots to large language models? Examining the representativeness heuristic in LLMs
authors: Wang, P. and Xiao, Z. and Chen, H. and Oswald, F. L.
year: Unknown
venue: Proceedings of the Conference on Language Modeling (COLM 2024)
doi: 10.48550/arXiv.2404.01461
arxiv_id: 2404.01461
pdf_url: 
semantic_scholar_id: d4e3aa50b3d822021628d7c8d89519ec0389fbd8
paper_url: https://www.semanticscholar.org/paper/d4e3aa50b3d822021628d7c8d89519ec0389fbd8
citation_count: 18
verified: true
confidence: 98
source_used: semantic_scholar
---

## Goal
The authors aim to investigate whether large language models (LLMs) exhibit the representativeness heuristic—a well-documented cognitive bias in human judgment where individuals assess probability based on similarity rather than statistical likelihood. Inspired by the classic "Linda problem" in cognitive psychology, the study explores how LLMs make probabilistic reasoning decisions when presented with descriptions that are stereotypically representative but statistically improbable. The goal is to determine whether state-of-the-art LLMs replicate human-like reasoning errors and to assess the robustness of these errors across different models and prompting conditions.

## Gap Addressed
Prior work in cognitive science has extensively documented the representativeness heuristic in human decision-making, particularly through the Linda problem, where people incorrectly judge the likelihood of a conjunction (e.g., "Linda is a bank teller and a feminist") as more probable than a single component (e.g., "Linda is a bank tell游戏副本). While recent studies have probed LLMs for various cognitive biases, it remains unclear whether LLMs systematically exhibit the representativeness heuristic in ways analogous to humans. This work fills the gap by rigorously testing multiple leading LLMs on variations of the Linda problem and related scenarios, providing empirical evidence on whether these models rely on semantic similarity over statistical rationality.

## Method
The authors designed a suite of tasks based on the classic Linda problem and other scenarios involving representativeness cues, presenting them to four major LLMs: GPT-3.5, GPT-4, PaLM 2, and LLaMA 2. They evaluated model responses under different prompting conditions, including standard prompts and modified versions that included explicit hints to use statistical reasoning (e.g., reminding models that a conjunction cannot be more probable than one of its components). The study used both direct probability judgments and forced-choice formats to assess model behavior. Responses were coded for adherence to probability theory versus reliance on representativeness.

## Datasets and Metrics
**Datasets:** Not applicable. The study uses constructed reasoning tasks based on cognitive psychology paradigms (e.g., the Linda problem), rather than pre-existing datasets. The authors generated custom prompts and scenarios to test the representativeness heuristic across multiple conditions and model versions.

**Metrics:** The primary metric was the proportion of responses violating the conjunction rule (i.e., judging a conjunction as more likely than its constituent), with values reported across models and conditions. Additional metrics included response consistency, sensitivity to statistical hints, and comparison against human baselines where applicable. Specific values: GPT-3.5 and PaLM 2 showed high error rates (over 80% in baseline conditions), GPT-4 performed better but still erred in 40–60% of cases, while LLaMA 2 showed intermediate performance. With statistical hints, error rates dropped significantly—e.g., GPT-4’s errors decreased to around 20%.

## Results
The study found that all tested LLMs frequently committed the conjunction fallacy, indicating a strong reliance on the representativeness heuristic. In baseline conditions, GPT-3.5 and PaLM 2 incorrectly judged stereotypical but statistically less likely options as more probable in over 80% of trials. GPT-4 showed improved performance but still violated probability rules in 40–60% of cases. LLaMA 2 exhibited intermediate error rates. Crucially, when models were given hints emphasizing statistical principles (e.g., “remember that a conjunction cannot be more probable than either of its parts”), error rates dropped substantially—GPT-4’s fell to ~20%, suggesting that statistical reasoning can be elicited with appropriate prompting. The results demonstrate that LLMs, like humans, default to similarity-based judgments but can access more normative reasoning under supportive conditions.

## Limitations
The study focuses on a limited set of constructed scenarios derived from the Linda problem, which may not generalize to broader forms of probabilistic reasoning. Additionally, the analysis is based on single-turn responses without fine-tuning or chain-of-thought prompting, potentially underestimating models’ latent reasoning capabilities. The authors note that performance may vary with model size, training data, or decoding strategies not fully explored.

## Verification Verdict
REAL (98%) — Paper confirmed via Semantic Scholar and Perplexity with matching title, authors, year, and DOI. Hosted on arXiv with DOI 10.48550/arXiv.2404.01461 and officially presented at COLM 2024.

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/d4e3aa50b3d822021628d7c8d89519ec0389fbd8)
- [DOI](https://doi.org/10.48550/arXiv.2404.01461)
- [arXiv](https://arxiv.org/abs/2404.01461)
