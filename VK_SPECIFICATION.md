# Wiki Compiler Compilation Specification (VK Spec 1.0)

本项目遵循一套标准化的“资料-知识”转换协议。这套规范旨在确保通过 AI 编译出的个人知识库具备**增量稳定性**、**学术严谨性**与**高度双链互联性**。

## 1. 目录拓扑结构 (Directory Topology)

所有 VK 兼容的仓库必须包含以下核心路径：

- `/raw/`: 存放未经处理的原始素材（PDF, Markdown, HTML 截取, 笔记摘要）。
- `/wiki/`: 存放编译后的长青知识库。
  - `/projects/`: 针对特定工程或研究主题的文章。
  - `/concepts/`: 原子化的概念卡片。
  - `/synthesis/`: 跨文献的 Map-Reduce 综述文档。
- `/.meta/`: 存放编译元数据（如 `compiled_ledger.json`）。

## 2. 元数据标准 (Frontmatter Standard)

每篇 Wiki 文章顶端必须包含以下 YAML 字段：

```yaml
---
name: 标题
type: concept | project | synthesis | stub
maturity: stub | draft | reviewed | authoritative
date: YYYY-MM-DD
sources: [raw_file_path]    # 必须指向原始素材路径
tags: [相关标签]
---
```

## 3. 编织与综述准则 (Synthesis Rules)

在执行 `/wiki-weaver` 任务时，必须严格遵守**“句级溯源 (LSC)”**：
- 综述文档中任何关于客观事实的陈述，结尾必须附带 `[[原始文章名]]` 形式的内部链接。
- 绝不允许引用不存在于知识库内的信息。

## 4. 幂等性保障 (Idempotency)

- 系统通过 `compiled_ledger.json` 维护文件指纹。
- 已处理的文件严禁二次重写，除非强制触发重编。

---

# Wiki Compiler V3 Roadmap

## V3.1: 矛盾检测引擎 (Contradiction Engine)
- 利用 LLM 对同一主题下的多篇文章进行事实冲突比对。
- 自动生成矛盾报告，提示用户知识库中存在的冲突观点。

## V3.2: 知识图谱持久化 (Graph Persistence)
- 将 Obsidian 的链接转换为全量 JSON 拓扑。
- 支持类似于“寻找两个领域间的跨界连接点”这类图查询指令。

## V3.5: 主动式研究助手 (ArXiv Proactive Supplement)
- 自动识别知识库中的“知识空白(Gap)”。
- 主动拉取 ArXiv 最新的论文并提示：“检测到你在 XX 领域的知识较陈旧，是否需要更新？”

## V4.0: 知识蒸馏与私有模型微调 (Distill & Fine-tune)
- 基于现有知识库生成高质量 QA 对。
- 让用户拥有一套“训练在自己笔记库上”的轻量级本地模型。