# Appendix B configuration authority

On 2026-09-19 the author clarified that the supplied code is a small demonstration, not the final submission implementation. Appendix B was rewritten as training configuration rather than an implementation audit. Statements about snapshot discrepancies, reruns, terminal masks, and historical overrides were removed.

Demo-only numerical hyperparameters were not relabeled as final experimental settings. Confirmation was initially requested for learning rate, epochs per round, PPO update schedule and optimization settings, allocation ratios, principle-revision schedule, and comparison thresholds. The controller settings subsequently confirmed by the author are recorded below; unspecified learner-training settings are not inferred from the demonstration.

The learner objective, curriculum method, and matched-evidence principle comparison retain their manuscript definitions. Equation and table labels are preserved. No experimental result values are changed.

## Author-confirmed PPO configuration

On 2026-09-20 the author explicitly corrected the update schedule to one PPO update after every curriculum round, with four optimization epochs over that round's rollout. This supersedes the earlier description of updating every three rounds; per-round updating is the actual experimental setting, not a future proposal.

The controller has a 40-dimensional input, a shared 128/64 MLP, a four-action Actor, and a scalar Critic. Baseline evaluation statistics informed 800 initialization states (balanced, broadly weak, locally weak, or regressed capabilities), labeled by deepseek-v4-flash (model name corrected by the author on 2026-09-26). A state-group split gives 640 training and 160 validation records. Cross-entropy training initializes the shared MLP and Actor; the best validation checkpoint is epoch 5. The Critic output head's weights and bias are reset to zero before real-feedback training. These 800 states are not real learner-training interactions.

PPO uses Adam at 3e-4, gamma 0.90, GAE lambda 0.95, clip 0.20, value/entropy coefficients 0.50/0.01, and gradient-norm limit 0.50. The author also supplied seed 42; it remains in this internal record under the standing request to omit seed discussion from the manuscript. External LLM weights are not updated by PPO. Rewards use actual learner-validation gains: VQA accuracy and report composite 0.5 ROUGE-L + 0.3 BLEU-4 + 0.2 METEOR, with within-family means and equal weighting of the two task families.

Sampling, old log-probabilities, new log-probabilities, and entropy all use mu = 0.8 * softmax(Actor(s)) + 0.05. Old log-probabilities are saved at sampling time and held fixed across all four optimization epochs; the ratio is mu_new / mu_old. Appendix A, Appendix B, the main-text sampling notation, and Appendix G use this executed mixture consistently. No additional cost, reward-scale, advantage-normalization, or bootstrap settings are inferred.

## Final-experiment feedback independence

On 2026-09-20 the author explicitly confirmed that the final experiments use validation data independent of the final evaluation data, and that final evaluation data never entered the EvoForma framework. Historical observations from the supplied demonstration code do not describe these final experiments. Appendix C.6 now states the confirmed separation between validation feedback and external evaluation; it no longer presents historical demo overlap records as evidence about the final experimental setup. This confirmation does not supply additional audit counts or patient-level split details.

## R7 checkpoint selection

On 2026-09-20 the author confirmed that R7 was chosen because it had the most balanced overall capabilities across the recorded training rounds. The main text, trajectory caption, Appendix C.4, and trajectory data record now state this cross-task rationale and the use of one checkpoint for all six main 2D results. No weighted aggregate, minimum-variance criterion, formal optimality guarantee, or early-stopping rule is introduced. The source of the observations used to judge this balance has been requested separately; validation-only selection is not inferred from the earlier confirmation that final evaluation data did not enter framework adaptation.

## Agent model correction and role mapping (2026-09-26)

The author explicitly confirmed that deepseek-v4-pro was not used and that manuscript references to it must use deepseek-v4-flash. This supersedes the model names retained in the historical demonstration snapshot and its teacher-label audit. Historical run files are preserved.

Appendix B maps the evidence verifier, factual evidence extraction, and validation-set annotation to Qwen3.6-27B; it maps the evidence selector, supervision constructor, and revision agent to deepseek-v4-flash. Curriculum allocation decisions remain with the learned Actor--Critic, with Flash supporting construction-target specification and supplying action labels for supervised initialization. This mapping follows the paper's established agent roles and the corresponding source-sampler, generator, verifier, semantic-planning, and principle-revision components. The author's model clarification and the manuscript's Qwen3.6-27B specification take precedence over conflicting model identifiers in older demonstration configurations.

On 2026-09-26, the author approved clarifying all five agent roles in Appendix B: evidence selector, supervision constructor, evidence verifier, curriculum planner, and revision agent. The revised paragraph introduces each role through its responsibilities and then gives its model configuration. The Actor--Critic is part of the curriculum planner; the established model mapping and training settings are unchanged.

## Unified presentation of 2D and volumetric experiments (2026-09-26)

The author requested that the appendix present the 2D and 3D settings together, because the previous separate training descriptions suggested separate learners. The author approved: “We evaluate the trained CoEvoMed-8B model on both 2D and volumetric benchmarks, representing each volume as a video of 64 slice frames.” This sentence now introduces Appendix C. Appendix B consolidates the common learner settings; the former standalone volumetric evaluation section is integrated into C.1 (datasets, inputs, and scoring) and C.2 (supplementary results).

The obsolete wording that separately introduced a volumetric learner initialized from Qwen3-VL-8B-Instruct was removed. The existing FullSFT, frozen vision tower, AdamW, hardware, BF16, TF32, ZeRO-3, 64-frame input, and pixel bounds are preserved across the consolidated description. The previously documented epoch count retains its 2D scope. This edit adds no data-mixing ratio, training-stage order, or specific 3D checkpoint identifier. The R7 statement continues to describe the six main 2D results. InternVL's independently trained task models remain explicitly distinguished in its existing paragraph and caption.
