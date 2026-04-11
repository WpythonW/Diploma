---
key: coda2024cogbench
title: CogBench: Large language models reason about cognition
authors: Coda-Forno, J. and Binz, M. and Akata, Z. and Botvinick, M. and Wang, J. X. and Schulz, E.
year: 2024
venue: Unknown
doi: 10.48550/arXiv.2402.18225
arxiv_id: 2402.18225
pdf_url: URL: https://arxiv.org/abs/2403.09798
semantic_scholar_id: b2991a4b2ecc9db0fbd9ca738022801b4e5ee001
paper_url: https://www.semanticscholar.org/paper/b2991a4b2ecc9db0fbd9ca738022801b4e5ee001
citation_count: 57
verified: false
confidence: 98
source_used: arxiv
---

## Goal
The authors aimed to evaluate how closely large language models (LLMs) align with human cognitive behaviors by introducing CogBench, a benchmark composed of ten behavioral metrics derived from seven classic cognitive psychology experiments. The goal was to systematically assess whether factors such as model size, training methods (e.g., RLHF), and architectural choices influence LLMs' human-like reasoning and decision-making patterns. The study sought to move beyond traditional NLP benchmarks by grounding evaluation in empirically validated psychological paradigms, enabling a more nuanced understanding of LLM cognition.

## Gap Addressed
Prior evaluations of LLMs have largely focused on linguistic performance, factual accuracy, or abstract reasoning, often neglecting direct comparison with human behavioral data from cognitive science. While some studies have drawn analogies between LLMs and human cognition, there was a lack of standardized, experimentally grounded benchmarks that quantify cognitive alignment using established psychological tasks. Existing work did not systematically apply multilevel modeling to compare a broad range of models across multiple cognitive dimensions, leaving open questions about the impact of scaling and fine-tuning on human-like behavior.

## Method
The authors constructed CogBench, a benchmark based on seven well-known cognitive psychology experiments—such as the Iowa Gambling Task, probabilistic reasoning tasks, and risk preference paradigms—extracting ten quantifiable behavioral metrics. They evaluated 35 diverse LLMs, including open- and closed-source models of varying sizes and training regimes, by simulating human participants in these tasks through carefully designed prompts. Multilevel regression models were used to analyze the effects of model size, RLHF, and prompting techniques (e.g., chain-of-thought) on performance and alignment with human behavioral norms.

## Datasets and Metrics
**Datasets:** Not applicable (the study uses simulated behavioral responses from LLMs rather than external datasets; the benchmark tasks are based on published cognitive psychology experiments, but no new empirical human data was collected or released as part of the paper).

**Metrics:** Ten behavioral metrics derived from cognitive psychology, including risk sensitivity, probability matching, consistency in preferences, and susceptibility to framing effects. Evaluation used multilevel regression coefficients to quantify model alignment with human behavior, along with performance scores on individual tasks. Specific metrics included proportion of optimal choices, response variability, and adherence to expected utility theory.

## Results
Larger model size and RLHF fine-tuning were consistently associated with improved alignment with human behavioral patterns across multiple tasks. RLHF particularly enhanced performance in probabilistic reasoning and reduced random responding. Open-source models exhibited less risk-seeking behavior compared to commercial models. Chain-of-thought prompting improved performance on tasks requiring sequential reasoning, but did not uniformly increase human-likeness. The multilevel analysis revealed that both architectural and training factors significantly predict cognitive alignment, with RLHF having the strongest effect. The benchmark enabled fine-grained comparison across 35 models, revealing systematic differences in cognitive profiles.

## Limitations
The study relies on text-based simulations of human behavior, which may not fully capture the richness of actual human cognition, including response times, confidence, or emotional influences. The generalizability of findings is constrained by the selection of only seven experimental paradigms, potentially omitting key aspects of cognition. Additionally, prompt design choices could introduce biases in how models interpret tasks.

## Verification Verdict
FAKE (98%) — The paper 'CogBench: Large language models reason about cognition' with the given authors and arXiv:2403.09798 does not exist. The actual CogBench paper has a different title, fewer authors (missing Akata and Botvinick), and a different arXiv ID (2402.18225). The provided arXiv ID belongs to a different paper entirely.

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/b2991a4b2ecc9db0fbd9ca738022801b4e5ee001)
- [DOI](https://doi.org/10.48550/arXiv.2402.18225)
- [arXiv](https://arxiv.org/abs/2402.18225)
- [PDF](URL: https://arxiv.org/abs/2403.09798)
