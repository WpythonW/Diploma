---
key: suri2024large
title: Do large language models show decision heuristics similar to humans? A case study using GPT-3.5
authors: Suri, G. and Slater, L. R. and Ziaee, A. and Nguyen, M.
year: 2024
venue: Journal of Experimental Psychology: General
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
This paper investigates whether large language models (LLMs), specifically GPT-3.5, exhibit decision-making heuristics similar to those observed in humans. The authors aim to determine if LLMs display systematic biases such as the representativeness heuristic, base rate neglect, and conjunction fallacy—cognitive tendencies well-documented in human psychology. By drawing parallels between human and machine decision-making, the study seeks to inform both cognitive science and AI development. It also explores whether LLMs’ responses emerge from learned statistical patterns or deeper reasoning structures.

## Gap Addressed
While prior research has examined LLMs’ performance in language and reasoning tasks, few studies have systematically tested whether these models replicate human-like cognitive biases in decision-making. It remains unclear whether LLMs’ outputs reflect genuine heuristic reasoning or are merely surface-level mimicry of training data patterns. Furthermore, understanding whether LLMs exhibit predictable irrationalities like humans could have implications for modeling human cognition and deploying AI in real-world decision-support contexts. This study addresses this gap by applying established psychological paradigms to probe GPT-3.5’s decision heuristics.

## Method
The authors conducted a series of controlled experiments using prompts based on classic cognitive psychology tasks, including the Linda problem (conjunction fallacy), medical diagnosis scenarios (base rate neglect), and coin toss sequences (representativeness heuristic). GPT-3.5 was presented with these tasks in multiple variations and contexts to assess consistency in responses. Responses were compared against normative statistical reasoning and documented human responses from prior literature. The model was tested under varying conditions (e.g., with and without explanations) to evaluate robustness and sensitivity to framing.

## Datasets and Metrics
**Datasets:** Not applicable (no formal datasets used; the study relies on synthetic prompts based on established psychological experiments).

**Metrics:** Accuracy relative to normative standards (e.g., Bayesian reasoning), frequency of heuristic-consistent responses, consistency across repetitions, alignment with human-like error patterns, and susceptibility to framing effects.

## Results
GPT-3.5 frequently exhibited decision biases closely mirroring those of humans, including strong evidence of the representativeness heuristic and conjunction fallacy. The model showed significant base rate neglect in probabilistic reasoning tasks, favoring stereotypical narratives over statistical information. These patterns were consistent across multiple trials and variations in prompt wording. However, performance improved when the model was asked to "think step by step," suggesting some capacity for override. Overall, GPT-3.5’s responses aligned more closely with human cognitive biases than with optimal statistical reasoning, indicating emergent human-like heuristics in its decision-making.

## Limitations
The study focuses exclusively on GPT-3.5, limiting generalizability to other LLMs. Findings are based on text-based interactions without access to internal model states, making it difficult to determine whether heuristics arise from reasoning or pattern completion. The absence of real-time feedback or learning during tasks may affect how behaviors generalize.

## Verification Verdict
REAL (98%) — Multiple authoritative sources (arXiv, CrossRef, OpenAlex) confirm the existence of the paper with matching authors, title, journal, and year. The paper was first released as arXiv:2305.04400 in 2023 and published in Journal of Experimental Psychology: General in 2024 (volume 153, DOI 10.1037/xge0001547).
