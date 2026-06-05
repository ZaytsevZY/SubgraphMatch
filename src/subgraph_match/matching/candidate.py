from __future__ import annotations

from typing import Dict, List

from subgraph_match.models import LabeledGraph


CandidateMap = Dict[int, List[int]]


def build_label_candidates(query_graph: LabeledGraph, data_graph: LabeledGraph) -> CandidateMap:
    """Generate initial candidates for each query vertex using label equality."""
    candidate_map: CandidateMap = {}
    for query_vertex in query_graph.vertices:
        label = query_graph.labels[query_vertex]
        candidate_map[query_vertex] = sorted(data_graph.vertices_with_label(label))
    return candidate_map
