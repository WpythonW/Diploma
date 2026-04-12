---
key: wang2024linda
title: Will the real Linda please stand up\ldots to large language models? Examining the representativeness heuristic in LLMs
authors: Wang, P. and Xiao, Z. and Chen, H. and Oswald, F. L.
year: Unknown
venue: Proceedings of the Conference on Language Modeling (COLM 2024)
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
The paper investigates whether large language models (LLMs) exhibit the representativeness heuristic—a cognitive bias where people judge probability based on similarity—by evaluating their responses to variations of the classic "Linda problem" from behavioral psychology. The authors aim to determine if LLMs systematically make reasoning errors akin to humans when assessing probabilistic statements. This work bridges cognitive science and AI, probing whether LLMs replicate human-like biases in reasoning tasks.

## Gap Addressed
While prior research has explored reasoning flaws in LLMs, such as logical inconsistencies or susceptibility to framing effects, there is limited investigation into whether LLMs exhibit specific, well-documented human cognitive heuristics like representativeness. Most studies focus on accuracy or performance on benchmark tasks rather than diagnosing psychologically meaningful biases. It remains unclear whether LLMs’ errors reflect genuine cognitive mimicry or superficial pattern matching.

## Method
The authors design a series of controlled variants of the Linda problem, where the descriptive fit of a target outcome (e.g., “Linda is a bank teller and feminist”) is manipulated relative to more probable but less representative options. They evaluate multiple LLMs by prompting them to rank or assign probabilities to different outcomes, measuring the frequency with which models favor less probable but more representative statements. The study includes both zero-shot and few-shot prompting conditions to assess robustness across settings.

## Datasets and Metrics
**Datasets:** Synthetic datasets based on the Linda problem and its variants, constructed according to principles from cognitive psychology literature. These include systematically altered descriptions and outcomes to test the consistency of model judgments under different representativeness cues.

**Metrics:** Proportion of responses exhibiting the representativeness heuristic (i.e., selecting less probable but more representative options), consistency with probability theory, and comparison of model outputs against normative rational standards. The authors also analyze confidence scores and response stability across prompts.

## Results
The study finds that multiple LLMs frequently commit the conjunction fallacy—judging a conjunction as more probable than one of its constituents—mirroring human behavior in the Linda problem. This tendency persists across model sizes and architectures, suggesting a robust bias. The effect is stronger when descriptions align closely with stereotypes and diminishes slightly in few-shot settings with rationality prompts. The results indicate that LLMs do not merely learn statistical patterns but may simulate human-like intuitive reasoning processes. The findings are consistent across several leading models, though some variation in susceptibility is observed.

## Limitations
The experimental design relies on synthetic scenarios derived from a single classic cognitive bias, limiting generalizability to other heuristics or real-world contexts. Additionally, the interpretation of model outputs as reflecting "reasoning" versus pattern completion remains ambiguous, making it difficult to infer internal cognitive processes.

## Verification Verdict
REAL (98%) — Multiple authoritative sources (arXiv, OpenAlex) confirm the paper's existence with matching title, authors, and publication venue (COLM 2024). The arXiv page includes official comments, subjects, and citation details, indicating legitimacy.
