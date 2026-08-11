#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描 vault，识别风控 junk 笔记，隔离到备份区，并从 imported_ids.json 移除其 noteId（便于下周增量重试）。"""
import os, re, json, shutil, datetime

VAULT = "/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/05_CONTENT/小红书收藏"
BASE = os.path.expanduser("~/Downloads/xhs_scraper")
QUAR = os.path.join(BASE, "_quarantine_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
IMPORTED = os.path.join(BASE, "imported_ids.json")

JUNK_BODY = [
    "too many requests", "try again later", "security verification",
    "安全验证", "当前笔记暂时无法", "滑动验证",
]

def extract_note_id(url):
    m = re.search(r"/(?:explore|board/[^/]+)/([0-9a-f]{16,32})", url or "")
    if m: return m.group(1)
    m = re.search(r"([0-9a-f]{24})", url or "")
    return m.group(1) if m else None

def is_junk(text):
    # 标题为「安全限制」
    tm = re.search(r'^title:\s*"?(.*?)"?\s*$', text, re.M)
    title = (tm.group(1).strip() if tm else "")
    if title in ("安全限制", "Security Verification", ""):
        # 空标题也可疑，但需正文佐证
        if title in ("安全限制", "Security Verification"):
            return True, title
    low = text.lower()
    # 取「原帖要点」之后的正文判断
    body = text
    idx = text.find("## 原帖要点")
    if idx >= 0:
        body = text[idx: idx+400]
    blow = body.lower()
    for kw in JUNK_BODY:
        if kw in blow:
            return True, title or "(空标题)"
    return False, title

def get_url(text):
    m = re.search(r'^url:\s*(.*?)\s*$', text, re.M)
    return m.group(1).strip() if m else ""

def main():
    imported = {}
    if os.path.exists(IMPORTED):
        imported = json.load(open(IMPORTED, encoding="utf-8"))

    report = {}
    removed_ids = 0
    os.makedirs(QUAR, exist_ok=True)

    for album in sorted(os.listdir(VAULT)):
        adir = os.path.join(VAULT, album)
        if not os.path.isdir(adir):
            continue
        junk_files = []
        for fn in os.listdir(adir):
            if not fn.endswith(".md"):
                continue
            if fn.startswith("_") or "索引" in fn or fn.lower().startswith("index"):
                continue
            fp = os.path.join(adir, fn)
            try:
                text = open(fp, encoding="utf-8").read()
            except Exception:
                continue
            junk, title = is_junk(text)
            if junk:
                nid = extract_note_id(get_url(text))
                junk_files.append((fp, fn, nid))

        if junk_files:
            qdir = os.path.join(QUAR, album)
            os.makedirs(qdir, exist_ok=True)
            ids_to_remove = set()
            for fp, fn, nid in junk_files:
                shutil.move(fp, os.path.join(qdir, fn))
                if nid:
                    ids_to_remove.add(nid)
            # 从 imported_ids 移除，便于重试
            if album in imported:
                before = len(imported[album])
                imported[album] = [x for x in imported[album] if x not in ids_to_remove]
                removed_ids += before - len(imported[album])
            report[album] = len(junk_files)

    # 写回 imported_ids
    json.dump(imported, open(IMPORTED, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("=== 清理结果 ===")
    tot = 0
    for k, v in report.items():
        print(f"{k:14s} 隔离 junk: {v}")
        tot += v
    print(f"-------------------------")
    print(f"junk 总计: {tot}   已从 imported_ids 移除 noteId: {removed_ids}")
    print(f"隔离目录: {QUAR}")
    print()
    print("=== 清理后各专辑剩余有效篇数 ===")
    for album in sorted(os.listdir(VAULT)):
        adir = os.path.join(VAULT, album)
        if not os.path.isdir(adir):
            continue
        cnt = len([f for f in os.listdir(adir) if f.endswith(".md")
                   and not f.startswith("_") and "索引" not in f])
        print(f"{album:14s} {cnt} 篇")

if __name__ == "__main__":
    main()
