---
name: duo podcast workbuddy
description: Produce, repair, mix, and quality-check DUODUO's Chinese AI-assisted dialogue podcasts on the **WorkBuddy** platform. Use whenever creating an episode from a SPEAKER_A/SPEAKER_B script, cloning 多多's approved voice, adding the fixed male co-host, inserting intro/outro music or SFX, diagnosing timestamped audio defects, or exporting a publish-ready MP3. This is the WorkBuddy authoritative standard (EP11 v4b verified) — independent from the codex/.codex duo-podcast skill; do NOT import codex's parameters (speed 1.04, temp 0.65, Ryan-clone B, "not too crisp" A) which conflict with local measurements.
---

# DUO Podcast — WorkBuddy Production Standard (EP11 v4b verified)

> **Platform authority.** 2026-08-11 多多确认：WorkBuddy 完全保留 EP11 v4b 全部设置（含男声 `dylan` 预设、A 清脆声线），与 `codex/.codex` 那边的 `duo-podcast` 独立。**执行细节以本 skill 为准，不要套用 codex 的参数**（其 speed 1.04 / temp 0.65 / 男声 Ryan 克隆 / "不要过度清脆" 均与本地实测冲突）。后续 EP12+ 迭代若改动参数，必须同步更新本文件对应章节。

## 0. Brand core (cross-platform shared principles)

- **Dual-voice identity:** A = 多多 (female host), B = fixed male co-host; strictly alternating, never overlapping unless script requests an interruption.
- **Privacy red line:** voice-reference / voiceprint materials are processed locally by default; sending to a third-party provider requires explicit per-provider permission.
- **QC iron rule:** any "done" claim MUST pass transcription-vs-script word comparison of the final mix. Never assert completion from duration or waveform alone.
- **Delivery discipline:** old versions are NOT backed up — overwrite and delete; never publish externally without explicit permission.

## 1. Voice lock (WorkBuddy verified)

### A — 多多

- **Model:** `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` (local mlx_audio, Metal).
- **Reference:** `/tmp/tts_ref/ref_duoduo_20s_24k.wav` — built from `Yongtai Street.m4a` first ~20s → 24k mono, **NO denoise**. Rebuild via `ensure_ref` after every Mac restart (see Pitfall 3).
- **Fixed `ref_text=`** (ICL anchor) — keep exactly as set; never append unrelated phrases.
- **Timbre target:** **crisp, like the real person** (多多 2026-08-11 explicit). **Never use `temperature=0`** — it flattens the timbre and kills the crisp grain (Pitfall 6). Use the library default sampling.
- **Never denoise A** — denoise makes the timbre muddy.
- `speed` is a dead parameter (Pitfall 1) — do not expect it to change pace.

### B — male co-host

- **`CustomVoice-bf16` + `voice="dylan"` (fixed preset — 多多 satisfied, DO NOT substitute).**
- This is the deliberate divergence from codex: codex locks the Ryan reference-clone and bans CustomVoice presets; WorkBuddy explicitly uses `dylan`. Both platforms keep their own; do not force unification.

## 2. 🚨 Pitfalls & bans (local measured, highest priority)

1. **`speed` is a dead parameter:** mlx_audio official "not supported yet". 0.8 / 0.9 / 1.04 all no-op; A is always default pace. **Do NOT substitute librosa `time_stretch` for slowing** → Pitfall 5.
2. **Female swallow root cause = long-generation random tail-drop:** any single render turn beyond ~22 chars, Qwen3-TTS randomly drops the final 1–2 chars (EP12/13 user-audited: MANY sentence-final chars vanished). Unrelated to fade/temp. **Cure = `_split_long` in `render_segments.py`** — split at `。！？\n` AND **hard-split any single chunk >MAX_CHARS=22 chars** (the original only split at punctuation, leaving long punctuation-less sentences whole → STILL swallowed). A only + `UNIT_PAUSE=0.2`. Proof: `temperature=0` full-turn render STILL drops tails, so splitting — not temp — is the fix. **MAX_CHARS=40 is NOT enough** (EP12/13 proved it); use 22.
3. **💥 Metal deadlock (fatal):** killed/timeout/ollana-occupied → `RuntimeError: Unable to load kernel`, unrecoverable within session. **Only fix = reboot Mac.** Avoid: background ≥3min, `kill -9 llama-server` before render. Reboot clears `/tmp` → rebuild ref (extract only, no denoise). **Deleting A wavs to force re-render is the standard method (SOP §4) — safe ONLY if the TTS script is intact** (segments regenerate from it); if render then hits Metal deadlock, reboot + re-render from script. Never delete wavs when you cannot re-render (no script/source).
4. **Python 3.13 compat:** mlx-audio source `from __future__` duplicate → STT SyntaxError → A ICL hangs. Fixed by cleaning 32 files (use the 3.13 venv path).
5. **🚫 `time_stretch` BANNED:** librosa phase vocoder on many short concatenated segments produces pre-echo / phase-swimming (sounds like reverb/echo) AND muddies the crisp timbre. 多多 2026-08-11: "有回音、不清脆不像我" → reverted. Slowing is currently unsolvable (unless engine swap); keep default pace + split long turns for clarity.
6. **🚫 `temperature=0` BANNED for A:** flattens timbre, kills crispness (Pitfall confirmed by 多多's "不清脆" feedback on v4). Use default sampling.

## 3. Mix lock (concat.py params — hard-coded)

- A/B strictly alternating; **A_GAIN=0.95, B_GAIN=0.88** (~ -1.5 dB, male slightly lower).
- Inter-segment gap **GAP=0.45s**.
- Tail **FADE_OUT=0.02** (anti-click only; 0.06 multiplied tail words like "释" to ~0) + head **FADE_IN=0.04**.
- **KEEP=0.12** (tail margin to preserve final syllables; 0.08 was too small and clipped tails).
- SEG20 followed by `tiny_applause`; lofi synthesized locally via numpy/scipy.
- Scripts must NOT live in `/tmp`.

## 4. Full SOP (every step)

1. **Prepare package:** reuse `05_CONTENT/02 developing/多多的未完成实验播客_EP03-EP06_原声重写版_20260731/Ep08-ep16_播客多多未完成实验/<EPxx>/draft/` — `render_segments.py` / `concat.py` / `verify/`. Same-structure packages reuse directly; do not rewrite. (All EP08–16 process files live here, NOT in `03 drafts`; `03 drafts/To publish_*` is the FINAL publish queue only.)
2. **Parse script →** `segments_render.json` manifest (SPEAKER_A/B per segment, units, wav paths, sfx).
3. **ensure_ref:** rebuild the non-denoised reference into `/tmp/tts_ref/` (mandatory after reboot).
4. **Render A:** `render_segments.py` auto `_split_long` (cures swallow). Delete old A wavs to trigger re-render; keep B wavs.
5. **Mix:** `concat.py` (lock params above) → outputs `to publish/<EPxx>_样片_草稿.{mp3,wav,纯人声.wav}`.
6. **QC** (see §5).
7. **Deliver:** overwrite `to publish`, **no backup** (多多 instruction); no external publish without permission.

## 5. QC iron rule

- Real proof = **transcribe the pure-voice track and word-compare to script** (faster-whisper small int8 CPU, `word_timestamps`). `qc_audio.py` default `--threshold 0.006` is too sensitive → use `--threshold 0.002 --max-gap 0.7`.
- Duration-proxy is unreliable (A/B pace diff, SFX char counts).
- Spot-check long turns (seg21-class): confirm the tail target word (e.g. "解释") appears in transcript — proves split cured the swallow.
- Chinese zero-drop judgment: delete/replace blocks that are ALL English-term ASR variants (digestion/dankoe/nichelifesworkoffer/etc.) ≠ real drop.
- **Before full retranscribe, DELETE stale cache `transcript_autozh.txt`** or it reuses old results and misjudges.

## 6. Reusable script locations

`/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/05_CONTENT/02 developing/DuoDuo_Podcast_EP08_EP16_FIXED (1)/EP11/draft/`
- `render_segments.py` (split-long + ensure_ref)
- `concat.py` (mix lock)
- `verify/verify_ep11.py` (transcribe word-compare QC)
- `verify/scan_final_audio.py` (silence-gap scan)

## 7. 自动化铁律（防超时截断半成品）

**单次自动化禁止一次生成两期以上。** 每期流水线 = 渲染（Metal，~15–50min）+ 混音 + 终检 + 命名 + 发布信息 + 进 Drafts，两期合计 >2h，必超单次 agent 时长/上下文上限 → 截断产半成品（有分段无成片、下一期零进展）。
**实测**：08-11 07:00 一次性自动化生成 EP12+EP13，EP12 渲染完被截断（无成片）、EP13 零进展。

**正确结构（二选一）：**
1. **每期独立自动化**：EP12 / EP13 各一个，各自跑完整流水线。
2. **两阶段拆分**：阶段A = 渲染（后台长任务，只出分段）；阶段B = 混音 + 终检 + 交付（纯 numpy/CPU，不碰 Metal，快速），阶段B 等阶段A 完成再触发。

**长任务与 Metal 状态（macOS）：**
- 无 `setsid`；渲染用 `run_in_background` 启动，不要前台等（会超时）。
- 若 segments 停止增长、log 卡 `ICL Generation 0%`：先查 `/tmp/tts_ref/` 是否还在——**`/tmp` 被清 = Mac 重启铁证**。重启会：① 清 Metal 死锁（推理恢复）② 删参考音。脚本 `ensure_ref()` 自动重建参考音（未降噪），重建后推理正常（已实测验证）。
- 判定 Metal 死锁：load_model 成功但推理卡死被杀 = 死锁遗留；Mac 重启后自愈，参考音重建即可重渲。

## 8. Version record

- **EP11 v4b (2026-08-11):** reverted `temp0` + reverted `time_stretch`; only split-long retained. mp3 17:08, Chinese zero-drop, seg21 "解释" intact. This standard is anchored to v4b.
