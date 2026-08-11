# duoduo-skills

多多个人公司 WorkBuddy 技能库 · 多设备共享源。

## 是什么
- `skills/` 下 24 个技能 = 多多所有自建 workflow skill 的**唯一权威版本**。
- Mac / Windows 任何设备的 WorkBuddy 都从这里安装或更新技能，不再依赖 Obsidian vault 镜像。
- `catalog.md` = 人读总览；`skills-manifest.json` = 机读清单（每文件 sha256，供比对同步）。

## 任何设备安装（WorkBuddy agent 照做）
```bash
git clone https://github.com/faifaida/duoduo-skills.git /tmp/duoduo-skills
cp -r /tmp/duoduo-skills/skills/* ~/.workbuddy/skills/
```
Windows（PowerShell）：
```powershell
git clone https://github.com/faifaida/duoduo-skills.git $env:TEMP\duoduo-skills
Copy-Item -Recurse -Force $env:TEMP\duoduo-skills\skills\* $env:USERPROFILE\.workbuddy\skills\
```
装完重启 WorkBuddy 会话即可被检测。

## 平台适用性
| 标记 | 含义 |
|---|---|
| ✅ 跨平台 | 直接可用 |
| ⚠️ 需改路径 | 技能内含 Mac 绝对路径，装到 Windows 后按本机路径调整 |
| ❌ Mac 专属 | 依赖 Mac 本机环境（微信客户端 / CalDAV venv / capcut-cli 等），别在其他设备跑 |

❌ Mac 专属：`duoduo-wechat-publish`、`duoduo-wechat-chat-export`、`duoduo-caldav-calendar-write`、`duoduo-video-edit`、`shifei-video-edit`、`duoduo-diary-to-calendar-pipeline`
⚠️ 需改路径：`duoduo-company-daily-os`、`duoduo-company-night-patrol`、`duoduo-expert-hourly-patrol`、`duoduo-approval-detect-and-release`、`duoduo-weekly-review-calendar`、`duoduo-podcast-sync`、`duoduo-podcast-build`
✅ 其余均为跨平台（写作 / 设计 / 方法论类）。

## 同步规则（Mac 侧维护）
- 权威源 = Mac `~/.workbuddy/skills/`。技能有任何修改，Mac 侧 agent 当次会话即同步推送本仓库（见 `skills/duoduo-github-sync/SKILL.md`）。
- 凭证 / 密码 / token **永不入库**；技能里只允许出现凭证的存放路径指针。

## 安全
本仓库当前为 public 时不得含任何敏感信息；目标状态为 private。
