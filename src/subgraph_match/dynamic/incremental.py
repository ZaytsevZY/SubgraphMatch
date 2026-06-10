from __future__ import annotations

from time import perf_counter
from typing import Dict, List, Tuple

from subgraph_match.dynamic.dynamic_metrics import DynamicMaintenanceResult
from subgraph_match.dynamic.edge_update import apply_edge_deletion, apply_edge_insertion
from subgraph_match.matching.candidate import build_label_candidates
from subgraph_match.models import LabeledGraph
from subgraph_match.reuse.query_relation import extract_edge_set

Mapping = Dict[int, int]
Edge = Tuple[int, int]
MappingKey = Tuple[Tuple[int, int], ...]


def _mapping_key(mapping: Mapping) -> MappingKey:
    return tuple(sorted(mapping.items()))


def enumerate_embeddings_using_edge(
    query_graph: LabeledGraph,
    graph: LabeledGraph,
    edge: Edge,
) -> Tuple[List[Mapping], Dict[str, int]]:
    """Enumerate every complete valid embedding that *uses* the data edge ``edge``.

    A complete embedding ``f`` of ``query_graph`` in ``graph`` is said to use the
    undirected data edge ``(a, b)`` if some query edge ``(u, v)`` satisfies
    ``{f(u), f(v)} == {a, b}``.

    By the monotonicity of subgraph isomorphism in the data edge set, this set is
    exactly the result difference caused by inserting or deleting ``(a, b)``:
    on insertion these are the *added* mappings, on deletion the *removed* ones.

    Precondition: ``graph`` already contains ``edge`` (i.e. we always enumerate in
    the graph version where the changed edge is present).

    Returns the deduplicated list of complete mappings plus a counters dict with
    ``partial`` (partial extensions explored) and ``anchors`` (number of pinned
    query-edge / orientation pairs that were searched).
    """

    data_u, data_v = edge
    if not graph.has_edge(data_u, data_v):
        # The affected set D_e is defined over the graph version that CONTAINS the
        # edge. Anchoring onto an absent edge would pin a query edge to a missing
        # data edge and emit spurious embeddings, so we reject it loudly.
        raise ValueError(
            f'enumerate_embeddings_using_edge requires the graph to contain edge {edge}; '
            'pass the graph version in which the changed edge is present.'
        )

    counters: Dict[str, int] = {'partial': 0, 'anchors': 0}
    seen: set[MappingKey] = set()
    results: List[Mapping] = []

    # Candidate sets (label + degree filter) computed once on the graph that
    # contains the changed edge; reused across every anchor.
    candidates = build_label_candidates(query_graph, graph)

    query_labels = query_graph.labels
    data_labels = graph.labels

    for query_edge in sorted(extract_edge_set(query_graph)):
        query_a, query_b = query_edge
        # The query edge may map onto the data edge in either orientation.
        for image_a, image_b in ((data_u, data_v), (data_v, data_u)):
            if image_a == image_b:
                continue  # self-loops are not part of this model
            if query_labels[query_a] != data_labels.get(image_a):
                continue
            if query_labels[query_b] != data_labels.get(image_b):
                continue
            counters['anchors'] += 1
            _anchored_search(
                query_graph=query_graph,
                graph=graph,
                candidates=candidates,
                anchor={query_a: image_a, query_b: image_b},
                results=results,
                seen=seen,
                counters=counters,
            )

    return results, counters


def _anchored_search(
    query_graph: LabeledGraph,
    graph: LabeledGraph,
    candidates: Dict[int, List[int]],
    anchor: Mapping,
    results: List[Mapping],
    seen: set[MappingKey],
    counters: Dict[str, int],
) -> None:
    """Backtracking search that extends the fixed ``anchor`` to full embeddings."""

    query_to_data: Mapping = dict(anchor)
    data_to_query: Dict[int, int] = {data: query for query, data in anchor.items()}

    remaining = [vertex for vertex in query_graph.vertices if vertex not in anchor]
    remaining.sort(
        key=lambda vertex: (len(candidates.get(vertex, [])), -query_graph.degree(vertex), vertex)
    )

    def is_feasible(query_vertex: int, data_vertex: int) -> bool:
        if data_vertex in data_to_query:
            return False
        for neighbor in query_graph.neighbors(query_vertex):
            mapped = query_to_data.get(neighbor)
            if mapped is not None and not graph.has_edge(data_vertex, mapped):
                return False
        return True

    def recurse(depth: int) -> None:
        if depth == len(remaining):
            mapping = dict(query_to_data)
            key = _mapping_key(mapping)
            if key not in seen:
                seen.add(key)
                results.append(mapping)
            return

        query_vertex = remaining[depth]
        for data_vertex in candidates.get(query_vertex, []):
            if not is_feasible(query_vertex, data_vertex):
                continue
            query_to_data[query_vertex] = data_vertex
            data_to_query[data_vertex] = query_vertex
            counters['partial'] += 1
            recurse(depth + 1)
            del query_to_data[query_vertex]
            del data_to_query[data_vertex]

    recurse(0)


def maintain_result_on_edge_change(
    query_graph: LabeledGraph,
    base_graph: LabeledGraph,
    prev_mappings: List[Mapping],
    edge: Edge,
    change_type: str,
) -> Tuple[DynamicMaintenanceResult, LabeledGraph]:
    """Incrementally maintain the result set when ``base_graph`` changes by one edge.

    ``base_graph`` is the data graph *before* the change and ``prev_mappings`` is
    its already-materialized result set ``Result(Q, base_graph)``. ``change_type``
    is ``'insert'`` or ``'delete'``.

    Returns the maintenance result (added / removed / new result set and counters)
    together with the new data graph ``base_graph (+/-) edge``.

    The graph copy is produced *before* timing starts, so the reported
    ``incremental_runtime_ms`` measures only the maintenance work (anchored search
    plus set bookkeeping) and is directly comparable to a from-scratch matcher
    runtime, which also excludes graph construction.
    """

    source, target = edge

    if change_type == 'insert':
        new_graph = apply_edge_insertion(base_graph, source, target)
        graph_with_edge = new_graph
    elif change_type == 'delete':
        new_graph = apply_edge_deletion(base_graph, source, target)
        graph_with_edge = base_graph
    else:
        raise ValueError(f"change_type must be 'insert' or 'delete', got {change_type!r}")

    start_time = perf_counter()

    affected, counters = enumerate_embeddings_using_edge(query_graph, graph_with_edge, edge)
    affected_by_key = {_mapping_key(mapping): mapping for mapping in affected}
    prev_by_key = {_mapping_key(mapping): mapping for mapping in prev_mappings}

    if change_type == 'insert':
        added = [mapping for key, mapping in affected_by_key.items() if key not in prev_by_key]
        removed: List[Mapping] = []
        new_result = list(prev_by_key.values()) + added
    else:
        removed = [mapping for key, mapping in affected_by_key.items() if key in prev_by_key]
        added = []
        removed_keys = {_mapping_key(mapping) for mapping in removed}
        new_result = [mapping for key, mapping in prev_by_key.items() if key not in removed_keys]

    runtime_ms = (perf_counter() - start_time) * 1000

    result = DynamicMaintenanceResult(
        change_type=change_type,
        changed_edge=(source, target),
        prev_result_mappings=len(prev_mappings),
        new_result_mappings=len(new_result),
        added_mappings=added,
        removed_mappings=removed,
        new_result=new_result,
        anchored_partial_mappings=counters['partial'],
        anchored_attempts=counters['anchors'],
        incremental_runtime_ms=runtime_ms,
    )
    return result, new_graph
