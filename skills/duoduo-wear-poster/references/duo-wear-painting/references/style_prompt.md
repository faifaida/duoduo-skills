# 品牌插画风格锁（style lock）

> 本文件是 `scripts/build_prompt.py` 的**人类可读权威源**。AI 生成任何 DUODUO WEAR 插画，都必须套用下面的风格锁 + 负面词。
> 改风格只改这里 + `build_prompt.py` 的常量，保持两处同步。

## 一、核心风格句（Base）
Editorial illustration, painterly hand-drawn style, DUODUO WEAR brand aesthetic:
**wild yet gentle, primal yet refined, handcrafted with worldliness.**
Flat or subtly textured paper feel — **NOT** photorealistic, **NOT** 3D render, **NOT** AI glossy stock-photo.

## 二、配色锁（Palette · 来自 brand-dna.md）
| 角色 | 色值 | 用法 |
|------|------|------|
| 主色·亮蓝绿 | `#00B6C5` | 海 / 主体 |
| 深青 | `#0FA3B8` | 暗场面 / 文字 |
| 次冷调 | `#1A9AA8` | 海洋中景 / 远水 |
| 米白麻 | `#F1E9DA` | 主背景（永远偏暖） |
| 米色玉髓 | `#E8DCC8` | 底 |
| 神秘赭金 | `#C9902E` | 灵性符号 / 高光，**≤10% 点睛** |
| 陶土红 | `#B5543A` | 点缀 / 重点，永远是点缀 |
| 暖墨 | `#2A2620` | 主文字（非纯黑） |

**禁用**：蓝紫渐变、cyan、neon、纯黑 `#000` / 纯白 `#fff` 大面积、AI 常用冷灰蓝调、多色渐变背景。

## 三、母题库（Motifs · 线描，单色，与底对比克制）
- 灵性：太阳 / 月亮 / 星辰、曼陀罗、神圣女性、阴阳眼、莲花、螺旋、护身符 / 塔罗、柏柏尔符号、萨满图腾。
- 部落 / 原始：岩画涂鸦（太阳/星星/举手人形/螺旋）、点刺 dotwork、几何部落图腾、箭头/羽毛、编织绳结。
- 单线融合：女人 × 动物（狮子/狼/豹/鸟/兔）连续一笔线条、圆形框架、留白极多。
- 自然（贯穿）：海浪、山、棕榈、贝壳、植物藤蔓、佩斯利 paisley。

**母题调用规则**：每张图至少 1 个明确母题；一律线描（stroke 非填充块），单色；符号有意义，不随机撒点。

## 四、字体（合成时叠加的标题，全衬线）
- 英文展示 / 大标题：`Baskerville, "Iowan Old Style", "Times New Roman", serif`
- 中文标题 + 正文：`Noto Serif SC` / `Source Han Serif SC` / 系统宋体栈
- 手写体点缀：`Caveat`（仅标签 / 批注，不进正文）

## 五、风格变体（variant，传给 build_prompt.py --style）
- `inkline`：细 ink 线描插画，单线宽，极少平涂，版画 / 蚀刻感。
- `watercolor`：宽松水彩晕染，可见纸纹，柔和渗化，杂志编辑感。
- `woodcut`：粗犷木刻 /  linocut 印花，高对比，雕刻肌理，原始部落能量。
- `flat`：扁平矢量感编辑插画，限色调，干净形状，现代民俗风。

## 六、负面词（Negative，永远带）
no photorealistic photo, no 3D render, no CGI, no neon, no blue-purple gradient,
no pure black or pure white large areas, no glassmorphism, no AI glow effects,
no watermark, no signature, no text in image unless requested,
no generic AI template look, no centered symmetric stock layout.

## 七、cutout 模式附加句（--cutout 时自动追加）
"Transparent background, isolated subject, no background, clean alpha edges, PNG."
（用于口播视频叠加；compose_note.py 的 cutout 模式直接输出透明 PNG）

## 八、气质自检
做出来截图发社媒，会不会被评「又是 AI 做的」？能不能一眼认出是「多多」的（蓝绿+米+线描母题+全衬线）？
