#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resync_broken.py — 重抓 xhs_broken_urls 清单里的失败页（Security Verification / 风控墙）。

机制（复用 xhs_obsidian_sync 的引擎与落盘）：
  - 解析 broken 文件（列: board \t status \t url），提取 noteId + xsec_token。
  - 对每条调 Spider_XHS 签名 API 抓详情，复用 process.note_md() 落盘到 VAULT/<board>/。
  - 已存在（按 noteId 命中 .md）跳过；成功写入后登记到 imported_ids.json（避免增量同步重复抓）。
  - 命中限流长退避。

用法:
  python resync_broken.py [broken_urls.txt]
默认 broken 文件: 03_资料员/xhs_broken_urls_20260730.txt
"""
import sys, os, json, time, re, random, datetime

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
SPIDER = os.path.join(SCRIPTS, "Spider_XHS")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, SPIDER)
os.chdir(SPIDER)
os.environ.setdefault("NODE_PATH", os.path.join(SPIDER, "node_modules"))

# 确保 node 可用（execjs 跑签名需要），并清掉沙箱机房代理（直连住宅 IP）
node_bin = "/Users/Zhuanz/.workbuddy/binaries/node/versions/22.22.2/bin"
if os.path.exists(node_bin) and node_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = node_bin + ":" + os.environ.get("PATH", "")
for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
    os.environ.pop(k, None)

import xhs_obsidian_sync as S   # 复用 check_session / fetch_note / is_ratelimit / imported 状态
import process

DEFAULT_BROKEN = ("/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/"
                 "Documents/DuoDuo_AI_Workspace/03_ACTIVE PROJECTS/ai个人公司/"
                 "公司档案/03_资料员/xhs_broken_urls_20260730.txt")


def parse_broken(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        board, status, url = parts[0].strip(), parts[1].strip(), parts[2].strip()
        m = re.search(r"/explore/([0-9a-f]{8,})", url)
        if not m:
            continue
        nid = m.group(1)
        mt = re.search(r"xsec_token=([^&]+)", url)
        xsec = mt.group(1) if mt else ""
        rows.append((board, nid, xsec, url))
    return rows


def note_exists(album_dir, nid):
    for fn in os.listdir(album_dir):
        if not fn.endswith(".md"):
            continue
        try:
            if nid in open(os.path.join(album_dir, fn), encoding="utf-8", errors="ignore").read():
                return True
        except Exception:
            pass
    return False


def main():
    broken = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BROKEN
    if not os.path.exists(broken):
        print("BROKEN_FILE_MISSING: %s" % broken)
        sys.exit(3)
    rows = parse_broken(broken)
    print("[resync] 解析到 %d 条待重抓" % len(rows), flush=True)

    cookies_str = S.load_cookie()
    proxies = S.load_proxies()
    engine, handle = S.load_engine()

    ok, why = S.check_session(cookies_str, proxies, engine)
    if not ok:
        print("LOGIN_EXPIRED: %s" % why)
        sys.exit(2)

    VAULT = process.VAULT
    imported = S.load_imported()
    success = failed = skipped = 0
    fails = []

    for board, nid, xsec, url in rows:
        album_dir = os.path.join(VAULT, board)
        os.makedirs(album_dir, exist_ok=True)
        if note_exists(album_dir, nid):
            skipped += 1
            continue
        info, msg = S.fetch_note(engine, handle, nid, xsec, cookies_str, proxies)
        if info is None:
            failed += 1
            fails.append((board, nid, msg[:120]))
            if S.is_ratelimit(msg):
                time.sleep(120)
            else:
                time.sleep(6)
            continue
        note = {
            "title": info.get("title") or "(无标题)",
            "author": info.get("nickname", ""),
            "url": info.get("note_url", ""),
            "time": info.get("upload_time") or datetime.date.today().isoformat(),
            "desc": info.get("desc") or "",
            "valid": True,
        }
        base = process.sanitize("%s - %s" % (note["title"], note["time"]))
        # 避免覆盖同名旧文件
        path = os.path.join(album_dir, base + ".md")
        if os.path.exists(path):
            path = os.path.join(album_dir, "%s_%s.md" % (base, nid[:6]))
        open(path, "w", encoding="utf-8").write(process.note_md(note, board))
        imported.setdefault(board, [])
        if nid not in imported[board]:
            imported[board].append(nid)
        success += 1
        if success % 5 == 0:
            print("[resync] 已写 %d 篇" % success, flush=True)
        try:
            process.rebuild_index(board)
        except Exception as e:
            print("[resync] 索引重建跳过(非致命): %s" % e, flush=True)
        time.sleep(random.uniform(3.0, 6.0))

    S.save_imported(imported)
    print("DONE success=%d failed=%d skipped=%d total=%d" % (success, failed, skipped, len(rows)), flush=True)

    if fails:
        still = broken + ".still_failed.txt"
        with open(still, "w", encoding="utf-8") as f:
            for b, n, m in fails:
                f.write("%s\t%s\t%s\n" % (b, n, m))
        print("STILL_FAILED: %d 条 -> %s" % (len(fails), still), flush=True)
    else:
        print("ALL_OK: 全部重抓成功", flush=True)


if __name__ == "__main__":
    main()
