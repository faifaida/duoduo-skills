# duoduo-* 技能总览（同步清单）

> 生成时间：2026-07-26T06:23:35  |  目标仓库：`faifaida/duoduo-skills` (main)  |  当前可见性：**public（待改为 private）**

> 共 **14** 个 duoduo-* 技能，合计 **21** 个文件 / **106 KB**。同步仅白名单，绝不推送凭证/配置/密码。


| # | 技能 | 用途 | 文件数 | 大小 |
|---|------|------|------:|-----:|
| 1 | `duoduo-approval-detect-and-release` | 检测 Obsidian 里多多的 == == 高亮批复，驱动下游释放：把已批复的待审文件移入 archive/（任务类），更新已审放行清单供员工自取。 | 1 | 2 KB |
| 2 | `duoduo-caldav-calendar-write` | macOS 沙箱下经 CalDAV 可靠读写 iCloud 日历（osascript/EventKit 在此环境走不通），支持事件 CREATE/UPDATE/DELETE。 | 1 | 4 KB |
| 3 | `duoduo-company-daily-os` | 个人公司每日 13:00 总办简报：汇总三名员工(内容运营/资料员/产品经理)前一日产出，生成简报+验收+次日任务+待审标记+下发。 | 1 | 3 KB |
| 4 | `duoduo-company-night-patrol` | 个人公司 23:00 夜巡：重扫当日任务留尾，跑每日 archive 归档 + 待审 emoji 标记(❗️>1天 / ‼️>2天)。 | 1 | 2 KB |
| 5 | `duoduo-design-system` | 多多个人品牌设计系统（蓝绿+米、全衬线、纹身/灵性/部落母题），任何前端/社媒/产品页设计自动触发。 | 8 | 50 KB |
| 6 | `duoduo-diary-to-calendar-pipeline` | 每日 13:00 拉取 IMA 日记→导出 Obsidian→抽取 todo→经 CalDAV 写入 iCloud 日历。 | 1 | 2 KB |
| 7 | `duoduo-expert-hourly-patrol` | 三名员工(内容运营/资料员/产品经理)每小时 10:00–23:00 自取机制：轮询自身文件夹指令+已审放行清单，自取执行并标记 done 防重复。 | 1 | 2 KB |
| 8 | `duoduo-github-sync` | 把 duoduo-* 技能库 + 总览备份到 GitHub 仓库 faifaida/duoduo-skills（按需）。 | 1 | 3 KB |
| 9 | `duoduo-netease-transcript` | 曲曲(网易)录音转录按需同步：拉取最新转录稿到 Obsidian/02_内容运营。 | 1 | 1 KB |
| 10 | `duoduo-voice-deai` | 多多内容「去 AI 味 + 原声重写」SOP：小红书/即刻/知识星球/朋友圈/X/Threads 等公开发文改写。 | 1 | 15 KB |
| 11 | `duoduo-wechat-chat-export` | 把指定微信会话从本机 macOS 微信沙盒导出为 Obsidian 带日期、可搜索的 Markdown。 | 1 | 2 KB |
| 12 | `duoduo-weekly-review-calendar` | 每周一 13:00 周复盘：总结上周一至周日日记→以多多周报格式产出→问 6 个固定问题对齐下周→写入系统日历(用已有标签颜色)。 | 1 | 11 KB |
| 13 | `duoduo-weread-digest` | 资料员每周二 09:00 微信读书划线摘要：拉取多多划线→Obsidian/03_资料员。 | 1 | 2 KB |
| 14 | `duoduo-xhs-weekly-digest` | 内容运营每周二 07:00 小红书收藏专辑新增摘要：抓指定专辑上周新增→Obsidian/02_内容运营。 | 1 | 2 KB |

## 每个技能的文件清单


### duoduo-approval-detect-and-release

- `SKILL.md` — 2145 B  (sha256:a2dcb25eae6d5469)

### duoduo-caldav-calendar-write

- `SKILL.md` — 5113 B  (sha256:802f24adbfb36784)

### duoduo-company-daily-os

- `SKILL.md` — 3659 B  (sha256:f37b0955877279bd)

### duoduo-company-night-patrol

- `SKILL.md` — 2798 B  (sha256:e1c327551b9c9673)

### duoduo-design-system

- `brand-dna.md` — 11337 B  (sha256:0e8a02f17785cc03)
- `SKILL.md` — 4528 B  (sha256:34c93d0aabe26c2a)
- `references/components.md` — 7190 B  (sha256:270b331e7c62982c)
- `references/layouts.md` — 5691 B  (sha256:4577d3e1fdaad5b3)
- `references/checklist.md` — 1551 B  (sha256:47bbe8065c55807c)
- `assets/template-brand.html` — 2678 B  (sha256:94cbe7fa193cc88e)
- `assets/template-landing.html` — 14315 B  (sha256:2b5330814d0b01cd)
- `assets/motifs.svg` — 3973 B  (sha256:06683b1c4d2f745c)

### duoduo-diary-to-calendar-pipeline

- `SKILL.md` — 2962 B  (sha256:36b38bd0dbc18e4d)

### duoduo-expert-hourly-patrol

- `SKILL.md` — 3053 B  (sha256:2885dd022f064050)

### duoduo-github-sync

- `SKILL.md` — 3339 B  (sha256:da1617db5672b250)

### duoduo-netease-transcript

- `SKILL.md` — 1749 B  (sha256:e3727ea06799502a)

### duoduo-voice-deai

- `SKILL.md` — 15455 B  (sha256:570ca92bf14dc98b)

### duoduo-wechat-chat-export

- `SKILL.md` — 2172 B  (sha256:e32a71fc803a6c43)

### duoduo-weekly-review-calendar

- `SKILL.md` — 11308 B  (sha256:08cf693ba09b57df)

### duoduo-weread-digest

- `SKILL.md` — 2077 B  (sha256:04773e680177dc7e)

### duoduo-xhs-weekly-digest

- `SKILL.md` — 2143 B  (sha256:c327f1c9a60e8d56)