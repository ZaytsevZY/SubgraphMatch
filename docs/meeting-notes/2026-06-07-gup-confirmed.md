# 2026-06-07 GUP 选题确认

## 会议结论
- 正式确定课程项目复现论文为 `[14] GUP`
- 项目主线改为：`自主复现 GUP-lite + 参考官方 Rust 实现`
- 保底切换方案仍保留为 `[17] VF3`，但当前不切换主线

## 选择原因
- `guard-based pruning` 与课程要求中的过滤策略消融高度一致
- 容易对齐 `runtime / result mappings / partial mappings / pruned partial mappings`
- 对二人小组而言，模块边界比索引型和分解型论文更清晰

## 当前实现状态
- baseline matcher 已可运行
- `gup_matcher.py` 已有雏形
- `reservation_guard.py` 和 `nogood_guard.py` 已有第一版实现
- 当前最缺的是测试闭环、实验设置整理和结果落盘脚本

## 接下来三件最重要的事
1. 补 `GUPMatcher` 的正确性与配置测试
2. 整理 `GUP` 原文实验设置，固定课程使用的数据集和查询集
3. 明确 `GUP-lite` 第一阶段只做哪些 guard 和统计字段

## 风险提醒
- 当前 guard 还是课程版近似实现，不等于论文完整版
- 若 guard 逻辑与论文定义偏差过大，后续需要及时修正
- 若 `GUP` 实现进度明显落后，才考虑切换到 `VF3`
