#!/usr/bin/env python3
"""
DUODUO WEAR 海报合成脚本
把 ImageGen 生成的主体图，统一叠加底部 linen footer + DUODUO WEAR logo。
确保所有输出的 logo 位置、footer 渐变、颜色完全一致。
"""

from PIL import Image
import argparse
import os
import sys


def overlay_footer(
    input_path: str,
    output_path: str,
    layout: str = "flatlay",
    target_width: int = 768,
    target_height: int = 1074,
    band_path: str | None = None,
    fade_height: int = 36,
):
    """
    将输入图 resize 到目标尺寸，底部叠加 logo_band。

    参数:
        input_path: ImageGen 生成的主体图路径
        output_path: 最终输出路径
        layout: flatlay 或 hero（目前仅影响缩放策略）
        target_width: 输出宽度
        target_height: 输出高度
        band_path: logo_band 图片路径，默认取脚本所在目录 assets/logo_band_768x134.png
        fade_height: 顶部渐变融合高度（像素）
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if band_path is None:
        band_path = os.path.join(base_dir, "assets", "logo_band_768x134.png")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入图不存在: {input_path}")
    if not os.path.exists(band_path):
        raise FileNotFoundError(f"logo_band 不存在: {band_path}")

    src = Image.open(input_path).convert("RGB")
    band = Image.open(band_path).convert("RGBA")

    # 将主体图 resize 到目标尺寸（保持比例裁剪/填充）
    src_ratio = src.width / src.height
    out_ratio = target_width / target_height

    if abs(src_ratio - out_ratio) < 0.001:
        src = src.resize((target_width, target_height), Image.LANCZOS)
    else:
        # 等比缩放并按 center crop 裁切
        if src_ratio > out_ratio:
            new_height = target_height
            new_width = int(src_ratio * target_height)
        else:
            new_width = target_width
            new_height = int(target_width / src_ratio)
        src = src.resize((new_width, new_height), Image.LANCZOS)
        left = (src.width - target_width) // 2
        top = (src.height - target_height) // 2
        src = src.crop((left, top, left + target_width, top + target_height))

    # 确保尺寸精确
    canvas = Image.new("RGB", (target_width, target_height), "#F1E9DA")
    canvas.paste(src, (0, 0))

    # 将 band resize 到目标宽度
    band_h = int(band.height * (target_width / band.width))
    band = band.resize((target_width, band_h), Image.LANCZOS)

    # 渐变蒙版：band 顶部 fade_height 像素做透明渐变
    mask = Image.new("L", (target_width, band_h), 255)
    if fade_height > 0 and fade_height < band_h:
        for y in range(fade_height):
            alpha = int(255 * (y / fade_height))
            for x in range(target_width):
                mask.putpixel((x, y), alpha)

    # 计算 band 贴到底部的位置
    band_top = target_height - band_h

    # 先把 band 区域从 canvas 上切下来做底，再贴 band
    # 但由于有渐变，直接 paste band 用 mask 即可
    canvas.paste(band, (0, band_top), mask)

    # 输出
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    canvas.save(output_path, "PNG")
    print(f"Saved: {output_path}  ({canvas.width}x{canvas.height})")


def main():
    parser = argparse.ArgumentParser(description="DUODUO WEAR poster composer")
    parser.add_argument("--input", "-i", required=True, help="ImageGen generated subject image")
    parser.add_argument("--output", "-o", required=True, help="Output final poster PNG path")
    parser.add_argument("--layout", "-l", choices=["flatlay", "hero"], default="flatlay")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=1074)
    parser.add_argument("--band", help="Custom logo band PNG path")
    parser.add_argument("--fade", type=int, default=36, help="Top fade height in px")
    args = parser.parse_args()

    overlay_footer(
        input_path=args.input,
        output_path=args.output,
        layout=args.layout,
        target_width=args.width,
        target_height=args.height,
        band_path=args.band,
        fade_height=args.fade,
    )


if __name__ == "__main__":
    main()
