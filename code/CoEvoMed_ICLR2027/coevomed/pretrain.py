from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import random

import torch
from torch.nn import functional as F

from .data import TASKS, digest, dump_json, write_jsonl
from .feedback import state_vector
from .policy import ACTIONS, ActorCritic


def build_states(baseline_summary, seed=42, horizon=10):
    rows = []
    active = [t for t in TASKS if t in baseline_summary["tasks"]]
    for group in range(20):
        for mode in ("balanced", "global_error", "concentrated_weakness", "regression_heavy"):
            for variant in range(10):
                rng = random.Random(int(digest([seed, group, mode, variant])[:16], 16))
                stats = deepcopy(baseline_summary)
                focused = set(rng.sample(active, min(2, max(1, len(active) // 2))))
                for task, item in stats["tasks"].items():
                    item["score"] = min(1, max(0, item["score"] + rng.uniform(-0.04, 0.04)))
                    item["delta"] = rng.uniform(-0.005, 0.015); item["regression"] = rng.uniform(0, 0.035)
                    item["gap"] = min(1, max(0, item["gap"] + rng.uniform(-0.08, 0.08)))
                    if mode == "global_error" or (mode == "concentrated_weakness" and task in focused):
                        item["score"] *= 0.5; item["gap"] = rng.uniform(0.65, 0.9)
                    if mode == "regression_heavy":
                        item["delta"] = rng.uniform(-0.08, -0.015); item["regression"] = rng.uniform(0.13, 0.38)
                episode = rng.randrange(horizon)
                features = state_vector(stats, episode=episode, horizon=horizon,
                                        previous_quota={t: rng.randrange(70, 130) for t in active},
                                        previous_action=rng.choice(ACTIONS), previous_reward=rng.uniform(-0.04, 0.04))
                rows.append({"id": f"state-{group:02d}-{mode}-{variant:02d}", "group": group,
                             "mode": mode, "features": features, "task_summary": stats["tasks"], "active_tasks": active})
    return rows


def teacher_label(rows, agents, workers=8):
    def label(row):
        result = agents.call("teacher", "Choose exactly one curriculum action for the supplied capability state: balanced, "
                             "repair_heavy, weakness_focus, retention_heavy. Consider residual gaps, progress and regressions. "
                             "Do not mistake low report NLG magnitude for high weakness; use the separate feedback gap.",
                             {"state": row, "output": {"action": "one action", "reason": "short justification"}})
        if result.get("action") not in ACTIONS or not result.get("reason"):
            raise ValueError("Invalid teacher label; no heuristic fallback")
        return {**row, **result}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(label, rows))


def train_actor(rows, output, seed=42, max_epochs=120, patience=20):
    from pathlib import Path
    profiles = {tuple(r.get("active_tasks", TASKS)) for r in rows}
    if len(profiles) != 1:
        raise ValueError("BC states cannot mix active task profiles")
    groups = sorted({r["group"] for r in rows})
    if len(rows) != 800 or len(groups) != 20 or any(n != 40 for n in Counter(r["group"] for r in rows).values()):
        raise ValueError("Expected 800 states in 20 disjoint groups of 40")
    if any(len(r["features"]) != 40 or r.get("action") not in ACTIONS for r in rows):
        raise ValueError("Invalid teacher data")
    ranked = sorted(groups, key=lambda g: (-len({r["action"] for r in rows if r["group"] == g}), digest([seed, g])))
    valid_groups = set(ranked[:4])
    train = [r for r in rows if r["group"] not in valid_groups]
    valid = [r for r in rows if r["group"] in valid_groups]
    for split in (train, valid):
        if {r["action"] for r in split} != set(ACTIONS):
            raise ValueError("Group split lacks at least one action")
    def tensors(items):
        return torch.tensor([r["features"] for r in items], dtype=torch.float32), torch.tensor([ACTIONS.index(r["action"]) for r in items])
    x, y = tensors(train); vx, vy = tensors(valid)
    if not torch.isfinite(x).all() or not torch.isfinite(vx).all():
        raise ValueError("Non-finite BC state")
    torch.manual_seed(seed); model = ActorCritic()
    optimizer = torch.optim.Adam([*model.shared.parameters(), *model.actor.parameters()], lr=1e-3)
    rng = torch.Generator().manual_seed(seed)
    best, best_epoch, stale, selected = -1, -1, 0, None
    history = []
    for epoch in range(max_epochs):
        for batch in torch.randperm(len(x), generator=rng).split(32):
            logits, _ = model(x[batch]); loss = F.cross_entropy(logits, y[batch], label_smoothing=0.05)
            optimizer.zero_grad(); loss.backward(); optimizer.step()
        with torch.no_grad():
            pred = model(vx)[0].argmax(-1)
            f1 = sum(float(2 * ((pred == a) & (vy == a)).sum()) /
                     max(int((pred == a).sum() + (vy == a).sum()), 1) for a in range(4)) / 4
        history.append({"epoch": epoch + 1, "validation_macro_f1": f1})
        if f1 > best + 1e-8:
            best, best_epoch, selected, stale = f1, epoch + 1, deepcopy(model.state_dict()), 0
        else:
            stale += 1
        if stale >= patience:
            break
    if selected is None:
        raise ValueError("No behavior-cloning optimization occurred")
    model.load_state_dict(selected)
    torch.nn.init.zeros_(model.critic.weight); torch.nn.init.zeros_(model.critic.bias)
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.state_dict(), "active_tasks": list(next(iter(profiles)))}, output / "actor.pt")
    metrics = {"train_count": len(train), "validation_count": len(valid), "best_epoch": best_epoch,
               "validation_macro_f1": best, "validation_groups": sorted(valid_groups), "history": history,
               "note": "Actor checkpoint selected by group-held-out validation macro-F1."}
    dump_json(output / "metrics.json", metrics)
    write_jsonl(output / "labeled_states.jsonl", rows)
    return metrics
