# DUO Company Ops（每日参谋长 + 夜巡 + 专家巡检）

合并型技能，目录结构：

```
duo-company/
├── SKILL.md            # 路由器：合并所有触发词 + 下方索引表
├── README.md           # 本文件（人话地图）
└── references/
    ├── 01-expert-hourly-patrol.md # 每日参谋长例程（原 duoduo-company-daily-os）
    ├── 02-expert-hourly-patrol.md # 夜巡归档（原 duoduo-company-night-patrol）
    ├── 03-expert-hourly-patrol.md # 专家每小时自取（原 duoduo-expert-hourly-patrol）
```

## 子能力索引

| # | 能力 | 原 skill | 入口文件 |
|---|------|----------|----------|
| 01 | 每日参谋长例程 | `duoduo-company-daily-os` | `references/01-company-daily-os.md` |
| 02 | 夜巡归档 | `duoduo-company-night-patrol` | `references/02-company-night-patrol.md` |
| 03 | 专家每小时自取 | `duoduo-expert-hourly-patrol` | `references/03-expert-hourly-patrol.md` |

## 怎么用

- AI 接到请求 → 查 SKILL.md 路由表 → 只加载对应 `references/NN-*` 那一份，不一次塞爆上下文。
- 你要改某个场景的细节，只动对应那一份文件即可。

## 合并来源（已停用独立 skill）

- duoduo-company-daily-os（→ references/01-*）
- duoduo-company-night-patrol（→ references/02-*）
- duoduo-expert-hourly-patrol（→ references/03-*）
