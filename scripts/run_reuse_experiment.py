from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.config import GUPConfig
from subgraph_match.io import load_graph_from_edge_list, load_graph_from_graph_format
from subgraph_match.matchers import BacktrackingMatcher, GUPMatcher
from subgraph_match.reuse import find_single_added_edge, filter_mappings_by_added_edge


def normalize_mappings(mappings: list[dict[int, int]]) -> set[tuple[tuple[int, int], ...]]:
    return {tuple(sorted(mapping.items())) for mapping in mappings}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Run a reuse-vs-scratch experiment on a single-edge-addition query pair.'
    )
    parser.add_argument('--matcher', choices=['baseline', 'gup'], default='baseline')
    parser.add_argument('--input-format', choices=['toy', 'graph'], default='toy')
    parser.add_argument('--data-file', type=Path, required=True)
    parser.add_argument('--prev-query-file', type=Path, required=True)
    parser.add_argument('--next-query-file', type=Path, required=True)
    parser.add_argument('--dataset-name', type=str, default='toy_graph')
    parser.add_argument('--prev-query-name', type=str, default='prev_query')
    parser.add_argument('--next-query-name', type=str, default='next_query')
    parser.add_argument('--output-file', type=Path, required=True)
    parser.add_argument('--disable-reservation-guard', action='store_true')
    parser.add_argument('--disable-nogood-guard', action='store_true')
    return parser.parse_args()


def build_matcher(args: argparse.Namespace):
    if args.matcher == 'baseline':
        return BacktrackingMatcher()

    return GUPMatcher(
        GUPConfig(
            enable_reservation_guard=not args.disable_reservation_guard,
            enable_nogood_guard=not args.disable_nogood_guard,
        )
    )


def main() -> None:
    args = parse_args()

    if args.input_format == 'toy':
        data_graph = load_graph_from_edge_list(args.data_file)
        prev_query = load_graph_from_edge_list(args.prev_query_file)
        next_query = load_graph_from_edge_list(args.next_query_file)
    else:
        data_graph = load_graph_from_graph_format(args.data_file)
        prev_query = load_graph_from_graph_format(args.prev_query_file)
        next_query = load_graph_from_graph_format(args.next_query_file)

    added_edge = find_single_added_edge(prev_query, next_query)
    if added_edge is None:
        raise ValueError(
            'The given query pair is not a valid single-edge-addition relation.'
        )

    matcher = build_matcher(args)

    prev_result = matcher.match(query_graph=prev_query, data_graph=data_graph)

    reuse_result = filter_mappings_by_added_edge(
        data_graph=data_graph,
        prev_mappings=prev_result.mappings,
        added_edge=added_edge,
    )

    scratch_result = matcher.match(query_graph=next_query, data_graph=data_graph)

    correctness_match = (
        normalize_mappings(reuse_result.reused_mappings)
        == normalize_mappings(scratch_result.mappings)
    )

    payload = {
        'dataset_name': args.dataset_name,
        'prev_query_name': args.prev_query_name,
        'next_query_name': args.next_query_name,
        'matcher_name': matcher.name,
        'relation_type': 'single_edge_addition',
        'added_edge': list(added_edge),
        'prev_result_mappings': len(prev_result.mappings),
        'reuse_result_mappings': len(reuse_result.reused_mappings),
        'scratch_result_mappings': len(scratch_result.mappings),
        'reuse_runtime_ms': reuse_result.reuse_runtime_ms,
        'scratch_runtime_ms': scratch_result.statistics.runtime_ms,
        'reuse_filtered_results': reuse_result.filtered_results,
        'correctness_match': correctness_match,
        'prev_statistics': prev_result.statistics.to_dict(),
        'scratch_statistics': scratch_result.statistics.to_dict(),
    }

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print('Reuse experiment completed.')
    print(f'  matcher={matcher.name}')
    print(f'  added_edge={added_edge}')
    print(f'  prev_result_mappings={len(prev_result.mappings)}')
    print(f'  reuse_result_mappings={len(reuse_result.reused_mappings)}')
    print(f'  scratch_result_mappings={len(scratch_result.mappings)}')
    print(f'  correctness_match={correctness_match}')
    print(f'  output={args.output_file}')


if __name__ == '__main__':
    main()
