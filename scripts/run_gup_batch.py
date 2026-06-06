from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class BatchRun:
    label: str
    matcher: str
    disable_reservation_guard: bool = False
    disable_nogood_guard: bool = False


DEFAULT_BATCH: list[BatchRun] = [
    BatchRun(label='baseline', matcher='baseline'),
    BatchRun(label='gup_reservation_only', matcher='gup', disable_nogood_guard=True),
    BatchRun(label='gup_nogood_only', matcher='gup', disable_reservation_guard=True),
    BatchRun(label='gup_full', matcher='gup'),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run a standard batch of baseline/GUP ablation experiments.')
    parser.add_argument(
        '--data-file',
        type=Path,
        default=ROOT / 'data' / 'sample' / 'toy_graph.txt',
        help='Path to the data graph file.',
    )
    parser.add_argument(
        '--query-file',
        type=Path,
        default=ROOT / 'data' / 'sample' / 'toy_query_path.txt',
        help='Path to the query graph file.',
    )
    parser.add_argument(
        '--dataset-name',
        type=str,
        default='toy_graph',
        help='Logical dataset name written to each result file.',
    )
    parser.add_argument(
        '--query-name',
        type=str,
        default='toy_query_path',
        help='Logical query name written to each result file.',
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=ROOT / 'results' / 'raw',
        help='Directory for JSON outputs.',
    )
    parser.add_argument(
        '--run-tag',
        type=str,
        default=None,
        help='Optional prefix tag for all output files. Defaults to a timestamped tag.',
    )
    parser.add_argument(
        '--omit-mappings',
        action='store_true',
        help='Do not include the full mappings list in output JSON files.',
    )
    return parser.parse_args()


def build_command(args: argparse.Namespace, run: BatchRun) -> list[str]:
    output_file = args.output_dir / f'{args.run_tag}_{args.dataset_name}_{args.query_name}_{run.label}.json'
    command = [
        sys.executable,
        str(ROOT / 'scripts' / 'run_gup_experiment.py'),
        '--matcher',
        run.matcher,
        '--data-file',
        str(args.data_file),
        '--query-file',
        str(args.query_file),
        '--dataset-name',
        args.dataset_name,
        '--query-name',
        args.query_name,
        '--output-file',
        str(output_file),
    ]
    if run.disable_reservation_guard:
        command.append('--disable-reservation-guard')
    if run.disable_nogood_guard:
        command.append('--disable-nogood-guard')
    if args.omit_mappings:
        command.append('--omit-mappings')
    return command


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.run_tag is None:
        args.run_tag = datetime.now().strftime('batch-%Y%m%d-%H%M%S')

    print('Starting batch experiment run.')
    print(f'  dataset={args.dataset_name}')
    print(f'  query={args.query_name}')
    print(f'  output_dir={args.output_dir}')
    print(f'  run_tag={args.run_tag}')

    for run in DEFAULT_BATCH:
        print(f'Running configuration: {run.label}')
        subprocess.run(build_command(args, run), check=True)

    print('Batch experiment completed.')


if __name__ == '__main__':
    main()
