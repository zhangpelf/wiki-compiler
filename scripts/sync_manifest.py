#!/usr/bin/env python3
"""
sync_manifest.py — wiki-compiler 增量同步引擎（三层卷积架构）

功能：
  1. 扫描 RAW_DIR 文件，计算 SHA256 哈希
  2. 对比 .index/compiled_ledger.json，找出新增/更改文件
  3. 检测 Layer 2 有但 Layer 3 缺失的文件
  4. --mark-done 模式：更新账本

三层结构：
  Layer 1: RAW_DIR (原始资料)
  Layer 2: WIKI_DIR/{concepts,projects}/ (精炼 Markdown)
  Layer 3: WIKI_DIR/.index/*.summary.md (总结 + 标签)
"""
import os
import json
import argparse
import hashlib

def get_file_hash(filepath):
    """计算文件的 SHA256 哈希值，确保防冗余。"""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception as e:
        return None

def find_missing_layer3(wiki_dir):
    """找出 Layer 2 有但 Layer 3 没有的文件（缺 summary）"""
    index_dir = os.path.join(wiki_dir, '.index')
    missing = []

    for layer2_dir in ["concepts", "projects"]:
        layer2_path = os.path.join(wiki_dir, layer2_dir)
        if not os.path.exists(layer2_path):
            continue
        for f in os.listdir(layer2_path):
            if not f.endswith(".md") or f.endswith(".marp.md"):
                continue
            basename = f[:-3]  # remove .md
            summary_file = os.path.join(index_dir, f"{basename}.summary.md")
            if not os.path.exists(summary_file):
                missing.append({
                    "layer2": os.path.join(layer2_dir, f),
                    "expected_layer3": os.path.join(".index", f"{basename}.summary.md"),
                })
    return missing


def main():
    parser = argparse.ArgumentParser(description="增量编译清单同步工具（三层卷积架构）")
    parser.add_argument("--raw", required=True, help="原始资料 RAW 目录的绝对路径")
    parser.add_argument("--wiki", required=True, help="Wiki 编译目录的绝对路径")
    parser.add_argument("--mark-done", action="store_true", help="是否标记当前 raw 作为已处理（更新 Ledger）")
    args = parser.parse_args()

    raw_dir = args.raw
    wiki_dir = args.wiki
    # V3: 使用 .index/ 目录（兼容旧 .meta/）
    index_dir = os.path.join(wiki_dir, '.index')
    meta_dir = os.path.join(wiki_dir, '.meta')
    # 优先使用 .index/，如果不存在但 .meta/ 存在则迁移
    if not os.path.exists(index_dir) and os.path.exists(meta_dir):
        os.rename(meta_dir, index_dir)
    ledger_path = os.path.join(index_dir, 'compiled_ledger.json')

    if not os.path.exists(raw_dir):
        print(f"Error: 原始数据目录不存在: {raw_dir}")
        return

    # 确保存放账本的目录存在
    os.makedirs(index_dir, exist_ok=True)
    os.makedirs(os.path.join(wiki_dir, 'concepts'), exist_ok=True)
    os.makedirs(os.path.join(wiki_dir, 'projects'), exist_ok=True)

    # 读取旧账本
    ledger = {}
    if os.path.exists(ledger_path):
        try:
            with open(ledger_path, 'r', encoding='utf-8') as f:
                ledger = json.load(f)
        except Exception:
            ledger = {}

    current_files = {}
    # 扫描 RAW 目录里的所有文件 (忽略隐藏文件)
    for root, dirs, files in os.walk(raw_dir):
        # 刨除一些明显的无关目录如 .git 等
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.startswith('.'):
                continue
            filepath = os.path.join(root, file)
            # 因为文件可能很大，计算摘要比较稳妥
            file_hash = get_file_hash(filepath)
            if file_hash:
                current_files[filepath] = file_hash

    if args.mark_done:
        # 当 LLM 完成更新后，把目前的库状态写入帐本（全量更新为当前）
        for filepath, fhash in current_files.items():
            ledger[filepath] = fhash
        with open(ledger_path, 'w', encoding='utf-8') as f:
            json.dump(ledger, f, ensure_ascii=False, indent=2)
        print("✅ Ledger 已更新，当前 raw 目录内容皆被标记为已处理防重复状态。")
        return

    # 如果是获取队列模式（过滤出新文件和修改过的文件）
    pending_files = []
    for filepath, fhash in current_files.items():
        if filepath not in ledger or ledger[filepath] != fhash:
            pending_files.append(filepath)

    if not pending_files:
        print("💡 当前没有任何增量更新内容，知识库已是最新状态。")
    else:
        print("======== 待编译的新资料 (Pending Queue) ========")
        for pf in pending_files:
            print(f"- {pf}")

    # 三层卷积架构：检测缺失的 Layer 3 summary
    missing_l3 = find_missing_layer3(wiki_dir)
    if missing_l3:
        print(f"\n⚠️  缺失 Layer 3 summary ({len(missing_l3)} 个):")
        for m in missing_l3:
            print(f"  Layer 2: {m['layer2']}")
            print(f"  需生成: {m['expected_layer3']}")
    else:
        print("\n✅ Layer 3 索引完整")

if __name__ == "__main__":
    main()
