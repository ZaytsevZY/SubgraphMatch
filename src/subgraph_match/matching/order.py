from __future__ import annotations

from typing import Dict, List

from subgraph_match.models import LabeledGraph


def compute_matching_order(query_graph: LabeledGraph, candidates: Dict[int, List[int]]) -> List[int]:
    """Order query vertices by smaller candidate set first, then by higher degree."""
    return sorted(
        query_graph.vertices,
        key=lambda vertex: (len(candidates.get(vertex, [])), -query_graph.degree(vertex), vertex),
    )
