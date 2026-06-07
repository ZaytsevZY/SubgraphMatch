from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Build report-specific CSV tables from raw experiment JSON files.')
    parser.add_argument(
        '--input-dir',
        type=Path,
        default=ROOT / 'results' / 'raw',
        help='Directory containing raw JSON files.',
    )
    parser.add_argument(
        '--glob-patterns',
        nargs='*',
        default=['report-*.json'],
        help='Glob patterns used to select JSON files inside input-dir.',
    )
    parser.add_argument(
        '--required-output',
        type=Path,
        default=ROOT / 'results' / 'tables' / 'report_required_metrics.csv',
        help='Output CSV for required-metrics table.',
    )
    parser.add_argument(
        '--ablation-output',
        type=Path,
        default=ROOT / 'results' / 'tables' / 'report_ablation.csv',
        help='Output CSV for ablation table.',
    )
    parser.add_argument(
        '--boundary-output',
        type=Path,
        default=ROOT / 'results' / 'tables' / 'report_boundary_datasets.csv',
        help='Output CSV for boundary/timeout datasets.',
    )
    return parser.parse_args()


def variant_from_payload(payload: dict[str, Any]) -> str:
    cfg = payload.get('matcher_config') or {}
    matcher = cfg.get('matcher')
    res = bool(cfg.get('enable_reservation_guard'))
    nog = bool(cfg.get('enable_nogood_guard'))
    if matcher == 'baseline':
        return 'baseline'
    if res and nog:
        return 'full_gup'
    if res and not nog:
        return 'reservation_only'
    if not res and nog:
        return 'nogood_only'
    return 'unknown'


def flatten_required(payload: dict[str, Any]) -> dict[str, Any]:
    stats = payload.get('statistics') or {}
    prune_reasons = stats.get('prune_reasons') or {}
    reservation_guard_filtered = int(prune_reasons.get('reservation_guard', 0) or 0)
    nogood_guard_filtered = int(prune_reasons.get('nogood_guard', 0) or 0)
    status = payload.get('status', 'success')
    return {
        'dataset_name': payload.get('dataset_name', ''),
        'query_name': payload.get('query_name', ''),
        'variant': variant_from_payload(payload),
        'status': status,
        'runtime_ms': stats.get('runtime_ms', ''),
        'result_mappings_count': payload.get('result_mappings_count', ''),
        'partial_mappings': stats.get('partial_mappings', ''),
        'reservation_guard_filtered': reservation_guard_filtered,
        'nogood_guard_filtered': nogood_guard_filtered,
        'paper_filter_filtered_total': reservation_guard_filtered + nogood_guard_filtered,
        'pruned_partial_mappings': stats.get('pruned_partial_mappings', ''),
        'edge_conflict_count': int(prune_reasons.get('edge_conflict', 0) or 0),
        'injectivity_conflict_count': int(prune_reasons.get('injectivity_conflict', 0) or 0),
        'query_num_vertices': payload.get('query_graph', {}).get('num_vertices', ''),
        'query_num_edges': payload.get('query_graph', {}).get('num_edges', ''),
        'data_num_vertices': payload.get('data_graph', {}).get('num_vertices', ''),
        'data_num_edges': payload.get('data_graph', {}).get('num_edges', ''),
        'time_limit_sec': payload.get('timeout_sec', ''),
        'notes': '' if status == 'success' else 'time-boxed boundary workload',
    }


def safe_float(value: Any) -> float | None:
    try:
        if value == '' or value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value: Any) -> int | None:
    try:
        if value == '' or value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def build_ablation_rows(required_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    baseline_map: dict[tuple[str, str], dict[str, Any]] = {}
    for row in required_rows:
        if row['status'] == 'success' and row['variant'] == 'baseline':
            baseline_map[(row['dataset_name'], row['query_name'])] = row

    ablation_rows: list[dict[str, Any]] = []
    for row in required_rows:
        if row['status'] != 'success':
            continue
        baseline = baseline_map.get((row['dataset_name'], row['query_name']))
        runtime = safe_float(row['runtime_ms'])
        partial = safe_int(row['partial_mappings'])
        result_count = safe_int(row['result_mappings_count'])
        if baseline is not None:
            base_runtime = safe_float(baseline['runtime_ms'])
            base_partial = safe_int(baseline['partial_mappings'])
        else:
            base_runtime = None
            base_partial = None

        runtime_delta = runtime - base_runtime if runtime is not None and base_runtime is not None else ''
        runtime_delta_pct = (
            ((runtime - base_runtime) / base_runtime) * 100.0
            if runtime is not None and base_runtime not in (None, 0)
            else ''
        )
        partial_delta = partial - base_partial if partial is not None and base_partial is not None else ''
        partial_delta_pct = (
            ((partial - base_partial) / base_partial) * 100.0
            if partial is not None and base_partial not in (None, 0)
            else ''
        )

        ablation_rows.append({
            'dataset_name': row['dataset_name'],
            'query_name': row['query_name'],
            'variant': row['variant'],
            'reservation_guard_on': int(row['variant'] in {'reservation_only', 'full_gup'}),
            'nogood_guard_on': int(row['variant'] in {'nogood_only', 'full_gup'}),
            'runtime_ms': row['runtime_ms'],
            'runtime_delta_vs_baseline': runtime_delta,
            'runtime_delta_pct_vs_baseline': runtime_delta_pct,
            'partial_mappings': row['partial_mappings'],
            'partial_delta_vs_baseline': partial_delta,
            'partial_delta_pct_vs_baseline': partial_delta_pct,
            'result_mappings_count': result_count if result_count is not None else '',
            'reservation_guard_filtered': row['reservation_guard_filtered'],
            'nogood_guard_filtered': row['nogood_guard_filtered'],
        })

    ablation_rows.sort(key=lambda r: (r['dataset_name'], r['query_name'], r['variant']))
    return ablation_rows


def build_boundary_rows(required_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in required_rows:
        if row['status'] == 'timeout':
            rows.append({
                'dataset_name': row['dataset_name'],
                'query_name': row['query_name'],
                'variant': row['variant'],
                'time_limit_sec': row['time_limit_sec'],
                'status': row['status'],
                'query_num_vertices': row['query_num_vertices'],
                'query_num_edges': row['query_num_edges'],
                'runtime_ms': row['runtime_ms'],
                'notes': row['notes'],
            })
    rows.sort(key=lambda r: (r['dataset_name'], r['query_name'], r['variant']))
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_payloads(input_dir: Path, patterns: list[str]) -> list[dict[str, Any]]:
    files: dict[Path, None] = {}
    for pattern in patterns:
        for path in input_dir.glob(pattern):
            if path.is_file():
                files[path] = None
    payloads = []
    for path in sorted(files):
        payload = json.loads(path.read_text(encoding='utf-8'))
        payloads.append(payload)
    return payloads


def main() -> None:
    args = parse_args()
    payloads = load_payloads(args.input_dir, args.glob_patterns)
    required_rows = [flatten_required(payload) for payload in payloads]
    required_rows.sort(key=lambda r: (r['dataset_name'], r['query_name'], r['variant']))

    required_fields = [
        'dataset_name', 'query_name', 'variant', 'status', 'runtime_ms',
        'result_mappings_count', 'partial_mappings',
        'reservation_guard_filtered', 'nogood_guard_filtered', 'paper_filter_filtered_total',
        'pruned_partial_mappings', 'edge_conflict_count', 'injectivity_conflict_count',
        'query_num_vertices', 'query_num_edges', 'data_num_vertices', 'data_num_edges',
        'time_limit_sec', 'notes',
    ]
    write_csv(args.required_output, required_rows, required_fields)

    ablation_rows = build_ablation_rows(required_rows)
    ablation_fields = [
        'dataset_name', 'query_name', 'variant',
        'reservation_guard_on', 'nogood_guard_on',
        'runtime_ms', 'runtime_delta_vs_baseline', 'runtime_delta_pct_vs_baseline',
        'partial_mappings', 'partial_delta_vs_baseline', 'partial_delta_pct_vs_baseline',
        'result_mappings_count', 'reservation_guard_filtered', 'nogood_guard_filtered',
    ]
    write_csv(args.ablation_output, ablation_rows, ablation_fields)

    boundary_rows = build_boundary_rows(required_rows)
    boundary_fields = [
        'dataset_name', 'query_name', 'variant', 'time_limit_sec', 'status',
        'query_num_vertices', 'query_num_edges', 'runtime_ms', 'notes',
    ]
    write_csv(args.boundary_output, boundary_rows, boundary_fields)

    print('Report tables built successfully.')
    print(f'  payloads={len(payloads)}')
    print(f'  required_output={args.required_output}')
    print(f'  ablation_output={args.ablation_output}')
    print(f'  boundary_output={args.boundary_output}')


if __name__ == '__main__':
    main()
