# 子图匹配课程项目

## 项目简介

本仓库用于完成《现代数据库系统概论》期末大作业 `选题 2：子图匹配`。

当前已知约束如下：

- 小组人数：`2`
- 必做任务：文献调研、复现 1 篇指定论文、在 3-4 组数据集上运行实验、完成过滤策略消融分析
- 报告要求：使用指定 LaTeX 模板撰写英文实验报告
- 代码要求：提供可复现实验步骤、数据集或数据集下载方式、绘图代码

本仓库当前目标不是一次性写完全部算法，而是先搭好一套适合课程复现项目推进的工程骨架，让后续的论文筛选、实现、实验、报告和答辩都有明确落点。

## 作业目标拆解

根据课程要求，项目需要完成以下 4 个核心部分：

1. 文献调研：整理子图匹配研究方向，形成分类体系。
2. 论文复现：从 `[13] [14] [15] [16] [17]` 中选择 1 篇进行复现。
3. 实验评测：在 3-4 个数据集上统计以下指标：
   - 运行时间
   - `result mappings` 数量
   - `partial mappings` 数量
   - 被过滤策略剪枝掉的 `partial mappings` 数量
4. 消融分析：逐项关闭论文中的过滤策略，分析各策略对运行时间和搜索空间的贡献。

## 当前项目策略

考虑到你们是 2 人小组，当前建议采用以下推进方式：

- 先用 `Python` 完成正确性优先的原型实现，确保文档、实验接口和统计指标统一。
- 论文选定后，再根据目标方法的性能需求决定是否局部切换到 `C++` 或引入更强的数据结构优化。
- 从一开始就把“指标统计”和“开关式消融”设计进代码结构，避免后期返工。

## 推荐论文选择思路

优先选择满足以下条件的论文：

- 方法结构清晰，过滤策略边界明确，便于拆成独立模块
- 数据集和预处理方式容易获取
- 能够比较自然地统计 `partial mappings` 和被剪枝数量
- 实现复杂度适合在课程项目时间范围内完成
- 最终算法能在汇报时讲清楚

从工程可控性角度，当前建议优先阅读和比较：

- `[13] Efficient subgraph matching`
- `[14] GUP`
- `[17] VF3`

`[15] BEE` 较新，工程复杂度和资料可得性可能更高；`[16] CECI` 若涉及较重索引结构，前期实现负担也可能更大。

## 当前论文决策

当前项目已正式选择 `[14] GUP` 作为复现对象，理由是：

- 方法边界清晰，核心集中在 guard-based pruning
- 最适合做课程要求中的过滤策略消融
- 更容易对齐 `partial mappings` 和 `pruned partial mappings` 的统计
- 更适合两人小组在有限周期内实现一个“正确、可统计、可讲解”的课程版本

补充说明：

- 已完成一轮代码可得性调查
- `GUP` 当前未查到明确公开仓库，因此默认按“自行实现课程版 `GUP-lite`”推进
- `VF3` 存在官方源码入口，但需要在作者实验室网站注册并申请获取源码
- 因此，`GUP` 是当前主线，`VF3` 是源码可得性更好的保底备选

## 目录结构

```text
SubgraphMatch/
├── data/
│   ├── raw/                  # 原始数据集
│   ├── processed/            # 统一格式后的数据
│   ├── queries/              # 查询图
│   └── sample/               # 小规模调试样例
├── docs/
│   ├── development-progress.md
│   ├── literature-review.md
│   ├── project-plan.md
│   ├── report-outline.md
│   ├── literature-review/    # 论文阅读笔记、选题比较
│   └── meeting-notes/        # 组会纪要
├── outputs/
│   ├── logs/                 # 运行日志
│   ├── tables/               # 中间统计表
│   └── tmp/                  # 临时文件
├── results/
│   ├── raw/                  # 原始实验结果
│   ├── tables/               # 报告可引用表格
│   └── figures/              # 报告可引用图片
├── references/               # 论文 PDF、阅读摘录
├── reports/                  # 英文报告源文件
├── scripts/                  # 预处理、实验、绘图脚本
├── slides/                   # 汇报材料
├── src/
│   └── subgraph_match/
│       ├── data/             # 数据格式与数据集元信息
│       ├── experiments/      # 实验组织与配置
│       ├── filters/          # 各类过滤策略
│       ├── graph/            # 图结构与图工具
│       ├── matchers/         # 匹配器主体
│       ├── matching/         # 搜索状态与映射逻辑
│       ├── metrics/          # 指标统计
│       ├── utils/            # 通用工具
│       ├── config.py
│       ├── io.py
│       └── models.py
├── tests/
└── 作业要求/
```

## 建议开发顺序

1. 阅读候选论文并锁定目标论文。
2. 明确数据图、查询图、标签格式和评测指标定义。
3. 完成图加载、样例数据、正确性测试。
4. 实现一个基础精确子图匹配框架。
5. 将论文中的过滤策略和匹配顺序策略拆分为可开关模块。
6. 建立实验脚本，统一记录运行时间和映射统计。
7. 跑通 3-4 组数据并输出图表。
8. 撰写英文报告和答辩材料。

## 新用户首次接入：先手动准备数据集

> 新用户拉取本仓库后，请先**手动下载数据集**，再运行真实数据实验。数据集文件不会完整提交到 Git 仓库中。

当前约定如下：

- 下载链接已放在 `data/raw/gup-paper/数据集链接`
- 下载得到的压缩包请放在 `data/raw/gup-paper/dataset.zip`
- 解压后的数据建议放在 `data/raw/gup-paper/extracted/dataset/`

如果你只想先验证代码是否能跑通，可以先使用仓库内置的 `toy` 样例；但如果要跑课程项目里的真实数据实验，请先完成上面的手动下载与解压。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_experiment.py
```

当前 `scripts/run_experiment.py` 已经会：

- 读取示例数据图 `data/sample/toy_graph.txt`
- 读取示例查询图 `data/sample/toy_query_path.txt`
- 运行一个正确性优先的 baseline 回溯匹配器
- 输出 `result mappings / partial mappings / pruned partial mappings / runtime_ms`

当前 `scripts/run_gup_experiment.py` 已经会：

- 运行单次 `baseline` 或 `GUP-lite` 实验
- 支持 `reservation guard` / `nogood guard` 开关
- 将原始结果写入 `results/raw/*.json`
- 支持官方 GUP 输入格式：`.vertices/.edges` + YAML query set + `query_index`

当前 `scripts/run_gup_batch.py` 和 `scripts/summarize_results.py` 已经会：

- 按标准消融配置批量运行 `baseline / reservation only / nogood only / full GUP`
- 将 `results/raw/*.json` 汇总成 `results/tables/summary.csv`
- 通过 `run_tag` 和 `glob-pattern` 只汇总某一批实验结果

当前 `scripts/run_query_set_batch.py` 已经会：

- 对真实 `.graph` 查询集按 `query_glob` 批量运行
- 按标准消融配置为每个 query 输出 JSON 结果
- 支持 `timeout_sec`，将过重 query 记录为 `timeout`

当前代码还已经支持读取 GUP 官方输入格式：

- 数据图：`.vertices` + `.edges`
- 查询集：YAML query set
- 示例文件见 `data/sample/gup_example.*` 和 `data/sample/gup_query_set.yaml`

如需运行当前测试：

```bash
python3 -m unittest -q
```

如需运行一次单次 GUP 实验：

```bash
python3 scripts/run_gup_experiment.py --matcher gup --omit-mappings
```

如需运行一次官方 GUP 格式样例：

```bash
python3 scripts/run_gup_experiment.py --matcher gup --input-format gup --data-file data/sample/gup_example --query-file data/sample/gup_query_set.yaml --query-index 1 --omit-mappings
```

如需运行一组标准消融实验并汇总：

```bash
python3 scripts/run_gup_batch.py --omit-mappings --run-tag toy-batch-20260607
python3 scripts/summarize_results.py --glob-pattern 'toy-batch-20260607*.json' --output-file results/tables/toy-batch-20260607-summary.csv
```

当前 baseline 的定位是：

- 先把统一接口、计数器和实验输出跑通
- 先保证 toy graph 上的正确性
- 为后续接入论文中的过滤策略和消融开关预留结构

已固定的文档入口：

- `docs/interface-spec.md`：图格式、matcher 接口、实验输出字段
- `docs/metrics-definition.md`：4 个课程核心指标的统一统计口径
- `docs/gup-experiment-datasets.md`：GUP 论文实验数据、课程主方案、下载与放置约定
- `configs/gup_real_workloads.yaml`：当前课程项目的真实 workload 清单

## 两人协作建议

推荐按“实现主线 + 文档实验主线”分工：

- 成员 A：论文阅读、调研文档、实验脚本、作图、报告初稿
- 成员 B：图结构、匹配器、过滤策略、计数器、正确性测试

两人共同负责：

- 论文最终选择
- 指标定义对齐
- 数据集选择
- 实验结果分析
- 最终汇报

## 当前状态

当前仓库已经完成：

- 课程要求阅读
- 项目目录初始化
- 项目文档初版搭建
- 最小可运行脚本与样例图准备
- baseline 回溯匹配器与基础计数器
- toy query 样例与单元测试
- 接口规范与指标定义文档
- 候选论文比较、评分与最终选题
- 论文代码可得性调查
- `GUP` 复现规划文档与阅读笔记

下一步最重要的事情是：

- 继续补齐 `GUP` 原文实验部分中的数据集和查询配置
- 将 `GUP` 中的 guard 设计成可开关模块
- 建立批量实验输出格式与结果落盘脚本
