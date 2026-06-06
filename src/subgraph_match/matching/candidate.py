from __future__ import annotations

from typing import Dict, List

from subgraph_match.models import LabeledGraph


CandidateMap = Dict[int, List[int]]


def build_label_candidates(query_graph: LabeledGraph, data_graph: LabeledGraph) -> CandidateMap:
    """Generate initial candidates using label equality and degree compatibility.

    This is still much lighter than the filtering used in the original GuP
    implementation, but it is already closer to the standard LDF baseline than
    pure label-only filtering.
    """
    candidate_map: CandidateMap = {}
    for query_vertex in query_graph.vertices:
        label = query_graph.labels[query_vertex]
        query_degree = query_graph.degree(query_vertex)
        candidate_map[query_vertex] = sorted(
            data_vertex
            for data_vertex in data_graph.vertices_with_label(label)
            if data_graph.degree(data_vertex) >= query_degree
        )
    return candidate_map
