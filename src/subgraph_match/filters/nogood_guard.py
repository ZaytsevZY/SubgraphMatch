from __future__ import annotations

from subgraph_match.filters.base import GuardContext


class NogoodGuard:
    """A conservative dead-end memo used as the first GUP-lite nogood guard."""

    name = 'nogood_guard'

    def __init__(self) -> None:
        self._dead_end_signatures: set[tuple[tuple[tuple[int, int], ...], int, int]] = set()

    def should_prune(self, context: GuardContext) -> str | None:
        if self._build_signature(context) in self._dead_end_signatures:
            return self.name
        return None

    def record_dead_end(self, context: GuardContext) -> None:
        self._dead_end_signatures.add(self._build_signature(context))

    def _build_signature(self, context: GuardContext) -> tuple[tuple[tuple[int, int], ...], int, int]:
        # The first version intentionally keys the nogood on the exact prefix
        # state to preserve correctness while keeping the API extensible.
        prefix = tuple(sorted(context.state.query_to_data.items()))
        return prefix, context.query_vertex, context.data_vertex