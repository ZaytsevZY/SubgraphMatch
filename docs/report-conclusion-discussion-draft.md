# Conclusion and Discussion Draft

## Conclusion

In this project, we reproduced the core idea of GuP through a correctness-first `GUP-lite` prototype for exact subgraph matching on vertex-labeled graphs.
Although our implementation is not yet a full system-level reproduction of the original GuP algorithm, it already captures the main intuition of guard-based pruning and supports ablation between the baseline search, reservation-based pruning, nogood-based pruning, and their combination.

Our experimental results lead to three main conclusions.

First, the reservation-based part of the method is effective in our reproduction.
After improving the reservation guard from a simple runtime forward check to a small precomputed reservation-set mechanism, we observed clear reductions in the search space on real queries from Yeast and Human.
More importantly, on some representative queries, such as `yeast/query_dense_4_10` and `human/query_dense_4_1`, the improved `GUP-lite` not only reduced the number of `partial mappings` but also outperformed the baseline in wall-clock time.

Second, the current nogood-based part remains incomplete compared with the original paper.
The implemented nogood guard is still conservative in pruning power, and its contribution is workload-dependent.
However, our later optimization showed that part of the earlier slowdown came from unnecessary guard checks rather than from the GuP idea itself.
Once those empty checks were reduced, the performance of `nogood only` and `full GUP` improved substantially on heavier real queries.

Third, the current Python prototype has a clear scalability boundary.
On the larger datasets, especially WordNet and Patents, even time-boxed smoke experiments frequently timed out.
This indicates that while the algorithmic direction is valid, the present implementation is still insufficient for the hardest workloads used in the original paper.

Overall, our reproduction should be viewed as a successful course-project-level reconstruction of the core GuP design, rather than as a full engineering reproduction of the original system.
It already demonstrates that guard-based pruning can be effective, but it also shows that the practical performance of GuP depends heavily on the quality of the implementation.

## Discussion

The most important lesson from this project is that a negative result in an early prototype does not necessarily invalidate the original algorithmic idea.
At first, our `GUP-lite` reduced the search space only slightly and often failed to improve runtime over the baseline.
A closer inspection revealed that the main issue was not the overall GuP direction, but the gap between our simplified implementation and the actual mechanisms described in the paper.

In particular, two implementation gaps were decisive.
The first gap was the reservation guard.
Our earliest version behaved more like a local forward-checking heuristic than a genuine reservation mechanism.
Once we switched to a small precomputed reservation-set design, the benefit became much more visible on real workloads.
The second gap was the treatment of nogood checks.
The earlier version spent too much time checking guards at locations where they could not meaningfully contribute.
After restricting guard activation to relevant query vertices, the runtime improved substantially on heavy queries, even though the nogood guard itself still remained weaker than the one in the original GuP.

These observations suggest that the current limitations are mainly implementation-driven rather than purely algorithm-driven.
The present prototype already supports the claim that GuP-style pruning is useful, but it also highlights that the paper's full performance cannot be expected without stronger data structures and a more faithful implementation of the nogood component.

From the perspective of future work, there are three promising directions.
First, the nogood mechanism should be strengthened by introducing a representation closer to the original search-node encoding and by supporting more general nogood discovery rules.
Second, the current candidate filtering stage can be extended further beyond `label + degree` filtering toward a guarded candidate space closer to the paper.
Third, if we aim to reproduce the behavior on large datasets such as WordNet and Patents more faithfully, a higher-performance implementation language or lower-overhead runtime design will likely be necessary.

In summary, the project already provides a meaningful and defensible reproduction result: the core GuP idea works, the reservation guard can bring practical improvements, and the remaining gap lies mainly in the strength and efficiency of the nogood-related implementation.

## Suggested Short Version for Final Report

If a shorter concluding paragraph is needed, the following version can be used directly.

> We reproduced the core idea of GuP with a correctness-first `GUP-lite` implementation and verified that guard-based pruning can improve real subgraph matching workloads. In particular, the improved reservation guard consistently reduced the search space and, on several real queries, also improved runtime over the baseline. At the same time, our study shows that the quality of the implementation strongly affects the observed benefit: the current nogood component remains conservative, and the Python prototype still struggles on larger datasets such as WordNet and Patents. Therefore, our work should be regarded as a successful core-method reproduction at course-project scale, while a full reproduction of the original paper would require stronger nogood machinery and a more optimized implementation.
