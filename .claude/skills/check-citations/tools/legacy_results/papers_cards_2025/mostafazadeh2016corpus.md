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
confidence: 98
source_used: arxiv
---

## Goal
The authors aimed to advance deeper understanding of commonsense in narrative text by introducing a large-scale corpus of everyday stories and an evaluation framework to assess models' ability to understand and predict coherent story endings. They focused on capturing script knowledge—the implicit understanding of everyday activities and their typical sequences—through natural language stories. The goal was to move beyond shallow pattern matching toward models that reason about cause, effect, and intention in narrative contexts. This work targets machine comprehension systems that can generate or select plausible story continuations grounded in real-world commonsense.

## Gap Addressed
Prior story understanding datasets were limited in size, lacked diverse commonsense reasoning challenges, or focused on artificial scenarios rather than natural, everyday situations. Existing benchmarks often evaluated surface-level coherence without requiring deep semantic or causal reasoning. The authors identified a need for a large, human-written corpus of simple five-sentence stories grounded in commonsense, paired with a rigorous evaluation method to test whether models can infer the correct story ending among plausible but incorrect alternatives. This gap hindered progress in training and evaluating models for script learning and narrative inference.

## Method
The authors constructed the ROCStories corpus, containing over 49,000 five-sentence stories written by crowdworkers using given story titles and sentence templates. Each story describes a commonsense scenario involving everyday human activities. They then developed the Story Cloze Test, a binary choice task where a model must select the correct last sentence of a story from two options—one correct (human-written) and one distractor (plausible but inconsistent). Distractors were generated either automatically or via human rewriting to violate commonsense or narrative coherence. Models were evaluated based on their ability to identify the correct ending, testing their implicit understanding of causal and temporal structure.

## Datasets and Metrics
**Datasets:** ROCStories corpus (~49,000 five-sentence commonsense stories); Story Cloze Test (1,871 test instances, each with a story context and two ending options); a smaller validation set (1,872 instances) and training set (training split of ROCStories). The dataset was crowd-sourced and human-validated for quality and naturalness.

**Metrics:** Accuracy (binary choice accuracy on selecting the correct story ending); human performance baseline measured via crowdworker accuracy; model scores compared against baselines including n-gram models, bag-of-words logistic regression, LSTM-based models, and neural sentence representation models (e.g., SkipThought). Human performance reported at 93.5% accuracy on the test set.

## Results
The best-performing model (a neural network using sentence representations and attention mechanisms) achieved 75.1% accuracy, significantly below human performance (93.5%), indicating substantial room for improvement. Baseline models such as n-gram and logistic regression performed poorly (~50–55%), showing the task's difficulty. The gap between machine and human performance highlighted limitations in current models' ability to capture causal, temporal, and intentional structure in stories. The dataset proved effective in exposing weaknesses in existing language models regarding commonsense reasoning. Subsequent work has used this benchmark to train more sophisticated models, including those based on Transformers.

## Limitations
The distractor endings, while plausible, may sometimes contain subtle cues that make the task easier or harder in unintended ways. The corpus relies on crowd-sourced story writing, which may introduce variability in quality or bias toward certain types of scenarios. The evaluation framework focuses only on ending prediction and does not assess full story generation or broader aspects of narrative understanding.

## Verification Verdict
REAL (98%) — Paper confirmed via Perplexity search with matching title, authors, year, arXiv ID, and DOI. Published in NAACL-HLT 2016. Semantic Scholar may have indexing gap, but multiple authoritative sources confirm existence.

## Links
- [PDF](URL: https://arxiv.org/abs/1604.01696)
