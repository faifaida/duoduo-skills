#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只跑指定子集专辑(关系恋爱/职业/养生大法/审美)的补抓。
复用 xhs_obsidian_sync 的枚举+签名+落盘函数, 依赖 imported_ids.json 做增量去重。
不修改 boards.json, 不影响每周全量自动化。"""
import sys, os
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import xhs_obsidian_sync as S

SUBSET = ["关系恋爱", "职业", "养生大法", "审美"]

def main():
    cfg = S.load_cfg()
    board_items = [(b["name"], b["id"]) for b in cfg["boards"] if b["name"] in SUBSET]
    cookie = S.load_cookie()
    proxies = S.load_proxies()
    engine, handle = S.load_engine()
    imported = S.load_imported()
    total = 0
    for album, board_id in board_items:
        ids = set(imported.get(album, []))
        before = len(ids)
        print("[subset] 开始 %s (已落盘 %d, 开始枚举+补抓)" % (album, before), flush=True)
        w = S.sync_one(album, board_id, ids, engine, handle, cookie, proxies)
        imported[album] = sorted(ids)
        S.save_imported(imported)
        print("[subset] %s 新增 %d 篇, 累计 %d" % (album, w, len(ids)), flush=True)
        total += w
    print("[subset] 全部完成, 新增 %d 篇" % total, flush=True)

if __name__ == "__main__":
    main()
