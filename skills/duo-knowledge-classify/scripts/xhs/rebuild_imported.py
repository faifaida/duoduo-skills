#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 vault 现有 md(前端 url 含 noteId) 重建 imported_ids.json 增量状态(全 8 本)。
避免无 imported 时把已落盘笔记全部重抓。"""
import os, re, json

VAULT = "/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/05_CONTENT/小红书收藏"
ALBUMS = ["习惯和思考", "文旅", "青旅", "剪辑", "职业", "养生大法", "关系恋爱", "审美"]

imported = {}
for a in ALBUMS:
    d = os.path.join(VAULT, a)
    if not os.path.isdir(d):
        imported[a] = []
        continue
    ids = set()
    for f in os.listdir(d):
        if not f.endswith(".md") or f.startswith("专辑-"):
            continue
        txt = open(os.path.join(d, f), encoding="utf-8").read()
        m = re.search(r'url:\s*https?://www\.xiaohongshu\.com/explore/([0-9a-f]{8,})', txt)
        if m:
            ids.add(m.group(1))
    imported[a] = sorted(ids)
    print("%-6s 已有 noteId %d 个" % (a, len(ids)))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imported_ids.json")
json.dump(imported, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("已写入", out)
