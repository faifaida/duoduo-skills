"""WEAR season graph v7: using the actual brand Shell Bird (rough totem style).
Clean each generated bird (remove text/watermark), standardize colors, compose 2x2.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = "C:/Users/Administrator/WorkBuddy/2026-07-29-04-33-04/generated-images"
OUT = os.path.join(BASE, "wear_season_graph_birds_v7.png")
LOGO = "C:/Users/Administrator/.workbuddy/skills/duoduo-design-system/assets/brand/current/duoduo-wear-full-logo.jpeg"

# Unified WEAR brand colors (logo's actual background beige is the authority)
BEIGE = np.array([230, 206, 184], dtype=np.uint8)   # #E6CEB8
BLUE = np.array([46, 39, 168], dtype=np.uint8)      # #2E27A8

FONTS = [
    r"C:/Windows/Fonts/simsun.ttc",
    r"C:/Windows/Fonts/STSong.ttf",
]

def find_font(size):
    for f in FONTS:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def clean_bird(path, bottom_crop_pct=0.10):
    """Load generated bird, remove text/watermark, standardize to 2 colors."""
    im = Image.open(path).convert("RGB")
    a = np.array(im)
    h, w = a.shape[:2]

    # Define clean region: mask out known text/watermark areas
    mask = np.ones((h, w), dtype=bool)
    # bottom band (text/watermark)
    if bottom_crop_pct > 0:
        band_h = int(h * bottom_crop_pct)
        mask[h - band_h:, :] = False
    # bottom-right watermark corner
    wm_h = int(h * 0.10)
    wm_w = int(w * 0.12)
    mask[h - wm_h:, w - wm_w:] = False

    # Classify pixels: blue-purple foreground vs background
    is_blue = (
        (a[:,:,0] < 100) & (a[:,:,1] < 100) & (a[:,:,2] > 80) &
        (a[:,:,2] > a[:,:,0] * 1.2) & (a[:,:,2] > a[:,:,1] * 1.2)
    )
    # Also accept near-brand-blue
    is_blue |= (np.abs(a.astype(int) - BLUE).sum(2) < 120)

    # Only keep blue pixels in clean region
    clean_blue = is_blue & mask

    # Remove small noise (watermark fragments, specks)
    from scipy import ndimage
    cleaned, n = ndimage.label(clean_blue)
    if n > 0:
        sizes = ndimage.sum(clean_blue, cleaned, range(1, n + 1))
        # keep components larger than 50 pixels
        keep = sizes > 50
        bird_mask = keep[cleaned - 1] & (cleaned > 0)
    else:
        bird_mask = clean_blue

    # Create output
    out = np.full((h, w, 3), BEIGE, dtype=np.uint8)
    out[bird_mask] = BLUE

    # Crop to content bbox
    ys, xs = np.where(bird_mask)
    if len(xs) == 0:
        return Image.fromarray(out)
    pad = 10
    x1 = max(0, xs.min() - pad)
    y1 = max(0, ys.min() - pad)
    x2 = min(w, xs.max() + pad)
    y2 = min(h, ys.max() + pad)
    return Image.fromarray(out[y1:y2, x1:x2])

def main():
    W, H = 1080, 1440
    canvas = Image.new("RGBA", (W, H), (*BEIGE, 255))
    draw = ImageDraw.Draw(canvas)

    font_title = find_font(56)
    font_label = find_font(42)

    birds = [
        # (label, path, bottom_crop_pct)
        ("春", os.path.join(BASE, "wear_birds_v7/fly_v2/Primitive_rough_cave_painting__2026-08-08T17-12-19.png"), 0.08),
        ("夏", os.path.join(BASE, "wear_birds_v7/walk_v3/Primitive_rough_hand_carved_wo_2026-08-08T17-28-41.png"), 0.00),
        ("秋", os.path.join(BASE, "wear_birds_v7/lie_v2/Primitive_rough_cave_painting__2026-08-08T17-13-17.png"), 0.08),
        ("冬", os.path.join(BASE, "wear_birds_v7/jacket_v4/Primitive_rough_hand_carved_wo_2026-08-08T17-23-25.png"), 0.18),
    ]

    margin = 70
    gap = 40
    panel_w = (W - 2 * margin - gap) // 2
    panel_h = (H - 240 - 160 - gap) // 2  # leave room for title and logo band
    title_h = 120
    band_h = 140

    positions = [
        (margin, title_h),
        (margin + panel_w + gap, title_h),
        (margin, title_h + panel_h + gap),
        (margin + panel_w + gap, title_h + panel_h + gap),
    ]

    for (label, path, bottom_crop), (px, py) in zip(birds, positions):
        # panel bg + border
        draw.rounded_rectangle([px, py, px + panel_w, py + panel_h], radius=18,
                               outline=(*BLUE, 255), width=2)

        # load and scale bird
        bird = clean_bird(path, bottom_crop_pct=bottom_crop)
        bw, bh = bird.size
        scale = min((panel_w - 80) / bw, (panel_h - 120) / bh)
        new_size = (int(bw * scale), int(bh * scale))
        bird = bird.resize(new_size, Image.LANCZOS)

        # center in panel (slightly above label)
        bx = px + (panel_w - new_size[0]) // 2
        by = py + (panel_h - new_size[1]) // 2 - 20
        canvas.paste(bird, (bx, by))

        # label at bottom center
        pb = py + panel_h
        draw.text((px + panel_w // 2, pb - 42), label, font=font_label,
                  fill=(*BLUE, 255), anchor="mm")

    # title
    draw.text((W // 2, 58), "你的肤色分四季", font=font_title, fill=(*BLUE, 255), anchor="mm")

    # logo band at bottom
    band = Image.new("RGBA", (W, band_h), (*BEIGE, 255))
    logo = Image.open(LOGO).convert("RGBA")
    # key out logo's beige background
    la = np.array(logo)
    bg = (la[:,:,0] > 150) & (la[:,:,1] > 130) & (la[:,:,2] > 110) & ((la[:,:,0] - la[:,:,2]) < 80)
    la[bg] = [230, 206, 184, 0]
    logo = Image.fromarray(la, "RGBA")
    # scale logo to fit band
    lw, lh = logo.size
    scale = min(W * 0.18 / lw, band_h * 0.70 / lh)
    logo = logo.resize((int(lw * scale), int(lh * scale)), Image.LANCZOS)
    lx = (W - logo.width) // 2
    ly = (band_h - logo.height) // 2
    band.paste(logo, (lx, ly), logo)
    canvas.paste(band, (0, H - band_h))

    # save as RGB
    canvas.convert("RGB").save(OUT)
    print("saved", OUT)

if __name__ == "__main__":
    main()
