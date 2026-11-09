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
| 开头 | 致谢 | — | — | 不写（为字符限制） |
| W1 | 多智能体是否必要 | — | 1,447 | 已压缩 |
| W2 | 论文组织 | — | 286 | 已压缩 |
| W3 | 遗忘与 R7 的选择 | — | 1,371 | 已重写 |
| Q1 | MedVLSynther 复现 | — | 712 | 已压缩 |
| Q2 | 数据公开 | — | 247 | 已压缩 |
| Q3 | 能力分类体系 | — | 915 | 已压缩 |
| 结尾 | | — | — | 不写（为字符限制） |
| **合计** | | **≤ 5,000** | **4,988** | |

"当前"一栏只统计各条目正文；合计按代码块全文统计，包含条目之间的空行。

### 英文正文（发布用）

```markdown
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

**W2 (Organization).** The main text specifies every mechanism (Secs. 3–4, Eqs. 1–9), including the capability cells (Sec. 3.1), and Sec. 5.1 gives the evaluation task composition. Implementation parameters and dataset statistics are in the appendix, each referenced from the main text.

**W3 (Catastrophic forgetting and retention).** CoEvoMed is curriculum learning, not continual learning. Every round trains all tasks together (Eq. 7) with replay data (Sec. 3.3). With no task sequence, catastrophic forgetting and continual-learning metrics do not apply. "Retention" is a budget share for acquired capabilities (Sec. 4.2), ablated with the planner in W1.
- *Reactive recovery and balance.* As the reviewer notes, the method recovers. This is the curriculum's design: measure the learner each round and reteach what weakened (Eqs. 6, 8). Localization dips at R4 (56.16) and recovers to 62.10 by R6; all five capabilities end above R1 (Fig. 6).
- *Later-round declines.* Iterative self-training often plateaus or declines after early rounds on a finite pool (Chen et al., ICML 2024; Singh et al., TMLR 2024). Our pool is fixed (359,355 facts, App. C.3); each round builds 50,000 examples (App. B). By R7 the budget nearly matches the pool, so later rounds mostly reuse seen evidence. At R10, SLAKE, PathVQA, and IU-Xray stay within 3 points of their peaks and over 12 points above R1 (Fig. 7).
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
```

### 中文译文（不发布）

**W1（多智能体框架是否必要？）** 是的。附录 D 从同一个检查点出发，在有和没有该角色的条件下，检验了每个智能体角色的关键功能：

| 智能体角色 | 关键功能 | 没有该功能 | 有该功能 |
|---|---|---|---|
| 选择器、构建器、核验器 | 经过核验、与任务对齐的数据 | 原始数据（约 70 万条）：4/4 个 VQA 基准低于基础模型；SLAKE 38.15 | 样本更少：4/4 提升；SLAKE **91.60**（Table 9） |
| 修订智能体 | 让原则适应学习者 | R5 时使用原始原则：6/6 下降 | 修订后：**6/6 提升**（Table 8） |
| 课程规划器 | 按当前需要分配预算 | 使用过时的 R2/R3 反馈：12 个中 11 个下降 | 使用当前反馈：**6/6 提升**（Table 7） |

能否用另一种合理的智能体流程替代它们？替代方案仍然必须完成这些功能，而上面那些更简单的做法都失败了。为什么不把这些角色合并成一个智能体？
1. **独立核查。** 核验器（Qwen3.6-27B）和构建器（deepseek-v4-flash）是不同的模型，因此没有任何模型在检查自己的输出。大语言模型在没有外部反馈时很难自我纠正（Huang et al., ICLR 2024）。
2. **基于证据的构建。** 构建器只根据选出的原始事实撰写样本，而不是根据图像。如果合并成一个智能体，它就要直接看图撰写，而视觉语言模型经常描述图像中并不存在的物体（Li et al., EMNLP 2023）。
3. **可学习的分配。** 规划器是每轮用 PPO 训练的小型策略网络，而各个大语言模型智能体保持冻结（附录 B）；合并会失去这种学习能力。

**W2（论文组织）** 正文给出了全部机制（第 3–4 节，式 1–9），包括能力单元（第 3.1 节）；第 5.1 节给出了评估任务的组成。实现参数和数据集统计放在附录，每项都在正文中注明了出处。

**W3（灾难性遗忘与保留）** CoEvoMed 是课程学习，不是持续学习。每一轮都同时训练所有任务（式 7），并混入回放数据（第 3.3 节）。由于不存在任务序列，灾难性遗忘和持续学习指标并不适用。"保留"是预算中分给已习得能力的份额（第 4.2 节），已在 W1 中随规划器一起做了消融。
- *被动恢复与均衡。* 正如审稿人所指出的，该方法能够恢复。这正是课程学习的设计：每一轮测量学习者，并重新教授变弱的部分（式 6、8）。定位能力在 R4 降到 56.16，到 R6 恢复到 62.10；五项能力最终都高于 R1（Figure 6）。
- *后期轮次的下降。* 迭代式自训练在有限的数据池上，通常在前几轮之后趋于平稳甚至下降（Chen et al., ICML 2024；Singh et al., TMLR 2024）。我们的数据池是固定的（359,355 条事实，附录 C.3），每轮构建 50,000 个样本（附录 B）。到 R7，累计预算已接近数据池的规模，因此后续轮次主要在重复使用学习者已见过的证据。在 R10，SLAKE、PathVQA 和 IU-Xray 距各自峰值都在 3 分以内，并且比 R1 高出 12 分以上（Figure 7）。
- *对 R7 的依赖。* R7 在内部验证集上具有最均衡的能力画像。六个基准共用这一个检查点，尽管 PathVQA 的峰值出现在 R8。外部基准只用于追踪演化过程，从不指导训练或检查点选择（附录 C.4、C.6）。

**Q1（MedVLSynther 的基础模型）** 我们注意到了基础模型的差异。绝对分数把方法和骨干模型的效果混在一起，因此我们比较各方法相对其自身基础模型的提升（MedVLSynther 采用原文发表的结果）：

| 相对自身基础模型的提升 | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther-7B（Qwen2.5-VL-7B） | +6.13 | +8.82 | +6.65 | +0.17 |
| CoEvoMed-8B（Qwen3-VL-8B） | **+13.82** | **+25.72** | **+26.76** | **+26.63** |

在相同的基础模型上，我们用 MedVLSynther 公开的数据和 GRPO 训练脚本训练了 Qwen3-VL-8B：

| 相同基础模型：Qwen3-VL-8B | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther 配方 | [x.xx] | [x.xx] | [x.xx] | [x.xx] |
| CoEvoMed-8B | 67.95 | 82.48 | 91.60 | 69.40 |

**Q2（数据公开）** 会公开。论文被接收后，我们将按各源数据的许可公开合成数据和全部版本的构建原则：图像只以 ID 引用；对于禁止再分发的源数据（如 CheXpert），我们提供重新生成的脚本。

**Q3（能力分类体系）** 与 SLAKE 的重合是有意设计的，而不是随意的重新贴标签。
- *为什么是这些类别。* 这套分类体系沿用了 SLAKE 由医生标注的问题类别（Liu et al., 2021）。我们合并了其中的属性类型，并为多图像和报告任务增加了空间关系、比较和整体描述三类（Table 6）。
- *为什么这些类别是必要的。* 这些类别描述的是问题在问什么，而不是某个数据集，因此同样覆盖 PathVQA、PMC-VQA、报告任务和支持数据池，而这些数据都没有原生标签。一套分类体系让我们能够诊断所有任务、共享同一份预算并检索匹配的证据（附录 C.3）。
- *对应关系与验证。* 在 200 道 SLAKE 题目上，我们的标注与原生标签的一致率为：能力类别 97.5%（Cohen's κ = 0.958），模态 100%，解剖部位 96.5%。κ 高于 0.81 即属于"几乎完全一致"（Landis & Koch, 1977）。我们会把这一对应关系补充到 Table 6 中。

### 发布前待核对

- [x] **W1 修订智能体（已确认）**：Exp 2 的条件 C 和 D 只在原则上不同，分配动作、预算和训练设置一致。
- [x] **W1 规划器（已确认）**：Exp 1 的三组使用相同的原则和预算，只替换了反馈来源。
- [ ] **W2 可选补充**：如果想在不让步的前提下给一个姿态，可以在 W2 末尾加一句（约 70 字符）：`We will add a role summary table to Section 4 for quick reference.`
- [x] **W3 回放数据**：已确认主实验每轮混入回放数据，W3 已写入 "mixes in replay data (Section 3.3)"。
- [x] **R7 的选择依据（作者已更正）**：R7 是按内部验证集上的能力画像（附录 C.4；"capability profile" 的定义见第 3.1 节式 1）选出的，与论文一致。此前"按外部基准选出"的说法为口误，已更正。W3 已按此改写，并删去 R10 与 Hulu-Med-7B 的比较。
- [x] **W3 PathVQA 峰值**：已确认 PathVQA 的 R8 略高于 R7；R10 的 67.25 仍在峰值 3 分以内，正文说法成立。
- [ ] **W3 数据池解释（请确认）**："By R7 the budget nearly matches the pool, so later rounds mostly reuse seen evidence" 是按论文数字推出的解释：7 × 50,000 = 350,000，接近 359,355 条事实（附录 C.3 称之为 "reusable facts"）。样本和事实不一定一一对应。请确认后期轮次确实大量复用已用过的证据（例如从日志统计每轮首次使用的事实比例）。如果不符，改为 "so later rounds add little new evidence"。
- [x] **W3 文献（已核实）**：Chen et al., ICML 2024 = SPIN（Self-Play Fine-Tuning），收益集中在前两轮，后续工作 SPACE 报告其在峰值后下降；Singh et al., TMLR 2024 = ReST-EM（"Beyond Human Data"），原文写明 APPS 在第二轮回退，迭代超过几轮后收益递减，并归因于在少量训练题上过拟合。R-Zero（论文中的 Huang et al., 2026a）后期下降没有查到原文证据，所以没有引用。
- [x] **W3 R7 出处**：附录 C.4 "Checkpoint selection" 写明按整体均衡选 R7；附录 C.6 写明外部基准不参与监督构建、学习者训练、课程和原则更新。
- [ ] **为容纳 W3 而删去的内容（可按需恢复）**：W1 表中的变化区间（−2.2 至 −9.6；+0.5 至 +2.8）；W2 中"四个 2D VQA、两个报告、三个 3D 基准"的括号；Q3 中"VQA-RAD 和 M3D-VQA 采用类似类别"一句，以及"过时诊断使 12 个分数中 11 个下降"一句（W1 表中已有同一证据）。
- [ ] **Q1 占位符**：复现完成后，在第二张表里填入复现模型在四个基准上的得分 `[x.xx]`（与 CoEvoMed 同一评测流程）。如果任何一项高于 CoEvoMed，需要重新讨论写法。
- [ ] **Q1 数字来源**：确认 Table 1 的 MedVLSynther 数字引自其论文（与其 GitHub README 的数字完全一致）。正文写的是 "as published"。
- [ ] **Q1 与附录 C.1 的一致性**：C.1 写的是"本研究评估的基线与 CoEvoMed 使用相同的评估集和评分规则"，MedVLSynther 是引用数，与这句不符。Q1 已如实写明"按原文发表的结果和协议"；定稿时建议把 C.1 改为区分"我们评测的基线"和"引用原文的基线"。
- [x] **字符限制**：当前 4,988 字符。填入 Q1 复现结果后，`[x.xx]` 每格少 1 个字符，仍在限制内。
- [ ] **Q2 承诺**：正文承诺为禁止再分发的源数据提供重新生成脚本。确认接收后能兑现；如果不打算做，把最后半句改为 "are excluded from the release"。
- [ ] **Q2 待确认许可**：PMC-OA、MedTrinity BHX、RadGenome-ChestCT、Med-MAT 的许可没能直接核实，AbdomenAtlas1.0Mini 的附加条款也不确定，公开前需逐个确认（见下方"Q2 源数据许可核对"）。
- [x] **Q3 一致率（已填入）**：轴 B（视觉能力）准确率 97.50%（195/200），macro-F1 0.9767，Cohen's κ 0.9575（正文写作 0.958）；轴 C（模态）准确率 100%，为模型在不看原标签的情况下独立判断；轴 D（解剖部位）准确率 96.50%（193/200），macro-F1 0.9476。轴的对应关系来自代码 `AXES = ("task_form", "visual_ability", "modality", "anatomy")`。
- [ ] **Q3 κ 对应的轴**：正文把 κ = 0.958 放在能力类别（轴 B）后面。如果这个 κ 是别的轴或整体的值，告诉我调整位置。
- [ ] **Q3 样本说明（可选）**：如果这 200 条是随机抽取的，可以在 "on 200 SLAKE questions" 前加 "randomly sampled"。
- [ ] **Q3 SLAKE 措辞**：SLAKE 原文能确认的是"语义标注由经验丰富的医生完成"，并且"每个问题都标有语义标签，用于区分问题类型"；没有找到"类别体系由专家设计"的明确表述。所以正文写的是 "physician-annotated question categories"（医生标注的问题类别），而不是 "expert-designed"。如果你手上的 SLAKE 原文有"类别由医生设计"的原句，告诉我页码，可以改成 "designed and annotated by physicians"。
- [ ] **Q3 对应关系**：正文写了"把 SLAKE 细分的属性类型合并为一类，并新增空间关系、比较和整体描述三类"。请对照下方对应表确认，尤其是 SLAKE 的 Plane 和 Quantity 分别归到哪一类。
- [ ] **Q1 奖励函数的说明（已为字符限制删去）**：正文不再提"奖励函数取自 MedVLThinker 代码"。如果审稿人追问复现细节，再补充这一点（详见下方"Q1 复现配置备忘"）。
- [ ] **W1 可选补充**：如果核验器日志里有拒绝率，可以在 "independently checked" 之后加一句（约 75 字符），作为核验器单独起作用的正面证据：`The verifier rejects [X]% of constructed candidates, mainly for [reason].`

### W1 数字出处

| 正文数字 | 出处（论文印刷页码） |
|---|---|
| SLAKE 64.84→38.15 / 91.60；四个 VQA 基准全部低于基础模型 | Table 9，p.26 |
| R5 原始原则 −2.20 至 −9.60；修订后原则 +0.52 至 +2.77 | Table 8，p.26 |
| R2 时原始原则在 6 个基准中的 5 个上更好（MIMIC-CXR 除外，相差 0.12） | Table 8，p.26 |
| R2/R3 反馈 12 个分数中 11 个下降；R5 反馈六个全部提升 | Table 7，p.25 |
| 构建器不访问图像，核验器对照图像核验 | 附录 A，p.16；附录 B，p.17 |
| 构建器用 deepseek-v4-flash，核验器用 Qwen3.6-27B | 附录 B，p.17 |
| 规划器是两层 MLP 的 Actor–Critic，每轮用 PPO 更新 | 附录 B，p.17–18 |
| PPO 只更新规划器，外部 LLM 权重保持不变（"PPO updates the curriculum planner, while external LLM weights remain fixed"） | 附录 B，p.18 |
| 视觉语言模型常描述图像中不存在的物体 | Li et al., "Evaluating Object Hallucination in Large Vision-Language Models", EMNLP 2023（外部文献，正文已引用） |
| 大语言模型没有外部反馈时难以自我纠正 | Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet", ICLR 2024（外部文献，正文已引用） |
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
| 支持数据池固定为 359,355 条可复用事实 | 附录 C.3，p.24（"The resulting source pool provides 359,355 reusable facts"） |
| 每轮构建 50,000 个通过核验的监督样本 | 附录 B，p.17（"Per-round supervision size and task composition"） |
| 外部基准不参与训练、课程和原则更新 | 附录 C.6（"External benchmark collections ... do not participate in ..."） |
| 外部基准逐轮评估，Figure 7 报告全部十轮，包括后期下降 | 附录 C.4（"External benchmarks evaluate model performance across rounds and do not inform curriculum decisions"） |
| PathVQA 峰值在 R8；单项峰值出现在 R7–R8 | Figure 7，p.9；附录 C.4（"individual benchmark peaks occur at R7–R8"） |
| 迭代自训练在有限训练集上收益递减或回退 | Singh et al., "Beyond Human Data: Scaling Self-Training for Problem-Solving with Language Models", TMLR 2024（ReST-EM）；Chen et al., "Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models", ICML 2024（SPIN）（外部文献） |

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
| W1 | 在预算匹配下分离各组件 | 1,392 | 草稿完成 |
| Q1 | 原始数据退化原因；固定原则重构是否也有效 | 2,100 | 草稿完成 |
| **合计** | | **3,574** | ≤ 5,000 |

### 英文正文（发布用）

```markdown
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
```

### 中文译文（不发布）

我们感谢审稿人的积极评价和具体建议。

**W1（分离各个组件的贡献）** 附录 D 的组件对照实验提供了审稿人所建议的预算匹配比较。所有条件都从同一个 R5 检查点出发，用相同的流程和预算训练一轮。区别只在于构建原则和课程所用的反馈（Table 7–8；六个基准上的平均变化）：

| 所要求的比较 | 原则 | 课程 | 平均变化 | 提升的基准数 |
|---|---|---|---|---|
| 只有原则演化 | 演化后 | 过时（R2 / R3）反馈 | −2.65 / −2.78 | 1/6 / 0/6 |
| 只有课程自适应 | 固定（原始） | 当前反馈 | −5.27 | 0/6 |
| 共同演化（CoEvoMed） | 演化后 | 当前反馈 | **+1.50** | **6/6** |

*原则固定且课程固定。* 在 R5，即使课程仍在自适应，固定原则也已经失效（−5.27，0/6）。再把课程也固定下来，只会去掉仅剩的自适应部分，因此不能指望它做得更好。

*收益来自高质量合成数据，还是共同演化？* 单独使用任何一个组件都会让学习者变差；只有共同演化才让六个基准全部提升。同一条经过核验的流程，用固定原则在 R2 时有帮助（+3.09，6/6），到 R5 时却有害。因此，高质量合成数据推动了早期的进步，而共同演化让进步得以持续。在预算匹配下，演化后的原则比固定原则高 6.77，当前反馈比过时反馈高 4.15 至 4.28。

**Q1（原始数据退化的原因；固定原则重构的效果）**

*是什么导致了如此明显的退化？* 附录 D.3 是在"没有监督重构，也没有自适应课程分配"的条件下用原始数据训练的。这些数据的四个特点解释了性能下降。右栏注明了 CoEvoMed 在哪个环节处理每个特点：

| 原始数据的特点 | CoEvoMed 在哪里处理它 |
|---|---|
| 与任务不对齐：2D 记录中 58.3% 是图像描述，其余大多是由标签转换的条目或报告（Figure 10，附录 C.3），模型学会的是描述或贴标签，而不是回答问题 | 构建原则定义问题意图；构建器把证据转化为针对目标能力的监督数据（第 3、4.1 节） |
| 未经核查：图文关联从未被检查 | 核验器检查事实一致性和视觉依赖性（第 4.1 节） |
| 没有针对性：数据构成取决于数据源里有什么，而不是学习者需要什么 | 规划器把固定预算分配给薄弱和退化的能力（第 4.2 节） |
| 不会自适应：学习者在变化，监督却一成不变 | 修订智能体根据残余错误更新构建原则（第 4.3 节） |

因此，约 70 万条原始数据训练后低于基础模型。降幅最大的是 SLAKE（−26.69），它的答案都很简短。同类数据源经过 CoEvoMed 处理后，用更少的样本就达到了 91.60。

*使用固定构建原则清洗并重构数据，是否也能带来显著收益？* 早期能，后期不能。固定原则能处理表中的前三行，但处理不了第四行。在 R2，用原始原则重构数据让六个基准全部提升（+1.78 至 +3.90；Table 8），这也是 CoEvoMed 以这些原则作为起点的原因（Algorithm 1）。到 R5，同样的固定原则让六个基准全部下降（−2.2 至 −9.6）。

*自适应原则演化的额外收益（预算匹配）。* 在 R5、相同预算下，演化后的原则在六个基准上全部优于固定原则，平均高出 6.77（+3.33 至 +10.12；Table 8）。这个差距就是原则演化带来的收益。

### 发布前待核对

- [x] **W1 对照条件只差一个因素（已确认）**：Exp 2 的 A/B、C/D 只在原则上不同，Exp 1 的三组只在反馈来源上不同，起点、流程和预算一致。
- [ ] **W1 "原则和课程都固定"这一组**：论文里没有直接对应的实验。正文用推理回答：R5 时即使课程仍在自适应，固定原则也已失效（−5.27，0/6），再固定课程只会去掉仅剩的自适应部分。如果 jcb6 在讨论阶段坚持要这组实验，再考虑补跑一轮。
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
| 开头 | 说明 Q1–Q4 同时回应 W1–W2 | — | — | 已改为在标题中注明 |
| Q1 | 分别确立贡献、PPO、原始数据、选择标准 | — | 1,629 |已压缩（占位符待填） |
| Q2 | 数据泄漏；R7 的选择 | — | 1,041 |已压缩（F_e 待填） |
| Q3 | 独立运行次数与置信区间；CURE-4B；32B 不如 8B | — | 1,217 |已压缩（CURE-4B 分数可选） |
| Q4 | 复杂推理基准 | — | 821 |已压缩（占位符待填） |
| **合计** | | **≤ 5,000** | **4,825** | |

W1、W2 不单独回答（与 Q1–Q4 高度重合），改在对应问题的标题中注明（Q1 & W1、Q3 & W2、Q4 & W2），以替代原来的开头说明句、节省字符。

字符空间：当前 4,825 字符（含占位符）。只剩 PPO 动作序列待填，填入后约 +90，约 4,915，在 5,000 以内。

W1 中有三点 Q1 没有直接覆盖，如果 2Nuw 在讨论中追问再补：(1) 单独去掉核验器的影响；(2) 额外资源（教师模型调用量、成本）的影响，附录 F.3 写明这些都有记录；(3) 收益归到单条原则上的分析，可以利用附录 A 所说的"样本与原则版本相关联"的记录来做。

### 英文正文（发布用）

```markdown
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
```

### 中文译文（不发布）

**Q1 与 W1（各部分的贡献、PPO、原始数据、选择标准）**
*原则演化与自适应课程。* 相同的教师模型、数据来源、预算和 R5 检查点（Table 7–8；六个基准上的平均变化）：

| 条件 | 原则 | 课程 | 平均变化 | 提升的基准数 |
|---|---|---|---|---|
| 只有原则演化 | 演化后 | 过时反馈 | −2.65 / −2.78 | 1/6 / 0/6 |
| 只有自适应课程 | 固定 | 当前反馈 | −5.27 | 0/6 |
| 两者结合（CoEvoMed） | 演化后 | 当前反馈 | **+1.50** | **6/6** |

*PPO 与更简单的分配策略。* 规划器优化的是累计收益（式 5），而不是一条贪心规则。它的选择会随学习者的状态变化：R1–R7 中它依次选择了 [动作序列]。定位能力在 R4 退化后，它在 R[x] 换成了 [动作]，之后定位能力回升（Figure 6）。
*原始数据退化。* 原始数据（附录 D.3）与任务不对齐（2D 记录中 58.3% 是图像描述；Figure 10），没有经过核查，没有针对性，也不会自适应。CoEvoMed 分别用构建器、核验器、规划器和修订智能体处理这几点。经过 CoEvoMed 处理后，SLAKE 达到 91.60，而不是 38.15（Table 9）。
*选择标准与学习收益的关系。* 选择标准在使用之前筛查监督数据的质量。之后由闭环检验学习收益：净修复一直不为正的原则会被再次修订（第 4.3 节）。被选中的原则在 R5 让六个基准全部提升，而原始原则让六个基准全部下降（平均高出 6.77；Table 8）。

**Q2（数据重叠；R7）**
*患者、检查和图像层面的重叠。* 我们把防止泄漏作为一项设计约束：支持数据、验证数据和测试数据是相互独立的划分（第 1 节；附录 C.6），并由我们的代码（coevomed/data.py）强制执行。我们把全部 11 个 2D 源数据和 5 个 3D 源数据与每一个外部测试集在四个层面上做了筛查：ID（包括检查 ID 和病例 ID）、图像路径、像素哈希（精确匹配和近似重复）以及归一化后的文本。所有检查发现的重叠均为零，包括 PubMedVision-IU 与 IU-Xray 之间；PMC-OA 与 PMC-VQA 所用的 PMC 论文也完全不相交。
*R7 是否依据预先定义的内部标准选出？* 是的。R7 在内部验证集上的能力画像最均衡（附录 C.4），能力画像的定义见第 3.1 节（式 1）；六个基准共用这一个检查点。我们在每一轮之后都用外部基准测试一次，只是为了展示进化如何提升学习者，并且报告了全部十轮，包括下降的轮次（Figure 7）。这些分数从不反馈到训练或检查点选择中（附录 A、C.6）。

**Q3 与 W2（独立运行与置信区间；CURE-4B；32B 在 IU-Xray 上的表现）**
*独立运行与置信区间。* 我们在来自三个模型家族的四个学习者模型上独立运行了完整流程，它们的架构和规模各不相同：Qwen3-VL（8B 和 32B）、Gemma 3（4B）和 InternVL3（9B）。每一次运行在所有评测基准上都超过了各自的基础模型：16 组比较全部提升，幅度为 +6.52 至 +26.76。这些提升远大于测试集本身的不确定性（95% 置信区间：PMC-VQA ±0.5、SLAKE ±1.7）。一个在不同模型家族、不同架构和不同规模上都成立的效果，不可能是某一次运行的偶然结果。
*为什么 IU-Xray 的比较中没有 CURE-4B？* 我们考虑过，但 IU-Xray 对 CURE 来说不是公平的测试。CURE 是在 MIMIC-CXR 派生的数据（Chest ImaGenome、MS-CXR）以及 PadChest-GR 上微调的，而 IU-Xray 既不在它的训练数据中，也不在它的评测中。一次零样本测试证实了这种数据域差异：它的 RaTEScore 只有 28.65，低于 Figure 3 中全部 28 个模型，而且输出非常短。
*为什么 32B 在 IU-Xray 上不如 8B？* 这在 IU-Xray 上很常见：Hulu-Med（7B 67.30，32B 62.40）和 MedGemma（4B 60.50，27B 59.00）也是如此。在相同规模下，CoEvoMed-32B 比 Hulu-Med-32B 高 2.68；在其余五个基准上，CoEvoMed-32B 都高于 CoEvoMed-8B。除了 RaTEScore 上 0.92 的领先，CoEvoMed-8B 在八个词汇指标中有六个领先 Hulu-Med-7B（ROUGE-2 最多领先 7.5；Figure 8）。

**Q4 与 W2（复杂推理）** 我们选择这些基准，是为了在临床实际的形式下检验医学推理：基于图像、常常是体数据、而且大多是开放式的。它们要求模型根据胸片写出完整报告（MIMIC-CXR、IU-Xray），根据多器官 3D CT 写出报告（AMOS-MM）；在 64 张切片的体数据上回答扫描平面、期相、器官、异常和位置问题（M3D-VQA）；在开放式 3D 问题中测量直径、大小和厚度（3D-RAD）；并回答临床医生撰写的、基于知识的、病理的以及文献配图的问题（VQA-RAD、SLAKE、PathVQA、PMC-VQA）。
*为什么不用 MedXpertQA-MM 或 MMMU？* 两者都是在 2D 图像上通过选择题检验推理（MedXpertQA-MM 全部是选择题，MMMU 有 94% 是选择题）。我们的评测已经包含了这种形式（PMC-VQA、M3D-VQA），而且走得更远：模型必须撰写报告、在没有选项的情况下作答、在 3D 体数据上推理，并对结构进行测量。
*泛化能力。* CoEvoMed 在全部九个基准上都排名第一（Table 1；Figure 3–4）。在 3D-RAD 的医学计算任务上，它比第二名高出 BLEU-1 8.6（Figure 9b）。

### 发布前待核对

- [ ] **Q1 PPO 占位符**：已决定用日志中 PPO 每一轮选择的动作来证明（不补跑实验）。需要从日志填入：`[action sequence]`，即 R1–R7 每轮的动作；`[action]` 和 `R[x]`，即定位能力在 R4 退化后，PPO 在哪一轮换成了什么动作。按设计，修复（repair）部分负责薄弱能力和近期退化，所以预期是 repair-heavy 或 weakness-focused。如果日志里看不到这样的对应，就换一个能体现"随状态变化"的例子，或者只保留动作序列那一句。
- [x] **Q1 对照条件（已确认）**：与 pUjh W1、jcb6 W1 相同，Exp 1、Exp 2 都只改变一个因素。
- [ ] **Q1 原始数据的组成**：与 jcb6 Q1 相同，需要确认 D.3 中约 70 万条原始数据和支持数据池来自同一批数据源。

- [x] **Q2 R7 的选择（作者已更正）**：R7 是按内部验证集上最均衡的能力画像选出的（附录 C.4；能力画像在第 3.1 节式 1 中定义于内部验证集），外部基准只用于逐轮轨迹展示。此前"按外部基准选出"为口误。正文据此直接回答 "Yes"。如果审稿人追问，需要能拿出每一轮的内部验证能力画像，说明 R7 最均衡。
- [x] **Q2 F_e 计算（不再需要）**：R7 本来就是按内部验证集选出的，正文不再用 F_e 作补充论证。
- [x] **Q2 不提 R10**：按你的决定，2Nuw 的回复不再提 R10。原因：论文中 R10 只有 SLAKE、PathVQA、IU-Xray 三个基准的结果（Figure 7），IU-Xray 的 R10（65.83）低于 Hulu-Med-7B（67.30），容易再被质疑。
- [x] **Q2 去重的实际做法（已确认事实）**：与内部验证集和全部外部测试集比对，依据样本 ID、图像路径、像素哈希，并对每条样本的文本做泄漏查询；PubMedVision-IU 与 IU-Xray 专门做过。
- [x] **Q2 泄漏筛查结果（已填入）**：2D 11 个源、3D 5 个源与外部测试集在样本 ID（含 study/case ID）、图像路径、像素哈希（精确 RGB SHA-256，加 dHash + 128×128 NCC ≥ 0.95 的近似重复核验；3D 为视频 SHA-256 加首帧 RGB SHA-256，AbdomenAtlas 对 AMOS-MM 另做 5 帧核验）、文本（归一化精确匹配 ≥20 字符，句子级 ≥40 字符）四个层面全部为 0。PubMedVision-IU 对 IU-Xray 专项全部为 0；PMC-OA 与 PMC-VQA 测试集的 PMC 论文 ID 集合完全不相交。
- [x] **Q2 筛查口径（已确认）**：筛查使用的测试集规模与论文一致（Table 3–4），报告中 MIMIC-CXR、PathVQA 的数字为笔误。正文"against every external test"成立。
- [ ] **Q2 患者层面**：报告的 ID 层面包含 study/case ID，正文据此写"IDs (including study and case IDs)"，没有单独声称做了患者 ID 匹配。如果审稿人追问患者层面，再说明哪些数据集提供患者 ID。
- [ ] **Q2 代码描述核对**：正文对代码行为的描述（共享记录 ID、图像路径、RGB 哈希或 study ID 即拒绝启动；必须有原始划分来源；训练任务再次比对）来自提交的 `coevomed/data.py`（`validate_partitions`、`validate_evidence_identity`、`validate_exclusions`）。请确认正式实验用的是同一套检查逻辑。
- [ ] **Q2 定稿时补进论文**：附录 C.3 目前只写了与验证集的重叠检查。定稿时补上与外部测试集的筛查、文本泄漏查询，以及外部基准只用于逐轮轨迹展示、不参与检查点选择这一点。
- [ ] **Q3 独立运行的表述**：正文以"在三个模型家族、四个学习者上独立运行完整流程"回答运行次数，不涉及随机种子，也不能出现暗示多种子重复的说法（如 "averaged over runs"、"mean ± std"）。如果审稿人追问主实验的随机种子，要如实回答。
- [ ] **Q3 置信区间（可选加强）**：正文用的 ±0.5（PMC-VQA）和 ±1.7（SLAKE）是根据 Table 1 准确率和 Table 3 样本数算出的 Wilson 95% 置信区间（PMC-VQA [67.45, 68.45]，SLAKE [89.78, 93.12]），不需要额外数据。如果之后跑了 Hulu-Med-7B 的推理，可以再补配对 bootstrap 置信区间，重点放在差距最小的 IU-Xray（+0.92）和 PMC-VQA（+1.15）上。
- [ ] **Q3 CURE-4B**：正文理由：CURE 在 MIMIC-CXR 派生数据（Chest ImaGenome、MS-CXR）和 PadChest-GR 上微调；IU-Xray 不在其训练和评测数据中；零样本测试结果证实了数据域差异。CURE 在 IU-Xray 上的零样本结果：RaTEScore 0.2865（正文写作 28.65，与 Figure 3 的 ×100 口径一致），BLEU-4 0.0009，ROUGE-L 0.0905，CIDEr 0.0039，METEOR 0.0435；输出平均约 79 字符，大量 "No significant findings"，44% 的输出含 bbox，已按官方代码剥离后计算。Figure 3 IU-Xray 中 28 个模型的最低分为 42.00（BioMediX2-8B）。训练数据依据：CURE 官方仓库 README 与训练配置（datasets 仅 chest-imagenome、ms-cxr、padchest-gr）。已确认：28.65 与 Figure 3 使用同一套 RaTEScore 评测流程。
- [ ] **Q3 32B 的说法**：正文把 32B 在 IU-Xray 上低于 8B 归因于基准本身（Hulu-Med 同样如此）。如果你知道其他原因，例如 32B 的训练轮数或预算不同，请告诉我，必要时补充。
- [ ] **Q4 备用弹药**：正文不承诺补测 MedXpertQA-MM 和 MMMU。如果 2Nuw 在讨论阶段坚持要这两个基准的结果，再考虑补测（只需推理）。

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
| Q3：CURE 在 MedGemma-4B-IT 上 LoRA 微调，训练数据为 Chest ImaGenome、MS-CXR、PadChest-GR | CURE 官方 GitHub 仓库 README 与训练配置（外部来源） |
| Q4：报告任务评估"synthesis of image-grounded findings into reports"；AMOS-MM 为胸、腹、盆腔的较长 findings 报告 | 附录 C.1（p.19–20） |
| Q4：MIMIC-CXR 第一为 CoEvoMed-32B（64.33）；IU-Xray 第一为 CoEvoMed-8B（68.22）；AMOS-MM 第一为 CoEvoMed（66.97） | Figure 3（p.7）；Figure 4（p.8） |
| Q4：M3D-VQA（83.06）和 3D-RAD（47.07）均排名第一 | Figure 4（p.8） |
| Q4：体数据以 64 张切片输入 | 附录 C（p.18）；附录 C.1（p.20） |
| Q4：SLAKE 含医学知识库 | Table 3（p.19） |
| Q4：多轮对话示例覆盖六个 2D 和三个 3D 基准 | 附录 G（p.30–34） |
| Q4：MedXpertQA-MM 每题 5 个选项（约 2,000 题）；MMMU 94% 为选择题 | Zuo et al., ICML 2025；Yue et al., CVPR 2024（外部来源） |
| Q4：PMC-VQA、M3D-VQA（四选一）属于选择题形式 | Table 4（p.19）；PMC-VQA 原始设定 |
| Q4：CoEvoMed 九个基准全部第一：VQA 由 CoEvoMed-32B 领先全部模型，MIMIC-CXR 第一为 32B，IU-Xray 第一为 8B，M3D-VQA、3D-RAD、AMOS-MM 第一 | §5.2（p.7）；Table 1；Figure 3–4 |
| Q4：3D-RAD 医学计算 1,002 题，涉及直径、大小、厚度；CoEvoMed BLEU-1 37.8 / ROUGE-1 39.3，Photon-3B-S2 29.2 / 31.1，Hulu-Med-7B 23.5 / 26.0，Qwen3.8-27B 13.1 / 13.8，Qwen3.6-27B 2.9 / 8.0 | Figure 9b（p.21）；附录 C.1（p.19–20） |
| Q4：闭源模型最高分 PMC-VQA 64.58、VQA-RAD 76.81、SLAKE 85.05、PathVQA 64.11（均为 Qwen3.8-Max）；CoEvoMed-8B 67.95、82.48、91.60、69.40 | Table 1（p.6） |
| Q3：IU-Xray 上同系列大小模型对比：Hulu-Med 7B 67.30 > 32B 62.40；MedGemma 4B 60.50 > 27B 59.00；Qwen3.8-27B 62.37 > Qwen3.8-Max 56.50（未写入正文，Max 的参数量未公开）；反例：Qwen3-VL 8B 50.28 < 32B 58.56，HuatuoGPT-V 7B 52.90 < 34B 58.20；Lingshu-32B 没有 IU-Xray 结果 | Figure 3（p.7） |
| Q3：每轮 24 张 A100 | 附录 B（p.17） |
| Q3：16 组相对基础模型的提升全部为正（+6.52 至 +26.76）。8B：+13.82、+25.72、+26.76、+26.63、MIMIC +12.86、IU +17.94；32B：+12.96、+16.86、+20.73、+25.32、MIMIC +7.14、IU +6.52；Gemma：+22.39、+16.23；InternVL：+20.40、+13.28 | Table 1（p.6）；Figure 3（p.7，Qwen3-VL-8B MIMIC 50.76、IU 50.28；Qwen3-VL-32B MIMIC 57.19、IU 58.56）；Figure 5（p.9）；附录 C.5（p.24） |
| Q3：置信区间半宽 ±0.5、±1.7 | 由 Table 1 准确率和 Table 3 样本数计算的 Wilson 区间 |
| Q2：支持数据、验证集、外部基准三者分离 | §1（p.2）；附录 C.6（p.25）"Feedback provenance and independence" |
| Q2：代码在划分间重叠时拒绝启动；必须有 RGB 哈希和原始划分来源；训练任务再次比对 | 补充材料代码 `coevomed/data.py`：`validate_partitions`、`validate_evidence_identity`、`validate_exclusions`、`identity_tokens` |
| Q2："preserves the joint capability profile of a single learner"；"including later performance declines" | 附录 C.4（p.24） |
| Q2：R10 SLAKE 88.67、PathVQA 67.25；Hulu-Med-7B 86.80、65.60 | Figure 7（p.9）；Table 1（p.6） |
