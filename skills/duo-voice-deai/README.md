# DUO Voice De-AI（去 AI 味原声重写 + 中文去 AI 痕迹）

合并型技能，目录结构：

```
duo-voice-deai/
├── SKILL.md            # 路由器：合并所有触发词 + 下方索引表
├── README.md           # 本文件（人话地图）
└── references/
    ├── 01-qu-ai-wei/   # 去 AI 味原声重写（原 duoduo-voice-deai）
    ├── 02-qu-ai-wei/   # 简体中文去 AI 痕迹（原 qu-ai-wei）
```

## 子能力索引

| # | 能力 | 原 skill | 入口文件 |
|---|------|----------|----------|
| 01 | 去 AI 味原声重写 | `duoduo-voice-deai` | `references/01-voice-deai/SKILL.md` |
| 02 | 简体中文去 AI 痕迹 | `qu-ai-wei` | `references/02-qu-ai-wei/SKILL.md` |

## 怎么用

- AI 接到请求 → 查 SKILL.md 路由表 → 只加载对应 `references/NN-*` 那一份，不一次塞爆上下文。
- 你要改某个场景的细节，只动对应那一份文件即可。

## 合并来源（已停用独立 skill）

- duoduo-voice-deai（→ references/01-*）
- qu-ai-wei（→ references/02-*）
