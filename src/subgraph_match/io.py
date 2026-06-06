from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised indirectly in tests
    yaml = None

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


def load_graph_from_graph_format(path: str | Path) -> LabeledGraph:
    """Load a graph from the .graph format used by the SubgraphMatching study.

    Format:
    - header: t <num_vertices> <num_edges>
    - vertex: v <vertex_id> <label_id> <degree>
    - edge:   e <src> <dst> <ignored>
    """

    graph = LabeledGraph()
    for raw_line in Path(path).read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split()
        record_type = parts[0]
        if record_type == 't':
            continue
        if record_type == 'v' and len(parts) >= 4:
            graph.add_vertex(int(parts[1]), parts[2])
        elif record_type == 'e' and len(parts) >= 3:
            graph.add_edge(int(parts[1]), int(parts[2]))
        else:
            raise ValueError(f'Unsupported .graph line format: {raw_line}')

    return graph


def load_graph_from_gup_prefix(prefix: str | Path) -> LabeledGraph:
    """Load a GUP-format undirected labeled graph.

    The graph is stored as a pair of TSV files:
    - <prefix>.vertices: <vertex_id> <tab> <label_id>
    - <prefix>.edges:    <src> <tab> <dst>
    """

    prefix_path = Path(prefix)
    vertices_path = prefix_path.with_suffix('.vertices')
    edges_path = prefix_path.with_suffix('.edges')

    graph = LabeledGraph()

    for raw_line in vertices_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line:
            continue
        vertex_id, label = line.split('\t')
        graph.add_vertex(int(vertex_id), str(label))

    for raw_line in edges_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line:
            continue
        source, target = line.split('\t')
        graph.add_edge(int(source), int(target))

    return graph


def load_query_set_from_gup_yaml(path: str | Path) -> list[LabeledGraph]:
    """Load a GUP-format YAML query set as a list of LabeledGraph objects."""

    raw_text = Path(path).read_text(encoding='utf-8')
    if yaml is not None:
        payload = yaml.safe_load(raw_text)
    else:
        payload = _load_gup_query_set_without_yaml(raw_text)

    query_graphs: list[LabeledGraph] = []

    for query_spec in payload:
        graph = LabeledGraph()
        for vertex_id, label in enumerate(query_spec.get('vertices', [])):
            graph.add_vertex(vertex_id, str(label))
        for source, target in query_spec.get('edges', []):
            graph.add_edge(int(source), int(target))
        query_graphs.append(graph)

    return query_graphs


def _load_gup_query_set_without_yaml(raw_text: str) -> list[dict[str, Any]]:
    """Parse the limited YAML shape used by GUP query-set files.

    Supported shape:

    - edges:
        - [0, 1]
      vertices:
        - 1
        - 2
    - ...
    """

    queries: list[dict[str, Any]] = []
    current_query: dict[str, Any] | None = None
    current_key: str | None = None

    for raw_line in raw_text.splitlines():
        if not raw_line.strip():
            continue

        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith('- edges:') or stripped.startswith('- vertices:'):
            if current_query is not None:
                queries.append(current_query)
            current_query = {'edges': [], 'vertices': []}
            current_key = stripped[2:-1].strip()
            continue

        if stripped in {'edges:', 'vertices:'}:
            current_key = stripped[:-1]
            continue

        if stripped.startswith('- ['):
            assert current_query is not None and current_key == 'edges'
            body = stripped[3:-1]
            source, target = [part.strip() for part in body.split(',')]
            current_query['edges'].append([int(source), int(target)])
            continue

        if stripped.startswith('- '):
            assert current_query is not None and current_key == 'vertices'
            current_query['vertices'].append(int(stripped[2:].strip()))
            continue

        raise ValueError(f'Unsupported GUP YAML line: {raw_line}')

    if current_query is not None:
        queries.append(current_query)

    return queries
