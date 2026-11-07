# ICLR 2027 — Official Human Reviews (English)

**Paper:** CoEvoMed: Co-Evolving Supervision Principles and Medical Vision–Language Models

**Submission:** 37342

**OpenReview:** https://openreview.net/forum?id=GeL7NntZTU

**Verified on:** 7 November 2026 (Asia/Shanghai)

This document contains all three human Official Reviews shown in the supplied screenshot, checked against the original OpenReview page. The text obscured by the floating toolbar in Reviewer 2Nuw’s second strength was recovered from that page. Original wording, spelling, scores, list structure, and emphasis are preserved; only webpage layout is converted to Markdown. Dates and times below are reproduced as displayed. Program Chairs’ LLM/PAT feedback is excluded. No rebuttal responses or editorial assessment are added.

| Reviewer | Rating | Confidence | Presentation | Informativeness | Soundness |
|---|---|---|---|---|---|
| pUjh | 2: Weak rejection | 3 | 1 | 2 | 2 |
| jcb6 | 3: Weak acceptance | 3 | 3 | 2 | 3 |
| 2Nuw | 2: Weak rejection | 4 | 3 | 2 | 2 |

## Reviewer pUjh

**Original review:** https://openreview.net/forum?id=GeL7NntZTU&noteId=QchN2puNuA

**Posted / modified:** 24 Oct 2026, 02:47 (modified: 06 Nov 2026, 20:30)

**Visibility:** Everyone

### Paper Summary

This paper propose a framework that can co-evolve the curriculum for learning objective and the medcial VLMs. The authors argue that learning gains and learning task usualy evolve unevenly, and this issue limiting the supervision quality. Therefore they are motivated to propose a data and learning objective construction pipeline and model trianing process framework that can evenly improve both. This framework is designed in a way that for every iterative round, the model will first be validated on a validate set and evaluate which capability is insufficient. And the curriculum desginer will adjust the next round learning objective based on this validation report.

### Presentation

1: Difficult to follow despite careful reading.

### Informativeness

2: I learned something interesting or useful.

### Soundness

2: I have minor or fixable concerns about the paper’s soundness.

### Critical Strengths

1. The concept behind the framework design is acceptable. Bascially, this framework is similar to those auto-research project that trying to propose and validate a scientific project by iteratively improve an algorith. But this framework is more about how to leverage medical context to do such job.

2. The experiments are very abudant and sufficient to prove their method's strenght and also honestly showing their weakness

### Critical Weaknesses

1. To me, the multi-agent framework seems unecessary. The experiments do not validate all critical function of each "agent role". Do we reall y need all of these agents or can we easily find another plausible agent process to substitude them.

2. The organization of this paper is relative poor. The authors move most of the detail about the framework design into the appendix, including most important deisng such as evaluation task composition.

3. The method demonstrates reactive recovery from selected capability regressions, but does not establish prevention of catastrophic forgetting or stable balanced convergence. Later-round declines, reliance on R7 checkpoint selection, absence of retention ablations, and lack of standard continual-learning metrics leave the central retention claim only partially supported.

### Questions For Authors

1. For medVLSynther results, do you use the same base model to replicate their results?

2. Would you consider to publicate the data generated in your evolving pipeline?

3. CoEvoMed relies on a hand-designed capability taxonomy to construct validation cells and guide curriculum allocation, but the paper does not justify why these dimensions and categories are necessary. Some datasets, such as SLAKE, already provide question-type annotations that overlap with categories such as organ recognition, abnormality detection, and localization. The authors should report this mapping, validate the generated annotations, and compare the proposed taxonomy against native dataset labels. Otherwise, it remains unclear whether the gains come from meaningful capability diagnosis or an arbitrary relabeling of existing task categories.

### Flag For Ethics Review

No

### Rating

2: Weak rejection

### Confidence

3: I am familiar with this topic and its relevant literature.

## Reviewer jcb6

**Original review:** https://openreview.net/forum?id=GeL7NntZTU&noteId=DgopY8rz3p

**Posted / modified:** 17 Oct 2026, 15:24 (modified: 06 Nov 2026, 20:30)

**Visibility:** Everyone

### Paper Summary

CoEvoMed is a framework that jointly adapts supervision construction and curriculum allocation for training medical vision–language models. A multi-agent pipeline generates and verifies evidence-grounded training examples, revises construction principles using learner feedback, and allocates data-generation effort according to learning progress. Experiments across 2D and 3D medical tasks show improvements in visual question answering and report generation, with additional analyses supporting the value of matching supervision to the learner’s current capabilities.

### Presentation

3: Clear and easy to follow.

### Informativeness

2: I learned something interesting or useful.

### Soundness

3: I have no substantive concerns about the paper’s soundness.

### Critical Strengths

1. Automatically constructing training data from a model’s learning feedback is an interesting and practically valuable research direction. The paper combines evolving construction principles with curriculum allocation to adapt both supervision content and data allocation to the learner’s current weaknesses.

2. The experiments cover 2D and 3D medical VQA and report generation across different model scales and backbones. Comparisons of current versus historical feedback and original versus evolved principles provide evidence that supervision should adapt to the learner’s training stage.

### Critical Weaknesses

The ablation study does not sufficiently isolate the contributions of the individual components. Budget-matched comparisons with fixed principles and a fixed curriculum, principle evolution alone, and curriculum adaptation alone would help determine whether the gains come primarily from high-quality synthetic data or the proposed co-evolution mechanism.

### Questions For Authors

Starting from the same initialization, training on raw data reduces performance on all four VQA benchmarks, with SLAKE accuracy dropping from 64.84% to 38.15%. What causes this substantial degradation? Would cleaning and reconstructing the data using fixed construction principles also yield substantial gains? A budget-matched comparison would help clarify the additional benefit of adaptive principle evolution.

### Flag For Ethics Review

No

### Rating

3: Weak acceptance

### Confidence

3: I am familiar with this topic and its relevant literature.

## Reviewer 2Nuw

**Original review:** https://openreview.net/forum?id=GeL7NntZTU&noteId=0fcUWvow5Z

**Posted / modified:** 12 Oct 2026, 12:04 (modified: 06 Nov 2026, 20:30)

**Visibility:** Everyone

### Paper Summary

The paper proposes CoEvoMed, a framework that couples medical vision-language model training with multi-agent supervision construction. It revises supervision principles and adjusts curriculum allocation using feedback on the learner’s evolving capabilities. The authors evaluate the framework on 2D medical VQA, report generation, and 3D medical tasks, reporting improvements over several baselines and presenting interventions examining feedback alignment and stage-dependent principle utility.

### Presentation

3: Clear and easy to follow.

### Informativeness

2: I learned something interesting or useful.

### Soundness

2: I have minor or fixable concerns about the paper’s soundness.

### Critical Strengths

1. **Stage-dependent supervision is supported by controlled comparisons.** Applying original and evolved construction principles at different checkpoints reveals a reversal in their relative effectiveness. This provides concrete evidence that supervision should adapt to the learner’s training stage, supporting a central motivation of the framework.

2. **Broad medical multimodal evaluation.** The experiments cover 2D visual question answering, report generation, and 3D tasks, with additional backbone evaluations. This breadth provides useful evidence that the framework can apply across multiple medical task formats and model architectures.

### Critical Weaknesses

1. **The experimental controls and mechanism analyses do not sufficiently establish the contribution of co-evolution.** The method combines teacher-generated supervision, data verification, principle revision, and adaptive curricula, but does not adequately isolate their effects or those of additional resources. Improvements are difficult to attribute to individual principles, and the relationship between principle-selection criteria and subsequent learning gains remains unvalidated. The substantial degradation of the raw-data training baseline also lacks sufficient explanation.

2. **Evaluation coverage and statistical reliability remain limited.** The 2D VQA evaluation lacks expert-level, complex medical reasoning tasks, and independent repeated runs or confidence intervals are not clearly reported. On IU-Xray, the 8B model improves over the strongest baseline by only 0.92 RaTEScore points, while the 32B model performs worse than the 8B model. The stability of the gains and benefits of scaling therefore remain unclear.

### Questions For Authors

1. Under the same teachers, data sources, and comparable budgets, could you separately establish the contributions of principle evolution and adaptive curricula, including PPO’s advantage over simpler allocation strategies? Could you also explain the raw-data baseline’s degradation and validate the relationship between principle-selection criteria and subsequent learning gains?

2. How are patient-, study-, and image-level overlaps excluded across support data, internal validation sets, and external tests, particularly between PubMedVision-IU and IU-Xray? Was R7 selected exclusively using a predefined internal validation criterion?

3. How many independent runs underlie the main results, and could you provide standard deviations and paired confidence intervals? Additionally, why is CURE-4B absent from the IU-Xray comparison, and why does the 32B model underperform the 8B model on this dataset?

4. Why were complex reasoning benchmarks such as MedXpertQA-MM or the Health & Medicine portion of MMMU not included? How do the existing results support generalization to complex medical reasoning?

### Flag For Ethics Review

No

### Rating

2: Weak rejection

### Confidence

4: I have substantial direct research experience on this topic.
