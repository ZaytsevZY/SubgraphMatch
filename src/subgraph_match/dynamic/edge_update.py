from __future__ import annotations

from typing import Tuple

from subgraph_match.models import LabeledGraph
from subgraph_match.reuse.query_relation import normalize_edge

Edge = Tuple[int, int]


def clone_graph(graph: LabeledGraph) -> LabeledGraph:
    """Return an independent copy of ``graph``.

    The clone shares no mutable state with the original, so edge updates applied
    to the clone never mutate the graph the previous results were computed on.
    """

    clone = LabeledGraph()
    clone.labels = dict(graph.labels)
    clone.adjacency = {vertex: set(neighbors) for vertex, neighbors in graph.adjacency.items()}
    # Guarantee every labeled vertex has an adjacency entry (isolated vertices included).
    for vertex in clone.labels:
        clone.adjacency.setdefault(vertex, set())
    return clone


def _require_valid_endpoints(graph: LabeledGraph, source: int, target: int) -> None:
    if source not in graph.labels or target not in graph.labels:
        raise ValueError(
            f'Edge endpoints {(source, target)} are not both present in the graph.'
        )
    if source == target:
        raise ValueError('Self-loop edges are not supported by the dynamic update model.')


def apply_edge_insertion(graph: LabeledGraph, source: int, target: int) -> LabeledGraph:
    """Return a new graph equal to ``graph`` plus the undirected edge ``(source, target)``.

    The original graph is left unchanged. Raises if the endpoints are invalid or
    if the edge already exists (so callers cannot silently insert a duplicate).
    """

    _require_valid_endpoints(graph, source, target)
    if graph.has_edge(source, target):
        raise ValueError(f'Edge {normalize_edge(source, target)} already exists; cannot insert.')

    new_graph = clone_graph(graph)
    new_graph.add_edge(source, target)
    return new_graph


def apply_edge_deletion(graph: LabeledGraph, source: int, target: int) -> LabeledGraph:
    """Return a new graph equal to ``graph`` minus the undirected edge ``(source, target)``.

    The original graph is left unchanged. Raises if the endpoints are invalid or
    if the edge does not exist.
    """

    _require_valid_endpoints(graph, source, target)
    if not graph.has_edge(source, target):
        raise ValueError(f'Edge {normalize_edge(source, target)} does not exist; cannot delete.')

    new_graph = clone_graph(graph)
    new_graph.adjacency[source].discard(target)
    new_graph.adjacency[target].discard(source)
    return new_graph
