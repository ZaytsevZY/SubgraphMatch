from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.io import load_graph_from_edge_list
from subgraph_match.matchers import BacktrackingMatcher


def main() -> None:
    data_file = ROOT / 'data' / 'sample' / 'toy_graph.txt'
    query_file = ROOT / 'data' / 'sample' / 'toy_query_path.txt'

    data_graph = load_graph_from_edge_list(data_file)
    query_graph = load_graph_from_edge_list(query_file)

    matcher = BacktrackingMatcher()
    result = matcher.match(query_graph=query_graph, data_graph=data_graph)

    print('Loaded graphs:')
    print(f'  data_graph: vertices={data_graph.num_vertices}, edges={data_graph.num_edges}')
    print(f'  query_graph: vertices={query_graph.num_vertices}, edges={query_graph.num_edges}')
    print('Matcher:')
    print(f'  name={matcher.name}')
    print(f'  vertex_order={result.vertex_order}')
    print('Statistics:')
    print(json.dumps(result.statistics.to_dict(), ensure_ascii=False, indent=2))
    print('Mappings:')
    print(json.dumps(result.mappings, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
