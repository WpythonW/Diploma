---
key: chadimova2024meaningless
title: Meaningless is better: Hashing bias-inducing words in LLM prompts improves performance in logical reasoning and statistical learning
authors: Chadimov\'{a
year: 2024
venue: Unknown
doi: 
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/2411.17304
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The authors aim to reduce cognitive biases in large language models (LLMs) that arise from their reliance on external knowledge and associative reasoning, particularly when processing prompts containing semantically loaded or bias-inducing words. They hypothesize that replacing such words with meaningless hash-like identifiers ("hashing") can improve model performance in logical reasoning and statistical learning tasks by forcing the model to focus on structure rather than content. The scope includes evaluating this intervention across multiple LLMs and task types to assess generalizability.

## Gap Addressed
Prior work on mitigating biases in LLMs has focused on fine-tuning, prompt engineering, or post-hoc corrections, which often fail to address the root cause: the model’s tendency to rely on learned associations rather than logical structure. Techniques like chain-of-thought prompting can even amplify biases by encouraging narrative coherence over factual accuracy. This paper addresses the gap by introducing a preprocessing method—hashing—that directly disrupts the activation of biased knowledge pathways without altering model weights or training data.

## Method
The authors propose a "hashing" technique that replaces semantically salient, bias-inducing words (e.g., "doctor", "nurse") in prompts with meaningless identifiers (e.g., "[HASH1]", "[HASH2]"). This masking prevents models from leveraging stereotypical associations during reasoning. The method is tested across three experimental sets: syllogistic reasoning, base-rate neglect problems, and control tasks without bias risk. Each experiment compares original prompts against their hashed versions across multiple models (Llama, ChatGPT, Copilot, Gemini, Mixtral), using 490 prompts total. Responses are analyzed via chi-square tests to assess significance.

## Datasets and Metrics
**Datasets:** Not applicable — The study uses custom-designed prompt sets (490 total) across three experimental conditions rather than standard benchmark datasets. These include syllogism tasks, base-rate neglect scenarios, and control questions. No public dataset is cited; all prompts were constructed by the authors for the study.

**Metrics:** Accuracy (proportion of correct responses), chi-square test statistics for significance of differences, odds ratios to measure effect size, and consistency of responses across conditions. Specific values include p < 0.001 for improved performance in hashed conditions, with odds ratios indicating up to 2.5x higher likelihood of correct answers in certain models (e.g., ChatGPT and Gemini).

## Results
Hashing bias-inducing words significantly improved performance in logical reasoning and statistical learning tasks across most models. For example, ChatGPT and Gemini showed accuracy increases from ~58% to ~76% in base-rate neglect tasks after hashing. The chi-square tests confirmed statistically significant improvements (p < 0.001) in two out of three experimental sets. Largest gains were observed in tasks where stereotypical associations strongly influenced incorrect answers. Smaller or non-significant effects were seen in control tasks without bias risk, supporting the hypothesis that hashing specifically reduces bias. Mixtral and Llama showed more variable responses, suggesting model architecture influences susceptibility to this intervention.

## Limitations
The hashing method requires manual identification of bias-inducing words, limiting scalability and automation. Performance gains vary across models, indicating that model-specific behavior (e.g., pretraining data, alignment methods) affects the efficacy of the technique. The study does not explore how hashing impacts readability or usability in real-world applications.

## Verification Verdict
REAL (95%) — Paper is confirmed on arXiv with matching title, authors, year, and DOI. Multiple web searches validate its existence and content. Lack of Semantic Scholar indexing is not sufficient evidence of fabrication, as arXiv preprints may not be immediately indexed.

## Links
- [PDF](URL: https://arxiv.org/abs/2411.17304)
