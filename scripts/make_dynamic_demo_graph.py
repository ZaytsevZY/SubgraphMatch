from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]

# Deterministic synthetic stress graph for the dynamic-maintenance demo.
#
# The graph is a disjoint union of identical gadgets. Each gadget has one
# A-labeled hub connected to ``fanout_b`` B-labeled vertices, and every B vertex
# is connected to ``fanout_c`` private C-labeled vertices.
#
# For the path query  A -- B -- C  this produces  blocks * fanout_b * fanout_c
# result mappings, but any single A--B edge is used by only ``fanout_c`` of them.
# That gap is exactly what makes incremental single-edge maintenance much cheaper
# than recomputing all mappings from scratch.


def build_demo(blocks: int, fanout_b: int, fanout_c: int) -> Tuple[List[Tuple[int, str]], List[Tuple[int, int]]]:
    vertices: List[Tuple[int, str]] = []
    edges: List[Tuple[int, int]] = []
    next_id = 0

    def new_vertex(label: str) -> int:
        nonlocal next_id
        vertex_id = next_id
        next_id += 1
        vertices.append((vertex_id, label))
        return vertex_id

    for _ in range(blocks):
        hub = new_vertex('A')
        for _ in range(fanout_b):
            b_vertex = new_vertex('B')
            edges.append((hub, b_vertex))
            for _ in range(fanout_c):
                c_vertex = new_vertex('C')
                edges.append((b_vertex, c_vertex))

    return vertices, edges


def write_edge_list(path: Path, vertices, edges, header: str) -> None:
    lines = [f'# {header}']
    for vertex_id, label in vertices:
        lines.append(f'v {vertex_id} {label}')
    for source, target in edges:
        lines.append(f'e {source} {target}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_query(path: Path) -> None:
    lines = [
        '# Path query A-B-C used by the dynamic-maintenance demo.',
        'v 0 A',
        'v 1 B',
        'v 2 C',
        'e 0 1',
        'e 1 2',
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate the deterministic dynamic-maintenance demo graph.')
    parser.add_argument('--blocks', type=int, default=120)
    parser.add_argument('--fanout-b', type=int, default=6)
    parser.add_argument('--fanout-c', type=int, default=6)
    parser.add_argument('--graph-out', type=Path, default=ROOT / 'data' / 'sample' / 'dynamic_demo_graph.txt')
    parser.add_argument('--query-out', type=Path, default=ROOT / 'data' / 'sample' / 'dynamic_demo_query_path.txt')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    vertices, edges = build_demo(args.blocks, args.fanout_b, args.fanout_c)
    header = (
        f'Dynamic-maintenance demo graph: {args.blocks} blocks, '
        f'fanout_b={args.fanout_b}, fanout_c={args.fanout_c}. '
        f'Path query A-B-C has {args.blocks * args.fanout_b * args.fanout_c} matches.'
    )
    write_edge_list(args.graph_out, vertices, edges, header)
    write_query(args.query_out)

    print('Demo graph generated.')
    print(f'  vertices={len(vertices)} edges={len(edges)}')
    print(f'  expected A-B-C path matches={args.blocks * args.fanout_b * args.fanout_c}')
    print(f'  graph={args.graph_out}')
    print(f'  query={args.query_out}')


if __name__ == '__main__':
    main()
