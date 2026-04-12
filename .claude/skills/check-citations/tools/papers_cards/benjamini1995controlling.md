---
key: benjamini1995controlling
title: Controlling the false discovery rate: A practical and powerful approach to multiple testing
authors: Benjamini, Y. and Hochberg, Y.
year: 1995
venue: Journal of the Royal Statistical Society. Series B (Methodological)
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 100
source_used: arxiv | CrossRef | OpenAlex
---

## Goal
The paper aims to address the problem of multiple hypothesis testing, where conducting many statistical tests simultaneously increases the likelihood of false positives. The authors propose controlling the False Discovery Rate (FDR) as a more powerful and practical alternative to the traditional Family-Wise Error Rate (FWER), particularly in exploratory analyses where some false positives can be tolerated in exchange for greater statistical power.

## Gap Addressed
Traditional multiple testing corrections, such as the Bonferroni method, control the FWER by keeping the probability of any false rejection extremely low, but this often results in very low power, especially when many hypotheses are tested. There was a need for a less stringent yet principled approach that could balance discovery and error control, particularly in large-scale testing scenarios common in fields like genomics and neuroscience.

## Method
The authors introduce a step-up procedure that controls the expected proportion of false rejections among all rejections—the FDR. The method orders the p-values from multiple tests and compares them to a set of increasing thresholds derived from the desired FDR level. It is both computationally simple and more powerful than FWER-controlling methods, making it suitable for large-scale testing problems.

## Datasets and Metrics
**Datasets:** Not applicable (the paper introduces a methodological framework rather than applying it to a specific dataset).

**Metrics:** False Discovery Rate (FDR), statistical power (ability to detect true positives), Type I error rate (specifically, the proportion of false positives among rejected hypotheses).

## Results
The proposed Benjamini-Hochberg (BH) procedure effectively controls the FDR under certain dependency assumptions, particularly independence or positive regression dependency among test statistics. It offers substantially higher power than FWER-controlling methods like Bonferroni, especially as the number of hypotheses increases. The method is shown to be robust and widely applicable across various scientific domains. It has become a standard tool in fields requiring large-scale inference, such as genomics, where it is routinely used in gene expression analysis. Theoretical justification and simulation studies support its validity and superiority in exploratory research settings.

## Limitations
The original BH procedure assumes independence or specific dependency structures among test statistics; its FDR control may not hold under arbitrary dependence. Later work has extended the method to handle more general dependency, but the original version may be overly optimistic in highly correlated settings.

## Verification Verdict
REAL (100%) — Multiple authoritative sources (CrossRef, OpenAlex) confirm the paper with exact title, authors, year, and journal. High citation counts and consistent references in other works support authenticity.
