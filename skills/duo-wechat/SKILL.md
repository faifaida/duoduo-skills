---
name: duo-wechat
summary: "DUO WeChat（公众号长图生成 + 长图发布 + 聊天导出）"
description: |
  微信公众号相关一站式技能：把长文生成 DUODUO 风格长图、自动发布长图到公众号后台、把微信聊天记录导出到 Obsidian。
  本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。
agent_created: true
type: consolidated
merged_from:
  - duo_longpic-gen
  - duoduo-wechat-publish
  - duoduo-wechat-chat-export
---

# DUO WeChat（公众号长图生成 + 长图发布 + 聊天导出）

> 合并型技能。SKILL.md 只做路由；每个子能力完整保留在 `references/` 下，用到哪个场景就加载哪一份。

## 触发路由表

- **公众号长图生成** → 读 `references/01-longpic-gen/SKILL.md`（原 `duo_longpic-gen`）
- **公众号长图发布** → 读 `references/02-wechat-publish/SKILL.md`（原 `duoduo-wechat-publish`）
- **微信聊天导出** → 读 `references/03-wechat-chat-export.md`（原 `duoduo-wechat-chat-export`）

## 使用约定

- 收到用户请求后，先在上方路由表判断属于哪个子能力，再 `Read` 对应 `references/NN-*.md`（或子目录下的 `SKILL.md`）。
- 各子能力内部依赖的 `scripts/`、`references/` 子文件已随原 skill 一并保留在对应 `references/NN-slug/` 目录中，路径相对调用即可。
- 修改某个子能力时，只改对应那一份文件，不要动其他子能力。
