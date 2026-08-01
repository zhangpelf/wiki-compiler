# Wiki Compiler Compilation Specification (VK Spec 1.0)

本项目遵循一套标准化的"资料-知识"转换协议。这套规范旨在确保通过 AI 编译出的个人知识库具备**增量稳定性**、**学术严谨性**与**高度双链互联性**。

## 1. 目录拓扑结构 (Directory Topology)

所有 VK 兼容的仓库必须包含以下核心路径：

- `/raw/`: 存放未经处理的原始素材（PDF, Markdown, HTML 截取, 笔记摘要）。
- `/wiki/`: 存放编译后的长青知识库。
  - `/projects/`: 针对特定工程或研究主题的文章（Layer 2）。
  - `/concepts/`: 原子化的概念卡片（Layer 2）。
  - `/synthesis/`: 跨文献的 Map-Reduce 综述文档。
  - `/.index/`: Layer 3 索引（总结 + 标签），存放 `<原名>.summary.md` 与 `compiled_ledger.json`。
    - `.index` 为 V3 标准路径；旧版 `.meta/` 目录在首次运行时自动迁移至 `.index/`。

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

maturity 生命周期：`stub`（仅占位）→ `draft`（初稿）→ `reviewed`（人工/做梦机制审视过）→ `authoritative`（多源交叉验证）。

## 3. 编织与综述准则 (Synthesis Rules)

在执行 `/wiki-weaver` 任务时，必须严格遵守**"句级溯源 (LSC)"**：

- 综述文档中任何关于客观事实的陈述，结尾必须附带 `[[原始文章名]]` 形式的内部链接。
- 绝不允许引用不存在于知识库内的信息。

## 4. 幂等性保障 (Idempotency)

- 系统通过 `compiled_ledger.json`（位于 `WIKI_DIR/.index/`）维护文件指纹。
- 已处理的文件严禁二次重写，除非强制触发重编。

## 5. 增量编译流程 (Incremental Compilation)

1. `sync_manifest.py --raw <RAW_DIR> --wiki <WIKI_DIR>` 比对 raw 文件哈希与账本，输出待编译清单。
2. LLM 通读目标源文件，提炼为 Layer 2 文章（含 YAML frontmatter + Obsidian 双链 + 必要的 Mermaid 结构图）。
3. 自动生成 Layer 3 `<原名>.summary.md` 到 `.index/`。
4. `sync_manifest.py --mark-done` 刷新账本，封存已处理文件。

> 未来演进（矛盾检测 / 图谱持久化 / 主动研究助手 / 知识蒸馏）见 `ROADMAP.md`。
