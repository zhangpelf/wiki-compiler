# Wiki Compiler Future Roadmap

这里记录了 Wiki Compiler (VK) 项目从个人助理向“跨领域学术研究中枢”进化的长期愿景。

## 📍 愿景：知识不应只是被“存放”，而应在深夜中“生长”。

### ✅ V3.1: 矛盾检测 MVP + 图谱 JSON 持久化 (已落地)
- `scripts/contradiction_detector.py`：同标签分组 + 成熟度错配/否定词/数字分歧/Jaccard 四信号打分，输出候选对 + LLM pairwise prompt（零 LLM 调用）
- `scripts/build_graph.py`：双链 + frontmatter 落盘 `.index/knowledge_graph.json`，输出孤儿/枢纽/幽灵/stub 统计

### V3.2: 知识图谱查询 — 按需灵活调整 ❌ 不做重型版
- ~~Neo4j / Cytoscape 持久化与语义查询~~：实测 `.index/knowledge_graph.json` 已够查询与可视化复用，重型图数据库投入产出比低，砍掉。
- 实际应用中需要再按需加（导出脚本半天可写），不预支复杂度。

### V3.3: Layer 3 可视化 Dashboard — 可选 📋
- Dataview 聚合 + 图谱展示，需要时再做，不阻塞主流程。

### V3.5: 主动式研究助手 (Proactive Research Agent)
- **目标**：自动补齐知识版图。
- **功能**：周期性对比领域内的最新顶级论文，提示：“该主题有 3 篇来自 ICML/NeurIPS 的最新变体，是否需要我将其总结并编入库中？”

### V4.0: 知识蒸馏与私有微调 (Distill & Fine-tune)
- **目标**：跨越上下文窗口的限制，将知识内化到权重中。
- **功能**：将高权重的知识库内容转化为合成数据集（Synthetic QA Pair），支持对 7B 等本地小模型进行 SFT 微调。

---
> [!TIP]
> 每一个功能的演进，都将严格遵循 VK Spec 1.0 的学术严谨性标准。