# DUO Life Tasks（日记/日历/灵魂拷问/周复盘/语音日记 综合）

合并型技能，目录结构：

```
duo-life-tasks/
├── SKILL.md            # 路由器：合并所有触发词 + 下方索引表
├── README.md           # 本文件（人话地图）
└── references/
    ├── 01-weekly-life-os/   # 当日日记汇总（原 duoduo-day-dy）
    ├── 02-weekly-life-os.md # 日记转日历流水线（原 duoduo-diary-to-calendar-pipeline）
    ├── 03-weekly-life-os.md # 每日灵魂拷问（原 duoduo-soul-question）
    ├── 04-weekly-life-os/   # 语音日记采集（原 duoduo-voice-journal）
    ├── 05-weekly-life-os.md # 周复盘与下周日程（原 duoduo-weekly-review-calendar）
    ├── 06-weekly-life-os.md # 日记草稿 AI 精修（原 journal-review-refine）
    ├── 07-weekly-life-os.md # Life OS 月相周历（原 weekly-life-os-calendar）
```

## 子能力索引

| # | 能力 | 原 skill | 入口文件 |
|---|------|----------|----------|
| 01 | 当日日记汇总 | `duoduo-day-dy` | `references/01-day-diary/SKILL.md` |
| 02 | 日记转日历流水线 | `duoduo-diary-to-calendar-pipeline` | `references/02-diary-to-calendar.md` |
| 03 | 每日灵魂拷问 | `duoduo-soul-question` | `references/03-soul-question.md` |
| 04 | 语音日记采集 | `duoduo-voice-journal` | `references/04-voice-journal/SKILL.md` |
| 05 | 周复盘与下周日程 | `duoduo-weekly-review-calendar` | `references/05-weekly-review.md` |
| 06 | 日记草稿 AI 精修 | `journal-review-refine` | `references/06-journal-review-refine.md` |
| 07 | Life OS 月相周历 | `weekly-life-os-calendar` | `references/07-weekly-life-os.md` |

## 怎么用

- AI 接到请求 → 查 SKILL.md 路由表 → 只加载对应 `references/NN-*` 那一份，不一次塞爆上下文。
- 你要改某个场景的细节，只动对应那一份文件即可。

## 合并来源（已停用独立 skill）

- duoduo-day-dy（→ references/01-*）
- duoduo-diary-to-calendar-pipeline（→ references/02-*）
- duoduo-soul-question（→ references/03-*）
- duoduo-voice-journal（→ references/04-*）
- duoduo-weekly-review-calendar（→ references/05-*）
- journal-review-refine（→ references/06-*）
- weekly-life-os-calendar（→ references/07-*）
