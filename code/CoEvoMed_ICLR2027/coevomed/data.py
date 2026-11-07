from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path, PurePosixPath

TASKS = ("vqa_rad", "slake", "pmc_vqa", "pathvqa", "mimic_cxr", "iu_xray")
DEMO_TASKS = ("vqa_rad", "mimic_cxr")
REPORTS = frozenset(TASKS[4:])
FORMS = ("closed_binary", "open_short", "open_long", "mcq", "report_gen")
ABILITIES = (
    "modality_recognition", "organ_recognition", "localization", "spatial_relation",
    "abnormality_detection", "attribute", "comparison", "holistic_description",
    "medical_knowledge",
)
AXES = ("task_form", "visual_ability", "modality", "anatomy")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=True, allow_nan=False) + "\n")
    tmp.replace(path)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def training_budget(count, learner):
    fields = (count, learner["world_size"], learner["per_device_batch_size"],
              learner["gradient_accumulation_steps"], learner["epochs"])
    if any(type(v) is not int or v <= 0 for v in fields) or learner.get("max_steps") != -1:
        raise ValueError("Student updates require positive integer budgets and max_steps=-1")
    count, world, batch, accumulation, epochs = fields
    batches = math.ceil(count / (world * batch))
    steps = math.ceil(batches / accumulation)
    return {"training_count": count, "world_size": world, "epochs": epochs,
            "effective_batch_size": world * batch * accumulation,
            "batches_per_rank": batches, "steps_per_epoch": steps, "training_steps": epochs * steps}


def validate_training_record(job, record, checkpoint):
    if not isinstance(record, dict):
        raise ValueError("A completed training record is required for learner feedback")
    for key in ("job_id", "checkpoint_in", "training_digest", "validation_digest", "exclusions_digest"):
        if record.get(key) != job[key]:
            raise ValueError(f"Training record does not match job: {key}")
    if record.get("learner_digest") != digest(job["learner"]):
        raise ValueError("Training record does not match learner settings")
    if not checkpoint or record.get("checkpoint") != checkpoint or checkpoint == job["checkpoint_in"]:
        raise ValueError("Training record does not match the new checkpoint")
    if type(record.get("training_steps")) is not int or record["training_steps"] <= 0:
        raise ValueError("Training record must contain a positive optimizer step count")
    expected = training_budget(job["training_count"], job["learner"])
    if job.get("training_budget") != expected or record.get("training_budget") != expected:
        raise ValueError("Training record does not match the planned training budget")
    if record["training_steps"] != expected["training_steps"]:
        raise ValueError("Training record optimizer steps differ from the full-epoch budget")
    epoch = record.get("completed_epochs")
    if not isinstance(epoch, (int, float)) or isinstance(epoch, bool) or not math.isclose(epoch, expected["epochs"], abs_tol=1e-6):
        raise ValueError("Training record does not complete the prescribed epochs")
    if record.get("loss_reduction") != "response_sum_example_mean":
        raise ValueError("Training record uses a different response loss")
    for key in ("training_seconds", "response_tokens"):
        value = record.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"Training record needs a positive {key}")


def unit_score(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Metric must be a numeric score, not a flag or string")
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("All input metrics must be finite and scaled to [0, 1]")
    return value


def validate_record(row, role):
    if row.get("role") != role or not row.get("id") or row.get("benchmark") not in TASKS:
        raise ValueError("Record requires a unique ID, known benchmark, and explicit role")
    if role != "external" and row.get("reserved_external"):
        raise ValueError("Reserved external evidence cannot enter adaptation")
    for key in AXES:
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError(f"Missing axis {key}")
    if row["task_form"] not in FORMS or row["visual_ability"] not in ABILITIES:
        raise ValueError("Task form / visual ability is outside the frozen ontology")
    if (row["benchmark"] in REPORTS) != (row["task_form"] == "report_gen"):
        raise ValueError("Report task/form mismatch")
    if not row.get("evidence_id") or not isinstance(row.get("images"), list) or not row["images"]:
        raise ValueError("Evidence ID and ordered image paths are required")
    for name in row["images"]:
        if not isinstance(name, str) or not name or PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts:
            raise ValueError("Media paths must be nonempty relative paths without parent traversal")
    if role == "support":
        facts = row.get("facts", [])
        if not facts or any(not f.get("id") or not f.get("text") for f in facts):
            raise ValueError("Support records need nonempty factual evidence")
        if len({f["id"] for f in facts}) != len(facts):
            raise ValueError("Duplicate fact IDs")
    elif not row.get("question") or not row.get("answer"):
        raise ValueError("Question and reference answer must be nonempty")


def validate_evidence_identity(row):
    hashes = row.get("image_rgb_sha256")
    if not isinstance(hashes, list) or len(hashes) != len(row["images"]) or any(
            not isinstance(h, str) or len(h) != 64 or any(c not in "0123456789abcdef" for c in h) for h in hashes):
        raise ValueError("Every real image requires its decoded RGB SHA256")
    if not isinstance(row.get("split_provenance"), str) or row["split_provenance"].strip().lower() in {"", "unknown"}:
        raise ValueError("Real evidence requires original split provenance")


def identity_tokens(row):
    tokens = {("id", row["id"]), ("evidence", row["evidence_id"])}
    tokens.update(("image", PurePosixPath(p).as_posix()) for p in row.get("images", []))
    tokens.update(("rgb", str(p)) for p in row.get("image_rgb_sha256", []))
    if row.get("study_id"):
        tokens.add(("study", str(row["study_id"])))
    return tokens


def evidence_exclusions(validation, external):
    return {role: sorted({digest(token) for row in rows for token in identity_tokens(row)})
            for role, rows in (("validation", validation), ("external", external))}


def validate_exclusions(training, validation, exclusions):
    if set(exclusions) != {"validation", "external"} or any(not isinstance(v, list) or not v for v in exclusions.values()):
        raise ValueError("Both held-out identity inventories are required")
    known_validation = {digest(t) for r in validation for t in identity_tokens(r)}
    if known_validation != set(exclusions["validation"]):
        raise ValueError("Validation identities differ from the exclusion inventory")
    if known_validation & set(exclusions["external"]):
        raise ValueError("Evidence overlap between validation and external")
    train_ids = {digest(t) for r in training for t in identity_tokens(r)}
    if train_ids & (known_validation | set(exclusions["external"])):
        raise ValueError("Training evidence overlaps validation or external evaluation")


def load_training_job(directory):
    directory = Path(directory)
    job = load_json(directory / "job.json")
    if job.get("schema") != "coevomed_exchange_v2":
        raise ValueError("Prepare a new coevomed_exchange_v2 job with budget and exclusion metadata")
    if job.get("fixture_mode"):
        raise ValueError("Synthetic fixtures are not medical SFT inputs")
    for key in ("training", "validation", "exclusions"):
        if Path(job[key]).name != job[key]:
            raise ValueError("Exchange files must be inside the job directory")
    training = read_jsonl(directory / job["training"])
    validation = read_jsonl(directory / job["validation"])
    exclusions = load_json(directory / job["exclusions"])
    for name, value in (("training", training), ("validation", validation), ("exclusions", exclusions)):
        if digest(value) != job[f"{name}_digest"]:
            raise ValueError(f"Transferred {name} differs from its manifest")
    if not validation or len({r["id"] for r in validation}) != len(validation):
        raise ValueError("Validation must contain distinct fixed cases")
    for role, rows in (("train", training), ("validation", validation)):
        for row in rows:
            validate_record(row, role)
            validate_evidence_identity(row)
    validate_exclusions(training, validation, exclusions)
    budget = training_budget(len(training), job["learner"])
    if job["training_count"] != len(training) or job.get("training_budget") != budget:
        raise ValueError("Job training count or budget is inconsistent")
    return job, training, validation


def validate_partitions(support, validation, external, original=(), *, require_all_tasks=True, active_tasks=TASKS,
                        require_identity=False):
    if not active_tasks or not set(active_tasks) <= set(TASKS):
        raise ValueError("Unknown or empty active task profile")
    partitions = {"support": support, "validation": validation, "external": external, "train": original}
    tokens = {}
    for role, rows in partitions.items():
        ids = set()
        for row in rows:
            validate_record(row, role)
            if require_identity:
                validate_evidence_identity(row)
            if row["benchmark"] not in active_tasks:
                raise ValueError("Input includes a task outside the frozen demo profile")
            if row["id"] in ids:
                raise ValueError(f"Duplicate ID within {role}")
            ids.add(row["id"])
        tokens[role] = set().union(*(identity_tokens(r) for r in rows)) if rows else set()
    if not validation or not external:
        raise ValueError("Both feedback and external evaluation inventories are required")
    for left, right in (("validation", "external"), ("support", "validation"),
                        ("support", "external"), ("train", "validation"), ("train", "external")):
        if tokens[left] & tokens[right]:
            raise ValueError(f"Evidence overlap between {left} and {right}")
    if require_all_tasks and {r["benchmark"] for r in validation} != set(active_tasks):
        raise ValueError("Validation must cover every active feedback task")


def cell_key(row):
    return "::".join([row["benchmark"], *(row[k] for k in AXES)])


def principle_key(row):
    return "::".join(row[k] for k in ("benchmark", "visual_ability", "modality", "anatomy"))


def to_qwen(row):
    return {
        "id": row["id"], "image": row["images"],
        "conversations": [
            {"from": "human", "value": "<image>\n" * len(row["images"]) + row["question"]},
            {"from": "gpt", "value": row["answer"]},
        ],
        "metadata": {k: row[k] for k in ("benchmark", "evidence_id", "source_id", "fact_ids",
                    "principle_id", "principle_version", "lane") if k in row},
    }
