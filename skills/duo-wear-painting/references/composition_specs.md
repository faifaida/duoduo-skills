# 合成规格（composition specs）

> `scripts/compose_note.py` 的输入参数与版面规则。所有尺寸像素级，导出 PNG。

## 一、模式与尺寸
| mode | 尺寸 | 用途 | 背景 |
|------|------|------|------|
| `note` | 1080×1440（3:4） | 小红书图文 / 知识卡片 | 米 `#F1E9DA` |
| `wechat` | 900×383（2.35:1）封面 / 或 1080×1440 | 公众号封面 / 内文插画 | 插画铺底 + 暗角 scrim |
| `explain` | 1280×720（16:9）或 1080×1080（1:1） | 口播讲解配图 | 米 / 插画铺底 |
| `cutout` | 原分辨率（透明） | 口播视频叠加层 | 透明（prompt 已要去背） |

## 二、note 模式版式骨架（自上而下）
1. **40px 线描边框**：外框统一 40px 单色线（ink / ochre / clay），四角可加部落点刺角标。**不得更细**。
2. **顶部品牌条**（y 40→120）：左侧母题（太阳线描）+ 右侧手写体小字「DUODUO WEAR」。
3. **主标题区**（y 140→360）：大字 Baskerville / 思源宋体，1~2 行；可叠巨大母题水印（opacity 0.08）。
4. **副文案**（≤3 行）：思源宋体，行高 1.9。
5. **中部视觉**（y 380→H-170）：插画（已去水印）contain 居中。
6. **底部留白 50px**（H-50→H）：专留给去水印处理，天然米底，**绝不放任何文字 / 水印**。

## 三、wechat 封面模式
- 插画 cover-fit 铺满画布；底部加 `linear-gradient(transparent→#151a2e 0.55)` scrim 保证标题可读。
- 标题叠在 scrim 上，颜色 `#faf6ee`（paper）；右下角小号「DUODUO WEAR」lockup。
- 同样先去过水印（裁底 50px）。

## 四、explain 口播配图模式
- 16:9：插画 cover-fit 铺底 + 轻 scrim；或左图右文（米底，插画 contain 在左 60%）。
- 1:1：同 note 但方形，标题更短。
- 仅作静态配图；若要动起来请走 cutout 模式叠加视频。

## 五、cutout 透明模式
- 输入插画应已由 prompt 要求透明背景；本模式只做去水印（裁底 50px）+ 转 RGBA 输出。
- 叠加到口播视频（ffmpeg，仅本模式用）：
  ```
  ffmpeg -i 口播.mp4 -i 插画.png -filter_complex "[1]scale=W:H[ov];[0][ov]overlay=X:Y" -c:a copy out.mp4
  ```
  - 位置 X:Y 按画面留白区定（通常底部或侧边，不挡人脸）。
  - **不引入 HyperFrames**；ffmpeg 足够做静态/序列叠加。

## 六、去水印铁律（所有模式通用）
- ImageGen 输出底部必带「图片由AI生成」水印 → **硬切底 50px**（`img.crop((0,0,w,h-50))`）。
- note 模式：裁掉后底部 50px 是天然米底留白，seam 被盖住，无需渐变。
- wechat / explain 铺底模式：裁底 50px 即够（标题 scrim 在底部，水印已删）。
- **绝不交付带水印的图**（用户红线：永远不要有这几个字）。

## 七、字体回退（compose_note.py 自动探测）
- 中文衬线候选：`/System/Library/Fonts/STSong.ttc` → `Supplemental/STSong.ttf` → `PingFang.ttc` → `Arial Unicode.ttf`
- 英文衬线候选：`Supplemental/Baskerville.ttf` → `Supplemental/Times New Roman.ttf` → `Times.ttc`
- 都找不到则 PIL 默认字体（会警告，仍出图）。
