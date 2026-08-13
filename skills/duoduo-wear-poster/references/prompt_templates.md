# DUODUO WEAR 海报 ImageGen Prompt 模板

## 通用负向提示（两版共用）

```text
No text, no watermark, no logo, no brand name, no AI artifacts, no illustration, no cartoon, no oversaturated colors, no hard cut at bottom, no pure white background, no studio backdrop, no artificial shadow.
```

## 1. Flatlay 平铺特写版

### 适用场景
- 产品图、电商图、招募海报、品牌 KV
- 不需要人物，只展示泳衣设计

### 模板

```text
A high-end fashion product photography of a {swimsuit_design} swimsuit laid flat on a cream-colored sandy beach. The sand is fine, warm, slightly textured, with natural ripples. Behind the sand is deep teal ocean water with gentle waves, shot in soft natural daylight. The swimsuit is centered in the upper two-thirds of the frame, styled naturally as if casually placed. Color palette: warm cream, oatmeal, sand, deep teal (#00B6C5 accent), navy-blue water. Film photography texture, subtle grain, matte finish, authentic vacation mood, editorial swimwear campaign. Leave the bottom 15% of the image as clean sand/water with no text, no logo, no objects.

Negative: {negative}
```

### 变量说明

- `{swimsuit_design}`：用户指定的泳衣设计。例如：
  - "cream white ribbed bikini with thin turquoise straps"
  - "rust orange one-piece swimsuit with open back"
  - "black high-waist bikini with gold ring details"
- `{negative}`：上方通用负向提示

### 示例

```text
A high-end fashion product photography of a cream white ribbed bikini with thin turquoise straps laid flat on a cream-colored sandy beach. The sand is fine, warm, slightly textured, with natural ripples. Behind the sand is deep teal ocean water with gentle waves, shot in soft natural daylight. The bikini is centered in the upper two-thirds of the frame, styled naturally as if casually placed. Color palette: warm cream, oatmeal, sand, deep teal accent, navy-blue water. Film photography texture, subtle grain, matte finish, authentic vacation mood, editorial swimwear campaign. Leave the bottom 15% of the image as clean sand/water with no text, no logo, no objects.

Negative: No text, no watermark, no logo, no brand name, no AI artifacts, no illustration, no cartoon, no oversaturated colors, no hard cut at bottom, no pure white background, no studio backdrop, no artificial shadow.
```

## 2. Hero 人穿着版

### 适用场景
- 品牌氛围图、社媒 feed、小红书/Instagram 竖图
- 需要展示泳衣上身效果

### 模板

```text
A cinematic film photograph of a young woman at the beach, {model_pose}. She is wearing a {swimsuit_design}. The setting is a sunny beach with soft waves in the background, shallow depth of field, warm golden-hour backlight making her hair glow. Her skin has a natural sun-kissed tone. The color palette is warm cream, sandy beige, deep teal ocean, with the swimsuit as the accent color. Editorial swimwear campaign, analog film grain, 35mm photography, authentic vacation mood, natural and relaxed. Crop from chin to mid-torso, upper body only. Leave the bottom 15% of the image as clean out-of-focus sand/water with no text, no logo, no objects.

Negative: {negative}
```

### 变量说明

- `{model_pose}`：人物姿势描述。例如：
  - "standing at the shoreline, looking to the side, wind blowing her hair"
  - "walking along the beach, one hand touching her hair, confident"
  - "standing with arms relaxed at her sides, facing the ocean"
- `{swimsuit_design}`：同 flatlay 版
- `{negative}`：通用负向提示

### 示例

```text
A cinematic film photograph of a young woman at the beach, standing at the shoreline with wind blowing her hair, looking to the side. She is wearing a teal ribbed bikini top with thin braided straps and a small shell pendant at center front. The setting is a sunny beach with soft waves in the background, shallow depth of field, warm golden-hour backlight making her hair glow. Her skin has a natural sun-kissed tone. The color palette is warm cream, sandy beige, deep teal ocean, with the swimsuit as the accent color. Editorial swimwear campaign, analog film grain, 35mm photography, authentic vacation mood, natural and relaxed. Crop from chin to mid-torso, upper body only. Leave the bottom 15% of the image as clean out-of-focus sand/water with no text, no logo, no objects.

Negative: No text, no watermark, no logo, no brand name, no AI artifacts, no illustration, no cartoon, no oversaturated colors, no hard cut at bottom, no pure white background, no studio backdrop, no artificial shadow.
```

## 3. 尺寸与比例提示

- 默认输出比例：3:4（竖图）
- 建议 ImageGen 尺寸：768×1074 或等比 3:4
- 如需手机壁纸/更长竖图：768×1274（约 3:5），脚本会自动调整 footer 比例

## 4. 输出后处理

生成主体图后，**必须**用 `scripts/compose_poster.py` 叠加 footer。不要在 ImageGen prompt 里要求 "with logo at bottom"，否则 logo 位置/样式不可控。

## 5. Image-to-Image 保真模式（背景要"一模一样"时用）

当用户要求"和某张参考海报完全相同的背景"时，用 image-to-image，不要从零生成。

### 调用方式（ImageGen）

```json
{
  "image": ["<参考海报本地路径>"],
  "input_fidelity": "high",
  "size": "768x1074",
  "quality": "high",
  "prompt": "Replace ONLY the swimsuit in this image with a {swimsuit_design}, laid flat in the exact same position and fold as the original. Keep the background, sand texture, rocks, ocean, waves, sky, lighting, colors, shadows, and every other element 100% identical to the original. Do not alter anything other than the swimsuit itself. Negative: no text, no watermark, no logo change, no new objects, no illustration, no oversaturated colors."
}
```

### 说明
- `input_fidelity: "high"` → 输出尽量贴近原图，背景/光影/沙石/海几乎不变。
- 输出再跑一次 `compose_poster.py`（脚本用参考图裁出的 `logo_band_768x134.png` 覆盖底部），logo 与参考图像素级一致。
- 适用：flatlay 与 hero 两版；只要参考图是已批准的标准版式即可。
