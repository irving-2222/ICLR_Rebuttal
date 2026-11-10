"""Paired bootstrap confidence interval for the score difference between two models.

Both models must be scored on the same test items. Each input file holds one row per
item with an item id and a per-item score: 1/0 correctness for VQA, or a per-report
metric such as RaTEScore for report generation.

Accepted formats: .jsonl (one JSON object per line) or .csv (with a header row).

Example:
    python paired_bootstrap.py --a coevomed_slake.jsonl --b qwen3vl8b_slake.jsonl \
        --id-field id --score-field correct --n-boot 10000 --seed 0
"""
import argparse
import csv
import json
import random
import sys


def load(path, id_field, score_field):
    rows = {}
    if path.endswith(".jsonl"):
        with open(path, encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
    elif path.endswith(".csv"):
        with open(path, encoding="utf-8", newline="") as f:
            records = list(csv.DictReader(f))
    else:
        sys.exit(f"Unsupported file type: {path} (use .jsonl or .csv)")
    for r in records:
        key = str(r[id_field])
        if key in rows:
            sys.exit(f"Duplicate item id {key} in {path}")
        rows[key] = float(r[score_field])
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", required=True, help="per-item scores of model A (e.g., CoEvoMed)")
    ap.add_argument("--b", required=True, help="per-item scores of model B (e.g., the base model)")
    ap.add_argument("--id-field", default="id")
    ap.add_argument("--score-field", default="correct")
    ap.add_argument("--n-boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--scale", type=float, default=100.0, help="multiply scores, e.g. 100 for percent")
    args = ap.parse_args()

    a = load(args.a, args.id_field, args.score_field)
    b = load(args.b, args.id_field, args.score_field)
    if set(a) != set(b):
        only_a, only_b = len(set(a) - set(b)), len(set(b) - set(a))
        sys.exit(f"Item ids differ: {only_a} only in A, {only_b} only in B. Both models must use the same test items.")

    ids = sorted(a)
    diffs = [(a[i] - b[i]) * args.scale for i in ids]
    n = len(diffs)
    observed = sum(diffs) / n

    rng = random.Random(args.seed)
    boots = []
    for _ in range(args.n_boot):
        s = 0.0
        for _ in range(n):
            s += diffs[rng.randrange(n)]
        boots.append(s / n)
    boots.sort()
    lo = boots[int(0.025 * args.n_boot)]
    hi = boots[int(0.975 * args.n_boot) - 1]
    p_le_zero = sum(1 for x in boots if x <= 0) / args.n_boot

    print(f"items: {n}")
    print(f"mean A: {sum(a[i] for i in ids) / n * args.scale:.2f}   mean B: {sum(b[i] for i in ids) / n * args.scale:.2f}")
    print(f"difference A - B: {observed:+.2f}")
    print(f"paired bootstrap 95% CI: [{lo:+.2f}, {hi:+.2f}]   ({args.n_boot} resamples, seed {args.seed})")
    print(f"share of resamples with difference <= 0: {p_le_zero:.4f}")


if __name__ == "__main__":
    main()
