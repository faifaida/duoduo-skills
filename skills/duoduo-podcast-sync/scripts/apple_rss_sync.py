#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple Podcasts RSS 同步（小宇宙 -> GitHub Pages rss.xml）。
流程：检测小宇宙新单集 -> 用 CM6 EditorView.dispatch 整体替换 rss.xml -> 提交 -> 校验线上 RAW。
只动 faifaida/duoduo-podcast 的 rss.xml。后台运行，绝不占屏幕。
"""
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xiaoyuzhou as xy  # noqa: E402

from playwright.sync_api import sync_playwright  # noqa: E402

REPO = "faifaida/duoduo-podcast"
EDIT_URL = f"https://github.com/{REPO}/edit/main/rss.xml"
RAW_URL = "https://faifaida.github.io/duoduo-podcast/rss.xml"
COVER = "https://faifaida.github.io/duoduo-podcast/cover.jpg"
SHOW_TITLE = "多多的未完成实验"
SHOW_LINK = xy.PODCAST_URL
SHOW_DESC = "多多的未完成实验 —— 一档关于用 AI 重新设计人生的播客。"

CDP = "http://localhost:9222"


def _rfc822(iso):
    if not iso:
        return time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    try:
        dt = time.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S")
        return time.strftime("%a, %d %b %Y %H:%M:%S +0000", dt)
    except Exception:
        return time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())


def _esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_rss(episodes):
    items = []
    for e in episodes:
        items.append(f"""  <item>
    <title>{_esc(e['title'])}</title>
    <description><![CDATA[{e.get('shownotes','')}]]></description>
    <enclosure url="{e['audio_url']}" type="audio/x-m4a"/>
    <guid isPermaLink="false">{xy.guid_of(e['id'])}</guid>
    <pubDate>{_rfc822(e.get('published_iso',''))}</pubDate>
  </item>""")
    items_xml = "\n".join(items)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SHOW_TITLE}</title>
    <link>{SHOW_LINK}</link>
    <atom:link href="{RAW_URL}" rel="self" type="application/rss+xml"/>
    <description>{_esc(SHOW_DESC)}</description>
    <language>zh-CN</language>
    <itunes:author>多多</itunes:author>
    <itunes:explicit>false</itunes:explicit>
    <image href="{COVER}"/>
    <itunes:image href="{COVER}"/>
{items_xml}
  </channel>
</rss>
"""


def _current_guids(page):
    return page.evaluate("""() => {
      const cm = document.querySelector('.cm-content');
      if (!cm) return '';
      let view = null;
      for (const el of document.querySelectorAll('.cm-content')) {
        for (const k in el) {
          const v = el[k];
          if (v && typeof v.dispatch === 'function' && v.state && v.state.doc) {
            if (!view || v.state.doc.length > view.state.doc.length) view = v;
          }
        }
      }
      return view ? view.state.doc.toString() : '';
    }""")


def _replace_content(page, content):
    page.evaluate("""(CONTENT) => {
      let view = null;
      for (const el of document.querySelectorAll('.cm-content')) {
        for (const k in el) {
          const v = el[k];
          if (v && typeof v.dispatch === 'function' && v.state && v.state.doc) {
            if (!view || v.state.doc.length > view.state.doc.length) view = v;
          }
        }
      }
      if (!view) throw new Error('CM6 EditorView not found');
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: CONTENT } });
    }""", content)


def _click_commit(page):
    # 点工具栏 "Commit changes"
    page.evaluate("""() => {
      const btns = [...document.querySelectorAll('button')].filter(b => /commit changes/i.test(b.textContent||''));
      if (!btns.length) throw new Error('no Commit button');
      btns[0].click();
    }""")
    page.wait_for_timeout(1500)
    # 弹窗里再点一次提交
    page.evaluate("""() => {
      const modal = document.querySelector('.Overlay, [role=dialog], .annotated-container') || document;
      const btns = [...modal.querySelectorAll('button')].filter(b => /commit changes|提交/i.test(b.textContent||''));
      if (!btns.length) throw new Error('no Commit button in modal');
      btns[btns.length-1].click();
    }""")


def _verify_raw(expected_count):
    try:
        req = urllib.request.Request(RAW_URL, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=20) as r:
            xml = r.read().decode("utf-8", "replace")
    except Exception as ex:
        return f"VERIFY_FETCH_FAIL: {ex}"
    import xml.dom.minidom as M
    try:
        M.parseString(xml)
    except Exception as ex:
        return f"VERIFY_NOT_WELLFORMED: {ex}"
    cnt = xml.count("<item>")
    if cnt != expected_count:
        return f"VERIFY_ITEM_MISMATCH: raw={cnt} expected={expected_count}"
    return f"VERIFY_OK items={cnt}"


def main():
    episodes = xy.get_episodes()
    print(f"[apple] 小宇宙单集数={len(episodes)}")
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP)
        page = browser.new_page()
        page.goto(EDIT_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector(".cm-content", timeout=30000)
        cur = _current_guids(page)
        existing = set(re.findall(r"<guid>[^<]+</guid>", cur))
        new = [e for e in episodes if xy.guid_of(e["id"]) not in existing]
        if not new:
            print("NO_NEW_EPISODES")
            browser.close()
            return 0
        print(f"[apple] 检测到新单集 {len(new)} 个，准备提交")
        content = build_rss(episodes)
        _replace_content(page, content)
        page.wait_for_timeout(800)
        _click_commit(page)
        time.sleep(6)  # 等 GitHub Pages 重建
        v = _verify_raw(len(episodes))
        print(v)
        browser.close()
        if not v.startswith("VERIFY_OK"):
            print("DONE_WITH_VERIFY_WARNING")
            return 2
        print("DONE: rss.xml 已更新")
        return 0


if __name__ == "__main__":
    sys.exit(main())
