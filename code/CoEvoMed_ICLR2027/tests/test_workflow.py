import json

import pytest

from coevomed.data import load_json
from coevomed.demo import FixtureAgents, run_demo
from coevomed.runner import Runner


def test_six_round_closed_loop(tmp_path):
    root = tmp_path / "run"
    trajectory = run_demo(root, rounds=6)
    assert len(trajectory) == 6
    assert all(r["loss_after"] < r["loss_before"] for r in trajectory)
    assert [r["ppo_update"] for r in trajectory] == list(range(1, 7))
    state = load_json(root / "state.json")
    assert state["next_round"] == 6 and state["pending"] is None
    assert load_json(root / "round_005/ppo.json")["terminal"] is True
    for round_id in range(6):
        ppo = load_json(root / f"round_{round_id:03d}/ppo.json")
        assert len(ppo["epochs"]) == 4
        assert ppo["epochs"][0]["ratio"] == pytest.approx(1.0)
        job = load_json(root / f"round_{round_id:03d}/job.json")
        assert "external" not in job
        assert set(job["counts"]["candidate"]) == {"vqa_rad", "mimic_cxr"}
        assert set(job["counts"]["training"]) == {"vqa_rad", "mimic_cxr"}
    with pytest.raises(ValueError, match="complete"):
        Runner(root, FixtureAgents()).prepare()
    with pytest.raises(ValueError, match="No pending"):
        Runner(root, FixtureAgents()).complete({})


def test_changed_metric_protocol_cannot_update_policy(tmp_path):
    from coevomed.demo import ToyLearner, fixtures
    from coevomed.data import TASKS
    data = fixtures(); learner = ToyLearner(); root = tmp_path / "run"
    config = {"seed": 42, "horizon": 2, "revision_every": 3, "workers": 1,
              "task_quotas": {t: 1 for t in TASKS}, "fixture_mode": True, "learner": {"backend": "toy"}}
    baseline = learner.outcomes(data["validation"])
    Runner.initialize(root, config, data["support"], data["validation"], data["external"], baseline)
    runner = Runner(root, FixtureAgents()); directory = runner.prepare()
    job = load_json(directory / "job.json")
    result = {k: job[k] for k in ("job_id", "checkpoint_in", "validation_digest", "training_digest")}
    result.update({"checkpoint_out": "fixture-new", "fixture_mode": True, "outcomes": baseline})
    result["outcomes"][0]["metric_protocol"] = "different-judge"
    before = runner.controller.weights_digest()
    with pytest.raises(ValueError, match="protocol"):
        runner.complete(result)
    assert runner.controller.weights_digest() == before
    assert runner.controller.update_index == 0
