"""WEAR validation: Excalidraw-style hand-drawn skeleton + brand Shell Bird IP.

Discipline-aligned workflow:
- Structure / flow / arrows = hand-drawn rough skeleton (Excalidraw look), drawn in code.
- Bird IP = approved Shell Bird totem (v7 cutouts, 2-color #E6CEB8 + #2E27A8).
- Brand text + formal logo band = program-added (never drawn by image model).
- Also exports a real .excalidraw source (skeleton only) so the user can tweak in Excalidraw app.
"""
import os
import json
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = "C:/Users/Administrator/WorkBuddy/2026-07-29-04-33-04/generated-images"
OUT_PNG = os.path.join(BASE, "wear_excalidraw_validation.png")
OUT_EX = os.path.join(BASE, "wear_excalidraw_validation.excalidraw")
LOGO = "C:/Users/Administrator/.workbuddy/skills/duoduo-design-system/assets/brand/current/duoduo-wear-full-logo.jpeg"

BEIGE = np.array([230, 206, 184], dtype=np.uint8)   # #E6CEB8
BLUE = np.array([46, 39, 168], dtype=np.uint8)      # #2E27A8
BEIGE_RGB = (230, 206, 184)
BLUE_RGB = (46, 39, 168)

FONTS = [r"C:/Windows/Fonts/simsun.ttc", r"C:/Windows/Fonts/STSong.ttf"]
def find_font(size):
    for f in FONTS:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()

# ---------- bird cleanup (reuse v7 logic) ----------
def clean_bird(path, bottom_crop_pct=0.10):
    im = Image.open(path).convert("RGB")
    a = np.array(im)
    h, w = a.shape[:2]
    mask = np.ones((h, w), dtype=bool)
    if bottom_crop_pct > 0:
        band_h = int(h * bottom_crop_pct)
        mask[h - band_h:, :] = False
    wm_h = int(h * 0.10); wm_w = int(w * 0.12)
    mask[h - wm_h:, w - wm_w:] = False
    is_blue = ((a[:,:,0] < 100) & (a[:,:,1] < 100) & (a[:,:,2] > 80) &
               (a[:,:,2] > a[:,:,0] * 1.2) & (a[:,:,2] > a[:,:,1] * 1.2))
    is_blue |= (np.abs(a.astype(int) - BLUE).sum(2) < 120)
    clean_blue = is_blue & mask
    from scipy import ndimage
    cleaned, n = ndimage.label(clean_blue)
    if n > 0:
        sizes = ndimage.sum(clean_blue, cleaned, range(1, n + 1))
        keep = sizes > 50
        bird_mask = keep[cleaned - 1] & (cleaned > 0)
    else:
        bird_mask = clean_blue
    out = np.full((h, w, 3), BEIGE, dtype=np.uint8)
    out[bird_mask] = BLUE
    ys, xs = np.where(bird_mask)
    if len(xs) == 0:
        return Image.fromarray(out)
    pad = 10
    x1 = max(0, xs.min() - pad); y1 = max(0, ys.min() - pad)
    x2 = min(w, xs.max() + pad); y2 = min(h, ys.max() + pad)
    return Image.fromarray(out[y1:y2, x1:x2])

# ---------- rough (Excalidraw-style) drawing ----------
def rough_line(draw, p1, p2, fill, width=2, seed=0, overshoot=5):
    rnd = random.Random(seed)
    dx = p2[0]-p1[0]; dy = p2[1]-p1[1]
    L = (dx*dx + dy*dy) ** 0.5
    if L == 0:
        return
    nx, ny = -dy/L, dx/L
    for _ in range(2):
        ox1 = p1[0] - dx/L*overshoot*rnd.uniform(0.4, 1.0)
        oy1 = p1[1] - dy/L*overshoot*rnd.uniform(0.4, 1.0)
        ox2 = p2[0] + dx/L*overshoot*rnd.uniform(0.4, 1.0)
        oy2 = p2[1] + dy/L*overshoot*rnd.uniform(0.4, 1.0)
        steps = 7
        pts = []
        for i in range(steps + 1):
            t = i/steps
            bx = ox1 + (ox2-ox1)*t
            by = oy1 + (oy2-oy1)*t
            if 0 < i < steps:
                j = rnd.uniform(-2.5, 2.5)
                bx += nx*j; by += ny*j
            pts.append((bx, by))
        draw.line(pts, fill=fill, width=width, joint="curve")

def rough_rect(draw, box, fill, width=2, seed=0):
    x1, y1, x2, y2 = box
    rough_line(draw, (x1, y1), (x2, y1), fill, width, seed+1, overshoot=7)
    rough_line(draw, (x2, y1), (x2, y2), fill, width, seed+2, overshoot=7)
    rough_line(draw, (x2, y2), (x1, y2), fill, width, seed+3, overshoot=7)
    rough_line(draw, (x1, y2), (x1, y1), fill, width, seed+4, overshoot=7)

def rough_arrow(draw, p1, p2, fill, width=2, seed=0, overshoot=5):
    rough_line(draw, p1, p2, fill, width, seed, overshoot)
    # arrowhead at p2
    dx = p2[0]-p1[0]; dy = p2[1]-p1[1]
    L = (dx*dx + dy*dy) ** 0.5
    if L == 0:
        return
    ux, uy = dx/L, dy/L
    nx, ny = -uy, ux
    hl = 22
    for s in (-1, 1):
        tip1 = (p2[0] - ux*hl + nx*hl*0.6*s, p2[1] - uy*hl + ny*hl*0.6*s)
        rough_line(draw, p2, tip1, fill, max(1, width-1), seed+10+abs(s), overshoot=0)

# ---------- layout ----------
W, H = 1080, 1440
margin = 70
gap = 56
cell_w = (W - 2*margin - gap) // 2
title_h = 150
band_h = 160
cell_h = (H - title_h - band_h - gap) // 2

cells = {
    "春": (margin, title_h),
    "夏": (margin + cell_w + gap, title_h),
    "秋": (margin, title_h + cell_h + gap),
    "冬": (margin + cell_w + gap, title_h + cell_h + gap),
}
bird_paths = {
    "春": os.path.join(BASE, "wear_birds_v7/fly_v2/Primitive_rough_cave_painting__2026-08-08T17-12-19.png"),
    "夏": os.path.join(BASE, "wear_birds_v7/walk_v3/Primitive_rough_hand_carved_wo_2026-08-08T17-28-41.png"),
    "秋": os.path.join(BASE, "wear_birds_v7/lie_v2/Primitive_rough_cave_painting__2026-08-08T17-13-17.png"),
    "冬": os.path.join(BASE, "wear_birds_v7/jacket_v4/Primitive_rough_hand_carved_wo_2026-08-08T17-23-25.png"),
}
bird_crop = {"春": 0.08, "夏": 0.00, "秋": 0.08, "冬": 0.18}

# arrows (four-season cycle): 春→夏 (right), 夏→秋 (down), 秋→冬 (right), 冬→春 (left spine up)
def cx(name): return cells[name][0] + cell_w//2
def cy(name): return cells[name][1] + cell_h//2
arrows = [
    (("春", "夏"), ((cells["春"][0]+cell_w, cy("春")), (cells["夏"][0]-2, cy("夏")))),
    (("夏", "秋"), ((cx("夏"), cells["夏"][1]+cell_h), (cx("秋"), cells["秋"][1]-2))),
    (("秋", "冬"), ((cells["秋"][0]+cell_w, cy("秋")), (cells["冬"][0]-2, cy("冬")))),
    (("冬", "春"), ((40, cells["冬"][1]+cell_h+10), (40, cells["春"][1]+10))),
]

def main():
    canvas = Image.new("RGBA", (W, H), (*BEIGE_RGB, 255))
    draw = ImageDraw.Draw(canvas)

    # hand-drawn frames (Excalidraw skeleton)
    seed = 100
    for name, (x, y) in cells.items():
        rough_rect(draw, (x, y, x+cell_w, y+cell_h), BLUE_RGB, width=2, seed=seed)
        seed += 7

    # arrows
    for (pair, (p1, p2)) in arrows:
        rough_arrow(draw, p1, p2, BLUE_RGB, width=2, seed=seed)
        seed += 11

    # birds (IP) inside cells
    font_label = find_font(44)
    for name, (x, y) in cells.items():
        bird = clean_bird(bird_paths[name], bottom_crop_pct=bird_crop[name])
        bw, bh = bird.size
        avail_w = cell_w - 90
        avail_h = cell_h - 130
        scale = min(avail_w/bw, avail_h/bh)
        bird = bird.resize((int(bw*scale), int(bh*scale)), Image.LANCZOS)
        bx = x + (cell_w - bird.width)//2
        by = y + (cell_h - bird.height)//2 - 25
        canvas.paste(bird, (bx, by))
        # season label (brand text, program-added)
        draw.text((x + cell_w//2, y + cell_h - 46), name, font=font_label,
                  fill=BLUE_RGB, anchor="mm")

    # title + hand-drawn underline
    font_title = find_font(58)
    draw.text((W//2, 62), "你的肤色分四季", font=font_title, fill=BLUE_RGB, anchor="mm")
    rough_line(draw, (W//2-180, 100), (W//2+180, 100), BLUE_RGB, width=2, seed=seed, overshoot=4)
    seed += 5

    # logo band at bottom
    band = Image.new("RGBA", (W, band_h), (*BEIGE_RGB, 255))
    logo = Image.open(LOGO).convert("RGBA")
    la = np.array(logo)
    bg = (la[:,:,0] > 150) & (la[:,:,1] > 130) & (la[:,:,2] > 110) & ((la[:,:,0]-la[:,:,2]) < 80)
    la[bg] = [230, 206, 184, 0]
    logo = Image.fromarray(la, "RGBA")
    lw, lh = logo.size
    scale = min(W*0.16/lw, band_h*0.66/lh)
    logo = logo.resize((int(lw*scale), int(lh*scale)), Image.LANCZOS)
    band.paste(logo, ((W-logo.width)//2, (band_h-logo.height)//2), logo)
    canvas.paste(band, (0, H-band_h))

    canvas.convert("RGB").save(OUT_PNG)
    print("saved", OUT_PNG)
    build_excalidraw()

# ---------- real .excalidraw skeleton source ----------
def build_excalidraw():
    elements = []
    counter = [1]
    def nid():
        counter[0] += 1
        return f"el{counter[0]:03d}"
    def add(el):
        elements.append(el)
        return el

    # frames
    for name, (x, y) in cells.items():
        add({
            "id": nid(), "type": "rectangle", "x": x, "y": y,
            "width": cell_w, "height": cell_h, "angle": 0,
            "strokeColor": "#2E27A8", "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
            "roughness": 2, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 3}, "seed": 1000+len(elements),
            "version": 1, "versionNonce": 1, "isDeleted": False,
            "boundElements": None, "updated": 1, "link": None, "locked": False,
        })
    # arrows
    for (pair, (p1, p2)) in arrows:
        dx = p2[0]-p1[0]; dy = p2[1]-p1[1]
        add({
            "id": nid(), "type": "arrow", "x": p1[0], "y": p1[1],
            "width": abs(dx), "height": abs(dy), "angle": 0,
            "strokeColor": "#2E27A8", "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
            "roughness": 2, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 2},
            "points": [[0, 0], [dx, dy]],
            "lastCommittedPoint": None, "startBinding": None, "endBinding": None,
            "startArrowhead": None, "endArrowhead": "arrow",
            "seed": 2000+len(elements), "version": 1, "versionNonce": 1,
            "isDeleted": False, "boundElements": None, "updated": 1,
            "link": None, "locked": False,
        })
    # title text
    add({
        "id": nid(), "type": "text", "x": W//2-180, "y": 36,
        "width": 360, "height": 60, "angle": 0,
        "strokeColor": "#2E27A8", "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
        "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
        "roundness": None, "seed": 3000,
        "version": 1, "versionNonce": 1, "isDeleted": False,
        "boundElements": None, "updated": 1, "link": None, "locked": False,
        "text": "你的肤色分四季", "fontSize": 58, "fontFamily": 2,
        "textAlign": "center", "verticalAlign": "top", "containerId": None,
        "originalText": "你的肤色分四季", "lineHeight": 1.25, "baseline": 50,
    })
    # season labels
    for name, (x, y) in cells.items():
        add({
            "id": nid(), "type": "text", "x": x+cell_w//2-30, "y": y+cell_h-70,
            "width": 60, "height": 50, "angle": 0,
            "strokeColor": "#2E27A8", "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": None, "seed": 4000+len(elements),
            "version": 1, "versionNonce": 1, "isDeleted": False,
            "boundElements": None, "updated": 1, "link": None, "locked": False,
            "text": name, "fontSize": 44, "fontFamily": 2,
            "textAlign": "center", "verticalAlign": "top", "containerId": None,
            "originalText": name, "lineHeight": 1.25, "baseline": 50,
        })

    doc = {
        "type": "excalidraw", "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": None, "viewBackgroundColor": "#E6CEB8",
        },
        "files": {},
    }
    with open(OUT_EX, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print("saved", OUT_EX)

if __name__ == "__main__":
    main()
