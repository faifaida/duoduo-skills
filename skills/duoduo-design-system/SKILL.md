---
name: duoduo-design-system
description: 多多的个人品牌设计系统。做 HTML 页面、个人网站、知识库页、产品页、纹身/首饰/服装实验页、社媒图文等任何前端设计时自动触发。包含品牌 DNA（蓝绿+米、全衬线、纹身/灵性/部落母题）和多个场景子规范。限制 AI 自由度 = 质量。
agent_created: true
author: 多多 (DuoDuo)
license: 改写自 esthersjw/esther-design-system（CC BY-NC-SA 4.0），内容已完全重写为多多品牌
repo: ~
---

# 多多 Design Skill

触发条件：当用户要求制作 HTML 网页、个人网站、知识库页、产品介绍页、landing page、活动页、纹身/首饰/服装实验页、作品集、社媒图文（小红书/公众号）等任何前端设计任务时触发。

## 使用方式（7 步工作流）

### Step 1: 澄清需求
向用户确认 5 个问题：
1. **类型** — 个人网站/品牌主页？知识库页？产品页？活动页/Landing？实验页（纹身/首饰/服装）？**图文卡片？** **公众号排版？**
2. **受众** — 给谁看的？
3. **Section 数** — 大概几屏内容？
4. **素材** — 有哪些文案/图片/数据？标志性图形/头像有吗？
5. **硬约束** — 必须包含什么？有没有要强调的母题（太阳/曼陀罗/图腾/女人×狮）？

### Step 2: 读规范
1. **必读** `brand-dna.md` — 确认品牌底层规范（token、字体、禁忌、**纹身/灵性/部落母题库**）
2. 根据类型选读场景文件：
   - 个人网站/品牌主页/知识库页 → `references/scene-landing.md`（主页型通用）
   - 产品介绍/活动页/Landing → `references/scene-landing.md`
   - App 型/功能型（看板/书架/Canvas） → `references/scene-app.md`
   - **图文卡片/小红书图文/文章转卡片** → `references/scene-cards.md`
   - **公众号排版/做分发** → `references/scene-wechat.md`
   - 教程型/介绍型/科普型 → `references/scene-tutorial.md`

### Step 3: 拷模板
从 `assets/` 选择对应模板作为起点（不存在的模板用 landing 改造）：
- 个人网站/品牌主页/产品页 → `assets/template-landing.html`
- 图文卡片/小红书/闲鱼 → `assets/template-cards.html`（3:4 社媒卡）
- App 型/教程型/公众号 → 从 `assets/template-landing.html` 起步，按 `scene-*.md` 改造（暂无独立模板）

**从模板开始改，不从零写。** 模板已内置 `:root` 变量与母题 SVG。

### Step 4: 选布局组合
从 `references/layouts.md` 中选取 3~5 种布局模式，为每个 section 分配不同布局。
**每个 section 布局必须不同。** 纹身/灵性/部落母题按 `brand-dna.md` 的"母题调用规则"嵌入对应布局。

### Step 5: 选组件填充
从 `references/components.md` 中选取组件填入各 section。
**硬规则：禁止使用任何 HTML 默认样式。** 所有引用块、列表、表格、卡片必须从 `components.md` 选用。绝不用默认 `<blockquote>`、默认 `border-left` 引用、无样式 `<ul>/<ol>`、默认 `<table>`。

### Step 6: 自检
对照 `references/checklist.md` 逐条检查：
- **P0 必须全过** — 任何一条不过就要改
- P1 应过 — 尽量满足
- P2 加分 — 锦上添花
额外核对：是否每个分区都有明确母题？灵性符号是否有意义？

### Step 7: 交付
输出最终 HTML 文件，确保可直接在浏览器打开；并确认母题、token、字体全部来自 `brand-dna.md`。

## 场景类型速查

| 类型 | 场景文件 | 模板 |
|------|----------|------|
| 个人网站/品牌主页/知识库页 | `references/scene-landing.md` | `assets/template-landing.html` |
| 产品介绍/活动页/Landing | `references/scene-landing.md` | `assets/template-landing.html` |
| 图文卡片/小红书图文/闲鱼图 | `references/scene-cards.md` | `assets/template-cards.html` |
| 公众号排版 | `references/scene-wechat.md` | 从 `template-landing.html` 改造（公众号需内联样式，见 scene-wechat.md） |
| App 型/功能型 | `references/scene-app.md` | 从 `template-landing.html` 改造（App 暂无独立模板） |
| 教程型/介绍型/科普型 | `references/scene-tutorial.md` | 从 `template-landing.html` 改造（教程暂无独立模板） |

> 模板现状：`template-landing.html`、`template-cards.html` 已就绪；App/教程/公众号暂无专属模板，统一从 `template-landing.html` 起步按对应 scene 文件改造。

## 关键原则
- **从模板开始改，不从零写** — 模板已内置品牌变量、母题 SVG、基础结构
- **每个 section 布局必须不同** — 从 `layouts.md` 选不同模式
- **母题驱动** — 没有母题 = 没做设计；灵性符号要有意义（见 `brand-dna.md`）
- **做完必须跑 checklist** — P0 全过才能交付

## AI 生成图水印红线（硬规则，先看 brand-dna.md）

- 任何文生图工具（ImageGen 等）产出图**必带「图片由AI生成」水印**，参数压不掉。
- **禁止**交付/上线/发社媒带水印的图。这是用户红线：「永远不要有这几个字」。
- 去水印方法：硬切底部 50px + 品牌色渐变覆盖（主图场景→`#151a2e`，米底/卡片场景→`#f1e9da`）。详见 `brand-dna.md`「AI 生成图水印红线」。
- 生图 prompt 先声明「无文字/无水印/无签名」，再走硬切兜底。

## 禁忌（核心底线）
严格遵守 `brand-dna.md` 的禁忌清单。底线：截图发社媒不会被说"又是 AI 做的"；且能一眼认出是"多多"。
