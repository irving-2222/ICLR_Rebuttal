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
| Q3 | 能力分类体系 | ~1,120 | 1,117 | 草稿完成（标注数据待填） |
| 结尾 | | ~80 | — | 待写 |
| **合计** | | **≤ 5,000**（需压缩约 671） | **5,621** | |

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

**Q3 (Capability taxonomy).** The overlap with SLAKE is by design. Our categories follow SLAKE's physician-annotated question categories (Liu et al., 2021), grouping its fine-grained attribute types and adding spatial relations, comparison, and holistic description for multi-object, multi-image, and report tasks (Table 6). The categories describe what a question asks of an image (acquisition, anatomy, location, abnormality, attributes, knowledge), not a particular dataset, so they apply equally to PathVQA, PMC-VQA, reports, and the support pool, none of which has native labels. Independent benchmarks converge on the same scheme, e.g., VQA-RAD's 11 question types and M3D-VQA's plane, phase, organ, abnormality, and location (Figure 9a). Our annotations agree with SLAKE's native labels at [xx.x]% (Cohen's κ = [0.xx], "[almost perfect]"; Landis & Koch, 1977), and a manual audit of [N] PathVQA, PMC-VQA, and support items confirms [xx.x]%. This unified taxonomy enables diagnosis, allocation, and evidence retrieval across all tasks, and the diagnosis matters: stale diagnoses lower 11 of 12 scores (Table 7).
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

**Q3（能力分类体系）** 与 SLAKE 的重合是有意设计的。我们的类别沿用了 SLAKE 由医生标注的问题类别（Liu et al., 2021），把其中细分的属性类型合并为一类，并为多目标、多图像和报告任务增加了空间关系、比较和整体描述三类（Table 6）。这些类别描述的是一个问题针对图像在问什么（成像方式、解剖结构、位置、异常、属性、医学知识），而不是某个特定数据集，因此同样适用于 PathVQA、PMC-VQA、报告生成任务和支持数据池，而这些数据都没有原生标签。其他独立构建的基准也收敛到了同一套体系，例如 VQA-RAD 的 11 种问题类型，以及 M3D-VQA 的扫描平面、期相、器官、异常和位置五类（Figure 9a）。我们的标注与 SLAKE 原生标签的一致率为 [xx.x]%（Cohen's κ = [0.xx]，属于"[几乎完全一致]"；Landis & Koch, 1977）；对 [N] 条 PathVQA、PMC-VQA 和支持数据样本的人工抽查确认准确率为 [xx.x]%。这套统一的分类体系让我们能在所有任务上进行诊断、分配预算和检索证据，而且这种诊断确实起作用：使用过时的诊断会使 12 个分数中的 11 个下降（Table 7）。

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
- [ ] **字符超预算**：全部条目写完后合计 5,621 字符，需压缩到 5,000 以内（留约 50 余量）。候选做法：不写开头结尾，W1、W3、Q3 各压约 150，Q1 精简说明文字。
- [ ] **Q2 承诺**：正文承诺为禁止再分发的源数据提供重新生成脚本。确认接收后能兑现；如果不打算做，把最后半句改为 "are excluded from the release"。
- [ ] **Q2 待确认许可**：PMC-OA、MedTrinity BHX、RadGenome-ChestCT、Med-MAT 的许可没能直接核实，AbdomenAtlas1.0Mini 的附加条款也不确定，公开前需逐个确认（见下方"Q2 源数据许可核对"）。
- [ ] **Q3 一致率**：拿到标注记录后计算与 SLAKE 原生标签的一致率和 Cohen's κ，填入 `[xx.x]%` 和 `[0.xx]`，并按下方"Q3 一致率解读标准"选择措辞：κ ≥ 0.81 写 "almost perfect"，0.61–0.80 写 "substantial"。低于 0.61 时需要重新讨论写法。VQA-RAD 有原生标签，也可以一并计算，作为补充。
- [ ] **Q3 人工抽查**：正文写了"对 [N] 条 PathVQA、PMC-VQA 和支持数据样本的人工抽查"，用来证明没有原生标签的数据也标得准。如果标注记录里没有人工抽查，有两种处理：(a) 现在抽 100–200 条做一次人工核对；(b) 删掉这半句，改为报告各数据集的类别分布，说明九类都被用到、没有大量无法归类的样本。
- [ ] **Q3 SLAKE 措辞**：SLAKE 原文能确认的是"语义标注由经验丰富的医生完成"，并且"每个问题都标有语义标签，用于区分问题类型"；没有找到"类别体系由专家设计"的明确表述。所以正文写的是 "physician-annotated question categories"（医生标注的问题类别），而不是 "expert-designed"。如果你手上的 SLAKE 原文有"类别由医生设计"的原句，告诉我页码，可以改成 "designed and annotated by physicians"。
- [ ] **Q3 对应关系**：正文写了"把 SLAKE 细分的属性类型合并为一类，并新增空间关系、比较和整体描述三类"。请对照下方对应表确认，尤其是 SLAKE 的 Plane 和 Quantity 分别归到哪一类。
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

评分 3（弱接收）· 信心 3 · 表述 3 · 信息价值 2 · 可靠性 3

### 进度与字符预算

| 条目 | 内容 | 当前 | 状态 |
|---|---|---:|---|
| 开头 | 致谢 | 78 | 草稿完成 |
| W1 | 在预算匹配下分离各组件 | 1,173 | 草稿完成 |
| Q1 | 原始数据退化原因；固定原则重构是否也有效 | 1,595 | 草稿完成 |
| **合计** | | **2,850** | ≤ 5,000 |

### 英文正文（发布用）

```markdown
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
```

### 中文译文（不发布）

我们感谢审稿人的积极评价和具体建议。

**W1（在预算匹配下分离各组件）** 附录 D 的组件对照实验正是为这种分解而设计的。所有条件都从同一个 R5 检查点出发，经过相同的"选择器—构建器—核验器"流程，在相同预算下训练一轮，区别只在于构建原则和驱动课程的反馈（Table 7–8；六个基准上的平均变化）：

| 条件 | 原则 | 课程所用反馈 | 平均变化 | 提升的基准数 |
|---|---|---|---|---|
| 只有课程自适应 | 固定（原始） | 当前 | −5.27 | 0/6 |
| 只有原则演化 | 演化后 | 过时（R2 / R3） | −2.65 / −2.78 | 1/6 / 0/6 |
| CoEvoMed | 演化后 | 当前 | **+1.50** | **6/6** |

任何一个组件单独使用都会让学习者变差；只有两者结合，六个基准才全部提升。因此，高质量合成数据本身并不足够：同一条经过核验的流程，用固定原则在 R2 时有帮助（+3.09，6/6），到 R5 时却有害；数据质量推动了早期的进步，而共同演化让进步得以持续。在预算匹配下，演化后的原则比固定原则平均高 6.77（+3.33 至 +10.12），当前反馈比过时反馈分别高 4.15 和 4.28。

**Q1（原始数据退化的原因；固定原则重构的效果）** 我们把这种退化归因于原始数据的四个特点；附录 D.3 正是在"没有监督重构，也没有自适应课程分配"的条件下用这些数据训练的。右栏注明了 CoEvoMed 在哪个环节处理每一个特点：

| 原始数据的特点 | CoEvoMed 在哪里处理它 |
|---|---|
| 与任务不对齐：2D 记录中 58.3% 是图像描述，其余大多是由标签转换的条目或报告（Figure 10，附录 C.3），模型学会的是描述或贴标签，而不是回答问题 | 构建原则定义问题意图；构建器把证据转化为针对目标能力的监督数据（第 3、4.1 节） |
| 未经核查：图文关联从未被检查 | 核验器检查事实一致性和视觉依赖性（第 4.1 节） |
| 没有针对性：数据构成取决于数据源里有什么，而不是学习者需要什么 | 规划器把固定预算分配给薄弱和退化的能力（第 4.2 节） |
| 不会自适应：学习者在变化，监督却一成不变 | 修订智能体根据残余错误更新构建原则（第 4.3 节） |

因此，约 70 万条原始数据训练后低于基础模型，其中答案简短的 SLAKE 降幅最大（−26.69）；而同类数据源经过 CoEvoMed 处理后，用更少的样本就达到 91.60。固定原则重构覆盖了前三行，但缺少第四行。所以它在 R2 有帮助（六个基准全部提升，+1.78 至 +3.90），到 R5 却有害；而在相同预算下，演化后的原则平均高出 6.77（见 W1）。正是原则演化让收益得以持续。

### 发布前待核对

- [ ] **W1 对照条件只差一个因素**：正文写的是"同一 R5 检查点、同一流程、同一预算，区别只在原则和驱动课程的反馈"。需要确认 Exp 2 的 C、D 两组分配动作和预算一致，Exp 1 三组的原则相同、预算一致（与 pUjh W1 的核对项相同）。
- [ ] **W1 缺少"原则和课程都固定"这一格**：jcb6 要求的第一组（原则固定 + 课程固定）论文里没有直接对应。正文用"固定原则在 R2 有帮助、R5 有害"来回答"高质量合成数据是否足够"。如果他追问，可以补一句承诺在修订版补充；算力允许的话也可以直接补跑一轮。
- [ ] **W1 "过时反馈"不等于"固定课程"**：表中"只有原则演化"一行用的是过时反馈驱动的课程，即课程没有对准当前学习者，而不是完全不调整的课程。正文写的是 "stale (R2 / R3)"，如实标明了这一点。
- [ ] **Q1 原始数据的组成**：Q1 用支持数据池的组成（Figure 10）解释退化。需要确认 D.3 中约 70 万条原始数据和支持数据池来自同一批数据源。支持数据池 2D 和 3D 合计约 47.5 万条记录，70 万这个数是怎么来的（例如一张图对应多条问答）？
- [ ] **Q1 SLAKE 的证据（可选）**：正文只写了"与降幅最大的是答案简短的 SLAKE 相吻合"，属于观察加推断。如果能看一下 Qwen3+Raw 在 SLAKE 上的输出，例如平均输出长度，或描述式回答的比例，可以补一个硬数字。

### 论据出处

| 正文说法 | 出处（论文印刷页码） |
|---|---|
| 只有课程自适应：R5 固定原则，平均 −5.27，0/6 | Table 8 条件 C（p.26），六个基准逐项取平均 |
| 只有原则演化：R5 演化原则 + R2/R3 过时反馈，平均 −2.65 / −2.78，1/6 / 0/6 | Table 7（p.25） |
| CoEvoMed：R5 演化原则 + 当前反馈，平均 +1.50，6/6 | Table 7 R5 反馈行 = Table 8 条件 D |
| R2 固定原则 +3.09，6/6 | Table 8 条件 A |
| 演化原则比固定原则平均高 6.77（+3.33 至 +10.12） | Table 8 条件 D 减 C |
| 当前反馈比过时反馈高 4.15 / 4.28 | Table 7 |
| Q1：2D 支持数据 58.3% 是图像描述（PMC-OA 79,858 + Quilt-1M 49,022 + ROCO 22,463，共 259,767 条） | Figure 10（p.22） |
| Q1：原始数据包括图像说明、分类标签、报告，需转换为事实 | 附录 C.3（p.22） |
| Q1：原始数据训练后四个 VQA 基准的降幅：PMC-VQA −8.62、VQA-RAD −13.75、SLAKE −26.69、PathVQA −6.83 | Table 9（p.26） |
| Q1：核验器检查事实一致性、视觉依赖性、有效性和重复 | §4.1（p.5） |
| Q1：CoEvoMed 从原始原则 Σ0 起步 | Algorithm 1 输入（p.16） |
| Q1：原始数据训练"without supervision reconstruction or adaptive curriculum allocation" | 附录 D.3（p.26）原文 |
| Q1：构建原则定义问题意图，指导回答如何依据医学证据 | 摘要；§3（p.3） |
| Q1：规划器把预算分配给薄弱能力和近期退化的能力 | §4.2（p.5） |
| Q1：修订智能体根据残余错误修订原则 | §4.1、§4.3（p.5–6） |
| Q1：CoEvoMed 用更少的样本，SLAKE 达到 91.60 | Table 9（p.26） |
| Q1：R2 原始原则六个基准 +1.78 至 +3.90；R5 六个基准全部下降 | Table 8 条件 A、C |

---

## Reviewer 2Nuw

评分 2（弱拒绝）· 信心 4 · 表述 3 · 信息价值 2 · 可靠性 2

### 进度与字符预算

| 条目 | 内容 | 预算 | 当前 | 状态 |
|---|---|---:|---:|---|
| 开头 | 说明 Q1–Q4 同时回应 W1–W2 | ~50 | 46 | 草稿完成（可删） |
| Q1 | 分别确立贡献、PPO、原始数据、选择标准 | ~2,250 | 2,441 | 草稿完成（PPO 日志数据待填） |
| Q2 | 数据泄漏；R7 的选择 | ~1,600 | 1,602 | 草稿完成（F_e、移除数量、患者层面待填） |
| Q3 | 独立运行次数与置信区间；CURE-4B；32B 不如 8B | ~1,180 | 1,183 | 草稿完成（运行次数、置信区间、CURE-4B 原因待填） |
| Q4 | 复杂推理基准 | ~700 | — | 待写 |
| **合计** | | **≤ 5,000** | **5,278** | |

W1、W2 不单独回答（与 Q1–Q4 高度重合）。

字符空间：加入 Q3 后合计 5,278，已超出 5,000。Q4 写完后统一压缩，主要压缩 Q1（约 2,440 字符）和 Q2（约 1,600 字符）。对应关系：W1 → Q1；W2 的复杂推理 → Q4；W2 的重复运行、置信区间、IU-Xray 提升幅度、32B 不如 8B → Q3。

W1 中有三点 Q1 没有直接覆盖，如果 2Nuw 在讨论中追问再补：(1) 单独去掉核验器的影响；(2) 额外资源（教师模型调用量、成本）的影响，附录 F.3 写明这些都有记录；(3) 收益归到单条原则上的分析，可以利用附录 A 所说的"样本与原则版本相关联"的记录来做。

### 英文正文（发布用）

```markdown
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

**Q3 (Runs and intervals; CURE-4B; 32B on IU-Xray).** *Runs and intervals.* Our protocol fixes metrics, matching rules, and decoding before any comparison and reports case-level counts (App. C.4). The main results come from [k] training run(s) per scale; paired bootstrap 95% CIs over test cases for CoEvoMed-8B minus Hulu-Med-7B are [PMC-VQA …, VQA-RAD …, SLAKE …, PathVQA …, MIMIC-CXR …, IU-Xray …]. Stability is further supported by independent runs of the full pipeline on two other learners, each improving substantially over its base (Gemma-3-4B: +22.39 VQA-RAD, +16.23 MIMIC-CXR; InternVL3-9B: +20.40, +13.28; Figure 5, App. C.5).

*CURE-4B.* [reason].

*32B on IU-Xray.* The strongest baseline family shows the same pattern: Hulu-Med-32B (62.40) trails Hulu-Med-7B (67.30) on IU-Xray, so the reversal reflects this 590-case benchmark rather than our method. At matched scale, CoEvoMed-32B exceeds Hulu-Med-32B by +2.68, and it exceeds CoEvoMed-8B on the other five benchmarks (+0.20 to +2.25; Table 1, Figure 3). Beyond the 0.92 RaTEScore margin, CoEvoMed-8B also leads Hulu-Med-7B on IU-Xray in six of eight lexical metrics, by up to +7.5 ROUGE-2 and +3.7 BLEU-4 (Figure 8).
```

### 中文译文（不发布）

下面对 Q1–Q4 的回答同时回应了 W1–W2。

**Q1（分别确立贡献、PPO、原始数据、选择标准）** 我们依次回答这四个部分。

*原则演化与自适应课程。* 附录 D 的对照实验使用相同的教师模型、支持数据池和每轮预算，并从同一个 R5 检查点出发（六个基准上的平均变化；Table 7–8）：

| 条件 | 原则 | 课程所用反馈 | 平均变化 | 提升的基准数 |
|---|---|---|---|---|
| 只有课程自适应 | 固定（原始） | 当前 | −5.27 | 0/6 |
| 只有原则演化 | 演化后 | 过时（R2 / R3） | −2.65 / −2.78 | 1/6 / 0/6 |
| CoEvoMed | 演化后 | 当前 | **+1.50** | **6/6** |

*PPO。* 课程分配是一个效果有延迟的序贯决策：现在花在"保留"上的预算，保护的是后续轮次的收益。因此，规划器优化的是累计的带符号验证收益（式 5，附录 F.4），而不是一条贪心规则。日志显示，这个策略会根据学习者的状态做出不同选择，而不是重复同一条规则：R1–R7 中它依次选择了 [动作序列]。例如，定位能力在 R4 出现退化后（Figure 6），它在 R[x] 转向了 [动作]，定位能力到 R6 回升至 62.10。

*原始数据退化。* 附录 D.3 是在"没有监督重构，也没有自适应课程分配"的条件下用原始数据训练的，退化可以由这些数据的四个特点来解释。第一，与任务不对齐：2D 记录中 58.3% 是图像描述，其余大多是由标签转换的条目或报告（Figure 10，附录 C.3），模型学会的是描述或贴标签，而不是回答问题，这在答案简短的 SLAKE 上最明显（−26.69）。此外，这些数据没有经过事实一致性和视觉依赖性的核查，没有针对学习者的薄弱能力，也不会随学习者的变化而调整。CoEvoMed 分别通过构建原则与构建器、核验器、规划器和修订智能体处理这四个特点（第 4.1–4.3 节），同类数据源经过 CoEvoMed 处理后，用更少的样本就让 SLAKE 达到 91.60（Table 9）。

*选择标准与学习收益的关系。* 可用产出率、配对覆盖率和语义审查在部署之前筛查监督数据的质量；之后的学习收益由闭环本身检验：论文写明"学习者的反应在后续训练轮次中评估"（附录 B），任何能力单元净修复不为正的原则都会被再次修订（第 4.3 节）。被选中的原则在 R5 让六个基准全部提升，而原始原则让六个基准全部下降（平均高出 6.77；Table 8）。

**Q2（数据重叠；R7 的选择）** *数据重叠。* 我们从一开始就把防止泄漏当作设计约束。论文把支持数据、内部验证集和外部测试集严格分开（第 1 节；附录 C.6"反馈来源与独立性"），提交的代码也强制执行了这一点：只要任何一条支持、验证或外部记录与其他划分共享记录 ID、图像路径、解码后 RGB 的 SHA-256 哈希或检查（study）ID，程序就拒绝启动；每条记录都必须带有其原始数据划分的来源信息；每个训练任务在执行前都会再次与留出集的身份清单比对（coevomed/data.py）。此外，每条支持数据的问题、答案或报告文本都与全部验证集和外部测试集做了泄漏查询。PubMedVision-IU 与 IU-Xray 之间按同样的方式做了筛查（移除了 [n] 条）。[患者层面：见核对清单。]

*R7。* 我们同样在论文中设置了两道防止检查点选择偏差的保障：六个基准共用同一个检查点，以"保持单个学习者的整体能力画像"；并报告全部十轮，"包括后期的性能下降"（附录 C.4，Figure 7）。R7 是按外部基准上跨任务的整体均衡性一次性选定的（第 5.2 节）；训练、课程分配和原则修订从不使用外部基准（附录 A、C.6）。按照预先定义的内部标准，即规划器优化的验证目标 F_e（附录 F.4），选出的是 [R7，同一个检查点 / R[x]，其分数为……]。即使不做任何选择，结果依然成立：最后一轮 R10 在 SLAKE（88.67 对 86.80）和 PathVQA（67.25 对 65.60）上仍超过 Hulu-Med-7B。

**Q3（独立运行与置信区间；CURE-4B；32B 在 IU-Xray 上的表现）** *独立运行与置信区间。* 我们的评测协议在任何比较之前就固定了评测指标、匹配规则和解码设置，并报告样本层面的计数（附录 C.4）。主要结果来自每个规模 [k] 次训练运行；CoEvoMed-8B 相对 Hulu-Med-7B 的差值，在测试样本上做配对 bootstrap 得到的 95% 置信区间为 [PMC-VQA …，VQA-RAD …，SLAKE …，PathVQA …，MIMIC-CXR …，IU-Xray …]。此外，完整流程在另外两个学习者模型上的独立运行也支持结果的稳定性，两者相对各自的基础模型都有大幅提升（Gemma-3-4B：VQA-RAD +22.39，MIMIC-CXR +16.23；InternVL3-9B：+20.40、+13.28；Figure 5，附录 C.5）。

*CURE-4B。* [原因]。

*32B 在 IU-Xray 上的表现。* 最强的基线模型系列也呈现同样的规律：在 IU-Xray 上，Hulu-Med-32B（62.40）低于 Hulu-Med-7B（67.30），因此这种反转反映的是这个只有 590 个样本的基准本身的特点，而不是我们方法的问题。在相同规模下，CoEvoMed-32B 比 Hulu-Med-32B 高 2.68；在另外五个基准上，CoEvoMed-32B 都高于 CoEvoMed-8B（+0.20 至 +2.25；Table 1，Figure 3）。除了 RaTEScore 上 0.92 的领先，CoEvoMed-8B 在 IU-Xray 的八个词汇层面指标中有六个领先 Hulu-Med-7B，最多在 ROUGE-2 上领先 7.5、在 BLEU-4 上领先 3.7（Figure 8）。

### 发布前待核对

- [ ] **Q1 PPO 占位符**：已决定用日志中 PPO 每一轮选择的动作来证明（不补跑实验）。需要从日志填入：`[action sequence]`，即 R1–R7 每轮的动作；`[action]` 和 `R[x]`，即定位能力在 R4 退化后，PPO 在哪一轮换成了什么动作。按设计，修复（repair）部分负责薄弱能力和近期退化，所以预期是 repair-heavy 或 weakness-focused。如果日志里看不到这样的对应，就换一个能体现"随状态变化"的例子，或者只保留动作序列那一句。
- [ ] **Q1 对照条件**：正文写的是"相同教师、支持数据池、每轮预算，同一 R5 检查点"，与 pUjh W1、jcb6 W1 是同一个待确认项。
- [ ] **Q1 原始数据的组成**：与 jcb6 Q1 相同，需要确认 D.3 中约 70 万条原始数据和支持数据池来自同一批数据源。

- [x] **Q2 R7 的选择（已确认事实）**：R7 是根据外部基准的整体均衡性选出的。论文 §5.2 和附录 C.4 写了"为什么选 R7"，但没有写明依据的是外部基准。Q2 已如实写明。
- [ ] **Q2 F_e 计算**：用日志算出每一轮内部验证集上的 F_e（附录 F.4：VQA 与报告两类任务验证分数的等权平均，即规划器优化的目标），看它选出哪一轮。选出 R7 时，占位符改为 "R7, the same checkpoint"；选出其他轮次时，写明轮次和该轮在外部基准上的分数。
- [x] **Q2 去重的实际做法（已确认事实）**：与内部验证集和全部外部测试集比对，依据样本 ID、图像路径、像素哈希，并对每条样本的文本做泄漏查询；PubMedVision-IU 与 IU-Xray 专门做过。
- [ ] **Q2 移除数量 `[n]`**：PubMedVision-IU 与 IU-Xray 筛查后移除（或命中）了多少条？如果是 0，改为 "and no overlap was found"。
- [ ] **Q2 患者层面**：2Nuw 也问了患者层面。提交的代码在有 study ID 时会按 study ID 比对（`identity_tokens` 中的 `study` 字段），像素哈希和路径覆盖图像层面，文本查询覆盖检查层面；代码里没有患者 ID 的比对。据我所知 IU-Xray（Open-i）没有公开患者 ID，无法在患者层面匹配。如果确实如此，占位符改为 "IU-Xray releases no patient identifiers, so matching there is at study and image level"。请确认你们是否做过患者层面的匹配。
- [ ] **Q2 代码描述核对**：正文对代码行为的描述（共享记录 ID、图像路径、RGB 哈希或 study ID 即拒绝启动；必须有原始划分来源；训练任务再次比对）来自提交的 `coevomed/data.py`（`validate_partitions`、`validate_evidence_identity`、`validate_exclusions`）。请确认正式实验用的是同一套检查逻辑。
- [ ] **Q2 定稿时补进论文**：附录 C.3 目前只写了与验证集的重叠检查。定稿时补上与外部测试集的筛查、文本泄漏查询，以及 R7 依据外部基准选出这一点。
- [ ] **Q3 运行次数 `[k]`**：主实验每个规模跑了几次？如果只有一次，如实写 "a single training run per scale"，并依靠配对 bootstrap 置信区间和跨骨干模型的独立运行来说明稳定性。
- [ ] **Q3 置信区间**：配对 bootstrap 需要 CoEvoMed-8B 和 Hulu-Med-7B 在六个测试集上逐条样本的预测结果（Hulu-Med-7B 需要是你们自己评测的）。提供后我写脚本计算（10,000 次重采样，报告差值的 95% 置信区间）。如果 Hulu-Med-7B 的分数是引用的，就改为报告 CoEvoMed-8B 自身得分的置信区间。
- [ ] **Q3 CURE-4B 的原因 `[reason]`**：IU-Xray 的比较中为什么没有 CURE-4B？例如原文没有报告 IU-Xray、没有公开权重，或训练数据包含 IU-Xray。图 3 标题写的是 "CURE-4B uses AGRG-29 + GRG"，请说明它的 MIMIC-CXR 分数是自己评测的还是引用的。
- [ ] **Q3 32B 的说法**：正文把 32B 在 IU-Xray 上低于 8B 归因于基准本身（Hulu-Med 同样如此）。如果你知道其他原因，例如 32B 的训练轮数或预算不同，请告诉我，必要时补充。

### Q2 泄漏分析清单

来源：论文 Figure 10（p.22）、Table 5（p.23）、Table 3–4（p.19）。"重点比对"一栏是我根据各数据集的公开构建方式判断的同源风险，标"需确认"的请以原数据集说明为准。

**支持数据（合成数据的来源）**

| 支持数据 | 记录数 | 内容 | 重点比对的评测集 | 同源风险 |
|---|---:|---|---|---|
| PMC-OA | 79,858 | PubMed Central 论文配图与说明 | PMC-VQA | **高**：PMC-VQA 由 PMC-OA 的图文对构建 |
| Quilt-1M | 49,022 | 病理图像与文本（YouTube 教学视频） | PathVQA | 低 |
| OmniMedVQA | 44,911 | 由 73 个公开数据集构建的选择题 | SLAKE、VQA-RAD | 中：子数据集可能与 SLAKE 的图像来源重合（需确认） |
| Med-MAT | 28,154 | 由 106 个公开数据集转换的选择题 | SLAKE、VQA-RAD | 中：同上（需确认） |
| ROCO | 22,463 | PubMed Central 放射图像与说明 | PMC-VQA | **高**：同为 PubMed Central 配图 |
| CheXpert | 12,000 | 胸片与分类标签（Stanford） | MIMIC-CXR、IU-Xray | 低：不同机构 |
| LLaVA-Med | 9,173 | PubMed Central 图像的指令对话 | PMC-VQA | **高**：同为 PubMed Central 配图 |
| TCGA-CRC | 5,000 | 结直肠癌病理切片 | PathVQA | 低 |
| ReXGradient-160K | 4,122 | 胸片与报告（多机构） | MIMIC-CXR、IU-Xray | 低：不同机构（需确认其来源机构） |
| PubMedVision-IU 子集 | 3,129 | 来自 IU-Xray（Open-i）的胸片 | **IU-Xray** | **高**：同一数据集，审稿人点名 |
| MedTrinity BHX | 1,935 | 头部 CT 出血框标注（基于 CQ500） | SLAKE（头部影像） | 低 |
| AbdomenAtlas1.0Mini | 36,064 | 腹部 CT 分割（汇集多个公开数据集） | **AMOS-MM** | **高**：汇集的公开数据集可能包含 AMOS（需确认） |
| CT-RATE | 69,891 问答 + 958 报告 | 胸部 CT 与报告 | **3D-RAD** | **高**：3D-RAD 基于 CT-RATE 构建 |
| RadGenome-ChestCT | 52,318 | 基于 CT-RATE 的区域标注 | **3D-RAD** | **高**：同样源自 CT-RATE |
| TotalSegmentator | 51,056 | 全身 CT 分割（Basel 医院） | AMOS-MM、M3D-VQA | 低 |
| M3D-Cap | 5,370 报告 | Radiopaedia 3D 影像与报告 | **M3D-VQA** | **高**：M3D-VQA 基于 M3D 数据构建 |

合计：2D 259,767 条记录，3D 215,657 条记录。

**需要比对的评测集**

| 类别 | 数据集 | 规模 |
|---|---|---|
| 2D 外部测试集 | VQA-RAD、SLAKE、PMC-VQA、PathVQA、MIMIC-CXR、IU-Xray | 451、1,061、33,430、6,761、2,343、590 条 |
| 3D 外部测试集 | M3D-VQA（测试划分）、3D-RAD（测试划分）、AMOS-MM（验证划分） | 13,791 条 / 2,000 序列；4,692 条 / 2,354 序列；400 条 |
| 内部验证集 | 按任务分层抽取，每个子集约 500 条（附录 C.3） | — |

另外两处也要一并筛查：
1. **回放数据 Re**：每轮训练都会混入，同样不能与验证集和外部测试集重叠。
2. **内部验证集与外部测试集之间**：验证集若取自这些基准的训练或验证划分，也要确认和测试划分不重叠。代码中的 `validate_partitions` 包含这一项检查。

建议的统计口径：对每一对"支持数据 × 评测集"，分别报告样本 ID、图像路径、RGB 哈希、study ID 和文本这几个层面的命中数与移除数。高风险的几对（PubMedVision-IU × IU-Xray，PMC-OA、ROCO、LLaVA-Med × PMC-VQA，CT-RATE、RadGenome-ChestCT × 3D-RAD，M3D-Cap × M3D-VQA，AbdomenAtlas × AMOS-MM）可以在回复里单独列出数字。

### 论据出处

| 正文说法 | 出处（论文印刷页码） |
|---|---|
| 分解表三行 | Table 7（p.25）、Table 8（p.26），同 jcb6 W1 |
| 规划器优化累计带符号验证收益 | 式 5、式 8（p.4–5）；附录 F.4（p.29） |
| 原始数据训练"without supervision reconstruction or adaptive curriculum allocation" | 附录 D.3（p.26） |
| 2D 支持数据 58.3% 是图像描述 | Figure 10（p.22） |
| SLAKE 降幅 −26.69；CoEvoMed 用更少样本达到 91.60 | Table 9（p.26） |
| 构建原则与构建器、核验器、规划器、修订智能体的职责 | §4.1–4.3（p.5–6） |
| 选择标准：可用产出率、配对覆盖率、语义审查 | §4.3（p.6）；附录 B（p.18） |
| "Selection uses paired supervision comparison, with learner responses assessed in subsequent training rounds." | 附录 B（p.18）原文 |
| 净修复不为正的原则会被纳入修订 | §4.3（p.6）；附录 A（p.16） |
| 演化原则比原始原则在 R5 平均高 6.77 | Table 8 条件 D 减 C |
| 定位能力 R4 退化到 56.16，R6 回升到 62.10 | Figure 6（p.9） |
| 修复部分针对薄弱能力和近期退化，保留部分维持已习得能力 | §4.2（p.5） |
| Q2：去重依据样本 ID、图像路径和 RGB 像素内容；检查与验证集的重叠 | 附录 C.3（p.22）；与外部测试集的比对和文本查询为作者确认的实际做法，论文未写 |
| Q2：R7 按跨任务整体均衡性选定 | §5.2（p.7）；附录 C.4（p.24） |
| Q2：外部基准不参与训练、课程和原则更新 | 附录 A（p.16）；附录 C.6（p.25） |
| Q2：F_e 定义 | 附录 F.4（p.29） |
| Q3：评测协议事先固定指标、匹配规则和解码设置，报告样本计数 | 附录 C.4（p.24） |
| Q3：Gemma-3-4B +22.39 / +16.23；InternVL3-9B +20.40 / +13.28 | Figure 5（p.9）；附录 C.5（p.24） |
| Q3：IU-Xray RaTEScore：CoEvoMed-8B 68.22、Hulu-Med-7B 67.30、CoEvoMed-32B 65.08、Hulu-Med-32B 62.40 | Figure 3（p.7） |
| Q3：32B 相对 8B：PMC-VQA +2.25、VQA-RAD +0.23、SLAKE +1.00、PathVQA +0.20、MIMIC-CXR +0.71 | Table 1（p.6）；Figure 3（p.7） |
| Q3：IU-Xray 词汇指标，CoEvoMed-8B 对 Hulu-Med-7B：METEOR +2.8、BLEU-1 −1.0、BLEU-2 +1.1、BLEU-3 +2.8、BLEU-4 +3.7、ROUGE-1 +5.2、ROUGE-2 +7.5、ROUGE-L −0.8 | Figure 8（p.20） |
| Q3：IU-Xray 测试集 590 个样本 | Table 3（p.19） |
| Q2：支持数据、验证集、外部基准三者分离 | §1（p.2）；附录 C.6（p.25）"Feedback provenance and independence" |
| Q2：代码在划分间重叠时拒绝启动；必须有 RGB 哈希和原始划分来源；训练任务再次比对 | 补充材料代码 `coevomed/data.py`：`validate_partitions`、`validate_evidence_identity`、`validate_exclusions`、`identity_tokens` |
| Q2："preserves the joint capability profile of a single learner"；"including later performance declines" | 附录 C.4（p.24） |
| Q2：R10 SLAKE 88.67、PathVQA 67.25；Hulu-Med-7B 86.80、65.60 | Figure 7（p.9）；Table 1（p.6） |
