from pathlib import Path
import random
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

    # Component 1: an A-A edge has two automorphic embeddings that use the same
    # data-vertex set. Once this disconnected component is complete, those two
    # histories induce the same future subproblem.
    data_graph.add_vertex(1, 'A')
    data_graph.add_vertex(2, 'A')
    data_graph.add_edge(1, 2)

    # Component 2: a 4-cycle cannot satisfy an X-X-X triangle query, but every
    # X vertex survives the label+degree candidate filter.
    for vertex in range(3, 7):
        data_graph.add_vertex(vertex, 'X')
    data_graph.add_edge(3, 4)
    data_graph.add_edge(4, 5)
    data_graph.add_edge(5, 6)
    data_graph.add_edge(6, 3)

    query_graph = LabeledGraph()
    query_graph.add_vertex(1, 'A')
    query_graph.add_vertex(2, 'A')
    query_graph.add_edge(1, 2)

    query_graph.add_vertex(3, 'X')
    query_graph.add_vertex(4, 'X')
    query_graph.add_vertex(5, 'X')
    query_graph.add_edge(3, 4)
    query_graph.add_edge(4, 5)
    query_graph.add_edge(3, 5)
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
        self.assertGreaterEqual(gup.statistics.guard_checks_total, 0)

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
        self.assertGreaterEqual(gup.statistics.guard_checks_total, 0)

    def test_nogood_guard_reuses_dead_end_subproblem(self) -> None:
        data_graph, query_graph = build_nogood_guard_reuse_case()

        baseline = BacktrackingMatcher().match(query_graph=query_graph, data_graph=data_graph)
        gup = GUPMatcher(GUPConfig(enable_reservation_guard=False, enable_nogood_guard=True)).match(
            query_graph=query_graph,
            data_graph=data_graph,
        )

        self.assertEqual(baseline.statistics.result_mappings, 0)
        self.assertEqual(gup.statistics.result_mappings, 0)
        self.assertLess(gup.statistics.partial_mappings, baseline.statistics.partial_mappings)
        self.assertGreater(gup.statistics.guard_checks_total, 0)
        self.assertGreater(gup.statistics.prune_reasons.get('nogood_guard', 0), 0)

    def test_nogood_matches_baseline_on_deterministic_random_graphs(self) -> None:
        rng = random.Random(20260610)

        for _ in range(40):
            data_graph = LabeledGraph()
            query_graph = LabeledGraph()

            for vertex in range(7):
                data_graph.add_vertex(vertex, rng.choice(('A', 'B')))
            for source in range(7):
                for target in range(source + 1, 7):
                    if rng.random() < 0.35:
                        data_graph.add_edge(source, target)

            for vertex in range(4):
                query_graph.add_vertex(vertex, rng.choice(('A', 'B')))
            for source in range(4):
                for target in range(source + 1, 4):
                    if rng.random() < 0.45:
                        query_graph.add_edge(source, target)

            baseline = BacktrackingMatcher().match(query_graph, data_graph)
            nogood = GUPMatcher(
                GUPConfig(enable_reservation_guard=False, enable_nogood_guard=True)
            ).match(query_graph, data_graph)

            self.assertEqual(
                normalize_mappings(nogood.mappings),
                normalize_mappings(baseline.mappings),
            )


if __name__ == '__main__':
    unittest.main()
