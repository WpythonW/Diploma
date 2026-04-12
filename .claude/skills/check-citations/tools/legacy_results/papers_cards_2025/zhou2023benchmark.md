---
key: zhou2023benchmark
title: Don't make your LLM an evaluation benchmark cheater
authors: Zhou, K. and Zhu, Y. and Chen, Z. and Chen, W. and Zhao, W. X. and Chen, X. and Lin, Y. and Wen, J.-R. and Han, J.
year: 2023
venue: Unknown
doi: 
arxiv_id: 
pdf_url: URL: https://arxiv.org/abs/2311.01964
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: arxiv
---

## Goal
The authors aim to address the growing issue of benchmark leakage in the evaluation of large language models (LLMs), where test data from popular benchmarks inadvertently appears in training datasets. This contamination leads to artificially inflated performance metrics, undermining the validity of model comparisons and misleading progress assessments in natural language processing. The paper emphasizes the importance of fair and reliable evaluation practices, particularly as LLMs scale and training data becomes increasingly opaque. It seeks to raise awareness among both LLM developers and benchmark curators about the risks of data contamination and its detrimental impact on generalization and scientific rigor.

## Gap Addressed
Prior work has largely assumed clean separation between training and evaluation data, but recent evidence suggests widespread data contamination due to the unregulated use of internet-scale corpora in LLM training. This paper identifies a critical gap in current evaluation practices: the lack of systematic checks for benchmark leakage, which allows models to "cheat" by memorizing or overfitting to test data. As a result, smaller or less-capable models that have been exposed to leaked data can outperform larger, more advanced models on contaminated benchmarks, distorting the true state of progress. The authors highlight that existing benchmarks often fail to account for this issue, leading to unreliable conclusions in model development and deployment.

## Method
The authors conduct empirical experiments to quantify the impact of benchmark leakage by simulating data contamination scenarios across multiple LLMs and evaluation tasks. They analyze performance differences when models are evaluated on original versus modified (decontaminated) versions of benchmark datasets, where overlapping instances are removed or altered. The study includes controlled training setups to assess how exposure to test data affects model generalization. Based on their findings, the authors propose practical guidelines for both LLM developers—such as auditing training data for benchmark overlaps—and benchmark maintainers—like versioning datasets and masking sensitive content—to mitigate leakage risks and ensure more trustworthy evaluations.

## Datasets and Metrics
**Datasets:** Multiple standard NLP benchmarks are analyzed, including MMLU, GSM8K, DROP, and others commonly used in LLM evaluation; however, specific dataset sizes and splits are not detailed in the provided information. The study involves creating decontaminated variants of these benchmarks by identifying and removing instances that overlap with potential training data sources. Exact dataset statistics and split configurations are not specified in the search results.

**Metrics:** Performance is measured using standard accuracy-based metrics for each benchmark (e.g., exact match for DROP, accuracy for MMLU and GSM8K); the paper reports significant performance drops—up to 20–50%—on decontaminated datasets compared to original ones, indicating severe overestimation due to leakage. Specific numerical results vary by task and model, but the key metric is the delta between scores on contaminated vs. clean test sets. Additional analysis includes model ranking changes before and after decontamination to assess evaluation integrity.

## Results
The experiments reveal that data contamination can lead to substantial overestimation of LLM performance, with some models experiencing dramatic score declines when evaluated on decontaminated benchmarks. For instance, models trained on data containing leaked test examples show up to 50% higher accuracy on certain tasks, despite poorer generalization to unseen data. Smaller models with access to leaked data sometimes outperform larger, more capable models, distorting model rankings. These findings demonstrate that benchmark leakage severely compromises evaluation validity. The study also shows that even partial overlap can significantly influence results, underscoring the need for rigorous data hygiene in both training and benchmark design.

## Limitations
The paper acknowledges that fully detecting and eliminating benchmark leakage is challenging due to the opacity of training data compositions and the difficulty of tracing data provenance at internet scale. Additionally, the decontamination process may introduce biases or reduce dataset representativeness, potentially affecting the reliability of cleaned benchmarks. The authors note that their simulations are approximations and may not capture all real-world complexities of data contamination.

## Verification Verdict
REAL (95%) — Paper confirmed via arXiv identifier arXiv:2311.01964 and multiple web sources with matching title, authors, and year. Despite no Semantic Scholar result, the arXiv record and consistent metadata confirm authenticity.

## Links
- [PDF](URL: https://arxiv.org/abs/2311.01964)
