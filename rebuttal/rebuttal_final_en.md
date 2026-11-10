# Rebuttal Responses — Submission 37342 (CoEvoMed)

Reviewer comments are quoted (>) for reference only and are not part of the posted text. Post only the response text. Each reviewer's response goes in one Official Comment of at most 5,000 characters.

---

## Response to Reviewer pUjh

*Posted text: 4,983 / 5,000 characters (quotes excluded).*

> **Weakness 1:** To me, the multi-agent framework seems unecessary. The experiments do not validate all critical function of each "agent role". Do we reall y need all of these agents or can we easily find another plausible agent process to substitude them.

**W1 (Necessity of the multi-agent framework).**
- **App. D** shows that the agents are needed (**Tables 7–9**). Changes from a shared start, all else fixed:

| Without | From | VQA-RAD | SLAKE | PMC-VQA | PathVQA |
|---|---|---|---|---|---|
| All agents: raw data | base | −13.75 | −26.69 | −8.62 | −6.83 |
| Revision agent: original principles | R5 | −5.64 | −3.60 | −9.60 | −2.20 |
| Curriculum planner: R2 feedback | R5 | −1.10 | −5.20 | −3.60 | −3.10 |
| Curriculum planner: R3 feedback | R5 | −1.77 | −5.80 | −1.80 | −2.40 |
| None: CoEvoMed | base | **+25.72** | **+26.76** | **+13.82** | **+26.63** |
| None: CoEvoMed | R5 | **+2.62** | **+0.69** | **+0.52** | **+1.13** |

- No simpler process can substitute them: each one above lowers every score; only the full one improves all. We also separate the roles by design (**App. B**):
    1. **Independent checking.** LLMs rarely self-correct without external feedback (Huang et al., ICLR 2024). We therefore designed the verifier (Qwen3.6-27B) and constructor (deepseek-v4-flash) as different models.
    2. **Grounded construction.** If the constructor wrote from the image, it could describe absent objects, as VLMs often do (Li et al., EMNLP 2023). We therefore let it write only from selected facts; the verifier checks the image.
    3. **Curriculum allocation.** If an LLM agent also set the budget, it could not learn, since LLM weights stay frozen. Curricula learned from learning progress match or beat hand-crafted ones (Matiisen et al., 2017). We therefore made the curriculum planner a separate policy network trained by PPO on validation gains (Sec. 4.2).

> **Weakness 2:** The organization of this paper is relative poor. The authors move most of the detail about the framework design into the appendix, including most important deisng such as evaluation task composition.

**W2 (Organization).** The main text follows the method's logic: problem (Sec. 3), mechanisms (Sec. 4, Eqs. 1–9), and evidence, including the evaluation task composition (Sec. 5.1). Each appendix part extends a main-text part that cites it; together they suffice for reproduction: full algorithm (**App. A**), models and hyperparameters (**App. B**), data sources, links, and metrics (**App. C**), and component controls (**App. D**).

> **Weakness 3:** The method demonstrates reactive recovery from selected capability regressions, but does not establish prevention of catastrophic forgetting or stable balanced convergence. Later-round declines, reliance on R7 checkpoint selection, absence of retention ablations, and lack of standard continual-learning metrics leave the central retention claim only partially supported.

**W3 (Catastrophic forgetting and retention).** CoEvoMed builds on curriculum learning, not continual learning. Every round trains all tasks together with replay data (Eq. 7; Sec. 3.3), so catastrophic forgetting and continual-learning metrics do not apply. "Retention" is a share of the curriculum planner's budget (Sec. 4.2) and is ablated with it (Table 7). We explain the other two points below:
- Later-round declines come from the data. The support pool is fixed (359,355 facts, App. C.3); each round builds 50,000 examples (App. B). By R7 the budget nearly matches the pool, so later rounds mostly reuse seen evidence. Self-training on finite data shows the same pattern (Chen et al., ICML 2024; Singh et al., TMLR 2024). While new evidence lasts, CoEvoMed improves up to R7–R8. At R10, all three Fig. 7 benchmarks stay within 3 points of their peaks and over 12 above R1. A larger pool extends the gains without changing the method.
- R7 has the most balanced capability profile on internal validation sets, though PathVQA peaks at R8. External benchmarks only track evolution, never training or selection (App. C.4, C.6).

> **Question 1:** For medVLSynther results, do you use the same base model to replicate their results?

**Q1 (MedVLSynther base model).** Absolute scores mix method and backbone, so we compare gains over each method's own base (MedVLSynther as published):

| Gain over own base | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther-7B (Qwen2.5-VL-7B) | +6.13 | +8.82 | +6.65 | +0.17 |
| CoEvoMed-8B (Qwen3-VL-8B) | **+13.82** | **+25.72** | **+26.76** | **+26.63** |

Same base, with MedVLSynther's released data and GRPO script:

| Same base: Qwen3-VL-8B | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther recipe | [x.xx] | [x.xx] | [x.xx] | [x.xx] |
| CoEvoMed-8B | 67.95 | 82.48 | 91.60 | 69.40 |

> **Question 2:** Would you consider to publicate the data generated in your evolving pipeline?

**Q2 (Data release).** Yes. Upon acceptance, we will release the synthesized data and all principle versions under each source's license (images by ID; regeneration scripts for non-redistributable sources, e.g., CheXpert).

> **Question 3:** CoEvoMed relies on a hand-designed capability taxonomy to construct validation cells and guide curriculum allocation, but the paper does not justify why these dimensions and categories are necessary. Some datasets, such as SLAKE, already provide question-type annotations that overlap with categories such as organ recognition, abnormality detection, and localization. The authors should report this mapping, validate the generated annotations, and compare the proposed taxonomy against native dataset labels. Otherwise, it remains unclear whether the gains come from meaningful capability diagnosis or an arbitrary relabeling of existing task categories.

**Q3 (Capability taxonomy).** The taxonomy is not a claimed contribution but the unit of validation feedback (App. C.3).
- We adopted SLAKE's physician-annotated question categories (Liu et al., 2021), so the overlap is by design. We merge its attribute types and add three for multi-image and report tasks.
- The categories are necessary: they describe what a question asks, not a dataset, so they also cover unlabeled data (PathVQA, PMC-VQA, reports, support pool). One taxonomy lets us diagnose all tasks, share one budget, and retrieve evidence.
- On 200 SLAKE questions, our annotations match native labels for capability at 97.5% (Cohen's κ = 0.958), modality at 100%, and body region at 96.5%. κ > 0.81 is "almost perfect" agreement (Landis & Koch, 1977). We will add the mapping to Table 6.
- Gains come from diagnosis, not relabeling: with the taxonomy fixed, stale diagnoses lower 11 of 12 scores (Table 7).

---

## Response to Reviewer jcb6

*Posted text: 3,408 / 5,000 characters (quotes excluded).*

We thank the reviewer for the positive assessment and the precise suggestions.

> **Weakness:** The ablation study does not sufficiently isolate the contributions of the individual components. Budget-matched comparisons with fixed principles and a fixed curriculum, principle evolution alone, and curriculum adaptation alone would help determine whether the gains come primarily from high-quality synthetic data or the proposed co-evolution mechanism.

**W1 (Isolating the contributions of individual components).** The component controls in App. D give the budget-matched comparisons the reviewer suggests. All conditions start from the same R5 checkpoint and train one round with the same pipeline and budget. Only the principles and the curriculum feedback differ (Tables 7–8; mean change over six benchmarks):

| Requested comparison | Principles | Curriculum | Mean Δ | Improved |
|---|---|---|---|---|
| Principle evolution alone | evolved | stale (R2 / R3) feedback | −2.65 / −2.78 | 1/6 / 0/6 |
| Curriculum adaptation alone | fixed (original) | current feedback | −5.27 | 0/6 |
| Co-evolution (CoEvoMed) | evolved | current feedback | **+1.50** | **6/6** |

- Fixing both principles and curriculum cannot do better. Fixed principles already fail at R5 while the curriculum still adapts (−5.27, 0/6), and fixing the curriculum removes the only remaining adaptation.
- The gains come from co-evolution. Each component alone degrades the learner; only co-evolution improves all six benchmarks. The same verified pipeline with fixed principles helps at R2 (+3.09, 6/6) but harms at R5. High-quality synthetic data thus drives early progress, while co-evolution sustains it. At matched budget, evolved principles add +6.77 over fixed ones, and current feedback adds +4.15 to +4.28 over stale feedback.

> **Question:** Starting from the same initialization, training on raw data reduces performance on all four VQA benchmarks, with SLAKE accuracy dropping from 64.84% to 38.15%. What causes this substantial degradation? Would cleaning and reconstructing the data using fixed construction principles also yield substantial gains? A budget-matched comparison would help clarify the additional benefit of adaptive principle evolution.

**Q1 (Raw-data degradation; fixed-principle reconstruction).** The raw data lack what CoEvoMed's agents add, and fixed principles help only early.
- Four properties of the raw sources cause the degradation. App. D.3 trains on these sources "without supervision reconstruction or adaptive curriculum allocation". The ~700K raw examples fall below the base model, most on SLAKE (−26.69), whose answers are short. Routed through CoEvoMed, the same kinds of sources reach 91.60 with fewer examples. The right column shows where CoEvoMed handles each property:

| Property of the raw sources | Where CoEvoMed handles it |
|---|---|
| Not task-aligned: 58.3% of 2D records are figure descriptions, most others label-derived items or reports (Figure 10, App. C.3), so the model learns to describe or label rather than answer | Principles define question intent; the constructor turns evidence into supervision for the target capability (Sections 3, 4.1) |
| Not verified: image–text associations are never checked | The verifier checks factual consistency and visual dependence (Section 4.1) |
| Not targeted: the mix follows source availability, not the learner's needs | The planner allocates a fixed budget to weak and regressing capabilities (Section 4.2) |
| Not adaptive: supervision stays fixed while the learner changes | The revision agent updates principles from residual errors (Section 4.3) |

- Reconstruction with fixed principles yields gains at first, but not later. Fixed principles handle the first three rows of the table, but not the fourth. At R2, reconstruction with the original principles improves all six benchmarks (+1.78 to +3.90; Table 8). This is why CoEvoMed starts from these principles (Algorithm 1). At R5, the same fixed principles lower all six benchmarks (−2.2 to −9.6).
- Adaptive principle evolution adds +6.77 on average under a matched budget. At R5, evolved principles outperform fixed ones on all six benchmarks (+3.33 to +10.12; Table 8).

---

## Response to Reviewer 2Nuw

*Posted text: 4,863 / 5,000 characters (quotes excluded).*

> **Weakness 1:** **The experimental controls and mechanism analyses do not sufficiently establish the contribution of co-evolution.** The method combines teacher-generated supervision, data verification, principle revision, and adaptive curricula, but does not adequately isolate their effects or those of additional resources. Improvements are difficult to attribute to individual principles, and the relationship between principle-selection criteria and subsequent learning gains remains unvalidated. The substantial degradation of the raw-data training baseline also lacks sufficient explanation.

> **Question 1:** Under the same teachers, data sources, and comparable budgets, could you separately establish the contributions of principle evolution and adaptive curricula, including PPO’s advantage over simpler allocation strategies? Could you also explain the raw-data baseline’s degradation and validate the relationship between principle-selection criteria and subsequent learning gains?

**Q1 & W1 (Contributions, PPO, raw data, selection criteria).** Each part is tested in App. D.
- Neither principle evolution nor adaptive curricula helps alone; only both together improve all six benchmarks. Same teachers, data sources, budget, and R5 checkpoint (Tables 7–8; mean change):

| Condition | Principles | Curriculum | Mean Δ | Improved |
|---|---|---|---|---|
| Principle evolution alone | evolved | stale feedback | −2.65 / −2.78 | 1/6 / 0/6 |
| Adaptive curriculum alone | fixed | current feedback | −5.27 | 0/6 |
| Both (CoEvoMed) | evolved | current feedback | **+1.50** | **6/6** |

- Unlike a greedy rule, the PPO planner optimizes cumulative gain (Eq. 5), and its choices follow the learner's state. Across R1–R7: balanced, weakness-focused, retention-heavy, balanced, repair-heavy, repair-heavy, balanced. After localization regressed at R4 (60.27 → 56.16), it switched to repair-heavy for R5 and R6, and localization recovered to 59.36 and 62.10 (Fig. 6). With localization above R1, it returned to balanced at R7.
- The raw-data baseline degrades because its sources (App. D.3) are not task-aligned (58.3% of 2D records are figure descriptions; Fig. 10), not verified, not targeted, and not adapted. CoEvoMed's constructor, verifier, planner, and revision agent handle these. With CoEvoMed, SLAKE reaches 91.60 instead of 38.15 (Table 9).
- The selection criteria screen supervision quality before use; the loop then checks learning gains: principles whose net repair stays non-positive are revised again (Sec. 4.3). The selected principles raise all six benchmarks at R5, where the originals lower all six (+6.77 mean; Table 8).

> **Question 2:** How are patient-, study-, and image-level overlaps excluded across support data, internal validation sets, and external tests, particularly between PubMedVision-IU and IU-Xray? Was R7 selected exclusively using a predefined internal validation criterion?

**Q2 (Overlaps; R7).**
- We excluded patient-, study-, and image-level overlaps by design: support, validation, and test data are separate partitions (Sec. 1; App. C.6), enforced in our code. We screened all 11 2D and 5 3D sources against every external test at four levels: IDs (including study and case IDs), image paths, pixel hashes (exact and near-duplicate), and normalized text. All checks found zero overlap, including PubMedVision-IU vs. IU-Xray; PMC-OA and PMC-VQA also draw on disjoint PMC articles.
- R7 was selected by a predefined internal criterion: it has the most balanced capability profile on the internal validation sets (Sec. 3.1, Eq. 1; App. C.4), and one checkpoint serves all six benchmarks. We test every round on external benchmarks only to show how evolution improves the learner, and report all ten rounds, including declines (Fig. 7). These scores never feed back into training or checkpoint selection (App. A, C.6).

> **Weakness 2:** **Evaluation coverage and statistical reliability remain limited.** The 2D VQA evaluation lacks expert-level, complex medical reasoning tasks, and independent repeated runs or confidence intervals are not clearly reported. On IU-Xray, the 8B model improves over the strongest baseline by only 0.92 RaTEScore points, while the 32B model performs worse than the 8B model. The stability of the gains and benefits of scaling therefore remain unclear.

> **Question 3:** How many independent runs underlie the main results, and could you provide standard deviations and paired confidence intervals? Additionally, why is CURE-4B absent from the IU-Xray comparison, and why does the 32B model underperform the 8B model on this dataset?

**Q3 & W2 (Runs and intervals; CURE-4B; 32B on IU-Xray).**
- We ran the full pipeline independently on four learners from three model families, with different architectures and scales: Qwen3-VL (8B and 32B), Gemma 3 (4B), and InternVL3 (9B). Every run improves over its own base on every benchmark evaluated (16 of 16, +6.52 to +26.76). These gains far exceed the test-set uncertainty (95% CI ±0.5 on PMC-VQA, ±1.7 on SLAKE). An effect that holds across families, architectures, and scales is not a single-run artifact.
- We considered CURE-4B, but IU-Xray is not a fair test for it. CURE is fine-tuned on MIMIC-CXR-derived data (Chest ImaGenome, MS-CXR) and PadChest-GR, and IU-Xray is outside its training and evaluation data. A zero-shot run confirms the domain shift: it scores 28.65 RaTEScore, below all 28 models in Fig. 3, with very short outputs.
- Larger models often trail smaller ones on IU-Xray: Hulu-Med (7B 67.30 vs. 32B 62.40) and MedGemma (4B 60.50 vs. 27B 59.00) do too. At matched scale, CoEvoMed-32B beats Hulu-Med-32B by +2.68, and it beats CoEvoMed-8B on the other five benchmarks. Beyond the 0.92 RaTEScore margin, CoEvoMed-8B leads Hulu-Med-7B on six of eight lexical metrics (up to +7.5 ROUGE-2; Fig. 8).

> **Weakness 2 (excerpt):** The 2D VQA evaluation lacks expert-level, complex medical reasoning tasks.

> **Question 4:** Why were complex reasoning benchmarks such as MedXpertQA-MM or the Health & Medicine portion of MMMU not included? How do the existing results support generalization to complex medical reasoning?

**Q4 & W2 (Complex reasoning).** We chose our benchmarks to test medical reasoning in its clinical form: image-grounded, often volumetric, and mostly open-ended. They require full reports from chest X-rays (MIMIC-CXR, IU-Xray) and multi-organ 3D CT (AMOS-MM); plane, phase, organ, abnormality, and location questions across 64-slice volumes (M3D-VQA); diameter, size, and thickness measurement in open-ended 3D questions (3D-RAD); and clinician-authored, knowledge-based, pathology, and literature-figure questions (VQA-RAD, SLAKE, PathVQA, PMC-VQA).
- MedXpertQA-MM and MMMU test reasoning through multiple choice on 2D images (all of MedXpertQA-MM, 94% of MMMU). Our suite already covers this format (PMC-VQA, M3D-VQA) and goes further: the model must write reports, answer without options, reason across 3D volumes, and measure structures.
- The results support generalization: CoEvoMed ranks first on all nine benchmarks (Table 1; Figs. 3–4). On 3D-RAD Medical Computation, it leads the next-best model by +8.6 BLEU-1 (Fig. 9b).
