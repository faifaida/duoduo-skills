# 组件库（多多版）

> 改写自 esther-design-system/components.md，结构沿用：**场景索引 + 编号组件 + 散点 CSS 变量 + 严格禁令**。
> 所有组件使用 `brand-dna.md` 的 token（`--teal/--sand/--clay/--ochre/--cream/--ink` 等）。换肤只改 `:root`，不改组件。
> 母题（太阳/月亮/曼陀罗/图腾/女人×狮）按 `brand-dna.md` 调用，作为线描 SVG 角标/水印。

---

## 📌 场景索引（推荐组件）

| 场景 | 推荐组件 |
|------|----------|
| Hero 首屏大标题 | #44 Sparkles Text、#47 Typing、#2 Section Header、#33 Dark Hero |
| 图片展示/头像 | #49 Pixel Image、#13 头像集群、#10 三列卡 |
| 正文重点标注 | #50 Text Highlighter、#3 Key Insight、#6 Pull Quote |
| 趣味/活动标题 | #51 Comic Text、#2 Section Header |
| 装饰/CTA | #52 Spinning Text、#18 CTA 按钮、#46 Cool Mode |
| 卡片类 | #1 卡片库、#10 三列卡、#34 编号卡网格、#32 悬停揭示卡 |
| 引用/金句 | #3 Key Insight、#6 Pull Quote、#38 巨大引号、#40 极简留白引号、#39 肖像分割引号 |
| 代码/终端 | #5 代码面板、#7 对话气泡、#25 打字机终端 |
| 导航/切换 | #9 导航栏、#14 Filter 标签、#27 Tab 切换 |
| 步骤/流程 | #11 系统流程条、#42 圆形步骤 |
| 对比/列表 | #12 Do/Don't、#19 对比表A、#20 对比表B |
| 动效/滑动 | #4 Scroll Reveal、#28 手风琴、#31 翻转卡、#30 堆叠卡、#26 横向滑动 |
| 时间线 | #17 日历网格、#41 横向时间线 |
| 作品/产品 | #21 作品卡、#22 产品卡、#15 书卡 |

---

## 🎨 设计令牌（在 `:root` 定义，组件引用）

```css
:root{
  --teal:#00B6C5; --teal-deep:#0F3D3A; --ocean:#1A9AA8; --teal-light:#1FCEDD;
  --sand:#C89B6A; --clay:#B5543A; --ochre:#C9902E;
  --cream:#F1E9DA; --cream-deep:#E8DCC8;
  --ink:#2A2620; --ink-light:#564E42; --ink-faint:#8A7F6E;
  --font-display:'Baskerville','Iowan Old Style','Times New Roman',serif;
  --font-serif-cn:'Noto Serif SC','Source Han Serif SC',serif;
  --font-hand:'Caveat',cursive;
}
```
> ⚠️ **token 以 `brand-dna.md` 为准**：上面 `--teal` 必须是 `#00B6C5`（亮蓝绿），**不是**旧稿的 `#1E6F68`（偏暗、错）。
> 组件内若出现硬编码 `rgba(30,111,104,…)`（即 `#1E6F68` 系），一律改用 `var(--teal)` 或 `rgba(0,182,197,…)`。
> 复刻「线上 faifaida.com 那种味道」优先用 `Baskerville` 英文栈（见 brand-dna.md「已部署站点实际取值」）；`Fraunces` 也可但非线上默认。
> 组件内用 `var(--token, fallback)`；fallback 与上面一致。

---

## 🚨 AI 组件选择三原则（最高优先级）

1. **连贯性 > 多样性**：一个页面视觉语言统一，同类内容用同一种组件，不要每 section 换全新视觉。
2. **内容决定形式**：先看内容（流程？对比？金句？），再查索引找组件，不硬塞。
3. **动效克制**：一页最多 1~2 个动效组件（#44–#52），只用在 Hero/结尾。

## 🚫 引用块禁令（最高优先级）
- **绝对禁止** HTML 默认 `<blockquote>`（左灰竖线+浅灰底）
- **绝对禁止** 左色条+白底卡片引用样式
- **绝对禁止** 任何未设计浏览器默认引用样式
- 需要引用/金句 → 必须选 #3 / #6 / #38 / #40 / #39
- 一句话重点标注 → 用 #50 Text Highlighter（荧光笔/波浪线/画圈），**不是**引用块
- 禁止用 `border-left` 竖线引用块（Notion/飞书式）

---

## 组件条目（核心组件含代码，其余给结构+用法）

### #1 卡片组件库（5 变体）
适用：`卡片` `功能展示` `列表` `核心卖点`
- 1A 杂志裁切风卡、1B 编号主导卡、1C 标签卡、1D 侧边 icon 卡、1E 观点/洞察卡（1E-A 大引号 / 1E-B 手写批注 / 1E-C 荧光笔 / 1E-D 终端风）
```html
<div class="card card-mag">
  <div class="card-motif">⟡</div>
  <h3>标题</h3><p>描述</p>
</div>
```
```css
.card{ background:var(--cream); border-radius:14px; padding:clamp(28px,3vw,44px); box-shadow:0 3px 16px rgba(42,38,32,.06); }
.card-motif{ font-family:var(--font-display); color:var(--ochre); font-size:1.6rem; }
```
⚠️ 1E 禁止 border-left 竖线引用。

### #2 Section Header（数字+标题）
```html
<div class="section-header"><span class="sh-num">01</span><h2>标题</h2></div>
```
```css
.sh-num{ font-family:var(--font-display); font-size:clamp(2rem,5vw,3.4rem); color:rgba(30,111,104,.25); }
```

### #3 Key Insight（金句/观点）
```html
<blockquote class="key-insight"><p>核心观点一句话。</p></blockquote>
```
```css
.key-insight{ border:none; font-family:var(--font-serif-cn); font-size:clamp(1.3rem,3vw,1.9rem); color:var(--ink); padding:0; }
.key-insight::before{ content:'❝'; font-family:var(--font-display); color:var(--clay); }
```

### #6 Pull Quote（大字引用+装饰引号）
```css
.pull-quote{ font-family:var(--font-serif-cn); font-size:clamp(1.6rem,4vw,2.6rem); color:var(--teal-deep); text-align:center; }
```

### #9 导航栏（Fixed + 毛玻璃）
```css
.nav{ position:fixed; top:0; backdrop-filter:blur(8px); background:rgba(245,237,221,.85); }
.nav a{ color:var(--ink); font-family:var(--font-serif-cn); }
.nav a:hover{ color:var(--clay); }
```

### #10 三列 Chair 卡（5 变体：10A 大编号叠底 / 10B 杂志 / 10C 手绘虚线框 / 10D 渐变底 / 10E 纯文字）
```css
.chair-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:clamp(20px,2.5vw,32px); }
```

### #11 系统流程条（Flow Arrow）
```html
<div class="flow"><span class="flow-step">1 需求</span><span class="flow-arrow">→</span><span class="flow-step">2 制作</span></div>
```
```css
.flow-arrow{ color:var(--sand); }
```

### #12 Do/Don't 对比（4 变体：12A 分栏 / 12B 手写笔记 / 12C 表格 / 12D 印章边框）

### #14 Filter 标签栏
```css
.filter-tag{ border:1px solid var(--sand); color:var(--ink); border-radius:50px; padding:.4rem 1rem; }
.filter-tag.active{ background:var(--teal); color:var(--cream); }
```

### #17 日历网格（Emoji 情绪记录）

### #18 CTA 按钮
```css
.cta{ background:var(--clay); color:var(--cream); border-radius:50px; padding:.9rem 2rem; font-family:var(--font-serif-cn); }
.cta:hover{ background:var(--teal-deep); }
```

### #19 对比表A（杂志 Editorial）
### #20 对比表B（圆点标识）
> 表格必须从组件选用，禁止默认 `<table>` 样式。

### #21 作品卡（3 变体：杂志排版 / 明信片邮票 / 格栅）
### #22 产品卡（3 变体：杂志 / 明信片 / 格栅）

### #25 打字机/终端风
### #26 横向滑动卡
### #27 Tab 切换面板
### #28 手风琴
### #30 堆叠卡
### #31 翻转卡（3D）
### #32 悬停揭示卡
### #33 Dark Hero Reveal（暗底大字+按钮）
### #34 编号卡网格
### #35 交互清单
### #36 缩略图轨道+侧面板
### #38 巨大引号、#39 肖像分割引号、#40 极简留白引号（引用三选一）
### #41 横向时间线
### #42 圆形步骤
### #44 Sparkles Text、#45 Morphing、#46 Cool Mode、#47 Typing、#48 Kinetic、#49 Pixel Image、#50 Text Highlighter、#51 Comic Text、#52 Spinning Text（动效类，克制用）

### 组件条目 recurring 结构（写新组件时遵循）
1. `## 编号. 名称`
2. 适用场景（反引号标签）
3. HTML 代码块
4. CSS 代码块（含 `var(--token, fallback)`）
5. 变体/使用建议（可选）
6. 禁止事项（如 1E 禁 border-left）
7. JS 配套（交互组件用 IntersectionObserver + `prefers-reduced-motion` 降级）

> 完整 52 组件编号体系沿用 esther 原目录；新增多多专属母题角标组件 `#60 Motif Badge`（线描符号，单色，置于卡角/页眉）。
