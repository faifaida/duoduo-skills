# 邮箱 IMAP 批量清理（Gmail + QQ / 中文邮箱）

# Mailbox IMAP bulk cleanup — Gmail & QQ (Chinese mailboxes)

> 统一入口：Gmail 走 `imap.gmail.com`，QQ 走 `imap.qq.com`。两者都用 16 位授权码（非登录密码）。
> 配套脚本：`scripts/mail_imap_cleanup.py`（参数化双账号，自助读 vault 取凭证，支持只读诊断 / 全自动可恢复归档）。

## When to use
- 用户有 **Gmail App Password**（16 位，myaccount.google.com/apppasswords 生成，**不是**登录密码、不是 OAuth token）。
- 用户有 **QQ IMAP 授权码**（QQ 邮箱网页端「设置 → 账户 → 开启 IMAP/SMTP」后生成 16 位授权码）。
- 任务：批量清理收件箱推广/订阅噪音（MOVE 进回收站 30 天可恢复，或 RFC 8058 一键退订）。
- ⚠️ 凭证已存 vault `00_凭证_passwords.md`（Gmail 在 `### gmail/google drive`、QQ 在 `### qq和qq邮箱`）。**脚本自助解析，绝不跟用户要码。**

## 账号与凭证（vault 段）
| 账号 | Host:Port | 凭证取处 | 登录密码 |
|---|---|---|---|
| `fayezang28@gmail.com` | `imap.gmail.com:993` | vault `### gmail/google drive` → 行 `应用密码：qvue twxe wilo weqy` | 16 位 app password（空格可去）|
| `939526417@qq.com` | `imap.qq.com:993` | vault `### qq和qq邮箱` → 行 `imap：gdbwifydxzyubfid` | IMAP 授权码（无空格）|

脚本解析逻辑（`scripts/mail_imap_cleanup.py:load_creds`）：按 `### <段名>` 切块，Gmail 块取 `@gmail.com` 邮箱 + `应用密码[:：]` 后串（去空格）；QQ 块取 `imap[:：]` 后串，邮箱回退 `939526417@qq.com`。

## 统一分类策略（两箱通用 · 反向白名单）
判据顺序：
1. **保留**：发件父域 ∈ `KEEP_ROOT`（apple/qq/tencent/gmail/outlook/microsoft/支付/社交/物流/国内主要服务/常见银行）或 ∈ `KEEP_CONTENT`（已知有价值内容订阅：medium/substack/consensus/heygen 等，即使带退订头也保留）。
2. **归档**：非核心域 **且** 带 `List-Unsubscribe` 头 → MOVE 进回收站（30 天可恢复，非永久删）。
3. **保留**：无任何退订头的事务/个人/未知系统邮件（无退订头 = 大概率非群发订阅）。

`KEEP_ROOT`（核心基础设施域，两箱同用）：
```
apple.com icloud.com qq.com tencent.com foxmail.com gmail.com outlook.com
microsoft.com live.com hotmail.com u.nus.edu paypal.com alipay.com wechat.com
fedex.com ups.com dhl.com 163.com netease.com baidu.com kingsoft.com naver.jp
nokia.com yinxiang.com shanbay.com jd.com qunar.com taobao.com service.netease.com
comms.nokia.com mail.qq.com exmail.qq.com id.apple.com itunes.com orders.apple.com
icbc.com.cn ccb.com abchina.com bankcomm.com cmbchina.com hsbc.com
bankofamerica.com chase.com citibank.com
```
> ⚠️ 社媒通知域（facebookmail.com / instagram.com / tiktok / twitter 等）**不放 KEEP_ROOT**——它们的退订类通知(带 List-Unsubscribe 头)应归档降噪；安全/登录/改绑提醒无退订头自动保留。与 Gmail 2026-08-17 执行一致（instagram/pinterest/facebook 通知划为归档）。
`KEEP_CONTENT`（有价值内容订阅，带退订头也保留，避免周自动化误清）：
```
medium.com substack.com consensus.app use.ai heygen.com timdenning.com
justinwelsh.com gagaoolala.com cinewav.com spotify.com
```
> 周自动化误清风险靠「30 天回收站可恢复」兜底；若某内容域重要，加进 `KEEP_CONTENT` 即可。

## ⚠️ TRAP 1 — 邮箱名编码（Gmail 非 ASCII 文件夹）
Gmail 非 ASCII 文件夹名用 **modified UTF-7**（RFC 3501）。标准 `str.encode('utf-7')` 错。必须：base64 UTF-16-BE → `/` 换逗号 `,` → 包 `&`…`-`。
```python
import base64
def mutf7(text):
    res=[]; buf=[]
    def flush():
        if buf:
            e=base64.b64encode("".join(buf).encode("utf-16-be")).decode("ascii").rstrip("=").replace("/",".")
            res.append("&"+e+"-"); buf.clear()
    for ch in text:
        o=ord(ch)
        if 0x20<=o<=0x7e and ch!="&": flush(); res.append(ch)
        elif ch=="&": flush(); res.append("&-")
        else: buf.append(ch)
    flush(); return "".join(res)
```
QQ 文件夹名多为英文，一般不触发此坑；Gmail 的 `[Gmail]/All Mail`、`[Gmail]/Trash` 也建议用 `c.list()` + 找 `\Trash` / `\All` 标志位，不要硬编码。

## ⚠️ TRAP 2 — Gmail 间歇性 IMAP 限流
症状（全是限流，不是你的 bug）：`TimeoutError: connect timed out`；`SELECT ... BAD [Could not parse command]`（和 TRAP 1 一模一样但其实是限流）。
生存法则（勿违反）：① 绝不 tight-loop 重连（限流更重）② 短超时（connect `timeout=30` 足够，别 45s）③ 限流后**断开 0 连接**睡长冷却再试一次干净会话 ④ 进度落 JSON 可续跑、只做幂等操作 ⑤ 用 before/after `search(ALL)` 校验。

## ⚠️ TRAP 3 — QQ 的 `SEARCH` 筛选**不可靠**（实战踩坑，2026-08-17）
- `SEARCH HEADER "List-Unsubscribe" ""`（空串）在 QQ 上**匹配全部邮件**（返回 34194），不能用来筛订阅类。
- `SEARCH FROM "@domain"` 在 QQ 上**返回 0**（与真实样本矛盾，apple/facebook 都查不到），不能用来按域名分类。
- ✅ **唯一稳的路：逐封 `fetch` 真实 `From` 头** → `re.search` 取发件域分类。34194 封约 35–55 分钟（受 QQ 响应速度影响）。脚本用 `CHUNK=200` 流式 fetch + 即时 MOVE，幂等可断点续跑。

## 回收站文件夹真名
- **Gmail**：通常 `[Gmail]/Trash`（英文）；用 `c.list()` 找 `\Trash` 标志位，别硬编码。
- **QQ**：**`Deleted Messages`**（英文）。实测确认。
- 统一探测：`list_folders()` 返回 `(flags, delimiter, name)`，优先匹配 `b'\\Trash'` 标志；回退按名含 `trash`/`deleted`（不区分大小写）。

## 批量操作（幂等、可续跑）
```python
# 归档进回收站（30 天可恢复，非永久删）—— 两箱通用
client.select_folder("INBOX")
for d in domains:
    uids = client.search(["FROM", "@"+d])   # 仅 Gmail 可靠；QQ 改用 fetch 分类
    for i in range(0, len(uids), 200):
        client.move(uids[i:i+200], trash_name); time.sleep(1)
```
- Gmail 归档替代 `STORE -FLAGS \\Inbox`（Gmail 返回 `BAD`，不支持）；用 `MOVE` 到 All Mail（`move` 可逆，邮件留在 All Mail）。
- **周自动化只 MOVE 进回收站，绝不 `EXPUNGE`**（EXPUNGE 才永久删）。30 天内可手救。

## 退订 + 归档（降噪，主要目标）
### 1) 扫退订头（只读，批量）
```python
client.select_folder("INBOX", readonly=True)
uids = client.search(["ALL"])
CH = 400
for s in range(0, len(uids), CH):
    rng = uids[s:s+CH]
    data = client.fetch(rng, ["BODY.PEEK[HEADER.FIELDS (FROM LIST-UNSUBSCRIBE LIST-UNSUBSCRIBE-POST)]"])
    for uid, item in data.items():
        raw = item[b"BODY[HEADER.FIELDS ...]"].decode("utf-8","ignore")
        # uid 取响应描述符（imapclient 已把 uid 作为 dict key，无需正则）
        lu = re.search(r"(?im)^List-Unsubscribe:\s*(.*)", raw, re.S)
        lp = re.search(r"(?im)^List-Unsubscribe-Post:", raw)
```
### 2) RFC 8058 One-Click 退订（POST）
```python
req = urllib.request.Request(url, data=b"List-Unsubscribe=One-Click",
     headers={"Content-Type":"application/x-www-form-urlencoded"})
with urllib.request.urlopen(req, timeout=15) as r: code = r.status   # 接受 200/202/204
```
- `mailto:` 退订：用 `smtplib.SMTP_SSL("smtp.gmail.com",465)` 同 app password 发空白邮件（实际常服务端失败，尽力即可）。
- 并发 16 worker 提速；每 URL 状态落结果文件，统计 2xx vs 失败。常见失败：404（链接过期）、403（拦截）、429（限流后退避）、DNS/超时。
- **实战实测（QQ 2026-08-17）**：3000 链接尝试 / 成功 1378 / 失败 1622（失败多为链接失效或发送端限流）。说明一键退订只能清理一部分，归档才是主降噪手段。

### 3) 归档出收件箱
- 见上「批量操作」。归档可逆（在回收站 / All Mail 可拖回）。

## 脚本形状（`scripts/mail_imap_cleanup.py`）
```
参数：--accounts gmail,qq  --diagnose(默认,只读)  --execute(归档+退订)  --limit N(取样测试)  --vault PATH
流程：
  load_creds()              # 自助解析 vault
  for acct in accounts:
      connect + login + select INBOX
      trash = detect_trash()      # \Trash 标志 / 名含 trash|deleted
      all_uids = search(ALL); total = len
      for chunk in 200:
          fetch 真实 From + 退订头
          classify → keep / archive
          diagnose: 仅计数 + 收集 top 发件人
          execute:  MOVE archive_uids → trash; 收集 unsub URL(cap)
      execute 末: 并发 POST 退订; verify before/after counts
  输出 HTML 周报 + JSON（total/archived/kept/failed/inbox_after/trash_after/unsub_ok/bad）
```
- 复用 Gmail TRAP 2 生存法则（短超时、长冷却、可续跑、幂等）。
- 输出落 `~/.workbuddy/email_diag/`，文件名含账号 + 日期。

## 实测结果（存档）
- **Gmail**（2026-08-17，手动照本 skill）：INBOX 3316 → 归档 72 / 保留其余；一键退订支持 62 成功 60 失败 1。
- **QQ**（2026-08-17，脚本跑完落盘 `qq_result.json`）：INBOX **34194 → 归档 21582 / 保留 12612 / 失败 0**；回收站增量与归档数一致、INBOX 后与保留数一致，无丢失/重复；一键退订 3000 尝试 / 1378 成功 / 1622 失败。

## What NOT to do
- 别用 Apple Mail AppleScript 做 Gmail/QQ 批量（不可靠）。
- 限流时别 tight-loop 重连。
- 别用 45s socket 超时。
- 周自动化**绝不 EXPUNGE**（永久删）；只 MOVE 进回收站。
- 别用 QQ 的 `SEARCH HEADER` / `SEARCH FROM` 筛选（见 TRAP 3），改逐封 fetch。
