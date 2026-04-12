---
key: han2023explaining
title: Explaining Emergent In-Context Learning as Kernel Regression
authors: Han, C. and Wang, Z. and Zhao, H. and Ji, H.
year: 2023
venue: Unknown
doi: 
arxiv_id: 2305.12766
pdf_url: URL: https://arxiv.org/abs/2305.12766
semantic_scholar_id: 3706bdb607a83a558e38b62dacfed7bc9e114310
paper_url: https://www.semanticscholar.org/paper/3706bdb607a83a558e38b62dacfed7bc9e114310
citation_count: 18
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The authors aim to explain the emergent phenomenon of in-context learning (ICL) in large language models (LLMs) by drawing a theoretical and empirical connection to kernel regression. They seek to understand how LLMs can perform tasks based on a few demonstrations in the prompt without explicit parameter updates, a behavior not observed in smaller models. By framing ICL as a form of non-parametric learning, the paper attempts to demystify how contextually relevant information is retrieved and utilized during inference. The scope includes both theoretical analysis and empirical validation across model behaviors and attention patterns.

## Gap Addressed
Prior work has observed ICL empirically but lacks a rigorous mechanistic explanation for how LLMs leverage demonstration examples to make predictions. While some studies suggest analogies to Bayesian inference or meta-learning, there is limited formal grounding linking these behaviors to concrete machine learning principles. This paper addresses the gap by proposing kernel regression as a unifying framework, showing that as the number of demonstrations increases, the model’s prediction asymptotically converges to a kernel-weighted average of labels, similar to Nadaraya-Watson estimators. This provides a mathematically grounded interpretation missing in earlier descriptive or simulation-based accounts.

## Method
The authors theoretically prove that under certain assumptions about feature representations and attention mechanisms, the attention weights in transformers converge to kernel regression form during ICL, where outputs are weighted averages of demonstration labels using similarity kernels over inputs. They derive conditions under which transformer attention approximates the kernel regression estimator \(\hat{y} = \sum_i y_i K(x, x_i)/\sum_i K(x, x_i)\). Empirically, they analyze attention patterns and feature similarities in LLMs, showing that attention weights correlate with input similarity and that model outputs align with kernel regression predictions. They also conduct ablation studies on synthetic and real tasks to validate the role of feature alignment and label consistency.

## Datasets and Metrics
**Datasets:** Unknown

**Metrics:** Not applicable (theoretical analysis and qualitative/quantitative behavioral analysis used; no standard benchmark metrics reported)

## Results
The paper shows that transformer attention during ICL behaves like a kernel regression estimator, with higher attention weights assigned to semantically or syntactically similar input examples. Empirical analysis reveals that LLMs are more influenced by in-distribution and format-consistent demonstrations, consistent with kernel-based weighting. The model’s sensitivity to demonstration order, similarity, and output formatting is explained through the lens of kernel similarity and feature alignment. Theoretical results establish that under Bayesian assumptions on prompts, ICL converges to kernel regression asymptotically as the number of demonstrations grows. These findings are validated across multiple LLMs and synthetic experiments, showing consistent alignment with kernel regression behavior.

## Limitations
The theoretical analysis relies on simplifying assumptions about feature isotropy and attention linearity, which may not fully hold in real-world LLMs. The empirical validation is largely qualitative and based on observational studies rather than comprehensive benchmarks, limiting generalizability across all ICL scenarios.

## Verification Verdict
REAL (95%) — The paper exists on arXiv with the exact title, authors, year, and URL provided. Semantic Scholar lists a near-identical paper with the same arXiv ID and authors but a slightly different title ('Understanding' vs 'Explaining'), which is a common metadata discrepancy. The core identifiers (arXiv:2305.12766, authors, year) match, confirming the paper is real.

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/3706bdb607a83a558e38b62dacfed7bc9e114310)
- [arXiv](https://arxiv.org/abs/2305.12766)
- [PDF](URL: https://arxiv.org/abs/2305.12766)
