#!/usr/bin/env python3
"""
build_graph.py — wiki-compiler 知识图谱持久化引擎 (V3.1)

功能：
  1. 扫描 WIKI_DIR 下 Layer2 Markdown (concepts/ projects/ synthesis/)
  2. 解析 YAML frontmatter (tags / maturity / type) + Obsidian 双链 [[...]]
  3. 落盘 WIKI_DIR/.index/knowledge_graph.json，可被查询与可视化复用
  4. 输出 孤儿 / 枢纽 / 幽灵概念 统计

复用约定 (与现有脚本一致)：
  - WIKILINK_RE 与 wiki_dreamer.py 同源
  - frontmatter 字段与 VK_SPECIFICATION.md 一致
  - stdlib only, Python 3.9+
"""
import os
import re
import json
import argparse
from datetime import datetime, timezone

# 与 wiki_dreamer.py 同源的维基链接正则
# 支持 [[链接]] [[链接|显示]] [[链接#锚点]] [[链接#锚点|显示]]
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#([^\]]*?))?(?:\|([^\]]*?))?\]\]")

LAYER2_DIRS = ("concepts", "projects", "synthesis")


def parse_frontmatter(content: str) -> dict:
    """解析 YAML frontmatter，stdlib 手写版 (只取 tags/maturity/type/name)。"""
    fm: dict = {}
    if not content.startswith("---"):
        return fm
    try:
        end = content.index("---", 3)
    except ValueError:
        return fm
    block = content[3:end]
    for line in block.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip().lower()
        v = v.strip().strip("\"'")
        if k == "tags":
            v = v.strip("[]")
            fm["tags"] = [t.strip().strip("\"'") for t in v.split(",") if t.strip()]
        elif k in ("maturity", "type", "name"):
            fm[k] = v
    return fm


def collect_md_files(wiki_dir: str) -> list:
    """收集 Layer2 Markdown，跳过 .index / 隐藏目录 / .marp.md。"""
    out = []
    for layer in LAYER2_DIRS:
        base = os.path.join(wiki_dir, layer)
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if not f.endswith(".md") or f.endswith(".marp.md") or f.startswith("."):
                    continue
                out.append(os.path.join(root, f))
    return sorted(out)


def node_id(wiki_dir: str, fp: str) -> str:
    """节点 id = 相对 wiki_dir、去 .md 后缀的路径 (跨目录唯一)。"""
    rel = os.path.relpath(fp, wiki_dir)
    if rel.lower().endswith(".md"):
        rel = rel[:-3]
    return rel.replace(os.sep, "/")


def main() -> None:
    parser = argparse.ArgumentParser(description="知识图谱持久化引擎 (V3.1)")
    parser.add_argument("--wiki", required=True, help="Wiki 目录绝对路径")
    parser.add_argument("--out", help="输出 JSON 路径 (默认 WIKI_DIR/.index/knowledge_graph.json)")
    parser.add_argument("--pretty", action="store_true", help="JSON 缩进输出")
    args = parser.parse_args()

    wiki_dir = os.path.abspath(args.wiki)
    if not os.path.isdir(wiki_dir):
        print(f"Error: Wiki 目录不存在: {wiki_dir}")
        return

    files = collect_md_files(wiki_dir)
    nodes: dict = {}
    edges: list = []

    for fp in files:
        try:
            content = open(fp, "r", encoding="utf-8").read()
        except Exception as e:
            print(f"⚠️ 跳过不可读文件 {fp}: {e}")
            continue
        fm = parse_frontmatter(content)
        nid = node_id(wiki_dir, fp)
        try:
            mtime = os.path.getmtime(fp)
        except OSError:
            mtime = 0.0
        links = [m.group(1).strip() for m in WIKILINK_RE.finditer(content)]
        nodes[nid] = {
            "id": nid,
            "path": os.path.relpath(fp, wiki_dir).replace(os.sep, "/"),
            "layer2_dir": os.path.relpath(fp, wiki_dir).split(os.sep)[0],
            "tags": fm.get("tags", []),
            "maturity": fm.get("maturity", "unknown"),
            "type": fm.get("type", "unknown"),
            "mtime": mtime,
            "out_links": links,
        }

    norm_index = {nid.lower().split("/")[-1]: nid for nid in nodes}
    norm_full = {nid.lower(): nid for nid in nodes}
    for nid, n in nodes.items():
        for raw in n.pop("out_links"):
            target = raw.strip()
            key = target.lower()
            dst = norm_full.get(key) or norm_index.get(key.split("/")[-1])
            edges.append({"src": nid, "dst": dst, "raw": target, "exists": dst is not None})

    indeg: dict = {nid: 0 for nid in nodes}
    outdeg: dict = {nid: 0 for nid in nodes}
    for e in edges:
        outdeg[e["src"]] = outdeg.get(e["src"], 0) + 1
        if e["dst"]:
            indeg[e["dst"]] = indeg.get(e["dst"], 0) + 1

    for nid, n in nodes.items():
        n["in_degree"] = indeg.get(nid, 0)
        n["out_degree"] = outdeg.get(nid, 0)

    orphans = sorted([nid for nid in nodes if indeg.get(nid, 0) == 0])
    ghosts = sorted({e["raw"] for e in edges if not e["exists"]})
    hubs = sorted(nodes, key=lambda k: outdeg.get(k, 0) + indeg.get(k, 0), reverse=True)[:5]
    stubs = sorted([nid for nid, n in nodes.items() if n.get("maturity") == "stub"])

    graph = {
        "version": "3.1",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "wiki_dir": wiki_dir,
        "nodes": list(nodes.values()),
        "edges": edges,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "missing_targets": len(ghosts),
            "orphans": len(orphans),
            "stubs": len(stubs),
        },
        "orphans": orphans,
        "hubs": hubs,
        "stubs": stubs,
        "ghosts": ghosts,
    }

    out_path = args.out or os.path.join(wiki_dir, ".index", "knowledge_graph.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2 if args.pretty else None)

    print("═══════════════════════════════════════")
    print("  🕸️ 知识图谱已持久化 (V3.1)")
    print("═══════════════════════════════════════")
    print(f"  节点: {len(nodes)}  边: {len(edges)}")
    print(f"  🏝️ 孤儿 (零入链): {len(orphans)}")
    for o in orphans[:10]:
        print(f"     - {o}")
    print(f"  ⭐ 枢纽 Top5: {', '.join(hubs) if hubs else '无'}")
    print(f"  👻 幽灵引用 (链到不存在): {len(ghosts)}")
    for g in ghosts[:10]:
        print(f"     - [[{g}]]")
    print(f"  📝 stub 待补: {len(stubs)}")
    print(f"  💾 已写入: {out_path}")


if __name__ == "__main__":
    main()
