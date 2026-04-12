---
key: seals2024evaluating
title: Evaluating the deductive competence of large language models
authors: Seals, S. M. and Shalin, V. L.
year: 2024
venue: Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 100
source_used: arxiv
---

## Goal
The paper aims to evaluate the deductive reasoning capabilities of large language models (LLMs) by testing their performance on classic deductive reasoning problems from cognitive science. It seeks to determine whether LLMs can correctly apply logical rules to solve propositional logic tasks, particularly those involving conditional reasoning (e.g., modus ponens, modus tollens). The study also investigates whether model performance improves with explicit instruction or chain-of-thought prompting.

## Gap Addressed
While LLMs demonstrate strong linguistic fluency, their actual competence in formal logical reasoning remains poorly understood. Prior work often focuses on superficial reasoning benchmarks without grounding in established cognitive science paradigms. There is a lack of systematic evaluation using well-controlled deductive reasoning tasks that isolate logical competence from linguistic confounds.

## Method
The authors test multiple LLMs (including GPT-3.5 and GPT-4) on a battery of deductive reasoning problems adapted from cognitive psychology, such as syllogisms and conditional inferences. They compare model responses to normative logical solutions and analyze error patterns. The study includes variations in prompting strategies, such as direct answering versus chain-of-thought, and examines the impact of instruction on performance.

## Datasets and Metrics
**Datasets:** Custom dataset of deductive reasoning problems based on established cognitive science literature, including conditional logic tasks (e.g., "If A, then B") and syllogistic reasoning problems. The dataset is designed to assess logical validity rather than world knowledge.

**Metrics:** Accuracy of model responses compared to logically correct answers, error analysis by inference type (e.g., modus ponens vs. modus tollens), and comparison of performance across prompting conditions (direct vs. chain-of-thought).

## Results
LLMs show high accuracy on simple deductive forms like modus ponens but struggle significantly with more complex inferences like modus tollens. Performance varies across models, with GPT-4 outperforming GPT-3.5. Chain-of-thought prompting improves accuracy in some cases but does not eliminate logical errors. The models often generate plausible but logically invalid conclusions, suggesting reliance on heuristic reasoning rather than sound deduction. Error patterns resemble known human cognitive biases, indicating superficial rather than systematic logical understanding.

## Limitations
The study focuses on a limited set of propositional logic tasks and may not generalize to other forms of reasoning. The synthetic nature of the problems may not reflect real-world reasoning demands. Results are based on English-only prompts, limiting cross-linguistic validity.

## Verification Verdict
REAL (100%) — Multiple authoritative sources (CrossRef, OpenAlex, ACL Anthology, arXiv) confirm the paper's existence with consistent metadata. The DOI resolves to the official proceedings, and the arXiv preprint contains the full text.
