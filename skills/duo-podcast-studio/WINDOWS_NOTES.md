# WINDOWS_NOTES · duo-podcast-studio（融合 duoduo-podcast-build）

> 2026-07-29 Windows 侧首次部署记录 · 复制完毕，但**未跑通**，以下为卡点（不硬凑）。

## 状态：BLOCKED（需多多提供密钥/资源后才能跑通）

### 卡点 1 — 用户专属密钥（Agent 无法替代）
- 需要 `ELEVENLABS_API_KEY` / `DUODUO_VOICE_ID`（多多本人授权克隆声，需 ElevenLabs 付费档 Instant Voice Cloning）/ `PODCAST_PARTNER_VOICE_ID`。
- 这三个值只能由多多本人在 ElevenLabs 上传授权录音、建 voice 后提供。Agent 无法凭空合成本人声音。

### 卡点 2 — 密钥路径是 Mac 路径
- SKILL.md 第 23 行示例路径为 `/Users/Zhuanz/IP_video_drafts/.env.ep02`（Mac）。
- Windows 上需改为 Vault 之外的本地路径（如 `C:\Users\Administrator\.duoduo\.env.ep02`），且**绝不**写入 Obsidian / 日志 / 聊天。

### 卡点 3 — 引擎脚本缺失
- SKILL.md 引用的 `scripts/build_podcast.py`（`--script/--secrets/--mode`）在镜像 `scripts/` 目录里**为空**，未随镜像提交。
- 需 Mac 侧补全该脚本后再在 Windows 重建，或改为调用 ElevenLabs API 的最小实现。

### 卡点 4 — Python 依赖
- 工具链指定 `imageio-ffmpeg`（自带静态 ffmpeg 二进制）与 `requests`。
- `requests` 已在 managed venv；`imageio-ffmpeg` 需在 managed venv 重装：
  `C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe -m venv C:\Users\Administrator\.workbuddy\binaries\python\envs\default` 后再 `pip install imageio-ffmpeg`。

## 验证记录
- 结构检查：SKILL.md 已就位（frontmatter 完整）。
- 最小用例：未跑（缺密钥 + 缺脚本）。`dry-run` 模式也因缺 `build_podcast.py` 无法执行。
- 结论：先挂起，等多多提供 ElevenLabs 授权声 + key，并由 Mac 侧补 `build_podcast.py`。
