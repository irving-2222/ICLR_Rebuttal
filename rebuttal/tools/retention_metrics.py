"""Forgetting and retention metrics from a finished CoEvoMed run (reply to pUjh W3).

Reads only the files the runner already writes, so no training is needed:
  <run>/round_XXX/feedback.json     per-cell counts on the fixed validation panel
  <run>/round_XXX/assignments.jsonl lane ("repair" / "retention") of each assignment
  <run>/round_XXX/result.json       per-case outcomes (optional, for recovery)
round_000 is R1. "Learned" follows coevomed/feedback.py: a correct VQA answer, or a
report with ROUGE-L >= 0.3.

Metrics (all on the internal validation panel, never on external benchmarks):
  1. Per round: share of previously learned cases lost (forgetting rate) and share of
     previously unlearned cases fixed (repair rate), overall and per task family.
  2. Average forgetting (Chaudhry et al., 2018) over capability cells at each round:
     mean over cells of (best earlier mastery - current mastery), count-weighted.
  3. Recovery: of cases lost in round e, the share learned again after round e+1.
  4. Retention link: forgetting rate in cells that received retention supervision
     in that round versus cells that received none.

Usage: python retention_metrics.py <run_dir> [--min-cell N] [--json out.json]
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

REPORTS = {"mimic_cxr", "iu_xray"}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def is_report(benchmark):
    return benchmark.lower().replace("-", "_") in REPORTS


def learned(row):
    if is_report(row["benchmark"]):
        return row["metrics"]["rougeL"] >= 0.3
    return bool(row["correct"])


def rounds(run):
    dirs = sorted(p for p in Path(run).glob("round_*") if (p / "feedback.json").exists())
    if not dirs:
        raise SystemExit(f"No round_*/feedback.json under {run}")
    return dirs


def per_round(dirs, min_cell):
    rows = []
    for k, d in enumerate(dirs, start=1):
        cells = load_json(d / "feedback.json")["cells"]
        agg = defaultdict(lambda: [0, 0, 0, 0])  # learned_before, lost, unlearned_before, fixed
        for c in cells.values():
            if c["count"] < min_cell:
                continue
            before = c["learned"] - c["repaired"] + c["regressed"]
            for fam in ("all", "report" if is_report(c["benchmark"]) else "vqa"):
                a = agg[fam]
                a[0] += before; a[1] += c["regressed"]
                a[2] += c["count"] - before; a[3] += c["repaired"]
        lanes = defaultdict(int)
        if (d / "assignments.jsonl").exists():
            for a in read_jsonl(d / "assignments.jsonl"):
                lanes[a["lane"]] += 1
        total = sum(lanes.values())
        row = {"round": f"R{k}", "retention_share": lanes["retention"] / total if total else None}
        for fam, (lb, lost, ub, fixed) in agg.items():
            row[fam] = {"forgetting_rate": lost / lb if lb else 0.0, "repair_rate": fixed / ub if ub else 0.0,
                        "lost": lost, "fixed": fixed, "net_repair": fixed - lost}
        rows.append(row)
    return rows


def average_forgetting(dirs, min_cell):
    history = defaultdict(list)  # cell -> [(count, mastery)] by round
    out = []
    for k, d in enumerate(dirs, start=1):
        cells = load_json(d / "feedback.json")["cells"]
        num = den = 0.0
        fam = defaultdict(lambda: [0.0, 0.0])
        for key, c in cells.items():
            if c["count"] < min_cell:
                continue
            past = history[key]
            if past:
                f = max(m for _, m in past) - c["mastery"]
                num += c["count"] * f; den += c["count"]
                g = fam["report" if is_report(c["benchmark"]) else "vqa"]
                g[0] += c["count"] * f; g[1] += c["count"]
            past.append((c["count"], c["mastery"]))
        if den:
            out.append({"round": f"R{k}", "all": 100 * num / den,
                        **{f: 100 * a / b for f, (a, b) in fam.items() if b}})
    return out


def recovery(dirs):
    outcomes = []
    for d in dirs:
        if not (d / "result.json").exists():
            return None
        outcomes.append({r["id"]: learned(r) for r in load_json(d / "result.json")["outcomes"]})
    out = []
    for e in range(1, len(outcomes) - 1):
        lost = [i for i, ok in outcomes[e].items() if not ok and outcomes[e - 1].get(i)]
        if lost:
            back = sum(outcomes[e + 1].get(i, False) for i in lost)
            out.append({"lost_in": f"R{e + 1}", "lost": len(lost), "relearned_next": back,
                        "recovery_rate": back / len(lost)})
    return out


def retention_link(dirs, min_cell):
    groups = {"with_retention": [0, 0], "without_retention": [0, 0]}  # lost, learned_before
    for d in dirs:
        if not (d / "assignments.jsonl").exists():
            return None
        got = defaultdict(int)
        for a in read_jsonl(d / "assignments.jsonl"):
            if a["lane"] == "retention":
                got[a["cell"]] += 1
        for key, c in load_json(d / "feedback.json")["cells"].items():
            before = c["learned"] - c["repaired"] + c["regressed"]
            if c["count"] < min_cell or before == 0:
                continue
            g = groups["with_retention" if got[key] else "without_retention"]
            g[0] += c["regressed"]; g[1] += before
    return {k: {"lost": a, "learned_before": b, "forgetting_rate": a / b if b else None} for k, (a, b) in groups.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--min-cell", type=int, default=1, help="skip cells with fewer validation cases")
    ap.add_argument("--json", help="also write all results to this file")
    args = ap.parse_args()
    dirs = rounds(args.run)
    res = {"per_round": per_round(dirs, args.min_cell), "average_forgetting": average_forgetting(dirs, args.min_cell),
           "recovery": recovery(dirs), "retention_link": retention_link(dirs, args.min_cell)}

    print("1. Per round (validation panel): forgetting rate = lost / learned before; repair rate = fixed / unlearned before")
    print(f"{'round':6s} {'ret.share':>9s} {'forget%':>8s} {'repair%':>8s} {'net':>6s}   {'VQA f%':>7s} {'rep f%':>7s}")
    for r in res["per_round"]:
        a = r["all"]; share = r["retention_share"]
        print(f"{r['round']:6s} {('%.2f' % share) if share is not None else '-':>9s} {100 * a['forgetting_rate']:8.2f} "
              f"{100 * a['repair_rate']:8.2f} {a['net_repair']:6d}   "
              f"{100 * r.get('vqa', {}).get('forgetting_rate', 0):7.2f} {100 * r.get('report', {}).get('forgetting_rate', 0):7.2f}")
    print("\n2. Average forgetting over cells (Chaudhry et al., 2018), points x100, count-weighted")
    for r in res["average_forgetting"]:
        print(f"{r['round']:6s} all {r['all']:6.2f}   " + "  ".join(f"{k} {v:6.2f}" for k, v in r.items() if k not in ("round", "all")))
    print("\n3. Recovery: cases lost in a round that are learned again after the next round")
    if res["recovery"] is None:
        print("   (skipped: result.json missing in some round)")
    else:
        for r in res["recovery"]:
            print(f"   lost in {r['lost_in']}: {r['lost']} cases, relearned {r['relearned_next']} ({100 * r['recovery_rate']:.1f}%)")
    print("\n4. Forgetting rate in cells with vs. without retention supervision in the same round (all rounds pooled)")
    if res["retention_link"] is None:
        print("   (skipped: assignments.jsonl missing in some round)")
    else:
        for k, v in res["retention_link"].items():
            rate = "-" if v["forgetting_rate"] is None else f"{100 * v['forgetting_rate']:.2f}%"
            print(f"   {k:18s} lost {v['lost']} of {v['learned_before']} learned cases ({rate})")
    if args.json:
        Path(args.json).write_text(json.dumps(res, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
