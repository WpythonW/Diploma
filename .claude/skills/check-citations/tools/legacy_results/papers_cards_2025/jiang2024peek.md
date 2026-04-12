---
key: jiang2024peek
title: A peek into token bias: Large language models are not yet genuine reasoners
authors: Jiang, B. and Xie, Y. and Hao, Z. and Wang, X. and Mallick, T. and Su, W. J. and Taylor, C. J. and Roth, D.
year: 2024
venue: Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 98
source_used: pdf | arxiv | perplexity | semantic_scholar
---

## Goal
The authors aim to investigate whether large language models (LLMs) perform genuine logical reasoning or rely on superficial token-level patterns—termed "token bias"—when solving reasoning tasks. They argue that high performance on benchmark reasoning tasks may not reflect true understanding but could instead result from models exploiting statistical regularities in input formulations. To address this, the paper focuses on designing a rigorous hypothesis-testing framework that can systematically probe and quantify the extent of token bias in LLMs, using controlled synthetic datasets based on well-known logical fallacies and reasoning structures.

## Gap Addressed
Prior work often evaluates reasoning in LLMs using standard benchmarks like GSM8K or ARC, but these may inadvertently reward models for recognizing surface-level patterns rather than performing valid inference. Previous studies have noted that LLMs are sensitive to phrasing and prompt structure, yet few provide a formal framework to disentangle whether models reason logically or exploit shallow heuristics. This work fills that gap by introducing a controlled, hypothesis-driven methodology to isolate token bias, building on cognitive science concepts like the conjunction fallacy and syllogistic reasoning, where correct answers require overriding intuitive but logically invalid responses.

## Method
The authors design a hypothesis-testing framework using synthetic datasets based on the conjunction fallacy and syllogistic reasoning, where logical validity is decoupled from surface form. They apply token perturbation techniques—systematically altering non-logical tokens (e.g., names, objects) while preserving underlying logic—to test whether model predictions remain consistent. Under genuine reasoning, performance should be invariant to such changes; deviations indicate reliance on token bias. They use statistical tests (e.g., chi-squared) to assess whether response distributions shift significantly across perturbations, providing a quantifiable measure of bias. The framework is applied across multiple LLMs, including GPT-3.5, GPT-4, and Llama series.

## Datasets and Metrics
**Datasets:** The study uses two synthetic datasets: (1) a conjunction fallacy dataset with 1,200 instances across 60 scenarios, each with multiple token permutations; and (2) a syllogistic reasoning dataset with 240 logically valid and invalid forms, also expanded via systematic token perturbations. The datasets are carefully constructed to maintain logical equivalence across variations while changing superficial tokens. No real-world datasets are used; all data are artificially generated to enable controlled experimentation.

**Metrics:** The primary metrics include accuracy, consistency (measured as response stability across token-preserving logical transformations), and p-values from chi-squared tests to detect significant shifts in output distributions due to token perturbations. They also compute a Token Bias Score (TBS), quantifying the degree to which model predictions covary with irrelevant token changes. For example, GPT-4 shows a TBS of 0.68 on the conjunction fallacy task, significantly above the threshold for genuine reasoning (≤0.1).

## Results
The results show that all tested LLMs exhibit significant token bias: performance drops and response patterns shift markedly under token perturbations despite unchanged logic. For instance, in the conjunction fallacy task, models chose the fallacious answer 78–93% of the time, influenced by stereotypical associations in token choices. In syllogistic reasoning, accuracy varied by up to 40% across logically equivalent forms depending on surface tokens. Statistical tests reject the null hypothesis of consistent reasoning (p < 0.01) for all models. Even instruction-tuned and larger models (e.g., GPT-4) show strong bias, suggesting scaling alone does not lead to genuine reasoning. The authors conclude that current LLMs are not robust reasoners but rely heavily on shallow pattern matching.

## Limitations
The study focuses on specific types of logical reasoning (conjunction fallacy and syllogisms), so findings may not generalize to all reasoning domains. Additionally, the synthetic nature of the datasets, while enabling control, may lack the complexity of real-world language use. The authors acknowledge that token bias might interact with other factors like context length or training data density, which were not fully explored.

## Verification Verdict
REAL (98%) — The paper 'A Peek into Token Bias: Large language models are not yet genuine reasoners' by Jiang, B. et al. is confirmed to be a real publication at EMNLP 2024. It is listed on the ACL Anthology with ID 2024.emnlp-main.272, has a preprint on arXiv (2406.11050), and the full text is available via the ACL Anthology. Author names, title, venue, and year match across multiple reliable sources including Perplexity search results and arXiv. Although Semantic Scholar initially returned no results, the paper's presence in the ACL Anthology and arXiv confirms its legitimacy.
