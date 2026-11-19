# Message to the Area Chair

Post as an Official Comment with the readers set to the Area Chairs (and Senior Area Chairs) only, if OpenReview offers that option. Paste the title into the Title field and the comment block into the Comment field. The Chinese translation below is for reference only.

**Title:**

```text
Thank you for handling our submission: summary of the discussion and revisions
```

**Comment:**

````markdown
Dear Area Chair,

Thank you for handling our submission. We summarize the discussion so far to support your assessment.

**Status.** Reviewer 2Nuw raised the rating to Weak Accept after our response, noting that the new ablations, the MMMU results, and the clarifications on data separation and checkpoint selection resolve most of their concerns. Reviewer jcb6 rated the paper Weak Accept. Reviewers pUjh and jcb6 have not yet responded to our rebuttal; we have sent each a short follow-up.

**Main concerns and new evidence** (revised PDF, changes in blue):

| Concern | Reviewers | New evidence | Location |
|---|---|---|---|
| Contribution of each component; necessity of the agents | pUjh, jcb6, 2Nuw | All four combinations of principle evolution and curriculum adaptation; replacing the selector, verifier, or revision agent, or merging all roles into a single agent, turns the round's gain into a loss; a map from components to ablations | App. D.4–D.5, Tables R3–R5 |
| Gains from more data rather than co-evolution | jcb6, 2Nuw | From the same base and under the same total budget, fixed principles trail CoEvoMed on all six benchmarks (by 1.35–7.76 points); raw data fall below the base on all six | App. D.3, Table 9 |
| Forgetting and retention | pUjh | Per-round forgetting and repair rates; average forgetting of 1.27 points at R7 and 2.84 at R10; a zero-retention ablation loses 6.9% of learned cases versus 3.3% | App. D.6 |
| Statistical reliability | 2Nuw | Standard deviations over three decoding seeds; paired 95% CIs against Hulu-Med-7B re-evaluated under the same protocol, all excluding zero | App. C.4, Table R2 |
| Data leakage; checkpoint selection | 2Nuw | Overlap screening at four levels with zero overlap; the selection rule on internal validation stated explicitly | App. C.6, C.4 |
| Baseline fairness; generalization | pUjh, 2Nuw | MedVLSynther retrained on our base; MMMU Health & Medicine results | App. C.2, Table R1 |
| Capability taxonomy | pUjh | Agreement with SLAKE's native labels (97.5%, Cohen's κ = 0.958) | App. C.3 |
| Organization | pUjh | Sec. 5.3 and App. D state which component each experiment ablates | Sec. 5.3; App. D |

The remaining point from Reviewer 2Nuw concerns stability across independent training runs. Each learner was trained once; the training-level evidence is that the pipeline, run independently on four learners from three model families, improves over each base in all 16 comparisons (Sec. 5.1; App. B).

All section, table, figure, and equation numbers from the submission are unchanged, and the main text remains nine pages.

Thank you for your time and consideration.
````

---

## 中文对照（不发布）

**标题：** 感谢您负责我们的投稿：讨论与修订情况汇总

**正文：**

尊敬的领域主席：

感谢您负责我们的投稿。我们将目前的讨论情况汇总如下，供您评估参考。

**进展。** 审稿人 2Nuw 在看过我们的回复后将评分提高到弱接收，并表示新增的消融实验、MMMU 结果，以及关于数据隔离和检查点选择的说明解决了其大部分疑虑。审稿人 jcb6 给出的评分为弱接收。审稿人 pUjh 和 jcb6 尚未回复我们的 rebuttal，我们已分别发送了简短的跟进消息。

**主要疑虑及新增证据**（修订版 PDF，改动以蓝色标出）：

| 疑虑 | 审稿人 | 新增证据 | 位置 |
|---|---|---|---|
| 各组件的贡献；智能体是否必要 | pUjh、jcb6、2Nuw | 原则演化与课程自适应的全部四种组合；替换选择器、核验器或修订智能体，或把所有角色合并为单个智能体，都会让这一轮从提升变为下降；组件与消融的对照表 | 附录 D.4–D.5，Table R3–R5 |
| 收益是否来自更多数据而非协同演化 | jcb6、2Nuw | 从同一基础模型出发、总预算相同，固定原则在六个基准上都低于 CoEvoMed（差 1.35–7.76 分）；原始数据在六个基准上都低于基础模型 | 附录 D.3，Table 9 |
| 遗忘与保留 | pUjh | 每轮遗忘率和修复率；平均遗忘在 R7 为 1.27 分、R10 为 2.84 分；保留份额设为 0 时丢掉 6.9% 的已学会题目，完整系统为 3.3% | 附录 D.6 |
| 统计可靠性 | 2Nuw | 三个解码种子的标准差；相对同协议重测的 Hulu-Med-7B 的 95% 配对置信区间，全部不含 0 | 附录 C.4，Table R2 |
| 数据泄漏；检查点选择 | 2Nuw | 四个层面的重叠筛查，均无重叠；明确写出基于内部验证集的选择规则 | 附录 C.6、C.4 |
| 基线公平性；泛化能力 | pUjh、2Nuw | 在我们的基础模型上重新训练 MedVLSynther；MMMU Health & Medicine 结果 | 附录 C.2，Table R1 |
| 能力分类体系 | pUjh | 与 SLAKE 原生标签的一致性（97.5%，Cohen's κ = 0.958） | 附录 C.3 |
| 论文组织 | pUjh | 第 5.3 节和附录 D 写明每个实验消融的是哪个组件 | 第 5.3 节；附录 D |

审稿人 2Nuw 剩下的一点是多次独立训练之间的稳定性。每个学习者模型只训练了一次；训练层面的证据是：这套流程在来自三个模型家族的四个学习者上各自独立运行，在全部 16 组比较中都超过了各自的基础模型（第 5.1 节；附录 B）。

投稿版中的章节、表格、图和公式编号均未改变，正文仍为九页。

感谢您的时间与考虑。
