# 微信聊天导出（原 skill: duoduo-wechat-chat-export）

# wechat-chat-export (微信聊天记录导出)

Export specific WeChat conversations to Obsidian Markdown. macOS WeChat has no built-in "export to
file"; data lives in the sandboxed container and is encrypted, so export is scoped and deliberate.

## When to use
- 多多 says "导出微信聊天" / "把某个群的记录弄出来" / similar.
- Never bulk-export everything — scope is chosen by 多多 each time.

## Procedure
1. **Confirm scope first.** Ask 多多 which conversations (groups / people) to export. Do NOT start until
   scope is confirmed. Present the candidate list if discoverable.
2. **Locate data.** WeChat is running; sandbox at
   `~/Library/Containers/com.tencent.xinWeChat/Data/...`. The chat DB is encrypted; extracting readable
   history requires the session key / a supported export method. Confirm the working method before
   touching data.
3. **Extract scoped conversations only** — the ones 多多 approved, nothing else.
4. **Convert to Markdown** with date frontmatter (yaml: date, peer, message count) and write into the
   Obsidian target folder 多多 specified.
5. **Report a manifest**: which conversations, how many messages, where they landed.

## Safety
- This reaches private message content. External actions are forbidden; keep output inside the Vault.
- Never export outside the approved scope.
- If the extraction method is uncertain, STOP and confirm with 多多 rather than guessing.

## 动作节点（多多能听懂的）
1. 你指定要导出哪些聊天（群/人），我不全量导。
2. 从本机微信数据里抽取指定会话的聊天记录。
3. 转成 Markdown 落进 Obsidian 指定目录，带日期，可检索。
4. 导出前先跟你确认范围，导出后给你一份清单（导了哪些、多少条、落在哪）。
