# Evaluation dataset scope confirmed on 2026-09-19

The user explicitly confirmed that SLAKE 1,061, PathVQA 6,761, and MIMIC-CXR 2,343 are the evaluation sizes underlying the final EvoForma results reported in the paper.

The complete EvoForma 2D scope follows `2D_result/2D_eval_datasets_our_model.md`: VQA-RAD 451, SLAKE 1,061, PMC-VQA 33,430, PathVQA 6,761, MIMIC-CXR 2,343, and IU-Xray 590. These are evaluation-instance counts, not image/patient counts. Baseline-specific counts in `2D_result/other_model.json` are retained; historical feedback-subset counts are not final evaluation counts.

The 3D description follows the user-supplied `3D_result/3d评测集特点.md`: M3D-VQA test closed questions 13,791 / 2,000 media paths; 3D-RAD test open questions 4,692 / 2,354 paths; AMOS-MM validation report generation 400 / 400 paths. Media counts and integrity checks are reported by that document; no new raw-media audit was performed during this manuscript edit.

The manuscript omits the blanket in-domain and clinical-annotation labels, does not equate generic lexical recall with clinical-concept recall, and retains the actual reported ROUGE-1/2/L and BLEU-1/2/3/4 2D metrics. The 3D AMOS-MM comparison uses BLEU-1 as separately confirmed by the Hulu-Med author through the user.
