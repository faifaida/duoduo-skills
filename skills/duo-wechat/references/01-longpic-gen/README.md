# duo_longpic-gen

一个面向任意 AI Agent / Coding Agent / Design Agent 的公众号长图生成 Skill。

## 文件结构

```text
duo_longpic-gen/
├── SKILL.md                       # 主技能规范，Agent 首先读取
├── README.md                      # 使用说明
├── references/
│   ├── visual-dna.md              # 色彩、材料和图像规则
│   ├── layout-recipes.md          # 可复用版式配方
│   └── production-pipeline.md     # 稳定生产流程
├── templates/
│   ├── input-brief.md             # 用户输入模板
│   ├── storyboard.yaml            # 视觉脚本模板
│   └── design-tokens.json         # 机器可读视觉 Token
├── checklists/
│   └── QA.md                      # 发布前检查
├── examples/
│   ├── example-brief.md           # 示例输入
│   └── example-storyboard.yaml    # 示例视觉脚本
└── assets/
    ├── reference_part_01.png
    └── reference_part_02.png
```

## 最快用法

让 Agent 先读取 `SKILL.md`，再提供文章与图片素材。

关键要求：

> 图片模型只生成无字底稿；中文必须用 HTML/SVG/Canvas/Pillow/Figma 精确排版。

## 推荐制作链路

1. LLM 编辑文章并生成 Storyboard。
2. 图片模型生成海洋、纸张和照片氛围底稿。
3. HTML/CSS 或 SVG 排版所有文字。
4. Playwright/浏览器截图导出 1080×1890 PNG。
5. 按 QA 清单检查后交付。

## 兼容性

- ChatGPT / Codex
- Claude / Claude Code
- Gemini
- Cursor
- WorkBuddy
- 任何可读取 Markdown 并调用图片或代码工具的 Agent

字体文件不包含在包中。Agent 应使用本地合法可用字体。
