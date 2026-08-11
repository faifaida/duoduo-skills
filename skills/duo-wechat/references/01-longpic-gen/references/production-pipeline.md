# Production Pipeline

## 推荐技术方案 A：HTML/CSS + Playwright

最稳定，适合中文与复杂拼贴。

1. 创建 1080×1890 固定画布。
2. 用绝对定位/网格实现纸张和图片层。
3. 使用 CSS 纹理叠层。
4. 使用真实文字节点。
5. Playwright 截图，deviceScaleFactor=1 或 2。

## 方案 B：SVG

适合大量可控文本与矢量装饰。

- 使用 `<foreignObject>` 或原生 `<text>`。
- 注意中文字体嵌入与运行环境。
- 不把字体文件随包分发。

## 方案 C：Pillow

适合批量自动化。

- 先计算文字换行与高度。
- 图片先统一裁剪、加白边、阴影和旋转。
- 纹理使用透明 PNG/WebP overlay。

## 纹理实现

不要只用一张纸纹贴图。建议组合：

- base fill
- subtle fiber noise
- low-opacity diagonal weave
- edge vignette
- inner 1px border
- soft cast shadow

## 导出

- PNG-24。
- 检查文件大小；公众号上传受限时另存 90–94% JPEG。
- 不改变画布宽高比。
