"""Plot the author-supplied Gemma cross-backbone results."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

# Preserve the published canvas and plot scale across font changes.
PAPER_BBOX = Bbox.from_bounds(0.22518576388888886, 0.09694791666666655, 8.890814236111112, 2.6466770833333335)
from matplotlib.ticker import MultipleLocator

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / '2D_result/gemma_3_4b_trajectory.json').read_text())
rows = data['records']
checkpoint_labels = ['Base'] + [f'R{i}' for i in range(1, len(rows))]
plt.rcParams.update({'font.family': 'Times New Roman', 'font.size': 10,
                     'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none'})
fig, axes = plt.subplots(1, 2, figsize=(9.2, 2.9))
specs = [
    ('VQA-RAD', 'vqa_semantic_accuracy_pct', 1, 'Semantic accuracy (%)', '#897CD3', (39, 77)),
    ('MIMIC-CXR', 'mimic_ratescore', 100, 'RaTEScore (x100)', '#60B0F4', (46, 70)),
]
for ax, (title, metric, scale, ylabel, color, limits) in zip(axes, specs):
    scores = [row[metric] * scale for row in rows]
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='#E9EDF0', linewidth=.7)
    edge = 'white'
    ax.plot(range(len(rows)), scores, color=color, linewidth=2, marker='o',
            markersize=5, markeredgecolor=edge, markeredgewidth=.6, zorder=3)
    endpoint = len(rows) - 1
    ax.scatter([endpoint], [scores[endpoint]], color=color, s=60, edgecolor=edge, linewidth=1, zorder=4)
    # Keep only the Base and final-checkpoint value labels in each panel.
    for i, offset in [(0, (0, 10)), (endpoint, (0, 11))]:
        ax.annotate(f'{scores[i]:.2f}', (i, scores[i]), xytext=offset,
                    textcoords='offset points', ha='center', fontsize=10, color='#35414D')
    ax.set_title(title, fontsize=12, fontweight='semibold', pad=10)
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Checkpoint', labelpad=8)
    ax.set_xticks(range(len(rows)), checkpoint_labels)
    ax.set_xlim(-.5, len(rows) - .5)
    ax.set_ylim(*limits)
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.tick_params(axis='both', color='#B3BAC1', length=3)
    ax.spines[['top', 'right']].set_visible(False)
    for side in ['left', 'bottom']:
        ax.spines[side].set_color('#BAC2C9')
fig.subplots_adjust(left=.085, right=.98, bottom=.23, top=.82, wspace=.32)
# Enlarge all main-figure text at the published paper scale.
for text in fig.findobj(match=matplotlib.text.Text):
    text.set_fontsize(text.get_fontsize() * 1.265)
for suffix in ['pdf', 'svg', 'png']:
    fig.savefig(ROOT / f'figures/gemma_trajectory.{suffix}', dpi=240, bbox_inches=PAPER_BBOX, facecolor='white')
plt.close(fig)
