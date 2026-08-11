---
name: ffmpeg-libass-drift-drawtext
description: >-
  Burn dense/long subtitles with ffmpeg when the libass `subtitles` filter drifts
  (blank frames, double-line overlaps, time misalignment). Bypass libass entirely
  with per-event `drawtext` (libfreetype) driven by `enable=between(t,s,e)`, which is
  frame-accurate by video PTS. Includes the 3 iron rules (file syntax, comma escaping,
  apostrophe U+2019) and a teal-pixel verification recipe for when image preview is blocked.
triggers:
  - "字幕烧录漂移 / libass 漂移 / 字幕双行 / 字幕空白"
  - "drawtext 逐事件字幕 / bypass libass / subtitles filter drifts on long video"
  - "ffmpeg 烧字幕 长视频 多事件 时序错"
---

# libass 长/稠密字幕漂移 → drawtext 逐事件绕过

## 何时用
- 用 ffmpeg `subtitles=xxx.ass` 把 **~100+ 条事件** 烧到 **数分钟长视频** 时，出现：
  - 中段某时刻**无字幕**（本该有）
  - **两行同时出现**（违反「单行」硬约束）
  - 时序整体错位且不均匀
- 诊断：把同一 ASS 单独烧到同长度黑底 `color=black:d=N + subtitles=xxx.ass`，
  若仍复现 → bug 在 libass 事件调度本身，与你的 concat/滤镜链无关。
- 结论：libass 在长/稠密 ASS 上不可靠 → 改用 `drawtext` 逐事件。

## 修法（核心）
每条字幕事件生成一段 `drawtext`，用 `enable=between(t,s,e)` 在 [s,e] 区间显示：
```
drawtext=fontfile=/System/Library/Fonts/Supplemental/Songti.ttc:fontsize=44:fontcolor=0x00B6C5
 :borderw=2:bordercolor=black@0.95
 :text='单行字幕':x=(w-text_w)/2:y=h-200
 :enable=between(t\,S\,E)
```
- `enable` 由 ffmpeg 滤镜调度器按**视频 PTS 逐帧求值** → frame-accurate，零漂移。
- **加粗**：同一条画两遍，第二遍 `x=(w-text_w)/2+1`（1px 偏移叠出粗体感）。
- 所有事件用 `,` 串成一条滤镜链：`[IN]drawtext=...,drawtext=...,...[OUT];`

## 三条铁律（照做，否则必炸）
1. **超长滤镜图用 `-/filter_complex <file>`**（ffmpeg 7.1）。
   `-filter_complex_script` 已废弃；几百条 drawtext 内联会超命令行长度或报 `Invalid argument`。
   把整条链写进 `body_dt_filter.txt`，脚本里 `-/filter_complex "$SCRIPT"`。
2. **`between(t,s,e)` 里逗号写成 `\,`**（raw `,` 被当滤镜链分隔符 → `No such filter`）。
   N 条事件 → 2N 个 `\,`（每个 between 两个逗号）。
3. **文本里的 ASCII 撇号 `'` 绝不写 `\'` 转义**（在 `-/filter_complex` 文件读取时
   会让整个 drawtext 链崩溃；inline 能过、文件读不过）。
   改用 typographic 撇号 **`'`（U+2019）**，无需转义。生成器里写：
   `safe = txt.replace("'", "\u2019")`。

## 验证（模型禁读图时）
抽帧后 crop 字幕带（竖屏底部 `crop=720:120:0:1000`），用 Pillow/numpy 数目标色像素 + 量纵向跨度：
- 该出现时出现 → 目标色像素 > 0（如 teal #00B6C5：R<90, G 120–235, B 150–245）。
- 单行 ≈ 39px 纵向跨度；双行 ≈ 80px → 用跨度判断有无重叠。
- 全片 5s 步长密抽，对照时间线：active 帧必 teal 出现、gap 帧必无；相邻卡间留 0.02s 微隙属正常（整数抽样可能正好落微隙，属假阳）。

## 最小可复用模板（Python 生成器思路）
```python
def make_filter(events):  # events: list[(start_sec, end_sec, text)]
    parts = []
    for s, e, txt in events:
        safe = txt.replace("'", "\u2019")          # 铁律 3
        base = (f"drawtext=fontfile={FF}:fontsize=44:fontcolor=0x00B6C5"
                f":borderw=2:bordercolor=black@0.95"
                f":text='{safe}':x=(w-text_w)/2:y=h-200"
                f":enable=between(t\\,{s}\\,{e})")   # 铁律 2：逗号 \,
        parts.append(base)
        parts.append(base.replace("x=(w-text_w)/2", "x=(w-text_w)/2+1"))  # 加粗
    return ",".join(parts)
# 写 body_dt_filter.txt: "[0:v]scale=720:1280,fps=30,format=yuv420p[bv0]; ... [BODYV]{chain}[BVS];"
# 渲染: ffmpeg -/filter_complex body_dt_filter.txt ...   # 铁律 1
```

## 关联
- 既有的 `video-subtitle` / `video-subtitles__skillhub` 负责 whisper 转写 + 生成 SRT/ASS；
  本 skill 是「ASS 烧录漂移时的兜底烧法」，不替代转写。
- 分段式渲染（输入 `-ss` + xfade/concat）见项目 MEMORY.md「ffmpeg xfade/concat」一节。
