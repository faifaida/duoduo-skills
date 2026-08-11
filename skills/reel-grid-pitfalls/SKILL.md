---
name: reel-grid-pitfalls
description: Fixed-duration-grid video reels (e.g. 2.8s/clip social reels). Five hard-won fixes — short clips must slow-mo not freeze, subtitles must be re-timed from the actual VO (never reuse a prior cut's hardcoded ASS times), the ffmpeg -t interpolated-value gotcha, you MUST verify VO/audio/subtitle sync programmatically before sending, and a FIXED brand-outro convention (last 5–10s BGM + ep1 "duoduo wear" voice tag) that must be applied to every DUODUO WEAR video. Use whenever building a multi-clip reel with burn-in subtitles.
agent_created: true
---

# Reel Grid Pitfalls (固定时长网格短视频)

适用：把 N 个素材各铺固定时长（如 2.8s/段）拼成一条成片、并烧录双语字幕的短视频 reels。

## 1. 短素材补长：用慢动作，别冻末帧

素材原生时长 < 网格时长时，错误做法是 `tpad=stop_mode=clone:stop_duration=SS`（冻末帧补长）→ 画面"动一下→定格→切"，观感就是"卡"。
正确做法：用 `setpts` 把整段拉到网格时长，运动连续不中断：

```
sd = probe_dur(src)                       # 原生秒数
factor = grid / sd                        # grid=2.8
vf = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920," \
     "setsar=1,setpts={factor:.4f}*(PTS-STARTPTS),fps=30,format=yuv420p"
# 输出再加 -t <grid> 兜底
```
慢放系数 ×1.0–1.6 都很自然（×1.5 偏慢但 cinematic 可接受）。验证连续性：抽该段 t=1.0 与 t=2.5 两帧做 PSNR，若 ~15–20dB（差异大）＝运动连续；若 ∞（相同）＝仍定格。

## 2. 字幕漂移：从真实 VO 重新打轴，别沿用别版的写死时间

把 A 版 reels 的字幕 ASS 时间轴直接抄到 B 版（哪怕镜头结构只差几段）→ 累积漂移，越往后字幕越慢于口播（用户感知"64s 起字幕比口播慢"）。
正确做法：对成片用的 VO 文件做转写，用逐词时间戳重打每行 ASS：

```
from faster_whisper import WhisperModel
m = WhisperModel("base", device="cpu", compute_type="int8")   # 模型常已缓存
segs,_ = m.transcribe(vo, word_timestamps=True, vad_filter=True)
# 取每段/每词 start/end，把既定双语字幕文本按语义对齐到对应词边界
```
base 模型 + CPU int8 转 73s 音频约 80s。字幕文本保持原稿（whisper 可能误听，但时间是准的）。每行 start=首词时间−0.05，end=末词+0.2，且与下一行留 ≥0.1s 间隙防重叠。

## 3. ffmpeg `-t` 插值值坑（致命）

把计算出的时长塞进 `-t` 时，**必须拆成两个独立参数**，且值要是 f-string：

```
# ✅ 正确
["-t", f"{end_dur:.2f}", out]
# ❌ 错误1：值漏 f 前缀 → ffmpeg 收到字面量 "{end_dur:.2f}" → Invalid duration
["-t", "{end_dur:.2f}", out]
# ❌ 错误2：合成一个带空格的串 → ffmpeg 当成选项名 "t 3.90" → Unrecognized option
[f"-t {end_dur:.2f}", out]
```
后果：尾卡/片段静默生成失败（capture_output 吞报错），成片缺尾卡、且 `-shortest` 可能把 VO 截短。务必对关键步骤查 returncode 并校验产物时长。

## 4. 交付前必须程序化验证「旁白/音/字」同步（用户硬性要求）

**绝不**只抽查 2 行字幕就说"已对齐"。用户明确：发我之前先把基本的旁边、音、字同步检查好。

做法：让成片每条字幕的英文文本 = 直录 VO 原文（verbatim），这样能用 whisper 词时间做精确匹配校验：

```
# 解析烧录用的 subs.ass → [(start, end, en_text)]
# 把每条 en_text 规范化(去标点/小写)后，在 VO 词序列里找连续匹配 span
#   expected = (words[j].start, words[j+Lt-1].end)
#   PASS 条件: |sub_start - expected_start| <= 0.5  且  sub_end >= expected_end - 0.3
#              （开头卡准即可；字幕比词稍长 OK，但不能早于词或早于词结束就消失）
# 覆盖率: 每个 VO 词的中点必须落在某条字幕区间 [s-0.05, e+0.05] 内 → 应 100%
# 相邻字幕最大间隙: 仅允许自然停顿(<=1.7s)，不应有"说话却没字幕"的洞
```

校验脚本范式见 `verify_subs_sync.py`（每版 reels 复用：传入 vo_segs.json + subs.ass，输出每行 dS/dE + 覆盖率 + 最大间隙 + PASS/FAIL）。
**只有 RESULT=PASS 才把文件交给用户。** 若有 ❌：绝大多数是字幕时间写错或某段 VO 漏了字幕行（如被切分的两段之间留了 0.3–0.8s 洞 → 把相邻行边界改成重叠消除）。

## 5. 固定品牌 Outro 约定（所有 DUODUO WEAR 视频适用 · 2026-08-04 用户确立）

每个视频结尾统一，且**固定给以后所有视频**，不可省略：

- **最后 5–10s 起放品牌 BGM**（淡入），增益压低（≈0.12，"小一点"，低于人声）。
- **结尾配 ep1 结尾那句「DUODUO WEAR.」人声**（从 Film01 MASTER 抽 39.0–40.5s 段，boost ≈1.4×），压在 logo 尾卡上，作品牌声音签名。
- 品牌固定 BGM = LolaMoore《Serene Acoustic Guitar Melodies》(Freesound, **CC BY**，直链 `https://cdn.freesound.org/previews/762/762604_16085454-hq.mp3`)。**发布必须在描述/评论保留 CC BY 署名**（法律强制，非引流）：`Music: "Serene Acoustic Guitar Melodies" by LolaMoore (CC BY) — freesound.org/people/LolaMoore/sounds/762604`。
- 实现（母版视频+VO 已锁定时，直接音频混音，video `-c:v copy` 不重编码保画质）：
  ```
  ffmpeg -i MASTER.mp4 -i bgm.mp3 -i duoduo_wear_voice.m4a \
    -filter_complex "
      [0:a]volume=1.0[vo];
      [1:a]aresample=44100,aformat=channel_layouts=mono,atrim=0:10,
            afade=t=in:st=0:d=1.5,volume=0.12,adelay=63470[bgm];
      [2:a]aresample=44100,aformat=channel_layouts=mono,volume=1.0,adelay=70000[voice];
      [vo][bgm][voice]amix=3:normalize=0[a];[a]alimiter=limit=0.9[aout]
    " -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -shortest OUT.mp4
  ```
  ⚠️ `adelay` 值 = 该元素应在成片出现的秒数 ×1000（ms）。BGM `atrim=0:10` 正好接到片尾（**勿取 12s**，否则音频拖长 2s 把成片撑到 75s）。`alimiter` 本版本**只接受 `limit=`**，不要加 `level=`（会报 boolean 解析错）。
- 验证：抽 63–73s 音频 volumedetect 应非静音（BGM+voice 能量）；抽 70–71.5s 应有峰值（≈人声）。

## 快速自检清单（交付前，逐项实测）
- [ ] 每段时长 ≈ 网格值（短素材已 slow-mo，无冻帧）
- [ ] 成片时长 == VO 时长（-shortest 不会截语音）
- [ ] blackdetect 无 ≥0.1s 黑帧
- [ ] **`verify_subs_sync.py` 跑出 RESULT=PASS**：每行字幕 onset 漂移≈0、覆盖率 100%、无"说话无字幕"洞
- [ ] 尾卡/特效底色与素材真实底色一致（抽像素验证，非"应如此"）
- [ ] **固定品牌 Outro 已落**：最后 10s BGM 淡入(增益≈0.12) + ep1「duoduo wear」人声压尾卡；CC BY 署名已备（发布用）
- [ ] 模型不读图 → 镜头内容/慢动作自然度/logo 字形大小须用户实机眼验
