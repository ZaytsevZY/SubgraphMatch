from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.config import GUPConfig
from subgraph_match.io import load_graph_from_edge_list
from subgraph_match.matchers import BacktrackingMatcher, GUPMatcher
from subgraph_match.models import LabeledGraph


def normalize_mappings(mappings: list[dict[int, int]]) -> set[tuple[tuple[int, int], ...]]:
    return {tuple(sorted(mapping.items())) for mapping in mappings}


def build_reservation_guard_case() -> tuple[LabeledGraph, LabeledGraph]:
    data_graph = LabeledGraph()
    data_graph.add_vertex(1, 'A')
    data_graph.add_vertex(2, 'B')
    data_graph.add_edge(1, 2)

    query_graph = LabeledGraph()
    query_graph.add_vertex(1, 'A')
    query_graph.add_vertex(2, 'B')
    query_graph.add_vertex(3, 'A')
    query_graph.add_edge(1, 2)
    query_graph.add_edge(2, 3)
    query_graph.add_edge(1, 3)
    return data_graph, query_graph


def build_nogood_guard_reuse_case() -> tuple[LabeledGraph, LabeledGraph]:
    data_graph = LabeledGraph()

    # Component 1: two automorphic matches that use the same vertex set {1, 2, 3}.
    data_graph.add_vertex(1, 'A')
    data_graph.add_vertex(2, 'B')
    data_graph.add_vertex(3, 'A')
    data_graph.add_edge(1, 2)
    data_graph.add_edge(2, 3)
    data_graph.add_edge(1, 3)

    # Component 2: a path of X-labeled vertices that cannot satisfy a triangle query.
    data_graph.add_vertex(4, 'X')
    data_graph.add_vertex(5, 'X')
    data_graph.add_vertex(6, 'X')
    data_graph.add_edge(4, 5)
    data_graph.add_edge(5, 6)

    query_graph = LabeledGraph()
    query_graph.add_vertex(1, 'A')
    query_graph.add_vertex(2, 'B')
    query_graph.add_vertex(3, 'A')
    query_graph.add_edge(1, 2)
    query_graph.add_edge(2, 3)

    query_graph.add_vertex(4, 'X')
    query_graph.add_vertex(5, 'X')
    query_graph.add_vertex(6, 'X')
    query_graph.add_edge(4, 5)
    query_graph.add_edge(5, 6)
    query_graph.add_edge(4, 6)
    return data_graph, query_graph


class GUPMatcherTest(unittest.TestCase):
    def test_guards_off_matches_baseline_on_toy_query(self) -> None:
        data_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        query_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_query_path.txt')

        baseline = BacktrackingMatcher().match(query_graph=query_graph, data_graph=data_graph)
        gup = GUPMatcher(GUPConfig(enable_reservation_guard=False, enable_nogood_guard=False)).match(
            query_graph=query_graph,
            data_graph=data_graph,
        )

        self.assertEqual(normalize_mappings(gup.mappings), normalize_mappings(baseline.mappings))
        self.assertEqual(gup.statistics.result_mappings, baseline.statistics.result_mappings)
        self.assertEqual(gup.statistics.partial_mappings, baseline.statistics.partial_mappings)
        self.assertEqual(gup.statistics.pruned_partial_mappings, baseline.statistics.pruned_partial_mappings)
        self.assertEqual(gup.statistics.guard_checks_total, 0)

    def test_all_guards_preserve_results_on_toy_query(self) -> None:
        data_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        query_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_query_path.txt')

        baseline = BacktrackingMatcher().match(query_graph=query_graph, data_graph=data_graph)
        gup = GUPMatcher().match(query_graph=query_graph, data_graph=data_graph)

        self.assertEqual(normalize_mappings(gup.mappings), normalize_mappings(baseline.mappings))
        self.assertEqual(gup.statistics.result_mappings, baseline.statistics.result_mappings)
        self.assertGreater(gup.statistics.guard_checks_total, 0)

    def test_reservation_guard_prunes_earlier_on_dead_end_case(self) -> None:
        data_graph, query_graph = build_reservation_guard_case()

        baseline = BacktrackingMatcher().match(query_graph=query_graph, data_graph=data_graph)
        gup = GUPMatcher(GUPConfig(enable_reservation_guard=True, enable_nogood_guard=False)).match(
            query_graph=query_graph,
            data_graph=data_graph,
        )

        self.assertEqual(baseline.statistics.result_mappings, 0)
        self.assertEqual(gup.statistics.result_mappings, 0)
        self.assertLessEqual(gup.statistics.partial_mappings, baseline.statistics.partial_mappings)

    def test_nogood_guard_configuration_preserves_results(self) -> None:
        data_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        query_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_query_path.txt')

        baseline = BacktrackingMatcher().match(query_graph=query_graph, data_graph=data_graph)
        gup = GUPMatcher(GUPConfig(enable_reservation_guard=False, enable_nogood_guard=True)).match(
            query_graph=query_graph,
            data_graph=data_graph,
        )

        self.assertEqual(normalize_mappings(gup.mappings), normalize_mappings(baseline.mappings))
        self.assertEqual(gup.statistics.result_mappings, baseline.statistics.result_mappings)
        self.assertGreater(gup.statistics.guard_checks_total, 0)

    def test_nogood_guard_reuses_dead_end_subproblem(self) -> None:
        data_graph, query_graph = build_nogood_guard_reuse_case()

        baseline = BacktrackingMatcher().match(query_graph=query_graph, data_graph=data_graph)
        gup = GUPMatcher(GUPConfig(enable_reservation_guard=False, enable_nogood_guard=True)).match(
            query_graph=query_graph,
            data_graph=data_graph,
        )

        self.assertEqual(baseline.statistics.result_mappings, 0)
        self.assertEqual(gup.statistics.result_mappings, 0)
        self.assertLessEqual(gup.statistics.partial_mappings, baseline.statistics.partial_mappings)


if __name__ == '__main__':
    unittest.main()
