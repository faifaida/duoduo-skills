# DUO WeChat（公众号长图生成 + 长图发布 + 聊天导出）

合并型技能，目录结构：

```
duo-wechat/
├── SKILL.md            # 路由器：合并所有触发词 + 下方索引表
├── README.md           # 本文件（人话地图）
└── references/
    ├── 01-wechat-chat-export/   # 公众号长图生成（原 duo_longpic-gen）
    ├── 02-wechat-chat-export/   # 公众号长图发布（原 duoduo-wechat-publish）
    ├── 03-wechat-chat-export.md # 微信聊天导出（原 duoduo-wechat-chat-export）
```

## 子能力索引

| # | 能力 | 原 skill | 入口文件 |
|---|------|----------|----------|
| 01 | 公众号长图生成 | `duo_longpic-gen` | `references/01-longpic-gen/SKILL.md` |
| 02 | 公众号长图发布 | `duoduo-wechat-publish` | `references/02-wechat-publish/SKILL.md` |
| 03 | 微信聊天导出 | `duoduo-wechat-chat-export` | `references/03-wechat-chat-export.md` |

## 怎么用

- AI 接到请求 → 查 SKILL.md 路由表 → 只加载对应 `references/NN-*` 那一份，不一次塞爆上下文。
- 你要改某个场景的细节，只动对应那一份文件即可。

## 合并来源（已停用独立 skill）

- duo_longpic-gen（→ references/01-*）
- duoduo-wechat-publish（→ references/02-*）
- duoduo-wechat-chat-export（→ references/03-*）
