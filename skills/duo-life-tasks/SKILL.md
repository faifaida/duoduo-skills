---
name: duo-life-tasks
summary: "DUO Life Tasks（日记/日历/灵魂拷问/周复盘/语音日记 综合）"
description: |
  多多个人生活操作系统：当日日记汇总、日记转日历、每日灵魂拷问、语音日记采集、周复盘、草稿 AI 精修、月相周历整合。
  本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。
agent_created: true
type: consolidated
merged_from:
  - duoduo-day-dy
  - duoduo-diary-to-calendar-pipeline
  - duoduo-soul-question
  - duoduo-voice-journal
  - duoduo-weekly-review-calendar
  - journal-review-refine
  - weekly-life-os-calendar
---

# DUO Life Tasks（日记/日历/灵魂拷问/周复盘/语音日记 综合）

> 合并型技能。SKILL.md 只做路由；每个子能力完整保留在 `references/` 下，用到哪个场景就加载哪一份。

## 触发路由表

- **当日日记汇总** → 读 `references/01-day-diary/SKILL.md`（原 `duoduo-day-dy`）
- **日记转日历流水线** → 读 `references/02-diary-to-calendar.md`（原 `duoduo-diary-to-calendar-pipeline`）
- **每日灵魂拷问** → 读 `references/03-soul-question.md`（原 `duoduo-soul-question`）
- **语音日记采集** → 读 `references/04-voice-journal/SKILL.md`（原 `duoduo-voice-journal`）
- **周复盘与下周日程** → 读 `references/05-weekly-review.md`（原 `duoduo-weekly-review-calendar`）
- **日记草稿 AI 精修** → 读 `references/06-journal-review-refine.md`（原 `journal-review-refine`）
- **Life OS 月相周历** → 读 `references/07-weekly-life-os.md`（原 `weekly-life-os-calendar`）

## 使用约定

- 收到用户请求后，先在上方路由表判断属于哪个子能力，再 `Read` 对应 `references/NN-*.md`（或子目录下的 `SKILL.md`）。
- 各子能力内部依赖的 `scripts/`、`references/` 子文件已随原 skill 一并保留在对应 `references/NN-slug/` 目录中，路径相对调用即可。
- 修改某个子能力时，只改对应那一份文件，不要动其他子能力。
