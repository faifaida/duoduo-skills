#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
duo-wear-painting · 插画去水印 + 品牌图文合成 (PIL)
把 ImageGen 出的插画：① 裁底去水印 ② 套品牌 40px 线描边框 + 母题角标 + 衬线标题 + DUODUO WEAR lockup
③ 输出目标尺寸。详见 SKILL.md / references/composition_specs.md。

用法：
  # 小红书知识卡片
  python3 compose_note.py --img illu.png --mode note --title "复利是一棵慢长的树" --subtitle "时间会替你长大" --out note.png
  # 公众号封面
  python3 compose_note.py --img illu.png --mode wechat --title "女性内在力量" --out cover.png
  # 口播讲解配图 (16:9)
  python3 compose_note.py --img illu.png --mode explain --title "这三点看懂边界感" --out explain.png
  # 透明 cutout（叠加口播视频用）
  python3 compose_note.py --img illu.png --mode cutout --out cutout.png

依赖：Pillow（default venv 已有）。字体自动探测（见 composition_specs.md）。
"""
import os
import sys
import math
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ===== 品牌色（来自 duoduo-design-system brand-dna.md）=====
TEAL       = (0x00, 0xB6, 0xC5)
TEAL_DEEP  = (0x0F, 0xA3, 0xB8)
OCEAN      = (0x1A, 0x9A, 0xA8)
SAND       = (0xC8, 0x9B, 0x6A)
CLAY       = (0xB5, 0x54, 0x3A)
OCHRE      = (0xC9, 0x90, 0x2E)
CREAM      = (0xF1, 0xE9, 0xDA)
CREAM_DEEP = (0xE8, 0xDC, 0xC8)
INK        = (0x2A, 0x26, 0x20)
INK_LIGHT  = (0x56, 0x4E, 0x42)
LINEN      = (0xF1, 0xE9, 0xDA)
NIGHT      = (0x15, 0x1A, 0x2E)
PAPER      = (0xFA, 0xF6, 0xEE)

CN_FONTS = [
    "/System/Library/Fonts/STSong.ttc",
    "/System/Library/Fonts/Supplemental/STSong.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]
EN_FONTS = [
    "/System/Library/Fonts/Supplemental/Baskerville.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "/System/Library/Fonts/Times.ttc",
]


def load_font(cands, size):
    for p in cands:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                try:
                    return ImageFont.truetype(p, size, index=0)
                except Exception:
                    continue
    sys.stderr.write("[compose_note] 警告: 未找到衬线字体，用默认字体\n")
    return ImageFont.load_default()


def remove_watermark(im):
    """ImageGen 输出底部带『图片由AI生成』水印，硬切底 50px。"""
    w, h = im.size
    if h > 60:
        im = im.crop((0, 0, w, h - 50))
    return im


def draw_sun(draw, cx, cy, r, color):
    """线描太阳母题（圆 + 射线），单色。"""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=max(2, int(r * 0.14)))
    rays = 12
    for i in range(rays):
        a = math.radians(i * (360.0 / rays))
        x1 = cx + math.cos(a) * r * 1.3
        y1 = cy + math.sin(a) * r * 1.3
        x2 = cx + math.cos(a) * r * 1.75
        y2 = cy + math.sin(a) * r * 1.75
        draw.line([x1, y1, x2, y2], fill=color, width=max(1, int(r * 0.10)))


def draw_lockup(draw, x, y, color, en_font, scale=1.0):
    """DUODUO WEAR 文字 lockup（英文衬线，全大写，字距靠空格模拟）。"""
    txt = "DUODUO WEAR"
    f = en_font
    draw.text((x, y), txt, font=f, fill=color)


def wrap_text(draw, text, font, max_w):
    """按像素宽度折行（中文按字、英文按词）。"""
    lines = []
    for para in text.split("\n"):
        cur = ""
        for ch in para:
            test = cur + ch
            if draw.textlength(test, font=font) <= max_w or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = ch
        lines.append(cur)
    return lines


def fit_font(draw, text, font, max_w, max_lines, min_size=20, start_size=64):
    """在 max_w / max_lines 约束下二分字号。"""
    lo, hi = min_size, start_size
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        f = ImageFont.truetype(font.path, mid) if hasattr(font, "path") else font
        # 重新用同族字体加载 mid 号
        f = _reload(font, mid)
        ls = wrap_text(draw, text, f, max_w)
        if len(ls) <= max_lines:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return _reload(font, best)


def _reload(font, size):
    # 用同路径重新加载指定字号
    for cands in (CN_FONTS, EN_FONTS):
        for p in cands:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    try:
                        return ImageFont.truetype(p, size, index=0)
                    except Exception:
                        continue
    return font


def place_illustration(canvas, im, box):
    """把插画 contain 进 box（x,y,w,h），居中，返回绘制后的画布。"""
    x, y, bw, bh = box
    im = remove_watermark(im)
    im = im.convert("RGB")
    iw, ih = im.size
    scale = min(bw / iw, bh / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    px = x + (bw - nw) // 2
    py = y + (bh - nh) // 2
    canvas.paste(im, (px, py))
    return canvas


# ---------- 各模式 ----------
def compose_note(im, title, subtitle, out):
    W, H = 1080, 1440
    canvas = Image.new("RGB", (W, H), LINEN)
    d = ImageDraw.Draw(canvas)
    # 40px 边框带
    d.rectangle([0, 0, W, 40], fill=CREAM_DEEP)
    d.rectangle([0, H - 40, W, H], fill=CREAM_DEEP)
    d.rectangle([0, 0, 40, H], fill=CREAM_DEEP)
    d.rectangle([W - 40, 0, W, H], fill=CREAM_DEEP)
    d.rectangle([40, 40, W - 40, H - 40], outline=INK, width=2)
    # 顶部品牌条
    draw_sun(d, 80, 90, 18, OCHRE)
    draw_lockup(d, 110, 78, INK, load_font(EN_FONTS, 22))
    # 主标题
    en = load_font(EN_FONTS, 30)
    cn = load_font(CN_FONTS, 30)
    ty = 150  # 标题起点；无标题时副文案从此处下推
    sy = 400  # 副文案/插画起点默认，标题块会下推它
    if title:
        tf = fit_font(d, title, cn, W - 140, 2, min_size=28, start_size=72)
        ls = wrap_text(d, title, tf, W - 140)
        ty = 150
        for ln in ls[:2]:
            d.text((70, ty), ln, font=tf, fill=INK)
            ty += int(tf.size * 1.25)
    # 副文案
    if subtitle:
        sf = load_font(CN_FONTS, 26)
        sls = wrap_text(d, subtitle, sf, W - 140)
        sy = ty + 10
        for ln in sls[:3]:
            d.text((70, sy), ln, font=sf, fill=INK_LIGHT)
            sy += int(sf.size * 1.9)
    # 中部插画
    place_illustration(canvas, im, (70, max(sy + 20, 400), W - 140, H - 400 - 60))
    canvas.save(out)
    return out


def compose_wechat(im, title, out):
    W, H = 900, 383
    canvas = Image.new("RGB", (W, H), NIGHT)
    im = remove_watermark(im).convert("RGB")
    im = im.resize((W, H), Image.LANCZOS)
    canvas.paste(im, (0, 0))
    d = ImageDraw.Draw(canvas)
    # 底部 scrim
    scrim = Image.new("RGB", (W, H), NIGHT)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rectangle([0, int(H * 0.45), W, H], fill=180)
    canvas = Image.composite(scrim, canvas, mask)
    d = ImageDraw.Draw(canvas)
    if title:
        tf = load_font(CN_FONTS, 40)
        ls = wrap_text(d, title, tf, W - 80)
        ty = H - 30 - int(tf.size * 1.3 * min(len(ls), 2))
        for ln in ls[:2]:
            d.text((40, ty), ln, font=tf, fill=PAPER)
            ty += int(tf.size * 1.3)
    draw_lockup(d, W - 200, H - 34, PAPER, load_font(EN_FONTS, 18))
    canvas.save(out)
    return out


def compose_explain(im, title, out, square=False):
    if square:
        W, H = 1080, 1080
    else:
        W, H = 1280, 720
    canvas = Image.new("RGB", (W, H), LINEN)
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, 30], fill=CREAM_DEEP)
    d.rectangle([0, H - 30, W, H], fill=CREAM_DEEP)
    place_illustration(canvas, im, (40, 40, W - 80, H - 160))
    if title:
        tf = load_font(CN_FONTS, 38)
        ls = wrap_text(d, title, tf, W - 80)
        ty = H - 140
        for ln in ls[:2]:
            d.text((40, ty), ln, font=tf, fill=INK)
            ty += int(tf.size * 1.3)
    canvas.save(out)
    return out


def compose_cutout(im, out):
    im = remove_watermark(im)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    im.save(out)
    return out


def main():
    ap = argparse.ArgumentParser(description="DUODUO WEAR 插画合成")
    ap.add_argument("--img", required=True, help="插画 PNG（ImageGen 输出）")
    ap.add_argument("--mode", required=True, choices=["note", "wechat", "explain", "cutout"])
    ap.add_argument("--title", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--square", action="store_true", help="explain 模式用 1:1")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    im = Image.open(args.img)
    if args.mode == "note":
        compose_note(im, args.title, args.subtitle, args.out)
    elif args.mode == "wechat":
        compose_wechat(im, args.title, args.out)
    elif args.mode == "explain":
        compose_explain(im, args.title, args.out, square=args.square)
    elif args.mode == "cutout":
        compose_cutout(im, args.out)
    print(f"[done] {args.out}")


if __name__ == "__main__":
    main()
