from copy import deepcopy
import time

import numpy as np
import torch
from torch import nn

from .data import DEMO_TASKS, REPORTS, TASKS, digest, dump_json, load_json, read_jsonl, write_jsonl
from .runner import Runner


class FixtureAgents:
    usage = ()

    def plan(self, cell, lane):
        return f"Fixture {lane} target: distinguish the supported synthetic color"

    def select_evidence(self, candidates, *, target, lane, intent, count):
        # Deterministic test double; model-backed runs use the configured selector LLM.
        return [r["id"] for r in candidates[:count]]

    def construct(self, assignment, principle):
        source = assignment["source"]
        revised = principle["version"] > 0
        prefix = "Contrast the marked and unmarked region" if revised else "Identify the marked color"
        return {"question": f"{prefix} in synthetic example {source['id']}?",
                "answer": source["facts"][0]["text"], "fact_ids": [source["facts"][0]["id"]]}

    def verify(self, assignment, candidate):
        valid = candidate["answer"] == assignment["source"]["facts"][0]["text"]
        return {"factual": valid, "visual": valid, "aligned": valid, "valid": valid,
                "reason": "Fixture oracle, not an LLM image assessment"}

    def revise(self, active, cells):
        strategy = deepcopy(active["strategy"])
        strategy["question_strategy"] = ["Contrast the supported marked color with an explicitly unmarked region"]
        return strategy, "Fixture residual classification error", {"error_semantics": ["marked-region confusion"]}

    def review(self, active, candidate, feedback, pairs):
        applied = bool(pairs) and all(p["candidate"]["question"].startswith("Contrast") for p in pairs)
        return {"applied": applied, "alignment": "improved" if applied else "same", "evidence_preserved": True,
                "reason": "Fixture-only semantic oracle; not evidence of clinical improvement"}


def fixtures(seed=42):
    rng = np.random.default_rng(seed)
    result = {}
    teacher = rng.normal(size=(4, 3))
    for role, count in (("support", 240), ("validation", 30), ("external", 12)):
        rows = []
        for task in TASKS:
            for index in range(count):
                features = rng.normal(size=4)
                label = int((features @ teacher).argmax())
                identity = f"fixture-{role}-{task}-{index:04d}"
                row = {"id": identity, "role": role, "benchmark": task, "evidence_id": identity,
                       "images": [f"{identity}.png"], "toy_features": features.tolist(), "toy_label": label,
                       "task_form": "report_gen" if task in REPORTS else "open_short",
                       "visual_ability": "holistic_description" if task in REPORTS else "attribute",
                       "modality": "synthetic", "anatomy": "none",
                       "question": f"Which fixture color is marked in panel {identity}?", "answer": ["red", "green", "blue"][label]}
                if role == "support":
                    row["facts"] = [{"id": f"{identity}-f0", "text": row["answer"]}]
                rows.append(row)
        result[role] = rows
    return result


class ToyLearner:
    def __init__(self, seed=42):
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed)
            self.model = nn.Linear(4, 3)

    def outcomes(self, panel):
        with torch.no_grad():
            logits = self.model(torch.tensor([r["toy_features"] for r in panel], dtype=torch.float32))
            predictions = logits.argmax(-1).tolist()
        rows = []
        for r, predicted in zip(panel, predictions):
            correct = predicted == r["toy_label"]
            row = {"id": r["id"], "benchmark": r["benchmark"], "role": "validation",
                   "prediction": ["red", "green", "blue"][predicted], "correct": correct,
                   "metric_protocol": "fixture-classification-proxy-not-medical"}
            if r["benchmark"] in REPORTS:
                row["metrics"] = {k: 0.7 if correct else 0.1 for k in ("rougeL", "bleu4", "meteor")}
            rows.append(row)
        return rows

    def train(self, rows):
        x = torch.tensor([r["toy_features"] for r in rows], dtype=torch.float32)
        y = torch.tensor([r["toy_label"] for r in rows], dtype=torch.long)
        optimizer = torch.optim.SGD(self.model.parameters(), lr=0.03)
        before = float(nn.functional.cross_entropy(self.model(x), y).detach())
        for _ in range(5):
            optimizer.zero_grad(); loss = nn.functional.cross_entropy(self.model(x), y)
            loss.backward(); optimizer.step()
        after = float(nn.functional.cross_entropy(self.model(x), y).detach())
        return {"loss_before": before, "loss_after": after}


def run_demo(root, rounds=6, seed=42, tasks=DEMO_TASKS):
    torch.set_num_threads(1)
    data = fixtures(seed)
    data = {role: [r for r in rows if r["benchmark"] in tasks] for role, rows in data.items()}
    config = {"seed": seed, "horizon": rounds, "revision_every": 3, "workers": 4,
              "active_tasks": list(tasks), "task_quotas": {t: 120 for t in tasks}, "fixture_mode": True,
              "min_principle_usage": 100, "original_count": 0, "learner": {"backend": "toy", "epochs": 1}}
    learner = ToyLearner(seed); agents = FixtureAgents()
    Runner.initialize(root, config, data["support"], data["validation"], data["external"],
                      learner.outcomes(data["validation"]), checkpoint="fixture-base")
    from pathlib import Path
    root = Path(root)
    trajectory = []
    for _ in range(rounds):
        runner = Runner(root, agents)
        directory = runner.prepare()
        rows = read_jsonl(directory / "training.jsonl"); job = load_json(directory / "job.json")
        start = time.monotonic(); loss = learner.train(rows)
        torch.save(learner.model.state_dict(), directory / "toy_learner.pt")
        result = {k: job[k] for k in ("job_id", "checkpoint_in", "training_digest", "validation_digest")}
        result.update({"checkpoint_out": f"fixture-round-{job['round']}", "fixture_mode": True,
                       "outcomes": learner.outcomes(data["validation"]), "learner_seconds": time.monotonic() - start})
        report = runner.complete(result)
        report.update(loss); trajectory.append(report)
        print(f"Round {job['round']}: reward={report['reward']:+.5f}; PPO update={report['ppo_update']}; "
              f"NLL={loss['loss_before']:.4f}->{loss['loss_after']:.4f}; principles={report['principle_decisions']}", flush=True)
    dump_json(root / "demo_summary.json", {"mode": "synthetic_fixture_with_real_toy_training",
              "not_paper_results": True, "rounds": trajectory, "ppo_updates": rounds, "optimizer_steps": 4 * rounds})
    return trajectory
