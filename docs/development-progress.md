# 开发进度

## 项目基本信息
- 课程：`现代数据库系统概论`
- 选题：`选题 2 - 子图匹配`
- 小组人数：`2`
- 当前阶段：`GUP 已选定 / 已完成代码可得性调查 / 进入 GUP-lite 设计阶段`

## 里程碑看板
| 里程碑 | 目标 | 当前状态 | 说明 |
| --- | --- | --- | --- |
| M0 | 阅读作业要求并确认选题 | 已完成 | 已确认为子图匹配 |
| M1 | 完善仓库骨架与项目文档 | 已完成 | `README`、计划、进度文档已建立 |
| M2 | 选择复现论文 | 已完成 | 已确定目标论文为 `[14] GUP` |
| M3 | 固定图输入格式和指标定义 | 已完成 | 已新增 `docs/interface-spec.md` 和 `docs/metrics-definition.md` |
| M4 | 实现图解析与基础数据结构 | 已完成 | 当前支持无向带标签图的 toy 数据读取与基础操作 |
| M5 | 实现基础匹配与计数器 | 已完成 | 已提供 baseline 回溯 matcher、统计对象和样例测试 |
| M6 | 实现论文过滤策略与消融开关 | 进行中 | 已建立 `GUP-lite` 设计方向，待完成代码与测试闭环 |
| M7 | 运行 3-4 组数据集实验 | 待开始 | 输出图表和表格 |
| M8 | 完成英文报告和汇报材料 | 待开始 | 包括组内分工和复现说明 |
| M9 | 调查论文代码可得性 | 已完成 | 已确认 `VF3` 有官方源码入口，`GUP` 暂未发现公开仓库 |

## 当前已完成内容
- 已阅读课程要求与个性化要求
- 已确认项目选题为 `子图匹配`
- 已建立基础目录结构
- 已准备样例图文件 `data/sample/toy_graph.txt`
- 已补充样例查询图 `data/sample/toy_query_path.txt`
- 已提供可运行 baseline 脚本 `scripts/run_experiment.py`
- 已新增接口规范文档 `docs/interface-spec.md`
- 已新增指标定义文档 `docs/metrics-definition.md`
- 已实现 `BacktrackingMatcher`、搜索状态、候选集生成与顶点顺序模块
- 已实现 `MatchStatistics`，可统计 `result/partial/pruned partial mappings`
- 已补充 `unittest` 测试 `tests/test_backtracking_matcher.py`
- 已建立调研、计划、报告大纲等文档
- 已完成候选论文比较并确定目标论文为 `GUP`
- 已在 `docs/literature-review/paper-selection.md` 中写出选择理由和推荐顺序
- 已完成候选论文代码可得性调查
- 已确认 `VF3` 存在官方源码入口，但需要注册后申请下载
- 已确认 `GUP` 当前未查到明确公开仓库，因此默认走“自己实现课程版”的路线
- 已开始设计 `GUP-lite` 所需的 guard 接口、统计字段和 matcher 骨架

## 当前进行中
- 规划 `GUP` 的 guard 如何映射到当前 matcher 结构
- 设计 `GUP` 的模块拆分与实现顺序
- 整理 `GUP` 原文实验部分中的数据集、查询规模和对比基线
- 设计实验结果落盘与后续批量运行接口

## 下一个工作周期任务
| 优先级 | 任务 | 负责人 | 状态 | 输出 |
| --- | --- | --- | --- | --- |
| 高 | 固定 `GUP-lite` 的最小实现范围 | 全组 | 进行中 | guard 模块清单 |
| 高 | 整理 `GUP` 实验部分的数据集和查询配置 | 成员 A | 进行中 | 数据集清单 |
| 高 | 将 guard 设计成开关式接口 | 成员 B | 进行中 | `src/subgraph_match/filters/` |
| 高 | 为 matcher 增加 guard 统计钩子 | 成员 B | 进行中 | `src/subgraph_match/matchers/` |
| 中 | 设计 `GUP` 实验结果输出文件格式 | 全组 | 待开始 | CSV/JSON 字段草案 |
| 中 | 规划 guard 消融顺序 | 全组 | 待开始 | 消融实验矩阵 |
| 中 | 准备 `3-4` 组数据集及查询来源 | 全组 | 待开始 | 数据集清单 |
| 低 | 建立会议纪要和分工记录 | 全组 | 待开始 | `docs/meeting-notes/` |

## 风险记录
- 论文不同会直接影响实现复杂度和实验周期
- 一些论文的查询集生成方法可能需要额外还原
- `partial mapping` 的计数定义必须从一开始固定
- 若目标算法性能要求较高，后续可能需要局部优化甚至换语言
- `GUP` 暂无公开实现可直接复用，因此论文细节理解错误会直接影响实现进度
- `VF3` 虽然有官方源码，但获取方式依赖注册和申请，不是即时可下载的 GitHub 仓库

## 决策记录
- 2026-06-05：确认选题为 `子图匹配`
- 2026-06-05：确认当前团队人数为 `2`
- 2026-06-05：完成项目目录骨架与首批文档初始化
- 2026-06-05：确定先以 Python 原型推进，实现正确性优先的复现框架
- 2026-06-05：固定 baseline 接口与核心指标口径，后续论文实现应尽量复用当前 matcher/metrics 结构
- 2026-06-05：当前测试体系采用 `unittest`，避免额外依赖 `pytest`
- 2026-06-05：正式确定复现论文为 `[14] GUP`
- 2026-06-05：完成候选论文代码可得性调查，确认 `VF3` 有官方源码申请入口
- 2026-06-05：确认 `GUP` 暂未发现明确公开仓库，主线改为“自己实现 GUP-lite”

## 本轮实现摘要
- 新增接口规范文档：`docs/interface-spec.md`
- 新增指标定义文档：`docs/metrics-definition.md`
- 新增 baseline matcher：`src/subgraph_match/matchers/backtracking_matcher.py`
- 新增候选集、顺序和状态模块：`src/subgraph_match/matching/`
- 新增统计对象：`src/subgraph_match/metrics/stats.py`
- 新增 toy query 样例：`data/sample/toy_query_path.txt`
- 新增回归测试：`tests/test_backtracking_matcher.py`
- 新增 `GUP` 相关文档：`docs/gup-reproduction-plan.md`、`docs/literature-review/notes-paper-14.md`
- 补充论文比较与代码可得性调查：`docs/literature-review/paper-selection.md`

## 建议下一步
1. 先补齐 `GUP` 原文实验部分，固定数据集、查询集和对比指标。
2. 实现一个 `GUP-lite` 版本，优先打通 `reservation guard` 和 `nogood guard` 的基本流程。
3. 把 guard 过滤逻辑拆到 `filters/` 并接入统一 prune 计数。
4. 建立批量实验脚本，把单次运行结果写入 `results/raw/`。