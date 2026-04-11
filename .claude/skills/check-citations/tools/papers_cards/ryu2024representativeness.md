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
verified: false
confidence: 92
source_used: perplexity
---

## Goal
The authors aim to investigate the presence and impact of representativeness heuristic (RH) biases in large language models (LLMs), focusing on how these cognitive biases lead to reasoning errors. They seek to understand the extent to which LLMs commit classic fallacies—such as conjunction and disjunction fallacies—when making probabilistic judgments. The study also explores methods to mitigate these biases, particularly through tailored prompting strategies, with the broader goal of improving the reliability and logical consistency of LLM reasoning in uncertain or ambiguous contexts.

## Gap Addressed
Prior work has documented human cognitive biases like representativeness heuristics in judgment and decision-making, but less is known about how these biases manifest in LLMs. While recent studies have begun examining reasoning flaws in models, there remains a lack of systematic evaluation across multiple types of RH-related fallacies. Existing prompting techniques such as zero-shot chain-of-thought (CoT) do not specifically address representativeness biases, leaving a gap in targeted mitigation strategies. This work addresses that gap by introducing a dedicated framework and dataset (ReHeAT) to evaluate and reduce RH-induced errors in LLMs.

## Method
The authors introduce ReHeAT, a dataset designed to test six types of representativeness heuristics in LLMs, including conjunction and disjunction fallacies. They evaluate multiple LLMs using this dataset to measure error rates in reasoning tasks. To mitigate these errors, they propose a novel prompting method called zero-shot-RH, which reframes queries to explicitly discourage reliance on representativeness cues. This method is compared against standard zero-shot and zero-shot-CoT baselines to assess its effectiveness in improving logical consistency and reducing cognitive-style biases in model outputs.

## Datasets and Metrics
**Datasets:** ReHeAT (Representativeness Heuristic Analysis Test), a manually constructed dataset covering six types of representativeness heuristics; specific size and split details are not provided in the search results. The dataset is used to evaluate model performance across fallacy types, with a focus on conjunction, disjunction, and base rate neglect scenarios.

**Metrics:** Correct reasoning accuracy; improvement in correct reasoning measured as +0.145 over zero-shot-CoT; improvement in correct reasoning by sex subgroup measured as +0.277; performance comparison across fallacy types (e.g., poor performance on conjunction and disjunction fallacies relative to base rate fallacies).

## Results
The study finds that LLMs exhibit significant vulnerability to representativeness heuristics, particularly in conjunction and disjunction fallacy tasks, where performance is notably worse than on base rate fallacies. The proposed zero-shot-RH prompt outperforms both zero-shot and zero-shot-CoT baselines, improving correct reasoning by 0.145 and achieving a 0.277 gain in correct reasoning when analyzing by sex subgroups. Results indicate that targeted prompting can reduce reliance on heuristic-based reasoning, suggesting that LLMs can be guided toward more logically consistent responses without fine-tuning. The ReHeAT dataset effectively exposes these biases across multiple reasoning scenarios.

## Limitations
The dataset size and diversity may limit generalizability across all types of reasoning tasks. The study focuses on English-language models and may not capture cross-cultural variations in heuristic reasoning. Additionally, the zero-shot-RH method, while effective, has not been tested across a wide range of model architectures or downstream applications.

## Verification Verdict
FAKE (92%) — The paper 'A Study on the Representativeness Heuristics Problem in Large Language Models' appears in DOAJ, but the attribution to authors Ryu et al. and publication in IEEE Access 2024 cannot be verified. The cited arXiv ID (2404.01461v4) belongs to a different paper. Absence of DOI, IEEE Xplore entry, and inconsistent metadata indicate the bibliography entry is fabricated or severely misattributed.
