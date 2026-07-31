#!/usr/bin/env python3
"""
face_id.py — 「这张素材里是不是本人」的程序化判定（InsightFace 人脸向量）

为什么存在：靠「手链 / 纹身 / 发型」认人只在夏天露肤时管用，穿上衣服就全失效，
而且会导致认错人 + 编造画面里不存在的人。人脸向量是唯一稳的判据。

用法:
  # 1) 放几张「已被本人确认」的清晰正脸照进 refs_raw/，然后建档
  python3 face_id.py build [--id-dir <工作目录>] [--exclude IMG_8577_face1,...]

  # 2) 单图判定
  python3 face_id.py check <图片> [--id-dir <工作目录>]

  # 3) 批量扫目录（支持递归）
  python3 face_id.py batch <目录> [--recursive] [--id-dir <工作目录>]

  # 4) 从视频/Live Photo 抽帧后判定（帧级投票）
  python3 face_id.py video <视频文件> [--frames 8] [--ffmpeg <路径>]

工作目录结构（默认 = 本脚本所在目录，用 --id-dir 换到项目里）:
  refs_raw/        你放进去的参考原图
  refs_cropped/    build 时裁出的人脸（★必须人工看一遍！）
  models/          InsightFace 模型缓存（首次自动下载 ~300MB）
  face_id.pkl      人脸向量档案

⚠️ 铁律（都是踩坑换来的）:
1. build 之后**必须逐张打开 refs_cropped/ 看**。参考图里常混进别人（合影中的路人/
   长辈），混进去会把整个 ID 向量拉偏，之后全盘误判。发现杂人用 --exclude 剔除重建。
2. 距离用 **余弦距离**，不是欧氏距离。欧氏距离在归一化后数值区分度差，会让你误以为
   「本人内部距离偏高、阈值不好定」。
3. 阈值不要照抄，**用负样本实测标定**：拿一张确定不是本人的图跑 check，看距离。
   实测参考（多多 · buffalo_l）：本人 0.25–0.50，非本人 0.92 → 阈值取 0.75，中间
   有 0.42 空隙，安全。
4. 侧脸/趴姿/极小人脸检测不到是正常的，不代表"不是本人"，输出会区分「无人脸」和
   「有人脸但不匹配」——别把前者当否定证据。
5. **人脸向量是生物特征数据，绝不推送到公开仓库。** face_id.pkl / refs_* 一律本地留存。
"""
import sys, os, json, glob, pickle, argparse, subprocess, shutil, tempfile
import numpy as np
import cv2
from insightface.app import FaceAnalysis

DEFAULT_THRESHOLD = 0.75
IMG_EXTS = ("*.jpg", "*.JPG", "*.jpeg", "*.JPEG", "*.png", "*.PNG", "*.webp")


def cos_dist(a, b):
    return float(1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class FaceID:
    def __init__(self, id_dir=None):
        self.base = os.path.abspath(id_dir or os.path.dirname(os.path.abspath(__file__)))
        self.refs_raw = os.path.join(self.base, "refs_raw")
        self.refs_crop = os.path.join(self.base, "refs_cropped")
        self.models = os.path.join(self.base, "models")
        self.pkl = os.path.join(self.base, "face_id.pkl")
        # 兼容旧文件名
        legacy = os.path.join(self.base, "duoduo_face_id.pkl")
        if not os.path.exists(self.pkl) and os.path.exists(legacy):
            self.pkl = legacy
        self._app = None

    @property
    def app(self):
        if self._app is None:
            self._app = FaceAnalysis(name="buffalo_l", root=self.models,
                                     providers=["CPUExecutionProvider"])
            self._app.prepare(ctx_id=0, det_size=(640, 640))
        return self._app

    def load(self):
        if not os.path.exists(self.pkl):
            sys.exit(f"ERROR: 还没建档。先把确认过的正脸照放进 {self.refs_raw}/ 再跑 build")
        with open(self.pkl, "rb") as f:
            d = pickle.load(f)
        return np.array(d["mean_embedding"]), d.get("threshold", DEFAULT_THRESHOLD)

    # ---------- build ----------
    def build(self, exclude=()):
        os.makedirs(self.refs_raw, exist_ok=True)
        files = []
        for e in IMG_EXTS:
            files.extend(glob.glob(os.path.join(self.refs_raw, e)))
        files = sorted(set(files))
        if not files:
            sys.exit(f"ERROR: {self.refs_raw}/ 里没有参考图")

        print(f"=== 建档：{len(files)} 张参考图 ===")
        os.makedirs(self.refs_crop, exist_ok=True)
        embs, meta = [], []
        for f in files:
            img = cv2.imread(f)
            if img is None:
                print(f"  ⚠️ 读不了 {os.path.basename(f)}")
                continue
            faces = self.app.get(img)
            stem = os.path.splitext(os.path.basename(f))[0]
            if not faces:
                print(f"  ⚠️ {stem}: 未检测到人脸（侧脸/太小/遮挡都会这样，正常）")
                continue
            for i, face in enumerate(faces):
                key = f"{stem}_face{i}"
                x1, y1, x2, y2 = face.bbox.astype(int)
                m = int(max(x2 - x1, y2 - y1) * 0.2)
                crop = img[max(0, y1 - m):min(img.shape[0], y2 + m),
                           max(0, x1 - m):min(img.shape[1], x2 + m)]
                cv2.imwrite(os.path.join(self.refs_crop, key + ".jpg"), crop)
                if key in exclude:
                    print(f"  ⊘ {key}: 已按 --exclude 剔除")
                    continue
                embs.append(face.embedding)
                meta.append({"key": key, "source": os.path.basename(f),
                             "det_score": float(face.det_score)})
                print(f"  ✓ {key}  置信度={face.det_score:.3f}")

        if not embs:
            sys.exit("ERROR: 一张可用人脸都没有，无法建档")

        mean = np.mean(embs, axis=0)
        mean = mean / np.linalg.norm(mean)
        dists = [cos_dist(e, mean) for e in embs]

        with open(self.pkl, "wb") as f:
            pickle.dump({"mean_embedding": mean.tolist(),
                         "individual_embeddings": [e.tolist() for e in embs],
                         "meta": meta,
                         "threshold": DEFAULT_THRESHOLD,
                         "n_references": len(embs),
                         "max_intra_dist": max(dists),
                         "mean_intra_dist": sum(dists) / len(dists)}, f)

        print(f"\n✅ 建档完成：{len(embs)} 张人脸")
        for m, d in zip(meta, dists):
            print(f"   {m['key']:<24} cos_dist={d:.4f}")
        print(f"   内部最大距离={max(dists):.4f}  平均={sum(dists)/len(dists):.4f}")
        print(f"   阈值={DEFAULT_THRESHOLD}（★请用一张确定不是本人的图跑 check 实测标定）")
        print(f"\n★ 下一步必做：逐张打开 {self.refs_crop}/ 确认没有混进别人。")
        print(f"  混进了就 --exclude <key1,key2> 重新 build。")

    # ---------- check ----------
    def check_image(self, path, mean=None, th=None, quiet=False):
        if mean is None:
            mean, th = self.load()
        img = cv2.imread(path)
        if img is None:
            return None
        faces = self.app.get(img)
        if not faces:
            if not quiet:
                print(f"{os.path.basename(path)}: 无人脸 → 无法判定（不等于「不是本人」）")
            return ("no_face", None, None)
        best = min(((cos_dist(f.embedding, mean), f) for f in faces), key=lambda x: x[0])
        d, face = best
        hit = d < th
        if not quiet:
            for i, f in enumerate(faces):
                dd = cos_dist(f.embedding, mean)
                mark = "✅ 是本人" if dd < th else "❌ 不是本人"
                print(f"{os.path.basename(path)} 人脸{i+1}: dist={dd:.4f} (阈值<{th}) → {mark}  conf={f.det_score:.3f}")
        return ("match" if hit else "other", d, float(face.det_score))

    # ---------- batch ----------
    def batch(self, d, recursive=False):
        mean, th = self.load()
        files = []
        if recursive:
            for dp, _, fns in os.walk(d):
                for fn in fns:
                    if fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) and not fn.startswith("."):
                        files.append(os.path.join(dp, fn))
        else:
            for e in IMG_EXTS:
                files.extend(glob.glob(os.path.join(d, e)))
        files = sorted(set(files))
        print(f"扫描 {len(files)} 张图...")

        match, other, noface = [], [], []
        for i, f in enumerate(files, 1):
            if i % 50 == 0:
                print(f"  ...{i}/{len(files)}")
            r = self.check_image(f, mean, th, quiet=True)
            if r is None:
                continue
            kind, dist, conf = r
            name = os.path.relpath(f, d)
            if kind == "no_face":
                noface.append(name)
            elif kind == "match":
                match.append((name, dist, conf))
            else:
                other.append((name, dist))

        print(f"\n{'='*52}")
        print(f"✅ 含本人 ({len(match)}):")
        for n, dd, c in sorted(match, key=lambda x: x[1]):
            print(f"  {n}  dist={dd:.4f} conf={c:.3f}")
        print(f"\n❌ 有人脸但不是本人 ({len(other)}) — 前 20:")
        for n, dd in sorted(other, key=lambda x: x[1])[:20]:
            print(f"  {n}  dist={dd:.4f}")
        print(f"\n⚪ 无人脸 ({len(noface)}) — 不作为否定证据")

        out = os.path.join(self.base, "batch_results.json")
        with open(out, "w") as f:
            json.dump({"match": [(n, float(d), float(c)) for n, d, c in match],
                       "other": [(n, float(d)) for n, d in other],
                       "no_face": noface}, f, ensure_ascii=False, indent=2)
        print(f"\n结果: {out}")

    # ---------- video ----------
    def video(self, path, n=8, ffmpeg=None):
        """从视频/Live Photo 均匀抽帧，帧级投票判定。"""
        ff = ffmpeg
        if not ff or not os.path.exists(ff):
            for c in ["/Users/Zhuanz/.workbuddy/binaries/ffmpeg-bin/ffmpeg",
                      "/Users/Zhuanz/.local/bin/ffmpeg", shutil.which("ffmpeg")]:
                if c and os.path.exists(c):
                    ff = c; break
        if not ff:
            sys.exit("ERROR: 找不到 ffmpeg")
        mean, th = self.load()
        import re
        err = subprocess.run([ff, "-i", path], capture_output=True, text=True, timeout=120).stderr
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", err)
        dur = (float(m.group(1))*3600 + float(m.group(2))*60 + float(m.group(3))) if m else 3.0

        tmp = tempfile.mkdtemp(prefix="faceid_")
        hits, checked = [], 0
        try:
            for i in range(n):
                t = dur * (0.08 + 0.84 * i / max(1, n - 1))
                fr = os.path.join(tmp, f"f{i}.jpg")
                subprocess.run([ff, "-y", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1",
                                "-vf", "scale=960:-1", fr], capture_output=True, timeout=120)
                if not (os.path.exists(fr) and os.path.getsize(fr) > 0):
                    continue
                r = self.check_image(fr, mean, th, quiet=True)
                if r is None or r[0] == "no_face":
                    continue
                checked += 1
                if r[0] == "match":
                    hits.append((round(t, 1), r[1]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        name = os.path.basename(path)
        if not checked:
            print(f"{name}: {n} 帧里没检测到人脸 → 无法判定")
        elif hits:
            best = min(hits, key=lambda x: x[1])
            print(f"{name}: ✅ 是本人（{len(hits)}/{checked} 帧命中，最佳 t={best[0]}s dist={best[1]:.4f}）")
            print(f"   命中时间点: {[h[0] for h in hits]}")
        else:
            print(f"{name}: ❌ 有人脸但都不是本人（{checked} 帧检测到人脸，0 命中）")


def main():
    ap = argparse.ArgumentParser(description="人脸向量身份判定")
    ap.add_argument("cmd", choices=["build", "check", "batch", "video"])
    ap.add_argument("target", nargs="?", help="图片 / 目录 / 视频路径")
    ap.add_argument("--id-dir", default=None, help="Face ID 工作目录（默认=脚本所在目录）")
    ap.add_argument("--exclude", default="", help="build 时剔除的人脸 key，逗号分隔，如 IMG_8577_face1")
    ap.add_argument("--recursive", action="store_true", help="batch 递归子目录")
    ap.add_argument("--frames", type=int, default=8, help="video 抽帧数")
    ap.add_argument("--ffmpeg", default=None)
    a = ap.parse_args()

    fid = FaceID(a.id_dir)
    if a.cmd == "build":
        fid.build({x.strip() for x in a.exclude.split(",") if x.strip()})
    elif a.cmd == "check":
        if not a.target: sys.exit("用法: face_id.py check <图片>")
        fid.check_image(a.target)
    elif a.cmd == "batch":
        if not a.target: sys.exit("用法: face_id.py batch <目录> [--recursive]")
        fid.batch(a.target, a.recursive)
    elif a.cmd == "video":
        if not a.target: sys.exit("用法: face_id.py video <视频>")
        fid.video(a.target, a.frames, a.ffmpeg)


if __name__ == "__main__":
    main()
