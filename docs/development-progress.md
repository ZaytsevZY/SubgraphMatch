# 开发进度

## 项目基本信息
- 课程：`现代数据库系统概论`
- 选题：`选题 2 - 子图匹配`
- 小组人数：`2`
- 当前阶段：`GUP 已正式选定 / 进入自主复现实施阶段`

## 里程碑看板
| 里程碑 | 目标 | 当前状态 | 说明 |
| --- | --- | --- | --- |
| M0 | 阅读作业要求并确认选题 | 已完成 | 已确认为子图匹配 |
| M1 | 完善仓库骨架与项目文档 | 已完成 | `README`、计划、进度文档已建立 |
| M2 | 选择复现论文 | 已完成 | 已正式确定目标论文为 `[14] GUP` |
| M3 | 固定图输入格式和指标定义 | 已完成 | 已新增 `docs/interface-spec.md` 和 `docs/metrics-definition.md` |
| M4 | 实现图解析与基础数据结构 | 已完成 | 当前支持无向带标签图的 toy 数据读取与基础操作 |
| M5 | 实现基础匹配与计数器 | 已完成 | 已提供 baseline 回溯 matcher、统计对象和样例测试 |
| M6 | 实现论文过滤策略与消融开关 | 进行中 | 已建立 `GUP-lite` 设计方向，待完成代码与测试闭环 |
| M7 | 运行 3-4 组数据集实验 | 待开始 | 输出图表和表格 |
| M8 | 完成英文报告和汇报材料 | 待开始 | 包括组内分工和复现说明 |
| M9 | 调查论文代码可得性 | 已完成 | 已确认 `DAF`、`GUP`、`CECI`、`VF3` 均存在公开代码入口 |

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
- 已完成候选论文比较并正式确定目标论文为 `GUP`
- 已在 `docs/literature-review/paper-selection.md` 中写出选择理由和推荐顺序
- 已完成候选论文代码可得性调查
- 已确认 `DAF`、`GUP`、`CECI`、`VF3` 均存在公开代码入口
- 已确认 `GUP` 有公开 Rust 实现，但当前课程仓库仍更适合走“参考论文与官方实现，自行做课程版复现”的路线
- 已开始预研 `GUP-lite` 所需的 guard 接口、统计字段和 matcher 骨架
- 已补充 `GUPMatcher` 回归测试，覆盖 guard 开关、结果一致性和 reservation guard 死路提前剪枝
- 已改进 `nogood_guard` 的状态签名，使其能复用“未来子问题”的 dead-end 信息
- 已补充 `nogood_guard` 收益样例测试，验证其可减少 `partial mappings`
- 已新增单次实验脚本 `scripts/run_gup_experiment.py`
- 已验证 baseline / GUP 样例结果可写入 `results/raw/` JSON 文件
- 已新增批量实验脚本 `scripts/run_gup_batch.py`
- 已新增结果汇总脚本 `scripts/summarize_results.py`
- 已验证 `results/raw/*.json` 可汇总为 `results/tables/summary.csv`
- 已支持使用 `run_tag` 为批量实验分批次命名，并按模式汇总单个批次结果
- 已整理 GUP 论文实验数据与查询集方案：`docs/gup-experiment-datasets.md`
- 已明确课程项目推荐主方案：`Yeast-24S / Human-24S / WordNet-16D / Patents-8S`
- 已明确正式数据下载需要人工完成一次，并约定原始数据放置目录为 `data/raw/gup-paper/`
- 已新增官方 GUP 格式读取器，支持 `.vertices/.edges` 数据图与 YAML query set
- 已补充 GUP 官方格式样例与测试，当前在无 `PyYAML` 环境下也可读取
- 已让 `scripts/run_gup_experiment.py` 支持官方 GUP 输入格式与 `query_index`
- 已验证官方格式 smoke test 可运行并写出 JSON 结果
- 已确认下载数据包中包含 `yeast / human / wordnet / patents` 四个目标数据集
- 已新增 `.graph` 读取器，并验证真实数据 smoke test 可运行
- 已新增真实 workload 清单：`configs/gup_real_workloads.yaml`
- 已为单次和批量实验脚本增加 `timeout_sec` 支持
- 已完成跨数据集真实 dense-4 smoke：`yeast/human` 成功，`wordnet/patents` 在 `120s` 下超时
- 已补 `human dense-4` 的完整 ablation 对比
- 已新增报告式结果表：`results/tables/gup_real_ablation_report_table.csv`
- 已新增当前结果摘要：`docs/current-results-summary.md`
- 已将 `reservation_guard` 升级为预计算小型 reservation set 版本
- 改进后在 `yeast/human` 的部分真实 query 上开始同时降低搜索空间和运行时间
- 已新增报告结果草稿：`docs/report-results-draft.md`
- 已新增英文实验分析草稿：`docs/report-experimental-analysis-draft.md`
- 已生成终版报告主表：`results/tables/final_report_main_table.csv`
- 已生成终版 Markdown 报告表：`results/tables/final_report_main_table.md`
- 已新增英文结论与讨论草稿：`docs/report-conclusion-discussion-draft.md`
- 已新增英文实现细节草稿：`docs/report-implementation-details-draft.md`
- 已将 guard 检查改为按 query vertex 激活，减少无效 nogood 检查
- `human/query_dense_4_10` 上的 `full GUP` 现已优于 baseline

## 当前进行中
- 规划 `GUP` 的 guard 如何映射到当前 matcher 结构
- 设计 `GUP` 的实现落地路径与阶段交付边界
- 整理 `GUP` 原文实验部分中的数据集、查询规模和对比基线
- 设计实验结果落盘与后续批量运行接口
- 评估当前 `nogood_guard` 与论文定义的差距，并准备下一轮修正
- 规划官方 `.vertices/.edges` + YAML query set` 输入如何接入当前代码`
- 规划如何把 `run_gup_batch.py` 升级为读取 query set 后逐 query 批量运行

## 下一个工作周期任务
| 优先级 | 任务 | 负责人 | 状态 | 输出 |
| --- | --- | --- | --- | --- |
| 高 | 固定 `GUP-lite` 的阶段交付边界 | 全组 | 进行中 | 分阶段实现清单 |
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
- `GUP` 虽然已有公开 Rust 实现，但若最终选它，语言迁移和细节理解仍会直接影响实现进度

## 决策记录
- 2026-06-05：确认选题为 `子图匹配`
- 2026-06-05：确认当前团队人数为 `2`
- 2026-06-05：完成项目目录骨架与首批文档初始化
- 2026-06-05：确定先以 Python 原型推进，实现正确性优先的复现框架
- 2026-06-05：固定 baseline 接口与核心指标口径，后续论文实现应尽量复用当前 matcher/metrics 结构
- 2026-06-05：当前测试体系采用 `unittest`，避免额外依赖 `pytest`
- 2026-06-05：完成候选论文比较，当前推荐 `[14] GUP`
- 2026-06-05：完成候选论文代码可得性调查，确认 `DAF`、`GUP`、`CECI`、`VF3` 均有公开代码入口
- 2026-06-05：确认 `GUP` 虽有公开 Rust 实现，但当前课程主线仍以“参考官方实现，自行做 GUP-lite 复现”为宜
- 2026-06-07：正式锁定复现论文为 `[14] GUP`
- 2026-06-07：确认后续主线从“候选方案设计”切换为“GUP 自主复现实施”

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
- 新增 `GUPMatcher` 测试：`tests/test_gup_matcher.py`
- 更新 matcher 导出：`src/subgraph_match/matchers/__init__.py`
- 改进 `nogood_guard`：`src/subgraph_match/filters/nogood_guard.py`
- 新增单次实验脚本：`scripts/run_gup_experiment.py`
- 生成样例原始结果：`results/raw/20260607-004620_toy_graph_toy_query_path_*.json`
- 新增批量实验脚本：`scripts/run_gup_batch.py`
- 新增结果汇总脚本：`scripts/summarize_results.py`
- 生成汇总表：`results/tables/summary.csv`
- 生成分批次汇总表：`results/tables/toy-batch-20260607-summary.csv`
- 新增数据集方案文档：`docs/gup-experiment-datasets.md`
- 新增原始数据放置说明：`data/raw/README.md`
- 新增 GUP 官方格式样例：`data/sample/gup_example.*`、`data/sample/gup_query_set.yaml`
- 新增 GUP IO 测试：`tests/test_gup_io.py`
- 新增官方格式 smoke 结果：`results/raw/gup-format-smoke.json`
- 新增 `.graph` IO 测试：`tests/test_graph_format_io.py`
- 新增真实 workload 清单：`configs/gup_real_workloads.yaml`
- 新增真实数据 smoke 结果：`results/raw/yeast-query-dense-4-23-smoke.json`
- 新增真实批量 smoke 汇总：`results/tables/real-smoke-yeast-d4-summary.csv`
- 新增跨数据集 smoke 汇总：`results/tables/real-dense4-cross-summary.csv`
- 新增人类可读结果摘要：`docs/current-results-summary.md`
- 新增报告式对比表：`results/tables/gup_real_ablation_report_table.csv`
- 新增改进后结果表：`results/tables/hall-human-d4-summary.csv`、`results/tables/hall-yeast-d4-summary.csv`
- 新增 guard-selective 结果表：`results/tables/nogsel-human-d410-summary.csv`

## 建议下一步
1. 按 `configs/gup_real_workloads.yaml` 对 4 组 workload 分别做小规模 smoke run。
2. 重新设计 `wordnet / patents` 的轻量 smoke 方案，优先尝试更容易的 sparse-8 或可控 timeout 配置。
3. 对 `yeast / human` 继续补 baseline / reservation / nogood / full GUP 的正式对比表。
4. 基于真实 `summary.csv` 增加绘图或报告表格生成脚本。
