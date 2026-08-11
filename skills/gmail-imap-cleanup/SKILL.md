---
name: gmail-imap-cleanup
description: Connect to Gmail via IMAP with an App Password and do bulk mailbox operations (rename labels, move/delete thousands of emails) reliably. Covers the two classic traps that silently break Gmail IMAP scripts: (1) the modified-UTF-7 mailbox-name encoding bug (comma vs dot), and (2) Gmail's intermittent IMAP throttling (returns malformed "Could not parse command" BAD responses) and how to survive it without hammering. Use when a user wants to bulk-clean, label-rename, or archive Gmail via script (App Password available), especially after Apple Mail / manual IMAP attempts failed.
agent_created: true
---

# Gmail IMAP bulk cleanup (App Password)

## When to use
- User has a Gmail **App Password** (16-char, generated once at myaccount.google.com/apppasswords — NOT the login password, NOT an OAuth token).
- Task: move/delete thousands of emails, rename a label, copy messages between labels, etc.
- Apple Mail automation failed (Gmail labels via Apple Mail are unreliable: move=add-tag, new-label-sync fails, bulk ops time out).

## Auth
```
import imaplib
c = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=8)
c.login("user@gmail.com", "xxxx xxxx xxxx xxxx")  # the 16-char app password, spaces optional
```
- Stores nothing; re-use the same password. It never expires until the user revokes it.
- 2FA stays ON — App Password bypasses the interactive 2FA prompt (that's the whole point).

## ⚠️ TRAP 1 — mailbox-name encoding (this silently breaks everything)
Gmail stores non-ASCII mailbox names in **modified UTF-7** (RFC 3501). The standard `str.encode('utf-7')` is WRONG. You must:
- base64 the UTF-16-BE bytes,
- replace `/` (base64 index 63) with **comma `,`** (NOT dot `.`!),
- wrap in `&` ... `-` (hyphen terminator, NOT comma!).

```python
import base64
def mutf7(text):
    res=[]; buf=[]
    def flush():
        if buf:
            e=base64.b64encode("".join(buf).encode("utf-16-be")).decode("ascii").rstrip("=").replace("/",".")
            res.append("&"+e+"-"); buf.clear()   # COMMA inside, HYPHEN terminator
    for ch in text:
        o=ord(ch)
        if 0x20<=o<=0x7e and ch!="&": flush(); res.append(ch)
        elif ch=="&": flush(); res.append("&-")
        else: buf.append(ch)
    flush(); return "".join(res)
```
Verify against reality before trusting it:
```python
c.list()   # shows server-side names, e.g. "2021&,w8-5&,w8-1&TktSTQ-"  (= 2021／5／1之前)
```
The encoding is CORRECT iff `mutf7("2021／5／1之前")` prints exactly `2021&,w8-5&,w8-1&TktSTQ-`. If you see a dot (`&.w8-`) the label SELECT will fail with `BAD [Could not parse command]` and you'll waste hours thinking it's a rate-limit.

## ⚠️ TRAP 2 — Gmail's intermittent IMAP throttling
Gmail throttles bulk IMAP. Symptoms (ALL are throttle, not your bug):
- `TimeoutError: connect timed out` / socket 30s timeout on `IMAP4_SSL`.
- `SELECT command error: BAD [b'Could not parse command']` even with **correct** encoding, on an otherwise-valid command. (This is the trap — looks identical to TRAP 1 but is a throttled server returning garbage.)
- Both your sandbox AND the user's Apple Mail can be blocked simultaneously (account-level, not IP).

### Survival rules (do NOT violate these)
1. **Never hammer.** A `while True` that restarts on every failure + reconnects in a tight loop makes the throttle WORSE. Kill any script doing connect-retry-spam.
2. **Short timeouts, fast fail.** `timeout=8` for connect so a dead connection fails in 8s, not 45s. Don't let one op hang for 45s.
3. **Long cooldowns between attempts.** When throttled, sleep 20 MINUTES with ZERO connections, then try ONE clean session. A single clean session does the whole job (a few hundred IMAP commands) in 2–5 min.
4. **Make it resumable.** Persist progress (`{"label_copied":false,"promo_done":["d1","d2"]}`) to a JSON file; each run picks up where it left off. Idempotent ops only (re-running a domain's search returns only what's left).
5. **Don't trust a single "success" window blindly** — but do verify with before/after counts via `c.search(None,"ALL")` on the label and a re-search of the source.

## Bulk operations (idempotent, resumable)
```python
# copy old label -> new label (rename = create new + copy + delete old)
c.select(mutf7(OLD)); r,d=c.search(None,"ALL"); uids=d[0].split()
for i in range(0,len(uids),150):
    c.uid("COPY", ",".join(uids[i:i+150]), mutf7(NEW)); time.sleep(1)
# verify new has ~same count, THEN delete old (deleting a label only untags; messages stay in All Mail)
c.select(mutf7(NEW)); r,d=c.search(None,"ALL")
if len(d[0].split()) >= 3300: c.delete(mutf7(OLD))

# move promo to Trash (30-day recoverable), per-domain
c.select("INBOX")
for d in domains:
    r,res=c.search(None,"FROM","@"+d)
    uids=res[0].split() if res[0] else []
    for i in range(0,len(uids),200):
        c.uid("MOVE", ",".join(uids[i:i+200]), trash_name); time.sleep(1)
```
- Trash mailbox name is usually `"[Gmail]/Trash"` (English) — detect via `c.list()` + find `\Trash` flag, don't hardcode.
- Search syntax: `c.search(None,"FROM","@domain")` works; `X-GM-RAW "from:a OR from:b"` does NOT (X-GM-RAW rejects OR). Use native IMAP `OR(FROM @a)(FROM @b)` tree or loop per domain.

## Unsubscribe + Archive (noise reduction — the usual goal)
The point of most Gmail cleanups is cutting future noise, not just moving mail. Two steps:

### 1) Scan for unsubscribe headers (read-only, batch)
```python
c.select("INBOX", readonly=True)
typ,d = c.search(None,"ALL"); uids=d[0].decode().split()
CH=400
for s in range(0,len(uids),CH):
    rng=",".join(uids[s:s+CH])
    typ,res = c.fetch(rng, '(UID BODY.PEEK[HEADER.FIELDS (FROM LIST-UNSUBSCRIBE LIST-UNSUBSCRIBE-POST)])')
    for i in range(0,len(res),2):
        blk=res[i][0].decode(); uid=re.search(r'UID\s+(\d+)',blk).group(1)
        hdr=res[i][1].decode(errors="ignore")
        lu=re.search(r'(?im)^List-Unsubscribe:\s*(.*)',hdr,re.S)
        lp=re.search(r'(?im)^List-Unsubscribe-Post:',hdr)
        # oneclick = first <https://...> in lu group; else <mailto:...>
```
- A message has a `List-Unsubscribe` header ⇒ it's a mailing list / subscription (noise candidate). No header ⇒ personal/billing/system, leave alone.

### 2) RFC 8058 One-Click unsubscribe (POST)
For each `https://` unsub URL with a `List-Unsubscribe-Post` header:
```python
req=urllib.request.Request(url, data=b"List-Unsubscribe=One-Click",
     headers={"Content-Type":"application/x-www-form-urlencoded"})
with urllib.request.urlopen(req,timeout=15) as r: code=r.status   # accept 200/202/204
```
- For `mailto:` unsub URLs: send a blank email from the account via `smtplib.SMTP_SSL("smtp.gmail.com",465)` login with the same App Password. (In practice mailto one-click often fails server-side — treat as best-effort.)
- Run POSTs concurrently (16 workers) for speed; persist per-URL status to a results file and tally 2xx vs fail. Common fails: 404 (link expired), 403 (blocked), 429 (rate-limited → back off), DNS/timeout.

### 3) Archive out of inbox (⚠️ NOT STORE -FLAGS \Inbox)
To pull subscription mail out of the inbox **without deleting** (kept in All Mail, fully recoverable):
- ❌ `c.uid("STORE", rng, "-FLAGS", "(\\Inbox)")` → Gmail returns `BAD [Unable to parse flag \Inbox]`. Does NOT work.
- ✅ `c.uid("MOVE", rng, ALLMAIL)` where `ALLMAIL = "[Gmail]/&YkBnCZCuTvY-"` (the modified-UTF-7 name for "All Mail"; verify via `c.list()` and find the mailbox with the `\All` flag — do not hardcode blindly).
- Verify with before/after `c.search(None,"ALL")` on INBOX (e.g. 9017 → 4372 after archiving 4645).
- Archiving is reversible: messages stay in All Mail and can be dragged back to Inbox anytime.
- If the goal is permanent deletion instead, MOVE to `[Gmail]/Trash` then `EXPUNGE` (30-day recoverable); only `EXPUNGE` makes it permanent.

## One-shot runner shape
```
for round in cycles:
    if progress_complete: break
    sleep(1200)                       # 20-min NO-CONNECT cooldown
    try:
        do_all_work()                 # one clean session, resumable
        break
    except Exception:                # throttle hit mid-way
        log("throttled, will cooldown again")
        # loop -> another 20-min cooldown
```

## What NOT to do
- Don't use Apple Mail AppleScript for Gmail bulk ops (unreliable).
- Don't keep reconnecting in a tight loop when throttled.
- Don't use a 45s socket timeout (you'll wait 45s × N retries per failure).
- Don't "fix" `Could not parse command` by changing encoding if you already verified the encoding matches `c.list()` output — it's throttle, cool down instead.
