from collections import Counter, defaultdict
from copy import deepcopy
import math
import random

from .data import AXES, REPORTS, TASKS, cell_key, digest, principle_key
from .policy import ACTIONS, REPAIR


def largest_remainder(total, weights):
    if total < 0 or not weights or any(not math.isfinite(w) or w < 0 for w in weights):
        raise ValueError("Invalid allocation weights")
    if sum(weights) <= 0:
        weights = [1.0] * len(weights)
    raw = [total * w / sum(weights) for w in weights]
    counts = [math.floor(x) for x in raw]
    order = sorted(range(len(raw)), key=lambda i: (-(raw[i] - counts[i]), i))
    for i in order[:total - sum(counts)]:
        counts[i] += 1
    return counts


class EvidenceSelector:
    def __init__(self, support, agents):
        self.agents = agents
        self.index = defaultdict(list)
        for record in support:
            for form in record.get("supported_task_forms", [record["task_form"]]):
                key_row = {**record, "task_form": form}
                self.index[cell_key(key_row)].append(record)

    def select(self, key, n, seed, *, target, lane, intent):
        if n <= 0:
            raise ValueError("Evidence selection requires a positive quota")
        pool = sorted(self.index.get(key, []), key=lambda r: r["id"])
        if not pool:
            raise ValueError(f"No compatible factual evidence for {key}; no cross-domain fallback")
        rng = random.Random(seed); rng.shuffle(pool)
        by_id = {r["id"]: r for r in pool}
        if len(by_id) != len(pool):
            raise ValueError("Evidence candidate source IDs must be unique")
        count = min(n, len(pool))
        selected = self.agents.select_evidence(deepcopy(pool), target=deepcopy(target), lane=lane,
                                              intent=intent, count=count)
        if (not isinstance(selected, list) or len(selected) != count or
                any(not isinstance(i, str) or i not in by_id for i in selected) or len(set(selected)) != count):
            raise ValueError("Evidence selector must return the requested distinct IDs from the compatible pool")
        # Reuse selected evidence only when the fixed quota exceeds the compatible pool.
        return [deepcopy(by_id[selected[i % count]]) for i in range(n)]


def compile_assignments(stats, selector, quotas, action, *, episode, seed=42, min_cell_count=1, form_quotas=None,
                        plan_target=None):
    if action not in ACTIONS or not quotas or not set(quotas) <= set(TASKS):
        raise ValueError("A known action and fixed quotas for active tasks are required")
    if any(type(v) is not int or v <= 0 for v in quotas.values()):
        raise ValueError("Task quotas must be positive integers")
    result = []
    for task in TASKS:
        if task not in quotas:
            continue
        cells = [(k, v) for k, v in sorted(stats["cells"].items()) if v["benchmark"] == task
                 and v["count"] >= min_cell_count and selector.index.get(k)]
        if not cells:
            raise ValueError(f"No supported capability cells for {task}")
        locked_forms = (form_quotas or {}).get(task)
        if locked_forms is not None and (sum(locked_forms.values()) != quotas[task] or
                                        any(type(v) is not int or v < 0 for v in locked_forms.values())):
            raise ValueError("Task-form quotas must partition the fixed task quota")
        groups = [(cells, quotas[task])] if locked_forms is None else [
            ([(k, v) for k, v in cells if v["task_form"] == form], count)
            for form, count in sorted(locked_forms.items()) if count]
        for candidates, total in groups:
            if not candidates:
                raise ValueError(f"No evidence for a required task form in {task}")
            repair, retain = largest_remainder(total, [REPAIR[action], 1 - REPAIR[action]])
            for lane, n in (("repair", repair), ("retention", retain)):
                weights = [(v["gap"] + 2 * v["regressed"]) if lane == "repair" else v["learned"] for _, v in candidates]
                if action == "weakness_focus" and lane == "repair":
                    top = sorted(range(len(candidates)), key=lambda i: (-weights[i], candidates[i][0]))[:2]
                    weights = [w if i in top else 0 for i, w in enumerate(weights)]
                for (key, cell), count in zip(candidates, largest_remainder(n, weights)):
                    if not count:
                        continue
                    local_seed = int(digest([seed, episode, key, lane])[:12], 16)
                    target = {k: cell[k] for k in AXES}
                    intent = plan_target(cell, lane) if plan_target is not None else ""
                    for source in selector.select(key, count, local_seed, target=target, lane=lane, intent=intent):
                        result.append({"id": f"r{episode:03d}-a{len(result):06d}", "cell": key,
                                       "benchmark": task, "lane": lane, "source": source,
                                       "principle_id": principle_key(cell),
                                       "target": dict(target), "intent": intent})
    assert Counter(a["benchmark"] for a in result) == Counter(quotas)
    return result


def mix_training(generated, original, *, original_count=0, seed=42, target_size=None):
    if original_count < 0 or original_count > len(original):
        raise ValueError("Insufficient permitted original training data; no implicit repetition")
    rng = random.Random(seed)
    extra = rng.sample(list(original), original_count)
    rows = [deepcopy(r) for r in generated] + [deepcopy(r) for r in extra]
    if any(r["role"] != "train" for r in rows):
        raise ValueError("Validation and external records cannot enter training")
    if target_size is not None and len(rows) != target_size:
        raise ValueError(f"Training shortfall: accepted/mixed={len(rows)}, requested={target_size}")
    rng.shuffle(rows)
    return rows


def validate_training_composition(rows, constraints):
    families = Counter("report" if r["benchmark"] in REPORTS else "vqa" for r in rows)
    forms = Counter(r["task_form"] for r in rows if r["benchmark"] not in REPORTS)
    if families != Counter(constraints["family_counts"]):
        raise ValueError("Realized training family counts differ from the frozen recipe")
    if forms != Counter(constraints["vqa_form_counts"]):
        raise ValueError("Realized VQA form counts differ from the frozen recipe")
