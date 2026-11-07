# CoEvoMed — ICLR 2027 Rebuttal Materials

Materials for submission **37342**, *CoEvoMed: Co-Evolving Supervision Principles and Medical Vision–Language Models*.

[OpenReview submission](https://openreview.net/forum?id=GeL7NntZTU) · Archived on **7 November 2026**.

## Reviews / 审稿意见

| File | Content |
|---|---|
| [English reviews](reviews/official_reviews_en.md) | Complete original text of the three human Official Reviews; original wording and spelling retained. |
| [中文审稿意见](reviews/official_reviews_zh.md) | 三位真人 reviewer 的完整中文译文，与英文逐项对应。 |
| [Structured source](reviews/human_reviews_source.json) | The same human review fields, review IDs, displayed dates, and source links. |

The reviews were checked against the original OpenReview page, including the sentence obscured in the supplied screenshot. Program Chairs’ automated LLM/PAT feedback is excluded. These documents contain the reviews, not rebuttal responses.

审稿意见已与 OpenReview 原始网页逐项核对，截图中被工具栏遮挡的句子已补全；未混入 LLM/PAT 自动反馈，也未加入作者回应。

## Paper and appendix / 论文与附录

| File | Original page range | Content |
|---|---|---|
| [Complete submitted PDF](papers/CoEvoMed_ICLR2027_submission.pdf) | 1–34 | Original PDF downloaded from OpenReview, preserved byte-for-byte. |
| [Paper, statements, and references](papers/CoEvoMed_ICLR2027_main.pdf) | 1–15 | Main text on pages 1–9; statements and references on pages 10–15. |
| [Appendix PDF](papers/CoEvoMed_ICLR2027_appendix.pdf) | 16–34 | Appendices A–G, extracted from the same submitted PDF. |

The two extracts retain the original printed page numbers, text, figures, and page dimensions. Every extracted page was checked against the source for identical text and rendering. Use original page numbers when preparing rebuttal citations.

完整 PDF 来自 OpenReview 实际投稿文件；正文与附录拆分版保留原页码和排版。准备 rebuttal 时，请按论文印刷页码引用。

## Code demo / 演示代码

- [Browsable source and instructions](code/CoEvoMed_ICLR2027/README.md)
- [Original submitted supplementary ZIP](code/CoEvoMed_ICLR2027_submitted.zip)

The ZIP was downloaded from the submission’s supplementary-material link. The expanded directory contains its 32 regular source/configuration/documentation/test files; macOS resource-fork metadata is omitted from the expanded copy. All 32 files match the local `CoEvoMed_ICLR2027` demo byte-for-byte. The original ZIP is unchanged.

This is the submitted two-task demonstration for VQA-RAD and MIMIC-CXR. Its CPU example uses synthetic fixtures. The supplied budgets are demonstration settings, not the full experimental configuration. Dataset files, model weights, credentials, and experimental outputs are not included. No code or paper content was modified during this archival upload; the demo was not rerun.

代码为投稿时的两任务 demo，未改动实现或实验配置；其 CPU 示例结果属于合成测试输出。使用方法见代码目录中的 README。

## Provenance

[MANIFEST.json](MANIFEST.json) records source URLs, PDF page ranges, file sizes, and SHA-256 checksums. The repository preserves the submission materials as retrieved on the archival date.
