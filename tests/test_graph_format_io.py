from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.io import load_graph_from_graph_format


class GraphFormatIOTest(unittest.TestCase):
    def test_load_graph_from_graph_format(self) -> None:
        graph = load_graph_from_graph_format(
            ROOT / 'data' / 'raw' / 'gup-paper' / 'extracted' / 'dataset' / 'yeast' / 'query_graph' / 'query_sparse_8_15.graph'
        )

        self.assertEqual(graph.num_vertices, 8)
        self.assertEqual(graph.num_edges, 11)
        self.assertEqual(graph.labels[0], '2')
        self.assertTrue(graph.has_edge(4, 6))
        self.assertTrue(graph.has_edge(6, 4))


if __name__ == '__main__':
    unittest.main()
