#!/usr/bin/env python3
import os
import argparse
import re
from datetime import date


def search_files(wiki_dir, query=None, tag=None):
    results = []
    # Simplified search: matching query in content or tag in frontmatter
    for root, dirs, files in os.walk(wiki_dir):
        if "/." in root or "\\." in root:
            continue
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".md") and not f.endswith(".marp.md"):
                fp = os.path.join(root, f)
                try:
                    content = open(fp, "r", encoding="utf-8").read()
                    if tag:
                        # naive tag check
                        if f"tag" in content.lower() and tag.lower() in content.lower():
                            results.append((fp, content))
                    elif query:
                        if (
                            query.lower() in content.lower()
                            or query.lower() in f.lower()
                        ):
                            results.append((fp, content))
                except Exception:
                    pass
    return results


def get_files_from_list(file_list, wiki_dir):
    """Get file contents from a comma-separated list of files"""
    results = []
    for file_path in file_list.split(","):
        file_path = file_path.strip()
        if not file_path:
            continue
        # Handle relative paths by making them absolute if needed
        if not os.path.isabs(file_path):
            # If it's a relative path, assume it's relative to the wiki directory
            file_path = os.path.join(wiki_dir, file_path)

        if os.path.isfile(file_path) and file_path.endswith(".md"):
            try:
                content = open(file_path, "r", encoding="utf-8").read()
                results.append((file_path, content))
            except Exception as e:
                print(f"警告: 无法读取文件 {file_path}: {e}")
        else:
            print(f"警告: 文件不存在或不是Markdown文件: {file_path}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Wiki Weaver 知识大串联抽取器")
    parser.add_argument("--wiki", required=True, help="Wiki 目录绝对路径")
    parser.add_argument("--query", help="提取包含此关键词的所有研究片段")
    parser.add_argument("--tag", help="提取属于此标签的所有研究片段")
    parser.add_argument(
        "--files", help="逗号分隔的文件列表，跳过BM25搜索直接处理指定文件"
    )
    args = parser.parse_args()

    # If files are specified, bypass search and use those files directly
    if args.files:
        docs = get_files_from_list(args.files, args.wiki)
        if not docs:
            print("⚠️ 未找到任何有效的文档。")
            return

        print("====================================")
        print(f"🧶 Wiki Weaver 已为您处理 {len(docs)} 份指定文档")
        print("====================================\n")

        for fp, _ in docs:
            print(fp)

        print("\n----------")
        print(
            "【系统指令】：请严格执行 MAP-REDUCE 任务流，使用阅读工具逐个读取上方输出的文件路径，开展并行的信息抽取（Map），然后执行大纲与溯源综述（Reduce & Synthesis）。"
        )
        return

    # Original search logic for query/tag
    if not args.query and not args.tag:
        print("请指定 --query 或 --tag")
        return

    docs = search_files(args.wiki, query=args.query, tag=args.tag)
    if not docs:
        print("⚠️ 未找到任何相关文档。")
        return

    print("====================================")
    print(f"🧶 Wiki Weaver 已为您找到 {len(docs)} 份相关文档的路径")
    print("====================================\n")

    for fp, _ in docs:
        print(fp)

    print("\n----------")
    print(
        "【系统指令】：请严格执行 MAP-REDUCE 任务流，使用阅读工具逐个读取上方输出的文件路径，开展并行的信息抽取（Map），然后执行大纲与溯源综述（Reduce & Synthesis）。"
    )


if __name__ == "__main__":
    main()
