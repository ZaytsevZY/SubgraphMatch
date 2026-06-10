"""Subgraph homomorphism matching (optional task 7).

Subgraph homomorphism relaxes subgraph isomorphism in two ways: the mapping
need not be injective, and the edge constraint is evaluated over
``E_G^+ = E_G ∪ {(w, w) : w ∈ V_G}`` instead of ``E_G``. Concretely, a query
edge ``(u, v)`` is satisfied iff ``f(u) == f(v)`` (a self-loop in ``E_G^+``) or
``(f(u), f(v))`` is an edge of ``G``.
"""

from subgraph_match.homomorphism.homomorphism_matcher import (
    HomomorphismMatcher,
    build_label_only_candidates,
)

__all__ = ['HomomorphismMatcher', 'build_label_only_candidates']
