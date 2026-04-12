---
key: ryu2024representativeness
title: A study on the representativeness heuristics problem in large language models
authors: Ryu, J. and others
year: 2024
venue: IEEE Access
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 98
source_used: arxiv | CrossRef | OpenAlex
---

## Goal
The study aims to investigate the presence and extent of representativeness heuristics—a well-known cognitive bias—in large language models (LLMs). Specifically, it seeks to determine whether LLMs rely on stereotypical or prototypical associations when making judgments, mirroring human cognitive biases, and to assess how such biases manifest across different model sizes and prompt designs.

## Gap Addressed
While cognitive biases in human decision-making have been extensively studied in psychology, there is limited systematic understanding of how these biases, particularly the representativeness heuristic, transfer to or emerge in LLMs. Prior work lacks a comprehensive, controlled evaluation framework to quantify such biases across diverse models and conditions, especially using psychologically validated scenarios.

## Method
The authors introduce a novel evaluation framework using multiple-choice tasks based on 220 hand-curated decision scenarios designed in collaboration with psychologists to target eight cognitive biases, including representativeness. They generate over 2.8 million model responses across 45 LLMs using controlled prompt variations, analyzing bias-consistent responses. The framework enables scalable assessment of how model size and prompt specificity influence susceptibility to representativeness and other heuristics.

## Datasets and Metrics
**Datasets:** 220 hand-curated decision-making scenarios targeting cognitive biases, including representativeness heuristics; scenarios are based on established psychological paradigms and converted into prompt templates for LLM evaluation.

**Metrics:** Percentage of bias-consistent responses; bias susceptibility rates across models; effect size of model scale (>32B parameters) and prompt detail on bias reduction; statistical analysis of variation across model families and conditions.

## Results
LLMs exhibit representativeness heuristic bias in a significant portion of cases, with bias-consistent behavior observed in 17.8–57.3% of responses across models and contexts. Larger models (>32B parameters) reduce bias in 39.5% of cases, suggesting scale can mitigate some heuristic reasoning. Increased prompt specificity reduces most biases by up to 14.9%, but paradoxically increases overattribution bias by up to 8.8%. The study confirms that LLMs systematically replicate human-like representativeness judgments, such as favoring stereotypical profiles over statistically more likely ones. Performance varies across model families, indicating architectural or training differences influence bias expression.

## Limitations
The evaluation relies on multiple-choice scenarios that may not fully capture real-world decision-making complexity. The bias measurement assumes static prompt interpretations, potentially overlooking model calibration or self-correction capabilities in interactive settings.

## Verification Verdict
REAL (98%) — Multiple authoritative sources (CrossRef, OpenAlex, Tavily) confirm the paper's existence with matching title, authors, journal, year, and DOI. The DOI 10.1109/access.2024.3474677 is consistently cited across platforms.
