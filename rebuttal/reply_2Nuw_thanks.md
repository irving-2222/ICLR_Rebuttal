# Follow-up reply to Reviewer 2Nuw (after the rating increase)

Paste the title into the Title field and the comment block into the Comment field. The optional sentence and the Chinese translation below are for reference only.

**Title:**

```text
Thank you for the updated assessment
```

**Comment:**

````markdown
Thank you for reading our responses and for raising your rating. We are glad that the new ablations, the MMMU results, and the clarifications on data separation and checkpoint selection address most of your concerns. All of them are now in the revised PDF (**App. C.2, C.4, C.6, D.4–D.7**).

We agree on run-to-run stability. The three sampling seeds measure the decoding variability of one checkpoint, not the variability across training runs, and **App. C.4** now states that each learner was trained once. The training-level evidence we have is that the pipeline, run independently on four learners from three model families, improves over each base in all 16 comparisons (**Sec. 5.1; App. B**).

Thank you again for the constructive review.
````

**Optional sentence** (add at the end of the second paragraph only if you can run it for the final version):

```text
We will add repeated training runs of CoEvoMed-8B to the final version.
```

---

## 中文对照（不发布）

**标题：** 感谢您更新评价

**正文：**

感谢您阅读我们的回复并提高评分。很高兴新增的消融实验、MMMU 结果，以及关于数据隔离和检查点选择的说明解决了您的大部分疑虑。这些内容都已写入修订版 PDF（**附录 C.2、C.4、C.6、D.4–D.7**）。

关于多次训练之间的稳定性，我们同意您的看法。三个采样种子衡量的是同一个检查点的解码波动，而不是不同训练之间的波动；**附录 C.4** 也已写明每个学习者模型只训练了一次。我们目前在训练层面的证据是：这套流程在来自三个模型家族的四个学习者上各自独立运行，在全部 16 组比较中都超过了各自的基础模型（**第 5.1 节；附录 B**）。

再次感谢您富有建设性的审稿意见。

**可选句：** 我们会在最终版中加入 CoEvoMed-8B 的多次独立训练结果。（只有在确定能做到时才加。）
