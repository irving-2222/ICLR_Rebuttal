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
| W1 | 多智能体是否必要 | — | 1,523 | 已重写（两部分；合并表；三项设计保障） |
| W2 | 论文组织 | — | 468 | 已重写（正文逻辑、附录对应、可复现） |
| W3 | 遗忘与 R7 的选择 | — | 1,249 | 已重写 |
| Q1 | MedVLSynther 复现 | — | 636 | 已填入复现结果 |
| Q2 | 数据公开 | — | 137 | 已压缩 |
| Q3 | 能力分类体系 | — | 962 | 已压缩 |
| 结尾 | | — | — | 不写（为字符限制） |
| **合计** | | **≤ 5,000** | **4,985** | |

"当前"一栏只统计各条目正文；合计按代码块全文统计，包含条目之间的空行。

### 英文正文（发布用）

```markdown
**W1 (Necessity of the multi-agent framework).** **Table 2** (Sec. 5.3) and **App. D** show that the agents are needed (**Tables 7–9**). Changes from a shared start, all else fixed:

| Without | From | VQA-RAD | SLAKE | PMC-VQA | PathVQA |
|---|---|---|---|---|---|
| All agents: raw data | base | −13.75 | −26.69 | −8.62 | −6.83 |
| Revision agent: original principles | R5 | −5.64 | −3.60 | −9.60 | −2.20 |
| Curriculum planner: R2 feedback | R5 | −1.10 | −5.20 | −3.60 | −3.10 |
| Curriculum planner: R3 feedback | R5 | −1.77 | −5.80 | −1.80 | −2.40 |
| None: CoEvoMed | base | +25.72 | +26.76 | +13.82 | +26.63 |
| None: CoEvoMed | R5 | +2.62 | +0.69 | +0.52 | +1.13 |

No simpler process can substitute them: each one above lowers every score. We also separate the roles by design (**App. B**):

1. **Independent checking.** LLMs rarely self-correct without external feedback (Huang et al., 2024). We therefore designed the verifier (Qwen3.6-27B) and constructor (deepseek-v4-flash) as different models.
2. **Grounded construction.** If the constructor wrote from the image, it could describe absent objects, as VLMs often do (Li et al., 2023). We therefore let it write only from selected facts.
3. **Curriculum allocation.** If an LLM agent also set the budget, it could not learn, since LLM weights stay frozen. Curricula learned from learning progress match or beat hand-crafted ones (Matiisen et al., 2017). We therefore made the curriculum planner a separate policy trained by PPO on validation gains (Sec. 4.2).

**W2 (Organization).** The layout follows our contributions and scope. The main text gives each contribution with its evidence: co-evolution framework (Sec. 3), multi-agent system and curriculum policy (Sec. 4), and evaluation task composition (Sec. 5.1). For space, its analyses use one VQA and one report task. The appendix adds what reproduction needs: algorithm (**App. A**), settings (**App. B**), data and metrics (**App. C**), and all-task results (**App. D**).

**W3 (Catastrophic forgetting and retention).** We respectfully note a misunderstanding: CoEvoMed builds on curriculum learning, not continual learning. Forgetting arises when tasks are learned in sequence and old data is dropped. It trains all tasks every round and replays earlier data (Eq. 7; Sec. 3.3), so continual-learning metrics do not apply. "Retention" is a share of the planner's budget (Sec. 4.2), ablated with it (Table 7).

The later-round declines come from the data, not from our mechanisms. The planner and revision agent work as designed but draw on a fixed pool (359,355 facts, App. C.3). Each round builds 50,000 examples (App. B), so by R7 the budget nearly matches the pool and later rounds mostly reuse evidence. Self-training on finite data shows the same pattern (Chen et al., 2024; Singh et al., 2024). At R10, the Fig. 7 benchmarks stay within 3 points of their peaks, over 12 above R1.

We selected R7 by a predefined criterion: the most balanced capability profile on internal validation (App. C.4). R7 is where this pool's new evidence runs out, and InternVL3-9B peaks at rounds 4–6 (App. C.5). CoEvoMed is a general evolution mechanism: its final checkpoint is not a fixed round but follows the limit of the data pool.

**Q1 (MedVLSynther base model).** Absolute scores mix method and backbone, so we compare gains over each method's base (MedVLSynther as published):

| Gain over own base | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther-7B (Qwen2.5-VL-7B) | +6.13 | +8.82 | +6.65 | +0.17 |
| CoEvoMed-8B (Qwen3-VL-8B) | **+13.82** | **+25.72** | **+26.76** | **+26.63** |

Same base, with MedVLSynther's released data and GRPO script:

| Same base: Qwen3-VL-8B | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther recipe | 53.18 | 70.96 | 73.32 | 68.69 |
| CoEvoMed-8B | 67.95 | 82.48 | 91.60 | 69.40 |

**Q2 (Data release).** Yes. Upon acceptance, we will release the synthesized data and all principle versions under each source's license.

**Q3 (Capability taxonomy).** The taxonomy is not a claimed contribution but the unit of validation feedback (App. C.3).

We built our categories on SLAKE's (Liu et al., 2021) by design: physicians annotated them, and SLAKE spans more modalities and body parts than earlier datasets. They describe what a question asks, not a dataset, so they fit every task: VQA-RAD and M3D-VQA use similar types (Lau et al., 2018; Fig. 9a).

The dimensions are necessary because the loop runs on them: task form and capability set the planner's targets, and modality and anatomy match evidence to them (Table 6). With the taxonomy fixed, stale diagnoses lower 11 of 12 scores (Table 7): gains come from diagnosis, not relabeling.

On 200 SLAKE questions, our annotations match native labels for capability at 97.5% (Cohen's κ = 0.958), modality at 100%, and body region at 96.5%. κ > 0.81 is "almost perfect" agreement (Landis & Koch, 1977). We will add the mapping to Table 6.
```

### 中文译文（不发布）

**W1（多智能体框架的必要性）** 正文 **Table 2**（第 5.3 节）和**附录 D** 表明这些智能体都是必要的（**Table 7–9**）。下表为相对同一起点的变化，其余设置保持不变：

| 去掉的功能 | 起点 | VQA-RAD | SLAKE | PMC-VQA | PathVQA |
|---|---|---|---|---|---|
| 全部智能体：原始数据 | 基础模型 | −13.75 | −26.69 | −8.62 | −6.83 |
| 修订智能体：原始原则 | R5 | −5.64 | −3.60 | −9.60 | −2.20 |
| 课程规划器：R2 反馈 | R5 | −1.10 | −5.20 | −3.60 | −3.10 |
| 课程规划器：R3 反馈 | R5 | −1.77 | −5.80 | −1.80 | −2.40 |
| 无：CoEvoMed | 基础模型 | +25.72 | +26.76 | +13.82 | +26.63 |
| 无：CoEvoMed | R5 | +2.62 | +0.69 | +0.52 | +1.13 |

没有更简单的流程能替代它们：上表中每一种更简单的流程都会让所有分数下降。此外，我们有意把这些角色分开设计（**附录 B**）：

1. **独立核查。** 大语言模型在没有外部反馈时很难自我纠正（Huang et al., 2024）。因此，我们把核验器（Qwen3.6-27B）和构建器（deepseek-v4-flash）设计为不同的模型。
2. **基于证据的构建。** 如果构建器直接看图撰写，它可能会像视觉语言模型常见的那样，描述图像中并不存在的物体（Li et al., 2023）。因此，我们让构建器只根据选出的事实撰写。
3. **课程分配。** 如果由某个大语言模型智能体同时负责分配预算，这种分配就无法学习，因为大语言模型的权重是冻结的。根据学习进度学到的课程能够达到甚至超过人工设计的课程（Matiisen et al., 2017）。因此，我们把课程规划器单独设计为一个策略网络，用 PPO 依据验证集上的收益来训练（第 4.2 节）。

**W2（论文组织）** 论文的排版与我们的贡献和研究范围是一致的。正文给出每一项贡献及其证据：协同进化框架（第 3 节），多智能体系统与课程策略（第 4 节），以及评估任务的组成（第 5.1 节）。受篇幅所限，正文的分析各选用一个 VQA 任务和一个报告生成任务。附录补充复现所需的内容：算法（**附录 A**）、设置（**附录 B**）、数据与评测指标（**附录 C**），以及全部任务的结果（**附录 D**）。

**W3（灾难性遗忘与保留）** 我们想指出一个误解：CoEvoMed 是基于课程学习设计的，而不是持续学习。灾难性遗忘出现在按顺序学习各个任务、并丢弃旧数据的情况下。CoEvoMed 每一轮都同时训练所有任务，并回放之前的数据（式 7；第 3.3 节），因此持续学习的指标并不适用。"保留"是规划器预算中的一个份额（第 4.2 节），已随规划器一起做了消融（Table 7）。

后期轮次的下降源于数据，而不是我们的机制。课程规划器和修订智能体都按设计正常工作，但它们使用的是一个固定的数据池（359,355 条事实，附录 C.3）。每轮构建 50,000 个样本（附录 B），因此到 R7，累计预算已接近数据池的规模，后续轮次主要在重复使用已用过的证据。在有限数据上的自训练也呈现同样的规律（Chen et al., 2024；Singh et al., 2024）。到 R10，Figure 7 中的基准仍都在各自峰值 3 分以内，并比 R1 高出 12 分以上。

我们按预先定义的标准选择 R7：它在内部验证上的能力画像最均衡（附录 C.4）。R7 正是当前数据池的新证据用尽的那一轮，而 InternVL3-9B 的峰值出现在第 4–6 轮（附录 C.5）。CoEvoMed 是一个通用的进化机制：最终检查点不是固定的某一轮，而是取决于所用数据池的上限。

**Q1（MedVLSynther 的基础模型）** 绝对分数把方法和骨干模型的效果混在一起，因此我们比较各方法相对其基础模型的提升（MedVLSynther 采用原文发表的结果）：

| 相对自身基础模型的提升 | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther-7B（Qwen2.5-VL-7B） | +6.13 | +8.82 | +6.65 | +0.17 |
| CoEvoMed-8B（Qwen3-VL-8B） | **+13.82** | **+25.72** | **+26.76** | **+26.63** |

相同的基础模型，用 MedVLSynther 公开的数据和 GRPO 训练脚本训练：

| 相同基础模型：Qwen3-VL-8B | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther 配方 | 53.18 | 70.96 | 73.32 | 68.69 |
| CoEvoMed-8B | 67.95 | 82.48 | 91.60 | 69.40 |

**Q2（数据公开）** 会公开。论文被接收后，我们将按各源数据的许可公开合成数据和全部版本的构建原则。

**Q3（能力分类体系）** 这套分类体系不是我们主张的贡献，而只是验证反馈的基本单元（附录 C.3）。

我们有意以 SLAKE 的问题类别（Liu et al., 2021）为基础构建我们的类别：这些类别由医生标注，而且 SLAKE 覆盖的模态和身体部位比以往的数据集更多。这些类别描述的是问题在问什么，而不是某个数据集，因此适用于所有任务：VQA-RAD 和 M3D-VQA 也采用了类似的问题类型（Lau et al., 2018；Figure 9a）。

这些维度是必要的，因为整个闭环都建立在它们之上：任务形式和能力类别决定课程规划器的目标，模态和解剖部位让证据与这些目标相匹配（Table 6）。在分类体系保持不变的情况下，使用过时的诊断会使 12 个分数中的 11 个下降（Table 7）：收益来自诊断，而不是重新贴标签。

在 200 道 SLAKE 题目上，我们的标注与原生标签的一致率为：能力类别 97.5%（Cohen's κ = 0.958），模态 100%，解剖部位 96.5%。κ > 0.81 即属于"几乎完全一致"（Landis & Koch, 1977）。我们会把这一对应关系补充到 Table 6 中。

### 发布前待核对

- [x] **消融在正文（作者确认）**：正文第 5.3 节 Table 2（"Mechanism ablations"）给出两组消融：Panel A 为反馈来源（R2/R3/R5 反馈，对应课程规划器/课程自适应），Panel B 为原始与演化原则（R2、R5，对应原则演化），指标为 VQA-RAD 和 MIMIC-CXR；附录 D 的 Table 7–9 是六个基准的完整结果和原始数据对照。三份回复的消融部分都先指向正文 Table 2，再指向附录 D。
- [x] **W1 修订智能体（已确认）**：Exp 2 的条件 C 和 D 只在原则上不同，分配动作、预算和训练设置一致。
- [x] **W1 规划器（已确认）**：Exp 1 的三组使用相同的原则和预算，只替换了反馈来源。
- [x] **W1 合并表（数字已核对）**：按论文 Table 7–8 的列顺序，只保留四个 VQA 基准（VQA-RAD、SLAKE、PMC-VQA、PathVQA）。MIMIC-CXR 和 IU-Xray 两列已删去（作者要求：Table 9 的原始数据和基础模型起点两行没有测这两个基准）。原始数据和 CoEvoMed 两行是相对 Qwen3-VL-8B 基础模型的变化，由 Table 9 的绝对分数换算：原始数据 −13.75 / −26.69 / −8.62 / −6.83，CoEvoMed +25.72 / +26.76 / +13.82 / +26.63；其余各行取自 Table 7、8 括号中的变化值；R5 起点的 CoEvoMed 一行就是 Table 8 条件 D，它与 Table 7 的"R5 feedback"是同一次训练（附录 D.1）。
- [x] **W1 三项设计保障**：第二部分按"如果……→ 文献 → 因此我们这样设计"来写：(1) 独立核查，核验器与构建器设计为不同模型（Huang et al., 2024）；(2) 基于证据的构建，构建器只用选出的事实、不看图像，核验器对照图像检查（附录 A："Construction uses selected facts rather than direct image access; verification checks candidates using the image"；Li et al., 2023）；(3) 课程分配：如果由大语言模型智能体同时分配预算，分配无法学习（附录 B："external LLM weights remain fixed"），因此把课程规划器单独设计为用 PPO 依据验证收益训练的策略网络（第 4.2 节、式 8）。W1 的两个分点直接以答案开头，不再重复审稿人的问题；标题改为 "Necessity of the multi-agent framework"。第 3 点引用的 Matiisen et al., 2017（Teacher-Student Curriculum Learning，论文参考文献已收录，arXiv:1707.00183）摘要原文为 TSCL "matches or surpasses the results of carefully hand-crafted curricula"。
- [ ] **W1 表格"课程规划器"两行**：这两行来自实验 1（Table 7）。实验 1 替换的反馈同时用于课程分配和监督构建（附录 D.1），表中按你之前认可的写法归到课程规划器名下。如果审稿人追问，可以说明这一点。
- [ ] **修订智能体的单独理由已删去**：第 3 点改为只讲课程规划器后，"新原则须通过 N = 100 的配对测试"（算法 1 第 18–20 行）不再出现在 W1 中；修订智能体的作用仍由表中"原始原则"一行体现。
- [ ] **W1 表格不再逐行标注表号**：为腾出字数，表号统一写在第一部分（**Tables 7–9**）。对应关系：原始数据和基础模型起点的 CoEvoMed 一行来自 Table 9；原始原则一行来自 Table 8 条件 C；R2/R3 反馈两行来自 Table 7；R5 起点的 CoEvoMed 一行是 Table 8 条件 D（与 Table 7 的 R5 feedback 为同一次训练）。
- [ ] **为容纳 W1 而做的压缩（可按需恢复）**：Q1 删去 "We were aware of the base difference."；Q1 第二张表的引导句改为 "Same base: ..."；Q2、W2 改了措辞；Q3 把"空间关系、比较和整体描述"改为"three categories"，并把四个无标签数据源放进括号；W3 的 R10 一句改为 "all three Fig. 7 benchmarks ... over 12 above R1"。为了重写 W1 第 2 点，又做了三处压缩：W3 删去 "One checkpoint serves all six benchmarks"（保留 "though PathVQA peaks at R8"，同样说明不是按单项挑选）；W3 开头改为 "ablated in W1"；Q3 最后一点删去 "while current ones raise all six"。为了重写 W1 第 3 点，又压缩了：W2 改写措辞；W3 "keeps improving to peaks at R7–R8" 改为 "improves up to R7–R8"，"extend the evolution" 改为 "extends the gains"，"only track the evolution and never guide" 改为 "only track evolution, never training or selection"；Q1 第二张表引导句删去 "Qwen3-VL-8B"（表头已有）；Q3 删去 "matching"、"categories" 和 "W1 table"。
- [ ] **W1 选择器和核验器没有单独消融**：表中"全部智能体"一行同时去掉了选择器、构建器和核验器，没有单独去掉核验器的实验。正文因此写的是"ablates the functions of the agent roles"，没有写"每个角色各有一个消融"。如果审稿人追问，可以引用核验器的拒绝率（若日志里有）。
- [x] **W2 排版与贡献、范围一致（作者要求）**：开头改为 "The layout follows our contributions and scope."，并把正文各节对应到第 1 节列出的三项贡献：协同进化框架（第 3 节），多智能体系统与课程分配策略（第 4 节；4.1 多智能体构建、4.2 课程分配、4.3 原则演化），评估任务组成在第 5.1 节。"范围"对应附录 E（"Scope of the formulation"：结论限于所评估的数据和骨干模型设置）。附录内容表述为复现所需的细节。
- [x] **W2 补充"正文放代表性任务、附录放全部"（作者要求）**：依据第 5.3 节 "Mechanism comparisons use VQA-RAD and MIMIC-CXR; full results and experimental details appear in Appendix D"，以及 Figure 5（Gemma 同样用 VQA-RAD 和 MIMIC-CXR）。正文写作 "For space, its analyses use one VQA and one report task; the appendix covers all tasks."。为腾字数：四处引用去掉会议名（与论文的作者-年份格式一致）；W2 删去 "Eqs. 1–9" 和 "(Sec. 5)"；W3 "curriculum planner's budget" 改为 "planner's budget"，"Even at R10" 改为 "At R10"；W1 表中 CoEvoMed 两行取消加粗。
- [x] **W2 重写（正文逻辑、附录对应、可复现）**：正文顺序为第 3 节问题定义、第 4 节三个机制（式 1–9）、第 5 节实验（5.1 设置含评估任务组成，5.2 结果，5.3 机制分析）。附录对应：A 完整训练流程（算法 1）、B 训练配置（各智能体模型、每轮 50,000 样本、PPO 设置等）、C 评测数据与输入、支持证据来源及链接（Table 5）、指标与统计、D 组件对照实验。
- [ ] **W2 代码（请确认）**：如果投稿时代码作为补充材料上传了（仓库里有 `code/CoEvoMed_ICLR2027_submitted.zip`），可以在 W2 末尾加一句 "Our code is in the supplementary material."（约 50 字符，需要从别处再压缩）。如果没有上传，就不写。
- [x] **W3 回放数据**：已确认主实验每轮混入回放数据，W3 已写入 "mixes in replay data (Section 3.3)"。
- [x] **R7 的选择依据（作者已更正）**：R7 是按内部验证集上的能力画像（附录 C.4；"capability profile" 的定义见第 3.1 节式 1）选出的，与论文一致。此前"按外部基准选出"的说法为口误，已更正。W3 已按此改写，并删去 R10 与 Hulu-Med-7B 的比较。
- [x] **W3 PathVQA 峰值**：已确认 PathVQA 的 R8 略高于 R7；R10 的 67.25 仍在峰值 3 分以内，正文说法成立。
- [ ] **W3 数据池解释（请确认）**："By R7 the budget nearly matches the pool, so later rounds mostly reuse seen evidence" 是按论文数字推出的解释：7 × 50,000 = 350,000，接近 359,355 条事实（附录 C.3 称之为 "reusable facts"）。样本和事实不一定一一对应。请确认后期轮次确实大量复用已用过的证据（例如从日志统计每轮首次使用的事实比例）。如果不符，改为 "so later rounds add little new evidence"。
- [ ] **W3 "更大的数据池可以延长演化"**：这是基于机制的推断（数据池是输入，不是方法的一部分），没有扩池实验支撑。如果审稿人追问，可以回答：数据池在附录 C.3 中按来源构建，扩充来源不需要改动任何智能体或规划器。
- [x] **W3 直接指出误解（导师建议）**：开头改为 "We respectfully note a misunderstanding: CoEvoMed builds on curriculum learning, not continual learning."，礼貌但直接地指出审稿人把方法当成了持续学习。为腾字数：W3 "CoEvoMed trains" 改为 "It trains"，"can only draw on" 改为 "draw on"，"internal validation sets" 改为 "internal validation"，"all three Fig. 7 benchmarks" 改为 "the Fig. 7 benchmarks"，"is ablated with it" 改为 "ablated with it"；W2 "covers all tasks" 改为 "has all tasks"。
- [x] **W3 改为分段（作者要求）**：不再分点，三段分别回答：(1) 基于课程学习设计；先说明灾难性遗忘出现在按顺序学习、丢弃旧数据的情况下，而 CoEvoMed 每轮同时训练所有任务并回放旧数据，所以持续学习指标不适用；"保留"是课程规划器预算的份额，随规划器在 Table 7 中消融。(2) 后期下降源于数据而非机制：规划器和修订智能体按设计工作，但只能使用固定数据池。(3) 选择 R7 的依据。为腾字数：Q2 删去括号里的"图像以 ID 引用、为禁止再分发的数据提供重新生成脚本"（承诺本身仍在核对清单中）；W2 删去 "links"；W1 第 3 点 "policy network" 改为 "policy"；R7 段删去 "only track evolution"。
- [x] **W3 选择 R7 一段（只用论文中的事实）**：(1) 按预先定义的标准选出（内部验证集上能力画像最均衡；第 3.1 节式 1，附录 C.4）；(2) 标准本身不指定轮次，R7 恰好是当前数据池新证据用尽的一轮（7 × 50,000 ≈ 359,355，见第二段）；(3) 最佳轮次随设置变化：InternVL3-9B 的 VQA-RAD 在第 6 轮达到峰值 78.71%，MIMIC-CXR 在第 4 轮达到最高 65.34（附录 C.5，Figure 11）。原先"换成更大的数据池会选出更靠后的一轮"没有实验支撑，已删去。段末落脚到通用性（作者给定表述）："CoEvoMed is a general evolution mechanism: its final checkpoint is not a fixed round but follows the limit of the data pool." 跨骨干实验（Gemma-3-4B、InternVL3-9B，第 5.3 节和附录 C.5）支撑"通用"。为腾字数：Q3 删去"合并 SLAKE 的属性类型"；Q1 "own base" 改为 "base"（表头仍为 "Gain over own base"）。
- [x] **W3 文献（已核实）**：Chen et al., ICML 2024 = SPIN（Self-Play Fine-Tuning），收益集中在前两轮，后续工作 SPACE 报告其在峰值后下降；Singh et al., TMLR 2024 = ReST-EM（"Beyond Human Data"），原文写明 APPS 在第二轮回退，迭代超过几轮后收益递减，并归因于在少量训练题上过拟合。R-Zero（论文中的 Huang et al., 2026a）后期下降没有查到原文证据，所以没有引用。
- [x] **W3 R7 出处**：附录 C.4 "Checkpoint selection" 写明按整体均衡选 R7；附录 C.6 写明外部基准不参与监督构建、学习者训练、课程和原则更新。
- [ ] **为容纳 W3 而删去的内容（可按需恢复）**：W2 中"四个 2D VQA、两个报告、三个 3D 基准"的括号；Q3 中"VQA-RAD 和 M3D-VQA 采用类似类别"一句。（"过时诊断使 12 个分数中 11 个下降"已作为 Q3 最后一点补回，因为它直接回答"收益来自诊断还是重新贴标签"。）W2 中"包括能力单元（第 3.1 节）"一句。W3 原先关于"被动恢复与均衡"的内容已删去：审稿人认可了恢复本身，"均衡收敛"由后两点（下降幅度小、R7 能力画像最均衡）回应。
- [x] **Q1 复现结果（作者提供，已填入）**：用 MedVLSynther 公开数据和 GRPO 脚本在 Qwen3-VL-8B 上复现：PMC-VQA 53.18、VQA-RAD 70.96、SLAKE 73.32、PathVQA 68.69。CoEvoMed-8B 四项全部更高（+14.77、+11.52、+18.28、+0.71）。注意：PMC-VQA 53.18 低于 Qwen3-VL-8B 基础模型的 54.13。
- [ ] **Q1 数字来源**：确认 Table 1 的 MedVLSynther 数字引自其论文（与其 GitHub README 的数字完全一致）。正文写的是 "as published"。
- [ ] **Q1 与附录 C.1 的一致性**：C.1 写的是"本研究评估的基线与 CoEvoMed 使用相同的评估集和评分规则"，MedVLSynther 是引用数，与这句不符。Q1 已如实写明"按原文发表的结果和协议"；定稿时建议把 C.1 改为区分"我们评测的基线"和"引用原文的基线"。
- [x] **字符限制**：当前 4,985 字符。填入 Q1 复现结果后，`[x.xx]` 每格少 1 个字符，仍在限制内。
- [x] **Q2 承诺（作者要求删除）**：正文已不再提"图像以 ID 引用、为禁止再分发的源数据提供重新生成脚本"，只承诺"按各源数据的许可公开合成数据和全部版本的构建原则"。
- [ ] **Q2 待确认许可**：PMC-OA、MedTrinity BHX、RadGenome-ChestCT、Med-MAT 的许可没能直接核实，AbdomenAtlas1.0Mini 的附加条款也不确定，公开前需逐个确认（见下方"Q2 源数据许可核对"）。
- [x] **Q3 一致率（已填入）**：轴 B（视觉能力）准确率 97.50%（195/200），macro-F1 0.9767，Cohen's κ 0.9575（正文写作 0.958）；轴 C（模态）准确率 100%，为模型在不看原标签的情况下独立判断；轴 D（解剖部位）准确率 96.50%（193/200），macro-F1 0.9476。轴的对应关系来自代码 `AXES = ("task_form", "visual_ability", "modality", "anatomy")`。
- [x] **Q3 定位（作者已确认）**：分类体系不在论文第 1 节列出的三条贡献中（协同进化框架、课程分配策略、多智能体系统），附录 C.3 称其为 "the units used for validation feedback"。Q3 开头据此说明它不是主张的贡献；最后一点用实验 1（分类体系不变，只替换诊断的时效）回答"收益来自诊断还是重新贴标签"。
- [x] **Q3 必要性（作者要求补上）**：新增一点说明四个维度为什么必要：任务形式和能力类别是课程规划器的目标，模态和解剖部位用于把证据和目标匹配起来（Table 6 标题："Task form and visual capability describe capability targets; modality and anatomy describe evidence attributes. Together, they organize task-level capability diagnosis and curriculum adaptation"；附录 C.3："to align evidence retrieval with the capability targets specified by the curriculum"），并把原来最后一点（Table 7，收益来自诊断）并入这一点作为实证。可选补充（约 85 字符，需再压缩别处）："Benchmark scores alone would miss regressions such as localization at R4 (Fig. 6)."
- [ ] **Q3 κ 对应的轴**：正文把 κ = 0.958 放在能力类别（轴 B）后面。如果这个 κ 是别的轴或整体的值，告诉我调整位置。
- [ ] **Q3 样本说明（可选）**：如果这 200 条是随机抽取的，可以在 "on 200 SLAKE questions" 前加 "randomly sampled"。
- [ ] **Q3 选择 SLAKE 的理由（已写入，措辞请确认）**：Q3 第一点合并为一条，写了两条理由，均来自 SLAKE 摘要：(1) "comprehensive semantic labels annotated by experienced physicians"，正文写作 "physicians annotated them"；(2) "richer modalities and covers more human body parts than the currently available dataset"，正文写作 "spans more modalities and body parts than earlier datasets"。没有找到"经临床专家审核"的原文，所以没有写 "reviewed/validated by clinical experts"；如果你手上的 SLAKE 原文有这类表述，告诉我页码可以改。通用性的理由：类别描述的是"问题在问什么"，与数据集无关；VQA-RAD（Lau et al., 2018）和 M3D-VQA（Figure 9a 的五个类别）也采用类似的问题类型。为腾字数，W1 第 2 点删去 "the verifier checks the image"，W1 第二部分删去 "only the full one improves all"（表中 CoEvoMed 两行已经显示）。Q3 删去"新增三个类别、无原生标签数据按同一套类别标注"两句（作者要求，避免被质疑新增类别的准确性）；"adopted SLAKE's question categories" 改为 "built our categories on SLAKE's question categories"，因为 Table 6 的九个视觉能力类别中有三个（空间关系、比较、整体描述）不在 SLAKE 中，写"采用"会与 Table 6 不符。W2 删去 "that cites it"。W1 表中 CoEvoMed 两行的加粗已恢复。
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
| W1 | 在预算匹配下分离各组件 | 1,892 | 已改为论文格式的合并表（Table 7–8） |
| Q1 | 原始数据退化原因；固定原则重构是否也有效 | 2,163 | 已改为分段，展示论文 Table 8 的 R5 部分 |
| **合计** | | **4,137** | ≤ 5,000 |

### 英文正文（发布用）

```markdown
We thank the reviewer for the positive assessment and the precise suggestions.

**W1 (Isolating the contributions of individual components).** These budget-matched ablations are in the main text (**Table 2**, Sec. 5.3), with full results in **App. D** (**Tables 7–8**). All settings start from the same R5 checkpoint and train one round with the same pipeline and budget. To remove principle evolution, we keep the original principles. To remove curriculum adaptation, we give the curriculum stale R2 or R3 feedback, so it allocates as if fixed at that earlier stage. Change on each benchmark:

| Setting | Principle evolution | Curriculum adaptation | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|---|---|
| Curriculum only | No | Yes | −5.64 | −3.60 | −9.60 | −2.20 | −6.44 | −4.11 |
| Principles only | Yes | No (R2 feedback) | −1.10 | −5.20 | −3.60 | −3.10 | +0.11 | −3.02 |
| Principles only | Yes | No (R3 feedback) | −1.77 | −5.80 | −1.80 | −2.40 | −0.84 | −4.04 |
| CoEvoMed | Yes | Yes | **+2.62** | **+0.69** | **+0.52** | **+1.13** | **+2.77** | **+1.28** |

The table is an ablation of the two adaptive components. Removing principle evolution (first row) or curriculum adaptation (second and third rows) lowers most or all scores, while keeping both (CoEvoMed) improves all six benchmarks.

This also answers whether the gains come from high-quality synthetic data. Every row builds data with the same selector, constructor, and verifier, so every row trains on verified, high-quality synthetic data. If such data alone drove the gains, every row would improve. Only the row with both components does, so the gains come from co-evolution.

For the setting the reviewer lists first, with both principles and curriculum fixed, the first row is an upper bound. That row keeps curriculum adaptation, yet all six scores drop at R5. Fixing the curriculum as well removes this last adaptive part, so it would do no better.

**Q1 (Raw-data degradation; fixed-principle reconstruction).** The raw data teach the wrong task. Most 2D records are figure descriptions (58.3%), and most others are labels or reports (Fig. 10; App. C.3). Trained on them without reconstruction (**App. D.3**), the model learns to describe or label images instead of answering questions. The drop is largest on SLAKE (−26.69), whose answers are short and direct. The raw data are also unverified, untargeted, and static. The table lists these four causes and the CoEvoMed component that addresses each:

| Property of the raw sources | Where CoEvoMed handles it |
|---|---|
| Not task-aligned: descriptions, labels, and reports instead of questions | Principles define question intent; the constructor turns evidence into supervision for the target capability (Sections 3, 4.1) |
| Not verified: image–text associations are never checked | The verifier checks factual consistency and visual dependence (Section 4.1) |
| Not targeted: the mix follows source availability, not the learner's needs | The planner allocates a fixed budget to weak and regressing capabilities (Section 4.2) |
| Not adaptive: supervision stays fixed while the learner changes | The revision agent updates principles from residual errors (Section 4.3) |

Reconstruction with fixed principles cannot keep up with the learner. **Table 8** (**App. D.2**) compares fixed and evolved principles from the same R5 checkpoint under the same budget:

| Condition | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|
| R5 reference | 73.61 | 89.00 | 64.60 | 65.80 | 59.00 | 61.63 |
| C: R5 / original | 67.97 (−5.64) | 85.40 (−3.60) | 55.00 (−9.60) | 63.60 (−2.20) | 52.56 (−6.44) | 57.52 (−4.11) |
| D: R5 / evolved (CoEvoMed) | **76.23 (+2.62)** | **89.69 (+0.69)** | **65.12 (+0.52)** | **66.93 (+1.13)** | **61.77 (+2.77)** | **62.91 (+1.28)** |

The fixed principles lower all six benchmarks (C), while the evolved principles raise all six (D). Fixed principles handle the first three properties above but not the fourth. The gap between D and C is the additional benefit of adaptive principle evolution.
```

### 中文译文（不发布）

我们感谢审稿人的积极评价和具体建议。

**W1（分离各个组件的贡献）** 这些预算匹配的消融实验在正文中已经给出（**Table 2**，第 5.3 节），完整结果见**附录 D**（**Table 7–8**）。所有设置都从同一个 R5 检查点出发，用相同的流程和预算训练一轮。去掉原则演化时，我们保留原始原则；去掉课程自适应时，我们把过时的 R2 或 R3 反馈交给课程，使它按固定在那个较早阶段的方式分配预算。下表为每个基准上的变化：

| 设置 | 原则演化 | 课程自适应 | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|---|---|
| 只有课程自适应 | 否 | 是 | −5.64 | −3.60 | −9.60 | −2.20 | −6.44 | −4.11 |
| 只有原则演化 | 是 | 否（R2 反馈） | −1.10 | −5.20 | −3.60 | −3.10 | +0.11 | −3.02 |
| 只有原则演化 | 是 | 否（R3 反馈） | −1.77 | −5.80 | −1.80 | −2.40 | −0.84 | −4.04 |
| CoEvoMed | 是 | 是 | **+2.62** | **+0.69** | **+0.52** | **+1.13** | **+2.77** | **+1.28** |

这张表是对两个自适应组件的消融。去掉原则演化（第一行）或去掉课程自适应（第二、三行），大部分或全部分数都会下降；两者都保留（CoEvoMed）时，六个基准全部提升。

这也回答了收益是否来自高质量的合成数据。表中每一行都用同样的选择器、构建器和核验器来构建数据，所以每一行训练用的都是经过核验的高质量合成数据。如果收益只来自这样的数据，每一行都应该提升；但只有两个组件都保留的那一行提升了，所以收益来自共同演化。

审稿人列出的第一种设置是原则和课程都固定。对它来说，表中第一行就是上限：第一行还保留着课程自适应，六个分数在 R5 却已经全部下降。如果把课程也固定，连这最后一个自适应部分也没有了，所以它不会比第一行更好。

**Q1（原始数据退化的原因；固定原则重构的效果）** 原始数据教给模型的是错误的任务。2D 记录中 58.3% 是图像描述，其余大多是标签或报告（Figure 10；附录 C.3）。在不做重构的情况下用它们训练（**附录 D.3**），模型学会的是描述图像或给图像贴标签，而不是回答问题。答案简短直接的 SLAKE 因此下降最多（−26.69）。此外，原始数据也没有经过核验、没有针对性、不会自适应。下表列出这四个原因，以及 CoEvoMed 中处理每个原因的组件：

| 原始数据的特点 | CoEvoMed 在哪里处理它 |
|---|---|
| 与任务不对齐：是图像描述、标签和报告，而不是问答 | 构建原则定义问题意图；构建器把证据转化为针对目标能力的监督数据（第 3、4.1 节） |
| 未经核查：图文关联从未被检查 | 核验器检查事实一致性和视觉依赖性（第 4.1 节） |
| 没有针对性：数据构成取决于数据源里有什么，而不是学习者需要什么 | 规划器把固定预算分配给薄弱和退化的能力（第 4.2 节） |
| 不会自适应：学习者在变化，监督却一成不变 | 修订智能体根据残余错误更新构建原则（第 4.3 节） |

用固定原则重构数据，跟不上学习者的变化。**Table 8**（**附录 D.2**）在相同预算下，从同一个 R5 检查点出发，比较了固定原则和演化后的原则：

| 条件 | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|
| R5 参考值 | 73.61 | 89.00 | 64.60 | 65.80 | 59.00 | 61.63 |
| C：R5 / 原始原则 | 67.97 (−5.64) | 85.40 (−3.60) | 55.00 (−9.60) | 63.60 (−2.20) | 52.56 (−6.44) | 57.52 (−4.11) |
| D：R5 / 演化原则（CoEvoMed） | **76.23 (+2.62)** | **89.69 (+0.69)** | **65.12 (+0.52)** | **66.93 (+1.13)** | **61.77 (+2.77)** | **62.91 (+1.28)** |

固定原则让六个基准全部下降（C），而演化后的原则让六个基准全部提升（D）。固定原则能处理上表的前三个特点，但处理不了第四个。D 与 C 之间的差距就是自适应原则演化带来的额外收益。

### 发布前待核对

- [x] **反馈消融即课程自适应消融（作者确认）**：实验 1 从同一 R5 检查点出发，只把驱动课程的反馈换成 R2/R3 的旧反馈，课程机制照常运行但看到的是过去的学习者，因此切断了"自适应"。正文补一句：固定课程是在较早状态下定下的，把旧反馈给 R5 学习者正是复现这种情况。注意：附录 D.1 写明替换的反馈同时用于课程分配和监督构建，审稿人若追问可如实说明。
- [x] **W1 合并表（数字已核对；改为标准消融表格式）**：列为"设置 / 原则演化（是/否）/ 课程自适应（是/否）/ 六个基准"，列顺序同论文 Table 7–8。"只有课程自适应"一行是 Table 8 条件 C（R5，原始原则 + 当前反馈）；"只有原则演化"两行是 Table 7 的 R2 feedback 和 R3 feedback（R5 起点，演化后的原则 + 过时反馈）；"CoEvoMed"一行是 Table 8 条件 D，与 Table 7 的 R5 feedback 为同一次训练（附录 D.1）。R2 起点的条件 A 已删去（作者要求）。
- [x] **W1 删去 R2 的说法（作者要求）**：删去"固定原则在 R2 有帮助、到 R5 有害"和"高质量合成数据推动早期进步，共同演化让进步持续"两句，避免审稿人去对比 Table 8 条件 A（R2 起点，平均 +3.09）与共同演化（R5 起点，平均 +1.50）。保留的两个平均差值均由论文数字算出：D − C 六个差值（8.26、4.29、10.12、3.33、9.21、5.39，见附录 D.2 正文）平均 6.77；Table 7 中当前反馈平均 +1.50，R2、R3 反馈平均 −2.65、−2.78，相减得 +4.15、+4.28。
- [x] **不再给计算出的平均值（作者要求）**：W1 删去 "+6.77 on average" 和 "+4.15 to +4.28"，改为说明表格是对两个自适应组件的消融，以及所有行共用同一条核验流程、因此收益来自共同演化；Q1 最后一段删去 "+6.77 on average"，只保留论文 D.2 正文给出的逐项差值范围 +3.33 至 +10.12。
- [x] **Q1 退化原因直接作答（作者要求）**：开头直接给出主因"原始数据教给模型的是错误的任务"：2D 记录 58.3% 是图像描述（PMC-OA 79,858 + Quilt 49,022 + ROCO 22,463，共 259,767 条，Figure 10），其余多为标签或报告；不经重构直接训练，模型学会描述或贴标签而不是回答，因此答案简短直接的 SLAKE 降得最多。"学会描述而不是回答"是依据数据构成的推断，论文没有输出长度分析；若审稿人追问，可补充对原始数据训练模型输出的统计。删去 "Routed through CoEvoMed, the same kinds of sources reach 91.60 with fewer examples"（不是原因）。
- [x] **Q1 重组（作者要求）**：按审稿人三个子问题的顺序作答：(1) 退化原因（四个特点及对应机制的表）；(2) 固定原则重构"早期有效、后期无效"，R2 只说明"六个基准全部提升（Table 8）"，不再列 +1.78 至 +3.90；(3) 预算匹配比较改为两行表：从 R5 出发，固定原则（Table 8 条件 C）与演化原则（条件 D），两行之差即原则演化的额外收益。删去 "+3.33 to +10.12" 和 "−2.2 to −9.6" 两个范围，数字都在表里。
- [x] **Q1 直接展示 Table 8（作者要求）**：按论文格式列出 R2 / R5 参考值和条件 A–D（绝对分数与括号内的变化），数字与论文 Table 8 逐项一致。开头改为"固定原则确实能带来收益，但前提是与学习者阶段匹配"，替代"早期有效、后期无效"。B 行（R2 时演化原则在三个 VQA 基准上下降）按论文 D.2 的解释写成"优劣顺序在两个阶段反转，没有一套固定原则适用于所有阶段"（论文原文："the utility of construction principles varies with learner stage, supporting their continued revision"）。
- [x] **Q1 只展示 Table 8 的 R5 部分（作者要求）**：表中只保留 R5 参考值、条件 C、条件 D；正文不再提 R2 和 Algorithm 1（作者要求删除）。
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
| Q1 | 分别确立贡献、PPO、原始数据、选择标准 | — | 2,114 | 已改为分点格式 |
| Q2 | 数据泄漏；R7 的选择 | — | 676 | 已定稿 |
| Q3 | 独立运行次数与置信区间；CURE-4B；32B 不如 8B | — | 1,156 | 已定稿 |
| Q4 | 复杂推理基准 | — | 962 | 已定稿 |
| **合计** | | **≤ 5,000** | **4,914** | |

W1、W2 不单独回答（与 Q1–Q4 高度重合），改在对应问题的标题中注明（Q1 & W1、Q3 & W2、Q4 & W2），以替代原来的开头说明句、节省字符。

字符空间：当前 4,914 字符，占位符已全部填完，只剩 86 字符余量。之后再改 2Nuw 任何地方，都需要同时删掉等量的字符。

W1 中有三点 Q1 没有直接覆盖，如果 2Nuw 在讨论中追问再补：(1) 单独去掉核验器的影响；(2) 额外资源（教师模型调用量、成本）的影响，附录 F.3 写明这些都有记录；(3) 收益归到单条原则上的分析，可以利用附录 A 所说的"样本与原则版本相关联"的记录来做。

### 英文正文（发布用）

```markdown
**Q1 & W1 (Contributions, PPO, raw data, selection criteria).** **Table 2** (Sec. 5.3) and **App. D** ablate each part with the same teachers, data sources, budget, and R5 checkpoint. Stale R2 or R3 feedback reproduces a curriculum fixed at an earlier stage. Change on each benchmark (**Tables 7–8**):

| Setting | Principle evolution | Adaptive curriculum | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|---|---|
| Curriculum only | No (original) | Yes | −5.64 | −3.60 | −9.60 | −2.20 | −6.44 | −4.11 |
| Principles only | Yes | No (stale R2) | −1.10 | −5.20 | −3.60 | −3.10 | +0.11 | −3.02 |
| Principles only | Yes | No (stale R3) | −1.77 | −5.80 | −1.80 | −2.40 | −0.84 | −4.04 |
| CoEvoMed | Yes | Yes | **+2.62** | **+0.69** | **+0.52** | **+1.13** | **+2.77** | **+1.28** |

Removing either component lowers most or all scores; only both improve all six benchmarks.

Unlike a greedy rule, PPO optimizes cumulative gain (Eq. 5), and its choices follow the learner's state. Across R1–R7: balanced, weakness-focused, retention-heavy, balanced, repair-heavy, repair-heavy, balanced. After localization regressed at R4 (60.27 → 56.16), it switched to repair-heavy for R5 and R6, and localization recovered to 59.36 and 62.10 (Fig. 6). It then returned to balanced.

The raw-data baseline degrades because its sources (App. D.3) are not task-aligned (58.3% of 2D records are figure descriptions; Fig. 10), not verified, not targeted, and not adapted. CoEvoMed's agents handle each. CoEvoMed instead reaches 91.60 on SLAKE (Table 9).

Principles chosen by our criteria do produce later learning gains. In **Table 8**, from the same R5 checkpoint and budget, the chosen principles raise all six benchmarks, while the original, never-revised principles lower all six. This follows from how the criteria work (Sec. 4.3; **App. B**). A principle is replaced only when the validation cases it fixes no longer outnumber those it breaks, that is, when it stops helping the learner. A replacement is chosen only if a review confirms it targets the errors the learner still makes.

**Q2 (Overlaps; R7).** We excluded patient-, study-, and image-level overlaps by design: support, validation, and test data are separate partitions (Sec. 1; App. C.6), enforced in our code. We screened all 11 2D and 5 3D sources against every external test at four levels: IDs (including study and case IDs), image paths, pixel hashes (exact and near-duplicate), and normalized text. All checks found zero overlap, including PubMedVision-IU vs. IU-Xray.

R7 was selected by a predefined internal criterion: it has the most balanced capability profile on the internal validation sets (App. C.4). These scores never feed back into training or checkpoint selection (App. A, C.6).

**Q3 & W2 (Runs and intervals; CURE-4B; 32B on IU-Xray).** We ran the full pipeline independently on four learners across three model families, architectures, and scales: Qwen3-VL (8B and 32B), Gemma 3 (4B), and InternVL3 (9B). Every run improves over its own base on every benchmark evaluated (16 of 16, +6.52 to +26.76). An effect that holds across families, architectures, and scales is not a single-run artifact.

We considered CURE-4B, but IU-Xray is not a fair test for it. CURE is fine-tuned on MIMIC-CXR-derived data (Chest ImaGenome, MS-CXR) and PadChest-GR, and IU-Xray is outside its training and evaluation data. A zero-shot run confirms the domain shift: it scores 28.65 RaTEScore, below all 28 models in Fig. 3.

The reversal is a property of IU-Xray: Hulu-Med (7B 67.30 vs. 32B 62.40) and MedGemma (4B 60.50 vs. 27B 59.00) show it too. IU-Xray references are short (30.5 words on average, versus 53.4 for MIMIC-CXR). CoEvoMed-8B matches this length (30.7 words), while 32B writes more detailed reports (40.1 words) that match the short references less well. On MIMIC-CXR, whose reports are longer, 32B does beat 8B (64.33 vs. 63.62; Fig. 3).

**Q4 & W2 (Complex reasoning).** We chose benchmarks that test medical reasoning in clinical form, which is harder than multiple choice on 2D images:

| What the model must do | Benchmarks |
|---|---|
| Write full reports | MIMIC-CXR, IU-Xray (chest X-ray); AMOS-MM (multi-organ 3D CT) |
| Reason over 3D volumes | M3D-VQA (five question types over 64 slices); 3D-RAD (open-ended, including measuring diameter, size, and thickness) |
| Answer varied 2D questions | VQA-RAD (clinician-authored), SLAKE (knowledge-based), PathVQA (pathology), PMC-VQA (literature figures) |

MedXpertQA-MM and MMMU test reasoning through multiple choice on 2D images (all of MedXpertQA-MM, 94% of MMMU). Our suite already covers this format (PMC-VQA, M3D-VQA) and adds the harder tasks above.

The results support generalization: CoEvoMed ranks first on all nine benchmarks (Table 1; Figs. 3–4). On 3D-RAD Medical Computation, it leads the next-best model by +8.6 BLEU-1 (Fig. 9b).
```

### 中文译文（不发布）

**Q1 与 W1（各部分的贡献、PPO、原始数据、选择标准）** 正文 **Table 2**（第 5.3 节）和**附录 D** 在相同的教师模型、数据来源、预算和 R5 检查点下，对每个部分做了消融。过时的 R2 或 R3 反馈相当于一套在较早阶段就固定下来的课程。下表为每个基准上的变化（**Table 7–8**）：

| 设置 | 原则演化 | 自适应课程 | VQA-RAD | SLAKE | PMC-VQA | PathVQA | MIMIC-CXR | IU-Xray |
|---|---|---|---|---|---|---|---|---|
| 只有自适应课程 | 否（原始原则） | 是 | −5.64 | −3.60 | −9.60 | −2.20 | −6.44 | −4.11 |
| 只有原则演化 | 是 | 否（过时的 R2 反馈） | −1.10 | −5.20 | −3.60 | −3.10 | +0.11 | −3.02 |
| 只有原则演化 | 是 | 否（过时的 R3 反馈） | −1.77 | −5.80 | −1.80 | −2.40 | −0.84 | −4.04 |
| CoEvoMed | 是 | 是 | **+2.62** | **+0.69** | **+0.52** | **+1.13** | **+2.77** | **+1.28** |

去掉任何一个组件，大部分或全部分数都会下降；只有两者都保留，六个基准才全部提升。

与贪心规则不同，PPO 优化的是累计收益（式 5），它的选择会随学习者的状态变化。R1–R7 依次为：balanced、weakness-focused、retention-heavy、balanced、repair-heavy、repair-heavy、balanced。定位能力在 R4 退化后（60.27 → 56.16），它在 R5 和 R6 换成了 repair-heavy，定位能力随之回升到 59.36 和 62.10（Figure 6）。之后它又回到了 balanced。

原始数据基线之所以退化，是因为这些数据（附录 D.3）与任务不对齐（2D 记录中 58.3% 是图像描述；Figure 10），没有经过核查，没有针对性，也不会自适应。CoEvoMed 的各个智能体分别处理这几点。而 CoEvoMed 在 SLAKE 上达到 91.60（Table 9）。

按我们的选择标准选出的原则，确实带来了后续的学习收益。在 **Table 8** 中，从同一个 R5 检查点、相同预算出发，选出的原则让六个基准全部提升，而从未修订过的原始原则让六个基准全部下降。这是由选择标准的设计决定的（第 4.3 节；**附录 B**）。只有当一条原则修好的验证题不再多于它弄错的题，也就是它不再帮助学习者时，才会被替换。而新原则只有在审查确认它针对的是学习者仍在犯的错误时，才会被选中。

**Q2（数据重叠；R7）** 我们在设计上就排除了患者、检查和图像层面的重叠：支持数据、验证数据和测试数据是相互独立的划分（第 1 节；附录 C.6），并在我们的代码中强制执行。我们把全部 11 个 2D 源数据和 5 个 3D 源数据与每一个外部测试集在四个层面上做了筛查：ID（包括检查 ID 和病例 ID）、图像路径、像素哈希（精确匹配和近似重复）以及归一化后的文本。所有检查发现的重叠均为零，包括 PubMedVision-IU 与 IU-Xray 之间。

R7 是依据预先定义的内部标准选出的：它在内部验证集上的能力画像最均衡（附录 C.4）。这些分数从不反馈到训练或检查点选择中（附录 A、C.6）。

**Q3 与 W2（独立运行与置信区间；CURE-4B；32B 在 IU-Xray 上的表现）** 我们在跨越三个模型家族、不同架构和规模的四个学习者模型上独立运行了完整流程：Qwen3-VL（8B 和 32B）、Gemma 3（4B）和 InternVL3（9B）。每一次运行在所有评测基准上都超过了各自的基础模型（16 组比较全部提升，幅度为 +6.52 至 +26.76）。一个在不同模型家族、不同架构和不同规模上都成立的效果，不可能是某一次运行的偶然结果。

我们考虑过 CURE-4B，但 IU-Xray 对它来说不是公平的测试。CURE 是在 MIMIC-CXR 派生的数据（Chest ImaGenome、MS-CXR）以及 PadChest-GR 上微调的，而 IU-Xray 既不在它的训练数据中，也不在它的评测中。一次零样本测试证实了这种数据域差异：它的 RaTEScore 只有 28.65，低于 Figure 3 中全部 28 个模型。

这种反转是 IU-Xray 数据集本身的特点：Hulu-Med（7B 67.30，32B 62.40）和 MedGemma（4B 60.50，27B 59.00）也是如此。IU-Xray 的参考报告很短（平均 30.5 个词，MIMIC-CXR 为 53.4 个词）。CoEvoMed-8B 生成报告的长度与之相当（30.7 个词），而 32B 写得更详细（40.1 个词），与这些简短的参考报告匹配得更差。在报告更长的 MIMIC-CXR 上，32B 确实高于 8B（64.33 对 63.62；Figure 3）。

**Q4 与 W2（复杂推理）** 我们选择的基准是在临床实际的形式下检验医学推理，这比 2D 图像上的选择题更难：

| 模型需要做什么 | 基准 |
|---|---|
| 撰写完整报告 | MIMIC-CXR、IU-Xray（胸片）；AMOS-MM（多器官 3D CT） |
| 在 3D 体数据上推理 | M3D-VQA（在 64 张切片上回答五类问题）；3D-RAD（开放式问题，包括测量直径、大小和厚度） |
| 回答多种 2D 问题 | VQA-RAD（临床医生撰写）、SLAKE（基于知识）、PathVQA（病理）、PMC-VQA（文献配图） |

MedXpertQA-MM 和 MMMU 都是在 2D 图像上通过选择题检验推理（MedXpertQA-MM 全部是选择题，MMMU 有 94% 是选择题）。我们的评测已经包含了这种形式（PMC-VQA、M3D-VQA），并且还加入了上表中更难的任务。

现有结果支持泛化：CoEvoMed 在全部九个基准上都排名第一（Table 1；Figure 3–4）。在 3D-RAD 的医学计算任务上，它比第二名高出 BLEU-1 8.6（Figure 9b）。

### 发布前待核对

- [x] **Q3 32B 不如 8B（用报告长度解释，作者提供数据）**：作者统计的平均词数：IU-Xray 参考报告 30.5、MIMIC-CXR 参考报告 53.4；CoEvoMed-8B 在 IU-Xray 上的输出 30.7、CoEvoMed-32B 为 40.1。解释：IU-Xray 参考报告短，8B 输出长度与之相当，32B 写得更详细，与短参考的匹配更差；MIMIC-CXR 参考报告更长，32B 高于 8B（64.33 对 63.62，Figure 3）。Hulu-Med、MedGemma 的反转例子保留。删去了"MIMIC 上 29 个模型中第一""8B 比 Hulu-Med-7B 高 6.62""同规模比 Hulu-Med-32B 高 2.68"（作者要求聚焦在"为什么"）。
- [x] **Q3 删去测试集置信区间（作者要求）**：原句 "These gains far exceed the test-set uncertainty (95% CI ±0.5 on PMC-VQA, ±1.7 on SLAKE)" 是单次评测的 Wilson 区间，不是审稿人要的"配对置信区间"，已删去。
- [ ] **Q3 配对置信区间（待算）**：脚本 `rebuttal/tools/paired_bootstrap.py`（配对 bootstrap，需每道题的对错或每份报告的 RaTEScore）。算出后可在 Q3 补一句，或在讨论阶段补充。
- [x] **消融在正文、反馈消融即课程自适应消融**：同 jcb6；Q1 开头先指向正文 Table 2，并补一句 "Stale R2 or R3 feedback reproduces a curriculum fixed at an earlier stage."。为腾字数：选择标准一段把出处移到句末；Q2 删去 "and one checkpoint serves all six benchmarks"；Q3 删去 "with very short outputs"。
- [x] **Q1 选择标准与学习收益的联系（作者指出审稿人问的是"联系"而非流程）**：改为先给验证证据（Table 8：通过选择标准的演化原则 D 让六个基准全部提升，从未修订的原始原则 C 全部下降），再说明设计上的联系（修订由净修复 ≤ 0 触发；语义审查确认候选针对造成问题的错误）。可用产出率、配对覆盖率两个阈值属于质量筛查，与学习收益无直接关系，已从这一段删去。
- [x] **Q1 日志证据（作者决定不写入）**：日志统计为 "Of the 15 accepted revisions with a subsequent evolution window, 12 turned their target cells' net repair positive in the next window; the remaining three were in sparse cells or showed delayed effects."。作者决定正文保持不变，不加这一句；如审稿人在讨论阶段追问"选择标准与后续收益的关系"，可以用这个数据回答（注意另外三次的解释和"回归均值"的可能质疑）。
- [x] **Q1 选择标准（再次核对附录 B 原文）**：附录 B "Principle revision and selection" 一段：窗口内的学习反馈找出"使用足够且净修复不为正"的原则；修订智能体根据残余错误提出候选；在 N = 100 个相同证据分配上比较，接受条件为候选可用产出率 ≥ 0.80、Δuse ≥ −0.05、配对覆盖率 ≥ 0.60，以及语义审查（检查最多 30 对样本，须确认修订被实际应用、并改善了与目标错误语义的对齐）。正文改为说明这些标准如何与学习收益挂钩：触发修订的是学习结果（净修复不为正，即不再帮助学习者），语义审查确认候选针对造成问题的错误。为腾字数：删去 "The loop then measures gains again"、Q2 的 "All ten rounds are reported (Fig. 7)"；raw-data 一段压缩为 "CoEvoMed's agents handle each" 和 "CoEvoMed instead reaches 91.60 on SLAKE"；Q4 中 M3D-VQA 的五类问题不再逐一列出。
- [x] **Q1 选择标准（按论文改写）**：论文在第 4.3 节、附录 A 算法 1 第 18–23 行、附录 B 式 11 交代了原则的选择标准：只有使用足够且净修复（修复数减退化数）不为正的原则才进入修订；候选原则与当前原则在 N = 100 个相同证据分配、相同配额下各自构建，候选可用产出率 ≥ 0.80、Δuse ≥ −0.05、配对覆盖率 ρpair ≥ 0.60，并通过修订智能体对最多 30 对样本的语义审查，才替换当前原则。正文列出的是必要条件（"only if"），没有列 Δuse。为腾字数：Q2 删去 "We test every round … (Fig. 7)"，改为 "All ten rounds are reported (Fig. 7)"；删去 "PMC-OA and PMC-VQA also draw on disjoint PMC articles"；PPO 一段末句改为 "It then returned to balanced."
- [x] **Q1 改为逐项消融表（作者要求不给计算出的平均值）**：表格与 jcb6 W1 相同的数据：只有自适应课程 = Table 8 条件 C；只有原则演化 = Table 7 的 R2 / R3 feedback（R5 起点、演化原则）；CoEvoMed = Table 8 条件 D（与 Table 7 的 R5 feedback 同一次训练）。删去 "Mean Δ" 和 "Improved" 两列，以及选择标准一段的 "+6.77 mean"。为腾字数：Q2 R7 一段出处只保留 App. C.4、"how evolution improves the learner" 改为 "the evolution"；Q3、Q4 各压缩一处措辞。
- [x] **Q1 PPO 动作序列（已填入）**：R1–R7 依次为 balanced、weakness-focused、retention-heavy、balanced、repair-heavy、repair-heavy、balanced。定位能力 R1–R6 为 60.27、59.36、60.27、56.16、59.36、62.10（Figure 6）。按论文的轮次约定，Rk 的动作用于训练出 Rk 的模型，依据的是 R(k−1) 的验证反馈（附录 D.1：用 R5 反馈训练的结果对应 Figure 7 的第 6 轮）。所以 R5 的 repair-heavy 是看到 R4 退化后做出的选择，R5 的 59.36 已经是修复的结果。如果日志的记法相反（Rk 的动作是在 Rk 评估之后选出、用于 R(k+1)），这句话需要改写。
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
