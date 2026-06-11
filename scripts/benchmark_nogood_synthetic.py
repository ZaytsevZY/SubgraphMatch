from __future__ import annotations

import argparse
import json
from statistics import median
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.config import GUPConfig
from subgraph_match.matchers import BacktrackingMatcher, GUPMatcher
from subgraph_match.models import LabeledGraph


def build_workload(
    prefix_size: int,
    cycle_size: int,
    connected: bool = True,
    include_valid_triangle: bool = False,
) -> tuple[LabeledGraph, LabeledGraph]:
    """Build many symmetric prefixes followed by one repeated dead-end.

    The A-labeled query clique has ``prefix_size!`` automorphic embeddings into
    the data clique. Every embedding then reaches the same X-labeled triangle
    query, while the X-labeled data component is only a cycle and therefore
    contains no triangle. An optional separate X triangle adds successful
    branches, producing a mixed workload with both results and reusable
    failures. By default, the two query regions are connected through one
    anchor vertex; the data graph contains all compatible A-X bridge edges.
    """

    if prefix_size < 2:
        raise ValueError('prefix_size must be at least 2')
    if cycle_size < 4:
        raise ValueError('cycle_size must be at least 4')
    if prefix_size >= cycle_size:
        raise ValueError('prefix_size must be smaller than cycle_size to preserve matching order')

    data_graph = LabeledGraph()
    query_graph = LabeledGraph()

    for vertex in range(prefix_size):
        data_graph.add_vertex(vertex, 'A')
        query_graph.add_vertex(vertex, 'A')
    for source in range(prefix_size):
        for target in range(source + 1, prefix_size):
            data_graph.add_edge(source, target)
            query_graph.add_edge(source, target)

    data_offset = prefix_size
    for index in range(cycle_size):
        data_graph.add_vertex(data_offset + index, 'X')
    for index in range(cycle_size):
        data_graph.add_edge(data_offset + index, data_offset + ((index + 1) % cycle_size))

    x_data_vertices = [data_offset + index for index in range(cycle_size)]
    if include_valid_triangle:
        triangle_offset = data_offset + cycle_size
        triangle_vertices = [triangle_offset + index for index in range(3)]
        for vertex in triangle_vertices:
            data_graph.add_vertex(vertex, 'X')
        data_graph.add_edge(triangle_vertices[0], triangle_vertices[1])
        data_graph.add_edge(triangle_vertices[1], triangle_vertices[2])
        data_graph.add_edge(triangle_vertices[0], triangle_vertices[2])
        x_data_vertices.extend(triangle_vertices)

    query_offset = prefix_size
    for index in range(3):
        query_graph.add_vertex(query_offset + index, 'X')
    query_graph.add_edge(query_offset, query_offset + 1)
    query_graph.add_edge(query_offset + 1, query_offset + 2)
    query_graph.add_edge(query_offset, query_offset + 2)

    if connected:
        query_graph.add_edge(0, query_offset)
        for a_vertex in range(prefix_size):
            for x_vertex in x_data_vertices:
                data_graph.add_edge(a_vertex, x_vertex)

    return data_graph, query_graph


def normalize_mappings(mappings: list[dict[int, int]]) -> set[tuple[tuple[int, int], ...]]:
    return {tuple(sorted(mapping.items())) for mapping in mappings}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Benchmark Nogood reuse on a deterministic synthetic workload.')
    parser.add_argument('--prefix-size', type=int, default=7)
    parser.add_argument('--cycle-size', type=int, default=9)
    parser.add_argument('--repeats', type=int, default=9)
    parser.add_argument('--warmups', type=int, default=2)
    parser.add_argument('--output-file', type=Path, default=None)
    parser.add_argument(
        '--include-valid-triangle',
        action='store_true',
        help='Add a valid X triangle so the workload has both results and reusable failures.',
    )
    parser.add_argument(
        '--disconnected',
        action='store_true',
        help='Use the simpler disconnected variant instead of the default connected query.',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_graph, query_graph = build_workload(
        args.prefix_size,
        args.cycle_size,
        connected=not args.disconnected,
        include_valid_triangle=args.include_valid_triangle,
    )

    baseline_times: list[float] = []
    nogood_times: list[float] = []
    baseline_result = None
    nogood_result = None

    def run_baseline():
        return BacktrackingMatcher().match(query_graph, data_graph)

    def run_nogood():
        return GUPMatcher(
            GUPConfig(enable_reservation_guard=False, enable_nogood_guard=True)
        ).match(query_graph, data_graph)

    for _ in range(args.warmups):
        run_baseline()
        run_nogood()

    for repeat in range(args.repeats):
        if repeat % 2 == 0:
            baseline_result = run_baseline()
            nogood_result = run_nogood()
        else:
            nogood_result = run_nogood()
            baseline_result = run_baseline()
        baseline_times.append(baseline_result.statistics.runtime_ms)
        nogood_times.append(nogood_result.statistics.runtime_ms)

    assert baseline_result is not None
    assert nogood_result is not None
    if normalize_mappings(baseline_result.mappings) != normalize_mappings(nogood_result.mappings):
        raise RuntimeError('Nogood result set differs from the baseline.')

    baseline_median = median(baseline_times)
    nogood_median = median(nogood_times)
    speedup = baseline_median / nogood_median if nogood_median else float('inf')

    payload = {
        'prefix_size': args.prefix_size,
        'cycle_size': args.cycle_size,
        'connected': not args.disconnected,
        'include_valid_triangle': args.include_valid_triangle,
        'warmups': args.warmups,
        'repeats': args.repeats,
        'result_mappings': baseline_result.statistics.result_mappings,
        'baseline_partial_mappings': baseline_result.statistics.partial_mappings,
        'nogood_partial_mappings': nogood_result.statistics.partial_mappings,
        'nogood_prunes': nogood_result.statistics.prune_reasons.get('nogood_guard', 0),
        'baseline_times_ms': baseline_times,
        'nogood_times_ms': nogood_times,
        'baseline_median_ms': baseline_median,
        'nogood_median_ms': nogood_median,
        'speedup': speedup,
    }

    for key, value in payload.items():
        if key.endswith('_times_ms'):
            continue
        suffix = 'x' if key == 'speedup' else ''
        rendered = f'{value:.6f}' if isinstance(value, float) else str(value)
        print(f'{key}={rendered}{suffix}')

    if args.output_file is not None:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
        args.output_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
        print(f'output_file={args.output_file}')


if __name__ == '__main__':
    main()
