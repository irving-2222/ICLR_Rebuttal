# Paste-ready responses (English)

Each block below is the full text of one Official Comment. Copy everything inside the block.

## Reviewer pUjh (4,948 / 5,000 characters)

````markdown
**W1 (Necessity of the multi-agent framework).** We replaced each agent except the constructor, which writes every example. From the same R5 checkpoint, each row trains one round with one change, all else fixed; entries are changes from R5. Rows 1 and 4 are conditions D and C of **Table 8**.

| From R5 | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|
| Full CoEvoMed | +2.62 | +0.69 | +0.52 | +1.13 | +2.77 | +1.28 |
| Selector → random evidence | −2.00 | −5.28 | −1.77 | −3.62 | −2.73 | −4.70 |
| Verifier → none | −3.33 | −2.83 | −3.13 | −2.91 | −4.17 | −4.42 |
| Revision → original principles | −5.64 | −3.60 | −9.60 | −2.20 | −6.44 | −4.11 |
| Allocation → uniform | +1.55 | +0.09 | +0.12 | +0.81 | +1.94 | +0.59 |
| Single agent | −10.42 | −11.59 | −6.74 | −7.38 | −7.93 | −9.50 |

Random evidence is drawn from the support pool, ignoring the target cell's modality and anatomy (**App. C.3**). Without the verifier, all constructed examples enter training. The single agent is one LLM that selects evidence, constructs and checks examples, and revises principles, under the same allocation.

Replacing the selector, verifier, or revision agent turns the round's gain into a loss on all six benchmarks. Uniform allocation still gains, but less on all six. The simplest substitute, a single agent, loses most on five of six. From the base, training on about 700,000 raw examples lowers all four VQA scores (**Table 9**). Each agent is thus needed; no simpler process we tested substitutes them.

**W2 (Organization).** The layout follows our contributions and scope. The main text presents each contribution: co-evolution formulation (**Sec. 3**), multi-agent system and curriculum policy (**Sec. 4**). **Sec. 5.1** gives the evaluation task composition (four 2D VQA, two report, three 3D); for space, main analyses use one VQA and one report task. The appendix adds what reproduction needs: algorithm (**App. A**), settings (**App. B**), evaluation (**App. C**), and mechanism analyses (**App. D**).

**W3 (Catastrophic forgetting and retention).** CoEvoMed builds on curriculum learning, not continual learning: it trains all tasks every round and replays earlier data (**Eq. 7; Sec. 3.3**). We still measured forgetting on validation cases (**Eq. 6**). Through R7, each round lost 2.3–4.7% of learned cases and fixed 10.9–23.8% of unlearned ones. Average cell-level forgetting (Chaudhry et al., 2018) is 1.27 points at R7 and 2.84 at R10.

Retention is the planner's budget share for learned cells (**Sec. 4.2**). Zeroing it from R5 (as in W1) loses 6.9% of learned cases instead of 3.3%.

Later-round declines come from the data, not our mechanisms. The support pool is fixed (359,355 facts, **App. C.3**), and 95% of it was used by R7; few later examples contain new evidence (18.0% at R8, 2.2% at R10). Scores peak at R7–R8, as new evidence runs out. At R10, **Fig. 7** benchmarks remain within 3 points of their peaks and over 12 above R1.

We chose R7 on internal validation only: it has the highest equal-weight mean of QA and report scores (**App. C.4**). InternVL3-9B peaks at rounds 4–6 (**App. C.5**), so our results do not rely on R7.

**Q1 (MedVLSynther base model).** **Table 1** uses MedVLSynther's published Qwen2.5-VL-7B results. We retrained it on our Qwen3-VL-8B base with its released data and GRPO script. CoEvoMed leads both:

| Model | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther-7B | 55.43 | 77.57 | 72.36 | 65.56 |
| MedVLSynther (our base) | 53.18 | 70.95 | 73.33 | 68.69 |
| CoEvoMed-8B | **67.95** | **82.48** | **91.60** | **69.40** |

**Q2 (Data release).** Yes, upon acceptance, with all principle versions and under each source's license. The data are reproducible now: our code is in the supplement, and all sources are public (**Table 5**).

**Q3 (Capability taxonomy).** The dimensions are necessary because every mechanism runs on the cells they define (**Table 6**). The profile is measured per cell (**Eq. 1**), the planner allocates budget across cells (**Eq. 7**), each principle serves one cell and is revised when it stops improving (**Sec. 4.3**), and the selector retrieves evidence by a cell's modality and anatomy (**App. C.3**). With the cells fixed, a uniform split gains less than current diagnoses (W1) and stale ones lower 11 of 12 scores (**Table 7**), so gains come from diagnosis, not relabeling.

We built our categories on SLAKE's (Liu et al., 2021): physicians annotated them, and SLAKE spans more modalities and body parts than prior datasets. They describe what a question asks, not a dataset, so they fit all tasks: VQA-RAD and M3D-VQA use similar types (Lau et al., 2018; **Fig. 9a**).

On 200 SLAKE questions, our labels match native ones: capability 97.5% (Cohen's κ = 0.958, "almost perfect"; Landis & Koch, 1977), modality 100%, body region 96.5%. We will add them and the new results to the revision.
````

## Reviewer jcb6 (4,902 / 5,000 characters)

````markdown
We thank the reviewer for the positive assessment and the precise suggestions.

**W1 (Isolating the contributions of individual components).** The paper already contains budget-matched ablations of both components. The main text tests them on VQA-RAD and MIMIC-CXR (**Table 2**, **Sec. 5.3**): Panel A for curriculum adaptation, Panel B for principle evolution. For space, **App. D** extends both to all six benchmarks (**Tables 7–8**). We have now run the two missing settings and will add them to the revision, so the table covers all four combinations. All settings start from the same R5 checkpoint and train one round with the same pipeline and budget. To remove principle evolution, we keep the original principles. To remove curriculum adaptation, we split the budget uniformly across capability cells, while construction still uses current feedback. Change from the R5 checkpoint on each benchmark:

| Setting | Principle evolution | Curriculum adaptation | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|---|---|
| Both fixed (new) | No | No | −6.21 | −4.52 | −10.48 | −2.84 | −7.65 | −4.75 |
| Curriculum only | No | Yes | −5.64 | −3.60 | −9.60 | −2.20 | −6.44 | −4.11 |
| Principles only (new) | Yes | No | +1.55 | +0.09 | +0.12 | +0.81 | +1.94 | +0.59 |
| CoEvoMed | Yes | Yes | **+2.62** | **+0.69** | **+0.52** | **+1.13** | **+2.77** | **+1.28** |

Of the two components, principle evolution has the larger effect: with either curriculum, the original principles lower all six benchmarks, while the evolved principles raise all six. Curriculum adaptation adds a smaller but consistent gain: with either principle set, it beats uniform allocation on all six. Keeping both gives the largest gain on every benchmark.

This also answers whether the gains come from high-quality synthetic data. That data is itself produced by our agents: without them, raw data lower all four VQA scores despite more examples (**Table 9**; report scores are new). We also ran fixed principles from the same base under the same total budget (new):

| From the base | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|
| Raw data, no agents | 43.01 | 38.15 | 45.51 | 35.94 | 46.65 | 49.18 |
| Fixed principles (new, same budget) | 74.72 | 88.88 | 61.49 | 62.46 | 62.27 | 61.31 |
| CoEvoMed | **82.48** | **91.60** | **67.95** | **69.40** | **63.62** | **68.22** |

CoEvoMed is higher on all six benchmarks (+1.35 to +7.76). Fixed principles help early but hurt from R5 (**Table 8**), so co-evolution is what sustains the gains. We will add this run to the revision.

**Q1 (Raw-data degradation; fixed-principle reconstruction).** Most of the raw data teach the wrong task. Most 2D records are figure descriptions (58.3%); the rest mix labels, reports, and question–answer pairs in other datasets' formats, such as OmniMedVQA (**Fig. 10; App. C.3**). Trained on them without reconstruction (**App. D.3**), the model mainly learns to describe images instead of answering the benchmark questions. The drop is largest on SLAKE (−26.69), whose answers are short and direct. The raw data are also unverified, untargeted, and static. The table lists these four causes and the CoEvoMed component that addresses each:

| Property of the raw sources | Where CoEvoMed handles it |
|---|---|
| Not task-aligned: mostly figure descriptions rather than questions | Principles define question intent; the constructor turns evidence into supervision for the target capability (**Sections 3, 4.1**) |
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
````

## Reviewer 2Nuw (4,983 / 5,000 characters)

````markdown
**Q1 & W1 (Contributions, PPO, raw data, selection criteria).** The paper already ablates both components with the same teachers, data, budget, and R5 checkpoint (**Table 2, Sec. 5.3; App. D**). We add a uniform split across capability cells as the simpler curriculum, to be added to the revision. Change from R5 on each benchmark:

| Setting | Principle evolution | Adaptive curriculum | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|---|---|
| Neither (new) | No (original) | No (uniform) | −6.21 | −4.52 | −10.48 | −2.84 | −7.65 | −4.75 |
| Curriculum only | No (original) | Yes | −5.64 | −3.60 | −9.60 | −2.20 | −6.44 | −4.11 |
| Principles only (new) | Yes | No (uniform) | +1.55 | +0.09 | +0.12 | +0.81 | +1.94 | +0.59 |
| CoEvoMed | Yes | Yes | **+2.62** | **+0.69** | **+0.52** | **+1.13** | **+2.77** | **+1.28** |

Of the two, principle evolution has the larger effect, and PPO beats uniform allocation on all six with either principle set.

PPO also optimizes cumulative gain (**Eq. 5**), and its choices follow the learner's state. After localization regressed at R4 (60.27 → 56.16), it switched to repair-heavy for R5 and R6, and localization recovered to 59.36 and 62.10 (**Fig. 6**).

The raw-data baseline degrades because its sources (**App. D.3**) are not task-aligned (58.3% of 2D records are figure descriptions; **Fig. 10**), not verified, not targeted, and not adapted. CoEvoMed's agents handle each, and it reaches 91.60 on SLAKE (**Table 9**).

Principles chosen by our criteria do produce later learning gains. In our logs, 12 of 15 accepted revisions turned their target cell's net repair (validation cases fixed minus broken) positive in the next window, versus 6 of 20 eligible principles kept unrevised. By design (**Sec. 4.3; App. B**), a principle is replaced only when the validation cases it fixes no longer outnumber those it breaks, that is, when it stops helping the learner. A replacement is chosen only if a review confirms it targets the errors the learner still makes.

**Q2 (Overlaps; R7).** We excluded patient-, study-, and image-level overlaps by design: support, validation, and test data are separate partitions (**Sec. 1; App. C.6**), enforced in our code. We screened all 11 2D and 5 3D sources against every external test at four levels: IDs (including study, case, and PMC article IDs), image paths, pixel hashes (exact and near-duplicate), and normalized text. All checks found zero overlap, including PubMedVision-IU vs. IU-Xray.

R7 was selected on internal validation only: it has the highest equal-weight mean of QA and report scores, whose per-round change is the planner's reward (**App. C.4**). External benchmark scores never feed back into training or checkpoint selection (**App. A, C.6**).

**Q3 & W2 (Runs and intervals; CURE-4B; 32B on IU-Xray).** Each of four learners (**Sec. 5.1; App. B**) was trained once, and all 16 comparisons beat the base. Table 1 and Fig. 3 use greedy decoding (**App. C.1**); for the std, we re-evaluated CoEvoMed-8B (R7) by sampling with three seeds. Paired CIs compare the greedy run with Hulu-Med-7B, rerun with the same prompts and its own evaluation code (MIMIC-CXR: top baseline Qwen3.6-27B):

| | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|
| Mean±std | 82.63±1.26 | 91.74±0.71 | 67.64±0.32 | 69.17±0.36 | 63.31±0.83 | 68.53±0.74 |
| Baseline | 72.5 | 84.8 | 61.4 | 58.5 | 61.92 | 66.06 |
| 95% paired CI | [5.99, 14.19] | [4.52, 9.14] | [6.08, 7.02] | [9.76, 12.07] | [0.71, 2.68] | [1.15, 3.15] |

Sampled means stay within one std of the greedy scores, and every CI excludes zero. The rerun scores below Hulu-Med's published numbers, which Table 1 keeps, so its margins are conservative. On IU-Xray, the gain is 2.16 under the same protocol and 0.92 against the published 67.30.

CURE-4B is out of domain (trained on MIMIC-CXR-derived data), scoring 28.65 zero-shot on IU-Xray, below every model in **Fig. 3**.

IU-Xray references are short (30.5 words; MIMIC-CXR 53.4): 8B matches them (30.7), 32B writes longer ones (40.1).

**Q4 & W2 (Complex reasoning).** We chose benchmarks that span the data clinical reasoning works on, from 2D images to 3D volumes and from short answers to full reports:

| Data | Benchmarks |
|---|---|
| Chest X-ray | MIMIC-CXR, IU-Xray (full reports) |
| CT, MRI, X-ray | VQA-RAD (clinician-authored), SLAKE (knowledge-based) |
| Pathology | PathVQA |
| Literature figures | PMC-VQA (multiple choice) |
| 3D CT volumes | M3D-VQA (64 slices), 3D-RAD (open-ended, with measurements), AMOS-MM (multi-organ reports) |

On the MMMU Health & Medicine test set (1,752 questions, public answers, **App. C.1** protocol), CoEvoMed-8B scores 62.04, versus 49.66 for its base and 61.30 for MediX-R1-8B, a medical model on the same base. We will add it to the revision.

The results support generalization: CoEvoMed ranks first on all nine benchmarks (**Table 1; Figs. 3–4**).
````
