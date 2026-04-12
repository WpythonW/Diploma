---
key: binz2023using
title: Using cognitive psychology to understand GPT-3
authors: Binz, M. and Schulz, E.
year: 2023
venue: Proceedings of the National Academy of Sciences
doi: 10.1073/pnas.2218523120
arxiv_id: 2206.14576
pdf_url: https://doi.org/10.1073/pnas.2218523120
semantic_scholar_id: fa3609e00f9f422a309c621a35394c4a38f88687
paper_url: https://www.semanticscholar.org/paper/fa3609e00f9f422a309c621a35394c4a38f88687
citation_count: 678
verified: true
confidence: 98
source_used: semantic_scholar
---

## Goal
The authors aim to investigate whether GPT-3 exhibits human-like cognitive processes by applying experimental paradigms from cognitive psychology. They seek to determine if the model's behavior aligns with established patterns of human decision-making, information search, deliberation, and causal reasoning. By borrowing well-validated psychological tasks, the study bridges AI and cognitive science to assess whether GPT-3’s responses reflect psychologically meaningful computations rather than mere statistical pattern matching. The broader goal is to evaluate the extent to which large language models can serve as models of human cognition.

## Gap Addressed
Prior evaluations of large language models have largely focused on linguistic performance, benchmarks, or machine learning metrics, without probing deeper cognitive mechanisms. While GPT-3 has demonstrated impressive language capabilities, it remains unclear whether its outputs emerge from processes analogous to human cognition. Existing work in AI interpretability often lacks grounding in psychological theory, missing opportunities to compare model behavior with empirically validated human cognitive patterns. This paper addresses that gap by systematically applying cognitive psychology methods to test for human-like reasoning in a machine learning model.

## Method
The authors administered a series of classic cognitive psychology experiments to GPT-3, including tasks involving the value of information, sequential decision-making under uncertainty, belief updating, and causal reasoning. They presented GPT-3 with scenarios adapted from human behavioral studies, such as medical diagnosis tasks and information search dilemmas, and compared its responses to typical human behavior. The model was prompted with instructions and contexts identical or closely matched to those used with human participants, without fine-tuning or parameter adjustments. Responses were analyzed qualitatively and quantitatively for alignment with known cognitive effects.

## Datasets and Metrics
**Datasets:** Not applicable. The study did not use traditional datasets but instead constructed experimental stimuli based on established cognitive psychology tasks (e.g., medical diagnosis, urn-and-balls probability tasks, and information search paradigms) drawn from the literature.

**Metrics:** The evaluation relied on qualitative and quantitative comparisons between GPT-3’s responses and human behavioral data from prior psychological studies. Metrics included choice proportions, information search patterns, probability judgments, and alignment with known cognitive biases (e.g., probability matching, conservatism in belief updating). No standard NLP metrics (e.g., accuracy, perplexity) were used.

## Results
GPT-3 closely replicated human-like behavior across multiple cognitive tasks: it exhibited probability matching, demonstrated appropriate valuation of information, updated beliefs in a Bayesian-consistent direction (though with conservatism), and showed structured causal reasoning. In sequential decision-making tasks, GPT-3 balanced exploration and exploitation similarly to humans. It also displayed context-sensitive deliberation patterns, such as reduced information search when decision outcomes were clear. However, the model occasionally produced inconsistent responses across repeated trials, suggesting sensitivity to phrasing and stochasticity in generation. Overall, GPT-3 mirrored a range of well-documented cognitive phenomena without explicit training on human behavioral data.

## Limitations
The authors acknowledge that GPT-3’s behavior, while human-like in many cases, may stem from learned surface-level patterns rather than genuine cognitive simulation. Additionally, the model’s responses can be sensitive to prompt wording and randomness in decoding, leading to variability that differs from human consistency. The study also does not address developmental or neurocognitive aspects of human reasoning.

## Verification Verdict
REAL (98%) — Paper confirmed by Semantic Scholar and web search with matching title, authors, venue, DOI, and publication details. Discrepancy in year (2022 vs 2023) is due to online preprint vs. final publication date, which is standard in academic publishing.

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/fa3609e00f9f422a309c621a35394c4a38f88687)
- [DOI](https://doi.org/10.1073/pnas.2218523120)
- [arXiv](https://arxiv.org/abs/2206.14576)
- [PDF](https://doi.org/10.1073/pnas.2218523120)
