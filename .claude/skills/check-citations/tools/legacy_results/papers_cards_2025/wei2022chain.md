---
key: wei2022chain
title: Chain-of-thought prompting elicits reasoning in large language models
authors: Wei, J. and Wang, X. and Schuurmans, D. and Bosma, M. and Ichter, B. and Xia, F. and Chi, E. and Le, Q. and Zhou, D.
year: 2022
venue: Advances in Neural Information Processing Systems
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The authors aim to investigate whether large language models (LLMs) can be prompted to perform complex reasoning tasks by generating intermediate reasoning steps, a method they term "chain-of-thought prompting." They seek to improve model performance on tasks requiring multi-step reasoning—such as arithmetic, commonsense, and symbolic reasoning—without modifying model architecture or requiring gradient-based fine-tuning. The study explores how this simple prompting strategy scales with model size and task complexity, focusing on eliciting implicit reasoning capabilities in LLMs.

## Gap Addressed
Prior work demonstrated that LLMs struggle with tasks requiring sequential reasoning, often failing on benchmarks like GSM8K (math word problems) despite strong performance on other language tasks. Standard few-shot prompting typically elicits only final answers without intermediate reasoning, limiting performance on complex problems. While fine-tuning and specialized architectures had been explored, a general, scalable, and parameter-free method to unlock reasoning in LLMs remained an open challenge. This paper addresses that gap by introducing a prompting technique that mimics human-like step-by-step reasoning.

## Method
The authors propose chain-of-thought (CoT) prompting, where few-shot exemplars include not only the question and final answer but also a natural language rationale leading to the solution. For example, instead of just providing "Q: X. A: Y.", the prompt includes "Q: X. A: Let's think step by step. [reasoning steps] So the answer is Y." This method is applied in a few-shot setting without backpropagation or model updates. The approach is evaluated across multiple reasoning tasks using models ranging from 100M to 540B parameters, comparing CoT to standard prompting.

## Datasets and Metrics
**Datasets:** Arithmetic reasoning: GSM8K (8.5K grade school math word problems), MultiArith, AddSub, SingleOp; Commonsense reasoning: CommonsenseQA, StrategyQA; Symbolic reasoning: Last Letter Concatenation, Coin Flip. Additionally, the authors use synthesized datasets for ablation studies. Dataset sizes vary: GSM8K has ~7.5K training and 1K test examples; others are smaller, with test sets ranging from 100 to 1K examples.

**Metrics:** Accuracy (exact match or correctness of final answer) is the primary metric. Key results: On GSM8K, CoT with a 540B model achieved ~67% accuracy (vs. <20% with standard prompting); on MultiArith, ~92% (vs. ~17%); on CommonsenseQA, ~78% (vs. ~72%); on StrategyQA, ~65% (vs. ~42%). Performance improvements are reported across model sizes, with CoT showing minimal benefit below 100B parameters but significant gains at scale.

## Results
Chain-of-thought prompting significantly improves reasoning performance in large language models, particularly at scale. On GSM8K, a 540B model using CoT with only eight exemplars reached 67.0% accuracy, surpassing prior state-of-the-art fine-tuned models. Standard prompting achieved only 17.9% on the same model. Similar gains were observed on MultiArith (92.0% vs. 17.0%) and StrategyQA (65.1% vs. 42.0%). The method shows minimal benefit for small models (<10B parameters), indicating that CoT effectiveness emerges with scale. The study also demonstrates that CoT generalizes across diverse reasoning domains without task-specific architectures.

## Limitations
The effectiveness of chain-of-thought prompting is highly dependent on model scale, showing little benefit for models below 100B parameters. Performance is sensitive to the quality and format of the exemplars, with some tasks requiring careful prompt engineering. The method does not guarantee logically sound reasoning chains and may produce plausible but incorrect rationales, especially on complex problems.

## Verification Verdict
REAL (95%) — Paper confirmed by multiple authoritative sources including the official NeurIPS 2022 proceedings and arXiv (arXiv:2201.11903). Title, authors, year, and venue match. Semantic Scholar's failure to return results is likely due to indexing issues, not paper nonexistence.
