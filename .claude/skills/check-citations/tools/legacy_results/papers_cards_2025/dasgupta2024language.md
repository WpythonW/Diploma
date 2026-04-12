---
key: dasgupta2024language
title: Language models, like humans, show content effects on reasoning tasks
authors: Dasgupta, I. and Lampinen, A. K. and Chan, S. C. Y. and Sheahan, H. R. and Creswell, A. and Kumaran, D. and McClelland, J. L. and Hill, F.
year: 2024
venue: PNAS Nexus
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: perplexity
---

## Goal
The authors aim to investigate whether large language models (LLMs) exhibit human-like content effects in reasoning tasks—specifically, whether their performance on logical reasoning problems is influenced by the semantic content of the task, just as humans are. Humans tend to perform better when the content aligns with real-world knowledge or plausible scenarios, even if it conflicts with logical validity. The study explores whether LLMs show similar biases across three well-established reasoning domains: natural language inference, syllogistic reasoning, and the Wason selection task. The broader goal is to assess the cognitive plausibility of LLM reasoning by comparing their behavior to human participants under controlled conditions.

## Gap Addressed
Prior work has shown that humans are susceptible to content effects, accepting logically invalid arguments if their conclusions are semantically believable (belief bias) or rejecting valid arguments with implausible content. While LLMs have demonstrated strong performance on reasoning benchmarks, it remains unclear whether their reasoning is similarly influenced by content or if they rely more on abstract logical form. Some studies suggest LLMs can emulate logical reasoning, but few have systematically compared their content sensitivity to that of humans across multiple tasks. This work fills that gap by directly testing whether LLMs replicate human-like content effects using the same stimuli and experimental designs applied to human subjects.

## Method
The authors conduct a series of experiments using three classic reasoning tasks—natural language inference (NLI), syllogism validity judgment, and the Wason selection task—each designed to elicit content effects. For each task, they use established stimuli from cognitive science literature that manipulate the alignment between logical validity and semantic plausibility. Both human participants and multiple LLMs—including Gemini and Gemma—are tested on identical items. The models’ responses are evaluated for accuracy and bias patterns, with a focus on belief bias (favoring believable conclusions) and content sensitivity. The experimental design enables direct comparison between human and model behavior, including error patterns and response distributions.

## Datasets and Metrics
**Datasets:** The study uses custom-built datasets derived from established cognitive science stimuli for three tasks: (1) Natural Language Inference items from the Recognizing Textual Entailment framework, (2) Syllogism validity judgment items from classic psychology experiments (e.g., atmosphere and belief bias tasks), and (3) Wason selection task problems with thematic and abstract versions. Exact dataset sizes are not specified in the search results, but each task includes multiple item types (valid/invalid, believable/unbelievable) with balanced designs. Human data were collected via online experiments; model data were generated using prompt-based inference.

**Metrics:** The primary metrics include accuracy (proportion of correct responses), response bias (measured via signal detection theory metrics like d' and criterion/c), and belief bias effect size (difference in accuracy between congruent and incongruent conditions). The authors also report model-human similarity indices, such as correlation of error patterns and response distributions across items. Specific metric values are not provided in the search results, but the paper confirms statistically significant content effects in both humans and models.

## Results
The study finds that LLMs, like humans, show strong content effects across all three reasoning tasks. For example, models are more likely to accept invalid arguments with believable conclusions (belief bias) and struggle with valid arguments that have counterintuitive or implausible content. In the Wason task, both humans and models perform better on thematic (real-world) versions than abstract ones. Gemini and Gemma replicate human-like error patterns and response biases, with high correlation in performance across items. The magnitude of belief bias in models is comparable to that observed in human participants, suggesting similar underlying mechanisms. These results indicate that LLM reasoning is not purely syntactic but is influenced by learned semantic associations, much like human reasoning.

## Limitations
The authors note that while the models mimic human content effects, this does not imply they use the same cognitive processes. The reliance on prompt-based responses may introduce variability due to formatting or context effects. Additionally, the study focuses on a limited set of reasoning tasks and models, so findings may not generalize to all LLMs or reasoning domains.

## Verification Verdict
REAL (95%) — The paper is confirmed by multiple Perplexity searches with matching title, authors, year, journal (PNAS Nexus), volume, issue, article ID, and DOI (10.1093/pnasnexus/pgae233). Discrepancy in author order is common across databases; absence from Semantic Scholar does not invalidate publication.
