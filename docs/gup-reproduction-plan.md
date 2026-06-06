# GUP 复现规划

## 1. 文档目的
本文件用于把目标论文 `[14] GUP` 转换成可执行的项目计划，回答以下问题：

- 先实现什么，后实现什么
- 哪些部分是课程必做，哪些属于增强
- 如何把论文方法映射到当前仓库代码结构
- 如何安排后续实验和消融

当前补充背景：
- 已完成一轮论文代码可得性调查。
- 已确认 `GUP` 存在公开 Rust 实现，可作为论文细节和输入输出行为的参考。
- 当前项目仍按“自己实现课程版 `GUP-lite`”推进，而不是直接依赖官方仓库。
- `VF3` 存在官方源码申请入口，可作为备选切换方案，但当前不改变主线。

## 2. 复现目标
本项目对 `GUP` 的复现目标分为三层：

### 2.1 必做目标
- 实现一个正确的 `GUP-lite` 匹配器
- 支持 `reservation guard` 和 `nogood guard`
- 能统计 `runtime_ms`
- 能统计 `result mappings`
- 能统计 `partial mappings`
- 能统计 `pruned partial mappings`
- 能支持 guard 开关式消融

### 2.2 强化目标
- 细分不同 guard 的剪枝来源
- 增加结构化实验输出
- 在 `3-4` 组数据集上跑批量实验
- 输出报告可引用的表格和图

### 2.3 可选增强目标
- 更贴近论文的 guarded candidate space 表达
- 搜索节点紧凑编码
- 并行化

## 3. 当前进度与状态
- 已完成论文选择，当前正式选题为 `[14] GUP`
- 已完成候选论文比较与评分
- 已完成 `GUP` 和 `VF3` 的代码可得性调查
- 已确认当前 baseline、接口规范、指标定义和基础测试可直接复用
- 已有 `gup_matcher.py`、`reservation_guard.py`、`nogood_guard.py` 的第一版实现
- 已开始设计 `GUP-lite` 需要的 guard 接口、matcher 骨架和统计字段
- 当前仍缺少 `GUP` 原文实验部分的完整数据集与查询配置整理

## 3.1 现阶段总原则
- 第一目标不是“逐字还原官方 Rust 代码”，而是做出一个正确、可测、可解释、可消融的课程版 `GUP-lite`。
- 当前仓库中的 guard 实现先视为“第一版近似实现”，后续要逐项验证其与论文定义的贴合程度。
- 任何新增优化都不能破坏现有四个核心指标的统计口径。

## 4. 论文方法拆分
为了降低实现风险，建议把 GUP 拆成以下模块。

### 4.1 Baseline 复用部分
- 图加载
- 基础候选集生成
- 基础顶点匹配顺序
- 回溯搜索框架
- 核心统计对象

这些已经在当前仓库中具备初始版本。

### 4.2 需要新增的 GUP 模块

#### 模块 A：Guard 接口
目标：
- 统一表示“某次扩展是否应被 guard 剪掉”
- 统一记录 guard 名称和 prune 次数

建议接口职责：
- 输入当前 `SearchState`
- 输入待尝试的查询顶点与数据顶点扩展
- 返回是否剪枝以及剪枝原因

#### 模块 B：Reservation Guard
目标：
- 在扩展前检查当前部分映射是否破坏某个候选扩展后续所需的保留顶点

第一版建议：
- 先做可解释、易调试的实现
- 先不追求最紧凑的数据结构

#### 模块 C：Nogood Guard
目标：
- 记录已知失败模式
- 当前状态命中失败模式时提前剪枝

第一版建议：
- 先支持简单而清晰的 nogood 记录方式
- 先把“正确剪掉”做出来，再考虑压缩存储

#### 模块 D：Guard 统计
目标：
- 给课程实验和报告提供可解释的指标

建议字段：
- `pruned_by_reservation_guard`
- `pruned_by_nogood_guard_vertex`
- `pruned_by_nogood_guard_edge`
- `guard_checks_total`

#### 模块 E：配置与消融
目标：
- 用统一配置控制哪些 guard 启用
- 支持自动跑消融实验

建议开关：
- `enable_reservation_guard`
- `enable_nogood_guard_vertex`
- `enable_nogood_guard_edge`

## 5. 代码结构映射
建议按如下路径落代码：

- `src/subgraph_match/filters/`
- `reservation_guard.py`
- `nogood_guard.py`
- `base.py`
- `src/subgraph_match/matchers/`
- `gup_matcher.py`
- `src/subgraph_match/metrics/`
- 在 `stats.py` 中扩展 guard 统计字段
- `src/subgraph_match/experiments/`
- 后续加入 GUP 专属实验配置

## 6. 建议实现顺序

### 第 1 步：接好 guard 扩展点
- 在当前 matcher 中预留扩展前检查钩子
- 统一 prune reason 的记录方式
- 保证 baseline 行为不被破坏

### 第 2 步：实现 Reservation Guard
- 先在 toy graph 上验证 guard 能起作用
- 补最小单元测试
- 确认计数是否进入统一统计对象

### 第 3 步：实现 Nogood Guard
- 先做简单版本
- 在失败回溯时记录 nogood
- 在后续扩展中进行命中检查

### 第 4 步：做 GUP-lite 集成
- 新建 `gup_matcher.py`
- 跑通 end-to-end
- 输出与 baseline 可比较的统计结果

当前状态：
- 该步骤已经有雏形代码，但还缺正确性回归测试、配置测试和 guard 行为解释文档。

### 第 5 步：加入消融配置
- baseline
- `+reservation`
- `+nogood`
- `+reservation+nogood`

### 第 6 步：准备正式实验
- 选 `3-4` 组数据集和查询集
- 固定输出表结构
- 批量运行并落盘

## 6.1 2026-06-07 之后的分阶段路线

### Phase A: 收口第一版正确性
目标：让 `GUP-lite` 在 toy graph 上稳定跑通，并能与 baseline 对齐最终匹配结果。

本阶段必须完成：
- 为 `GUPMatcher` 补 `unittest`
- 验证 guard 开启后 `result mappings` 不变
- 验证至少一个 toy case 上 `pruned_partial_mappings` 高于 baseline
- 明确当前 `reservation_guard` 和 `nogood_guard` 分别近似论文中的哪一部分

交付物：
- `tests/test_gup_matcher.py`
- guard 行为说明补充到文档

当前状态：
- 已新增 `tests/test_gup_matcher.py`
- 已验证：关闭 guard 时，`GUPMatcher` 与 baseline 的结果和核心统计一致
- 已验证：开启全部 guard 时，toy path 样例上的 `result mappings` 不变
- 已验证：`reservation_guard` 在一个构造的 dead-end 三角查询上能比 baseline 更早剪枝
- 已验证：`nogood_guard` 已从“精确前缀 memo”升级为“未来子问题 memo”，并能在一个断开组件样例上复用 dead-end
- 在当前构造样例上，`nogood_guard` 将 `partial_mappings` 从 `19` 降到 `12`，并产生 `3` 次明确的 `nogood_guard` 命中
- 当前仍需注意：在 toy 级别样例上，搜索空间下降不一定立刻带来更低的 `runtime_ms`，因为 guard 检查本身也有开销

### Phase B: 固定课程实验版接口
目标：让 GUP 的不同 guard 能以统一配置开关运行，并把统计结果结构化落盘。

本阶段必须完成：
- `GUPConfig` 增加更细的 guard 开关
- `MatchStatistics` 明确区分不同 guard 的命中次数
- 单次实验结果输出为 JSON/CSV 可落盘结构

交付物：
- `scripts/run_gup_experiment.py`
- `results/raw/` 下的样例结果文件

当前状态：
- 已新增 `scripts/run_gup_experiment.py`
- 已支持 `baseline` / `gup` 两类单次运行
- 已支持 `reservation guard` / `nogood guard` 开关配置
- 已支持将单次运行结果写入 `results/raw/*.json`
- 已新增 `scripts/run_gup_batch.py`，支持标准消融配置的批量运行
- 已新增 `scripts/summarize_results.py`，可将 `results/raw/*.json` 汇总为 `results/tables/summary.csv`
- 已支持使用 `run_tag` 区分不同批次实验，并按 `glob-pattern` 定向生成单批次汇总表
- 当前下一步是把 toy 示例切换为正式数据集与查询集

### Phase C: 还原论文实验设置
目标：确定 3-4 组正式实验数据，并把查询规模、超时阈值、对比基线写入文档。

本阶段必须完成：
- 补完 `GUP` 原文实验部分摘要
- 固定课程报告里实际使用的数据集和查询集
- 设计 guard 消融矩阵

交付物：
- 数据集清单文档
- 消融矩阵表

当前状态：
- 已新增 `docs/gup-experiment-datasets.md`
- 已正式明确课程主方案为 `Yeast-24S / Human-24S / WordNet-16D / Patents-8S`
- 已明确正式数据下载需要人工完成一次
- 已新增官方 GUP 输入格式读取器
- 已让 `scripts/run_gup_experiment.py` 支持 `.vertices/.edges` + YAML query set + `query_index`
- 当前还未把正式 query set 的“逐条批量运行”接到 `run_gup_batch.py`
- 已新增 `.graph` 读取器
- 已新增 `scripts/run_query_set_batch.py`，可按 `query_glob` 批量运行真实 `.graph` 查询文件
- 已新增 `configs/gup_real_workloads.yaml` 作为当前课程项目的真实 workload 清单
- 已为真实实验脚本增加 `timeout_sec` 支持，可将过重 query 记录为 `timeout` 而不是无界运行
- 已完成一轮跨数据集 dense-4 smoke，用于识别当前 Python 原型的可跑性边界
- 已将 `reservation_guard` 从运行时前向检查改为预计算 reservation set 的课程版近似实现
- 改进后在 `yeast/human` 的部分真实 query 上开始体现更接近论文方向的收益

### Phase D: 正式实验与报告素材
目标：生成报告可直接引用的表格、图和结论草稿。

本阶段必须完成：
- 批量运行 baseline / reservation / nogood / full GUP-lite
- 汇总 runtime、result mappings、partial mappings、pruned partial mappings
- 输出报告图表草稿

## 7. 测试策略
建议测试分三层：

### 6.1 正确性测试
- GUP 在 toy graph 上的结果与 baseline 一致
- 开启 guard 后不应改变最终 `result mappings`

### 6.2 统计测试
- `partial mappings` 会记录
- `pruned partial mappings` 会增加
- 不同 guard 的 prune 字段能区分开

### 6.3 配置测试
- 关闭全部 guard 时，行为退化为接近 baseline
- 单独开启某一 guard 时，结果仍正确

## 8. 实验计划

### 7.1 必做实验
- 在 `3-4` 组数据集上运行 `GUP-lite`
- 统计：
- `runtime_ms`
- `result_mappings`
- `partial_mappings`
- `pruned_partial_mappings`

### 7.2 消融实验
建议至少包含：

1. `Baseline`
2. `GUP-lite (reservation only)`
3. `GUP-lite (nogood only)`
4. `GUP-lite (reservation + nogood)`

### 7.3 可选补充分析
- 不同 guard 的 prune 占比
- 查询规模变化时的趋势
- guard 检查开销与收益对比

当前实验准备状态：
- 课程要求中的四类核心指标口径已在仓库中固定
- 正式数据集与查询集尚未锁定
- 下一步应优先从论文实验部分还原出 `3-4` 组可执行组合

## 9. 两人分工建议

### 成员 A
- 整理论文阅读笔记
- 整理数据集与查询来源
- 维护实验脚本与结果表
- 撰写报告相关章节

### 成员 B
- 实现 `gup_matcher`
- 实现 reservation/nogood guard
- 接入统计与测试
- 调试性能和正确性

### 共同负责
- 确定消融矩阵
- 核对指标定义
- 分析实验结果
- 准备答辩

## 10. 近期待办
- 补充 `GUP` 实验部分的具体数据集和查询配置
- 在 `filters/` 下建立 guard 模块骨架
- 设计 guard 统计字段
- 新建 `gup_matcher.py`
- 补一组最小测试用例

## 10.1 当前最近三天的具体任务

### 2026-06-07
- 正式锁定 `GUP`
- 收口文档中的“待确认”状态
- 盘点现有 `GUP-lite` 雏形代码与缺口

### 2026-06-08
- 补 `GUPMatcher` 单元测试
- 校验 guard 启用 / 关闭时的结果一致性
- 补最小实验脚本

### 2026-06-09
- 整理论文实验设置
- 固定正式数据集与消融矩阵
- 开始首轮真实实验

## 11. 当前结论
当前项目已经完成“论文选择”阶段，正式进入 `GUP` 复现阶段。

后续实现策略应坚持三点：

- 先正确，再优化
- 先可统计，再扩展
- 先做 `GUP-lite`，再贴近论文完整版

同时需要保持一个现实判断：
- 当前 `GUP` 的实现路径以“自主实现”为主，而不是“直接复用官方 Rust 代码”
- 若后续实现风险显著升高，`VF3` 是最可行的源码型备选
