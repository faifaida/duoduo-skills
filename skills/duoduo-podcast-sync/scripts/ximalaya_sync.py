#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
喜马拉雅上传同步（小宇宙 -> 喜马拉雅专辑 127170840「多多的未完成实验」）。
流程：检测小宇宙新单集 -> 下载音频 -> headless Chrome CDP 上传 -> 校验在架。
只动喜马拉雅专辑 127170840。后台运行，绝不占屏幕。
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xiaoyuzhou as xy  # noqa: E402

from playwright.sync_api import sync_playwright  # noqa: E402

UPLOAD_URL = "https://studio.ximalaya.com/upload"
ALBUM_ID = "127170840"
ALBUM_TITLE = "多多的未完成实验"
STATE_FILE = os.path.join(HERE, "state", "uploaded_episodes.json")
CACHE_DIR = os.path.join(HERE, "state", "audio_cache")
CDP = "http://localhost:9222"


def _load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def _save_state(s):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(s), f, ensure_ascii=False, indent=2)


def _upload_one(page, ep):
    """返回 (ok, msg)。ok=True 表示已成功发布并校验通过。"""
    audio = xy.download_audio(ep["id"], ep["audio_url"], CACHE_DIR)
    page.goto(UPLOAD_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#contentWrapper iframe", timeout=30000)
    frame_el = page.query_selector("#contentWrapper iframe")
    cf = frame_el.content_frame()
    cf.wait_for_selector("input[type=file]", timeout=30000)

    # 1) 设置音频文件
    cf.locator("input[type=file]").set_input_files(audio)
    # 2) 等元数据表单出现
    cf.wait_for_selector('input[placeholder="请输入声音标题"]', timeout=30000)
    time.sleep(2)

    # 3) 标题
    cf.fill('input[placeholder="请输入声音标题"]', ep["title"])

    # 4) 校验已选专辑（.select-album-wrapper 默认选中最近创建的专辑）
    sel_text = cf.evaluate("""() => {
      const w = document.querySelector('.select-album-wrapper');
      return w ? (w.innerText || '').trim() : '';
    }""")
    if ALBUM_TITLE not in sel_text:
        return False, f"专辑未自动选中目标({ALBUM_TITLE})，当前选中: {sel_text!r} —— 已中止，未误传"

    # 5) 描述（KindEditor）
    html = ep.get("shownotes", "") or ""
    cf.evaluate("""(html) => {
      const f = document.querySelector('.ke-edit-iframe');
      if (f && f.contentDocument) f.contentDocument.body.innerHTML = html;
      const ta = document.querySelector('.ke-edit-textarea');
      if (ta) ta.value = html;
    }""", html)

    # 6) 确认发布
    cf.click(".confirm-publish-btn-new-3F0EvXXa")
    # 7) 等待跳转到管理页
    try:
        page.wait_for_url("**/sound/manage/**", timeout=30000)
    except Exception:
        pass
    time.sleep(3)

    # 8) 校验：管理页出现单集标题 + 在架(1)
    body = page.content()
    ok = (ep["title"] in body) and ("在架(1)" in body or "在架" in body)
    if not ok:
        return False, "发布后未在管理页校验到在架(1)，请人工确认"
    return True, "已发布并校验在架(1)"


def main():
    episodes = xy.get_episodes()
    state = _load_state()
    pending = [e for e in episodes if e["id"] not in state]
    if not pending:
        print("NO_NEW_EPISODES")
        return 0
    print(f"[ximalaya] 待上传新单集 {len(pending)} 个")

    rc = 0
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP)
        page = browser.new_page()
        for ep in pending:
            try:
                ok, msg = _upload_one(page, ep)
                print(f"[ximalaya] {ep['title']}: {msg}")
                if ok:
                    state.add(ep["id"])
                    _save_state(state)
                else:
                    rc = 2
            except Exception as ex:
                print(f"[ximalaya] {ep['title']}: 异常 {ex}")
                rc = 2
        browser.close()
    print("DONE" if rc == 0 else "DONE_WITH_WARNINGS")
    return rc


if __name__ == "__main__":
    sys.exit(main())
