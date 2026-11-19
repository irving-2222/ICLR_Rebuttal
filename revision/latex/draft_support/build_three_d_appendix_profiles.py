"""Appendix-only profiles; supplied evaluations override published cells."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Patch, Rectangle
from matplotlib.transforms import Bbox

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "3D_result/3d_other_model.json.txt"
PUBLISHED = "Hulu-Med Figure 3(a-c), author-supplied screenshot"
CATEGORIES = ["Plane", "Phase", "Organ", "Abnormality", "Location"]
TASKS = ["Anomaly Detection", "Image Observation", "Medical Computation"]
METRICS = ["RaTEScore", "BLEU-1", "ROUGE-L", "METEOR"]
pool = {b: {} for b in ["M3D-VQA", "3D-RAD", "AMOS-MM"]}

def put(benchmark, model, values, source):
    row = pool[benchmark].setdefault(model, {})
    for metric, value in values.items():
        if value is not None:
            row[metric] = {"value": value, "source": source}

# Transcribed from the supplied Hulu-Med figure. On 2026-09-19 the user
# reported confirmation from its author that the AMOS-MM BLEU column is BLEU-1.
for model, values in {
    "Hulu-Med-7B": [99.0, 88.0, 78.9, 70.7, 67.3],
    "M3D-Llama2-7B": [98.8, 79.8, 74.8, 66.7, 58.9],
    "Lingshu-32B": [93.8, 61.6, 60.9, 61.5, 57.6],
    "Qwen2.5VL-72B": [94.8, 50.0, 62.4, 62.5, 59.8],
    "RadFM": [19.6, 28.7, 16.8, 18.9, 14.9],
}.items():
    put("M3D-VQA", model, dict(zip(CATEGORIES, values)), PUBLISHED)
for model, values in {
    "Hulu-Med-7B": [[23.4, 35.9], [23.0, 37.1], [23.5, 26.0]],
    "Qwen2.5VL-72B": [[15.5, 25.2], [16.9, 27.3], [6.7, 11.6]],
    "M3D-LaMed-4B": [[16.3, 23.2], [15.1, 23.2], [2.5, 5.6]],
    "Lingshu-7B": [[9.3, 21.6], [10.4, 22.2], [0.9, 8.4]],
    "M3D-Llama2-7B": [[10.7, 20.8], [9.1, 18.6], [15.9, 23.2]],
    "Lingshu-32B": [[7.6, 16.1], [7.8, 16.3], [0.9, 4.8]],
}.items():
    put("3D-RAD", model, {f"{t}/{m}": v for t, pair in zip(TASKS, values)
                           for m, v in zip(["BLEU-1", "ROUGE-1"], pair)}, PUBLISHED)
for model, values in {
    "Hulu-Med-7B": [67.4, 39.9, 43.0, 32.6],
    "M3D-LaMed-4B": [57.1, 27.6, 39.4, 36.0],
    "M3D-Llama3.1-8B": [57.0, 26.4, 37.9, 35.5],
    "M3D-Mistralv0.3-7B": [56.9, 25.8, 37.4, 34.6],
    "Qwen2.5VL-32B": [52.9, 24.6, 19.1, 21.1],
    "Lingshu-7B": [52.0, 24.2, 20.0, 17.7],
    "Lingshu-32B": [49.2, 26.0, 18.3, 17.9],
}.items():
    put("AMOS-MM", model, dict(zip(METRICS, values)), PUBLISHED)

aliases = {"Med3DVLM-Qwen-2.5-7B": "Med3DVLM-7B",
           "M3D-LaMed-Phi-3-4B": "M3D-LaMed-4B"}
supplied = json.loads((ROOT / SOURCE).read_text())["models"]
for original, benchmarks in supplied.items():
    if "released" in original or original in {"Hulu-Med-14B", "Hulu-Med-32B"}:
        continue
    for benchmark, scores in benchmarks.items():
        name = aliases.get(original, original)
        if original.startswith("Photon-3B ("):
            name = "Photon-3B-S1" if benchmark == "M3D-VQA" else "Photon-3B-S2 (local)"
        if benchmark == "M3D-VQA":
            values = {c: scores[f"{c} Accuracy (%)"] for c in CATEGORIES
                      if f"{c} Accuracy (%)" in scores}
        elif benchmark == "3D-RAD":
            values = {f"{t}/{m}": scores[t][m] for t in TASKS if t in scores
                      for m in ["BLEU-1", "ROUGE-1"] if m in scores[t]}
        else:
            values = {m: scores[m] for m in METRICS if m in scores}
        put(benchmark, name, values, SOURCE)

path = "3D_result/m3d-vqa-closed.json"
raw = json.loads((ROOT / path).read_text())
put("M3D-VQA", "CoEvoMed", {c: 100 * raw["by_category"][c]["closed"]["accuracy"] for c in CATEGORIES}, path)
path = "3D_result/3d-rad.json"
raw = json.loads((ROOT / path).read_text())["benchmark_official"]["by_task"]
put("3D-RAD", "CoEvoMed", {f"{t}/{m}": 100 * raw[t][k] for t in TASKS
                           for m, k in [("BLEU-1", "bleu1"), ("ROUGE-1", "rouge1")]}, path)
path = "3D_result/amoss-mm.json"
raw = json.loads((ROOT / path).read_text())
put("AMOS-MM", "CoEvoMed", {m: 100 * raw[k] for m, k in zip(METRICS, ["rate", "bleu1", "rougeL", "meteor"])}, path)

rank_keys = {"M3D-VQA": CATEGORIES, "3D-RAD": [f"{t}/ROUGE-1" for t in TASKS], "AMOS-MM": ["RaTEScore"]}
limits = {"M3D-VQA": 5, "3D-RAD": 4, "AMOS-MM": 7}
selected = {}
for benchmark, rows in pool.items():
    keys = rank_keys[benchmark]
    rank = sorted([n for n, row in rows.items() if n != "CoEvoMed" and all(k in row for k in keys)],
                  key=lambda n: -np.mean([rows[n][k]["value"] for k in keys]))
    selected[benchmark] = ["CoEvoMed"] + rank[:limits[benchmark]]

assert pool["AMOS-MM"]["Hulu-Med-7B"]["RaTEScore"]["value"] == 64.35
assert pool["AMOS-MM"]["Qwen3.5-9B"]["RaTEScore"]["value"] == 53.68
assert pool["AMOS-MM"]["M3D-Llama3.1-8B"]["BLEU-1"]["value"] == 26.4
assert pool["AMOS-MM"]["Hulu-Med-7B"]["BLEU-1"]["value"] == 35.84
assert all(m in pool["AMOS-MM"][n] for n in selected["AMOS-MM"] for m in METRICS)
assert all("released" not in n for names in selected.values() for n in names)
manifest = {"precedence": "Supplied cell > published fallback; no checkpoint substitution.",
            "bleu_confirmation": "2026-09-19: user reports the Hulu-Med author confirmed that Figure 3(c) AMOS-MM BLEU means BLEU-1.",
            "units": "All displayed values multiplied by 100; heatmap colors use a fixed 0-100 scale.",
            "selection": {b: {"baseline_count": limits[b], "rank_by_mean_of": rank_keys[b], "models": selected[b]} for b in pool},
            "cells": pool}
(ROOT / "figures/three_d_appendix_profiles.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

plt.rcParams.update({"font.family": "Times New Roman", "font.size": 14,
                     "pdf.fonttype": 42, "svg.fonttype": "none", "axes.titleweight": "bold"})
colors = {"CoEvoMed": "#E8A4B8", "Hulu-Med-7B": "#B0E1EC", "Med3DVLM-7B": "#8AB0D8",
          "M3D-Llama2-7B": "#FFD293", "Qwen3.6-27B": "#C7B2DE", "Qwen3.5-9B": "#BDDDBA",
          "Photon-3B-S2 (local)": "#8AB0D8", "Qwen3.8-27B": "#FFD293"}
BASE_HEIGHT = 12.0
PANEL_GAP_IN = 0.45
FIGURE_HEIGHT = BASE_HEIGHT + 2 * PANEL_GAP_IN
fig = plt.figure(figsize=(11.5, FIGURE_HEIGHT), facecolor="white")

def panel_y(y, panel):
    """Add space between panels without scaling their internal geometry."""
    return (BASE_HEIGHT * y + (2 - panel) * PANEL_GAP_IN) / FIGURE_HEIGHT

def panel_axes(bounds, panel):
    x, y, width, height = bounds
    return fig.add_axes([x, panel_y(y, panel), width, height * BASE_HEIGHT / FIGURE_HEIGHT])

def label(benchmark, name):
    source_rows = pool[benchmark][name].values()
    return name + ("*" if any(c["source"] == PUBLISHED for c in source_rows) else "")

def style(ax, ymax):
    ax.set_ylim(0, ymax)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#E5E9EF", linewidth=.65)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#A9AFB8")
    ax.tick_params(length=3)

def bar_value(value):
    return str(Decimal(str(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))

# (a): a wide category panel keeps five groups and every value legible.
ax = panel_axes([.095, .736, .88, .158], 0)
names = selected["M3D-VQA"]
x = np.arange(5)
w = .132
for j, name in enumerate(names):
    values = [pool["M3D-VQA"][name][c]["value"] for c in CATEGORIES]
    bars = ax.bar(x + (j - (len(names)-1)/2)*w, values, w*.94, color=colors[name],
                  edgecolor="#5E6470", linewidth=.45)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x()+bar.get_width()/2, v+1.4, bar_value(v), ha="center", va="bottom", rotation=90, fontsize=11.5)
ax.set_xticks(x, CATEGORIES)
ax.set_ylabel("Accuracy (%)")
style(ax, 116)
ax.set_yticks([0, 25, 50, 75, 100])
fig.text(.085, panel_y(.966, 0), "(a)  M3D-VQA: closed-ended recognition", fontsize=17, weight="bold")
fig.legend([Patch(facecolor=colors[n], edgecolor="#5E6470", linewidth=.4) for n in names],
           [label("M3D-VQA", n) for n in names], loc="upper left", bbox_to_anchor=(.078,panel_y(.962, 0)),
           ncol=3, frameon=False, fontsize=12.5, columnspacing=1.6, handlelength=1.3)

# (b): identical scales across the three open-ended tasks; all bars start at zero.
fig.text(.085, panel_y(.676, 1), "(b)  3D-RAD: open-ended question answering", fontsize=17, weight="bold")
names = selected["3D-RAD"]
fig.legend([Patch(facecolor=colors[n], edgecolor="#5E6470", linewidth=.4) for n in names],
           [label("3D-RAD", n) for n in names], loc="upper left", bbox_to_anchor=(.078,panel_y(.664, 1)),
           ncol=3, frameon=False, fontsize=12.5, columnspacing=1.1, handlelength=1.3)
for i, task in enumerate(TASKS):
    ax = panel_axes([.085+i*.305, .427, .267, .155], 1)
    for j, name in enumerate(names):
        values = [pool["3D-RAD"][name][f"{task}/{m}"]["value"] for m in ["BLEU-1", "ROUGE-1"]]
        bars = ax.bar(np.arange(2)+(j-2)*.16, values, .15, color=colors[name], edgecolor="#5E6470", linewidth=.45)
        for bar, v in zip(bars, values):
            ax.text(bar.get_x()+bar.get_width()/2, v+1.0, bar_value(v), ha="center", va="bottom", rotation=90, fontsize=11.5)
    ax.set_xticks([0, 1], ["BLEU-1", "ROUGE-1"], fontsize=13)
    ax.set_title(task, fontsize=13.5, pad=10)
    style(ax, 70)
    ax.set_yticks([0, 20, 40, 60])
    if i == 0:
        ax.set_ylabel("Score (0-100)")

# (c): shared raw-score scale, with values shown directly (not correlations).
fig.text(.085, panel_y(.365, 2), "(c)  AMOS-MM: report generation", fontsize=17, weight="bold")
names = selected["AMOS-MM"]
data = np.array([[pool["AMOS-MM"][n].get(m, {}).get("value", np.nan) for m in METRICS] for n in names])
ax = panel_axes([.251, .065, .59, .273], 2)
cmap = LinearSegmentedColormap.from_list("soft_blue", ["#FBF7FB", "#E7DCEE", "#D4E4FD", "#8AB0D8"])
cmap.set_bad("#FFFFFF")
im = ax.imshow(data, aspect="auto", cmap=cmap, norm=Normalize(0, 100))
ax.set_xticks(np.arange(4), METRICS, fontsize=13)
ax.set_yticks(np.arange(len(names)), [label("AMOS-MM", n) for n in names], fontsize=12.5)
ax.tick_params(length=0, pad=6)
for tick in ax.get_yticklabels():
    if tick.get_text() == "CoEvoMed":
        tick.set_weight("bold")
for (r, c), value in np.ndenumerate(data):
    ax.text(c, r, "-" if np.isnan(value) else f"{value:.2f}", ha="center", va="center", fontsize=13,
            weight="bold" if r == 0 else "normal", color="#253342")
ax.set_xticks(np.arange(-.5, 4, 1), minor=True)
ax.set_yticks(np.arange(-.5, len(names), 1), minor=True)
ax.grid(which="minor", color="white", linewidth=1.5)
ax.tick_params(which="minor", length=0)
ax.spines[:].set_visible(False)
ax.add_patch(Rectangle((-.5,-.5), 4, 1, facecolor="none", edgecolor=colors["CoEvoMed"], linewidth=2))
cax = panel_axes([.86,.065,.016,.273], 2)
cb = fig.colorbar(im, cax=cax, ticks=[0,25,50,75,100])
cb.ax.tick_params(labelsize=11)
cb.set_label("Score (0-100)", fontsize=12)
cb.outline.set_visible(False)
# Enlarge text while preserving the published canvas and paper scale.
for text in fig.findobj(match=matplotlib.text.Text):
    text.set_fontsize(text.get_fontsize() * 1.265)
PAPER_BBOX = Bbox.from_bounds(.2229166666666667, .38266666666666664,
                              11.046371527777778, 12.435359375)
for ext in ["pdf", "png"]:
    fig.savefig(ROOT / f"figures/three_d_appendix_profiles.{ext}", dpi=220, bbox_inches=PAPER_BBOX, pad_inches=0)
plt.close(fig)
print(json.dumps(selected, indent=2))
