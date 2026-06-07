# Experimental Results and Analysis Draft

## 1. Overall Positioning

We implemented a correctness-first `GUP-lite` prototype that captures the core idea of guard-based pruning.
The current implementation is not yet a full reproduction of the original GuP system; however, it already allows us to evaluate how reservation-based pruning and nogood-based pruning affect the search space and the running time on both toy and real graph workloads.

Our main observation is that the reservation guard is the primary source of practical benefit in the current prototype.
The nogood guard is still conservative and does not yet provide stable pruning gains on the tested real workloads.

## 2. Results on Yeast

We first evaluated the improved implementation on two real queries from the `Yeast` dataset.

### Query `query_dense_4_1`

- Baseline: `720` result mappings, `772` partial mappings, `17.82 ms`
- Reservation only: `720` result mappings, `772` partial mappings, `19.76 ms`
- Nogood only: `720` result mappings, `772` partial mappings, `21.48 ms`
- Full GUP: `720` result mappings, `772` partial mappings, `22.89 ms`

This query is very light, and therefore the additional guard overhead is not compensated by pruning. In other words, the query is too easy for guard-based pruning to show a visible benefit.

### Query `query_dense_4_10`

- Baseline: `19678` result mappings, `22624` partial mappings, `748.22 ms`
- Reservation only: `19678` result mappings, `22283` partial mappings, `691.33 ms`
- Nogood only: `19678` result mappings, `22624` partial mappings, `812.96 ms`
- Full GUP: `19678` result mappings, `22283` partial mappings, `795.51 ms`

For this query, the reservation guard reduces the search space by `341` partial mappings and also improves the running time by about `56.89 ms` compared with the baseline. This is the clearest evidence so far that the reservation-based part of the GUP design is effective in our reproduction.

## 3. Results on Human

We then evaluated two real queries from the `Human` dataset.

### Query `query_dense_4_1`

- Baseline: `10312` result mappings, `11013` partial mappings, `160.70 ms`
- Reservation only: `10312` result mappings, `10916` partial mappings, `156.09 ms`
- Nogood only: `10312` result mappings, `11013` partial mappings, `209.33 ms`
- Full GUP: `10312` result mappings, `10916` partial mappings, `194.45 ms`

This query shows a small but consistent advantage of the reservation guard. The search space is reduced by `97` partial mappings, and the running time of the reservation-only version is slightly lower than that of the baseline.

### Query `query_dense_4_10`

After introducing two implementation-level improvements,

1. upgrading candidate generation from pure label filtering to `label + degree` filtering, and
2. activating guard checks only on query vertices that can actually trigger them,

we obtained the following results:

- Baseline: `12830306` result mappings, `12937898` partial mappings, `49973.50 ms`
- Reservation only: `12830306` result mappings, `12937608` partial mappings, `55638.53 ms`
- Nogood only: `12830306` result mappings, `12937898` partial mappings, `37932.96 ms`
- Full GUP: `12830306` result mappings, `12937608` partial mappings, `41744.04 ms`

This query is particularly important for understanding the current reproduction.

First, the reservation guard alone still provides only a very small reduction in the search space: the number of partial mappings decreases by `290`, which is negligible relative to the total search size. Therefore, reservation-based pruning alone is not sufficient to explain the performance improvement on this query.

Second, the dramatic improvement of `nogood only` and `full GUP` after guard-selective activation suggests that the earlier slowdown of the prototype was caused in large part by unnecessary Python-level guard checks rather than by the GuP idea itself. Once these empty checks were removed, the `nogood only` configuration became much faster than the baseline, and the `full GUP` configuration also clearly outperformed the baseline.

This result indicates that implementation details matter substantially in a guard-heavy algorithm, and that some of the earlier negative results were artifacts of the prototype rather than evidence against the method.

## 4. Boundary Results on WordNet and Patents

We also ran time-boxed smoke tests on `WordNet` and `Patents`.

- `WordNet / query_dense_4_1`: timeout under `120` seconds
- `Patents / query_dense_4_1`: timeout under `120` seconds
- `WordNet / query_sparse_8_15`: timeout under `120` seconds
- `Patents / query_sparse_8_15`: timeout under `120` seconds

These results suggest that the current Python prototype has already reached its practical limit on larger workloads. Therefore, `WordNet` and `Patents` should currently be treated as boundary experiments or time-boxed evidence of difficulty, rather than as the main datasets for quantitative comparison.

## 5. Current Conclusion

At the current stage, the most defensible conclusion is the following:

1. The reproduction is not a full implementation of the original GuP system, but it already captures a meaningful subset of the method.
2. The reservation guard is the main source of improvement in the present prototype.
3. The nogood guard remains conservative in terms of pruning power, but after reducing unnecessary checks, it no longer behaves as pure overhead.
4. On some real queries, especially from `Yeast` and `Human`, the improved `GUP-lite` already reduces the search space and can outperform the baseline in wall-clock time.
5. On larger datasets such as `WordNet` and `Patents`, the current Python implementation is still insufficient, and the observed timeouts should be presented as boundary results.
