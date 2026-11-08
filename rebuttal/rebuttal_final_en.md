# Rebuttal Responses — Submission 37342 (CoEvoMed)

---

## Response to Reviewer pUjh

**W1 (Is the multi-agent framework necessary?)** Yes. The experiments in App. D validate the critical function of each agent role. Each comparison starts from the same checkpoint, with and without that function:

| Agent role | Critical function | Without it | With it |
|---|---|---|---|
| Selector, constructor, verifier | Turn medical evidence into verified, task-aligned supervision | Raw data (~700K): all 4 VQA benchmarks fall below the base model; SLAKE 64.84 → 38.15 | Fewer examples: all 4 improve; SLAKE → **91.60** (Table 9) |
| Revision agent | Update the principles as the learner changes | Original principles at R5: 6/6 benchmarks decline (−2.2 to −9.6) | Revised principles: **6/6 improve** (+0.5 to +2.8) (Table 8) |
| Curriculum planner | Allocate the budget to the learner's current needs | Stale R2/R3 feedback: 11/12 scores decline | Current feedback: **6/6 improve** (Table 7) |

The original principles work better at R2 (5 of 6 benchmarks) but worse at R5 (6 of 6; Table 8). No fixed set of principles works at every stage, so an online revision agent is needed.

Can another plausible agent process substitute them? Any substitute must still perform these functions, and the simpler alternatives in the table (raw data, fixed principles, stale feedback) all fail.

Why not merge the roles into one agent? We separate them for three reasons (App. A–B):
1. **Independent checking.** The verifier (Qwen3.6-27B) is a different model from the constructor (deepseek-v4-flash), so no model checks its own output. LLMs struggle to correct their own outputs without external feedback (Huang et al., ICLR 2024).
2. **Evidence grounding.** The constructor never sees the image and writes only from selected source facts, so every claim comes from the evidence. The verifier then checks it against the image. A merged agent would see the image while writing and could add findings that no source supports.
3. **Different decisions.** The planner is not a language model. It is a small policy network trained with PPO every round. The revision agent acts only at the end of each window.

**W2 (Organization).** The main text specifies every mechanism (Sections 3–4, Eqs. 1–9), including the capability cells defined on task-organized validation sets (Section 3.1), and Section 5.1 gives the evaluation task composition (four 2D VQA, two report-generation, and three 3D benchmarks). The appendix contains implementation parameters (agent models, budgets, thresholds) and dataset statistics, each referenced from the relevant section. Given the page limit, this arrangement keeps the method readable while ensuring full reproducibility.

**W3 (Forgetting and R7).** CoEvoMed is curriculum learning, not continual learning. Every round trains all tasks jointly under fixed quotas (Eq. 7), mixes in replay data (Section 3.3), and validates every task. With no task sequence, catastrophic forgetting and the continual-learning metrics defined over task sequences do not apply, and the paper makes no forgetting claim. "Retention" denotes the allocation lane that maintains coverage of acquired capabilities (Section 4.2), evaluated with the planner in W1. Regressions are still measured more finely, per case and per capability cell each round (Section 4.1, Eq. 6), and enter the signed reward (Eq. 8). Reacting to them is the intended closed-loop behavior, and the outcome is balanced: from R1 to R6, all five reported categories end above their R1 level, including localization after its dip (Figure 6). Later-round declines are small: at R10, SLAKE, PathVQA, and IU-Xray stay within 3 points of their peaks and retain +21.5, +26.9, and +12.8 over R1 (Figure 7). The results do not depend on R7, which was chosen once for overall cross-task balance (Section 5.2, App. C.4): one checkpoint serves all six benchmarks, and even the final R10 checkpoint exceeds Hulu-Med-7B on SLAKE (88.67 vs. 86.80) and PathVQA (67.25 vs. 65.60).

**Q1 (MedVLSynther base model).** We were aware of the base difference. Absolute scores across different bases conflate a method with its backbone, so the meaningful comparison is each method's gain over its own base (MedVLSynther as published, under its protocol):

| Gain over own base | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther-7B (Qwen2.5-VL-7B) | +6.13 | +8.82 | +6.65 | +0.17 |
| CoEvoMed-8B (Qwen3-VL-8B) | **+13.82** | **+25.72** | **+26.76** | **+26.63** |

To remove the base difference entirely, we also trained Qwen3-VL-8B with MedVLSynther's released data and GRPO script (reward function from the authors' MedVLThinker code) and evaluated it under our protocol:

| Same base: Qwen3-VL-8B | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther recipe | [x.xx] | [x.xx] | [x.xx] | [x.xx] |
| CoEvoMed-8B | **67.95** | **82.48** | **91.60** | **69.40** |

**Q2 (Data release).** Yes. Upon acceptance, we will release the synthesized data and all principle versions under each source's license: images are referenced by identifiers, and sources that prohibit redistribution (e.g., CheXpert, ReXGradient-160K) are covered by regeneration scripts.

**Q3 (Capability taxonomy).** The overlap with SLAKE is by design. Our categories follow SLAKE's physician-annotated question categories (Liu et al., 2021), grouping its fine-grained attribute types and adding spatial relations, comparison, and holistic description for multi-object, multi-image, and report tasks (Table 6). The categories describe what a question asks of an image (acquisition, anatomy, location, abnormality, attributes, knowledge), not a particular dataset, so they apply equally to PathVQA, PMC-VQA, reports, and the support pool, none of which has native labels. Independent benchmarks converge on the same scheme, e.g., VQA-RAD's 11 question types and M3D-VQA's plane, phase, organ, abnormality, and location (Figure 9a). Our annotations agree with SLAKE's native labels at [xx.x]% (Cohen's κ = [0.xx], "[almost perfect]"; Landis & Koch, 1977), and a manual audit of [N] PathVQA, PMC-VQA, and support items confirms [xx.x]%. This unified taxonomy enables diagnosis, allocation, and evidence retrieval across all tasks, and the diagnosis matters: stale diagnoses lower 11 of 12 scores (Table 7).

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

**Q1 (Raw-data degradation; fixed-principle reconstruction).** We attribute the degradation to four properties of the raw sources, on which App. D.3 trains "without supervision reconstruction or adaptive curriculum allocation". The right column notes where each property is handled in CoEvoMed:

| Property of the raw sources | Where CoEvoMed handles it |
|---|---|
| Not task-aligned: 58.3% of 2D records are figure descriptions, most others label-derived items or reports (Figure 10, App. C.3), so the model learns to describe or label rather than answer | Principles define question intent; the constructor turns evidence into supervision for the target capability (Sections 3, 4.1) |
| Not verified: image–text associations are never checked | The verifier checks factual consistency and visual dependence (Section 4.1) |
| Not targeted: the mix follows source availability, not the learner's needs | The planner allocates a fixed budget to weak and regressing capabilities (Section 4.2) |
| Not adaptive: supervision stays fixed while the learner changes | The revision agent updates principles from residual errors (Section 4.3) |

Hence ~700K raw examples fall below the base model, most sharply on SLAKE (−26.69), whose answers are short, while the same kinds of sources routed through CoEvoMed reach 91.60 with fewer examples. Fixed-principle reconstruction covers the first three rows but not the fourth. It therefore helps at R2 (+1.78 to +3.90, all six) yet harms at R5, whereas evolved principles add +6.77 under the same budget (W1). Principle evolution is what sustains the gains.

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
