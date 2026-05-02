# Diploma Criteria

## 1. Relevance

Research relevance is determined by the priority of the scientific problem at the present time, the resolution of a concrete research problem, and the identification of gaps in the state of the art. The problem statement must be grounded in specific academic sources.

Possible artifacts:

- a full literature review has been conducted, and the limitations of existing approaches have been identified correctly;
- a research hypothesis or research question has been formulated;
- the work is connected to current trends in the field (ML, CV, NLP, RL, robotics, multimodality, etc.).

## 2. Practical Significance and Value

This criterion concerns developing a result that can effectively support sustainable change in a given domain. The results should be useful for specialists and/or end users. The need for such an approach should be supported by both academic evidence and practical considerations.

Possible artifacts:

- a clear target group and its needs have been identified;
- specific application scenarios for the result have been described;
- the improvements or new capabilities created by the research have been demonstrated;
- there is evidence of significance (expert discussions, talks, feedback).

## 3. Novelty

This criterion includes the distinction between the proposed method and state-of-the-art solutions, as well as the contribution to the scientific field.

Possible artifacts:

- positioning relative to the state of the art has been carried out correctly;
- the scientific contribution has been described: a new method, architecture modification, pipeline, dataset, metrics, reproducibility improvement, and so on;
- expert confirmation is available (from supervisors, reviewers, or authors of related work).

## 4. Effectiveness of the Solution

This criterion shows whether the method is better than or comparable to existing approaches, whether its effect has been demonstrated experimentally, whether the experimental methodology is sound, and whether the study's limitations have been identified.

Possible artifacts:

- a reproducible experimental cycle is provided: baseline → method → comparison;
- metrics are reported on known benchmarks or datasets;
- quality, error, robustness, and limitation analyses have been conducted;
- it has been shown that the method achieves the stated goals.

## 5. Technical Complexity and Implementation Quality

This criterion describes whether the study has been designed competently, whether models, methods, metrics, and data have been selected appropriately, which technical challenges were solved, and what the student's personal contribution was.

Possible artifacts:

- the implementation is structured, correct, and reproducible;
- the student's personal technical contribution is stated clearly;
- understanding of methodology and experimental design is demonstrated;
- risks and limitations have been taken into account (bias, validation, overfitting).

## 6. Scaling Potential

The main dimensions here are the future development trajectory of the research, scaling risks, and interest from the academic and industrial communities. Visibility of the results in academic or professional communities and the presence of feedback are also considered.

Possible artifacts:

- an assessment of risks and development paths for scaling;
- confirmed interest from the academic community or industry partners;
- a roadmap for extending the research: a series of papers, applications in other domains, a grant proposal, participation in international collaborations.

---

## Recommendations for Formulating the Thesis Topic

The title of the thesis and the title of the project are not the same. For example, a project may be called `SAYIT`, while the thesis topic may be formulated as `Development of an LLM Agent for Dynamic Learning Support`.

Recommendations:

1. The ideal formula is: `Development/Research/Creation of _______ for/with the goal of ________`.
2. The title should be composed of Russian words only, without slang, colloquial wording, or abbreviations.
3. Do not specify narrow concrete technologies, because they may change during the work.
4. Do not make the title too general; it should reflect your personal contribution. If you work in a team, each team member should have an individual thesis title reflecting their personal contribution and role in the project.

For a thesis submitted in the scientific article format, the thesis topic matches the article title and should be provided in both Russian and English.

The thesis may be defended either in Russian or in English. If it is defended in English, the full thesis text must also be in English.

---

## Official Chapter Structure (4-Chapter Framework)

> **Source:** Recommendation from MSc program supervisor (Magistratura track lead).
> Applicable to all tracks; below is the **scientific track adaptation** (no deployment/engineering chapter).

### Chapter 1. Introduction to the Domain. Problem Analysis. Related Work. Problem Statement and Hypotheses.

- Problem statement and relevance justification
- Comprehensive literature review with critical analysis
- Identification of gaps in the state of the art
- Research question(s) and hypothesis formulation
- Definition of scope, objectives, and evaluation criteria
- *(Maps to Criteria: Relevance, Novelty)*

### Chapter 2. Research: Experiments, Model/Approach Selection, Comparison with Baselines.

- Experimental design and methodology
- Model/approach selection rationale
- Baseline comparisons and ablation studies
- Data collection, dataset construction, contamination control
- Metrics definition and statistical protocol
- Experimental results (per-experiment or per-paradigm)
- Cross-experiment comparison and hypothesis validation
- *(Maps to Criteria: Effectiveness, Technical Complexity)*

### Chapter 3. Technical Implementation: Architecture, Development, Reproducible Pipeline.

> **Note for scientific track:** No deployment or production engineering. This chapter covers the **reproducible experimental framework** — code architecture, data pipelines, metric implementations, and infrastructure that enables the research.

- Software architecture of the experimental framework
- Data pipeline and dataset generation/management
- Implementation of metrics and evaluation scripts
- Reproducibility infrastructure (dependency management, config, logging)
- Technical challenges encountered and solutions
- *(Maps to Criteria: Technical Complexity and Implementation Quality)*

### Chapter 4. Validation, Limitations, Scientific Dissemination.

- Validation of results (statistical rigor, robustness checks)
- Threats to validity and methodological limitations
- Scientific impact: publications, presentations, peer feedback
- Interpretation of findings in the context of hypotheses
- Future research directions and scaling potential
- *(Maps to Criteria: Scaling Potential, Practical Significance)*

---

## Additional Thesis Requirements

### Statements Submitted for Defense

The **statements submitted for defense** (item 4 of the official requirements) are described as key results and conclusions showing the usefulness and value of the research or development. These appear in the **Conclusion** chapter.

### Author's Personal Contribution

The **author's personal contribution** (item 9 of the official requirements) must be clearly identified and distinguished from the contributions of other project team members. The main body of the thesis should primarily reflect the author's own contribution. This is stated in the **Introduction and/or Conclusion**.

The thesis may be completed by a team of students; however, each participant must submit a thesis that emphasizes their own contribution to the project.

### Use of AI Tools Disclosure

A section titled **Use of AI Tools and Author's Contribution** (item 11 of the official requirements) must be included (for Russian-language theses, the corresponding Russian title is used). In this section, the student transparently documents which AI tools were used during thesis writing, solution development, project work, experiments, and analysis of results.

The thesis must also account for the anti-plagiarism and AI-use disclosure requirements described in the corresponding guidance materials.

### Formal Structure and Formatting

- Special requirements for a thesis in the scientific article format are defined in Chapter 3 of the official document.
- The thesis must comply with ITMO University's local regulation `Requirements for Theses`, as well as with the requirements of the educational program.
- The recommended length of a master's thesis is **60 to 80 pages**, excluding appendices.

The thesis includes the following structural elements:

- title page (completed and generated via `my.itmo`);
- assignment sheet (completed and generated via `my.itmo`);
- abstract (completed and generated via `my.itmo`);
- table of contents;
- thesis text;
- list of references;
- appendices (optional).

### Interdisciplinary Requirement (ITMO Advanced Engineering School Track)

For defense within the ITMO Advanced Engineering School track, the work must be interdisciplinary, including analysis of multiple subject areas and their interaction or overlap.

---

## ИТОГОВАЯ СВОДКА — Аудит диплома по критериям

> **Дата аудита:** 2026-04-29
> **Статусы:** ✅ DONE | ⚠️ NEEDS WORK | ❌ MISSING | 🔧 IN PROGRESS

| # | Критерий | Статус | Проблема | Приоритет |
|---|---|---|---|---|
| 1 | Актуальность (Relevance) | ✅ DONE | Введение содержит анализ проблемы и пробела в литературе. Можно чуть чётче сформулировать «проанализировали X работ → выявили пробел → поэтому…» | Низкий |
| 2 | Практическая значимость | ✅ DONE | Три конкретных сценария + целевая аудитория + пример с claude-sonnet-4.6. Один из сильнейших разделов. | — |
| 3 | Новизна (Novelty) | ✅ DONE | 6 пунктов новизны, сравнение с CogBench/BIG-bench/Binz/Suri. Рекомендация: добавить 1-2 прямых контрастных сравнения с SOTA во введении. | Низкий |
| 4 | Эффективность решения | ⚠️ NEEDS WORK | **КРИТИЧЕСКИ: conclusion.tex — шаблон-заглушка** (текст про «классификацию данных и глубокие нейронные сети», не по теме). Метрики и таблицы есть, но заключение надо переписать полностью. | **ВЫСОКИЙ** |
| 5 | Личный вклад + техническая сложность | ✅ DONE | Подробный параграф с перечислением: датасеты, пайплайн, метрики, анализ. Прозрачное раскрытие использования ИИ. | — |
| 6 | Публичность и обратная связь | ⚠️ NEEDS WORK | Только кандидатский экзамен в ИТМО. Рукопись «планируется к подаче» — не опубликована. Нет препринта, нет внешних отзывов. Рекомендация: опубликовать препринт/код, получить внешний фидбек. | Средний |
| 7 | Потенциал масштабирования | ⚠️ NEEDS WORK | Нигде прямо не обсуждается: расширение на новые модели/парадигмы/языки, интеграция в CI/CD, применение в индустрии. Нужно добавить раздел в главу 4 или заключение. | Средний |

### Критические действия (по приоритету)

1. **[ВЫСОКИЙ] Переписать conclusion.tex** — сейчас шаблонный текст не по теме диплома. Должно отражать реальные результаты: гипотезы H1–H4, выводы по экспериментам, ограничения, дальнейшие работы.
2. **[СРЕДНИЙ] Добавить раздел о масштабировании** — в главу 4 или заключение: как фреймворк расширяется на новые модели, парадигмы, языки; интеграция в production.
3. **[СРЕДНИЙ] Усилить публичность** — опубликовать код/датасеты на GitHub, выложить препринт, зафиксировать отзывы экспертов.
4. **[НИЗКИЙ] Уточнить формулировку актуальности** — добавить во введение явную фразу «проанализировав X работ за 2023–2025 гг., мы выявили…».
5. **[НИЗКИЙ] Добавить контрастные сравнения с SOTA** — 1-2 прямых предложения «В отличие от работы X, мы…» в разделе новизны.
