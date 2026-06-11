from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.config import GUPConfig
from subgraph_match.io import load_graph_from_graph_format
from subgraph_match.matchers import BacktrackingMatcher, GUPMatcher


VARIANTS = ('baseline', 'reservation_only', 'nogood_only', 'full')


def build_matcher(variant: str):
    if variant == 'baseline':
        return BacktrackingMatcher()
    if variant == 'reservation_only':
        return GUPMatcher(GUPConfig(enable_reservation_guard=True, enable_nogood_guard=False))
    if variant == 'nogood_only':
        return GUPMatcher(GUPConfig(enable_reservation_guard=False, enable_nogood_guard=True))
    if variant == 'full':
        return GUPMatcher(GUPConfig(enable_reservation_guard=True, enable_nogood_guard=True))
    raise ValueError(f'Unknown variant: {variant}')


def normalize_mappings(mappings: list[dict[int, int]]) -> set[tuple[tuple[int, int], ...]]:
    return {tuple(sorted(mapping.items())) for mapping in mappings}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Repeat a real-data GuP ablation with rotated run order.')
    parser.add_argument('--data-file', type=Path, required=True)
    parser.add_argument('--query-file', type=Path, required=True)
    parser.add_argument('--dataset-name', required=True)
    parser.add_argument('--query-name', required=True)
    parser.add_argument('--warmups', type=int, default=2)
    parser.add_argument('--repeats', type=int, default=9)
    parser.add_argument('--output-file', type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_graph = load_graph_from_graph_format(args.data_file)
    query_graph = load_graph_from_graph_format(args.query_file)

    def run(variant: str):
        return build_matcher(variant).match(query_graph, data_graph)

    for _ in range(args.warmups):
        for variant in VARIANTS:
            run(variant)

    times: dict[str, list[float]] = {variant: [] for variant in VARIANTS}
    final_results = {}
    expected_mappings = None

    for repeat in range(args.repeats):
        offset = repeat % len(VARIANTS)
        run_order = VARIANTS[offset:] + VARIANTS[:offset]
        for variant in run_order:
            result = run(variant)
            normalized = normalize_mappings(result.mappings)
            if expected_mappings is None:
                expected_mappings = normalized
            elif normalized != expected_mappings:
                raise RuntimeError(f'{variant} result set differs from the other variants')
            times[variant].append(result.statistics.runtime_ms)
            final_results[variant] = result

    variants_payload = {}
    for variant in VARIANTS:
        statistics = final_results[variant].statistics
        variants_payload[variant] = {
            'result_mappings': statistics.result_mappings,
            'partial_mappings': statistics.partial_mappings,
            'pruned_partial_mappings': statistics.pruned_partial_mappings,
            'guard_checks_total': statistics.guard_checks_total,
            'prune_reasons': statistics.prune_reasons,
            'times_ms': times[variant],
            'median_runtime_ms': median(times[variant]),
        }

    baseline_median = variants_payload['baseline']['median_runtime_ms']
    for variant in VARIANTS[1:]:
        runtime = variants_payload[variant]['median_runtime_ms']
        variants_payload[variant]['speedup_vs_baseline'] = baseline_median / runtime

    payload = {
        'dataset_name': args.dataset_name,
        'query_name': args.query_name,
        'data_file': str(args.data_file.resolve()),
        'query_file': str(args.query_file.resolve()),
        'warmups': args.warmups,
        'repeats': args.repeats,
        'variants': variants_payload,
    }

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'dataset={args.dataset_name}')
    print(f'query={args.query_name}')
    for variant in VARIANTS:
        row = variants_payload[variant]
        speedup = row.get('speedup_vs_baseline', 1.0)
        nogood_prunes = row['prune_reasons'].get('nogood_guard', 0)
        reservation_prunes = row['prune_reasons'].get('reservation_guard', 0)
        print(
            f'{variant}: results={row["result_mappings"]} '
            f'partial={row["partial_mappings"]} '
            f'reservation_prunes={reservation_prunes} '
            f'nogood_prunes={nogood_prunes} '
            f'median_ms={row["median_runtime_ms"]:.6f} '
            f'speedup={speedup:.3f}x'
        )
    print(f'output_file={args.output_file}')


if __name__ == '__main__':
    main()
