"""Dynamic single-edge maintenance of subgraph-matching results (optional task 6).

When the data graph changes by inserting or deleting exactly one edge, we
incrementally maintain the set of result mappings instead of recomputing it from
scratch, and report the exact result difference (added / removed mappings)
caused by the change.
"""

from subgraph_match.dynamic.dynamic_metrics import DynamicMaintenanceResult
from subgraph_match.dynamic.edge_update import (
    apply_edge_deletion,
    apply_edge_insertion,
    clone_graph,
)
from subgraph_match.dynamic.incremental import (
    enumerate_embeddings_using_edge,
    maintain_result_on_edge_change,
)

__all__ = [
    'DynamicMaintenanceResult',
    'apply_edge_deletion',
    'apply_edge_insertion',
    'clone_graph',
    'enumerate_embeddings_using_edge',
    'maintain_result_on_edge_change',
]
