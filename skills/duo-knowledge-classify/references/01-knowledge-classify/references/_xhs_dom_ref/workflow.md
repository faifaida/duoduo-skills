# 小红书 → Obsidian 导入：技术细节参考

> ⚠️ **LEGACY** — 本文件是**旧 DOM 抓取方式**（原 `xhs-obsidian-import` 技能）的参考，已被 `../01_小红书通道.md` 的签名 API 方案取代，仅供调试 / 考古查阅。对应脚本在 `scripts/xhs_legacy_dom/`。

## 脚本清单（scripts/）
| 文件 | 作用 |
|---|---|
| `core.py` | Chrome 驱动底层：`launch(url)` 开新窗口返回 id、`run_js(win, jsfile, timeout)` 执行页面 JS、`close_win`、`relaunch_chrome`、`osa(script)`。JS 文件从脚本同目录读取。 |
| `collect.js` | 在 board 页增量滚动，累积所有 `section.note-item > a.cover` 的站内链接到 `window.__xhsArr`，返回当前数量。 |
| `scroll_bottom.js` | `scrollTop = scrollHeight` 触发无限滚动加载更多卡片。 |
| `get_arr.js` | 返回 `window.__xhsArr` 的 JSON。 |
| `probe.js` | 详情页提取：`#detail-title`(title)、`#detail-desc`(desc)、`.author-wrapper .name`(author)、`.date`(date，补全年份)、`valid` 标记。 |
| `has_title.js` | 详情页是否渲染出标题（轮询等待用），返回 `"1"`/`"0"`。 |
| `scrape.py` | `collect_links(url,name)` 采集链接（带缓存 `links_<name>.json`）；`scrape_details(name,links,out_json)` 逐篇抓详情，断点续传 `done_<name>.jsonl`。 |
| `process.py` | `process(board_json, album)` 把 JSON 生成笔记到 `VAULT/<album>/` 并写 `专辑-<album>.md` 索引；`rebuild_index(album)` 按文件夹现状重建索引；`note_md(note,album)` 单篇渲染；`infer_focus/infer_threads` 主题推断。 |
| `sync.py` | **每周任务入口**：读 `boards.json` → 对每个专辑增量去重抓取并生成笔记、更新 `imported_ids.json`。 |
| `run_rest.py` | 顺序全量重抓 `boards.json` 全部（纠正历史数据用）。 |
| `fetch_boards.py` | 打开用户 profile 收藏专辑页，抓所有 `/board/<id>` 链接。 |
| `resolve_boards.py` | 逐个打开 board 页，用 `board_title.js` 解析真实名称，输出 id→name 映射。 |
| `board_title.js` | 读 `document.title`（去「 - 小红书」后缀）作为 board 名。 |
| `boards.json` | **唯一数据源**：vault 路径、profile URL、8 个专辑 name/id。 |
| `imported_ids.json` | 去重表：`{专辑: [noteId,...]}`。 |

## 核心数据流
```
profile 页 (fetch_boards + resolve_boards)  →  board id
        ↓
board 页 (collect.js 轮询+scroll_bottom 增量滚动)  →  window.__xhsArr (站内链接)
        ↓ to_explore() 重建
/explore/<id>?xsec_token=...&xsec_source=pc_user  详情页
        ↓ probe.js
{noteId,title,author,time,desc,url,valid}  →  done_<album>.jsonl (检查点)
        ↓
xhs_<album>.json  →  process.py  →  VAULT/<album>/标题-日期.md + 专辑-<album>.md
```

## 详情页 DOM 选择器（probe.js 依赖）
- 标题：`#detail-title`（兜底 `.title`）
- 正文：`#detail-desc`（干净无 footer）
- 作者：`.author-wrapper .name`
- 日期：`.date`，格式 `MM-DD`（当年）或 `YYYY-MM-DD`（更早/编辑过）。补年规则：只有 `MM-DD` 时取 `new Date().getFullYear()`。

## 笔记 frontmatter 与正文结构
```markdown
---
type: xhs-save
title: "可读标题"
collected_date: "2026-07-21"
author: 作者名
url: https://www.xiaohongshu.com/explore/<24hex>
category: [专辑名]
focus: ["🌻自我", "🔥个人提升／技能"]
company_threads: []
why_saved: "[AI推断] 偏「🌻自我」主题，收藏后拆为己用。"
action: 待拆解
related: ""
status: categorized
knowledge_work: false
source: xiaohongshu
---

# 可读标题

> [!note] 边收边分工作流 ...

## 原帖要点

<抓到的真实正文>

## 我的提取

- 可取：<要点>
- 可复用方法：<做法/步骤>
- 想验证：这条能否变成【🌻自我】的一个小实验 / 一篇内容？

## 可转化输出的内容

<按 focus 主课题给的转化建议>
```
**注意**：`focus` 必须是纯文本 YAML 列表，**绝不能**写 `[[八个人生课题#...]]` —— 否则整块 frontmatter 解析失败，Obsidian 不显示任何属性。

## 八个人生课题（focus 取值）
🔥个人提升／技能 / 🌻自我 / 🍓关系 / 🍍资源 / 💫职业 / 🦋探索 / 💗美丽 / 🍀生活方式／健康
对应 `process.py` 里 `TOPIC_KW`（关键词→课题）、`ALBUM_FOCUS`（专辑默认课题）、`ALBUM_THREAD`（company_threads：文旅青旅 / 内容 / 流动生活 / 关系与社群）。

## 调试命令
```bash
# 查看某本实时采集进度
wc -l ~/Downloads/xhs_scraper/done_<专辑>.jsonl

# 校验 frontmatter 是否为合法 YAML
python3 -c "import yaml,re;t=open('笔记.md').read();yaml.safe_load(re.match(r'^---\n(.*?)\n---',t,re.S).group(1))"

# Chrome 是否可驱动
osascript -e 'tell application "Google Chrome" to get count of windows'

# 重启 Chrome（卡死时）
killall "Google Chrome"; sleep 3; open -a "Google Chrome"
```

## 已知限制
- **服务端隐藏笔记**：原作者私密/注销的笔记，web feed 不渲染，任何网页抓取都拿不到。表现为「board 标称 N 篇，实际最多放出 M 篇（M<N）」。不是脚本 bug，不要反复重试。
- **依赖本机环境**：抓取靠用户真实 Chrome + VPN，定时任务只有在 Mac 醒着、Chrome 开、VPN 连时才跑得起来。
- **点赞数拿不到**：无 `INITIAL_STATE__` 时 DOM 只显示「赞」无计数，故笔记不含 likes 字段。
