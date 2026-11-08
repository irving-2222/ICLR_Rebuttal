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

**W1 (Isolating components at matched budget).** The component controls in App. D were designed for this decomposition. All conditions start from the same R5 checkpoint and train one round through the same selector–constructor–verifier pipeline under the same budget, differing only in the principles and in the feedback that drives the curriculum (Tables 7–8; mean change over six benchmarks):

| Condition | Principles | Curriculum feedback | Mean Δ | Improved |
|---|---|---|---|---|
| Curriculum adaptation alone | fixed (original) | current | −5.27 | 0/6 |
| Principle evolution alone | evolved | stale (R2 / R3) | −2.65 / −2.78 | 1/6 / 0/6 |
| CoEvoMed | evolved | current | **+1.50** | **6/6** |

Each component alone degrades the learner; only their combination improves all six benchmarks. High-quality synthetic data is therefore not sufficient. The same verified pipeline with fixed principles helps at R2 (+3.09, 6/6) but harms at R5, so data quality drives early progress while co-evolution sustains it. At matched budget, evolved principles add +6.77 on average over fixed ones (+3.33 to +10.12), and current feedback adds +4.15 and +4.28 over stale feedback.

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

Our answers to Q1–Q4 below also address W1–W2.

**Q1 (Separate contributions, PPO, raw data, selection criteria).** We address the four parts in turn.

*Principle evolution vs. adaptive curriculum.* The App. D controls share the same teachers, support pool, and per-round budget, and start from the same R5 checkpoint (mean change over six benchmarks; Tables 7–8):

| Condition | Principles | Curriculum feedback | Mean Δ | Improved |
|---|---|---|---|---|
| Curriculum adaptation alone | fixed (original) | current | −5.27 | 0/6 |
| Principle evolution alone | evolved | stale (R2 / R3) | −2.65 / −2.78 | 1/6 / 0/6 |
| CoEvoMed | evolved | current | **+1.50** | **6/6** |

*PPO.* Allocation is a sequential decision with delayed effects: retention spent now protects gains in later rounds. The planner therefore optimizes cumulative signed validation gain (Eq. 5, App. F.4) rather than a greedy rule. The logged policy responds to the learner's state instead of repeating one rule: across R1–R7 it selected [action sequence]. For example, after localization regressed at R4 (Figure 6), it switched to [action] at R[x], and localization recovered to 62.10 by R6.

*Raw-data degradation.* App. D.3 trains on the raw sources "without supervision reconstruction or adaptive curriculum allocation", and four properties of these sources explain the drop. They are not task-aligned: 58.3% of 2D records are figure descriptions and most others are label-derived items or reports (Figure 10, App. C.3), so the model learns to describe or label rather than answer, most visibly on short-answer SLAKE (−26.69). They are also not verified for factual consistency or visual dependence, not targeted to the learner's weak capabilities, and not adapted as the learner changes. CoEvoMed handles these four properties through the principles and constructor, the verifier, the planner, and the revision agent, respectively (Sections 4.1–4.3), and the same kinds of sources reach 91.60 on SLAKE with fewer examples (Table 9).

*Selection criteria vs. learning gains.* Usable yield, paired coverage, and semantic review screen supervision quality before deployment; learning gains are then assessed by the loop itself, since "learner responses [are] assessed in subsequent training rounds" (App. B) and any principle whose cells show non-positive net repair is revised again (Section 4.3). The selected principles raise all six benchmarks at R5, where the originals lower all six (+6.77 on average; Table 8).

**Q2 (Overlap; R7 selection).** *Overlap.* We treated leakage as a design constraint from the outset. The paper separates support evidence, internal validation, and external tests (Section 1; App. C.6, "Feedback provenance and independence"), and the submitted code enforces this: a run refuses to start if any support, validation, or external record shares a record ID, image path, decoded-RGB SHA-256 hash, or study ID with another partition, each record must carry its original split provenance, and every training job is re-checked against the held-out identity inventories (coevomed/data.py). In addition, every support record's question, answer, or report text was queried for leakage against all validation and external test sets. PubMedVision-IU was screened against IU-Xray in the same way ([n] items removed). [Patient level: see note.]

*R7.* We likewise built two safeguards against checkpoint-selection bias into the paper: one checkpoint for all six benchmarks, which "preserves the joint capability profile of a single learner", and reporting of all ten rounds, "including later performance declines" (App. C.4, Figure 7). R7 was chosen once, for overall cross-task balance on the external benchmarks (Section 5.2); training, curriculum, and principle revision never use them (App. A, C.6). The predefined internal criterion, the validation objective F_e that the planner optimizes (App. F.4), selects [R7, the same checkpoint / R[x], with scores …]. The results also hold without any selection: the final R10 exceeds Hulu-Med-7B on SLAKE (88.67 vs. 86.80) and PathVQA (67.25 vs. 65.60).

**Q3 (Runs and intervals; CURE-4B; 32B on IU-Xray).** *Reliability.* Training the full pipeline is costly (24 A100 GPUs per round over ten rounds; App. B), so we replicated it across learners rather than seeds. It was run end to end on four learners spanning three architecture families and three scales (Qwen3-VL-8B and 32B, Gemma-3-4B, InternVL3-9B), and every run improves over its own base on every benchmark evaluated: 16 of 16 comparisons, by +6.52 to +26.76 (Table 1, Figures 3 and 5, App. C.5). These gains far exceed the sampling uncertainty of the test sets (95% CI half-width about ±0.5 on PMC-VQA and ±1.7 on SLAKE).

*CURE-4B.* CURE targets anatomy-grounded chest X-ray reporting. The mode compared in Figure 3 (AGRG-29 + GRG) relies on the 29 Chest ImaGenome regions defined on MIMIC-CXR, and its authors evaluate report generation on MIMIC-CXR but not on IU-Xray, so we compared it on the benchmark it targets.[ On IU-Xray, it scores [x] RaTEScore.]

*32B on IU-Xray.* This scale reversal is common on IU-Xray: the strongest baseline, Hulu-Med (7B 67.30 vs. 32B 62.40), and MedGemma (4B 60.50 vs. 27B 59.00) show it too, so it reflects this 590-case benchmark rather than our method. At matched scale, CoEvoMed-32B exceeds Hulu-Med-32B by +2.68, and it exceeds CoEvoMed-8B on the other five benchmarks (+0.20 to +2.25; Table 1, Figure 3). Beyond the 0.92 RaTEScore margin, CoEvoMed-8B also leads Hulu-Med-7B on IU-Xray in six of eight lexical metrics, by up to +7.5 ROUGE-2 and +3.7 BLEU-4 (Figure 8).

**Q4 (Complex medical reasoning).** We evaluate complex reasoning in open-ended, image-grounded form rather than through multiple-choice exam benchmarks such as MedXpertQA-MM and MMMU, where answer options constrain the output. Our suite already contains such tasks, and CoEvoMed leads each:
- *Multi-finding synthesis:* report generation on MIMIC-CXR, IU-Xray, and AMOS-MM requires detecting, localizing, and characterizing findings and composing them into a report; CoEvoMed ranks first on all three (Figures 3–4), including multi-organ 3D reports on AMOS-MM.
- *Volumetric reasoning:* M3D-VQA and 3D-RAD require integrating evidence across 64-slice volumes; CoEvoMed ranks first on both (Figure 4).
- *Quantitative computation:* on 3D-RAD Medical Computation (1,002 questions on diameter, size, and thickness), CoEvoMed leads the next-best model by +8.6 BLEU-1 and +8.2 ROUGE-1, while both 27B general models score below 14 (Figure 9b).
- *Knowledge-based questions:* SLAKE draws on a medical knowledge base (Table 3); on all four 2D VQA benchmarks, CoEvoMed-8B exceeds every proprietary model, including Qwen3.8-Max and GPT-5.6-sol (Table 1).

App. G further shows multi-turn clinical reasoning on all nine benchmarks.
