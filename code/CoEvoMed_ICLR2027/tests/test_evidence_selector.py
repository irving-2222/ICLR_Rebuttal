from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

from coevomed.agents import APIAgents, AgentCallError
from coevomed.curriculum import EvidenceSelector
from coevomed.data import AXES, DEMO_TASKS, cell_key, load_json, read_jsonl
from coevomed.demo import FixtureAgents, ToyLearner, fixtures
from coevomed.runner import Runner
from coevomed.student_worker import training_kwargs


def test_model_configuration_and_training_arguments():
    config = load_json(Path(__file__).resolve().parents[1] / "configs/demo_vqarad_mimic.json")
    for role in ("selector", "planner", "constructor", "revision", "teacher"):
        assert config["agents"][role] == "deepseek-v4-flash"
    assert config["agents"]["verifier"] == config["agents"]["judge"] == "qwen3.6-27b"
    assert training_kwargs(config["learner"], "test-output")["gradient_checkpointing"] is False


def test_selector_uses_llm_choice_and_preserves_source_facts():
    source = fixtures()["support"][:3]
    original = deepcopy(source)
    incompatible = deepcopy(source[0])
    incompatible.update(id="other-anatomy", anatomy="other")
    target = {k: source[0][k] for k in AXES}
    agents = object.__new__(APIAgents)
    calls = []

    def call(role, system, payload, **kwargs):
        calls.append((role, payload, kwargs))
        assert {r["source_id"] for r in payload["candidates"]} == {r["id"] for r in source}
        assert payload["target"] == target and payload["intent"] == "Distinguish supported attributes"
        return {"source_ids": [source[2]["id"], source[0]["id"]]}

    agents.call = call
    selector = EvidenceSelector(source + [incompatible], agents)
    selected = selector.select(cell_key(source[0]), 2, 42, target=target, lane="repair",
                               intent="Distinguish supported attributes")
    assert calls[0][0] == "selector" and "images" not in calls[0][2]
    assert selected == [original[2], original[0]]
    selected[0]["facts"][0]["text"] = "changed output copy"
    assert source == original


@pytest.mark.parametrize("response", [None, "s0", [], ["s0"], ["s0", "s0"],
                                      ["s0", "outside-pool"], ["s0", {}]])
def test_invalid_selector_results_cannot_fall_back_to_sampling(response):
    source = fixtures()["support"][:2]
    for i, row in enumerate(source):
        row["id"] = f"s{i}"
    agents = SimpleNamespace(select_evidence=lambda *args, **kwargs: response)
    selector = EvidenceSelector(source, agents)
    with pytest.raises(ValueError, match="requested distinct IDs"):
        selector.select(cell_key(source[0]), 2, 42, target={}, lane="repair", intent="target")


def test_quota_above_pool_size_reuses_selected_evidence():
    source = fixtures()["support"][:2]
    def choose(candidates, **kwargs):
        assert kwargs["count"] == 2
        return [source[1]["id"], source[0]["id"]]
    selector = EvidenceSelector(source, SimpleNamespace(select_evidence=choose))
    selected = selector.select(cell_key(source[0]), 5, 42, target={}, lane="retention", intent="target")
    assert [r["id"] for r in selected] == [source[i]["id"] for i in (1, 0, 1, 0, 1)]


def test_runner_plans_then_selects_and_logs_selector_calls(tmp_path):
    class RecordingAgents(FixtureAgents):
        def __init__(self):
            self.usage = []
            self.targets = []
            self.selected = set()

        def plan(self, cell, lane):
            intent = f"{cell['benchmark']}:{lane}"
            self.targets.append(intent)
            return intent

        def select_evidence(self, candidates, **kwargs):
            assert kwargs["intent"] in self.targets
            assert all(all(r[k] == v for k, v in kwargs["target"].items()) for r in candidates)
            chosen = super().select_evidence(candidates, **kwargs)
            self.selected.update(chosen)
            self.usage.append({"role": "selector", "model": "fixture"})
            return chosen

        def construct(self, assignment, principle):
            assert assignment["intent"] == f"{assignment['benchmark']}:{assignment['lane']}"
            assert assignment["source"]["id"] in self.selected
            return super().construct(assignment, principle)

    data = {role: [r for r in rows if r["benchmark"] in DEMO_TASKS] for role, rows in fixtures().items()}
    config = {"seed": 42, "horizon": 1, "revision_every": 3, "workers": 1,
              "active_tasks": list(DEMO_TASKS), "task_quotas": {t: 4 for t in DEMO_TASKS},
              "fixture_mode": True, "learner": {"backend": "toy"}}
    baseline = ToyLearner().outcomes(data["validation"])
    Runner.initialize(tmp_path, config, data["support"], data["validation"], data["external"], baseline)
    agents = RecordingAgents()
    runner = Runner(tmp_path, agents)
    directory = runner.prepare()
    assert len(read_jsonl(directory / "assignments.jsonl")) == 8
    assert len(agents.usage) == len(agents.targets) == 4
    assert runner.state["pending"]["generation_agent_calls"] == agents.usage
    job = load_json(directory / "job.json")
    result = {k: job[k] for k in ("job_id", "checkpoint_in", "validation_digest", "training_digest")}
    result.update(checkpoint_out="fixture-next", fixture_mode=True, outcomes=baseline)
    runner.complete(result)
    assert load_json(directory / "costs.json")["agent_calls"] == agents.usage


def test_selector_api_failure_is_not_replaced_by_random_evidence():
    def unavailable(*args, **kwargs):
        raise AgentCallError("selector unavailable")
    source = fixtures()["support"][:1]
    selector = EvidenceSelector(source, SimpleNamespace(select_evidence=unavailable))
    with pytest.raises(AgentCallError, match="selector unavailable"):
        selector.select(cell_key(source[0]), 1, 42, target={}, lane="repair", intent="target")
