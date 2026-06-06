# GUP 实验数据与查询集方案

## 1. 文档目的
本文件用于把 GUP 论文中的实验设置落成当前课程项目可执行的数据方案，回答以下问题：

- 论文原始实验用了哪些数据图和查询集
- 当前课程项目准备实际跑哪 `3-4` 组
- 数据从哪里来、需要手动做什么
- 当前仓库还差哪些与数据相关的脚本

## 2. 论文原始实验设置

### 2.1 数据图
GUP 论文实验使用 4 个数据图：

- `Yeast`：`3,112` vertices, `12,519` edges, `71` labels
- `Human`：`4,674` vertices, `86,282` edges, `44` labels
- `WordNet`：`76,853` vertices, `120,399` edges, `5` labels
- `Patents`：`3,774,768` vertices, `16,518,947` edges, `20` labels

说明：
- 前 3 个是常见的带标签真实图
- `Patents` 原始上是无标签图，论文沿用 Sun 等人公开实验中的随机标签版本

### 2.2 查询集生成方式
论文沿用既有工作中的 query 生成方式：

- 在数据图上执行随机游走
- 取访问顶点诱导出的子图作为查询图
- 平均度 `< 3` 记为 sparse，否则记为 dense

查询规模分为：

- sparse：`8S`, `16S`, `24S`, `32S`
- dense：`8D`, `16D`, `24D`, `32D`

因此总共有：

- `4` 个数据图
- `4` 个大小档位
- `2` 个密度档位
- 合计 `32` 个 query sets

每个 query set 含：

- `50,000` 个 query graphs

### 2.3 论文实验停止条件
论文实验中的关键停止条件如下：

- 单个 query 找到 `10^5` 个 embeddings 后停止
- 单个 query 的时间上限：`1` 小时
- query set 以 `100` 个 query 为一组；任一组总时长超过 `3` 小时，则整组 query set 记为 `DNF`

## 3. 当前课程项目的现实取舍

课程项目不需要完整复制论文的 `32` 个 query sets，也不需要每组 `50,000` 个 query graphs 才算成立。

当前更合理的目标是：

- 保留论文的数据图和 query 类型风格
- 选 `3-4` 组足够有代表性的组合
- 先跑出一套能支撑报告和消融的课程版实验

## 4. 当前推荐的数据集方案

### 4.0 已验证数据包的实际情况

当前课程项目所使用的 `dataset.zip` 来自 `SubgraphMatching` 仓库提供的真实数据入口。下面的内容是基于该数据包结构做过检查后的结论，供新用户下载后对照使用。

与 GUP 论文正文相比，这包数据有两个重要区别：

1. 数据文件格式是 `.graph`，不是 GuP 官方仓库的 `.vertices/.edges + YAML`
2. query 集并不是论文中精确描述的 `32` 个 query sets，而是每个数据集自带 `1800` 个单独的 query `.graph` 文件

当前已确认该数据包中包含的 8 个数据集是：

- `yeast`
- `human`
- `wordnet`
- `patents`
- `dblp`
- `eu2005`
- `hprd`
- `youtube`

其中与 GUP 论文正文直接对应的 4 个是：

- `yeast`
- `human`
- `wordnet`
- `patents`

每个目标数据集通常都包含：

- `1` 个数据图 `.graph`
- `1800` 个 query `.graph`

已确认的 query 大小档位如下：

- `yeast`：dense = `4, 8, 16, 24, 32`；sparse = `8, 16, 24, 32`
- `human`：dense = `4, 8, 12, 16, 20`；sparse = `8, 12, 16, 20`
- `wordnet`：dense = `4, 8, 12, 16, 20`；sparse = `8, 12, 16, 20`
- `patents`：dense = `4, 8, 16, 24, 32`；sparse = `8, 16, 24, 32`

### 4.1 推荐主方案（4 组）

建议当前正式实验优先选以下 4 组真实可用组合：

1. `Yeast-24S`
2. `Human-20S`
3. `WordNet-16D`
4. `Patents-8S`

### 4.2 选择理由

#### `Yeast-24S`
- 小图，最适合作为“先跑通正式实验管线”的第一组
- 相比 `8/16` 顶点 query，`24` 顶点更容易体现 guard 的收益

#### `Human-20S`
- 当前已检查的数据包中，`human` 的 sparse query 最大只到 `20`
- 它是最接近论文中 `24S of Human` 的可用替代组
- 适合在报告里解释为“课程版复现实验采用下载包中最接近论文难度的可用组”

#### `WordNet-16D`
- dense query 更容易制造大搜索空间
- 论文也单独讨论了 `16D of WordNet` 的困难性，适合做 guard 消融

#### `Patents-8S`
- 保留论文中最大的真实图，体现方法的规模感
- 同时把 query 大小控制在 `8`，降低课程项目第一次正式实验的风险

## 5. 备用保守方案

如果后续发现下载、格式转换或运行成本明显高于预期，则切换到更保守的 4 组：

1. `Yeast-16S`
2. `Human-16S`
3. `WordNet-12S`
4. `Patents-8S`

这套方案的目标不是最大化论文味，而是优先保证：

- 实验能在课程时间内稳定完成
- 消融矩阵能完整跑出来
- 报告中每组数据都有结果可讲

## 6. 下载与放置约定

### 6.1 当前已确认的来源
- GUP 官方仓库提供了输入格式、命令行和 probe 输出说明
- Sun 等人的 SubgraphMatching 仓库 README 给出了真实数据集与 query sets 的下载入口
- 该入口会跳转到 SharePoint 上的 `dataset.zip`

### 6.2 推荐本地放置位置

新用户拉取仓库后，请按以下方式手动放置数据：

- 下载链接文件：`data/raw/gup-paper/数据集链接`
- 压缩包路径：`data/raw/gup-paper/dataset.zip`
- 解压目录：`data/raw/gup-paper/extracted/dataset/`

解压完成后，每个数据集目录下通常包含：

- `data_graph/<dataset>.graph`
- `query_graph/query_*.graph`

## 7. 新用户需要手动完成的动作

请新用户首次接入项目时手动完成以下步骤：

1. 打开 `data/raw/gup-paper/数据集链接`
2. 根据其中的链接下载 `dataset.zip`
3. 将压缩包保存到 `data/raw/gup-paper/dataset.zip`
4. 将压缩包解压到 `data/raw/gup-paper/extracted/dataset/`

补充说明：

- 数据集本体不会完整提交到 Git 仓库中
- 如果只想验证代码流程，可先使用 `data/sample/` 下的 toy 数据
- 如果要运行真实数据实验，则必须先完成上述下载与解压

## 8. 与当前仓库代码的差距

这是现在最关键的工程差距：

- 真实数据下载包的主要格式是：`.graph`
- GUP 官方仓库样例格式是：`.vertices` + `.edges` + YAML query set
- 当前仓库现在已经同时支持：
  - toy `v/e` 文本格式
  - GUP 官方 `.vertices/.edges + YAML`
  - SubgraphMatching `.graph`

当前剩余差距主要变为：

1. 让批量脚本直接按 query 文件集合运行真实数据
2. 固定课程项目最终使用的 query 文件集合或 query glob
3. 生成真实数据上的首轮正式结果表

## 9. 下一步动作

1. 将主方案 4 组写成可执行实验清单
2. 让批量脚本按 query glob 跑真实 `.graph` 查询集
3. 先对每组取较小子集做 smoke experiment
4. 再扩大到课程报告使用的正式规模

## 9.1 当前 smoke 结果

基于已下载并检查过的真实数据，我们已经完成一轮跨数据集 smoke：

- `Yeast / query_dense_4_23`：成功
- `Human / query_dense_4_1`：成功
- `WordNet / query_dense_4_1`：在 `120` 秒 timebox 下超时
- `Patents / query_dense_4_1`：在 `120` 秒 timebox 下超时

对应汇总表：

- `results/tables/real-dense4-cross-summary.csv`

这说明当前 Python 原型在真实数据上已经可以稳定处理 `Yeast` 和 `Human` 的轻量 query，
而 `WordNet` 和 `Patents` 即便是 `dense-4` 查询，在当前实现下也仍然较重。

因此后续课程实验应采用分层策略：

- `Yeast / Human`：优先做更完整的 baseline vs GUP 对比
- `WordNet / Patents`：优先做 timeboxed smoke 与更轻 query 选择，再决定正式规模

## 10. 当前结论

到目前为止，数据集层面的情况已经明确：

- 论文完整实验：`Yeast / Human / WordNet / Patents` + `32` 个 query sets
- 已验证的数据包：包含上述 4 个目标数据集，且每个数据集带 `1800` 个 `.graph` 查询文件
- 课程项目主方案：`Yeast-24S / Human-20S / WordNet-16D / Patents-8S`
- 课程项目保守方案：`Yeast-16S / Human-16S / WordNet-12S / Patents-8S`
- 对仓库维护者来说，下一步重点是“选定 query 文件集合并开始真实批量实验”；对新用户来说，第一步仍然是先手动准备数据集
