#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""轻量限流探测: 取一篇已落盘笔记的完整 url, 调一次 get_note_info, 看是否命中限流。"""
import sys, os, re
SP = os.path.dirname(os.path.abspath(__file__))
SPIDER = os.path.join(SP, "Spider_XHS")
os.chdir(SPIDER)
os.environ["NODE_PATH"] = os.path.join(SPIDER, "node_modules")
sys.path.insert(0, SP)
sys.path.insert(0, SPIDER)

import xhs_obsidian_sync as S
from apis.xhs_pc_apis import XHS_Apis

VAULT = "/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/05_CONTENT/小红书收藏"
cookie = S.load_cookie()
proxies = S.load_proxies()
eng = XHS_Apis()

# 取一篇完整 url(含 xsec_token)
test_url = None
for a in ["关系恋爱", "职业", "养生大法", "审美"]:
    d = os.path.join(VAULT, a)
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        if not f.endswith(".md") or f.startswith("专辑-"):
            continue
        txt = open(os.path.join(d, f), encoding="utf-8").read()
        m = re.search(r'url:\s*(\S+)', txt)
        if m and "xiaohongshu.com/explore/" in m.group(1):
            test_url = m.group(1).strip().strip('"')
            break
    if test_url:
        break

if not test_url:
    print("PROBE: 未找到可用 url, 跳过")
    sys.exit(0)

print("PROBE url:", test_url[:80], "...")
ok, msg, res = eng.get_note_info(test_url, cookie, proxies)
print("PROBE success =", ok)
print("PROBE msg =", (msg or "")[:400])
if not ok and any(k in (msg or "").lower() for k in ["limit", "频繁", "too many", "rate", "请求过于", "访问频繁"]):
    print("PROBE RESULT: 命中限流, 不可跑")
else:
    print("PROBE RESULT: 未限流, 可以跑")
