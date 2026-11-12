# Rebuttal Responses — Submission 37342 (CoEvoMed)

Reviewer comments are quoted (>) for reference only and are not part of the posted text. Post only the response text. Each reviewer's response goes in one Official Comment of at most 5,000 characters.

---

## Response to Reviewer pUjh

*Posted text: 4,984 / 5,000 characters (quotes excluded).*

> **Weakness 1:** To me, the multi-agent framework seems unecessary. The experiments do not validate all critical function of each "agent role". Do we reall y need all of these agents or can we easily find another plausible agent process to substitude them.

**W1 (Necessity of the multi-agent framework).** The main text already tests the agents: **Sec. 5.2** against raw data, and **Table 2** by ablating curriculum adaptation and principle evolution on VQA-RAD and MIMIC-CXR. For space, **App. D** gives full results; below are the four VQA benchmarks shared by **Tables 7–9**, all else fixed:

| Without | From | VQA-RAD | SLAKE | PMC-VQA | PathVQA |
|---|---|---|---|---|---|
| All agents: raw data | base | −13.75 | −26.69 | −8.62 | −6.83 |
| Revision agent: original principles | R5 | −5.64 | −3.60 | −9.60 | −2.20 |
| Curriculum adaptation: R2 feedback | R5 | −1.10 | −5.20 | −3.60 | −3.10 |
| Curriculum adaptation: R3 feedback | R5 | −1.77 | −5.80 | −1.80 | −2.40 |
| None: CoEvoMed | base | +25.72 | +26.76 | +13.82 | +26.63 |
| None: CoEvoMed | R5 | +2.62 | +0.69 | +0.52 | +1.13 |

Each agent fixes a failure these results expose:

1. **Construction.** The selector picks evidence, the constructor writes questions from it, and the verifier, a different model, checks them against the image. With no agents, raw data lower all four scores despite about 700,000 examples, more than CoEvoMed uses (**Sec. 5.2**): 58.3% of raw 2D records are figure descriptions, not questions (**Fig. 10**).
2. **Principle revision.** The revision agent updates construction principles as the learner's errors change. Original principles help at R2 but hurt at R5 (**Table 2**, Panel B).
3. **Curriculum allocation.** The planner allocates the budget from current validation feedback. Stale R2 or R3 feedback lowers all four scores, while current feedback raises them.

No simpler process substitutes them.

> **Weakness 2:** The organization of this paper is relative poor. The authors move most of the detail about the framework design into the appendix, including most important deisng such as evaluation task composition.

**W2 (Organization).** The layout follows our contributions and scope. The main text presents each contribution: co-evolution formulation (**Sec. 3**), multi-agent system and curriculum policy (**Sec. 4**). **Sec. 5.1** gives the evaluation task composition (four 2D VQA, two report, three 3D); for space, main analyses use one VQA and one report task. The appendix adds what reproduction needs: algorithm (**App. A**), settings (**App. B**), evaluation (**App. C**), and mechanism analyses (**App. D**). Code is in the supplementary material.

> **Weakness 3:** The method demonstrates reactive recovery from selected capability regressions, but does not establish prevention of catastrophic forgetting or stable balanced convergence. Later-round declines, reliance on R7 checkpoint selection, absence of retention ablations, and lack of standard continual-learning metrics leave the central retention claim only partially supported.

**W3 (Catastrophic forgetting and retention).** We respectfully note a misunderstanding: CoEvoMed builds on curriculum learning, not continual learning. Forgetting arises when tasks are learned in sequence and old data is dropped. It trains all tasks every round and replays earlier data (**Eq. 7; Sec. 3.3**), so continual-learning metrics do not apply. "Retention" is a share of the planner's budget (**Sec. 4.2**), ablated with it (**Table 7**).

Later-round declines come from the data, not our mechanisms. The support pool is fixed (359,355 facts, **App. C.3**), and logs show 95% of it is used by R7. After that, few examples contain new evidence (18.0% at R8, 2.2% at R10), so later rounds mostly retrain on seen evidence. Scores peak at R7–R8, just as new evidence runs out; self-training on finite data does the same (Chen et al., 2024; Singh et al., 2024). At R10, **Fig. 7** benchmarks remain within 3 points of their peaks and over 12 above R1.

We chose R7 by a predefined criterion: the most balanced capability profile on internal validation (**App. C.4**). R7 is where new evidence runs out, and InternVL3-9B peaks at rounds 4–6 (**App. C.5**). Our results therefore do not rely on the choice of R7.

> **Question 1:** For medVLSynther results, do you use the same base model to replicate their results?

**Q1 (MedVLSynther base model).** **Table 1** uses MedVLSynther's published results on Qwen2.5-VL-7B. We retrained it on our Qwen3-VL-8B base with its released data and GRPO script. CoEvoMed leads on all four:

| Same base: Qwen3-VL-8B | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther recipe | 53.18 | 70.96 | 73.32 | 68.69 |
| CoEvoMed-8B | **67.95** | **82.48** | **91.60** | **69.40** |

> **Question 2:** Would you consider to publicate the data generated in your evolving pipeline?

**Q2 (Data release).** Yes. Upon acceptance, we will release the synthesized data and all principle versions under each source's license.

> **Question 3:** CoEvoMed relies on a hand-designed capability taxonomy to construct validation cells and guide curriculum allocation, but the paper does not justify why these dimensions and categories are necessary. Some datasets, such as SLAKE, already provide question-type annotations that overlap with categories such as organ recognition, abnormality detection, and localization. The authors should report this mapping, validate the generated annotations, and compare the proposed taxonomy against native dataset labels. Otherwise, it remains unclear whether the gains come from meaningful capability diagnosis or an arbitrary relabeling of existing task categories.

**Q3 (Capability taxonomy).** The dimensions are necessary because every mechanism runs on the cells they define (**Table 6**). The profile is measured per cell (**Eq. 1**), the planner allocates budget across cells (**Eq. 7**), each principle serves one cell and is revised when it stops improving (**Sec. 4.3**), and the selector retrieves evidence matching a cell's modality and anatomy (**App. C.3**). With the taxonomy fixed, stale diagnoses lower 11 of 12 scores (**Table 7**), so gains come from diagnosis, not relabeling.

We built our categories on SLAKE's (Liu et al., 2021): physicians annotated them, and SLAKE spans more modalities and body parts than prior datasets. They describe what a question asks, not a dataset, so they fit all tasks: VQA-RAD and M3D-VQA use similar types (Lau et al., 2018; **Fig. 9a**).

On 200 SLAKE questions, our annotations match native labels: capability 97.5% (Cohen's κ = 0.958), modality 100%, body region 96.5%. κ > 0.81 is "almost perfect" agreement (Landis & Koch, 1977).

---

## Response to Reviewer jcb6

*Posted text: 4,330 / 5,000 characters (quotes excluded).*

We thank the reviewer for the positive assessment and the precise suggestions.

> **Weakness:** The ablation study does not sufficiently isolate the contributions of the individual components. Budget-matched comparisons with fixed principles and a fixed curriculum, principle evolution alone, and curriculum adaptation alone would help determine whether the gains come primarily from high-quality synthetic data or the proposed co-evolution mechanism.

**W1 (Isolating the contributions of individual components).** The paper already contains budget-matched ablations of both components. The main text tests them on VQA-RAD and MIMIC-CXR (**Table 2**, **Sec. 5.3**): Panel A for curriculum adaptation, Panel B for principle evolution. For space, **App. D** extends both to all six benchmarks (**Tables 7–8**). All settings below start from the same R5 checkpoint and train one round with the same pipeline and budget. To remove principle evolution, we keep the original principles. To remove curriculum adaptation, we give the curriculum stale R2 or R3 feedback, so it allocates as if fixed at that earlier stage. Change on each benchmark:

| Setting | Principle evolution | Curriculum adaptation | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|---|---|
| Curriculum only | No | Yes | −5.64 | −3.60 | −9.60 | −2.20 | −6.44 | −4.11 |
| Principles only | Yes | No (R2 feedback) | −1.10 | −5.20 | −3.60 | −3.10 | +0.11 | −3.02 |
| Principles only | Yes | No (R3 feedback) | −1.77 | −5.80 | −1.80 | −2.40 | −0.84 | −4.04 |
| CoEvoMed | Yes | Yes | **+2.62** | **+0.69** | **+0.52** | **+1.13** | **+2.77** | **+1.28** |

The table is an ablation of the two adaptive components. Removing principle evolution (first row) or curriculum adaptation (second and third rows) lowers most or all scores, while keeping both (CoEvoMed) improves all six benchmarks.

This also answers whether the gains come from high-quality synthetic data. Every row builds data with the same selector, constructor, and verifier, so every row trains on verified, high-quality synthetic data. If such data alone drove the gains, every row would improve. Only the row with both components does, so the gains come from co-evolution.

For the setting the reviewer lists first, with both principles and curriculum fixed, the first row is an upper bound. That row keeps curriculum adaptation, yet all six scores drop at R5. Fixing the curriculum as well removes this last adaptive part, so it would do no better.

> **Question:** Starting from the same initialization, training on raw data reduces performance on all four VQA benchmarks, with SLAKE accuracy dropping from 64.84% to 38.15%. What causes this substantial degradation? Would cleaning and reconstructing the data using fixed construction principles also yield substantial gains? A budget-matched comparison would help clarify the additional benefit of adaptive principle evolution.

**Q1 (Raw-data degradation; fixed-principle reconstruction).** The raw data teach the wrong task. Most 2D records are figure descriptions (58.3%), and most others are labels or reports (**Fig. 10; App. C.3**). Trained on them without reconstruction (**App. D.3**), the model learns to describe or label images instead of answering questions. The drop is largest on SLAKE (−26.69), whose answers are short and direct. The raw data are also unverified, untargeted, and static. The table lists these four causes and the CoEvoMed component that addresses each:

| Property of the raw sources | Where CoEvoMed handles it |
|---|---|
| Not task-aligned: descriptions, labels, and reports instead of questions | Principles define question intent; the constructor turns evidence into supervision for the target capability (**Sections 3, 4.1**) |
| Not verified: image–text associations are never checked | The verifier checks factual consistency and visual dependence (**Section 4.1**) |
| Not targeted: the mix follows source availability, not the learner's needs | The planner allocates a fixed budget to weak and regressing capabilities (**Section 4.2**) |
| Not adaptive: supervision stays fixed while the learner changes | The revision agent updates principles from residual errors (**Section 4.3**) |

Reconstruction with fixed principles cannot keep up with the learner. **Table 8** (**App. D.2**) compares fixed and evolved principles from the same R5 checkpoint under the same budget:

| Condition | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|
| R5 reference | 73.61 | 89.00 | 64.60 | 65.80 | 59.00 | 61.63 |
| C: R5 / original | 67.97 (−5.64) | 85.40 (−3.60) | 55.00 (−9.60) | 63.60 (−2.20) | 52.56 (−6.44) | 57.52 (−4.11) |
| D: R5 / evolved (CoEvoMed) | **76.23 (+2.62)** | **89.69 (+0.69)** | **65.12 (+0.52)** | **66.93 (+1.13)** | **61.77 (+2.77)** | **62.91 (+1.28)** |

The fixed principles lower all six benchmarks (C), while the evolved principles raise all six (D). Fixed principles handle the first three properties above but not the fourth. The gap between D and C is the additional benefit of adaptive principle evolution.

---

## Response to Reviewer 2Nuw

*Posted text: 4,994 / 5,000 characters (quotes excluded).*

> **Weakness 1:** **The experimental controls and mechanism analyses do not sufficiently establish the contribution of co-evolution.** The method combines teacher-generated supervision, data verification, principle revision, and adaptive curricula, but does not adequately isolate their effects or those of additional resources. Improvements are difficult to attribute to individual principles, and the relationship between principle-selection criteria and subsequent learning gains remains unvalidated. The substantial degradation of the raw-data training baseline also lacks sufficient explanation.

> **Question 1:** Under the same teachers, data sources, and comparable budgets, could you separately establish the contributions of principle evolution and adaptive curricula, including PPO’s advantage over simpler allocation strategies? Could you also explain the raw-data baseline’s degradation and validate the relationship between principle-selection criteria and subsequent learning gains?

**Q1 & W1 (Contributions, PPO, raw data, selection criteria).** The paper already ablates both components with the same teachers, data sources, budget, and R5 checkpoint (**Table 2, Sec. 5.3; App. D**). Stale R2 or R3 feedback reproduces a curriculum fixed at an earlier stage. Change on each benchmark (**Tables 7–8**):

| Setting | Principle evolution | Adaptive curriculum | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|---|---|
| Curriculum only | No (original) | Yes | −5.64 | −3.60 | −9.60 | −2.20 | −6.44 | −4.11 |
| Principles only | Yes | No (stale R2) | −1.10 | −5.20 | −3.60 | −3.10 | +0.11 | −3.02 |
| Principles only | Yes | No (stale R3) | −1.77 | −5.80 | −1.80 | −2.40 | −0.84 | −4.04 |
| CoEvoMed | Yes | Yes | **+2.62** | **+0.69** | **+0.52** | **+1.13** | **+2.77** | **+1.28** |

Removing either component lowers most or all scores; only both improve all six benchmarks.

Unlike a greedy rule, PPO optimizes cumulative gain (**Eq. 5**), and its choices follow the learner's state. Across R1–R7: balanced, weakness-focused, retention-heavy, balanced, repair-heavy, repair-heavy, balanced. After localization regressed at R4 (60.27 → 56.16), it switched to repair-heavy for R5 and R6, and localization recovered to 59.36 and 62.10 (**Fig. 6**). It then returned to balanced.

The raw-data baseline degrades because its sources (**App. D.3**) are not task-aligned (58.3% of 2D records are figure descriptions; **Fig. 10**), not verified, not targeted, and not adapted. CoEvoMed's agents handle each. CoEvoMed instead reaches 91.60 on SLAKE (**Table 9**).

Principles chosen by our criteria do produce later learning gains. In **Table 8**, from the same R5 checkpoint and budget, the chosen principles raise all six benchmarks, while the original, never-revised principles lower all six. This follows from how the criteria work (**Sec. 4.3; App. B**). A principle is replaced only when the validation cases it fixes no longer outnumber those it breaks, that is, when it stops helping the learner. A replacement is chosen only if a review confirms it targets the errors the learner still makes.

> **Question 2:** How are patient-, study-, and image-level overlaps excluded across support data, internal validation sets, and external tests, particularly between PubMedVision-IU and IU-Xray? Was R7 selected exclusively using a predefined internal validation criterion?

**Q2 (Overlaps; R7).** We excluded patient-, study-, and image-level overlaps by design: support, validation, and test data are separate partitions (**Sec. 1; App. C.6**), enforced in our code. We screened all 11 2D and 5 3D sources against every external test at four levels: IDs (including study and case IDs), image paths, pixel hashes (exact and near-duplicate), and normalized text. All checks found zero overlap, including PubMedVision-IU vs. IU-Xray.

R7 was selected by a predefined internal criterion: it has the most balanced capability profile on the internal validation sets (**App. C.4**). External benchmark scores never feed back into training or checkpoint selection (**App. A, C.6**).

> **Weakness 2:** **Evaluation coverage and statistical reliability remain limited.** The 2D VQA evaluation lacks expert-level, complex medical reasoning tasks, and independent repeated runs or confidence intervals are not clearly reported. On IU-Xray, the 8B model improves over the strongest baseline by only 0.92 RaTEScore points, while the 32B model performs worse than the 8B model. The stability of the gains and benefits of scaling therefore remain unclear.

> **Question 3:** How many independent runs underlie the main results, and could you provide standard deviations and paired confidence intervals? Additionally, why is CURE-4B absent from the IU-Xray comparison, and why does the 32B model underperform the 8B model on this dataset?

**Q3 & W2 (Runs and intervals; CURE-4B; 32B on IU-Xray).** We ran the full pipeline independently on four learners across three model families, architectures, and scales: Qwen3-VL (8B and 32B), Gemma 3 (4B), and InternVL3 (9B). Every run improves over its own base on every benchmark evaluated (16 of 16, +6.52 to +26.76). An effect that holds across families, architectures, and scales is not a single-run artifact.

We considered CURE-4B, but IU-Xray is not a fair test for it. CURE is fine-tuned on MIMIC-CXR-derived data (Chest ImaGenome, MS-CXR) and PadChest-GR, and IU-Xray is outside its training and evaluation data. A zero-shot run confirms the domain shift: it scores 28.65 RaTEScore, below all 28 models in **Fig. 3**.

The reversal is a property of IU-Xray: Hulu-Med (7B 67.30 vs. 32B 62.40) and MedGemma (4B 60.50 vs. 27B 59.00) show it too. IU-Xray references are short (30.5 words on average, versus 53.4 for MIMIC-CXR). CoEvoMed-8B matches this length (30.7 words), while 32B writes more detailed reports (40.1 words) that match the short references less well. On MIMIC-CXR, whose reports are longer, 32B does beat 8B (64.33 vs. 63.62; **Fig. 3**).

> **Weakness 2 (excerpt):** The 2D VQA evaluation lacks expert-level, complex medical reasoning tasks.

> **Question 4:** Why were complex reasoning benchmarks such as MedXpertQA-MM or the Health & Medicine portion of MMMU not included? How do the existing results support generalization to complex medical reasoning?

**Q4 & W2 (Complex reasoning).** We chose benchmarks that test medical reasoning in clinical form, which is harder than multiple choice on 2D images:

| What the model must do | Benchmarks |
|---|---|
| Write full reports | MIMIC-CXR, IU-Xray (chest X-ray); AMOS-MM (multi-organ 3D CT) |
| Reason over 3D volumes | M3D-VQA (five question types over 64 slices); 3D-RAD (open-ended, including measuring diameter, size, and thickness) |
| Answer varied 2D questions | VQA-RAD (clinician-authored), SLAKE (knowledge-based), PathVQA (pathology), PMC-VQA (literature figures) |

MedXpertQA-MM and MMMU test reasoning through multiple choice on 2D images (all of MedXpertQA-MM, 94% of MMMU). Our suite already covers this format (PMC-VQA, M3D-VQA) and adds the harder tasks above.

The results support generalization: CoEvoMed ranks first on all nine benchmarks (**Table 1; Figs. 3–4**). On 3D-RAD Medical Computation, it leads the next-best model by +8.6 BLEU-1 (**Fig. 9b**).
