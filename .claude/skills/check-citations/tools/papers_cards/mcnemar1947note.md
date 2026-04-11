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
confidence: 95
source_used: perplexity
---

## Goal
The paper aims to address the statistical challenge of determining the significance of the difference between two correlated proportions, which commonly arise in repeated measures or matched-pair study designs. Prior methods were inadequate for handling dependencies between proportions, especially in psychological and educational testing contexts. McNemar sought to provide a rigorous method for assessing whether changes in binary responses (e.g., before and after an intervention) are statistically significant. The focus is on improving inference accuracy by accounting for the correlation between paired observations.

## Gap Addressed
Existing statistical tests at the time did not properly account for the dependency between paired binary outcomes, leading to inaccurate standard error estimates and invalid significance testing. Traditional chi-square tests assumed independence, which is violated in within-subjects or matched designs. McNemar identified this flaw in applying standard methods to correlated data and aimed to correct it by deriving a proper sampling error formula. His work fills a critical methodological gap in psychometrics and behavioral sciences where pre-test/post-test or matched-pair designs are common.

## Method
McNemar derived a formula for the standard error of the difference between two correlated proportions using a 2×2 contingency table of discordant and concordant pairs. He proposed a test statistic based on the counts of discordant pairs (i.e., cases where one member of the pair changes but the other does not), which is equivalent to a chi-square distribution with one degree of freedom. The resulting test—now known as McNemar's Test—focuses on the off-diagonal elements of the table, effectively isolating the variability due to change. The method assumes that the two proportions are derived from the same sample or matched pairs.

## Datasets and Metrics
**Datasets:** Not applicable

**Metrics:** Not applicable

## Results
The paper introduced a statistically valid method for testing the significance of changes in binary responses within paired samples. The proposed test statistic follows a chi-square distribution and is shown to be more accurate than existing methods when data are correlated. It became the standard approach for analyzing matched-pair binary data and is widely implemented in statistical software. The test is particularly powerful in studies with small sample sizes due to its exact binomial properties under certain conditions. The work has been cited over 3,750 times and remains a cornerstone of nonparametric statistics.

## Limitations
The test is limited to binary outcomes and 2×2 contingency tables, making it inapplicable to multi-category or continuous data. It assumes that the data are paired or matched and that the discordant pair counts are sufficiently large for the chi-square approximation to hold, though exact versions exist for small samples.

## Verification Verdict
REAL (95%) — Verified via Perplexity with matching title, author, journal, year, volume, and DOI (10.1007/BF02295996). The paper is widely recognized as the original source of McNemar's Test, with over 3,750 citations. Semantic Scholar may have failed to index it due to its age, but external confirmation is strong.
