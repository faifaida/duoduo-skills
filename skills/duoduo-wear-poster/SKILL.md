---
name: duoduo-wear-poster
agent_created: true
description: Generate DUODUO WEAR swimwear brand posters that lock the background, lighting, color grade, model pose range, logo placement, and linen footer while only changing the swimsuit design. Trigger whenever the user asks for DUODUO WEAR posters, swimwear product images, "same poster but different swimsuit", or any brand image that must carry the DUODUO WEAR full logo + wordmark at the bottom.
---

# DUODUO WEAR 泳衣海报生成 Skill

## 1. 触发条件

当用户表达以下任一意图时触发本 skill：

- "生成 DUODUO WEAR 海报"
- "和之前招募海报一样的图，只换泳衣"
- "做一张 DUODUO WEAR 泳衣产品图"
- "给我一张 DUODUO WEAR 品牌图，要保留 logo 和底部米色带"
- "用 xx 泳衣设计替换图里的白色泳衣"
- 任何要求生成「与 `DUODUO WEAR_v2招募海报_20260729.png` 或 `poster_hero_phone.jpg` 同款构图、只变泳衣」的请求

## 2. 输出目标

生成一张 768×1074（3:4 画幅）的 DUODUO WEAR 品牌海报。除了泳衣设计可动之外，其余所有视觉参数必须锁死：

- 场景/背景
- 光线与色调
- 人物位置与姿势范围（仅限 hero 版可动）
- 底部米色 footer 渐变
- DUODUO WEAR 图形 logo + 文字 logo 的位置、比例、颜色

## 3. 两种固定版式

### 3.1 Flatlay 平铺特写版

参考资产：`assets/ref_poster_flatlay_768x1074.png`

- 主体：一套泳衣平铺在浅色沙滩/沙地上，居中偏上
- 泳衣：默认米白/奶油色（具体颜色按用户 swimsuit_design 参数），可带青绿色/蓝绿色系带细节
- 背景：深蓝绿色海水 + 米色沙滩，海浪纹理，自然日光
- 人物：不出现人物，只出现泳衣
- 底部 footer：从画面约 88% 高度开始向下，是 `linen #F1E9DA` 米色带，顶部与沙滩做柔和渐变过渡（不硬切）
- Logo：footer 中央，左侧蓝色图形 logo，右侧 "DUODUO WEAR" 深蓝/海军蓝无衬线大写文字

### 3.2 Hero 人穿着版

参考资产：`assets/ref_poster_hero_phone.jpg`

- 主体：一位女性在海边穿着泳衣上半身的特写（下巴到腰部）
- 人物：小麦色/晒后皮肤，金发或浅棕发随风飘动，姿态自然（姿势可按用户要求变）
- 泳衣：青绿色/蓝绿色吊带 bikini top，胸前可有抽褶、吊坠细节；具体泳衣设计按用户参数
- 背景：海边沙滩 + 海浪，浅景深虚化
- 光线：金色侧逆光/背光，发丝光，胶片质感，温暖柔和
- 底部 footer：与 flatlay 版完全相同 —— `linen #F1E9DA` 米色带 + 中央 DUODUO WEAR logo
- 画幅：可保持 768×1074；若用户要手机壁纸/竖屏，可扩展到 768×1274，但 footer 比例不变

## 4. 锁死参数清单

| 参数 | 值 | 是否可变 |
|---|---|---|
| 画布基准 | 768×1074 px | 否（手机竖屏可扩展高度，logo 带比例不变） |
| 品牌色 night | `#151A2E` | 否 |
| 品牌色 linen | `#F1E9DA` | 否（footer 底色） |
| 品牌色 teal | `#00B6C5` | 仅用于泳衣点缀/系带 |
| 品牌色 rust | `#B4553A` | 否（如需强调色） |
| Logo 位置 | 底部 footer 中央 | 否 |
| Logo 组合 | 左侧蓝色图形 logo + 右侧 "DUODUO WEAR" 文字 | 否 |
| Footer 高度 | 约 12-15% 画面高度，顶部渐变融入画面 | 否 |
| 背景环境 | 海边/沙滩/海水/自然光 | 否 |
| 胶片/真实摄影质感 | 去 AI 感、无 AI 水印 | 否 |
| 泳衣设计 | 款式、颜色、纹理、系带、金属件 | ✅ 唯一可变量 |
| Hero 版人物姿势 | 可动（但必须是海边、半身、自然姿态） | ✅ 可变量 |

## 5. 工作流程

### Step 1：确认版式与泳衣设计

读取用户请求，提取：

- `layout`: `"flatlay"` 或 `"hero"`（用户未指定时默认 `flatlay`）
- `swimsuit_design`: 用户描述的泳衣设计（款式、颜色、关键细节）
- `model_pose`（仅 hero 版）：用户对人物姿势的描述，若未提供则随机生成自然海边姿态
- `aspect`: 默认 `"768x1074"`，可选 `"768x1274"` 用于手机竖屏 hero

### Step 2：生成主体图

使用 ImageGen 生成主体图。Prompt 模板在 `references/prompt_templates.md`。

关键要求：

- 生成图必须留出底部 12-15% 的干净区域（沙滩/人体下半部分/水面），用于后续叠加 footer
- 不要在生成图中自带任何 logo、文字、水印
- 不要自带底部米色带（由脚本统一叠加，确保所有输出一致）

#### ⚠️ 背景一致性铁律（重要）

- **用户要求"和某张参考海报一模一样的背景"（如 `DUODUO WEAR_v2招募海报_20260729.png`）时，禁止从零生成（每次背景都不同，必定不一）。**
- 必须用 **ImageGen 的 image-to-image 模式**：把那张参考图作为 `image` 输入，`input_fidelity` 设 `"high"`，prompt 只要求"替换中间的泳衣为指定设计、其余（背景/沙石/海水/光影/logo）100% 不变"。
- 这样背景、光线、沙石、海、甚至底部 logo 都和参考图一致；Step 3 再叠加一次参考图裁出的 `logo_band` 做最终锁定（防止 AI 微调 logo）。
- 只有当用户明确接受"全新但风格一致"的背景时，才走从零生成路径。

### Step 3：统一叠加底部 footer 与 logo

运行 `scripts/compose_poster.py`：

```bash
python scripts/compose_poster.py \
  --input generated_swimsuit.png \
  --layout flatlay \
  --output final_duoduo_wear_poster.png
```

脚本行为：

1. 将输入图 resize 到目标尺寸（768×1074 或 768×1274）
2. 从画面底部向上约 134px 区域，覆盖 `assets/logo_band_768x134.png`（包含 linen 渐变带 + 完整 logo）
3. 在 logo 带顶部做 30-40px 的柔和渐变融合，避免硬边
4. 输出最终 PNG

### Step 4：交付

- 将最终 PNG 保存到用户指定路径；若未指定，保存到 `05_CONTENT/00 photo_materials/duoduo_wear/` 并按时间命名
- 向用户展示成品，并说明这是「仅泳衣可变」的锁死版式
- 如需批量生成多版泳衣，重复 Step 2-3

## 6. 可复用资源

### assets/

- `ref_poster_flatlay_768x1074.png`：平铺版黄金标准参考图
- `ref_poster_hero_phone.jpg`：人穿着版参考图
- `logo_band_768x134.png`：可直接叠加的底部 linen 带 + 完整 DUODUO WEAR logo
- `logo_only_768x94.png`：纯 logo 条（无顶部渐变，用于自定义融合）
- `brand_library/`：**真实品牌图库（2026-08-09 起存入）**，供图文笔记 carousel 下半部调用：
  - `fella/`：Fella 官网真实产品 / campaign 图
  - `vbq/`：Vilebrequin 官网真实泳裤产品图
  - `abysse/`：abysseofficial.com 真实产品图（Shopify `products.json` 抓取）
  - `duoduo_wear/`：DUODUO WEAR 自有四张海报 `poster_hero / shimmer / fluorescent / tribal`
  - ⚠ 此目录为「真实品牌图」资产库；生成图文笔记下半部时直接引用，绝不用 ImageGen 仿图替代。

### references/

- `prompt_templates.md`：ImageGen prompt 模板（flatlay / hero 两版）
- `technical_specs.md`：尺寸、颜色、字体、logo 位置等技术规范

### scripts/

- `compose_poster.py`：叠加 footer/logo 的确定性脚本

## 7. 禁止事项

- 禁止改变底部 logo 组合、位置、比例
- 禁止改变 linen #F1E9DA 米色带的颜色
- 禁止用硬切边分隔 footer 和画面
- 禁止在生成主体图时自带 logo/水印
- 禁止把 logo 放在除底部 footer 中央以外的任何位置
- 禁止用纯白/暖白替代 linen 米色

## 8. 自检清单

交付前核验：

- [ ] 输出尺寸 = 768×1074（或用户指定的 768×1274）
- [ ] 底部 footer 颜色 = `#F1E9DA` linen
- [ ] footer 顶部与画面为渐变过渡，非硬切
- [ ] logo 组合居中，左侧图形 + 右侧 "DUODUO WEAR" 文字
- [ ] 无 AI 水印、无额外文字、无额外图形
- [ ] 泳衣设计与用户要求一致
- [ ] 背景/光线/色调与参考图一致

## 9. 编辑插画能力（DUO WEAR Painting · 已并入本技能）

> 品牌「绘画风」插画（知识分享图 / 口播讲解配图 / 公众号插画）已并入本技能，统一复用 DUODUO WEAR 品牌 DNA。
> 允许 AI 生图的**唯一**例外场景见 `references/duo-wear-painting/`（视频封面与品牌实拍图仍禁 AI 生图）。

- 风格锁（配色/母题/字体）：`references/duo-wear-painting/references/style_prompt.md`
- 合成规格（小红书 3:4 / 公众号 / 口播 16:9·1:1 / cutout 透明）：`references/duo-wear-painting/references/composition_specs.md`
- 出图 prompt 拼装：`references/duo-wear-painting/scripts/build_prompt.py`
- 去水印 + 品牌边框合成：`references/duo-wear-painting/scripts/compose_note.py`
- 铁律：ImageGen 出水印 → 硬切底 50px；**绝不交付带「图片由AI生成」水印的图**。
