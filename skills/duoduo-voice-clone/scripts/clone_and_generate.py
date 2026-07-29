#!/usr/bin/env python3
"""
duoduo-voice-clone · 开源声音克隆生成器（OpenVoice v2 后端，零样本）

输入：
  --ref-a   多多本人参考音频（必填，WAV/MP3，10-15s 干净人声）
  --ref-b   伴侣/第二人声参考音频（可选；缺省用 OpenVoice base speaker）
  --script  带 Speaker 标签的 TTS 脚本（如 EP02_TTS安全脚本.txt）
  --out-dir 输出目录（默认 ./podcast_out）
  --ov-dir  OpenVoice checkpoints_v2 目录
  --mode    dry-run（只解析）| full（生成+拼接）

输出：
  <out-dir>/segments/seg_NN.wav   每段克隆音频
  <out-dir>/ep_final.wav          拼接母版
  <out-dir>/ep_final.mp3          发布版
  <out-dir>/manifest.json         段落清单

依赖（实测可用 venv）：
  /Users/Zhuanz/.workbuddy/binaries/python/envs/ov310/bin/python
  + openvoice (git main) + torch CPU + imageio-ffmpeg
  + 权重 /Users/Zhuanz/IP_video_drafts/ov_weights/checkpoints_v2/

API 注意（实测）：OpenVoice 当前包是 v1 式签名
  base_tts = BaseSpeakerTTS(config, device='cpu'); base_tts.load_ckpt(ckpt)
  converter = ToneColorConverter(config, device='cpu'); converter.load_ckpt(conv_ckpt)
  target_se = converter.extract_se([ref_wav])   # 避开 se_extractor 的 VAD/Whisper 依赖
"""
import argparse, json, os, re, sys, subprocess

def parse_script(path):
    txt = open(path, encoding="utf-8").read()
    parts = re.split(r"\[SEGMENT_(\d+)\]", txt)
    segs = []
    for i in range(1, len(parts), 2):
        num = int(parts[i]); body = parts[i + 1]
        m = re.search(r"SPEAKER_([AB]):\s*(.+?)(?=\n\[SEGMENT_|\Z)", body, re.S)
        if not m:
            speaker, text = "A", body.strip()
        else:
            speaker, text = m.group(1), m.group(2).strip()
        text = text.replace("\n", " ").strip()
        if not text:
            continue
        segs.append({"id": num, "speaker": speaker, "text": text})
    segs.sort(key=lambda x: x["id"])
    return segs

def _first(p):
    return p[0] if isinstance(p, (list, tuple)) else p

def build_openvoice(ref_a, ref_b, segs, out_dir, ov_dir, device="cpu", lang="Chinese"):
    import torch
    from openvoice.api import BaseSpeakerTTS, ToneColorConverter

    # 语言 → 底座目录：Chinese=ZH(zh_default_se.pth) / English=EN(default_se.pth)
    spk_dir = "ZH" if lang == "Chinese" else "EN"
    se_name = "zh_default_se.pth" if lang == "Chinese" else "default_se.pth"
    base_ckpt = os.path.join(ov_dir, "base_speakers", spk_dir, "checkpoint.pth")
    base_cfg  = os.path.join(ov_dir, "base_speakers", spk_dir, "config.json")
    if not os.path.exists(base_cfg):
        base_cfg = os.path.join(ov_dir, "config.json")
    conv_ckpt = os.path.join(ov_dir, "converter", "checkpoint.pth")
    conv_cfg  = os.path.join(ov_dir, "converter", "config.json")
    if not os.path.exists(conv_cfg):
        conv_cfg = os.path.join(ov_dir, "config.json")
    default_se = os.path.join(ov_dir, "base_speakers", spk_dir, se_name)
    for f in (base_ckpt, base_cfg, conv_ckpt, conv_cfg, default_se):
        if not os.path.exists(f):
            print(f"[ERR] 缺失权重文件: {f}", file=sys.stderr); sys.exit(2)

    base_tts = BaseSpeakerTTS(base_cfg, device=device); base_tts.load_ckpt(base_ckpt)
    converter = ToneColorConverter(conv_cfg, device=device); converter.load_ckpt(conv_ckpt)
    source_se = torch.load(default_se, map_location=device, weights_only=True)

    target_se_a = _first(converter.extract_se([ref_a]))
    target_se_b = _first(converter.extract_se([ref_b])) if ref_b else None

    os.makedirs(os.path.join(out_dir, "segments"), exist_ok=True)
    manifest = []
    for s in segs:
        out_wav = os.path.join(out_dir, "segments", f"seg_{s['id']:02d}.wav")
        tgt = target_se_a if s["speaker"] == "A" else (target_se_b if target_se_b is not None else source_se)
        base_tts.tts(s["text"], out_wav, speaker="default", language=lang)
        converter.convert(out_wav, source_se, tgt, out_wav)
        print(f"[OK] seg_{s['id']:02d} [{s['speaker']}] -> {out_wav}")
        manifest.append({"id": s["id"], "speaker": s["speaker"], "text": s["text"], "wav": out_wav})
    return manifest

def concat(manifest, out_dir):
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    silent = os.path.join(out_dir, "_silence.wav")
    subprocess.run([ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:d=0.4",
                    "-c:a", "pcm_s16le", silent], capture_output=True)
    wavs = []
    for m in manifest:
        wavs.append(m["wav"]); wavs.append(silent)
    list_file = os.path.join(out_dir, "_list.txt")
    with open(list_file, "w") as f:
        for w in wavs:
            f.write(f"file '{w}'\n")
    final_wav = os.path.join(out_dir, "ep_final.wav")
    subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", list_file,
                    "-c", "copy", final_wav], capture_output=True)
    final_mp3 = os.path.join(out_dir, "ep_final.mp3")
    subprocess.run([ffmpeg, "-y", "-i", final_wav, "-b:a", "192k", final_mp3], capture_output=True)
    print(f"[OK] 拼接完成：{final_wav}\n[OK] 发布版：{final_mp3}")
    return final_wav, final_mp3

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-a", required=True)
    ap.add_argument("--ref-b", default=None)
    ap.add_argument("--script", required=True)
    ap.add_argument("--out-dir", default="./podcast_out")
    ap.add_argument("--ov-dir", default="/Users/Zhuanz/IP_video_drafts/ov_weights/checkpoints_v2")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--lang", default="Chinese", choices=["Chinese", "English"])
    args = ap.parse_args()

    segs = parse_script(args.script)
    print(f"[INFO] 解析到 {len(segs)} 段")
    if args.mode == "dry-run":
        for s in segs:
            print(f"  seg_{s['id']:02d} [{s['speaker']}] {s['text'][:30]}...")
        return
    os.makedirs(args.out_dir, exist_ok=True)
    manifest = build_openvoice(args.ref_a, args.ref_b, segs, args.out_dir, args.ov_dir, lang=args.lang)
    json.dump(manifest, open(os.path.join(args.out_dir, "manifest.json"), "w"), ensure_ascii=False, indent=2)
    concat(manifest, args.out_dir)

if __name__ == "__main__":
    main()
