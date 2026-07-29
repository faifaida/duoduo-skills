---
name: duoduo-voice-clone
description: 多多声音克隆 + 播客/视频配音生成。输入一段参考音频（多多本人声纹），用开源方案（OpenVoice v2 零样本 / GPT-SoVITS v2Pro 微调）克隆声音，批量生成带 Speaker 标签的 TTS 脚本为克隆音频，拼接后期出片。MIT 协议、本地/自托管、免费可控。
---

# duoduo-voice-clone · 多多声音克隆

> 解决「用多多本人声音自动生成播客/视频配音」的能力。替代闭源 ElevenLabs（路线 A），声音资产 100% 自持。

## 何时用
- 用户要求「用我的声音」「克隆我自己」「开源不要 ElevenLabs」「本地可控」生成音频。
- 播客 EP（如 EP02 人生不该每次重启）、视频口播配音、任何需要多多本人音色的 TTS。

## 后端选择（二选一）
| 后端 | 样本 | 中文质量 | 算力 | 协议 |
|---|---|---|---|---|
| **OpenVoice v2**（默认·零样本） | 10–15s 参考音频，给音频即用，**无需训练** | 中（跨语言转换，可能带轻微腔） | CPU 可跑（慢但可行） | MIT |
| **GPT-SoVITS v2Pro**（高质量） | 5s 零样本 / 1min 微调最佳 | **中文最佳** | 训练需 NVIDIA GPU；Apple Silicon 可推理 | MIT |

> 今晚优先 OpenVoice 零样本（无需训练等待，最快出片）。要中文长篇更稳，再上 GPT-SoVITS 微调（1min 样本，云端 GPU 训 15–40min）。

## 输入
- 参考音频（多多本人干净人声，安静环境录制，WAV/MP4 均可；OpenVoice 10–15s，GPT-SoVITS 1min 更佳）。
- 带 Speaker 标签的 TTS 脚本（如 `EP02_TTS安全脚本.txt`，格式 `[SEGMENT_n]` + `SPEAKER_A/B:` + 文本）。
- 伴侣/第二人声（SPEAKER_B）可选：再给一段参考音频 `--ref-b`；缺省用 OpenVoice base speaker（非克隆）。

## 执行流程
1. **解析** TTS 脚本 → `[{id, speaker, text}]` 清单（复用 `scripts/clone_and_generate.py` 的解析器）。
2. **克隆/加载**：OpenVoice 实测 API 为 v1 式——`converter.extract_se([ref_wav])` 提取 target embedding（**勿用 `se_extractor.get_se`**，其 VAD/Whisper 依赖装不上）；中文用 `base_speakers/ZH` 底座 + `zh_default_se.pth` 作 source_se，`language='Chinese'`。GPT-SoVITS 加载微调模型。
3. **逐段生成**：A 段用多多克隆声，B 段用伴侣克隆声或 base speaker。失败重试 ≤2 次。
4. **拼接**：段间留 0.3–0.5s 静音（章节感），`ffmpeg` 统一音量（-16 LUFS 区间）。
5. **后期**：加片头/片尾（克制动效），导出 MP3（发布）+ WAV（母版）。
6. **质检**：对照 `EP02_音频质检表.md` 跑（段数/漏句/声音未交换/发音/自然度/音量），出 QC 报告。

## 运行位置（2026-07-27 实测已固化，直接用）
- **venv**：`/Users/Zhuanz/.workbuddy/binaries/python/envs/ov310/bin/python`（Python 3.10.20，openvoice+torch2.13+jieba/cn2an/pypinyin 全齐；⚠️ 该 venv 无 pip 模块，装包用 uv）。
- **权重**：`/Users/Zhuanz/IP_video_drafts/ov_weights/checkpoints_v2/`，含 `base_speakers/EN/`（checkpoint+config+default_se）、`base_speakers/ZH/`（checkpoint 153M+config+zh_default_se，2026-07-27 从 hf-mirror.com 补齐；大文件断线用 `curl -C -` 续传）、`converter/`。
- **多多参考音频**：`/Users/Zhuanz/IP_video_drafts/EP02_audio/refs/duoduo_zh.wav`（2:57 中文）+ `duoduo_en.wav`（54s 英文），源文件在 vault `02_CONTEXT/多多照片/多多声音*.m4a`。
- 一键命令：`ov310/bin/python scripts/clone_and_generate.py --ref-a refs/duoduo_zh.wav --script <TTS脚本> --lang Chinese`。
- 中文长篇在 CPU 上生成慢（约每 100 字 15–30s），整期 25min 播客预估 30–90min，务必后台跑。

## 与现有流水线接线
- `scripts/clone_and_generate.py` 是 `build_podcast.py`（ElevenLabs 版）的开源后端替换：把 TTS 调用从 ElevenLabs API 换成 OpenVoice/GPT-SoVITS 本地推理。
- 输出目录、拼接、后期、质检逻辑完全复用。

## 质量预期与风险
- OpenVoice 零样本中文：能出可发表版本，但可能带轻微非母语腔；长篇播客建议后续用 GPT-SoVITS 微调替换。
- 首次运行需下载模型权重（OpenVoice checkpoints ~百 MB），确保运行环境能联网。
- 任何「声音不像」问题：加长参考音频 / 换 GPT-SoVITS / 检查参考音频是否干净（去背景音）。

## 依赖
- Python 3.10+，`pip install openvoice torch`（OpenVoice）；GPT-SoVITS 用其 WebUI/Docker。
- `ffmpeg`（用 `imageio-ffmpeg` 静态二进制或系统安装）。
