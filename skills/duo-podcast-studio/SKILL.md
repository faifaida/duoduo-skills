---
name: duo-podcast-studio
description: 多多《多多的未完成实验》双人 AI 播客「制作 + 重用途 + 音频生成 + 发布分发」统一标准 skill。融合原 duo-podcast-studio（锁定声纹/混音/全片质检生产标准）、podcast-ops（一期节目拆 20+ 跨平台内容的内容重用途流水线）、duoduo-podcast-build（带 SPEAKER_A/B 标签的 TTS 安全脚本 → 成片音频 MP3/WAV + 克隆声）。当用户说"做播客/出 EP/把脚本生成音频/今晚发播客/把一期节目拆成多平台内容/发布 EP 到各播客平台/把 EP 发到小宇宙喜马拉雅Apple"时触发。发布分发细节见下方「D · 发布 / 分发到各播客平台」。
agent_created: true
---

# DUO Podcast Studio — 锁定生产标准 + 内容重用途 + TTS 音频生成

本 skill 是多多双人 AI 播客的**统一标准入口**，融合三块能力：

- **A · 锁定生产标准（Studio）**：声纹、节奏、逐段清理、全片质检门、修复、交付归档。这是"怎样算 publish-ready"的硬性标准，任何成片都必须过 7 项质检门。
- **B · 内容重用途流水线（Ops）**：把一期节目（RSS/转录稿）拆成 20+ 跨平台内容（短视频切片/推特线程/领英文章/通讯/金句卡/博客大纲/脚本），带病毒分与去重。脚本 `podcast_pipeline.py`，详见 `README_podcast_ops.md`。
- **C · TTS 音频生成（Build）**：把带 `SPEAKER_A`/`SPEAKER_B` 标签的 TTS 安全脚本，经 ElevenLabs 克隆声（多多本人 A + 固定搭档 B）生成成片 MP3/WAV + 质检报告。

三者关系：B 把节目变素材与分发清单 → C 把分镜/脚本变成声音成片 → A 的质量门罩住 C 的产出（以及任何手工混音）。**未过 A 的质检门，不可标 publish-ready / 不可外发。**

---

# A · 锁定生产标准（Studio）

This is a reproducible production package, not a loose style guide. Use the approved assets and settings below unless 多多 explicitly changes them. Never substitute a generic female voice, invent a new male host, or silently alter pacing.

## Privacy and required assets

All files in `references/voice-reference/` are private voice materials. Process locally by default; send them to a third-party provider only with explicit permission for that provider.

- **A / 多多 source reference:** `references/voice-reference/Yongtai Street.m4a`
- **A / approved timbre anchor:** `references/voice-reference/EP02_试听_多多本人_Yongtai_HeyGen.mp3`
- **Approved A characteristics:** conversational Mandarin, slightly husky / with a little vocal fry, natural energy; do not make it overly crisp, slow, polished, or presenter-like.
- **B / fixed co-host:** `ryan` only. Warm, calm Chinese male host; never replace with a different preset during an episode.

If these files are absent, ask for them; do not manufacture a face, voiceprint, or "close enough" imitation.

## Locked baseline voice configuration

### A — 多多

Primary local baseline:

- Model: `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16`
- Reference: the approved timbre anchor above, preferably a clean 12–20 second excerpt.
- Language: `zh`; baseline speed: `1.04`; temperature: `0.65–0.70`; top-p: `0.85–0.90`.
- Preserve the approved voice sample's slightly husky texture. Do **not** globally increase pitch, add "bright/clear" processing, or speed up the whole A track.
- Optional final timbre conversion: Seed-VC with `Yongtai Street.m4a` as target. First produce a 20-second A/B sample against the anchor; use it only if it remains at least as similar and intelligible. It is a correction pass, not permission to change delivery.

### B — male co-host

- Model: `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16`
- Fixed voice: `ryan`; language: `zh`; speed: `1.05`; temperature: `0.20–0.35`; top-p: `0.70–0.80`.
- Do **not** use an instruction prompt, dynamic pitch, a different speaker ID, or style randomization with this local custom voice. These have caused shouting, prolonged pseudo-speech, missing tails, and speaker drift.
- Render every B turn as single sentences (maximum about 45 Chinese characters per render), then rejoin in source order. This is mandatory even when the script labels it as one turn.
- Reduce B by about **3 dB** relative to A (starting gain `0.68–0.71`); match perceptual loudness by listening, not just peak level.

## Script and pacing protocol

1. Parse every individual `SPEAKER_A:` / `SPEAKER_B:` occurrence into a chronological JSON manifest before rendering. A segment is not a turn: `A → B → A` creates three turns.
2. Each manifest record must contain `turn_id`, `speaker`, exact source text, sentence parts, render paths, duration, and QC status. Never hand-copy text into a regeneration command.
3. A is not globally slow. Preserve sentence-to-sentence breathing space: **0.30–0.40 s** (use `0.35 s` default). B sentence joins: **0.12–0.18 s** (use `0.15 s`). Dialogue turn joins: **0.28–0.35 s** (use `0.32 s`).
4. Add 25–40 ms fades to every assembled unit. Join tracks serially; never place A and B on overlapping timelines unless the script explicitly requests an interruption.
5. An original cold open, one small clean transition effect, or a 60-second lofi outro is optional only when requested. Effects must never mask syllables or resemble static. Keep music clearly under speech and append it only after dialogue.

## Per-turn cleanup and validation

Before mixing, every rendered unit must pass:

- Trim leading/trailing dead air with activity detection; retain only intentional speech pauses.
- Reject and regenerate any unit with clipping, an abrupt final-consonant cut, a long low-energy / pseudo-speech tail, a pitch jump, shouting, or a missing phrase.
- Inspect both absolute silence and low-energy "fake audio." Any internal low-energy gap longer than **0.8 s** is a failure unless the exact script calls for a pause.
- Check duration against its text. A sentence that is dramatically shorter than normal speech or longer than roughly 2.5× its expected reading time is suspect and must be listened to.
- Render A sentence-by-sentence only when artifact repair requires it; retain A's natural sentence gaps after reassembly.

## Mandatory full quality gate

Do this after every rebuild — including a one-line repair — before describing an export as checked or moving it into `to publish`.

1. **Manifest integrity:** source label count equals manifest count; every manifest row has exactly one completed turn audio file; no missing, duplicated, or substituted text.
2. **Exact-text integrity:** programmatically read source text from the manifest for every rerender. Manually compare repaired rows to the source as an additional check.
3. **Silence and coverage scan:** inspect every turn and the final mix in short RMS windows. Fail on >0.8 s accidental silence / low-energy gap, clipped regions, or long tails. Do not accept a zero-silence scan alone as proof; pseudo-speech must be checked.
4. **Timeline integrity:** verify serial order and no accidental overlay. Specifically inspect all turn boundaries for lost last syllables / cut-off phonemes.
5. **Voice integrity:** listen to early, middle, and late A and B samples. B must remain `ryan`, stable in register and calmer than A; it must not shout or vary as if different people. Check B sits about 3 dB below A.
6. **Content and duration:** compare final runtime and ordered spoken text to the script. A material duration change from a small repair signals a structural error — stop and rebuild from the manifest.
7. **Human spot check:** listen to the first minute, one point in every quarter, every repaired timestamp, and the final minute. This is required; numerical detection cannot replace it.

Only label an output `完整版` / publish-ready after all seven checks. Until then use `draft` or `待确认`; preserve the last approved master unchanged.

## Repair protocol

When 多多 gives a timestamp, map it to the manifest first, inspect the exact source unit, rerender only that unit from manifest text, rebuild the full serial mix, then rerun the entire quality gate. Never claim that a full check occurred unless it actually did. If any test fails, report the failure rather than exporting a false final.

## Delivery and archive

- Store source script, manifest, all final assets, and the approved export in the episode folder. Preserve render intermediates in `draft/`.
- Provide a playable absolute local-file link and state final runtime.
- Never publish externally without explicit permission.
- When passing work to another agent, give them this skill folder plus `references/voice-reference/`; that package is the source of truth.

---

# B · 内容重用途流水线（Ops）

把一期节目（RSS 或本地转录稿）拆成 15–20 条跨平台内容，带病毒分与去重。主脚本 `podcast_pipeline.py`（依赖见 `requirements.txt`，用法见 `README_podcast_ops.md`）。

## 流水线

1. **Ingest** — 取转录稿。RSS（`--rss <url>` 自动下载 + Whisper 转写）/ 本地转录稿（`--transcript <file>`，支持 txt/SRT/VTT）/ 批量（`--batch <rss> --episodes N`）。
2. **Extract（Editorial Brain）** — LLM 抽取 7 类内容原子：Narrative Arcs / Quotable Moments / Controversial Takes / Data Points / Stories / Frameworks / Predictions。每条原子标注类型、文本、时间戳、上下文、Viral Score、建议平台。
3. **Generate** — 每期生成：3–5 条短视频切片（含 hook + 时间戳 + 字幕建议 + 平台）/ 2–3 条 X 线程 / 1 篇领英文章 / 1 段通讯 / 3–5 张金句卡 / 1 个博客大纲（带 SEO 关键词）/ 1 个 YouTube Shorts/TikTok 脚本。
4. **Score** — 每条约 Viral Score = Novelty×0.4 + Controversy×0.3 + Utility×0.3（各 0–100）。阈值：80+ 优先发、60–79 填充、40–59 补位、<40 砍掉。
5. **Dedup** — 与本批及近 N 天（默认 30）已发内容做语义相似度检查，>70% 重叠保留高分、砍低分。
6. **Calendar** — 按平台最佳时段生成周发布日历（`--calendar`）。

## 关键约束（贴合多多项目）

- 所有生成内容须过 `duoduo-voice-deai` 去 AI 味；**不虚构事实**，素材来自节目真实内容。
- 分发清单里涉及公众号/小红书等，按对应 skill 的版式与发布流程走（公众号=duo-wechat 制作 + duo-socialpublish-cdp 发布）。
- 输出结构：`output/episodes/<date>-<slug>/{transcript.txt,atoms.json,content_pieces.json,calendar.json}` + `output/calendar/` + `content_history.json`（去重追踪）。

## CLI 速查

```bash
python podcast_pipeline.py --rss "https://feeds.example.com/podcast.xml"   # 最新一期
python podcast_pipeline.py --transcript episode-42.txt                    # 本地转录
python podcast_pipeline.py --batch "<rss>" --episodes 5                    # 批量
python podcast_pipeline.py --calendar                                     # 仅生成周历
python podcast_pipeline.py --rss "<rss>" --min-score 80                   # 只保留高分
```

环境变量：`OPENAI_API_KEY`（Whisper 转写）、`ANTHROPIC_API_KEY`（生成）、`OPENAI_LLM_KEY`（可选，GPT 生成）。

---

# C · TTS 音频生成（Build）

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
- 三个密钥放在 **Vault 之外**的本地文件（如 `C:\Users\Administrator\.duoduo\.env.ep02`），**绝不**写进聊天、日志、成片元数据或 Obsidian。
- 脚本读取该文件、**绝不打印密钥值**（只打印进度/状态）。
- 禁止把 API Key / voice_id / 声音样本输出到任何日志。

## 执行流程
1. **解析** TTS 安全脚本 → 逐段拆成 `{seg_id, speaker, text}` 的 speaker-block 清单。
   - 注意：一个 `[SEGMENT_xx]` 内可能含多个 `SPEAKER_A`/`SPEAKER_B` block，需按行内标签切分。
   - 脚本中"AI"应已替换成"人工智能"（规避英文发音），如未替换，生成前先替换。
2. **试听（mandatory 人工确认节点）**：先生成 `SEGMENT 01–03` → 拼接 → 输出试听 MP3 → **交多多本人试听**（像不像/搭档区分/停顿自然/无播音腔）。
3. **全量生成**：确认后逐段调 ElevenLabs API（A→DUODUO_VOICE_ID，B→PODCAST_PARTNER_VOICE_ID），每段独立生成，失败最多重试 2 次。
4. **后期**：`ffmpeg` 段间留 ~0.45s 静音（章节间隔）→ 音量统一（`loudnorm I=-16`）→ 导出 MP3(128k) + WAV 母版。
5. **质检**：对照音频质检表跑程序化检查（段数一致/漏句/声音未交换/发音词/音量/时长 24–30min）+ 人工确认项（多多试听）。**质检口径与 Part A 的「Mandatory full quality gate」对齐**。
6. **发布前**：多多本人试听 + 确认声音授权范围 + 标题简介与成片一致。

## 工具链
- **ffmpeg**：本沙箱无系统 ffmpeg/brew → 用 `imageio-ffmpeg` pip 包（自带静态二进制，`imageio_ffmpeg.get_ffmpeg_exe()`）。
- **HTTP**：`requests`（managed venv 已装）。
- ElevenLabs API：`POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44_128`，header `xi-api-key`，body `{"text","model_id":"eleven_multilingual_v2","voice_settings":{stability:0.4,similarity_boost:0.78,style:0,use_speaker_boost:true}}`。

## 配套文本（不卡声音，可并行做）
生产包里的 Show Notes / 小红书切片 / 公众号长文，可在音频生成期间整理成发布就绪草稿（配合 Part B 与 duo-wechat / duo-socialpublish-cdp）。

## 引擎脚本
`scripts/build_podcast.py`：`--script <TTS脚本路径> --secrets <密钥文件> --mode {dry-run|pilot|full}`。
- `dry-run`：解析+估算时长（不调 API）。
- `pilot`：生成试听段（默认 01,02,03）。
- `full`：全量生成+拼接+导出+QC。
⚠️ 现状：该引擎脚本在镜像中缺失（详见 `WINDOWS_NOTES.md`），在 Windows 重建前 `dry-run`/`pilot`/`full` 均无法执行；需 Mac 侧补全或改为最小 ElevenLabs API 实现。

---

# D · 发布 / 分发到各播客平台（2026-08-11 EP04 实战固化）

成品过 Part A 的 7 项质检门后，按此分发。**平台全集 = 小宇宙（唯一源头）+ Apple Podcasts + 喜马拉雅**。网易云等若订阅了 RSS 会自动跟，无需手动。

## 架构与分工（别乱序）
- **小宇宙 = 源头**。先发小宇宙，其余平台从小宇宙拉数据。绝不可跳过小宇宙直接发别的平台。
- **Apple Podcasts**：`apple_rss_sync_api.py` 把小宇宙单集拼成 `rss.xml` 推到 GitHub 仓库 `faifaida/duoduo-podcast`，由 GitHub Pages 提供 `https://faifaida.github.io/duoduo-podcast/rss.xml`，Apple 抓取该 RSS。**不碰浏览器，只需 GitHub PAT（凭证文件读）**。
- **喜马拉雅**：`ximalaya_sync_win.py` 经 Playwright `connect_over_cdp("http://localhost:9222")` 上传到专辑 `127170840`（"多多的未完成实验"），靠 `99_Systems/.../state/uploaded_episodes.json` 去重。**需 9222 浏览器已登录喜马拉雅（APP 扫码）**。

## 标准发布流程（照做，不要绕路）
1. **小宇宙**：用 `duo-socialpublish-cdp` 技能的 `podcast_publish.py --package "<To publish_播客第X期>"`（详见该 skill「小宇宙」节；要点：直连 9222 + websocket-client、音频 chooser 拦截、`就绪判据 sec>=30`、勾「阅读并同意」、点「创建」跳 `/stats`）。发布后列表页 + 公开页（`www.xiaoyuzhoufm.com/episode/{id}`）双核验。
2. **Apple**：小宇宙发布后**等几分钟**（见坑①）再跑 `python apple_rss_sync_api.py`（可先 `--dry-run` 确认 `new>0`），PUT 返回 200 后等 ~45s GitHub Pages 重建，再抓 raw URL 核验 `<item>` 数 + 本集标题。
3. **喜马拉雅**：确认 9222 已登录喜马拉雅 → `python ximalaya_sync_win.py`。脚本自动拉未同步单集上传，成功写 state；内容管理页核验标题。

## 已验证坑（2026-08-11 EP04 实战，别重踩）
- **① 小宇宙 SSR 滞后**：`xiaoyuzhou.get_episodes()` 读播客页 `__NEXT_DATA__`，刚发布的单集可能要几分钟才进 SSR。表现：Apple/喜马拉雅 sync 报 `new=0` / `NO_NEW_EPISODES`，但过几分钟重跑就有。→ 小宇宙发布后**等 3–5 分钟再跑同步**，别信第一次 `new=0`（EP04 初跑报 new=0，5 分钟后重跑才识别到）。
- **② 喜马拉雅必须 APP 扫码登录 9222**：登录页无密码，只有「喜马拉雅APP扫码登录」。Agent 无法代登 → **必须多多在 9222 调试 Chrome 用喜马拉雅 APP 扫二维码登录后**，再跑 `ximalaya_sync_win.py`。未登录就跑会卡在 `passport.ximalaya.com` 登录墙，上传 0 条。
- **③ 9222 的 CDP 姿势**：裸 `websocket-client` 的 `Runtime.evaluate` 在 attached target 上易因缺 `contextId` 返回 `None`（连 `1+1` 都 None）。一律用 **Playwright `connect_over_cdp("http://localhost:9222")`** 这条已验证路径（9222 用，夸克是 9223）。用户在占用浏览器时 CDP 会 throttle，此时别硬抢，先确认浏览器空闲。
- **④ Apple RSS 传播延迟**：PUT 200 ≠ 立即生效。GitHub Pages 重建 + CDN 约 30–60s，验证要隔 ~45s 再抓 raw URL（脚本内只等 8s，会误报 `VERIFY_ITEM_MISMATCH`，属正常，等后再抓确认即可）。
- **⑤ GitHub API 走代理**：本机 `HTTPS_PROXY=http://127.0.0.1:7897` 已设，urllib 自动用；脚本无需改。直连 `api.github.com` 也可达（返回 200）。
- **⑥ 七牛/大文件**：小宇宙音频上传走七牛，调试 Chrome 须 `--no-proxy-server` 直连 9222（见 `duo-socialpublish-cdp` 三·代理与大文件上传）。

## 脚本位置（均在 `98_Windows_work/03_发布助手/`）
- `podcast_publish.py` —— 小宇宙通用发布器（`--scan` / `--package` / `--dry-run`）
- `apple_rss_sync_api.py` —— Apple RSS 同步（GitHub API 版，无需浏览器）
- `ximalaya_sync_win.py` —— 喜马拉雅上传（Playwright connect_over_cdp）
- 共享模块：`99_Systems/00_Workflows/duoduo-podcast-sync/scripts/xiaoyuzhou.py`（`get_episodes` / `download_audio` / `guid_of`）

## 自动发布编排建议
EP 发布是三平台联动：小宇宙（podcast_publish.py）→ 等几分钟 → Apple（apple_rss_sync_api.py）+ 喜马拉雅（ximalaya_sync_win.py）。现有每日自动化 `automation-1786399807809`（PAUSED，10:00/22:00 扫 `03 drafts` 发小宇宙）如需覆盖全平台，应在小宇宙发布步骤后追加这两个同步脚本，并把「喜马拉雅是否已登录 9222」作为前置检查（未登录即报，不硬发）。

---

# 参考文件（本 skill 已固化）

- 生产标准资产：`references/voice-reference/`（私密声纹，默认本地处理）
- 混音/声纹标准：`references/voice-and-mix-standard.md`
- 解析脚本：`scripts/parse_turn_manifest.py`、`scripts/qc_audio.py`
- 重用途流水线：`podcast_pipeline.py` + `requirements.txt` + `README_podcast_ops.md`
- Build 部署记录（Windows 卡点）：`WINDOWS_NOTES.md`
- 智能体接口：`agents/openai.yaml`
