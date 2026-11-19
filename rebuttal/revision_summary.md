# Summary of revisions (general comment to all reviewers)

Paste the title into the Title field and the comment block into the Comment field. The Chinese translation at the end is for reference only and is not posted.

**Title:**

```text
Thank you to all reviewers: summary of revisions in the updated PDF
```

**Comment:**

````markdown
We thank all reviewers for their feedback. We have uploaded a revised PDF in which all new or changed text is shown in blue. Section, table, figure, and equation numbers from the submission are unchanged, so the references in our responses still apply; new tables are numbered R1–R5. The main text remains nine pages.

**Main text**

| Location | Change | Reviewers |
|---|---|---|
| Sec. 5.3, Table 2 | States that panel A ablates curriculum adaptation and panel B ablates principle evolution, and points to the further ablations in App. D | pUjh, jcb6, 2Nuw |

**Appendix**

| Location | Change | Reviewers |
|---|---|---|
| App. C.2, Table R1 | MedVLSynther retrained on our Qwen3-VL-8B base, next to its published results | pUjh (Q1) |
| App. C.2 | MMMU Health & Medicine results (1,752 questions) | 2Nuw (Q4) |
| App. C.3 | Agreement of our capability labels with SLAKE's native labels on 200 questions | pUjh (Q3) |
| App. C.4, Table R2 | Standard deviations over three decoding seeds, and paired 95% CIs against Hulu-Med-7B re-evaluated under the same protocol (Qwen3.6-27B on MIMIC-CXR) | 2Nuw (Q3) |
| App. C.4 | Checkpoint selection rule: the highest equal-weight mean of QA and report validation scores | pUjh (W3), 2Nuw (Q2) |
| App. C.6 | Overlap screening between all support sources and the external test sets | 2Nuw (Q2) |
| App. D, Table R3 | Retitled "Ablations of CoEvoMed's components"; a map from each component to its ablations; D.1 and D.2 titles name the ablated component | pUjh, jcb6, 2Nuw |
| App. D.3, Table 9 | Report benchmarks added, and a run with fixed principles from the base under the same total budget | jcb6 (W1, Q1) |
| App. D.4, Table R4 (new) | All four combinations of principle evolution and curriculum adaptation | jcb6 (W1), 2Nuw (Q1) |
| App. D.5, Table R5 (new) | Replacing individual agents: random evidence for the selector, no verifier, and a single agent | pUjh (W1) |
| App. D.6 (new) | Forgetting measurements and the zero-retention ablation | pUjh (W3) |
| App. D.7 (new) | Learning gains after accepted principle revisions | 2Nuw (Q1) |

New references: Chaudhry et al. (2018), Landis & Koch (1977), and Yue et al. (2024, MMMU).
````

---

## 中文对照（不发布）

**标题：** 感谢各位审稿人：修订版 PDF 的修改汇总

**正文：**

感谢各位审稿人的意见。我们已上传修订版 PDF，所有新增或改动的文字都用蓝色标出。投稿版中的章节、表格、图和公式编号均未改变，因此各份回复中的引用仍然有效；新增表格编号为 R1–R5。正文仍为九页。

**正文**

| 位置 | 改动 | 对应审稿人 |
|---|---|---|
| 第 5.3 节、Table 2 | 写明 panel A 消融课程自适应、panel B 消融原则演化，并指向附录 D 中的其他消融 | pUjh、jcb6、2Nuw |

**附录**

| 位置 | 改动 | 对应审稿人 |
|---|---|---|
| 附录 C.2、Table R1 | 在我们的 Qwen3-VL-8B 基础模型上重新训练 MedVLSynther，与其发表结果并列 | pUjh（Q1） |
| 附录 C.2 | MMMU Health & Medicine 结果（1,752 题） | 2Nuw（Q4） |
| 附录 C.3 | 200 道 SLAKE 题上，我们的能力标签与 SLAKE 原生标签的一致性 | pUjh（Q3） |
| 附录 C.4、Table R2 | 三个解码种子的标准差，以及相对同协议重测的 Hulu-Med-7B 的 95% 配对置信区间（MIMIC-CXR 上为 Qwen3.6-27B） | 2Nuw（Q3） |
| 附录 C.4 | 检查点选择规则：问答与报告验证分数的等权平均最高 | pUjh（W3）、2Nuw（Q2） |
| 附录 C.6 | 全部支持数据源与外部测试集之间的重叠筛查 | 2Nuw（Q2） |
| 附录 D、Table R3 | 标题改为"Ablations of CoEvoMed's components"；新增组件与消融的对照表；D.1、D.2 标题注明所消融的组件 | pUjh、jcb6、2Nuw |
| 附录 D.3、Table 9 | 增加两个报告基准，以及从基础模型出发、同总预算的固定原则一行 | jcb6（W1、Q1） |
| 附录 D.4、Table R4（新增） | 原则演化与课程自适应的四种组合 | jcb6（W1）、2Nuw（Q1） |
| 附录 D.5、Table R5（新增） | 逐个替换智能体：选择器改为随机证据、去掉核验器、单智能体 | pUjh（W1） |
| 附录 D.6（新增） | 遗忘测量，以及保留份额设为 0 的消融 | pUjh（W3） |
| 附录 D.7（新增） | 被接受的原则修订之后的学习收益 | 2Nuw（Q1） |

新增参考文献：Chaudhry et al.（2018）、Landis & Koch（1977）、Yue et al.（2024，MMMU）。
