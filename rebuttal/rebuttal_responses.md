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
| Q1 | MedVLSynther 复现 | ~800 | 797 | 草稿完成（复现结果待填） |
| Q2 | 数据公开 | ~150 | — | 待写 |
| Q3 | 能力分类体系 | ~950 | — | 待写 |
| 结尾 | | ~80 | — | 待写 |
| **合计** | | **≤ 5,000**（加入 Q1 后预计超出约 300，需压缩） | **4,088** | |

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

**Q1 (MedVLSynther base model).** Table 1 reports MedVLSynther-7B as published, on its own base (Qwen2.5-VL-7B) and protocol; this avoids re-tuning a baseline's recipe on a backbone it was not designed for. The informative comparison is the gain over each method's own base:

| Gain over own base | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther-7B (Qwen2.5-VL-7B, published) | +6.13 | +8.82 | +6.65 | +0.17 |
| MedVLSynther recipe (Qwen3-VL-8B, our run) | [+x.xx] | [+x.xx] | [+x.xx] | [+x.xx] |
| CoEvoMed-8B (Qwen3-VL-8B) | **+13.82** | **+25.72** | **+26.76** | **+26.63** |

For the same-base row, we trained Qwen3-VL-8B with the released MedSynVQA-13K data and GRPO script (reward function from the authors' MedVLThinker code) and evaluated it under our protocol.
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

**Q1（MedVLSynther 的基础模型）** Table 1 中的 MedVLSynther-7B 按其原文发表的结果报告，使用的是它自己的基础模型（Qwen2.5-VL-7B）和评测协议；这样可以避免在一个并非为其设计的骨干模型上重新调整基线的训练配方。因此，更有意义的比较是各方法相对其自身基础模型的提升：

| 相对自身基础模型的提升 | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
|---|---|---|---|---|
| MedVLSynther-7B（Qwen2.5-VL-7B，原文发表） | +6.13 | +8.82 | +6.65 | +0.17 |
| MedVLSynther 配方（Qwen3-VL-8B，我们复现） | [+x.xx] | [+x.xx] | [+x.xx] | [+x.xx] |
| CoEvoMed-8B（Qwen3-VL-8B） | **+13.82** | **+25.72** | **+26.76** | **+26.63** |

对于基础模型相同的那一行，我们用公开的 MedSynVQA-13K 数据和 GRPO 训练脚本训练 Qwen3-VL-8B（奖励函数取自作者的 MedVLThinker 代码），并在我们的评测协议下评估。

### 发布前待核对

- [ ] **W1 修订智能体**：Exp 2 的条件 C 和 D 是否只在原则上不同（分配动作、预算一致）？正文把两者的差距归因于原则。
- [ ] **W1 规划器**：Exp 1 的三组是否使用相同的原则，只替换了反馈？
- [ ] **W2 可选补充**：如果想在不让步的前提下给一个姿态，可以在 W2 末尾加一句（约 70 字符）：`We will add a role summary table to Section 4 for quick reference.`
- [x] **W3 回放数据**：已确认主实验每轮混入回放数据，W3 已写入 "mixes in replay data (Section 3.3)"。
- [ ] **R7 的选择依据（留给 2Nuw Q2）**：W3 只引用了论文的说法（按跨任务整体均衡性选定），没有说这个"整体均衡"是在内部验证集上还是外部基准上衡量的；论文也没写明。2Nuw 的 Q2 会直接问"R7 是否完全依据预先定义的内部验证标准选出"，需要你提供实际做法。
- [x] **W3 PathVQA 峰值**：已确认 PathVQA 的 R8 略高于 R7；R10 的 67.25 仍在峰值 3 分以内，正文说法成立。
- [ ] **Q1 占位符**：复现完成后填入四个 `[+x.xx]`，即复现模型得分减去 Qwen3-VL-8B 基础分（PMC-VQA 54.13、VQA-RAD 56.76、SLAKE 64.84、PathVQA 42.77）。如果某项提升超过 CoEvoMed，需要重新讨论写法。
- [ ] **Q1 数字来源**：确认 Table 1 的 MedVLSynther 数字引自其论文（与其 GitHub README 的数字完全一致）。正文写的是 "as published"。
- [ ] **Q1 与附录 C.1 的一致性**：C.1 写的是"本研究评估的基线与 CoEvoMed 使用相同的评估集和评分规则"，MedVLSynther 是引用数，与这句不符。Q1 已如实写明"按原文发表的结果和协议"；定稿时建议把 C.1 改为区分"我们评测的基线"和"引用原文的基线"。
- [ ] **字符超预算**：加入 Q1 后剩余空间不够写 Q2、Q3。Q3 写完后统一压缩约 300 字符，候选做法：去掉开头和结尾、W1 和 W3 各压约 100。
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

---

## Reviewer jcb6

评分 3（弱接收）· 信心 3 — 待写

---

## Reviewer 2Nuw

评分 2（弱拒绝）· 信心 4 — 待写
