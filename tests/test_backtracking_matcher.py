from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.io import load_graph_from_edge_list
from subgraph_match.matchers import BacktrackingMatcher


class BacktrackingMatcherTest(unittest.TestCase):
    def test_toy_query_path_returns_two_mappings(self) -> None:
        data_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_graph.txt')
        query_graph = load_graph_from_edge_list(ROOT / 'data' / 'sample' / 'toy_query_path.txt')

        matcher = BacktrackingMatcher()
        result = matcher.match(query_graph=query_graph, data_graph=data_graph)

        normalized = {
            tuple(sorted(mapping.items()))
            for mapping in result.mappings
        }

        self.assertEqual(result.statistics.result_mappings, 2)
        self.assertEqual(
            normalized,
            {
                ((1, 1), (2, 2), (3, 3)),
                ((1, 3), (2, 2), (3, 1)),
            },
        )
        self.assertGreaterEqual(result.statistics.partial_mappings, result.statistics.result_mappings)
        self.assertGreaterEqual(result.statistics.pruned_partial_mappings, 1)


if __name__ == '__main__':
    unittest.main()
