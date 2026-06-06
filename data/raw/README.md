# 原始数据放置说明

## 当前约定

新用户首次接入本项目时，如果需要运行真实数据实验，请先手动下载数据集，并放到：

- `data/raw/gup-paper/`

建议保留原始压缩包和来源信息，不要随意重命名原始文件。

## 当前目录约定

当前仓库中的推荐放置方式如下：

- 数据集链接文件：`data/raw/gup-paper/数据集链接`
- 下载后的压缩包：`data/raw/gup-paper/dataset.zip`
- 解压后的数据目录：`data/raw/gup-paper/extracted/dataset/`

## 新用户需要手动完成的动作

1. 打开 `data/raw/gup-paper/数据集链接`
2. 根据其中的链接手动下载数据集
3. 将下载后的文件保存为 `data/raw/gup-paper/dataset.zip`
4. 将压缩包解压到 `data/raw/gup-paper/extracted/dataset/`

## 补充说明

- 如果只是验证仓库代码是否能跑通，可以先使用 `data/sample/` 下的 toy 样例
- 如果要运行课程项目中的真实数据实验，请先完成上述手动下载和解压
- 数据集本体不会完整提交到 Git 仓库中
