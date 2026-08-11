---
name: duo-voice-deai
summary: "DUO Voice De-AI（去 AI 味原声重写 + 中文去 AI 痕迹）"
description: |
  多多对外文案去 AI 味 + 原声重写总入口：覆盖所有平台公开发文与口播稿，并扩展接入简体中文专用去 AI 痕迹（qu-ai-wei）。
  本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。
agent_created: true
type: consolidated
merged_from:
  - duoduo-voice-deai
  - qu-ai-wei
---

# DUO Voice De-AI（去 AI 味原声重写 + 中文去 AI 痕迹）

> 合并型技能。SKILL.md 只做路由；每个子能力完整保留在 `references/` 下，用到哪个场景就加载哪一份。

## 触发路由表

- **去 AI 味原声重写** → 读 `references/01-voice-deai/SKILL.md`（原 `duoduo-voice-deai`）
- **简体中文去 AI 痕迹** → 读 `references/02-qu-ai-wei/SKILL.md`（原 `qu-ai-wei`）

## 使用约定

- 收到用户请求后，先在上方路由表判断属于哪个子能力，再 `Read` 对应 `references/NN-*.md`（或子目录下的 `SKILL.md`）。
- 各子能力内部依赖的 `scripts/`、`references/` 子文件已随原 skill 一并保留在对应 `references/NN-slug/` 目录中，路径相对调用即可。
- 修改某个子能力时，只改对应那一份文件，不要动其他子能力。
