from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys
from typing import List

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_SCRIPT = ROOT / 'scripts' / 'run_dynamic_experiment.py'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Run insert + delete dynamic-maintenance experiments and summarize them.'
    )
    parser.add_argument('--matcher', choices=['baseline', 'gup'], default='baseline')
    parser.add_argument('--input-format', choices=['toy', 'graph'], default='toy')
    parser.add_argument('--data-file', type=Path, required=True)
    parser.add_argument('--query-file', type=Path, required=True)
    parser.add_argument('--dataset-name', type=str, required=True)
    parser.add_argument('--query-name', type=str, required=True)
    parser.add_argument('--run-tag', type=str, required=True)
    parser.add_argument('--raw-dir', type=Path, default=ROOT / 'results' / 'raw')
    parser.add_argument('--summary-file', type=Path, default=None)
    return parser.parse_args()


def run_one(args: argparse.Namespace, change_type: str) -> Path:
    output_file = args.raw_dir / f'{args.run_tag}_{args.dataset_name}_{args.query_name}_{change_type}.json'
    command = [
        sys.executable,
        str(EXPERIMENT_SCRIPT),
        '--matcher', args.matcher,
        '--input-format', args.input_format,
        '--data-file', str(args.data_file),
        '--query-file', str(args.query_file),
        '--change-type', change_type,
        '--dataset-name', args.dataset_name,
        '--query-name', args.query_name,
        '--output-file', str(output_file),
    ]
    print(f'Running {change_type} ...')
    subprocess.run(command, check=True)
    return output_file


def summarize(paths: List[Path], summary_file: Path) -> None:
    header = [
        'dataset', 'query', 'change_type', 'changed_edge', 'prev_results', 'new_results',
        'added', 'removed', 'anchored_partials', 'incremental_ms', 'scratch_ms', 'speedup', 'correct',
    ]
    rows = [header]
    for path in paths:
        payload = json.loads(path.read_text(encoding='utf-8'))
        speedup = payload.get('speedup_scratch_over_incremental')
        speedup_text = f'{speedup:.2f}' if isinstance(speedup, (int, float)) else ''
        rows.append(
            [
                payload['dataset_name'],
                payload['query_name'],
                payload['change_type'],
                '-'.join(str(v) for v in payload['changed_edge']),
                payload['prev_result_mappings'],
                payload['new_result_mappings'],
                payload['added_mappings'],
                payload['removed_mappings'],
                payload['anchored_partial_mappings'],
                f"{payload['incremental_runtime_ms']:.5f}",
                f"{payload['scratch_runtime_ms']:.5f}",
                speedup_text,
                payload['correctness_match'],
            ]
        )

    summary_file.parent.mkdir(parents=True, exist_ok=True)
    with summary_file.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    print(f'Summary written to {summary_file}')
    print('\n'.join(','.join(str(cell) for cell in row) for row in rows))


def main() -> None:
    args = parse_args()
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    paths = [run_one(args, change_type) for change_type in ('insert', 'delete')]

    summary_file = args.summary_file or (
        ROOT / 'results' / 'tables' / f'{args.run_tag}-dynamic-summary.csv'
    )
    summarize(paths, summary_file)


if __name__ == '__main__':
    main()
