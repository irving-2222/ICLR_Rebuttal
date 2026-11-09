# Rebuttal Responses — Submission 37342 (CoEvoMed)

---

## Response to Reviewer pUjh

**W1 (Is the multi-agent framework necessary?)** Yes. App. D validates the critical function of each agent role, from the same checkpoint with and without it:

| Agent role | Critical function | Without it | With it |
|---|---|---|---|
| Selector, constructor, verifier | Verified, task-aligned supervision | Raw data (~700K): 4/4 VQA below base; SLAKE 38.15 | Fewer examples: 4/4 improve; SLAKE **91.60** (Tab. 9) |
| Revision agent | Adapt principles to the learner | Original principles at R5: 6/6 decline (−2.2 to −9.6) | Revised: **6/6 improve** (+0.5 to +2.8) (Tab. 8) |
| Curriculum planner | Allocate budget to current needs | Stale R2/R3 feedback: 11/12 decline | Current: **6/6 improve** (Tab. 7) |

Can another plausible agent process substitute them? It must still perform these functions; the simpler alternatives above all fail. Why not merge the roles into one agent?
1. **Independent checking.** The verifier (Qwen3.6-27B) is a different model from the constructor (deepseek-v4-flash), so no model checks its own output. LLMs struggle to correct their own outputs without external feedback (Huang et al., ICLR 2024).
2. **Grounded construction.** The constructor writes only from selected source facts and does not read the image. A merged agent would write from the image, where vision–language models often describe absent objects (Li et al., EMNLP 2023).
3. **Learned allocation.** The planner is a small policy network trained with PPO every round, while the LLM agents stay frozen (App. B). Merging it into an LLM would lose this learning.

**W2 (Organization).** The main text specifies every mechanism (Secs. 3–4, Eqs. 1–9), including the capability cells (Sec. 3.1), and Sec. 5.1 gives the evaluation task composition (four 2D VQA, two report, three 3D benchmarks). Implementation parameters and dataset statistics are in the appendix, each referenced from the main text.

**W3 (Catastrophic forgetting and the retention claim).** CoEvoMed is curriculum learning, not continual learning. Every round trains all tasks together (Eq. 7) with replay data (Sec. 3.3) and evaluates every task. With no task sequence, catastrophic forgetting and continual-learning metrics do not apply, and the paper makes no forgetting claim. "Retention" is the part of the budget that keeps training acquired capabilities (Sec. 4.2); W1 tests it as part of the planner.
- *Reactive recovery and balance.* This is the intended closed loop, which measures and penalizes regressions every round (Eqs. 6, 8). From R1 to R6, all five capabilities in Fig. 6 end above R1.
- *Later-round declines.* At R10, SLAKE, PathVQA, and IU-Xray stay within 3 points of their peaks and +21.5, +26.9, and +12.8 above R1 (Fig. 7).
- *Reliance on R7.* R7 was chosen once, for cross-task balance, for all six benchmarks (Sec. 5.2). Even the final R10 beats Hulu-Med-7B on SLAKE (88.67 vs. 86.80) and PathVQA (67.25 vs. 65.60).

**Q1 (MedVLSynther base model).** We were aware of the base difference. Absolute scores mix method and backbone, so we compare gains over each method's own base (MedVLSynther as published):

| Gain over own base | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther-7B (Qwen2.5-VL-7B) | +6.13 | +8.82 | +6.65 | +0.17 |
| CoEvoMed-8B (Qwen3-VL-8B) | **+13.82** | **+25.72** | **+26.76** | **+26.63** |

On the same base, we also trained Qwen3-VL-8B with MedVLSynther's released data and GRPO script:

| Same base: Qwen3-VL-8B | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther recipe | [x.xx] | [x.xx] | [x.xx] | [x.xx] |
| CoEvoMed-8B | 67.95 | 82.48 | 91.60 | 69.40 |

**Q2 (Data release).** Yes. Upon acceptance, we will release the synthesized data and all principle versions under each source's license: images are referenced by identifiers, and sources that forbid redistribution (e.g., CheXpert) get regeneration scripts.

**Q3 (Capability taxonomy).** The overlap with SLAKE is by design, not an arbitrary relabeling.
- *Why these categories.* The taxonomy follows SLAKE's physician-annotated question categories (Liu et al., 2021). We merge its attribute types and add spatial relations, comparison, and holistic description for multi-image and report tasks (Table 6). VQA-RAD and M3D-VQA (Fig. 9a) use similar categories.
- *Why they are necessary.* The categories describe what a question asks, not a dataset, so they also cover PathVQA, PMC-VQA, reports, and the support pool, which lack native labels. One taxonomy lets us diagnose all tasks, share one budget, and retrieve matching evidence (App. C.3), and the diagnosis matters: stale diagnoses lower 11 of 12 scores (Table 7).
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
*Principle evolution vs. adaptive curricula.* Under the same teachers, data sources, and budget, from the same R5 checkpoint (Tables 7–8; mean change over six benchmarks):

| Condition | Principles | Curriculum | Mean Δ | Improved |
|---|---|---|---|---|
| Principle evolution alone | evolved | stale feedback | −2.65 / −2.78 | 1/6 / 0/6 |
| Adaptive curriculum alone | fixed | current feedback | −5.27 | 0/6 |
| Both (CoEvoMed) | evolved | current feedback | **+1.50** | **6/6** |

*PPO vs. simpler allocation.* Allocation has delayed effects, so the planner optimizes cumulative gain (Eq. 5), not a greedy rule. Its choices follow the learner's state: across R1–R7 it chose [action sequence]. After localization regressed at R4, it switched to [action] at R[x], and localization then recovered (Fig. 6).
*Raw-data degradation.* The raw sources (App. D.3) are not task-aligned (58.3% of 2D records are figure descriptions; Fig. 10), not verified, not targeted, and not adapted. CoEvoMed handles these with the constructor, verifier, planner, and revision agent. The same kinds of sources then reach 91.60 on SLAKE instead of 38.15 (Table 9).
*Selection criteria vs. learning gains.* The criteria screen supervision quality before use. Learning gains are then checked by the loop itself: "learner responses [are] assessed in subsequent training rounds" (App. B), and principles with non-positive net repair are revised again (Sec. 4.3). The selected principles raise all six benchmarks at R5, where the originals lower all six (+6.77 on average; Table 8).

**Q2 (Overlaps; R7).**
*Patient-, study-, and image-level overlaps.* We treated leakage as a design constraint: support data, internal validation, and external tests are separate partitions (Sec. 1; App. C.6), enforced by the submitted code (coevomed/data.py). We screened all 11 2D and 5 3D sources against every external test at four levels: IDs (including study and case IDs), image paths, pixel hashes (exact RGB SHA-256 plus near-duplicate dHash/NCC ≥ 0.95), and normalized text. All checks found zero overlap, including PubMedVision-IU vs. IU-Xray; PMC-OA and PMC-VQA also draw on disjoint PMC articles.
*Was R7 selected by a predefined internal criterion?* R7 was chosen once, for cross-task balance on the external benchmarks (Sec. 5.2). Training, curriculum, and principle revision never use them (App. A, C.6). The predefined internal criterion, the validation objective F_e (App. F.4), selects [R7]. The results also hold without selection: the final R10 beats Hulu-Med-7B on SLAKE (88.67 vs. 86.80) and PathVQA (67.25 vs. 65.60).

**Q3 & W2 (Runs and intervals; CURE-4B; 32B on IU-Xray).**
*Independent runs and intervals.* We ran the full pipeline independently on four learners from three model families, with different architectures and scales: Qwen3-VL (8B and 32B), Gemma 3 (4B), and InternVL3 (9B). Every run improves over its own base on every benchmark evaluated: 16 of 16 comparisons, by +6.52 to +26.76 (Tab. 1; Figs. 3, 5). These gains far exceed the test-set uncertainty (95% CI about ±0.5 on PMC-VQA and ±1.7 on SLAKE). An effect that holds across families, architectures, and scales is not a single-run artifact.
*Why is CURE-4B absent from IU-Xray?* We considered it, but IU-Xray is not a fair test for CURE. IU-Xray is outside CURE's training and evaluation data, so it would be a zero-shot, cross-dataset test, and its reports are longer and differ in style. A score there would mainly reflect this domain shift, not CURE's report quality.
*Why does 32B underperform 8B on IU-Xray?* This is common on IU-Xray: Hulu-Med (7B 67.30 vs. 32B 62.40) and MedGemma (4B 60.50 vs. 27B 59.00) show it too. At matched scale, CoEvoMed-32B beats Hulu-Med-32B by +2.68, and it beats CoEvoMed-8B on the other five benchmarks. Beyond the 0.92 RaTEScore margin, CoEvoMed-8B leads Hulu-Med-7B on six of eight lexical metrics (up to +7.5 ROUGE-2; Fig. 8).

**Q4 & W2 (Complex reasoning).**
*Why not MedXpertQA-MM or MMMU?* We test complex reasoning in open-ended, image-grounded form, where no answer options constrain the output.
*How do the results support generalization?* CoEvoMed leads each such task:
- *Multi-finding synthesis:* first on MIMIC-CXR, IU-Xray, and multi-organ 3D AMOS-MM report generation (Figs. 3–4).
- *Volumetric reasoning:* first on M3D-VQA and 3D-RAD, across 64-slice volumes (Fig. 4).
- *Quantitative computation:* on 3D-RAD Medical Computation (1,002 quantitative questions), +8.6 BLEU-1 over the next-best model, while 27B general models score below 14 (Fig. 9b).
- *Knowledge-based questions:* on all four 2D VQA benchmarks (incl. knowledge-based SLAKE), CoEvoMed-8B beats every proprietary model, e.g., Qwen3.8-Max (Table 1).
