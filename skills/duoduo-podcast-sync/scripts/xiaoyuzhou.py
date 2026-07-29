#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宇宙公开页检测 + 音频下载（被 apple_rss_sync.py / ximalaya_sync.py 共用）。

只读取公开 SSR 页面（__NEXT_DATA__ JSON），无需登录。
节目 id（pid）：6a5a306305d4bfbabc3ea16b
单集音频直链格式：https://media.xyzcdn.net/<pid>/<hash>.m4a
"""
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

PID = "6a5a306305d4bfbabc3ea16b"
PODCAST_URL = f"https://www.xiaoyuzhoufm.com/podcast/{PID}"
EPISODE_URL = lambda eid: f"https://www.xiaoyuzhoufm.com/episode/{eid}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

_AUDIO_RE = re.compile(r"https://media\.xyzcdn\.net/[^\"'\\ ]+?\.m4a")
_DATE_KEYS = ("pubDate", "updatedAt", "createdAt", "publishedAt", "releaseDate", "displayDate")


def _fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def _extract_next_data(html):
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                  html, re.S)
    if not m:
        raise RuntimeError("__NEXT_DATA__ not found on page")
    return json.loads(m.group(1))


def _find_episodes_in_obj(obj, acc):
    """递归收集含 audio 直链 + title 的对象，作为单集。"""
    if isinstance(obj, dict):
        title = obj.get("title")
        audio = None
        # 找音频直链：优先 'url' 字段，否则扫整个对象的字符串值
        if isinstance(obj.get("url"), str) and _AUDIO_RE.search(obj["url"]):
            audio = _AUDIO_RE.search(obj["url"]).group(0)
        else:
            blob = json.dumps(obj, ensure_ascii=False)
            mm = _AUDIO_RE.search(blob)
            if mm:
                audio = mm.group(0)
        if audio and title and isinstance(title, str) and len(title) > 0:
            eid = obj.get("eid") or obj.get("id") or obj.get("episodeId")
            if eid:
                acc.setdefault(eid, {
                    "id": eid,
                    "title": title,
                    "audio_url": audio,
                    "shownotes": obj.get("shownotes") or obj.get("description") or "",
                    "published_iso": _first_date(obj),
                    "duration": obj.get("duration") or "",
                })
        for v in obj.values():
            _find_episodes_in_obj(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _find_episodes_in_obj(v, acc)


def _first_date(obj):
    for k in _DATE_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def get_episodes():
    """返回按发布时间倒序的单集列表（最新在前）。"""
    html = _fetch(PODCAST_URL)
    data = _extract_next_data(html)
    acc = {}
    _find_episodes_in_obj(data, acc)
    eps = list(acc.values())
    if not eps:
        raise RuntimeError("未从小宇宙页面解析到任何单集")
    # 按发布时间排序（无时间信息放最后），保持最新在前
    def _ts(e):
        iso = e.get("published_iso", "")
        if iso:
            try:
                return -datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
            except Exception:
                return 0
        return 0
    eps.sort(key=_ts)
    return eps


def guid_of(eid):
    return f"https://www.xiaoyuzhoufm.com/episode/{eid}"


def download_audio(eid, audio_url, cache_dir):
    """下载音频到 cache_dir/<eid>.m4a，返回本地路径。已存在则跳过。"""
    os.makedirs(cache_dir, exist_ok=True)
    out = os.path.join(cache_dir, f"{eid}.m4a")
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        return out
    req = urllib.request.Request(audio_url, headers={"User-Agent": UA,
                                                     "Referer": PODCAST_URL})
    with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as f:
        while True:
            buf = r.read(1024 * 1024)
            if not buf:
                break
            f.write(buf)
    if os.path.getsize(out) < 10000:
        raise RuntimeError(f"音频下载过小，疑似失败: {out}")
    return out


if __name__ == "__main__":
    eps = get_episodes()
    print(json.dumps(eps, ensure_ascii=False, indent=2))
