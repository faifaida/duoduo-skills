---
name: duo-company
summary: "DUO Company Ops（每日参谋长 + 夜巡 + 专家巡检）"
description: |
  多多个人公司运营节律：每日 13:00 参谋长聚合、23:00 夜巡归档、三专家每小时自取机制。
  本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。
agent_created: true
type: consolidated
merged_from:
  - duoduo-company-daily-os
  - duoduo-company-night-patrol
  - duoduo-expert-hourly-patrol
---

# DUO Company Ops（每日参谋长 + 夜巡 + 专家巡检）

> 合并型技能。SKILL.md 只做路由；每个子能力完整保留在 `references/` 下，用到哪个场景就加载哪一份。

## 触发路由表

- **每日参谋长例程** → 读 `references/01-company-daily-os.md`（原 `duoduo-company-daily-os`）
- **夜巡归档** → 读 `references/02-company-night-patrol.md`（原 `duoduo-company-night-patrol`）
- **专家每小时自取** → 读 `references/03-expert-hourly-patrol.md`（原 `duoduo-expert-hourly-patrol`）

## 使用约定

- 收到用户请求后，先在上方路由表判断属于哪个子能力，再 `Read` 对应 `references/NN-*.md`（或子目录下的 `SKILL.md`）。
- 各子能力内部依赖的 `scripts/`、`references/` 子文件已随原 skill 一并保留在对应 `references/NN-slug/` 目录中，路径相对调用即可。
- 修改某个子能力时，只改对应那一份文件，不要动其他子能力。
