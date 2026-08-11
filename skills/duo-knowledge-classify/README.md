# DUO Knowledge Classify（碎片知识统一加工总入口，扩展版）

合并型技能，目录结构：

```
duo-knowledge-classify/
├── SKILL.md            # 路由器：合并所有触发词 + 下方索引表
├── README.md           # 本文件（人话地图）
└── references/
    ├── 01-notion-journal-split/   # 知识采集分类总入口（原 duo-knowledge-classify）
    ├── 02-notion-journal-split.md # iCloud 日历写入（原 duoduo-caldav-calendar-write）
    ├── 03-notion-journal-split.md # 微信读书周摘要（原 duoduo-weread-digest）
    ├── 04-notion-journal-split.md # 小红书周摘要（原 duoduo-xhs-weekly-digest）
    ├── 05-notion-journal-split.md # Gmail 批量清理（原 gmail-imap-cleanup）
    ├── 06-notion-journal-split.md # Notion 日记拆分（原 notion-journal-split）
```

## 子能力索引

| # | 能力 | 原 skill | 入口文件 |
|---|------|----------|----------|
| 01 | 知识采集分类总入口 | `duo-knowledge-classify` | `references/01-knowledge-classify/SKILL.md` |
| 02 | iCloud 日历写入 | `duoduo-caldav-calendar-write` | `references/02-caldav-calendar-write.md` |
| 03 | 微信读书周摘要 | `duoduo-weread-digest` | `references/03-weread-digest.md` |
| 04 | 小红书周摘要 | `duoduo-xhs-weekly-digest` | `references/04-xhs-weekly-digest.md` |
| 05 | Gmail 批量清理 | `gmail-imap-cleanup` | `references/05-gmail-imap-cleanup.md` |
| 06 | Notion 日记拆分 | `notion-journal-split` | `references/06-notion-journal-split.md` |

## 怎么用

- AI 接到请求 → 查 SKILL.md 路由表 → 只加载对应 `references/NN-*` 那一份，不一次塞爆上下文。
- 你要改某个场景的细节，只动对应那一份文件即可。

## 合并来源（已停用独立 skill）

- duo-knowledge-classify（→ references/01-*）
- duoduo-caldav-calendar-write（→ references/02-*）
- duoduo-weread-digest（→ references/03-*）
- duoduo-xhs-weekly-digest（→ references/04-*）
- gmail-imap-cleanup（→ references/05-*）
- notion-journal-split（→ references/06-*）
