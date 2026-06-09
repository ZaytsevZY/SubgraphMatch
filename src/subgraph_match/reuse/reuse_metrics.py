from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ReuseResult:
    reused_mappings: List[Dict[int, int]]
    source_results: int
    survived_results: int
    filtered_results: int
    reuse_runtime_ms: float

    def to_dict(self) -> Dict[str, object]:
        return {
            'source_results': self.source_results,
            'survived_results': self.survived_results,
            'filtered_results': self.filtered_results,
            'reuse_runtime_ms': self.reuse_runtime_ms,
        }
