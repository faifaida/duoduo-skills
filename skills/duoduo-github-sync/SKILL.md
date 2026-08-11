---
name: duoduo-github-sync
description: >
  把多多的 duoduo-* 工作流技能（及主目录 catalog / manifest）备份到她的 GitHub 仓库
  faifaida/duoduo-skills。触发词：「同步技能到 GitHub / 备份 skill / github sync」，
  或任一批量改完技能后想留底。默认按需（无固定自动化）。仓库已存在（发播客到 Apple Podcasts
  时建过），当前为 public，需改为 private——这一步需要多多的邮箱 OTP 或 PAT，助理无法纯无头完成。
agent_created: true
---

# duoduo-github-sync — 技能库 GitHub 备份

## 0. 现状（务必先读）
- **账号 / 仓库**：`faifaida` / `faifaida/duoduo-skills`，分支 `main`。**仓库已存在**（发播客到 Apple Podcasts 时由助理建过），**不要叫多多手动建仓**。
- **当前可见性：PUBLIC**（已用未鉴权 API 确认 `private=false`）。**目标：private**。
- **改 private 是交互操作**：GitHub 改可见性要走 sudo 邮箱验证码（**8 位、15 分钟有效、一次性**）。助理在本沙箱里**无法无头完成**这步——要么多多自己在网页点（推荐，最安全），要么多多给一个 GitHub PAT 让助理用 API 改。详见 §4。
- 本环境 GitHub MCP 连接器 = `connector:github` → `https://api.githubcopilot.com/mcp/`。它**没有**改可见性的工具，只有 `push_files` 推内容。

## 1. 同步范围（白名单，只推这些）
1. `~/.workbuddy/skills/duoduo-*/**` + `qu-ai-wei` → 仓库 `skills/<skill-name>/`（排除 `.git`/`__pycache__`/`node_modules`/`.DS_Store`/`*.pyc`；⚠️ qu-ai-wei 自带嵌套 `.git`，必须先删掉其 `.git` 再 add，否则推上去是空 gitlink）
2. vault 独有技能（本机 skills 目录没有的）：`99_Systems/00_Workflows/` 下的 `duoduo-podcast-sync`、`daily-diary-skill`、`duo_longpic-gen` → 同样进 `skills/`
3. 仓库根：`README.md`（多设备安装命令 + 平台适用性 ✅/⚠️/❌ 标注）+ `catalog.md`（人读总览）+ `skills-manifest.json`（机读清单，每文件 sha256）
4. **绝不推**任何凭证 / 配置：`caldav_config.json`、token、密码、`mcp.json`、`.credentials.*`、日记、公司档案其余文件、微信导出。推送前 Grep `password|secret|token|专用密码|app-specific` 扫一遍，命中先人工判断是真密钥还是文字引用；真密钥剔除并报告。

## 1.5 本地暂存仓 + 实时同步铁律（2026-07-29 起）
- 暂存仓：`~/.workbuddy/duoduo-skills-repo/`（git，branch main）。同步动作 = rsync 重刷 `skills/` → 重算 catalog/manifest（脚本见 §3）→ `git add -A && commit -m "sync: <日期>"` → push。
- **实时同步铁律（多多 2026-07-29 要求）**：任何会话修改了白名单技能（新建/编辑/删除），**同一会话内**必须同步暂存仓并 push GitHub。
- vault `99_Systems/00_Workflows/` 镜像自 2026-07-29 起**废弃**，不再维护（多多要求 Obsidian 不再存技能）；GitHub 是唯一分发源。

## 2. 写入路径（两条，按可用性选）
**A. GitHub MCP 连接器（优先）**
- 工具：`mcp__github__push_files`（批量写）、`mcp__github__create_or_update_file`（单文件）、`mcp__github__get_file_contents`（抽查）。
- ⚠️ 实测：**部分会话里这些工具没有被加载进 deferred 索引**（`DeferExecuteTool` 报 "not found"）。若加载不到，直接走 B。
- 参数：owner=`faifaida`，repo=`duoduo-skills`，branch=`main`，commit message=`sync: <日期> <批次>`。

**B. GitHub PAT + git / curl（兜底，最稳）**
- 多多提供 **fine-grained PAT**（权限：对 `faifaida/duoduo-skills` 的 `Contents: Read/Write` + `Administration: Read/Write` 以便改可见性）。
- 克隆 / 推送：
  ```bash
  git clone https://github.com/faifaida/duoduo-skills.git /tmp/duoduo-skills
  # 把 skills/* 与 catalog.md / skills-manifest.json 拷进去
  cd /tmp/duoduo-skills && git add -A && git commit -m "sync: <日期>" && \
  git push https://<PAT>@github.com/faifaida/duoduo-skills.git main
  ```
- 改可见性（仅 PAT 能办）：
  ```bash
  curl -sS -X PATCH -H "Authorization: Bearer <PAT>" \
    -H "Accept: application/vnd.github+json" \
    https://api.github.com/repos/faifaida/duoduo-skills \
    -d '{"private":true}'
  ```
  ※ `api.githubcopilot.com/mcp/` 的 OAuth token **不是 PAT**，不能改可见性；必须用真 PAT。

## 3. 步骤
1. （可选）`ToolSearch` / `DeferExecuteTool` 试 `mcp__github__get_me` 验证 MCP 是否可用；不可用 → 走 B。
2. 收集待推文件：`ls ~/.workbuddy/skills/duoduo-*/` + 本目录 `catalog.md` / `skills-manifest.json`。
3. 敏感信息扫描（见 §1），命中即剔除并报告。
4. 推送：路径 A 分批（≤4 文件 / 次）或路径 B 一次 `git push`。commit message `sync: <日期>`。
5. 验证（**先验证再交差**）：路径 A 用 `get_file_contents` 抽查 1–2 个；路径 B 用 `GET /repos/faifaida/duoduo-skills/contents/skills` 确认文件数。
6. 若仓库仍是 public：提醒多多改 private（§4），或拿到 PAT 后用 §2-B 的 curl 改。
7. 汇报：推了几个文件、几个 commit、仓库链接 https://github.com/faifaida/duoduo-skills 、可见性状态。

## 4. 把仓库改成 private（关键约束）
改可见性是 GitHub sudo 操作，需要**邮箱验证码**：
- **方式 1（推荐，最安全）**：多多自己进 Settings → 右下 "Change visibility" → "Change to private" → 确认 → 她邮箱收 8 位码 → 填码。这一步只有多多能收验证码，助理不参与。
- **方式 2（给 PAT 让助理代办）**：多多在 GitHub → Settings → Developer settings → Fine-grained PAT，授权 `faifaida/duoduo-skills` 的 Administration，把 PAT 给助理；助理用 §2-B 的 curl 改。
- ⚠️ 验证码是 **8 位**（不是 6 位），15 分钟内有效、一次性。过期重发。
- ⚠️ 本沙箱曾用无头 Chrome 走这条流程，但会因跨标签页 / 会话失效而卡死；**不要依赖无头浏览器改可见性**，走方式 1 或 2。

## 5. 已知坑（已修正）
| 症状 | 原因 | 解法 |
|---|---|---|
| 仓库是 public 不是 private | 建仓时没改可见性 | §4 改 private |
| MCP 工具 `not found` | 该会话没把 github 工具加载进索引 | 走 §2-B PAT + git 兜底 |
| create_repository 403 | 旧版误以为要建仓；其实仓已存在 | 直接 push，不建仓 |
| push_files 单次超限 / 截断 | 文件多 | 分批 ≤4 文件 / 次（路径 A） |
| 误推凭证 | 白名单外文件混入 | §1 扫描 + 只推白名单 |

## 6. 多多能听懂的动作节点
1. 你说「同步技能到 GitHub」→ 我把全部 duoduo-* 技能 + 总览推到 `faifaida/duoduo-skills`。
2. 推之前扫一遍，**任何密码 / 凭证绝不上传**。
3. 推完抽查仓库确认真的传上去了，再汇报。
4. 仓库暂为 public——改 private 需要你的邮箱验证码（你点一下最安全），或给我一个 PAT 我代改。
5. 默认按需，不定时自动跑；想并进夜巡每天自动备份，说一声。
