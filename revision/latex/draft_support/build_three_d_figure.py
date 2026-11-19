"""Render source-tagged 3D comparisons without imputing missing scores."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'figures/three_d_results.json').read_text())
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                    'pdf.fonttype': 42, 'svg.fonttype': 'none'})
fig = plt.figure(figsize=(9.3, 10.5), facecolor='white')
cmap = LinearSegmentedColormap.from_list('ice', ['#FCFAFD', '#DCE8F0', '#94B6CD'])

def heatmap(rect, rows, labels, values):
    ax = fig.add_axes(rect)
    im = ax.imshow(values, cmap=cmap, vmin=0, vmax=100, aspect='auto')
    ax.set_xticks(range(len(labels)), labels, fontsize=8)
    ax.set_yticks(range(len(rows)), [r['model'] for r in rows], fontsize=7.8)
    ax.tick_params(length=0, pad=5)
    for i, row in enumerate(rows):
        ours = row['model'] == 'EvoForma'
        if ours:
            ax.get_yticklabels()[i].set_weight('bold')
        for j, value in enumerate(values[i]):
            ax.text(j, i, f'{value:.2f}', ha='center', va='center',
                    fontsize=7.6, weight='bold' if ours else 'normal')
    ax.set_xticks(np.arange(-.5, len(labels), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(rows), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=1)
    ax.tick_params(which='minor', length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return im

fig.text(.025, .975, '(a) M3D-VQA: closed-ended category accuracy', weight='bold', fontsize=11)
rows = list(reversed(data['m3d']['rows']))
heatmap([.25, .715, .72, .235], rows, data['m3d']['categories'],
        np.array([r['scores'] for r in rows]))

fig.text(.025, .665, '(b) 3D-RAD: open-ended task comparison', weight='bold', fontsize=11)
rows = list(reversed(data['rad']['rows']))
im = heatmap([.25, .375, .72, .265], rows,
             ['AD B1', 'AD R1', 'IO B1', 'IO R1', 'MC B1', 'MC R1'],
             np.array([np.array(r['scores']).flatten() for r in rows]))
fig.text(.25, .329, 'B1: BLEU-1    R1: ROUGE-1', fontsize=8, color='#53616F')
cax = fig.add_axes([.69, .330, .28, .009])
cb = fig.colorbar(im, cax=cax, orientation='horizontal', ticks=[0, 50, 100])
cb.ax.tick_params(labelsize=7, length=2)
cb.outline.set_visible(False)

fig.text(.025, .279, '(c) EvoForma: fine-grained 3D-RAD profile', weight='bold', fontsize=11)
ax = fig.add_axes([.31, .057, .66, .200])
subtasks = data['rad']['subtasks']
y = np.arange(len(subtasks), dtype=float)
y[4:] += .45
y[6:] += .45
labels = [f"{r['name']}  (n={r['samples']:,})" for r in subtasks]
for metric, color, marker in [(0, '#739BB6', 'o'), (1, '#C38297', 'D')]:
    offset = -.16 if metric == 0 else .16
    ax.scatter([r['scores'][metric] for r in subtasks], y + offset, s=23,
               color=color, marker=marker, label=data['rad']['metrics'][metric], zorder=3)
    for yi, row in zip(y, subtasks):
        value = row['scores'][metric]
        ax.text(value + .9, yi + offset, f'{value:.2f}', va='center', fontsize=6.8, color=color)
ax.set_yticks(y, labels, fontsize=7.5)
ax.set_ylim(y[-1] + .65, -.7)
ax.set_xlim(0, 80)
ax.set_xticks([0, 20, 40, 60, 80])
ax.set_xlabel('Score (0-100)', fontsize=8, labelpad=3)
ax.tick_params(length=2, labelsize=7.5)
ax.xaxis.grid(True, color='#E4E9EC', linestyle='--', linewidth=.6)
for boundary in [(y[3]+y[4])/2, (y[5]+y[6])/2]:
    ax.axhline(boundary, color='#E5E8EB', linewidth=.7)
ax.spines[['top', 'right']].set_visible(False)
ax.spines[['left', 'bottom']].set_linewidth(.6)
ax.legend(loc='lower right', frameon=False, fontsize=7)
fig.text(.025, .009, 'AD: Anomaly Detection; IO: Image Observation; MC: Medical Computation.',
         fontsize=8, color='#53616F')
for ext in ['pdf', 'svg', 'png']:
    fig.savefig(ROOT / f'figures/three_d_analysis.{ext}', dpi=220)
plt.close(fig)
print('Built figures/three_d_analysis.pdf, .svg, .png')
