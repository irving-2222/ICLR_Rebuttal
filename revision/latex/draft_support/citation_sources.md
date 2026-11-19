# 初稿引用来源记录

初次检索日期：2026-09-05；最近核对日期：2026-09-26。中英文稿共同使用项目根目录的 `iclr2027_conference.bib`，当前共 71 条文献。本记录保存书目信息来源与引用用途。

## 2026-09-26：恢复 InternVL3 并补充已有模型与训练方法的出处

- 按作者最新要求，恢复 InternVL3 原始条目及中英文正文首次介绍该模型时的引用；此前删除记录作为历史保留。另补充下列六条出处，均对应稿件中已有的基线模型或训练方法，实验结果不变。
- 本次从 [ICLR 2027 官方模板包](https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip)重新核对 `.sty` 与 `.bst`，项目文件与官方版本逐字相同。保留原有字号、页边距、文献间距和附录分页指令，参考文献继续不显示 DOI 或 URL。

| 引用键 | 核实来源 | 引用位置与用途 |
|---|---|---|
| `sellergren2025medgemma` | [MedGemma 原始技术报告 v1](https://arxiv.org/abs/2507.05201v1) | 二维评测附录：主表中已有 MedGemma 基线的出处。 |
| `he2024meddr` | [MedDr 原始技术报告 v1](https://arxiv.org/abs/2404.15127v1) | 二维评测附录：主表中已有 MedDr 基线的出处。 |
| `li2026gmai` | [AAAI 2026 正式论文](https://ojs.aaai.org/index.php/AAAI/article/view/39485)、[注册元数据](https://api.crossref.org/works/10.1609/aaai.v40i28.39485) | 二维评测附录：主表中已有 GMAI-VL 基线的出处。 |
| `rajbhandari2020zero` | [SC20 正式论文](https://doi.org/10.1109/SC41405.2020.00024)、[作者机构页面](https://www.microsoft.com/en-us/research/publication/zero-memory-optimizations-toward-training-trillion-parameter-models/) | 附录 B：现有 DeepSpeed ZeRO-3 训练设置的算法出处。 |
| `bai2025qwen25` | [Qwen2.5-VL 技术报告](https://arxiv.org/abs/2502.13923) | 二维评测附录：报告生成图中已有 Qwen2.5-VL 基线的出处。 |
| `lin2025healthgpt` | [ICML 2025 正式论文](https://proceedings.mlr.press/v267/lin25n.html)、[正式论文 PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/lin25n/lin25n.pdf) | 二维评测附录：报告生成图中已有 HealthGPT 基线的出处。 |

- MedDr 明确引用 `2404.15127v1`：该原始版本题名为 MedDr，后续版本已更名为 GSCo。
- MedGemma 使用 2025 年原始报告，完整保留 79 名作者。arXiv 的机器元数据将 Dmitry 与 Lepikhin 拆成两个字段，依据可见作者列表合并为 Dmitry (Dima) Lepikhin；保留原有作者顺序。
- GMAI-VL 使用 AAAI 2026 正式发表信息及完整 19 名作者，包含 Shixiang Tang；保留卷 40、页码 23177–23185。会议条目不再同时设置期号，避免官方 BibTeX 样式关于卷与期同时使用的警告。
- HealthGPT 使用 ICML 2025 正式版本（PMLR 267，37975–37995）。PMLR 导出将 Xiaohui Song 的姓名字段颠倒，依据正式 PDF 首页改为 `Song, Xiaohui`。
- 最终中英文各有 71 条实际引用，原有 64 条书目信息不变。英文正文 9 页、全文 34 页，参考文献止于第 15 页；中文正文 8 页、全文 31 页。已检查参考文献及受影响正文、附录页面，编译无未定义引用和排版警告。

## 2026-09-26：按作者要求删除末页单独参考文献

- 此前从中英文引用列表移除 InternVL3 技术报告（`zhu2025internvl3`）及两处正文引用标记，保留模型介绍和实验结果；随后已按作者最新要求恢复，见上方记录。

## 2026-09-20：ICLR 2027 参考文献规范化

- 核对 [ICLR 2027 作者指南](https://iclr.cc/Conferences/2027/AuthorGuidelines)及[官方模板第 4.1 节](https://github.com/ICLR/Master-Template/blob/master/iclr2027/iclr2027_conference.tex)：正文使用 natbib 作者—年份引用，文献表按作者字母顺序排列，条目格式全文一致。项目 `.sty` 和 `.bst` 与官方文件逐字一致，未修改官方样式、字号或间距。
- 采用完整作者列表，由官方 `.bst` 输出；补全 Hulu-Med v2 和 Lingshu v1 的作者，保留原有版本链接。原书目中的 Table/Figure 定位说明移至本台账：Hulu-Med v2 的 Table 1、Figure 2(b)；Lingshu v1 的 Table 8。
- Gemma 3 的 `Jean-bastien Grill` 和 `Ju-yeong Ji` 改为显式姓、名字段，并保护连字符名字，避免 BibTeX 将小写名字组成部分解释为姓氏前缀。姓名拼写、作者顺序和导出中的重复贡献者记录保持不变。
- PMC-VQA 改引 *Communications Medicine* 4(1):277（2024）的正式期刊版本；保留原引用键 `zhang2024pmc`。
- 添加 InternVL3 原始技术报告，在中英文正文首次介绍该跨骨干学习者时引用。来源采用作者官方文档的 Citation 条目。
- 统一标题为句式大小写，保护模型名、方法名和缩写；预印本统一显示 `arXiv preprint arXiv:编号`。按已核实的正式元数据补入 Reflexion、DataEnvGym 和 Automated Design of Agentic Systems 的页码，统一作者大小写及 HTTPS 链接。不改动任何实验数值或 Evo-PI 的正文概括。
- 编译核验：中英文均输出 41 条参考文献，无未定义引用、BibTeX 错误或越界文本框；英文全文 32 页、中文全文 29 页，正文分别仍为 9 页与 8 页。已渲染核对正文新增引用、参考文献页及两处 Gemma 连字符姓名。

## 来源与允许的引用范围

| 引用键 | 原始 BibTeX / 元数据来源 | 支持的内容 |
|---|---|---|
| `matiisen2017teacher` | [原始来源](https://arxiv.org/bibtex/1707.00183) | 教师根据学生反馈选择任务；POMDP/历史依赖的课程视角。 |
| `schulman2017proximal` | [原始来源](https://arxiv.org/bibtex/1707.06347) | 课程策略的 PPO 更新；不支持“全部 Agent 联合 RL”表述。 |
| `schulman2016high` | [原始来源](https://dblp.org/rec/journals/corr/SchulmanMLJA15.bib) | 优势估计的 GAE 来源。 |
| `huang2026rzero` | [原始来源](https://proceedings.iclr.cc/paper_files/paper/6381-/bibtex) | Challenger–Solver 通过交互共同形成学习任务与能力。 |
| `yun2026graph` | [原始来源](https://proceedings.iclr.cc/paper_files/paper/6521-/bibtex) | 基于图结构的多智能体协作。 |
| `zhang2026viper` | [原始来源](https://proceedings.iclr.cc/paper_files/paper/10163-/bibtex) | 视觉感知能力的自进化。 |
| `zhang2026agentic` | [原始来源](https://proceedings.iclr.cc/paper_files/paper/9816-/bibtex) | ACE：通过生成、反思、整理演化上下文与策略。 |
| `xia2026mmedagent` | [原始来源](https://proceedings.iclr.cc/paper_files/paper/10947-/bibtex) | 多模态医学推理中的多智能体协作优化。 |
| `huang2026synthesizing` | [原始来源](https://proceedings.iclr.cc/paper_files/paper/7406-/bibtex) | 医学文档驱动的 Generator–Verifier 视觉问答合成。 |
| `wu2026k2` | [原始来源](https://proceedings.iclr.cc/paper_files/paper/6839-/bibtex) | 声明性知识和程序性知识协同演化的层次化设备控制。 |
| `xue2026comas` | [原始来源](https://proceedings.iclr.cc/paper_files/paper/7792-/bibtex) | 交互奖励驱动的多智能体协同演化。 |
| `liu2021slake` | [原始来源](https://api.crossref.org/works/10.1109/ISBI48211.2021.9434010/transform/application/x-bibtex) | SLAKE 数据集与语义/知识标注。 |
| `zhang2024pmc` | [正式期刊原文](https://www.nature.com/articles/s43856-024-00709-2) | PMC-VQA 数据集与医学视觉问答。 |
| `he2020pathvqa` | [原始来源](https://arxiv.org/bibtex/2003.10286) | PathVQA 病理视觉问答数据集。 |
| `bai2025qwen3` | [原始来源](https://arxiv.org/bibtex/2511.21631) | Qwen3-VL 骨干模型；不证明本项目已经训练完成。 |
| `gemmateam2025gemma` | [原始来源](https://arxiv.org/bibtex/2503.19786) | Gemma 3 模型家族；Gemma-3-4B-IT 跨模型验证的来源。 |
| `lau2018dataset` | [原始来源](https://api.crossref.org/works/10.1038/sdata.2018.251/transform/application/x-bibtex) | VQA-RAD 临床专家编写的放射图像问答。 |
| `johnson2019mimic` | [原始来源](https://api.crossref.org/works/10.1038/s41597-019-0322-0/transform/application/x-bibtex) | MIMIC-CXR 图像与自由文本报告。 |
| `demnerfushman2016preparing` | [原始来源](https://api.crossref.org/works/10.1093/jamia/ocv080/transform/application/x-bibtex) | IU-Xray/Open-i 放射检查图像及报告。 |
| `bengio2009curriculum` | [原始来源](https://api.crossref.org/works/10.1145/1553374.1553380/transform/application/x-bibtex) | 课程学习的基础动机与训练顺序。 |
| `zhao2024ratescore` | [原始来源](https://aclanthology.org/2024.emnlp-main.836.bib) | 实体感知的放射报告评价指标。 |
| `wang2023self` | [原始来源](https://aclanthology.org/2023.acl-long.754.bib) | 生成、过滤、再训练的自生成指令数据流程。 |
| `lin2004rouge` | [原始来源](https://aclanthology.org/W04-1013.bib) | ROUGE 报告文本重叠指标。 |
| `papineni2002bleu` | [原始来源](https://aclanthology.org/P02-1040.bib) | BLEU 文本生成指标。 |
| `banerjee2005meteor` | [原始来源](https://aclanthology.org/W05-0909/) | METEOR 文本生成指标。 |
| `li2023llava` | [原始来源](https://proceedings.neurips.cc/paper_files/paper/21475-/bibtex) | LLaVA-Med：医学图文指令训练及阶段化课程。 |
| `moor2023med` | [原始来源](https://proceedings.mlr.press/v225/moor23a.html) | Med-Flamingo：医学多模态少样本学习。 |
| `wu2024autogen` | [COLM 2024 官方录用列表](https://colmweb.org/2024/AcceptedPapers.html)、[OpenReview 论文页](https://openreview.net/forum?id=BAakY1hNKS) | 正式题名为 AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversations；使用复数 Conversations，无 framework。 |
| `madaan2023selfrefine` | [原始来源](https://proceedings.neurips.cc/paper_files/paper/20017-/bibtex) | Self-Refine：同一 LLM 生成反馈并迭代修订输出；原方法是无需额外训练的推理时改进。本项目若用于 Skill，应注明是对迭代自反馈原则的适配，不是原论文已有的 Skill 演化实验。 |

### 后续补充条目

| 引用键 | 原始 BibTeX / 元数据来源 | 支持的内容 |
|---|---|---|
| `jiang2025hulumed` | [arXiv v2](https://arxiv.org/abs/2510.08668v2) | Hulu-Med 方法与文献报告的基线结果；Table 1、Figure 2(b)。 |
| `khan2025dataenvgym` | [ICLR 2025 正式论文](https://proceedings.iclr.cc/paper_files/paper/2025/hash/846d3ef94d8c1a833a62cff05569c851-Abstract-Conference.html) | 学生反馈指导的数据生成；页码 53480--53507。 |
| `zheng2026evopi` | [原始报告](https://arxiv.org/abs/2606.31800) | 医学推理中的原则引导监督；本次保留现有正文概括。 |
| `liu2017iterative` | [ICML 2017 正式论文](https://proceedings.mlr.press/v70/liu17b.html) | 根据学习者状态迭代选择教学样本。 |
| `such2020generative` | [ICML 2020 正式论文](https://proceedings.mlr.press/v119/such20a.html) | 通过元梯度优化合成训练数据。 |
| `shinn2023reflexion` | [NeurIPS 官方 BibTeX](https://proceedings.neurips.cc/paper_files/paper/20995-/bibtex) | 语言反馈与跨尝试反思；页码 8634--8652。 |
| `hu2025automated` | [ICLR 2025 正式论文](https://proceedings.iclr.cc/paper_files/paper/2025/hash/36b7acf6f6010652b3f2a433774a66fe-Abstract-Conference.html) | 元智能体搜索智能体程序；页码 21344--21377。 |
| `wu2025radfm` | [正式期刊原文](https://www.nature.com/articles/s41467-025-62385-7) | 二维和三维医学视觉语言建模。 |
| `bai2024m3d` | [原始报告](https://arxiv.org/abs/2404.00578) | 三维医学图文与指令数据及模型。 |
| `lasateam2025lingshu` | [arXiv v1](https://arxiv.org/abs/2506.07044v1) | 医学多模态基础模型与 Table 8 中的基线结果。 |
| `messina2026cure` | [CVPR 2026 正式元数据](https://openaccess.thecvf.com/content/CVPR2026/html/Messina_CURE_Curriculum-guided_Multi-task_Training_for_Reliable_Anatomy_Grounded_Report_Generation_CVPR_2026_paper.html)；[作者完整版本](https://arxiv.org/abs/2601.15408v2) | 课程引导的报告生成；AGRG-29 + GRG 的 RaTEScore 为 0.597。 |
| `zhu2025internvl3` | [作者官方 Citation](https://internvl.readthedocs.io/en/latest/internvl3.0/introduction.html#citation)；[原始报告](https://arxiv.org/abs/2504.10479) | InternVL3 模型家族及跨骨干学习者的文献归属。2026-09-26 按作者最新要求恢复条目及中英文正文引用。 |

## 元数据处理说明

- 初次整理的 29 条及后续补充的 12 条均依据实际取得的 BibTeX、作者页面或官方出版元数据；没有从记忆补写作者。OpenReview 接口需要验证时，采用 ICLR 官方 proceedings 的 BibTeX 或元数据，保留正式会议版本。
- 规范化仅包括引用键、必要的大小写保护、LaTeX 重音字符、页码连字符、删去不影响识别的导出附属字段，以及 ICLR/ICML 会议名的简化。作者列表完整保留；没有使用 `and others` 截断。
- GAE 使用已取得的 DBLP ICLR 2016 导出，未使用 arXiv 最新版本导出的 2018 修订年。
- IU-Xray 的 DOI 导出年为在线发表的 2015；按卷 23、期 2 的正式期刊年份 2016 引用，依据 [IU 官方机构条目](https://scholarworks.indianapolis.iu.edu/items/f25c8fd2-1b90-45aa-b793-91814c1c875d)及 [DBLP 期刊记录](https://dblp1.uni-trier.de/rec/journals/jamia/Demner-FushmanK16.html)。完整作者、题名、卷期、页码与 DOI 来自实际 DOI 导出。
- PMC-VQA 的预印本首次提交于 2023，曾采用其 2024 修订版本；当前改用 2024 正式期刊版本，标题、卷期、文章号和 DOI 同步。SLAKE 使用 DOI 导出的 ISBI 2021 正式会议版本。
- VQA-RAD 的文章号 180251、MIMIC-CXR 的文章号 317 由 [Scientific Data 原文](https://www.nature.com/articles/sdata2018251)和 [MIMIC-CXR 原文](https://www.nature.com/articles/s41597-019-0322-0)补足；没有把网页页数误作文章号。
- ACE 使用官方 proceedings 更新后的题名 “Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models”，而不是本地早期 manifest 中的旧题名。
- Gemma 3 与 Qwen3-VL 均保留 arXiv 导出的完整作者列表。Gemma 导出的 “Dmitry and Lepikhin” 已依据[原始报告贡献者列表](https://arxiv.org/html/2503.19786v1)修正为单一姓名 “Dmitry (Dima) Lepikhin”；重复出现在不同贡献角色中的姓名保留导出顺序，没有凭猜测删除作者。
- 这些来源说明既有研究、数据集、模型和指标，不为本项目尚未提供的实验结果、训练完成状态或性能提升提供证据。所有本项目数值必须来自实验记录。


## 2026-09-25：URL 精简与引用缺口补充

- 原有 43 条书目中，15 条正式发表文献已有 DOI；删除其重复 URL，保留 DOI。其余原有 URL 全部保留。官方 `.bst` 和 `.sty` 不变。
- 新增 21 条文献，均用于已有方法、数据集或基线的出处，不据此改写实验结果。中英文使用相同引用键。支持集资源表仍保留数据下载地址，这些地址与文献 DOI 用途不同。
- 已有正式版本时使用正式版元数据，包括 CT-RATE、RadGenome-ChestCT、PubMedVision、PMC-CLIP、Quilt-1M、MedTrinity-25M 和 Photon；AMOS-MM 使用多模态挑战设计报告。作者、年份与题名均来自下列原始来源或其 DOI 注册元数据。

| 引用键 | 已核实来源 | 文中对应内容 |
|---|---|---|
| `kaelbling1998planning` | [原始来源](https://doi.org/10.1016/s0004-3702(98)00023-x) | POMDP 建模的基础来源 |
| `lin2023pmcclip` | [原始来源](https://doi.org/10.1007/978-3-031-43993-3_51) | PMC-OA 支持数据集 |
| `pelka2018roco` | [原始来源](https://doi.org/10.1007/978-3-030-01364-6_20) | ROCO 支持数据集 |
| `irvin2019chexpert` | [原始来源](https://doi.org/10.1609/aaai.v33i01.3301590) | CheXpert 支持数据集 |
| `li2024abdomenatlas` | [原始来源](https://doi.org/10.1016/j.media.2024.103285) | AbdomenAtlas1.0Mini 的母数据集 |
| `hamamci2026ctrate` | [原始来源](https://doi.org/10.1038/s41551-025-01599-y) | CT-RATE 支持数据集，采用正式期刊版本 |
| `zhang2025radgenome` | [原始来源](https://doi.org/10.1038/s41597-025-05922-9) | RadGenome-ChestCT 支持数据集，采用正式期刊版本 |
| `wasserthal2023totalsegmentator` | [原始来源](https://doi.org/10.1148/ryai.230024) | TotalSegmentator 支持数据集 |
| `ikezogwo2023quilt` | [原始来源](https://doi.org/10.52202/075280-1654) | Quilt-1M 支持数据集 |
| `gai2025threedrad` | [原始来源](https://doi.org/10.52202/085713-5656) | 3D-RAD 评测数据集 |
| `tcga2012colorectal` | [原始来源](https://doi.org/10.1038/nature11252) | TCGA-CRC 的母数据集，与表中 NCI 官方资源一致 |
| `zheng2024llamafactory` | [原始来源](https://doi.org/10.18653/v1/2024.acl-demos.38) | InternVL 实验使用的 LLaMA-Factory |
| `cai2025medmat` | [原始来源](https://doi.org/10.18653/v1/2025.acl-long.639) | Med-MAT 支持数据集 |
| `chen2024pubmedvision` | [原始来源](https://doi.org/10.18653/v1/2024.emnlp-main.418) | PubMedVision-IU 的母数据集，采用 EMNLP 正式版本 |
| `fang2026photon` | [原始来源](https://proceedings.iclr.cc/paper_files/paper/2026/file/633780c1344d0c95e4d2dd3431fe08d9-Paper-Conference.pdf) | 三维基线 Photon S2 |
| `xie2025medtrinity` | [原始来源](https://proceedings.iclr.cc/paper_files/paper/2025/file/11c483499c285f30daf832c17dc752bd-Paper-Conference.pdf) | MedTrinity BHX 的母数据集 |
| `kingma2015adam` | [原始来源](https://arxiv.org/abs/1412.6980) | 课程规划器使用的 Adam 优化器；arXiv 页面明确记录 ICLR 2015 发表信息 |
| `xin2025med3dvlm` | [原始来源](https://arxiv.org/abs/2503.20047) | 三维基线 Med3DVLM |
| `zhang2025rexgradient` | [原始来源](https://arxiv.org/abs/2505.00228) | ReXGradient 支持数据集 |
| `ji2024amosmm` | [原始来源](https://zenodo.org/records/10992155) | AMOS-MM 多模态评测任务的原始挑战设计报告 |
| `hu2024omnimedvqa` | [原始来源](https://openaccess.thecvf.com/content/CVPR2024/html/Hu_OmniMedVQA_A_New_Large-Scale_Comprehensive_Evaluation_Benchmark_for_Medical_LVLM_CVPR_2024_paper.html) | OmniMedVQA 支持数据集 |

- OmniMedVQA 的正式 DOI 另由 [Crossref 注册元数据](https://api.crossref.org/works/10.1109/cvpr52733.2024.02093) 核实，新增条目只显示 DOI。Photon 保留 ICLR 2026 的正式书目信息，访问链接使用同一论文的 [arXiv 稳定页面](https://arxiv.org/abs/2603.25155)，避免过长文件地址造成多余换行。

- 最终编译核验：中英文各64条书目，无未定义引用、重复标签、BibTeX 警告或越界文本。英文正文9页、全文34页；中文正文8页、全文31页。已检查中英文参考文献页、新增引用所在正文页及支持数据来源表；官方样式和图片未修改。


## 2026-09-25：学习者 AdamW 配置

- 根据作者确认，Qwen3-VL 8B 和 32B 学习者使用 AdamW；正文保留课程规划器的 Adam 设置。
- 新增 `loshchilov2019decoupled`：Ilya Loshchilov and Frank Hutter, *Decoupled Weight Decay Regularization*, ICLR 2019。作者、题名和会议年份已对照 [原始论文页面](https://arxiv.org/abs/1711.05101) 核实。引用位于中英文附录 B 的训练配置表。当前共65条文献。
