from itertools import combinations
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.dynamic import (
    apply_edge_deletion,
    apply_edge_insertion,
    enumerate_embeddings_using_edge,
    maintain_result_on_edge_change,
)
from subgraph_match.io import load_graph_from_edge_list
from subgraph_match.matchers import BacktrackingMatcher
from subgraph_match.models import LabeledGraph


def normalize_mappings(mappings) -> set:
    return {tuple(sorted(mapping.items())) for mapping in mappings}


def build_toy_path_query() -> LabeledGraph:
    query = LabeledGraph()
    query.add_vertex(1, 'A')
    query.add_vertex(2, 'B')
    query.add_vertex(3, 'A')
    query.add_edge(1, 2)
    query.add_edge(2, 3)
    return query


def build_gadget_graph() -> LabeledGraph:
    """Two small A-B-C gadgets; small enough for an exhaustive edge sweep."""
    graph = LabeledGraph()
    next_id = 0

    def add(label: str) -> int:
        nonlocal next_id
        graph.add_vertex(next_id, label)
        next_id += 1
        return next_id - 1

    for _ in range(2):
        hub = add('A')
        for _ in range(2):
            b_vertex = add('B')
            graph.add_edge(hub, b_vertex)
            for _ in range(2):
                c_vertex = add('C')
                graph.add_edge(b_vertex, c_vertex)
    return graph


def build_abc_path_query() -> LabeledGraph:
    query = LabeledGraph()
    query.add_vertex(0, 'A')
    query.add_vertex(1, 'B')
    query.add_vertex(2, 'C')
    query.add_edge(0, 1)
    query.add_edge(1, 2)
    return query


class EdgeUpdateTest(unittest.TestCase):
    def test_insertion_does_not_mutate_original(self) -> None:
        graph = build_gadget_graph()
        edges_before = graph.num_edges
        # vertices 0 (A) and 1 (B) are already adjacent; pick a non-edge instead.
        new_graph = apply_edge_insertion(graph, 0, 5)
        self.assertEqual(graph.num_edges, edges_before)
        self.assertTrue(new_graph.has_edge(0, 5))
        self.assertFalse(graph.has_edge(0, 5))

    def test_insertion_rejects_existing_edge(self) -> None:
        graph = build_gadget_graph()
        with self.assertRaises(ValueError):
            apply_edge_insertion(graph, 0, 1)

    def test_deletion_rejects_missing_edge(self) -> None:
        graph = build_gadget_graph()
        with self.assertRaises(ValueError):
            apply_edge_deletion(graph, 0, 5)

    def test_self_loop_rejected(self) -> None:
        graph = build_gadget_graph()
        with self.assertRaises(ValueError):
            apply_edge_insertion(graph, 0, 0)


class EnumerateUsingEdgeTest(unittest.TestCase):
    def test_toy_deletion_affected_set(self) -> None:
        data_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        query = build_toy_path_query()
        # Edge (2,3) carries label pair (B,A); it is used by some A-B-A path matches.
        affected, counters = enumerate_embeddings_using_edge(query, data_graph, (2, 3))
        matcher = BacktrackingMatcher()
        scratch_with = normalize_mappings(matcher.match(query, data_graph).mappings)
        scratch_without = normalize_mappings(
            matcher.match(query, apply_edge_deletion(data_graph, 2, 3)).mappings
        )
        self.assertEqual(normalize_mappings(affected), scratch_with - scratch_without)
        self.assertGreater(counters['anchors'], 0)

    def test_label_incompatible_edge_is_noop(self) -> None:
        graph = build_gadget_graph()
        query = build_abc_path_query()
        # Find a C-C non-edge: no query edge has the label pair (C, C), so no
        # result mapping can ever use it.
        c_vertices = [v for v, label in graph.labels.items() if label == 'C']
        u, v = c_vertices[0], c_vertices[1]
        self.assertFalse(graph.has_edge(u, v))
        with_edge = apply_edge_insertion(graph, u, v)
        affected, _ = enumerate_embeddings_using_edge(query, with_edge, (u, v))
        self.assertEqual(affected, [])


class IncrementalMatchesScratchTest(unittest.TestCase):
    def assert_matches_scratch(self, query, base_graph, edge, change_type) -> None:
        matcher = BacktrackingMatcher()
        prev = matcher.match(query, base_graph).mappings
        maintenance, new_graph = maintain_result_on_edge_change(
            query, base_graph, prev, edge, change_type
        )
        scratch = normalize_mappings(matcher.match(query, new_graph).mappings)
        prev_keys = normalize_mappings(prev)

        self.assertEqual(normalize_mappings(maintenance.new_result), scratch)
        self.assertEqual(normalize_mappings(maintenance.added_mappings), scratch - prev_keys)
        self.assertEqual(normalize_mappings(maintenance.removed_mappings), prev_keys - scratch)
        # Monotonicity: insertion never removes, deletion never adds.
        if change_type == 'insert':
            self.assertEqual(maintenance.removed_count, 0)
        else:
            self.assertEqual(maintenance.added_count, 0)

    def _exhaustive_sweep(self, query, graph) -> None:
        existing = [(u, v) for u in graph.vertices for v in graph.neighbors(u) if u < v]
        for edge in existing:
            self.assert_matches_scratch(query, graph, edge, 'delete')

        for u, v in combinations(graph.vertices, 2):
            if graph.has_edge(u, v):
                continue
            self.assert_matches_scratch(query, graph, (u, v), 'insert')

    def test_toy_exhaustive(self) -> None:
        data_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        self._exhaustive_sweep(build_toy_path_query(), data_graph)

    def test_gadget_exhaustive(self) -> None:
        self._exhaustive_sweep(build_abc_path_query(), build_gadget_graph())

    def test_insert_is_inverse_of_delete(self) -> None:
        graph = build_gadget_graph()
        query = build_abc_path_query()
        matcher = BacktrackingMatcher()
        full = normalize_mappings(matcher.match(query, graph).mappings)

        # Delete a used A-B edge, then insert it back; the added set on insertion
        # must equal the removed set on deletion.
        edge = (0, 1)  # hub A (0) -- B (1)
        self.assertTrue(graph.has_edge(*edge))

        prev_full = matcher.match(query, graph).mappings
        del_maint, reduced_graph = maintain_result_on_edge_change(
            query, graph, prev_full, edge, 'delete'
        )

        prev_reduced = matcher.match(query, reduced_graph).mappings
        ins_maint, restored_graph = maintain_result_on_edge_change(
            query, reduced_graph, prev_reduced, edge, 'insert'
        )

        self.assertEqual(
            normalize_mappings(del_maint.removed_mappings),
            normalize_mappings(ins_maint.added_mappings),
        )
        self.assertEqual(normalize_mappings(ins_maint.new_result), full)


if __name__ == '__main__':
    unittest.main()
