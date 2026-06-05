from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol

from subgraph_match.matching.state import SearchState
from subgraph_match.models import LabeledGraph


CandidateMap = Dict[int, List[int]]


@dataclass(frozen=True)
class GuardContext:
    query_vertex: int
    data_vertex: int
    depth: int
    query_graph: LabeledGraph
    data_graph: LabeledGraph
    candidates: CandidateMap
    vertex_order: List[int]
    state: SearchState


class SearchGuard(Protocol):
    name: str

    def should_prune(self, context: GuardContext) -> Optional[str]:
        ...

    def record_dead_end(self, context: GuardContext) -> None:
        ...