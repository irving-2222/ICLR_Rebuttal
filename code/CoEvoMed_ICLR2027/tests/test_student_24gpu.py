from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from coevomed.agents import generate_batch
from coevomed.curriculum import EvidenceSelector, compile_assignments
from coevomed.data import (DEMO_TASKS, digest, dump_json, evidence_exclusions, load_json,
                           load_training_job, read_jsonl, training_budget, validate_evidence_identity,
                           validate_exclusions, validate_partitions, validate_training_record, write_jsonl)
from coevomed.demo import FixtureAgents, ToyLearner, fixtures
from coevomed.feedback import summary
from coevomed.preprocessing import rgb_digest
from coevomed.principles import PrincipleRegistry
from coevomed.runner import Runner
from coevomed.student_worker import main as worker_main, training_kwargs, verify_media
from tools.run_student_24gpu import launch_command


def recipe():
    return load_json(Path(__file__).resolve().parents[1] / "configs/demo_vqarad_mimic.json")


def image_row(root, identity, role, color):
    path = root / f"{identity}.png"
    Image.new("RGB", (16, 16), color).save(path)
    return {"id": identity, "role": role, "benchmark": "vqa_rad", "evidence_id": identity,
            "images": [path.name], "image_rgb_sha256": [rgb_digest(path)],
            "split_provenance": f"independent-fixture-{role}", "task_form": "open_short",
            "visual_ability": "attribute", "modality": "synthetic", "anatomy": "none",
            "question": "Which color?", "answer": str(color)}


def exchange(root):
    training = [image_row(root, "train", "train", "red")]
    validation = [image_row(root, "valid", "validation", "blue")]
    external = [image_row(root, "test", "external", "green")]
    exclusions = evidence_exclusions(validation, external)
    config = recipe()["learner"]
    job = {"schema": "coevomed_exchange_v2", "job_id": "round_000", "checkpoint_in": "base", "fixture_mode": False,
           "training": "training.jsonl", "validation": "validation.jsonl", "exclusions": "exclusions.json",
           "training_count": len(training), "learner": config, "training_digest": digest(training),
           "validation_digest": digest(validation), "exclusions_digest": digest(exclusions),
           "training_budget": training_budget(len(training), config)}
    write_jsonl(root / "training.jsonl", training)
    write_jsonl(root / "validation.jsonl", validation)
    dump_json(root / "exclusions.json", exclusions)
    dump_json(root / "job.json", job)
    return job, training, validation, external


def completed_record(job):
    record = {key: job[key] for key in ("job_id", "checkpoint_in", "training_digest", "validation_digest", "exclusions_digest")}
    record.update(checkpoint="trained", learner_digest=digest(job["learner"]),
                  training_budget=job["training_budget"], training_steps=job["training_budget"]["training_steps"],
                  completed_epochs=job["learner"]["epochs"], training_seconds=1.0, response_tokens=12,
                  loss_reduction="response_sum_example_mean")
    return record


@pytest.mark.parametrize("count,batch,accumulation,epochs,steps", [
    (50000, 1, 1, 1, 2084), (200, 1, 1, 1, 9), (49, 1, 2, 2, 4), (97, 2, 2, 1, 2)])
def test_full_epoch_budget_includes_last_distributed_batch(count, batch, accumulation, epochs, steps):
    config = {**recipe()["learner"], "per_device_batch_size": batch,
              "gradient_accumulation_steps": accumulation, "epochs": epochs}
    budget = training_budget(count, config)
    assert budget["training_steps"] == steps
    assert budget["effective_batch_size"] == 24 * batch * accumulation


def test_max_steps_cannot_override_full_epochs():
    with pytest.raises(ValueError, match="max_steps=-1"):
        training_budget(50000, {**recipe()["learner"], "max_steps": 8})


@pytest.mark.parametrize("field,value", [
    ("training_steps", 1), ("completed_epochs", 0.01), ("exclusions_digest", "different"),
    ("loss_reduction", "token_mean"), ("training_budget", {})])
def test_partial_or_different_student_update_is_rejected(tmp_path, field, value):
    job, _, _, _ = exchange(tmp_path)
    job["training_count"] = 50000
    job["training_budget"] = training_budget(50000, job["learner"])
    record = completed_record(job)
    validate_training_record(job, record, "trained")
    record[field] = value
    with pytest.raises(ValueError, match="Training record"):
        validate_training_record(job, record, "trained")


def test_training_options_are_explicit_and_do_not_select_on_test():
    config = recipe()["learner"]
    options = training_kwargs(config, Path("worker"))
    for key in ("learning_rate", "optim", "adam_beta1", "adam_beta2", "adam_epsilon", "weight_decay",
                "warmup_ratio", "lr_scheduler_type", "max_grad_norm", "seed", "max_steps"):
        assert options[key] == config[key]
    assert options["eval_strategy"] == "no"
    assert options["load_best_model_at_end"] is False
    assert options["save_strategy"] == "no"
    assert options["dataloader_drop_last"] is False
    assert options["deepspeed"] == load_json(Path(__file__).resolve().parents[1] / "configs/zero3.json")
    options["deepspeed"]["zero_optimization"]["stage"] = 2
    assert config["deepspeed"]["zero_optimization"]["stage"] == 3


@pytest.mark.parametrize("mode", ["train", "answer"])
@pytest.mark.parametrize("rank", [0, 1, 2])
def test_three_node_launcher_uses_24_processes_and_shared_output(tmp_path, mode, rank):
    job, _, _, _ = exchange(tmp_path)
    args = SimpleNamespace(mode=mode, job=tmp_path, media_root=tmp_path, output=tmp_path / "worker",
                           node_rank=rank, master_addr="head-node", master_port=29500)
    command, manifest = launch_command(args)
    assert manifest == job
    assert "--nnodes=3" in command and "--nproc-per-node=8" in command
    assert f"--node-rank={rank}" in command
    assert "--master-addr=head-node" in command and "--max-restarts=0" in command
    assert str(tmp_path / "worker/logs" / mode / f"node_{rank}") in command
    if mode == "answer":
        assert "--inference-only" in command
        assert str(tmp_path / "worker/train/checkpoint_final") in command
        assert str(tmp_path / "worker/train/train_completed.json") in command
    else:
        assert "--inference-only" not in command


def test_check_only_verifies_pixels_without_cuda_or_checkpoint(tmp_path, capsys):
    exchange(tmp_path)
    worker_main(["--job", str(tmp_path), "--media-root", str(tmp_path),
                 "--output", str(tmp_path / "check"), "--check-only"])
    assert '"verified_images": 2' in capsys.readouterr().out
    assert not (tmp_path / "check").exists()


def test_media_replacement_is_detected(tmp_path):
    _, training, validation, _ = exchange(tmp_path)
    assert verify_media(training + validation, tmp_path) == 2
    Image.new("RGB", (16, 16), "blue").save(tmp_path / "train.png")
    with pytest.raises(ValueError, match="Image content differs"):
        verify_media(training, tmp_path)


def test_path_alias_overlap_is_rejected():
    data = fixtures()
    data["support"][0]["images"] = ["images/same.png"]
    data["external"][0]["images"] = ["images/./same.png"]
    with pytest.raises(ValueError, match="Evidence overlap"):
        validate_partitions(data["support"], data["validation"], data["external"])


@pytest.mark.parametrize("role", ["support", "validation", "train"])
def test_external_role_cannot_be_relabeled_for_adaptation(role):
    data = fixtures()
    row = deepcopy(data["external"][0])
    row.update(role=role, reserved_external=True)
    values = {"support": data["support"], "validation": data["validation"], "original": []}
    values["original" if role == "train" else role].append(row)
    with pytest.raises(ValueError, match="Reserved external"):
        validate_partitions(values["support"], values["validation"], data["external"], values["original"])


def test_real_inputs_require_rgb_identity_and_provenance(tmp_path):
    _, training, _, _ = exchange(tmp_path)
    validate_evidence_identity(training[0])
    del training[0]["image_rgb_sha256"]
    with pytest.raises(ValueError, match="RGB SHA256"):
        validate_evidence_identity(training[0])


@pytest.mark.parametrize("heldout", ["validation", "external"])
def test_copied_heldout_pixels_cannot_enter_training_under_new_id(tmp_path, heldout):
    _, training, validation, external = exchange(tmp_path)
    copied = deepcopy((validation if heldout == "validation" else external)[0])
    copied.update(id="new-id", evidence_id="new-evidence", role="train", images=["different-file.png"])
    with pytest.raises(ValueError, match="Training evidence overlaps"):
        validate_exclusions(training + [copied], validation, evidence_exclusions(validation, external))


def test_exclusion_inventory_contains_no_external_questions_or_answers(tmp_path):
    _, _, validation, external = exchange(tmp_path)
    inventory = evidence_exclusions(validation, external)
    assert set(inventory) == {"validation", "external"}
    assert all(len(item) == 64 for values in inventory.values() for item in values)
    assert external[0]["question"] not in str(inventory) and external[0]["answer"] not in str(inventory)


def test_tampered_exclusion_file_is_rejected(tmp_path):
    exchange(tmp_path)
    inventory = load_json(tmp_path / "exclusions.json")
    inventory["external"] = []
    dump_json(tmp_path / "exclusions.json", inventory)
    with pytest.raises(ValueError, match="Transferred exclusions"):
        load_training_job(tmp_path)


def test_generated_rows_retain_source_identity():
    data = fixtures()
    for row in data["support"]:
        row.update(image_rgb_sha256=[digest(row["id"])], study_id=row["evidence_id"], split_provenance="fixture-source")
    stats = summary(data["validation"], ToyLearner().outcomes(data["validation"]))
    assignments = compile_assignments(stats, EvidenceSelector(data["support"], FixtureAgents()), {t: 1 for t in DEMO_TASKS}, "balanced", episode=0)
    rows, rejected = generate_batch(assignments, PrincipleRegistry(), FixtureAgents(), [])
    assert not rejected
    sources = {a["source"]["id"]: a["source"] for a in assignments}
    for row in rows:
        for key in ("image_rgb_sha256", "study_id", "split_provenance"):
            assert row[key] == sources[row["source_id"]][key]


def test_prepare_exports_only_exclusion_fingerprints_for_external(tmp_path):
    data = {role: [r for r in rows if r["benchmark"] in DEMO_TASKS] for role, rows in fixtures().items()}
    config = {"seed": 42, "horizon": 1, "revision_every": 3, "workers": 1, "active_tasks": list(DEMO_TASKS),
              "task_quotas": {t: 3 for t in DEMO_TASKS}, "fixture_mode": True, "learner": {"backend": "toy"}}
    Runner.initialize(tmp_path, config, data["support"], data["validation"], data["external"],
                      ToyLearner().outcomes(data["validation"]))
    runner = Runner(tmp_path, FixtureAgents())
    directory = runner.prepare()
    assert not (directory / "external.jsonl").exists()
    assert load_json(directory / "exclusions.json") == evidence_exclusions(data["validation"], data["external"])
    assert all(r["role"] == "train" for r in read_jsonl(directory / "training.jsonl"))
