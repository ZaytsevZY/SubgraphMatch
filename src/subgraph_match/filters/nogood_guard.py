from __future__ import annotations

from subgraph_match.filters.base import GuardContext


class NogoodGuard:
    """A conservative subproblem memo for the course-project GUP-lite matcher.

    The guard stores dead-end signatures for the *future subproblem* after a
    candidate extension is applied. The signature keeps:
    - the current search depth / extension identity,
    - the used data-vertex set after the extension, and
    - the mapped frontier vertices that still constrain the remaining search.

    This is more reusable than an exact-prefix memo while remaining safe for the
    current fixed-order DFS: if two prefixes induce the same frontier mapping and
    the same used-vertex set, the remaining completion problem is identical.
    """

    name = 'nogood_guard'

    def __init__(self) -> None:
        self._dead_end_signatures: set[
            tuple[int, int, int, tuple[int, ...], tuple[tuple[int, int], ...]]
        ] = set()

    def should_prune(self, context: GuardContext) -> str | None:
        if self._build_signature(context) in self._dead_end_signatures:
            return self.name
        return None

    def record_dead_end(self, context: GuardContext) -> None:
        self._dead_end_signatures.add(self._build_signature(context))

    def _build_signature(
        self,
        context: GuardContext,
    ) -> tuple[int, int, int, tuple[int, ...], tuple[tuple[int, int], ...]]:
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
            context.query_vertex,
            context.data_vertex,
            hypothetical_used_vertices,
            tuple(sorted(frontier_mapping)),
        )
