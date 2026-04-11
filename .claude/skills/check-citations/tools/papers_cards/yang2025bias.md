---
key: yang2025bias
title: Bias A-head? Analyzing Bias in Transformer-Based Language Model Attention Heads
authors: Yang, Y. and Duan, H. and Abbasi, A. and Lalor, J. P. and Tam, K. Y.
year: 2025
venue: Proceedings of the 5th Workshop on Trustworthy NLP (TrustNLP 2025)
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 98
source_used: aclanthology | arxiv
---

## Goal
The authors aim to investigate and understand how bias manifests in the attention mechanisms of Transformer-based pretrained language models (PLMs), with a focus on gender and racial stereotypes. They seek to determine whether specific attention heads within these models are responsible for encoding and propagating social biases, and if so, to what extent. The study targets widely used models such as BERT, GPT, LLaMA-2 (7B), and LLaMA-2-Chat (7B), analyzing their internal attention patterns to uncover systematic biases. The ultimate goal is to develop a framework that enables fine-grained bias diagnosis at the level of individual attention heads, contributing to more transparent and trustworthy NLP systems.

## Gap Addressed
Prior research on bias in language models has largely focused on input-output behavior, word embeddings, or model outputs using indirect probing methods, often overlooking the internal mechanisms that generate biased responses. While some studies have examined attention patterns, few have systematically analyzed how individual attention heads contribute to gender and racial bias. Existing work also lacks a comprehensive framework for identifying and quantifying biased attention heads across diverse PLMs. This paper addresses the gap by proposing a novel methodology to directly analyze attention head behavior in context, enabling precise localization of bias within model components.

## Method
The authors propose a bias analysis framework that identifies biased attention heads by measuring attention weights on stereotype-relevant word pairs (e.g., gender-occupation or race-associated names) across a diverse set of context sentences. They use bias-specific templates and real-world corpora to generate inputs that elicit biased associations, then compute attention-based bias scores for each head. The framework includes clustering attention heads by their bias patterns and evaluating the impact of masking biased heads on overall model bias. Experiments are conducted on BERT, GPT, LLaMA-2 (7B), and LLaMA-2-Chat (7B), comparing pre-trained and instruction-tuned variants.

## Datasets and Metrics
**Datasets:** Not applicable (The study uses constructed bias evaluation sets based on templates and stereotype word lists rather than standard public datasets. Input contexts are generated synthetically using predefined templates involving gender- and race-related terms.)

**Metrics:** Bias scores based on attention weights (e.g., differential attention to stereotypical vs. counter-stereotypical word pairs), clustering similarity of attention head bias patterns, and debiasing effectiveness measured by reduction in bias score after head masking. Specific numerical values are not provided in the search results.

## Results
The study finds that only a small subset of attention heads are responsible for the majority of gender and racial bias in the tested models. These biased heads are often concentrated in middle-to-later layers and show consistent patterns across models. Head masking experiments demonstrate that removing or suppressing these specific heads significantly reduces overall model bias without severely impacting general performance. Instruction-tuned models like LLaMA-2-Chat exhibit slightly lower attention-based bias compared to their base counterparts, suggesting alignment training may mitigate some internal biases. The clustering analysis reveals distinct types of bias-specialized heads, indicating modular bias encoding within the architecture.

## Limitations
The authors note that their method relies on predefined bias templates and word lists, which may not capture the full spectrum of real-world bias expressions. Additionally, masking attention heads may have unintended side effects on model functionality, and the current evaluation is limited to attention weight analysis rather than downstream task performance.

## Verification Verdict
REAL (98%) — Paper confirmed via ACL Anthology (official proceedings) with matching title, authors, year, and page numbers. arXiv preprint (2311.10395) and workshop details are consistent. Semantic Scholar may not yet index TrustNLP 2025, but ACL Anthology is definitive for ACL-affiliated workshops.
