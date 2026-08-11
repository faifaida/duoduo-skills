#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补对标（轻量·风控安全版）。

设计目标：每词仅 1 次搜索（最多点赞排序），不查粉丝、不调 get_user_info，
从搜索结果直接拿互动量 → 调用量极低（6 词 ≈ 6~12 次），不会触发 300011。
遇到「账号异常/300011」立刻停止并写出已拿到的部分，绝不狂锤加重风控。

输出：03_补对标_家族二代等.json（每词 Top 笔记：标题/作者/形式/互动量）。
"""
import sys, os, json, time, random

SP = "/Users/Zhuanz/.workbuddy/skills/duo-knowledge-classify/scripts/xhs"
SPIDER = os.path.join(SP, "Spider_XHS")
sys.path.insert(0, SP)
sys.path.insert(0, SPIDER)
os.chdir(SPIDER)
os.environ["NODE_PATH"] = os.path.join(SPIDER, "node_modules")

import xhs_obsidian_sync as S
from apis.xhs_pc_apis import XHS_Apis

OUT = ("/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/"
       "DuoDuo_AI_Workspace/03_ACTIVE PROJECTS/ai个人公司/公司档案/02_内容运营/"
       "Human3_内容执行包/03_补对标_家族二代等.json")

# 6 个词覆盖 3 个新号对应品类
KEYWORDS = ["家族企业二代", "女性创业", "AI副业", "小众泳衣", "人生教练", "职场关系"]
PER_KW = 20          # 每词抓 20 篇（1 次搜索）
TOP_N = 12           # 每词保留互动最高 Top12
SORT = 2             # 2=最多点赞（直接拿爆款）

def parse_num(v):
    if v is None:
        return None
    s = str(v).strip().replace("+", "").replace(" ", "")
    try:
        if "万" in s or "w" in s.lower():
            return int(float(s.replace("万", "").replace("w", "").replace("W", "")) * 10000)
        return int(float(s))
    except Exception:
        return None

def get_interactions(note):
    cand = []
    nc = note.get("note_card") or {}
    for d in (nc.get("interact_info") or {}, note.get("interact_info") or {}):
        if not isinstance(d, dict):
            continue
        for k in ("liked_count", "collected_count", "comment_count", "share_count", "likes"):
            n = parse_num(d.get(k))
            if n is not None:
                cand.append(n)
    return sum(cand) if cand else 0

def note_title(note):
    nc = note.get("note_card") or {}
    return (nc.get("display_title") or nc.get("title") or note.get("display_title")
            or note.get("title") or "").strip()

def note_form(note):
    nc = note.get("note_card") or {}
    t = (nc.get("type") or note.get("type") or "").lower()
    return "video" if t == "video" else "image"

def main():
    cookie = S.load_cookie()
    proxies = S.load_proxies()
    engine = XHS_Apis()
    results = {}
    blocked = False

    for kw in KEYWORDS:
        print("[kw] %s" % kw, flush=True)
        try:
            ok, msg, notes = engine.search_some_note(kw, PER_KW, cookie, sort_type_choice=SORT)
        except Exception as e:
            ok, msg, notes = False, str(e), None

        # 风控命中：立刻停，写出已拿到的部分
        if not ok or S.is_ratelimit(msg):
            print("  [BLOCKED] 命中风控或搜索失败: %s" % str(msg)[:60], flush=True)
            print("  [BLOCKED] 停止后续搜索，避免加重风控。已产出部分结果。", flush=True)
            blocked = True
            break

        if not isinstance(notes, list):
            print("  [空] 无结果", flush=True)
            results[kw] = []
            time.sleep(random.uniform(8, 12))
            continue

        rows = []
        for n in notes:
            nc = n.get("note_card") or {}
            a = nc.get("user") or {}
            aid = a.get("user_id") or nc.get("user_id")
            nick = a.get("nickname") or a.get("name") or ""
            rows.append({
                "author": nick,
                "author_id": aid,
                "title": note_title(n),
                "form": note_form(n),
                "interactions": get_interactions(n),
            })
        rows.sort(key=lambda x: -x["interactions"])
        top = rows[:TOP_N]
        print("  [ok] %s 拿到 %d 篇，Top%d 互动量: %s" % (
            kw, len(rows), len(top),
            ", ".join("%s(%d)" % (r["title"][:12], r["interactions"]) for r in top[:3])), flush=True)
        results[kw] = top
        time.sleep(random.uniform(8, 12))   # 词间冷却，极保守

    json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if blocked:
        print("[done-BLOCKED] 部分写入 %s（后续需在风控解除后重跑）" % OUT, flush=True)
    else:
        print("[done] 写入 %s" % OUT, flush=True)

if __name__ == "__main__":
    main()
