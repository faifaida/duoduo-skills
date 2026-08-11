# duoduo-skills

多多个人公司 WorkBuddy 技能库 · 多设备共享源。

## 是什么
- `skills/` 下 24 个技能 = 多多所有自建 workflow skill 的**唯一权威版本**。
- Mac / Windows 任何设备的 WorkBuddy 都从这里安装或更新技能，不再依赖 Obsidian vault 镜像。
- `catalog.md` = 人读总览；`skills-manifest.json` = 机读清单（每文件 sha256，供比对同步）。

## 安装 / 同步（本地镜像，GitHub 为唯一权威源）
本仓库是技能的**唯一权威源**。本地 `~/.workbuddy/skills/` 只是一份自动同步的镜像，**不要手改本地**。

推荐方式（无需 git，走 GitHub REST API，代理环境也可用）：
```bash
python3 scripts/sync_skills.py              # 同步到最新 release
python3 scripts/sync_skills.py --dry-run    # 只看会改哪些，不落盘
python3 scripts/sync_skills.py --version=v1.2.0  # 同步到指定版本
```
只同步本仓库包含的技能（按文件夹名匹配、且含 SKILL.md），不会删除本地其它技能。

备选方式（网络正常时）：
```bash
git clone https://github.com/faifaida/duoduo-skills.git /tmp/duoduo-skills
cp -r /tmp/duoduo-skills/skills/* ~/.workbuddy/skills/
```
装完 / 同步完重启 WorkBuddy 会话即可被检测。

## 平台适用性
| 标记 | 含义 |
|---|---|
| ✅ 跨平台 | 直接可用 |
| ⚠️ 需改路径 | 技能内含 Mac 绝对路径，装到 Windows 后按本机路径调整 |
| ❌ Mac 专属 | 依赖 Mac 本机环境（微信客户端 / CalDAV venv / capcut-cli 等），别在其他设备跑 |

❌ Mac 专属：`duoduo-wechat-publish`、`duoduo-wechat-chat-export`、`duoduo-caldav-calendar-write`、`duoduo-video-edit`、`shifei-video-edit`、`duoduo-diary-to-calendar-pipeline`
⚠️ 需改路径：`duoduo-company-daily-os`、`duoduo-company-night-patrol`、`duoduo-expert-hourly-patrol`、`duoduo-approval-detect-and-release`、`duoduo-weekly-review-calendar`、`duoduo-podcast-sync`、`duoduo-podcast-build`
✅ 其余均为跨平台（写作 / 设计 / 方法论类）。

## 同步规则（GitHub 为权威源）
- **权威源 = 本 GitHub 仓库**，不是本地。任何技能修改都在仓库里发生（agent 经 REST API 推送），本地只做镜像。
- 更新流程：开 Issue → 改技能 → 提 PR 关 Issue → 合并 `main` → release-please 自动打 tag + 建 GitHub Release（版本号如 `v1.11.2`）。
- 本地刷新：跑 `python3 scripts/sync_skills.py` 把最新 release 拉回 `~/.workbuddy/skills/`。
- 凭证 / 密码 / token **永不入库**；技能里只允许出现凭证的存放路径指针。

## 版本与发版
- 版本号由 [release-please](https://github.com/googleapis/release-please) 自动管理：提交信息用 conventional commits（`feat:`/`fix:`/`docs:`…），合并 `main` 后自动开「发版 PR」→ 合并即生成 `vX.Y.Z` tag + GitHub Release。
- 每次 Release 的说明自动汇总当次关掉的 Issues / 合进的 PR，所以「GitHub 显示版本号 + Issues 填得满」是同一套流程的产物。
- 首个版本从 `1.0.0` 起（见 `.release-please-manifest.json`，想首发就是 `1.11.2` 改这一行即可）。

## 安全
本仓库当前为 public 时不得含任何敏感信息；目标状态为 private。
