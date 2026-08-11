#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xhs_obsidian_sync.py — 小红书收藏专辑 → Obsidian 自动同步 (Spider_XHS 引擎版)

设计(混合架构, 已针对被限流教训优化):
  1. 枚举: 用本机真实 Chrome(osascript 驱动)打开 board 页, 滚动加载并提取每条笔记的
     noteId + xsec_token。这一步此前稳定可用(不被限流)。
  2. 详情: 用 Spider_XHS 的签名 API(POST /api/sns/web/v1/feed, 含 x-s/x-t 逆向签名)
     抓取单篇详情, 取代之前被限流的 DOM 详情抓取。
  3. 落盘: 复用 process.py 的 note_md(), 保持与现有 561 篇完全一致的 frontmatter 与三段结构。
  4. 增量: imported_ids.json 记录已抓 noteId, 只补新增; 命中限流长退避, 不把整批标脏。

前置(见 SKILL.md):
  - pip install -r Spider_XHS/requirements.txt
  - cd Spider_XHS && npm install   (提供 crypto-js/jsdom 供 execjs 签名)
  - 运行 extract_xhs_cookies.py 导出 .env.cookies(或从 Spider_XHS/.env 读 COOKIES)
  - 建议住宅/移动代理(当前 Clash 节点为机房 IP, 风险高), 可用 XHS_PROXY 注入
"""
import sys, os, json, time, re, subprocess, random, datetime

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
SPIDER = os.path.join(SCRIPTS, "Spider_XHS")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, SPIDER)

# 自修复 Spider_XHS 运行环境：其静态 JS 用相对 require('./static/...')，
# 且 execjs 跑 Node 需能找到 crypto-js/jsdom。无论从哪个 CWD 启动都先切到 SPIDER 并设 NODE_PATH。
os.chdir(SPIDER)
os.environ.setdefault("NODE_PATH", os.path.join(SPIDER, "node_modules"))

import process  # 复用 frontmatter / 专辑映射 / sanitize

def log(*a):
    print("[sync]", *a, flush=True)

# ---------- 配置 ----------
def load_cfg():
    cfg = json.load(open(os.path.join(SCRIPTS, "boards.json"), encoding="utf-8"))
    return cfg

def load_cookie():
    p = os.path.join(SCRIPTS, ".env.cookies")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line.startswith("XHS_COOKIE="):
                return line.split("=", 1)[1].strip().strip("'\"")
    pe = os.path.join(SPIDER, ".env")
    if os.path.exists(pe):
        for line in open(pe, encoding="utf-8"):
            if line.strip().startswith("COOKIES="):
                return line.split("=", 1)[1].strip().strip("'\"")
    raise SystemExit("未找到 cookie：请先运行 extract_xhs_cookies.py 导出 .env.cookies")

def load_proxies():
    """返回 requests 用的 proxies 参数。
    - 设了 XHS_PROXY → 用指定代理（例如住宅/移动代理）。
    - 没设 → 默认【直连本机住宅 IP】：清掉沙箱注入的 HTTP(S)_PROXY 环境变量，
      确保小红书 API 调用从「和 Chrome 登录相同的住宅 IP」出去。
      根因：此前默认走沙箱机房代理(89.31.126.148)，IP 与登录地不符，
      小红书风控直接干掉 web_session，导致每次都要回 Chrome 重新扫码。
      返回 {} 表示不使用代理 = 直连（住宅 IP）。
    """
    p = os.environ.get("XHS_PROXY")
    if p:
        return {"http": p, "https": p}
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
              "ALL_PROXY", "all_proxy"):
        os.environ.pop(k, None)
    return {}

# ---------- 跑前 session 自检 ----------
def check_session(cookies_str, proxies, engine=None):
    """用 /api/sns/web/v1/user/selfinfo 验证 web_session 是否还活着。
    返回 (ok: bool, why: str)。session 失效时给清晰原因，供自动化/用户判断是否需扫码。"""
    if engine is None:
        engine, _ = load_engine()
    try:
        success, msg, res = engine.get_user_self_info(cookies_str, proxies)
    except Exception as e:
        return False, "自检请求异常: %r" % e
    if success and isinstance(res, dict) and res.get("data"):
        d = res.get("data") or {}
        name = d.get("nickname") or d.get("name") or d.get("user_id") or "?"
        return True, "登录有效（当前账号: %s）" % name
    return False, "登录已失效（%s）" % (msg or "未知原因，可能需在 Chrome 重新扫码")


# ---------- 真实 Chrome 按 board 枚举 noteId ----------
def osa(script, tout=30):
    return subprocess.run(["osascript", "-e", script], capture_output=True,
                          text=True, timeout=tout)

def chrome_open(url):
    osa('tell application "Google Chrome" to activate', 10)
    osa('tell application "Google Chrome" to if (count of windows) = 0 then make new window', 10)
    osa('tell application "Google Chrome" to set URL of active tab of front window to "%s"'
        % url.replace('"', '\\"'), 15)
    time.sleep(5)

def run_js(js, tout=20):
    js = js.replace('\\', '\\\\').replace('"', '\\"')
    r = osa('tell application "Google Chrome" to tell active tab of front window to execute javascript "%s"' % js, tout)
    return r.stdout.strip()

JS_LINKS = ("JSON.stringify(Array.from(document.querySelectorAll('section.note-item a.cover'))"
            ".map(function(a){return a.href;}))")

def collect_board_links(board_id, max_scroll=220):
    """枚举 board 页全部 noteId。
    ⚠️ 2026-07-27 修复的关键 bug：board 页是【虚拟滚动】——DOM 里任何时刻只保留约 30 个
    note-item 卡片，滚过去的会被卸载。旧实现每步 `scrollTo(底部)` 大跳，第一次采样前就把
    顶部（=最新收藏）卡片卸载掉了，导致新收藏永远抓不到（剪辑专辑官方 83 篇只枚举出 68）。
    正确做法：先回到顶部，【先采样再小步滚动】(0.6 屏/步)，让每张卡片都在 DOM 里出现过。"""
    url = "https://www.xiaohongshu.com/board/%s/" % board_id
    chrome_open(url)
    run_js("window.scrollTo(0, 0);")
    time.sleep(2)
    seen = set()
    out = []
    stall = 0
    for i in range(max_scroll):
        # 先采样当前视口的卡片, 再滚动
        try:
            raw = run_js(JS_LINKS, 15)
        except Exception:
            raw = "[]"
        try:
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
            out.append((nid, xsec))
            new += 1
        stall = stall + 1 if new == 0 else 0
        at_bottom = run_js("(window.innerHeight+window.scrollY)>=document.body.scrollHeight-10")
        if stall > 12 and at_bottom == "true":
            break  # 已到底且连续多轮无新增(阈值放宽, 等懒加载)
        run_js("window.scrollBy(0, Math.floor(window.innerHeight*0.5));")
        time.sleep(1.3)
    log("枚举完成: 共 %d 条链接" % len(out))
    return out

# ---------- Spider_XHS 签名详情抓取 ----------
def load_engine():
    from apis.xhs_pc_apis import XHS_Apis
    from xhs_utils.data_util import handle_note_info
    return XHS_Apis(), handle_note_info

def fetch_note(engine, handle, nid, xsec, cookies_str, proxies):
    note_url = ("https://www.xiaohongshu.com/explore/%s?xsec_token=%s&xsec_source=pc_user"
                % (nid, xsec))
    success, msg, res = engine.get_note_info(note_url, cookies_str, proxies)
    if not success:
        return None, msg
    # success=True 但无 items：笔记已删/私密/xsec 失效（非限流，限流会 success=False）
    res = res or {}
    data = res.get("data") or {}
    items = data.get("items") or []
    if not items:
        return None, "no_items:" + json.dumps(res, ensure_ascii=False)[:200]
    item = items[0]
    item["url"] = note_url
    return handle(item), msg

def is_ratelimit(msg):
    m = (msg or "").lower()
    return any(k in m for k in ["limit", "频繁", "too many", "rate", "请求过于", "访问频繁",
                                "账号异常", "300011", "keyerror", "success'", "稍后重试"])

# ---------- 增量状态 ----------
def load_imported():
    p = os.path.join(SCRIPTS, "imported_ids.json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return {}

def save_imported(data):
    json.dump(data, open(os.path.join(SCRIPTS, "imported_ids.json"), "w", encoding="utf-8"),
               ensure_ascii=False, indent=1)

# ---------- 主流程 ----------
def sync_one(album, board_id, imported_set, engine, handle, cookies_str, proxies):
    links = collect_board_links(board_id)
    album_dir = os.path.join(process.VAULT, album)
    os.makedirs(album_dir, exist_ok=True)
    written = 0
    for nid, xsec in links:
        if nid in imported_set:
            continue
        info, msg = fetch_note(engine, handle, nid, xsec, cookies_str, proxies)
        if info is None:
            log("抓取失败 %s: %s" % (nid, msg))
            if is_ratelimit(msg):
                log("命中限流, 退避 120s 后继续")
                time.sleep(120)
            else:
                time.sleep(6)
            # 不写检查点, 下次重试用
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
        path = os.path.join(album_dir, base + ".md")
        open(path, "w", encoding="utf-8").write(process.note_md(note, album))
        imported_set.add(nid)
        written += 1
        if written % 5 == 0:
            log("%s 已写 %d 篇" % (album, written))
        time.sleep(random.uniform(3.0, 6.0))  # 降速, 防行为层风控
    # 重建索引(增量追加后保持清单最新)
    try:
        process.rebuild_index(album)
    except Exception as e:
        log("索引重建失败(非致命):", e)
    return written

def main():
    cfg = load_cfg()
    raw_boards = cfg.get("boards", cfg)
    # 兼容 list[{name,id}] 与 dict{name:id} 两种结构
    if isinstance(raw_boards, list):
        board_items = [(b["name"], b["id"]) for b in raw_boards]
    elif isinstance(raw_boards, dict):
        board_items = [(k, v) for k, v in raw_boards.items() if k != "vault"]
    else:
        board_items = []
    cookies_str = load_cookie()
    proxies = load_proxies()
    engine, handle = load_engine()

    # 跑前自检：session 失效就别在死 session 上浪费调用/加重风控，明确告诉用户去扫码
    ok, why = check_session(cookies_str, proxies, engine)
    if not ok:
        log("⚠️ 小红书登录已过期：%s" % why)
        log("   需要你在 Chrome 打开 xiaohongshu.com 重新扫码登录一次；")
        log("   登录后告诉我，我重提一次 cookie 即可——之后会稳定（已改为住宅 IP 直连，不再每次被杀）。")
        raise SystemExit(1)

    imported = load_imported()
    total = 0
    for album, board_id in board_items:
        ids = set(imported.get(album, []))
        w = sync_one(album, board_id, ids, engine, handle, cookies_str, proxies)
        imported[album] = sorted(ids)
        save_imported(imported)
        log("专辑 %s 本次新增 %d 篇 (累计 %d)" % (album, w, len(ids)))
        total += w
    log("全部完成, 本次共新增 %d 篇" % total)

if __name__ == "__main__":
    main()
