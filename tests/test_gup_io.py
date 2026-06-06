from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.io import load_graph_from_gup_prefix, load_query_set_from_gup_yaml


class GUPIOTest(unittest.TestCase):
    def test_load_graph_from_gup_prefix(self) -> None:
        graph = load_graph_from_gup_prefix(ROOT / 'data' / 'sample' / 'gup_example')

        self.assertEqual(graph.num_vertices, 9)
        self.assertEqual(graph.num_edges, 10)
        self.assertEqual(graph.labels[0], '1')
        self.assertTrue(graph.has_edge(1, 8))
        self.assertTrue(graph.has_edge(8, 1))

    def test_load_query_set_from_gup_yaml(self) -> None:
        queries = load_query_set_from_gup_yaml(ROOT / 'data' / 'sample' / 'gup_query_set.yaml')

        self.assertEqual(len(queries), 3)
        self.assertEqual(queries[0].num_vertices, 3)
        self.assertEqual(queries[1].num_edges, 3)
        self.assertEqual(queries[2].labels[2], '0')
        self.assertTrue(queries[1].has_edge(0, 2))


if __name__ == '__main__':
    unittest.main()
