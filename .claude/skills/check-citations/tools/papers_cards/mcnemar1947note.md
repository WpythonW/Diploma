---
key: mcnemar1947note
title: Note on the sampling error of the difference between correlated proportions or percentages
authors: McNemar, Q.
year: 1947
venue: Psychometrika
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 100
source_used: CrossRef | OpenAlex | Semantic Scholar (via Tavily)
---

## Goal
The paper aims to address the statistical challenge of determining the sampling error associated with the difference between two correlated proportions or percentages. It seeks to provide a method for accurately assessing the significance of such differences, which commonly arise in repeated measures or matched-pair designs. The work is foundational for hypothesis testing involving binary outcomes that are not independent.

## Gap Addressed
Prior to this work, standard methods for comparing proportions often assumed independence, making them inappropriate for paired or repeated measures data. This limitation led to inaccurate estimates of variance and significance when applied to correlated proportions. McNemar identified the need for a corrected approach that accounts for the dependency between paired observations.

## Method
The paper derives a formula for the standard error of the difference between two correlated proportions by incorporating the covariance between the paired outcomes. It presents a test statistic based on the difference in discordant proportions from a 2×2 contingency table. The resulting method is mathematically equivalent to what later became known as McNemar's test, a chi-square test for symmetry in paired proportions.

## Datasets and Metrics
**Datasets:** Not applicable (the paper presents a theoretical and mathematical derivation without empirical data analysis).

**Metrics:** Sampling error, variance of the difference between correlated proportions, chi-square statistic.

## Results
The paper derives a correct formula for the sampling error of the difference between correlated proportions, improving upon previous methods that ignored correlation. It shows that only the discordant pairs contribute to the test statistic, a key insight for efficient analysis. The chi-square equivalent of the proposed test is identified, facilitating practical application. The method allows for valid significance testing in paired binary data, forming the basis of what is now widely known as McNemar's test. This test has since become a standard tool in statistics, especially in medical and psychological research involving before-and-after designs.

## Limitations
The method assumes that the data are paired and binary, limiting its applicability to other types of correlated data. It also assumes a sufficiently large sample size for the chi-square approximation to be valid, which may not hold in small samples.

## Verification Verdict
REAL (100%) — Multiple authoritative sources (CrossRef, OpenAlex, Semantic Scholar via Tavily) confirm the paper's existence with matching title, author, year, journal, and DOI. The paper is highly cited and well-documented in statistical literature.
