#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""稳健枚举: 打开后等首屏渲染(空则刷新) + 滚动到底等高度稳定 + 每本低于已落盘数则刷新重试取并集。
前台运行(依赖 Chrome GUI), 缓存到 _enum_cache.json, 打印每本真正缺失数。"""
import sys, os, json, time, re
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import xhs_obsidian_sync as S

def enum_once(board_id, max_iter=400, wait=2.5, init_wait=8):
    S.chrome_open("https://www.xiaohongshu.com/board/%s/" % board_id)
    time.sleep(init_wait)
    try:
        f = S.run_js(S.JS_LINKS, 20)
        fn = len(json.loads(f) if f else [])
    except Exception:
        fn = 0
    if fn == 0:
        S.run_js("location.reload();")
        time.sleep(init_wait)
    seen = set(); out = []; last_h = 0; stable = 0
    for i in range(max_iter):
        S.run_js("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait)
        try:
            raw = S.run_js(S.JS_LINKS, 20)
            hrefs = json.loads(raw) if raw else []
        except Exception:
            hrefs = []
        new = 0
        for h in hrefs:
            m = re.search(r"/(?:explore|board/[^/]+)/([0-9a-f]{8,})", h or "")
            if not m:
                continue
            nid = m.group(1)
            if nid in seen:
                continue
            seen.add(nid)
            mt = re.search(r"xsec_token=([^&]+)", h)
            xsec = mt.group(1) if mt else ""
            out.append((nid, xsec)); new += 1
        try:
            h_now = int(S.run_js("document.body.scrollHeight", 10) or 0)
        except Exception:
            h_now = last_h
        if new == 0 and h_now == last_h:
            stable += 1
            if stable >= 8:
                break
        else:
            stable = 0
        last_h = h_now
    return out

def enum_with_retry(board_id, have_count, tries=3):
    best = []
    for t in range(tries):
        links = enum_once(board_id)
        if len(links) > len(best):
            best = links
        if len(links) >= have_count:
            break
        print("  [retry] 第%d次 %d 条 < 已落盘 %d, 刷新重试" % (t + 1, len(links), have_count), flush=True)
        time.sleep(4)
    return best

SUBSET = ["关系恋爱", "职业", "养生大法", "审美"]
cfg = S.load_cfg()
board_items = [(b["name"], b["id"]) for b in cfg["boards"] if b["name"] in SUBSET]
imported = S.load_imported()
cache = {}
for album, board_id in board_items:
    have = len(imported.get(album, []))
    t0 = time.time()
    print("[enum] 开始枚举 %s (已落盘 %d)" % (album, have), flush=True)
    links = enum_with_retry(board_id, have)
    cache[album] = links
    print("[enum] %s 枚举到 %d 条, 用时 %.0fs" % (album, len(links), time.time() - t0), flush=True)
json.dump(cache, open(os.path.join(SP, "_enum_cache.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("[enum] 缓存已写入 _enum_cache.json", flush=True)

print("=== 对比(枚举 vs 已落盘 vs 真正缺失) ===")
total_missing = 0
for a, ls in cache.items():
    enum_ids = set(n for n, x in ls)
    have = set(imported.get(a, []))
    missing = enum_ids - have
    total_missing += len(missing)
    print("  %s: 枚举%d, 已落盘%d, 真正缺失%d" % (a, len(enum_ids), len(have), len(missing)), flush=True)
print("  4 本合计真正缺失: %d" % total_missing, flush=True)
