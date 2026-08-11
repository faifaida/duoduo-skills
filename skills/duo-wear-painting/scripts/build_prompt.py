#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
duo-wear-painting · 插画 prompt 拼装器
把「概念 + 品牌风格锁」拼成完整 ImageGen prompt，打印到 stdout（agent 复制后调用 ImageGen 工具）。

用法：
  python3 build_prompt.py --concept "解释'复利'像种一棵慢长的树" --style watercolor
  python3 build_prompt.py --concept "女性内在力量" --style woodcut --cutout
  python3 build_prompt.py --concept "..." --style inkline --extra "minimal, lots of negative space" --out prompt.txt

风格锁与 references/style_prompt.md 保持一致（改风格两处同步）。
"""
import argparse
import sys

# ===== 品牌风格锁（与 references/style_prompt.md 同步）=====
STYLE_LOCK = (
    "Editorial illustration, painterly hand-drawn style, DUODUO WEAR brand aesthetic: "
    "wild yet gentle, primal yet refined, handcrafted with worldliness. "
    "Palette locked to teal #00B6C5 / deep teal #0FA3B8 / ocean #1A9AA8 with warm linen #F1E9DA / #E8DCC8, "
    "ochre #C9902E used sparingly (<=10%) as spiritual accent, clay #B5543A as minor accent. "
    "Line-drawn spiritual / nature / tribal motifs (sun, moon, mandala, waves, vines, "
    "woman-and-animal single-line) in single ink or ochre stroke. "
    "All overlaid text in serif (Baskerville / Noto Serif SC). "
    "Flat or subtly textured paper feel. "
    "NO photorealism, NO 3D render, NO neon, NO blue-purple gradient, NO AI glossy stock-photo look. "
    "Composition breathes, asymmetric tension, not a centered template grid."
)

NEGATIVE = (
    "no photorealistic photo, no 3D render, no CGI, no neon, no blue-purple gradient, "
    "no pure black or pure white large areas, no glassmorphism, no AI glow effects, "
    "no watermark, no signature, no text in image unless requested, "
    "no generic AI template look, no centered symmetric stock layout"
)

STYLE_VARIANTS = {
    "inkline": "Fine ink line-art illustration, single-weight strokes, minimal flat color fills, woodcut/etching feel.",
    "watercolor": "Loose watercolor wash illustration, visible paper texture, soft bleeds, editorial magazine feel.",
    "woodcut": "Bold woodcut / linocut print illustration, high contrast, carved texture, primal tribal energy.",
    "flat": "Flat vector-ish editorial illustration with limited palette, clean shapes, modern folk-art feel.",
}

CUTOUT_ADD = "Transparent background, isolated subject, no background, clean alpha edges, PNG."


def build(concept, style, cutout, extra):
    if style not in STYLE_VARIANTS:
        raise SystemExit(f"[build_prompt] 未知 style={style!r}，可选: {list(STYLE_VARIANTS)}")
    parts = [STYLE_LOCK, STYLE_VARIANTS[style], f"Subject: {concept}"]
    if cutout:
        parts.append(CUTOUT_ADD)
    if extra:
        parts.append(extra)
    prompt = " ".join(parts)
    neg = "Negative: " + NEGATIVE
    return prompt, neg


def main():
    ap = argparse.ArgumentParser(description="DUODUO WEAR 插画 prompt 拼装器")
    ap.add_argument("--concept", required=True, help="要画的subject/概念")
    ap.add_argument("--style", default="inkline",
                    choices=list(STYLE_VARIANTS), help="插画风格变体")
    ap.add_argument("--cutout", action="store_true", help="加透明背景句（口播叠加用）")
    ap.add_argument("--extra", default="", help="额外风格补充")
    ap.add_argument("--out", default="", help="把 prompt 写到该文件（同时仍打印）")
    args = ap.parse_args()

    prompt, neg = build(args.concept, args.style, args.cutout, args.extra)
    full = prompt + "\n" + neg
    print(full)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(full)
        print(f"\n[written] {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
