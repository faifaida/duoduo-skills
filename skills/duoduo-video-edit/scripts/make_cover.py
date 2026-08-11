#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DUODUO WEAR 通用封面生成器 —— 规范模板 (canonical cover template).

设计语言锁定自 ep1 (Film01) 最终定稿封面 Film01_Cover_Final.jpg:
  - 背景: 真实照片 / 真实帧 (★禁 AI 生图★)
  - 底部米色渐变带 (cream, 底部最实, 与照片平滑过渡、无分隔线)
  - 完整 logo lockup: 徽标(emblem) + 全大写 DUODUO WEAR 字标(wordmark) 并排一行 (不是只放图形)
  - 标题: 衬线体 (Baskerville/Georgia 英文 · Songti 中文), 米白 fill + 暖墨阴影, 放天空/上方可见区
  - 非 9:16 封面用 scale→cover 再 center-crop, 绝不 resize 直接拉 (会变形!)

★ 所有 DUODUO WEAR 视频封面必须用本脚本生成。禁止: AI 背景图 / 白字标题(必须用米白+暖墨) /
  只放图形不放字标。改下面常量即可出下一条视频的封面。

品牌 token 取自 duoduo-design-system/brand-dna.md。
"""
import os
import sys
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ============================ 可编辑常量（每条视频改这里） ============================
PROJ  = "/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/03_ACTIVE PROJECTS/ai个人公司/公司档案/09_泳衣品牌导演/Film02_Production/"
# 背景必须是真实照片/真实帧；这里用 ep1 同款真实泳衣侧脸照（无脸安全）。换 Film02 自己的真实帧时改这行。
# 🚫🚫🚫 封面「永不撞图」铁律 🚫🚫🚫：
#   每条 Film 的封面背景必须是【各自独有】的真实照片/真实帧，互不相同。
#   绝不可沿用 IMG_8208（ep2 已用）、SL2604 微笑帧（ep5 已用）或任何别的 Film 用过的图。
#   复制本模板出下一条片时，第一件事就是改成该片自己的背景；排版可克隆，背景必须换。
PHOTO = "/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/03_ACTIVE PROJECTS/ai个人公司/公司档案/09_泳衣品牌导演/_face_id/refs_raw/IMG_8208.jpg"
# —— 防撞图注册表（机械护栏）——
# FILM_ID / PHOTO_SOURCE 复制模板出下一条片时必须改成当前片自己的；否则下方 check_cover_collision() 直接报错退出。
FILM_ID      = "Film02"   # ← 改成当前片编号（如 Film03）
PHOTO_SOURCE = PHOTO      # ← 背景原始素材（照片原图 或 抽帧视频 clip，不是抽出的 png）。改 PHOTO 时一起改。
LOGO  = "/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/03_ACTIVE PROJECTS/ai个人公司/泳衣品牌建设/duoduowear 品牌logo.jpeg"

TITLE    = "Not to be seen — to be living."   # 英文钩子主标题（衬线米白，天空区）
SUBTITLE = "泳衣不是为了被看见"                 # 中文副标（衬线暖墨，主标下方）
RULES    = ""                                  # 可选小字（留空则不画）；ep1 极简无此行

W_UNIV, H_UNIV = 1080, 1350                     # 通用 4:5
# =====================================================================================

# 品牌 token
CREAM_DEEP = np.array([232, 220, 200], dtype=np.float32)   # #E8DCC8
CREAM      = np.array([241, 233, 218], dtype=np.float32)   # #F1E9DA
INK        = (42, 38, 32)                                 # #2A2620 暖墨
CREAM_W    = (241, 233, 218)                              # 米白(标题)
PEAK_ALPHA = 255

def load_serif(size, cjk=False):
    paths = (["/System/Library/Fonts/Supplemental/Songti.ttc"] if cjk
             else ["/System/Library/Fonts/Supplemental/Baskerville.ttc",
                   "/System/Library/Fonts/Supplemental/Georgia.ttf"])
    for p in paths:
        try:
            return ImageFont.truetype(p, size, index=0)
        except Exception:
            continue
    return ImageFont.load_default()

def to_rgba(im, ref=(232, 206, 183), thr=45):
    arr = np.array(im).astype(np.int16)
    d = np.sqrt(((arr - np.array(ref)) ** 2).sum(2))
    a = np.where(d < thr, 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([arr.astype(np.uint8), a]), "RGBA")

def tight_crop(im_rgba):
    a = np.array(im_rgba)[:, :, 3]
    ys, xs = np.where(a > 0)
    if len(ys) == 0:
        return im_rgba
    return im_rgba.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

def apply_cover_grade(im):
    """统一封面调色（所有 DUODUO WEAR 封面共用，保证主页色调一致）：
    轻微提亮 + 降对比柔光 + 微降饱和 + 暖调偏移，海景/人物都更干净柔和。"""
    from PIL import ImageFilter, ImageEnhance
    im = ImageEnhance.Brightness(im).enhance(1.05)
    im = ImageEnhance.Contrast(im).enhance(0.96)
    im = ImageEnhance.Color(im).enhance(0.90)
    arr = np.array(im).astype(np.int16)
    arr[:, :, 0] = np.clip(arr[:, :, 0] + 8, 0, 255)   # 暖调 R+
    arr[:, :, 2] = np.clip(arr[:, :, 2] - 6, 0, 255)   # 冷调 B-
    im = Image.fromarray(arr.astype(np.uint8), "RGB")
    blur = im.filter(ImageFilter.GaussianBlur(16))
    im = Image.blend(im, blur, 0.16)                   # 轻柔光
    return im

def build_universal():
    # 1) 真实照片铺满 4:5（等比 scale 到宽1080→高1920，再裁掉上半部保留底部1350，不变形）
    photo = Image.open(PHOTO).convert("RGB")
    ph_full = int(round(photo.height * W_UNIV / photo.width))
    photo = photo.resize((W_UNIV, ph_full), Image.LANCZOS)
    photo = photo.crop((0, ph_full - H_UNIV, W_UNIV, ph_full))   # 截顶，保留底
    photo = apply_cover_grade(photo)                           # 统一封面调色（主页一致）
    base = np.array(photo).astype(np.float32)

    # 2) 顶部轻微暗角 scrim（仅保证标题可读，不改变设计；alpha 低）
    scrim = np.zeros((H_UNIV, W_UNIV, 4), dtype=np.float32)
    for y in range(0, int(H_UNIV * 0.34)):
        t = 1 - y / (H_UNIV * 0.34)
        scrim[y, :, :3] = 30
        scrim[y, :, 3] = 70 * t
    canvas = Image.fromarray(base.astype(np.uint8), "RGB").convert("RGBA")
    canvas = Image.alpha_composite(canvas, Image.fromarray(scrim.astype(np.uint8), "RGBA"))

    # 3) 底部米色渐变带 (与照片平滑过渡，顶部无暗分隔线)
    band_h = int(H_UNIV * 0.26)
    band_top = H_UNIV - band_h
    overlay = np.zeros((H_UNIV, W_UNIV, 4), dtype=np.float32)
    for y in range(band_top, H_UNIV):
        t = (y - band_top) / band_h
        col = CREAM_DEEP * (1 - t) + CREAM * t
        a = PEAK_ALPHA * min(1.0, t * 2.2)
        overlay[y, :, :3] = col
        overlay[y, :, 3] = a
    canvas = Image.alpha_composite(canvas, Image.fromarray(overlay.astype(np.uint8), "RGBA"))
    d = ImageDraw.Draw(canvas)

    # 4) 标题（衬线米白 + 暖墨阴影，天空区）
    tsize = 74
    while tsize > 38:
        tf = load_serif(tsize)
        if d.textlength(TITLE, font=tf) <= 1000:
            break
        tsize -= 2
    tf = load_serif(tsize)
    title_cy = 250
    d.text((W_UNIV / 2 + 2, title_cy + 3), TITLE, font=tf, fill=INK + (190,), anchor="mm")
    d.text((W_UNIV / 2, title_cy), TITLE, font=tf, fill=CREAM_W, anchor="mm")
    # 中文副标（衬线米白，与英文主标统一；带暖墨阴影保证可读）
    if SUBTITLE:
        sf = load_serif(46, cjk=True)
        d.text((W_UNIV / 2 + 2, title_cy + tsize * 0.85 + 3), SUBTITLE, font=sf, fill=INK + (190,), anchor="mm")
        d.text((W_UNIV / 2, title_cy + tsize * 0.85), SUBTITLE, font=sf, fill=CREAM_W, anchor="mm")
    # 可选小字
    if RULES:
        rf = load_serif(30, cjk=True)
        d.text((W_UNIV / 2, title_cy + tsize * 0.85 + 60), RULES, font=rf, fill=INK, anchor="mm")

    # 5) 完整 logo lockup（徽标 + 字标 并排）
    logo_full = Image.open(LOGO).convert("RGB")
    emblem_raw = logo_full.crop((0, 70, logo_full.width, 762))
    word_raw   = logo_full.crop((0, 792, logo_full.width, 928))
    emblem = tight_crop(to_rgba(emblem_raw))
    word   = tight_crop(to_rgba(word_raw))
    EH = 140
    ew = int(emblem.width * EH / emblem.height)
    emblem = emblem.resize((ew, EH), Image.LANCZOS)
    WH = 77
    ww = int(word.width * WH / word.height)
    word = word.resize((ww, WH), Image.LANCZOS)
    gap = 26
    total_w = ew + gap + ww
    if total_w > 900:
        sc = 900.0 / total_w
        ew, EH = int(ew * sc), int(EH * sc)
        ww, WH = int(ww * sc), int(WH * sc)
        emblem = emblem.resize((ew, EH), Image.LANCZOS)
        word = word.resize((ww, WH), Image.LANCZOS)
        total_w = ew + gap + ww
    cx = W_UNIV / 2
    row_cy = 1200
    ex = int(cx - total_w / 2)
    ey = int(row_cy - EH / 2)
    canvas = canvas.convert("RGBA")
    canvas.paste(emblem, (ex, ey), emblem)
    wx = ex + ew + gap
    wy = int(row_cy - WH / 2)
    canvas.paste(word, (wx, wy), word)
    return canvas.convert("RGB")

def cover_crop(src, tw, th):
    sw, sh = src.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    s = src.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return s.crop((left, top, left + tw, top + th))

# —— 封面背景唯一性机械护栏 ——
REGISTRY_PATH = "/Users/Zhuanz/.workbuddy/skills/duoduo-video-edit/scripts/cover_photo_registry.json"
TEMPLATE_DEFAULT_PHOTO = "/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/03_ACTIVE PROJECTS/ai个人公司/公司档案/09_泳衣品牌导演/_face_id/refs_raw/IMG_8208.jpg"

def _norm(p):
    try: return os.path.realpath(p)
    except Exception: return os.path.abspath(p)
def _load_reg():
    try: return json.load(open(REGISTRY_PATH, encoding="utf-8"))
    except Exception: return {}
def _save_reg(reg):
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    json.dump(reg, open(REGISTRY_PATH, "w"), ensure_ascii=False, indent=2)
def check_cover_collision():
    # 1) 模板默认背景（IMG_8208=ep2）只允许 Film02 自己用；其它片复制模板忘了改 → 直接报错
    if _norm(PHOTO_SOURCE) == _norm(TEMPLATE_DEFAULT_PHOTO) and FILM_ID != "Film02":
        sys.exit("❌ [封面撞图防护] PHOTO_SOURCE 还是模板默认(IMG_8208=ep2背景)！复制模板出下一条片必须把 PHOTO 和 PHOTO_SOURCE 都改成当前片自己的背景。")
    # 2) 注册表：任何已登记给别的片的背景一律不得复用
    reg = _load_reg()
    for fid, src in reg.items():
        if fid != FILM_ID and _norm(src) == _norm(PHOTO_SOURCE):
            used = "\n  ".join(f"{k} -> {v}" for k, v in reg.items())
            sys.exit(f"❌ [封面撞图防护] 背景素材 {PHOTO_SOURCE}\n    已被 {fid} 用过！封面背景必须每条片独有。\n已登记：\n  {used}")
    print(f"[guard] 封面背景唯一性 OK —— {FILM_ID} 用 {PHOTO_SOURCE}")
def register_cover():
    reg = _load_reg()
    reg[FILM_ID] = PHOTO_SOURCE
    _save_reg(reg)
    print(f"[guard] 已登记 {FILM_ID} 背景 -> {PHOTO_SOURCE}")

def main():
    check_cover_collision()
    uni = build_universal()
    out_uni = os.path.join(PROJ, "Film02_Cover_Final.jpg")
    uni.save(out_uni, "JPEG", quality=95)
    print("[OK] Final 4:5 ->", out_uni, uni.size)
    variants = {
        "Film02_Cover_9x16.jpg": (1080, 1920),
        "Film02_Cover_XHS.jpg": (1080, 1440),       # 小红书 3:4
        "Film02_Cover_Douyin.jpg": (1080, 1920),    # 抖音 9:16
        "Film02_Cover_IG.jpg": (1080, 1350),        # Instagram 4:5
        "Film02_Cover_Shipinhao.jpg": (1080, 1080), # 视频号 1:1
    }
    for name, (tw, th) in variants.items():
        crop = cover_crop(uni, tw, th)
        p = os.path.join(PROJ, name)
        crop.save(p, "JPEG", quality=92)
        print(f"[OK] {name} ({tw}x{th})")
    # 自检
    c = np.array(uni)
    print("--- self-check ---")
    print("顶部中心(应=照片/暗角):", c[80, 540].tolist())
    print("底部中心(应≈米色实心):", c[1320, 540].tolist())
    print("带顶过渡区(y=1002, 应≈照片无暗线):", c[1002, 540].tolist())
    register_cover()

if __name__ == "__main__":
    main()
