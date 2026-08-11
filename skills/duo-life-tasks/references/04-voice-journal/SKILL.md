---
name: duoduo-voice-journal
description: >
  多多个人日记流水线的「手机采集 → Obsidian」机制层（2026-08-03 起取代 IMA）。
  两条源：① Apple 语音备忘录（原件进 voice 箱）；② Apple 备忘录（iPhone 快捷指令实时转写成的 Note 进 notes 箱）。
  脚本只做机制（解析碎片笔记、音频↔笔记对照、移音频进 vault 并修 embed、归档）；
  语义汇总（反填 topics/highlights、合并成当日日记）由 duoduo-day-dy skill 在 10:00 自动化里完成。
  用于「每日10:00 日记同步」自动化（1784742918079）。
agent_created: true
---

# duoduo-voice-journal（语音备忘录 + 备忘录 → Obsidian 日记 · 机制层）

把手机上的语音和文字日记，经 iCloud 采集箱，合并进 Obsidian 当日日记。**已彻底停用 IMA**（2026-08-03 多多拍板）。

## 工作流（2026-08-03 二次升级）
- **快捷指令已实时转写**：iPhone 快捷指令现在把语音**实时转成 Note** 丢进 notes 箱（自动转录），语音原件同时进 voice 箱。
- 因此 **10:00 不再转录音频**，改为「用 Note 汇总当日日记」；但仍核对 **音频↔笔记对照**。
- **机制 / 语义分离**：本 skill 的 `voice_to_journal.py` 只做机械活（解析、移音频、修 embed、归档）；**语义汇总**（反填空字段、跨碎片合并成日记）由 `duoduo-day-dy` skill 在 10:00 自动化里以 LLM 执行。

## 采集箱总览（脚本扫这两个 notes 箱 + 两个 voice 箱）
- 语音：`$VAULT/01_INBOX/voice/`（Mac 本地，向后兼容）+ `~/Library/Mobile Documents/com~apple~CloudDocs/DuoDuo_Inbox/voice/`（手机）
- 文字：`$VAULT/01_INBOX/notes/` + `~/Library/Mobile Documents/com~apple~CloudDocs/DuoDuo_Inbox/notes/`（手机，Note 实时转录后丢这里）

## Procedure（三步走，自动化内调用）
1. **--prepare（机制，无 LLM/无网络）**：
   ```
   /Users/Zhuanz/.workbuddy/binaries/python/envs/default/bin/python \
     /Users/Zhuanz/.workbuddy/skills/duoduo-voice-journal/voice_to_journal.py \
     --date <今天> --prepare
   ```
   - 解析当天 notes 箱所有碎片笔记（兼容全角冒号 + `•` 项目符号）；
   - 把每篇 embed 的录音从 voice 箱**移进** `07_Journals/01 Daily/<YYYY>/audio/`，重命名 `rec-<YYYYMMDD>-<HHMMSS>.m4a`（12/14 位命名都兼容），embed 改 `![[audio/rec-...m4a]]`；
   - 检测**孤儿音频**（voice 里有、但无笔记引用）→ 一并移进 vault audio/ 留存；
   - 打印 prepared fragments 的 JSON（每篇 frontmatter、修正后 embed、原文 body、cross_check / orphans 对照结果）。
   - `--dry-run` 可不移动文件只报告。
2. **语义汇总（加载 duoduo-day-dy skill）**：LLM 读 JSON，反填 `topics`/`highlights`、合并 frontmatter、写出 `07_Journals/01 Daily/<YYYY>/<今天>.md`（正文逐字保留），含孤儿录音段。
3. **--archive（机制）**：`...voice_to_journal.py --date <今天> --archive` 把已处理笔记移入 notes/done/。

## 已知约束
- 写入 iCloud 路径时 `os.replace` 偶发 `Errno 1 Operation not permitted`（iCloud 文件锁）→ 日记落盘可能留 `.md.tmp` 残留，先清理再重试。
- 碎片笔记 frontmatter 可能用**全角冒号**（`source：苹果录音`）与 `•` 项目符号，解析已兼容，不要当标准 YAML 硬解。
- 苹果自动转录可能有错别字（同音/中英文混），汇总时**保留原文不纠错**（除非多多明确要求）。
- 录音请用 m4a（自带 creation_time，命名含时间戳最准）；mp3/wav 无时间戳时回退文件名/文件时间。
- 一天无碎片 → 不写空日记。
- Mac 当日 10:00 睡眠 → 文件延到下一个 10:00 处理，属正常非失败。

## 动作节点（多多能听懂的）
1. 你睡前用语音备忘录录一段（或写备忘录一段）→ 快捷指令一键丢进对应采集箱（Note 已自动转写）。
2. 每天 10:00（Mac 在线时）自动把碎片 Note 汇总成当天 Obsidian 日记，并**内嵌可播放的音频**、**反填 topics/highlights**。
3. 你打开 Obsidian 就能看到带音频播放器的日记，按需改几个字；要加日历待办就单独跟我说。
