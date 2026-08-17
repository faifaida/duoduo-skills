---
name: duo-knowledge-classify
summary: DUO Knowledge Classify（碎片知识统一加工总入口，扩展版）
description: >
  多多个人公司碎片知识统一加工系统：小红书/微信读书/微信聊天/云盘归档采集分类，并扩展接入日历写入、微信读书周摘要、小红书周摘要、邮箱
  IMAP 批量清理（Gmail + QQ）、Notion 日记拆分。

  本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。
agent_created: true
type: consolidated
merged_from:
  - duo-knowledge-classify
  - duoduo-caldav-calendar-write
  - duoduo-weread-digest
  - duoduo-xhs-weekly-digest
  - gmail-imap-cleanup
  - notion-journal-split
disable-model-invocation: true
---

# DUO Knowledge Classify（碎片知识统一加工总入口，扩展版）

> 合并型技能。SKILL.md 只做路由；每个子能力完整保留在 `references/` 下，用到哪个场景就加载哪一份。

## 触发路由表

- **知识采集分类总入口** → 读 `references/01-knowledge-classify/SKILL.md`（原 `duo-knowledge-classify`）
- **iCloud 日历写入** → 读 `references/02-caldav-calendar-write.md`（原 `duoduo-caldav-calendar-write`）
- **微信读书周摘要** → 读 `references/03-weread-digest.md`（原 `duoduo-weread-digest`）
- **小红书周摘要** → 读 `references/04-xhs-weekly-digest.md`（原 `duoduo-xhs-weekly-digest`）
- **邮箱 IMAP 批量清理（Gmail + QQ / 中文邮箱）** → 读 `references/05-gmail-imap-cleanup.md`（原 `gmail-imap-cleanup`，已扩展支持 Gmail + QQ 双账号；配套 `scripts/mail_imap_cleanup.py` 自助读 vault 取凭证、只读诊断 / 全自动可恢复归档）
- **Notion 日记拆分** → 读 `references/06-notion-journal-split.md`（原 `notion-journal-split`）
- **R 笔记 T02 第一人称重写（重做/新建 Research 笔记）** → 读 `references/07-rnote-t02-rewrite.md`（原 `duo-rnote-t02-rewrite`，已并入）

## 使用约定

- 收到用户请求后，先在上方路由表判断属于哪个子能力，再 `Read` 对应 `references/NN-*.md`（或子目录下的 `SKILL.md`）。
- 各子能力内部依赖的 `scripts/`、`references/` 子文件已随原 skill 一并保留在对应 `references/NN-slug/` 目录中，路径相对调用即可。
- 修改某个子能力时，只改对应那一份文件，不要动其他子能力。
