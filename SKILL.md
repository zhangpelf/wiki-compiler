---
name: wiki-compiler
description: 个人知识库全自动编译器 (Andrej Karpathy 风格)。支持 /wiki-compiler (增量编译), /wiki-dream (沉思/做梦), /wiki-weaver (Map-Reduce 综述)。利用幂等引擎防止冗余，内置“句级溯源”严谨性检查。
version: 2.1.0
emoji: 🧠
os: ["macos", "linux", "windows"]
author: zhangpelf
repository: https://github.com/zhangpelf/wiki-compiler
---

# Wiki Compiler (VK) 🧠: 复刻卡帕西的“第二大脑”

> "笔记，本来就应该是大语言模型（LLM）的领地。" —— Andrej Karpathy

Wiki Compiler 不仅仅是一个 Obsidian 插件或脚本，它是为您量身定制的**全自动知识生命体**。它旨在终结“只记不读”的数字化囤积症，将您散乱的原始素材（`raw/`）自动化、增量化地编译成具备**句级溯源 (LSC)**、**高度互联**的学术级长青库（`wiki/`）。

---

## 🌟 为什么它与众不同？ (The Gimmicks)

1. **增量编译 (Incremental Compiler)**：扔进一篇论文或长文，模型自动分区、打标、关联。绝不制造冗余，只做增量。
2. **深夜“做梦”机制 (Nightly Dreaming)**：当您休息时，Agent 在巡逻。它会在看似不相关的知识点（Node）之间进行“潜意识漫游”，捕捉跨界灵感并自动生成 `Insight` 启发卡片。
3. **Map-Reduce 学术综述**：百篇文献一键并行处理。每一句陈述都必须带上 `[[原始文献]]` 引用。杜绝幻觉，严谨到变态。
4. **防幻觉裁判 (Hallucination Referee)**：遇到知识盲区自动生成 `⚠️ Definition_Needed` 标记，强制进行二元判别。

---

## 🛠️ 适用场景 (When to use)
当您发出 `/wiki-compiler`、或用户要求“将新资料存放到知识库”，以及要求触发 `/wiki-dream` 时，启动此流程。

## 关键流程约定

无论哪种模式，始终要求确定前置变量：
**`RAW_DIR`** 和 **`WIKI_DIR`**。如果用户在触发时没有提供对应参数，或上下文环境中未获取到，请询问这俩目录的**绝对路径**。对于 `/wiki-dream` 仅需 `WIKI_DIR`。

### 工作流 A：增量编译 (Trigger: `/wiki-compiler`)

核心原则：**严禁制造冗余，增量永远大于全量**。
1. **同步对比**：
   运行环境钩子脚本 `python3 <INSTALL_DIR>/wiki-compiler/scripts/sync_manifest.py --raw "$RAW_DIR" --wiki "$WIKI_DIR"`。
   该脚本会比对 `RAW_DIR` 内文件的修改时间哈希与 `WIKI_DIR/.meta/compiled_ledger.json`，在终端输出【待处理的新增/更改文件列表】。
2. **提取与编译**：
   根据上述脚本输出的文件：
   - 充分通读目标源文件（如果是文本、代码或小网页内容）。
   - 将其提炼成干净、学术的汇编文章。存入 `WIKI_DIR/projects/` 或 `WIKI_DIR/concepts/` 中。若无合适类目，可根据概念自建新文件。
   - 深入文本语义，提取关键实体，插入必需的 Obsidian 双向链接 `[[相关条目]]`。发现孤立词条时，主动查找是否有近义词并统一。
3. **原生降维可视化构建 (Marp & Dataview & Mermaid)**：
   在输出 Markdown 文件时：
   - **元数据 (Dataview)**：文件顶端必须有 YAML Frontmatter (如 `type`, `date`, `tags`, `aliases`, `project`)，以便后续聚合。
   - **内容结构图 (Mermaid)**：遇到关系映射或复杂机制，请使用 ````mermaid` 代码块嵌入可视化时序、节点关系。
   - **伴生幻灯片 (Marp)**：如果是提炼了一篇宏大论文或重点工程，必须再新建一个配套的 `<原名>.marp.md`。其顶端加入：
     ```yaml
     ---
     marp: true
     theme: default
     ---
     ```
     并且在正文中间隔性地用 `---` 划开页面，以方便用户一键预览演讲幻灯片形式。
4. **收尾 (更新账本)**：
   全部写入完成后，运行 `python3 <INSTALL_DIR>/wiki-compiler/scripts/sync_manifest.py --raw "$RAW_DIR" --wiki "$WIKI_DIR" --mark-done` 刷新 `ledger` 账本，确保这些文件已被彻底封存、未来不再重新编译。

### 工作流 B：沉思/做梦机制 (Trigger: `/wiki-dream`)

核心原则：**静默巡逻、打理未处理文件、深层上下文理解与关系映射**。
当触发“做梦”机制时，你就像是一个在夜间巡逻和沉思的守护者：

**第一阶段：巡逻与拾遗 (Night Watcher)**
1. 如果上下文中已存在或你能查到 `$RAW_DIR` 和 `$WIKI_DIR`，在沉思前，请顺手跑一次扫描：`python3 <INSTALL_DIR>/wiki-compiler/scripts/sync_manifest.py --raw "$RAW_DIR" --wiki "$WIKI_DIR"`。
2. 如果扫描显示有**待处理的增量名单**（漏网遗忘的数据），你必须在这个梦境的开场，**主动向用户发出提醒并请求授权**：“提示：发现有一些你丢进去但遗忘处理的原始资料（包含 XXX），是否需要我借助现在的做梦时间顺手帮你把它们编译入库？”若用户同意，请走一遍工作流 A。

**第二阶段：沉思与灵感连接 (Dreaming & Latent Walk)**
3. 运行脚本 `python3 <INSTALL_DIR>/wiki-compiler/scripts/wiki_dreamer.py --wiki "$WIKI_DIR" --limit 3`。
4. 脚本将返回 3 篇系统经过算法随机采样的不相关老文章的绝对路径。
5. **沉思与研读**：完整调阅这些卡片并且寻找隐蔽的链接。你现在是极具创意的研究型智能体，请在这几个风马牛不相及的碎片之间，洞察它们的“共有结构”和“创新性结合点”。
6. **结晶凝练**：新建一篇命名大概如 `WIKI_DIR/concepts/Insight-新理念-<日期>.md` 的文章。记录本次“梦境”带来的灵感碰撞，并通过使用 `[[文章A]]`、`[[文章B]]` 等将新 Insight 打造为跨领域的集散节点。

**第三阶段：健康检查 (Health Check)**
7. 运行 `python3 <INSTALL_DIR>/wiki-compiler/scripts/health_vis_engine.py --wiki "$WIKI_DIR" --auto-stub`。
8. 该脚本会检测死链、孤立页面，并为被高频引用的死链自动生成 Stub 占位卡片（带 `maturity: stub` 标记）。
9. 将检查报告中有价值的发现汇总告知用户。

### 工作流 C：知识穿梭/编织 (Trigger: `/wiki-weaver`)

核心原则：**深度跨文献综述、Map-Reduce 范式、拒绝幻觉、严缝紧凑。**
当用户需要对某个复杂主题（如“城市景观格局的碳中和效应”）进行跨多篇文献的综合论证时：

1. **Map (全库检索与精读)**：
   运行 `python3 <INSTALL_DIR>/wiki-compiler/scripts/wiki_weaver.py --wiki "$WIKI_DIR" --query "搜索词"`。
   该脚本将利用 BM25 算法筛选出库内相关度最高的研究片段路径。
2. **Reduce (分而治之)**：
   你将获得一组文件绝对路径列表。如果你认为文章超长，请独立分段读取。记录每一条关键结论，并标注原始文件来源。
3. **Synthesis (句级溯源撰写)**：
   生成一篇全新的综述卡片存入 `WIKI_DIR/concepts/`。
   **强制要求**：综述中的每一句针对事实的客观陈述，末尾必须带有 `[[原始文献名]]` 形式的引用。严禁出现任何无出处的结论。
4. **验证**：
   在输出前，自检所有引用是否真实存在于知识库内。

### 工作流 D：知识库搜索 (供 Agent 自用或用户直接调用)

当需要在知识库中查找特定信息时（回答用户问题前、编译新资料需要查重时），运行：
```
python3 <INSTALL_DIR>/wiki-compiler/scripts/query_wiki.py --wiki "$WIKI_DIR" --query "搜索关键词" --top 5
```
该脚本基于 BM25 算法进行全文检索，返回相关度排序的结果和上下文片段。**务必在回答复杂跨领域问题前先查一遍知识库**，避免凭空编造。

### 工作流 D：Q&A 回填闭环

当你为用户完成了一次需要深度研究才能回答的问题后（尤其是涉及跨文章综合分析的），必须在回答末尾主动提议：

> "本次回答涉及了较深的知识整合，是否需要我将核心结论归档到知识库中？建议存入 `[[建议的卡片名]]`。"

若用户同意，将回答的精华浓缩写入 `WIKI_DIR/concepts/` 或 `WIKI_DIR/projects/` 下对应的卡片（新建或追加到现有卡片的新章节中），并确保带有完整的 YAML frontmatter。

## 元数据约定 (Frontmatter 规范)

所有由本技能生成的 Markdown 文件，顶部必须包含以下 YAML 字段：

```yaml
---
type: concept | project | insight | stub
maturity: stub | draft | reviewed | authoritative
date: YYYY-MM-DD           # 创建日期
updated: YYYY-MM-DD        # 最后更新日期
tags: [相关标签]
aliases: [别名, 同义词]
project: 所属项目名         # 可选
sources: [来源文件路径]     # 可选，追溯到 raw/ 中的原始文件
---
```

**maturity 生命周期**：
- `stub`：仅有标题和反向链接，内容待补充（通常由健康检查引擎自动生成）
- `draft`：已有初步内容但未经人工审核
- `reviewed`：经过用户或 Agent 做梦机制审视过
- `authoritative`：经多源交叉验证，可信度高

## 严格约束
- **输出语言**：必须以中文交互输出。
- **防止重叠**：编写 `[[新卡片]]` 前，若不确定现有知识树内是否已有同义卡片（如 "Agent" 和 "智能体"），请用搜索工具 `query_wiki.py` 或 `grep_search` 进行查重防范。
- **溯源标注**：编译自 `raw/` 的内容，必须在 frontmatter 的 `sources` 字段中注明原始文件路径。
- **不篡改原始数据**：永远不要修改 `raw/` 目录下的任何文件。

---

## 🗺️ 中长期路线图 (Future Work)

以下功能尚未实现，记录于此供后续迭代参考：

### 矛盾检测引擎 (Contradiction Detection)
- 在 `/wiki-dream` 中增加高级模式：对同一主题下的多篇文章进行交叉事实比对
- 当发现 "文章 A 说 X 导致 Y" 而 "文章 B 说 X 导致 Z" 时，自动标记并生成矛盾报告卡片
- 技术路线：需要 LLM 对同主题文章做 pairwise 阅读 + 结构化 claim 提取

### 知识图谱持久化 (Persistent Knowledge Graph)
- 维护 `WIKI_DIR/.meta/knowledge_graph.json`，记录所有实体和关系
- 支持图查询：如"所有与 X 距离 ≤2 的概念"、"连接两个领域的桥接节点"
- 可导出为 Neo4j / Cytoscape 格式用于高级可视化

### 知识空白主动建议 (Gap Suggestion Engine)
- 分析领域覆盖密度，识别只有粗浅概述的薄弱区域
- 主动建议："你在 XX 领域只有 2 篇浅层文章，是否需要深入研究？"
- 可结合 `/arxiv` 技能自动拉取相关论文补充

### 合成数据与微调 (Synthetic Data + Fine-tuning)
- 参考 Karpathy 原文的远期构想：当知识库足够大时，可考虑生成 QA pairs 做微调
- 让模型把知识"内化"到权重中，而非仅依赖上下文窗口
