from __future__ import annotations

from time import perf_counter
from typing import Dict, List

from subgraph_match.matchers.backtracking_matcher import MatchResult
from subgraph_match.matching.order import compute_matching_order
from subgraph_match.metrics.stats import MatchStatistics
from subgraph_match.models import LabeledGraph

CandidateMap = Dict[int, List[int]]


def build_label_only_candidates(query_graph: LabeledGraph, data_graph: LabeledGraph) -> CandidateMap:
    """Build candidate sets using label equality only.

    Unlike subgraph isomorphism, the degree filter ``deg_data >= deg_query`` is
    *unsound* for homomorphism. Because the mapping need not be injective, several
    query neighbors may map to the same data vertex, or even to ``f(v)`` itself
    through the self-loops in ``E_G^+``. Hence a low-degree (or even isolated)
    data vertex can still legitimately host a high-degree query vertex, and
    pruning by degree would discard valid homomorphisms.
    """

    candidates: CandidateMap = {}
    for query_vertex in query_graph.vertices:
        label = query_graph.labels[query_vertex]
        candidates[query_vertex] = sorted(data_graph.vertices_with_label(label))
    return candidates


class HomomorphismMatcher:
    """Correctness-first subgraph homomorphism matcher.

    Enumerates every label-preserving map ``f: V_Q -> V_G`` (not necessarily
    injective) such that every query edge ``(u, v)`` satisfies
    ``(f(u), f(v)) in E_G^+``, where ``E_G^+ = E_G ∪ {(w, w) : w in V_G}``.
    """

    name = 'subgraph_homomorphism'

    def match(self, query_graph: LabeledGraph, data_graph: LabeledGraph) -> MatchResult:
        candidates = build_label_only_candidates(query_graph, data_graph)
        vertex_order = compute_matching_order(query_graph, candidates)
        statistics = MatchStatistics(vertex_order=list(vertex_order))
        results: List[Dict[int, int]] = []
        assignment: Dict[int, int] = {}

        start_time = perf_counter()
        self._search(
            depth=0,
            query_graph=query_graph,
            data_graph=data_graph,
            candidates=candidates,
            vertex_order=vertex_order,
            assignment=assignment,
            statistics=statistics,
            results=results,
        )
        statistics.runtime_ms = (perf_counter() - start_time) * 1000

        return MatchResult(mappings=results, statistics=statistics, vertex_order=vertex_order)

    def _search(
        self,
        depth: int,
        query_graph: LabeledGraph,
        data_graph: LabeledGraph,
        candidates: CandidateMap,
        vertex_order: List[int],
        assignment: Dict[int, int],
        statistics: MatchStatistics,
        results: List[Dict[int, int]],
    ) -> None:
        if depth == len(vertex_order):
            statistics.record_result_mapping()
            results.append(dict(assignment))
            return

        query_vertex = vertex_order[depth]
        for data_vertex in candidates.get(query_vertex, []):
            if not self._is_feasible(
                query_vertex=query_vertex,
                data_vertex=data_vertex,
                query_graph=query_graph,
                data_graph=data_graph,
                assignment=assignment,
                statistics=statistics,
            ):
                continue

            assignment[query_vertex] = data_vertex
            statistics.record_partial_mapping()
            self._search(
                depth=depth + 1,
                query_graph=query_graph,
                data_graph=data_graph,
                candidates=candidates,
                vertex_order=vertex_order,
                assignment=assignment,
                statistics=statistics,
                results=results,
            )
            del assignment[query_vertex]

    def _is_feasible(
        self,
        query_vertex: int,
        data_vertex: int,
        query_graph: LabeledGraph,
        data_graph: LabeledGraph,
        assignment: Dict[int, int],
        statistics: MatchStatistics,
    ) -> bool:
        # No injectivity check: homomorphism allows several query vertices to map
        # to the same data vertex.
        for neighbor in query_graph.neighbors(query_vertex):
            mapped_neighbor = assignment.get(neighbor)
            if mapped_neighbor is None:
                continue
            # Edge constraint over E_G^+: a self-loop (collapsed endpoints) is
            # always present, otherwise the pair must be a real data edge.
            if data_vertex == mapped_neighbor:
                continue
            if not data_graph.has_edge(data_vertex, mapped_neighbor):
                statistics.record_prune('homomorphism_edge_conflict')
                return False

        return True
