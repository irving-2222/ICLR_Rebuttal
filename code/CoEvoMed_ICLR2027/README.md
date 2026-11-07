# CoEvoMed

A two-task demonstration of CoEvoMed for VQA-RAD and MIMIC-CXR, with curriculum
optimization, supervision construction, principle evolution, and Qwen3-VL
training and evaluation interfaces.

## Quick Start (No API or GPU)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-demo.txt
python -m pip install --no-deps -e .
python -m coevomed.cli demo --output ./runs/demo --rounds 6
python -m pytest -q -p no:cacheprovider
```

The CPU example uses synthetic fixtures and a small classifier to test the control
loop. Its scores are synthetic test outputs. Six rounds produce six learner updates
and six PPO updates, each with four optimization epochs. Use a new output directory
for each run.

## Included Mechanisms

1. Fixed four-axis validation cells and aligned predictions from successive learners.
2. A 40D history summary, 128/64 shared MLP, four-action Actor and scalar Critic.
3. Sampling, stored log likelihoods, PPO ratios and entropy all use
   `mu = 0.8 * softmax(actor) + 0.05`.
4. One learner transition per PPO update; four optimizer epochs; signed task-family
   balanced validation gain. External benchmark scores never enter the controller.
5. Fixed task quotas; adaptive repair/retention allocation within each task.
6. Capability-matched evidence retrieval followed by LLM evidence selection, text-only
   construction from the selected source facts, and image-aware factual verification.
7. Versioned principle revision every configured window; 100 matched evidence assignments,
   up to 30 common pairs for semantic review, and next-round deployment only.
8. An exchange boundary between online agents/scoring and offline learner SFT/inference.
9. A three-node, 24-GPU Qwen3-VL launcher with explicit response-token SFT settings and
   full-epoch budget checks. Real inputs require provenance and RGB image identities;
   external content is excluded from training jobs and adaptation.

The selected-task reward is `0.5 * delta(VQA-RAD accuracy) + 0.5 * delta(MIMIC NLG)`.
The 40D Actor input uses zero padding for inactive tasks. Teacher initialization
uses the same two-task profile.

The supplied integration configuration requests 140 VQA-RAD and 60 MIMIC-CXR
candidates per round. Accepted and mixed training counts are recorded separately.
These are small demonstration budgets, not the paper's experimental configuration.
Review the configuration and set `recipe_confirmed=true` before a model-backed run.
Data, model weights, and API credentials are supplied separately.

In model-backed runs, deepseek-v4-flash selects supporting evidence, constructs
supervision, specifies curriculum targets, labels initialization states, and revises
and reviews principles. Principle proposals and their semantic assessment both
belong to the revision agent and use its configured model. Qwen3.6-27B performs visual verification, fact extraction,
validation annotation, and semantic answer scoring. The learned Actor--Critic selects
allocation actions. Evidence selection returns source IDs from a compatible pool;
source facts remain unchanged. When a quota exceeds that pool, selected evidence is
reused to fill candidate requests. The CPU demo uses fixture agents for these calls.
The Qwen learner configuration disables gradient checkpointing.

Verification covers CPU tests and a small-model, two-GPU integration test.
Full three-node execution remains to be verified on the target cluster.

## Files

| Location | Purpose |
|---|---|
| `coevomed/policy.py`, `feedback.py` | State, reward, executed-policy PPO |
| `coevomed/curriculum.py`, `agents.py` | Allocation, evidence retrieval, frozen LLM agents |
| `coevomed/principles.py`, `runner.py` | Principle comparison and complete round orchestration |
| `coevomed/pretrain.py`, `preprocessing.py` | Teacher initialization and data preparation |
| `coevomed/student_worker.py`, `scoring.py` | Optional Qwen worker and online evaluation |
| `tools/run_student_24gpu.py` | Three-node training, checkpoint answering and image/budget preflight |
| `coevomed/demo.py` | Two-task CPU closed-loop demo |
| `configs/demo_vqarad_mimic.json` | Two-task agent and learner configuration |
| `tests/` | Algorithm, contract, and closed-loop tests |
