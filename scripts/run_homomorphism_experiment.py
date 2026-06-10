from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.homomorphism import HomomorphismMatcher
from subgraph_match.io import load_graph_from_edge_list, load_graph_from_graph_format
from subgraph_match.matchers import BacktrackingMatcher
from subgraph_match.models import LabeledGraph

Mapping = Dict[int, int]


def normalize_mappings(mappings: List[Mapping]) -> set:
    return {tuple(sorted(mapping.items())) for mapping in mappings}


def is_injective(mapping: Mapping) -> bool:
    return len(set(mapping.values())) == len(mapping)


def load_graph(path: Path, input_format: str) -> LabeledGraph:
    if input_format == 'toy':
        return load_graph_from_edge_list(path)
    return load_graph_from_graph_format(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            'Run a subgraph-homomorphism experiment and compare it with subgraph '
            'isomorphism on the same data and query graphs.'
        )
    )
    parser.add_argument('--input-format', choices=['toy', 'graph'], default='toy')
    parser.add_argument('--data-file', type=Path, required=True)
    parser.add_argument('--query-file', type=Path, required=True)
    parser.add_argument('--dataset-name', type=str, default='toy_graph')
    parser.add_argument('--query-name', type=str, default='query')
    parser.add_argument('--output-file', type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    data_graph = load_graph(args.data_file, args.input_format)
    query_graph = load_graph(args.query_file, args.input_format)

    hom_result = HomomorphismMatcher().match(query_graph=query_graph, data_graph=data_graph)
    iso_result = BacktrackingMatcher().match(query_graph=query_graph, data_graph=data_graph)

    injective_hom = [mapping for mapping in hom_result.mappings if is_injective(mapping)]
    non_injective_hom = len(hom_result.mappings) - len(injective_hom)

    # An injective homomorphism is exactly a subgraph isomorphism, so the
    # injective subset of the homomorphism results must equal the isomorphism
    # results. This is an independent built-in correctness cross-check.
    injective_hom_equals_iso = normalize_mappings(injective_hom) == normalize_mappings(iso_result.mappings)
    hom_superset_of_iso = normalize_mappings(iso_result.mappings).issubset(
        normalize_mappings(hom_result.mappings)
    )

    payload = {
        'dataset_name': args.dataset_name,
        'query_name': args.query_name,
        'hom_matcher_name': HomomorphismMatcher.name,
        'iso_matcher_name': BacktrackingMatcher.name,
        'hom_result_mappings': len(hom_result.mappings),
        # Note: hom_partial_mappings counts a strictly larger, injectivity-unpruned
        # search tree than iso_partial_mappings, so the two are not a like-for-like
        # search-effort comparison; they are reported for reference only.
        'hom_partial_mappings': hom_result.statistics.partial_mappings,
        'hom_pruned_partial_mappings': hom_result.statistics.pruned_partial_mappings,
        'iso_result_mappings': len(iso_result.mappings),
        'iso_partial_mappings': iso_result.statistics.partial_mappings,
        'injective_hom_mappings': len(injective_hom),
        'non_injective_hom_mappings': non_injective_hom,
        'hom_runtime_ms': hom_result.statistics.runtime_ms,
        'iso_runtime_ms': iso_result.statistics.runtime_ms,
        'injective_hom_equals_iso': injective_hom_equals_iso,
        'hom_superset_of_iso': hom_superset_of_iso,
        'hom_statistics': hom_result.statistics.to_dict(),
        'iso_statistics': iso_result.statistics.to_dict(),
    }

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print('Homomorphism experiment completed.')
    print(f'  dataset={args.dataset_name} query={args.query_name}')
    print(f'  hom_result_mappings={len(hom_result.mappings)}')
    print(f'  iso_result_mappings={len(iso_result.mappings)}')
    print(f'  injective_hom_mappings={len(injective_hom)} (should equal iso)')
    print(f'  non_injective_hom_mappings={non_injective_hom}')
    print(f'  hom_partial_mappings={hom_result.statistics.partial_mappings}')
    print(f'  injective_hom_equals_iso={injective_hom_equals_iso}')
    print(f'  hom_superset_of_iso={hom_superset_of_iso}')
    print(f'  output={args.output_file}')


if __name__ == '__main__':
    main()
