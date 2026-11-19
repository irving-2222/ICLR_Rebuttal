"""Plot InternVL3-9B trajectories directly from the author's Markdown record."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.transforms import Bbox

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ablation/intervl消融.md"
keys = ["vqa_accuracy_pct", "mimic_rouge_l", "mimic_bleu4", "mimic_meteor",
        "mimic_ratescore", "mimic_composite", "global_score"]
records = []
for line in SOURCE.read_text().splitlines():
    if not line.startswith("| 基线") and not line.startswith("| 第"):
        continue
    cells = [v.strip().replace("**", "") for v in line.strip().strip("|").split("|")]
    round_id = 0 if cells[0] == "基线" else int(cells[0].replace("第", "").replace("轮", ""))
    assert len(cells) == len(keys) + 1
    records.append({"round": round_id, **dict(zip(keys, map(float, cells[1:])))})
assert [r["round"] for r in records] == list(range(9))
data = {"model": "InternVL3-9B", "source": str(SOURCE.relative_to(ROOT)),
        "training": "Separate VQA-RAD and MIMIC-CXR models; full-parameter SFT with LLaMA-Factory; consecutive rounds continue from previous weights.",
        "raw_ratescore_scale": "0-1", "displayed_ratescore_scale": "0-100",
        "records": records}
(ROOT / "figures/internvl_trajectory.json").write_text(json.dumps(data, indent=2) + "\n")

plt.rcParams.update({"font.family": "Times New Roman", "font.size": 10,
                     "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"})
fig, axes = plt.subplots(1, 2, figsize=(9.2, 2.9))
specs = [
    ("VQA-RAD", "vqa_accuracy_pct", 1, "Accuracy (%)", "#897CD3", (52, 84)),
    ("MIMIC-CXR", "mimic_ratescore", 100, "RaTEScore (x100)", "#60B0F4", (47, 69)),
]
for ax, (title, metric, scale, ylabel, color, limits) in zip(axes, specs):
    x = [r["round"] for r in records]
    y = [r[metric] * scale for r in records]
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#E9EDF0", linewidth=.7)
    ax.plot(x, y, color=color, linewidth=2, marker="o", markersize=5,
            markeredgecolor="white", markeredgewidth=.6, zorder=3)
    ax.scatter([x[-1]], [y[-1]], color=color, s=60, edgecolor="white", linewidth=1, zorder=4)
    for i, offset in [(0, (4, -12)), (len(x)-1, (0, 11))]:
        ax.annotate(f"{y[i]:.2f}", (x[i], y[i]), xytext=offset,
                    textcoords="offset points", ha="left" if i == 0 else "center", fontsize=10, color="#35414D")
    ax.set_title(title, fontsize=12, fontweight="semibold", pad=10)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Completed training rounds", labelpad=8)
    ax.set_xticks(x, ["Base"] + [str(i) for i in range(1, 9)])
    ax.set_xlim(-.5, 8.5)
    ax.set_ylim(*limits)
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.tick_params(axis="both", color="#B3BAC1", length=3)
    ax.spines[["top", "right"]].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color("#BAC2C9")
fig.subplots_adjust(left=.095, right=.98, bottom=.26, top=.80, wspace=.32)
# Enlarge text while preserving the published canvas and paper scale.
for text in fig.findobj(match=matplotlib.text.Text):
    text.set_fontsize(text.get_fontsize() * 1.265)
PAPER_BBOX = Bbox.from_bounds(.21991666666666674, .08561111111111103,
                              8.892424628831943, 2.6466770833333335)
for suffix in ["pdf", "svg", "png"]:
    fig.savefig(ROOT / f"figures/internvl_trajectory.{suffix}", dpi=240,
                bbox_inches=PAPER_BBOX, pad_inches=0, facecolor="white")
plt.close(fig)
print("InternVL3-9B: 9 checkpoints, VQA accuracy and RaTEScore only")
print("Final gains:", round(records[-1][keys[0]] - records[0][keys[0]], 2),
      round(100 * (records[-1]["mimic_ratescore"] - records[0]["mimic_ratescore"]), 2))
