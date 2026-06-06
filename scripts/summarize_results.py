from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Summarize raw experiment JSON files into a CSV table.')
    parser.add_argument(
        '--input-dir',
        type=Path,
        default=ROOT / 'results' / 'raw',
        help='Directory containing raw JSON result files.',
    )
    parser.add_argument(
        '--output-file',
        type=Path,
        default=ROOT / 'results' / 'tables' / 'summary.csv',
        help='CSV file to write.',
    )
    parser.add_argument(
        '--glob-pattern',
        type=str,
        default='*.json',
        help='Glob pattern used to select result files inside the input directory.',
    )
    return parser.parse_args()


def flatten_result(payload: dict) -> dict[str, object]:
    statistics = payload.get('statistics') or {}
    matcher_config = payload.get('matcher_config', {})
    prune_reasons = statistics.get('prune_reasons', {})

    return {
        'dataset_name': payload.get('dataset_name', ''),
        'query_name': payload.get('query_name', ''),
        'status': payload.get('status', 'success'),
        'timeout_sec': payload.get('timeout_sec', ''),
        'matcher_name': payload.get('matcher_name', ''),
        'matcher': matcher_config.get('matcher', ''),
        'enable_reservation_guard': matcher_config.get('enable_reservation_guard', ''),
        'enable_nogood_guard': matcher_config.get('enable_nogood_guard', ''),
        'data_file': payload.get('data_file', ''),
        'query_file': payload.get('query_file', ''),
        'data_num_vertices': payload.get('data_graph', {}).get('num_vertices', ''),
        'data_num_edges': payload.get('data_graph', {}).get('num_edges', ''),
        'query_num_vertices': payload.get('query_graph', {}).get('num_vertices', ''),
        'query_num_edges': payload.get('query_graph', {}).get('num_edges', ''),
        'result_mappings_count': payload.get('result_mappings_count', ''),
        'statistics_result_mappings': statistics.get('result_mappings', ''),
        'partial_mappings': statistics.get('partial_mappings', ''),
        'pruned_partial_mappings': statistics.get('pruned_partial_mappings', ''),
        'guard_checks_total': statistics.get('guard_checks_total', ''),
        'runtime_ms': statistics.get('runtime_ms', ''),
        'vertex_order': ' '.join(map(str, statistics.get('vertex_order', []))),
        'prune_reasons_json': json.dumps(prune_reasons, ensure_ascii=False, sort_keys=True),
    }


def main() -> None:
    args = parse_args()
    json_files = sorted(path for path in args.input_dir.glob(args.glob_pattern) if path.is_file())
    rows = [flatten_result(json.loads(path.read_text(encoding='utf-8'))) for path in json_files]

    args.output_file.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        args.output_file.write_text('', encoding='utf-8')
        print(f'No JSON result files found in {args.input_dir}. Wrote empty file to {args.output_file}.')
        return

    fieldnames = list(rows[0].keys())
    with args.output_file.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print('Summary completed.')
    print(f'  input_dir={args.input_dir}')
    print(f'  glob_pattern={args.glob_pattern}')
    print(f'  files={len(json_files)}')
    print(f'  output={args.output_file}')


if __name__ == '__main__':
    main()
