#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补齐剩余关键词对标（轻量·合并版）。

只跑「尚未拿到」的关键词（默认：小众泳衣/人生教练/职场关系），
从已有 03_补对标_*.json 读旧数据合并，避免覆盖第一次已拿到的词。
每词仅 1 次搜索（最多点赞），遇风控/限流立刻停，绝不狂锤。

用法：
  python benchmark_scan_remaining.py
  python benchmark_scan_remaining.py "小众泳衣,人生教练,职场关系"
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

DEFAULT_KW = ["小众泳衣", "人生教练", "职场关系"]
PER_KW = 20
TOP_N = 12
SORT = 2  # 最多点赞

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

def title_of(note):
    nc = note.get("note_card") or {}
    return (nc.get("display_title") or nc.get("title") or note.get("display_title")
            or note.get("title") or "").strip()

def form_of(note):
    nc = note.get("note_card") or {}
    return "video" if (nc.get("type") or note.get("type") or "").lower() == "video" else "image"

def main():
    kws = sys.argv[1].split(",") if len(sys.argv) > 1 else DEFAULT_KW
    kws = [k.strip() for k in kws if k.strip()]

    # 读已有数据合并
    results = {}
    if os.path.exists(OUT):
        try:
            results = json.load(open(OUT, encoding="utf-8"))
        except Exception:
            results = {}

    cookie = S.load_cookie()
    proxies = S.load_proxies()
    engine = XHS_Apis()
    blocked = False

    for kw in kws:
        print("[kw] %s" % kw, flush=True)
        try:
            ok, msg, notes = engine.search_some_note(kw, PER_KW, cookie, sort_type_choice=SORT)
        except Exception as e:
            ok, msg, notes = False, str(e), None
        if not ok or S.is_ratelimit(msg):
            print("  [BLOCKED] %s — 停止，避免加重风控" % str(msg)[:60], flush=True)
            blocked = True
            break
        if not isinstance(notes, list) or len(notes) == 0:
            print("  [空] 限流中(data为空) 或真无结果，跳过，待冷却后重跑", flush=True)
            results[kw] = []   # 保留空，下次再补
            time.sleep(random.uniform(8, 12))
            continue
        rows = []
        for n in notes:
            nc = n.get("note_card") or {}
            a = nc.get("user") or {}
            rows.append({
                "author": a.get("nickname") or a.get("name") or "",
                "author_id": a.get("user_id") or nc.get("user_id"),
                "title": title_of(n),
                "form": form_of(n),
                "interactions": get_interactions(n),
            })
        rows.sort(key=lambda x: -x["interactions"])
        results[kw] = rows[:TOP_N]
        print("  [ok] %s 拿到 %d 篇" % (kw, len(rows)), flush=True)
        time.sleep(random.uniform(8, 12))

    json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if blocked:
        print("[done-BLOCKED] 部分补齐，剩余词待冷却后重跑", flush=True)
    else:
        print("[done] 已合并写入 %s" % OUT, flush=True)

if __name__ == "__main__":
    main()
