from copy import deepcopy
from types import SimpleNamespace
import sys
import threading

import pytest
import torch

from coevomed.agents import APIAgents, AgentCallError, generate_batch
from coevomed.data import (DEMO_TASKS, digest, dump_json, load_json, read_jsonl,
                           training_budget, validate_training_record, write_jsonl)
from coevomed.demo import FixtureAgents, ToyLearner, fixtures
from coevomed.principles import PrincipleRegistry
from coevomed.runner import Runner
from coevomed.scoring import ratescore, score_predictions
from coevomed.student_worker import freeze_vision_tower, main as worker_main


def make_run(root, agents=None, **overrides):
    data = {role: [r for r in rows if r["benchmark"] in DEMO_TASKS]
            for role, rows in fixtures().items()}
    config = {"seed": 42, "horizon": 2, "revision_every": 3, "workers": 1,
              "active_tasks": list(DEMO_TASKS), "task_quotas": {t: 3 for t in DEMO_TASKS},
              "fixture_mode": True, "learner": {"backend": "toy"}, **overrides}
    baseline = ToyLearner().outcomes(data["validation"])
    Runner.initialize(root, config, data["support"], data["validation"], data["external"], baseline)
    runner = Runner(root, agents or FixtureAgents())
    directory = runner.prepare()
    job = load_json(directory / "job.json")
    result = {k: job[k] for k in ("job_id", "checkpoint_in", "training_digest", "validation_digest")}
    result.update({"checkpoint_out": "fixture-new", "fixture_mode": True, "outcomes": baseline})
    return runner, directory, result


@pytest.mark.parametrize("where", ["disk", "memory"])
def test_config_cannot_change_between_sampling_and_ppo(tmp_path, where):
    runner, _, result = make_run(tmp_path)
    changed = deepcopy(runner.config)
    changed["task_quotas"]["vqa_rad"] += 1
    if where == "disk":
        dump_json(tmp_path / "config.json", changed)
        with pytest.raises(ValueError, match="Frozen config"):
            Runner(tmp_path, FixtureAgents())
    else:
        runner.config = changed
    with pytest.raises(ValueError, match="Frozen config"):
        runner.complete(result)
    assert runner.controller.update_index == 0


@pytest.mark.parametrize("name", ["accepted.jsonl", "assignments.jsonl", "training.jsonl", "validation.jsonl"])
def test_round_artifact_edits_are_rejected_before_ppo(tmp_path, name):
    runner, directory, result = make_run(tmp_path)
    rows = read_jsonl(directory / name)
    rows[0]["id"] = "edited"
    write_jsonl(directory / name, rows)
    with pytest.raises(ValueError, match="Pending artifact changed"):
        runner.complete(result)
    assert runner.controller.update_index == 0


def test_pending_learner_settings_cannot_be_swapped(tmp_path):
    runner, directory, result = make_run(tmp_path)
    job = load_json(directory / "job.json")
    job["learner"]["epochs"] = 5
    dump_json(directory / "job.json", job)
    with pytest.raises(ValueError, match="manifest changed"):
        runner.complete(result)
    assert runner.controller.update_index == 0


def test_zero3_empty_placeholder_is_still_a_vision_parameter():
    tower = torch.nn.Parameter(torch.empty(0))
    tower.ds_numel = 128
    merger = torch.nn.Parameter(torch.ones(3))
    language = torch.nn.Parameter(torch.ones(4))
    model = SimpleNamespace(named_parameters=lambda: iter([
        ("model.visual.blocks.0.weight", tower), ("model.visual.merger.weight", merger),
        ("model.language_model.weight", language)]))
    assert freeze_vision_tower(model) == 128
    assert not tower.requires_grad and merger.requires_grad and language.requires_grad
    with pytest.raises(ValueError, match="vision tower"):
        freeze_vision_tower(SimpleNamespace(named_parameters=lambda: iter([("language", language)])))


def training_contract():
    job = {"job_id": "round_000", "checkpoint_in": "base", "training_digest": "train",
           "validation_digest": "panel", "exclusions_digest": "excluded", "training_count": 48,
           "learner": {"epochs": 1, "world_size": 24, "per_device_batch_size": 1,
                       "gradient_accumulation_steps": 1, "max_steps": -1}}
    job["training_budget"] = training_budget(job["training_count"], job["learner"])
    record = {k: job[k] for k in ("job_id", "checkpoint_in", "training_digest", "validation_digest", "exclusions_digest")}
    record.update({"checkpoint": "trained", "learner_digest": digest(job["learner"]),
                   "training_steps": 2, "training_seconds": 1.0, "response_tokens": 12,
                   "training_budget": job["training_budget"], "completed_epochs": 1.0,
                   "loss_reduction": "response_sum_example_mean"})
    return job, record


@pytest.mark.parametrize("key", ["job_id", "checkpoint_in", "training_digest", "validation_digest",
                                 "learner_digest", "checkpoint", "training_steps"])
def test_training_record_is_bound_to_data_recipe_and_new_weights(key):
    job, record = training_contract()
    validate_training_record(job, record, "trained")
    record[key] = "wrong" if key != "training_steps" else 0
    with pytest.raises(ValueError, match="Training record"):
        validate_training_record(job, record, "trained")


def test_inference_only_without_update_record_fails_before_cuda(tmp_path):
    job, _ = training_contract()
    training, validation = [{"role": "train"}], [{"role": "validation"}]
    job.update({"training": "training.jsonl", "validation": "validation.jsonl",
                "training_digest": digest(training), "validation_digest": digest(validation)})
    write_jsonl(tmp_path / "training.jsonl", training)
    write_jsonl(tmp_path / "validation.jsonl", validation)
    dump_json(tmp_path / "job.json", job)
    with pytest.raises(ValueError, match="requires --training-record"):
        worker_main(["--job", str(tmp_path), "--output", str(tmp_path / "answer"),
                     "--media-root", str(tmp_path), "--inference-only"])
    with pytest.raises(ValueError, match="Training must continue"):
        worker_main(["--job", str(tmp_path), "--output", str(tmp_path / "answer"),
                     "--media-root", str(tmp_path), "--checkpoint", "unrelated-model"])


def test_partial_api_failure_keeps_other_assignments_and_counts_failure(tmp_path):
    runner, directory, _ = make_run(tmp_path)
    assignments = read_jsonl(directory / "assignments.jsonl")
    agents = FixtureAgents()
    construct = agents.construct

    def unstable(assignment, principle):
        if assignment["id"] == assignments[0]["id"]:
            raise AgentCallError("constructor: timeout")
        return construct(assignment, principle)

    agents.construct = unstable
    accepted, rejected = generate_batch(assignments, runner.registry, agents, [], workers=2)
    assert len(accepted) + len(rejected) == len(assignments)
    assert rejected[0]["assignment_id"] == assignments[0]["id"]
    assert rejected[0]["failure_type"] == "api"
    assert accepted


@pytest.mark.parametrize("stage", ["revision", "probe"])
def test_failed_revision_defers_without_losing_completed_ppo(tmp_path, stage):
    class UnavailableAgents(FixtureAgents):
        def revise(self, active, cells):
            if stage == "revision":
                raise AgentCallError("revision: timeout")
            return super().revise(active, cells)

        def construct(self, assignment, principle):
            if stage == "probe" and principle["version"] > 0:
                raise AgentCallError("constructor: timeout")
            return super().construct(assignment, principle)

    runner, directory, result = make_run(tmp_path, UnavailableAgents(), revision_every=1, min_principle_usage=1)
    report = runner.complete(result)
    assert report["principle_decisions"] and set(report["principle_decisions"]) == {"deferred"}
    resumed = Runner(tmp_path, FixtureAgents())
    assert resumed.controller.update_index == resumed.state["next_round"] == 1
    assert resumed.state["checkpoint"] == result["checkpoint_out"]
    assert all(v["active"] == 0 for v in resumed.registry.payload.values())
    assert len(load_json(directory / "ppo.json")["epochs"]) == 4


@pytest.mark.parametrize("status", [None, 408, 409, 429, 503, 401])
def test_api_transport_failures_are_logged_and_auth_fails_fast(tmp_path, monkeypatch, status):
    class ConnectionError(Exception):
        pass

    class StatusError(Exception):
        def __init__(self, code):
            self.status_code = code

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(
        APIConnectionError=ConnectionError, APIStatusError=StatusError))

    def fail(**kwargs):
        raise ConnectionError() if status is None else StatusError(status)

    agents = object.__new__(APIAgents)
    agents.config = {"constructor": "test-model"}
    agents.media_root = tmp_path
    agents.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fail)))
    agents.usage, agents.lock = [], threading.Lock()
    with pytest.raises(StatusError if status == 401 else AgentCallError):
        agents.call("constructor", "test", {})
    assert len(agents.usage) == 1 and agents.usage[0]["error_type"]


@pytest.mark.parametrize("scores", [[], [0.9], [0.8, 0.6, 0.7]])
def test_ratescore_cannot_silently_drop_or_add_cases(monkeypatch, scores):
    monkeypatch.setitem(sys.modules, "RaTEScore", SimpleNamespace(
        RaTEScore=lambda: SimpleNamespace(compute_score=lambda p, r: scores)))
    with pytest.raises(ValueError, match="incomplete panel"):
        ratescore(["report1", "report2"], ["reference1", "reference2"])


def test_ratescore_uses_all_paired_cases(monkeypatch):
    monkeypatch.setitem(sys.modules, "RaTEScore", SimpleNamespace(
        RaTEScore=lambda: SimpleNamespace(compute_score=lambda p, r: [0.8, 0.6])))
    assert ratescore(["report1", "report2"], ["reference1", "reference2"]) == pytest.approx(0.7)


def test_mcq_empty_normalizations_are_not_correct_answers():
    row = {"id": "v1", "role": "validation", "benchmark": "vqa_rad", "task_form": "mcq", "answer": "A"}
    assert not score_predictions([row], [{"id": "v1", "prediction": "the"}])[0]["correct"]
    assert score_predictions([row], [{"id": "v1", "prediction": "A."}])[0]["correct"]
    with pytest.raises(ValueError, match="scoring scope"):
        score_predictions([], [], report_scope="typo")
