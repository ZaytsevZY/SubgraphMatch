from __future__ import annotations

from typing import Optional, Tuple

from subgraph_match.models import LabeledGraph


Edge = Tuple[int, int]


def normalize_edge(u: int, v: int) -> Edge:
    return (u, v) if u <= v else (v, u)


def extract_edge_set(graph: LabeledGraph) -> set[Edge]:
    edges: set[Edge] = set()
    for u in graph.labels:
        for v in graph.neighbors(u):
            if u < v:
                edges.add((u, v))
    return edges


def have_same_labeled_vertices(
    prev_query: LabeledGraph,
    next_query: LabeledGraph,
) -> bool:
    if set(prev_query.labels) != set(next_query.labels):
        return False

    for vertex, label in prev_query.labels.items():
        if next_query.labels.get(vertex) != label:
            return False

    return True


def find_single_added_edge(
    prev_query: LabeledGraph,
    next_query: LabeledGraph,
) -> Optional[Edge]:
    """Return the single added edge if next_query = prev_query + one edge.

    Required conditions:
    - same vertex id set
    - same vertex labels
    - next edge set is prev edge set plus exactly one undirected edge
    """
    if not have_same_labeled_vertices(prev_query, next_query):
        return None

    prev_edges = extract_edge_set(prev_query)
    next_edges = extract_edge_set(next_query)

    if not prev_edges.issubset(next_edges):
        return None

    added_edges = next_edges - prev_edges
    if len(added_edges) != 1:
        return None

    return next(iter(added_edges))
