# 布局模式库（多多版）

> 16 种经过验证的布局模式，按使用频率排序。每个 section 选不同的布局，组合使用。
> 已换肤为多多 token（`--teal/--sand/--clay/--ochre/--cream/--cream-deep/--ink`）+ 全衬线字体。
> 每个布局后附「母题建议」——按 `brand-dna.md` 的纹身/灵性/部落轴嵌入线描 SVG。

---

## 1. Hero 双栏不对称（文字+视觉）
**适用**: 个人网站首屏、知识库介绍首屏、产品介绍首屏
```html
<section class="hero">
  <div class="hero-text">
    <span class="label-caps">CATEGORY</span>
    <h1>主标题</h1>
    <p>描述文字</p>
  </div>
  <div class="hero-visual"><!-- 母题 SVG：女人×狮 / 曼陀罗 --></div>
</section>
```
```css
.hero{ min-height:100vh; display:grid; grid-template-columns:1fr 0.6fr; align-items:center; gap:48px; padding:6rem 2rem 4rem; }
```
⚠️ 不要对称 50/50，不对称才有张力。**母题建议**：右侧放「女人×狮」单线融合或曼陀罗线描，单色 `--ink`/`--ochre`。

## 2. Sticky 侧栏 + 内容滚动
**适用**: 长内容分段、知识库目录、深度内容
```css
.layout-sticky{ display:grid; grid-template-columns:0.35fr 1fr; gap:clamp(40px,6vw,100px); align-items:start; }
.sticky-side{ position:sticky; top:80px; }
```
⚠️ 移动端（<900px）sticky 变 static。**母题建议**：侧栏序号用母题符号（太阳/螺旋）替代纯数字。

## 3. 三等分卡片网格
**适用**: 能力矩阵、产品并列、知识库分类
```css
.features-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:clamp(20px,2.5vw,32px); }
```
⚠️ 不要落单孤儿卡，保持 3/6/9。**母题建议**：每张卡角标一个灵性符号（月/星/莲），轮换。

## 4. 纵向 Step 流程线
**适用**: 发布流程、制作步骤、教学引导
```css
.steps-container::before{ content:''; position:absolute; left:22px; top:40px; bottom:40px; width:2px; border-left:2px dashed var(--sand); }
.step-num{ background:var(--teal); color:var(--cream); font-family:'Fraunces',serif; }
```
⚠️ 步骤 ≤5，超过拆分。**母题建议**：连接线用「点刺」虚线，step 点用太阳/螺旋。

## 5. 中轴时间线交错
**适用**: 时间线、对比、并列要点
```css
.timeline-axis{ background:rgba(30,111,104,.15); }
```
⚠️ 移动端变单列。**母题建议**：轴用海浪曲线替代直线。

## 6. 全宽深色面板
**适用**: 重要金句、核心观点（打破米底节奏）
```css
.dark-section{ background:var(--teal-deep); color:#e8dcc4; padding:clamp(60px,8vh,120px) 0; }
```
⚠️ 一页 ≤1~2 个。**母题建议**：面板内嵌巨大曼陀罗线描作水印（opacity 0.08）。

## 7. 横向 Step 连接线
**适用**: 简短 3~4 步概览
```css
.steps-layout::before{ background:linear-gradient(90deg,var(--sand),var(--teal)); }
.step-dot{ background:var(--teal); color:var(--cream); font-family:'Fraunces',serif; }
```
⚠️ 仅 3~4 步。

## 8. Hero 全屏居中型
**适用**: 个人品牌首页（强冲击首屏，仅一次）
```css
.hero-card{ background:var(--cream); border-radius:24px; padding:clamp(2.5rem,5vw,4.5rem); box-shadow:0 4px 32px rgba(42,38,32,.08); }
```
⚠️ 仅 Hero 首屏一次，后续 section 左对齐为主。

## 9. Hero 单栏纵向（中心辐射型）
**适用**: 个人介绍、理念页（以头像/Logo 为中心）
```css
.hero-vertical{ min-height:100vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; }
.hero-avatar{ border-radius:50%; }
```
⚠️ 仅 Hero 区域。

## 10. 自适应卡片网格（auto-fill）
**适用**: 作品集、知识库条目、不确定数量集合
```css
.auto-grid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:1rem; }
```
⚠️ 自动换行。

## 11. 全宽品牌色面板
**适用**: 情绪高潮、CTA 邀请、核心观点
```css
.section-accent{ background:var(--teal); color:var(--cream); padding:clamp(80px,12vh,160px) 0; }
```
⚠️ 一页 ≤1~2 个；可换 `--sand`（文字改 `--ink`）。**母题建议**：面板边缘用部落点刺带。

## 12. 横向滚动时间线
**适用**: 经历时间线、横向浏览
```css
.timeline-card{ background:var(--cream); border-radius:16px; box-shadow:0 4px 20px rgba(42,38,32,.06); }
.timeline-card .year{ font-family:'Fraunces',serif; color:var(--teal); opacity:.6; }
```

## 13. 分栏对称（Pain Point 展示）
**适用**: 问题 vs 方案、before/after
```css
.split-right{ background:var(--cream-deep); }
```
⚠️ 左放大字标题，右放内容/列表。

## 14. Tab 切换单栏（Dashboard 型）
**适用**: 个人看板、功能切换、知识库分栏
```css
.tab.active{ border-bottom-color:var(--teal); color:var(--teal); }
```

## 15. 无限画布（Canvas 型）
**适用**: 白板、信息可视化、自由布局（App 型）
```css
.canvas-grid{ background-image:radial-gradient(circle, rgba(30,111,104,.13) 1.2px, transparent 1.2px); background-size:28px 28px; }
```

## 16. Sticky 编号侧栏 + 大图杂志卡片
**适用**: 步骤教程、流程拆解（5~10 步）
```css
.layout-sticky-mag .nav li::before{ font-family:'Fraunces',serif; color:rgba(30,111,104,.15); }
.step-item:nth-child(3n+2) .step-num{ color:rgba(200,155,106,.35); }
.step-item:nth-child(3n) .step-num{ color:rgba(181,84,58,.2); }
```
⚠️ 步骤 5~10 合适；编号三色轮换（teal/sand/clay）保持节奏；移动端侧栏隐藏。

---

> 所有布局的字体默认 `--font-serif-cn`；英文展示用 `--font-display`；批注用 `--font-hand`。
> token 定义在 `brand-dna.md`，组件在 `components.md`。
