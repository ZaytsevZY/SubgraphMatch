# 当前结果摘要

## 1. 当前是否算复现成功

当前更准确的说法是：

- 已成功实现一个可运行的 `GUP-lite` 原型
- 已成功在 toy 数据和部分真实数据上跑通
- 已支持 `baseline / reservation only / nogood only / full GUP` 的消融对比
- 但当前还不能声称已经完整复现论文中的 `GuP` 工程实现

因此，当前阶段最合适的表述是：

> 已完成 `GuP` 核心思想的课程版复现，但仍属于 `GUP-lite`，不是论文完整版实现。

## 2. 当前真实数据上的主要结论

### 2.1 Yeast 与 Human

在当前已完成的真实对比中，`reservation_guard` 已经表现出稳定但有限的搜索空间缩减效果。

#### Yeast / query_dense_4_10
- baseline: `partial_mappings = 22731`, `runtime_ms ≈ 549.02`
- reservation_only: `22286`, `≈ 559.36`
- nogood_only: `22731`, `≈ 604.73`
- full GUP: `22286`, `≈ 599.83`

结论：
- `reservation_guard` 将 `partial_mappings` 降低了 `445`（约 `1.96%`）
- 但当前 Python 原型的运行时间并未优于 baseline

#### Yeast / query_dense_4_1
- baseline: `partial_mappings = 777`, `runtime_ms ≈ 13.17`
- reservation_only: `772`, `≈ 14.33`
- nogood_only: `777`, `≈ 15.38`
- full GUP: `772`, `≈ 15.65`

结论：
- `reservation_guard` 将 `partial_mappings` 降低了 `5`（约 `0.64%`）
- `nogood_guard` 未体现收益

#### Human / query_dense_4_1
- baseline: `partial_mappings = 11013`, `runtime_ms ≈ 169.59`
- reservation_only: `10916`, `≈ 203.85`
- nogood_only: `11013`, `≈ 216.40`
- full GUP: `10916`, `≈ 230.24`

结论：
- `reservation_guard` 将 `partial_mappings` 降低了 `97`（约 `0.88%`）
- `nogood_guard` 仍未体现收益

### 2.2 WordNet 与 Patents

在当前 Python 原型与 `120` 秒 timebox 下：

- `WordNet / query_dense_4_1`：`timeout`
- `Patents / query_dense_4_1`：`timeout`
- `WordNet / query_sparse_8_15`：`timeout`
- `Patents / query_sparse_8_15`：`timeout`

结论：
- 当前原型已经摸到了真实 workload 的可跑边界
- `WordNet` 和 `Patents` 对当前 Python 实现仍明显偏重

## 3. 当前最稳妥的结论

### 3.1 能说“比 baseline 好一点”吗

可以，但必须限定在“搜索空间指标”上。

当前可以稳妥地说：

- `reservation_guard` 已经在真实数据上降低了 `partial_mappings`
- 因此，当前 `GUP-lite` 在“搜索空间”上已经优于 baseline 一点

### 3.2 能说“运行时间优于 baseline”吗

当前还不能。

目前的情况是：

- 搜索空间缩小了
- 但 guard 检查带来的开销仍然较大
- 因此 wall-clock time 尚未稳定优于 baseline

### 3.3 当前哪个 guard 真正有效

当前结论非常清楚：

- `reservation_guard`：有效
- `nogood_guard`：在 toy 构造样例上有效，但在当前真实 query 上尚未体现稳定收益

## 4. 当前最适合写进报告的说法

建议当前报告中使用如下表述：

> We implemented a correctness-first `GUP-lite` prototype that captures the core idea of guard-based pruning.
> On real datasets such as Yeast and Human, the current implementation already reduces the search space, mainly due to the reservation guard.
> However, the current Python prototype does not yet consistently outperform the baseline in wall-clock time, because the guard overhead is still nontrivial and the nogood guard remains conservative.

## 5. 对后续实验的建议

当前应采用分层实验策略：

1. `Yeast / Human`：继续作为主结果数据集，完成完整对比与消融
2. `WordNet / Patents`：先作为 timeboxed smoke 或边界实验写入报告
3. 若想在 `WordNet / Patents` 上拿到非 timeout 结果，需要进一步降低 workload，或提升实现性能

## 6. 2026-06-07 改进后的最新观察

在将候选过滤升级为 `label + degree`，并把 `reservation_guard` 从运行时前向检查改为“小型预计算 reservation set”之后，结果出现了更积极的变化。

### 6.1 Human / query_dense_4_1
- baseline: `partial_mappings = 11013`, `runtime_ms ≈ 191.82`
- reservation_only: `10916`, `≈ 172.20`
- full GUP: `10916`, `≈ 204.48`

当前解释：
- `reservation_guard` 仍然将 `partial_mappings` 降低了 `97`
- 更重要的是，`reservation_only` 的运行时间已经接近并略优于 baseline
- `nogood_guard` 依旧没有体现收益，并会拉高整体时间

### 6.2 Yeast / query_dense_4_10
- baseline: `partial_mappings = 22624`, `runtime_ms ≈ 805.71`
- reservation_only: `22283`, `≈ 741.69`
- full GUP: `22283`, `≈ 770.27`

当前解释：
- `reservation_guard` 将 `partial_mappings` 降低了 `341`
- 这一次 `reservation_only` 与 `full GUP` 都已经在 wall-clock time 上优于 baseline
- 说明当前改进后的 `reservation_guard` 已经开始真正体现论文路线的效果

### 6.3 Human / query_dense_4_10 after guard-selective optimization
- baseline: `partial_mappings = 12937898`, `runtime_ms ≈ 49973.50`
- reservation_only: `12937608`, `≈ 55638.53`
- nogood_only: `12937898`, `≈ 37932.96`
- full GUP: `12937608`, `≈ 41744.04`

当前解释：
- `reservation_guard` 仍然只能小幅减少搜索空间（降低 `290` 个 `partial_mappings`）
- 但将 `nogood_guard` 改成“只在相关 query vertex 上激活”之后，`nogood_only` 不再是纯负担
- 更重要的是，`full GUP` 已经在该真实重 query 上明显优于 baseline 的 wall-clock time

这说明：

1. 之前 `full GUP` 很慢，确实有一部分是实现层的空检查开销，而不是算法路线本身的问题
2. 当前 `nogood_guard` 虽然仍然没有体现强 pruning，但在去掉无效检查后，不再像之前那样严重拖累运行时间

### 6.4 当前最新判断

最新结果比上一轮更乐观：

- 之前的结论是“只在搜索空间上略好，但时间还没打赢 baseline”
- 现在的结论应改为：

> 改进后的 `reservation_guard` 已经在部分真实查询上同时减少搜索空间，并开始在运行时间上优于 baseline。
> 此外，经过 guard-selective 优化后，`full GUP` 在某些较重的真实 query 上也开始明显优于 baseline。

但仍需保留两个限定：

1. 当前收益仍然主要来自 `reservation_guard`
2. `nogood_guard` 在真实数据上依旧保守，尚未带来稳定增益
