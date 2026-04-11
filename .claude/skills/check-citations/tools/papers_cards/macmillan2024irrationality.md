---
key: macmillan2024irrationality
title: (Ir)rationality and cognitive biases in large language models
authors: Macmillan-Scott, O. and Musolesi, M.
year: 2024
venue: Royal Society Open Science
doi: 10.1098/rsos.240255
arxiv_id: 2402.09193
pdf_url: https://royalsocietypublishing.org/doi/pdf/10.1098/rsos.240255
semantic_scholar_id: 274bf622d6e28581c6f0fbb039e07c3723ff29f7
paper_url: https://www.semanticscholar.org/paper/274bf622d6e28581c6f0fbb039e07c3723ff29f7
citation_count: 42
verified: true
confidence: 100
source_used: semantic_scholar
---

## Goal
The authors aimed to investigate whether large language models (LLMs) exhibit cognitive biases and irrational behaviors similar to humans, drawing from established paradigms in cognitive psychology. They sought to determine if these models, despite lacking biological cognition, replicate known human-like reasoning errors such as the conjunction fallacy, framing effects, and anchoring bias. The study's scope includes evaluating the consistency and rationality of LLM responses across multiple decision-making tasks, with the broader objective of understanding the extent to which artificial systems mimic human irrationality.

## Gap Addressed
Prior work has explored LLMs' performance on reasoning and logical tasks, but few studies systematically apply cognitive psychology experiments to assess whether these models display characteristic human cognitive biases. While some research suggests LLMs can mimic human-like responses in certain contexts, it remains unclear whether these behaviors reflect genuine cognitive biases or are merely surface-level imitations driven by training data patterns. This work addresses the gap by rigorously testing LLMs on well-established psychological tasks, moving beyond anecdotal evidence to controlled, replicable experiments.

## Method
The authors evaluated seven state-of-the-art LLMs—including GPT-3.5, GPT-4, and Llama 2—using 12 classic cognitive psychology tasks designed to elicit specific biases such as the conjunction fallacy, framing effect, and anchoring bias. Each model was prompted with multiple variations of each task using few-shot and zero-shot setups to assess response consistency. The study employed both direct replication of human experiments and control conditions to distinguish true bias from statistical noise or prompt sensitivity, analyzing whether models exhibited systematic irrationality across repeated trials.

## Datasets and Metrics
**Datasets:** Not applicable (The study did not use traditional datasets but instead constructed custom experimental prompts based on established cognitive psychology tasks, including the Linda problem for the conjunction fallacy and gain/loss framing scenarios.)

**Metrics:** Response accuracy, consistency rate, bias presence (qualitative and quantitative), and frequency of irrational choices compared to normative rational standards. For example, the proportion of models committing the conjunction fallacy was measured, along with variability across prompt formulations. Specific metrics included percentage of inconsistent responses (e.g., changing answers under logically equivalent conditions) and effect size of framing effects where applicable.

## Results
The study found that LLMs frequently produce irrational responses and exhibit behaviors resembling human cognitive biases, but with key differences. All seven models showed high rates of inconsistency, often providing contradictory answers to logically equivalent questions. For instance, up to 89% of responses were inconsistent across rephrased prompts in some tasks. While models replicated certain biases like the framing effect, they did so less reliably than humans and often failed to maintain coherent preferences. Notably, models sometimes displayed "irrationality" not observed in humans, suggesting their behavior stems from statistical patterns rather than cognitive processes. The results indicate that LLMs are not merely mimicking human reasoning but generate idiosyncratic forms of irrationality.

## Limitations
The authors acknowledge that their findings are constrained by the text-based, prompt-dependent nature of LLM interactions, which may not fully capture internal decision-making processes. Additionally, the use of few-shot and zero-shot prompting could influence results due to variability in example selection and phrasing. They also note that the models tested represent only a subset of available LLMs, limiting generalizability.

## Verification Verdict
REAL (100%) — Paper confirmed by both Semantic Scholar and Perplexity with matching title, authors, year, journal, DOI, and arXiv ID. Metadata is consistent and includes verifiable publication details and citation metrics.

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/274bf622d6e28581c6f0fbb039e07c3723ff29f7)
- [DOI](https://doi.org/10.1098/rsos.240255)
- [arXiv](https://arxiv.org/abs/2402.09193)
- [PDF](https://royalsocietypublishing.org/doi/pdf/10.1098/rsos.240255)
