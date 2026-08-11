# DUO Podcast Studio（录制剪辑 + 跨平台分发同步）

合并型技能，目录结构：

```
duo-podcast-studio/
├── SKILL.md            # 路由器：合并所有触发词 + 下方索引表
├── README.md           # 本文件（人话地图）
└── references/
    ├── 01-podcast-sync.md # 录制剪辑与质检（原 duo-podcast-workbuddy）
    ├── 02-podcast-sync/   # 跨平台分发同步（原 duoduo-podcast-sync）
```

## 子能力索引

| # | 能力 | 原 skill | 入口文件 |
|---|------|----------|----------|
| 01 | 录制剪辑与质检 | `duo-podcast-workbuddy` | `references/01-podcast-workbuddy.md` |
| 02 | 跨平台分发同步 | `duoduo-podcast-sync` | `references/02-podcast-sync/SKILL.md` |

## 怎么用

- AI 接到请求 → 查 SKILL.md 路由表 → 只加载对应 `references/NN-*` 那一份，不一次塞爆上下文。
- 你要改某个场景的细节，只动对应那一份文件即可。

## 合并来源（已停用独立 skill）

- duo-podcast-workbuddy（→ references/01-*）
- duoduo-podcast-sync（→ references/02-*）
