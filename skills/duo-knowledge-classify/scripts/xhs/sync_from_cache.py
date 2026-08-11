#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""后台抓取: 用前台缓存的 _enum_cache.json, 只抓 枚举集-已落盘 的缺失篇(签名API, 不驱动Chrome)。
健壮版: 死笔记(no_items)重试1次后永久跳过; 限流退避重试; 其余失败有限重试, 不阻塞整批。"""
import sys, os, json, time, random, datetime
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import xhs_obsidian_sync as S

SKIP_PATH = os.path.join(SP, "_skipped_notes.json")

def fetch_one(nid, xsec):
    """返回 (info, None) 成功; 或 (None, 'dead'|'skip') 失败且已处理。"""
    # 1) 死笔记(success=True 但无 items): 重试1次排除瞬时, 仍失败则永久跳过
    info, msg = S.fetch_note(S.engine, S.handle, nid, xsec, S.cookie, S.proxies)
    if info is not None:
        return info, None
    if msg and msg.startswith("no_items"):
        time.sleep(15)
        info, msg = S.fetch_note(S.engine, S.handle, nid, xsec, S.cookie, S.proxies)
        if info is not None:
            return info, None
        return None, "dead"
    # 2) 限流(success=False + 限流关键词): 退避120s, 最多15次
    if S.is_ratelimit(msg):
        for _ in range(15):
            print("[ratelimit] %s 退避120s" % nid, flush=True)
            time.sleep(120)
            info, msg = S.fetch_note(S.engine, S.handle, nid, xsec, S.cookie, S.proxies)
            if info is not None:
                return info, None
            if msg and msg.startswith("no_items"):
                return None, "dead"
            if not S.is_ratelimit(msg):
                break
    # 3) 其它失败: 退避6s, 最多3次
    for _ in range(3):
        time.sleep(6)
        info, msg = S.fetch_note(S.engine, S.handle, nid, xsec, S.cookie, S.proxies)
        if info is not None:
            return info, None
        if msg and msg.startswith("no_items"):
            return None, "dead"
        if S.is_ratelimit(msg):
            break
    return None, "skip"

def main():
    cache = json.load(open(os.path.join(SP, "_enum_cache.json"), encoding="utf-8"))
    skipped = json.load(open(SKIP_PATH, encoding="utf-8")) if os.path.exists(SKIP_PATH) else {}
    S.cookie = S.load_cookie()
    S.proxies = S.load_proxies()
    S.engine, S.handle = S.load_engine()
    imported = S.load_imported()
    total = 0
    for album, links in cache.items():
        ids = set(imported.get(album, []))
        album_dir = os.path.join(S.process.VAULT, album)
        os.makedirs(album_dir, exist_ok=True)
        written = 0
        dead = 0
        for nid, xsec in links:
            if nid in ids:
                continue
            info, status = fetch_one(nid, xsec)
            if info is None:
                if status == "dead":
                    dead += 1
                    skipped.setdefault(album, []).append({"nid": nid, "xsec": xsec, "reason": "no_items"})
                    print("[dead] %s 笔记失效, 永久跳过" % nid, flush=True)
                else:
                    print("[skip] %s 多次重试仍失败" % nid, flush=True)
                json.dump(skipped, open(SKIP_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                continue
            note = {
                "title": info.get("title") or "(无标题)",
                "author": info.get("nickname", ""),
                "url": info.get("note_url", ""),
                "time": info.get("upload_time") or datetime.date.today().isoformat(),
                "desc": info.get("desc") or "",
                "valid": True,
            }
            base = S.process.sanitize("%s - %s" % (note["title"], note["time"]))
            path = os.path.join(album_dir, base + ".md")
            open(path, "w", encoding="utf-8").write(S.process.note_md(note, album))
            ids.add(nid)
            written += 1
            if written % 5 == 0:
                print("[%s] 已写 %d 篇" % (album, written), flush=True)
            time.sleep(random.uniform(3.0, 6.0))
        try:
            S.process.rebuild_index(album)
        except Exception as e:
            print("[warn] 索引重建失败: %s" % e, flush=True)
        imported[album] = sorted(ids)
        S.save_imported(imported)
        print("[%s] 新增 %d 篇 (累计 %d), 死笔记跳过 %d" % (album, written, len(ids), dead), flush=True)
        total += written
    print("[done] 全部新增 %d 篇" % total, flush=True)

if __name__ == "__main__":
    main()
