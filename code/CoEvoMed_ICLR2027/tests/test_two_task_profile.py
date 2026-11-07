from copy import deepcopy

import pytest
import torch

from coevomed.data import DEMO_TASKS, TASKS, validate_partitions
from coevomed.demo import fixtures, ToyLearner
from coevomed.feedback import summary, state_vector
from coevomed.policy import Controller
from coevomed.pretrain import build_states


def selected_data():
    return {role: [r for r in rows if r["benchmark"] in DEMO_TASKS] for role, rows in fixtures().items()}


def test_two_task_reward_does_not_average_absent_benchmarks():
    data = selected_data(); panel = data["validation"]
    old = ToyLearner().outcomes(panel); new = deepcopy(old)
    for a, b in zip(old, new):
        if a["benchmark"] == "vqa_rad":
            a["correct"] = False; b["correct"] = True
        else:
            a["metrics"] = dict(rougeL=0.2, bleu4=0.2, meteor=0.2)
            b["metrics"] = dict(rougeL=0.4, bleu4=0.4, meteor=0.4)
    stats = summary(panel, new, old)
    assert stats["reward"] == pytest.approx(0.6)
    assert set(stats["tasks"]) == set(DEMO_TASKS)
    vector = state_vector(stats, episode=1, horizon=6)
    assert len(vector) == 40
    for index, task in enumerate(TASKS):
        if task not in DEMO_TASKS:
            assert vector[index * 5:index * 5 + 5] == [0.0] * 5
    assert vector[30] == pytest.approx(1.0)
    assert vector[31] == pytest.approx(0.4)


def test_two_task_partition_rejects_unselected_data():
    data = selected_data()
    validate_partitions(data["support"], data["validation"], data["external"], active_tasks=DEMO_TASKS)
    unrelated = next(r for r in fixtures()["support"] if r["benchmark"] == "slake")
    with pytest.raises(ValueError, match="outside"):
        validate_partitions(data["support"] + [unrelated], data["validation"], data["external"], active_tasks=DEMO_TASKS)


def test_two_task_bc_states_keep_inactive_slots_zero():
    data = selected_data()
    stats = summary(data["validation"], ToyLearner().outcomes(data["validation"]))
    states = build_states(stats)
    assert len(states) == 800
    for row in states:
        assert row["active_tasks"] == list(DEMO_TASKS)
        assert set(row["task_summary"]) == set(DEMO_TASKS)
        assert row["features"][5:20] == [0.0] * 15
        assert row["features"][25:30] == [0.0] * 5


def test_actor_profile_must_match_demo_tasks(tmp_path):
    controller = Controller()
    path = tmp_path / "actor.pt"
    torch.save({"model": controller.model.state_dict(), "active_tasks": list(TASKS)}, path)
    with pytest.raises(ValueError, match="profile"):
        controller.load_actor(path, active_tasks=DEMO_TASKS)
    torch.save({"model": controller.model.state_dict(), "active_tasks": list(DEMO_TASKS)}, path)
    controller.load_actor(path, active_tasks=DEMO_TASKS)
    assert torch.count_nonzero(controller.model.critic.weight) == 0


def test_single_family_cannot_silently_change_reward_definition():
    panel = [r for r in fixtures()["validation"] if r["benchmark"] == "vqa_rad"]
    with pytest.raises(ValueError, match="both VQA and report"):
        summary(panel, ToyLearner().outcomes(panel))
