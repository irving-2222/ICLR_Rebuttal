# Rebuttal Responses — Submission 37342 (CoEvoMed)

---

## Response to Reviewer pUjh

**W1 (Is the multi-agent framework necessary?)** Yes. App. D tests each agent role's critical function from the same checkpoint, with and without it:

| Agent role | Critical function | Without it | With it |
|---|---|---|---|
| Selector, constructor, verifier | Verified, task-aligned data | Raw data (~700K): 4/4 VQA below base; SLAKE 38.15 | Fewer examples: 4/4 improve; SLAKE **91.60** (Tab. 9) |
| Revision agent | Adapt principles to learner | Original principles at R5: 6/6 decline | Revised: **6/6 improve** (Tab. 8) |
| Curriculum planner | Allocate budget to current needs | Stale R2/R3 feedback: 11/12 decline | Current: **6/6 improve** (Tab. 7) |

Can another plausible agent process substitute them? It must still perform these functions; the simpler alternatives above all fail. Why not merge the roles into one agent?
1. **Independent checking.** The verifier (Qwen3.6-27B) and the constructor (deepseek-v4-flash) are different models, so no model checks its own output. LLMs struggle to self-correct without external feedback (Huang et al., ICLR 2024).
2. **Grounded construction.** The constructor writes only from selected source facts, not the image. A merged agent would write from the image, where VLMs often describe absent objects (Li et al., EMNLP 2023).
3. **Learned allocation.** The planner is a small policy network trained by PPO each round, while the LLM agents stay frozen (App. B); merging would lose this learning.

**W2 (Organization).** The main text specifies every mechanism (Secs. 3–4, Eqs. 1–9), and Sec. 5.1 gives the evaluation task composition. Implementation parameters and dataset statistics are in the appendix, each referenced from the main text.

**W3 (Catastrophic forgetting and retention).** CoEvoMed is curriculum learning, not continual learning. Every round trains all tasks together (Eq. 7) with replay data (Sec. 3.3), so catastrophic forgetting and continual-learning metrics do not apply. "Retention" is a budget share (Sec. 4.2), ablated with the planner in W1. The two remaining points concern data and checkpoint choice, not the method:
- *Later-round declines come from the data.* The support pool is fixed (359,355 facts, App. C.3); each round builds 50,000 examples (App. B). By R7 the budget nearly matches the pool, so later rounds mostly reuse seen evidence. Self-training on finite data shows the same pattern (Chen et al., ICML 2024; Singh et al., TMLR 2024). While new evidence lasts, CoEvoMed keeps improving to peaks at R7–R8. Even at R10, all three benchmarks stay within 3 points of their peaks and over 12 points above R1 (Fig. 7). A larger pool can extend the evolution without changing the method.
- *Reliance on R7.* R7 has the most balanced capability profile on internal validation sets. One checkpoint serves all six benchmarks, though PathVQA peaks at R8. External benchmarks only track the evolution and never guide training or selection (App. C.4, C.6).

**Q1 (MedVLSynther base model).** We were aware of the base difference. Absolute scores mix method and backbone, so we compare gains over each method's own base (MedVLSynther as published):

| Gain over own base | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther-7B (Qwen2.5-VL-7B) | +6.13 | +8.82 | +6.65 | +0.17 |
| CoEvoMed-8B (Qwen3-VL-8B) | **+13.82** | **+25.72** | **+26.76** | **+26.63** |

On the same base, we trained Qwen3-VL-8B with MedVLSynther's released data and GRPO script:

| Same base: Qwen3-VL-8B | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther recipe | [x.xx] | [x.xx] | [x.xx] | [x.xx] |
| CoEvoMed-8B | 67.95 | 82.48 | 91.60 | 69.40 |

**Q2 (Data release).** Yes. Upon acceptance, we will release the synthesized data and all principle versions under each source's license: images are referenced by ID, and sources forbidding redistribution (e.g., CheXpert) get regeneration scripts.

**Q3 (Capability taxonomy).** The overlap with SLAKE is by design, not an arbitrary relabeling.
- *Why these categories.* The taxonomy follows SLAKE's physician-annotated question categories (Liu et al., 2021). We merge its attribute types and add spatial relations, comparison, and holistic description for multi-image and report tasks (Table 6).
- *Why they are necessary.* The categories describe what a question asks, not a dataset, so they also cover PathVQA, PMC-VQA, reports, and the support pool, which lack native labels. One taxonomy lets us diagnose all tasks, share one budget, and retrieve matching evidence (App. C.3).
- *Mapping and validation.* On 200 SLAKE questions, our annotations match the native labels for capability at 97.5% (Cohen's κ = 0.958), modality at 100%, and body region at 96.5%. κ above 0.81 is "almost perfect" agreement (Landis & Koch, 1977). We will add the mapping to Table 6.

---

## Response to Reviewer jcb6

We thank the reviewer for the positive assessment and the precise suggestions.

**W1 (Isolating the contributions of individual components).** The component controls in App. D give the budget-matched comparisons the reviewer suggests. All conditions start from the same R5 checkpoint and train one round with the same pipeline and budget. Only the principles and the curriculum feedback differ (Tables 7–8; mean change over six benchmarks):

| Requested comparison | Principles | Curriculum | Mean Δ | Improved |
|---|---|---|---|---|
| Principle evolution alone | evolved | stale (R2 / R3) feedback | −2.65 / −2.78 | 1/6 / 0/6 |
| Curriculum adaptation alone | fixed (original) | current feedback | −5.27 | 0/6 |
| Co-evolution (CoEvoMed) | evolved | current feedback | **+1.50** | **6/6** |

*Fixed principles and a fixed curriculum.* Fixed principles already fail at R5 while the curriculum still adapts (−5.27, 0/6). Fixing the curriculum as well removes the only remaining adaptation, so it cannot be expected to do better.

*High-quality synthetic data or co-evolution?* Each component alone degrades the learner; only co-evolution improves all six benchmarks. The same verified pipeline with fixed principles helps at R2 (+3.09, 6/6) but harms at R5. High-quality synthetic data thus drives early progress, while co-evolution sustains it. At matched budget, evolved principles add +6.77 over fixed ones, and current feedback adds +4.15 to +4.28 over stale feedback.

**Q1 (Raw-data degradation; fixed-principle reconstruction).**

*What causes this substantial degradation?* App. D.3 trains on the raw sources "without supervision reconstruction or adaptive curriculum allocation". Four properties of these sources explain the drop. The right column shows where CoEvoMed handles each:

| Property of the raw sources | Where CoEvoMed handles it |
|---|---|
| Not task-aligned: 58.3% of 2D records are figure descriptions, most others label-derived items or reports (Figure 10, App. C.3), so the model learns to describe or label rather than answer | Principles define question intent; the constructor turns evidence into supervision for the target capability (Sections 3, 4.1) |
| Not verified: image–text associations are never checked | The verifier checks factual consistency and visual dependence (Section 4.1) |
| Not targeted: the mix follows source availability, not the learner's needs | The planner allocates a fixed budget to weak and regressing capabilities (Section 4.2) |
| Not adaptive: supervision stays fixed while the learner changes | The revision agent updates principles from residual errors (Section 4.3) |

As a result, ~700K raw examples fall below the base model. The largest drop is on SLAKE (−26.69), whose answers are short. The same kinds of sources, routed through CoEvoMed, reach 91.60 with fewer examples.

*Would cleaning and reconstructing the data with fixed construction principles also yield substantial gains?* Yes at first, but not later. Fixed principles handle the first three rows of the table, but not the fourth. At R2, reconstruction with the original principles improves all six benchmarks (+1.78 to +3.90; Table 8). This is why CoEvoMed starts from these principles (Algorithm 1). At R5, the same fixed principles lower all six benchmarks (−2.2 to −9.6).

*Additional benefit of adaptive principle evolution (budget-matched).* At R5 and under the same budget, evolved principles outperform fixed ones on all six benchmarks, by +6.77 on average (+3.33 to +10.12; Table 8). This margin is the benefit of principle evolution.

---

## Response to Reviewer 2Nuw

**Q1 & W1 (Contributions, PPO, raw data, selection criteria).**
*Principle evolution vs. adaptive curricula.* Same teachers, data sources, budget, and R5 checkpoint (Tables 7–8; mean change over six benchmarks):

| Condition | Principles | Curriculum | Mean Δ | Improved |
|---|---|---|---|---|
| Principle evolution alone | evolved | stale feedback | −2.65 / −2.78 | 1/6 / 0/6 |
| Adaptive curriculum alone | fixed | current feedback | −5.27 | 0/6 |
| Both (CoEvoMed) | evolved | current feedback | **+1.50** | **6/6** |

*PPO vs. simpler allocation.* The planner optimizes cumulative gain (Eq. 5), not a greedy rule. Its choices follow the learner's state: across R1–R7 it chose [action sequence]. After localization regressed at R4, it switched to [action] at R[x], and localization then recovered (Fig. 6).
*Raw-data degradation.* The raw sources (App. D.3) are not task-aligned (58.3% of 2D records are figure descriptions; Fig. 10), not verified, not targeted, and not adapted. CoEvoMed handles these with the constructor, verifier, planner, and revision agent. With CoEvoMed, SLAKE reaches 91.60 instead of 38.15 (Table 9).
*Selection criteria vs. learning gains.* The criteria screen supervision quality before use. The loop then checks learning gains: principles whose net repair stays non-positive are revised again (Sec. 4.3). The selected principles raise all six benchmarks at R5, where the originals lower all six (+6.77 on average; Table 8).

**Q2 (Overlaps; R7).**
*Patient-, study-, and image-level overlaps.* We treated leakage as a design constraint: support, validation, and test data are separate partitions (Sec. 1; App. C.6), enforced by our code (coevomed/data.py). We screened all 11 2D and 5 3D sources against every external test at four levels: IDs (including study and case IDs), image paths, pixel hashes (exact and near-duplicate), and normalized text. All checks found zero overlap, including PubMedVision-IU vs. IU-Xray; PMC-OA and PMC-VQA also draw on disjoint PMC articles.
*Was R7 selected by a predefined internal criterion?* Yes. R7 has the most balanced capability profile on the internal validation sets (App. C.4), as defined in Sec. 3.1 (Eq. 1), and one checkpoint serves all six benchmarks. We test every round on the external benchmarks only to show how evolution improves the learner, and report all ten rounds, including declines (Fig. 7). These scores never feed back into training or checkpoint selection (App. A, C.6).

**Q3 & W2 (Runs and intervals; CURE-4B; 32B on IU-Xray).**
*Independent runs and intervals.* We ran the full pipeline independently on four learners from three model families, with different architectures and scales: Qwen3-VL (8B and 32B), Gemma 3 (4B), and InternVL3 (9B). Every run improves over its own base on every benchmark evaluated: 16 of 16 comparisons, by +6.52 to +26.76. These gains far exceed the test-set uncertainty (95% CI ±0.5 on PMC-VQA, ±1.7 on SLAKE). An effect that holds across families, architectures, and scales is not a single-run artifact.
*Why is CURE-4B absent from IU-Xray?* We considered it, but IU-Xray is not a fair test for CURE. CURE is fine-tuned on MIMIC-CXR-derived data (Chest ImaGenome, MS-CXR) and PadChest-GR, and IU-Xray is outside its training and evaluation data. A zero-shot run confirms the domain shift: it scores 28.65 RaTEScore, below all 28 models in Fig. 3, with very short outputs.
*Why does 32B underperform 8B on IU-Xray?* This is common on IU-Xray: Hulu-Med (7B 67.30 vs. 32B 62.40) and MedGemma (4B 60.50 vs. 27B 59.00) show it too. At matched scale, CoEvoMed-32B beats Hulu-Med-32B by +2.68, and it beats CoEvoMed-8B on the other five benchmarks. Beyond the 0.92 RaTEScore margin, CoEvoMed-8B leads Hulu-Med-7B on six of eight lexical metrics (up to +7.5 ROUGE-2; Fig. 8).

**Q4 & W2 (Complex reasoning).** We chose our benchmarks to test medical reasoning in its clinical form: image-grounded, often volumetric, and mostly open-ended. They require full reports from chest X-rays (MIMIC-CXR, IU-Xray) and multi-organ 3D CT (AMOS-MM); plane, phase, organ, abnormality, and location questions across 64-slice volumes (M3D-VQA); diameter, size, and thickness measurement in open-ended 3D questions (3D-RAD); and clinician-authored, knowledge-based, pathology, and literature-figure questions (VQA-RAD, SLAKE, PathVQA, PMC-VQA).
*Why not MedXpertQA-MM or MMMU?* Both test reasoning through multiple choice on 2D images (all of MedXpertQA-MM, 94% of MMMU). Our suite already covers this format (PMC-VQA, M3D-VQA) and goes further: the model must write reports, answer without options, reason across 3D volumes, and measure structures.
*Generalization.* CoEvoMed ranks first on all nine benchmarks (Table 1; Figs. 3–4). On 3D-RAD Medical Computation, it leads the next-best model by +8.6 BLEU-1 (Fig. 9b).
