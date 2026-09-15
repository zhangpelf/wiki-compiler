#!/usr/bin/env python3
"""
contradiction_detector.py — wiki-compiler 矛盾检测引擎 MVP (V3.1)

ROADMAP V3.1 目标：解决"同一概念，不同来源"之间的事实性冲突。
本 MVP 为启发式初筛 (无 LLM 调用)：同标签分组 → 四信号打分 → 输出候选对 +
可直接贴给 LLM 的 pairwise 判定 prompt。重型判定交给 LLM，脚本只负责找茬。

四信号：
  1. maturity_mismatch — authoritative/reviewed vs stub/draft 同组出现
  2. negation_hits — 否定/转折词命中数 (中英词表)
  3. number_mismatch — 两文抽到的数字/年份集合不一致
  4. jaccard — 同标签但正文 Jaccard < 0.3 视为可疑分歧

stdlib only, Python 3.9+
"""
import os
import re
import json
import argparse
from datetime import datetime, timezone

NEGATION_RE = re.compile(
    r"(不|没|无|非|反对|冲突|矛盾|然而|但是|相反|质疑|推翻|证伪|不一致|not\b|no\b"
    r"|against|however|contradict|conflict|false\b|refut)",
    re.IGNORECASE,
)
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?%?")
TOKEN_RE = re.compile(r"[\u4e00-\u9fff]+|[a-zA-Z]{2,}")
HIGH_MATURITY = {"authoritative", "reviewed"}
LOW_MATURITY = {"stub", "draft"}


def parse_frontmatter(content: str) -> dict:
    fm: dict = {}
    if not content.startswith("---"):
        return fm
    try:
        end = content.index("---", 3)
    except ValueError:
        return fm
    for line in content[3:end].splitlines():
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


def strip_frontmatter(content: str) -> str:
    if content.startswith("---"):
        try:
            end = content.index("---", 3)
            return content[end + 3:]
        except ValueError:
            pass
    return content


def jaccard(a: str, b: str) -> float:
    sa, sb = set(TOKEN_RE.findall(a.lower())), set(TOKEN_RE.findall(b.lower()))
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def collect_docs(wiki_dir: str) -> list:
    """收集 Layer2 + Layer3 文本 (跳过隐藏目录与 .marp.md)。"""
    docs = []
    for root, dirs, files in os.walk(wiki_dir):
        if "/." in root or "\\." in root:
            continue
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if not f.endswith(".md") or f.endswith(".marp.md") or f.startswith("."):
                continue
            fp = os.path.join(root, f)
            try:
                content = open(fp, "r", encoding="utf-8").read()
            except Exception:
                continue
            fm = parse_frontmatter(content)
            docs.append(
                {
                    "path": os.path.relpath(fp, wiki_dir).replace(os.sep, "/"),
                    "tags": fm.get("tags", []),
                    "maturity": fm.get("maturity", "unknown"),
                    "body": strip_frontmatter(content),
                }
            )
    return docs


def llm_prompt(a: dict, b: dict, shared: list) -> str:
    return (
        "请做 pairwise 矛盾判定 (V3.1)：\n"
        f"共享标签：{', '.join(shared)}\n"
        f"A《{a['path']}》(maturity={a['maturity']}) vs B《{b['path']}》(maturity={b['maturity']})\n"
        "1) 两文对同一概念的事实断言是否直接冲突？2) 冲突点原文引用。\n"
        "3) verdict: 同义/互补/真矛盾/证据不足，并给一句话理由。"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="矛盾检测引擎 MVP (V3.1)")
    parser.add_argument("--wiki", required=True, help="Wiki 目录绝对路径")
    parser.add_argument("--min-shared-tags", type=int, default=1)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--json-out", help="候选 JSON 输出路径 (默认仅 stdout)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    wiki_dir = os.path.abspath(args.wiki)
    if not os.path.isdir(wiki_dir):
        print(f"Error: Wiki 目录不存在: {wiki_dir}")
        return

    docs = collect_docs(wiki_dir)
    tag_groups: dict = {}
    for i, d in enumerate(docs):
        for t in d["tags"]:
            tag_groups.setdefault(t, []).append(i)

    seen = set()
    candidates = []
    for tag, idxs in tag_groups.items():
        for x in range(len(idxs)):
            for y in range(x + 1, len(idxs)):
                i, j = idxs[x], idxs[y]
                key = (min(i, j), max(i, j))
                if key in seen:
                    continue
                seen.add(key)
                a, b = docs[i], docs[j]
                shared = sorted(set(a["tags"]) & set(b["tags"]))
                if len(shared) < args.min_shared_tags:
                    continue
                mat = (
                    (a["maturity"] in HIGH_MATURITY and b["maturity"] in LOW_MATURITY)
                    or (b["maturity"] in HIGH_MATURITY and a["maturity"] in LOW_MATURITY)
                )
                neg = len(NEGATION_RE.findall(a["body"])) + len(NEGATION_RE.findall(b["body"]))
                na, nb = set(NUMBER_RE.findall(a["body"])), set(NUMBER_RE.findall(b["body"]))
                num_mismatch = bool((na ^ nb)) and bool(na or nb)
                jac = jaccard(a["body"], b["body"])
                score = (2.0 if mat else 0.0) + min(neg * 0.5, 3.0) + (1.5 if num_mismatch else 0.0) + (1.0 if jac < 0.3 else 0.0)
                if score <= 0:
                    continue
                candidates.append(
                    {
                        "a": a["path"],
                        "b": b["path"],
                        "shared_tags": shared,
                        "score": round(score, 2),
                        "signals": {
                            "maturity_mismatch": mat,
                            "negation_hits": neg,
                            "number_mismatch": num_mismatch,
                            "jaccard": round(jac, 3),
                        },
                        "llm_prompt": llm_prompt(a, b, shared),
                    }
                )
                if len(candidates) >= 500:
                    break

    candidates.sort(key=lambda c: c["score"], reverse=True)
    top = candidates[: args.top]

    if args.json_out:
        out = args.json_out if os.path.isabs(args.json_out) else os.path.join(wiki_dir, args.json_out)
        od = os.path.dirname(out)
        if od:
            os.makedirs(od, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(
                {"version": "3.1-mvp", "checked_at": datetime.now(timezone.utc).isoformat(), "candidates": top},
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"💾 已写入: {out}")

    if args.format == "json" and not args.json_out:
        print(json.dumps(top, ensure_ascii=False, indent=2))
        return

    print("═══════════════════════════════════════")
    print("  ⚔️ 矛盾候选报告 (V3.1 MVP)")
    print("═══════════════════════════════════════")
    print(f"  文档: {len(docs)}  标签组: {len(tag_groups)}  候选: {len(candidates)} (Top{args.top})")
    if not top:
        print("  ✅ 未发现明显矛盾候选，知识库自洽。")
        return
    for k, c in enumerate(top, 1):
        s = c["signals"]
        print(f"\n  #{k} score={c['score']} [{', '.join(c['shared_tags'])}]")
        print(f"     A: {c['a']}")
        print(f"     B: {c['b']}")
        print(f"     成熟度错配={s['maturity_mismatch']} 否定命中={s['negation_hits']} 数字分歧={s['number_mismatch']} Jaccard={s['jaccard']}")


if __name__ == "__main__":
    main()
