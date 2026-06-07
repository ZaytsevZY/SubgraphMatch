# 实验结果草稿

## 1. 当前最关键的实验结论

在将候选过滤升级为 `label + degree`，并把 `reservation_guard` 改为“预计算小型 reservation set”之后，
当前 `GUP-lite` 已经开始在部分真实 query 上体现出有效的剪枝收益，且在个别 query 上已经可以优于 baseline 的运行时间。

但需要同时说明：

- 收益主要来自 `reservation_guard`
- `nogood_guard` 在当前真实数据上仍然没有表现出稳定增益
- 不同 query 的结果差异较大，因此当前结论应表述为“部分 query 上有效”，而不是“全面优于 baseline”

## 2. Yeast 结果

### Query: `query_dense_4_1`

| Variant | Result mappings | Partial mappings | Runtime (ms) | 观察 |
| --- | ---: | ---: | ---: | --- |
| Baseline | 720 | 772 | 17.82 | 参考线 |
| Reservation only | 720 | 772 | 19.76 | 未改善时间 |
| Nogood only | 720 | 772 | 21.48 | 无收益 |
| Full GUP | 720 | 772 | 22.89 | 无收益 |

结论：
- 这条 query 太轻，改进空间有限
- 即使 guard 不出错，也不足以覆盖额外开销

### Query: `query_dense_4_10`

| Variant | Result mappings | Partial mappings | Runtime (ms) | 观察 |
| --- | ---: | ---: | ---: | --- |
| Baseline | 19678 | 22624 | 748.22 | 参考线 |
| Reservation only | 19678 | 22283 | 691.33 | 同时降低搜索空间和时间 |
| Nogood only | 19678 | 22624 | 812.96 | 无收益 |
| Full GUP | 19678 | 22283 | 795.51 | 仍优于搜索空间，但时间不如 reservation only |

结论：
- `reservation_guard` 将 `partial_mappings` 降低了 `341`
- 与 baseline 相比，`reservation_only` 时间缩短约 `56.89 ms`
- 这是当前最明确的一条“真实数据上优于 baseline”的证据

## 3. Human 结果

### Query: `query_dense_4_1`

| Variant | Result mappings | Partial mappings | Runtime (ms) | 观察 |
| --- | ---: | ---: | ---: | --- |
| Baseline | 10312 | 11013 | 160.70 | 参考线 |
| Reservation only | 10312 | 10916 | 156.09 | 同时降低搜索空间和时间 |
| Nogood only | 10312 | 11013 | 209.33 | 无收益 |
| Full GUP | 10312 | 10916 | 194.45 | 搜索空间更小，但时间仍偏高 |

结论：
- `reservation_guard` 将 `partial_mappings` 降低了 `97`
- `reservation_only` 已经略优于 baseline 的运行时间
- `nogood_guard` 仍未表现出正向贡献

### Query: `query_dense_4_10`

| Variant | Result mappings | Partial mappings | Runtime (ms) | 观察 |
| --- | ---: | ---: | ---: | --- |
| Baseline | 12830306 | 12937898 | 50590.13 | 参考线 |
| Reservation only | 12830306 | 12937608 | 75098.38 | 搜索空间略减，但时间显著变差 |
| Nogood only | 12830306 | 12937898 | 102290.66 | 无收益 |
| Full GUP | 12830306 | 12937608 | 105222.99 | 搜索空间略减，但时间显著变差 |

结论：
- 这条 query 很重，结果说明当前 Python 原型的 guard 开销在某些真实 query 上依然非常明显
- 因此当前不能把“优于 baseline”泛化到所有真实 query

## 4. 当前最稳妥的报告表述

建议在报告中使用如下表达：

> Our current `GUP-lite` implementation already shows measurable pruning benefits on real datasets, especially through the reservation guard.
> On some queries from Yeast and Human, the improved reservation guard reduces both the search space and the runtime compared with the baseline.
> However, the improvement is not uniform across all queries, and the current nogood guard remains conservative and ineffective on the tested real workloads.

## 5. 当前阶段性判断

当前可以更有底气地说：

- 复现不是完全失败的
- 当前实现已经在部分真实 query 上开始体现出论文路线的有效性
- 但它仍然是 `GUP-lite`，离论文完整版还有明显差距

更具体地说：

1. `reservation_guard` 已经证明是有效方向
2. `nogood_guard` 仍是主要短板
3. `wordnet / patents` 在当前 Python 原型下仍属于边界实验，而非主结果数据集

## 6. 进一步优化后的补充结论

在加入两个实现层优化后：

1. 候选过滤从纯 label 升级为 `label + degree`
2. guard 检查改为“只在可能命中的 query vertex 上激活”

我们观察到 `human / query_dense_4_10` 的结果明显改善：

| Variant | Partial mappings | Runtime (ms) |
| --- | ---: | ---: |
| Baseline | 12937898 | 49973.50 |
| Reservation only | 12937608 | 55638.53 |
| Nogood only | 12937898 | 37932.96 |
| Full GUP | 12937608 | 41744.04 |

这条结果说明：

- `reservation_guard` 本身仍主要提供搜索空间缩减
- 但在去掉无效 nogood 检查后，`nogood_only` 与 `full GUP` 的运行时间都显著下降
- 因此，之前“full GUP 很慢”的一部分原因来自实现层的空检查开销，而不完全是算法设计本身的问题
