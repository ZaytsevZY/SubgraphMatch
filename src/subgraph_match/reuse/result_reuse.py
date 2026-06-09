from __future__ import annotations

from time import perf_counter
from typing import Dict, List, Tuple

from subgraph_match.models import LabeledGraph
from subgraph_match.reuse.reuse_metrics import ReuseResult


def filter_mappings_by_added_edge(
    data_graph: LabeledGraph,
    prev_mappings: List[Dict[int, int]],
    added_edge: Tuple[int, int],
) -> ReuseResult:
    """Filter previous query results using the one newly added query edge."""
    start_time = perf_counter()

    query_u, query_v = added_edge
    reused_mappings: List[Dict[int, int]] = []

    for mapping in prev_mappings:
        data_u = mapping[query_u]
        data_v = mapping[query_v]
        if data_graph.has_edge(data_u, data_v):
            reused_mappings.append(dict(mapping))

    runtime_ms = (perf_counter() - start_time) * 1000
    source_results = len(prev_mappings)
    survived_results = len(reused_mappings)

    return ReuseResult(
        reused_mappings=reused_mappings,
        source_results=source_results,
        survived_results=survived_results,
        filtered_results=source_results - survived_results,
        reuse_runtime_ms=runtime_ms,
    )
