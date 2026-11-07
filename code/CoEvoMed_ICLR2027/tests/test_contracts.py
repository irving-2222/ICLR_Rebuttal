import copy
from pathlib import Path

import pytest
import torch

from coevomed.agents import APIAgents, generate_batch
from coevomed.curriculum import EvidenceSelector, compile_assignments
from coevomed.data import TASKS, load_json, validate_record
from coevomed.demo import FixtureAgents, ToyLearner, fixtures
from coevomed.feedback import summary
from coevomed.policy import Controller
from coevomed.principles import PrincipleRegistry, initial_principle, probe_decision


def test_constructor_receives_no_images_but_verifier_does():
    agents = object.__new__(APIAgents); captured = []
    agents.call = lambda *args, **kwargs: captured.append((args, kwargs)) or {}
    source = fixtures()["support"][0]
    assignment = {"source": source, "target": {}, "benchmark": "vqa_rad", "lane": "repair"}
    agents.construct(assignment, initial_principle("p"))
    assert "images" not in captured[-1][1]
    assert "images" not in captured[-1][0][2]
    agents.verify(assignment, {})
    assert captured[-1][1]["images"] == source["images"]


def test_two_task_demo_budget_is_explicit():
    config = load_json(Path(__file__).resolve().parents[1] / "configs/demo_vqarad_mimic.json")
    assert config["active_tasks"] == ["vqa_rad", "mimic_cxr"]
    assert config["task_quotas"] == {"vqa_rad": 140, "mimic_cxr": 60}
    assert "training_size" not in config
    assert config["recipe_confirmed"] is False


def test_principle_semantic_review_uses_revision_agent():
    agents = object.__new__(APIAgents)
    captured = []
    verdict = {"applied": True, "alignment": "improved", "evidence_preserved": True,
               "reason": "Supported distinction is expressed"}
    agents.call = lambda *args, **kwargs: captured.append((args, kwargs)) or verdict
    active = initial_principle("p")
    candidate = copy.deepcopy(active)
    candidate["version"] = 1
    pairs = [{"assignment_id": "paired-evidence"}]
    assert agents.review(active, candidate, {"error_semantics": ["localization"]}, pairs) == verdict
    assert captured[0][0][0] == "revision"
    assert captured[0][0][2]["pairs"] == pairs
    config = load_json(Path(__file__).resolve().parents[1] / "configs/demo_vqarad_mimic.json")
    assert "reviewer" not in config["agents"]


def test_compile_form_quota_failure_cannot_silently_change_format():
    data = fixtures(); stats = summary(data["validation"], ToyLearner().outcomes(data["validation"]))
    with pytest.raises(ValueError, match="required task form"):
        compile_assignments(stats, EvidenceSelector(data["support"], FixtureAgents()), {t: 10 for t in TASKS}, "balanced",
                            episode=0, form_quotas={"vqa_rad": {"mcq": 10}})


def test_duplicate_filter_and_unsupported_fact_rejection():
    data = fixtures(); stats = summary(data["validation"], ToyLearner().outcomes(data["validation"]))
    assignments = compile_assignments(stats, EvidenceSelector(data["support"], FixtureAgents()), {t: 1 for t in TASKS}, "balanced", episode=0)
    agents = FixtureAgents(); registry = PrincipleRegistry()
    duplicate = copy.deepcopy(assignments[0]); duplicate["id"] = "duplicate"
    accepted, rejected = generate_batch([assignments[0], duplicate], registry, agents, [])
    assert len(accepted) == len(rejected) == 1
    assert rejected[0]["reason"] == "duplicate_supervision"
    original = agents.construct
    agents.construct = lambda a, p: {**original(a, p), "fact_ids": ["invented"]}
    accepted, rejected = generate_batch(assignments, registry, agents, [])
    assert not accepted and all(r["reason"] == "unsupported_fact_ids" for r in rejected)


def test_exact_mix_ratio_not_actor_ratio():
    c = Controller(); state = [0.2] * 40
    with torch.no_grad(): c.model.actor.bias.copy_(torch.tensor([3.0, 1.0, -1.0, -2.0]))
    decision = c.sample(state, 0)
    original = c.distribution; observed = []
    def record(x):
        mu, value = original(x)
        observed.append(mu.detach().clone())
        return mu, value
    c.distribution = record
    update = c.update(state, decision, 0.4, state, terminal=True)
    for row, mu in zip(update["epochs"], observed[2:]):
        assert row["ratio"] == pytest.approx(float(mu[decision.action]) / decision.probabilities[decision.action], abs=1e-6)


def test_semantic_regression_and_invalid_denominator():
    ids = list(range(100))
    assert probe_decision(ids, ids, ids, {"alignment": "worse"})["status"] == "rejected"
    with pytest.raises(ValueError): probe_decision(ids, ids, [999], {})
    with pytest.raises(ValueError): probe_decision(ids + [0], ids, ids, {})


def test_portable_media_contract():
    row = fixtures()["support"][0]
    row["images"] = ["../private.png"]
    with pytest.raises(ValueError): validate_record(row, "support")
