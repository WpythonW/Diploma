---
key: mostafazadeh2016corpus
title: A corpus and evaluation framework for deeper understanding of commonsense stories
authors: Mostafazadeh, N. and Chambers, N. and He, X. and Parikh, D. and Batra, D. and Vanderwende, L. and Kohli, P. and Allen, J.
year: 2016
venue: Unknown
doi: 
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/1604.01696
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The paper aims to advance the understanding of commonsense reasoning in narrative texts by introducing a new dataset and evaluation framework. It focuses on developing models that can comprehend the sequence of everyday events in stories, particularly by predicting what happens next, identifying inconsistencies, and filling in missing information. The goal is to push beyond surface-level understanding and encourage deeper reasoning about the causes, effects, and intentions behind events in short stories.

## Gap Addressed
Existing datasets at the time were limited in their ability to evaluate deep commonsense understanding of narratives, often focusing on syntactic or shallow semantic tasks. There was a lack of benchmarks that required models to reason about the motivations and implications of characters’ actions. The authors identified a need for a corpus that explicitly tests inference capabilities over everyday scenarios in a story context.

## Method
The authors introduce the Story Cloze Test, a new evaluation framework where a model must select the correct ending to a four-sentence story from two options. They also release the Large-scale Cloze Test (LSTC) dataset, derived from ROCStories, which contains over 100,000 five-sentence commonsense stories. The method evaluates models on their ability to understand narrative coherence and apply commonsense knowledge to predict plausible story endings.

## Datasets and Metrics
**Datasets:** ROCStories, Story Cloze Test, Large-scale Cloze Test (LSTC)

**Metrics:** Accuracy

## Results
The paper reports that human performance on the Story Cloze Test reaches 85–90% accuracy, while baseline models, including bag-of-words and LSTM-based architectures, perform significantly worse, with accuracies around 70%. More advanced models incorporating semantic features or knowledge grounding show modest improvements but still lag behind humans. The results highlight the difficulty of the task and the limitations of current models in capturing commonsense reasoning. The dataset is shown to be effective in differentiating model performance and driving research in narrative understanding.

## Limitations
The stories in the dataset are short and simplified, potentially limiting their complexity and real-world applicability. The binary choice format of the cloze task may allow models to exploit stylistic or lexical cues rather than perform true reasoning.

## Verification Verdict
REAL (95%) — arXiv: title match (sim=1.00); arXiv: authors match (8/8)

## Links
- [PDF](URL: https://arxiv.org/abs/1604.01696)
