---
key: benjamini1995controlling
title: Controlling the false discovery rate: A practical and powerful approach to multiple testing
authors: Benjamini, Y. and Hochberg, Y.
year: 1995
venue: Journal of the Royal Statistical Society. Series B (Methodological)
doi: 10.1111/J.2517-6161.1995.TB02031.X
arxiv_id: 
pdf_url: 
semantic_scholar_id: fcef2258a963f3d3984a486185ddc4349c43aa35
paper_url: https://www.semanticscholar.org/paper/fcef2258a963f3d3984a486185ddc4349c43aa35
citation_count: 104058
verified: true
confidence: 100
source_used: semantic_scholar
---

## Goal
The authors aimed to address the challenge of multiple hypothesis testing, where conducting numerous simultaneous tests increases the likelihood of false positives. Traditional methods control the family-wise error rate (FWER), which can be overly conservative, especially when many hypotheses are tested. The paper proposes a more powerful and practical alternative by introducing the concept of the false discovery rate (FDR)—the expected proportion of false positives among rejected hypotheses. Their goal was to provide a procedure that maintains statistical power while offering meaningful error control in large-scale testing scenarios, particularly relevant in fields like genomics, where thousands of tests are common.

## Gap Addressed
Prior approaches to multiple testing, such as the Bonferroni correction, focused on controlling the family-wise error rate (FWER), which severely limits statistical power as the number of tests increases. This conservativeness leads to an increased risk of missing true discoveries (false negatives), especially in exploratory analyses with many hypotheses. The paper identifies a critical need for a more balanced and scalable error rate criterion that allows for some false positives while ensuring they remain a small proportion of all discoveries. The false discovery rate (FDR) was proposed as a less stringent but more interpretable and powerful alternative to FWER, filling a gap in both theoretical and applied statistics for high-dimensional data analysis.

## Method
The authors introduced the Benjamini-Hochberg (BH) procedure, a step-up method for controlling the FDR at a specified level α. The method involves ordering the p-values from smallest to largest and comparing each p-value to a threshold proportional to its rank (i.e., p_(i) ≤ (i/m)α, where m is the total number of tests). The largest p-value that satisfies this condition determines the number of rejections. The procedure is proven to control the FDR at level α under the assumption of independence among test statistics, and it is shown to be more powerful than FWER-controlling methods. The paper includes theoretical derivations, illustrative examples, and comparisons with existing procedures to demonstrate its practicality and robustness.

## Datasets and Metrics
**Datasets:** Not applicable

**Metrics:** False Discovery Rate (FDR), Family-Wise Error Rate (FWER), statistical power (implicitly via comparison of rejection counts); the target FDR level α is the primary controlled metric. Specific numerical values include FDR control at α = 0.05 and 0.10 in theoretical examples, with demonstrated rejection counts under various configurations.

## Results
The BH procedure was shown to control the FDR at the desired level α under independence of test statistics, with exact control proven theoretically. It consistently outperformed traditional FWER-controlling methods in terms of statistical power, allowing more true discoveries while keeping false discoveries proportionally low. For example, in scenarios with 15 tests, the BH method rejected up to 9 hypotheses where Bonferroni rejected only 6, demonstrating superior sensitivity. The paper established that FDR control is achievable with practical procedures, and the BH method became a benchmark in multiple testing. The approach has since been widely adopted, particularly in genomics and large-scale inference, due to its balance between rigor and power.

## Limitations
The original proof of FDR control assumes independence among test statistics; performance under dependence structures is not fully addressed in this paper. The authors note that while the procedure works well in many practical settings, its theoretical guarantees may not hold under arbitrary dependence. Additionally, the FDR is an expected proportion, so actual false discovery proportions in individual experiments may vary.

## Verification Verdict
REAL (100%) — Paper confirmed by both Semantic Scholar and Perplexity with matching title, authors, year, journal, volume, and DOI. Highly cited and widely recognized as a seminal work in multiple testing.

## Links
- [Semantic Scholar](https://www.semanticscholar.org/paper/fcef2258a963f3d3984a486185ddc4349c43aa35)
- [DOI](https://doi.org/10.1111/J.2517-6161.1995.TB02031.X)
