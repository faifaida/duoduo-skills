# DUODUO Skills Catalog

> 共 18 个技能（design-system 已移出，改为独立仓 faifaida/duoduo-design-system 为唯一真源）。生成于 2026-08-12T01:40:00 UTC。

## 合并型技能（consolidated）

### duo-company
- 文件数: 5
- 说明: 多多个人公司运营节律：每日 13:00 参谋长聚合、23:00 夜巡归档、三专家每小时自取机制。 本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。

### duo-knowledge-classify
- 文件数: 96
- 说明: 多多个人公司碎片知识统一加工系统：小红书/微信读书/微信聊天/云盘归档采集分类，并扩展接入日历写入、微信读书周摘要、小红书周摘要、Gmail 清理、Notion 日记拆分。 本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。

### duo-life-tasks
- 文件数: 12
- 说明: 多多个人生活操作系统：当日日记汇总、日记转日历、每日灵魂拷问、语音日记采集、周复盘、草稿 AI 精修、月相周历整合。 本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。

### duo-podcast-studio
- 文件数: 10
- 说明: 多多中文 AI 对话播客「未完成实验」一站式技能：从单集制作/修复/混音/质检，到把小宇宙新单集同步到 Apple Podcasts 与喜马拉雅。 本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。

### duo-voice-deai
- 文件数: 95
- 说明: 多多对外文案去 AI 味 + 原声重写总入口：覆盖所有平台公开发文与口播稿，并扩展接入简体中文专用去 AI 痕迹（qu-ai-wei）。 本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。

### duo-video-script
- 文件数: 1
- 说明: （从 workbuddy-skills 并入）视频脚本生成技能。

### duo-wear-painting
- 文件数: 6
- 说明: 

### duo-wechat
- 文件数: 21
- 说明: 微信公众号相关一站式技能：把长文生成 DUODUO 风格长图、自动发布长图到公众号后台、把微信聊天记录导出到 Obsidian。 本 skill 由多个相关子能力合并而成，触发时按下方索引表加载对应子模块，避免一次性载入全部内容。

### duoduo-approval-detect-and-release
- 文件数: 1
- 说明: 

### duoduo-github-sync
- 文件数: 3
- 说明: 

### duoduo-netease-transcript
- 文件数: 1
- 说明: 

### duoduo-video-edit
- 文件数: 12
- 说明: 

### duoduowear-illustrations
- 文件数: 9
- 说明: （从 workbuddy-skills 并入）DUODUO WEAR 品牌插画/素材生成技能。

### ffmpeg-libass-drift-drawtext
- 文件数: 1
- 说明: 

### grill-me-plus__skillhub
- 文件数: 4
- 说明: 

### reel-grid-pitfalls
- 文件数: 1
- 说明: 

### shifei-video-edit
- 文件数: 9
- 说明: 

### visual-understanding-toolkit
- 文件数: 3
- 说明: 

## 新增（Windows 侧 codex 视频剪辑技能，2026-08-15 推）

### jianying-editor
- 说明: 剪映 (JianYing) AI自动化剪辑的高级封装 API (JyWrapper)，提供开箱即用的 Python 接口，支持录屏、素材导入、字幕生成、Web 动效合成及项目导出。全面适配 MacOS (Apple Silicon/Intel) 与 Windows，支持 v5.9+ (draft_info.json) 架构、工程自修复、智能配音字幕及录屏变焦。
- 来源: Windows 本地 `.codex/skills/` 推入（按本地推）

### openchatcut
- 说明: Connect an MCP-capable coding agent to OpenChatCut and edit local video projects. Use when the user asks to install, connect, or set up OpenChatCut; inspect or edit an OpenChatCut project; work with its timeline, transcript, captions, media, generation, motion graphics, audio, color, or export tools; or recover from an OpenChatCut MCP error.
- 来源: Windows 本地 `.codex/skills/` 推入（按本地推）

### os-video-edit-gpt
- 说明: Direct and edit Duoduo OS personal-account nonfiction videos, especially the 回家接班实验 series. Use for A-roll cleanup, transcript-led story editing, HTML/shot-list execution, B-roll selection, OpenChatCut or FFmpeg timelines, captions, keyword typography, documentary sound, warm color, cover design, QC, and release packages containing the video, cover, title, and publishing copy.
- 来源: Windows 本地 `.codex/skills/` 推入（按本地推）

### skw-video-editorial
- 说明: Design story-led audiovisual briefs, case films, demo reels, institutional videos, event aftermovies, employer-branding pieces, image-bank productions, sales campaigns, and recurring performance bulletins. Use when an agent must define the business outcome, audience transformation, narrative beats, decupagem, footage-selection criteria, edit rhythm, lettering, sound design, continuity, or a Palmier Pro assembly plan.
- 来源: Windows 本地 `.codex/skills/` 推入（按本地推）

### xiaolan-aroll
- 说明: 自动剪辑「小蓝」式口播 A-roll（口播原片）视频：去掉静音/停顿，剪掉口头喊 「卡 / cut」标记的废 take，去掉重复的 retake（保留更干净的那条），然后把剪好的视频 渲染（RENDER）回来——音画同步。输入是未剪辑的 A-roll 视频（音频是检测信号）加一份 参考脚本（SCRIPT，判断保留哪条 take、修 whisper 同音字错误的 ground truth）。 输出是收紧后的粗剪视频，后续进 CapCut 精修。全自动（FULL AUTO，所有剪切直接应用）， 但一定输出一份 keep/cut 的 EDL 日志供扫查。触发场景："edit my a-roll"、 "cut my talking head"、"remove the pauses and retakes"、"clean up my recording"、 "去掉停顿和重复/废话"、"口播剪辑"、"cut where I said 卡"、"give me the edited video"。 这是内容流水线的前半段——先把口播剪干净；`xiaolan-broll` 再往上叠 b-roll + 卡拉OK字幕。不管 b-roll/字幕（用 `xiaolan-broll`），不管开场 hook （用 `xiaolan-hook-broll`，未包含在本仓库）。
- 来源: Windows 本地 `.codex/skills/` 推入（按本地推）

### xiaolan-broll
- 说明: 把一条完整长度的小蓝口播视频做成品牌锁定的 b-roll（配图动画层）+ 逐词弹出卡拉OK字幕层，以透明叠加层（带 alpha 的 ProRes MOV）交付， 由小蓝自己叠在她的高清 A-roll 上——A-roll 永远不烧进成片。 适用于 cream（奶油底）+ cutout（绿幕抠像素材）的 9:16 竖屏： 人物坐在画面中下方，上半屏是空的。产出 object-first 的 b-roll （每个叙事节拍一个具体的动画物件，循环 glyph 母题）、锁 VO 的逐词弹出卡拉OK （当前词 Klein blue（克莱因蓝）+ 薄荷绿下划线），johnbucog 巨字主角处理只留给金句。 触发场景："make b-roll and karaoke captions for this video / a-roll"、 "整条视频的 b-roll 和字幕"、"口播配图"、"full b-roll"、 "动图 + 字幕 for my talking head"、"transparent overlay I'll composite myself"， 或给一整条小蓝讲解视频加/重做图形+字幕。 覆盖 VO 转写、头顶测量、分段/金句规划、卡拉OK引擎、object-first 场景搭建、 自检、透明 MOV 渲染和交付。 不适用于：字幕直接烧在片段上的短 hook/开场（用 `xiaolan-hook-broll`， 未包含在本仓库），也不适用于人物在右下角的口播（用 `shorts-hyperframe`， 未包含在本仓库）。
- 来源: Windows 本地 `.codex/skills/` 推入（按本地推）

