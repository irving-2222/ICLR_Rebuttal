"""Render author-supplied checkpoint trajectories without interpolation."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

# Preserve the published canvas and plot scale across font changes.
PAPER_BBOX = Bbox.from_bounds(0.16254687500000006, 0.09318576388888913, 10.618114573794445, 3.0674392361111114)
from matplotlib.ticker import MultipleLocator

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / '2D_result/evolution_trajectory.json').read_text())
plt.rcParams.update({'font.family': 'Times New Roman', 'font.size': 10,
                     'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none'})
fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.25))
colors = ['#719DC5', '#BE7890', '#79A991']
limits = [(62, 97), (35, 76), (49, 73)]
rounds = data['completed_rounds']
for ax, (name, scores), color, lim in zip(axes, data['scores'].items(), colors, limits):
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='#E9EDF0', linewidth=.7)
    ax.axvline(7, color='#A5ABB3', linewidth=1, linestyle=(0, (3, 3)), zorder=1)
    ax.plot(rounds, scores, color=color, linewidth=2, marker='o', markersize=4.5,
            markeredgecolor='white', markeredgewidth=.6, zorder=3)
    ax.scatter([7], [scores[6]], color=color, s=58, edgecolor='white', linewidth=1, zorder=4)
    for idx, offset, align in [(0, (4, -14), 'left'), (6, (-5, 12), 'right'), (9, (0, -16), 'center')]:
        ax.annotate(f'{scores[idx]:.2f}', (rounds[idx], scores[idx]), xytext=offset,
                    textcoords='offset points', ha=align, fontsize=9, color='#35414D')
    ax.set_title(name, fontweight='semibold', fontsize=12, pad=10)
    ax.set_xlabel('Completed training rounds', fontsize=10, labelpad=8)
    ax.set_ylabel(data['metrics'][name], fontsize=10)
    ax.set_xlim(.5, 10.5)
    ax.set_ylim(*lim)
    ax.set_xticks(rounds)
    ax.yaxis.set_major_locator(MultipleLocator(10 if name != 'IU-Xray' else 5))
    ax.tick_params(axis='both', labelsize=9, color='#B3BAC1', length=3)
    ax.spines[['top', 'right']].set_visible(False)
    for side in ['left', 'bottom']:
        ax.spines[side].set_color('#BAC2C9')
fig.subplots_adjust(left=.065, right=.985, bottom=.20, top=.86, wspace=.32)
# Enlarge all main-figure text at the published paper scale.
for text in fig.findobj(match=matplotlib.text.Text):
    text.set_fontsize(text.get_fontsize() * 1.3915)
for suffix in ['pdf', 'svg', 'png']:
    fig.savefig(ROOT / f'figures/evolution_trajectory.{suffix}', dpi=240, bbox_inches=PAPER_BBOX, facecolor='white')
plt.close(fig)
