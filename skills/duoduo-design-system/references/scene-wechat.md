# 场景：公众号排版 / 做分发

> 给微信公众号文章的 HTML 排版（或导入编辑器的富文本）。约束：公众号容器**不支持外部 CSS 文件、不支持 `<style>` 全局、JS 受限**，样式必须**内联**或用平台自带样式块。
> 模板：从 `assets/template-landing.html` 改造，把所有样式改为 `style="..."` 内联；或参考本文件结构手写。

## 结构
- **封面**：单独 900×383 或 1080×1440 图（走 `scene-cards.md` 的 3:4 规范，去过水印）。
- **开头导语**：思源宋体，字号 16~17px，行高 1.9，首行不缩进或缩进 2em（统一）。
- **小标题**：用 `#2 Section Header` 思路 — 序号 + 标题，Baskerville 数字 + 思源宋体，下方 40px 母题分隔线（线描 SVG 或 border-bottom 单色）。
- **正文重点**：用 `#50 Text Highlighter`（荧光笔/波浪线）标重点，**不是**引用块。
- **金句/引用**：用 `#3 Key Insight` / `#6 Pull Quote` — 自带装饰引号，内联实现（`border:none` + `::before` 引号无法内联时用 `<span>❝</span>` 模拟）。
- **结尾**：母题水印 + 手写体引导关注。

## 内联要点
- 颜色用 `brand-dna.md` 实际取值（teal `#00b6c5`、gold `#c99a3f`、ink `#25262b`、linen `#f1e9da`）。
- 段落 `style="font-family:'Noto Serif SC',serif;font-size:16px;line-height:1.9;color:#25262b;"`。
- 不依赖 Google Fonts（公众号环境无），中文走系统宋体栈。
- 图片全部走图床/CDN，且**去过 AI 水印**。

## 禁止
- 默认 `<blockquote>` 左竖线、无样式列表、默认表格。
- 深色大块、渐变文字、glassmorphism。
- 带水印的 AI 图。
