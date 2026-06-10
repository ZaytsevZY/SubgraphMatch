from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

Mapping = Dict[int, int]


@dataclass
class DynamicMaintenanceResult:
    """Outcome of incrementally maintaining result mappings under one edge change."""

    change_type: str  # 'insert' or 'delete'
    changed_edge: Tuple[int, int]
    prev_result_mappings: int
    new_result_mappings: int
    added_mappings: List[Mapping] = field(default_factory=list)
    removed_mappings: List[Mapping] = field(default_factory=list)
    new_result: List[Mapping] = field(default_factory=list)
    anchored_partial_mappings: int = 0  # partial extensions explored by the anchored search
    anchored_attempts: int = 0  # number of (query-edge x orientation) anchors enumerated
    incremental_runtime_ms: float = 0.0

    @property
    def added_count(self) -> int:
        return len(self.added_mappings)

    @property
    def removed_count(self) -> int:
        return len(self.removed_mappings)

    def to_dict(self) -> Dict[str, object]:
        return {
            'change_type': self.change_type,
            'changed_edge': list(self.changed_edge),
            'prev_result_mappings': self.prev_result_mappings,
            'new_result_mappings': self.new_result_mappings,
            'added_mappings': self.added_count,
            'removed_mappings': self.removed_count,
            'anchored_partial_mappings': self.anchored_partial_mappings,
            'anchored_attempts': self.anchored_attempts,
            'incremental_runtime_ms': self.incremental_runtime_ms,
        }
