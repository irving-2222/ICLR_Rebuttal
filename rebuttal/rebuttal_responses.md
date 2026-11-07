# CoEvoMed (Submission 37342) — Rebuttal Responses

每位审稿人的全部回复（所有 W 和 Q）合并为**一条** Official Comment 发布，长度 **≤ 5000 字符**。

- **英文正文**放在代码块里，是正式发布的内容。GitHub 上点代码块右上角的复制按钮即可原样复制 Markdown。
- **中文译文**仅供核对，不发布。

## 发布说明

1. 在对应审稿下方点 **Reply**，不要发成顶层评论。
2. **Readers** 勾选全部五项：Program Chairs、Senior Area Chairs、Area Chairs、**Reviewers**、Authors。不勾 Reviewers 和 Area Chairs，审稿人和 AC 就看不到回复。
3. 发布前点 **Preview**，确认加粗和表格显示正常。
4. 数值变化统一写成相对起点的带符号差值（如 −9.6、+2.8）。对比结果放在表格里，"去掉或断开该智能体"与"CoEvoMed"分列两栏。

---

## Reviewer pUjh

评分 2（弱拒绝）· 信心 3 · 表述 1 · 信息价值 2 · 可靠性 2

### 进度与字符预算

| 条目 | 内容 | 预算 | 当前 | 状态 |
|---|---|---:|---:|---|
| 开头 | 致谢 | ~100 | — | 待写 |
| W1 | 多智能体是否必要 | ~1,450 | 1,451 | 草稿完成 |
| W2 | 论文组织 | ~550 | 546 | 草稿完成 |
| W3 | 遗忘与 R7 的选择 | ~1,290 | 1,288 | 草稿完成 |
| Q1 | MedVLSynther 复现 | ~920 | 921 | 草稿完成（复现结果待填） |
| Q2 | 数据公开 | ~290 | 288 | 草稿完成 |
| Q3 | 能力分类体系 | ~1,020 | 1,029 | 草稿完成（一致率待填） |
| 结尾 | | ~80 | — | 待写 |
| **合计** | | **≤ 5,000**（需压缩约 583） | **5,533** | |

"当前"一栏只统计各条目正文；合计按代码块全文统计，包含条目之间的空行。

### 英文正文（发布用）

```markdown
**W1 (Are the agents necessary?)** Yes. Each agent performs a function the learner measurably depends on. In controlled comparisons from the same starting checkpoint, removing or decoupling an agent degrades performance, whereas the full pipeline improves it:

| Agent | Agent removed or decoupled | CoEvoMed |
|---|---|---|
| Construction agents (Table 9) | Raw data (~700K): all 4 VQA benchmarks fall below base; SLAKE 64.84 → 38.15 (−26.69) | Fewer examples: all 4 improve; SLAKE 64.84 → **91.60 (+26.76)** |
| Revision agent (Table 8, R5) | Original principles: 6/6 benchmarks decline (−2.2 to −9.6) | Revised principles: 6/6 improve (**+0.5 to +2.8**) |
| Planner (Table 7, R5) | Stale R2/R3 feedback: 11/12 scores decline | Current feedback: 6/6 improve |

Because the original principles perform better at R2, no fixed principle set suffices, and online revision is required. The roles must be separate because one agent cannot be both blind and sighted: the constructor writes only from selected source facts without seeing the image, while a different model verifies each example against the image. Every training claim is thus traceable to evidence and independently checked, which is essential for medical data. The same design transfers across four learners and 2D/3D tasks (VQA-RAD: +22.4 on Gemma-3-4B, +20.4 on InternVL3-9B). A substitute would have to perform these same functions, and our controls show that simpler alternatives fail.

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

**Q3 (Capability taxonomy).** The overlap with SLAKE is by design. Rather than inventing categories, our taxonomy adopts the clinically grounded question types of SLAKE and VQA-RAD, whose questions were curated or authored by physicians (Liu et al., 2021; Lau et al., 2018), and extends them in two ways that native labels cannot. (i) Coverage: native capability types exist only for SLAKE and VQA-RAD, in incompatible schemes, while PMC-VQA, PathVQA, report generation, and the support pool have none. A unified taxonomy is required to diagnose all tasks, allocate one budget across them, and retrieve matching evidence (App. C.3). (ii) Granularity: cells cross capability with modality, anatomy, and task form (e.g., localization in abdominal CT). The diagnosis is consequential: replacing it with stale diagnoses lowers 11 of 12 scores (Table 7). Where native labels exist, our annotations agree with them at [xx.x]% (Cohen's κ = [0.xx], "[almost perfect]" agreement; Landis & Koch, 1977). We will add this mapping to Table 6.
```

### 中文译文（不发布）

**W1（这些智能体是否必要？）** 是的。每个智能体都承担着学习者可测量地依赖的功能。在从同一起始检查点出发的受控比较中，去掉或断开某个智能体会使性能下降，而完整流程会使性能提升：

| 智能体 | 去掉或断开该智能体 | CoEvoMed |
|---|---|---|
| 构建智能体（Table 9） | 原始数据（约 70 万条）：四个 VQA 基准全部低于基础模型；SLAKE 64.84 → 38.15（−26.69） | 样本更少：四个基准全部提升；SLAKE 64.84 → **91.60（+26.76）** |
| 修订智能体（Table 8，R5） | 原始原则：6/6 个基准下降（−2.2 至 −9.6） | 修订后的原则：6/6 个基准提升（**+0.5 至 +2.8**） |
| 规划器（Table 7，R5） | 过时的 R2/R3 反馈：12 个分数中 11 个下降 | 当前反馈：6/6 个基准提升 |

由于原始原则在 R2 时表现更好，任何一套固定原则都不够用，必须在线修订。这些角色必须分开，因为同一个智能体不可能既看不见图像又看得见图像：构建器只依据选中的原始事实撰写样本，看不到图像；另一个模型则对照图像核验每个样本。因此每条训练内容都可以追溯到证据，并经过独立核查，这对医学数据至关重要。同一套设计可以迁移到四个学习者模型以及 2D/3D 任务（VQA-RAD：Gemma-3-4B 上提升 22.4，InternVL3-9B 上提升 20.4）。任何替代方案都必须完成同样的功能，而我们的对照实验表明，更简单的方案都失败了。

**W2（论文组织）** 正文给出了全部机制（第 3–4 节，式 1–9），包括在按任务组织的验证集上定义的能力单元（第 3.1 节）；第 5.1 节给出了评估任务的组成（四个 2D VQA 基准、两个报告生成基准和三个 3D 基准）。附录包含实现参数（各智能体所用模型、预算、阈值）和数据集统计，并且每项都在正文相应章节中注明了出处。在页数限制下，这样的安排既保证了方法易读，又保证了完全可复现。

**W3（遗忘与 R7）** CoEvoMed 是课程学习，不是持续学习。每一轮都在固定配额下对所有任务联合训练（式 7），混入回放数据（第 3.3 节），并在每一轮验证所有任务。由于不存在任务序列，灾难性遗忘以及基于任务序列定义的持续学习指标并不适用，论文也没有提出任何关于遗忘的主张。"保留"（retention）指的是分配中维持已习得能力覆盖的那一部分（第 4.2 节），它的作用已在 W1 中与规划器一并检验。尽管如此，退化仍然以更细的粒度被测量：每一轮按样本、按能力单元统计（第 4.1 节，式 6），并计入带符号的奖励（式 8）。对测得的退化做出反应正是闭环设计的预期行为，而且结果是均衡的：从 R1 到 R6，图中报告的五个能力类别最终都高于各自的 R1 水平，定位能力在一度下滑后也回升了（Figure 6）。后期轮次的下降幅度很小：在 R10，SLAKE、PathVQA 和 IU-Xray 都保持在各自峰值的 3 分以内，并且相对 R1 仍分别高出 21.5、26.9 和 12.8（Figure 7）。结果并不依赖 R7。R7 是按跨任务的整体均衡性一次性选定的（第 5.2 节，附录 C.4）：六个基准用的是同一个检查点，而且即使是最后的 R10 检查点，在 SLAKE（88.67 对 86.80）和 PathVQA（67.25 对 65.60）上也超过了 Hulu-Med-7B。

**Q1（MedVLSynther 的基础模型）** 我们注意到了基础模型的差异。不同基础模型之间的绝对分数会把方法本身的效果和骨干模型的效果混在一起，因此有意义的比较是各方法相对其自身基础模型的提升（MedVLSynther 采用其原文发表的结果和评测协议）：

| 相对自身基础模型的提升 | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther-7B（Qwen2.5-VL-7B） | +6.13 | +8.82 | +6.65 | +0.17 |
| CoEvoMed-8B（Qwen3-VL-8B） | **+13.82** | **+25.72** | **+26.76** | **+26.63** |

为了彻底消除基础模型的差异，我们还用 MedVLSynther 公开的数据和 GRPO 训练脚本训练了 Qwen3-VL-8B（奖励函数取自作者的 MedVLThinker 代码），并在我们的评测协议下进行评估：

| 相同基础模型：Qwen3-VL-8B | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther 配方 | [x.xx] | [x.xx] | [x.xx] | [x.xx] |
| CoEvoMed-8B | **67.95** | **82.48** | **91.60** | **69.40** |

**Q2（数据公开）** 会公开。论文被接收后，我们将按各源数据的许可公开合成数据和全部版本的构建原则：图像只以源数据中的标识引用、不重新分发；对于协议禁止再分发的源数据（如 CheXpert、ReXGradient-160K），我们提供可重新生成这部分数据的脚本。

**Q3（能力分类体系）** 与 SLAKE 的重合是有意设计的。我们没有另起炉灶发明新类别，而是采用了 SLAKE 和 VQA-RAD 在临床上有依据的问题类型，这两个数据集的问题由医生审定或撰写（Liu et al., 2021；Lau et al., 2018）。在此基础上，我们从两个方面做了原生标签无法做到的扩展。(i) 覆盖范围：只有 SLAKE 和 VQA-RAD 带有原生的能力类型标签，而且两套体系互不兼容；PMC-VQA、PathVQA、报告生成任务和支持数据池都没有这类标签。要诊断所有任务、在它们之间分配同一份预算并检索匹配的证据（附录 C.3），就必须有一套统一的分类体系。(ii) 粒度：能力单元是能力与模态、解剖部位、任务形式的组合（例如腹部 CT 中的定位）。这种诊断有实际作用：用过时的诊断替代它，会使 12 个分数中的 11 个下降（Table 7）。在有原生标签的数据上，我们的标注与原生标签的一致率为 [xx.x]%（Cohen's κ = [0.xx]，属于"[几乎完全一致]"；Landis & Koch, 1977）。我们会把这一对应关系补充到 Table 6 中。

### 发布前待核对

- [ ] **W1 修订智能体**：Exp 2 的条件 C 和 D 是否只在原则上不同（分配动作、预算一致）？正文把两者的差距归因于原则。
- [ ] **W1 规划器**：Exp 1 的三组是否使用相同的原则，只替换了反馈？
- [ ] **W2 可选补充**：如果想在不让步的前提下给一个姿态，可以在 W2 末尾加一句（约 70 字符）：`We will add a role summary table to Section 4 for quick reference.`
- [x] **W3 回放数据**：已确认主实验每轮混入回放数据，W3 已写入 "mixes in replay data (Section 3.3)"。
- [ ] **R7 的选择依据（留给 2Nuw Q2）**：W3 只引用了论文的说法（按跨任务整体均衡性选定），没有说这个"整体均衡"是在内部验证集上还是外部基准上衡量的；论文也没写明。2Nuw 的 Q2 会直接问"R7 是否完全依据预先定义的内部验证标准选出"，需要你提供实际做法。
- [x] **W3 PathVQA 峰值**：已确认 PathVQA 的 R8 略高于 R7；R10 的 67.25 仍在峰值 3 分以内，正文说法成立。
- [ ] **Q1 占位符**：复现完成后，在第二张表里填入复现模型在四个基准上的得分 `[x.xx]`（与 CoEvoMed 同一评测流程）。如果任何一项高于 CoEvoMed，需要重新讨论写法。
- [ ] **Q1 数字来源**：确认 Table 1 的 MedVLSynther 数字引自其论文（与其 GitHub README 的数字完全一致）。正文写的是 "as published"。
- [ ] **Q1 与附录 C.1 的一致性**：C.1 写的是"本研究评估的基线与 CoEvoMed 使用相同的评估集和评分规则"，MedVLSynther 是引用数，与这句不符。Q1 已如实写明"按原文发表的结果和协议"；定稿时建议把 C.1 改为区分"我们评测的基线"和"引用原文的基线"。
- [ ] **字符超预算**：全部条目写完后合计 5,533 字符，需压缩到 5,000 以内（留约 50 余量）。候选做法：不写开头结尾，W1、W3、Q3 各压约 150，Q1 精简说明文字。
- [ ] **Q2 承诺**：正文承诺为禁止再分发的源数据提供重新生成脚本。确认接收后能兑现；如果不打算做，把最后半句改为 "are excluded from the release"。
- [ ] **Q2 待确认许可**：PMC-OA、MedTrinity BHX、RadGenome-ChestCT、Med-MAT 的许可没能直接核实，AbdomenAtlas1.0Mini 的附加条款也不确定，公开前需逐个确认（见下方"Q2 源数据许可核对"）。
- [ ] **Q3 一致率**：拿到标注记录后计算与 SLAKE、VQA-RAD 原生标签的一致率和 Cohen's κ，填入 `[xx.x]%` 和 `[0.xx]`，并按下方"Q3 一致率解读标准"选择措辞：κ ≥ 0.81 写 "almost perfect"，0.61–0.80 写 "substantial"。低于 0.61 时需要重新讨论写法。
- [ ] **Q3 类别来源**：正文写的是分类体系采用了 SLAKE **和 VQA-RAD** 的问题类型。你说的是参照 SLAKE；如果没有参照 VQA-RAD，删掉 "and VQA-RAD" 和 "Lau et al., 2018"，但"两套体系互不兼容"那半句也要相应改写。
- [ ] **Q3 对应关系**：下方"Q3 原生标签与我们类别的对应关系"中，Plane 和 Quantity / COUNT 两行的归属需要你确认。
- [ ] **W1 可选补充**：如果核验器日志里有拒绝率，可以在 "independently checked" 之后加一句（约 75 字符），作为核验器单独起作用的正面证据：`The verifier rejects [X]% of constructed candidates, mainly for [reason].`

### W1 数字出处

| 正文数字 | 出处（论文印刷页码） |
|---|---|
| SLAKE 64.84→38.15 / 91.60；四个 VQA 基准全部低于基础模型 | Table 9，p.26 |
| R5 原始原则 −2.20 至 −9.60；修订后原则 +0.52 至 +2.77 | Table 8，p.26 |
| R2 时原始原则在四个 VQA 基准上更好 | Table 8，p.26 |
| R2/R3 反馈 12 个分数中 11 个下降；R5 反馈六个全部提升 | Table 7，p.25 |
| 构建器不访问图像，核验器对照图像核验 | 附录 A，p.16；附录 B，p.17 |
| Gemma-3-4B VQA-RAD +22.39 | §5.3，p.8 |
| InternVL3-9B VQA-RAD +20.40 | 附录 C.5，p.24 |

### W2 论据出处

| 正文说法 | 出处（论文印刷页码） |
|---|---|
| 正文给出全部机制（式 1–9） | §3–4，p.3–6 |
| 能力单元定义在按任务组织的验证集上 | §3.1，p.3（式 1） |
| 评估任务组成：四个 2D VQA、两个报告生成、三个 3D 基准 | §5.1，p.7 |
| 所有主结果和机制分析都在正文 | §5.2–5.3，p.6–9（Table 1–2，Figure 3–7） |
| 附录的内容在正文中注明出处 | 正文共 11 处显式引用附录（A、B×3、C×2、C.5、D、D.2、F、F.4） |

### W2 可能被追问的点

四种课程动作的具体名称、各智能体所用模型、每轮预算和修订阈值只写在附录 B（p.17–18），正文 §4 没有。如果 pUjh 在讨论阶段追问，可以回答这些属于实现参数，并指出在附录 B 的具体位置。

### W3 论据出处

| 正文说法 | 出处（论文印刷页码） |
|---|---|
| 每轮在固定任务配额下联合训练所有任务 | §3，p.3；式 7，§4.2，p.5 |
| 每轮验证所有任务 | 算法 1 第 9 行，p.16 |
| 论文没有关于遗忘的主张 | 全文检索：forgetting、catastrophic、continual 均未出现 |
| retention 是分配中维持已习得能力覆盖的部分 | §4.2，p.5；附录 B 的四种动作，p.17 |
| 按样本、按能力单元统计退化 | §4.1，p.5（式 6）；附录 C.4，p.24 |
| 带符号的奖励保留退化 | §4.2，p.5（式 8 之后） |
| R1→R6 五类全部高于 R1：异常检测 +4.33、器官识别 +0.88、定位 +1.83（R4 曾降到 56.16）、模态识别 +2.09、属性 +10.27 | Figure 6，p.9 |
| R10 距峰值：SLAKE −2.93、PathVQA 约 −2.2 至 −2.6（按图读数）、IU-Xray −2.39；R10 相对 R1：+21.47、+26.85、+12.77 | Figure 7，p.9 |
| Hulu-Med-7B：SLAKE 86.80、PathVQA 65.60 | Table 1，p.6 |
| 每轮混入回放数据 | §3.3，p.4；附录 B，p.17 |
| 六个基准使用同一检查点 | §5.2，p.7；附录 C.4，p.24 |
| R7 按跨任务整体均衡性一次性选定 | §5.2，p.7（"selected for the best overall cross-task balance"）；附录 C.4，p.24（"Checkpoint selection" 一段） |

### Q1 论据出处

| 正文说法 | 出处 |
|---|---|
| MedVLSynther-7B：PMC-VQA 55.43、VQA-RAD 77.57、SLAKE 72.36、PathVQA 65.56 | 本文 Table 1，p.6；MedVLSynther GitHub README 结果表 |
| Qwen2.5-VL-7B（其协议）：PMC-VQA 49.30、VQA-RAD 68.75、SLAKE 65.71、PathVQA 65.39 | MedVLSynther GitHub README 结果表 |
| Qwen3-VL-8B（我们的协议）：54.13、56.76、64.84、42.77；CoEvoMed-8B：67.95、82.48、91.60、69.40 | 本文 Table 1，p.6 |

### Q1 复现配置备忘

| 项目 | 设置 |
|---|---|
| 数据 | Hugging Face `MedVLSynther/MedSynVQA-13K`（README 中也写作 MedVLSynther-13K），用其仓库的 `data_process/convert_verl_format.py` 转成 verl 格式 |
| 训练脚本 | `train/7b_biomedica_webdataset_glm_generated_qwen_verified_VQA_parquet_25k_filtered_13k_grpo_8a100.sh`，只把基础模型路径换成 Qwen3-VL-8B-Instruct |
| 官方 7B 超参 | verl GRPO；train batch 64；PPO mini batch 32；每卡 micro batch 8；每条 prompt 8 个 rollout；最长回复 4096；学习率 1e-6；1 个 epoch（约 205 步）；KL loss 系数 0.01（low_var_kl）；vLLM，TP=2，显存占用 0.6；单机 8×A100 |
| 奖励函数 | MedVLSynther 仓库缺少 `train/my_reward.py`，使用 MedVLThinker 仓库的 `train/my_reward.py`。它读取的字段（answer、answer_label、ground_truth）与 MedVLSynther 的数据格式一致 |
| 开跑前检查 | 奖励要求整段回复完整匹配 `<think>…</think><answer>…</answer>`，否则得 0 分。正式训练前先在几十条样本上检查格式奖励的通过率 |
| 评测 | 用与其他基线相同的评测流程测 PMC-VQA、VQA-RAD、SLAKE、PathVQA；模型输出带 `<think>`，需要解析 `<answer>` 中的答案 |
| 预计时间 | 搭环境 0.5–1 天；训练约 10–20 小时（先跑 10 步实测每步耗时）；评测约 0.5 天 |

### Q2 源数据许可核对

范围：附录 C.3 和 Table 5（p.21–23）列出的支持数据池，即合成数据的来源。外部评测基准（含 MIMIC-CXR、IU-Xray 测试集）不进入合成数据，不在此列。Hugging Face 和 arXiv 在本会话中无法访问，以下结论来自各数据集的 GitHub 仓库和网页检索，标"待确认"的需要你在公开前到官方页面核实。

| 源数据 | 许可或使用条款 | 派生数据能否公开 | 依据 |
|---|---|---|---|
| TotalSegmentator | CC BY 4.0 | 可以，注明出处 | Zenodo 记录与镜像元数据 |
| TCGA-CRC | GDC 开放获取层 | 可以，注明出处 | GDC 数据政策 |
| PubMedVision（非 IU 部分） | Apache-2.0（数据卡） | 可以 | Hugging Face 数据卡（经检索） |
| LLaVA-Med | CC BY-NC 4.0，仅限研究 | 可以，限非商业研究；图像只给链接 | LLaVA-Med GitHub README |
| CT-RATE | CC BY-NC-SA 4.0 | 可以，须用相同许可（NC-SA） | CT-CLIP GitHub README |
| RadGenome-ChestCT | 基于 CT-RATE，推测同为 NC-SA | 待确认 | 未找到明确声明 |
| M3D-Cap | 图像与报告来自 Radiopaedia，已获其授权，支持非商业机器学习使用 | 可以，限非商业 | M3D GitHub README |
| ROCO | 图像来自 CC BY 或 CC BY-NC 的 PMC 开放获取论文 | 可以，限非商业；图像按原论文许可 | ROCOv2 数据卡与论文（经检索） |
| PMC-OA | PMC 开放获取子集，逐篇许可 | 待确认 | 主数据集许可字段未找到 |
| OmniMedVQA | 按各子数据集：开放获取部分直接提供，受限部分只给图像相对路径 | 可以，按子数据集许可，图像不分发 | 其 HF 数据卡与 CVPR 补充材料（经检索） |
| Med-MAT | 按各子数据集，部分子集"因许可不能分享" | 部分可以 | Med-MAT GitHub README |
| AbdomenAtlas1.0Mini | HF 标注 CC BY-NC-SA 4.0，另有访问条款；GitHub 仓库 LICENSE 写 CC BY-NC-ND 4.0；1.1 版条款禁止再分发 | 待确认，可能受限 | AbdomenAtlas GitHub 仓库；HF 页面（经检索） |
| MedTrinity BHX | BHX 在 PhysioNet 为开放获取，具体许可未查到 | 待确认 | PhysioNet 页面（经检索） |
| PubMedVision-IU 子集 | 图像来自 IU-Xray（Open-i），CC BY-NC-ND 4.0 | 不可以（禁止演绎作品） | 镜像与 Open-i 说明（经检索） |
| Quilt-1M | 需同意条款才能获取，条款禁止进一步分发、限定研究用途 | 不可以直接分发 | Quilt-1M GitHub README |
| CheXpert | Stanford 研究使用协议，非商业，禁止分发或复制数据集 | 不可以 | Stanford AIMI 页面（经检索） |
| ReXGradient-160K | 数据使用协议：仅限非商业研究，只能与本项目授权人员共享，禁止公开数据汇编 | 不可以 | 协议文本镜像（经检索） |

结论与建议：
1. 不是所有源数据都能公开派生数据。CheXpert、ReXGradient-160K、Quilt-1M、IU-Xray（PubMedVision-IU）明确受限，AbdomenAtlas 可能受限。
2. 可公开部分的通行做法（OmniMedVQA、Med-MAT、LLaVA-Med 都这样做）：只发布合成的文本（问答与报告）和源数据中的图像标识，不重新分发图像，使用者自行按原许可获取图像。
3. 因为含 CT-RATE（NC-SA）派生内容，整体发布许可建议用 CC BY-NC-SA 4.0。
4. 构建原则（各版本）和代码是我们自己的产出，不受源数据许可约束，可以完整公开。

### Q3 原生标签与我们类别的对应关系（初稿，需你确认）

| SLAKE 原生 content type | VQA-RAD 原生 question type | 我们的视觉能力类别（Table 6） |
|---|---|---|
| Modality | MODALITY | 模态识别 |
| Plane | PLANE | **待确认**（模态识别，或属性判断） |
| Organ | ORGAN | 器官识别 |
| Abnormality | ABN、PRES | 异常检测 |
| Position | POS | 定位（部分可能属于空间关系） |
| Color、Shape、Size | COLOR、SIZE、ATTRIB | 属性判断 |
| Quantity | COUNT | **待确认**（属性判断？） |
| KG | — | 医学知识 |
| — | OTHER | 不纳入一致率统计 |
| — | — | 空间关系、比较、整体描述：无原生对应，属于我们的扩展 |

计算方法：只在有明确对应的类别上统计。报告总体一致率、Cohen's κ 和混淆矩阵，SLAKE 和 VQA-RAD 分别报告。

### Q3 一致率解读标准与可引用文献

| 文献 | 可引用的内容 | 核实情况 |
|---|---|---|
| Landis & Koch (1977). The measurement of observer agreement for categorical data. *Biometrics* 33(1):159–174 | κ 分级：0.41–0.60 moderate，0.61–0.80 substantial，0.81–1.00 almost perfect | 经典标准，正文已引用 |
| McHugh (2012). Interrater reliability: the kappa statistic. *Biochemia Medica* 22(3):276–282 | 认为上述标准对医疗研究偏宽松，提出更严格的分级 | 论点经检索确认；具体分级（印象中 ≥0.80 为 strong、>0.90 为 almost perfect）需对照原文 |
| Gilardi, Alizadeh & Kubli (2023). ChatGPT outperforms crowd workers for text-annotation tasks. *PNAS* 120(30):e2305016120 | LLM 标注准确率平均比众包高约 25 个百分点；受训标注员之间的一致率约 79% | 经检索确认 |
| Mukherjee et al. (2023). Feasibility of using the privacy-preserving large language model Vicuna for labeling radiology reports. *Radiology* 309(1):e231147 | 放射报告的 LLM 标注与成熟标注器的一致性为中等到较高（Fleiss κ 中位数约 0.52–0.64） | 经检索确认，可作为同领域对照 |
| Liu et al. (2021). SLAKE. *ISBI 2021* | 语义标注由经验丰富的医生完成；候选问题交给医生保留或修改 | 经检索确认（摘要与原文片段） |
| Lau et al. (2018). A dataset of clinically generated visual questions and answers about radiology images. *Scientific Data* 5:180251 | 问题由临床医生撰写，问答对人工归入 11 种问题类型 | 经检索确认 |

用法建议：κ 达到 0.81 以上，正文只引 Landis & Koch 即可。κ 在 0.61–0.80 之间时，写 "substantial"，并补一句与 Mukherjee et al. (2023) 的对比（高于其 0.52–0.64），说明在同类放射学 LLM 标注中处于较高水平。

---

## Reviewer jcb6

评分 3（弱接收）· 信心 3 — 待写

---

## Reviewer 2Nuw

评分 2（弱拒绝）· 信心 4 — 待写
