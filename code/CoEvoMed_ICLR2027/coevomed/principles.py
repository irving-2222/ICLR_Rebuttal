from copy import deepcopy

from .data import digest

LOCKED = ("semantic_goal", "hard_constraints")
MUTABLE = ("question_strategy", "answer_strategy", "contrast_strategy", "diversity_strategy", "preferred_vocabulary")


def initial_principle(key):
    report = key.startswith(("mimic_cxr::", "iu_xray::"))
    return {"id": key, "version": 0, "parent": None, "strategy": {
        "semantic_goal": [f"Train {key} from grounded source facts"],
        "question_strategy": ["Request one study-level report from all views" if report else
                              "Ask a concise image-dependent question about a supported fact"],
        "answer_strategy": ["Preserve fact coverage, laterality, negation, severity, and uncertainty"],
        "contrast_strategy": ["Express supported distinctions without inventing a counterfactual finding"],
        "diversity_strategy": ["Vary question intent before making synonym-only paraphrases"],
        "preferred_vocabulary": [],
        "hard_constraints": ["Use only selected source facts", "Do not copy validation questions",
                             "Keep task, capability, modality, anatomy, and task form fixed"],
    }}


class PrincipleRegistry:
    def __init__(self, payload=None):
        self.payload = deepcopy(payload or {})

    def active(self, key):
        if key not in self.payload:
            self.payload[key] = {"active": 0, "versions": [initial_principle(key)]}
        entry = self.payload[key]
        return deepcopy(next(v for v in entry["versions"] if v["version"] == entry["active"]))

    def candidate(self, key, strategy, reason):
        active = self.active(key)
        if set(strategy) != set(LOCKED + MUTABLE):
            raise ValueError("Candidate must preserve the seven-field strategy schema")
        if any(strategy[k] != active["strategy"][k] for k in LOCKED):
            raise ValueError("Candidate changed the fixed capability or factual constraints")
        if any(not isinstance(strategy[k], list) or any(not isinstance(s, str) for s in strategy[k]) for k in strategy):
            raise ValueError("Strategy fields must be lists of strings")
        if not any(strategy[k] != active["strategy"][k] for k in MUTABLE[:-1]):
            raise ValueError("A vocabulary-only change is not a rewriting revision")
        if any(digest(v["strategy"]) == digest(strategy) for v in self.payload[key]["versions"]):
            raise ValueError("Previously tried strategy")
        candidate = {"id": key, "version": len(self.payload[key]["versions"]), "parent": active["version"],
                     "strategy": deepcopy(strategy), "reason": reason, "status": "candidate"}
        self.payload[key]["versions"].append(candidate)
        return deepcopy(candidate)

    def select(self, candidate, decision, next_round):
        key = candidate["id"]
        entry = self.payload[key]
        if entry["active"] != candidate["parent"]:
            raise ValueError("Candidate is based on a stale active version")
        record = entry["versions"][candidate["version"]]
        record["status"] = decision["status"]
        record["comparison"] = deepcopy(decision)
        record["effective_round"] = next_round if decision["status"] == "accepted" else None
        if decision["status"] == "accepted":
            entry["active"] = candidate["version"]


def probe_decision(requested_ids, current_ids, candidate_ids, review, *, target_count=100):
    requested, current, candidate = map(set, (requested_ids, current_ids, candidate_ids))
    if len(requested_ids) != len(requested) or not current <= requested or not candidate <= requested:
        raise ValueError("Probe assignment identities are invalid")
    n = len(requested)
    if not n:
        return {"status": "deferred", "reason": "no_assignments", "requested": 0}
    cur, cand, paired = len(current) / n, len(candidate) / n, len(current & candidate) / n
    result = {"requested": n, "current_yield": cur, "candidate_yield": cand,
              "delta_use": cand - cur, "paired_coverage": paired, "review": review}
    regression = review.get("alignment") == "worse" or review.get("evidence_preserved") is False
    if cand < cur - 0.05 - 1e-12 or (cand < 0.8 and cur >= 0.8) or regression:
        return {**result, "status": "rejected", "reason": "yield_or_semantic_regression"}
    if n != target_count or cand < 0.8 or paired < 0.6:
        return {**result, "status": "deferred", "reason": "insufficient_yield_or_coverage"}
    if not (review.get("applied") is True and review.get("alignment") == "improved"
            and review.get("evidence_preserved") is True and review.get("reason")):
        return {**result, "status": "deferred", "reason": "semantic_improvement_unconfirmed"}
    return {**result, "status": "accepted", "reason": "paired_semantic_improvement"}


def usage_by_version(rows):
    usage = {}
    for row in rows:
        key, version = row["principle_id"], row["principle_version"]
        item = usage.setdefault(key, {"version": version, "count": 0})
        if item["version"] != version:
            raise ValueError("One round cannot deploy multiple versions of the same principle")
        item["count"] += 1
    return usage


def matched_assignments(assignments, key, count=100):
    first, repeats, ids, evidence = [], [], set(), set()
    for assignment in assignments:
        if assignment["principle_id"] != key:
            continue
        if assignment["id"] in ids:
            raise ValueError("Duplicate probe assignment ID")
        ids.add(assignment["id"])
        identity = assignment["source"]["evidence_id"]
        (repeats if identity in evidence else first).append(assignment)
        evidence.add(identity)
    return (first + repeats)[:count]


def eligible_principles(window, *, min_usage=100, min_cell_count=1, active_versions=None):
    totals = {}
    for record in window:
        for key, usage in record["usage"].items():
            cells = [c for c in record["cells"].values()
                     if c["principle_id"] == key and c["count"] >= min_cell_count]
            if not cells:
                continue
            identity = (key, usage["version"])
            item = totals.setdefault(identity, {"usage": 0, "net_repair": 0, "persistent_gap": 0})
            item["usage"] += usage["count"]
            for cell in cells:
                item["net_repair"] += cell["net_repair"]
                item["persistent_gap"] += cell["persistent_gap"]
    eligible = {}
    for (key, version), values in totals.items():
        if active_versions is not None and active_versions.get(key) != version:
            continue
        if values["usage"] >= min_usage and values["net_repair"] <= 0:
            eligible[key] = eligible.get(key, 0) + values["persistent_gap"]
    return sorted(eligible, key=lambda key: (-eligible[key], key))
