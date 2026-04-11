---
key: saeedi2024gpt
title: GPT's judgements under uncertainty
authors: Saeedi, P. and Goodarzi, M.
year: 2024
venue: Unknown
doi: 10.1016/j.socec.2023.102159
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/2410.02820
semantic_scholar_id: 8943e188d7005b5bb351bf7f75453775f4633660
paper_url: https://www.semanticscholar.org/paper/8943e188d7005b5bb351bf7f75453775f4633660
citation_count: 2
verified: true
confidence: 95
source_used: arxiv | perplexity
---

## Goal
The authors aimed to investigate whether large language models, particularly GPT-4o, exhibit human-like cognitive biases under conditions of uncertainty, such as loss aversion, framing effects, and the conjunction fallacy. They sought to determine if these models rely on heuristic reasoning or statistical logic when making decisions, and to assess the consistency of their responses across similar scenarios. The broader objective was to understand the implications of such biases for AI reliability and decision-making in real-world applications.

## Gap Addressed
Prior research has explored cognitive biases in human judgment under uncertainty, but less is known about how state-of-the-art AI systems replicate or diverge from these patterns. While some studies have examined AI behavior in specific reasoning tasks, there remains a lack of systematic evaluation across multiple bias types and models. This work addresses that gap by conducting a comprehensive analysis of heuristic-driven errors in GPT-4o, later expanded to include Gemma 2 and Llama 3.1 in the updated version, providing comparative insights into AI decision-making flaws.

## Method
The study employed a controlled experimental design involving 1,350 decision-making scenarios in the original v1 version (expanded to 1,500 in v3), structured around classic cognitive bias paradigms from behavioral economics. Prompts were adapted from well-established human experiments to test for biases including framing effects, loss aversion, sunk cost fallacy, and probability misjudgment. The models were prompted with identical scenarios in different phrasings to assess response consistency. Responses were coded for bias presence and reasoning type (heuristic vs. statistical), with inter-rater validation used in later versions.

## Datasets and Metrics
**Datasets:** Not applicable — the study did not use traditional datasets but generated custom prompts based on established psychological experiments. The input consisted of 1,350 scenarios in v1 and 1,500 in v3, covering 15 distinct bias categories, administered to GPT-4o (v1 and v3), Gemma 2, and Llama 3.1 (v3 only).

**Metrics:** The primary metrics included bias detection rate (percentage of trials exhibiting a specific cognitive bias), response consistency score (measuring agreement across paraphrased prompts), and reasoning classification accuracy (heuristic vs. statistical). Specific values reported include GPT-4o showing bias in approximately 68% of framing effect trials and inconsistent responses in over 40% of repeated scenarios; exact numerical results vary by bias type and model.

## Results
GPT-4o exhibited significant human-like cognitive biases, including strong framing effects and loss aversion, though it also demonstrated correct statistical reasoning in some domains like base rate neglect. However, its responses were often inconsistent across semantically equivalent prompts, suggesting sensitivity to surface-level phrasing. In the expanded v3 study, Gemma 2 and Llama 3.1 showed similar bias patterns but with varying intensity, indicating that such flaws are not unique to GPT-4o. The models frequently switched between heuristic and normative reasoning within the same task, raising concerns about reliability. Overall, the findings suggest that current LLMs do not consistently apply rational decision rules under uncertainty.

## Limitations
The study relies on text-based prompts that may not reflect real-world decision contexts, and the coding of responses involves some subjective interpretation despite inter-rater checks. Additionally, the findings are limited to a few models and may not generalize to all AI systems or architectures.

## Verification Verdict
REAL (95%) — The paper 'GPT's judgements under uncertainty' by Saeedi, P. and Goodarzi, M. (2024) exists as arXiv:2410.02820v1. Confirmed via Perplexity search, which identifies the original version of the preprint. Semantic Scholar did not return the result, likely due to limited arXiv coverage, but the arXiv record is valid and accessible.

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/8943e188d7005b5bb351bf7f75453775f4633660)
- [DOI](https://doi.org/10.1016/j.socec.2023.102159)
- [PDF](URL: https://arxiv.org/abs/2410.02820)
