# 中文报告对照稿

本文件作为当前英文 LaTeX 报告的中文对照版本，便于本地审阅与修改。下文按报告正文顺序整理主要内容。

---

## 1. 引言（Introduction）

精确子图匹配是图查询中的基础问题，在社交网络分析、生物网络分析、欺诈检测和图数据库系统中都有重要应用。给定一个带顶点标签的大型数据图和一个较小的查询图，目标是枚举所有同时保持标签一致性和边一致性的单射映射。尽管问题定义直观，但随着查询图规模增大，搜索空间会迅速膨胀，因此高效的候选过滤、匹配顺序优化和状态感知剪枝技术在实际中非常关键。

本项目聚焦于复现 GuP，一种基于 guard-based pruning 的精确子图匹配方法。GuP 的两个核心思想分别是 reservation guard 和 nogood guard：前者把 injectivity 相关约束向更早的搜索阶段传播，后者尝试复用搜索过程中发现的 dead end 信息，从而避免重复探索。这些机制的目标是在保持精确性的前提下，减少无效递归搜索。

本课程项目的目标不仅是得到一个可运行实现，也包括形成一份结构完整、实验充分、结论清晰的课程报告。因此，除了实现和评估一个 correctness-first 的 GuP 复现版本，我们还围绕文献调研、论文复现、多数据集实验和过滤策略消融四个核心部分来组织全文。

### 1.1 项目范围（Project Scope）

我们的实现采用分阶段策略：先构造 baseline 深度优先回溯匹配器，再加入 GuP 风格的 reservation 和 nogood guard，最后在统一指标框架下比较不同变体。当前系统仍然是课程项目级复现，而不是对原作者生产级代码的逐行系统重写；但它已经覆盖了进行课程级实验分析所需的核心算法组成。

---

## 2. 文献调研与多维分类体系（Literature Review and Multi-dimensional Taxonomy）

精确子图匹配已经发展了较长时间，相关研究既来自数据库系统方向，也来自图算法方向。这个领域并不是沿着单一技术主线演进的：有些方法把重点放在搜索开始前的候选集压缩，有些方法强调匹配顺序优化，有些方法试图复用 dead end 信息来减少重复失败，还有一些方法则从更整体的系统执行框架出发做高性能查询处理。因此，对于本课程项目而言，文献调研的目标不应只是按年份罗列论文，而应构建一个**多维分类体系**，解释不同方法分别在哪些维度上发力、彼此之间如何区分，以及 GuP 在整个研究谱系中所处的位置。

### 2.1 文献调研概览

子图匹配相关工作较多，优化重点也并不一致，因此本报告不按单纯时间线展开，而是用一个简洁的多维分类框架来组织代表性方法。这样更便于说明不同论文主要解决的到底是候选过滤问题、搜索顺序问题、冲突复用问题，还是更整体的系统执行问题。

### 2.2 分类维度

本报告使用四个主要维度组织相关工作：

1. **Candidate filtering**：方法在搜索前或搜索中压缩候选域的能力。典型依据包括标签、度数、局部邻域结构或更复杂的签名信息。过滤越强，搜索树分支因子通常越小，但代价可能是更重的预处理或辅助结构。
2. **Matching order**：方法如何决定下一个扩展的查询顶点。由于精确匹配本质上通常仍是搜索问题，顶点访问顺序会显著影响冲突是尽早暴露还是滞后暴露。静态顺序实现简单，而自适应顺序更灵活，但也可能引入控制开销。
3. **Conflict reuse / failing sets**：方法是否会记忆 dead end，并在后续搜索中复用失败信息。如果很多分支都因相似原因失败，那么“记住失败的结构”可能比继续加强局部过滤更有效。
4. **System-level acceleration**：方法是否依赖更重的索引、候选空间工程化组织、集合交运算或整体执行框架，而不仅仅是局部剪枝规则。这个维度有助于区分“算法思想本身强”与“系统实现整体强”。

这四个维度彼此互补，而不是互斥。很多优秀方法同时覆盖多个维度，但不同论文的主导强调点并不一样。因此，这套分类体系不是要把每篇论文硬塞进单一类别，而是识别其**主要贡献重心**。

### 2.3 代表性研究路线

#### （1）候选空间优先的过滤路线

GraphQL 可以看作较早的代表性方法之一。它强调通过签名和图访问方式，在正式枚举之前尽量缩小候选空间。这类方法的重要意义在于，它们较早明确了一个核心事实：精确子图匹配的后续搜索开销，往往首先取决于候选域是否已经被压缩到足够小。它们的优点是前置过滤思路清晰、对很多查询都有效；但局限也很明显——如果局部签名的区分能力不够强，那么大量歧义仍然会留给后续搜索阶段处理。

#### （2）搜索过程联合优化路线

DAF 代表了另一条非常重要的路线，即把精确子图匹配明确地视为一个搜索控制问题，并尝试把 candidate filtering、matching order 和 failure handling 协同优化。它把 dynamic programming、adaptive matching order 和 failing set 放在统一框架中考虑，说明现代精确匹配算法的性能不只是“候选集小不小”，还取决于“先扩展谁”“失败信息能不能复用”。与更早的候选空间方法相比，这一路线把更多优化重点从静态预处理转移到了动态搜索阶段。

#### （3）比较研究与方法学视角

除了不断提出新算法，领域内也开始出现对子图匹配系统进行系统性比较的工作。Sun 和 Luo 的 in-memory subgraph matching study 对本项目尤其有帮助，因为它并不是只强调某个单点技巧，而是分析 candidate generation、matching order、中间状态表示和实现细节如何共同影响性能。这个视角非常适合课程报告：它提醒我们，runtime 只是最终表象，真正决定实验结果的往往是搜索空间规模和执行过程中的多个耦合因素。因此，我们后续才会把 `partial mappings` 等指标与 runtime 一起报告。

#### （4）系统级整体执行优化路线

RapidMatch 更偏向系统级思路。它不是只围绕某一种局部剪枝规则展开，而是把 subgraph query processing 作为一个整体执行流程来重新组织。它的价值在于说明：高性能并不一定完全来自“更聪明的剪枝条件”，也可能来自候选空间的组织方式、中间结果的表示方式，以及不同执行阶段之间的配合。从课程复现角度看，这类方法通常更难高保真复现，因为最终性能往往很依赖底层工程实现。

#### （5）冗余与等价状态消除路线

VEQ 则体现了另一类思路，即通过识别等价或近似等价的搜索状态来减少重复工作。它与 failing set 路线有联系，因为二者都试图避免反复进入本质相似的无效分支；但它更强调 redundancy reduction，而不是单纯记录显式失败。这个方向的意义在于，它说明“减少 partial mappings”不只有继续加强过滤这一种办法，也可以从压缩重复计算的角度入手。

#### （6）这些路线之间的关系

综合来看，精确子图匹配的发展并不是单线推进的，而是沿着多个互补方向演进：有的方法试图更早缩小问题规模，有的方法优化搜索树的遍历方式，有的方法复用失败信息，还有的方法从整体执行系统出发提升性能。这样的组织方式比简单按时间线罗列更适合本报告，因为它能自然引出 GuP 的 reservation guard 和 nogood guard 分别解决什么问题。

### 2.4 GuP 在分类体系中的位置

在这套分类体系下，GuP 最适合被理解为一种**搜索驱动 + 动态状态感知剪枝**的精确匹配方法。它的核心贡献既不是最重的离线候选过滤，也不是最系统化的执行引擎，而是把 pruning decision 更紧密地绑定到当前搜索状态上。具体来说：

- **reservation guard** 会更早传播未来 injectivity 相关的约束；
- **nogood guard** 会尝试复用已发现 dead end 的信息，拒绝未来等价或近似等价的失败扩展。

因此，GuP 位于“经典 candidate-space 方法”和“更强 conflict reuse 方法”之间：它仍然属于回溯枚举框架，但已经明显不是只依赖静态过滤的方案。

### 2.5 为什么 GuP 适合作为课程项目复现对象

GuP 之所以适合本课程项目，主要有以下几点：

1. **方法边界清晰**：核心创新点集中在 reservation / nogood 两类 guard，主线容易讲清楚；
2. **便于做消融实验**：两个 guard 可以自然开关，能够直接对应课程要求中的“依次关闭过滤策略”；
3. **容易对齐课程指标**：GuP 的贡献与搜索空间缩减高度相关，因此很适合统计 `partial mappings` 与 `paper-filtered partial mappings`；
4. **工程实现可控**：相比更重的索引型或系统型方法，GuP 更适合在课程周期内完成一个 correctness-first 的复现版本；
5. **利于报告表达**：在答辩或写作时，可以相对直接地说明“为什么这个方法有效、有效在哪里、哪些模块起主要作用”。

换言之，GuP 在“研究新意”“可解释性”“实验可拆解性”和“实现风险可控性”之间取得了较好的平衡。这也是我们最终选择它作为复现对象的重要原因。

### 2.6 本节对后续章节的作用

文献调研并不是孤立存在的，它直接决定了后续报告的组织方式。基于上述分类，我们在后文中会做三个明确选择：

- 第一，把 GuP 放在“conflict-aware exact matching”的更大背景下理解，而不是把它写成一篇孤立论文；
- 第二，实验部分不仅比较 runtime，还比较搜索空间指标，从而反映 guard 对枚举过程的具体影响；
- 第三，在讨论局限性时，区分“算法思想本身的局限”和“课程版 Python 复现的系统性能边界”，避免把工程实现问题误判为方法无效。

## 3. 问题定义与评测指标（Problem Definition and Evaluation Metrics）

设数据图为 $G = (V_G, E_G, \ell_G)$，查询图为 $Q = (V_Q, E_Q, \ell_Q)$，其中顶点带有离散标签。精确子图匹配要求找出所有单射映射

\[
f: V_Q \rightarrow V_G
\]

满足：

1. 对任意查询顶点 $u \in V_Q$，有 $\ell_Q(u) = \ell_G(f(u))$；
2. 对任意查询边 $(u, u') \in E_Q$，有 $(f(u), f(u')) \in E_G$。

在当前实现中，所有图都被视为无向、带顶点标签且无自环。课程项目的必做部分不涉及边标签、同态语义或动态图更新。

### 3.1 课程要求中的四类核心指标

课程要求至少统计四类指标，我们在报告中将其固定为：

- **Runtime (ms)**：匹配主过程的墙钟时间，不计文件读取；
- **Result mappings**：最终完整合法嵌入数量；
- **Partial mappings**：搜索过程中成功生成的部分映射数量；
- **Paper-filtered partial mappings**：被复现论文的过滤策略本身剪掉的 partial mapping 数量。

### 3.2 为什么要区分 `pruned_partial_mappings` 与 `paper-filtered partial mappings`

内部统计器中的 `pruned_partial_mappings` 会记录所有被拒绝的扩展，包括：

- injectivity conflict
- edge conflict
- reservation guard
- nogood guard

但如果只看总剪枝数，就无法单独看出论文过滤策略本身的贡献。因此，报告中会额外单独提取：

- `reservation_guard_filtered`
- `nogood_guard_filtered`
- `paper_filter_filtered_total = reservation + nogood`

这样，论文过滤策略造成的剪枝数量就能被单独呈现，而不是混在所有剪枝原因里。

---

## 4. 复现论文与复现范围（Reproduced Paper and Reproduction Scope）

本项目选择复现的论文是：

> **GuP: Fast Subgraph Matching by Guard-Based Pruning**

论文的核心观察是：许多 dead-end partial embeddings 实际上可以在出现显式结构冲突之前就被识别出来，因此可以更早地被剪掉。为此，GuP 引入了 guard-based pruning。

### 4.1 GuP 的两个核心机制

#### Reservation guard

直观上，当我们尝试扩展候选 $(u, v)$ 时，未来一些查询顶点实际上已经被迫只能使用一小组特定的数据顶点。如果这些顶点在更早阶段已被占用，那么当前扩展其实已经不可能延伸成合法完整解，可以提前剪掉。

#### Nogood guard

nogood guard 不只依赖局部一致性，而是记录 dead end 的某种签名，在后续搜索中拒绝那些会诱导相同未来子问题的扩展。论文中的完整版还包含更强的候选空间结构与更丰富的 guard discovery 规则。

### 4.2 复现范围（Reproduction Scope）

报告中加入了一张 reproduction scope table，用来明确回答：

- 原论文哪些组件已经实现；
- 哪些是 partial reproduction；
- 哪些尚未覆盖；
- 这些差异会如何影响实验结果。

核心结论是：

- baseline exact search：已实现；
- candidate generation：已实现，但较简化；
- matching order：已实现，但比原论文更基础；
- reservation guard：已实现，是当前最有效模块；
- nogood guard：已实现，但为保守近似版本；
- guarded candidate-space engineering：只做了最低限度支持；
- 系统级低层优化：未完整复现。

因此，本报告对项目的定位不是“没有复现完整”，而是：

> 已完成课程项目级的核心算法复现，并明确说明了复现边界。

---

## 5. 实现细节（Implementation Details）

整个项目使用 Python 实现，强调 correctness-first。代码中包含两个主要 matcher：

- baseline 深度优先回溯匹配器
- 在同一搜索框架上加入 guard-based pruning 的 `GUP-lite`

这种共享结构很适合课程项目，因为它可以让不同过滤策略的效果被直接隔离并比较。

### 5.1 图表示与输入格式

所有图最终都会转换成统一的 `LabeledGraph` 结构。当前项目支持三种输入格式：

- toy `v/e` 文本格式
- GuP 官方样例的 `.vertices/.edges + YAML` 格式
- 真实 benchmark 使用的 `.graph` 格式

### 5.2 Baseline matcher

baseline matcher 会：

- 构造候选集
- 生成匹配顺序
- 递归扩展 partial embedding
- 用 injectivity 与 edge consistency 检查每个扩展

同时统一记录：

- `result_mappings`
- `partial_mappings`
- `pruned_partial_mappings`
- `runtime_ms`

### 5.3 Candidate generation 与 matching order

候选过滤从最初的纯 label 过滤升级为 `label + degree` 规则；匹配顺序则按候选集大小、顶点度数和顶点编号生成。这一部分对应原论文中的 candidate-space preparation，但仍比原论文完整版更简化。

### 5.4 Reservation guard

reservation guard 的最终实现不是简单前向检查，而是“预计算的小型 reservation set”。

对候选 `(u, v)`，它会查看 matching order 中 `u` 之后的 forward neighbors，计算这些邻居在数据图里的兼容候选集合；如果某个小子集满足类似 Hall-style 的等式条件，就把那一组数据顶点视为“保留集合”。搜索时，只需检查这些保留顶点是否已被过早占用。

这一模块直接对应课程要求中的过滤策略之一，而且它也是当前实验中唯一稳定产生非零 `paper-filtered partial mappings` 的模块。

### 5.5 Nogood guard

当前 nogood guard 不是原论文中的完整实现，而是一个保守的 future-subproblem memoization 版本。它记录扩展后的未来子问题签名，包括：

- 搜索深度
- 假想已使用数据顶点集合
- frontier mapping

后期我们又加入了 selective activation：只有某个 query vertex 确实积累了相关 dead-end 信息时，才启用 nogood 检查，从而减少无意义的 Python 层检查。

当前结论是：

- 它是正确且可用的；
- 但在真实 workload 上仍然偏保守，因此显式 pruning 收益有限。

---

## 6. 实验设置（Experimental Setup）

实验设置中明确区分了：

- **main successful datasets**
- **time-boxed boundary datasets**

### 6.1 使用的数据集

报告中使用的数据集如下：

- `Yeast`：主结果数据集
- `Human`：主结果数据集
- `HPRD`：新增的第 3 个成功数据集
- `WordNet`：boundary dataset
- `Patents`：boundary dataset

### 6.2 为什么 HPRD 很关键

目前主结果不再只有 `Yeast + Human` 两个成功数据集，而是进一步补齐了：

- `HPRD/query_dense_4_1`
- `HPRD/query_dense_4_10`

这使得正文已经满足了课程要求中的“3–4 个数据集实验”这一点。

### 6.3 四种比较配置

实验比较以下四种配置：

- Baseline
- Reservation only
- Nogood only
- Full GUP

并明确给出策略开关表：

- Baseline：reservation off, nogood off
- Reservation only：reservation on, nogood off
- Nogood only：reservation off, nogood on
- Full GUP：reservation on, nogood on

### 6.4 Time-box policy

对 `WordNet` 和 `Patents`，当前使用统一的 `120` 秒 time box。若在规定时间内无法完成，就显式记录为 `timeout`，而不是直接删除不报。这样 boundary workload 也成为报告的一部分。

---

## 7. 多数据集实验结果（Required Experimental Results on Multiple Datasets）

当前主结果表显式汇报以下指标：

- runtime
- result mappings
- partial mappings
- paper-filtered partial mappings

### 7.1 三个成功数据集

当前成功主数据集为：

- `Yeast`
- `Human`
- `HPRD`

这意味着报告已经可以明确说：

> 已满足“3–4 个数据集”的成功实验要求。

### 7.2 HPRD 的结果

#### HPRD d4-1

- baseline: `980` result mappings, `1514` partial mappings, `237.90 ms`
- reservation only: `980`, `1440`, `211.05 ms`
- nogood only: `980`, `1514`, `224.05 ms`
- full GUP: `980`, `1440`, `208.63 ms`

结论：

- reservation / full GUP 都把 partial mappings 降低了 `74`
- full GUP 相比 baseline 提升约 `12.30%`

#### HPRD d4-10

- baseline: `4` result mappings, `51` partial mappings, `8.96 ms`
- reservation only: `4`, `11`, `1.36 ms`
- nogood only: `4`, `51`, `6.88 ms`
- full GUP: `4`, `11`, `1.35 ms`

结论：

- reservation / full GUP 把 partial mappings 从 `51` 降到 `11`
- 降幅达到 `78.43%`
- runtime 改善约 `85%`

这组结果也是全文中最有说服力的正面证据之一。

### 7.3 Human 的结果

#### Human d4-1

- baseline: `185.86 ms`
- reservation only: `170.25 ms`
- nogood only: `161.53 ms`
- full GUP: `143.34 ms`

结论：

- full GUP 在该 query 上最好
- reservation guard 对搜索空间有非零贡献（`97`）

#### Human d4-10

- baseline: `50314.48 ms`
- reservation only: `55887.18 ms`
- nogood only: `55239.79 ms`
- full GUP: `56733.61 ms`

结论：

- reservation guard 虽然减少了 `290` 个 partial mappings
- 但这一下降非常小，无法覆盖当前 Python prototype 的额外 overhead
- 因此时间仍慢于 baseline

### 7.4 Yeast 的结果

#### Yeast d4-1

- reservation 相关剪枝几乎没有体现
- 运行时间差异也很小

#### Yeast d4-10

- baseline: `22624` partial mappings, `805.98 ms`
- reservation only: `22283`, `682.42 ms`
- full GUP: `22283`, `731.28 ms`

结论：

- reservation guard 降低了 `341` 个 partial mappings
- reservation-only 是这组中最快的配置

### 7.5 Boundary datasets

报告中还单独保留了 `WordNet` 与 `Patents` 的 boundary dataset 表：

- `WordNet d4-1`: timeout
- `WordNet s8-15`: timeout
- `Patents d4-1`: timeout
- `Patents s8-15`: timeout

这意味着：

- 它们没有被隐藏
- 而是作为 prototype scalability boundary 的证据被显式报告

---

## 8. 过滤策略消融分析（Ablation Study of Filtering Strategies）

当前消融实验采用统一写法，直接给出：

- reservation-only 的 delta
- nogood-only 的 delta
- full GUP 的 delta

并分别统计：

- partial delta
- partial delta (%)
- runtime delta (ms)

### 8.1 Reservation guard 的结论

reservation guard 是当前复现中最有效的过滤策略。它几乎承担了所有非零 `paper-filtered partial mappings` 的来源，也是多个 workload 上加速的主因。尤其在：

- `HPRD d4-10`
- `Yeast d4-10`

上体现得最明显。

### 8.2 Nogood guard 的结论

当前 nogood guard 仍然较保守：

- 在成功主 workload 上，几乎没有显式 nonzero nogood-based pruning
- 因此 partial delta 通常为 0

但在实现层面，经过 selective activation 后，nogood-only 不再总是纯负担，说明它至少在 runtime overhead 上得到一定控制。

### 8.3 组合效果

full GUP 的效果与 workload 密切相关：

- 在 `HPRD` 和 `Human d4-1` 上能够继承 reservation 的收益
- 在 `Human d4-10` 上则仍然因为 overhead 大于收益而慢于 baseline

因此当前最稳妥的结论是：

> reservation-based pruning 已经相对稳定有效，nogood-based pruning 仍需更接近论文的强实现才能体现稳定增益。

---

## 9. 总结、发展背景与心得（Conclusion, Development Context, and Reflection）

这一节不只是结论，也包含方法发展背景与项目心得。

### 9.1 发展背景

从子图匹配的发展历史来看，研究路线已经从早期的 candidate-space / access-method 方法，逐渐演进到同时结合：

- filtering
- matching order
- conflict reuse
- execution engineering

的更整体系统。GuP 正好是这一发展脉络中的一个代表点：它强调动态状态感知剪枝，同时又保持模块边界清晰，适合课程项目级分析。

### 9.2 当前最终结论

英文稿目前的三点总括结论是：

1. 当前项目已经满足 3 个成功数据集的要求：`Yeast`、`Human`、`HPRD`；
2. reservation-based pruning 是当前实现中唯一稳定产生搜索空间收益的核心机制；
3. `WordNet` 与 `Patents` 明确揭示了当前 Python prototype 的 scalability boundary。

### 9.3 心得

这里强调的心得是：

- 复现论文并不只是复现最终指标；
- 更重要的是理解：
  - 哪些算法思想是核心；
  - 哪些工程细节决定实际表现；
  - 如何诚实地报告复现边界。

这也解释了为什么报告会显式区分：

- 算法思想是否成立
- 系统级工程是否足以达到原论文同级性能

---

## 10. 组内分工（Division of Labor）

当前组内分工为：

- 查益（Yi Zha）：框架搭建、算法复现、整体 pipeline 集成、报告撰写
- 王锦鹏（Jinpeng Wang）：算法优化、实验执行、汇报 PPT 准备

两位成员共同参与最终展示与答辩说明。

---

## 说明

如果你现在看的是这个文件，那么答案是：

**现在这份中文对照稿已经与当前英文稿保持一致。**

尤其是下面这些原先不一致的地方，现在都已经同步：

- `HPRD` 已被纳入第 3 个成功数据集
- 数据集结构改为 `3 main + 2 boundary`
- 实验指标改为显式区分 `paper-filtered partial mappings`
- 复现范围增加 scope 说明
- ablation 改成更标准的统一写法
- conclusion 改成含发展背景与心得的版本

所以你接下来可以直接用这份中文稿审查整体逻辑，而不会再被旧版本误导。
