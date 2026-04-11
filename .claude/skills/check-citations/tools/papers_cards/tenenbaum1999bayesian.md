---
key: tenenbaum1999bayesian
title: A Bayesian framework for concept learning
authors: Tenenbaum, J. B.
year: Unknown
venue: Unknown
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: b1cd67acc177c04ce8ef7dd8359b2ad7310fa80a
paper_url: https://www.semanticscholar.org/paper/b1cd67acc177c04ce8ef7dd8359b2ad7310fa80a
citation_count: 154
verified: true
confidence: 98
source_used: semantic_scholar
---

## Goal
The goal of this Ph.D. thesis is to develop a Bayesian framework that explains how humans learn concepts from limited data, particularly focusing on the rapid and flexible nature of human concept acquisition. The author aims to model concept learning as a form of probabilistic inference, where learners use prior knowledge and observed examples to make predictions about new instances. The work seeks to bridge cognitive science and computational modeling by formalizing intuitive theories of concept formation using Bayesian statistics. It emphasizes explaining phenomena such as one-shot learning, generalization from small samples, and the influence of prior knowledge on inductive biases.

## Gap Addressed
Prior models of concept learning often struggled to account for the speed and flexibility with which humans learn new concepts, especially from very few examples. Traditional approaches like prototype or exemplar models lacked a principled way to balance simplicity and fit to data or to incorporate structured prior knowledge. Symbolic models could represent abstract knowledge but were brittle and lacked mechanisms for handling uncertainty. This work addresses the gap by introducing a Bayesian framework that formally integrates prior knowledge with observed data, enabling robust generalization and explaining how people make rich inductive inferences from sparse input—a challenge not adequately solved by earlier connectionist, rule-based, or similarity-based models.

## Method
The thesis develops a Bayesian model of concept learning in which concepts are represented as hypotheses within a hypothesis space, and learning proceeds via probabilistic inference over this space. The framework uses Bayes' rule to compute the posterior probability of a hypothesis given observed examples, combining likelihood (how well the hypothesis explains the data) with prior probability (reflecting generalization bias or background knowledge). The hypothesis space is structured to reflect intuitive theories about natural categories, such as geometric shapes or number patterns. The model is applied to tasks like learning object categories, number concepts, and word meanings, with simulations demonstrating how different priors lead to different generalization behaviors.

## Datasets and Metrics
**Datasets:** Not applicable. The work is theoretical and computational, relying on simulations and qualitative comparisons to human behavioral data rather than empirical datasets. Experimental data from human participants are discussed in related publications but are not detailed in the thesis itself based on available information.

**Metrics:** Not applicable. Evaluation is based on qualitative fit to human cognitive phenomena (e.g., one-shot learning, typicality gradients, generalization patterns) rather than quantitative metrics. The model's success is judged by its ability to reproduce human-like inferences in concept learning tasks through simulation studies.

## Results
The Bayesian framework successfully explains a range of human concept learning behaviors, including the ability to generalize from one or a few examples, sensitivity to the shape of the hypothesis space, and the effects of prior knowledge on inductive generalization. Simulations show that the model can account for typicality effects, non-monotonic generalization, and the "size principle"—a preference for the simplest hypothesis that fits the data. The model outperforms classical models in capturing the richness and flexibility of human inferences. It laid the foundation for subsequent work in Bayesian cognitive science, influencing models of word learning, causal reasoning, and theory-based induction.

## Limitations
The model assumes that the hypothesis space and prior knowledge are pre-specified, raising questions about how these structures themselves are learned or acquired. It does not fully address the computational complexity of inference in large or unstructured hypothesis spaces. Additionally, the framework relies on hand-crafted representations, limiting its scalability to open-ended, real-world learning scenarios.

## Verification Verdict
REAL (98%) — Both Perplexity and Semantic Scholar confirm the existence of the 1999 Ph.D. thesis by J. B. Tenenbaum with matching title and author. Semantic Scholar lists 154 citations, indicating academic recognition. The lack of DOI is expected for older theses.

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/b1cd67acc177c04ce8ef7dd8359b2ad7310fa80a)
