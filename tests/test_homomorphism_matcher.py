from itertools import product
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.homomorphism import HomomorphismMatcher
from subgraph_match.io import load_graph_from_edge_list
from subgraph_match.matchers import BacktrackingMatcher
from subgraph_match.models import LabeledGraph


def normalize_mappings(mappings) -> set:
    return {tuple(sorted(mapping.items())) for mapping in mappings}


def query_edges(query: LabeledGraph):
    return [(u, v) for u in query.vertices for v in query.neighbors(u) if u < v]


def brute_force_homomorphisms(query: LabeledGraph, data: LabeledGraph):
    """Independent oracle: enumerate every label-preserving map and test E_G^+."""
    q_vertices = query.vertices
    candidates = {
        q: [d for d in data.vertices if data.labels[d] == query.labels[q]] for q in q_vertices
    }
    edges = query_edges(query)
    results = []
    for combo in product(*[candidates[q] for q in q_vertices]):
        mapping = dict(zip(q_vertices, combo))
        ok = True
        for u, v in edges:
            f_u, f_v = mapping[u], mapping[v]
            if f_u == f_v:
                continue  # self-loop in E_G^+
            if not data.has_edge(f_u, f_v):
                ok = False
                break
        if ok:
            results.append(mapping)
    return results


def build_aa_edge_query() -> LabeledGraph:
    query = LabeledGraph()
    query.add_vertex(0, 'A')
    query.add_vertex(1, 'A')
    query.add_edge(0, 1)
    return query


def build_clique(label: str, size: int) -> LabeledGraph:
    graph = LabeledGraph()
    for vertex in range(size):
        graph.add_vertex(vertex, label)
    for i in range(size):
        for j in range(i + 1, size):
            graph.add_edge(i, j)
    return graph


def build_triangle_query() -> LabeledGraph:
    query = LabeledGraph()
    for vertex in range(3):
        query.add_vertex(vertex, 'A')
    query.add_edge(0, 1)
    query.add_edge(1, 2)
    query.add_edge(0, 2)
    return query


class HomomorphismMatcherTest(unittest.TestCase):
    def assert_matches_oracle(self, query, data) -> None:
        hom = HomomorphismMatcher().match(query, data)
        oracle = brute_force_homomorphisms(query, data)
        self.assertEqual(normalize_mappings(hom.mappings), normalize_mappings(oracle))

    def assert_injective_equals_iso(self, query, data) -> None:
        hom = HomomorphismMatcher().match(query, data)
        iso = BacktrackingMatcher().match(query, data)
        injective = [m for m in hom.mappings if len(set(m.values())) == len(m)]
        self.assertEqual(normalize_mappings(injective), normalize_mappings(iso.mappings))
        # Homomorphisms are a superset of isomorphisms.
        self.assertTrue(
            normalize_mappings(iso.mappings).issubset(normalize_mappings(hom.mappings))
        )

    def test_toy_aa_query_matches_oracle(self) -> None:
        data = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        query = build_aa_edge_query()
        self.assert_matches_oracle(query, data)

    def test_toy_aa_query_counts(self) -> None:
        # Toy graph has A vertices {1, 3} with the single A-A edge (1, 3).
        data = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        query = build_aa_edge_query()
        hom = HomomorphismMatcher().match(query, data)
        iso = BacktrackingMatcher().match(query, data)
        # Iso: (1->1,1->3) and (0->3,1->1) i.e. the two ordered distinct adjacent A pairs.
        self.assertEqual(len(iso.mappings), 2)
        # Hom adds the two self-loop collapses (both query vertices to vertex 1, or to 3).
        self.assertEqual(len(hom.mappings), 4)
        self.assert_injective_equals_iso(query, data)

    def test_self_loop_collapse_without_edge(self) -> None:
        # Two A vertices with NO A-A edge: no isomorphism, but two collapses exist.
        data = LabeledGraph()
        data.add_vertex(0, 'A')
        data.add_vertex(1, 'A')
        query = build_aa_edge_query()

        hom = HomomorphismMatcher().match(query, data)
        iso = BacktrackingMatcher().match(query, data)
        self.assertEqual(len(iso.mappings), 0)
        self.assertEqual(
            normalize_mappings(hom.mappings),
            normalize_mappings([{0: 0, 1: 0}, {0: 1, 1: 1}]),
        )

    def test_triangle_on_clique_counts(self) -> None:
        for size in (3, 4, 6):
            data = build_clique('A', size)
            query = build_triangle_query()
            hom = HomomorphismMatcher().match(query, data)
            iso = BacktrackingMatcher().match(query, data)
            self.assertEqual(len(hom.mappings), size ** 3)
            self.assertEqual(len(iso.mappings), size * (size - 1) * (size - 2))
            self.assert_matches_oracle(query, data)
            self.assert_injective_equals_iso(query, data)

    def test_isolated_vertex_high_degree_query(self) -> None:
        # A single isolated A vertex must still host the whole triangle via
        # self-loops (degree filtering would wrongly reject this).
        data = LabeledGraph()
        data.add_vertex(0, 'A')
        query = build_triangle_query()
        hom = HomomorphismMatcher().match(query, data)
        self.assertEqual(normalize_mappings(hom.mappings), normalize_mappings([{0: 0, 1: 0, 2: 0}]))

    def test_empty_query_yields_empty_homomorphism(self) -> None:
        # The empty query has one (vacuous) homomorphism: the empty map.
        data = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        hom = HomomorphismMatcher().match(LabeledGraph(), data)
        self.assertEqual(hom.mappings, [{}])

    def test_exhaustive_small_queries(self) -> None:
        data = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        queries = [build_aa_edge_query(), build_triangle_query()]
        # Also a mixed-label path A-B-A.
        path = LabeledGraph()
        path.add_vertex(0, 'A')
        path.add_vertex(1, 'B')
        path.add_vertex(2, 'A')
        path.add_edge(0, 1)
        path.add_edge(1, 2)
        queries.append(path)
        for query in queries:
            self.assert_matches_oracle(query, data)
            self.assert_injective_equals_iso(query, data)


if __name__ == '__main__':
    unittest.main()
