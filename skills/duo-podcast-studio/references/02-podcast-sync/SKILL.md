---
name: duoduo-podcast-sync
description: 播客「多多的未完成实验」跨平台同步技能。当多多说"启动播客同步 / 同步播客 / 跑一下播客同步"时调用。把小宇宙的新单集同步到 Apple Podcasts（GitHub Pages RSS）和喜马拉雅（专辑 127170840）。只在被明确要求"启动"时运行，不自动定时。后台 headless 运行，绝不占屏幕。
agent_created: true
---

# 播客同步技能（小宇宙 → Apple Podcasts + 喜马拉雅）

## 触发方式
- 多多说「启动播客同步」「同步播客」「跑一下播客同步」等 → 运行 `scripts/run_sync.sh`。
- **不在定时自动化里跑**（原两个自动化已取消，改为按需触发）。
- 运行前先确认多多确实发了新单集，或至少允许做一次检测（无新集会自动跳过，rc=0，不误报）。

## 关键事实（写死在脚本里，勿改除非多多确认）
- 小宇宙节目 pid：`6a5a306305d4bfbabc3ea16b`（公开页 SSR，无需登录）。
- 单集音频直链：`https://media.xyzcdn.net/<pid>/<hash>.m4a`（用于 RSS enclosure 与下载上传）。
- **Apple Podcasts**：读 GitHub Pages `https://faifaida.github.io/duoduo-podcast/rss.xml`（仓库 `faifaida/duoduo-podcast`，main 分支根目录）。Apple 不读小宇宙（账号未开放 RSS 分发），所以新单集必须改这个 RSS。覆盖 `rss.xml` 即可，Apple 自动抓取。
- **喜马拉雅**：专辑 `127170840`「多多的未完成实验」，上传页 `studio.ximalaya.com/upload`。

## 运行步骤
1. `bash scripts/run_sync.sh`
   - 先 `ensure_headless.sh`：若 9222 不在线则启动 headless Chrome（用持久登录态 `/Users/Zhuanz/.xm_headless_profile`，`--headless=new` 无可见窗口）。**绝不 pkill 用户真实 Chrome。**
   - 跑 `apple_rss_sync.py`：检测小宇宙新单集 → 用 CM6 `EditorView.dispatch` 整体替换 `rss.xml` → 提交 → 校验线上 RAW（well-formed + item 数=小宇宙单集数）。
   - 跑 `ximalaya_sync.py`：检测新单集 → 下载音频 → 上传专辑 127170840 → 校验管理页「在架(1)」。
2. 读脚本输出判断结果：
   - `NO_NEW_EPISODES` → 无新单集，正常跳过。
   - `DONE: rss.xml 已更新` / `DONE` → 已同步/已发布。
   - `DONE_WITH_WARNINGS` / 非零 → 见下方排查。

## 硬性约束（必须遵守）
- **绝不占屏幕**：所有 Chrome 操作走 headless CDP（端口 9222），不开可见窗口。
- **只动两处**：① `faifaida/duoduo-podcast` 的 `rss.xml`；② 喜马拉雅专辑 `127170840`。不动喜马拉雅其他专辑、不动其他仓库。
- **绝不 pkill 用户真实 Chrome**：headless 是独立 `--user-data-dir` 副本。

## 故障排查（不要假装成功）
- **headless 启动失败 / CDP 离线**：`curl -s --max-time 4 http://localhost:9222/json/version` 看是否在线。离线则脚本会自愈重启。
- **GitHub / 喜马拉雅登录态过期**（提交被拒、编辑器跳登录页、上传报未授权）：说明 `/Users/Zhuanz/.xm_headless_profile` 会话过期。**明确告诉多多需要重新登录刷新该 profile，不要重试假装成功。** 刷新方法：用该 profile 路径手动开一次 Chrome 登录，或直接让多多在真实 Chrome 登录后由我重新固化。
- **网络瞬时 503/超时**：可重试一次 `run_sync.sh`。
- **Apple 实际状态兜底核验**（任何 rc≠0 时都做，作为结论依据）：
  - 小宇宙公开页单集数 vs 线上 `rss.xml` 的 item 数、guid 是否对齐。
  - 若对齐且 well-formed=YES → Apple 实际已正确，只是提交路径故障，不恐慌。

## 备注
- 本技能从原「小宇宙→喜马拉雅」与「小宇宙→Apple Podcasts」两个定时自动化合并而来（2026-07-27 取消定时、改为按需技能）。
- 脚本原在 `/tmp` 被系统清理丢失，现固化在 Obsidian `99_systems/00_Workflows/duoduo-podcast-sync/`（持久、不丢）。
