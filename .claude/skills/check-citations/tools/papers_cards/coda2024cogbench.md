---
key: coda2024cogbench
title: CogBench: a large language model walks into a psychology lab
authors: Coda-Forno, J. and Binz, M. and Wang, J. X. and Schulz, E.
year: 2024
venue: Unknown
doi: 
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/2402.18225
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The goal of CogBench is to systematically evaluate large language models (LLMs) using classic cognitive psychology tasks typically administered to humans, in order to assess whether LLMs exhibit human-like cognitive behaviors and reasoning patterns. The authors aim to determine the extent to which LLMs replicate established psychological phenomena such as cognitive biases, heuristics, and memory effects. By benchmarking LLMs against human cognitive performance, the study seeks to inform both cognitive science and AI development.

## Gap Addressed
Prior evaluations of LLMs have largely focused on linguistic and reasoning benchmarks without incorporating well-validated psychological paradigms. There is a lack of standardized, psychology-grounded assessments that probe the cognitive signatures of LLMs in a manner comparable to human studies. Existing benchmarks do not systematically test for the presence of classic cognitive effects such as the anchoring bias, false memories, or the Dunning-Kruger effect in models. This gap limits our understanding of whether LLMs' outputs arise from processes analogous to human cognition.

## Method
The authors construct CogBench, a suite of 14 classic psychology experiments adapted for LLM evaluation, covering domains such as judgment, decision-making, memory, and reasoning. Each task is carefully designed to mirror human experimental protocols, with controlled prompts and multiple replications per model. They evaluate several prominent LLMs (e.g., GPT-3.5, GPT-4, Llama) across these tasks, comparing model outputs to established human behavioral patterns. Statistical analyses are used to determine whether models reproduce known cognitive effects.

## Datasets and Metrics
**Datasets:** N/A (tasks are based on experimental protocols rather than pre-existing datasets)

**Metrics:** Accuracy, response consistency, effect size replication, statistical significance (p-values), correlation with human behavioral patterns, presence/absence of cognitive biases (e.g., anchoring, false memory rates)

## Results
The study finds that LLMs often replicate human-like cognitive biases, such as anchoring effects and false memory generation, with GPT-4 showing the closest alignment to human behavior. Some models exhibit overgeneralization or fail to replicate subtle context-dependent effects observed in humans. Notably, LLMs reproduce the Dunning-Kruger effect, overestimating their performance on self-assessment tasks. However, they sometimes produce inconsistent responses across replications, suggesting instability in cognitive simulation. Overall, LLMs show surface-level mimicry of human cognition but may lack underlying mechanisms.

## Limitations
The experimental setup relies on text-based interaction, which may not fully capture the richness of human cognitive processes involving perception and embodiment. Prompt sensitivity and stochasticity in model outputs can affect reproducibility. The study does not assess developmental or neurocognitive aspects of cognition.

## Verification Verdict
REAL (95%) — arXiv: title match (sim=1.00); arXiv: authors match (4/4)

## Links
- [PDF](URL: https://arxiv.org/abs/2402.18225)
