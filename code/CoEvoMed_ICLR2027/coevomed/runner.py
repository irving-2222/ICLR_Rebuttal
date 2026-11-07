from collections import Counter
from dataclasses import asdict
from pathlib import Path
import time

from .agents import AgentCallError, generate_batch, near_validation_copy
from .curriculum import EvidenceSelector, compile_assignments, mix_training, validate_training_composition
from .data import (TASKS, digest, dump_json, evidence_exclusions, load_json, read_jsonl, to_qwen,
                   training_budget, validate_exclusions, validate_partitions, validate_training_record, write_jsonl)
from .feedback import state_vector, summary
from .policy import Controller, Decision
from .principles import (PrincipleRegistry, eligible_principles, matched_assignments,
                         probe_decision, usage_by_version)


class Runner:
    def __init__(self, root, agents):
        self.root = Path(root)
        self.agents = agents
        self.config = load_json(self.root / "config.json")
        self.state = load_json(self.root / "state.json")
        self._check_config()
        self.panel = read_jsonl(self.root / "inputs/validation.jsonl")
        self.support = read_jsonl(self.root / "inputs/support.jsonl")
        self.original = read_jsonl(self.root / "inputs/train.jsonl")
        for name, expected in self.state["input_digests"].items():
            if digest(read_jsonl(self.root / f"inputs/{name}.jsonl")) != expected:
                raise ValueError(f"Frozen input changed: {name}")
        self.exclusions = evidence_exclusions(self.panel, read_jsonl(self.root / "inputs/external.jsonl"))
        self.registry = PrincipleRegistry(self.state["principles"])
        self.controller = Controller(self.config["seed"])
        self.controller.load(self.root / self.state["controller_file"])

    def _check_config(self):
        expected = self.state.get("config_digest")
        if expected is None or digest(self.config) != expected or digest(load_json(self.root / "config.json")) != expected:
            raise ValueError("Frozen config changed or missing; start a new run for a different protocol")

    def _check_pending_artifacts(self, pending):
        directory = self.root / pending["directory"]
        if load_json(directory / "job.json") != pending["job"]:
            raise ValueError("Pending job manifest changed")
        for name, expected in pending["artifact_digests"].items():
            value = load_json(directory / name) if name.endswith(".json") else read_jsonl(directory / name)
            if digest(value) != expected:
                raise ValueError(f"Pending artifact changed: {name}")

    @staticmethod
    def initialize(root, config, support, validation, external, baseline, *, original=(), actor_path=None, checkpoint="base"):
        root = Path(root)
        if root.exists() and any(root.iterdir()):
            raise ValueError("Run directory must be empty")
        active = config.get("active_tasks", TASKS)
        if config.get("review_required") and config.get("recipe_confirmed") is not True:
            raise ValueError("Confirm the experiment recipe by setting recipe_confirmed=true")
        validate_partitions(support, validation, external, original, active_tasks=active,
                            require_identity=not config.get("fixture_mode", False))
        if config["horizon"] <= 0 or config["revision_every"] <= 0 or config["workers"] <= 0:
            raise ValueError("Invalid run horizon, revision interval, or worker count")
        if set(config["task_quotas"]) != set(active):
            raise ValueError("Freeze the quotas for every active task before initialization")
        if not config.get("fixture_mode", False) and actor_path is None:
            raise ValueError("Real runs require a behavior-cloned Actor; random initialization is demo-only")
        stats = summary(validation, baseline, min_cell_count=config.get("min_cell_count", 1))
        protocols = {r["id"]: r.get("metric_protocol") for r in baseline}
        if not all(isinstance(p, str) and p for p in protocols.values()):
            raise ValueError("Baseline must declare its frozen scoring protocol for every case")
        root.mkdir(parents=True, exist_ok=True)
        for name, rows in (("support", support), ("validation", validation), ("external", external), ("train", original)):
            write_jsonl(root / f"inputs/{name}.jsonl", rows)
        dump_json(root / "config.json", config)
        controller = Controller(config["seed"])
        if actor_path:
            controller.load_actor(actor_path, active_tasks=active)
        controller.save(root / "controller_initial.pt")
        dump_json(root / "state.json", {"next_round": 0, "checkpoint": checkpoint, "outcomes": baseline,
                  "summary": stats, "principles": {}, "window": [], "previous_quota": {}, "previous_action": "",
                  "previous_reward": 0.0, "controller_file": "controller_initial.pt", "validation_digest": digest(validation),
                  "external_digest": digest(external), "metric_protocols": protocols, "pending": None,
                  "config_digest": digest(config),
                  "input_digests": {name: digest(rows) for name, rows in (
                      ("support", support), ("validation", validation), ("external", external), ("train", original))}})

    def _features(self):
        return state_vector(self.state["summary"], episode=self.state["next_round"], horizon=self.config["horizon"],
                            previous_quota=self.state["previous_quota"], previous_action=self.state["previous_action"],
                            previous_reward=self.state["previous_reward"])

    def prepare(self):
        self._check_config()
        if self.state["pending"] is not None:
            raise ValueError("Complete the pending round before sampling another action")
        episode = self.state["next_round"]
        if episode >= self.config["horizon"]:
            raise ValueError("Configured horizon is complete")
        start = time.monotonic()
        usage_start = len(getattr(self.agents, "usage", []))
        directory = self.root / f"round_{episode:03d}"
        directory.mkdir(exist_ok=True)
        features = self._features(); decision = self.controller.sample(features, episode)
        selector = EvidenceSelector(self.support, self.agents)
        assignments = compile_assignments(self.state["summary"], selector, self.config["task_quotas"], decision.name,
                                          episode=episode, seed=self.config["seed"],
                                          min_cell_count=self.config.get("min_cell_count", 1),
                                          form_quotas=self.config.get("task_form_quotas"),
                                          plan_target=self.agents.plan)
        questions = [r["question"] for r in self.panel if r["task_form"] != "report_gen"]
        generated, rejected = generate_batch(assignments, self.registry, self.agents, questions,
                                             workers=self.config["workers"])
        write_jsonl(directory / "assignments.jsonl", assignments)
        write_jsonl(directory / "accepted.jsonl", generated)
        write_jsonl(directory / "rejected.jsonl", rejected)
        training = mix_training(generated, self.original, original_count=self.config.get("original_count", 0),
                                seed=self.config["seed"] + episode, target_size=self.config.get("training_size"))
        if not training:
            raise ValueError("No accepted supervision; learner update requires training data")
        if self.config.get("training_composition"):
            validate_training_composition(training, self.config["training_composition"])
        validate_exclusions(training, self.panel, self.exclusions)
        write_jsonl(directory / "training.jsonl", training)
        write_jsonl(directory / "training_qwen.jsonl", [to_qwen(r) for r in training])
        write_jsonl(directory / "validation.jsonl", self.panel)
        dump_json(directory / "exclusions.json", self.exclusions)
        job = {"schema": "coevomed_exchange_v2", "job_id": f"round_{episode:03d}", "round": episode,
               "checkpoint_in": self.state["checkpoint"], "validation_digest": self.state["validation_digest"],
               "training_digest": digest(training), "training": "training.jsonl", "validation": "validation.jsonl",
               "training_count": len(training), "learner": self.config["learner"],
               "exclusions": "exclusions.json", "exclusions_digest": digest(self.exclusions),
               "fixture_mode": self.config.get("fixture_mode", False),
               "counts": {"candidate": dict(Counter(a["benchmark"] for a in assignments)),
                          "accepted": dict(Counter(r["benchmark"] for r in generated)),
                          "training": dict(Counter(r["benchmark"] for r in training)),
                          "training_forms": dict(Counter(r["task_form"] for r in training)),
                          "original": self.config.get("original_count", 0), "generated": len(generated)},
               "note": "Return predictions for online scoring; weights stay on the training host."}
        if not job["fixture_mode"]:
            job["training_budget"] = training_budget(len(training), job["learner"])
        dump_json(directory / "job.json", job)
        pending = {"directory": directory.name, "features": features, "decision": asdict(decision),
                   "job": job, "generation_seconds": time.monotonic() - start,
                   "artifact_digests": {name: digest(rows) for name, rows in (
                       ("assignments.jsonl", assignments), ("accepted.jsonl", generated),
                       ("training.jsonl", training), ("validation.jsonl", self.panel), ("exclusions.json", self.exclusions))},
                   "generation_agent_calls": list(getattr(self.agents, "usage", []))[usage_start:]}
        self.state["pending"] = pending
        self.state["principles"] = self.registry.payload
        dump_json(self.root / "state.json", self.state)
        return directory

    def complete(self, result):
        self._check_config()
        usage_start = len(getattr(self.agents, "usage", []))
        pending = self.state["pending"]
        if pending is None:
            raise ValueError("No pending transition; completion is not repeatable")
        self._check_pending_artifacts(pending)
        job = pending["job"]
        for key in ("job_id", "validation_digest", "training_digest", "checkpoint_in"):
            if result.get(key) != job[key]:
                raise ValueError(f"Result does not match pending job: {key}")
        if not result.get("checkpoint_out") or result["checkpoint_out"] == job["checkpoint_in"]:
            raise ValueError("A new learner checkpoint is required")
        if result.get("fixture_mode", False) != self.config.get("fixture_mode", False):
            raise ValueError("Fixture results cannot be used as real model feedback")
        if not self.config.get("fixture_mode", False):
            validate_training_record(job, result.get("training_record"), result["checkpoint_out"])
        if {r["id"]: r.get("metric_protocol") for r in result["outcomes"]} != self.state["metric_protocols"]:
            raise ValueError("Scoring protocol changed after the frozen baseline")
        stats = summary(self.panel, result["outcomes"], self.state["outcomes"],
                        min_cell_count=self.config.get("min_cell_count", 1))
        episode = self.state["next_round"]; decision = Decision(**pending["decision"])
        next_features = state_vector(stats, episode=episode + 1, horizon=self.config["horizon"],
                                     previous_quota=self.config["task_quotas"], previous_action=decision.name,
                                     previous_reward=stats["reward"])
        ppo = self.controller.update(pending["features"], decision, stats["reward"], next_features,
                                     terminal=episode + 1 == self.config["horizon"])
        directory = self.root / pending["directory"]
        accepted = read_jsonl(directory / "accepted.jsonl")
        usage = usage_by_version(accepted)
        self.state["window"].append({"episode": episode, "usage": usage, "cells": stats["cells"]})
        revisions = []
        if (episode + 1) % self.config["revision_every"] == 0:
            revisions = self._revise(stats, episode, directory)
            self.state["window"] = []
        dump_json(directory / "result.json", result)
        dump_json(directory / "feedback.json", stats)
        dump_json(directory / "ppo.json", ppo)
        dump_json(directory / "principle_comparisons.json", revisions)
        dump_json(directory / "costs.json", {"generation_seconds": pending["generation_seconds"],
                  "learner_seconds": result.get("learner_seconds"), "response_tokens": result.get("response_tokens"),
                  "candidate_count": sum(self.config["task_quotas"].values()), "accepted_count": len(accepted),
                  "training_count": job["training_count"], "agent_calls": pending["generation_agent_calls"] +
                  list(getattr(self.agents, "usage", []))[usage_start:]})
        controller_file = f"{directory.name}/controller.pt"
        self.controller.save(self.root / controller_file)
        self.state.update({"next_round": episode + 1, "checkpoint": result["checkpoint_out"],
                           "outcomes": result["outcomes"], "summary": stats, "principles": self.registry.payload,
                           "previous_quota": self.config["task_quotas"], "previous_action": decision.name,
                           "previous_reward": stats["reward"], "controller_file": controller_file, "pending": None})
        dump_json(self.root / "state.json", self.state)
        return {"round": episode, "reward": stats["reward"], "ppo_update": ppo["update_index"],
                "action": decision.name, "principle_decisions": [r.get("status") for r in revisions]}

    def _revise(self, stats, episode, directory):
        min_cell_count = self.config.get("min_cell_count", 1)
        keys = eligible_principles(self.state["window"], min_usage=self.config.get("min_principle_usage", 100),
                                  min_cell_count=min_cell_count,
                                  active_versions={k: v["active"] for k, v in self.registry.payload.items()})
        limit = self.config.get("max_principle_candidates")
        if limit is not None:
            keys = keys[:limit]
        results = []; all_assignments = []
        for record in self.state["window"]:
            all_assignments.extend(read_jsonl(self.root / f"round_{record['episode']:03d}/assignments.jsonl"))
        questions = [r["question"] for r in self.panel if r["task_form"] != "report_gen"]
        for key in keys:
            active = self.registry.active(key)
            cells = [c for c in stats["cells"].values()
                     if c["principle_id"] == key and c["count"] >= min_cell_count]
            candidate = None
            try:
                strategy, reason, semantic = self.agents.revise(active, cells)
                texts = [s for lines in strategy.values() for s in lines]
                if any(near_validation_copy(text, questions) for text in texts):
                    raise ValueError("Revision contains validation question text")
                candidate = self.registry.candidate(key, strategy, reason)
                assignments = matched_assignments(all_assignments, key)
                cur, cur_rejected = generate_batch(assignments, self.registry, self.agents, questions,
                                                   workers=self.config["workers"], override=active)
                cand, cand_rejected = generate_batch(assignments, self.registry, self.agents, questions,
                                                     workers=self.config["workers"], override=candidate)
                if any(r.get("failure_type") == "api" for r in cur_rejected + cand_rejected):
                    raise AgentCallError("Paired comparison had API failures; quality comparison is inconclusive")
                left = {r["id"]: r for r in cur}; right = {r["id"]: r for r in cand}
                common = sorted(left.keys() & right.keys())
                sources = {a["id"]: a["source"]["facts"] for a in assignments}
                pairs = [{"assignment_id": i, "facts": sources[i], "current": left[i], "candidate": right[i]} for i in common[:30]]
                coverage = len(common) / max(len(assignments), 1)
                review = self.agents.review(active, candidate, semantic, pairs) if coverage >= 0.6 else {}
                outcome = probe_decision([a["id"] for a in assignments], left, right, review)
                self.registry.select(candidate, outcome, episode + 1)
                detail = {"principle_id": key, **outcome, "active": active, "candidate": candidate,
                          "semantic_feedback": semantic, "pairs_reviewed": pairs,
                          "current_rejections": cur_rejected, "candidate_rejections": cand_rejected,
                          "assignment_ids": [a["id"] for a in assignments]}
                results.append(detail)
            except (ValueError, KeyError, TypeError, AgentCallError) as error:
                outcome = {"principle_id": key, "status": "deferred", "reason": str(error)}
                if candidate is not None:
                    self.registry.select(candidate, outcome, episode + 1)
                results.append(outcome)
        return results
