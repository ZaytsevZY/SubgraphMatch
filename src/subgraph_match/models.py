from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set


@dataclass
class LabeledGraph:
    """Simple in-memory labeled undirected graph representation."""

    adjacency: Dict[int, Set[int]] = field(default_factory=dict)
    labels: Dict[int, str] = field(default_factory=dict)

    def add_vertex(self, vertex_id: int, label: str) -> None:
        self.labels[vertex_id] = label
        self.adjacency.setdefault(vertex_id, set())

    def add_edge(self, source: int, target: int) -> None:
        if source == target:
            raise ValueError('Self-loops are not supported in the current baseline graph model.')
        self.adjacency.setdefault(source, set()).add(target)
        self.adjacency.setdefault(target, set()).add(source)

    @property
    def num_vertices(self) -> int:
        return len(self.labels)

    @property
    def num_edges(self) -> int:
        return sum(len(neighbors) for neighbors in self.adjacency.values()) // 2

    @property
    def vertices(self) -> List[int]:
        return sorted(self.labels)

    def neighbors(self, vertex_id: int) -> Set[int]:
        return self.adjacency.get(vertex_id, set())

    def degree(self, vertex_id: int) -> int:
        return len(self.neighbors(vertex_id))

    def has_edge(self, source: int, target: int) -> bool:
        return target in self.adjacency.get(source, set())

    def vertices_with_label(self, label: str) -> List[int]:
        return [vertex_id for vertex_id, vertex_label in self.labels.items() if vertex_label == label]

    def induced_labels(self, vertices: Iterable[int]) -> Dict[int, str]:
        return {vertex_id: self.labels[vertex_id] for vertex_id in vertices}
