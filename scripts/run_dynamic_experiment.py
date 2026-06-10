from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.config import GUPConfig
from subgraph_match.dynamic import (
    apply_edge_deletion,
    maintain_result_on_edge_change,
)
from subgraph_match.io import load_graph_from_edge_list, load_graph_from_graph_format
from subgraph_match.matchers import BacktrackingMatcher, GUPMatcher
from subgraph_match.models import LabeledGraph
from subgraph_match.reuse.query_relation import extract_edge_set

Mapping = Dict[int, int]
Edge = Tuple[int, int]


def normalize_mappings(mappings: List[Mapping]) -> set:
    return {tuple(sorted(mapping.items())) for mapping in mappings}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            'Run an incremental-vs-scratch experiment for maintaining result '
            'mappings under a single data-graph edge insertion or deletion.'
        )
    )
    parser.add_argument('--matcher', choices=['baseline', 'gup'], default='baseline')
    parser.add_argument('--input-format', choices=['toy', 'graph'], default='toy')
    parser.add_argument('--data-file', type=Path, required=True)
    parser.add_argument('--query-file', type=Path, required=True)
    parser.add_argument('--change-type', choices=['insert', 'delete'], required=True)
    parser.add_argument(
        '--edge',
        type=str,
        default=None,
        help='Changed data edge as "a,b". If omitted, an edge used by a result is auto-picked.',
    )
    parser.add_argument('--dataset-name', type=str, default='toy_graph')
    parser.add_argument('--query-name', type=str, default='query')
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


def load_graph(path: Path, input_format: str) -> LabeledGraph:
    if input_format == 'toy':
        return load_graph_from_edge_list(path)
    return load_graph_from_graph_format(path)


def parse_edge(text: str) -> Edge:
    parts = text.replace(' ', '').split(',')
    if len(parts) != 2:
        raise ValueError(f'--edge must be "a,b", got {text!r}')
    return int(parts[0]), int(parts[1])


def pick_used_edge(query_graph: LabeledGraph, mappings: List[Mapping]) -> Optional[Edge]:
    """Pick a data edge that is actually used by some result mapping.

    Deleting such an edge is guaranteed to remove at least one result mapping,
    which makes the experiment non-trivial.
    """

    for query_a, query_b in sorted(extract_edge_set(query_graph)):
        for mapping in mappings:
            data_a = mapping.get(query_a)
            data_b = mapping.get(query_b)
            if data_a is not None and data_b is not None and data_a != data_b:
                return (data_a, data_b)
    return None


def main() -> None:
    args = parse_args()

    data_graph = load_graph(args.data_file, args.input_format)
    query_graph = load_graph(args.query_file, args.input_format)
    matcher = build_matcher(args)

    explicit_edge = parse_edge(args.edge) if args.edge else None

    # Determine the "current" base graph (before the change) and the changed edge.
    # For a delete experiment the base graph is the loaded graph G.
    # For an insert experiment we construct the base graph as G minus the chosen
    # edge, so that inserting it back is a meaningful, guaranteed-non-trivial change.
    if args.change_type == 'delete':
        if explicit_edge is not None:
            changed_edge = explicit_edge
        else:
            probe = matcher.match(query_graph=query_graph, data_graph=data_graph)
            changed_edge = pick_used_edge(query_graph, probe.mappings)
            if changed_edge is None:
                raise ValueError(
                    'No result mapping uses any query edge on this workload; '
                    'cannot auto-pick a deletion edge. Pass --edge explicitly.'
                )
        base_graph = data_graph
    else:  # insert
        if explicit_edge is not None:
            changed_edge = explicit_edge
            # For an insert experiment the loaded graph is treated as the "after"
            # graph G'; the base ("before") graph is G' minus the inserted edge.
            # Hence --edge must name an edge that EXISTS in the loaded graph.
            try:
                base_graph = apply_edge_deletion(data_graph, *changed_edge)
            except ValueError as exc:
                raise ValueError(
                    f'For --change-type insert, --edge {changed_edge} must already exist in the '
                    "loaded data graph, which is treated as the post-insertion graph G'. "
                    f'(underlying error: {exc})'
                ) from exc
        else:
            probe = matcher.match(query_graph=query_graph, data_graph=data_graph)
            changed_edge = pick_used_edge(query_graph, probe.mappings)
            if changed_edge is None:
                raise ValueError(
                    'No result mapping uses any query edge on this workload; '
                    'cannot auto-pick an insertion edge. Pass --edge explicitly.'
                )
            base_graph = apply_edge_deletion(data_graph, *changed_edge)

    # "Current" indexed result on the base graph (before the change).
    prev_result = matcher.match(query_graph=query_graph, data_graph=base_graph)

    # --- Incremental maintenance ---
    maintenance, new_graph = maintain_result_on_edge_change(
        query_graph=query_graph,
        base_graph=base_graph,
        prev_mappings=prev_result.mappings,
        edge=changed_edge,
        change_type=args.change_type,
    )

    # --- From-scratch recomputation on the changed graph + diff ---
    scratch_result = matcher.match(query_graph=query_graph, data_graph=new_graph)
    prev_keys = normalize_mappings(prev_result.mappings)
    scratch_keys = normalize_mappings(scratch_result.mappings)
    scratch_added = scratch_keys - prev_keys
    scratch_removed = prev_keys - scratch_keys

    # --- Correctness checks ---
    new_result_match = normalize_mappings(maintenance.new_result) == scratch_keys
    added_match = normalize_mappings(maintenance.added_mappings) == scratch_added
    removed_match = normalize_mappings(maintenance.removed_mappings) == scratch_removed
    correctness_match = new_result_match and added_match and removed_match

    speedup = (
        scratch_result.statistics.runtime_ms / maintenance.incremental_runtime_ms
        if maintenance.incremental_runtime_ms > 0
        else None
    )

    payload = {
        'dataset_name': args.dataset_name,
        'query_name': args.query_name,
        'matcher_name': matcher.name,
        'relation_type': f'single_edge_{args.change_type}',
        'change_type': args.change_type,
        'changed_edge': list(changed_edge),
        'prev_result_mappings': maintenance.prev_result_mappings,
        'new_result_mappings': maintenance.new_result_mappings,
        'scratch_result_mappings': len(scratch_result.mappings),
        'added_mappings': maintenance.added_count,
        'removed_mappings': maintenance.removed_count,
        'anchored_partial_mappings': maintenance.anchored_partial_mappings,
        'anchored_attempts': maintenance.anchored_attempts,
        'incremental_runtime_ms': maintenance.incremental_runtime_ms,
        'scratch_runtime_ms': scratch_result.statistics.runtime_ms,
        'speedup_scratch_over_incremental': speedup,
        'correctness_match': correctness_match,
        'correctness_detail': {
            'new_result_match': new_result_match,
            'added_match': added_match,
            'removed_match': removed_match,
        },
        'prev_statistics': prev_result.statistics.to_dict(),
        'scratch_statistics': scratch_result.statistics.to_dict(),
    }

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print('Dynamic maintenance experiment completed.')
    print(f'  matcher={matcher.name}')
    print(f'  change_type={args.change_type}')
    print(f'  changed_edge={changed_edge}')
    print(f'  prev_result_mappings={maintenance.prev_result_mappings}')
    print(f'  new_result_mappings={maintenance.new_result_mappings}')
    print(f'  added={maintenance.added_count} removed={maintenance.removed_count}')
    print(f'  incremental_runtime_ms={maintenance.incremental_runtime_ms:.5f}')
    print(f'  scratch_runtime_ms={scratch_result.statistics.runtime_ms:.5f}')
    if speedup is not None:
        print(f'  speedup_scratch_over_incremental={speedup:.2f}x')
    print(f'  correctness_match={correctness_match}')
    print(f'  output={args.output_file}')


if __name__ == '__main__':
    main()
