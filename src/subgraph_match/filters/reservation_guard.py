from __future__ import annotations

from subgraph_match.filters.base import GuardContext


class ReservationGuard:
    """A lightweight forward-checking approximation of the GUP reservation guard."""

    name = 'reservation_guard'

    def should_prune(self, context: GuardContext) -> str | None:
        used_data_vertices = set(context.state.data_to_query)
        used_data_vertices.add(context.data_vertex)

        for neighbor in context.query_graph.neighbors(context.query_vertex):
            if context.state.is_query_vertex_matched(neighbor):
                continue
            if self._has_future_candidate(neighbor, context, used_data_vertices):
                continue
            return self.name

        return None

    def record_dead_end(self, context: GuardContext) -> None:
        return None

    def _has_future_candidate(
        self,
        future_query_vertex: int,
        context: GuardContext,
        used_data_vertices: set[int],
    ) -> bool:
        for candidate in context.candidates.get(future_query_vertex, []):
            if candidate in used_data_vertices:
                continue
            if self._respects_matched_neighbors(future_query_vertex, candidate, context):
                return True
        return False

    def _respects_matched_neighbors(
        self,
        future_query_vertex: int,
        candidate: int,
        context: GuardContext,
    ) -> bool:
        for matched_neighbor in context.query_graph.neighbors(future_query_vertex):
            if matched_neighbor == context.query_vertex:
                if not context.data_graph.has_edge(candidate, context.data_vertex):
                    return False
                continue

            if not context.state.is_query_vertex_matched(matched_neighbor):
                continue
            mapped_neighbor = context.state.query_to_data[matched_neighbor]
            if not context.data_graph.has_edge(candidate, mapped_neighbor):
                return False
        return True