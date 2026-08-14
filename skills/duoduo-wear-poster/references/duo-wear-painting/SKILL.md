---
name: duo-wear-painting
description: DUODUO WEAR 品牌插画生成与图文合成技能。用 AI 生成符合多多品牌 DNA 的「绘画风」插画（小红书图文笔记知识分享、口播类讲解笔记的视觉解释、公众号插画），套品牌排版合成社媒图文。触发词：插画、画一张、知识卡片、口播配图、讲解配图、公众号插画、小红书图文、generate illustration、brand illustration、explain with drawing。
agent_created: true
author: 多多 (DuoDuo)
license: 复用 duoduo-design-system 品牌 DNA（CC BY-NC-SA 4.0 改写版）
---

# DUO WEAR Painting — 品牌插画生成与图文合成

> 把 xiaolan-auto-edit 的 **broll 思路**（透明 cutout 插画 + 叠加层 + 卡拉OK式逐词字幕）与 **duoduo-video-edit / duoduo-design-system 的品牌与审美** 融合，
> 专做「知识分享 / 讲解解释 / 公众号」这一类**绘画风插画 + 图文合成**。
> 这是用户**明确授权**的 AI 生图场景（见 §红线关系）。

## 这个 skill 管什么 / 不管什么
- **管**：AI 生成的「绘画风 / 编辑插画」——
  ① 小红书图文笔记的知识分享图　② 口播类讲解笔记的视觉解释图　③ 公众号插画。
- **不管**：视频封面背景（仍必须用真实照片/真实帧，**禁 AI 生图**）、品牌实拍产品图、任何冒充实拍的 AI 图。

## 与两条红线的关系（重要，照此执行）
- **duoduo-video-edit 的「禁 AI 生图背景」红线仍然有效**，但**只限视频封面与品牌实拍图**。
- **本 skill 是那条红线的显式例外**：知识分享 / 讲解解释 / 公众号插画**允许 AI 绘画**（用户 2026-08-06 明确授权）。
- 但 **ImageGen 产出图必定带「图片由AI生成」水印**（参数压不掉）——本 skill **强制去水印**（硬切底 50px），见 §去水印铁律。绝不可交付带水印的图。

## 核心流程（4 步）
1. **Brief** — 向用户确认：要解释的概念 / 主题、用途（小红书 note / 口播配图 explain / 公众号 wechat）、风格（inkline 线描 / watercolor 水彩 / woodcut 版画 / flat 扁平）、是否要**透明 cutout**（用于叠加到口播视频）。
2. **生成插画** — 用 `scripts/build_prompt.py` 把「概念 + 风格锁」拼成完整 ImageGen prompt（含品牌 DNA 风格锁 + 负面词），然后调用 **ImageGen** 工具出图。
3. **去水印 + 合成** — 用 `scripts/compose_note.py`：自动裁底去水印 → 套品牌 40px 线描边框 + 母题角标 + 衬线标题 + DUODUO WEAR lockup → 输出目标尺寸。
4. **交付** — 出 PNG。若选 cutout 模式则出**透明 PNG**，用户自行叠到口播视频（ffmpeg 叠加见 references/composition_specs.md）。

## 品牌插画风格锁（必读 references/style_prompt.md）
- **绘画风**：editorial illustration / watercolor / ink-line / woodcut，**绝不像照片、绝不像 3D 渲染、绝不像 AI stock**。
- **配色锁**：蓝绿 `#00B6C5`/`#0FA3B8`/`#1A9AA8` + 米 `#F1E9DA`/`#E8DCC8` 为主，赭金 `#C9902E` ≤10% 点睛，陶土红 `#B5543A` 点缀；**绝不用蓝紫渐变 / neon / 纯黑白大面积**。
- **母题**：太阳 / 月亮 / 曼陀罗 / 海浪 / 植物藤蔓 / 女人×动物 single-line 等灵性·自然·部落线描（详见 duoduo-design-system `brand-dna.md` §第四审美轴）。
- **字体**（合成时叠加的标题）：全衬线——英文 Baskerville 栈、中文思源宋体 / 系统宋体。
- **气质**：野而温柔、手作而有世界、**不像 AI**。

## 合成规格（必读 references/composition_specs.md）
- 小红书图文：`1080×1440`（3:4），米底，40px 线描边框，底部 50px 留白去过水印。
- 公众号封面：`900×383`（2.35:1）或 `1080×1440`；内文插画 1080 宽自适应。
- 口播讲解配图：`16:9`（1280×720）或 `1:1`（1080×1080）。
- cutout 透明 PNG：原分辨率去背，供 ffmpeg 叠加。

## 工具路由（HyperFrames vs ffmpeg 结论）
- **插画生成**：ImageGen 工具（本环境）。Codex imagegen 为等价外部备选（需 API key）。
- **合成 / 去水印**：PIL（default venv）。
- **视频叠加**（仅 cutout 模式）：`ffmpeg`（`/Users/Zhuanz/.local/bin/ffmpeg`），透明 PNG 用 `overlay` 滤镜；**不引入 HyperFrames**。
- **HyperFrames vs ffmpeg（已评估，结论）**：本 skill **不依赖 HyperFrames**。ffmpeg 已覆盖去背叠加 / 裁剪 / 序列帧；HyperFrames 是代码驱动 motion-graphics 引擎（关键帧动画 / Lottie / 参数化场景），**仅在「把插画做成关键帧动画 b-roll」时才需要**，与「ffmpeg-only / 无重型 GUI」约束冲突，留作**未来可选**，不在本 skill 默认栈内。

## 铁律（P0 必过）
1. **去水印是强制步骤，不可跳过**（红线：永远不要有「图片由AI生成」）。
2. 3:4 卡片**禁深色底**（必须米 `#F1E9DA`/`#E8DCC8`）。
3. 外框统一 **40px** 单色线描，不得更细。
4. 每张图**至少 1 个明确母题**（太阳 / 浪 / 曼陀罗 / 图腾之一），符号有意义。
5. **绝不用 AI 图冒充实拍 / 视频封面**。
6. 输出前自检：截图像不像 AI 模板？一眼认不认得出是多多（蓝绿+米+线描母题+全衬线）？

## 与 duoduo-design-system / duoduo-video-edit 的分工
- **duoduo-design-system**：HTML 网页 / 长页 / 社媒卡前端（含去水印 HTML 法）。
- **duoduo-video-edit**：视频成片 / 封面（真实照片，禁 AI 生图）。
- **duo-wear-painting（本 skill）**：AI 绘画插画 + 静态图文合成，补齐「知识分享 / 讲解 / 公众号插画」这一块。

## 交付前自检清单
- [ ] 插画已去水印（底 50px 裁掉，无「图片由AI生成」字样）
- [ ] 配色在品牌 DNA 内（蓝绿+米为主，无蓝紫/neon）
- [ ] 有 ≥1 个线描母题（太阳/浪/曼陀罗/图腾）
- [ ] 标题全衬线（Baskerville / 思源宋体）
- [ ] 边框 40px、底部 50px 留白（note 模式）
- [ ] 未用于视频封面 / 未冒充实拍
