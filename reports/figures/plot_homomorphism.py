"""Optional task 7 figure: subgraph homomorphism vs. isomorphism.

Reads homomorphism_data.csv and renders, for each workload, a stacked bar whose
total height is the homomorphism count, split into the injective part (which
equals the isomorphism count) and the additional non-injective homomorphisms.
Two panels are used because the toy and demo counts differ by three orders of
magnitude. Source data: results/raw/hom-*.json.

Run: python3 reports/figures/plot_homomorphism.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent

ISO_COLOR = '#238b45'
NONINJ_COLOR = '#a1d99b'


def load_rows():
    with (HERE / 'homomorphism_data.csv').open(encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def draw_panel(ax, label, iso, noninj):
    ax.bar([0], [iso], width=0.6, label='Isomorphisms (injective)', color=ISO_COLOR)
    ax.bar([0], [noninj], width=0.6, bottom=[iso],
           label='Non-injective homomorphisms', color=NONINJ_COLOR)
    total = iso + noninj
    ax.text(0, total, f'Hom = {total}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.text(0, iso / 2, f'Iso\n{iso}', ha='center', va='center', fontsize=8, color='white')
    if noninj > 0:
        ax.text(0, iso + noninj / 2, f'+{noninj}', ha='center', va='center', fontsize=8)
    ax.set_xticks([0])
    ax.set_xticklabels([label], fontsize=9)
    ax.set_ylim(0, total * 1.18)
    ax.grid(axis='y', linestyle=':', alpha=0.5)
    ax.set_axisbelow(True)


def main() -> None:
    rows = load_rows()
    fig, axes = plt.subplots(1, len(rows), figsize=(6.0, 3.4))
    if len(rows) == 1:
        axes = [axes]

    for ax, row in zip(axes, rows):
        draw_panel(ax, row['workload'], int(row['isomorphisms']), int(row['non_injective_homomorphisms']))

    axes[0].set_ylabel('Number of mappings')
    handles, labels = axes[0].get_legend_handles_labels()
    fig.suptitle('Subgraph homomorphism vs. isomorphism', y=1.0, fontsize=11)
    fig.legend(handles, labels, frameon=False, fontsize=8, loc='lower center', ncol=2,
               bbox_to_anchor=(0.5, -0.04))

    fig.tight_layout(rect=(0, 0.07, 1, 0.94))
    for suffix in ('pdf', 'png'):
        fig.savefig(HERE / f'homomorphism.{suffix}', dpi=200, bbox_inches='tight')
    print('wrote homomorphism.pdf / homomorphism.png')


if __name__ == '__main__':
    main()
