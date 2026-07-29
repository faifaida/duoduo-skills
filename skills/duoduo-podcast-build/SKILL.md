---
name: duoduo-podcast-build
description: 把《多多的未完成实验》这类「双人 Deep Dive 播客」从带 Speaker 标签的 TTS 安全脚本，自动生成成片音频（MP3+WAV）+ 质检报告。路线 = ElevenLabs API（多多本人克隆声 + 固定搭档声）。当用户说"做播客/出 EP/把脚本生成音频/今晚发播客"且已有 TTS 安全脚本时触发。
---

# 多多播客音频自动生产线

把一份**带 `SPEAKER_A` / `SPEAKER_B` 标签**的 TTS 安全脚本，自动生成成片音频。

## 何时用
- 用户已有播客脚本（生产包 + TTS 安全脚本），要出音频成片。
- 节目形式：双人 Deep Dive（主持人 A = 多多本人授权声音，主持人 B = 固定研究搭档声）。
- 触发词：「做播客 / 出 EP0x / 把脚本生成音频 / 今晚发播客」。

## ⚠️ 唯一硬依赖（只有用户能给，Agent 无法替代）
**多多本人的授权克隆声音模型 + ElevenLabs API Key。**
- Agent 无法凭空合成"本人声音"。必须由多多本人在 ElevenLabs 上传授权录音、建 voice（**Instant Voice Cloning 需付费档，免费档不支持克隆**），拿到 `voice_id`。
- 研究搭档 B 可用 ElevenLabs 公共库任一中文/多语声线（与 A 明显不同），或用克隆声。
- 三个值：`ELEVENLABS_API_KEY` / `DUODUO_VOICE_ID` / `PODCAST_PARTNER_VOICE_ID`。
- **`notebooklm-studio` 不适用**：它生成 NotebookLM 自带双 AI 主播腔，非多多本人声 → 不满足"主持人A用本人授权声音"硬要求。

## 密钥安全（铁律）
- 三个密钥放在 **Vault 之外**的本地文件（如 `/Users/Zhuanz/IP_video_drafts/.env.ep02`），**绝不**写进聊天、日志、成片元数据或 Obsidian。
- 脚本读取该文件、**绝不打印密钥值**（只打印进度/状态）。
- 禁止把 API Key / voice_id / 声音样本输出到任何日志。

## 执行流程
1. **解析** TTS 安全脚本 → 逐段拆成 `{seg_id, speaker, text}` 的 speaker-block 清单。
   - 注意：一个 `[SEGMENT_xx]` 内可能含多个 `SPEAKER_A`/`SPEAKER_B` block，需按行内标签切分。
   - 脚本中"AI"应已替换成"人工智能"（规避英文发音），如未替换，生成前先替换。
2. **试听（mandatory 人工确认节点）**：先生成 `SEGMENT 01–03` → 拼接 → 输出试听 MP3 → **交多多本人试听**（像不像/搭档区分/停顿自然/无播音腔）。
3. **全量生成**：确认后逐段调 ElevenLabs API（A→DUODUO_VOICE_ID，B→PODCAST_PARTNER_VOICE_ID），每段独立生成，失败最多重试 2 次。
4. **后期**：`ffmpeg` 段间留 ~0.45s 静音（章节间隔）→ 音量统一（`loudnorm I=-16`）→ 导出 MP3(128k) + WAV 母版。
5. **质检**：对照 `音频质检表.md` 跑程序化检查（段数一致/漏句/声音未交换/发音词/音量/时长 24–30min）+ 人工确认项（多多试听）。
6. **发布前**：多多本人试听 + 确认声音授权范围 + 标题简介与成片一致。

## 工具链
- **ffmpeg**：本沙箱无系统 ffmpeg/brew → 用 `imageio-ffmpeg` pip 包（自带静态二进制，`imageio_ffmpeg.get_ffmpeg_exe()`）。
- **HTTP**：`requests`（managed venv 已装）。
- ElevenLabs API：`POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44_128`，header `xi-api-key`，body `{"text","model_id":"eleven_multilingual_v2","voice_settings":{stability:0.4,similarity_boost:0.78,style:0,use_speaker_boost:true}}`。

## 配套文本（不卡声音，可并行做）
生产包里的 Show Notes / 小红书切片 / 公众号长文，可在音频生成期间整理成发布就绪草稿。

## 引擎脚本
`scripts/build_podcast.py`：`--script <TTS脚本路径> --secrets <密钥文件> --mode {dry-run|pilot|full}`。
- `dry-run`：解析+估算时长（不调 API）。
- `pilot`：生成试听段（默认 01,02,03）。
- `full`：全量生成+拼接+导出+QC。
