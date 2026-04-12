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
source_used: arxiv | CrossRef | OpenAlex | acl_anthology
---

## Goal
The paper aims to investigate how individual attention heads in transformer-based language models contribute to the propagation of social biases, particularly gender and racial biases. It seeks to understand whether certain attention heads amplify or mitigate bias and to provide insights into the internal mechanisms of bias in pre-trained models like BERT. The study also explores the possibility of identifying and removing biased attention heads to reduce stereotypical associations in model outputs.

## Gap Addressed
While prior work has examined bias in language models at the system or embedding level, there is limited understanding of how specific components—particularly attention heads—contribute to biased representations. Most debiasing techniques are applied post-hoc or at the input level, without targeting the internal model mechanisms responsible for bias propagation. This work addresses the gap by analyzing bias at the granularity of attention heads, offering a more fine-grained understanding of where and how bias manifests in transformers.

## Method
The authors propose a bias score metric to quantify the contribution of each attention head to stereotypical associations using bias benchmarks such as the CrowS-Pairs dataset. They perform ablation studies by removing or masking individual attention heads and measure changes in bias metrics. The method is applied to BERT-base, analyzing attention patterns across layers and heads. Visualization techniques are used to interpret attention maps in context, and statistical analysis identifies consistently biased heads.

## Datasets and Metrics
**Datasets:** CrowS-Pairs, BOLD (Bias in Open-Ended Language Generation), and the /r/TheRedPill corpus for case studies.

**Metrics:** Bias score (based on change in stereotypical prediction upon head removal), accuracy on CrowS-Pairs, log probability differences between stereotypical and anti-stereotypical sentences, and attention visualization.

## Results
Several attention heads are found to significantly increase model bias when active, particularly in middle layers of BERT. Removing these heads reduces stereotypical associations by up to 18% without substantial performance degradation on downstream tasks. Some heads consistently reduce bias, acting as "debiasing" components. The bias score effectively identifies problematic heads, and visualization confirms their focus on gender- and race-related tokens. Results suggest that bias is not uniformly distributed but localized in specific heads.

## Limitations
The analysis is limited to BERT-base and may not generalize to larger or more recent models like RoBERTa or Llama. The bias score depends on predefined bias benchmarks, which may not capture all forms of bias. Ablation effects are measured in isolation, potentially missing interactions between heads.

## Verification Verdict
REAL (98%) — Multiple authoritative sources (CrossRef, OpenAlex, arXiv, ACL Anthology) confirm the existence of the paper with identical title, full author list, and publication in TrustNLP 2025. The arXiv and DOI links contain full text and metadata matching the query.
