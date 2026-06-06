from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import signal
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from subgraph_match.config import GUPConfig
from subgraph_match.io import (
    load_graph_from_edge_list,
    load_graph_from_graph_format,
    load_graph_from_gup_prefix,
    load_query_set_from_gup_yaml,
)
from subgraph_match.matchers import BacktrackingMatcher, GUPMatcher


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run a single baseline/GUP experiment and save raw results.')
    parser.add_argument(
        '--matcher',
        choices=['baseline', 'gup'],
        default='gup',
        help='Matcher to run. Default: gup.',
    )
    parser.add_argument(
        '--input-format',
        choices=['toy', 'gup', 'graph'],
        default='toy',
        help='Input format. toy uses edge-list files; gup uses <prefix>.vertices/.edges plus a YAML query set; graph uses the .graph format.',
    )
    parser.add_argument(
        '--data-file',
        type=Path,
        default=ROOT / 'data' / 'sample' / 'toy_graph.txt',
        help='Path to the data graph file or GUP graph prefix.',
    )
    parser.add_argument(
        '--query-file',
        type=Path,
        default=ROOT / 'data' / 'sample' / 'toy_query_path.txt',
        help='Path to the query graph file or GUP YAML query set.',
    )
    parser.add_argument(
        '--query-index',
        type=int,
        default=0,
        help='Query index inside a GUP YAML query set. Ignored for toy input format.',
    )
    parser.add_argument(
        '--dataset-name',
        type=str,
        default='toy_graph',
        help='Logical dataset name written to the result file.',
    )
    parser.add_argument(
        '--query-name',
        type=str,
        default='toy_query_path',
        help='Logical query name written to the result file.',
    )
    parser.add_argument(
        '--disable-reservation-guard',
        action='store_true',
        help='Disable the reservation guard for GUP runs.',
    )
    parser.add_argument(
        '--disable-nogood-guard',
        action='store_true',
        help='Disable the nogood guard for GUP runs.',
    )
    parser.add_argument(
        '--output-file',
        type=Path,
        default=None,
        help='Optional explicit JSON output path. Defaults to results/raw/<generated-name>.json',
    )
    parser.add_argument(
        '--omit-mappings',
        action='store_true',
        help='Do not include the full mappings list in the JSON output.',
    )
    parser.add_argument(
        '--timeout-sec',
        type=int,
        default=None,
        help='Optional wall-clock timeout in seconds for a single query run.',
    )
    return parser.parse_args()


class ExperimentTimeoutError(RuntimeError):
    pass


def _timeout_handler(signum: int, frame: object) -> None:
    raise ExperimentTimeoutError('Experiment timed out.')


def build_matcher(args: argparse.Namespace) -> tuple[object, dict[str, Any]]:
    if args.matcher == 'baseline':
        matcher = BacktrackingMatcher()
        config = {
            'matcher': 'baseline',
            'enable_reservation_guard': False,
            'enable_nogood_guard': False,
        }
        return matcher, config

    gup_config = GUPConfig(
        enable_reservation_guard=not args.disable_reservation_guard,
        enable_nogood_guard=not args.disable_nogood_guard,
    )
    matcher = GUPMatcher(gup_config)
    config = {
        'matcher': 'gup',
        'enable_reservation_guard': gup_config.enable_reservation_guard,
        'enable_nogood_guard': gup_config.enable_nogood_guard,
    }
    return matcher, config


def build_output_path(args: argparse.Namespace, config: dict[str, Any]) -> Path:
    if args.output_file is not None:
        return args.output_file

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    guard_suffix = 'baseline'
    if config['matcher'] == 'gup':
        guard_suffix = f"res-{int(config['enable_reservation_guard'])}_nog-{int(config['enable_nogood_guard'])}"

    filename = f"{timestamp}_{args.dataset_name}_{args.query_name}_{config['matcher']}_{guard_suffix}.json"
    return ROOT / 'results' / 'raw' / filename


def main() -> None:
    args = parse_args()
    matcher, config = build_matcher(args)

    if args.input_format == 'toy':
        data_graph = load_graph_from_edge_list(args.data_file)
        query_graph = load_graph_from_edge_list(args.query_file)
    elif args.input_format == 'gup':
        data_graph = load_graph_from_gup_prefix(args.data_file)
        query_graphs = load_query_set_from_gup_yaml(args.query_file)
        query_graph = query_graphs[args.query_index]
    else:
        data_graph = load_graph_from_graph_format(args.data_file)
        query_graph = load_graph_from_graph_format(args.query_file)

    previous_handler = signal.getsignal(signal.SIGALRM)
    result = None
    status = 'success'
    if args.timeout_sec is not None:
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(args.timeout_sec)

    try:
        result = matcher.match(query_graph=query_graph, data_graph=data_graph)
    except ExperimentTimeoutError:
        status = 'timeout'
    finally:
        if args.timeout_sec is not None:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_handler)

    payload: dict[str, Any] = {
        'dataset_name': args.dataset_name,
        'query_name': args.query_name,
        'data_file': str(args.data_file.resolve()),
        'query_file': str(args.query_file.resolve()),
        'input_format': args.input_format,
        'query_index': args.query_index if args.input_format == 'gup' else None,
        'status': status,
        'timeout_sec': args.timeout_sec,
        'matcher_name': matcher.name,
        'matcher_config': config,
        'data_graph': {
            'num_vertices': data_graph.num_vertices,
            'num_edges': data_graph.num_edges,
        },
        'query_graph': {
            'num_vertices': query_graph.num_vertices,
            'num_edges': query_graph.num_edges,
        },
    }

    if result is not None:
        payload['statistics'] = result.statistics.to_dict()
        payload['result_mappings_count'] = len(result.mappings)
    else:
        payload['statistics'] = None
        payload['result_mappings_count'] = None

    if result is not None and not args.omit_mappings:
        payload['mappings'] = result.mappings

    output_path = build_output_path(args, config)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    print('Experiment completed.')
    print(f'  status={status}')
    print(f'  matcher={matcher.name}')
    print(f'  dataset={args.dataset_name}')
    print(f'  query={args.query_name}')
    print(f'  output={output_path}')
    print(f"  result_mappings={payload['result_mappings_count']}")
    if payload['statistics'] is not None:
        print(f"  partial_mappings={payload['statistics']['partial_mappings']}")
        print(f"  pruned_partial_mappings={payload['statistics']['pruned_partial_mappings']}")
        print(f"  runtime_ms={payload['statistics']['runtime_ms']:.6f}")


if __name__ == '__main__':
    main()
