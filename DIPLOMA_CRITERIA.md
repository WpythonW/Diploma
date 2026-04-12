# Diploma Criteria

1. Relevance

Research relevance is determined by the priority of the scientific problem at the present time, the resolution of a concrete research problem, and the identification of gaps in the state of the art. The problem statement must be grounded in specific academic sources.

Possible artifacts:

- a full literature review has been conducted, and the limitations of existing approaches have been identified correctly;
- a research hypothesis or research question has been formulated;
- the work is connected to current trends in the field (ML, CV, NLP, RL, robotics, multimodality, etc.).

2. Practical Significance and Value

This criterion concerns developing a result that can effectively support sustainable change in a given domain. The results should be useful for specialists and/or end users. The need for such an approach should be supported by both academic evidence and practical considerations.

Possible artifacts:

- a clear target group and its needs have been identified;
- specific application scenarios for the result have been described;
- the improvements or new capabilities created by the research have been demonstrated;
- there is evidence of significance (expert discussions, talks, feedback).

3. Novelty

This criterion includes the distinction between the proposed method and state-of-the-art solutions, as well as the contribution to the scientific field.

Possible artifacts:

- positioning relative to the state of the art has been carried out correctly;
- the scientific contribution has been described: a new method, architecture modification, pipeline, dataset, metrics, reproducibility improvement, and so on;
- expert confirmation is available (from supervisors, reviewers, or authors of related work).

4. Effectiveness of the Solution

This criterion shows whether the method is better than or comparable to existing approaches, whether its effect has been demonstrated experimentally, whether the experimental methodology is sound, and whether the study’s limitations have been identified.

Possible artifacts:

- a reproducible experimental cycle is provided: baseline -> method -> comparison;
- metrics are reported on known benchmarks or datasets;
- quality, error, robustness, and limitation analyses have been conducted;
- it has been shown that the method achieves the stated goals.

5. Technical Complexity and Implementation Quality

This criterion describes whether the study has been designed competently, whether models, methods, metrics, and data have been selected appropriately, which technical challenges were solved, and what the student’s personal contribution was.

Possible artifacts:

- the implementation is structured, correct, and reproducible;
- the student’s personal technical contribution is stated clearly;
- understanding of methodology and experimental design is demonstrated;
- risks and limitations have been taken into account (bias, validation, overfitting).

6. Scaling Potential

The main dimensions here are the future development trajectory of the research, scaling risks, and interest from the academic and industrial communities. Visibility of the results in academic or professional communities and the presence of feedback are also considered.

Possible artifacts:

- an assessment of risks and development paths for scaling;
- confirmed interest from the academic community or industry partners;
- a roadmap for extending the research: a series of papers, applications in other domains, a grant proposal, participation in international collaborations.

## Recommendations for Formulating the Thesis Topic

The title of the thesis and the title of the project are not the same. For example, a project may be called `SAYIT`, while the thesis topic may be formulated as `Development of an LLM Agent for Dynamic Learning Support`.

Recommendations for formulating the thesis topic:

1. The ideal formula is: `Development/Research/Creation of _______ for/with the goal of ________`.
2. The title should be composed of Russian words only, without slang, colloquial wording, or abbreviations.
3. Do not specify narrow concrete technologies, because they may change during the work.
4. Do not make the title too general; it should reflect your personal contribution. If you work in a team, each team member should have an individual thesis title reflecting their personal contribution and role in the project.

For a thesis submitted in the scientific article format, the thesis topic matches the article title and should be provided in both Russian and English.

The thesis may be defended either in Russian or in English. If it is defended in English, the full thesis text must also be in English.

## Official Chapter Structure (4-Chapter Framework)

> **Source:** Recommendation from MSc program supervisor (Magistratura track lead).
> Applicable to all tracks; below is the **scientific track adaptation** (no deployment/engineering chapter).

The recommended structure for a scientific-track thesis is **four chapters**:

### Глава 1. Введение в предметную область. Анализ проблемы. Related Work. Постановка задачи и гипотезы.

- Problem statement and relevance justification
- Comprehensive literature review with critical analysis
- Identification of gaps in the state of the art
- Research question(s) and hypothesis formulation
- Definition of scope, objectives, and evaluation criteria
- *(Maps to Diploma Criteria: Relevance, Novelty)*

### Глава 2. Исследование: эксперименты, выбор моделей / подходов, сравнение с базовыми линиями.

- Experimental design and methodology
- Model/approach selection rationale
- Baseline comparisons and ablation studies
- Data collection, dataset construction, contamination control
- Metrics definition and statistical protocol
- Experimental results (per-experiment or per-paradigm)
- Cross-experiment comparison and hypothesis validation
- *(Maps to Diploma Criteria: Effectiveness, Technical Complexity)*

### Глава 3. Техническая реализация: архитектура, разработка, воспроизводимый пайплайн.

> **Note for scientific track:** No deployment or production engineering. This chapter covers the **reproducible experimental framework** — code architecture, data pipelines, metric implementations, and infrastructure that enables the research.

- Software architecture of the experimental framework
- Data pipeline and dataset generation/management
- Implementation of metrics and evaluation scripts
- Reproducibility infrastructure (dependency management, config, logging)
- Technical challenges encountered and solutions
- *(Maps to Diploma Criteria: Technical Complexity and Implementation Quality)*

### Глава 4. Валидация, ограничения, научная апробация.

- Validation of results (statistical rigor, robustness checks)
- Threats to validity and methodological limitations
- Scientific impact: publications, presentations, peer feedback
- Interpretation of findings in the context of hypotheses
- Future research directions and scaling potential
- *(Maps to Diploma Criteria: Scaling Potential, Practical Significance)*

---

### Mapping: 4-Chapter Structure ↔ Required Thesis Elements

| Required Element (from DIPLOMA_CRITERIA §1–11) | Primary Chapter |
|---|---|
| 1. Problem description + relevance | Ch. 1 (Introduction) |
| 2. Research/development task | Ch. 1 |
| 3. Solution concept + hypotheses + metrics | Ch. 1 (end) / Ch. 2 (intro) |
| 4. Statements submitted for defense | Conclusion |
| 5. Review of known solutions + critical analysis | Ch. 1 |
| 6. Scientific novelty | Ch. 1 (end) / Ch. 2 (intro) |
| 7. Path toward solution + technical complexity | Ch. 2 + Ch. 3 |
| 8. Degree of readiness + feedback | Ch. 4 |
| 9. Author's personal contribution | Intro / Conclusion |
| 10. Impact + validation approach | Ch. 4 |
| 11. Use of AI Tools disclosure | Separate section |

---

## Requirements for the Thesis Text

- Special requirements for a thesis in the scientific article format are defined in Chapter 3 of the official document.
- The thesis must comply with ITMO University's local regulation `Requirements for Theses`, as well as with the requirements of the educational program.
- The **4-chapter structure above** is the officially recommended framework for scientific-track MSc theses.

The thesis includes the following structural elements:

- title page (completed and generated via `my.itmo`);
- assignment sheet (completed and generated via `my.itmo`);
- abstract (completed and generated via `my.itmo`);
- table of contents;
- thesis text;
- list of references;
- appendices (optional).

The recommended length of a master’s thesis is **60 to 80 pages**, excluding appendices.

The thesis text should cover the following aspects of the work:

1. Description of the **problem**, including justification of its significance and relevance (usually in the Introduction):
   - what the original problem is;
   - who the target audience or end users of the solution are;
   - whether the problem is interdisciplinary;
   - why the problem and the corresponding task need to be addressed now.
2. The **research/development task** is formulated both in the language of business requirements and in terms of a technical task (for example, a machine learning or data analysis task).
3. The **solution concept** and the main **research hypotheses** (or product hypothesis) are described together with the criteria and metrics used to evaluate them.
4. The **statements submitted for defense** are described as key results and conclusions showing the usefulness and value of the research or development.
5. A **review of known solutions** and related work is provided, including a critical analysis of current sources by the author.
6. The scientific and/or applied **novelty** of the work is identified relative to existing known solutions.
7. The **path toward developing the solution** and/or the research plan is defined and justified, and the **technical complexity** and depth of the solution are explained, including problems solved during the work and lessons learned from successful or unsuccessful hypotheses.
8. The current **degree of readiness of the solution** is defined, together with substantive feedback from end users, the customer, or other stakeholders, and a plan for future improvements is formulated.
9. The **author’s personal contribution** is clearly identified and distinguished from the contributions of other project team members. The main body of the thesis should primarily reflect the author’s own contribution.
10. The **impact** is defined as the measurable effect of the work results on the original problem, and the approach to **validation of results** is justified. The evaluation must be objective and adequate to the claimed impacts, and it must be verifiable by experts and the scientific supervisor, interpretable, and reproducible.
11. A section titled **Use of AI Tools and Author’s Contribution** must be included (for Russian-language theses, the corresponding Russian title is used). In this section, the student transparently documents which AI tools were used during thesis writing, solution development, project work, experiments, and analysis of results.

The thesis must also account for the anti-plagiarism and AI-use disclosure requirements described in the corresponding guidance materials.

For defense within the ITMO Advanced Engineering School track, the work must be interdisciplinary, including analysis of multiple subject areas and their interaction or overlap.

The thesis may be completed by a team of students; however, each participant must submit a thesis that emphasizes their own contribution to the project.
