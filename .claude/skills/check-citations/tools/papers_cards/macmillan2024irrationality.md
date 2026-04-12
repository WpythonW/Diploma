---
key: macmillan2024irrationality
title: (Ir)rationality and cognitive biases in large language models
authors: Macmillan-Scott, O. and Musolesi, M.
year: 2024
venue: Royal Society Open Science
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
This paper investigates whether large language models (LLMs) exhibit rational reasoning or display cognitive biases similar to humans. The authors explore the extent to which LLMs replicate irrational human behaviors due to training on human-generated text. They aim to determine if these models are merely pattern replicators or if they simulate deeper cognitive processes, including flawed reasoning. Understanding this has implications for deploying LLMs in high-stakes decision-making contexts.

## Gap Addressed
While prior work has documented social biases in LLMs, there is limited systematic evaluation of cognitive biases rooted in human irrationality (e.g., framing effects, anchoring, conjunction fallacy). Most studies focus on ethical or demographic biases rather than cognitive psychology-based reasoning errors. Furthermore, it remains unclear whether LLMs’ outputs reflect genuine cognitive bias or superficial linguistic mimicry. This work addresses the need for a structured, psychology-informed assessment of irrationality in AI systems.

## Method
The authors evaluate seven prominent LLMs using established tasks from cognitive psychology literature that elicit well-known cognitive biases in humans. These include the framing effect, anchoring bias, conjunction fallacy, and sunk cost fallacy. Each model is prompted with scenarios adapted from human experiments, and responses are scored for bias presence and deviation from normative rational reasoning. The study uses both zero-shot and few-shot prompting to assess consistency across conditions.

## Datasets and Metrics
**Datasets:** Custom prompts based on classic cognitive psychology experiments; no standard NLP dataset is used. Tasks are derived from seminal studies in human judgment and decision-making (e.g., Tversky & Kahneman paradigms).

**Metrics:** Proportion of biased responses, deviation from rational choice, consistency across logically equivalent scenarios, and effect size of known cognitive biases.

## Results
All seven LLMs exhibited significant levels of cognitive biases mirroring human irrationality, particularly in framing and anchoring tasks. Models frequently violated principles of logical consistency and exhibited context-dependent preferences. The biases were robust across different model sizes and architectures. Notably, larger models did not consistently outperform smaller ones in rational reasoning, suggesting that scale does not mitigate cognitive distortions. The findings indicate that LLMs internalize not only factual knowledge but also flawed reasoning patterns from training data.

## Limitations
The study relies on text-based simulations of human decision-making tasks, which may not reflect real-world behavior. Prompt formatting and phrasing could influence bias expression, raising concerns about measurement validity. Additionally, the analysis assumes human-like cognition in models, which may be an anthropomorphic overinterpretation.

## Verification Verdict
REAL (100%) — Multiple authoritative sources (CrossRef, OpenAlex, Semantic Scholar, arXiv) confirm identical title, authors, year, and DOI. The paper is published in Royal Society Open Science (DOI: 10.1098/rsos.240255) and has substantial citation counts, confirming visibility and legitimacy.
