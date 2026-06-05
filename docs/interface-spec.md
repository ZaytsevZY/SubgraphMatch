# 接口规范

## 1. 文档目的
本文件用于固定课程项目中“图输入格式、匹配器接口、实验输出结构”的统一约定。
后续无论切换论文方案、补过滤策略，还是多人并行开发，都应尽量保持这些接口稳定。

## 2. 图模型约定

### 2.1 问题类型
当前项目默认处理：
- **带顶点标签的无向图**
- **精确子图匹配（subgraph isomorphism）**
- 查询图到数据图的映射要求为**单射**

### 2.2 顶点与边
- 顶点 ID：使用整数表示
- 顶点标签：使用字符串表示
- 边：当前按无向边处理
- 不允许平行边
- 默认不考虑边标签

### 2.3 内存结构
当前统一使用 `LabeledGraph` 表示图：
- `labels: Dict[int, str]`
- `adjacency: Dict[int, Set[int]]`

后续如需支持更复杂属性，应尽量通过扩展字段实现，而不是破坏现有接口。

## 3. 图文件格式约定

### 3.1 文本格式
当前统一使用简单文本格式：

```text
# comment
v <vertex_id> <label>
e <src> <dst>
```

示例：

```text
v 1 A
v 2 B
v 3 A
e 1 2
e 2 3
```

### 3.2 解析约束
- 以 `#` 开头的行为注释
- 空行忽略
- `v` 表示顶点记录
- `e` 表示边记录
- 顶点应先于依赖它的语义使用出现
- 当前不支持边标签与图名称头部

### 3.3 目录约定
- 数据图：`data/raw/` 或 `data/processed/`
- 查询图：`data/queries/`
- 调试样例：`data/sample/`

## 4. 匹配器接口约定

### 4.1 输入
一个 matcher 至少接收：
- 数据图 `data_graph: LabeledGraph`
- 查询图 `query_graph: LabeledGraph`
- 可选配置 `ExperimentConfig` 或 matcher 专属参数

### 4.2 输出
matcher 应返回一个结果对象，至少包含：
- `mappings`: 最终匹配结果列表
- `statistics`: 匹配过程统计信息
- `vertex_order`: 实际使用的查询顶点顺序

### 4.3 统一结果结构
建议统一使用：
- `MatchResult`
- `MatchStatistics`
- `SearchState`

避免直接在脚本层返回松散字典，方便后续扩展与测试。

## 5. baseline matcher 设计约定
当前 baseline 采用“标签过滤 + 固定顺序 + 回溯搜索”的正确性优先方案。

### 5.1 处理流程
1. 为每个查询顶点构造初始候选集（按标签过滤）
2. 根据候选集大小和度数生成查询顶点匹配顺序
3. 深度优先扩展 `partial mapping`
4. 每步检查：
   - 标签一致性
   - 单射约束
   - 已匹配邻接约束
5. 找到完整映射后记录为一个 `result mapping`

### 5.2 模块边界
- `matching/candidate.py`：候选集生成
- `matching/order.py`：查询顶点顺序
- `matching/state.py`：搜索状态
- `matchers/backtracking_matcher.py`：搜索主体
- `metrics/stats.py`：计数器与统计信息

## 6. 过滤策略扩展约定
后续论文中的过滤策略应遵循以下原则：
- 每个策略尽量可单独启停
- 每个策略应有唯一名称
- 每个策略要能统计自己的 prune 次数
- 策略尽量在统一检查接口下运行

建议未来扩展为：
- 预过滤（候选集裁剪）
- 搜索时过滤（扩展前剪枝）
- 匹配顺序优化

## 7. 实验输出字段约定
单次运行结果建议至少包含：
- `dataset_name`
- `query_name`
- `matcher_name`
- `runtime_ms`
- `result_mappings`
- `partial_mappings`
- `pruned_partial_mappings`
- `vertex_order`
- `enabled_filters`
- `notes`

批量实验阶段可在此基础上扩展 CSV/JSON 输出。

## 8. 当前不做的内容
本轮先不实现：
- 边标签
- 有向图
- 子图同态
- 增量维护
- 并行搜索
- 大规模索引结构

这些内容如后续需要，应在不破坏 baseline 接口的前提下逐步扩展。
