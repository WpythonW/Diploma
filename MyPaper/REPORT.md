# Comparative Analysis of Cognitive Biases in Large Language Models
**Comprehensive Report on Experiments 1, 2, and 3**

## 1. Introduction
This paper investigates the presence and intensity of cognitive biases in nine state-of-the-art Large Language Models (LLMs) across three classical psychological paradigms: the Conjunction Fallacy (Probabilistic Reasoning), the Wason Selection Task (Deductive Reasoning), and the 2-4-6 Rule Discovery Task (Inductive Reasoning).

---

## 2. Experiment 1: Conjunction Fallacy (The Linda Problem)

### 2.1. Methodology
We utilized a decontaminated dataset of **130 original biographical vignettes**. Each vignette describes a persona (e.g., a social worker, a pilot).
- **Conditions:** 
  - **Correlated:** The conjunctive option (T & F) contains an element semantically consistent with the biography.
  - **Uncorrelated:** The conjunctive option contains a neutral element.
- **Metrics:** McNemar's test for binary errors and **Delta Bias ($\Delta B$)** to measure shifts in self-reported confidence.

### 2.2. Key Results
- **Widespread Bias:** 8 out of 9 models exhibited a significant conjunction fallacy.
- **The Scale Paradox:** Inside the Gemma family, the larger **Gemma-3-27b** was **12 times** more biased than the 12b version, suggesting that increased semantic capability can paradoxically amplify representativeness heuristics.
- **Confidence Calibration:** Models are highly certain (80-99%) even when committing the fallacy.

**Table 1: Conjunction Fallacy Performance**
| Model | n_pairs | McNemar p | Delta Bias | Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| qwen3-next-80b | 520 | 1.50e-95 | +0.5648 | Very High Bias |
| gemma-3-27b-it | 520 | 3.07e-92 | +0.4975 | Very High Bias |
| gpt-5.2 | 520 | 2.43e-63 | +0.3746 | High Bias |
| claude-sonnet-4.6 | 520 | 1.0 | +0.1049 | Latent Bias only |
| qwen3.5-397b | 3120 | 0.0625 | -0.0052 | No Bias |

---

## 3. Experiment 2: Wason Selection Task (Deductive Reasoning)

### 3.2. Methodology
Models were tested on **400 rules** across four content types:
1. **Formal Logic (Abstract)**
2. **Concrete Facts**
3. **Familiar Social Contracts** (e.g., drinking age)
4. **Unfamiliar Fantasy Social Contracts** (to test deontic structure vs. familiarity)

### 3.2. Key Results
- **Content Effect:** All models showed significant facilitation in social contract conditions compared to abstract ones (median EMA gain of +0.084).
- **Deontic Logic:** Performance in "Fantasy Social Contracts" was nearly as high as in familiar ones, supporting the theory that LLMs recognize the **deontic structure** of obligations rather than just relying on training memory.
- **Chain-of-Thought (CoT) Divergence:** CoT improved performance for proprietary models but **increased biases** for some open models (e.g., GLM-4.7), where models used "thinking" to justify matching bias.

**Table 2: Expected Metric Accuracy (EMA) by Content**
| Model | FL Neutral | Fam. Social | Unf. Fantasy |
| :--- | :---: | :---: | :---: |
| gpt-5.2 | 0.972 | 0.996 | 0.978 |
| qwen3.5-397b | 0.818 | 0.982 | 0.986 |
| gemma-3-27b-it | 0.578 | 0.904 | 0.888 |
| glm-4.7-flash | 0.614 | 0.686 | 0.590 |

---

## 4. Experiment 3: 2-4-6 Rule Discovery (Inductive Reasoning)

### 4.1. Methodology
An interactive dialogue where models must discover a hidden rule (e.g., "strictly increasing sequence").
- **Metrics:** **Success Rate (SR)** and **Confirming Test Rate (CTR)**. A high CTR indicates the model is only testing triples that it *expects* to be true, failing to falsify.

### 4.2. Key Results
- **Universal Confirmation Bias:** In the baseline condition, all non-reasoning models showed high CTR (>0.63), indicating a failure to adopt a falsificationist strategy.
- **Reasoning Advantage:** Only models with native "reasoning" (extended thinking) could effectively break the confirmation bias loop. GPT-5.2 reasoning achieved the highest SR (0.48).
- **The Qwen Paradox:** Qwen 3.5 reduced its CTR significantly (became more "falsificationist") in the adaptive condition, yet its Success Rate **fell**, highlighting a gap between testing strategy and hypothesis revision.

**Table 3: 2-4-6 Performance (Baseline vs. Adaptive)**
| Model | SR (Base) | SR (Adap) | CTR (Base) | CTR (Adap) |
| :--- | :---: | :---: | :---: | :---: |
| gpt-5.2 (reasoning) | 0.38 | 0.48 | 0.726 | 0.559 |
| claude-sonnet-4.6 | 0.28 | 0.28 | 0.812 | 0.787 |
| deepseek-v3.2 | 0.10 | 0.16 | 0.879 | 0.768 |
| gemma-3-27b-it | 0.04 | 0.10 | 0.688 | 0.842 |

---

## 5. Synthesis and Conclusion
The cross-paradigm analysis reveals that cognitive biases in LLMs are **multidimensional**. A model's performance in one type of reasoning (e.g., deduction) does not predict its susceptibility to bias in another (e.g., probabilistic judgment). 

**Key takeaways:**
1. **Representativeness** is amplified by semantic richness (Experiment 1).
2. **Deontic structures** facilitate logic more than simple familiarity (Experiment 2).
3. **Inductive falsification** remains the most difficult task, requiring native reasoning capabilities to overcome innate confirmation bias (Experiment 3).
