from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Dict, List

from subgraph_match.matching.candidate import build_label_candidates
from subgraph_match.matching.order import compute_matching_order
from subgraph_match.matching.state import SearchState
from subgraph_match.metrics.stats import MatchStatistics
from subgraph_match.models import LabeledGraph


@dataclass
class MatchResult:
    mappings: List[Dict[int, int]]
    statistics: MatchStatistics
    vertex_order: List[int]


class BacktrackingMatcher:
    """Correctness-first baseline subgraph matcher."""

    name = 'baseline_backtracking'

    def match(self, query_graph: LabeledGraph, data_graph: LabeledGraph) -> MatchResult:
        candidates = build_label_candidates(query_graph, data_graph)
        vertex_order = compute_matching_order(query_graph, candidates)
        statistics = MatchStatistics(vertex_order=list(vertex_order))
        results: List[Dict[int, int]] = []
        state = SearchState()

        start_time = perf_counter()
        self._search(
            depth=0,
            query_graph=query_graph,
            data_graph=data_graph,
            candidates=candidates,
            vertex_order=vertex_order,
            state=state,
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
        candidates: Dict[int, List[int]],
        vertex_order: List[int],
        state: SearchState,
        statistics: MatchStatistics,
        results: List[Dict[int, int]],
    ) -> None:
        if depth == len(vertex_order):
            statistics.record_result_mapping()
            results.append(state.copy_mapping())
            return

        query_vertex = vertex_order[depth]
        for data_vertex in candidates.get(query_vertex, []):
            if not self._is_feasible(
                query_vertex=query_vertex,
                data_vertex=data_vertex,
                query_graph=query_graph,
                data_graph=data_graph,
                state=state,
                statistics=statistics,
            ):
                continue

            state.assign(query_vertex, data_vertex)
            statistics.record_partial_mapping()
            self._search(
                depth=depth + 1,
                query_graph=query_graph,
                data_graph=data_graph,
                candidates=candidates,
                vertex_order=vertex_order,
                state=state,
                statistics=statistics,
                results=results,
            )
            state.unassign(query_vertex)

    def _is_feasible(
        self,
        query_vertex: int,
        data_vertex: int,
        query_graph: LabeledGraph,
        data_graph: LabeledGraph,
        state: SearchState,
        statistics: MatchStatistics,
    ) -> bool:
        if state.is_data_vertex_used(data_vertex):
            statistics.record_prune('injectivity_conflict')
            return False

        for matched_neighbor in query_graph.neighbors(query_vertex):
            if not state.is_query_vertex_matched(matched_neighbor):
                continue
            mapped_neighbor = state.query_to_data[matched_neighbor]
            if not data_graph.has_edge(data_vertex, mapped_neighbor):
                statistics.record_prune('edge_conflict')
                return False

        return True
