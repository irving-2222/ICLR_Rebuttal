"""Compact 3D summary: supplied scores first, published scores for missing cells only."""
from pathlib import Path
import json
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

# Preserve the published canvas and plot scale across font changes.
PAPER_BBOX = Bbox.from_bounds(0.23147743055555553, 0.1843020833333333, 9.063745486111111, 2.2158003472222223)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "3D_result/3d_other_model.json.txt"
supplied = json.loads((ROOT / SOURCE).read_text())["models"]
categories = ["Plane", "Phase", "Organ", "Abnormality", "Location"]
tasks = ["Anomaly Detection", "Image Observation", "Medical Computation"]

# Verified against the local Hulu-Med PDF, Figure 3(a-c), printed page 21.
# These fill missing benchmark entries; they never supersede supplied evaluations.
published = {
    "M3D-VQA": {
        "RadFM": [19.6, 28.7, 16.8, 18.9, 14.9],
        "Qwen2.5VL-72B": [94.8, 50.0, 62.4, 62.5, 59.8],
        "Lingshu-32B": [93.8, 61.6, 60.9, 61.5, 57.6],
        "M3D-Llama2-7B": [98.8, 79.8, 74.8, 66.7, 58.9],
        "Hulu-Med-7B": [99.0, 88.0, 78.9, 70.7, 67.3],
    },
    "3D-RAD": {
        "Qwen2.5VL-72B": [25.2, 27.3, 11.6],
        "M3D (Phi3-4B)": [23.2, 23.2, 5.6],
        "Lingshu-7B": [21.6, 22.2, 8.4],
        "M3D-Llama2-7B": [20.8, 18.6, 23.2],
        "Lingshu-32B": [16.1, 16.3, 4.8],
        "Hulu-Med-7B": [35.9, 37.1, 26.0],
    },
    "AMOS-MM": {
        "Hulu-Med-7B": [67.4],
        "M3D-LaMed-4B": [57.1],  # M3D-Phi-3; superseded by supplied Phi-3 evaluation.
        "M3D-Llama3.1-8B": [57.0],
        "M3D-Mistralv0.3-7B": [56.9],
        "Qwen2.5VL-32B": [52.9],
        "Lingshu-7B": [52.0],
        "Lingshu-32B": [49.2],
    },
}
aliases = {
    "Med3DVLM-Qwen-2.5-7B": "Med3DVLM-7B",
    "M3D-LaMed-Phi-3-4B": "M3D-LaMed-4B",
}
panels = []
for benchmark, metric in [("M3D-VQA", "Macro accuracy (%)"),
                          ("3D-RAD", "Macro ROUGE-1"),
                          ("AMOS-MM", "RaTEScore")]:
    rows = {}
    for model, scores in published[benchmark].items():
        rows[model] = dict(model=model, components=scores, score=mean(scores),
                           source="Hulu-Med, Figure 3(a-c), PDF page 21",
                           provenance="published; fills missing supplied benchmark")
    for model, benchmarks in supplied.items():
        if "released" in model or model in {"Hulu-Med-14B", "Hulu-Med-32B"}:
            continue
        if benchmark not in benchmarks:
            continue
        values = benchmarks[benchmark]
        if benchmark == "M3D-VQA":
            scores = [values[f"{c} Accuracy (%)"] for c in categories]
        elif benchmark == "3D-RAD":
            scores = [values[t]["ROUGE-1"] for t in tasks]
        else:
            scores = [values["RaTEScore"]]
        name = aliases.get(model, model)
        if model.startswith("Photon-3B ("):
            name = "Photon-3B-S1" if benchmark == "M3D-VQA" else "Photon-3B-S2"
        rows[name] = dict(model=name, source_model=model, components=scores,
                          score=mean(scores), source=SOURCE, provenance="supplied")
    if benchmark == "M3D-VQA":
        ours_path = "3D_result/m3d-vqa-closed.json"
        raw = json.loads((ROOT / ours_path).read_text())
        ours = [100 * raw["by_category"][c]["closed"]["accuracy"] for c in categories]
        assert abs(mean(ours) - 100 * raw["category_macro"]["closed_accuracy"]) < 1e-9
    elif benchmark == "3D-RAD":
        ours_path = "3D_result/3d-rad.json"
        raw = json.loads((ROOT / ours_path).read_text())
        ours = [100 * raw["benchmark_official"]["by_task"][t]["rouge1"] for t in tasks]
    else:
        ours_path = "3D_result/amoss-mm.json"
        raw = json.loads((ROOT / ours_path).read_text())
        ours = [100 * raw["rate"]]
    # Existing comparison pool, all available eligible baselines, top four by this metric.
    ranked = sorted(rows.values(), key=lambda r: (-r["score"], r["model"]))
    displayed = ranked[:4] + [dict(model="CoEvoMed", components=ours,
                                   score=mean(ours), source=ours_path, provenance="supplied")]
    displayed.sort(key=lambda r: -r["score"])
    panels.append(dict(benchmark=benchmark, metric=metric, rows=displayed,
                       all_eligible_baselines=ranked))

assert next(r for r in panels[2]["rows"] if r["model"] == "Hulu-Med-7B")["score"] == 64.35
assert next(r for r in panels[2]["all_eligible_baselines"] if r["model"] == "M3D-LaMed-4B")["score"] == 39.0
assert all(p["rows"] == sorted(p["rows"], key=lambda r: -r["score"]) for p in panels)
assert all("released" not in r["model"] for p in panels for r in p["rows"])
manifest = {
    "precedence": "Current user-supplied evaluation > published missing benchmark. No imputation.",
    "selection": "CoEvoMed and the four highest-scoring eligible baselines per benchmark after supplementing missing evaluations from Hulu-Med Figure 3(a-c).",
    "excluded": "Hulu-Med-14B/32B remain excluded per the author's prior comparison scope. Photon released predictions do not replace local-input evaluations.",
    "model_aliases": {"M3D-Phi-3 (Hulu-Med)": "M3D-LaMed-Phi-3-4B (supplied); supplied result takes precedence"},
    "aggregation": "M3D: unweighted mean of five category accuracies; RAD: unweighted mean of three task ROUGE-1 scores; AMOS: RaTEScore. All scaled to 100.",
    "published_reference": "Hulu-Med, local hulumed.pdf; bibliography key jiang2025hulumed",
    "published_page": 21,
    "missing": "Unavailable combinations remain unreported. Photon AMOS-MM is absent from Hulu-Med. No cross-checkpoint substitutions.",
    "panels": panels,
}
(ROOT / "figures/three_d_main_results.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

plt.rcParams.update({"font.family": "Times New Roman", "font.size": 10,
                     "pdf.fonttype": 42, "svg.fonttype": "none"})
fig = plt.figure(figsize=(9.3, 2.45), facecolor="white")
pink, blue = "#E8A4B8", "#8AB0D8"
for i, panel in enumerate(panels):
    ax = fig.add_axes([.158 + i * .333, .26, .164, .55])
    rows = panel["rows"]
    lo = int(min(r["score"] for r in rows) // 5) * 5
    hi = (int(max(r["score"] for r in rows) // 5) + 2) * 5
    for y, row in enumerate(rows):
        is_ours = row["model"] == "CoEvoMed"
        if is_ours:
            ax.axhspan(y - .39, y + .39, color=pink, alpha=.14, linewidth=0, zorder=0)
        ax.scatter(row["score"], y, s=48 if is_ours else 35,
                   color=pink if is_ours else blue, zorder=3, edgecolor="white", linewidth=.6)
        ax.annotate(f'{row["score"]:.2f}', (row["score"], y), xytext=(5, 0),
                    textcoords="offset points", va="center", fontsize=9.3,
                    weight="bold" if is_ours else "normal", color="#253342")
    ax.set_yticks(range(len(rows)), [r["model"] for r in rows], fontsize=9.3)
    for tick, row in zip(ax.get_yticklabels(), rows):
        if row["model"] == "CoEvoMed":
            tick.set_weight("bold")
    ax.set_ylim(4.6, -.6)
    ax.set_xlim(lo - 1.5, hi)
    ax.set_xticks(list(range(lo, hi + 1, 10 if hi - lo > 25 else 5)))
    ax.tick_params(axis="y", length=0, pad=4)
    ax.tick_params(axis="x", length=2, labelsize=8.7, color="#ADB5BE")
    ax.set_xlabel(panel["metric"], fontsize=9.3, labelpad=4)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#E9EDF2", linewidth=.65)
    ax.spines[["top", "left", "right"]].set_visible(False)
    ax.spines["bottom"].set_color("#ADB5BE")
    fig.text(.168 + i * .333, .905, f'({"abc"[i]}) {panel["benchmark"]}',
             ha="center", fontsize=11, weight="bold")
# Enlarge all main-figure text at the published paper scale.
for text in fig.findobj(match=matplotlib.text.Text):
    text.set_fontsize(text.get_fontsize() * 1.265)
for ext in ["pdf", "png", "svg"]:
    fig.savefig(ROOT / f"figures/three_d_main.{ext}", dpi=250, bbox_inches=PAPER_BBOX, pad_inches=.03)
plt.close(fig)
for panel in panels:
    print(panel["benchmark"], [(r["model"], round(r["score"], 2)) for r in panel["rows"]])
