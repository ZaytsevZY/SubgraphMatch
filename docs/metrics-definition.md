# 指标定义

## 1. 文档目的
本文件用于固定课程项目实验中各项指标的统计口径，避免不同脚本、不同组员、不同阶段对结果含义理解不一致。

## 2. 核心指标
课程要求至少统计以下 4 类指标：
- 运行时间（runtime）
- `result mappings` 数量
- `partial mappings` 数量
- 被过滤策略剪枝掉的 `partial mappings` 数量

## 3. 口径定义

### 3.1 result mapping
当查询图的所有顶点都成功映射到数据图，并同时满足：
- 标签约束
- 单射约束
- 边一致性约束

则记为 1 个 `result mapping`。

说明：
- 每个完整合法映射计数 1 次
- 不对同一映射做额外去重逻辑，除非后续论文方法明确涉及等价类压缩

### 3.2 partial mapping
`partial mapping` 指搜索过程中，已经给前 `k` 个查询顶点分配了合法数据顶点、且当前仍满足所有已检查约束的部分映射。

当前 baseline 口径采用：
- **每当一个新顶点成功扩展进当前映射，就记 1 个 partial mapping**
- 空映射不计入 `partial mappings`
- 完整映射同时也属于一次成功扩展，因此会包含在扩展计数轨迹中；但报告时仍单独汇报 `result mappings`

这样做的优点：
- 与 DFS/回溯实现自然一致
- 易于统计搜索空间规模
- 便于后续比较不同过滤策略减少了多少扩展

### 3.3 pruned partial mapping
当某个候选扩展本来将形成一个新的部分映射，但由于过滤策略或约束检查失败而被剪掉时，记为 1 个 `pruned partial mapping`。

当前细分为两类：
- `injectivity_conflict`：违反单射约束
- `edge_conflict`：违反已匹配边约束

后续引入论文策略后，可继续加入：
- 标签/度数预过滤剪枝
- neighborhood consistency 剪枝
- guard / failing set / path-based 剪枝

### 3.4 runtime_ms
`runtime_ms` 定义为 matcher 主搜索过程的墙钟时间，单位毫秒。

当前建议：
- 不把文件读取时间计入主搜索时间
- 单次实验至少记录一次完整匹配调用的耗时
- 如后续有预处理/索引构建，应单独记录 `preprocess_ms`

## 4. 统计对象设计
当前代码中建议用统一统计对象保存：
- 总 `partial_mappings`
- 总 `result_mappings`
- 总 `pruned_partial_mappings`
- 各剪枝原因的计数
- 实际顶点顺序
- 运行时间

## 5. 报告中如何解释
实验部分建议同时解释：
- `result mappings` 反映最终答案规模
- `partial mappings` 反映搜索空间规模
- `pruned partial mappings` 反映剪枝策略有效性
- `runtime_ms` 反映整体执行代价

其中：
- 若两个方法 `result mappings` 相同，但一个 `partial mappings` 明显更少，说明其过滤/顺序策略更有效
- 若 `pruned partial mappings` 更多，同时 `runtime_ms` 更低，通常说明剪枝能抵消额外判断开销
- 若 `pruned partial mappings` 上升但运行时间未下降，说明过滤器成本可能偏高

## 6. 当前 baseline 统计边界
本轮 baseline 的 `pruned partial mappings` 主要来自：
- 查询顶点尝试映射到已使用的数据顶点
- 查询边在数据图中找不到对应边

因此，当前统计结果主要用于：
- 验证计数器框架是通的
- 为后续论文专属过滤策略预留统一计数接口

## 7. 后续扩展原则
后续新增指标时应满足：
- 定义清晰
- 与当前 4 个核心指标不冲突
- 能写入结构化结果文件
- 能在报告中被解释

建议后续可扩展：
- `candidate_vertices_total`
- `candidate_vertices_after_filter`
- `max_search_depth`
- `backtrack_steps`
- `preprocess_ms`
