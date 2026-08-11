---
name: duo-podcast-studio
summary: "DUO Podcast Studio（录制剪辑 + 跨平台分发同步）"
description: |
  多多中文 AI 对话播客「未完成实验」一站式技能：从单集制作/修复/混音/质检，到把小宇宙新单集同步到 Apple Podcasts 与喜马拉雅。
  本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。
agent_created: true
type: consolidated
merged_from:
  - duo-podcast-workbuddy
  - duoduo-podcast-sync
---

# DUO Podcast Studio（录制剪辑 + 跨平台分发同步）

> 合并型技能。SKILL.md 只做路由；每个子能力完整保留在 `references/` 下，用到哪个场景就加载哪一份。

## 触发路由表

- **录制剪辑与质检** → 读 `references/01-podcast-workbuddy.md`（原 `duo-podcast-workbuddy`）
- **跨平台分发同步** → 读 `references/02-podcast-sync/SKILL.md`（原 `duoduo-podcast-sync`）

## 使用约定

- 收到用户请求后，先在上方路由表判断属于哪个子能力，再 `Read` 对应 `references/NN-*.md`（或子目录下的 `SKILL.md`）。
- 各子能力内部依赖的 `scripts/`、`references/` 子文件已随原 skill 一并保留在对应 `references/NN-slug/` 目录中，路径相对调用即可。
- 修改某个子能力时，只改对应那一份文件，不要动其他子能力。
