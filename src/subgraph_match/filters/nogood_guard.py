from __future__ import annotations

from subgraph_match.filters.base import GuardContext


class NogoodGuard:
    """A conservative subproblem memo for the course-project GUP-lite matcher.

    The guard stores dead-end signatures for the *future subproblem* after a
    candidate extension is applied. The signature keeps:
    - the current search depth,
    - the used data-vertex set after the extension, and
    - the mapped frontier vertices that still constrain the remaining search.

    The current query vertex and candidate are intentionally omitted: under the
    fixed matching order they are already represented by the depth, used set,
    and frontier mapping. If two prefixes induce the same values for those
    fields, the remaining completion problem is identical.
    """

    name = 'nogood_guard'
    learns_from_dead_ends = True

    def __init__(self) -> None:
        self._dead_end_signatures: set[
            tuple[int, tuple[int, ...], tuple[tuple[int, int], ...]]
        ] = set()
        self._active_query_vertices: set[int] = set()

    def should_prune(self, context: GuardContext) -> str | None:
        if self._build_signature(context) in self._dead_end_signatures:
            return self.name
        return None

    def record_dead_end(self, context: GuardContext) -> None:
        self._dead_end_signatures.add(self._build_signature(context))
        self._active_query_vertices.add(context.query_vertex)

    def is_active(self, query_vertex: int) -> bool:
        return query_vertex in self._active_query_vertices

    def _build_signature(
        self,
        context: GuardContext,
    ) -> tuple[int, tuple[int, ...], tuple[tuple[int, int], ...]]:
        hypothetical_mapping = dict(context.state.query_to_data)
        hypothetical_mapping[context.query_vertex] = context.data_vertex

        hypothetical_used_vertices = tuple(sorted(hypothetical_mapping.values()))
        remaining_query_vertices = set(context.vertex_order[context.depth + 1 :])

        frontier_mapping: list[tuple[int, int]] = []
        for query_vertex, data_vertex in hypothetical_mapping.items():
            if any(neighbor in remaining_query_vertices for neighbor in context.query_graph.neighbors(query_vertex)):
                frontier_mapping.append((query_vertex, data_vertex))

        return (
            context.depth,
            hypothetical_used_vertices,
            tuple(sorted(frontier_mapping)),
        )
