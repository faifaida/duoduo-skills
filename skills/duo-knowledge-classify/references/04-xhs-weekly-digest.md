# 小红书周摘要（原 skill: duoduo-xhs-weekly-digest）

# duoduo-xhs-weekly-digest (小红书专辑新增 → 整理 · 内容运营 每周二 7:00)

Weekly intake of new Xiaohongshu saved notes, organized for content reuse.

## When to use
- The Tuesday 07:00 content-ops automation (expertId = duoduo-content-ops / 内容运营).
- Any "grab this week's new XHS saved notes and tidy them" request.

## Procedure
1. **Grab new notes** from 多多's Xiaohongshu saved albums. Use `xhs-spider-sync` (incremental board
   sync) and/or `xhs-obsidian-import` to pull only what was added since last week (dedupe by noteId).
2. **Organize** the new notes into `02_内容运营/` (e.g. a `小红书素材/` or `dispatch/` subfolder) with
   frontmatter (source=小红书, board, date, tags).
3. **Triage for content reuse:** flag notes that could become posts / dispatching material vs pure
   reference. Do NOT auto-publish (SOP forbids auto-publish).
4. **Log** what was pulled and where it landed.

## Notes
- This is a 内容运营 (content-ops) task; owner = 内容运营.
- Built on existing `xhs-spider-sync` / `xhs-obsidian-import` — this skill is the weekly cadence +
  organizing layer, not a new scraper.
- Incremental only: never re-pull the whole history each week.

## 动作节点（多多能听懂的）
1. 每周二上午 7 点，内容运营从小红书你收藏的专辑里，抓出自上周新增的笔记（按 ID 去重，不全量重抓）。
2. 整理进 `02_内容运营/` 的素材/分发目录，带来源、专辑、日期、标签。
3. 标出哪些能变成发文/分发素材、哪些只是参考（不自动发，SOP 禁自动发布）。
4. 记录抓了什么、落在哪。
