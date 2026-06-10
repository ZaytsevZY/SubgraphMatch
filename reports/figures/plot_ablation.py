"""Ablation figure: search-space reduction by filtering strategy.

Reads ablation_data.csv (partial-mapping reduction percentage relative to the
baseline, per real workload) and renders a grouped bar chart. Source data are
the |Partial delta (%)| values from the ablation table in the report.

Run: python3 reports/figures/plot_ablation.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent


def load_rows():
    with (HERE / 'ablation_data.csv').open(encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    rows = load_rows()
    workloads = [r['workload'] for r in rows]
    reservation = [float(r['reservation_only']) for r in rows]
    nogood = [float(r['nogood_only']) for r in rows]
    full = [float(r['full_gup']) for r in rows]

    x = np.arange(len(workloads))
    width = 0.26

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.bar(x - width, reservation, width, label='Reservation only', color='#2c7fb8')
    ax.bar(x, nogood, width, label='Nogood only', color='#cccccc')
    ax.bar(x + width, full, width, label='Full GuP', color='#253494')

    ax.set_ylabel('Partial-mapping reduction vs. baseline (%)')
    ax.set_title('Search-space reduction by filtering strategy')
    ax.set_xticks(x)
    ax.set_xticklabels(workloads, rotation=20, ha='right', fontsize=8)
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis='y', linestyle=':', alpha=0.5)
    ax.set_axisbelow(True)

    # Annotate the dominant bar to make the headline finding explicit.
    ax.annotate('reservation guard\ndrives all pruning',
                xy=(1 - width, 78.43), xytext=(1.6, 64),
                fontsize=8, ha='left',
                arrowprops=dict(arrowstyle='->', color='#2c7fb8'))

    fig.tight_layout()
    for suffix in ('pdf', 'png'):
        fig.savefig(HERE / f'ablation.{suffix}', dpi=200, bbox_inches='tight')
    print('wrote ablation.pdf / ablation.png')


if __name__ == '__main__':
    main()
