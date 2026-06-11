# Nogood Cold-Start Fix and Synthetic Benchmark

## Fix

The previous matcher only created a `GuardContext` for guards whose
`is_active(query_vertex)` returned true. `NogoodGuard` activated a query vertex
only after recording a dead end, so a Nogood-only run could never record its
first signature.

The matcher now separates checking from learning:

- inactive Nogood guards skip signature lookups;
- learning guards still receive a context;
- a failed subtree records its first signature;
- later candidates at that query vertex can query and reuse the learned
  signature.

The regression test uses two symmetric prefix histories that reach the same
future triangle dead-end. It now requires nonzero Nogood pruning and a strict
partial-mapping reduction.

## Validation

`python3 -m unittest -q` passes all 32 tests. The graph-format test now uses a
repository-local fixture rather than an uncommitted Yeast dataset file, and 40
deterministic random cases compare complete Baseline and Nogood result sets.

## Reproducible Synthetic Benchmark

Run:

```bash
python3 scripts/benchmark_nogood_synthetic.py \
  --prefix-size 7 \
  --cycle-size 9 \
  --warmups 3 \
  --repeats 11 \
  --output-file results/raw/nogood-fixed-synthetic-p7.json
```

The default benchmark is connected. An A-labeled clique creates many symmetric
prefix histories, and an anchored X-labeled triangle query repeatedly reaches
the same dead-end because the X-labeled data region is only a cycle. Baseline
and Nogood runs are alternated after warm-up, and the median runtime is reported.

| Prefix size | Baseline PM | Nogood PM | Nogood prunes | Baseline median | Nogood median | Speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 5 | 2,845 | 246 | 233 | 9.825 ms | 3.437 ms | 2.86x |
| 6 | 19,236 | 1,290 | 922 | 78.496 ms | 19.014 ms | 4.13x |
| 7 | 149,779 | 8,728 | 5,367 | 687.270 ms | 144.491 ms | 4.76x |

All variants return zero mappings on this intentionally unsatisfiable workload,
and the complete result sets are checked for equality.

### Mixed workload with valid results

Passing `--include-valid-triangle` adds a valid X triangle alongside the
failing cycle. The matcher must preserve and enumerate all valid results while
reusing only the repeated failing branches.

| Prefix size | Results | Baseline PM | Nogood PM | Nogood prunes | Baseline median | Nogood median | Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 720 | 4,645 | 2,146 | 833 | 19.374 ms | 18.655 ms | 1.04x |
| 6 | 4,320 | 30,036 | 12,780 | 5,752 | 144.801 ms | 126.668 ms | 1.14x |
| 7 | 30,240 | 225,379 | 89,326 | 45,351 | 1,194.011 ms | 1,013.255 ms | 1.18x |

The complete result sets are equal in every comparison. The smaller runtime
gain is expected: Nogood removes repeated failing work, but both variants must
still materialize every valid mapping.

## Interpretation

The benchmark demonstrates that the fixed implementation can learn and reuse
Nogood signatures, and that the benefit grows when many histories induce the
same failing future subproblem. The failure-only benchmark shows the favorable
upper regime, while the mixed benchmark shows a smaller but measurable runtime
gain when tens of thousands of valid mappings must still be emitted. Neither
replaces the real-dataset ablation: the benchmarks are deterministic and
structurally favorable to Nogood.

## Real-data follow-up

After restoring the dataset package, the six original dense-4 workloads were
rerun. Their qualitative conclusion remains unchanged: Reservation accounts
for nearly all useful pruning, while Nogood has zero or negligible hits. Human
`d4-10`, for example, produces only two Nogood prunes while enumerating more
than 12.8 million results, so lookup overhead dominates.

A broader scan of Yeast dense-8 queries found two useful real workloads.
Repeated runs use `scripts/benchmark_real_ablation.py`, warm-up, rotated
execution order, and complete result-set equality checks.

| Query | Variant | Results | Partial mappings | Reservation prunes | Nogood prunes | Median | Speedup |
|---|---|---:|---:|---:|---:|---:|---:|
| d8-103 | Baseline | 38 | 463 | 0 | 0 | 59.75 ms | 1.00x |
| d8-103 | Reservation only | 38 | 238 | 221 | 0 | 28.89 ms | 2.07x |
| d8-103 | Nogood only | 38 | 290 | 0 | 173 | 37.24 ms | 1.60x |
| d8-103 | Full | 38 | 168 | 221 | 70 | 19.40 ms | 3.08x |
| d8-132 | Baseline | 548 | 13,461 | 0 | 0 | 3,217.62 ms | 1.00x |
| d8-132 | Reservation only | 548 | 13,452 | 5 | 0 | 3,258.45 ms | 0.99x |
| d8-132 | Nogood only | 548 | 5,932 | 0 | 2,818 | 1,418.07 ms | 2.27x |
| d8-132 | Full | 548 | 5,924 | 5 | 2,817 | 1,412.19 ms | 2.28x |

These queries were selected after scanning for nonzero Nogood hits, so they are
targeted mechanism evidence rather than an unbiased average over all queries.
