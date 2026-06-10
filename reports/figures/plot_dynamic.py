"""Optional task 6 figure: incremental maintenance vs. from-scratch recomputation.

Reads dynamic_data.csv (incremental and scratch runtimes on the demo-stress
graph for one edge insertion and one deletion) and renders a log-scale grouped
bar chart, annotating the speedup. Source data: results/raw/dyn-demo_*.json.

Run: python3 reports/figures/plot_dynamic.py
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
    with (HERE / 'dynamic_data.csv').open(encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    rows = load_rows()
    updates = [r['update'] for r in rows]
    incremental = [float(r['incremental_ms']) for r in rows]
    scratch = [float(r['scratch_ms']) for r in rows]

    x = np.arange(len(updates))
    width = 0.34

    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    bars_inc = ax.bar(x - width / 2, incremental, width, label='Incremental maintenance', color='#41ab5d')
    bars_scr = ax.bar(x + width / 2, scratch, width, label='From-scratch recomputation', color='#cb181d')

    ax.set_yscale('log')
    ax.set_ylabel('Runtime (ms, log scale)')
    ax.set_title('Single-edge result maintenance (demo-stress, 4{,}320 matches)'.replace('{,}', ','))
    ax.set_xticks(x)
    ax.set_xticklabels([u.capitalize() for u in updates])
    ax.grid(axis='y', linestyle=':', alpha=0.5)
    ax.set_axisbelow(True)
    ax.set_ylim(top=max(scratch) * 4)

    for bars in (bars_inc, bars_scr):
        for bar in bars:
            ax.annotate(f'{bar.get_height():.1f}', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 2), textcoords='offset points', ha='center', fontsize=7)

    for i in range(len(updates)):
        speedup = scratch[i] / incremental[i]
        ax.annotate(f'{speedup:.0f}x\nfaster', xy=(x[i], scratch[i]), xytext=(x[i], scratch[i] * 1.7),
                    ha='center', fontsize=9, fontweight='bold', color='#252525')

    fig.legend(frameon=False, fontsize=8, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    for suffix in ('pdf', 'png'):
        fig.savefig(HERE / f'dynamic_speedup.{suffix}', dpi=200, bbox_inches='tight')
    print('wrote dynamic_speedup.pdf / dynamic_speedup.png')


if __name__ == '__main__':
    main()
