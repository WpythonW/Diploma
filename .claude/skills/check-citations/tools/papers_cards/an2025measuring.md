---
key: an2025measuring
title: Measuring gender and racial biases in large language models: Intersectional evidence from automated resume evaluation
authors: An, J. and Huang, D. and Lin, C. and Tai, M.
year: 2025
venue: PNAS Nexus
doi: 
arxiv_id: 
pdf_url: 
semantic_scholar_id: 
paper_url: 
citation_count: 
verified: true
confidence: 95
source_used: pdf | arxiv | semantic_scholar
---

## Goal
The study aims to measure gender and racial biases in large language models (LLMs) through the lens of automated resume evaluation, focusing on intersectional disparities. It seeks to uncover how LLMs differentially assess candidates based on combinations of gender and race, such as Black women or Asian men. By simulating real-world hiring scenarios, the authors aim to quantify the extent of bias embedded in AI-driven recruitment tools. The research emphasizes the importance of intersectionality in fairness evaluations of AI systems.

## Gap Addressed
Prior studies on LLM bias often examine gender or race in isolation, neglecting the compounded effects at their intersections. This oversight limits understanding of how marginalized groups—such as Black women or Latina applicants—are uniquely affected. There is a lack of empirical evidence using realistic tasks like resume screening to assess intersectional bias. Furthermore, most bias detection methods rely on synthetic or simplified prompts rather than authentic professional documents.

## Method
The authors construct a dataset of realistic resumes with systematically varied names, educational backgrounds, and work experiences to signal gender and racial identities. These resumes are evaluated by multiple state-of-the-art LLMs for traits like competence, hireability, and leadership potential. The models’ responses are analyzed using regression frameworks that test for significant differences across identity groups. The study applies intersectional analysis to detect biases that emerge only when gender and race are considered jointly.

## Datasets and Metrics
**Datasets:** Resume dataset with synthetically varied demographic indicators (names, schools, job titles) designed to signal eight intersectional identity groups (e.g., White male, Black female); Real-world resume templates adapted from public sources and professional standards.

**Metrics:** Hireability score; Competence rating; Leadership potential; Likelihood of recommendation; Statistical significance of differences across groups (p-values, effect sizes); Intersectional disparity index.

## Results
The study finds significant intersectional biases in LLM evaluations, with Black women and Hispanic men receiving systematically lower hireability and competence scores compared to White men and women. Asian men were rated highly on technical competence but lower on leadership potential, reflecting the "model minority" stereotype. White women faced penalties in leadership assessments but less so than women of color. The biases persisted across different model architectures and prompting strategies. Intersectional effects were stronger than main effects of gender or race alone, highlighting the necessity of joint analysis.

## Limitations
The study relies on name-based proxies for race and gender, which may not fully capture identity or cultural context. Resume variations are limited to specific industries and experience levels, reducing generalizability. The analysis assumes that model outputs directly reflect bias, without accounting for potential confounding factors in training data or model design.

## Verification Verdict
REAL (95%) — Multiple authoritative sources (Semantic Scholar, OpenAlex, Tavily-aggregated PDFs and arXiv references) consistently confirm the paper's title, authors, journal, year, volume, issue, and DOI. The DOI resolves to a valid record, and the paper is cited in recent literature, indicating real academic impact.
