from pathlib import Path

from subgraph_match.models import LabeledGraph


def load_graph_from_edge_list(path: str | Path) -> LabeledGraph:
    """Load a toy labeled undirected graph from a simple text format.

    Vertex line: v <id> <label>
    Edge line:   e <src> <dst>
    """

    graph = LabeledGraph()
    for raw_line in Path(path).read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue

        parts = line.split()
        record_type = parts[0]
        if record_type == 'v' and len(parts) >= 3:
            graph.add_vertex(int(parts[1]), parts[2])
        elif record_type == 'e' and len(parts) >= 3:
            graph.add_edge(int(parts[1]), int(parts[2]))
        else:
            raise ValueError(f'Unsupported line format: {raw_line}')

    return graph
