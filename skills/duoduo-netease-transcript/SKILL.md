---
name: duoduo-netease-transcript
description: >
  On-demand transcript sync for 曲曲 (NetEase/网易) recordings. When 多多 asks to transcribe (or after a
  new recording is ready), pull the latest transcript progress and land new segments into the
  product-manager folder (owner = 产品经理) so 多多 can see how far transcription has gotten. NOT a
  scheduled automation — triggered on demand only. Renamed from the former ququ-transcript-sync on
  2026-07-26.
agent_created: true
---

# duoduo-netease-transcript (转录进度同步 · 按需)

Keeps the transcription visible and owned — but only when 多多 actually needs it.

## When to use
- 多多说"转录一下 / 同步转录 / 转录跟到哪了"等按需触发。
- 新录音/新一期出来，需要把进度落盘时。
- **不是**定时任务，不要设每2小时自动跑（转录已按需，跑完即止）。

## Procedure
1. **On-demand sync**: 多多触发后才拉最新转录进度（不要周期性轮询）。
2. **Land new segments** into the product-manager folder (`04_产品经理/`), Owner = 产品经理.
3. 多多可随时打开文件夹看转录进度。

## Notes
- Owner is 产品经理 (moved from the original GPT owner per 多多's 2026-07-24 decision).
- This is a sync/landing task, not a publish task.
- Renamed from `ququ-transcript-sync` → `duoduo-netease-transcript` on 2026-07-26.
- 2026-07-26 修正：从「每2小时自动」改为「按需触发」。转录已完成时无需再跑。

## 动作节点（多多能听懂的）
1. 你让我转录/同步时，我才去拉一次进度（不是每2小时自己跑）。
2. 新转录段落落进产品经理文件夹（owner=产品经理）。
3. 你随时能看转录跟到哪了。
