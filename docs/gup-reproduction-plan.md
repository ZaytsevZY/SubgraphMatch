# GUP 复现规划

## 1. 文档目的
本文件用于把目标论文 `[14] GUP` 转换成可执行的项目计划，回答以下问题：

- 先实现什么，后实现什么
- 哪些部分是课程必做，哪些属于增强
- 如何把论文方法映射到当前仓库代码结构
- 如何安排后续实验和消融

当前补充背景：
- 已完成一轮论文代码可得性调查。
- 当前未发现 `GUP` 的明确公开仓库，因此本规划默认按“自己实现课程版 `GUP-lite`”推进。
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
- 已开始设计 `GUP-lite` 需要的 guard 接口、matcher 骨架和统计字段
- 当前仍缺少 `GUP` 原文实验部分的完整数据集与查询配置整理

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

### 第 5 步：加入消融配置
- baseline
- `+reservation`
- `+nogood`
- `+reservation+nogood`

### 第 6 步：准备正式实验
- 选 `3-4` 组数据集和查询集
- 固定输出表结构
- 批量运行并落盘

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

## 11. 当前结论
当前项目已经完成“论文选择”阶段，正式进入 `GUP` 复现阶段。

后续实现策略应坚持三点：

- 先正确，再优化
- 先可统计，再扩展
- 先做 `GUP-lite`，再贴近论文完整版

同时需要保持一个现实判断：
- 当前 `GUP` 的实现路径以“自主实现”为主，而不是“下载现成代码”
- 若后续实现风险显著升高，`VF3` 是最可行的源码型备选