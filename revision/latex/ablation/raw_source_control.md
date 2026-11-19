# 原始源数据直接训练对照

骨干：Qwen3-VL-8B。
Qwen3+Raw 直接使用 500,000 条原始 source data 训练。
两组采用相同的 Qwen3-VL-8B 起始模型。用户于 2026-09-20 确认 Raw 训练数据量显著大于 EvoForma；EvoForma 的确切训练样本数尚未提供，不计算数据量比例。
本条更正原有样本数匹配记录；论文不再将该实验称为“等预算对照”，不据此宣称 token 数或训练步数匹配。
实验目的：检验更大的原始训练数据规模能否复现 EvoForma 的增益，考察自适应监督构造与课程配置在数据规模之外的有效性。
准确率单位：%。截图列顺序按用户给定的 PMC、VQA-RAD、SLAKE、Path 记录。

| 模型 | PMC-VQA | VQA-RAD | SLAKE | PathVQA |
| --- | ---: | ---: | ---: | ---: |
| Qwen3-VL-8B (base) | 54.13 | 56.76 | 64.84 | 42.77 |
| Qwen3+Raw | 45.51 | 43.01 | 38.15 | 35.94 |
| EvoForma-8B | 67.95 | 82.48 | 91.60 | 69.40 |

Qwen3+Raw 来源：2026-09-19 用户提供截图 codex-clipboard-606a83de-8abc-4bf2-bfdc-46c0c8699591.png。
Base 与 EvoForma 来源：论文当前主表 sections/main_results_rows.tex。
EvoForma 相对 Raw 的提升依次为 22.44、39.47、53.45、33.46 个百分点。
