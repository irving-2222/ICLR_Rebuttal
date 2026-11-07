import copy
import math

import pytest
import torch

from coevomed.curriculum import EvidenceSelector, compile_assignments, largest_remainder, mix_training
from coevomed.data import REPORTS, TASKS, validate_partitions
from coevomed.demo import FixtureAgents, ToyLearner, fixtures
from coevomed.feedback import state_vector, summary
from coevomed.policy import Controller
from coevomed.principles import PrincipleRegistry, eligible_principles, probe_decision
from coevomed.student_worker import response_labels


@pytest.fixture
def inputs():
    return fixtures()


def test_mixed_policy_likelihood_and_four_epochs():
    torch.set_num_threads(1)
    controller = Controller()
    state = [0.1] * 40
    decision = controller.sample(state, 0)
    probabilities, _ = controller.distribution(state)
    assert min(decision.probabilities) >= 0.05
    assert math.isclose(sum(decision.probabilities), 1, abs_tol=1e-6)
    assert math.isclose(math.exp(decision.old_logp), float(probabilities[decision.action]), abs_tol=1e-7)
    report = controller.update(state, decision, 0.2, state, terminal=True)
    assert len(report["epochs"]) == 4
    assert report["epochs"][0]["ratio"] == pytest.approx(1)
    assert report["advantage"] == pytest.approx(0.2)
    assert report["weights_before"] != report["weights_after"]
    with pytest.raises(ValueError, match="Stale"):
        controller.update(state, decision, 0.2, state)


def test_negative_singleton_advantage_is_not_centered():
    c = Controller(); state = [0.0] * 40; decision = c.sample(state, 0)
    report = c.update(state, decision, -0.1, state, terminal=True)
    assert report["advantage"] < 0
    assert report["epochs"][0]["policy_loss"] > 0


def test_terminal_mask_disables_bootstrap():
    c = Controller()
    with torch.no_grad(): c.model.critic.bias.fill_(2)
    state = [0.0] * 40; decision = c.sample(state, 0)
    report = c.update(state, decision, 0.5, state, terminal=True)
    assert report["value_target"] == pytest.approx(0.5)


def test_round_resume_matches_sampling(tmp_path):
    c = Controller(); c.save(tmp_path / "c.pt")
    other = Controller(17); other.load(tmp_path / "c.pt")
    assert c.sample([0.1] * 40, 2) == other.sample([0.1] * 40, 2)


def test_feedback_family_weighting(inputs):
    panel = inputs["validation"]; learner = ToyLearner()
    old = learner.outcomes(panel); new = copy.deepcopy(old)
    for o, n in zip(old, new):
        if o["benchmark"] in REPORTS:
            o["metrics"] = dict(rougeL=0.2, bleu4=0.2, meteor=0.2)
            n["metrics"] = dict(rougeL=0.4, bleu4=0.4, meteor=0.4)
        else:
            o["correct"] = False; n["correct"] = True
    stats = summary(panel, new, old)
    assert stats["reward"] == pytest.approx(0.6)
    assert len(state_vector(stats, episode=1, horizon=10)) == 40


def test_missing_case_and_external_feedback_fail(inputs):
    panel = inputs["validation"]; rows = ToyLearner().outcomes(panel)
    with pytest.raises(ValueError): summary(panel, rows[:-1])
    rows[0]["role"] = "external"
    with pytest.raises(ValueError): summary(panel, rows)


def test_partition_leakage_by_identity_and_pixels(inputs):
    validate_partitions(inputs["support"], inputs["validation"], inputs["external"])
    inputs["support"][0]["image_rgb_sha256"] = ["same-image"]
    inputs["external"][0]["image_rgb_sha256"] = ["same-image"]
    with pytest.raises(ValueError, match="overlap"):
        validate_partitions(inputs["support"], inputs["validation"], inputs["external"])


@pytest.mark.parametrize("action", ["balanced", "repair_heavy", "weakness_focus", "retention_heavy"])
def test_actions_cannot_change_task_quotas(inputs, action):
    from collections import Counter
    stats = summary(inputs["validation"], ToyLearner().outcomes(inputs["validation"]))
    quotas = {t: 17 for t in TASKS}
    assignments = compile_assignments(stats, EvidenceSelector(inputs["support"], FixtureAgents()), quotas, action, episode=0)
    assert Counter(a["benchmark"] for a in assignments) == Counter(quotas)


def test_no_incompatible_evidence_fallback(inputs):
    stats = summary(inputs["validation"], ToyLearner().outcomes(inputs["validation"]))
    with pytest.raises(ValueError, match="No supported"):
        compile_assignments(stats, EvidenceSelector([], FixtureAgents()), {t: 1 for t in TASKS}, "balanced", episode=0)


@pytest.mark.parametrize("current,candidate,common,status", [(90, 85, 80, "accepted"), (90, 84, 80, "rejected"),
    (70, 75, 65, "deferred"), (70, 80, 55, "deferred"), (80, 80, 60, "accepted")])
def test_paired_thresholds(current, candidate, common, status):
    left = set(range(current)); right = set(range(common)) | set(range(current, current + candidate - common))
    review = {"applied": True, "alignment": "improved", "evidence_preserved": True, "reason": "supported"}
    result = probe_decision(list(range(100)), left, right, review)
    assert result["status"] == status
    assert result["candidate_yield"] == candidate / 100


def test_synonyms_do_not_pass_and_missing_assignments_defer():
    ids = list(range(100))
    same = {"applied": True, "alignment": "same", "evidence_preserved": True, "reason": "only style"}
    assert probe_decision(ids, ids, ids, same)["status"] == "deferred"
    better = {**same, "alignment": "improved"}
    assert probe_decision(ids[:90], ids[:90], ids[:90], better)["status"] == "deferred"


def test_candidate_never_overwrites_active_before_acceptance():
    registry = PrincipleRegistry(); active = registry.active("example")
    strategy = copy.deepcopy(active["strategy"]); strategy["answer_strategy"].append("Specify a supported spatial relation")
    candidate = registry.candidate("example", strategy, "localization errors")
    assert registry.active("example") == active
    registry.select(candidate, {"status": "deferred"}, 3)
    assert registry.active("example") == active


def test_accepted_candidate_is_used_by_subsequent_construction():
    from coevomed.agents import generate_batch
    registry = PrincipleRegistry(); key = "vqa_rad::attribute::synthetic::none"
    active = registry.active(key); strategy = copy.deepcopy(active["strategy"])
    strategy["question_strategy"] = ["Contrast the marked color with the unmarked region"]
    candidate = registry.candidate(key, strategy, "residual error")
    registry.select(candidate, {"status": "accepted"}, 3)
    source = fixtures()["support"][0]
    assignment = {"id": "next-round-assignment", "source": source, "benchmark": "vqa_rad", "lane": "repair",
                  "principle_id": key, "target": {k: source[k] for k in ("task_form", "visual_ability", "modality", "anatomy")}}
    rows, rejected = generate_batch([assignment], registry, FixtureAgents(), [])
    assert rows[0]["principle_version"] == 1 and rows[0]["question"].startswith("Contrast")
    assert not rejected


def test_eligibility_requires_usage_and_nonpositive_repair():
    cell = {"principle_id": "p", "count": 3, "net_repair": 0, "persistent_gap": 2}
    window = [{"usage": {"p": {"version": 0, "count": 100}}, "cells": {"c": cell}}]
    assert eligible_principles(window) == ["p"]
    cell["net_repair"] = 1
    assert not eligible_principles(window)


def test_training_cannot_include_feedback(inputs):
    with pytest.raises(ValueError): mix_training([], inputs["validation"], original_count=1)
    with pytest.raises(ValueError, match="shortfall"): mix_training([], [], target_size=1)


def test_response_only_mask():
    labels = response_labels(torch.tensor([1, 2, 3, 4, 0]), torch.tensor([1, 2]), torch.tensor([1, 1, 1, 1, 0]))
    assert labels.tolist() == [-100, -100, 3, 4, -100]
    with pytest.raises(ValueError):
        response_labels(torch.tensor([1, 2]), torch.tensor([8]), torch.tensor([1, 1]))


def test_pretraining_split_sizes(inputs, tmp_path):
    from coevomed.pretrain import build_states, train_actor
    stats = summary(inputs["validation"], ToyLearner().outcomes(inputs["validation"]))
    rows = build_states(stats)
    assert len(rows) == 800
    actions = ("balanced", "repair_heavy", "weakness_focus", "retention_heavy")
    for i, r in enumerate(rows): r["action"] = actions[(i // 10) % 4]
    metrics = train_actor(rows, tmp_path, max_epochs=2)
    assert (metrics["train_count"], metrics["validation_count"]) == (640, 160)
