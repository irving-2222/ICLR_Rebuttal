"""Build vector report comparison from explicit, source-tagged scores."""
from pathlib import Path
import argparse
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ratescore-only', action='store_true', help='Update the RaTEScore chart without rewriting lexical heatmaps.')
parser.add_argument('--lexical-only', action='store_true', help='Update lexical heatmaps without rewriting the RaTEScore chart.')
args = parser.parse_args()
if args.ratescore_only and args.lexical_only:
    parser.error('Choose only one output mode.')
data = json.loads((ROOT/'figures/report_results.json').read_text())
models = data['models']
# Shared heatmap row order; main-text panels are ranked within each dataset.
ordered = sorted((r for r in models if r.get('show_lexical', True)), key=lambda r: (0 if r['model'].startswith('CoEvoMed') else 1 if r['model'].startswith('Hulu') else 2, r['model']))
plt.rcParams.update({'font.family':'Times New Roman','font.size':9,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'})
lexical_height = max(3.5, 1.4 + .22 * len(ordered))
fig = plt.figure(figsize=(8.7,lexical_height),facecolor='white')
cmap=LinearSegmentedColormap.from_list('soft_ice',['#FCFAFD','#E9E5F4','#CDE1F7'])
cmap.set_bad('#FFFFFF')
heatmap_bottom = .85 / lexical_height
heatmap_height = 1 - 1.4 / lexical_height
for d,dataset in enumerate(data['datasets']):
    ax=fig.add_axes([.205+d*.363,heatmap_bottom,.325,heatmap_height])
    vals=np.array([r['lexical'][d] for r in ordered],dtype=float)
    scaled=np.full_like(vals,np.nan)
    for j in range(vals.shape[1]):
        keep=np.isfinite(vals[:,j]); v=vals[keep,j]
        if len(v): scaled[keep,j]=(v-v.min())/(v.max()-v.min()) if v.max()>v.min() else .5
    heatmap=ax.imshow(np.ma.masked_invalid(scaled),cmap=cmap,vmin=0,vmax=1,aspect='auto')
    ax.set_title(dataset,fontsize=11,pad=7)
    ax.set_xticks(range(8),data['metrics'],rotation=45,ha='right',rotation_mode='anchor',fontsize=8)
    ax.set_yticks(range(len(ordered)),[r['model'] for r in ordered] if d==0 else ['']*len(ordered),fontsize=8)
    ax.tick_params(length=0,pad=5)
    for i in range(len(ordered)):
        for j in range(8):
            v=vals[i,j]
            ax.text(j,i,f'{v:.1f}' if np.isfinite(v) else '--',ha='center',va='center',fontsize=7.4,color='#263346' if np.isfinite(v) else '#A1A7AE')
    ax.set_xticks(np.arange(-.5,8,1),minor=True);ax.set_yticks(np.arange(-.5,len(ordered),1),minor=True)
    ax.grid(which='minor',color='white',linewidth=.8);ax.tick_params(which='minor',length=0)
    for spine in ax.spines.values():spine.set_visible(False)
# One shared scale for the existing per-metric, per-dataset normalization.
colorbar_ax = fig.add_axes([.920, heatmap_bottom, .014, heatmap_height])
colorbar = fig.colorbar(heatmap, cax=colorbar_ax, ticks=np.linspace(0, 1, 6))
colorbar.set_label('Normalized score', fontsize=8, rotation=270, labelpad=10)
colorbar.ax.tick_params(labelsize=8, length=2.5, width=.6, pad=3, colors='#4B5563')
colorbar.outline.set_edgecolor('#7B8490')
colorbar.outline.set_linewidth(.6)
# Match the text enlargement used in the main-paper figures.
for text in fig.findobj(match=matplotlib.text.Text):
    text.set_fontsize(text.get_fontsize() * 1.265)
if not args.ratescore_only:
    for ext in ['pdf','svg','png']:
        fig.savefig(ROOT/f'figures/report_lexical.{ext}',dpi=220)
plt.close(fig)

if args.lexical_only:
    print('Built figures/report_lexical (.pdf, .svg, .png)')
    raise SystemExit(0)
plt.rcParams.update({'font.family': 'Times New Roman'})
models = [r for r in models if r.get('show_rate', True)]
if any(len(r['rate']) != len(data['datasets']) for r in models):
    raise ValueError('RaTEScore entries must follow the dataset order; use null for unavailable scores.')
from matplotlib.patches import Patch
fig = plt.figure(figsize=(10.5, 8.4), facecolor='white')
colors = {'CoEvoMed': '#E8A4B8', 'Other models': '#8AB0D8'}
# Rank each dataset independently and label both x axes in full.
for d, dataset in enumerate(data['datasets']):
    ax = fig.add_axes([.065, .69 if d == 0 else .20, .92, .24])
    ranked = sorted((r for r in models if r['rate'][d] is not None),
                    key=lambda r: (-r['rate'][d], r['model']))
    if not ranked:
        raise ValueError(f'No RaTEScores available for {dataset}.')
    x = np.arange(len(ranked))
    own = [r['model'].startswith('CoEvoMed') for r in ranked]
    values = [r['rate'][d] for r in ranked]
    ax.bar(x, values, width=.70,
           color=[colors['CoEvoMed'] if flag else colors['Other models'] for flag in own],
           edgecolor='none', zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([r['model'] for r in ranked], fontsize=9,
                       rotation=60, ha='right', rotation_mode='anchor')
    for label, flag in zip(ax.get_xticklabels(), own):
        if flag:
            label.set_weight('bold')
    for xi, value, flag in zip(x, values, own):
        ax.text(xi, value + 1.0, f'{value:.2f}', va='bottom', ha='center',
                fontsize=7.4, weight='bold' if flag else 'normal', color='#263346')
    ax.set_xlim(-.7, len(ranked) - .3)
    ax.set_ylim(0, 80)
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.set_ylabel('RaTEScore', fontsize=10)
    ax.set_title(dataset, fontsize=12, fontweight='bold', pad=8)
    ax.tick_params(axis='x', length=0, pad=5)
    ax.tick_params(axis='y', length=3, width=.6, labelsize=8.5)
    ax.grid(axis='y', color='#E9EDF2', linewidth=.65, zorder=0)
    ax.spines[['top', 'right']].set_visible(False)
    for side in ['left', 'bottom']:
        ax.spines[side].set_color('#9BA7B3')
        ax.spines[side].set_linewidth(.65)
fig.legend(handles=[Patch(facecolor=color, label=label) for label, color in colors.items()],
           loc='upper center', bbox_to_anchor=(.53, 1.005), ncol=2, frameon=False,
           fontsize=10, handlelength=1.5, columnspacing=2.5)
# Enlarge all main-figure text at the published paper scale.
for text in fig.findobj(match=matplotlib.text.Text):
    text.set_fontsize(text.get_fontsize() * 1.265)
for ext in ['pdf', 'svg', 'png']:
    fig.savefig(ROOT / f'figures/report_ratescore.{ext}', dpi=250)
plt.close(fig)
print('Built stacked vertical RaTEScore bar chart (.pdf, .svg, .png)')
