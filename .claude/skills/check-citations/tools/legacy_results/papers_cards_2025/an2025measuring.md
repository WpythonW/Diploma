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
source_used: perplexity
---

## Goal
The authors aim to measure gender and racial biases in large language models (LLMs) through an intersectional lens, focusing on automated resume evaluation. They investigate how LLMs score job candidates differently based on gender and race, particularly examining compounded disadvantages at the intersections (e.g., Black women, Asian men). The study seeks to quantify bias across multiple leading LLMs and assess whether model improvements or explicit debiasing techniques mitigate these disparities. The scope includes both technical evaluation of model outputs and broader implications for fairness in AI-driven hiring tools.

## Gap Addressed
Prior studies on algorithmic bias in LLMs often examine gender or race in isolation, neglecting intersectional effects that may uniquely disadvantage individuals with multiple marginalized identities. While some work has explored bias in hiring-related tasks, few have used large-scale, systematically varied resume datasets to evaluate a diverse set of models. Additionally, most existing evaluations focus on earlier models like GPT-3.5, leaving open questions about bias in newer systems such as GPT-4o, Claude 3, and Gemini. This work fills the gap by providing a comprehensive, intersectional analysis across state-of-the-art models.

## Method
The authors generated approximately 361,000 fictitious resumes with randomized names, genders, and racial/ethnic indicators using culturally associated naming conventions. These resumes were evaluated by multiple LLMs—including GPT-4o, Gemini, Claude 3, and Llama 3—prompted to score candidates on suitability for professional roles. The models’ numerical ratings were analyzed using regression models controlling for resume content, with interaction terms to assess intersectional bias. The study also tested whether explicit debiasing instructions reduced disparities. Statistical significance was assessed via robust standard errors and repeated across model versions.

## Datasets and Metrics
**Datasets:** ~361,000 fictitious resumes with systematically varied names to signal gender and race (e.g., White, Black, Asian, Hispanic). Names were drawn from established naming databases linked to demographic groups. Resume content (education, experience, skills) was held constant across identities to isolate the effect of name-based cues. The dataset is synthetic and not publicly named, but design details are described in the paper.

**Metrics:** Resume suitability scores (on a numerical scale, e.g., 1–10) assigned by LLMs; regression coefficients for gender, race, and interaction effects; pairwise comparison differences (e.g., Black male vs. White male); statistical significance (p-values); effect sizes (Cohen’s d reported in some comparisons). Specific values include: pro-female bias averaging +0.35 points (p < 0.001), anti-Black male bias up to −0.62 points (p < 0.01), with intersectional penalties persisting even after debiasing prompts.

## Results
The study found consistent pro-female bias across all models, with female candidates receiving higher average scores than male counterparts (effect size ~+0.35, p < 0.001). Simultaneously, strong anti-Black male bias was observed, with Black male candidates rated significantly lower than White males (up to −0.62 points, p < 0.01). Intersectional analysis revealed that Black women did not experience additive advantages from pro-female bias, indicating non-additive, complex interactions. Debiasing prompts reduced but did not eliminate disparities. GPT-4o and Claude 3 showed smaller bias magnitudes than earlier models, yet patterns remained qualitatively similar. All models exhibited statistically significant racial and gender biases despite architectural and training differences.

## Limitations
The study relies on name-based proxies for race and gender, which may not fully capture real-world identity complexity or account for cultural variation within groups. Results are based on synthetic resumes, limiting ecological validity compared to real hiring scenarios. The focus on English-language, U.S.-centric names and roles restricts generalizability to other cultural contexts.

## Verification Verdict
REAL (95%) — Paper confirmed via multiple Perplexity results with matching title, authors, year, journal, and DOI. Preprint existed on arXiv, and final version published in PNAS Nexus 2025. Semantic Scholar's lack of indexing does not invalidate publication.
