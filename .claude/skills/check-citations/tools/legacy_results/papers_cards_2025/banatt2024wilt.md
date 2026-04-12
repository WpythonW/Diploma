---
key: banatt2024wilt
title: WILT: A multi-turn, memorization-robust inductive logic benchmark for LLMs
authors: Banatt, E. and Cheng, J. Y. and Vaidyanath, S. and Hwu, T.
year: 2024
venue: Unknown
doi: 
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/2410.10998
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The authors aim to address the lack of robust evaluation benchmarks for inductive logic reasoning in large language models (LLMs), particularly in multi-turn, interactive settings. Existing benchmarks often focus on single-turn reasoning or are vulnerable to memorization, limiting their ability to assess true generalization. WILT (Wason Inductive Logic Test) is designed to evaluate how well LLMs gather evidence, refine hypotheses, and converge on correct rules through iterative interaction. The benchmark emphasizes real-time, dynamic reasoning rather than static problem-solving, targeting a core cognitive skill—inductive inference—under conditions that prevent shortcut learning.

## Gap Addressed
Prior reasoning benchmarks often fail to assess multi-turn, interactive hypothesis testing and are susceptible to data contamination or memorization due to static, human-authored problems. While datasets like MMLU or GSM8K evaluate factual knowledge or arithmetic, they do not capture the process of evidence gathering and rule induction central to scientific reasoning. The Wason 2-4-6 task, a classic psychology experiment, provides a foundation for such evaluation but has not been scaled or adapted robustly for LLMs. WILT fills this gap by procedural generation of tasks, ensuring memorization resistance and enabling systematic evaluation of iterative reasoning—a capability underexplored in current LLM assessments.

## Method
WILT is based on the Wason 2-4-6 task, where a model proposes triplets of numbers (e.g., (2,4,6)) and receives binary feedback (True/False) indicating whether the triplet satisfies a hidden rule (e.g., x < y < z). The model must iteratively propose test cases, interpret feedback, and refine its hypothesis over multiple turns until it identifies the correct rule. Tasks are procedurally generated to prevent memorization, with 50 unique test instances. Each model response is evaluated for correctness, rule accuracy, and reasoning efficiency. The benchmark is implemented as an interactive environment where models engage in up to 30 turns per task, with performance measured across multiple metrics.

## Datasets and Metrics
**Datasets:** WILT consists of 50 procedurally generated inductive reasoning tasks. The dataset is not based on pre-existing human-authored examples but algorithmically created to ensure diversity and memorization resistance. Each task involves a hidden rule over numerical triplets, and models interact through multiple turns to infer the rule. The dataset is available via the project’s GitHub repository.

**Metrics:** The evaluation metrics include Exact Matches (number of correct final rules out of 50), Perfect Rules (number of times the exact rule was stated correctly), Average Score (percentage of correct responses across turns), and Average Steps (number of turns taken to converge). Additional process-based metrics include hypothesis refinement rate and feedback utilization efficiency. The average score is reported as a percentage, with top models achieving around 28% accuracy.

## Results
On the WILT benchmark (50 tasks), Mistral Large 2 achieved 11 exact matches and 5 perfect rules (26.56% avg score, 2.84 avg steps), outperforming several leading models. GPT-4o (2024-08-06) scored lower with 9 exact matches, 6 perfect rules, and only 15.26% average score, taking just 0.52 steps on average—suggesting premature convergence. GPT-4o-mini achieved 6 exact matches (20.36% score), while Gemini 1.5 Pro and Flash both reached 5 exact matches and 6 perfect rules (16.78% and 16.5% scores, respectively). Claude 3.5 Sonnet outperformed o1-mini and o1-preview, despite their strength in single-turn reasoning, highlighting its superior multi-turn reasoning capability. Overall, no model exceeds 28% accuracy, indicating significant limitations in current LLMs for sustained inductive reasoning.

## Limitations
The benchmark currently uses a limited set of 50 tasks, which, while procedurally generated, may not cover the full space of inductive rules. The evaluation focuses on numerical triplets, potentially limiting generalizability to other domains like symbolic or visual reasoning. Additionally, the scoring relies on rule matching, which may not fully capture partial understanding or creative alternative hypotheses.

## Verification Verdict
REAL (95%) — Paper confirmed via arXiv ID (2410.10998), consistent title/authors/year across sources, hosted on arXiv, presented at NeurIPS 2024 workshop, and cited externally. Semantic Scholar's lack of indexing is not sufficient to质疑 authenticity given multiple corroborating sources.

## Links
- [PDF](URL: https://arxiv.org/abs/2410.10998)
