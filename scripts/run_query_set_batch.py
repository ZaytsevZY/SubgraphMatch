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
    parser = argparse.ArgumentParser(description='Run a standard ablation batch over a set of .graph query files.')
    parser.add_argument('--data-file', type=Path, required=True, help='Path to the data graph .graph file.')
    parser.add_argument('--query-dir', type=Path, required=True, help='Directory containing query .graph files.')
    parser.add_argument('--query-glob', type=str, required=True, help='Glob pattern inside query-dir, e.g. query_sparse_24_*.graph')
    parser.add_argument('--dataset-name', type=str, required=True, help='Logical dataset name written to result files.')
    parser.add_argument('--run-tag', type=str, default=None, help='Batch tag prefix. Defaults to a timestamped tag.')
    parser.add_argument('--max-queries', type=int, default=None, help='Optional maximum number of query files to process.')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'results' / 'raw', help='Directory for JSON outputs.')
    parser.add_argument('--omit-mappings', action='store_true', help='Do not include mappings in output JSON files.')
    parser.add_argument('--timeout-sec', type=int, default=None, help='Optional timeout in seconds for each single-query run.')
    return parser.parse_args()


def build_command(args: argparse.Namespace, query_file: Path, run: BatchRun) -> list[str]:
    query_name = query_file.stem
    output_file = args.output_dir / f'{args.run_tag}_{args.dataset_name}_{query_name}_{run.label}.json'
    command = [
        sys.executable,
        str(ROOT / 'scripts' / 'run_gup_experiment.py'),
        '--matcher', run.matcher,
        '--input-format', 'graph',
        '--data-file', str(args.data_file),
        '--query-file', str(query_file),
        '--dataset-name', args.dataset_name,
        '--query-name', query_name,
        '--output-file', str(output_file),
    ]
    if run.disable_reservation_guard:
        command.append('--disable-reservation-guard')
    if run.disable_nogood_guard:
        command.append('--disable-nogood-guard')
    if args.omit_mappings:
        command.append('--omit-mappings')
    if args.timeout_sec is not None:
        command.extend(['--timeout-sec', str(args.timeout_sec)])
    return command


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.run_tag is None:
        args.run_tag = datetime.now().strftime('queryset-%Y%m%d-%H%M%S')

    query_files = sorted(path for path in args.query_dir.glob(args.query_glob) if path.is_file())
    if args.max_queries is not None:
        query_files = query_files[: args.max_queries]

    print('Starting query-set batch run.')
    print(f'  dataset={args.dataset_name}')
    print(f'  data_file={args.data_file}')
    print(f'  query_dir={args.query_dir}')
    print(f'  query_glob={args.query_glob}')
    print(f'  queries={len(query_files)}')
    print(f'  run_tag={args.run_tag}')
    print(f'  timeout_sec={args.timeout_sec}')

    for query_file in query_files:
        print(f'Query file: {query_file.name}')
        for run in DEFAULT_BATCH:
            subprocess.run(build_command(args, query_file, run), check=True)

    print('Query-set batch completed.')


if __name__ == '__main__':
    main()
