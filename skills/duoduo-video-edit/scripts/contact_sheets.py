#!/usr/bin/env python3
"""
contact_sheets.py — 素材审片联系表生成器（通用 CLI）

把一整个素材目录（Live Photo / 视频 / 照片）转成「可被 AI 逐张看完」的联系表，
外加 manifest.csv 供后续分级与交叉核对。

用法:
  python3 contact_sheets.py --src <素材目录> --out <输出目录> [--mode all|live|video|photo]
                            [--ffmpeg <ffmpeg路径>] [--workers 6]
                            [--video-dirs Caz,长视频]   # 这些子目录下的 .mov 当正片视频而非 Live Photo

产出:
  <out>/live_strips/*.jpg      每段 Live Photo 的 5 帧动态条
  <out>/video_strips/*.jpg     每条视频的 8-14 帧关键帧条
  <out>/sheets_live/*.jpg      动态条联系表（3 列 × 7 行 = 21 段/张）
  <out>/sheets_video/*.jpg     关键帧条联系表（2 列 × 7 行 = 14 条/张）
  <out>/sheets_photo/*.jpg     高清照片联系表（4 列 × 6 行 = 24 张/张，大字 ID）
  <out>/manifest.csv           id,type,duration_sec,sheet
  <out>/pipeline.log

⚠️ 关键设计决策（都是踩坑换来的，别改小）:
- 照片联系表用 4×6 大格 + 44px 大字 ID。早期版本用 8 列小缩略图，审片员反馈
  「ID 文字读不清」→ 整批审核作废重做。格子太小 = 审核等于没做。
- Live Photo 必须看 5 帧动态条，不能只抽 1 帧静帧。只看静帧会把「主体完全静止的
  伪 Live Photo」误判为可用动态素材。
- 用线程池不用进程池：GB 级大文件会让子进程被 OOM kill 并连带炸掉整个 pool。
- 每个 ffmpeg 调用都带 timeout，单个坏文件不许拖死全批。
"""
import os, re, csv, math, subprocess, logging, time, argparse, shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None


def find_ffmpeg(explicit=None):
    if explicit and os.path.exists(explicit):
        return explicit
    for c in ["/Users/Zhuanz/.workbuddy/binaries/ffmpeg-bin/ffmpeg",
              "/Users/Zhuanz/.local/bin/ffmpeg",
              "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
        if os.path.exists(c):
            return c
    w = shutil.which("ffmpeg")
    if w:
        return w
    raise SystemExit("ERROR: 找不到 ffmpeg，用 --ffmpeg 指定路径")


def load_font(sz):
    for p in ["/System/Library/Fonts/Helvetica.ttc",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial.ttf"]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


class Pipeline:
    def __init__(self, src, out, ffmpeg, workers=6, video_dirs=()):
        self.src, self.out, self.ffmpeg = src, out, ffmpeg
        self.workers = workers
        self.video_dirs = set(video_dirs)
        os.makedirs(out, exist_ok=True)
        logging.basicConfig(filename=os.path.join(out, "pipeline.log"),
                            level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")
        self.log = logging.getLogger()
        self.manifest = []

    # ---------- ffmpeg helpers ----------
    def duration(self, path):
        """用 ffmpeg -i 读时长。不用 ffprobe：iCloud 路径下 ffprobe 会触发整文件下载并挂死。"""
        try:
            out = subprocess.run([self.ffmpeg, "-i", path],
                                 capture_output=True, text=True, timeout=90).stderr
            m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", out)
            if m:
                return float(m.group(1)) * 3600 + float(m.group(2)) * 60 + float(m.group(3))
        except Exception as e:
            self.log.warning("dur fail %s %s", path, e)
        return None

    def frames(self, path, n, outdir, w=320, dur=None):
        if dur is None:
            dur = self.duration(path) or 3.0
        sid = os.path.splitext(os.path.basename(path))[0]
        got = []
        for i in range(n):
            t = dur * (0.08 + 0.84 * i / (n - 1)) if n > 1 else dur * 0.1
            t = max(0.0, min(dur * 0.98, t))
            fr = os.path.join(outdir, f"{sid}_f{i}.jpg")
            try:
                subprocess.run([self.ffmpeg, "-y", "-ss", f"{t:.3f}", "-i", path,
                                "-frames:v", "1", "-vf", f"scale={w}:-1", fr],
                               capture_output=True, timeout=90)
            except Exception:
                pass
            if os.path.exists(fr) and os.path.getsize(fr) > 0:
                got.append(fr)
        return got, dur

    @staticmethod
    def strip(frames, out, target_h=130):
        imgs = [Image.open(f).convert("RGB") for f in frames]
        sc = [im.resize((max(40, int(im.width * target_h / im.height)), target_h)) for im in imgs]
        s = Image.new("RGB", (sum(i.width for i in sc), target_h))
        x = 0
        for im in sc:
            s.paste(im, (x, 0)); x += im.width
        s.save(out, quality=85)
        for f in frames:
            try: os.remove(f)
            except Exception: pass

    @staticmethod
    def sheet(items, out, cols, cell_w, label_px=20, font_px=15, fixed_h=None):
        """items = [(PIL.Image | path, label)]"""
        imgs = []
        for s, _ in items:
            im = s if isinstance(s, Image.Image) else Image.open(s).convert("RGB")
            if fixed_h:
                im.thumbnail((cell_w - 8, fixed_h - label_px - 8))
            else:
                im = im.resize((cell_w, int(im.height * cell_w / im.width)))
            imgs.append(im)
        if not imgs:
            return False
        cell_h = fixed_h or max(i.height for i in imgs)
        rows = math.ceil(len(imgs) / cols)
        sh = Image.new("RGB", (cell_w * cols, cell_h * rows), (18, 18, 20))
        d = ImageDraw.Draw(sh)
        font = load_font(font_px)
        for idx, (im, (_, label)) in enumerate(zip(imgs, items)):
            r, c = divmod(idx, cols)
            x, y = c * cell_w, r * cell_h
            sh.paste(im, (x + 4, y + label_px + 2))
            d.rectangle([x, y, x + cell_w, y + label_px], fill=(0, 0, 0))
            d.text((x + 6, y + 2), str(label)[:44], fill=(255, 240, 120), font=font)
        sh.save(out, quality=85)
        return True

    # ---------- enumerate ----------
    def scan(self):
        live, video, photo = [], [], []
        for dp, _, fns in os.walk(self.src):
            for fn in fns:
                if fn.startswith("."):
                    continue
                low, full = fn.lower(), os.path.join(dp, fn)
                if low.endswith(".mov"):
                    # .mov 默认当 Live Photo；但指定子目录（如 Caz）里的当正片视频
                    (video if os.path.basename(dp) in self.video_dirs else live).append(full)
                elif low.endswith((".mp4", ".m4v")):
                    video.append(full)
                elif low.endswith((".jpg", ".jpeg", ".png")):
                    photo.append(full)
        return sorted(live), sorted(video), sorted(photo)

    # ---------- passes ----------
    def _do_live(self, p):
        sid = os.path.splitext(os.path.basename(p))[0]
        d = os.path.join(self.out, "live_strips"); os.makedirs(d, exist_ok=True)
        fr, dur = self.frames(p, 5, d)
        if len(fr) < 2:
            return None
        sp = os.path.join(d, sid + "_strip.jpg")
        self.strip(fr, sp, 130)
        return (sp, sid, round(dur, 1))

    def _do_video(self, p):
        sid = os.path.splitext(os.path.basename(p))[0]
        d = os.path.join(self.out, "video_strips"); os.makedirs(d, exist_ok=True)
        dur = self.duration(p) or 5.0
        n = max(8, min(14, int(dur / 3)))
        fr, _ = self.frames(p, n, d, w=300, dur=dur)
        if len(fr) < 2:
            return None
        sp = os.path.join(d, sid + "_strip.jpg")
        self.strip(fr, sp, 110)
        return (sp, sid, round(dur, 1))

    def _parallel(self, fn, files, tag):
        res = []
        with ThreadPoolExecutor(max_workers=self.workers) as ex:
            futs = [ex.submit(fn, p) for p in files]
            for fu in as_completed(futs):
                try:
                    r = fu.result()
                    if r:
                        res.append(r)
                except Exception as e:
                    self.log.warning("%s err %s", tag, e)
        res.sort(key=lambda x: x[1])
        self.log.info("%s strips=%d", tag, len(res))
        return res

    @staticmethod
    def chunked(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def run(self, mode="all"):
        live, video, photo = self.scan()
        self.log.info("scan live=%d video=%d photo=%d", len(live), len(video), len(photo))
        print(f"扫描到: Live Photo={len(live)}  视频={len(video)}  照片={len(photo)}")
        t0 = time.time()
        counts = {}

        if mode in ("all", "live") and live:
            strips = self._parallel(self._do_live, live, "live")
            d = os.path.join(self.out, "sheets_live"); os.makedirs(d, exist_ok=True)
            for i, c in enumerate(self.chunked(strips, 21)):
                sh = os.path.join(d, f"live_sheet_{i:02d}.jpg")
                self.sheet([(s, lab) for (s, lab, _) in c], sh, cols=3, cell_w=620)
                for (_, lab, dur) in c:
                    self.manifest.append([lab, "live", dur, os.path.basename(sh)])
            counts["sheets_live"] = len(os.listdir(d))

        if mode in ("all", "video") and video:
            strips = self._parallel(self._do_video, video, "video")
            d = os.path.join(self.out, "sheets_video"); os.makedirs(d, exist_ok=True)
            for i, c in enumerate(self.chunked(strips, 14)):
                sh = os.path.join(d, f"video_sheet_{i:02d}.jpg")
                self.sheet([(s, f"{lab} ({dur}s)") for (s, lab, dur) in c], sh, cols=2, cell_w=900)
                for (_, lab, dur) in c:
                    self.manifest.append([lab, "video", dur, os.path.basename(sh)])
            counts["sheets_video"] = len(os.listdir(d))

        if mode in ("all", "photo") and photo:
            # 高清模式：4 列 × 6 行，大字 ID。小格子会导致 ID 读不清 → 审核作废。
            d = os.path.join(self.out, "sheets_photo"); os.makedirs(d, exist_ok=True)
            for i, batch in enumerate(self.chunked(photo, 24)):
                items = []
                for p in batch:
                    try:
                        items.append((Image.open(p).convert("RGB"),
                                      os.path.splitext(os.path.basename(p))[0]))
                    except Exception as e:
                        self.log.warning("photo open fail %s %s", p, e)
                if not items:
                    continue
                sh = os.path.join(d, f"photo_sheet_{i:02d}.jpg")
                self.sheet(items, sh, cols=4, cell_w=560,
                           label_px=52, font_px=44, fixed_h=480)
                for (_, lab) in items:
                    self.manifest.append([lab, "photo", "", os.path.basename(sh)])
            counts["sheets_photo"] = len(os.listdir(d))

        with open(os.path.join(self.out, "manifest.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "type", "duration_sec", "sheet"])
            w.writerows(self.manifest)

        self.log.info("DONE rows=%d (%.1fs)", len(self.manifest), time.time() - t0)
        print(f"DONE  manifest={len(self.manifest)} 条  用时 {time.time()-t0:.0f}s")
        for k, v in counts.items():
            print(f"  {k}: {v} 张")
        print(f"输出目录: {self.out}")


def main():
    ap = argparse.ArgumentParser(description="素材审片联系表生成器")
    ap.add_argument("--src", required=True, help="素材根目录（递归扫描）")
    ap.add_argument("--out", required=True, help="输出目录")
    ap.add_argument("--mode", default="all", choices=["all", "live", "video", "photo"])
    ap.add_argument("--ffmpeg", default=None)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--video-dirs", default="",
                    help="逗号分隔的子目录名，这些目录下的 .mov 当正片视频而非 Live Photo（如 Caz）")
    a = ap.parse_args()
    vd = [x.strip() for x in a.video_dirs.split(",") if x.strip()]
    Pipeline(a.src, a.out, find_ffmpeg(a.ffmpeg), a.workers, vd).run(a.mode)


if __name__ == "__main__":
    main()
