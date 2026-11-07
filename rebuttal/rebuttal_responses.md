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
| 开头 | 致谢 | ~150 | — | 待写 |
| W1 | 多智能体是否必要 | ~1,450 | 1,451 | 草稿完成 |
| W2 | 论文组织 | ~350 | — | 待写 |
| W3 | 遗忘与 R7 的选择 | ~1,100 | — | 待写 |
| Q1 | MedVLSynther 复现 | ~300 | — | 待写 |
| Q2 | 数据公开 | ~200 | — | 待写 |
| Q3 | 能力分类体系 | ~1,000 | — | 待写 |
| 结尾 | | ~100 | — | 待写 |
| **合计** | | **≤ 5,000** | **1,451** | |

### 英文正文（发布用）

```markdown
**W1 (Are the agents necessary?)** Yes. Each agent performs a function the learner measurably depends on. In controlled comparisons from the same starting checkpoint, removing or decoupling an agent degrades performance, whereas the full pipeline improves it:

| Agent | Agent removed or decoupled | CoEvoMed |
|---|---|---|
| Construction agents (Table 9) | Raw data (~700K): all 4 VQA benchmarks fall below base; SLAKE 64.84 → 38.15 (−26.69) | Fewer examples: all 4 improve; SLAKE 64.84 → **91.60 (+26.76)** |
| Revision agent (Table 8, R5) | Original principles: 6/6 benchmarks decline (−2.2 to −9.6) | Revised principles: 6/6 improve (**+0.5 to +2.8**) |
| Planner (Table 7, R5) | Stale R2/R3 feedback: 11/12 scores decline | Current feedback: 6/6 improve |

Because the original principles perform better at R2, no fixed principle set suffices, and online revision is required. The roles must be separate because one agent cannot be both blind and sighted: the constructor writes only from selected source facts without seeing the image, while a different model verifies each example against the image. Every training claim is thus traceable to evidence and independently checked, which is essential for medical data. The same design transfers across four learners and 2D/3D tasks (VQA-RAD: +22.4 on Gemma-3-4B, +20.4 on InternVL3-9B). A substitute would have to perform these same functions, and our controls show that simpler alternatives fail.
```

### 中文译文（不发布）

**W1（这些智能体是否必要？）** 是的。每个智能体都承担着学习者可测量地依赖的功能。在从同一起始检查点出发的受控比较中，去掉或断开某个智能体会使性能下降，而完整流程会使性能提升：

| 智能体 | 去掉或断开该智能体 | CoEvoMed |
|---|---|---|
| 构建智能体（Table 9） | 原始数据（约 70 万条）：四个 VQA 基准全部低于基础模型；SLAKE 64.84 → 38.15（−26.69） | 样本更少：四个基准全部提升；SLAKE 64.84 → **91.60（+26.76）** |
| 修订智能体（Table 8，R5） | 原始原则：6/6 个基准下降（−2.2 至 −9.6） | 修订后的原则：6/6 个基准提升（**+0.5 至 +2.8**） |
| 规划器（Table 7，R5） | 过时的 R2/R3 反馈：12 个分数中 11 个下降 | 当前反馈：6/6 个基准提升 |

由于原始原则在 R2 时表现更好，任何一套固定原则都不够用，必须在线修订。这些角色必须分开，因为同一个智能体不可能既看不见图像又看得见图像：构建器只依据选中的原始事实撰写样本，看不到图像；另一个模型则对照图像核验每个样本。因此每条训练内容都可以追溯到证据，并经过独立核查，这对医学数据至关重要。同一套设计可以迁移到四个学习者模型以及 2D/3D 任务（VQA-RAD：Gemma-3-4B 上提升 22.4，InternVL3-9B 上提升 20.4）。任何替代方案都必须完成同样的功能，而我们的对照实验表明，更简单的方案都失败了。

### 发布前待核对

- [ ] **W1 修订智能体**：Exp 2 的条件 C 和 D 是否只在原则上不同（分配动作、预算一致）？正文把两者的差距归因于原则。
- [ ] **W1 规划器**：Exp 1 的三组是否使用相同的原则，只替换了反馈？
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

---

## Reviewer jcb6

评分 3（弱接收）· 信心 3 — 待写

---

## Reviewer 2Nuw

评分 2（弱拒绝）· 信心 4 — 待写
