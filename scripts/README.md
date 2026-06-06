# 脚本目录

后续可在此目录放置：

- 数据预处理脚本
- 实验批量运行脚本
- 实验结果汇总脚本
- 绘图脚本

当前已提供：

- `run_experiment.py`：运行 baseline toy 示例并打印统计信息
- `run_gup_experiment.py`：运行单次 baseline / GUP 实验，并将原始结果写入 `results/raw/`
- `run_gup_batch.py`：按标准消融配置批量运行 baseline / GUP 实验，支持使用 `run_tag` 区分批次
- `summarize_results.py`：将指定模式的 `results/raw/*.json` 汇总成 `results/tables/*.csv`
