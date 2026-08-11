# duoduo-skills 技能库总览

> 更新：2026-08-11 · 共 35 个技能 · 权威源：Mac `~/.workbuddy/skills/`

## daily-diary-skill
- 文件数：2
- 用途：每日语音日记整理——将用户当天的语音和文字碎片忠实保存为结构化个人日记。当用户说"记一下"、"今天想法"、"今日日记"、"今天发生了"、"把今天的事记下来"、"整理日记"等表达记录当天生活意图时触发。每天首次对话时自动检测是否需要整理前一天日记。不适用于：纯知识问答、学习讨论、报告分析等非日记记录场

## duo_longpic-gen
- 文件数：13
- 用途：将中文公众号长文转化为 DUODUO 风格的高质感公众号长图：海洋背景、棉麻手工纸拼贴、编辑式层级、真实照片、航海符号与双语点缀。支持 2 张等宽长图、全文版或编辑摘要版，并要求将文字通过 HTML/SVG/Canvas/Pillow 精确排版，而不是让图片模型直接生成文字。

## duoduo-approval-detect-and-release
- 文件数：1
- 用途：> Detect 多多's == == highlight approvals in Obsidian and drive the downstream release: move approved pending-review files into archive/ (task-type ones

## duoduo-caldav-calendar-write
- 文件数：1
- 用途：> Reinforced iCloud Calendar writer via CalDAV for this macOS sandbox. Use it whenever a task must CREATE, UPDATE, or DELETE events in 多多's iCloud cal

## duoduo-company-daily-os
- 文件数：1
- 用途：> The 多多个人公司 daily 13:00 Chief-of-Staff routine: aggregate the three employees' (content-ops / researcher / product-manager) prior-day output, produce

## duoduo-company-night-patrol
- 文件数：1
- 用途：> The 多多个人公司 23:00 night patrol: re-sweep the day's tasks for loose ends, then run the once-daily archive triage + pending-review emoji flag (merged f

## duoduo-design-system
- 文件数：14
- 用途：多多的个人品牌设计系统。做 HTML 页面、个人网站、知识库页、产品页、纹身/首饰/服装实验页、社媒图文等任何前端设计时自动触发。包含品牌 DNA（蓝绿+米、全衬线、纹身/灵性/部落母题）和多个场景子规范。限制 AI 自由度 = 质量。

## duoduo-diary-to-calendar-pipeline
- 文件数：1
- 用途：> Daily pipeline that pulls 多多's IMA journal, exports it to Obsidian, extracts todos, and writes them to iCloud Calendar via CalDAV. Use it for the 13

## duoduo-expert-hourly-patrol
- 文件数：1
- 用途：> The hourly self-pickup mechanism for 多多's three WorkBuddy expert employees (content-ops / researcher / product-manager). Each expert polls its own f

## duoduo-github-sync
- 文件数：3
- 用途：> 把多多的 duoduo-* 工作流技能（及主目录 catalog / manifest）备份到她的 GitHub 仓库 faifaida/duoduo-skills。触发词：「同步技能到 GitHub / 备份 skill / github sync」， 或任一批量改完技能后想留底。默认按需（无

## duoduo-netease-transcript
- 文件数：1
- 用途：> On-demand transcript sync for 曲曲 (NetEase/网易) recordings. When 多多 asks to transcribe (or after a new recording is ready), pull the latest transcript

## duoduo-podcast-build
- 文件数：1
- 用途：把《多多的未完成实验》这类「双人 Deep Dive 播客」从带 Speaker 标签的 TTS 安全脚本，自动生成成片音频（MP3+WAV）+ 质检报告。路线 = ElevenLabs API（多多本人克隆声 + 固定搭档声）。当用户说"做播客/出 EP/把脚本生成音频/今晚发播客"且已有 TTS

## duoduo-podcast-sync
- 文件数：7
- 用途：播客「多多的未完成实验」跨平台同步技能。当多多说"启动播客同步 / 同步播客 / 跑一下播客同步"时调用。把小宇宙的新单集同步到 Apple Podcasts（GitHub Pages RSS）和喜马拉雅（专辑 127170840）。只在被明确要求"启动"时运行，不自动定时。后台 headless 

## duoduo-soul-question
- 文件数：1
- 用途：> 多多个人公司「研究学习官」的每日灵魂拷问仪式。每天下午 13:00 主动给多多提出一个、且只有一个 与她当下真实生活有关的「灵魂问题」——不是心灵鸡汤打卡，而是让她带着一个真问题进入这一天， 在生活/工作/身体/选择里慢慢观察答案。问题基于多多最近的日记、项目、情绪、身体状态、个人公司 与理财实

## duoduo-video-edit
- 文件数：1
- 用途：多多个人 IP 号视频制作——基于 capcut-cli 的剪映草稿自动化流水线（竖屏 9:16）。覆盖：本地工具链部署（ffmpeg/ffprobe/capcut-cli）、素材方向探测、从零建草稿、加视频/字幕/标题、横拍自动裁 9:16、代理预览、导出给用户在剪映渲染。当用户要做抖音/小红书竖

## duoduo-voice-clone
- 文件数：2
- 用途：多多声音克隆 + 播客/视频配音生成。输入一段参考音频（多多本人声纹），用开源方案（OpenVoice v2 零样本 / GPT-SoVITS v2Pro 微调）克隆声音，批量生成带 Speaker 标签的 TTS 脚本为克隆音频，拼接后期出片。MIT 协议、本地/自托管、免费可控。

## duoduo-voice-deai
- 文件数：3
- 用途：> 多多内容「去 AI 味 + 原声重写」专用 SOP，覆盖所有对外文案。当用户要求改写/润色/生成 多多的公开发文（小红书/即刻/知识星球/朋友圈/X/Threads/Medium/Substack 等文字，以及 视频口播稿/脚本/分镜文案），或说「去 AI 味 / 太 AI 了 / 改得说人话 

## duoduo-wechat-chat-export
- 文件数：1
- 用途：> Export selected WeChat conversations from the local macOS WeChat sandbox data into Obsidian as dated, searchable Markdown. Use it when 多多 asks to ex

## duoduo-wechat-publish
- 文件数：5

## duoduo-weekly-review-calendar
- 文件数：1
- 用途：> 多多的每周一 13:00 周复盘 + 下周日程仪式。复盘「上周一→周日」的日记（直接从 Obsidian 07_Journals/01 Daily 调取），以多多的周报格式产出一份日记周报 + 六维下周计划；按 email-to-calendar 的「先提取→提问对齐→确认后再写」模式，问她固定

## duoduo-weread-digest
- 文件数：1
- 用途：> Weekly WeChat-Reading (微信读书) digest for the researcher employee (资料员): every Tuesday 09:00, pull 多多's highlights from WeChat Reading via the weread-

## duoduo-xhs-weekly-digest
- 文件数：1
- 用途：> Weekly Xiaohongshu (小红书) album digest for the content-ops employee (内容运营): every Tuesday 07:00, grab the new notes added to 多多's saved XHS albums an

## qu-ai-wei
- 文件数：89
- 用途：| 去除简体中文文本里的 AI 写作痕迹,不虚构事实,让终稿干净、精准。 触发:显式 `/qu-ai-wei`,或用户说「去 AI 味 / 改得说人话 / humanize 中文 / 改自然点 / 读着别扭 / 太生硬了」时自动调用。 约束:按「冲突仲裁顺序」六级执行;终稿强制附打磨报告。 范围:只

## duo-podcast-workbuddy
- 文件数：1
- 用途：WorkBuddy 平台播客生产权威标准（EP11 v4b 验证）。生成/修复/混音/质检多多中文双声线 AI 播客：克隆多多声线（A）、固定男声 co-host（CustomVoice voice="dylan"）、插入片头片尾/SFX、诊断定点音频缺陷、导出可发布 MP3。与 codex 的 duo-podcast 是独立分支（男声 dylan / A 清脆 / 禁用 time_stretch 与 temp0），不可互套参数。

## shifei-video-edit
- 文件数：8
- 用途：剪辑多多的世斐（Shifei）非虚构旅行、人物、现场事件与 Sri Lanka Field Notes 视频。用于人物采访、旅行档案、对谈、现场事件、旁白+B-roll、字幕校对、声音修复、调色、概念卡、封面和交付；当用户要求"世斐""这个人让我看懂了这里""People of Sri Lanka""Field Notes"或复刻世斐人物对谈时必须使用。

## gmail-imap-cleanup
- 文件数：1
- 用途：用 Gmail App Password 走 IMAP 批量清理邮箱（改标签/移动/删除上千封），规避 modified-UTF-7 编码坑与 Gmail 限流 BAD 响应。

## journal-review-refine
- 文件数：1
- 用途：把 Obsidian 批量生成的「月度/周/年复盘」占位符草稿，升级为有洞察的 AI 精修版（预处理→并行子代理精修→YAML/占位符校验）。

## notion-journal-split
- 文件数：1
- 用途：把 Notion 按月聚合的日记页，按正文 M/D 日期拆成独立 Obsidian daily note。

## reel-grid-pitfalls
- 文件数：1
- 用途：固定时长网格短视频 reels 的 5 个实战坑（慢动作补长/字幕按 VO 重定时/程序化校验音画同步/品牌 outro 约定）。

