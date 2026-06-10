from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]

# Deterministic synthetic graph for the subgraph-homomorphism demo.
#
# The graph is a disjoint union of cliques, all vertices labeled A. For the
# triangle query A-A-A:
#   * every function from the 3 query vertices into a single clique is a valid
#     homomorphism (distinct endpoints are adjacent, equal endpoints use the
#     E_G^+ self-loop), giving clique_size^3 homomorphisms per clique;
#   * only the injective ones are isomorphisms, giving
#     clique_size*(clique_size-1)*(clique_size-2) per clique.
# The gap is exactly the set of non-injective homomorphisms produced by the
# self-loop relaxation, which is what this demo highlights.


def build_demo(blocks: int, clique_size: int) -> Tuple[List[Tuple[int, str]], List[Tuple[int, int]]]:
    vertices: List[Tuple[int, str]] = []
    edges: List[Tuple[int, int]] = []
    next_id = 0

    for _ in range(blocks):
        members: List[int] = []
        for _ in range(clique_size):
            vertices.append((next_id, 'A'))
            members.append(next_id)
            next_id += 1
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                edges.append((members[i], members[j]))

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
        '# Triangle query A-A-A used by the homomorphism demo.',
        'v 0 A',
        'v 1 A',
        'v 2 A',
        'e 0 1',
        'e 1 2',
        'e 0 2',
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate the deterministic homomorphism demo graph.')
    parser.add_argument('--blocks', type=int, default=15)
    parser.add_argument('--clique-size', type=int, default=6)
    parser.add_argument('--graph-out', type=Path, default=ROOT / 'data' / 'sample' / 'homomorphism_demo_graph.txt')
    parser.add_argument('--query-out', type=Path, default=ROOT / 'data' / 'sample' / 'homomorphism_demo_query_triangle.txt')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    vertices, edges = build_demo(args.blocks, args.clique_size)
    hom = args.blocks * args.clique_size ** 3
    iso = args.blocks * args.clique_size * (args.clique_size - 1) * (args.clique_size - 2)
    header = (
        f'Homomorphism demo graph: {args.blocks} cliques of size {args.clique_size}, all label A. '
        f'Triangle query A-A-A has {hom} homomorphisms and {iso} isomorphisms.'
    )
    write_edge_list(args.graph_out, vertices, edges, header)
    write_query(args.query_out)

    print('Homomorphism demo graph generated.')
    print(f'  vertices={len(vertices)} edges={len(edges)}')
    print(f'  expected homomorphisms={hom} isomorphisms={iso} non_injective={hom - iso}')
    print(f'  graph={args.graph_out}')
    print(f'  query={args.query_out}')


if __name__ == '__main__':
    main()
