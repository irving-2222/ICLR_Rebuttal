from collections import defaultdict

from .data import REPORTS, TASKS, cell_key, principle_key, unit_score
from .policy import ACTIONS


def index_outcomes(panel, outcomes):
    if len({r["id"] for r in panel}) != len(panel):
        raise ValueError("Duplicate panel IDs")
    indexed = {}
    for row in outcomes:
        if row.get("role") != "validation" or row.get("error") or not str(row.get("prediction", "")).strip():
            raise ValueError("Feedback must be successful validation predictions, never external scores")
        if row["id"] in indexed:
            raise ValueError("Duplicate prediction ID")
        indexed[row["id"]] = row
    if set(indexed) != {r["id"] for r in panel}:
        raise ValueError("Feedback IDs differ from frozen validation panel")
    for row in panel:
        outcome = indexed[row["id"]]
        if outcome.get("benchmark") != row["benchmark"]:
            raise ValueError("Outcome benchmark mismatch")
        if row["benchmark"] in REPORTS:
            for name in ("rougeL", "bleu4", "meteor"):
                unit_score(outcome["metrics"][name])
        elif type(outcome.get("correct")) is not bool:
            raise ValueError("VQA correctness must be an explicit boolean")
    return indexed


def score(row):
    if row["benchmark"] not in REPORTS:
        return float(row["correct"])
    m = row["metrics"]
    return 0.5 * m["rougeL"] + 0.3 * m["bleu4"] + 0.2 * m["meteor"]


def learned(row):
    return row["metrics"]["rougeL"] >= 0.3 if row["benchmark"] in REPORTS else row["correct"]


def summary(panel, outcomes, previous=None, *, min_cell_count=1):
    now = index_outcomes(panel, outcomes)
    old = index_outcomes(panel, previous) if previous is not None else now
    by_task, by_cell = defaultdict(list), defaultdict(list)
    for row in panel:
        by_task[row["benchmark"]].append(row)
        by_cell[cell_key(row)].append(row)
    vqa_tasks = [t for t in TASKS[:4] if t in by_task]
    report_tasks = [t for t in TASKS[4:] if t in by_task]
    if not set(by_task) <= set(TASKS) or not vqa_tasks or not report_tasks:
        raise ValueError("Feedback needs known tasks in both VQA and report families")
    tasks = {}
    for task, rows in by_task.items():
        ids = [r["id"] for r in rows]; n = len(ids)
        tasks[task] = {
            "score": sum(score(now[i]) for i in ids) / n,
            "delta": sum(score(now[i]) - score(old[i]) for i in ids) / n,
            "gap": sum(not learned(now[i]) for i in ids) / n,
            "regression": sum(learned(old[i]) and not learned(now[i]) for i in ids) / n,
            "count": n,
        }
    cells = {}
    for key, rows in sorted(by_cell.items()):
        ids = [r["id"] for r in rows]; n = len(ids)
        repaired = sum(not learned(old[i]) and learned(now[i]) for i in ids)
        regressed = sum(learned(old[i]) and not learned(now[i]) for i in ids)
        cells[key] = {
            **{k: rows[0][k] for k in ("benchmark", "task_form", "visual_ability", "modality", "anatomy")},
            "principle_id": principle_key(rows[0]), "count": n, "supported": n >= min_cell_count,
            "mastery": sum(score(now[i]) for i in ids) / n,
            "gap": sum(not learned(now[i]) for i in ids),
            "learned": sum(learned(now[i]) for i in ids),
            "repaired": repaired, "regressed": regressed,
            "persistent_gap": sum(not learned(old[i]) and not learned(now[i]) for i in ids),
            "net_repair": repaired - regressed,
            "delta": sum(score(now[i]) - score(old[i]) for i in ids) / n,
            "residual_errors": [{"question": r["question"], "reference": r["answer"],
                                 "prediction": now[r["id"]]["prediction"]}
                                for r in rows if not learned(now[r["id"]])][:8],
        }
    reward = 0.5 * sum(tasks[t]["delta"] for t in vqa_tasks) / len(vqa_tasks)
    reward += 0.5 * sum(tasks[t]["delta"] for t in report_tasks) / len(report_tasks)
    return {"tasks": tasks, "cells": cells, "reward": reward}


def state_vector(stats, *, episode, horizon, previous_quota=None, previous_action="", previous_reward=0.0):
    quota = {t: n for t, n in (previous_quota or {}).items() if t in stats["tasks"]}
    total = max(sum(quota.values()), 1)
    values = []
    for task in TASKS:
        if task not in stats["tasks"]:
            values.extend([0.0] * 5)
            continue
        item = stats["tasks"][task]
        values.extend((item["score"], item["delta"], item["gap"], item["regression"], quota.get(task, 0) / total))
    vqa = [v["score"] for t, v in stats["tasks"].items() if t not in REPORTS]
    reports = [v["score"] for t, v in stats["tasks"].items() if t in REPORTS]
    values.extend((sum(vqa) / len(vqa), sum(reports) / len(reports),
                   min(v["delta"] for v in stats["tasks"].values()), min(episode / horizon, 1.0),
                   previous_reward, float(episode > 0)))
    values.extend(float(previous_action == a) for a in ACTIONS)
    assert len(values) == 40
    return values
