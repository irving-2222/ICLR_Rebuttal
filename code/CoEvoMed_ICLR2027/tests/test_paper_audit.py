from copy import deepcopy
from types import SimpleNamespace

import pytest
import torch

from coevomed.curriculum import validate_training_composition
from coevomed.data import DEMO_TASKS, TASKS, load_json, read_jsonl, write_jsonl
from coevomed.demo import FixtureAgents, ToyLearner, fixtures
from coevomed.feedback import state_vector, summary
from coevomed.preprocessing import normalize_native, report_sections, stratified_validation
from coevomed.principles import eligible_principles, matched_assignments, usage_by_version
from coevomed.runner import Runner
from coevomed.student_worker import ResponseNLLMixin, response_nll


def test_equation10_sums_tokens_then_averages_examples():
    logits = torch.zeros(2, 5, 3, requires_grad=True)
    labels = torch.tensor([[-100, -100, 1, -100, -100], [-100, 2, 1, 0, -100]])
    loss = response_nll(logits, labels)
    assert float(loss.detach()) == pytest.approx(2 * torch.log(torch.tensor(3.)).item())
    loss.backward()
    assert logits.grad[0, 0].abs().sum() == 0
    assert logits.grad[0, 1].abs().sum() > 0
    assert logits.grad[1, 4].abs().sum() == 0


def test_loss_adapter_ignores_trainer_token_denominator():
    class TrainerBase:
        pass

    class Trainer(ResponseNLLMixin, TrainerBase):
        pass

    trainer = Trainer()
    logits = torch.zeros(1, 4, 3)
    batch = {"input_ids": torch.tensor([[1, 1, 1, 1]]), "labels": torch.tensor([[-100, 1, 2, 0]])}
    seen = []

    def model(**inputs):
        seen.append(inputs)
        return SimpleNamespace(logits=logits)

    loss, output = trainer.compute_loss(model, batch, return_outputs=True, num_items_in_batch=3)
    assert float(loss) == pytest.approx(3 * torch.log(torch.tensor(3.)).item())
    assert "labels" not in seen[0] and "labels" in batch
    assert output.logits is logits
    assert trainer.model_accepts_loss_kwargs is False


def test_empty_response_cannot_contribute_zero_loss():
    with pytest.raises(ValueError, match="response token"):
        response_nll(torch.zeros(2, 3, 4), torch.full((2, 3), -100))


def test_principle_statistics_do_not_mix_versions_or_unexposed_rounds():
    cell = {"principle_id": "p", "count": 6, "net_repair": -2, "persistent_gap": 4}
    first = {"usage": {"p": {"version": 0, "count": 100}}, "cells": {"c": cell}}
    improved = {"usage": {"p": {"version": 1, "count": 100}},
                "cells": {"c": {**cell, "net_repair": 1}}}
    assert eligible_principles([first, improved], active_versions={"p": 1}) == []
    assert eligible_principles([first, improved], active_versions={"p": 0}) == ["p"]
    unexposed = {"usage": {}, "cells": {"c": {**cell, "net_repair": 10}}}
    assert eligible_principles([first, unexposed], active_versions={"p": 0}) == ["p"]


def test_usage_tracks_active_version():
    rows = [{"principle_id": "p", "principle_version": 2}] * 3
    assert usage_by_version(rows) == {"p": {"version": 2, "count": 3}}
    with pytest.raises(ValueError, match="multiple versions"):
        usage_by_version(rows + [{"principle_id": "p", "principle_version": 1}])


def test_new_regressions_do_not_need_a_persistent_gap_to_be_eligible():
    window = [{"usage": {"p": {"version": 0, "count": 100}},
               "cells": {"c": {"principle_id": "p", "count": 3, "net_repair": -1, "persistent_gap": 0}}}]
    assert eligible_principles(window, active_versions={"p": 0}) == ["p"]


@pytest.mark.parametrize("count,supported", [(2, False), (3, True)])
def test_sparse_cell_status_preserves_task_scores_and_ppo_state(count, supported):
    panel = fixtures()["validation"]
    for row in [r for r in panel if r["benchmark"] == "vqa_rad"][:count]:
        row["task_form"] = "closed_binary"
    old = ToyLearner().outcomes(panel)
    new = deepcopy(old)
    new[0]["correct"] = not old[0]["correct"]
    original = summary(panel, new, old)
    filtered = summary(panel, new, old, min_cell_count=3)
    cell = next(c for c in filtered["cells"].values()
                if c["benchmark"] == "vqa_rad" and c["task_form"] == "closed_binary")
    assert cell["count"] == count and cell["supported"] is supported
    assert filtered["tasks"] == original["tasks"]
    assert filtered["reward"] == original["reward"]
    assert state_vector(filtered, episode=1, horizon=6) == state_vector(original, episode=1, horizon=6)


@pytest.mark.parametrize("net_repair,expected", [(1, []), (-1, ["p"])])
def test_sparse_repairs_and_regressions_cannot_change_principle_eligibility(net_repair, expected):
    cells = {"supported": {"principle_id": "p", "count": 3, "net_repair": net_repair, "persistent_gap": 0},
             "sparse": {"principle_id": "p", "count": 2, "net_repair": -2 * net_repair, "persistent_gap": 0}}
    window = [{"usage": {"p": {"version": 0, "count": 100}}, "cells": cells}]
    assert eligible_principles(window, min_cell_count=3) == expected


def test_repeated_sparse_cells_cannot_establish_supported_feedback():
    cell = {"principle_id": "p", "count": 2, "net_repair": -1, "persistent_gap": 1}
    window = [{"usage": {"p": {"version": 0, "count": 100}}, "cells": {"c": cell}}] * 3
    assert eligible_principles(window, min_cell_count=3) == []
    assert eligible_principles([{**window[0], "cells": {}}], min_cell_count=3) == []


def test_sparse_gaps_do_not_change_principle_priority():
    cells = {"p": {"principle_id": "p", "count": 3, "net_repair": 0, "persistent_gap": 1},
             "q": {"principle_id": "q", "count": 3, "net_repair": 0, "persistent_gap": 2},
             "sparse": {"principle_id": "p", "count": 2, "net_repair": 0, "persistent_gap": 2}}
    window = [{"usage": {k: {"version": 0, "count": 100} for k in ("p", "q")}, "cells": cells}]
    assert eligible_principles(window, min_cell_count=3) == ["q", "p"]


@pytest.mark.parametrize("net_repair", [-1, 1])
def test_runner_excludes_sparse_cells_from_revision_feedback(tmp_path, net_repair):
    class RecordingAgents(FixtureAgents):
        def __init__(self):
            self.revisions = []

        def revise(self, active, cells):
            self.revisions.append(deepcopy(cells))
            return super().revise(active, cells)

    data = {role: [r for r in rows if r["benchmark"] in DEMO_TASKS]
            for role, rows in fixtures().items()}
    vqa = [r for r in data["validation"] if r["benchmark"] == "vqa_rad"]
    for row in vqa[:2]:
        row["task_form"] = "closed_binary"
    baseline = ToyLearner().outcomes(data["validation"])
    indexed = {r["id"]: r for r in baseline}
    for row in vqa[:2]:
        indexed[row["id"]]["correct"] = net_repair == 1
    indexed[vqa[2]["id"]]["correct"] = net_repair == -1
    outcomes = deepcopy(baseline)
    for row in outcomes:
        if row["id"] in {r["id"] for r in vqa[:3]}:
            row["correct"] = not row["correct"]
    config = {"seed": 42, "horizon": 1, "revision_every": 1, "workers": 1,
              "active_tasks": list(DEMO_TASKS), "task_quotas": {t: 3 for t in DEMO_TASKS},
              "min_cell_count": 3, "min_principle_usage": 1,
              "fixture_mode": True, "learner": {"backend": "toy"}}
    Runner.initialize(tmp_path, config, data["support"], data["validation"], data["external"], baseline)
    agents = RecordingAgents()
    runner = Runner(tmp_path, agents)
    initial_cells = list(runner.state["summary"]["cells"].values())
    assert [c["task_form"] for c in initial_cells if not c["supported"]] == ["closed_binary"]
    directory = runner.prepare()
    job = load_json(directory / "job.json")
    result = {k: job[k] for k in ("job_id", "checkpoint_in", "training_digest", "validation_digest")}
    result.update({"checkpoint_out": "fixture-new", "fixture_mode": True, "outcomes": outcomes})
    runner.complete(result)
    expected_tasks = set(DEMO_TASKS) if net_repair < 0 else {"mimic_cxr"}
    assert {c["benchmark"] for cells in agents.revisions for c in cells} == expected_tasks
    assert all(c["count"] >= 3 and c["supported"] for cells in agents.revisions for c in cells)
    feedback = load_json(directory / "feedback.json")
    assert [c["task_form"] for c in feedback["cells"].values() if not c["supported"]] == ["closed_binary"]
    assert feedback["reward"] == summary(data["validation"], outcomes, baseline)["reward"]
    assert runner.controller.update_index == 1


def test_probe_counts_assignments_not_unique_images():
    rows = [{"id": f"a{i}", "principle_id": "p", "source": {"evidence_id": f"image{i % 60}"}}
            for i in range(130)]
    selected = matched_assignments(rows, "p")
    assert len(selected) == len({r["id"] for r in selected}) == 100
    assert len({r["source"]["evidence_id"] for r in selected}) == 60
    assert matched_assignments(rows[:20], "p") == rows[:20]
    with pytest.raises(ValueError, match="Duplicate"):
        matched_assignments(rows + [rows[0]], "p")


def test_report_sections_are_explicit_and_facts_keep_section(tmp_path):
    from PIL import Image
    Image.new("RGB", (4, 4)).save(tmp_path / "x.png")
    row = next(deepcopy(r) for r in fixtures()["support"] if r["benchmark"] == "mimic_cxr")
    row.pop("facts")
    row.update({"images": ["x.png"], "source_kind": "report", "split_provenance": "permitted_source",
                "answer": "FINDINGS: No left effusion. Heart size is normal. IMPRESSION: No acute disease."})
    normalized = normalize_native(row, role="support", media_root=tmp_path)
    assert set(normalized["report_sections"]) == {"findings", "impression"}
    assert [f["section"] for f in normalized["facts"]] == ["findings", "findings", "impression"]
    assert normalized["facts"][0]["text"] == "No left effusion."
    assert normalized["answer"] == row["answer"]
    assert report_sections({"answer": "No acute disease."}) == {"unsectioned": "No acute disease."}
    assert report_sections({"findings": "No effusion.", "impression": "No acute disease."}) == {
        "findings": "No effusion.", "impression": "No acute disease."}


def test_validation_count_is_per_task():
    data = fixtures()["validation"]
    with pytest.raises(ValueError, match="per task"):
        stratified_validation(data, 6)
    selected = stratified_validation([r for r in data if r["benchmark"] == "vqa_rad"], 20)
    assert len(selected) == 20


def test_realized_mixture_checks_original_data_too():
    rows = [{"benchmark": "vqa_rad", "task_form": "open_short"},
            {"benchmark": "mimic_cxr", "task_form": "report_gen"}]
    constraints = {"family_counts": {"vqa": 1, "report": 1}, "vqa_form_counts": {"open_short": 1}}
    validate_training_composition(rows, constraints)
    with pytest.raises(ValueError, match="family counts"):
        validate_training_composition(rows + [rows[0]], constraints)
    rows[0]["task_form"] = "mcq"
    with pytest.raises(ValueError, match="form counts"):
        validate_training_composition(rows, constraints)


def test_frozen_input_edits_fail_on_resume(tmp_path):
    data = fixtures()
    config = {"seed": 42, "horizon": 2, "revision_every": 3, "workers": 1,
              "task_quotas": {t: 1 for t in TASKS}, "fixture_mode": True, "learner": {"backend": "toy"}}
    root = tmp_path / "run"
    Runner.initialize(root, config, data["support"], data["validation"], data["external"],
                      ToyLearner().outcomes(data["validation"]))
    path = root / "inputs/validation.jsonl"
    rows = read_jsonl(path)
    rows[0]["answer"] = "changed reference"
    write_jsonl(path, rows)
    with pytest.raises(ValueError, match="Frozen input changed: validation"):
        Runner(root, FixtureAgents())


def test_reference_recipe_requires_explicit_confirmation(tmp_path):
    data = fixtures()
    config = {"horizon": 2, "revision_every": 3, "workers": 1, "review_required": True,
              "recipe_confirmed": False, "task_quotas": {t: 1 for t in TASKS}}
    with pytest.raises(ValueError, match="Confirm the experiment recipe"):
        Runner.initialize(tmp_path, config, data["support"], data["validation"], data["external"],
                          ToyLearner().outcomes(data["validation"]))
