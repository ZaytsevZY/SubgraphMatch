from __future__ import annotations

from itertools import combinations

from subgraph_match.filters.base import GuardContext
from subgraph_match.models import LabeledGraph


class ReservationGuard:
    """A lightweight precomputed reservation guard.

    For each candidate assignment (u, v), we inspect forward neighbors of u in
    the current matching order. If a small subset of those neighbors has a
    candidate-union whose size equals the subset size, that union must remain
    free in any valid extension because those vertices are already fully
    reserved by Hall-style injectivity reasoning.

    This is still a course-project simplification of GuP, but it is more
    faithful than the earlier on-the-fly forward-checking approximation.
    """

    name = 'reservation_guard'

    def __init__(self, size_limit: int = 3) -> None:
        self.size_limit = size_limit
        self._reservation_map: dict[tuple[int, int], tuple[int, ...]] = {}
        self._impossible_candidates: set[tuple[int, int]] = set()
        self._active_query_vertices: set[int] = set()

    def prepare(
        self,
        query_graph: LabeledGraph,
        data_graph: LabeledGraph,
        candidates: dict[int, list[int]],
        vertex_order: list[int],
    ) -> None:
        self._reservation_map.clear()
        self._impossible_candidates.clear()
        self._active_query_vertices.clear()

        position = {query_vertex: depth for depth, query_vertex in enumerate(vertex_order)}

        for query_vertex in vertex_order:
            forward_neighbors = sorted(
                neighbor
                for neighbor in query_graph.neighbors(query_vertex)
                if position[neighbor] > position[query_vertex]
            )
            if not forward_neighbors:
                continue

            for data_vertex in candidates.get(query_vertex, []):
                compatible_sets: dict[int, set[int]] = {}
                impossible = False
                for neighbor in forward_neighbors:
                    compatible = {
                        candidate
                        for candidate in candidates.get(neighbor, [])
                        if data_graph.has_edge(data_vertex, candidate)
                    }
                    if not compatible:
                        impossible = True
                        break
                    compatible_sets[neighbor] = compatible

                if impossible:
                    self._impossible_candidates.add((query_vertex, data_vertex))
                    self._active_query_vertices.add(query_vertex)
                    continue

                reservation = self._build_reservation_set(compatible_sets)
                if reservation:
                    self._reservation_map[(query_vertex, data_vertex)] = tuple(sorted(reservation))
                    self._active_query_vertices.add(query_vertex)

    def is_active(self, query_vertex: int) -> bool:
        return query_vertex in self._active_query_vertices

    def should_prune(self, context: GuardContext) -> str | None:
        candidate_key = (context.query_vertex, context.data_vertex)
        if candidate_key in self._impossible_candidates:
            return self.name

        reserved_vertices = self._reservation_map.get(candidate_key)
        if reserved_vertices is None:
            return None

        used_data_vertices = set(context.state.data_to_query)
        if any(vertex in used_data_vertices for vertex in reserved_vertices):
            return self.name

        return None

    def record_dead_end(self, context: GuardContext) -> None:
        return None

    def _build_reservation_set(self, compatible_sets: dict[int, set[int]]) -> set[int]:
        neighbors = list(compatible_sets)
        best: set[int] | None = None

        max_subset_size = min(self.size_limit, len(neighbors))
        for subset_size in range(1, max_subset_size + 1):
            for subset in combinations(neighbors, subset_size):
                union: set[int] = set()
                for neighbor in subset:
                    union.update(compatible_sets[neighbor])

                if len(union) != subset_size:
                    continue

                if best is None or len(union) < len(best):
                    best = set(union)

            if best is not None:
                break

        return best or set()
