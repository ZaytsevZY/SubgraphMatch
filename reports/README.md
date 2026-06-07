# 报告目录

当前报告目录已经按课程项目最终提交的思路整理完成，核心文件如下：

- `main.tex`：英文报告主入口
- `references.bib`：参考文献条目
- `sections/`：按章节拆分的正文内容
- `latex-template/`：原始 ACM 模板备份
- `acmart.cls` 与相关样式文件：放在 `reports/` 根目录，便于本地编译
- `chinese-report-draft.md`：中文对照稿，便于快速修改与核对逻辑
- `TODO.md`：提交前可再次核对的遗留事项

## 当前报告结构

当前英文报告已经按评分项对齐，主要章节为：

1. `Introduction`
2. `Literature Review and Multi-dimensional Taxonomy`
3. `Problem Definition and Evaluation Metrics`
4. `Reproduced Paper and Reproduction Scope`
5. `Implementation Details`
6. `Experimental Setup`
7. `Required Experimental Results on Multiple Datasets`
8. `Ablation Study of Filtering Strategies`
9. `Conclusion, Development Context, and Reflection`
10. `Division of Labor`

## 报告专用结果表

报告正文当前依赖以下表格文件：

- `../results/tables/report_dataset_summary.csv`
- `../results/tables/report_required_metrics.csv`
- `../results/tables/report_ablation.csv`
- `../results/tables/report_boundary_datasets.csv`
- `../results/tables/report_reproduction_scope.csv`
- `../results/tables/report_taxonomy_table.csv`

其中：

- `report_required_metrics.csv`：对应课程要求中的 4 类核心指标
- `report_ablation.csv`：对应 reservation / nogood 两种过滤策略的消融结果
- `report_boundary_datasets.csv`：记录 `WordNet` / `Patents` 的 time-boxed boundary workloads

## 推荐修改方式

推荐后续写作方式：

1. 优先修改 `sections/` 中的章节正文
2. 若实验数据有更新，先重新生成 `results/tables/report_*.csv`
3. 再同步调整正文中的表格数值与分析文字
4. 最后使用 `main.tex` 统一编译

## 重新生成报告表格

如需根据 `results/raw/*.json` 重新生成报告专用表格，可执行：

```bash
python3 scripts/build_report_tables.py \
  --glob-patterns 'report-hprd-*.json' 'final-human-*.json' 'final-yeast-*.json' \
                  'wordnet-query-*-timeboxed.json' 'patents-query-*-timeboxed.json'
```

## 说明

当前环境中未检测到本地 `latexmk` / `pdflatex` 可执行程序，因此如果需要重新编译 PDF，请在具备 TeX 环境的机器上执行 `main.tex` 的编译流程。
