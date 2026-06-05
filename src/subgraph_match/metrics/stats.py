from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MatchStatistics:
    partial_mappings: int = 0
    result_mappings: int = 0
    pruned_partial_mappings: int = 0
    guard_checks_total: int = 0
    prune_reasons: Dict[str, int] = field(default_factory=dict)
    vertex_order: List[int] = field(default_factory=list)
    runtime_ms: float = 0.0

    def record_partial_mapping(self) -> None:
        self.partial_mappings += 1

    def record_result_mapping(self) -> None:
        self.result_mappings += 1

    def record_guard_check(self) -> None:
        self.guard_checks_total += 1

    def record_prune(self, reason: str) -> None:
        self.pruned_partial_mappings += 1
        self.prune_reasons[reason] = self.prune_reasons.get(reason, 0) + 1

    def to_dict(self) -> Dict[str, object]:
        return {
            'partial_mappings': self.partial_mappings,
            'result_mappings': self.result_mappings,
            'pruned_partial_mappings': self.pruned_partial_mappings,
            'guard_checks_total': self.guard_checks_total,
            'prune_reasons': dict(sorted(self.prune_reasons.items())),
            'vertex_order': list(self.vertex_order),
            'runtime_ms': self.runtime_ms,
        }