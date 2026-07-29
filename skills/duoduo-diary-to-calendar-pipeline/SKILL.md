---
name: duoduo-diary-to-calendar-pipeline
description: >
  Daily pipeline that pulls 多多's IMA journal, exports it to Obsidian, extracts todos, and writes them
  to iCloud Calendar via CalDAV. Use it for the 13:00 daily-journal-sync automation and any "turn my
  journal into calendar events" task. Simplified per 多多's 2026-07-26 instruction: the "封口" (closing)
  is handled between 多多 and IMA — this pipeline just pulls the journal from IMA. Still encodes the
  D-1 date extraction, 18/21 retry safety net, 1-hour default block, and atomic export write.
agent_created: true
---

# duoduo-diary-to-calendar-pipeline (IMA 日记 → Obsidian → 日历)

Daily chain: IMA journal → Obsidian markdown → extract todos → iCloud calendar (via `duoduo-caldav-calendar-write`).

## When to use
- The 13:00 journal-sync automation.
- Any request to convert 多多's written journal into calendar events or Obsidian notes.

## Procedure
1. **Pull from IMA** using `export_diary.py` (located in the journal-export workspace). Run it with the
   managed venv python. The "封口" (when the journal is considered closed/final) is agreed between 多多
   and IMA — this pipeline does NOT implement its own closing gate; it simply grabs the journal that IMA
   has made available.
2. **Extract by DATE, not "latest".** Pull the **D-1 (previous day)** entry by its journal date, never by
   `create_time` "most recent" — that catches a stale jumped-entry and writes old content to today.
3. **Safety net (A).** If 13:00 finds no usable D-1 entry, retry at 18:00 and 21:00. Never write an empty
   or stale entry to the calendar.
4. **Write todos to calendar** via `duoduo-caldav-calendar-write` (datetime normalized, verified). Todos
   with no explicit time get a **1-hour default block** (see that skill).
5. **Atomic export.** `export_diary.py` must write to a `.tmp` file then `os.replace()` onto the final
   path, retrying on failure — this prevents iCloud file-lock deadlock that corrupts the Obsidian file.

## Known failure modes
| Symptom | Root cause | Fix |
|---|---|---|
| Calendar empty / shows yesterday's stale text | Pulled "latest by create_time" | Pull by D-1 date |
| Obsidian file corrupted / locked | Non-atomic write under iCloud | `.tmp` + `os.replace` + retry |
| Todo missing | Journal not yet sent before 13:00 | 18/21 retry safety net |
| Timeless todo lost | No default duration | 1-hour default block |

## 动作节点（多多能听懂的）
1. 每天 13:00，去 IMA 取你**昨天**写的日记（不是"最新一篇"，防止跳记抓到旧文）。封口由你和 IMA 之间完成，我直接抓就行。
2. 抽出的待办写进 iCloud 日历（走 `duoduo-caldav-calendar-write` 规则；没写时间的待办自动填 1 小时块）。
3. 安全网：13:00 没抽到→18/21 点自动重试，绝不写空或写陈旧内容。
4. 导出文件用临时文件+原子替换，防止 iCloud 文件锁卡死。
