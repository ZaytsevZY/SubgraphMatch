from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.io import load_graph_from_edge_list
from subgraph_match.matchers import BacktrackingMatcher
from subgraph_match.models import LabeledGraph
from subgraph_match.reuse import find_single_added_edge, filter_mappings_by_added_edge


def normalize_mappings(mappings: list[dict[int, int]]) -> set[tuple[tuple[int, int], ...]]:
    return {tuple(sorted(mapping.items())) for mapping in mappings}


def build_prev_query() -> LabeledGraph:
    query = LabeledGraph()
    query.add_vertex(1, 'A')
    query.add_vertex(2, 'B')
    query.add_vertex(3, 'A')
    query.add_edge(1, 2)
    query.add_edge(2, 3)
    return query


def build_next_query() -> LabeledGraph:
    query = build_prev_query()
    query.add_edge(1, 3)
    return query


def build_invalid_query_extra_vertex() -> LabeledGraph:
    query = build_prev_query()
    query.add_vertex(4, 'C')
    query.add_edge(1, 3)
    return query


def build_invalid_query_label_change() -> LabeledGraph:
    query = LabeledGraph()
    query.add_vertex(1, 'A')
    query.add_vertex(2, 'B')
    query.add_vertex(3, 'C')
    query.add_edge(1, 2)
    query.add_edge(2, 3)
    query.add_edge(1, 3)
    return query


def build_invalid_query_two_added_edges() -> LabeledGraph:
    query = build_prev_query()
    query.add_edge(1, 3)
    query.add_vertex(4, 'A')
    query.add_edge(3, 4)
    return query


class ResultReuseTest(unittest.TestCase):
    def test_find_single_added_edge(self) -> None:
        prev_query = build_prev_query()
        next_query = build_next_query()

        added_edge = find_single_added_edge(prev_query, next_query)
        self.assertEqual(added_edge, (1, 3))

    def test_find_single_added_edge_rejects_extra_vertex(self) -> None:
        prev_query = build_prev_query()
        invalid_query = build_invalid_query_extra_vertex()

        added_edge = find_single_added_edge(prev_query, invalid_query)
        self.assertIsNone(added_edge)

    def test_find_single_added_edge_rejects_label_change(self) -> None:
        prev_query = build_prev_query()
        invalid_query = build_invalid_query_label_change()

        added_edge = find_single_added_edge(prev_query, invalid_query)
        self.assertIsNone(added_edge)

    def test_find_single_added_edge_rejects_multiple_changes(self) -> None:
        prev_query = build_prev_query()
        invalid_query = build_invalid_query_two_added_edges()

        added_edge = find_single_added_edge(prev_query, invalid_query)
        self.assertIsNone(added_edge)

    def test_reuse_matches_scratch_results(self) -> None:
        data_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        prev_query = build_prev_query()
        next_query = build_next_query()

        matcher = BacktrackingMatcher()
        prev_result = matcher.match(query_graph=prev_query, data_graph=data_graph)

        added_edge = find_single_added_edge(prev_query, next_query)
        self.assertIsNotNone(added_edge)

        reuse_result = filter_mappings_by_added_edge(
            data_graph=data_graph,
            prev_mappings=prev_result.mappings,
            added_edge=added_edge,
        )
        scratch_result = matcher.match(query_graph=next_query, data_graph=data_graph)

        self.assertEqual(
            normalize_mappings(reuse_result.reused_mappings),
            normalize_mappings(scratch_result.mappings),
        )

    def test_reuse_result_count_is_not_larger_than_source(self) -> None:
        data_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        prev_query = build_prev_query()
        next_query = build_next_query()

        matcher = BacktrackingMatcher()
        prev_result = matcher.match(query_graph=prev_query, data_graph=data_graph)

        added_edge = find_single_added_edge(prev_query, next_query)
        self.assertIsNotNone(added_edge)

        reuse_result = filter_mappings_by_added_edge(
            data_graph=data_graph,
            prev_mappings=prev_result.mappings,
            added_edge=added_edge,
        )

        self.assertLessEqual(reuse_result.survived_results, reuse_result.source_results)
        self.assertEqual(
            reuse_result.filtered_results,
            reuse_result.source_results - reuse_result.survived_results,
        )


if __name__ == '__main__':
    unittest.main()
