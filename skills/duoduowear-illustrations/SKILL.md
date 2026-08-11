---
name: duoduowear-illustrations
description: 为 DUODUO WEAR 的品牌文章、图文笔记、视频、包装、吊牌、产品讲解、身体与版型内容生成插画策略、三鸟图腾、静态资产和微动画资产。视觉只使用米色与品牌蓝紫色，真实产品可保留本来颜色。
---

# DUODUO WEAR Illustrations

## 核心定位

固定视觉母体：同一物种家族，不同职能分身。

### Mountain Bird｜山鸟
- 品牌精神
- 封面
- 更立住的主视觉
- Logo 延展
- 静态、图腾、粗线条

### Shell Bird with Eyes｜有眼睛的贝壳鸟
- 最灵活
- 文章配图
- 视频小插图
- 吊牌
- 贴纸
- 品牌说明
- 贝壳可开合，鸟保留眼睛

### Wave / Coastal Bird｜浪鸟 / 海岸鸟
- 产品与海边场景
- 身体动作
- 流动
- 浪线与鸟形变换

## 使用层级

- 品牌主视觉：鸟是主图腾
- 产品 / 身体说明：鸟作为小印章或观察者
- 技术版型图：只保留鸟形签名
- 纯真实照片：不强行叠鸟

每件公开 Wear 视觉应有品牌痕迹，但不要求鸟永远占中央。

## 颜色

非产品视觉仅使用：
- 米色 `#E6CEB8`（WEAR 深米色，实测自正式 logo `duoduo-wear-full-logo.jpeg` 背景；**取代原 `#F1E9DA`**，今后 WEAR 所有标准色里的米色统一用这个，禁止再用 `#E4D0BC`）
- 蓝紫色 `#2E27A8`

允许使用这两个颜色的明暗与透明度变化，不引入第三种装饰色。

例外：
- 真实产品
- 真实面料
- 真实人物穿着
可保留本来颜色。

## 字体

正文与 OS 共用：
- 中文：Songti SC / STSong / Noto Serif CJK SC / 思源宋体
- 英文：Iowan Old Style / Baskerville / Times New Roman

标题分开：
- DUODUO WEAR 品牌名必须调用正式 Logo / Wordmark 资产
- 其他标题匹配正式 Logo 的衬线字形
- 未确认精确字体名时，不伪造字体名称
- 可用批准 serif stack 做视觉匹配，并在正式 Logo 旁回看

## Motion DNA

### Mountain Bird
- 睁眼
- 缓慢转头
- 山与浪线从脚下生长
- 以印章压下出现

### Shell Bird
- 贝壳轻轻打开
- 有眼睛的鸟探出
- 眨一次眼
- 看向左右
- 贝壳与海浪轻微呼吸
- 最后恢复图腾轮廓

### Wave Bird
- 单线浪纹升起
- 变成鸟
- 保持
- 融回浪线

动画必须：
慢、静、图腾、手作、有印记感。

## 参考资产

所有已批准参考图见 `assets/reference/`：
- `official-logo-reference.png` — 正式 Logo，不可由图片模型重画
- `approved-shell-bird-system.png` — 有眼贝壳鸟系统
- `approved-mountain-bird-board.png` — 山鸟图腾板
- `approved-wave-bird-board.png` — 浪鸟 / 海岸鸟
- `approved-wear-motion-dna.png` — 动画 DNA
- `approved-character-shell-scene.png` — 手绘质量参考（深米色底、蓝紫点缀、贝壳鸟场景画风）。**仅取"鸟 + 贝壳场景"的画法；图中多多人物不用于 WEAR —— WEAR 的 IP 仅限鸟，绝不放多多人物。**

使用参考图时：WEAR 只用鸟 / 贝壳场景由图像模型参考生成（**不放多多人物**）；文字 / Logo / 标签 / 箭头必须后期程序添加。

## Canonical Examples｜已拍板样例（照抄，不要 improvise）

### 「你的肤色分四季」四格图解 = v7（2026-08-09 多多拍板）
- **成品**：`assets/examples/wear_season_graph_birds_v7.png`（1080×1440，2×2 四格：春飞 / 夏走 / 秋卧 / 冬穿棉袄）+ 同目录 `assets/examples/wear_season_graph_birds_v7_preview.html`。
- **组装脚本**：`assets/examples/compose_wear_season_graph_v7.py`（PIL 后制：去水印/去文字 → 统一 #E6CEB8+#2E27A8 两色 → 2×2 面板 → 标题/四季标签 → 底部同色 logo 色带）。
- **生成管线（必须照此）**：
  1. 以 `approved-shell-bird-system.png` + `approved-wave-bird-board.png` + `approved-mountain-bird-board.png` 作 **img2img reference**，ImageGen `input_fidelity=high` 生成四动作鸟（飞/走/卧/穿棉袄）。
  2. **绝不准**让图像模型凭空画鸟 / 用卡通圆头鸟 / 改图腾设计——只变动作，设计锁死品牌 Shell Bird。
  3. PIL 后制统一两色、抠图、拼面板、加程序化文字与底部 logo 色带。
- **色号锁死**：背景与 logo 色带 = `#E6CEB8`；鸟形与文字 = `#2E27A8`；仅两色，无第三色。
- **已接受的小差异（不必再改，除非多多单独要求）**：飞鸟周围少量运动短线、夏/秋/冬喙略开、冬鸟无贝壳。
- **铁律**：今后任何 WEAR 图解，鸟 = 品牌 Shell Bird 图腾，禁止抽象/卡通版；配色 = #E6CEB8 + #2E27A8。

### Excalidraw × Shell Bird IP 融合验证图（2026-08-09 多多拍板）
- **成品**：`assets/examples/wear_excalidraw_validation.png`（1080×1440）+ 同目录 `assets/examples/wear_excalidraw_validation_preview.html`。
- **可编辑骨架源**：`assets/examples/wear_excalidraw_validation.excalidraw`（Excalidraw app 可打开；仅框/箭头/文字，**不含鸟 IP**——鸟按纪律由图生图后程序合成）。
- **组装脚本**：`assets/examples/compose_wear_excalidraw_validation.py`（PIL 手绘 rough 骨架 + 嵌入 v7 鸟 cutout + 程序加文字/logo 色带）。
- **用途**：验证「Excalidraw 手绘结构（骨架）+ 品牌鸟 IP cutout + 程序合成」这条工艺跑得通，是 WEAR 图解的标准组合范式。
- **流程（照抄）**：
  1. 用 `rough_line` / `rough_rect` / `rough_arrow`（PIL 抖线模拟 Excalidraw）画结构骨架（框 + 四季循环箭头 + 标题下划线）。
  2. 嵌入 v7 已拍板 Shell Bird 两色 cutout（春飞/夏走/秋卧/冬棉袄）。
  3. 程序化添加中文标题/季节标签/正式 logo 色带（文字、Logo 绝不由图模型生成）。
  4. 同步导出 `.excalidraw` 源文件，方便在 Excalidraw app 里手调骨架。
- **纪律检查点**：Excalidraw 仅作结构骨架；鸟 IP 来自图像模型；文字/Logo 程序添加；两色 #E6CEB8 + #2E27A8，无第三色。

## 图文笔记格式铁律（2026-08-09 多多拍板）
1. **不单独生成封面卡**：多图 carousel / 小红书图文笔记以第一张图为入口图，不另出一张「封面卡」。需要首图冲击力的，直接让图1承担封面功能。
2. **底部品牌 logo 必须横向一行**：每张图底部的品牌落款要让「图形（鸟/图腾印章）」与「duoduo wear / DUODUO WEAR」文字在同一水平行内平行排列。禁止图片模型原生 logo 里常见的「图形在上、文字在下」的竖排堆叠；程序合成时把图形与文字拆件后左右并放。
3. 以上两条优先于任何默认模板；若与既有样例（如 v7 四格图解的底部 logo）冲突，以本铁律为准重排。

## 禁止
- 萌宠
- 快速跳跃
- 频繁眨眼
- 拍翅膀卖萌
- 塑料 3D 潮玩
- 高奢光泽
- 儿童卡通
- 第三种装饰色
- 让图片模型重画正式 Logo
