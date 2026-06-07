# Implementation Details Draft

## 1. Implementation Overview

We implemented the project in Python with a correctness-first design philosophy.
The goal of the implementation was not to replicate the full engineering complexity of the original GuP system in a single step, but to build a reproducible and extensible framework that supports correctness checking, metric collection, and ablation experiments.

The final codebase consists of two main matchers:

1. `BacktrackingMatcher`, which serves as the baseline exact subgraph matcher.
2. `GUPMatcher`, which extends the same search framework with guard-based pruning.

This separation makes it possible to compare the baseline and the GuP-inspired variants under the same graph model, candidate generation rule, search order, and metric definitions.

## 2. Graph Representation and Input Handling

All graph variants are converted into a unified in-memory structure `LabeledGraph`, which stores:

- an adjacency dictionary for undirected edges, and
- a label dictionary for vertex labels.

This unified representation allows the same matcher code to work across multiple input formats.

The project currently supports three input formats:

1. a simple toy text format (`v/e`) used for debugging,
2. the official GuP example format (`.vertices`, `.edges`, and YAML query sets), and
3. the `.graph` format used by the downloaded real datasets.

Adding these loaders was important because the downloaded benchmark package does not share the same format as the official GuP repository examples.

## 3. Baseline Matcher

The baseline matcher performs exact subgraph matching through depth-first backtracking.
Its processing pipeline is:

1. construct candidate sets for each query vertex,
2. generate a matching order over query vertices,
3. recursively extend a partial embedding, and
4. validate each extension with injectivity and edge-consistency checks.

The baseline is intentionally simple but already instrumented with statistics.
Therefore, it provides a clean reference point for later evaluating the effect of guard-based pruning.

## 4. Candidate Generation and Matching Order

The candidate generation rule was initially label-based only, but was later upgraded to a `label + degree` rule.
Concretely, a data vertex is kept as a candidate of a query vertex only if:

- the labels are equal, and
- the degree of the data vertex is at least the degree of the query vertex.

This change makes the candidate generation closer to the standard label-and-degree filter used in classical subgraph matching systems.

The matching order is computed by sorting query vertices using:

1. ascending candidate set size,
2. descending degree, and
3. vertex identifier as a tiebreaker.

Although this is still simpler than the full order generation strategy in GuP, it is sufficient to provide a deterministic and reproducible order for both the baseline and the guard-based matcher.

## 5. Search State and Metrics

The current search state stores two maps:

- `query_to_data`, the current embedding from query vertices to data vertices, and
- `data_to_query`, used to test injectivity efficiently.

We track the following core metrics throughout search:

- `result_mappings`
- `partial_mappings`
- `pruned_partial_mappings`
- `runtime_ms`
- `guard_checks_total`
- prune reasons such as `edge_conflict`, `injectivity_conflict`, and guard-specific causes

These statistics are shared by all matcher variants, which ensures that the ablation results are directly comparable.

## 6. GUP-lite Design

Our `GUP-lite` implementation reuses the baseline DFS/backtracking structure and inserts guard checks before extending a partial embedding.
This design keeps the implementation easy to validate while still exposing the main GuP idea: prune candidate extensions by reasoning about the future search space.

The current `GUP-lite` supports two guard modules:

1. `ReservationGuard`
2. `NogoodGuard`

These guards can be enabled or disabled independently through `GUPConfig`, which allows us to evaluate:

- baseline,
- reservation only,
- nogood only, and
- full GUP.

## 7. Reservation Guard

The reservation guard went through several iterations.

### 7.1 Early version
The earliest version behaved like a lightweight forward-checking rule. It inspected future neighbors during search and pruned a candidate if no valid continuation remained. While correct, this design was weak and expensive because it repeatedly scanned future possibilities online.

### 7.2 Improved version
The improved reservation guard is closer to the intuition of the paper.
Before search begins, it precomputes small reservation sets for candidate assignments.
For a candidate `(u, v)`, it inspects forward neighbors of `u` in the matching order and collects compatible future candidate sets.
If a small subset of those future candidates satisfies a Hall-style equality between subset size and candidate-union size, that union is treated as reserved.

At runtime, the guard only checks whether one of those reserved data vertices has already been used.
This change shifts work from online repeated scans to a smaller amount of precomputed information and substantially improves the practical behavior of the reservation-based pruning.

## 8. Nogood Guard

The current nogood guard is a conservative memoization mechanism rather than a full reproduction of the original GuP nogood machinery.

Instead of implementing the full search-node encoding from the paper, the current version stores a signature of the future subproblem after a candidate extension. This signature records:

- search depth and extension identity,
- the used data-vertex set after the extension, and
- the frontier mapping that still constrains the remaining search.

This design preserves correctness and allows dead-end reuse, but it is much weaker than the original GuP nogood design.

Later in the project, we observed that a large fraction of the runtime overhead came from checking nogoods at query vertices where no useful nogood had ever been learned. Therefore, we introduced guard-selective activation: the nogood guard is now checked only for query vertices that have previously produced relevant dead-end information.

This optimization does not strengthen the pruning logic itself, but it reduces empty-check overhead substantially.

## 9. Timeout and Workload Management

To make experiments reproducible on real datasets, we added timeboxing support to the experiment scripts.
Each single-query run can optionally receive a wall-clock timeout, and the result is then recorded with a `status` field (`success` or `timeout`) instead of hanging indefinitely.

This is particularly important for larger datasets such as WordNet and Patents, where the current Python prototype frequently reaches its practical limit.

## 10. Experimental Workflow

The experimental workflow now consists of three layers:

1. `run_gup_experiment.py` for a single run,
2. `run_query_set_batch.py` and `run_gup_batch.py` for standard ablation batches, and
3. `summarize_results.py` for aggregating raw JSON files into CSV tables.

This workflow was built incrementally so that every algorithmic change could be evaluated quickly on toy graphs, then on real smoke workloads, and finally on the chosen report queries.

## 11. Current Limitations

The implementation still has several limitations relative to the original paper:

1. the nogood guard is still a simplified version,
2. the candidate space is not yet a full guarded candidate space as in GuP,
3. the matching order is simpler than the one used in the paper, and
4. the entire system is implemented in Python, which imposes substantial overhead on large workloads.

Nevertheless, the current implementation is already sufficient to support a meaningful course-project-level reproduction and to reveal which parts of the GuP idea are most effective in practice.
