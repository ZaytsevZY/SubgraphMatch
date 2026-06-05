from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class SearchState:
    query_to_data: Dict[int, int] = field(default_factory=dict)
    data_to_query: Dict[int, int] = field(default_factory=dict)

    def is_query_vertex_matched(self, query_vertex: int) -> bool:
        return query_vertex in self.query_to_data

    def is_data_vertex_used(self, data_vertex: int) -> bool:
        return data_vertex in self.data_to_query

    def assign(self, query_vertex: int, data_vertex: int) -> None:
        self.query_to_data[query_vertex] = data_vertex
        self.data_to_query[data_vertex] = query_vertex

    def unassign(self, query_vertex: int) -> None:
        data_vertex = self.query_to_data.pop(query_vertex)
        self.data_to_query.pop(data_vertex, None)

    def copy_mapping(self) -> Dict[int, int]:
        return dict(self.query_to_data)
