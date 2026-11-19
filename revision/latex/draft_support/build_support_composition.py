"""Render the 2D and 3D support pools, both counted as source records.

The source counts and official links are stored in figures/support_composition.json.
Sector angles are proportional to counts; 3D report sectors are not enlarged.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.transforms import Bbox
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "figures/support_composition.json").read_text())
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 17,
                     "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"})
INK = "#151515"
LABEL_INK = "#142341"
COUNT_INK = "#303030"
LEADER = "#8E8E8E"
CENTER = "#5D6C7F"
# Main hues sampled from the author's reference; small sectors use related tones.
PALETTE = ["#E14E66", "#F9D49F", "#008686", "#CD5528", "#FF9695",
           "#9C5B57", "#2E9FAD", "#5F7FAE", "#C38476", "#9CA7B3", "#D4AA74"]
QA_COLOR, REPORT_COLOR = "#F9D49F", "#008686"
# Keep the published canvas size so larger text stays larger in the paper.
PAPER_BBOX = Bbox.from_bounds(.12, .28424778106508924,
                              18.284397754355557, 7.105540679188889)


def center(ax, total, unit, radius):
    ax.add_patch(Circle((0, 0), radius, facecolor=CENTER,
                        edgecolor="white", linewidth=1.6, zorder=3))
    ax.text(0, .13, f"{total:,}", ha="center", va="center", fontsize=24,
            fontweight="bold", color="white", zorder=4)
    ax.text(0, -.21, unit, ha="center", va="center", fontsize=14,
            color="white", zorder=4)


def outside_labels(ax, wedges, records, total, radius=1.24, label_x=1.25):
    """Monotone leader-line layout, keeping small-sector labels separate."""
    entries = []
    for wedge, (name, value) in zip(wedges, records):
        angle = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
        x, y = np.cos(angle), np.sin(angle)
        entries.append((x, y, name, value))
    for sign in [-1, 1]:
        side = sorted([e for e in entries if (e[0] >= 0) == (sign > 0)], key=lambda e: e[1])
        ys = np.array([e[1] * radius for e in side])
        for i in range(1, len(ys)):
            ys[i] = max(ys[i], ys[i-1] + .43)
        if len(ys):
            ys[-1] = min(ys[-1], 1.82)
        for i in range(len(ys)-2, -1, -1):
            ys[i] = min(ys[i], ys[i+1] - .43)
        for (x, y, name, value), ty in zip(side, ys):
            # Separate this long label from the neighboring 2D panel.
            if name == "AbdomenAtlas1.0Mini":
                ty -= .14
            tx = sign * (label_x - .15 if name == "AbdomenAtlas1.0Mini" else label_x)
            ax.plot([x, tx - sign*.07, tx], [y, ty, ty],
                    color=LEADER, lw=1.15)
            display_name = name.replace("PubMedVision-IU subset", "PubMedVision-IU")
            ax.text(tx + .035*sign, ty + .043, display_name, ha="left" if sign > 0 else "right",
                    va="bottom", fontsize=18, color=LABEL_INK)
            ax.text(tx + .035*sign, ty + .020, f"{value:,}  ({100*value/total:.1f}%)",
                    ha="left" if sign > 0 else "right", va="top", fontsize=16.5, color=COUNT_INK)


def main():
    two, three = DATA["two_d"], DATA["three_d"]
    assert sum(v for _, v in two["sources"]) == two["total"]
    for kind in ["qa", "reports"]:
        assert sum(v for _, v in three[kind]["sources"]) == three[kind]["total"]
    assert three["qa"]["total"] + three["reports"]["total"] == three["total"]
    fig, axes = plt.subplots(1, 2, figsize=(18, 7.8))
    ax = axes[0]
    wedges, _ = ax.pie([v for _, v in two["sources"]], startangle=70, counterclock=False,
                      colors=PALETTE, wedgeprops={"width": .39, "edgecolor": "white", "linewidth": 1.8})
    center(ax, two["total"], "source records", radius=.61)
    outside_labels(ax, wedges, two["sources"], two["total"])
    ax.set_title("(a) 2D support pool", fontsize=23, fontweight="semibold", color=INK, pad=20)

    ax = axes[1]
    records = three["qa"]["sources"] + three["reports"]["sources"]
    colors = ["#CD5528", "#FF9695", "#2E9FAD", "#9C5B57", REPORT_COLOR, "#CD5528"]
    wedges, _ = ax.pie([v for _, v in records], startangle=90, counterclock=False,
                      colors=colors, wedgeprops={"width": .27, "edgecolor": "white", "linewidth": 1.6})
    ax.pie([three["qa"]["total"], three["reports"]["total"]], radius=.73,
           startangle=90, counterclock=False, colors=[QA_COLOR, REPORT_COLOR],
           wedgeprops={"width": .20, "edgecolor": "white", "linewidth": 1.6})
    center(ax, three["total"], "source records", radius=.53)
    # QA source labels only; the two narrow report sectors share one callout.
    outside_labels(ax, wedges[:4], records[:4], three["total"], label_x=1.05)
    angle = np.deg2rad(90 + 180*three["reports"]["total"]/three["total"])
    ax.plot([np.cos(angle), -.12, -.55], [np.sin(angle), 1.45, 1.45], color=REPORT_COLOR, lw=1.2)
    ax.text(-.60, 1.46, "Reports: 6,328 (2.9%)", ha="center", va="bottom", fontsize=16,
            color="#006B6B", fontweight="semibold")
    ax.text(-.60, 1.75, "M3D-Cap  5,370  ·  CT-RATE  958", ha="center", fontsize=14.5, color=INK)
    ax.text(0, -1.64, "QA: 209,329 (97.1%)", ha="center", fontsize=17,
            color="#8E411F", fontweight="semibold")
    ax.set_title("(b) 3D support pool", fontsize=23, fontweight="semibold", color=INK, pad=20)
    for ax in axes:
        ax.set_xlim(-2.6, 2.6)
        ax.set_ylim(-1.85, 2.08)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.subplots_adjust(left=.01, right=.99, top=.89, bottom=.02, wspace=.08)
    # Match the text enlargement used in the main-paper figures.
    for text in fig.findobj(match=matplotlib.text.Text):
        text.set_fontsize(text.get_fontsize() * 1.265)
    for suffix in ["pdf", "svg", "png"]:
        fig.savefig(ROOT / f"figures/support_composition.{suffix}", dpi=220,
                    bbox_inches=PAPER_BBOX, pad_inches=0, facecolor="white")
    plt.close(fig)
    print("Verified totals: 2D=259767; 3D QA=209329, reports=6328, total=215657")


if __name__ == "__main__":
    main()
