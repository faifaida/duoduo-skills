#!/usr/bin/env python3
"""
邮箱 IMAP 批量清理（Gmail + QQ / 中文邮箱）
============================================
配套 duo-knowledge-classify/references/05-gmail-imap-cleanup.md

功能：
  - 自助读 vault `00_凭证_passwords.md` 提取 Gmail / QQ 凭证（绝不跟用户要码）
  - 探测回收站文件夹真名（Gmail [Gmail]/Trash / QQ Deleted Messages）
  - 反向白名单分类：核心域 + 无退订头事务/个人邮件保留；非核心域且带
    List-Unsubscribe 头的推广/订阅类归档进回收站（30 天可恢复，绝不 EXPUNGE）
  - RFC 8058 One-Click 退订并发 POST
  - 输出 HTML 周报 + JSON 实测前后计数

用法：
  python mail_imap_cleanup.py --diagnose            # 只读诊断（默认）
  python mail_imap_cleanup.py --execute             # 归档 + 退订
  python mail_imap_cleanup.py --accounts gmail,qq --limit 2000   # 取样测试
  python mail_imap_cleanup.py --vault /path/to/00_凭证_passwords.md

依赖：imapclient（隔离 venv：~/.workbuddy/binaries/python/envs/default/bin/pip install imapclient）
"""
import argparse, re, json, time, os, sys, urllib.request, datetime, concurrent.futures

# ---------- 账号配置 ----------
ACCOUNTS = {
    "gmail": {
        "host": "imap.gmail.com", "user": "fayezang28@gmail.com",
        "email_hint": "@gmail.com", "vault_block": "gmail/google drive",
        "pw_key": "应用密码", "use_mutf7": True,
    },
    "qq": {
        "host": "imap.qq.com", "user": "939526417@qq.com",
        "email_hint": "@qq.com", "vault_block": "qq和qq邮箱",
        "pw_key": "imap", "use_mutf7": False,
    },
}

# 核心基础设施域（两箱同用，保留）
# 注意：社媒通知（facebookmail/instagram/tiktok/twitter 等）不放这里——
# 它们的退订类通知(带 List-Unsubscribe 头)应归档降噪；安全/登录/改绑提醒无退订头会自动保留。
KEEP_ROOT = {
    "apple.com","icloud.com","qq.com","tencent.com","foxmail.com","gmail.com",
    "outlook.com","microsoft.com","live.com","hotmail.com","u.nus.edu","paypal.com",
    "alipay.com","wechat.com","fedex.com","ups.com",
    "dhl.com","163.com","netease.com","baidu.com","kingsoft.com","naver.jp","nokia.com",
    "yinxiang.com","shanbay.com","jd.com","qunar.com","taobao.com","service.netease.com",
    "comms.nokia.com","mail.qq.com","exmail.qq.com","id.apple.com","itunes.com",
    "orders.apple.com","icbc.com.cn","ccb.com","abchina.com","bankcomm.com","cmbchina.com",
    "hsbc.com","bankofamerica.com","chase.com","citibank.com",
}
# 有价值内容订阅（带退订头也保留，避免周自动化误清）
KEEP_CONTENT = {
    "medium.com","substack.com","consensus.app","use.ai","heygen.com","timdenning.com",
    "justinwelsh.com","gagaoolala.com","cinewav.com","spotify.com",
}
UNSUB_CAP = 3000  # 最多 POST 退订链接数
CHUNK = 200
HDR_KEY = b"BODY[HEADER.FIELDS (FROM LIST-UNSUBSCRIBE LIST-UNSUBSCRIBE-POST)]"


def log(*a, **k):
    print(*a, flush=True, **k)


# ---------- vault 凭证自助解析 ----------
def find_vault(explicit=None):
    if explicit:
        return explicit
    cands = [
        os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/03_ACTIVE PROJECTS/ai个人公司/公司档案/00_共享公司资料/00_凭证_passwords.md"),
        os.path.expanduser("~/Documents/DuoDuo_AI_Workspace/03_ACTIVE PROJECTS/ai个人公司/公司档案/00_共享公司资料/00_凭证_passwords.md"),
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    return None


def load_creds(vault_path, acct_key):
    """从 vault 的指定 ### 段 提取账号 + 密码。"""
    cfg = ACCOUNTS[acct_key]
    if not vault_path or not os.path.exists(vault_path):
        raise SystemExit(f"[ERR] vault 未找到：{vault_path}")
    text = open(vault_path, encoding="utf-8").read()
    # 按 ### 段切块
    blocks = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^###\s*(.+?)\s*$", line)
        if m:
            cur = m.group(1).strip().lower()
            blocks[cur] = []
        elif cur is not None:
            blocks[cur].append(line)
    # 匹配段（含关键字即可）
    target = None
    for name, lines in blocks.items():
        if cfg["vault_block"].lower() in name:
            target = lines
            break
    if target is None:
        raise SystemExit(f"[ERR] vault 找不到段：{cfg['vault_block']}")
    email = None
    pw = None
    for line in target:
        low = line.lower()
        if cfg["email_hint"] in low and "@" in line:
            m = re.search(r"[\w.+-]+@[\w.-]+", line)
            if m:
                email = m.group(0)
        if cfg["pw_key"] in low and pw is None:
            # 取冒号后内容；去掉所有空格（Gmail 应用密码形如 qvue twxe ...）
            after = re.split(r"[:：]", line, maxsplit=1)[-1].strip()
            after = after.replace(" ", "")
            if after:
                pw = after
    if not email:
        email = cfg["user"]
    if not pw:
        raise SystemExit(f"[ERR] vault 段 {cfg['vault_block']} 找不到 {cfg['pw_key']}")
    return email, pw


# ---------- 分类 ----------
def classify(raw):
    frm = re.search(r"(?im)^From:\s*(.*)", raw)
    addr = ""
    if frm:
        m = re.search(r"[\w.+-]+@[\w.-]+", frm.group(1))
        if m:
            addr = m.group(0).lower()
    dom = addr.split("@")[-1] if "@" in addr else "?"
    parts = dom.split(".")
    pdom = ".".join(parts[-2:]) if len(parts) >= 2 else dom
    has_unsub = bool(re.search(r"(?im)^List-Unsubscribe:\s*(?!\s*$)", raw))
    return pdom, has_unsub


def decide(pdom, has_unsub):
    if pdom in KEEP_ROOT or pdom in KEEP_CONTENT:
        return "keep"
    if has_unsub:
        return "archive"
    return "keep"  # 无退订头的事务/个人/未知系统邮件保留


# ---------- 退订 ----------
def post_unsub(url):
    try:
        req = urllib.request.Request(
            url, data=b"List-Unsubscribe=One-Click",
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return url, r.status
    except Exception as e:
        return url, f"ERR:{type(e).__name__}"


def fetch_with_retry(client, batch):
    for attempt in range(4):
        try:
            return client.fetch(batch, [HDR_KEY])
        except Exception as e:
            log(f"  fetch ERR {e}; sleep 20; retry {attempt}")
            time.sleep(20)
    return None


def move_with_retry(client, uids, folder):
    for attempt in range(4):
        try:
            client.move(uids, folder)
            return True
        except Exception as e:
            log(f"  move ERR {e}; sleep 20; retry {attempt}")
            time.sleep(20)
    return False


def detect_trash(client):
    folders = client.list_folders()
    for flags, _delim, name in folders:
        if b"\\Trash" in flags:
            return name
    for flags, _delim, name in folders:
        if "trash" in name.lower() or "deleted" in name.lower():
            return name
    raise SystemExit("[ERR] 找不到回收站文件夹")


# ---------- 单账号处理 ----------
def process(acct_key, mode, limit, vault_path):
    from imapclient import IMAPClient
    cfg = ACCOUNTS[acct_key]
    email, pw = load_creds(vault_path, acct_key)
    log(f"\n=== [{acct_key}] {email} → {cfg['host']} ===")
    client = IMAPClient(cfg["host"], ssl=True, timeout=30)
    client.login(email, pw)
    client.select_folder("INBOX")
    all_uids = client.search(["ALL"])
    total = len(all_uids)
    if limit:
        total = min(total, limit)
        all_uids = all_uids[:total]
    log(f"INBOX total (limit={limit or 'all'}): {total}")

    trash = detect_trash(client)
    log(f"Trash folder: {trash}")

    archived = kept = 0
    failed = []
    unsub_urls = []
    top_domains = {}
    done = 0

    for s in range(0, total, CHUNK):
        batch = all_uids[s:s + CHUNK]
        data = fetch_with_retry(client, batch)
        if data is None:
            failed.extend(batch)
            done += len(batch)
            continue
        archive_uids = []
        for uid, item in data.items():
            raw = item[HDR_KEY].decode("utf-8", "ignore")
            pdom, has_unsub = classify(raw)
            top_domains[pdom] = top_domains.get(pdom, 0) + 1
            d = decide(pdom, has_unsub)
            if d == "keep":
                kept += 1
            else:
                archive_uids.append(uid)
                lu = re.search(r"(?im)^List-Unsubscribe:\s*(.*)", raw)
                lp = re.search(r"(?im)^List-Unsubscribe-Post:", raw)
                if lu and lp and len(unsub_urls) < UNSUB_CAP:
                    m = re.search(r"<(https?://[^>]+)>", lu.group(1))
                    if m:
                        unsub_urls.append(m.group(1))
        if mode == "execute" and archive_uids:
            if move_with_retry(client, archive_uids, trash):
                archived += len(archive_uids)
            else:
                failed.extend(archive_uids)
        elif mode == "diagnose":
            archived += len(archive_uids)  # 诊断模式下仅计数，不移动
        done += len(batch)
        if done % 2000 < CHUNK:
            log(f"  progress {done}/{total}  archived(拟)={archived} kept={kept}")

    unsub_ok = unsub_bad = 0
    if mode == "execute" and unsub_urls:
        log(f"Collected {len(unsub_urls)} one-click unsub URLs; POSTing...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
            for _u, status in ex.map(post_unsub, unsub_urls):
                if isinstance(status, int) and 200 <= status <= 299:
                    unsub_ok += 1
                else:
                    unsub_bad += 1
        log(f"unsub POST ok={unsub_ok} bad={unsub_bad}")

    # 校验
    client.select_folder("INBOX")
    inbox_after = len(client.search(["ALL"]))
    client.select_folder(trash)
    trash_after = len(client.search(["ALL"]))
    client.select_folder("INBOX")
    client.logout()

    top = sorted(top_domains.items(), key=lambda x: -x[1])[:15]
    out = {
        "account": acct_key, "email": email, "mode": mode,
        "total": total, "archived": archived, "kept": kept, "failed": len(failed),
        "inbox_after": inbox_after, "trash_after": trash_after,
        "unsub_ok": unsub_ok, "unsub_bad": unsub_bad, "unsub_attempted": len(unsub_urls),
        "top_domains": top,
    }
    return out


# ---------- 报告 ----------
def build_html(results, date_str):
    rows = ""
    for r in results:
        rows += f"""<tr><td>{r['account']}<br><span class='m'>{r['email']}</span></td>
        <td>{r['total']:,}</td><td class='red'>{r['archived']:,}</td>
        <td class='green'>{r['kept']:,}</td><td>{r['failed']}</td>
        <td>{r['unsub_ok']:,}/{r['unsub_attempted']:,} ok</td></tr>"""
    toprows = ""
    for r in results:
        items = " ".join(f"<span class='pill'>{d}:{c}</span>" for d, c in r["top_domains"])
        toprows += f"<tr><td>{r['account']}</td><td>{items}</td></tr>"
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>邮箱周清理报告 {date_str}</title>
<style>body{{font-family:-apple-system,"PingFang SC",sans-serif;background:#f7f8fa;color:#1f2329;padding:28px;margin:0}}
.wrap{{max-width:880px;margin:0 auto}} h1{{font-size:22px;margin:0 0 4px}}
.sub{{color:#6b7280;font-size:13px;margin-bottom:20px}}
.card{{background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:18px 20px;margin-bottom:16px}}
table{{width:100%;border-collapse:collapse;font-size:14px}} th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid #e5e7eb}}
th{{color:#6b7280;font-weight:600;font-size:12px}} .red{{color:#e23c3c;font-weight:600}} .green{{color:#1a9e57;font-weight:600}}
.m{{color:#6b7280;font-size:12px}} .pill{{display:inline-block;background:#eef2ff;color:#3730a3;font-size:11px;padding:2px 7px;border-radius:8px;margin:2px}}
.badge{{display:inline-block;font-size:11px;padding:2px 8px;border-radius:999px;background:#dcfce7;color:#166534}}</style></head>
<body><div class="wrap"><h1>邮箱周清理报告</h1>
<div class="sub">生成于 {date_str} · 模式：{results[0]['mode'] if results else '-'} · 只 MOVE 进回收站(30天可恢复)，未 EXPUNGE</div>
<div class="card"><table><tr><th>账号</th><th>总数</th><th>归档(拟)</th><th>保留</th><th>失败</th><th>退订</th></tr>{rows}</table></div>
<div class="card"><h3 style="margin-top:0">TOP 发件域分布</h3><table><tr><th>账号</th><th>域名:数量</th></tr>{toprows}</table></div>
<div class="card"><span class="badge">提示</span> 归档邮件在回收站 30 天内可手动恢复；确认无误后可在网页端清空回收站做永久删除。</div>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--accounts", default="gmail,qq")
    ap.add_argument("--mode", default="diagnose", choices=["diagnose", "execute"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--vault", default=None)
    args = ap.parse_args()

    vault = find_vault(args.vault)
    if not vault:
        raise SystemExit("[ERR] 找不到 vault，请用 --vault 指定 00_凭证_passwords.md 路径")
    log(f"vault: {vault}")

    accts = [a.strip() for a in args.accounts.split(",") if a.strip()]
    results = []
    for a in accts:
        if a not in ACCOUNTS:
            log(f"  [skip] 未知账号 {a}")
            continue
        try:
            results.append(process(a, args.mode, args.limit, vault))
        except Exception as e:
            log(f"  [ERR] {a} 失败: {e}")

    date_str = datetime.date.today().isoformat()
    out_dir = os.path.expanduser("~/.workbuddy/email_diag")
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, f"mail_cleanup_{date_str}.json")
    html_path = os.path.join(out_dir, f"mail_cleanup_{date_str}.html")
    with open(json_path, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open(html_path, "w") as f:
        f.write(build_html(results, date_str))
    log(f"\nWROTE {json_path}\nWROTE {html_path}")
    for r in results:
        log(f"  [{r['account']}] total={r['total']} archived={r['archived']} kept={r['kept']} failed={r['failed']} unsub_ok={r['unsub_ok']}")


if __name__ == "__main__":
    main()
